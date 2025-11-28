// Generated WASM-compatible Rust code from SBML model: PBPK_BPA_model
// Uses SymPy CSE for optimized derivatives and Jacobian

use diffsol::{OdeBuilder, OdeSolverMethod, OdeSolverStopReason, Vector};
use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

type M = diffsol::NalgebraMat<f64>;
type LS = diffsol::NalgebraLU<f64>;

#[derive(Serialize, Deserialize)]
pub struct SimulationResult {
    pub species: std::collections::HashMap<String, Vec<f64>>,
    pub time: Vec<f64>,
}

#[derive(Serialize, Deserialize)]
pub struct SimulationParams {
    pub Kabs: f64,
    pub koa: f64,
    pub t0: f64,
    pub t1: f64,
    pub Kelm: f64,
    pub EoA_O: f64,
    pub D_o: f64,
    pub vplasma: f64,
    pub period_O: f64,
    pub n_O: f64,
    pub uptake_O: f64,
    pub comp1: f64,
    pub final_time: Option<f64>,
}

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

#[wasm_bindgen]
pub fn run_simulation(params: &str) -> String {
    console_log!("Starting simulation...");

    let sim_params: SimulationParams = match serde_json::from_str(params) {
        Ok(p) => p,
        Err(e) => {
            console_log!("Error parsing params: {}", e);
            return serde_json::to_string(&SimulationResult {
                species: HashMap::new(),
                time: vec![],
            }).unwrap();
        }
    };

    let Kabs = sim_params.Kabs;
    let koa = sim_params.koa;
    let t0 = sim_params.t0;
    let t1 = sim_params.t1;
    let Kelm = sim_params.Kelm;
    let EoA_O = sim_params.EoA_O;
    let D_o = sim_params.D_o;
    let vplasma = sim_params.vplasma;
    let period_O = sim_params.period_O;
    let n_O = sim_params.n_O;
    let uptake_O = sim_params.uptake_O;
    let comp1 = sim_params.comp1;




    // RHS Closure
    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {
        // Map species names to y indices
        let Aplasma = y[0];

        // Temporary variables (CSE)
        let x0 = 1.0*Kelm;

        // Derivatives
        dy[0] = -1.0*Aplasma*x0 + 0.5*Kabs*koa*((100.0*t - 100.0*t0).tanh() - 1.0*(100.0*t - 100.0*t1).tanh());
    };

    // Jacobian Closure (Matrix-Vector Product)
    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..jv.len() { jv[i] = 0.0; }

        // Map species names to y indices
        let Aplasma = y[0];

        // Temporary variables (CSE)
        let x0 = 1.0*Kelm;

        // Jacobian-Vector Product
        jv[0] += (-1.0*x0) * v[0];
    };

    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..1 { y[i] = 0.0; }
    };

    let problem = OdeBuilder::<M>::new()
        .rhs_implicit(rhs, jac)
        .init(init, 1)
        
        .build()
        .unwrap();

    let mut solver = problem.bdf::<LS>().unwrap();
    let mut time = Vec::new();

    // Initialize result vectors
    let mut aplasma = Vec::new();

    aplasma.push(solver.state().y[0]);
    time.push(0.0);

    let final_time = sim_params.final_time.unwrap_or(24.0);
    solver.set_stop_time(final_time).unwrap();
    loop {
        match solver.step() {
            Ok(OdeSolverStopReason::InternalTimestep) => {
            aplasma.push(solver.state().y[0]);
                time.push(solver.state().t);
            },
            Ok(OdeSolverStopReason::TstopReached) => break,
            Err(_) => panic!("Solver Error"),
        }
    }

    let mut species_map = HashMap::new();
        species_map.insert("aplasma".to_string(), aplasma);

    let result = SimulationResult {
        time,
        species: species_map,
    };

    serde_json::to_string(&result).unwrap()
}
