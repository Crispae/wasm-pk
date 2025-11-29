"""Tests for assignment rule processing functionality"""

import pytest
import sympy
from symbolic.assignment_processor import AssignmentRuleProcessor
from parsers.expression_parser import SbmlExpressionParser


class TestAssignmentRuleProcessor:
    """Tests for AssignmentRuleProcessor class"""

    @pytest.fixture
    def parser(self):
        """Create an expression parser for testing"""
        context = {
            'x': sympy.Symbol('x'),
            'y': sympy.Symbol('y'),
            'k1': sympy.Symbol('k1'),
            'k2': sympy.Symbol('k2'),
            'V1': sympy.Symbol('V1'),
            'V2': sympy.Symbol('V2'),
            't': sympy.Symbol('t'),
        }
        return SbmlExpressionParser(context, {})

    @pytest.fixture
    def processor(self, parser):
        """Create an assignment rule processor for testing"""
        return AssignmentRuleProcessor(parser)

    def test_process_simple_assignment_rules(self, processor):
        """Test processing simple assignment rules"""
        model_data = {
            "assignmentRules": {
                "rule1": {
                    "variable": "V1",
                    "math": "k1 * x"
                }
            }
        }
        
        result = processor.process(model_data)
        
        assert len(result) == 1
        assert result[0][0] == "V1"
        assert isinstance(result[0][1], sympy.Expr)

    def test_process_multiple_independent_rules(self, processor):
        """Test processing multiple independent assignment rules"""
        model_data = {
            "assignmentRules": {
                "rule1": {
                    "variable": "V1",
                    "math": "k1 * x"
                },
                "rule2": {
                    "variable": "V2",
                    "math": "k2 * y"
                }
            }
        }
        
        result = processor.process(model_data)
        
        assert len(result) == 2
        variables = [var for var, _ in result]
        assert "V1" in variables
        assert "V2" in variables

    def test_sort_assignment_rules_with_dependencies(self, processor):
        """Test sorting assignment rules with dependencies"""
        assignment_rules = {
            "rule1": {
                "variable": "V1",
                "math": "k1 * x"
            },
            "rule2": {
                "variable": "V2",
                "math": "V1 + k2"
            }
        }
        
        result = processor.sort_assignment_rules(assignment_rules)
        
        # V1 should come before V2 (V2 depends on V1)
        variables = [var for var, _ in result]
        assert variables.index("V1") < variables.index("V2")

    def test_sort_assignment_rules_complex_dependencies(self, processor):
        """Test sorting assignment rules with complex dependency chain"""
        assignment_rules = {
            "rule1": {
                "variable": "V1",
                "math": "k1 * x"
            },
            "rule2": {
                "variable": "V2",
                "math": "V1 + k2"
            },
            "rule3": {
                "variable": "V3",
                "math": "V2 * 2"
            }
        }
        
        result = processor.sort_assignment_rules(assignment_rules)
        
        variables = [var for var, _ in result]
        # V1 should come first, then V2, then V3
        assert variables.index("V1") < variables.index("V2")
        assert variables.index("V2") < variables.index("V3")

    def test_sort_assignment_rules_circular_dependency(self, processor):
        """Test that circular dependencies raise ValueError"""
        assignment_rules = {
            "rule1": {
                "variable": "V1",
                "math": "V2 + k1"
            },
            "rule2": {
                "variable": "V2",
                "math": "V1 + k2"
            }
        }
        
        with pytest.raises(ValueError, match="Circular dependency"):
            processor.sort_assignment_rules(assignment_rules)

    def test_process_empty_assignment_rules(self, processor):
        """Test processing empty assignment rules"""
        model_data = {
            "assignmentRules": {}
        }
        
        result = processor.process(model_data)
        
        assert result == []

    def test_process_assignment_rules_missing_key(self, processor):
        """Test processing when assignmentRules key is missing"""
        model_data = {}
        
        result = processor.process(model_data)
        
        assert result == []

    def test_build_dependency_graph(self, processor):
        """Test building dependency graph"""
        assignment_rules = {
            "rule1": {
                "variable": "V1",
                "math": "k1 * x"
            },
            "rule2": {
                "variable": "V2",
                "math": "V1 + k2"
            }
        }
        
        parsed_rules = {}
        for rule_id, rule in assignment_rules.items():
            variable = rule.get("variable")
            math_expr = rule.get("math", "0")
            expr = processor.parser.parse(math_expr)
            parsed_rules[variable] = expr
        
        dependencies = processor._build_dependency_graph(parsed_rules)
        
        assert "V1" in dependencies
        assert "V2" in dependencies
        # V2 depends on V1
        assert "V1" in dependencies["V2"]
        # V1 has no dependencies (only depends on k1 and x, not other assignment variables)
        assert len(dependencies["V1"]) == 0 or "V1" not in dependencies["V1"]

    def test_topological_sort_simple(self, processor):
        """Test topological sort with simple dependencies"""
        dependencies = {
            "V1": set(),
            "V2": {"V1"},
            "V3": {"V2"}
        }
        
        result = processor._topological_sort(dependencies)
        
        assert result.index("V1") < result.index("V2")
        assert result.index("V2") < result.index("V3")

    def test_topological_sort_circular(self, processor):
        """Test topological sort detects circular dependencies"""
        dependencies = {
            "V1": {"V2"},
            "V2": {"V1"}
        }
        
        with pytest.raises(ValueError, match="Circular dependency"):
            processor._topological_sort(dependencies)

    def test_get_assigned_variables(self, processor):
        """Test getting set of assigned variables"""
        assignment_rules = {
            "rule1": {
                "variable": "V1",
                "math": "k1 * x"
            },
            "rule2": {
                "variable": "V2",
                "math": "k2 * y"
            }
        }
        
        result = processor.get_assigned_variables(assignment_rules)
        
        assert "V1" in result
        assert "V2" in result
        assert len(result) == 2

    def test_process_assignment_rule_with_invalid_math(self, processor):
        """Test processing assignment rule with invalid math expression"""
        model_data = {
            "assignmentRules": {
                "rule1": {
                    "variable": "V1",
                    "math": "invalid_expression_!!!"
                }
            }
        }
        
        # Should handle gracefully, using default value
        result = processor.process(model_data)
        # Should still return a result, but with default value
        assert len(result) == 1






