# File: sbml_rust_generator/parsers/expression_parser.py
"""Handles parsing of SBML mathematical expressions to SymPy"""

import re
import sympy
from typing import Dict, Any
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from ..core.base import Parser
from .function_inliner import FunctionInliner


class SbmlExpressionParser(Parser):
    """Handles parsing of SBML mathematical expressions to SymPy expressions"""

    def __init__(self, context: Dict[str, sympy.Symbol], functions: Dict[str, Any]):
        """Initialize the expression parser

        Args:
            context: Dictionary mapping identifier names to SymPy symbols
            functions: Dictionary of user-defined functions for inlining
        """
        self.context = context.copy()
        self.function_inliner = FunctionInliner(functions)
        self._setup_context()

    def _setup_context(self):
        """Setup parsing context with mathematical and logical functions"""
        # Standard Math Functions
        self.context["pow"] = lambda b, e: b**e
        self.context["sqrt"] = sympy.sqrt
        self.context["exp"] = sympy.exp
        self.context["log"] = sympy.log
        self.context["ln"] = sympy.log
        self.context["sin"] = sympy.sin
        self.context["cos"] = sympy.cos
        self.context["tan"] = sympy.tan
        self.context["abs"] = sympy.Abs

        # Logic / Comparison Mappings
        self.context["gt"] = sympy.Gt
        self.context["lt"] = sympy.Lt
        self.context["ge"] = sympy.Ge
        self.context["le"] = sympy.Le
        self.context["eq"] = sympy.Eq
        self.context["neq"] = sympy.Ne
        self.context["and"] = sympy.And
        self.context["or"] = sympy.Or

        # Helper for transformed piecewise
        self.context["sbml_piecewise"] = self._create_piecewise_function()

    def parse(self, expression: str) -> sympy.Expr:
        """Parse SBML expression to SymPy expression

        Args:
            expression: SBML mathematical expression string

        Returns:
            SymPy expression

        Raises:
            Exception: If parsing fails
        """
        if not expression or expression == "None":
            return sympy.Float(0.0)

        try:
            # 1. Clean Units
            expression = self._remove_units(expression)

            # 2. Inline Function Definitions
            expression = self.function_inliner.inline(expression)

            # 3. Handle Piecewise formatting for SymPy
            expression = self._transform_piecewise(expression)

            # 4. Parse with SymPy
            # Enable implicit multiplication (e.g., "k1 A" -> "k1 * A")
            transformations = standard_transformations + (
                implicit_multiplication_application,
            )

            return parse_expr(
                expression, local_dict=self.context, transformations=transformations
            )
        except Exception as e:
            print(f"Error parsing expression: {expression}")
            raise e

    def _remove_units(self, expr: str) -> str:
        """Remove unit annotations from expressions

        Args:
            expr: Expression string potentially containing units

        Returns:
            Expression with units removed
        """
        units = [
            "dimensionless",
            "litre",
            "liter",
            "mole",
            "gram",
            "second",
            "minute",
            "hour",
            "day",
            "kilogram",
            "milligram",
            "microgram",
            "millilitre",
            "milliliter",
            "nanomole",
            "picomole",
            "micromole",
            "millimole",
            "per_second",
            "per_minute",
            "per_hour",
        ]
        # Sort by length desc to avoid replacing substrings
        units.sort(key=len, reverse=True)

        for unit in units:
            expr = re.sub(rf"\b{unit}\b", "", expr, flags=re.IGNORECASE)

        return expr

    def _transform_piecewise(self, expr: str) -> str:
        """Transform SBML piecewise to SymPy format

        SBML format: piecewise(val1, cond1, val2, cond2, ..., default)
        SymPy format: Piecewise((val1, cond1), (val2, cond2), ..., (default, True))

        Args:
            expr: Expression string

        Returns:
            Transformed expression
        """
        if "piecewise" not in expr:
            return expr
        return expr.replace("piecewise", "sbml_piecewise")

    def _create_piecewise_function(self):
        """Create a function that converts SBML piecewise to SymPy Piecewise

        Returns:
            Callable that creates SymPy Piecewise expressions
        """
        def sbml_piecewise(*args):
            """Convert SBML piecewise arguments to SymPy Piecewise

            SBML: piecewise(val1, cond1, val2, cond2, default)
            SymPy: Piecewise((val1, cond1), (val2, cond2), (default, True))
            """
            pairs = []
            # Pair up values and conditions
            for i in range(0, len(args) - 1, 2):
                pairs.append((args[i], args[i + 1]))

            # If odd number of args, last one is default case
            if len(args) % 2 == 1:
                pairs.append((args[-1], True))

            return sympy.Piecewise(*pairs)

        return sbml_piecewise


class UnitsRemover:
    """Utility class for removing SBML units from expressions"""

    @staticmethod
    def remove(expression: str) -> str:
        """Remove SBML unit annotations

        Args:
            expression: Expression string

        Returns:
            Expression with units removed
        """
        parser = SbmlExpressionParser({}, {})
        return parser._remove_units(expression)
