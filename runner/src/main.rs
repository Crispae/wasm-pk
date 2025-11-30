#![recursion_limit = "256"]
use std::fs;

mod talinolol_model;

fn main() {
    println!("Retrieving default parameters...");
    let default_params = talinolol_model::get_default_parameters();
    println!("Default parameters loaded successfully\n");
    
    // Save default parameters to file for reference
    fs::write("default_params.json", &default_params)
        .expect("Failed to write default_params.json");
    println!("Default parameters saved to default_params.json\n");
    
    // Run simulation with default parameters (no dose - baseline)
    println!("Running baseline simulation (no drug dose)...");
    let result = talinolol_model::run_simulation(&default_params);
    
    // Save baseline result
    fs::write("result_baseline.json", &result)
        .expect("Failed to write result_baseline.json");
    println!("Baseline simulation completed!");
    println!("Result saved to result_baseline.json\n");
    
    // Run simulation with IV dose
    println!("Running simulation with 50mg IV dose...");
    let mut params_with_dose: serde_json::Value = serde_json::from_str(&default_params).unwrap();
    params_with_dose["IVDOSE_tal"] = serde_json::json!(50.0); // 50mg IV dose
    let params_with_dose_str = serde_json::to_string(&params_with_dose).unwrap();
    let result_with_dose = talinolol_model::run_simulation(&params_with_dose_str);
    
    // Save result with dose
    fs::write("result_with_dose.json", &result_with_dose)
        .expect("Failed to write result_with_dose.json");
    println!("Simulation with dose completed!");
    println!("Result saved to result_with_dose.json\n");
    
    // Get model metadata
    let metadata = talinolol_model::get_model_metadata();
    println!("Model metadata: {}", metadata);
    
    println!("\nAll done! Check the output files:");
    println!("  - default_params.json: Model parameters");
    println!("  - result_baseline.json: Baseline simulation (no dose)");
    println!("  - result_with_dose.json: Simulation with 50mg IV dose");
}