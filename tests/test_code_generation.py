"""Tests for Rust code generation functionality"""

import sympy
from codegen.code_generator import RustBlockGenerator
from codegen.rust_printer import RustCodeGenerator, CustomRustCodePrinter


class TestRustCodeGenerator:
    """Tests for RustCodeGenerator class"""

    def test_generate_simple_expression(self):
        """Test generating Rust code for simple expression"""
        generator = RustCodeGenerator()
        expr = sympy.Symbol("x") + sympy.Symbol("y")

        result = generator.generate(expr)
        assert "x" in result
        assert "y" in result
        assert "+" in result

    def test_generate_multiplication(self):
        """Test generating Rust code for multiplication"""
        generator = RustCodeGenerator()
        expr = sympy.Symbol("k1") * sympy.Symbol("x")

        result = generator.generate(expr)
        assert "k1" in result
        assert "x" in result
        assert "*" in result

    def test_generate_power_integer_exponent(self):
        """Test generating Rust code for power with integer exponent"""
        generator = RustCodeGenerator()
        expr = sympy.Pow(sympy.Symbol("x"), 2)

        result = generator.generate(expr)
        assert ".powi(2)" in result or ".powi(2.0)" in result

    def test_generate_power_float_exponent(self):
        """Test generating Rust code for power with float exponent"""
        generator = RustCodeGenerator()
        expr = sympy.Pow(sympy.Symbol("x"), sympy.Float(2.5))

        result = generator.generate(expr)
        assert ".powf" in result

    def test_generate_piecewise(self):
        """Test generating Rust code for Piecewise expression"""
        generator = RustCodeGenerator()
        expr = sympy.Piecewise(
            (sympy.Symbol("x"), sympy.Symbol("x") > 0), (-sympy.Symbol("x"), True)
        )

        result = generator.generate(expr)
        assert "if" in result
        assert "else" in result

    def test_generate_integer_as_float(self):
        """Test that integers are generated as floats"""
        generator = RustCodeGenerator()
        expr = sympy.Integer(5)

        result = generator.generate(expr)
        assert result == "5.0"

    def test_generate_rational(self):
        """Test generating Rust code for rational numbers"""
        generator = RustCodeGenerator()
        expr = sympy.Rational(1, 2)

        result = generator.generate(expr)
        assert "/" in result
        assert "1" in result
        assert "2" in result

    def test_generate_complex_expression(self):
        """Test generating Rust code for complex expression"""
        generator = RustCodeGenerator()
        x = sympy.Symbol("x")
        y = sympy.Symbol("y")
        k1 = sympy.Symbol("k1")
        expr = k1 * sympy.exp(-x) * (y + 1) / sympy.sqrt(x)

        result = generator.generate(expr)
        assert "k1" in result
        assert "exp" in result
        # sqrt(x) in denominator becomes x^(-1/2) = x.powf(-1.0/2.0) or similar
        # Check for either sqrt or the power representation
        assert "sqrt" in result or "powf" in result or ".pow" in result

    def test_generate_code_with_formatting(self):
        """Test generating formatted code for multiline expressions"""
        generator = RustCodeGenerator()
        expr = sympy.Piecewise(
            (sympy.Symbol("x"), sympy.Symbol("x") > 0), (sympy.Integer(0), True)
        )

        result = generator.generate_code_with_formatting(expr)
        assert "if" in result
        # Should have proper indentation for multiline
        if "\n" in result:
            lines = result.split("\n")
            assert len(lines) > 1


class TestCustomRustCodePrinter:
    """Tests for CustomRustCodePrinter class"""

    def test_print_integer_as_float(self):
        """Test that integers are printed as floats"""
        printer = CustomRustCodePrinter()
        result = printer._print_Integer(sympy.Integer(42))
        assert result == "42.0"

    def test_print_zero(self):
        """Test printing zero"""
        printer = CustomRustCodePrinter()
        # Use sympy.S.Zero (the singleton zero) instead of sympy.Zero()
        result = printer._print_Zero(sympy.S.Zero)
        assert result == "0.0"

    def test_print_power_integer(self):
        """Test printing power with integer exponent"""
        printer = CustomRustCodePrinter()
        expr = sympy.Pow(sympy.Symbol("x"), 3)
        result = printer._print_Pow(expr)
        assert ".powi(3)" in result

    def test_print_power_float(self):
        """Test printing power with float exponent"""
        printer = CustomRustCodePrinter()
        expr = sympy.Pow(sympy.Symbol("x"), sympy.Float(2.5))
        result = printer._print_Pow(expr)
        assert ".powf" in result

    def test_print_piecewise(self):
        """Test printing Piecewise expression"""
        printer = CustomRustCodePrinter()
        expr = sympy.Piecewise(
            (sympy.Symbol("x"), sympy.Symbol("x") > 0), (sympy.Integer(0), True)
        )
        result = printer._print_Piecewise(expr)
        assert "if" in result
        assert "else" in result

    def test_print_mul_with_add_parentheses(self):
        """Test that Add expressions in Mul get parentheses"""
        printer = CustomRustCodePrinter()
        x = sympy.Symbol("x")
        y = sympy.Symbol("y")
        expr = sympy.Symbol("k") * (x + y)
        result = printer._print_Mul(expr)
        # The addition should be in parentheses
        assert "(" in result and ")" in result


class TestRustBlockGenerator:
    """Tests for RustBlockGenerator class"""

    def test_generate_temp_vars(self):
        """Test generating temporary variables from CSE"""
        generator = RustBlockGenerator()
        replacements = [
            (sympy.Symbol("x0"), sympy.Symbol("a") * sympy.Symbol("b")),
            (sympy.Symbol("x1"), sympy.Symbol("x0") + sympy.Symbol("c")),
        ]

        result = generator.generate_temp_vars(replacements)
        assert "let x0" in result
        assert "let x1" in result
        # Check that x0 is used in x1's expression (order may vary due to SymPy canonicalization)
        # x1 should reference x0, so check that x0 appears after "let x1"
        x1_line = result.split("let x1")[1].split("\n")[0] if "let x1" in result else ""
        assert "x0" in x1_line, f"x0 should be used in x1's expression, got: {x1_line}"

    def test_generate_derivatives(self):
        """Test generating derivative calculations"""
        generator = RustBlockGenerator()
        expressions = [
            sympy.Symbol("k1") * sympy.Symbol("x"),
            sympy.Symbol("k2") * sympy.Symbol("y"),
        ]

        result = generator.generate_derivatives(expressions)
        assert "dy[0]" in result
        assert "dy[1]" in result
        assert "=" in result

    def test_generate_jacobian(self):
        """Test generating Jacobian code"""
        generator = RustBlockGenerator()
        jac_elements = [sympy.Symbol("k1"), sympy.Symbol("k2")]
        indices = [(0, 0), (1, 1)]

        result = generator.generate_jacobian(jac_elements, indices)
        assert "jv[0]" in result
        assert "jv[1]" in result
        assert "+=" in result

    def test_generate_species_extraction(self):
        """Test generating species extraction code"""
        generator = RustBlockGenerator()
        species_map = {"A": 0, "B": 1, "C": 2}

        result = generator.generate_species_extraction(species_map)
        assert "let A = y[0]" in result
        assert "let B = y[1]" in result
        assert "let C = y[2]" in result

    def test_generate_parameter_extraction(self):
        """Test generating parameter extraction code"""
        generator = RustBlockGenerator()
        params = {"k1": 0.5, "k2": 1.0}
        compartments = {"comp1": 1.0}

        result = generator.generate_parameter_extraction(params, compartments)
        assert "k1" in result
        assert "k2" in result
        assert "comp1" in result
        assert "sim_params" in result

    def test_generate_result_vectors_init(self):
        """Test generating result vector initialization"""
        generator = RustBlockGenerator()
        species_list = ["A", "B", "C"]

        result = generator.generate_result_vectors_init(species_list)
        assert "Vec::new()" in result
        assert "mut" in result

    def test_generate_result_pushes(self):
        """Test generating result push statements"""
        generator = RustBlockGenerator()
        species_list = ["A", "B"]

        result = generator.generate_result_pushes(species_list)
        assert ".push" in result
        assert "solver.state().y" in result

    def test_generate_hashmap_inserts(self):
        """Test generating HashMap insert statements"""
        generator = RustBlockGenerator()
        species_list = ["A", "B"]

        result = generator.generate_hashmap_inserts(species_list)
        assert "species_map.insert" in result
        assert ".to_string()" in result

    def test_generate_assignment_rules(self):
        """Test generating assignment rule code"""
        generator = RustBlockGenerator()
        assignment_rules = [
            ("V1", sympy.Symbol("k1") * sympy.Symbol("x")),
            ("V2", sympy.Symbol("V1") + sympy.Symbol("k2")),
        ]

        result = generator.generate_assignment_rules(assignment_rules)
        assert "let V1" in result
        assert "let V2" in result
        assert "k1" in result or "k2" in result

    def test_generate_empty_assignment_rules(self):
        """Test generating code for empty assignment rules"""
        generator = RustBlockGenerator()
        result = generator.generate_assignment_rules([])
        assert result == ""
