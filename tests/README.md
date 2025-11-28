# Test Suite for SBML Rust Generator

This directory contains comprehensive tests for all components of the SBML to Rust code generator.

## Test Structure

The test suite is organized into the following files:

- **`test_parsing.py`**: Tests for SBML file parsing (`sbmlParser/parser.py`)
  - Parameter parsing
  - Species parsing
  - Compartment parsing
  - Function parsing
  - Reaction parsing
  - Rule parsing (assignment, rate, algebraic)
  - Event parsing
  - Initial assignment parsing
  - Full SBML file parsing

- **`test_expression_parser.py`**: Tests for mathematical expression parsing
  - Simple arithmetic operations
  - Mathematical functions (exp, log, sin, sqrt, etc.)
  - Piecewise expressions
  - Logical operators
  - Unit removal
  - MathML parsing
  - Custom function handling
  - Nested function calls

- **`test_function_inliner.py`**: Tests for function inlining
  - Simple function inlining
  - Nested function calls
  - Multiple function calls
  - Complex function bodies
  - Argument substitution
  - Recursion prevention

- **`test_code_generation.py`**: Tests for Rust code generation
  - Expression to Rust code conversion
  - Temporary variable generation
  - Derivative code generation
  - Jacobian code generation
  - Species/parameter extraction
  - Assignment rule code generation
  - Piecewise expression handling

- **`test_ode_builder.py`**: Tests for ODE system building
  - Simple reactions
  - Reversible reactions
  - Multiple reactions
  - Complex rate laws
  - Stoichiometry handling

- **`test_assignment_processor.py`**: Tests for assignment rule processing
  - Simple assignment rules
  - Dependency resolution
  - Topological sorting
  - Circular dependency detection
  - Complex dependency chains

- **`test_integration.py`**: Integration tests for the complete pipeline
  - Full SBML to Rust conversion
  - Models with assignment rules
  - Models with functions
  - Complex rate laws

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_parsing.py
pytest tests/test_expression_parser.py
pytest tests/test_code_generation.py
```

### Run Specific Test Class

```bash
pytest tests/test_parsing.py::TestParseParameterAssignment
```

### Run Specific Test Function

```bash
pytest tests/test_parsing.py::TestParseParameterAssignment::test_parse_parameter_with_all_fields
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests (Skip Slow Tests)

```bash
pytest -m "not slow"
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `sample_sbml_file`: Creates a minimal valid SBML file
- `sample_model_data`: Parsed model data from sample SBML file
- `expression_parser`: Expression parser with basic context
- `simple_reaction_data`: Sample reaction data
- `assignment_rules_data`: Sample assignment rules

## Writing New Tests

When adding new functionality, follow these guidelines:

1. **Test Structure**: Use descriptive test class and function names
   ```python
   class TestNewFeature:
       def test_feature_basic_case(self):
           # Test basic functionality
   ```

2. **Use Fixtures**: Leverage existing fixtures from `conftest.py` when possible

3. **Test Edge Cases**: Include tests for:
   - Empty inputs
   - Invalid inputs
   - Boundary conditions
   - Error cases

4. **Test Documentation**: Add docstrings explaining what each test verifies

5. **Assertions**: Use clear, specific assertions with helpful error messages

## Test Coverage Goals

- **Parsing**: 100% coverage of all parsing functions
- **Expression Parsing**: 100% coverage of expression parser methods
- **Code Generation**: 100% coverage of code generation methods
- **Integration**: Test complete pipeline with various model types

## Notes

- Some tests may be skipped if optional dependencies (like `sbmlmath`) are not available
- Tests use temporary files that are automatically cleaned up
- Integration tests may take longer to run than unit tests



