# WASM Test Suite

This directory contains tests to verify that the compiled WASM package can properly execute pharmacokinetic simulations.

## Prerequisites

- Node.js (v14 or later)
- Compiled WASM package in `../pkg/`

## Running Tests

```bash
# Install dependencies
npm install

# Run the test suite
npm test
```

## What the Tests Do

The test suite performs the following validations:

1. **WASM Module Loading**: Verifies the WASM module can be loaded successfully
2. **Single Dose Simulation**: Runs a simulation with a single dose at t=0
3. **Multiple Dose Simulation**: Runs a simulation with multiple doses at different time points
4. **Output Validation**:
   - Checks that time series data is present
   - Verifies species concentration data exists
   - Ensures all data arrays have consistent lengths
   - Validates time is monotonically increasing
   - Confirms extended simulations have appropriate timelines

## Expected Output

A successful test run will show:
- ✅ WASM module loaded successfully
- ✅ Simulation completed with time points and species data
- ✅ All validation checks passed
- 🎉 All tests PASSED!

## Test Parameters

The tests use sample parameters for the euromix pharmacokinetic model including:
- Body weight (BW)
- Tissue volumes and partition coefficients
- Metabolic parameters
- Dosing schedules

You can modify `test_wasm.js` to adjust test parameters or add additional test cases.

## Troubleshooting

If tests fail, check:
1. The WASM package was built successfully in `../pkg/`
2. The package includes all required files (`.wasm`, `.js`, `package.json`)
3. Node.js version is compatible (v14+)
4. All model parameters are provided correctly
