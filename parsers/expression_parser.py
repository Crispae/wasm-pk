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
from core.base import Parser
from parsers.function_inliner import FunctionInliner

# Try to import sbmlmath, fallback to formula string parsing if not available
try:
    from sbmlmath import SBMLMathMLParser

    SBMLMATH_AVAILABLE = True
except ImportError:
    SBMLMATH_AVAILABLE = False
    print("Warning: sbmlmath not installed. Using fallback formula string parsing.")


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
        self.functions = functions  # Store for custom function expansion

        # Initialize sbmlmath parser if available
        if SBMLMATH_AVAILABLE:
            self.mathml_parser = SBMLMathMLParser(evaluate=False)
        else:
            self.mathml_parser = None

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
        # Note: 'and' and 'or' are Python keywords, so we use 'And' and 'Or' in context
        # The _transform_logical_keywords method converts 'and(...)' to 'And(...)'
        self.context["And"] = sympy.And
        self.context["Or"] = sympy.Or

        # Helper for transformed piecewise
        self.context["sbml_piecewise"] = self._create_piecewise_function()

    def parse(self, expression: str) -> sympy.Expr:
        """Parse SBML expression to SymPy expression

        Supports both MathML (preferred) and formula string formats.
        If sbmlmath is available, MathML will be parsed directly for better
        accuracy and operator precedence handling.

        Args:
            expression: SBML mathematical expression (MathML or formula string)

        Returns:
            SymPy expression

        Raises:
            Exception: If parsing fails
        """
        if not expression or expression == "None":
            return sympy.Float(0.0)

        try:
            # Detect format and use appropriate parser
            if self._is_mathml(expression):
                return self._parse_mathml(expression)
            else:
                return self._parse_formula_string(expression)
        except Exception as e:
            print(f"Error parsing expression: {expression[:100]}...")
            raise e

    def _is_mathml(self, expression: str) -> bool:
        """Check if expression is MathML format

        Args:
            expression: Expression string

        Returns:
            True if expression appears to be MathML
        """
        stripped = expression.strip()
        return stripped.startswith(("<?xml", "<math", "<apply", "<ci", "<cn"))

    def _parse_mathml(self, mathml: str) -> sympy.Expr:
        """Parse MathML using sbmlmath (if available)

        Args:
            mathml: MathML expression string

        Returns:
            SymPy expression

        Raises:
            Exception: If sbmlmath not available or parsing fails
        """
        if not SBMLMATH_AVAILABLE or self.mathml_parser is None:
            # Fallback: try to extract formula string and parse that
            print("Warning: sbmlmath not available, cannot parse MathML directly")
            raise Exception("sbmlmath required for MathML parsing")

        # Preprocess MathML to remove problematic attributes
        # sbmlmath uses pint for unit parsing, which doesn't recognize SBML custom units
        # and can cause recursion errors. We strip these attributes and warn the user.
        cleaned_mathml, removed_units = self._preprocess_mathml_for_sbmlmath(mathml)

        if removed_units:
            unit_list = ", ".join(sorted(set(removed_units)))
            print(
                f"Warning: Removed sbml:units attributes ({unit_list}) from MathML. "
                f"These SBML unit definitions are not parseable by pint (used by sbmlmath) "
                f"and are not needed for mathematical expression parsing."
            )

        # Parse with sbmlmath
        expr = self.mathml_parser.parse_str(cleaned_mathml)

        # Replace SBML-specific symbols with our context symbols
        expr = self._replace_sbml_symbols(expr)

        # Inline any custom SBML functions
        expr = self._inline_custom_functions(expr)

        return expr

    def _preprocess_mathml_for_sbmlmath(self, mathml: str) -> tuple[str, list[str]]:
        """Preprocess MathML to remove attributes that cause issues with sbmlmath

        sbmlmath uses pint library for unit parsing, which doesn't recognize SBML
        custom unit definitions (like "l_per_kg", "s_per_min") and can cause
        recursion errors. This function removes these problematic attributes.

        Args:
            mathml: Raw MathML string from libsbml.writeMathMLToString()

        Returns:
            Tuple of (cleaned_mathml, removed_units_list)
            - cleaned_mathml: MathML with problematic attributes removed
            - removed_units_list: List of unit names that were removed
        """
        import re

        removed_units = []

        # Remove XML declaration if present (sbmlmath doesn't need it)
        cleaned = re.sub(r"<\?xml[^>]*\?>", "", mathml, flags=re.IGNORECASE)

        # Find and remove sbml:units attributes from <cn> elements
        # Pattern: <cn sbml:units="unit_name"> -> <cn>
        # We capture the unit name for warning purposes
        def remove_units_attr(match):
            full_tag = match.group(0)
            # Extract unit name if present
            unit_match = re.search(r'sbml:units=["\']([^"\']+)["\']', full_tag)
            if unit_match:
                removed_units.append(unit_match.group(1))
            # Return tag without attributes
            return "<cn>"

        # Remove all attributes from <cn> elements (including sbml:units and type)
        # This is safe because these are metadata attributes, not needed for parsing
        cleaned = re.sub(r"<cn\s+[^>]*>", remove_units_attr, cleaned)

        # Clean up extra whitespace (but preserve structure)
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.strip()

        return cleaned, removed_units

    def _replace_sbml_symbols(self, expr: sympy.Expr) -> sympy.Expr:
        """Replace SBML-specific symbols (TimeSymbol, etc.) with standard symbols

        Args:
            expr: SymPy expression from sbmlmath

        Returns:
            SymPy expression with replaced symbols
        """
        # Replace TimeSymbol with 't'
        time_symbols = [
            s
            for s in expr.atoms(sympy.Dummy)
            if hasattr(s, "definition_url")
            and "time" in getattr(s, "definition_url", "")
        ]
        for ts in time_symbols:
            expr = expr.subs(ts, self.context.get("t", sympy.Symbol("t")))

        # Replace avogadro constant if present
        avogadro_symbols = [
            s
            for s in expr.atoms(sympy.Dummy)
            if hasattr(s, "definition_url")
            and "avogadro" in getattr(s, "definition_url", "")
        ]
        for av in avogadro_symbols:
            # SBML L3V2 defines avogadro as 6.02214179e23
            expr = expr.subs(av, sympy.Float(6.02214179e23))

        return expr

    def _inline_custom_functions(self, expr: sympy.Expr) -> sympy.Expr:
        """Inline custom SBML functions that appear as undefined SymPy functions

        When sbmlmath parses MathML with custom functions, it creates SymPy
        Function objects (e.g., metab_MM). We need to replace these with their
        actual mathematical definitions, including handling nested function calls.

        Args:
            expr: SymPy expression potentially containing custom functions

        Returns:
            Expression with custom functions inlined
        """
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            # Find all undefined functions in the expression
            undefined_funcs = [
                atom
                for atom in expr.atoms(sympy.Function)
                if isinstance(atom, sympy.core.function.AppliedUndef)
            ]

            if not undefined_funcs:
                # No more undefined functions, we're done
                break

            found_substitution = False

            # Replace each undefined function with its definition
            for func_call in undefined_funcs:
                func_name = func_call.func.__name__

                # Check if this is a custom SBML function we know about
                if func_name in self.functions:
                    func_def = self.functions[func_name]
                    func_args = func_def["arguments"]
                    func_body = func_def["mathString"]

                    # Create context with function arguments to prevent implicit multiplication issues
                    func_context = {arg: sympy.Symbol(arg) for arg in func_args}

                    # Parse the function body as a formula string
                    # This will recursively inline any nested functions
                    try:
                        body_expr = self._parse_formula_string(
                            func_body, extra_context=func_context
                        )
                    except Exception:
                        # If formula parsing fails, continue
                        continue

                    # Create substitution mapping from formal params to actual args
                    subs_dict = {}
                    for i, arg_name in enumerate(func_args):
                        if i < len(func_call.args):
                            subs_dict[sympy.Symbol(arg_name)] = func_call.args[i]

                    # Substitute arguments in the body
                    expanded = body_expr.subs(subs_dict)

                    # Replace the function call with the expanded expression
                    expr = expr.subs(func_call, expanded)
                    found_substitution = True
                    break  # Start over to handle newly revealed nested functions

            if not found_substitution:
                # No substitutions made, we're stuck
                break

            iteration += 1

        return expr

    def _parse_formula_string(
        self, expression: str, extra_context: dict = None
    ) -> sympy.Expr:
        """Parse formula string (old method - for backward compatibility)

        Args:
            expression: Formula string (e.g. "k1 * A")
            extra_context: Optional dictionary of extra symbols to include in context

        Returns:
            SymPy expression
        """
        # 1. Clean Units
        expression = self._remove_units(expression)

        # 2. Inline Function Definitions
        expression = self.function_inliner.inline(expression)

        # 3. Handle Piecewise formatting for SymPy
        expression = self._transform_piecewise(expression)

        # 4. Transform Python keywords (and, or) to SymPy functions (And, Or)
        expression = self._transform_logical_keywords(expression)

        # 5. Parse with SymPy
        # Enable implicit multiplication (e.g., "k1 A" -> "k1 * A")
        transformations = standard_transformations + (
            implicit_multiplication_application,
        )

        # Prepare context
        context = self.context.copy()
        if extra_context:
            context.update(extra_context)

        return parse_expr(
            expression, local_dict=context, transformations=transformations
        )

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

        # Clean up any dangling operators left after unit removal
        # Examples: "x * " -> "x", " * second" -> "", "x * * y" -> "x * y"
        expr = self._cleanup_dangling_operators(expr)

        return expr

    def _cleanup_dangling_operators(self, expr: str) -> str:
        """Clean up dangling operators left after unit removal

        Handles cases like:
        - "x * " -> "x"
        - " * second" -> ""
        - "x * * y" -> "x * y" (spaced duplicates)
        - "x + " -> "x"
        - " / second" -> ""

        Note: Protects ** (power operator) from being treated as duplicate * operators.

        Args:
            expr: Expression string potentially with dangling operators

        Returns:
            Cleaned expression string
        """
        # IMPORTANT: Protect power operator (**) from being treated as duplicate *
        # Replace ** with a temporary placeholder that's unlikely to appear in real expressions
        POWER_PLACEHOLDER = "__POWER_OP__"
        expr = expr.replace("**", POWER_PLACEHOLDER)

        # Remove trailing operators (with optional whitespace)
        expr = re.sub(r"\s*[\*\+\-\/]\s*$", "", expr)

        # Remove leading operators (with optional whitespace)
        expr = re.sub(r"^\s*[\*\+\-\/]\s*", "", expr)

        # Remove duplicate operators with spaces (e.g., " * * " -> " * ")
        expr = re.sub(r"\s*([\*\+\-\/])\s*\1\s*", r" \1 ", expr)

        # Remove operators with nothing on both sides (e.g., " * " in middle)
        expr = re.sub(r"\s*[\*\+\-\/]\s*[\*\+\-\/]\s*", " ", expr)

        # Restore power operator
        expr = expr.replace(POWER_PLACEHOLDER, "**")

        # Clean up extra whitespace
        expr = re.sub(r"\s+", " ", expr)
        expr = expr.strip()

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

    def _transform_logical_keywords(self, expr: str) -> str:
        """Transform Python keywords (and, or) to SymPy function names (And, Or)

        Python keywords like 'and' and 'or' cannot be used as function names in
        SymPy's parse_expr. This function replaces them with their capitalized
        versions which are valid function names.

        Args:
            expr: Expression string

        Returns:
            Transformed expression with 'and' -> 'And' and 'or' -> 'Or'
        """
        # Use word boundaries to match complete identifiers only
        # This prevents replacing 'and' inside 'stand' or 'or' inside 'for'
        import re

        # Replace 'and(' with 'And(' (function call)
        expr = re.sub(r"\band\s*\(", "And(", expr)
        # Replace 'or(' with 'Or(' (function call)
        expr = re.sub(r"\bor\s*\(", "Or(", expr)

        return expr

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
