# File: sbml_rust_generator/facade.py
"""Main facade class for SBML to Rust conversion"""

import sympy
from typing import Dict, Any
from models.sbml_model import SbmlModel
from parsers.expression_parser import SbmlExpressionParser
from symbolic.ode_builder import OdeSystemBuilder
from symbolic.jacobian_builder import JacobianBuilder
from symbolic.optimizer import SymbolicOptimizer
from symbolic.assignment_processor import AssignmentRuleProcessor
from codegen.code_generator import RustBlockGenerator
from codegen.template_manager import RustTemplateManager
from codegen.event_generator import EventCodeGenerator


class SbmlToRustConverter:
    """Main facade class for SBML to Rust conversion

    This class orchestrates the entire conversion pipeline:
    1. Parse SBML model data
    2. Build ODE system symbolically
    3. Compute Jacobian matrix
    4. Optimize with CSE
    5. Generate Rust code
    6. Assemble final file
    """

    def __init__(self, model_data: Dict[str, Any]):
        """Initialize converter with SBML model data

        Args:
            model_data: Dictionary containing SBML model (from JSON or parser)
        """
        # Store raw data
        self.model_data = model_data

        # Initialize model
        self.model = SbmlModel.from_dict(model_data)

        # Create mappings
        self.species_map = {s_id: i for i, s_id in enumerate(self.model.species.keys())}
        self.species_list = list(self.model.species.keys())


        self.params_map = {p_id: p.value for p_id, p in self.model.parameters.items()}

        # Merge local reaction parameters into global parameter map
        # This fixes the Zake2021 issue where Km, V, k1, k2 are defined locally
        for rxn_id, rxn_data_dict in self.model_data.get("reactions", {}).items():
            local_params = rxn_data_dict.get("rxnParameters", [])
            for param_id, param_value in local_params:
                # Check for name collision
                if param_id in self.params_map:
                    # Use reaction-qualified name
                    qualified_name = f"{rxn_id}_{param_id}"
                    self.params_map[qualified_name] = param_value
                    print(f"Warning: Parameter '{param_id}' collision in reaction '{rxn_id}', using '{qualified_name}'")
                else:
                    self.params_map[param_id] = param_value


        self.compartments_map = {
            c_id: c.size for c_id, c in self.model.compartments.items()
        }

        # Create symbols
        self.sym_species = {s: sympy.Symbol(s) for s in self.species_list}
        self.sym_params = {p: sympy.Symbol(p) for p in self.params_map}
        self.sym_compartments = {c: sympy.Symbol(c) for c in self.compartments_map}

        # Setup components
        self._setup_components()

    def _setup_components(self):
        """Initialize all pipeline components"""
        # Create parsing context
        context = {}
        context.update(self.sym_species)
        context.update(self.sym_params)
        context.update(self.sym_compartments)
        context["time"] = sympy.Symbol("t")
        context["t"] = sympy.Symbol("t")

        # Get functions as dict
        functions_dict = {
            f_id: {"arguments": f.arguments, "mathString": f.math_string}
            for f_id, f in self.model.functions.items()
        }

        # Initialize components
        self.expression_parser = SbmlExpressionParser(context, functions_dict)
        self.assignment_processor = AssignmentRuleProcessor(self.expression_parser)
        self.ode_builder = OdeSystemBuilder(self.species_map, self.expression_parser)
        self.jacobian_builder = JacobianBuilder(self.sym_species, self.species_list)
        self.optimizer = SymbolicOptimizer(optimization_level=2)
        self.code_generator = RustBlockGenerator()
        self.event_generator = EventCodeGenerator(
            self.code_generator, self.expression_parser
        )
        self.template_manager = RustTemplateManager()

    def convert(self, model_name: str = "sbml_model", wasm: bool = True) -> str:
        """Main conversion method

        Args:
            model_name: Name for the generated Rust module
            wasm: If True, generate WASM-compatible code (browser). If False, generate native Rust code.

        Returns:
            Complete Rust source code as string
        """
        # 1. Process assignment rules
        print("Processing assignment rules...")
        assignment_rules = self.assignment_processor.process(self.model_data)
        print(f"Found {len(assignment_rules)} assignment rules")

        # 2. Build ODE system
        print("Building ODE system...")
        ode_system = self.ode_builder.build_ode_system(self.model_data["reactions"])

        # 3. Compute Jacobian
        jacobian_elements, jac_indices = self.jacobian_builder.compute_sparse_jacobian(
            ode_system
        )

        # 4. Optimize expressions (combined optimization)
        replacements, reduced_ode, reduced_jac = self.optimizer.optimize_combined(
            ode_system, jacobian_elements
        )

        # 5. Generate code blocks
        code_blocks = self._generate_code_blocks(
            replacements, reduced_ode, reduced_jac, jac_indices, assignment_rules, model_name, wasm
        )

        # 6. Assemble final Rust file
        return self.template_manager.assemble_rust_file(
            model_name, code_blocks, wasm=wasm
        )

    def _generate_code_blocks(
        self, replacements, reduced_ode, reduced_jac, jac_indices, assignment_rules, model_name, wasm
    ) -> Dict[str, str]:
        """Generate all code blocks needed for the template

        Args:
            replacements: CSE replacements
            reduced_ode: Reduced ODE expressions
            reduced_jac: Reduced Jacobian expressions
            jac_indices: Jacobian sparsity indices
            assignment_rules: List of (variable, expression) tuples for assignment rules

        Returns:
            Dictionary with all code block components
        """
        # Get set of assigned variables to exclude from struct
        assigned_vars = {var for var, _ in assignment_rules}

        # Also exclude variables with initial assignments
        initial_assignments = self.model_data.get("initialAssignments", {})
        initial_assigned_vars = {ia.get("variable") for ia in initial_assignments.values() if ia.get("variable")}
        all_assigned_vars = assigned_vars | initial_assigned_vars

        # Filter params and compartments to exclude assigned variables
        filtered_params = {
            k: v for k, v in self.params_map.items() if k not in all_assigned_vars
        }
        filtered_compartments = {
            k: v for k, v in self.compartments_map.items() if k not in all_assigned_vars
        }

        # Extract species initial amounts from model
        species_initial_amounts = {
            s_id: species.initial_amount
            for s_id, species in self.model.species.items()
        }

        # Generate struct fields (with initial amount options)
        species_fields, param_fields = self.template_manager.generate_struct_fields(
            self.species_list, filtered_params, filtered_compartments, species_initial_amounts
        )
        
        # Classify rules into static and dynamic
        # First, determine which variables are from initial assignments (these are static)
        # Classify initial assignments into static (param-only) and dynamic (rule-dependent)
        initial_assignments = self.model_data.get("initialAssignments", {})
        initial_assignment_rules = []
        for ia in initial_assignments.values():
            if ia.get("variable") and ia.get("math"):
                expr = self.expression_parser.parse(ia.get("math"))
                initial_assignment_rules.append((ia.get("variable"), expr))
        
        # We use a fresh analyzer for this, knowing only parameters are static initially
        from core.dependency_analyzer import DependencyAnalyzer
        # Only use filtered_params and filtered_compartments (constants), not all params (which include rules)
        constant_vars = list(filtered_params.keys()) + list(filtered_compartments.keys())
        
        ia_analyzer = DependencyAnalyzer(self.species_list, constant_vars)
        static_ia, dynamic_ia = ia_analyzer.classify_rules(initial_assignment_rules)
        
        # Initialize DependencyAnalyzer for assignment rules
        # Now we know which initial assignments are static (available for static rules)
        static_ia_vars = {var for var, _ in static_ia}
        dynamic_ia_vars = {var for var, _ in dynamic_ia}
        all_static_base = list(self.params_map.keys()) + list(static_ia_vars)
        dependency_analyzer = DependencyAnalyzer(self.species_list, all_static_base)
        
        # Pass dynamic_ia_vars so rules depending on them are classified as dynamic
        static_rules, dynamic_rules = dependency_analyzer.classify_rules(assignment_rules, dynamic_ia_vars)
        
        # Re-classify dynamic_ia based on whether they depend on assignment rules
        # Some dynamic IAs might depend on dynamic assignment rules
        assignment_rule_vars = {var for var, _ in assignment_rules}
        dynamic_ia_before_rules = []
        dynamic_ia_after_rules = []
        
        for var, expr in dynamic_ia:
            symbols = {str(s) for s in expr.free_symbols}
            # Check if depends on any assignment rule
            if symbols & assignment_rule_vars:
                dynamic_ia_after_rules.append((var, expr))
            else:
                dynamic_ia_before_rules.append((var, expr))

        # Generate code blocks
        code_blocks = {
            "species_fields": species_fields,
            "param_fields": param_fields,
            "param_extract": self.code_generator.generate_parameter_extraction(
                filtered_params, filtered_compartments
            ),
            "static_assignment_rules": self.code_generator.generate_assignment_rules(
                static_rules, add_type_annotation=True
            ),
            "assignment_rules": self.code_generator.generate_assignment_rules(
                dynamic_rules
            ),
            "initial_assignments_static": self.code_generator.generate_assignment_rules(
                static_ia
            ),
            "initial_assignments_dynamic_before": self.code_generator.generate_assignment_rules(
                dynamic_ia_before_rules
            ),
            "initial_assignments_dynamic_after": self.code_generator.generate_assignment_rules(
                dynamic_ia_after_rules
            ),
            "species_extract": self.code_generator.generate_species_extraction(
                self.species_map
            ),
            "temp_vars": self.code_generator.generate_temp_vars(replacements),
            "rhs_block": self.code_generator.generate_derivatives(reduced_ode),
            "jac_block": self.code_generator.generate_jacobian(
                reduced_jac, jac_indices
            ),
            "init_block": self.code_generator.generate_init_function(
                self.species_list, self.species_map, species_initial_amounts
            ),
            "result_vectors_init": self.code_generator.generate_result_vectors_init(
                self.species_list
            ),
            "initial_pushes": self.code_generator.generate_result_pushes(
                self.species_list, indent="    "
            ),
            "loop_pushes": self.code_generator.generate_result_pushes(
                self.species_list, indent="            "
            ),
            "map_inserts": self.code_generator.generate_hashmap_inserts(
                self.species_list
            ),
            "n_species": len(self.species_list),
            "gut_idx": self.species_map.get("QGut", 5),  # Default to 5 if not found
        }

        # Add metadata functions for UI/tools
        code_blocks["metadata_functions"] = self.code_generator.generate_metadata_functions(
            model_name,
            self.species_list,
            species_initial_amounts,
            filtered_params,
            filtered_compartments,
            wasm
        )

        # Add event handling if events exist
        events = self.model_data.get("events", {})
        if events:
            print(f"Generating event handling for {len(events)} events...")
            event_components = self.event_generator.generate_event_handling(
                events, self.species_map
            )
            code_blocks.update(event_components)

        return code_blocks

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model

        Returns:
            Dictionary with model statistics
        """
        return {
            "num_species": len(self.model.species),
            "num_parameters": len(self.model.parameters),
            "num_compartments": len(self.model.compartments),
            "num_reactions": len(self.model.reactions),
            "num_functions": len(self.model.functions),
            "species_list": self.species_list,
        }

    def validate_model(self) -> bool:
        """Validate the model

        Returns:
            True if model is valid
        """
        return self.model.validate()
