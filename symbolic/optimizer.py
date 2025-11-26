# File: sbml_rust_generator/symbolic/optimizer.py
"""Handles symbolic optimization of mathematical expressions"""

import sympy
from typing import List, Tuple, Any
from ..core.base import Optimizer


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
            replacements, reduced = sympy.cse(expressions, optimizations='basic')

            print(f"CSE extracted {len(replacements)} common subexpressions")
            return replacements, reduced
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
