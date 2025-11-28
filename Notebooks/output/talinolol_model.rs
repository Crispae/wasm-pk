// Generated WASM-compatible Rust code from SBML model: talinolol_model
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
    pub BW: f64,
    pub HEIGHT: f64,
    pub HR: f64,
    pub HRrest: f64,
    pub COBW: f64,
    pub COHRI: f64,
    pub Fblood: f64,
    pub HCT: f64,
    pub f_shunting_forearm: f64,
    pub FVgu: f64,
    pub FVki: f64,
    pub FVli: f64,
    pub FVlu: f64,
    pub FVfo: f64,
    pub FVve: f64,
    pub FVar: f64,
    pub FVpo: f64,
    pub FVhv: f64,
    pub FVfov: f64,
    pub FQgu: f64,
    pub FQki: f64,
    pub FQh: f64,
    pub FQlu: f64,
    pub FQfo: f64,
    pub conversion_min_per_day: f64,
    pub f_cirrhosis: f64,
    pub PODOSE_tal: f64,
    pub Ka_dis_tal: f64,
    pub Mr_tal: f64,
    pub fup_tal: f64,
    pub ftissue_tal: f64,
    pub Kp_tal: f64,
    pub IVDOSE_tal: f64,
    pub ti_tal: f64,
    pub Ri_tal: f64,
    pub cum_dose_tal: f64,
    pub cum_dose_intestine_tal: f64,
    pub Vurine: f64,
    pub Vfeces: f64,
    pub Vstomach: f64,
    pub Vfo: f64,
    pub Vfov: f64,
    pub Vduodenum: f64,
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

    let BW = sim_params.BW;
    let HEIGHT = sim_params.HEIGHT;
    let HR = sim_params.HR;
    let HRrest = sim_params.HRrest;
    let COBW = sim_params.COBW;
    let COHRI = sim_params.COHRI;
    let Fblood = sim_params.Fblood;
    let HCT = sim_params.HCT;
    let f_shunting_forearm = sim_params.f_shunting_forearm;
    let FVgu = sim_params.FVgu;
    let FVki = sim_params.FVki;
    let FVli = sim_params.FVli;
    let FVlu = sim_params.FVlu;
    let FVfo = sim_params.FVfo;
    let FVve = sim_params.FVve;
    let FVar = sim_params.FVar;
    let FVpo = sim_params.FVpo;
    let FVhv = sim_params.FVhv;
    let FVfov = sim_params.FVfov;
    let FQgu = sim_params.FQgu;
    let FQki = sim_params.FQki;
    let FQh = sim_params.FQh;
    let FQlu = sim_params.FQlu;
    let FQfo = sim_params.FQfo;
    let conversion_min_per_day = sim_params.conversion_min_per_day;
    let f_cirrhosis = sim_params.f_cirrhosis;
    let PODOSE_tal = sim_params.PODOSE_tal;
    let Ka_dis_tal = sim_params.Ka_dis_tal;
    let Mr_tal = sim_params.Mr_tal;
    let fup_tal = sim_params.fup_tal;
    let ftissue_tal = sim_params.ftissue_tal;
    let Kp_tal = sim_params.Kp_tal;
    let IVDOSE_tal = sim_params.IVDOSE_tal;
    let ti_tal = sim_params.ti_tal;
    let Ri_tal = sim_params.Ri_tal;
    let cum_dose_tal = sim_params.cum_dose_tal;
    let cum_dose_intestine_tal = sim_params.cum_dose_intestine_tal;
    let Vurine = sim_params.Vurine;
    let Vfeces = sim_params.Vfeces;
    let Vstomach = sim_params.Vstomach;
    let Vfo = sim_params.Vfo;
    let Vfov = sim_params.Vfov;
    let Vduodenum = sim_params.Vduodenum;
    let f_shunts = f_cirrhosis;
    let f_tissue_loss = f_cirrhosis;
    let FVre = 1.0 - 1.0*(FVfo + (FVar + (FVve + (FVlu + (FVli + (FVgu + FVki))))));
    let FQre = 1.0 - 1.0*(FQfo + (FQh + FQki));
    let BSA = 4853.0/200000.0*(BW*1.0.powi(-1)).powf(2689.0/5000.0)*(HEIGHT*1.0.powi(-1)).powf(991.0/2500.0);
    let CO = BW*COBW + 1.0/60.0*(HR - 1.0*HRrest)*COHRI;
    let Vgu = BW*FVgu;
    let Vki = BW*FVki;
    let Vli = BW*FVli;
    let Vlu = BW*FVlu;
    let Vve = BW*FVve - 1.0*FVve*(FVar + FVve).powi(-1)*BW*Fblood*(-1.0*FVar + (1.0 - 1.0*FVve));
    let Var = BW*FVar - 1.0*FVar*(FVar + FVve).powi(-1)*BW*Fblood*(-1.0*FVar + (1.0 - 1.0*FVve));
    let Vpo = (1.0 - 1.0*HCT)*(BW*FVpo - 1.0*FVpo*(FVfo + (FVhv + (FVpo + (FVar + FVve)))).powi(-1)*BW*Fblood*(1.0 - 1.0*(FVfo + (FVhv + (FVpo + (FVar + FVve))))));
    let Vhv = (1.0 - 1.0*HCT)*(BW*FVhv - 1.0*FVhv*(FVfo + (FVhv + (FVpo + (FVar + FVve)))).powi(-1)*BW*Fblood*(1.0 - 1.0*(FVfo + (FVhv + (FVpo + (FVar + FVve))))));
    let Vfo_plasma = Vfo*Fblood*(1.0 - 1.0*HCT);
    let Vfo_tissue = Vfo*(1.0 - 1.0*Fblood);
    let Ki_tal = 693.0/1000.0*ti_tal.powi(-1)*60.0;
    let Afov_tal = Cfov_tal*Vfov;
    let Xurine_tal = Aurine_tal*Mr_tal;
    let Xfeces_tal = Afeces_tal*Mr_tal;
    let Vre = BW*FVre;
    let QC = 1.0/1000.0*CO*60.0;
    let Vgu_plasma = Vgu*Fblood*(1.0 - 1.0*HCT);
    let Vgu_tissue = Vgu*(1.0 - 1.0*Fblood);
    let Vki_plasma = Vki*Fblood*(1.0 - 1.0*HCT);
    let Vki_tissue = Vki*(1.0 - 1.0*Fblood);
    let Vli_plasma = Vli*Fblood*(1.0 - 1.0*HCT);
    let Vli_tissue = Vli*(1.0 - 1.0*f_tissue_loss)*(1.0 - 1.0*Fblood);
    let Vlu_plasma = Vlu*Fblood*(1.0 - 1.0*HCT);
    let Vlu_tissue = Vlu*(1.0 - 1.0*Fblood);
    let Ave_tal = Cve_tal*Vve;
    let Aar_tal = Car_tal*Var;
    let Apo_tal = Cpo_tal*Vpo;
    let Ahv_tal = Chv_tal*Vhv;
    let Afo_plasma_tal = Cfo_plasma_tal*Vfo_plasma;
    let Xfov_tal = Afov_tal*Mr_tal;
    let Mfov_tal = Afov_tal*Vfov.powi(-1)*Mr_tal;
    let Vre_plasma = Vre*Fblood*(1.0 - 1.0*HCT);
    let Vre_tissue = Vre*(1.0 - 1.0*Fblood);
    let Qgu = QC*FQgu;
    let Qki = QC*FQki;
    let Qh = QC*FQh;
    let Qlu = QC*FQlu;
    let Qre = QC*FQre;
    let Qfo = QC*FQfo;
    let Agu_plasma_tal = Cgu_plasma_tal*Vgu_plasma;
    let Aki_plasma_tal = Cki_plasma_tal*Vki_plasma;
    let Ali_plasma_tal = Cli_plasma_tal*Vli_plasma;
    let Alu_plasma_tal = Clu_plasma_tal*Vlu_plasma;
    let Xve_tal = Ave_tal*Mr_tal;
    let Mve_tal = Ave_tal*Vve.powi(-1)*Mr_tal;
    let Xar_tal = Aar_tal*Mr_tal;
    let Mar_tal = Aar_tal*Var.powi(-1)*Mr_tal;
    let Xpo_tal = Apo_tal*Mr_tal;
    let Mpo_tal = Apo_tal*Vpo.powi(-1)*Mr_tal;
    let Xhv_tal = Ahv_tal*Mr_tal;
    let Mhv_tal = Ahv_tal*Vhv.powi(-1)*Mr_tal;
    let Xfo_plasma_tal = Afo_plasma_tal*Mr_tal;
    let Mfo_plasma_tal = Afo_plasma_tal*Vfo_plasma.powi(-1)*Mr_tal;
    let Are_plasma_tal = Cre_plasma_tal*Vre_plasma;
    let Qpo = Qgu;
    let Qha = -1.0*Qgu + Qh;
    let Xgu_plasma_tal = Agu_plasma_tal*Mr_tal;
    let Mgu_plasma_tal = Agu_plasma_tal*Vgu_plasma.powi(-1)*Mr_tal;
    let Xki_plasma_tal = Aki_plasma_tal*Mr_tal;
    let Mki_plasma_tal = Aki_plasma_tal*Vki_plasma.powi(-1)*Mr_tal;
    let Xli_plasma_tal = Ali_plasma_tal*Mr_tal;
    let Mli_plasma_tal = Ali_plasma_tal*Vli_plasma.powi(-1)*Mr_tal;
    let Xlu_plasma_tal = Alu_plasma_tal*Mr_tal;
    let Mlu_plasma_tal = Alu_plasma_tal*Vlu_plasma.powi(-1)*Mr_tal;
    let Xre_plasma_tal = Are_plasma_tal*Mr_tal;
    let Mre_plasma_tal = Are_plasma_tal*Vre_plasma.powi(-1)*Mr_tal;



    // RHS Closure
    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {
        // Map species names to y indices
        let Cki_plasma_tal = y[0];
        let Cli_plasma_tal = y[1];
        let Clu_plasma_tal = y[2];
        let Cgu_plasma_tal = y[3];
        let Cre_plasma_tal = y[4];
        let Cfo_plasma_tal = y[5];
        let Car_tal = y[6];
        let Cve_tal = y[7];
        let Cpo_tal = y[8];
        let Chv_tal = y[9];
        let Cfov_tal = y[10];
        let Clu_tal = y[11];
        let Cre_tal = y[12];
        let Aurine_tal = y[13];
        let Afeces_tal = y[14];
        let Cduodenum_tal = y[15];

        // Temporary variables (CSE)
        let x0 = 1.0*Qki;
        let x1 = 1.0*f_shunts;
        let x2 = Car_tal*Qha;
        let x3 = Cpo_tal*Qpo;
        let x4 = Qha + Qpo;
        let x5 = Cve_tal*Qlu;
        let x6 = Kp_tal*fup_tal;
        let x7 = ftissue_tal*(-1.0*Clu_plasma_tal*x6 + Clu_tal);
        let x8 = -1.0*Clu_plasma_tal*Qlu;
        let x9 = 1.0*Qgu;
        let x10 = Car_tal*Qre;
        let x11 = ftissue_tal*(-1.0*Cre_plasma_tal*x6 + Cre_tal);
        let x12 = Cre_plasma_tal*Qre;
        let x13 = Car_tal*f_shunting_forearm;
        let x14 = f_shunting_forearm - 1.0;
        let x15 = Cfo_plasma_tal*x14;
        let x16 = 1.0*Qfo;
        let x17 = f_shunts*x2;
        let x18 = f_shunts - 1.0;
        let x19 = Chv_tal*Qh;
        let x20 = f_shunts*x3;
        let x21 = 1.0*x18*x4;
        let x22 = 1.0*Qpo;
        let x23 = ftissue_tal*x6;
        let x24 = 1.0*Qlu;
        let x25 = 1.0*ftissue_tal;
        let x26 = 1.0*Qre;
        let x27 = 1.0*Qfo*x14;
        let x28 = Qfo*f_shunting_forearm;
        let x29 = 1.0*Qh;
        let x30 = x25*x6;
        let x31 = -1.0*x25;

        // Derivatives
        dy[0] = x0*(Car_tal - 1.0*Cki_plasma_tal);
        dy[1] = (x1 - 1.0)*(Cli_plasma_tal*x4 - 1.0*x2 - 1.0*x3);
        dy[2] = 1.0*x5 + 1.0*x7 + 1.0*x8;
        dy[3] = x9*(Car_tal - 1.0*Cgu_plasma_tal);
        dy[4] = 1.0*x10 + 1.0*x11 - 1.0*x12;
        dy[5] = x16*(-1.0*Car_tal*x14 - 1.0*x13 + x15);
        dy[6] = 1.0*Car_tal*Qfo*x14 - 1.0*Car_tal*Qgu + 1.0*Car_tal*Qha*x18 - 1.0*Car_tal*Qki + 1.0*Cfo_plasma_tal*Qfo*x14 - 1.0*Qfo*x13 - 1.0*x10 - 1.0*x17 - 1.0*x8;
        dy[7] = 1.0*Cfov_tal*Qfo + 1.0*Cki_plasma_tal*Qki + 1.0*IVDOSE_tal*Ki_tal*Mr_tal.powi(-1) + 1.0*x12 + 1.0*x19 - 1.0*x5;
        dy[8] = 1.0*Cgu_plasma_tal*Qgu + 1.0*x18*x3 - 1.0*x20;
        dy[9] = -1.0*Cli_plasma_tal*x18*x4 + 1.0*x17 - 1.0*x19 + 1.0*x20;
        dy[10] = x16*(-1.0*Cfov_tal + x13 - 1.0*x15);
        dy[11] = -1.0*x7;
        dy[12] = -1.0*x11;
        dy[13] = 0.0;
        dy[14] = 0.0;
        dy[15] = 0.0;
    };

    // Jacobian Closure (Matrix-Vector Product)
    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..jv.len() { jv[i] = 0.0; }

        // Map species names to y indices
        let Cki_plasma_tal = y[0];
        let Cli_plasma_tal = y[1];
        let Clu_plasma_tal = y[2];
        let Cgu_plasma_tal = y[3];
        let Cre_plasma_tal = y[4];
        let Cfo_plasma_tal = y[5];
        let Car_tal = y[6];
        let Cve_tal = y[7];
        let Cpo_tal = y[8];
        let Chv_tal = y[9];
        let Cfov_tal = y[10];
        let Clu_tal = y[11];
        let Cre_tal = y[12];
        let Aurine_tal = y[13];
        let Afeces_tal = y[14];
        let Cduodenum_tal = y[15];

        // Temporary variables (CSE)
        let x0 = 1.0*Qki;
        let x1 = 1.0*f_shunts;
        let x2 = Car_tal*Qha;
        let x3 = Cpo_tal*Qpo;
        let x4 = Qha + Qpo;
        let x5 = Cve_tal*Qlu;
        let x6 = Kp_tal*fup_tal;
        let x7 = ftissue_tal*(-1.0*Clu_plasma_tal*x6 + Clu_tal);
        let x8 = -1.0*Clu_plasma_tal*Qlu;
        let x9 = 1.0*Qgu;
        let x10 = Car_tal*Qre;
        let x11 = ftissue_tal*(-1.0*Cre_plasma_tal*x6 + Cre_tal);
        let x12 = Cre_plasma_tal*Qre;
        let x13 = Car_tal*f_shunting_forearm;
        let x14 = f_shunting_forearm - 1.0;
        let x15 = Cfo_plasma_tal*x14;
        let x16 = 1.0*Qfo;
        let x17 = f_shunts*x2;
        let x18 = f_shunts - 1.0;
        let x19 = Chv_tal*Qh;
        let x20 = f_shunts*x3;
        let x21 = 1.0*x18*x4;
        let x22 = 1.0*Qpo;
        let x23 = ftissue_tal*x6;
        let x24 = 1.0*Qlu;
        let x25 = 1.0*ftissue_tal;
        let x26 = 1.0*Qre;
        let x27 = 1.0*Qfo*x14;
        let x28 = Qfo*f_shunting_forearm;
        let x29 = 1.0*Qh;
        let x30 = x25*x6;
        let x31 = -1.0*x25;

        // Jacobian-Vector Product
        jv[0] += (-1.0*x0) * v[0];
        jv[0] += (x0) * v[6];
        jv[1] += (x21) * v[1];
        jv[1] += (-1.0*Qha*x18) * v[6];
        jv[1] += (-1.0*x18*x22) * v[8];
        jv[2] += (-1.0*Qlu - 1.0*x23) * v[2];
        jv[2] += (x24) * v[7];
        jv[2] += (x25) * v[11];
        jv[3] += (-1.0*x9) * v[3];
        jv[3] += (x9) * v[6];
        jv[4] += (-1.0*Qre - 1.0*x23) * v[4];
        jv[4] += (x26) * v[6];
        jv[4] += (x25) * v[12];
        jv[5] += (x27) * v[5];
        jv[5] += (-1.0*x16*(2.0*f_shunting_forearm - 1.0)) * v[6];
        jv[6] += (x24) * v[2];
        jv[6] += (x27) * v[5];
        jv[6] += (1.0*Qfo*x14 - 1.0*Qgu - 1.0*Qha*f_shunts + 1.0*Qha*x18 - 1.0*Qki - 1.0*Qre - 1.0*x28) * v[6];
        jv[7] += (x0) * v[0];
        jv[7] += (x26) * v[4];
        jv[7] += (-1.0*x24) * v[7];
        jv[7] += (x29) * v[9];
        jv[7] += (x16) * v[10];
        jv[8] += (x9) * v[3];
        jv[8] += (-1.0*x22) * v[8];
        jv[9] += (-1.0*x21) * v[1];
        jv[9] += (Qha*x1) * v[6];
        jv[9] += (Qpo*x1) * v[8];
        jv[9] += (-1.0*x29) * v[9];
        jv[10] += (-1.0*x27) * v[5];
        jv[10] += (1.0*x28) * v[6];
        jv[10] += (-1.0*x16) * v[10];
        jv[11] += (x30) * v[2];
        jv[11] += (x31) * v[11];
        jv[12] += (x30) * v[4];
        jv[12] += (x31) * v[12];
    };

    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..16 { y[i] = 0.0; }
    };

    let problem = OdeBuilder::<M>::new()
        .rhs_implicit(rhs, jac)
        .init(init, 16)
        
        .build()
        .unwrap();

    let mut solver = problem.bdf::<LS>().unwrap();
    let mut time = Vec::new();

    // Initialize result vectors
    let mut cki_plasma_tal = Vec::new();
    let mut cli_plasma_tal = Vec::new();
    let mut clu_plasma_tal = Vec::new();
    let mut cgu_plasma_tal = Vec::new();
    let mut cre_plasma_tal = Vec::new();
    let mut cfo_plasma_tal = Vec::new();
    let mut car_tal = Vec::new();
    let mut cve_tal = Vec::new();
    let mut cpo_tal = Vec::new();
    let mut chv_tal = Vec::new();
    let mut cfov_tal = Vec::new();
    let mut clu_tal = Vec::new();
    let mut cre_tal = Vec::new();
    let mut aurine_tal = Vec::new();
    let mut afeces_tal = Vec::new();
    let mut cduodenum_tal = Vec::new();

    cki_plasma_tal.push(solver.state().y[0]);
    cli_plasma_tal.push(solver.state().y[1]);
    clu_plasma_tal.push(solver.state().y[2]);
    cgu_plasma_tal.push(solver.state().y[3]);
    cre_plasma_tal.push(solver.state().y[4]);
    cfo_plasma_tal.push(solver.state().y[5]);
    car_tal.push(solver.state().y[6]);
    cve_tal.push(solver.state().y[7]);
    cpo_tal.push(solver.state().y[8]);
    chv_tal.push(solver.state().y[9]);
    cfov_tal.push(solver.state().y[10]);
    clu_tal.push(solver.state().y[11]);
    cre_tal.push(solver.state().y[12]);
    aurine_tal.push(solver.state().y[13]);
    afeces_tal.push(solver.state().y[14]);
    cduodenum_tal.push(solver.state().y[15]);
    time.push(0.0);

    let final_time = sim_params.final_time.unwrap_or(24.0);
    solver.set_stop_time(final_time).unwrap();
    loop {
        match solver.step() {
            Ok(OdeSolverStopReason::InternalTimestep) => {
            cki_plasma_tal.push(solver.state().y[0]);
            cli_plasma_tal.push(solver.state().y[1]);
            clu_plasma_tal.push(solver.state().y[2]);
            cgu_plasma_tal.push(solver.state().y[3]);
            cre_plasma_tal.push(solver.state().y[4]);
            cfo_plasma_tal.push(solver.state().y[5]);
            car_tal.push(solver.state().y[6]);
            cve_tal.push(solver.state().y[7]);
            cpo_tal.push(solver.state().y[8]);
            chv_tal.push(solver.state().y[9]);
            cfov_tal.push(solver.state().y[10]);
            clu_tal.push(solver.state().y[11]);
            cre_tal.push(solver.state().y[12]);
            aurine_tal.push(solver.state().y[13]);
            afeces_tal.push(solver.state().y[14]);
            cduodenum_tal.push(solver.state().y[15]);
                time.push(solver.state().t);
            },
            Ok(OdeSolverStopReason::TstopReached) => break,
            Err(_) => panic!("Solver Error"),
        }
    }

    let mut species_map = HashMap::new();
        species_map.insert("cki_plasma_tal".to_string(), cki_plasma_tal);
        species_map.insert("cli_plasma_tal".to_string(), cli_plasma_tal);
        species_map.insert("clu_plasma_tal".to_string(), clu_plasma_tal);
        species_map.insert("cgu_plasma_tal".to_string(), cgu_plasma_tal);
        species_map.insert("cre_plasma_tal".to_string(), cre_plasma_tal);
        species_map.insert("cfo_plasma_tal".to_string(), cfo_plasma_tal);
        species_map.insert("car_tal".to_string(), car_tal);
        species_map.insert("cve_tal".to_string(), cve_tal);
        species_map.insert("cpo_tal".to_string(), cpo_tal);
        species_map.insert("chv_tal".to_string(), chv_tal);
        species_map.insert("cfov_tal".to_string(), cfov_tal);
        species_map.insert("clu_tal".to_string(), clu_tal);
        species_map.insert("cre_tal".to_string(), cre_tal);
        species_map.insert("aurine_tal".to_string(), aurine_tal);
        species_map.insert("afeces_tal".to_string(), afeces_tal);
        species_map.insert("cduodenum_tal".to_string(), cduodenum_tal);

    let result = SimulationResult {
        time,
        species: species_map,
    };

    serde_json::to_string(&result).unwrap()
}
