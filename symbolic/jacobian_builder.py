# File: sbml_rust_generator/symbolic/jacobian_builder.py
"""Computes Jacobian matrix for ODE systems"""

import sympy
from typing import List, Tuple, Dict


class JacobianBuilder:
    """Computes Jacobian matrix for ODE system"""

    def __init__(self, species_symbols: Dict[str, sympy.Symbol], species_list: List[str]):
        """Initialize Jacobian builder

        Args:
            species_symbols: Dictionary mapping species IDs to SymPy symbols
            species_list: Ordered list of species IDs (defines matrix order)
        """
        self.species_symbols = species_symbols
        self.species_list = species_list
        self.n_species = len(species_list)

    def compute_jacobian(self, ode_system: List[sympy.Expr]) -> List[List[sympy.Expr]]:
        """Compute full Jacobian matrix

        Computes J[i,j] = d(dy_dt[i])/d(y[j]) for all i,j

        Args:
            ode_system: List of dy/dt expressions

        Returns:
            2D list representing Jacobian matrix
        """
        print("Computing Jacobian...")
        jacobian = []

        for i in range(self.n_species):
            row = []
            for j in range(self.n_species):
                species_symbol = self.species_symbols[self.species_list[j]]
                derivative = sympy.diff(ode_system[i], species_symbol).doit()
                row.append(derivative)
            jacobian.append(row)

        return jacobian

    def compute_sparse_jacobian(
        self, ode_system: List[sympy.Expr]
    ) -> Tuple[List[sympy.Expr], List[Tuple[int, int]]]:
        """Compute only non-zero Jacobian elements (sparse representation)

        More efficient than full matrix when system is sparse.

        Args:
            ode_system: List of dy/dt expressions

        Returns:
            Tuple of:
                - List of non-zero Jacobian elements
                - List of (row, col) indices for each element
        """
        print("Computing Jacobian (sparse)...")
        jacobian_elements = []
        jac_indices = []

        for i in range(self.n_species):
            for j in range(self.n_species):
                species_symbol = self.species_symbols[self.species_list[j]]
                derivative = sympy.diff(ode_system[i], species_symbol).doit()

                # Only store non-zero elements
                if derivative != 0:
                    jac_indices.append((i, j))
                    jacobian_elements.append(derivative)

        print(f"Jacobian sparsity: {len(jacobian_elements)}/{self.n_species**2} non-zero")
        return jacobian_elements, jac_indices

    def compute_jacobian_action(
        self, ode_system: List[sympy.Expr]
    ) -> Tuple[List[sympy.Expr], List[Tuple[int, int]]]:
        """Compute Jacobian for matrix-vector product J*v

        Useful for implicit ODE solvers that need Jacobian-vector products
        rather than full Jacobian matrix.

        Args:
            ode_system: List of dy/dt expressions

        Returns:
            Tuple of (jacobian_elements, indices) for sparse J*v computation
        """
        return self.compute_sparse_jacobian(ode_system)

    def get_sparsity_pattern(self, ode_system: List[sympy.Expr]) -> List[Tuple[int, int]]:
        """Get sparsity pattern of Jacobian

        Args:
            ode_system: List of dy/dt expressions

        Returns:
            List of (row, col) tuples for non-zero elements
        """
        _, indices = self.compute_sparse_jacobian(ode_system)
        return indices

    def estimate_sparsity(self, ode_system: List[sympy.Expr]) -> float:
        """Estimate fraction of non-zero Jacobian elements

        Args:
            ode_system: List of dy/dt expressions

        Returns:
            Fraction of non-zero elements (0.0 to 1.0)
        """
        _, indices = self.compute_sparse_jacobian(ode_system)
        total_elements = self.n_species ** 2
        non_zero = len(indices)
        return non_zero / total_elements if total_elements > 0 else 0.0
