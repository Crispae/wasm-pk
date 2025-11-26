# File: sbml_rust_generator/codegen/rust_printer.py
"""Custom Rust code printer for SymPy expressions"""

import re
import sympy
from sympy.printing.rust import RustCodePrinter
from ..core.base import CodeGenerator


class CustomRustCodePrinter(RustCodePrinter):
    """Custom Rust code printer that handles Piecewise and ensures float literals"""

    def _print_Pow(self, expr):
        """Handle power operations correctly for Rust

        Uses .powi() for integer exponents and .powf() for float exponents
        Guards against division by zero for negative exponents

        Args:
            expr: SymPy Pow expression

        Returns:
            Rust code string for power operation
        """
        base = self._print(expr.base)
        exp = expr.exp

        # Check if base needs parentheses (for Add, Mul, etc.)
        # This ensures correct operator precedence in Rust
        needs_parens = isinstance(expr.base, (sympy.Add, sympy.Mul))
        if needs_parens and not base.startswith('('):
            base = f"({base})"

        # Check if exponent is an integer
        if exp.is_integer:
            # Use powi with integer literal
            if exp.is_number:
                exp_val = int(exp)
                # Guard against division by zero for negative exponents
                # when the base could be zero (contains Piecewise)
                if exp_val < 0 and expr.base.has(sympy.Piecewise):
                    # Generate safe division
                    return f"(if {base} != 0.0 {{ {base}.powi({exp_val}) }} else {{ f64::INFINITY }})"
                return f"{base}.powi({exp_val})"
            else:
                # If it's a symbol that represents an integer, cast it
                return f"{base}.powi({self._print(exp)} as i32)"
        else:
            # Use powf for non-integer exponents
            exp_str = self._print(exp)
            # Ensure float literal
            if re.match(r"^-?\d+$", exp_str):
                exp_str = exp_str + ".0"
            return f"{base}.powf({exp_str})"

    def _print_Piecewise(self, expr):
        """Print a Piecewise expression as nested if-else blocks

        Args:
            expr: SymPy Piecewise expression

        Returns:
            Rust if-else chain as string
        """
        lines = []
        for i, (e, c) in enumerate(expr.args):
            if i == 0:
                # Remove parentheses around condition
                cond_str = self._print(c)
                lines.append("if %s {" % cond_str)
            elif i == len(expr.args) - 1 and c == True:
                lines.append("} else {")
            else:
                cond_str = self._print(c)
                lines.append("} else if %s {" % cond_str)

            # Ensure the expression is printed correctly
            e_str = self._print(e)
            # If it's just an integer literal, make it a float
            if re.match(r"^-?\d+$", e_str):
                e_str = e_str + ".0"
            lines.append("    %s" % e_str)

        lines.append("}")
        return "\n".join(lines)

    def _print_Integer(self, expr):
        """Always print integers as floats in our context

        Args:
            expr: SymPy Integer

        Returns:
            Float literal string
        """
        return str(expr) + ".0"

    def _print_int(self, expr):
        """Always print Python ints as floats

        Args:
            expr: Python int

        Returns:
            Float literal string
        """
        return str(expr) + ".0"

    def _print_Zero(self, expr):
        """Print Zero as 0.0

        Args:
            expr: SymPy Zero

        Returns:
            "0.0"
        """
        return "0.0"

    def _print_Rational(self, expr):
        """Print rational numbers as float division

        Args:
            expr: SymPy Rational

        Returns:
            Rust division expression
        """
        return f"{float(expr.p)}/{float(expr.q)}"


class RustCodeGenerator(CodeGenerator):
    """Generates Rust code from SymPy expressions"""

    def __init__(self):
        """Initialize the Rust code generator with custom printer"""
        self.printer = CustomRustCodePrinter()

    def generate(self, expression) -> str:
        """Generate Rust code from SymPy expression

        Args:
            expression: SymPy expression to convert

        Returns:
            Rust code string
        """
        return self.printer.doprint(expression)

    def generate_code_with_formatting(self, expression) -> str:
        """Generate Rust code and handle multiline formatting

        Args:
            expression: SymPy expression to convert

        Returns:
            Formatted Rust code string
        """
        rust_expr = self.generate(expression)

        # Clean up - ensure multiline if statements are properly formatted
        if "\n" in rust_expr:
            # For multiline (Piecewise), indent properly
            lines = rust_expr.split("\n")
            rust_expr = lines[0]
            for line in lines[1:]:
                rust_expr += "\n        " + line

        return rust_expr


def custom_rust_code(expr):
    """Generate Rust code using our custom printer

    Convenience function for backward compatibility

    Args:
        expr: SymPy expression

    Returns:
        Rust code string
    """
    generator = RustCodeGenerator()
    return generator.generate(expr)
