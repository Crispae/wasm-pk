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
            components: Dictionary with keys:
                - species_fields: Struct fields for species
                - param_fields: Struct fields for parameters
                - param_extract: Parameter extraction code
                - species_extract: Species extraction code
                - temp_vars: Temporary variable declarations
                - rhs_block: RHS derivative calculations
                - jac_block: Jacobian calculations
                - result_vectors_init: Result vector initialization
                - initial_pushes: Initial state pushes
                - loop_pushes: Loop state pushes
                - map_inserts: HashMap insert statements
                - n_species: Number of species
                - gut_idx: Index of gut compartment species (default 5)

        Returns:
            Complete Rust source code
        """
        template = f'''// Generated WASM-compatible Rust code from SBML model: {model_name}
// Uses SymPy CSE for optimized derivatives and Jacobian

use diffsol::{{OdeBuilder, OdeSolverMethod, OdeSolverStopReason, Vector}};
use wasm_bindgen::prelude::*;
use serde::{{Deserialize, Serialize}};
use std::collections::HashMap;

type M = diffsol::NalgebraMat<f64>;
type LS = diffsol::NalgebraLU<f64>;

#[derive(Serialize, Deserialize)]
pub struct SimulationResult {{
{components["species_fields"]}
    pub time: Vec<f64>,
}}

#[derive(Serialize, Deserialize)]
pub struct SimulationParams {{
{components["param_fields"]}
    pub doses: Vec<(f64, f64)>,
    pub final_time: Option<f64>,
}}

#[wasm_bindgen]
extern "C" {{
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}}

macro_rules! console_log {{
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}}

#[wasm_bindgen]
pub fn run_simulation(params: &str) -> String {{
    console_log!("Starting simulation...");

    let sim_params: SimulationParams = match serde_json::from_str(params) {{
        Ok(p) => p,
        Err(e) => {{
            console_log!("Error parsing params: {{}}", e);
            return serde_json::to_string(&SimulationResult {{
                species: HashMap::new(),
                time: vec![],
            }}).unwrap();
        }}
    }};

{components["param_extract"]}
    let doses = sim_params.doses;

    // RHS Closure
    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, _t: f64, dy: &mut diffsol::NalgebraVec<f64>| {{
        // Map species names to y indices
{components["species_extract"]}

        // Temporary variables (CSE)
{components["temp_vars"]}

        // Derivatives
{components["rhs_block"]}
    }};

    // Jacobian Closure (Matrix-Vector Product)
    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, _t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {{
        for i in 0..jv.len() {{ jv[i] = 0.0; }}

        // Map species names to y indices
{components["species_extract"]}

        // Temporary variables (CSE)
{components["temp_vars"]}

        // Jacobian-Vector Product
{components["jac_block"]}
    }};

    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {{
        for i in 0..{components["n_species"]} {{ y[i] = 0.0; }}
    }};

    let problem = OdeBuilder::<M>::new()
        .rhs_implicit(rhs, jac)
        .init(init, {components["n_species"]})
        .build()
        .unwrap();

    let mut solver = problem.bdf::<LS>().unwrap();
    let mut time = Vec::new();

    // Initialize result vectors
{components["result_vectors_init"]}

    // First Dose
    if !doses.is_empty() {{
        let gut_idx = {components["gut_idx"]};
        solver.state_mut().y[gut_idx] = doses[0].1;
    }}

{components["initial_pushes"]}
    time.push(0.0);

    // Simulation Loop
    for (t, dose) in doses.into_iter().skip(1) {{
        solver.set_stop_time(t).unwrap();
        loop {{
            match solver.step() {{
                Ok(OdeSolverStopReason::InternalTimestep) => {{
{components["loop_pushes"]}
                    time.push(solver.state().t);
                }},
                Ok(OdeSolverStopReason::TstopReached) => break,
                Ok(OdeSolverStopReason::RootFound(_)) => break,
                Err(_) => panic!("Solver Error"),
            }}
        }}
        let gut_idx = {components["gut_idx"]};
        solver.state_mut().y[gut_idx] += dose;
    }}

    let final_time = sim_params.final_time.unwrap_or(24.0);
    solver.set_stop_time(final_time).unwrap();
    loop {{
        match solver.step() {{
            Ok(OdeSolverStopReason::InternalTimestep) => {{
{components["loop_pushes"]}
                time.push(solver.state().t);
            }},
            Ok(OdeSolverStopReason::TstopReached) => break,
            Ok(OdeSolverStopReason::RootFound(_)) => break,
            Err(_) => panic!("Solver Error"),
        }}
    }}

    let mut species_map = HashMap::new();
{components["map_inserts"]}

    let result = SimulationResult {{
        time,
        species: species_map,
    }};

    serde_json::to_string(&result).unwrap()
}}
'''
        return template

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
