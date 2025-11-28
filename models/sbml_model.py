# File: sbml_rust_generator/models/sbml_model.py
"""Data models for SBML components"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional


@dataclass
class Species:
    """Represents an SBML species"""
    id: str
    name: str
    compartment: str
    initial_amount: float
    boundary_condition: bool = False
    has_only_substance_units: bool = False


@dataclass
class Parameter:
    """Represents an SBML parameter"""
    id: str
    value: float
    constant: bool = True
    name: Optional[str] = None


@dataclass
class Compartment:
    """Represents an SBML compartment"""
    id: str
    size: float
    constant: bool = True
    spatial_dimensions: int = 3


@dataclass
class Reaction:
    """Represents an SBML reaction"""
    id: str
    reactants: List[Tuple[float, str]]  # List of (stoichiometry, species_id)
    products: List[Tuple[float, str]]   # List of (stoichiometry, species_id)
    rate_law: str
    reversible: bool = False
    name: Optional[str] = None


@dataclass
class FunctionDefinition:
    """Represents an SBML function definition"""
    id: str
    arguments: List[str]
    math_string: str


class SbmlModel:
    """Complete SBML model representation"""

    def __init__(self):
        """Initialize an empty SBML model"""
        self.species: Dict[str, Species] = {}
        self.parameters: Dict[str, Parameter] = {}
        self.compartments: Dict[str, Compartment] = {}
        self.reactions: Dict[str, Reaction] = {}
        self.functions: Dict[str, FunctionDefinition] = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SbmlModel':
        """Create model from dictionary (backward compatible with original format)

        Args:
            data: Dictionary with keys: species, parameters, compartments, reactions, functions

        Returns:
            SbmlModel instance
        """
        model = cls()

        # Parse species
        for species_id, species_data in data.get("species", {}).items():
            model.species[species_id] = Species(
                id=species_id,
                name=species_data.get("name", species_id),
                compartment=species_data.get("compartment", "default"),
                initial_amount=species_data.get("value", 0.0),  # Parser stores as "value"
                boundary_condition=species_data.get("boundaryCondition", False),
                has_only_substance_units=species_data.get("hasOnlySubstanceUnits", False)
            )

        # Parse parameters
        for param_id, param_data in data.get("parameters", {}).items():
            model.parameters[param_id] = Parameter(
                id=param_id,
                value=param_data.get("value", 0.0),
                constant=param_data.get("constant", True),
                name=param_data.get("name")
            )

        # Parse compartments
        for comp_id, comp_data in data.get("compartments", {}).items():
            model.compartments[comp_id] = Compartment(
                id=comp_id,
                size=comp_data.get("size", 1.0),
                constant=comp_data.get("constant", True),
                spatial_dimensions=comp_data.get("spatialDimensions", 3)
            )

        # Parse reactions
        for rxn_id, rxn_data in data.get("reactions", {}).items():
            model.reactions[rxn_id] = Reaction(
                id=rxn_id,
                reactants=rxn_data.get("reactants", []),
                products=rxn_data.get("products", []),
                rate_law=rxn_data.get("rateLaw", "0"),
                reversible=rxn_data.get("reversible", False),
                name=rxn_data.get("name")
            )

        # Parse functions
        for func_id, func_data in data.get("functions", {}).items():
            model.functions[func_id] = FunctionDefinition(
                id=func_id,
                arguments=func_data.get("arguments", []),
                math_string=func_data.get("mathString", "0")
            )

        return model

    def to_dict(self) -> Dict[str, Any]:
        """Convert model back to dictionary format

        Returns:
            Dictionary representation compatible with original format
        """
        return {
            "species": {
                s_id: {
                    "name": s.name,
                    "compartment": s.compartment,
                    "initialAmount": s.initial_amount,
                    "boundaryCondition": s.boundary_condition,
                    "hasOnlySubstanceUnits": s.has_only_substance_units
                }
                for s_id, s in self.species.items()
            },
            "parameters": {
                p_id: {
                    "value": p.value,
                    "constant": p.constant,
                    "name": p.name
                }
                for p_id, p in self.parameters.items()
            },
            "compartments": {
                c_id: {
                    "size": c.size,
                    "constant": c.constant,
                    "spatialDimensions": c.spatial_dimensions
                }
                for c_id, c in self.compartments.items()
            },
            "reactions": {
                r_id: {
                    "reactants": r.reactants,
                    "products": r.products,
                    "rateLaw": r.rate_law,
                    "reversible": r.reversible,
                    "name": r.name
                }
                for r_id, r in self.reactions.items()
            },
            "functions": {
                f_id: {
                    "arguments": f.arguments,
                    "mathString": f.math_string
                }
                for f_id, f in self.functions.items()
            }
        }

    def validate(self) -> bool:
        """Validate model consistency

        Returns:
            True if model is valid
        """
        # Check all species reference valid compartments
        for species in self.species.values():
            if species.compartment not in self.compartments:
                return False

        # Check all reactions reference valid species
        for reaction in self.reactions.values():
            for _, species_id in reaction.reactants + reaction.products:
                if species_id not in self.species:
                    return False

        return True
