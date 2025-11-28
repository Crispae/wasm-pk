mod pbpk_bpa_model;  // This will use your generated model

use std::fs;

fn main() {
    // Create JSON parameters matching SimulationParams struct for euromix model
    let params_json = r#"
    {
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
        "PCAir": 1e99,
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
    }
    "#;

    //println!("Running euromix simulation...");
    //let result = pbpk_bpa_model::run_simulation(params_json);
    
     // Save JSON result
     //std::fs::write("result.json", &result)
     //.expect("Failed to write result.json");

     let params = pbpk_bpa_model::get_default_parameters();
     println!("Default parameters: {}", params);
 
    println!("Simulation completed!");
    println!("Result saved to result.json");
}