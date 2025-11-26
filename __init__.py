# File: sbml_rust_generator/__init__.py
"""
SBML to Rust Code Generator

A modular, object-oriented framework for converting SBML (Systems Biology Markup Language)
models into optimized Rust code for WebAssembly pharmacokinetic simulations.

Main Components:
    - SbmlToRustConverter: Main facade for converting SBML to Rust
    - SbmlModel: Data model for SBML components
    - SbmlExpressionParser: Parses SBML expressions to SymPy
    - OdeSystemBuilder: Builds ODE system from reactions
    - JacobianBuilder: Computes Jacobian matrices
    - SymbolicOptimizer: Applies CSE and simplification
    - RustCodeGenerator: Generates Rust code from SymPy expressions

Usage:
    >>> from sbml_rust_generator import SbmlToRustConverter
    >>> import json
    >>>
    >>> # Load SBML model data
    >>> with open('model.json') as f:
    ...     model_data = json.load(f)
    >>>
    >>> # Convert to Rust
    >>> converter = SbmlToRustConverter(model_data)
    >>> rust_code = converter.convert("my_model")
    >>>
    >>> # Save to file
    >>> with open('my_model.rs', 'w') as f:
    ...     f.write(rust_code)
"""

from .facade import SbmlToRustConverter
from .models import SbmlModel, Species, Parameter, Compartment, Reaction, FunctionDefinition
from .parsers import SbmlExpressionParser, FunctionInliner
from .symbolic import OdeSystemBuilder, JacobianBuilder, SymbolicOptimizer
from .codegen import RustCodeGenerator, CustomRustCodePrinter, RustBlockGenerator
from .utils import IdentifierValidator

__version__ = '1.0.0'

__all__ = [
    # Main facade
    'SbmlToRustConverter',

    # Data models
    'SbmlModel',
    'Species',
    'Parameter',
    'Compartment',
    'Reaction',
    'FunctionDefinition',

    # Parsers
    'SbmlExpressionParser',
    'FunctionInliner',

    # Symbolic math
    'OdeSystemBuilder',
    'JacobianBuilder',
    'SymbolicOptimizer',

    # Code generation
    'RustCodeGenerator',
    'CustomRustCodePrinter',
    'RustBlockGenerator',

    # Utilities
    'IdentifierValidator',
]
