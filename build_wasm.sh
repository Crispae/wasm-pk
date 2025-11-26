#!/bin/bash
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: build_wasm.sh <input_rust_file> <output_dir>"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_DIR=$2

# Create a temporary project directory in /tmp (not in mounted volume)
TEMP_DIR="/tmp/sbml_wasm_build"
PROJECT_NAME="sbml_wasm_project"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR
cd $TEMP_DIR

cargo new --lib $PROJECT_NAME
cd $PROJECT_NAME

# Configure Cargo.toml - replace the entire file
cat > Cargo.toml <<EOF
[package]
name = "sbml_wasm_project"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
diffsol = "0.6.3"
getrandom = { version = "0.2", features = ["js"] }
EOF

# Copy the input file to src/lib.rs
cp "$INPUT_FILE" src/lib.rs

# Build with wasm-pack to a temporary output directory
echo "Building WASM package..."
TEMP_OUTPUT="/tmp/wasm_output"
rm -rf $TEMP_OUTPUT
wasm-pack build --target web --out-dir "$TEMP_OUTPUT" --out-name "sbml_model"

# Copy the output to the final destination
echo "Copying output to $OUTPUT_DIR..."
mkdir -p "$OUTPUT_DIR"
cp -r "$TEMP_OUTPUT"/* "$OUTPUT_DIR"/

echo "Build complete! Output in $OUTPUT_DIR"
