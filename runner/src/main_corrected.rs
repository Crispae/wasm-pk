mod pbpk_bpa_model;  // This will use your generated model

use std::fs;

fn main() {
    // Create JSON parameters matching SimulationParams struct
    // NOTE: koa, t1, and uptake_O are now CALCULATED from initial assignments
    // So we do NOT pass them in the JSON anymore!
    let params_json = r#"
    {
        "Kabs": 0.4,
        "t0": 0.0,
        "Kelm": 0.13,
        "EoA_O": 1.0,
        "D_o": 1.3381102,
        "vplasma": 3.6,
        "period_O": 0.0003,
        "n_O": 1.0,
        "comp1": 3.6,
        "final_time": 36.0
    }
    "#;

    println!("Running PBPK_BPA simulation with corrected SBML...");
    println!("Expected calculations:");
    println!("  koa = 1.2e8 * 1.0 * 1.3381102 = {}", 1.2e8 * 1.0 * 1.3381102);
    println!("  t1 = 0.0 + 0.0003 = {}", 0.0 + 0.0003);
    println!("  uptake_O = 1.0 * 1.3381102 / 1.0 = {}", 1.0 * 1.3381102 / 1.0);
    println!();

    let result = pbpk_bpa_model::run_simulation(params_json);

    // Save JSON result
    std::fs::write("result_corrected.json", &result)
        .expect("Failed to write result_corrected.json");

    println!("Simulation completed!");
    println!("Result saved to result_corrected.json");

    // Parse and show first few data points
    let result_data: serde_json::Value = serde_json::from_str(&result).unwrap();
    if let Some(aplasma) = result_data["species"]["aplasma"].as_array() {
        println!("\nFirst 5 Aplasma concentrations:");
        for (i, val) in aplasma.iter().take(5).enumerate() {
            println!("  [{}] {}", i, val);
        }
        println!("  ...");
        println!("  Peak should be around 0.3-0.4 (not 1e-12!)");
    }
}
