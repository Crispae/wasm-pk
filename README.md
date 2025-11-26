# SBML Rust Generator

A modular, object-oriented framework for converting SBML (Systems Biology Markup Language) models into optimized Rust code for WebAssembly pharmacokinetic simulations.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for parsing, symbolic math, and code generation
- **SymPy Integration**: Symbolic differentiation and automatic Jacobian computation
- **CSE Optimization**: Common Subexpression Elimination for efficient code
- **Sparse Jacobian**: Automatic detection and optimization of sparse Jacobian matrices
- **WASM Compatible**: Generates Rust code ready for WebAssembly compilation
- **Type-Safe**: Uses Python dataclasses for type-safe model representation

## Architecture

```
sbml_rust_generator/
├── core/              # Abstract base classes
│   └── base.py       # Parser, CodeGenerator, ModelProcessor interfaces
├── models/            # Data models
│   └── sbml_model.py # Species, Parameter, Compartment, Reaction, etc.
├── parsers/           # Expression parsing
│   ├── expression_parser.py  # SBML to SymPy conversion
│   └── function_inliner.py   # User-defined function inlining
├── symbolic/          # Symbolic mathematics
│   ├── ode_builder.py       # ODE system construction
│   ├── jacobian_builder.py  # Jacobian computation
│   └── optimizer.py         # CSE and simplification
├── codegen/           # Code generation
│   ├── rust_printer.py      # Custom Rust printer for SymPy
│   ├── code_generator.py    # Code block generation
│   └── template_manager.py  # Rust file assembly
├── utils/             # Utilities
│   └── validators.py  # Identifier validation
└── facade.py          # Main API (SbmlToRustConverter)
```

## Installation

```bash
# Ensure you have the required dependencies
pip install sympy

# The package is ready to use in-place
cd d:\Rust\parsing
```

## Quick Start

```python
from sbml_rust_generator import SbmlToRustConverter
from sbmlParser.parser import ParseSBMLFile

# 1. Parse SBML file
model_data = ParseSBMLFile("path/to/model.sbml")

# 2. Create converter
converter = SbmlToRustConverter(model_data)

# 3. Get model information
info = converter.get_model_info()
print(f"Species: {info['num_species']}")
print(f"Reactions: {info['num_reactions']}")

# 4. Validate model
if converter.validate_model():
    print("Model is valid")

# 5. Convert to Rust
rust_code = converter.convert("my_model")

# 6. Save output
with open("my_model.rs", "w") as f:
    f.write(rust_code)
```

## Docker WASM Build

After generating Rust code, you can compile it to WebAssembly using Docker.

### Prerequisites
- Docker installed and running
- Generated Rust file (e.g., from the Jupyter notebook)

### Building the Docker Image

```bash
docker build -t sbml-wasm .
```

### Running the Container

**PowerShell (Windows)**
```powershell
docker run -v ${PWD}:/app sbml-wasm /app/Notebooks/output/euromix_model.rs /app/pkg
```

**Bash/Linux/Mac**
```bash
docker run -v $(pwd):/app sbml-wasm /app/Notebooks/output/euromix_model.rs /app/pkg
```

### Arguments
1. First argument: Path to the input Rust file (relative to /app in container)
2. Second argument: Output directory for the WASM package (relative to /app in container)

### Output
The WASM package will be created in the specified output directory with:
- `sbml_model_bg.wasm` - The compiled WebAssembly binary
- `sbml_model.js` - JavaScript bindings
- `sbml_model.d.ts` - TypeScript definitions
- `package.json` - NPM package metadata

### Example Workflow

1. Generate Rust code using the notebook
2. Build Docker image: `docker build -t sbml-wasm .`
3. Run the build:
   - **PowerShell**: `docker run -v ${PWD}:/app sbml-wasm /app/Notebooks/output/euromix_model.rs /app/pkg`
   - **Bash**: `docker run -v $(pwd):/app sbml-wasm /app/Notebooks/output/euromix_model.rs /app/pkg`
4. The WASM package will be in the `pkg/` directory

## Usage Examples

### Basic Conversion

```python
from sbml_rust_generator import SbmlToRustConverter

# Load model data (from JSON or SBML parser)
model_data = {
    "species": {...},
    "parameters": {...},
    "reactions": {...}
}

converter = SbmlToRustConverter(model_data)
rust_code = converter.convert("pharmacokinetic_model")
```

### Working with Components

```python
from sbml_rust_generator import (
    SbmlExpressionParser,
    OdeSystemBuilder,
    JacobianBuilder,
    SymbolicOptimizer
)
import sympy

# Create symbols
species_syms = {
    "A": sympy.Symbol("A"),
    "B": sympy.Symbol("B")
}

# Parse expression
parser = SbmlExpressionParser(species_syms, {})
expr = parser.parse("k1 * A - k2 * B")

# Build ODE system
species_map = {"A": 0, "B": 1}
ode_builder = OdeSystemBuilder(species_map, parser)
ode_system = ode_builder.build_ode_system(reactions)

# Compute Jacobian
jac_builder = JacobianBuilder(species_syms, ["A", "B"])
jac_elements, indices = jac_builder.compute_sparse_jacobian(ode_system)

# Optimize
optimizer = SymbolicOptimizer(optimization_level=2)
replacements, reduced = optimizer.optimize(ode_system + jac_elements)
```

## API Reference

### Main Classes

#### `SbmlToRustConverter`

Main facade for SBML to Rust conversion.

**Methods:**
- `__init__(model_data: Dict)` - Initialize with SBML model data
- `convert(model_name: str) -> str` - Convert to Rust code
- `get_model_info() -> Dict` - Get model statistics
- `validate_model() -> bool` - Validate model consistency

#### `SbmlModel`

Data model for SBML components.

**Methods:**
- `from_dict(data: Dict) -> SbmlModel` - Create from dictionary
- `to_dict() -> Dict` - Convert to dictionary
- `validate() -> bool` - Validate model

#### `SbmlExpressionParser`

Parse SBML expressions to SymPy.

**Methods:**
- `parse(expression: str) -> sympy.Expr` - Parse expression

#### `OdeSystemBuilder`

Build ODE system from reactions.

**Methods:**
- `build_ode_system(reactions: Dict) -> List[sympy.Expr]` - Build ODEs

#### `JacobianBuilder`

Compute Jacobian matrices.

**Methods:**
- `compute_jacobian(ode_system: List) -> List[List]` - Full Jacobian
- `compute_sparse_jacobian(ode_system: List) -> Tuple` - Sparse Jacobian

#### `SymbolicOptimizer`

Optimize expressions with CSE.

**Methods:**
- `optimize(expressions: List) -> Tuple` - Apply CSE
- `optimize_combined(ode, jac) -> Tuple` - Optimize ODE and Jacobian together

## Testing

Run the test suite:

```bash
python test_refactored.py
```

The test will:
1. Load an SBML model (euromix.sbml)
2. Convert it to Rust code
3. Validate the output
4. Compare with the original implementation

## Benefits Over Monolithic Design

### Before (Monolithic)
- 576 lines in single file
- Tightly coupled components
- Difficult to test individual parts
- Hard to extend or reuse

### After (OOP/Modular)
- ~1500 lines across 15 well-organized modules
- Loose coupling with dependency injection
- Each component independently testable
- Easy to add new backends (C, Julia, Python)
- Clear separation of concerns

## Design Patterns Used

1. **Facade Pattern**: `SbmlToRustConverter` provides simple interface
2. **Strategy Pattern**: Abstract base classes allow swapping implementations
3. **Builder Pattern**: Step-by-step construction of Rust code
4. **Template Method**: Code generation follows consistent pipeline

## Performance

The refactored version maintains the same performance as the original:
- CSE optimization reduces redundant calculations
- Sparse Jacobian minimizes memory usage
- Generated Rust code is identical in efficiency

## Examples

### euromix Model Results

```
Species: 14
Parameters: 42
Compartments: 13
Reactions: 22
Functions: 3
Jacobian sparsity: 34/196 non-zero (17.3%)
CSE temporaries: 74
Generated code: ~18,600 chars
```

## Contributing

To add a new backend (e.g., C code generation):

1. Implement `CodeGenerator` interface
2. Create printer in `codegen/c_printer.py`
3. Create template manager in `codegen/c_template.py`
4. Update facade to support new backend



