"""Tests for SBML parsing functionality"""

import pytest
import libsbml
import tempfile
import os
from sbmlParser.parser import (
    ParseSBMLFile,
    ParseParameterAssignment,
    ParseSpecies,
    ParseCompartment,
    ParseFunction,
    ParseReaction,
    ParseRule,
    ParseEvent,
    ParseInitialAssignment,
)
from sbmlParser import dataclasses


class TestParseParameterAssignment:
    """Tests for ParseParameterAssignment function"""

    def test_parse_parameter_with_all_fields(self):
        """Test parsing a parameter with all fields set"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        param = model.createParameter()
        param.setId("k1")
        param.setName("rate_constant")
        param.setValue(0.5)
        param.setConstant(True)

        result = ParseParameterAssignment(0, param)

        assert result.Id == "k1"
        assert result.name == "rate_constant"
        assert result.value == 0.5
        assert result.isConstant is True

    def test_parse_parameter_without_name(self):
        """Test parsing a parameter without a name"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        param = model.createParameter()
        param.setId("k2")
        param.setValue(1.0)

        result = ParseParameterAssignment(0, param)

        assert result.Id == "k2"
        assert result.name == ""
        assert result.value == 1.0

    def test_parse_parameter_without_id_raises_exception(self):
        """Test that parameter without ID raises exception"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        param = model.createParameter()
        # Don't set ID

        with pytest.raises(Exception, match="Parameter with no Id"):
            ParseParameterAssignment(0, param)

    def test_parse_parameter_without_value(self):
        """Test parsing a parameter without a value"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        param = model.createParameter()
        param.setId("k3")
        # Don't set value

        result = ParseParameterAssignment(0, param)

        assert result.Id == "k3"
        assert result.value is None


class TestParseSpecies:
    """Tests for ParseSpecies function"""

    def test_parse_species_with_initial_amount(self):
        """Test parsing species with initial amount"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        species = model.createSpecies()
        species.setId("S1")
        species.setName("Species1")
        species.setCompartment("comp1")
        species.setInitialAmount(10.0)
        species.setBoundaryCondition(False)
        species.setHasOnlySubstanceUnits(False)

        result = ParseSpecies(0, species)

        assert result.Id == "S1"
        assert result.name == "Species1"
        assert result.compartment == "comp1"
        assert result.value == 10.0
        assert result.valueType == "Amount"
        assert result.isBoundarySpecies is False

    def test_parse_species_with_initial_concentration(self):
        """Test parsing species with initial concentration"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        species = model.createSpecies()
        species.setId("S2")
        species.setCompartment("comp1")
        species.setInitialConcentration(5.0)

        result = ParseSpecies(0, species)

        assert result.Id == "S2"
        assert result.value == 5.0
        assert result.valueType == "Concentration"

    def test_parse_species_without_initial_value(self):
        """Test parsing species without initial value"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        species = model.createSpecies()
        species.setId("S3")
        species.setCompartment("comp1")
        # Don't set initial value

        result = ParseSpecies(0, species)

        assert result.Id == "S3"
        assert result.value is None
        assert result.valueType == "Amount"

    def test_parse_boundary_species(self):
        """Test parsing boundary species"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        species = model.createSpecies()
        species.setId("S4")
        species.setCompartment("comp1")
        species.setInitialAmount(1.0)
        species.setBoundaryCondition(True)

        result = ParseSpecies(0, species)

        assert result.isBoundarySpecies is True


class TestParseCompartment:
    """Tests for ParseCompartment function"""

    def test_parse_compartment_with_all_fields(self):
        """Test parsing compartment with all fields"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        comp = model.createCompartment()
        comp.setId("comp1")
        comp.setName("Compartment1")
        comp.setSize(1.0)
        comp.setSpatialDimensions(3)
        comp.setConstant(True)

        result = ParseCompartment(0, comp)

        assert result.Id == "comp1"
        assert result.name == "Compartment1"
        assert result.size == 1.0
        assert result.dimensionality == 3
        assert result.isConstant is True

    def test_parse_compartment_without_size(self):
        """Test parsing compartment without size"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        comp = model.createCompartment()
        comp.setId("comp2")
        # Don't set size

        result = ParseCompartment(0, comp)

        assert result.Id == "comp2"
        assert result.size is None


class TestParseFunction:
    """Tests for ParseFunction function"""

    def test_parse_simple_function(self):
        """Test parsing a simple function definition"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        func = model.createFunctionDefinition()
        func.setId("multiply")
        func.setName("Multiply")

        # Create lambda(x, y, x * y)
        math_ast = libsbml.parseL3Formula("lambda(x, y, x * y)")
        func.setMath(math_ast)

        result = ParseFunction(0, func)

        assert result.Id == "multiply"
        assert result.name == "Multiply"
        assert len(result.arguments) == 2
        assert "x" in result.arguments
        assert "y" in result.arguments
        assert "x * y" in result.mathString or "*" in result.mathString


class TestParseReaction:
    """Tests for ParseReaction function"""

    def test_parse_simple_reaction(self):
        """Test parsing a simple reaction"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()

        # Create species
        species1 = model.createSpecies()
        species1.setId("A")
        species1.setCompartment("comp1")
        species2 = model.createSpecies()
        species2.setId("B")
        species2.setCompartment("comp1")

        # Create compartment
        comp = model.createCompartment()
        comp.setId("comp1")

        # Create reaction
        reaction = model.createReaction()
        reaction.setId("R1")
        reaction.setName("Reaction1")

        # Add reactant
        reactant = reaction.createReactant()
        reactant.setSpecies("A")
        reactant.setStoichiometry(1.0)

        # Add product
        product = reaction.createProduct()
        product.setSpecies("B")
        product.setStoichiometry(1.0)

        # Add kinetic law
        kl = reaction.createKineticLaw()
        math_ast = libsbml.parseL3Formula("k1 * A")
        kl.setMath(math_ast)

        result = ParseReaction(0, reaction)

        assert result.Id == "R1"
        assert result.name == "Reaction1"
        assert len(result.reactants) == 1
        assert result.reactants[0][0] == 1.0
        assert result.reactants[0][1] == "A"
        assert len(result.products) == 1
        assert result.products[0][0] == 1.0
        assert result.products[0][1] == "B"
        assert result.rateLaw is not None
        assert "k1" in result.rateLaw or "A" in result.rateLaw

    def test_parse_reaction_without_kinetic_law_raises_exception(self):
        """Test that reaction without kinetic law raises exception"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        reaction = model.createReaction()
        reaction.setId("R2")
        # Don't set kinetic law

        with pytest.raises(Exception):
            ParseReaction(0, reaction)


class TestParseRule:
    """Tests for ParseRule function"""

    def test_parse_assignment_rule(self):
        """Test parsing an assignment rule"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        rule = model.createAssignmentRule()
        rule.setIdAttribute("rule1")  # Use setIdAttribute for rules
        rule.setVariable("x")
        rule.setName("Assignment")
        math_ast = libsbml.parseL3Formula("k1 * y")
        rule.setMath(math_ast)

        result = ParseRule(0, rule)

        assert isinstance(result, dataclasses.AssignmentRuleData)
        assert result.Id == "rule1"
        assert result.variable == "x"
        assert result.math is not None

    def test_parse_rate_rule(self):
        """Test parsing a rate rule"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        rule = model.createRateRule()
        rule.setIdAttribute("rule2")  # Use setIdAttribute for rules
        rule.setVariable("x")
        math_ast = libsbml.parseL3Formula("k1")
        rule.setMath(math_ast)

        result = ParseRule(0, rule)

        assert isinstance(result, dataclasses.RateRuleData)
        assert result.Id == "rule2"
        assert result.variable == "x"

    def test_parse_algebraic_rule_raises_exception(self):
        """Test that algebraic rules raise exception"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        rule = model.createAlgebraicRule()
        rule.setId("rule3")
        math_ast = libsbml.parseL3Formula("x + y = 0")
        rule.setMath(math_ast)

        with pytest.raises(
            Exception, match="Algebraic rules are currently not supported"
        ):
            ParseRule(0, rule)


class TestParseEvent:
    """Tests for ParseEvent function"""

    def test_parse_simple_event(self):
        """Test parsing a simple event"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        event = model.createEvent()
        event.setId("event1")
        event.setName("Event1")

        # Create trigger
        trigger = event.createTrigger()
        math_ast = libsbml.parseL3Formula("t > 5")
        trigger.setMath(math_ast)
        trigger.setPersistent(True)

        # Create event assignment
        assignment = event.createEventAssignment()
        assignment.setVariable("x")
        math_ast2 = libsbml.parseL3Formula("10")
        assignment.setMath(math_ast2)

        result = ParseEvent(0, event)

        assert result.Id == "event1"
        assert result.name == "Event1"
        assert result.trigger is not None
        assert len(result.eventAssignments) == 1
        assert result.eventAssignments[0].variable == "x"


class TestParseInitialAssignment:
    """Tests for ParseInitialAssignment function"""

    def test_parse_initial_assignment(self):
        """Test parsing an initial assignment"""
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        assignment = model.createInitialAssignment()
        assignment.setIdAttribute("init1")  # Use setIdAttribute for initial assignments
        assignment.setSymbol("x")
        assignment.setName("Initial")
        math_ast = libsbml.parseL3Formula("k1 * 2")
        assignment.setMath(math_ast)

        result = ParseInitialAssignment(0, assignment)

        assert result.Id == "init1"
        assert result.variable == "x"
        assert result.math is not None


class TestParseSBMLFile:
    """Tests for ParseSBMLFile function"""

    def test_parse_simple_sbml_file(self, sample_sbml_file):
        """Test parsing a simple SBML file"""
        result = ParseSBMLFile(sample_sbml_file)

        assert "parameters" in result
        assert "compartments" in result
        assert "species" in result
        assert "reactions" in result
        assert "functions" in result
        assert "assignmentRules" in result
        assert "rateRules" in result
        assert "initialAssignments" in result
        assert "events" in result

    def test_parse_sbml_file_with_all_components(self):
        """Test parsing SBML file with all component types"""
        # Create comprehensive SBML model
        doc = libsbml.SBMLDocument(3, 2)
        model = doc.createModel()
        model.setId("comprehensive_model")

        # Add compartment (with required attributes for SBML L3V2)
        comp = model.createCompartment()
        comp.setId("comp1")
        comp.setSize(1.0)
        comp.setConstant(True)  # Required attribute

        # Add species (with required attributes for SBML L3V2)
        species = model.createSpecies()
        species.setId("S1")
        species.setCompartment("comp1")
        species.setInitialAmount(1.0)
        species.setBoundaryCondition(False)  # Required attribute
        species.setHasOnlySubstanceUnits(False)  # Required attribute
        species.setConstant(False)  # Required attribute

        # Add parameter (with required attributes for SBML L3V2)
        param = model.createParameter()
        param.setId("k1")
        param.setValue(0.5)
        param.setConstant(True)  # Required attribute

        # Add function
        func = model.createFunctionDefinition()
        func.setId("multiply")
        math_ast = libsbml.parseL3Formula("lambda(x, y, x * y)")
        func.setMath(math_ast)

        # Add assignment rule
        rule = model.createAssignmentRule()
        rule.setIdAttribute("rule1")  # Set ID for rule
        rule.setVariable("x")
        math_ast2 = libsbml.parseL3Formula("k1 * S1")
        rule.setMath(math_ast2)

        # Add reaction (with required attributes for SBML L3V2)
        reaction = model.createReaction()
        reaction.setId("R1")
        reaction.setReversible(False)  # Required attribute
        reactant = reaction.createReactant()
        reactant.setSpecies("S1")
        reactant.setStoichiometry(1.0)
        reactant.setConstant(True)  # Required attribute for speciesReference
        kl = reaction.createKineticLaw()
        math_ast3 = libsbml.parseL3Formula("k1 * S1")
        kl.setMath(math_ast3)

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            libsbml.writeSBMLToFile(doc, temp_path)
            result = ParseSBMLFile(temp_path)

            assert len(result["parameters"]) > 0
            assert len(result["compartments"]) > 0
            assert len(result["species"]) > 0
            assert len(result["reactions"]) > 0
            assert len(result["functions"]) > 0
            assert len(result["assignmentRules"]) > 0
        finally:
            # Cleanup - close file handle before deleting on Windows
            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # File may already be deleted or locked

    def test_parse_invalid_sbml_file_raises_exception(self):
        """Test that invalid SBML file raises exception"""
        # Create invalid SBML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name
            f.write("<?xml version='1.0'?><invalid>content</invalid>")
            f.flush()

        try:
            with pytest.raises(Exception):
                ParseSBMLFile(temp_path)
        finally:
            # Cleanup - close file handle before deleting on Windows
            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # File may already be deleted or locked
