# SBML WASM Package Release

Generated: 2025-11-30 00:39:27 UTC

## Contents

- `sbml_model_bg.wasm` - WebAssembly binary
- `sbml_model.js` - JavaScript bindings
- `sbml_model.d.ts` - TypeScript definitions
- `package.json` - NPM package metadata
- `index.html` - Web UI for simulation
- `RELEASE.md` - This file

## Usage

### Option 1: Open Directly
Open `index.html` in a modern web browser that supports WebAssembly.

### Option 2: Serve with HTTP Server
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server -p 8000

# Using PHP
php -S localhost:8000
```

Then navigate to: http://localhost:8000/

## Requirements

- Modern web browser with WebAssembly support
- JavaScript enabled

