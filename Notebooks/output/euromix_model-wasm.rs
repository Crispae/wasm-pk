// Generated WASM-compatible Rust code from SBML model: euromix_model
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
    pub BM: f64,
    pub BSA: f64,
    pub scVFat: f64,
    pub scVRich: f64,
    pub scVLiver: f64,
    pub scVBlood: f64,
    pub scVArt: f64,
    pub scFBlood: f64,
    pub scFFat: f64,
    pub scFPoor: f64,
    pub scFLiver: f64,
    pub scFSkin: f64,
    pub fSA_exposed: f64,
    pub Height_sc: f64,
    pub Height_vs: f64,
    pub Falv: f64,
    pub PCFat: f64,
    pub PCLiver: f64,
    pub PCRich: f64,
    pub PCPoor: f64,
    pub PCSkin_sc: f64,
    pub PCSkin: f64,
    pub PCAir: f64,
    pub kGut: f64,
    pub Kp_sc_vs: f64,
    pub Km: f64,
    pub Michaelis: f64,
    pub Vmax: f64,
    pub CLH: f64,
    pub Ke: f64,
    pub fub: f64,
    pub Air: f64,
    pub Urine: f64,
    pub Gut: f64,

    // Initial amounts (optional, for runtime dosing)
    pub init_QFat: Option<f64>,
    pub init_QRich: Option<f64>,
    pub init_QPoor: Option<f64>,
    pub init_QLiver: Option<f64>,
    pub init_QMetab: Option<f64>,
    pub init_QGut: Option<f64>,
    pub init_QSkin_u: Option<f64>,
    pub init_QSkin_e: Option<f64>,
    pub init_QSkin_sc_u: Option<f64>,
    pub init_QSkin_sc_e: Option<f64>,
    pub init_QArt: Option<f64>,
    pub init_QVen: Option<f64>,
    pub init_QExcret: Option<f64>,
    pub init_QAir: Option<f64>,
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

    let BM = sim_params.BM;
    let BSA = sim_params.BSA;
    let scVFat = sim_params.scVFat;
    let scVRich = sim_params.scVRich;
    let scVLiver = sim_params.scVLiver;
    let scVBlood = sim_params.scVBlood;
    let scVArt = sim_params.scVArt;
    let scFBlood = sim_params.scFBlood;
    let scFFat = sim_params.scFFat;
    let scFPoor = sim_params.scFPoor;
    let scFLiver = sim_params.scFLiver;
    let scFSkin = sim_params.scFSkin;
    let fSA_exposed = sim_params.fSA_exposed;
    let Height_sc = sim_params.Height_sc;
    let Height_vs = sim_params.Height_vs;
    let Falv = sim_params.Falv;
    let PCFat = sim_params.PCFat;
    let PCLiver = sim_params.PCLiver;
    let PCRich = sim_params.PCRich;
    let PCPoor = sim_params.PCPoor;
    let PCSkin_sc = sim_params.PCSkin_sc;
    let PCSkin = sim_params.PCSkin;
    let PCAir = sim_params.PCAir;
    let kGut = sim_params.kGut;
    let Kp_sc_vs = sim_params.Kp_sc_vs;
    let Km = sim_params.Km;
    let Michaelis = sim_params.Michaelis;
    let Vmax = sim_params.Vmax;
    let CLH = sim_params.CLH;
    let Ke = sim_params.Ke;
    let fub = sim_params.fub;
    let Air = sim_params.Air;
    let Urine = sim_params.Urine;
    let Gut = sim_params.Gut;
    let Fat = BM*scVFat;
    let Rich = BM*scVRich;
    let Liver = BM*scVLiver;
    let Skin_e = BSA*Height_vs*fSA_exposed;
    let Skin_u = BSA*Height_vs*(1.0 - 1.0*fSA_exposed);
    let Skin_sc_e = BSA*Height_sc*fSA_exposed;
    let Skin_sc_u = BSA*Height_sc*(1.0 - 1.0*fSA_exposed);
    let f_su = Kp_sc_vs*BSA*(1.0 - 1.0*fSA_exposed);
    let f_se = Kp_sc_vs*BSA*fSA_exposed;
    let VBlood = BM*scVBlood;
    let FBlood = scFBlood*BM;
    let Poor = -1.0*Skin_sc_u + (-1.0*Skin_sc_e + (-1.0*Skin_u + (BM*(-1.0*scVBlood + (-1.0*scVLiver + (-1.0*scVRich + (1.0 - 1.0*scVFat))) - 1.0/10.0) - 1.0*Skin_e)));
    let Art = VBlood*scVArt;
    let FFat = FBlood*scFFat;
    let FPoor = FBlood*scFPoor;
    let FLiver = FBlood*scFLiver;
    let FSkin = FBlood*scFSkin;
    let Ven = -1.0*Art + VBlood;
    let FRich = -1.0*FSkin + (-1.0*FLiver + (-1.0*FPoor + (FBlood - 1.0*FFat)));
    let FSkin_e = FSkin*fSA_exposed;
    let FSkin_u = FSkin - 1.0*FSkin_e;



    // RHS Closure
    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {
        // Map species names to y indices
        let QFat = y[0];
        let QRich = y[1];
        let QPoor = y[2];
        let QLiver = y[3];
        let QMetab = y[4];
        let QGut = y[5];
        let QSkin_u = y[6];
        let QSkin_e = y[7];
        let QSkin_sc_u = y[8];
        let QSkin_sc_e = y[9];
        let QArt = y[10];
        let QVen = y[11];
        let QExcret = y[12];
        let QAir = y[13];

        // Temporary variables (CSE)
        let x0 = Art.powi(-1);
        let x1 = -1.0*QArt*x0;
        let x2 = Fat.powi(-1)*PCFat.powi(-1);
        let x3 = QFat*x2;
        let x4 = 1.0*FFat;
        let x5 = PCRich.powi(-1)*Rich.powi(-1);
        let x6 = QRich*x5;
        let x7 = 1.0*FRich;
        let x8 = PCPoor.powi(-1)*Poor.powi(-1);
        let x9 = QPoor*x8;
        let x10 = 1.0*FPoor;
        let x11 = Liver.powi(-1);
        let x12 = QLiver*x11;
        let x13 = Liver > 0.0;
        let x14 = if x13 {
            x12
        } else {
            0.0
        };
        let x15 = if Km*PCLiver + x14 != 0.0 {
            (Km*PCLiver + x14).powi(-1)
        } else {
            10000000000.0
        };
        let x16 = x14*x15;
        let x17 = Liver*Vmax;
        let x18 = Michaelis > 1.0/2.0;
        let x19 = PCLiver.powi(-1);
        let x20 = CLH*x19;
        let x21 = fub*if x18 {
            x16*x17
        } else {
            x14*x20
        };
        let x22 = QArt*x0;
        let x23 = FLiver*x22;
        let x24 = FLiver*x19;
        let x25 = x12*x24;
        let x26 = Skin_sc_u.powi(-1);
        let x27 = Skin_sc_u > 0.0;
        let x28 = if x27 {
            QSkin_sc_u*x26
        } else {
            0.0
        };
        let x29 = Skin_u.powi(-1);
        let x30 = Skin_u > 0.0;
        let x31 = if x30 {
            QSkin_u*x29
        } else {
            0.0
        };
        let x32 = PCSkin.powi(-1);
        let x33 = FSkin_u*x32;
        let x34 = x31*x33;
        let x35 = PCSkin_sc.powi(-1);
        let x36 = FSkin_u*x22;
        let x37 = Skin_sc_e.powi(-1);
        let x38 = Skin_sc_e > 0.0;
        let x39 = if x38 {
            QSkin_sc_e*x37
        } else {
            0.0
        };
        let x40 = Skin_e.powi(-1);
        let x41 = Skin_e > 0.0;
        let x42 = if x41 {
            QSkin_e*x40
        } else {
            0.0
        };
        let x43 = FSkin_e*x32;
        let x44 = x42*x43;
        let x45 = FSkin_e*x22;
        let x46 = 1.0*f_su;
        let x47 = 1.0*f_se;
        let x48 = FBlood*Ven.powi(-1);
        let x49 = -1.0*QVen*x48;
        let x50 = Ke*fub;
        let x51 = x22*x50;
        let x52 = FBlood*Air.powi(-1);
        let x53 = Falv*PCAir.powi(-1);
        let x54 = -1.0*QAir*x52 + x22*x53;
        let x55 = x2*x4;
        let x56 = x5*x7;
        let x57 = x10*x8;
        let x58 = if x13 {
            x11
        } else {
            0.0
        };
        let x59 = fub*if x18 {
            x15*x17*x58*(1.0 - 1.0*x16)
        } else {
            x20*x58
        };
        let x60 = x11*x24;
        let x61 = 1.0*kGut;
        let x62 = 1.0*x0;
        let x63 = f_su*x35;
        let x64 = 1.0*if x30 {
            x29
        } else {
            0.0
        };
        let x65 = x46*if x27 {
            x26
        } else {
            0.0
        };
        let x66 = f_se*x35;
        let x67 = 1.0*if x41 {
            x40
        } else {
            0.0
        };
        let x68 = x47*if x38 {
            x37
        } else {
            0.0
        };
        let x69 = 1.0*x48;
        let x70 = 1.0*x52;

        // Derivatives
        dy[0] = x4*(-1.0*x1 - 1.0*x3);
        dy[1] = x7*(-1.0*x1 - 1.0*x6);
        dy[2] = x10*(-1.0*x1 - 1.0*x9);
        dy[3] = 1.0*QGut*kGut - 1.0*x21 + 1.0*x23 - 1.0*x25;
        dy[4] = 1.0*x21;
        dy[5] = -1.0*QGut*kGut;
        dy[6] = 1.0*f_su*x28 - 1.0*f_su*x31*x35 - 1.0*x34 + 1.0*x36;
        dy[7] = -1.0*f_se*x35*x42 + 1.0*f_se*x39 - 1.0*x44 + 1.0*x45;
        dy[8] = x46*(-1.0*x28 + x31*x35);
        dy[9] = x47*(x35*x42 - 1.0*x39);
        dy[10] = -1.0*FFat*x22 - 1.0*FPoor*x22 - 1.0*FRich*x22 - 1.0*x23 - 1.0*x36 - 1.0*x45 - 1.0*x49 - 1.0*x51 - 1.0*x54;
        dy[11] = 1.0*FFat*x3 + 1.0*FPoor*x9 + 1.0*FRich*x6 + 1.0*x25 + 1.0*x34 + 1.0*x44 + 1.0*x49;
        dy[12] = 1.0*x51;
        dy[13] = 1.0*x54;
    };

    // Jacobian Closure (Matrix-Vector Product)
    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..jv.len() { jv[i] = 0.0; }

        // Map species names to y indices
        let QFat = y[0];
        let QRich = y[1];
        let QPoor = y[2];
        let QLiver = y[3];
        let QMetab = y[4];
        let QGut = y[5];
        let QSkin_u = y[6];
        let QSkin_e = y[7];
        let QSkin_sc_u = y[8];
        let QSkin_sc_e = y[9];
        let QArt = y[10];
        let QVen = y[11];
        let QExcret = y[12];
        let QAir = y[13];

        // Temporary variables (CSE)
        let x0 = Art.powi(-1);
        let x1 = -1.0*QArt*x0;
        let x2 = Fat.powi(-1)*PCFat.powi(-1);
        let x3 = QFat*x2;
        let x4 = 1.0*FFat;
        let x5 = PCRich.powi(-1)*Rich.powi(-1);
        let x6 = QRich*x5;
        let x7 = 1.0*FRich;
        let x8 = PCPoor.powi(-1)*Poor.powi(-1);
        let x9 = QPoor*x8;
        let x10 = 1.0*FPoor;
        let x11 = Liver.powi(-1);
        let x12 = QLiver*x11;
        let x13 = Liver > 0.0;
        let x14 = if x13 {
            x12
        } else {
            0.0
        };
        let x15 = if Km*PCLiver + x14 != 0.0 {
            (Km*PCLiver + x14).powi(-1)
        } else {
            10000000000.0
        };
        let x16 = x14*x15;
        let x17 = Liver*Vmax;
        let x18 = Michaelis > 1.0/2.0;
        let x19 = PCLiver.powi(-1);
        let x20 = CLH*x19;
        let x21 = fub*if x18 {
            x16*x17
        } else {
            x14*x20
        };
        let x22 = QArt*x0;
        let x23 = FLiver*x22;
        let x24 = FLiver*x19;
        let x25 = x12*x24;
        let x26 = Skin_sc_u.powi(-1);
        let x27 = Skin_sc_u > 0.0;
        let x28 = if x27 {
            QSkin_sc_u*x26
        } else {
            0.0
        };
        let x29 = Skin_u.powi(-1);
        let x30 = Skin_u > 0.0;
        let x31 = if x30 {
            QSkin_u*x29
        } else {
            0.0
        };
        let x32 = PCSkin.powi(-1);
        let x33 = FSkin_u*x32;
        let x34 = x31*x33;
        let x35 = PCSkin_sc.powi(-1);
        let x36 = FSkin_u*x22;
        let x37 = Skin_sc_e.powi(-1);
        let x38 = Skin_sc_e > 0.0;
        let x39 = if x38 {
            QSkin_sc_e*x37
        } else {
            0.0
        };
        let x40 = Skin_e.powi(-1);
        let x41 = Skin_e > 0.0;
        let x42 = if x41 {
            QSkin_e*x40
        } else {
            0.0
        };
        let x43 = FSkin_e*x32;
        let x44 = x42*x43;
        let x45 = FSkin_e*x22;
        let x46 = 1.0*f_su;
        let x47 = 1.0*f_se;
        let x48 = FBlood*Ven.powi(-1);
        let x49 = -1.0*QVen*x48;
        let x50 = Ke*fub;
        let x51 = x22*x50;
        let x52 = FBlood*Air.powi(-1);
        let x53 = Falv*PCAir.powi(-1);
        let x54 = -1.0*QAir*x52 + x22*x53;
        let x55 = x2*x4;
        let x56 = x5*x7;
        let x57 = x10*x8;
        let x58 = if x13 {
            x11
        } else {
            0.0
        };
        let x59 = fub*if x18 {
            x15*x17*x58*(1.0 - 1.0*x16)
        } else {
            x20*x58
        };
        let x60 = x11*x24;
        let x61 = 1.0*kGut;
        let x62 = 1.0*x0;
        let x63 = f_su*x35;
        let x64 = 1.0*if x30 {
            x29
        } else {
            0.0
        };
        let x65 = x46*if x27 {
            x26
        } else {
            0.0
        };
        let x66 = f_se*x35;
        let x67 = 1.0*if x41 {
            x40
        } else {
            0.0
        };
        let x68 = x47*if x38 {
            x37
        } else {
            0.0
        };
        let x69 = 1.0*x48;
        let x70 = 1.0*x52;

        // Jacobian-Vector Product
        jv[0] += (-1.0*x55) * v[0];
        jv[0] += (x0*x4) * v[10];
        jv[1] += (-1.0*x56) * v[1];
        jv[1] += (x0*x7) * v[10];
        jv[2] += (-1.0*x57) * v[2];
        jv[2] += (x0*x10) * v[10];
        jv[3] += (-1.0*x59 - 1.0*x60) * v[3];
        jv[3] += (x61) * v[5];
        jv[3] += (FLiver*x62) * v[10];
        jv[4] += (1.0*x59) * v[3];
        jv[5] += (-1.0*x61) * v[5];
        jv[6] += (-1.0*x64*(x33 + x63)) * v[6];
        jv[6] += (x65) * v[8];
        jv[6] += (FSkin_u*x62) * v[10];
        jv[7] += (-1.0*x67*(x43 + x66)) * v[7];
        jv[7] += (x68) * v[9];
        jv[7] += (FSkin_e*x62) * v[10];
        jv[8] += (x63*x64) * v[6];
        jv[8] += (-1.0*x65) * v[8];
        jv[9] += (x66*x67) * v[7];
        jv[9] += (-1.0*x68) * v[9];
        jv[10] += (-1.0*x62*(FFat + FLiver + FPoor + FRich + FSkin_e + FSkin_u + x50 + x53)) * v[10];
        jv[10] += (x69) * v[11];
        jv[10] += (x70) * v[13];
        jv[11] += (x55) * v[0];
        jv[11] += (x56) * v[1];
        jv[11] += (x57) * v[2];
        jv[11] += (1.0*x60) * v[3];
        jv[11] += (x33*x64) * v[6];
        jv[11] += (x43*x67) * v[7];
        jv[11] += (-1.0*x69) * v[11];
        jv[12] += (x50*x62) * v[10];
        jv[13] += (x53*x62) * v[10];
        jv[13] += (-1.0*x70) * v[13];
    };

    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {
        y[0] = sim_params.init_QFat.unwrap_or(0.0);
        y[1] = sim_params.init_QRich.unwrap_or(0.0);
        y[2] = sim_params.init_QPoor.unwrap_or(0.0);
        y[3] = sim_params.init_QLiver.unwrap_or(0.0);
        y[4] = sim_params.init_QMetab.unwrap_or(0.0);
        y[5] = sim_params.init_QGut.unwrap_or(1.0);
        y[6] = sim_params.init_QSkin_u.unwrap_or(0.0);
        y[7] = sim_params.init_QSkin_e.unwrap_or(0.0);
        y[8] = sim_params.init_QSkin_sc_u.unwrap_or(0.0);
        y[9] = sim_params.init_QSkin_sc_e.unwrap_or(0.0);
        y[10] = sim_params.init_QArt.unwrap_or(0.0);
        y[11] = sim_params.init_QVen.unwrap_or(0.0);
        y[12] = sim_params.init_QExcret.unwrap_or(0.0);
        y[13] = sim_params.init_QAir.unwrap_or(0.0);
    };
    let problem = OdeBuilder::<M>::new()
        .rhs_implicit(rhs, jac)
        .init(init, 14)
        .build()
        .unwrap();

    let mut solver = problem.bdf::<LS>().unwrap();
    let mut time = Vec::new();

    // Initialize result vectors
    let mut qfat = Vec::new();
    let mut qrich = Vec::new();
    let mut qpoor = Vec::new();
    let mut qliver = Vec::new();
    let mut qmetab = Vec::new();
    let mut qgut = Vec::new();
    let mut qskin_u = Vec::new();
    let mut qskin_e = Vec::new();
    let mut qskin_sc_u = Vec::new();
    let mut qskin_sc_e = Vec::new();
    let mut qart = Vec::new();
    let mut qven = Vec::new();
    let mut qexcret = Vec::new();
    let mut qair = Vec::new();

    qfat.push(solver.state().y[0]);
    qrich.push(solver.state().y[1]);
    qpoor.push(solver.state().y[2]);
    qliver.push(solver.state().y[3]);
    qmetab.push(solver.state().y[4]);
    qgut.push(solver.state().y[5]);
    qskin_u.push(solver.state().y[6]);
    qskin_e.push(solver.state().y[7]);
    qskin_sc_u.push(solver.state().y[8]);
    qskin_sc_e.push(solver.state().y[9]);
    qart.push(solver.state().y[10]);
    qven.push(solver.state().y[11]);
    qexcret.push(solver.state().y[12]);
    qair.push(solver.state().y[13]);
    time.push(0.0);

    let final_time = sim_params.final_time.unwrap_or(24.0);
    solver.set_stop_time(final_time).unwrap();
    loop {
        match solver.step() {
            Ok(OdeSolverStopReason::InternalTimestep) => {
            qfat.push(solver.state().y[0]);
            qrich.push(solver.state().y[1]);
            qpoor.push(solver.state().y[2]);
            qliver.push(solver.state().y[3]);
            qmetab.push(solver.state().y[4]);
            qgut.push(solver.state().y[5]);
            qskin_u.push(solver.state().y[6]);
            qskin_e.push(solver.state().y[7]);
            qskin_sc_u.push(solver.state().y[8]);
            qskin_sc_e.push(solver.state().y[9]);
            qart.push(solver.state().y[10]);
            qven.push(solver.state().y[11]);
            qexcret.push(solver.state().y[12]);
            qair.push(solver.state().y[13]);
                time.push(solver.state().t);
            },
            Ok(OdeSolverStopReason::TstopReached) => break,
            Ok(OdeSolverStopReason::RootFound(_)) => break,
            Err(_) => panic!("Solver Error"),
        }
    }

    let mut species_map = HashMap::new();
        species_map.insert("qfat".to_string(), qfat);
        species_map.insert("qrich".to_string(), qrich);
        species_map.insert("qpoor".to_string(), qpoor);
        species_map.insert("qliver".to_string(), qliver);
        species_map.insert("qmetab".to_string(), qmetab);
        species_map.insert("qgut".to_string(), qgut);
        species_map.insert("qskin_u".to_string(), qskin_u);
        species_map.insert("qskin_e".to_string(), qskin_e);
        species_map.insert("qskin_sc_u".to_string(), qskin_sc_u);
        species_map.insert("qskin_sc_e".to_string(), qskin_sc_e);
        species_map.insert("qart".to_string(), qart);
        species_map.insert("qven".to_string(), qven);
        species_map.insert("qexcret".to_string(), qexcret);
        species_map.insert("qair".to_string(), qair);

    let result = SimulationResult {
        time,
        species: species_map,
    };

    serde_json::to_string(&result).unwrap()
}

#[wasm_bindgen]
pub fn get_model_metadata() -> String {
    let metadata = serde_json::json!({
        "model_id": "euromix_model",
        "num_species": 14,
        "num_parameters": 34,
        "time_units": "HR",
        "substance_units": "MilliMOL",
        "volume_units": "L"
    });
    serde_json::to_string(&metadata).unwrap()
}

#[wasm_bindgen]
pub fn get_parameters_info() -> String {
    let params = serde_json::json!([
        {
            "id": "BM",
            "default_value": 70.0,
            "required": true
        },
        {
            "id": "BSA",
            "default_value": 190.0,
            "required": true
        },
        {
            "id": "scVFat",
            "default_value": 0.209,
            "required": true
        },
        {
            "id": "scVRich",
            "default_value": 0.105,
            "required": true
        },
        {
            "id": "scVLiver",
            "default_value": 0.024,
            "required": true
        },
        {
            "id": "scVBlood",
            "default_value": 0.068,
            "required": true
        },
        {
            "id": "scVArt",
            "default_value": 0.333333333333333,
            "required": true
        },
        {
            "id": "scFBlood",
            "default_value": 4.8,
            "required": true
        },
        {
            "id": "scFFat",
            "default_value": 0.085,
            "required": true
        },
        {
            "id": "scFPoor",
            "default_value": 0.12,
            "required": true
        },
        {
            "id": "scFLiver",
            "default_value": 0.27,
            "required": true
        },
        {
            "id": "scFSkin",
            "default_value": 0.05,
            "required": true
        },
        {
            "id": "fSA_exposed",
            "default_value": 0.1,
            "required": true
        },
        {
            "id": "Height_sc",
            "default_value": 0.0001,
            "required": true
        },
        {
            "id": "Height_vs",
            "default_value": 0.0122,
            "required": true
        },
        {
            "id": "Falv",
            "default_value": 2220.0,
            "required": true
        },
        {
            "id": "PCFat",
            "default_value": 2.53,
            "required": true
        },
        {
            "id": "PCLiver",
            "default_value": 0.923,
            "required": true
        },
        {
            "id": "PCRich",
            "default_value": 0.875,
            "required": true
        },
        {
            "id": "PCPoor",
            "default_value": 0.647,
            "required": true
        },
        {
            "id": "PCSkin_sc",
            "default_value": 0.889,
            "required": true
        },
        {
            "id": "PCSkin",
            "default_value": 0.889,
            "required": true
        },
        {
            "id": "PCAir",
            "default_value": 1e+99,
            "required": true
        },
        {
            "id": "kGut",
            "default_value": 1.0,
            "required": true
        },
        {
            "id": "Kp_sc_vs",
            "default_value": 0.01,
            "required": true
        },
        {
            "id": "Km",
            "default_value": 0.0,
            "required": true
        },
        {
            "id": "Michaelis",
            "default_value": 0.0,
            "required": true
        },
        {
            "id": "Vmax",
            "default_value": 0.0,
            "required": true
        },
        {
            "id": "CLH",
            "default_value": 132.0,
            "required": true
        },
        {
            "id": "Ke",
            "default_value": 7.5,
            "required": true
        },
        {
            "id": "fub",
            "default_value": 0.51,
            "required": true
        },
        {
            "id": "Air",
            "default_value": 1.0,
            "required": true
        },
        {
            "id": "Urine",
            "default_value": 1.0,
            "required": true
        },
        {
            "id": "Gut",
            "default_value": 1.0,
            "required": true
        }
    ]);
    serde_json::to_string(&params).unwrap()
}

#[wasm_bindgen]
pub fn get_species_info() -> String {
    let species = serde_json::json!([
        {
            "id": "QFat",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QRich",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QPoor",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QLiver",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QMetab",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QGut",
            "initial_amount": 1.0,
            "units": "MilliMOL"
        },
        {
            "id": "QSkin_u",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QSkin_e",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QSkin_sc_u",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QSkin_sc_e",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QArt",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QVen",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QExcret",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "QAir",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        }
    ]);
    serde_json::to_string(&species).unwrap()
}

#[wasm_bindgen]
pub fn get_default_parameters() -> String {
    let defaults = serde_json::json!({
        "BM": 70.0,
        "BSA": 190.0,
        "scVFat": 0.209,
        "scVRich": 0.105,
        "scVLiver": 0.024,
        "scVBlood": 0.068,
        "scVArt": 0.333333333333333,
        "scFBlood": 4.8,
        "scFFat": 0.085,
        "scFPoor": 0.12,
        "scFLiver": 0.27,
        "scFSkin": 0.05,
        "fSA_exposed": 0.1,
        "Height_sc": 0.0001,
        "Height_vs": 0.0122,
        "Falv": 2220.0,
        "PCFat": 2.53,
        "PCLiver": 0.923,
        "PCRich": 0.875,
        "PCPoor": 0.647,
        "PCSkin_sc": 0.889,
        "PCSkin": 0.889,
        "PCAir": 1e+99,
        "kGut": 1.0,
        "Kp_sc_vs": 0.01,
        "Km": 0.0,
        "Michaelis": 0.0,
        "Vmax": 0.0,
        "CLH": 132.0,
        "Ke": 7.5,
        "fub": 0.51,
        "Air": 1.0,
        "Urine": 1.0,
        "Gut": 1.0,
        "final_time": 24.0
    });
    serde_json::to_string(&defaults).unwrap()
}
