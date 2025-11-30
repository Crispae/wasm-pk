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

# Check if we have a cached project
if [ -d "/build/cache/sbml_wasm_project" ]; then
    echo "Using cached project dependencies..."
    cp -r /build/cache/sbml_wasm_project/* $TEMP_DIR/
else
    echo "Creating new project (no cache found)..."
    cd $TEMP_DIR
    cargo new --lib $PROJECT_NAME
    cd $PROJECT_NAME
    
    # Configure Cargo.toml
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
fi

cd $TEMP_DIR

# Copy the input file to src/lib.rs
cp "$INPUT_FILE" src/lib.rs

# Build with wasm-pack to a temporary output directory
echo "Building WASM package..."
TEMP_OUTPUT="/tmp/wasm_output"
rm -rf $TEMP_OUTPUT
wasm-pack build --target web --out-dir "$TEMP_OUTPUT" --out-name "sbml_model" 2>&1

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "ERROR: wasm-pack build failed!"
    exit 1
fi

if [ ! -d "$TEMP_OUTPUT" ] || [ -z "$(ls -A $TEMP_OUTPUT)" ]; then
    echo "ERROR: Build output directory is empty or doesn't exist!"
    exit 1
fi

# Copy the output to the final destination
echo "Copying output to $OUTPUT_DIR..."
mkdir -p "$OUTPUT_DIR"
cp -r "$TEMP_OUTPUT"/* "$OUTPUT_DIR"/

# Copy UI files to the output directory
echo "Copying UI files..."
if [ -f "/app/index.html" ]; then
    cp "/app/index.html" "$OUTPUT_DIR"/
    echo "✓ Copied index.html"
else
    echo "⚠ Warning: index.html not found in /app/"
fi

# Create a release manifest
cat > "$OUTPUT_DIR/RELEASE.md" <<EOF
# SBML WASM Package Release

Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Contents

- \`sbml_model_bg.wasm\` - WebAssembly binary
- \`sbml_model.js\` - JavaScript bindings
- \`sbml_model.d.ts\` - TypeScript definitions
- \`package.json\` - NPM package metadata
- \`index.html\` - Web UI for simulation
- \`RELEASE.md\` - This file

## Usage

### Option 1: Open Directly
Open \`index.html\` in a modern web browser that supports WebAssembly.

### Option 2: Serve with HTTP Server
\`\`\`bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server -p 8000

# Using PHP
php -S localhost:8000
\`\`\`

Then navigate to: http://localhost:8000/

## Requirements

- Modern web browser with WebAssembly support
- JavaScript enabled

EOF

echo "Build complete! Output in $OUTPUT_DIR"
echo ""
echo "Release package contains:"
echo "  - WASM module and JavaScript bindings"
echo "  - Web UI (index.html)"
echo "  - Release manifest (RELEASE.md)"
