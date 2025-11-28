# File: sbml_rust_generator/symbolic/optimizer.py
"""Handles symbolic optimization of mathematical expressions"""

import sympy
from typing import List, Tuple, Any
from core.base import Optimizer


class SymbolicOptimizer(Optimizer):
    """Handles symbolic optimization (CSE, simplification) of expressions"""

    def __init__(self, optimization_level: int = 2):
        """Initialize symbolic optimizer

        Args:
            optimization_level: Level of optimization (0-3)
                0: No optimization
                1: Basic simplification
                2: Common Subexpression Elimination (default)
                3: Aggressive optimization (CSE + simplification)
        """
        self.optimization_level = optimization_level

    def optimize(self, expressions: List[sympy.Expr]) -> Tuple[List[Tuple], List[sympy.Expr]]:
        """Apply Common Subexpression Elimination to expressions

        CSE identifies repeated subexpressions and extracts them as
        temporary variables, reducing redundant calculations.

        Args:
            expressions: List of SymPy expressions to optimize

        Returns:
            Tuple of:
                - List of (symbol, expression) pairs for temporary variables
                - List of reduced expressions using those temporaries

        Example:
            Input: [a*b + a*b*c, a*b + d]
            Output: ([(x0, a*b)], [x0 + x0*c, x0 + d])
        """
        if self.optimization_level == 0:
            return [], expressions

        print("Optimizing expressions with CSE...")

        if self.optimization_level >= 2:
            # Apply Common Subexpression Elimination
            # Use 'basic' optimizations to avoid aggressive rewrites that can
            # introduce division by zero (e.g., rewriting 1/(a+b) as (a+b)^-1)
            replacements, reduced = sympy.cse(
                expressions,
                optimizations='basic',
                order='none'  # Preserve original expression structure
            )

            # Post-process to avoid unsafe divisions
            safe_replacements = self._ensure_safe_divisions(replacements)

            print(f"CSE extracted {len(safe_replacements)} common subexpressions")
            return safe_replacements, reduced
        else:
            # Basic simplification only
            simplified = [self.simplify(expr) for expr in expressions]
            return [], simplified

    def simplify(self, expression: sympy.Expr) -> sympy.Expr:
        """Simplify a symbolic expression

        Args:
            expression: SymPy expression to simplify

        Returns:
            Simplified expression
        """
        if self.optimization_level == 0:
            return expression

        return sympy.simplify(expression)

    def optimize_separately(
        self,
        ode_system: List[sympy.Expr],
        jacobian: List[sympy.Expr]
    ) -> Tuple[List[Tuple], List[sympy.Expr], List[sympy.Expr]]:
        """Optimize ODE and Jacobian separately

        Args:
            ode_system: List of dy/dt expressions
            jacobian: List of Jacobian elements

        Returns:
            Tuple of (ode_replacements, reduced_ode, reduced_jacobian)
        """
        # Optimize ODE system
        ode_replacements, reduced_ode = self.optimize(ode_system)

        # Optimize Jacobian (reusing ODE temporaries)
        jac_replacements, reduced_jac = self.optimize(jacobian)

        # Combine replacements
        all_replacements = ode_replacements + jac_replacements

        return all_replacements, reduced_ode, reduced_jac

    def optimize_combined(
        self,
        ode_system: List[sympy.Expr],
        jacobian: List[sympy.Expr]
    ) -> Tuple[List[Tuple], List[sympy.Expr], List[sympy.Expr]]:
        """Optimize ODE and Jacobian together for maximum sharing

        More efficient than separate optimization as it can find common
        subexpressions between ODE and Jacobian.

        Args:
            ode_system: List of dy/dt expressions
            jacobian: List of Jacobian elements

        Returns:
            Tuple of:
                - Combined replacements for both
                - Reduced ODE expressions
                - Reduced Jacobian expressions
        """
        print("Optimizing ODE and Jacobian together...")

        # Combine all expressions
        all_exprs = ode_system + jacobian
        replacements, reduced = self.optimize(all_exprs)

        # Split back
        n_ode = len(ode_system)
        reduced_ode = reduced[:n_ode]
        reduced_jac = reduced[n_ode:]

        return replacements, reduced_ode, reduced_jac

    def set_optimization_level(self, level: int):
        """Change optimization level

        Args:
            level: New optimization level (0-3)
        """
        if 0 <= level <= 3:
            self.optimization_level = level
        else:
            raise ValueError("Optimization level must be between 0 and 3")

    def _ensure_safe_divisions(self, replacements: List[Tuple]) -> List[Tuple]:
        """Post-process CSE replacements to avoid unsafe divisions

        Checks if any replacement contains Pow(x, -n) where x could be zero.
        Tracks which symbols can be zero across replacements.

        Args:
            replacements: List of (symbol, expression) pairs from CSE

        Returns:
            List of safe (symbol, expression) pairs
        """
        safe_replacements = []
        # Track which symbols can evaluate to zero
        zero_symbols = set()

        print(f"DEBUG: Processing {len(replacements)} CSE replacements for safe divisions...")

        for sym, expr in replacements:
            # Debug: print the expression for x16
            if str(sym) == 'x16':
                print(f"DEBUG: x16 expression tree: {expr}")
                print(f"DEBUG: x16 expression type: {type(expr)}")
                print(f"DEBUG: x16 expression args: {expr.args if hasattr(expr, 'args') else 'N/A'}")

            # Check if this expression itself can be zero
            if self._expr_can_be_zero(expr):
                zero_symbols.add(sym)
                print(f"DEBUG: Symbol {sym} can be zero")

            # Check if expression contains negative powers of potentially zero values
            has_unsafe_pow = False
            pow_count = 0
            for subexpr in sympy.preorder_traversal(expr):
                if isinstance(subexpr, sympy.Pow):
                    pow_count += 1
                    exp = subexpr.exp
                    if exp.is_number and exp < 0:
                        base = subexpr.base
                        if str(sym) == 'x16':
                            print(f"DEBUG: x16 Pow#{pow_count}: base={base}, base_type={type(base).__name__}, exp={exp}")
                            print(f"DEBUG: x16 Pow#{pow_count}: is base a Symbol? {isinstance(base, sympy.Symbol)}")
                            if isinstance(base, sympy.Symbol):
                                print(f"DEBUG: x16 Pow#{pow_count}: is {base} in zero_symbols? {base in zero_symbols}")

                        # Check if base is a zero symbol
                        if isinstance(base, sympy.Symbol) and base in zero_symbols:
                            print(f"DEBUG: Found unsafe division in {sym}: {base}^{exp} (zero symbol)")
                            has_unsafe_pow = True
                            break
                        # Check if base contains Piecewise with 0
                        elif self._expr_can_be_zero(base):
                            print(f"DEBUG: Found unsafe division in {sym}: {base}^{exp} (Piecewise)")
                            has_unsafe_pow = True
                            break
                        # NEW: Check if base contains any zero symbols (e.g., in an Add or Mul)
                        elif self._contains_zero_symbol(base, zero_symbols):
                            print(f"DEBUG: Found unsafe division in {sym}: {base}^{exp} (contains zero symbol)")
                            has_unsafe_pow = True
                            break

            if has_unsafe_pow:
                # Rewrite to make divisions safe
                print(f"DEBUG: Rewriting {sym} expression to make safe")
                safe_expr = self._make_division_safe(expr, zero_symbols)
                safe_replacements.append((sym, safe_expr))
            else:
                safe_replacements.append((sym, expr))

        print(f"DEBUG: Total zero-valued symbols found: {len(zero_symbols)}")
        if zero_symbols:
            print(f"DEBUG: Zero symbols: {zero_symbols}")
        return safe_replacements

    def _expr_can_be_zero(self, expr: sympy.Expr) -> bool:
        """Check if an expression can evaluate to zero

        Args:
            expr: SymPy expression to check

        Returns:
            True if expression contains Piecewise that can be 0
        """
        # Check if expression is or contains a Piecewise with 0.0 as value
        for piece in sympy.preorder_traversal(expr):
            if isinstance(piece, sympy.Piecewise):
                for val, _ in piece.args:
                    if val == 0 or val == sympy.Float(0) or val == sympy.Integer(0):
                        return True
        return False

    def _contains_zero_symbol(self, expr: sympy.Expr, zero_symbols: set) -> bool:
        """Check if expression contains any symbol that can be zero

        Args:
            expr: SymPy expression to check
            zero_symbols: Set of symbols that can be zero

        Returns:
            True if expression contains any zero symbol
        """
        for subexpr in sympy.preorder_traversal(expr):
            if isinstance(subexpr, sympy.Symbol) and subexpr in zero_symbols:
                return True
        return False

    def _make_division_safe(self, expr: sympy.Expr, zero_symbols: set) -> sympy.Expr:
        """Rewrite expression to make divisions safe

        Replaces x^(-n) with Piecewise((x^(-n), base != 0), (large_value, True))
        where x or base could be zero.

        Args:
            expr: Expression potentially containing unsafe divisions
            zero_symbols: Set of symbols that can be zero

        Returns:
            Rewritten safe expression
        """
        def is_unsafe_base(base):
            """Check if a base is unsafe (can be zero)"""
            # Check if base is a zero symbol
            if isinstance(base, sympy.Symbol) and base in zero_symbols:
                return True
            # Check if base contains Piecewise with 0
            if self._expr_can_be_zero(base):
                return True
            # Check if base contains any zero symbol
            if self._contains_zero_symbol(base, zero_symbols):
                return True
            return False

        def safe_pow(base, exp):
            """Helper to create safe power expression"""
            if exp < 0 and is_unsafe_base(base):
                # Need to check if base is zero - if so, return large value
                # We need to find all zero symbols in the base and construct a condition
                # For simplicity, check if base != 0
                return sympy.Piecewise(
                    (sympy.Pow(base, exp), sympy.Ne(base, 0)),
                    (sympy.Float(1e10), True)
                )
            return sympy.Pow(base, exp)

        # Check if the expression itself is an unsafe Pow
        if isinstance(expr, sympy.Pow) and expr.exp.is_number and expr.exp < 0:
            if is_unsafe_base(expr.base):
                return safe_pow(expr.base, expr.exp)

        # Replace all Pow expressions with negative exponents
        return expr.replace(
            lambda e: isinstance(e, sympy.Pow) and e.exp.is_number and e.exp < 0,
            lambda e: safe_pow(e.base, e.exp)
        )

    def get_stats(self, expressions: List[sympy.Expr]) -> dict:
        """Get optimization statistics

        Args:
            expressions: Expressions to analyze

        Returns:
            Dictionary with optimization statistics
        """
        replacements, reduced = self.optimize(expressions)

        return {
            "num_expressions": len(expressions),
            "num_temporaries": len(replacements),
            "num_reduced": len(reduced),
            "optimization_level": self.optimization_level
        }
