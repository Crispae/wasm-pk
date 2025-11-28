# File: sbml_rust_generator/facade.py
"""Main facade class for SBML to Rust conversion"""

import sympy
from typing import Dict, Any
from .models.sbml_model import SbmlModel
from .parsers.expression_parser import SbmlExpressionParser
from .symbolic.ode_builder import OdeSystemBuilder
from .symbolic.jacobian_builder import JacobianBuilder
from .symbolic.optimizer import SymbolicOptimizer
from .symbolic.assignment_processor import AssignmentRuleProcessor
from .codegen.code_generator import RustBlockGenerator
from .codegen.template_manager import RustTemplateManager
from .codegen.event_generator import EventCodeGenerator


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
        self.species_map = {
            s_id: i for i, s_id in enumerate(self.model.species.keys())
        }
        self.species_list = list(self.model.species.keys())

        self.params_map = {
            p_id: p.value for p_id, p in self.model.parameters.items()
        }

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
            f_id: {
                "arguments": f.arguments,
                "mathString": f.math_string
            }
            for f_id, f in self.model.functions.items()
        }

        # Initialize components
        self.expression_parser = SbmlExpressionParser(context, functions_dict)
        self.assignment_processor = AssignmentRuleProcessor(self.expression_parser)
        self.ode_builder = OdeSystemBuilder(self.species_map, self.expression_parser)
        self.jacobian_builder = JacobianBuilder(self.sym_species, self.species_list)
        self.optimizer = SymbolicOptimizer(optimization_level=2)
        self.code_generator = RustBlockGenerator()
        self.event_generator = EventCodeGenerator(self.code_generator, self.expression_parser)
        self.template_manager = RustTemplateManager()

    def convert(self, model_name: str = "sbml_model") -> str:
        """Main conversion method

        Args:
            model_name: Name for the generated Rust module

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
            replacements, reduced_ode, reduced_jac, jac_indices, assignment_rules
        )

        # 6. Assemble final Rust file
        return self.template_manager.assemble_rust_file(model_name, code_blocks)

    def _generate_code_blocks(
        self,
        replacements,
        reduced_ode,
        reduced_jac,
        jac_indices,
        assignment_rules
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
        
        # Filter params and compartments to exclude assigned variables
        filtered_params = {k: v for k, v in self.params_map.items() if k not in assigned_vars}
        filtered_compartments = {k: v for k, v in self.compartments_map.items() if k not in assigned_vars}
        
        # Generate struct fields
        species_fields, param_fields = self.template_manager.generate_struct_fields(
            self.species_list, filtered_params, filtered_compartments
        )

        # Generate code blocks
        code_blocks = {
            "species_fields": species_fields,
            "param_fields": param_fields,
            "param_extract": self.code_generator.generate_parameter_extraction(
                filtered_params, filtered_compartments
            ),
            "assignment_rules": self.code_generator.generate_assignment_rules(
                assignment_rules
            ),
            "species_extract": self.code_generator.generate_species_extraction(
                self.species_map
            ),
            "temp_vars": self.code_generator.generate_temp_vars(replacements),
            "rhs_block": self.code_generator.generate_derivatives(reduced_ode),
            "jac_block": self.code_generator.generate_jacobian(reduced_jac, jac_indices),
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
        
        # Add event handling if events exist
        events = self.model_data.get("events", {})
        if events:
            print(f"Generating event handling for {len(events)} events...")
            event_components = self.event_generator.generate_event_handling(events, self.species_map)
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
