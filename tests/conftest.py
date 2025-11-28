"""Pytest configuration and shared fixtures"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import libsbml
import sympy
from sbmlParser.parser import ParseSBMLFile
from parsers.expression_parser import SbmlExpressionParser


@pytest.fixture
def sample_sbml_file():
    """Create a minimal valid SBML file for testing"""
    # Create a simple SBML model programmatically
    doc = libsbml.SBMLDocument(3, 2)
    model = doc.createModel()
    model.setId("test_model")
    
    # Add a compartment (with required attributes for SBML L3V2)
    compartment = model.createCompartment()
    compartment.setId("comp1")
    compartment.setSize(1.0)
    compartment.setConstant(True)  # Required attribute
    
    # Add a species (with required attributes for SBML L3V2)
    species = model.createSpecies()
    species.setId("S1")
    species.setCompartment("comp1")
    species.setInitialAmount(1.0)
    species.setBoundaryCondition(False)  # Required attribute
    species.setHasOnlySubstanceUnits(False)  # Required attribute
    species.setConstant(False)  # Required attribute
    
    # Add a parameter (with required attributes for SBML L3V2)
    param = model.createParameter()
    param.setId("k1")
    param.setValue(0.5)
    param.setConstant(True)  # Required attribute
    
    # Add a simple reaction (with required attributes for SBML L3V2)
    reaction = model.createReaction()
    reaction.setId("R1")
    reaction.setReversible(False)  # Required attribute
    reactant = reaction.createReactant()
    reactant.setSpecies("S1")
    reactant.setStoichiometry(1.0)
    reactant.setConstant(True)  # Required attribute for speciesReference
    kl = reaction.createKineticLaw()
    math_ast = libsbml.parseL3Formula("k1 * S1")
    kl.setMath(math_ast)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        temp_path = f.name
    
    libsbml.writeSBMLToFile(doc, temp_path)
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except (OSError, PermissionError):
        pass  # File may already be deleted or locked


@pytest.fixture
def sample_model_data(sample_sbml_file):
    """Parse sample SBML file and return model data"""
    return ParseSBMLFile(sample_sbml_file)


@pytest.fixture
def expression_parser():
    """Create an expression parser with basic context"""
    context = {
        'x': sympy.Symbol('x'),
        'y': sympy.Symbol('y'),
        'k1': sympy.Symbol('k1'),
        'k2': sympy.Symbol('k2'),
        't': sympy.Symbol('t'),
        'time': sympy.Symbol('t'),
    }
    return SbmlExpressionParser(context, {})


@pytest.fixture
def simple_reaction_data():
    """Sample reaction data for testing"""
    return {
        "R1": {
            "Id": "R1",
            "reactants": [[1.0, "A"]],
            "products": [[1.0, "B"]],
            "rateLaw": "k1 * A"
        }
    }


@pytest.fixture
def assignment_rules_data():
    """Sample assignment rules for testing"""
    return {
        "rule1": {
            "variable": "V1",
            "math": "k1 * x"
        },
        "rule2": {
            "variable": "V2",
            "math": "V1 + k2"
        }
    }


