# File: sbml_rust_generator/symbolic/ode_builder.py
"""Builds ODE system from SBML model reactions"""

import sympy
from typing import Dict, List, Tuple, Any
from ..core.base import ModelProcessor
from ..parsers.expression_parser import SbmlExpressionParser


class OdeSystemBuilder(ModelProcessor):
    """Builds ODE system from SBML model reactions"""

    def __init__(self, species_map: Dict[str, int], parser: SbmlExpressionParser):
        """Initialize ODE system builder

        Args:
            species_map: Dictionary mapping species IDs to indices
            parser: Expression parser for rate laws
        """
        self.species_map = species_map
        self.parser = parser
        self.n_species = len(species_map)

    def process(self, model_data: Dict[str, Any]) -> List[sympy.Expr]:
        """Build ODE system from reactions

        Args:
            model_data: Dictionary containing model data with 'reactions' key

        Returns:
            List of SymPy expressions representing dy/dt for each species
        """
        return self.build_ode_system(model_data.get("reactions", {}))

    def build_ode_system(self, reactions: Dict[str, Any]) -> List[sympy.Expr]:
        """Build differential equations from reactions

        For each reaction, adds contributions to species rates based on
        stoichiometry. Products get positive contributions, reactants get
        negative contributions.

        Args:
            reactions: Dictionary of reactions with rate laws

        Returns:
            List of dy/dt expressions for each species

        Example:
            For reaction: A + B -> C with rate k*A*B
            - dy_dt[A] -= k*A*B
            - dy_dt[B] -= k*A*B
            - dy_dt[C] += k*A*B
        """
        # Initialize all rates to zero
        dy_dt = [sympy.Float(0.0)] * self.n_species

        print("Parsing reactions...")
        for rxn_id, rxn in reactions.items():
            try:
                # Parse the rate law expression
                rate_expr = self.parser.parse(rxn.get("rateLaw", "0"))

                # Add contributions from reactants (negative stoichiometry)
                for stoich, species_id in rxn.get("reactants", []):
                    if species_id in self.species_map:
                        idx = self.species_map[species_id]
                        dy_dt[idx] -= stoich * rate_expr

                # Add contributions from products (positive stoichiometry)
                for stoich, species_id in rxn.get("products", []):
                    if species_id in self.species_map:
                        idx = self.species_map[species_id]
                        dy_dt[idx] += stoich * rate_expr

            except Exception as e:
                print(f"Failed to process reaction {rxn_id}: {e}")
                raise e

        return dy_dt

    def get_species_count(self) -> int:
        """Get number of species in the system

        Returns:
            Number of species
        """
        return self.n_species

    def get_species_index(self, species_id: str) -> int:
        """Get index for a species

        Args:
            species_id: Species identifier

        Returns:
            Index of species in state vector

        Raises:
            KeyError: If species not found
        """
        return self.species_map[species_id]
