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
        compartments: Dict[str, float]
    ) -> Tuple[str, str]:
        """Generate struct field definitions

        Args:
            species_list: List of species IDs
            params: Dictionary of parameters
            compartments: Dictionary of compartments

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

        return species_fields, param_fields

    def assemble_rust_file(
        self,
        model_name: str,
        components: Dict[str, str]
    ) -> str:
        """Assemble complete Rust file from components

        Args:
            model_name: Name of the model
            components: Dictionary with component code blocks

        Returns:
            Complete Rust source code
        """
        # Build template string without f-string interpolation in the Rust code
        template_parts = [
            f"// Generated WASM-compatible Rust code from SBML model: {model_name}\n",
            "// Uses SymPy CSE for optimized derivatives and Jacobian\n\n",
            "use diffsol::{OdeBuilder, OdeSolverMethod, OdeSolverStopReason, Vector};\n",
            "use wasm_bindgen::prelude::*;\n",
            "use serde::{Deserialize, Serialize};\n",
            "use std::collections::HashMap;\n\n",
            "type M = diffsol::NalgebraMat<f64>;\n",
            "type LS = diffsol::NalgebraLU<f64>;\n\n",
            "#[derive(Serialize, Deserialize)]\n",
           "pub struct SimulationResult {\n",
            components["species_fields"], "\n",
            "    pub time: Vec<f64>,\n",
            "}\n\n",
            "#[derive(Serialize, Deserialize)]\n",
            "pub struct SimulationParams {\n",
            components["param_fields"],
            "    pub final_time: Option<f64>,\n",
            "}\n\n",
            "#[wasm_bindgen]\n",
            'extern "C" {\n',
            "    #[wasm_bindgen(js_namespace = console)]\n",
            "    fn log(s: &str);\n",
            "}\n\n",
            "macro_rules! console_log {\n",
            "    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))\n",
           "}\n\n",
            "#[wasm_bindgen]\n",
            "pub fn run_simulation(params: &str) -> String {\n",
            '    console_log!("Starting simulation...");\n\n',
            "    let sim_params: SimulationParams = match serde_json::from_str(params) {\n",
            "        Ok(p) => p,\n",
            "        Err(e) => {\n",
            '            console_log!("Error parsing params: {}", e);\n',
            "            return serde_json::to_string(&SimulationResult {\n",
            "                species: HashMap::new(),\n",
            "                time: vec![],\n",
            "            }).unwrap();\n",
            "        }\n",
            "    };\n\n",
            components["param_extract"], "\n",
            components.get("assignment_rules", ""), "\n\n",
            components.get("initial_assignments", ""), "\n\n",
            components.get("root_fn", ""),
            "    // RHS Closure\n",
            "    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {\n",
            "        // Map species names to y indices\n",
            components["species_extract"], "\n\n",
            "        // Temporary variables (CSE)\n",
            components["temp_vars"], "\n\n",
            "        // Derivatives\n",
            components["rhs_block"], "\n",
            "    };\n\n",
            "    // Jacobian Closure (Matrix-Vector Product)\n",
            "    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {\n",
            "        for i in 0..jv.len() { jv[i] = 0.0; }\n\n",
            "        // Map species names to y indices\n",
            components["species_extract"], "\n\n",
            "        // Temporary variables (CSE)\n",
            components["temp_vars"], "\n\n",
            "        // Jacobian-Vector Product\n",
            components["jac_block"], "\n",
            "    };\n\n",
            "    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {\n",
            f"        for i in 0..{components['n_species']} {{ y[i] = 0.0; }}\n",
            "    };\n\n",
            "    let problem = OdeBuilder::<M>::new()\n",
            "        .rhs_implicit(rhs, jac)\n",
            f"        .init(init, {components['n_species']})\n",
            "        ", components.get("root_registration", ""), "\n",
            "        .build()\n",
            "        .unwrap();\n\n",
            "    let mut solver = problem.bdf::<LS>().unwrap();\n",
            "    let mut time = Vec::new();\n\n",
            "    // Initialize result vectors\n",
            components["result_vectors_init"], "\n\n",
            components["initial_pushes"], "\n",
            "    time.push(0.0);\n\n",
            "    let final_time = sim_params.final_time.unwrap_or(24.0);\n",
            "    solver.set_stop_time(final_time).unwrap();\n",
            "    loop {\n",
            "        match solver.step() {\n",
            "            Ok(OdeSolverStopReason::InternalTimestep) => {\n",
            components["loop_pushes"], "\n",
            "                time.push(solver.state().t);\n",
            "            },\n",
            components.get("event_handling", ""),
            "            Ok(OdeSolverStopReason::TstopReached) => break,\n",
            '            Err(_) => panic!("Solver Error"),\n',
            "        }\n",
            "    }\n\n",
            "    let mut species_map = HashMap::new();\n",
            components["map_inserts"], "\n\n",
            "    let result = SimulationResult {\n",
            "        time,\n",
            "        species: species_map,\n",
            "    };\n\n",
            "    serde_json::to_string(&result).unwrap()\n",
            "}\n"
        ]
        
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
