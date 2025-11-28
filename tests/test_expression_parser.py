"""Tests for math expression parsing functionality"""

import pytest
import sympy
from parsers.expression_parser import SbmlExpressionParser


class TestSbmlExpressionParser:
    """Tests for SbmlExpressionParser class"""

    def test_parse_simple_arithmetic(self, expression_parser):
        """Test parsing simple arithmetic expressions"""
        expr = expression_parser.parse("x + y")
        assert isinstance(expr, sympy.Add)
        assert sympy.Symbol("x") in expr.free_symbols
        assert sympy.Symbol("y") in expr.free_symbols

    def test_parse_multiplication(self, expression_parser):
        """Test parsing multiplication expressions"""
        expr = expression_parser.parse("k1 * x")
        assert isinstance(expr, sympy.Mul)
        assert sympy.Symbol("k1") in expr.free_symbols
        assert sympy.Symbol("x") in expr.free_symbols

    def test_parse_division(self, expression_parser):
        """Test parsing division expressions"""
        expr = expression_parser.parse("x / y")
        assert isinstance(
            expr, sympy.Mul
        )  # Division is represented as multiplication with power -1
        # Check that it's equivalent to x/y
        assert expr == sympy.Symbol("x") / sympy.Symbol("y")

    def test_parse_power(self, expression_parser):
        """Test parsing power expressions"""
        expr = expression_parser.parse("x**2")
        assert isinstance(expr, sympy.Pow)
        assert expr.base == sympy.Symbol("x")
        assert expr.exp == 2

    def test_parse_mathematical_functions(self, expression_parser):
        """Test parsing mathematical functions"""
        # Test exp - exp(x) returns a Function with func == exp
        expr = expression_parser.parse("exp(x)")
        assert isinstance(expr, sympy.Function)
        assert expr.func == sympy.exp

        # Test log - log(x) returns a Function with func == log
        expr = expression_parser.parse("log(x)")
        assert isinstance(expr, sympy.Function)
        assert expr.func == sympy.log

        # Test sqrt - sqrt(x) is represented as Pow(x, 1/2) in SymPy
        expr = expression_parser.parse("sqrt(x)")
        assert isinstance(expr, sympy.Pow)
        assert expr.exp == sympy.Rational(1, 2) or expr.exp == 0.5

        # Test sin - sin(x) returns a Function with func == sin
        expr = expression_parser.parse("sin(x)")
        assert isinstance(expr, sympy.Function)
        assert expr.func == sympy.sin

    def test_parse_piecewise(self, expression_parser):
        """Test parsing piecewise expressions"""
        # SBML piecewise format: piecewise(val1, cond1, val2, cond2, default)
        expr_str = "piecewise(x, x > 0, -x, True)"
        expr = expression_parser.parse(expr_str)
        assert isinstance(expr, sympy.Piecewise)

    def test_parse_with_units_removal(self, expression_parser):
        """Test that units are removed from expressions"""
        expr = expression_parser.parse("x * second")
        # Units should be removed, so this should parse as just x
        assert sympy.Symbol("x") in expr.free_symbols
        # 'second' should not be in free symbols (it should be removed)
        assert sympy.Symbol("second") not in expr.free_symbols

    def test_parse_empty_expression(self, expression_parser):
        """Test parsing empty or None expressions"""
        expr = expression_parser.parse("")
        assert expr == sympy.Float(0.0)

        expr = expression_parser.parse("None")
        assert expr == sympy.Float(0.0)

    def test_parse_complex_expression(self, expression_parser):
        """Test parsing complex nested expressions"""
        expr_str = "k1 * exp(-k2 * t) * (x + y) / sqrt(z)"
        expr = expression_parser.parse(expr_str)

        # Verify all symbols are present
        assert sympy.Symbol("k1") in expr.free_symbols
        assert sympy.Symbol("k2") in expr.free_symbols
        assert sympy.Symbol("t") in expr.free_symbols
        assert sympy.Symbol("x") in expr.free_symbols
        assert sympy.Symbol("y") in expr.free_symbols
        assert sympy.Symbol("z") in expr.free_symbols

    def test_parse_implicit_multiplication(self, expression_parser):
        """Test parsing expressions with implicit multiplication"""
        # This should work: "k1 x" should be parsed as "k1 * x"
        expr = expression_parser.parse("k1 x")
        assert isinstance(expr, sympy.Mul)
        assert sympy.Symbol("k1") in expr.free_symbols
        assert sympy.Symbol("x") in expr.free_symbols

    def test_parse_logical_operators(self, expression_parser):
        """Test parsing logical and comparison operators"""
        # Test greater than
        expr = expression_parser.parse("gt(x, 0)")
        assert isinstance(expr, sympy.Gt)

        # Test less than
        expr = expression_parser.parse("lt(x, 10)")
        assert isinstance(expr, sympy.Lt)

        # Test and
        expr = expression_parser.parse("and(gt(x, 0), lt(x, 10))")
        assert isinstance(expr, sympy.And)

    def test_parse_with_custom_functions(self):
        """Test parsing expressions with custom function definitions"""
        context = {
            "x": sympy.Symbol("x"),
            "y": sympy.Symbol("y"),
        }
        functions = {"multiply": {"arguments": ["a", "b"], "mathString": "a * b"}}
        parser = SbmlExpressionParser(context, functions)

        # Parse expression using custom function
        expr = parser.parse("multiply(x, y)")
        # After inlining, this should be equivalent to x * y
        assert expr == sympy.Symbol("x") * sympy.Symbol("y")

    def test_parse_mathml_format(self):
        """Test parsing MathML format expressions"""
        context = {
            "x": sympy.Symbol("x"),
            "y": sympy.Symbol("y"),
        }
        parser = SbmlExpressionParser(context, {})

        # Simple MathML expression
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
                <plus/>
                <ci>x</ci>
                <ci>y</ci>
            </apply>
        </math>"""

        try:
            expr = parser.parse(mathml)
            assert isinstance(expr, sympy.Add)
            assert sympy.Symbol("x") in expr.free_symbols
            assert sympy.Symbol("y") in expr.free_symbols
        except Exception as e:
            # If sbmlmath is not available, this is expected
            if "sbmlmath required" in str(e) or "sbmlmath not available" in str(e):
                pytest.skip("sbmlmath not available for MathML parsing")
            else:
                raise

    def test_parse_nested_functions(self):
        """Test parsing nested function calls"""
        context = {
            "x": sympy.Symbol("x"),
        }
        functions = {
            "square": {"arguments": ["a"], "mathString": "a * a"},
            "double": {"arguments": ["a"], "mathString": "2 * a"},
        }
        parser = SbmlExpressionParser(context, functions)

        # Parse nested function: double(square(x))
        expr = parser.parse("double(square(x))")
        # Should be equivalent to 2 * (x * x)
        expected = 2 * sympy.Symbol("x") * sympy.Symbol("x")
        assert expr == expected

    def test_parse_rational_numbers(self, expression_parser):
        """Test parsing rational numbers"""
        expr = expression_parser.parse("1/2")
        # Should be parsed as a rational
        assert expr == sympy.Rational(1, 2)

    def test_parse_absolute_value(self, expression_parser):
        """Test parsing absolute value function"""
        expr = expression_parser.parse("abs(x)")
        assert isinstance(expr, sympy.Abs)

    def test_context_symbols_available(self, expression_parser):
        """Test that context symbols are available in parsed expressions"""
        expr = expression_parser.parse("k1 * x + k2 * y")

        # All symbols from context should be accessible
        assert sympy.Symbol("k1") in expr.free_symbols
        assert sympy.Symbol("k2") in expr.free_symbols
        assert sympy.Symbol("x") in expr.free_symbols
        assert sympy.Symbol("y") in expr.free_symbols

    def test_parse_time_symbol(self, expression_parser):
        """Test parsing time symbol"""
        expr = expression_parser.parse("t + 1")
        assert sympy.Symbol("t") in expr.free_symbols

        # Also test 'time' alias
        expr2 = expression_parser.parse("time * 2")
        assert sympy.Symbol("t") in expr2.free_symbols
