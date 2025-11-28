"""Tests for ODE system building functionality"""

import pytest
import sympy
from symbolic.ode_builder import OdeSystemBuilder
from parsers.expression_parser import SbmlExpressionParser


class TestOdeSystemBuilder:
    """Tests for OdeSystemBuilder class"""

    @pytest.fixture
    def species_map(self):
        """Create a species map for testing"""
        return {"A": 0, "B": 1, "C": 2}

    @pytest.fixture
    def parser(self):
        """Create an expression parser for testing"""
        context = {
            "A": sympy.Symbol("A"),
            "B": sympy.Symbol("B"),
            "C": sympy.Symbol("C"),
            "k1": sympy.Symbol("k1"),
            "k2": sympy.Symbol("k2"),
            "t": sympy.Symbol("t"),
        }
        return SbmlExpressionParser(context, {})

    @pytest.fixture
    def ode_builder(self, species_map, parser):
        """Create an ODE builder for testing"""
        return OdeSystemBuilder(species_map, parser)

    def test_build_simple_reaction(self, ode_builder):
        """Test building ODE from a simple reaction"""
        reactions = {
            "R1": {
                "reactants": [[1.0, "A"]],
                "products": [[1.0, "B"]],
                "rateLaw": "k1 * A",
            }
        }

        ode_system = ode_builder.build_ode_system(reactions)

        assert len(ode_system) == 3  # A, B, C
        # A should decrease (negative contribution)
        assert ode_system[0] != sympy.Float(0.0)
        # B should increase (positive contribution)
        assert ode_system[1] != sympy.Float(0.0)
        # C should be unchanged
        assert ode_system[2] == sympy.Float(0.0)

    def test_build_reversible_reaction(self, ode_builder):
        """Test building ODE from reversible reaction"""
        reactions = {
            "R1": {
                "reactants": [[1.0, "A"]],
                "products": [[1.0, "B"]],
                "rateLaw": "k1 * A",
            },
            "R2": {
                "reactants": [[1.0, "B"]],
                "products": [[1.0, "A"]],
                "rateLaw": "k2 * B",
            },
        }

        ode_system = ode_builder.build_ode_system(reactions)

        # Both A and B should have non-zero rates
        assert ode_system[0] != sympy.Float(0.0)
        assert ode_system[1] != sympy.Float(0.0)

    def test_build_reaction_with_stoichiometry(self, ode_builder):
        """Test building ODE with non-unity stoichiometry"""
        reactions = {
            "R1": {
                "reactants": [[2.0, "A"]],
                "products": [[1.0, "B"]],
                "rateLaw": "k1 * A",
            }
        }

        ode_system = ode_builder.build_ode_system(reactions)

        # A should decrease by 2 * rate
        # B should increase by 1 * rate
        assert ode_system[0] != sympy.Float(0.0)
        assert ode_system[1] != sympy.Float(0.0)

    def test_build_multiple_reactions(self, ode_builder):
        """Test building ODE from multiple reactions"""
        reactions = {
            "R1": {
                "reactants": [[1.0, "A"]],
                "products": [[1.0, "B"]],
                "rateLaw": "k1 * A",
            },
            "R2": {
                "reactants": [[1.0, "B"]],
                "products": [[1.0, "C"]],
                "rateLaw": "k2 * B",
            },
        }

        ode_system = ode_builder.build_ode_system(reactions)

        # All species should have non-zero rates
        assert ode_system[0] != sympy.Float(0.0)  # A decreases
        assert ode_system[1] != sympy.Float(
            0.0
        )  # B: increases from R1, decreases from R2
        assert ode_system[2] != sympy.Float(0.0)  # C increases

    def test_build_reaction_with_complex_rate_law(self, ode_builder):
        """Test building ODE with complex rate law"""
        reactions = {
            "R1": {
                "reactants": [[1.0, "A"]],
                "products": [[1.0, "B"]],
                "rateLaw": "k1 * A * B / (k2 + A)",
            }
        }

        ode_system = ode_builder.build_ode_system(reactions)

        # Should successfully parse and build
        assert len(ode_system) == 3
        assert ode_system[0] != sympy.Float(0.0)

    def test_build_empty_reactions(self, ode_builder):
        """Test building ODE with no reactions"""
        reactions = {}

        ode_system = ode_builder.build_ode_system(reactions)

        # All rates should be zero
        assert all(rate == sympy.Float(0.0) for rate in ode_system)

    def test_build_reaction_with_unknown_species(self, ode_builder):
        """Test building ODE with species not in species_map"""
        reactions = {
            "R1": {
                "reactants": [[1.0, "Unknown"]],
                "products": [[1.0, "A"]],
                "rateLaw": "k1",
            }
        }

        ode_system = ode_builder.build_ode_system(reactions)

        # Unknown species should be ignored
        # A should still get positive contribution
        assert ode_system[0] != sympy.Float(0.0)

    def test_get_species_count(self, ode_builder):
        """Test getting species count"""
        assert ode_builder.get_species_count() == 3

    def test_get_species_index(self, ode_builder):
        """Test getting species index"""
        assert ode_builder.get_species_index("A") == 0
        assert ode_builder.get_species_index("B") == 1
        assert ode_builder.get_species_index("C") == 2

    def test_get_species_index_not_found(self, ode_builder):
        """Test getting index for unknown species raises KeyError"""
        with pytest.raises(KeyError):
            ode_builder.get_species_index("Unknown")

