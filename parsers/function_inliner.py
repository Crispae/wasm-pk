# File: sbml_rust_generator/parsers/function_inliner.py
"""Handles inlining of user-defined functions in expressions"""

import re
from typing import Dict, Any, List


class FunctionInliner:
    """Handles inlining of user-defined functions in SBML expressions"""

    def __init__(self, functions: Dict[str, Any]):
        """Initialize function inliner

        Args:
            functions: Dictionary mapping function IDs to function definitions
                      Each definition should have 'arguments' and 'mathString' keys
        """
        self.functions = functions
        self.max_depth = 10  # Prevent infinite recursion

    def inline(self, expression: str) -> str:
        """Inline all function calls in an expression

        Recursively substitutes function calls with their definitions until
        no more functions remain or max depth is reached.

        Args:
            expression: String expression potentially containing function calls

        Returns:
            Expression string with all functions inlined

        Examples:
            >>> functions = {
            ...     'multiply': {
            ...         'arguments': ['x', 'y'],
            ...         'mathString': 'x * y'
            ...     }
            ... }
            >>> inliner = FunctionInliner(functions)
            >>> inliner.inline('multiply(a, b) + c')
            '(a * b) + c'
        """
        depth = 0
        while depth < self.max_depth:
            found_substitution = False

            for func_id, func_def in self.functions.items():
                # Look for function calls: func_id(...)
                pattern = rf"\b{func_id}\s*\("
                match = re.search(pattern, expression)

                if match:
                    # Extract arguments
                    start_idx = match.end()
                    args_str, end_idx = self._extract_arguments(expression, start_idx)

                    if end_idx is not None:
                        # Parse arguments
                        args = self._split_arguments(args_str)

                        # Get function body and parameters
                        body = func_def["mathString"]
                        def_args = func_def["arguments"]

                        # Substitute arguments in function body
                        substituted_body = self._substitute_arguments(body, def_args, args)

                        # Replace function call with substituted body
                        full_match = expression[match.start():end_idx]
                        expression = expression.replace(full_match, substituted_body, 1)
                        found_substitution = True
                        break  # Start over to handle nested calls properly

            if not found_substitution:
                break
            depth += 1

        return expression

    def _extract_arguments(self, expr_str: str, start_idx: int) -> tuple:
        """Extract arguments from a function call

        Args:
            expr_str: The expression string
            start_idx: Starting index (after opening parenthesis)

        Returns:
            Tuple of (arguments_string, end_index) or (None, None) if unmatched
        """
        open_count = 1
        end_idx = start_idx
        args_str = ""

        while end_idx < len(expr_str) and open_count > 0:
            if expr_str[end_idx] == "(":
                open_count += 1
            elif expr_str[end_idx] == ")":
                open_count -= 1

            if open_count > 0:
                args_str += expr_str[end_idx]
            end_idx += 1

        if open_count == 0:
            return args_str, end_idx
        else:
            return None, None

    def _split_arguments(self, args_str: str) -> List[str]:
        """Split function arguments respecting nested parentheses

        Args:
            args_str: Comma-separated argument string

        Returns:
            List of argument strings

        Examples:
            >>> inliner = FunctionInliner({})
            >>> inliner._split_arguments('a, b, f(x, y)')
            ['a', 'b', 'f(x, y)']
        """
        args = []
        current = ""
        depth = 0

        for char in args_str:
            if char == "," and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def _substitute_arguments(self, body: str, def_args: List[str], args: List[str]) -> str:
        """Substitute argument values into function body

        Args:
            body: Function body expression
            def_args: Formal parameter names
            args: Actual argument values

        Returns:
            Function body with substituted arguments
        """
        # Sort arguments by length (descending) to prevent partial replacements
        # e.g., replace 'abc' before 'ab' to avoid turning 'abc' into 'XYZc'
        sorted_def_args = sorted(
            enumerate(def_args), key=lambda x: len(x[1]), reverse=True
        )

        substituted_body = f"({body})"

        for idx, arg_name in sorted_def_args:
            if idx < len(args):
                val = args[idx]
                # Use word boundaries to match complete identifiers only
                substituted_body = re.sub(
                    rf"\b{arg_name}\b", f"({val})", substituted_body
                )

        return substituted_body
