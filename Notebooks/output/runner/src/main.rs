mod euromix_model;

use std::fs;

fn main() {
    let params_path = "../../../test/sample_params.json";
    let params = match fs::read_to_string(params_path) {
        Ok(content) => {
            println!("Successfully read params file: {}", params_path);
            println!("File size: {} bytes", content.len());

            // Strip BOM if present (UTF-8 BOM is EF BB BF, appears as '\u{FEFF}')
            let cleaned = content.trim_start_matches('\u{FEFF}').trim();

            println!("First 100 chars: {}", &cleaned.chars().take(100).collect::<String>());
            cleaned.to_string()
        },
        Err(e) => {
            eprintln!("Failed to read params file '{}': {}", params_path, e);
            std::process::exit(1);
        }
    };
    
    println!("Running simulation with params from: {}", params_path);
    let result = euromix_model::run_simulation(&params);
    println!("Simulation Result: {}", result);
}