# File: sbml_rust_generator/codegen/code_generator.py
"""Generates Rust code blocks from symbolic expressions"""

from typing import List, Tuple, Dict
import sympy
from codegen.rust_printer import RustCodeGenerator


class RustBlockGenerator:
    """Generates Rust code blocks for ODE solver"""

    def __init__(self):
        """Initialize code block generator"""
        self.code_gen = RustCodeGenerator()
    
    def generate(self, expr: sympy.Expr) -> str:
        """Generate Rust code from SymPy expression
        
        This is a convenience method used by event generator and other components.
        
        Args:
            expr: SymPy expression to convert to Rust
            
        Returns:
            Rust code string
        """
        return self.code_gen.generate(expr)


    def generate_temp_vars(self, replacements: List[Tuple[sympy.Symbol, sympy.Expr]]) -> str:
        """Generate temporary variable declarations from CSE

        Args:
            replacements: List of (symbol, expression) pairs from CSE

        Returns:
            Rust code block with let statements

        Example:
            Input: [(x0, a*b), (x1, x0 + c)]
            Output:
                let x0 = a * b;
                let x1 = x0 + c;
        """
        temp_vars_code = []

        for sym, expr in replacements:
            rust_expr = self.code_gen.generate_code_with_formatting(expr)
            temp_vars_code.append(f"        let {sym} = {rust_expr};")

        return "\n".join(temp_vars_code)

    def generate_derivatives(self, expressions: List[sympy.Expr]) -> str:
        """Generate derivative calculations (dy[i] = ...)

        Args:
            expressions: List of dy/dt expressions

        Returns:
            Rust code block with dy assignments
        """
        rhs_code = []

        for i, expr in enumerate(expressions):
            rust_expr = self.code_gen.generate(expr)
            rhs_code.append(f"        dy[{i}] = {rust_expr};")

        return "\n".join(rhs_code)

    def generate_jacobian(
        self,
        jac_elements: List[sympy.Expr],
        indices: List[Tuple[int, int]]
    ) -> str:
        """Generate Jacobian-vector product (jv[i] += J[i,j] * v[j])

        Args:
            jac_elements: List of non-zero Jacobian elements
            indices: List of (row, col) indices for each element

        Returns:
            Rust code block with jv calculations
        """
        jac_code = []

        for k, (row, col) in enumerate(indices):
            expr = jac_elements[k]
            term = self.code_gen.generate(expr)
            jac_code.append(f"        jv[{row}] += ({term}) * v[{col}];")

        return "\n".join(jac_code)

    def generate_species_extraction(
        self,
        species_map: Dict[str, int]
    ) -> str:
        """Generate code to extract species from y vector

        Args:
            species_map: Dictionary mapping species IDs to indices

        Returns:
            Rust code block with let statements

        Example:
            let A = y[0];
            let B = y[1];
        """
        species_extract = []

        for s_id, idx in species_map.items():
            species_extract.append(f"        let {s_id} = y[{idx}];")

        return "\n".join(species_extract)

    def generate_parameter_extraction(
        self,
        params: Dict[str, float],
        compartments: Dict[str, float]
    ) -> str:
        """Generate code to extract parameters from struct

        Args:
            params: Dictionary of parameters
            compartments: Dictionary of compartments

        Returns:
            Rust code block with parameter extraction
        """
        param_extract = []

        for p in params:
            param_extract.append(f"    let {p} = sim_params.{p};")

        for c in compartments:
            if c not in params:  # Avoid duplicates
                param_extract.append(f"    let {c} = sim_params.{c};")

        return "\n".join(param_extract)

    def generate_result_vectors_init(self, species_list: List[str]) -> str:
        """Generate initialization of result vectors

        Args:
            species_list: List of species IDs

        Returns:
            Rust code block initializing Vec::new() for each species
        """
        from utils.validators import IdentifierValidator

        init_code = []
        for species_id in species_list:
            rust_id = IdentifierValidator.to_rust_identifier(species_id)
            init_code.append(f"    let mut {rust_id} = Vec::new();")

        return "\n".join(init_code)

    def generate_result_pushes(
        self,
        species_list: List[str],
        indent: str = "    "
    ) -> str:
        """Generate code to push current state to result vectors

        Args:
            species_list: List of species IDs
            indent: Indentation string

        Returns:
            Rust code block with push statements
        """
        from utils.validators import IdentifierValidator

        pushes = []
        for i, species_id in enumerate(species_list):
            rust_id = IdentifierValidator.to_rust_identifier(species_id)
            pushes.append(f"{indent}{rust_id}.push(solver.state().y[{i}]);")

        return "\n".join(pushes)

    def generate_hashmap_inserts(self, species_list: List[str]) -> str:
        """Generate code to insert species vectors into HashMap

        Args:
            species_list: List of species IDs

        Returns:
            Rust code block with HashMap insert statements
        """
        from utils.validators import IdentifierValidator

        map_inserts = []
        for species_id in species_list:
            rust_id = IdentifierValidator.to_rust_identifier(species_id)
            map_inserts.append(
                f'        species_map.insert("{rust_id}".to_string(), {rust_id});'
            )

        return "\n".join(map_inserts)

    def generate_initial_assignments(
        self,
        initial_assignments: Dict[str, any],
        expression_parser
    ) -> str:
        """Generate code for initial assignments

        Args:
            initial_assignments: Dictionary of initial assignment data from SBML
            expression_parser: Expression parser to convert MathML to SymPy

        Returns:
            Rust code block with initial assignment calculations
        """
        if not initial_assignments:
            return ""

        init_code = []
        for assignment_id, assignment in initial_assignments.items():
            variable = assignment.get("variable")
            math_ml = assignment.get("math")

            if not variable or not math_ml:
                continue

            # Parse MathML to SymPy expression
            try:
                expr = expression_parser.parse(math_ml)
                # Generate Rust code from expression
                rust_expr = self.code_gen.generate(expr)
                init_code.append(f"    let {variable} = {rust_expr};")
            except Exception as e:
                print(f"Warning: Could not parse initial assignment for {variable}: {e}")
                continue

        return "\n".join(init_code)

    def generate_assignment_rules(
        self,
        assignment_rules: List[Tuple[str, sympy.Expr]],
        add_type_annotation: bool = False
    ) -> str:
        """Generate code for assignment rule calculations

        Args:
            assignment_rules: List of (variable, expression) tuples in dependency order
            add_type_annotation: If True, add `: f64` type annotation (for static rules)

        Returns:
            Rust code block with assignment calculations

        Example:
            Input: [("Fat", BM * scVFat), ("VBlood", BM * scVBlood)]
            Output:
                let Fat: f64 = BM * scVFat;
                let VBlood: f64 = BM * scVBlood;
        """
        if not assignment_rules:
            return ""

        assignment_code = []
        for variable, expr in assignment_rules:
            rust_expr = self.code_gen.generate_code_with_formatting(expr)
            if add_type_annotation:
                assignment_code.append(f"    let {variable}: f64 = {rust_expr};")
            else:
                assignment_code.append(f"    let {variable} = {rust_expr};")

        return "\n".join(assignment_code)

    def generate_init_function(
        self,
        species_list: List[str],
        species_map: Dict[str, int],
        initial_amounts: Dict[str, float]
    ) -> str:
        """Generate init function with species initial values

        Args:
            species_list: List of species IDs
            species_map: Dictionary mapping species IDs to indices
            initial_amounts: Dictionary of species initial amounts from SBML

        Returns:
            Rust code block for init function

        Example:
            let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {
                y[0] = sim_params.init_QFat.unwrap_or(0.0);
                y[1] = sim_params.init_QGut.unwrap_or(1.0);
                ...
            };
        """
        init_code = []
        init_code.append("    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {")

        for species_id in species_list:
            idx = species_map[species_id]
            default_value = initial_amounts.get(species_id, 0.0)
            init_code.append(f"        y[{idx}] = sim_params.init_{species_id}.unwrap_or({default_value});")

        init_code.append("    };\n")

        return "\n".join(init_code)

    def generate_metadata_functions(
        self,
        model_name: str,
        species_list: List[str],
        species_initial_amounts: Dict[str, float],
        params: Dict[str, float],
        compartments: Dict[str, float],
        wasm: bool = False
    ) -> str:
        """Generate metadata exposure functions for UI/tools

        Args:
            model_name: Name of the model
            species_list: List of species IDs
            species_initial_amounts: Initial amounts from SBML
            params: Dictionary of parameters
            compartments: Dictionary of compartments
            wasm: If True, add wasm_bindgen attribute

        Returns:
            Rust code block with metadata functions
        """
        code = []

        # Add decorator for WASM
        decorator = "#[wasm_bindgen]\n" if wasm else ""

        # get_model_metadata function
        code.append(f"{decorator}pub fn get_model_metadata() -> String {{")
        code.append('    let metadata = serde_json::json!({')
        code.append(f'        "model_id": "{model_name}",')
        code.append(f'        "num_species": {len(species_list)},')
        code.append(f'        "num_parameters": {len(params) + len(compartments)},')
        code.append('        "time_units": "HR",')
        code.append('        "substance_units": "MilliMOL",')
        code.append('        "volume_units": "L"')
        code.append('    });')
        code.append('    serde_json::to_string(&metadata).unwrap()')
        code.append('}\n')

        # get_parameters_info function
        code.append(f"{decorator}pub fn get_parameters_info() -> String {{")
        code.append('    let params = serde_json::json!([')

        for param_id, param_value in params.items():
            # Handle None values
            value_str = 'null' if param_value is None else str(param_value)
            code.append('        {')
            code.append(f'            "id": "{param_id}",')
            code.append(f'            "default_value": {value_str},')
            code.append('            "required": true')
            code.append('        },')

        for comp_id, comp_value in compartments.items():
            # Handle None values
            value_str = 'null' if comp_value is None else str(comp_value)
            code.append('        {')
            code.append(f'            "id": "{comp_id}",')
            code.append(f'            "default_value": {value_str},')
            code.append('            "required": true')
            code.append('        },')

        if code[-1].endswith(','):
            code[-1] = code[-1][:-1]  # Remove trailing comma

        code.append('    ]);')
        code.append('    serde_json::to_string(&params).unwrap()')
        code.append('}\n')

        # get_species_info function
        code.append(f"{decorator}pub fn get_species_info() -> String {{")
        code.append('    let species = serde_json::json!([')

        for species_id in species_list:
            init_amount = species_initial_amounts.get(species_id, 0.0)
            code.append('        {')
            code.append(f'            "id": "{species_id}",')
            code.append(f'            "initial_amount": {init_amount},')
            code.append('            "units": "MilliMOL"')
            code.append('        },')

        if code[-1].endswith(','):
            code[-1] = code[-1][:-1]  # Remove trailing comma

        code.append('    ]);')
        code.append('    serde_json::to_string(&species).unwrap()')
        code.append('}\n')

        # get_default_parameters function
        code.append(f"{decorator}pub fn get_default_parameters() -> String {{")
        code.append('    let defaults = serde_json::json!({')

        for param_id, param_value in params.items():
            # Handle None values
            value_str = 'null' if param_value is None else str(param_value)
            code.append(f'        "{param_id}": {value_str},')

        for comp_id, comp_value in compartments.items():
            # Handle None values
            value_str = 'null' if comp_value is None else str(comp_value)
            code.append(f'        "{comp_id}": {value_str},')

        code.append('        "final_time": 24.0')
        code.append('    });')
        code.append('    serde_json::to_string(&defaults).unwrap()')
        code.append('}\n')

        return "\n".join(code)
