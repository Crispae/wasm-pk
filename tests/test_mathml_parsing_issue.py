"""Test to reproduce MathML parsing issues with talinolol model

This test specifically checks MathML parsing with:
- XML declarations
- sbml:units attributes
- type attributes on <cn> elements
- xmlns:sbml namespace declarations
"""

import pytest
import sympy
import libsbml
from parsers.expression_parser import SbmlExpressionParser


class TestMathMLParsingIssues:
    """Test cases to reproduce MathML parsing failures"""

    def test_parse_mathml_with_xml_declaration(self, expression_parser):
        """Test parsing MathML that includes XML declaration"""
        # MathML with XML declaration (as returned by libsbml.writeMathMLToString)
        mathml = '''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <apply>
    <minus/>
    <cn> 1 </cn>
    <ci> x </ci>
  </apply>
</math>'''
        
        try:
            expr = expression_parser.parse(mathml)
            assert isinstance(expr, sympy.Expr)
        except Exception as e:
            pytest.fail(f"Failed to parse MathML with XML declaration: {e}")

    def test_parse_mathml_with_sbml_units_attribute(self, expression_parser):
        """Test parsing MathML with sbml:units attribute (like talinolol model)"""
        # This is the format that fails in talinolol model
        mathml = '''<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:sbml="http://www.sbml.org/sbml/level3/version2/core">
  <apply>
    <minus/>
    <cn sbml:units="l_per_kg"> 1 </cn>
    <apply>
      <plus/>
      <ci> FVgu </ci>
      <ci> FVki </ci>
    </apply>
  </apply>
</math>'''
        
        try:
            expr = expression_parser.parse(mathml)
            assert isinstance(expr, sympy.Expr)
        except Exception as e:
            pytest.fail(f"Failed to parse MathML with sbml:units attribute: {e}")

    def test_parse_mathml_with_type_attribute(self, expression_parser):
        """Test parsing MathML with type attribute on <cn> element"""
        mathml = '''<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:sbml="http://www.sbml.org/sbml/level3/version2/core">
  <apply>
    <plus/>
    <apply>
      <times/>
      <ci> BW </ci>
      <ci> COBW </ci>
    </apply>
    <apply>
      <divide/>
      <apply>
        <times/>
        <apply>
          <minus/>
          <ci> HR </ci>
          <ci> HRrest </ci>
        </apply>
        <ci> COHRI </ci>
      </apply>
      <cn sbml:units="s_per_min" type="integer"> 60 </cn>
    </apply>
  </apply>
</math>'''
        
        try:
            expr = expression_parser.parse(mathml)
            assert isinstance(expr, sympy.Expr)
        except Exception as e:
            pytest.fail(f"Failed to parse MathML with type attribute: {e}")

    def test_parse_talinolol_fvre_rule(self, expression_parser):
        """Test parsing the exact FVre rule from talinolol model"""
        # This is the exact MathML from talinolol_body.xml for FVre
        mathml = '''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:sbml="http://www.sbml.org/sbml/level3/version2/core">
  <apply>
    <minus/>
    <cn sbml:units="l_per_kg"> 1 </cn>
    <apply>
      <plus/>
      <ci> FVgu </ci>
      <ci> FVki </ci>
      <ci> FVli </ci>
      <ci> FVlu </ci>
      <ci> FVve </ci>
      <ci> FVar </ci>
      <ci> FVfo </ci>
    </apply>
  </apply>
</math>'''
        
        # Add required symbols to context
        for var in ['FVgu', 'FVki', 'FVli', 'FVlu', 'FVve', 'FVar', 'FVfo']:
            if var not in expression_parser.context:
                expression_parser.context[var] = sympy.Symbol(var)
        
        try:
            expr = expression_parser.parse(mathml)
            assert isinstance(expr, sympy.Expr)
            # Should be: 1 - (FVgu + FVki + FVli + FVlu + FVve + FVar + FVfo)
            assert isinstance(expr, (sympy.Add, sympy.Mul))
        except Exception as e:
            pytest.fail(f"Failed to parse talinolol FVre rule: {e}")

    def test_parse_talinolol_co_rule(self, expression_parser):
        """Test parsing the exact CO rule from talinolol model"""
        mathml = '''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:sbml="http://www.sbml.org/sbml/level3/version2/core">
  <apply>
    <plus/>
    <apply>
      <times/>
      <ci> BW </ci>
      <ci> COBW </ci>
    </apply>
    <apply>
      <divide/>
      <apply>
        <times/>
        <apply>
          <minus/>
          <ci> HR </ci>
          <ci> HRrest </ci>
        </apply>
        <ci> COHRI </ci>
      </apply>
      <cn sbml:units="s_per_min" type="integer"> 60 </cn>
    </apply>
  </apply>
</math>'''
        
        # Add required symbols to context
        for var in ['BW', 'COBW', 'HR', 'HRrest', 'COHRI']:
            if var not in expression_parser.context:
                expression_parser.context[var] = sympy.Symbol(var)
        
        try:
            expr = expression_parser.parse(mathml)
            assert isinstance(expr, sympy.Expr)
        except Exception as e:
            pytest.fail(f"Failed to parse talinolol CO rule: {e}")

    def test_compare_working_vs_failing_mathml(self, expression_parser):
        """Compare MathML that works vs MathML that fails"""
        # Working MathML (no sbml:units, no xmlns:sbml)
        working_mathml = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <apply>
    <minus/>
    <cn> 1 </cn>
    <ci> x </ci>
  </apply>
</math>'''
        
        # Failing MathML (with sbml:units and xmlns:sbml)
        failing_mathml = '''<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:sbml="http://www.sbml.org/sbml/level3/version2/core">
  <apply>
    <minus/>
    <cn sbml:units="l_per_kg"> 1 </cn>
    <ci> x </ci>
  </apply>
</math>'''
        
        # Both should parse successfully
        expr1 = expression_parser.parse(working_mathml)
        expr2 = expression_parser.parse(failing_mathml)
        
        # Both should produce equivalent expressions
        assert isinstance(expr1, sympy.Expr)
        assert isinstance(expr2, sympy.Expr)
        # They should be mathematically equivalent (1 - x)
        assert expr1.equals(expr2)




