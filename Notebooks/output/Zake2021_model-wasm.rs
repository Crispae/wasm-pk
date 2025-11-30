#![recursion_limit = "256"]
// Generated WASM-compatible Rust code from SBML model: Zake2021_model
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
    pub Metformin_Dose_in_Lumen_in_mg: f64,
    pub Body_Weight: f64,
    pub Metformin_Dose_in_Plasma_in_mg: f64,
    pub Cardiac_Output: f64,
    pub Ktp_Liver: f64,
    pub Ktp_Brain: f64,
    pub Ktp_Adipose: f64,
    pub Ktp_Heart: f64,
    pub Ktp_Kidney: f64,
    pub Ktp_Muscle: f64,
    pub Ktp_Remainder: f64,
    pub Ktp_Lung: f64,
    pub Ktp_Stomach: f64,
    pub Ktp_IntestineVascular: f64,
    pub Qgfr: f64,
    pub IntestineLumen: f64,
    pub Urine: f64,
    pub Feces: f64,
    pub StomachLumen: f64,

    // Initial amounts (optional, for runtime dosing)
    pub init_mLiver: Option<f64>,
    pub init_mKidneyPlasma: Option<f64>,
    pub init_mRemainder: Option<f64>,
    pub init_mPlasmaVenous: Option<f64>,
    pub init_mHeart: Option<f64>,
    pub init_mMuscle: Option<f64>,
    pub init_mAdipose: Option<f64>,
    pub init_mBrain: Option<f64>,
    pub init_mFeces: Option<f64>,
    pub init_mUrine: Option<f64>,
    pub init_mIntestineLumen: Option<f64>,
    pub init_mPlasmaArterial: Option<f64>,
    pub init_mLung: Option<f64>,
    pub init_mPortalVein: Option<f64>,
    pub init_mStomach: Option<f64>,
    pub init_mIntestineEnterocytes: Option<f64>,
    pub init_mKidneyTissue: Option<f64>,
    pub init_mIntestineVascular: Option<f64>,
    pub init_mStomachLumen: Option<f64>,
    pub init_mKidneyTubular: Option<f64>,
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

    let Metformin_Dose_in_Lumen_in_mg = sim_params.Metformin_Dose_in_Lumen_in_mg;
    let Body_Weight = sim_params.Body_Weight;
    let Metformin_Dose_in_Plasma_in_mg = sim_params.Metformin_Dose_in_Plasma_in_mg;
    let Cardiac_Output = sim_params.Cardiac_Output;
    let Ktp_Liver = sim_params.Ktp_Liver;
    let Ktp_Brain = sim_params.Ktp_Brain;
    let Ktp_Adipose = sim_params.Ktp_Adipose;
    let Ktp_Heart = sim_params.Ktp_Heart;
    let Ktp_Kidney = sim_params.Ktp_Kidney;
    let Ktp_Muscle = sim_params.Ktp_Muscle;
    let Ktp_Remainder = sim_params.Ktp_Remainder;
    let Ktp_Lung = sim_params.Ktp_Lung;
    let Ktp_Stomach = sim_params.Ktp_Stomach;
    let Ktp_IntestineVascular = sim_params.Ktp_IntestineVascular;
    let Qgfr = sim_params.Qgfr;
    let IntestineLumen = sim_params.IntestineLumen;
    let Urine = sim_params.Urine;
    let Feces = sim_params.Feces;
    let StomachLumen = sim_params.StomachLumen;


    let mPlasmaVenous = 1000000.0_f64*Metformin_Dose_in_Plasma_in_mg*(3229.0/25.0*PlasmaVenous).powi(-1)*PlasmaVenous;
    let Compartment_10 = Adipose;
    let Compartment_9 = Brain;
    let Compartment_6 = Feces;
    let Compartment_7 = Heart;
    let Compartment_15 = IntestineEnterocytes;
    let Compartment_0 = IntestineLumen;
    let Compartment_17 = IntestineVascular;
    let Compartment_2 = KidneyPlasma;
    let Compartment_16 = KidneyTissue;
    let Compartment_19 = KidneyTubular;
    let Compartment_1 = Liver;
    let Compartment_12 = Lung;
    let Compartment_8 = Muscle;
    let Compartment_11 = PlasmaArterial;
    let Compartment_4 = PlasmaVenous;
    let Compartment_13 = PortalVein;
    let Compartment_3 = Remainder;
    let Compartment_18 = StomachLumen;
    let Compartment_14 = Stomach;
    let Compartment_5 = Urine;
    let ModelValue_1 = Body_Weight;
    let ModelValue_3 = Cardiac_Output;
    let ModelValue_0 = Metformin_Dose_in_Lumen_in_mg;
    let ModelValue_37 = QIntestineVascular;
    let ModelValue_34 = QLiverArtery;
    let ModelValue_47 = QPortalVeinOut;
    let ModelValue_36 = QPortalVein;
    let ModelValue_35 = QStomach;

    let root_fn = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, roots: &mut diffsol::NalgebraVec<f64>| {
        roots[0] = 1.0; // Oral_at_0_001: parse error
    };

    // RHS Closure
    let rhs = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, dy: &mut diffsol::NalgebraVec<f64>| {
        // Map species names to y indices
        let mLiver = y[0];
        let mKidneyPlasma = y[1];
        let mRemainder = y[2];
        let mPlasmaVenous = y[3];
        let mHeart = y[4];
        let mMuscle = y[5];
        let mAdipose = y[6];
        let mBrain = y[7];
        let mFeces = y[8];
        let mUrine = y[9];
        let mIntestineLumen = y[10];
        let mPlasmaArterial = y[11];
        let mLung = y[12];
        let mPortalVein = y[13];
        let mStomach = y[14];
        let mIntestineEnterocytes = y[15];
        let mKidneyTissue = y[16];
        let mIntestineVascular = y[17];
        let mStomachLumen = y[18];
        let mKidneyTubular = y[19];

        // Assignment Rules
    let mgUrine = 1.0/1000000.0*3229.0/25.0*mUrine*Urine.powi(-1)*Compartment_5;
    let mgFeces = 1.0/1000000.0*3229.0/25.0*mFeces*Feces.powi(-1)*Compartment_6;
    let Liver = 549.0/10000.0*ModelValue_1;
    let KidneyPlasma = 7.0/1250.0*ModelValue_1;
    let Remainder = 717.0/2000.0*ModelValue_1;
    let PlasmaVenous = 3.0/80.0*ModelValue_1;
    let Heart = 1.0/200.0*ModelValue_1;
    let Muscle = 48.0/125.0*ModelValue_1;
    let Brain = 33.0/2000.0*ModelValue_1;
    let Adipose = 7.0/100.0*ModelValue_1;
    let PlasmaArterial = 1.0/80.0*ModelValue_1;
    let Lung = 73.0/10000.0*ModelValue_1;
    let PortalVein = 29.0/5000.0*ModelValue_1;
    let Stomach = 3.0/500.0*ModelValue_1;
    let IntestineEnterocytes = 1.0/400.0*ModelValue_1;
    let KidneyTissue = 7.0/1250.0*ModelValue_1;
    let IntestineVascular = 57.0/2500.0*ModelValue_1;
    let KidneyTubular = 7.0/1250.0*ModelValue_1;
    let QAdipose = 1.0/200.0*ModelValue_3;
    let QBrain = 33.0/1000.0*ModelValue_3;
    let QHeart = 33.0/500.0*ModelValue_3;
    let QKidney = 91.0/1000.0*ModelValue_3;
    let QMuscle = 159.0/1000.0*ModelValue_3;
    let QRemainder = 411.0/1000.0*ModelValue_3;
    let mgIntestineLumen = 1.0/1000000.0*3229.0/25.0*mIntestineLumen*IntestineLumen.powi(-1)*Compartment_0;
    let mgStomachLumen = 1.0/1000000.0*3229.0/25.0*mStomachLumen*StomachLumen.powi(-1)*Compartment_18;
    let QLiverArtery = 1.0/50.0*ModelValue_3;
    let QStomach = 1.0/50.0*ModelValue_3;
    let QPortalVein = 3.0/50.0*ModelValue_3;
    let QIntestineVascular = 27.0/200.0*ModelValue_3;
    let QPortalVeinOut = ModelValue_37 + (ModelValue_35 + ModelValue_36);
    let QLiverOut = ModelValue_34 + ModelValue_47;
    let mgLiver = 1.0/1000000.0*3229.0/25.0*mLiver*Liver.powi(-1)*Compartment_1;
    let mgKidneyPlasma = 1.0/1000000.0*3229.0/25.0*mKidneyPlasma*KidneyPlasma.powi(-1)*Compartment_2;
    let mgRemainder = 1.0/1000000.0*3229.0/25.0*mRemainder*Remainder.powi(-1)*Compartment_3;
    let mgPlasmaVenous = 1.0/1000000.0*3229.0/25.0*mPlasmaVenous*PlasmaVenous.powi(-1)*Compartment_4;
    let mgHeart = 1.0/1000000.0*3229.0/25.0*mHeart*Heart.powi(-1)*Compartment_7;
    let mgMuscle = 1.0/1000000.0*3229.0/25.0*mMuscle*Muscle.powi(-1)*Compartment_8;
    let mgBrain = 1.0/1000000.0*3229.0/25.0*mBrain*Brain.powi(-1)*Compartment_9;
    let mgAdipose = 1.0/1000000.0*3229.0/25.0*mAdipose*Adipose.powi(-1)*Compartment_10;
    let mArterialPlasma__for_kidney = mPlasmaArterial*PlasmaArterial.powi(-1);
    let mgPlasmaArterial = 1.0/1000000.0*3229.0/25.0*mPlasmaArterial*PlasmaArterial.powi(-1)*Compartment_11;
    let mgLung = 1.0/1000000.0*3229.0/25.0*mLung*Lung.powi(-1)*Compartment_12;
    let mgPortalVein = 1.0/1000000.0*3229.0/25.0*mPortalVein*PortalVein.powi(-1)*Compartment_13;
    let mgStomach = 1.0/1000000.0*3229.0/25.0*mStomach*Stomach.powi(-1)*Compartment_14;
    let mgIntestineEnterocytes = 1.0/1000000.0*3229.0/25.0*mIntestineEnterocytes*IntestineEnterocytes.powi(-1)*Compartment_15;
    let mgKidneyTissues = 1.0/1000000.0*3229.0/25.0*Compartment_16*mKidneyTissue*KidneyTissue.powi(-1);
    let mgIntestineVascular = 1.0/1000000.0*3229.0/25.0*mIntestineVascular*IntestineVascular.powi(-1)*Compartment_17;
    let mIntestineSum = (mIntestineEnterocytes*IntestineEnterocytes.powi(-1)*Compartment_15 + Compartment_17*mIntestineVascular*IntestineVascular.powi(-1))*(Compartment_15 + Compartment_17).powi(-1);
    let mKidneySum = (Compartment_19*mKidneyTubular*KidneyTubular.powi(-1) + (Compartment_16*mKidneyTissue*KidneyTissue.powi(-1) + Compartment_2*mKidneyPlasma*KidneyPlasma.powi(-1)))*(Compartment_19 + (Compartment_16 + Compartment_2)).powi(-1);
    let mgKidneyTubular = 1.0/1000000.0*3229.0/25.0*Compartment_19*mKidneyTubular*KidneyTubular.powi(-1);
    let mgIntestineTotal = mgIntestineEnterocytes + mgIntestineVascular;
    let mgKidneyTotal = mgKidneyTubular + (mgKidneyPlasma + mgKidneyTissues);

        // Temporary variables (CSE)
        let x0 = PlasmaArterial.powi(-1);
        let x1 = mPlasmaArterial*x0;
        let x2 = QLiverArtery*x1;
        let x3 = QPortalVeinOut*PortalVein.powi(-1);
        let x4 = mPortalVein*x3;
        let x5 = QLiverOut*Ktp_Liver.powi(-1)*Liver.powi(-1);
        let x6 = mLiver*x5;
        let x7 = Qgfr*mArterialPlasma__for_kidney;
        let x8 = QKidney*x1;
        let x9 = KidneyPlasma.powi(-1);
        let x10 = mKidneyPlasma*x9;
        let x11 = QKidney*Ktp_Kidney.powi(-1);
        let x12 = x10*x11;
        let x13 = Km + x10;
        let x14 = x13.powi(-1);
        let x15 = V*x14;
        let x16 = Ktp_Remainder.powi(-1)*Remainder.powi(-1);
        let x17 = mRemainder*x16;
        let x18 = 1.0*QRemainder;
        let x19 = PlasmaVenous.powi(-1);
        let x20 = mPlasmaVenous*x19;
        let x21 = Adipose.powi(-1)*Ktp_Adipose.powi(-1);
        let x22 = mAdipose*x21;
        let x23 = Brain.powi(-1)*Ktp_Brain.powi(-1);
        let x24 = mBrain*x23;
        let x25 = Heart.powi(-1)*Ktp_Heart.powi(-1);
        let x26 = mHeart*x25;
        let x27 = Ktp_Muscle.powi(-1)*Muscle.powi(-1);
        let x28 = mMuscle*x27;
        let x29 = 1.0*QHeart;
        let x30 = 1.0*QMuscle;
        let x31 = 1.0*QAdipose;
        let x32 = 1.0*QBrain;
        let x33 = IntestineLumen.powi(-1);
        let x34 = mIntestineLumen*x33;
        let x35 = k1*x34;
        let x36 = k1*KidneyTubular.powi(-1);
        let x37 = mKidneyTubular*x36;
        let x38 = 1.0*k1;
        let x39 = x38*StomachLumen.powi(-1);
        let x40 = mStomachLumen*x39;
        let x41 = IntestineEnterocytes.powi(-1);
        let x42 = mIntestineEnterocytes*x41;
        let x43 = k2*x42;
        let x44 = IntestineVascular.powi(-1);
        let x45 = k2*x44;
        let x46 = mIntestineVascular*x45;
        let x47 = 3.0*k1;
        let x48 = Km + x34;
        let x49 = V*x48.powi(-1);
        let x50 = 2.0*x49;
        let x51 = QIntestineVascular*x1;
        let x52 = QPortalVein*x1;
        let x53 = Ktp_Lung.powi(-1);
        let x54 = Lung.powi(-1);
        let x55 = x53*x54;
        let x56 = 1.0*Cardiac_Output;
        let x57 = QIntestineVascular*Ktp_IntestineVascular.powi(-1);
        let x58 = mIntestineVascular*x44*x57;
        let x59 = Ktp_Stomach.powi(-1)*Stomach.powi(-1);
        let x60 = mStomach*x59;
        let x61 = 1.0*QStomach;
        let x62 = Km + x42;
        let x63 = x62.powi(-1);
        let x64 = V*x63;
        let x65 = x42*x64;
        let x66 = x34*x49 + x35;
        let x67 = KidneyTissue.powi(-1);
        let x68 = mKidneyTissue*x67;
        let x69 = (Km + x68).powi(-1);
        let x70 = x68*x69;
        let x71 = -1.0_f64*x10*x14;
        let x72 = 1.0*V;
        let x73 = 1.0*x5;
        let x74 = 1.0*x0;
        let x75 = 1.0*x3;
        let x76 = 1.0*x9;
        let x77 = x16*x18;
        let x78 = x19*x56;
        let x79 = x25*x29;
        let x80 = x27*x30;
        let x81 = x21*x31;
        let x82 = x23*x32;
        let x83 = 1.0*x36;
        let x84 = x48.powi(-2);
        let x85 = 1.0*x41;
        let x86 = x55*x56;
        let x87 = x59*x61;
        let x88 = 1.0*x44;
        let x89 = 1.0*x33*(-1.0_f64*V*x34*x84 + k1 + x49);
        let x90 = 1.0_f64 - 1.0_f64*x70;
        let x91 = x67*x69*x72;

        // Derivatives
        dy[0] = 1.0*x2 + 1.0*x4 - 1.0*x6;
        dy[1] = -1.0*x10*x15 - 1.0*x12 - 1.0*x7 + 1.0*x8;
        dy[2] = x18*(x1 - 1.0_f64*x17);
        dy[3] = -1.0*Cardiac_Output*x20 + 1.0*QAdipose*x22 + 1.0*QBrain*x24 + 1.0*QHeart*x26 + 1.0*QMuscle*x28 + 1.0*QRemainder*x17 + 1.0*x12 + 1.0*x6;
        dy[4] = x29*(x1 - 1.0_f64*x26);
        dy[5] = x30*(x1 - 1.0_f64*x28);
        dy[6] = x31*(x1 - 1.0_f64*x22);
        dy[7] = x32*(x1 - 1.0_f64*x24);
        dy[8] = 1.0*x35;
        dy[9] = 1.0*x37;
        dy[10] = -1.0_f64*x34*x47 - 1.0_f64*x34*x50 + x40 + 1.0*x43 + 1.0*x46;
        dy[11] = 1.0*Cardiac_Output*mLung*x53*x54 - 1.0*QAdipose*x1 - 1.0*QBrain*x1 - 1.0*QHeart*x1 - 1.0*QMuscle*x1 - 1.0*QRemainder*x1 - 1.0*QStomach*x1 - 1.0*x2 - 1.0*x51 - 1.0*x52 - 1.0*x8;
        dy[12] = x56*(-1.0_f64*mLung*x55 + x20);
        dy[13] = 1.0*QStomach*x60 - 1.0*x4 + 1.0*x52 + 1.0*x58;
        dy[14] = x61*(x1 - 1.0_f64*x60);
        dy[15] = -1.0*x43 - 1.0*x65 + 1.0*x66;
        dy[16] = x72*(-1.0_f64*x70 - 1.0_f64*x71);
        dy[17] = -1.0*x46 + 1.0*x51 - 1.0*x58 + 1.0*x65 + 1.0*x66;
        dy[18] = -1.0_f64*x40;
        dy[19] = 1.0*V*x70 - 1.0*x37 + 1.0*x7;
    };

    // Jacobian Closure (Matrix-Vector Product)
    let jac = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, v: &diffsol::NalgebraVec<f64>, jv: &mut diffsol::NalgebraVec<f64>| {
        for i in 0..jv.len() { jv[i] = 0.0; }

        // Map species names to y indices
        let mLiver = y[0];
        let mKidneyPlasma = y[1];
        let mRemainder = y[2];
        let mPlasmaVenous = y[3];
        let mHeart = y[4];
        let mMuscle = y[5];
        let mAdipose = y[6];
        let mBrain = y[7];
        let mFeces = y[8];
        let mUrine = y[9];
        let mIntestineLumen = y[10];
        let mPlasmaArterial = y[11];
        let mLung = y[12];
        let mPortalVein = y[13];
        let mStomach = y[14];
        let mIntestineEnterocytes = y[15];
        let mKidneyTissue = y[16];
        let mIntestineVascular = y[17];
        let mStomachLumen = y[18];
        let mKidneyTubular = y[19];

        // Assignment Rules
    let mgUrine = 1.0/1000000.0*3229.0/25.0*mUrine*Urine.powi(-1)*Compartment_5;
    let mgFeces = 1.0/1000000.0*3229.0/25.0*mFeces*Feces.powi(-1)*Compartment_6;
    let Liver = 549.0/10000.0*ModelValue_1;
    let KidneyPlasma = 7.0/1250.0*ModelValue_1;
    let Remainder = 717.0/2000.0*ModelValue_1;
    let PlasmaVenous = 3.0/80.0*ModelValue_1;
    let Heart = 1.0/200.0*ModelValue_1;
    let Muscle = 48.0/125.0*ModelValue_1;
    let Brain = 33.0/2000.0*ModelValue_1;
    let Adipose = 7.0/100.0*ModelValue_1;
    let PlasmaArterial = 1.0/80.0*ModelValue_1;
    let Lung = 73.0/10000.0*ModelValue_1;
    let PortalVein = 29.0/5000.0*ModelValue_1;
    let Stomach = 3.0/500.0*ModelValue_1;
    let IntestineEnterocytes = 1.0/400.0*ModelValue_1;
    let KidneyTissue = 7.0/1250.0*ModelValue_1;
    let IntestineVascular = 57.0/2500.0*ModelValue_1;
    let KidneyTubular = 7.0/1250.0*ModelValue_1;
    let QAdipose = 1.0/200.0*ModelValue_3;
    let QBrain = 33.0/1000.0*ModelValue_3;
    let QHeart = 33.0/500.0*ModelValue_3;
    let QKidney = 91.0/1000.0*ModelValue_3;
    let QMuscle = 159.0/1000.0*ModelValue_3;
    let QRemainder = 411.0/1000.0*ModelValue_3;
    let mgIntestineLumen = 1.0/1000000.0*3229.0/25.0*mIntestineLumen*IntestineLumen.powi(-1)*Compartment_0;
    let mgStomachLumen = 1.0/1000000.0*3229.0/25.0*mStomachLumen*StomachLumen.powi(-1)*Compartment_18;
    let QLiverArtery = 1.0/50.0*ModelValue_3;
    let QStomach = 1.0/50.0*ModelValue_3;
    let QPortalVein = 3.0/50.0*ModelValue_3;
    let QIntestineVascular = 27.0/200.0*ModelValue_3;
    let QPortalVeinOut = ModelValue_37 + (ModelValue_35 + ModelValue_36);
    let QLiverOut = ModelValue_34 + ModelValue_47;
    let mgLiver = 1.0/1000000.0*3229.0/25.0*mLiver*Liver.powi(-1)*Compartment_1;
    let mgKidneyPlasma = 1.0/1000000.0*3229.0/25.0*mKidneyPlasma*KidneyPlasma.powi(-1)*Compartment_2;
    let mgRemainder = 1.0/1000000.0*3229.0/25.0*mRemainder*Remainder.powi(-1)*Compartment_3;
    let mgPlasmaVenous = 1.0/1000000.0*3229.0/25.0*mPlasmaVenous*PlasmaVenous.powi(-1)*Compartment_4;
    let mgHeart = 1.0/1000000.0*3229.0/25.0*mHeart*Heart.powi(-1)*Compartment_7;
    let mgMuscle = 1.0/1000000.0*3229.0/25.0*mMuscle*Muscle.powi(-1)*Compartment_8;
    let mgBrain = 1.0/1000000.0*3229.0/25.0*mBrain*Brain.powi(-1)*Compartment_9;
    let mgAdipose = 1.0/1000000.0*3229.0/25.0*mAdipose*Adipose.powi(-1)*Compartment_10;
    let mArterialPlasma__for_kidney = mPlasmaArterial*PlasmaArterial.powi(-1);
    let mgPlasmaArterial = 1.0/1000000.0*3229.0/25.0*mPlasmaArterial*PlasmaArterial.powi(-1)*Compartment_11;
    let mgLung = 1.0/1000000.0*3229.0/25.0*mLung*Lung.powi(-1)*Compartment_12;
    let mgPortalVein = 1.0/1000000.0*3229.0/25.0*mPortalVein*PortalVein.powi(-1)*Compartment_13;
    let mgStomach = 1.0/1000000.0*3229.0/25.0*mStomach*Stomach.powi(-1)*Compartment_14;
    let mgIntestineEnterocytes = 1.0/1000000.0*3229.0/25.0*mIntestineEnterocytes*IntestineEnterocytes.powi(-1)*Compartment_15;
    let mgKidneyTissues = 1.0/1000000.0*3229.0/25.0*Compartment_16*mKidneyTissue*KidneyTissue.powi(-1);
    let mgIntestineVascular = 1.0/1000000.0*3229.0/25.0*mIntestineVascular*IntestineVascular.powi(-1)*Compartment_17;
    let mIntestineSum = (mIntestineEnterocytes*IntestineEnterocytes.powi(-1)*Compartment_15 + Compartment_17*mIntestineVascular*IntestineVascular.powi(-1))*(Compartment_15 + Compartment_17).powi(-1);
    let mKidneySum = (Compartment_19*mKidneyTubular*KidneyTubular.powi(-1) + (Compartment_16*mKidneyTissue*KidneyTissue.powi(-1) + Compartment_2*mKidneyPlasma*KidneyPlasma.powi(-1)))*(Compartment_19 + (Compartment_16 + Compartment_2)).powi(-1);
    let mgKidneyTubular = 1.0/1000000.0*3229.0/25.0*Compartment_19*mKidneyTubular*KidneyTubular.powi(-1);
    let mgIntestineTotal = mgIntestineEnterocytes + mgIntestineVascular;
    let mgKidneyTotal = mgKidneyTubular + (mgKidneyPlasma + mgKidneyTissues);

        // Temporary variables (CSE)
        let x0 = PlasmaArterial.powi(-1);
        let x1 = mPlasmaArterial*x0;
        let x2 = QLiverArtery*x1;
        let x3 = QPortalVeinOut*PortalVein.powi(-1);
        let x4 = mPortalVein*x3;
        let x5 = QLiverOut*Ktp_Liver.powi(-1)*Liver.powi(-1);
        let x6 = mLiver*x5;
        let x7 = Qgfr*mArterialPlasma__for_kidney;
        let x8 = QKidney*x1;
        let x9 = KidneyPlasma.powi(-1);
        let x10 = mKidneyPlasma*x9;
        let x11 = QKidney*Ktp_Kidney.powi(-1);
        let x12 = x10*x11;
        let x13 = Km + x10;
        let x14 = x13.powi(-1);
        let x15 = V*x14;
        let x16 = Ktp_Remainder.powi(-1)*Remainder.powi(-1);
        let x17 = mRemainder*x16;
        let x18 = 1.0*QRemainder;
        let x19 = PlasmaVenous.powi(-1);
        let x20 = mPlasmaVenous*x19;
        let x21 = Adipose.powi(-1)*Ktp_Adipose.powi(-1);
        let x22 = mAdipose*x21;
        let x23 = Brain.powi(-1)*Ktp_Brain.powi(-1);
        let x24 = mBrain*x23;
        let x25 = Heart.powi(-1)*Ktp_Heart.powi(-1);
        let x26 = mHeart*x25;
        let x27 = Ktp_Muscle.powi(-1)*Muscle.powi(-1);
        let x28 = mMuscle*x27;
        let x29 = 1.0*QHeart;
        let x30 = 1.0*QMuscle;
        let x31 = 1.0*QAdipose;
        let x32 = 1.0*QBrain;
        let x33 = IntestineLumen.powi(-1);
        let x34 = mIntestineLumen*x33;
        let x35 = k1*x34;
        let x36 = k1*KidneyTubular.powi(-1);
        let x37 = mKidneyTubular*x36;
        let x38 = 1.0*k1;
        let x39 = x38*StomachLumen.powi(-1);
        let x40 = mStomachLumen*x39;
        let x41 = IntestineEnterocytes.powi(-1);
        let x42 = mIntestineEnterocytes*x41;
        let x43 = k2*x42;
        let x44 = IntestineVascular.powi(-1);
        let x45 = k2*x44;
        let x46 = mIntestineVascular*x45;
        let x47 = 3.0*k1;
        let x48 = Km + x34;
        let x49 = V*x48.powi(-1);
        let x50 = 2.0*x49;
        let x51 = QIntestineVascular*x1;
        let x52 = QPortalVein*x1;
        let x53 = Ktp_Lung.powi(-1);
        let x54 = Lung.powi(-1);
        let x55 = x53*x54;
        let x56 = 1.0*Cardiac_Output;
        let x57 = QIntestineVascular*Ktp_IntestineVascular.powi(-1);
        let x58 = mIntestineVascular*x44*x57;
        let x59 = Ktp_Stomach.powi(-1)*Stomach.powi(-1);
        let x60 = mStomach*x59;
        let x61 = 1.0*QStomach;
        let x62 = Km + x42;
        let x63 = x62.powi(-1);
        let x64 = V*x63;
        let x65 = x42*x64;
        let x66 = x34*x49 + x35;
        let x67 = KidneyTissue.powi(-1);
        let x68 = mKidneyTissue*x67;
        let x69 = (Km + x68).powi(-1);
        let x70 = x68*x69;
        let x71 = -1.0_f64*x10*x14;
        let x72 = 1.0*V;
        let x73 = 1.0*x5;
        let x74 = 1.0*x0;
        let x75 = 1.0*x3;
        let x76 = 1.0*x9;
        let x77 = x16*x18;
        let x78 = x19*x56;
        let x79 = x25*x29;
        let x80 = x27*x30;
        let x81 = x21*x31;
        let x82 = x23*x32;
        let x83 = 1.0*x36;
        let x84 = x48.powi(-2);
        let x85 = 1.0*x41;
        let x86 = x55*x56;
        let x87 = x59*x61;
        let x88 = 1.0*x44;
        let x89 = 1.0*x33*(-1.0_f64*V*x34*x84 + k1 + x49);
        let x90 = 1.0_f64 - 1.0_f64*x70;
        let x91 = x67*x69*x72;

        // Jacobian-Vector Product
        jv[0] += (-1.0_f64*x73) * v[0];
        jv[0] += (QLiverArtery*x74) * v[11];
        jv[0] += (x75) * v[13];
        jv[1] += (x76*(V*mKidneyPlasma*x9*x13.powi(-2) - 1.0_f64*x11 - 1.0_f64*x15)) * v[1];
        jv[1] += (QKidney*x74) * v[11];
        jv[2] += (-1.0_f64*x77) * v[2];
        jv[2] += (x0*x18) * v[11];
        jv[3] += (x73) * v[0];
        jv[3] += (x11*x76) * v[1];
        jv[3] += (x77) * v[2];
        jv[3] += (-1.0_f64*x78) * v[3];
        jv[3] += (x79) * v[4];
        jv[3] += (x80) * v[5];
        jv[3] += (x81) * v[6];
        jv[3] += (x82) * v[7];
        jv[4] += (-1.0_f64*x79) * v[4];
        jv[4] += (x0*x29) * v[11];
        jv[5] += (-1.0_f64*x80) * v[5];
        jv[5] += (x0*x30) * v[11];
        jv[6] += (-1.0_f64*x81) * v[6];
        jv[6] += (x0*x31) * v[11];
        jv[7] += (-1.0_f64*x82) * v[7];
        jv[7] += (x0*x32) * v[11];
        jv[8] += (x33*x38) * v[10];
        jv[9] += (x83) * v[19];
        jv[10] += (x33*(2.0*V*mIntestineLumen*x33*x84 - 1.0_f64*x47 - 1.0_f64*x50)) * v[10];
        jv[10] += (k2*x85) * v[15];
        jv[10] += (1.0*x45) * v[17];
        jv[10] += (x39) * v[18];
        jv[11] += (-1.0_f64*x74*(QAdipose + QBrain + QHeart + QIntestineVascular + QKidney + QLiverArtery + QMuscle + QPortalVein + QRemainder + QStomach)) * v[11];
        jv[11] += (x86) * v[12];
        jv[12] += (x78) * v[3];
        jv[12] += (-1.0_f64*x86) * v[12];
        jv[13] += (QPortalVein*x74) * v[11];
        jv[13] += (-1.0_f64*x75) * v[13];
        jv[13] += (x87) * v[14];
        jv[13] += (x57*x88) * v[17];
        jv[14] += (x0*x61) * v[11];
        jv[14] += (-1.0_f64*x87) * v[14];
        jv[15] += (x89) * v[10];
        jv[15] += (x85*(V*mIntestineEnterocytes*x41*x62.powi(-2) - 1.0_f64*k2 - 1.0_f64*x64)) * v[15];
        jv[16] += (x15*x76*(x71 + 1.0_f64)) * v[1];
        jv[16] += (-1.0_f64*x90*x91) * v[16];
        jv[17] += (x89) * v[10];
        jv[17] += (QIntestineVascular*x74) * v[11];
        jv[17] += (x64*x85*(-1.0_f64*x42*x63 + 1.0_f64)) * v[15];
        jv[17] += (-1.0_f64*x88*(k2 + x57)) * v[17];
        jv[18] += (-1.0_f64*x39) * v[18];
        jv[19] += (x90*x91) * v[16];
        jv[19] += (-1.0_f64*x83) * v[19];
    };

    let init = |_y0: &diffsol::NalgebraVec<f64>, _t: f64, y: &mut diffsol::NalgebraVec<f64>| {
        y[0] = sim_params.init_mLiver.unwrap_or(0.0);
        y[1] = sim_params.init_mKidneyPlasma.unwrap_or(0.0);
        y[2] = sim_params.init_mRemainder.unwrap_or(0.0);
        y[3] = sim_params.init_mPlasmaVenous.unwrap_or(10645.7107463611);
        y[4] = sim_params.init_mHeart.unwrap_or(0.0);
        y[5] = sim_params.init_mMuscle.unwrap_or(0.0);
        y[6] = sim_params.init_mAdipose.unwrap_or(0.0);
        y[7] = sim_params.init_mBrain.unwrap_or(0.0);
        y[8] = sim_params.init_mFeces.unwrap_or(0.0);
        y[9] = sim_params.init_mUrine.unwrap_or(0.0);
        y[10] = sim_params.init_mIntestineLumen.unwrap_or(0.0);
        y[11] = sim_params.init_mPlasmaArterial.unwrap_or(0.0);
        y[12] = sim_params.init_mLung.unwrap_or(0.0);
        y[13] = sim_params.init_mPortalVein.unwrap_or(0.0);
        y[14] = sim_params.init_mStomach.unwrap_or(0.0);
        y[15] = sim_params.init_mIntestineEnterocytes.unwrap_or(0.0);
        y[16] = sim_params.init_mKidneyTissue.unwrap_or(0.0);
        y[17] = sim_params.init_mIntestineVascular.unwrap_or(0.0);
        y[18] = sim_params.init_mStomachLumen.unwrap_or(0.0);
        y[19] = sim_params.init_mKidneyTubular.unwrap_or(0.0);
    };
    let problem = OdeBuilder::<M>::new()
        .rhs_implicit(rhs, jac)
        .init(init, 20)
        .root(1, root_fn)
        .build()
        .unwrap();

    let mut solver = problem.bdf::<LS>().unwrap();
    let mut time = Vec::new();

    // Initialize result vectors
    let mut mliver = Vec::new();
    let mut mkidneyplasma = Vec::new();
    let mut mremainder = Vec::new();
    let mut mplasmavenous = Vec::new();
    let mut mheart = Vec::new();
    let mut mmuscle = Vec::new();
    let mut madipose = Vec::new();
    let mut mbrain = Vec::new();
    let mut mfeces = Vec::new();
    let mut murine = Vec::new();
    let mut mintestinelumen = Vec::new();
    let mut mplasmaarterial = Vec::new();
    let mut mlung = Vec::new();
    let mut mportalvein = Vec::new();
    let mut mstomach = Vec::new();
    let mut mintestineenterocytes = Vec::new();
    let mut mkidneytissue = Vec::new();
    let mut mintestinevascular = Vec::new();
    let mut mstomachlumen = Vec::new();
    let mut mkidneytubular = Vec::new();

    mliver.push(solver.state().y[0]);
    mkidneyplasma.push(solver.state().y[1]);
    mremainder.push(solver.state().y[2]);
    mplasmavenous.push(solver.state().y[3]);
    mheart.push(solver.state().y[4]);
    mmuscle.push(solver.state().y[5]);
    madipose.push(solver.state().y[6]);
    mbrain.push(solver.state().y[7]);
    mfeces.push(solver.state().y[8]);
    murine.push(solver.state().y[9]);
    mintestinelumen.push(solver.state().y[10]);
    mplasmaarterial.push(solver.state().y[11]);
    mlung.push(solver.state().y[12]);
    mportalvein.push(solver.state().y[13]);
    mstomach.push(solver.state().y[14]);
    mintestineenterocytes.push(solver.state().y[15]);
    mkidneytissue.push(solver.state().y[16]);
    mintestinevascular.push(solver.state().y[17]);
    mstomachlumen.push(solver.state().y[18]);
    mkidneytubular.push(solver.state().y[19]);
    time.push(0.0);

    let final_time = sim_params.final_time.unwrap_or(24.0);
    solver.set_stop_time(final_time).unwrap();
    loop {
        match solver.step() {
            Ok(OdeSolverStopReason::InternalTimestep) => {
            mliver.push(solver.state().y[0]);
            mkidneyplasma.push(solver.state().y[1]);
            mremainder.push(solver.state().y[2]);
            mplasmavenous.push(solver.state().y[3]);
            mheart.push(solver.state().y[4]);
            mmuscle.push(solver.state().y[5]);
            madipose.push(solver.state().y[6]);
            mbrain.push(solver.state().y[7]);
            mfeces.push(solver.state().y[8]);
            murine.push(solver.state().y[9]);
            mintestinelumen.push(solver.state().y[10]);
            mplasmaarterial.push(solver.state().y[11]);
            mlung.push(solver.state().y[12]);
            mportalvein.push(solver.state().y[13]);
            mstomach.push(solver.state().y[14]);
            mintestineenterocytes.push(solver.state().y[15]);
            mkidneytissue.push(solver.state().y[16]);
            mintestinevascular.push(solver.state().y[17]);
            mstomachlumen.push(solver.state().y[18]);
            mkidneytubular.push(solver.state().y[19]);
                time.push(solver.state().t);
            },
            Ok(OdeSolverStopReason::RootFound(root_idx)) => {
                console_log!("Event triggered at t={}", solver.state().t);
                match root_idx {
                    0 => {
                        // Event: Oral_at_0_001
                        // Parse error for mStomachLumen
                    },
                    _ => console_log!("Unknown event index: {}", root_idx),
                }
            },
            Ok(OdeSolverStopReason::TstopReached) => break,
            Ok(OdeSolverStopReason::RootFound(_)) => break,
            Err(_) => panic!("Solver Error"),
        }
    }

    let mut species_map = HashMap::new();
        species_map.insert("mliver".to_string(), mliver);
        species_map.insert("mkidneyplasma".to_string(), mkidneyplasma);
        species_map.insert("mremainder".to_string(), mremainder);
        species_map.insert("mplasmavenous".to_string(), mplasmavenous);
        species_map.insert("mheart".to_string(), mheart);
        species_map.insert("mmuscle".to_string(), mmuscle);
        species_map.insert("madipose".to_string(), madipose);
        species_map.insert("mbrain".to_string(), mbrain);
        species_map.insert("mfeces".to_string(), mfeces);
        species_map.insert("murine".to_string(), murine);
        species_map.insert("mintestinelumen".to_string(), mintestinelumen);
        species_map.insert("mplasmaarterial".to_string(), mplasmaarterial);
        species_map.insert("mlung".to_string(), mlung);
        species_map.insert("mportalvein".to_string(), mportalvein);
        species_map.insert("mstomach".to_string(), mstomach);
        species_map.insert("mintestineenterocytes".to_string(), mintestineenterocytes);
        species_map.insert("mkidneytissue".to_string(), mkidneytissue);
        species_map.insert("mintestinevascular".to_string(), mintestinevascular);
        species_map.insert("mstomachlumen".to_string(), mstomachlumen);
        species_map.insert("mkidneytubular".to_string(), mkidneytubular);

    let result = SimulationResult {
        time,
        species: species_map,
    };

    serde_json::to_string(&result).unwrap()
}

#[wasm_bindgen]
pub fn get_model_metadata() -> String {
    let metadata = serde_json::json!({
        "model_id": "Zake2021_model",
        "num_species": 20,
        "num_parameters": 19,
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
            "id": "Metformin_Dose_in_Lumen_in_mg",
            "default_value": 0.0,
            "required": true
        },
        {
            "id": "Body_Weight",
            "default_value": 27.5,
            "required": true
        },
        {
            "id": "Metformin_Dose_in_Plasma_in_mg",
            "default_value": 1.375,
            "required": true
        },
        {
            "id": "Cardiac_Output",
            "default_value": 838.8,
            "required": true
        },
        {
            "id": "Ktp_Liver",
            "default_value": 5.5,
            "required": true
        },
        {
            "id": "Ktp_Brain",
            "default_value": 0.8,
            "required": true
        },
        {
            "id": "Ktp_Adipose",
            "default_value": 0.73,
            "required": true
        },
        {
            "id": "Ktp_Heart",
            "default_value": 2.50008880523789,
            "required": true
        },
        {
            "id": "Ktp_Kidney",
            "default_value": 4.5,
            "required": true
        },
        {
            "id": "Ktp_Muscle",
            "default_value": 4.1,
            "required": true
        },
        {
            "id": "Ktp_Remainder",
            "default_value": 0.8,
            "required": true
        },
        {
            "id": "Ktp_Lung",
            "default_value": 3.0,
            "required": true
        },
        {
            "id": "Ktp_Stomach",
            "default_value": 3.20000000001417,
            "required": true
        },
        {
            "id": "Ktp_IntestineVascular",
            "default_value": 4.6,
            "required": true
        },
        {
            "id": "Qgfr",
            "default_value": 20.0,
            "required": true
        },
        {
            "id": "IntestineLumen",
            "default_value": 0.6,
            "required": true
        },
        {
            "id": "Urine",
            "default_value": 1.0,
            "required": true
        },
        {
            "id": "Feces",
            "default_value": 1.0,
            "required": true
        },
        {
            "id": "StomachLumen",
            "default_value": 0.4,
            "required": true
        }
    ]);
    serde_json::to_string(&params).unwrap()
}

#[wasm_bindgen]
pub fn get_species_info() -> String {
    let species = serde_json::json!([
        {
            "id": "mLiver",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mKidneyPlasma",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mRemainder",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mPlasmaVenous",
            "initial_amount": 10645.7107463611,
            "units": "MilliMOL"
        },
        {
            "id": "mHeart",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mMuscle",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mAdipose",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mBrain",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mFeces",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mUrine",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mIntestineLumen",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mPlasmaArterial",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mLung",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mPortalVein",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mStomach",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mIntestineEnterocytes",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mKidneyTissue",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mIntestineVascular",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mStomachLumen",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        },
        {
            "id": "mKidneyTubular",
            "initial_amount": 0.0,
            "units": "MilliMOL"
        }
    ]);
    serde_json::to_string(&species).unwrap()
}

#[wasm_bindgen]
pub fn get_default_parameters() -> String {
    let defaults = serde_json::json!({
        "Metformin_Dose_in_Lumen_in_mg": 0.0,
        "Body_Weight": 27.5,
        "Metformin_Dose_in_Plasma_in_mg": 1.375,
        "Cardiac_Output": 838.8,
        "Ktp_Liver": 5.5,
        "Ktp_Brain": 0.8,
        "Ktp_Adipose": 0.73,
        "Ktp_Heart": 2.50008880523789,
        "Ktp_Kidney": 4.5,
        "Ktp_Muscle": 4.1,
        "Ktp_Remainder": 0.8,
        "Ktp_Lung": 3.0,
        "Ktp_Stomach": 3.20000000001417,
        "Ktp_IntestineVascular": 4.6,
        "Qgfr": 20.0,
        "IntestineLumen": 0.6,
        "Urine": 1.0,
        "Feces": 1.0,
        "StomachLumen": 0.4,
        "final_time": 24.0
    });
    serde_json::to_string(&defaults).unwrap()
}
