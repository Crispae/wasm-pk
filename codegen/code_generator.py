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
        assignment_rules: List[Tuple[str, sympy.Expr]]
    ) -> str:
        """Generate code for assignment rule calculations

        Args:
            assignment_rules: List of (variable, expression) tuples in dependency order

        Returns:
            Rust code block with assignment calculations

        Example:
            Input: [("Fat", BM * scVFat), ("VBlood", BM * scVBlood)]
            Output:
                let Fat = BM * scVFat;
                let VBlood = BM * scVBlood;
        """
        if not assignment_rules:
            return ""

        assignment_code = []
        for variable, expr in assignment_rules:
            rust_expr = self.code_gen.generate_code_with_formatting(expr)
            assignment_code.append(f"    let {variable} = {rust_expr};")

        return "\n".join(assignment_code)
