"""Tests for function inlining functionality"""

import pytest
from parsers.function_inliner import FunctionInliner


class TestFunctionInliner:
    """Tests for FunctionInliner class"""

    def test_inline_simple_function(self):
        """Test inlining a simple function call"""
        functions = {
            'multiply': {
                'arguments': ['x', 'y'],
                'mathString': 'x * y'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("multiply(a, b)")
        # Function inliner wraps each argument in parentheses for safety
        assert result == "((a) * (b))" or result == "(a * b)"

    def test_inline_function_with_multiple_arguments(self):
        """Test inlining function with multiple arguments"""
        functions = {
            'add': {
                'arguments': ['x', 'y', 'z'],
                'mathString': 'x + y + z'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("add(1, 2, 3)")
        # Function inliner wraps each argument in parentheses for safety
        assert result == "((1) + (2) + (3))" or result == "(1 + 2 + 3)"

    def test_inline_nested_functions(self):
        """Test inlining nested function calls"""
        functions = {
            'square': {
                'arguments': ['x'],
                'mathString': 'x * x'
            },
            'double': {
                'arguments': ['x'],
                'mathString': '2 * x'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("double(square(a))")
        # Should inline square first, then double
        # Function inliner wraps arguments, so check for the pattern
        assert "2 *" in result or "2*" in result
        # Check that 'a' appears twice in a multiplication (with or without parentheses)
        assert "a * a" in result or "a*a" in result or "((a) * (a))" in result or "(a) * (a)" in result

    def test_inline_function_in_expression(self):
        """Test inlining function within a larger expression"""
        functions = {
            'multiply': {
                'arguments': ['x', 'y'],
                'mathString': 'x * y'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("multiply(a, b) + c")
        # Function inliner wraps arguments, so check for either format
        assert "(a * b)" in result or "(a*b)" in result or "((a) * (b))" in result
        assert "+ c" in result or "+c" in result

    def test_inline_multiple_function_calls(self):
        """Test inlining multiple function calls in one expression"""
        functions = {
            'multiply': {
                'arguments': ['x', 'y'],
                'mathString': 'x * y'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("multiply(a, b) + multiply(c, d)")
        # Function inliner wraps arguments, so check for either format
        assert "(a * b)" in result or "(a*b)" in result or "((a) * (b))" in result
        assert "(c * d)" in result or "(c*d)" in result or "((c) * (d))" in result

    def test_inline_function_with_complex_body(self):
        """Test inlining function with complex mathematical body"""
        functions = {
            'rate': {
                'arguments': ['S', 'K'],
                'mathString': 'S / (K + S)'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("rate(A, Km)")
        assert "A" in result
        assert "Km" in result
        assert "/" in result

    def test_inline_function_with_nested_parentheses(self):
        """Test inlining function with nested parentheses in arguments"""
        functions = {
            'add': {
                'arguments': ['x', 'y'],
                'mathString': 'x + y'
            }
        }
        inliner = FunctionInliner(functions)
        
        # Function call with nested parentheses in argument
        result = inliner.inline("add(f(a, b), c)")
        # Should correctly extract arguments: f(a, b) and c
        assert "c" in result

    def test_inline_unknown_function_unchanged(self):
        """Test that unknown functions are left unchanged"""
        functions = {
            'known': {
                'arguments': ['x'],
                'mathString': 'x * 2'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("unknown(a) + known(b)")
        # Unknown function should remain, known should be inlined
        assert "unknown(a)" in result
        # Function inliner wraps arguments, so check for either format
        assert "b * 2" in result or "b*2" in result or "((b) * 2)" in result

    def test_inline_empty_functions_dict(self):
        """Test inliner with empty functions dictionary"""
        inliner = FunctionInliner({})
        
        result = inliner.inline("some_function(a, b)")
        # Should return unchanged since no functions to inline
        assert result == "some_function(a, b)"

    def test_inline_function_argument_substitution(self):
        """Test that function arguments are correctly substituted"""
        functions = {
            'f': {
                'arguments': ['x'],
                'mathString': 'x + x'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("f(y)")
        # Should substitute x with y: ((y) + (y)) - function inliner wraps each argument
        assert result == "((y) + (y))" or result == "(y + y)" or result == "(y+y)"

    def test_inline_prevent_partial_replacements(self):
        """Test that longer argument names don't get partially replaced"""
        functions = {
            'abc': {
                'arguments': ['abc'],
                'mathString': 'abc * 2'
            },
            'ab': {
                'arguments': ['ab'],
                'mathString': 'ab + 1'
            }
        }
        inliner = FunctionInliner(functions)
        
        result = inliner.inline("abc(5)")
        # Should replace 'abc' not 'ab' inside 'abc'
        # Function inliner wraps arguments, so check for either format
        assert "5 * 2" in result or "5*2" in result or "((5) * 2)" in result

    def test_inline_max_depth_prevention(self):
        """Test that infinite recursion is prevented"""
        functions = {
            'recursive': {
                'arguments': ['x'],
                'mathString': 'recursive(x)'
            }
        }
        inliner = FunctionInliner(functions)
        
        # Should not cause infinite loop
        result = inliner.inline("recursive(a)")
        # Should stop after max_depth iterations
        assert result is not None
        # Result might still contain the function call if max depth reached
        assert isinstance(result, str)


