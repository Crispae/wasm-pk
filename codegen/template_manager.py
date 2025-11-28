# File: sbml_rust_generator/codegen/template_manager.py
"""Manages Rust code templates and file assembly"""

from typing import Dict, List, Tuple


class RustTemplateManager:
    """Manages Rust code templates and assembles complete files"""

    def __init__(self):
        """Initialize template manager"""
        pass

    def generate_struct_fields(
        self,
        species_list: List[str],
        params: Dict[str, float],
        compartments: Dict[str, float],
        species_initial_amounts: Dict[str, float] = None,
    ) -> Tuple[str, str]:
        """Generate struct field definitions

        Args:
            species_list: List of species IDs
            params: Dictionary of parameters
            compartments: Dictionary of compartments
            species_initial_amounts: Dictionary of species initial amounts (optional)

        Returns:
            Tuple of (species_fields, param_fields)
        """
        # Species field (HashMap)
        species_fields = "    pub species: std::collections::HashMap<String, Vec<f64>>,"

        # Parameter and compartment fields
        param_fields = ""
        for p in params:
            param_fields += f"    pub {p}: f64,\n"

        for c in compartments:
            if c not in params:  # Avoid duplicates
                param_fields += f"    pub {c}: f64,\n"

        # Add initial amount fields for each species (optional, for runtime dosing)
        if species_initial_amounts:
            param_fields += "\n    // Initial amounts (optional, for runtime dosing)\n"
            for species_id in species_list:
                param_fields += f"    pub init_{species_id}: Option<f64>,\n"

        return species_fields, param_fields

    def assemble_rust_file(
        self, model_name: str, components: Dict[str, str], wasm: bool = True
    ) -> str:
        """Assemble complete Rust file from components

        Args:
            model_name: Name of the model
            components: Dictionary with component code blocks
            wasm: If True, generate WASM-compatible code. If False, generate native Rust code.

        Returns:
            Complete Rust source code
        """
        # Build template string without f-string interpolation in the Rust code
        template_parts = []

        # Header comment
        if wasm:
            template_parts.append(
                f"// Generated WASM-compatible Rust code from SBML model: {model_name}\n"
            )
        else:
            template_parts.append(
                f"// Generated native Rust code from SBML model: {model_name}\n"
            )
        template_parts.append(
            "// Uses SymPy CSE for optimized derivatives and Jacobian\n\n"
        )

        # Imports
        template_parts.append(
            "use diffsol::{OdeBuilder, OdeSolverMethod, OdeSolverStopReason, Vector};\n"
        )
        if wasm:
            template_parts.append("use wasm_bindgen::prelude::*;\n")
        template_parts.append("use serde::{Deserialize, Serialize};\n")
        template_parts.append("use std::collections::HashMap;\n\n")

        template_parts.append("type M = diffsol::NalgebraMat<f64>;\n")
        template_parts.append("type LS = diffsol::NalgebraLU<f64>;\n\n")

        # Structs
        template_parts.append("#[derive(Serialize, Deserialize)]\n")
        template_parts.append("pub struct SimulationResult {\n")
        template_parts.append(components["species_fields"])
        template_parts.append("\n")
        template_parts.append("    pub time: Vec<f64>,\n")
        template_parts.append("}\n\n")

        template_parts.append("#[derive(Serialize, Deserialize)]\n")
        template_parts.append("pub struct SimulationParams {\n")
        template_parts.append(components["param_fields"])
        template_parts.append("    pub final_time: Option<f64>,\n")
        template_parts.append("}\n\n")

        # WASM-specific console logging setup
        if wasm:
            template_parts.append("#[wasm_bindgen]\n")
            template_parts.append('extern "C" {\n')
            template_parts.append("    #[wasm_bindgen(js_namespace = console)]\n")
            template_parts.append("    fn log(s: &str);\n")
            template_parts.append("}\n\n")
            template_parts.append("macro_rules! console_log {\n")
            template_parts.append(
                "    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))\n"
            )
            template_parts.append("}\n\n")

        # Function signature
        if wasm:
            template_parts.append("#[wasm_bindgen]\n")
        template_parts.append("pub fn run_simulation(params: &str) -> String {\n")

        # Logging statement
        if wasm:
            template_parts.append('    console_log!("Starting simulation...");\n\n')
        else:
            template_parts.append('    println!("Starting simulation...");\n\n')

        # Parameter parsing
        template_parts.append(
            "    let sim_params: SimulationParams = match serde_json::from_str(params) {\n"
        )
        template_parts.append("        Ok(p) => p,\n")
        template_parts.append("        Err(e) => {\n")
        if wasm:
            template_parts.append(
                '            console_log!("Error parsing params: {}", e);\n'
            )
        else:
            template_parts.append(
                '            eprintln!("Error parsing params: {}", e);\n'
            )
        template_parts.append(
            "            return serde_json::to_string(&SimulationResult {\n"
        )
        template_parts.append("                species: HashMap::new(),\n")
        template_parts.append("                time: vec![],\n")
        template_parts.append("            }).unwrap();\n")
        template_parts.append("        }\n")
        template_parts.append("    };\n\n")

        template_parts.append(components["param_extract"])
        template_parts.append("\n")
        template_parts.append(components.get("assignment_rules", ""))
        template_parts.append("\n\n")
        template_parts.append(components.get("initial_assignments", ""))
        template_parts.append("\n\n")
        template_parts.append(components.get("root_fn", ""))

        template_parts.append("    // RHS Closure\n")
        template_parts.append(
            "    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {\n"
        )
        template_parts.append("        // Map species names to y indices\n")
        template_parts.append(components["species_extract"])
        template_parts.append("\n\n")
        template_parts.append("        // Temporary variables (CSE)\n")
        template_parts.append(components["temp_vars"])
        template_parts.append("\n\n")
        template_parts.append("        // Derivatives\n")
        template_parts.append(components["rhs_block"])
        template_parts.append("\n")
        template_parts.append("    };\n\n")

        template_parts.append("    // Jacobian Closure (Matrix-Vector Product)\n")
        template_parts.append(
            "    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {\n"
        )
        template_parts.append("        for i in 0..jv.len() { jv[i] = 0.0; }\n\n")
        template_parts.append("        // Map species names to y indices\n")
        template_parts.append(components["species_extract"])
        template_parts.append("\n\n")
        template_parts.append("        // Temporary variables (CSE)\n")
        template_parts.append(components["temp_vars"])
        template_parts.append("\n\n")
        template_parts.append("        // Jacobian-Vector Product\n")
        template_parts.append(components["jac_block"])
        template_parts.append("\n")
        template_parts.append("    };\n\n")

        # Init function with species initial values
        init_block = components.get("init_block", "")
        if init_block:
            template_parts.append(init_block)
        else:
            # Fallback to old behavior
            template_parts.append(
                "    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {\n"
            )
            template_parts.append(
                f"        for i in 0..{components['n_species']} {{ y[i] = 0.0; }}\n"
            )
            template_parts.append("    };\n\n")

        template_parts.append("    let problem = OdeBuilder::<M>::new()\n")
        template_parts.append("        .rhs_implicit(rhs, jac)\n")
        template_parts.append(f"        .init(init, {components['n_species']})\n")
        root_reg = components.get("root_registration", "")
        if root_reg:
            template_parts.append("        ")
            template_parts.append(root_reg)
            template_parts.append("\n")
        template_parts.append("        .build()\n")
        template_parts.append("        .unwrap();\n\n")

        template_parts.append("    let mut solver = problem.bdf::<LS>().unwrap();\n")
        template_parts.append("    let mut time = Vec::new();\n\n")

        template_parts.append("    // Initialize result vectors\n")
        template_parts.append(components["result_vectors_init"])
        template_parts.append("\n\n")
        template_parts.append(components["initial_pushes"])
        template_parts.append("\n")
        template_parts.append("    time.push(0.0);\n\n")

        template_parts.append(
            "    let final_time = sim_params.final_time.unwrap_or(24.0);\n"
        )
        template_parts.append("    solver.set_stop_time(final_time).unwrap();\n")
        template_parts.append("    loop {\n")
        template_parts.append("        match solver.step() {\n")
        template_parts.append(
            "            Ok(OdeSolverStopReason::InternalTimestep) => {\n"
        )
        template_parts.append(components["loop_pushes"])
        template_parts.append("\n")
        template_parts.append("                time.push(solver.state().t);\n")
        template_parts.append("            },\n")
        event_handling = components.get("event_handling", "")
        if event_handling:
            template_parts.append(event_handling)
        template_parts.append(
            "            Ok(OdeSolverStopReason::TstopReached) => break,\n"
        )
        template_parts.append(
            "            Ok(OdeSolverStopReason::RootFound(_)) => break,\n"
        )
        template_parts.append('            Err(_) => panic!("Solver Error"),\n')
        template_parts.append("        }\n")
        template_parts.append("    }\n\n")

        template_parts.append("    let mut species_map = HashMap::new();\n")
        template_parts.append(components["map_inserts"])
        template_parts.append("\n\n")

        template_parts.append("    let result = SimulationResult {\n")
        template_parts.append("        time,\n")
        template_parts.append("        species: species_map,\n")
        template_parts.append("    };\n\n")

        template_parts.append("    serde_json::to_string(&result).unwrap()\n")
        template_parts.append("}\n\n")

        # Add metadata functions
        metadata_functions = components.get("metadata_functions", "")
        if metadata_functions:
            template_parts.append(metadata_functions)

        return "".join(template_parts)

    def create_minimal_template(self, model_name: str) -> str:
        """Create a minimal Rust template for testing

        Args:
            model_name: Name of the model

        Returns:
            Minimal Rust code template
        """
        return f"""// Minimal SBML model: {model_name}

pub fn hello() {{
    println!("Hello from {model_name}!");
}}
"""
