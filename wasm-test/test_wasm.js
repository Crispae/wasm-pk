import init, { run_simulation } from 'sbml_wasm_project';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testWASM() {
    console.log("🧪 Starting WASM Test Suite...\n");

    try {
        // Initialize the WASM module with file path
        console.log("📦 Loading WASM module...");
        const wasmPath = join(__dirname, 'node_modules', 'sbml_wasm_project', 'sbml_model_bg.wasm');
        const wasmBuffer = readFileSync(wasmPath);
        await init({ module_or_path: wasmBuffer });
        console.log("✅ WASM module loaded successfully\n");

        // Test 1: Single dose simulation
        console.log("Test 1: Single dose simulation");
        console.log("─".repeat(50));
        
        const testParams1 = {
            // Actual euromix model parameters
            BM: 70.0,
            BSA: 190.0,
            scVFat: 0.209,
            scVRich: 0.105,
            scVLiver: 0.024,
            scVBlood: 0.068,
            scVArt: 0.333333333333333,
            scFBlood: 4.8,
            scFFat: 0.085,
            scFPoor: 0.12,
            scFLiver: 0.27,
            scFSkin: 0.05,
            fSA_exposed: 0.1,
            Height_sc: 0.0001,
            Height_vs: 0.0122,
            Falv: 2220.0,
            PCFat: 2.53,
            PCLiver: 0.923,
            PCRich: 0.875,
            PCPoor: 0.647,
            PCSkin_sc: 0.889,
            PCSkin: 0.889,
            PCAir: 1e+99,
            kGut: 1.0,
            Kp_sc_vs: 0.01,
            Km: 0.0,
            Michaelis: 0.0,
            Vmax: 0.0,
            CLH: 132.0,
            Ke: 7.5,
            fub: 0.51,
            f_su: 1.71,
            f_se: 0.19,
            VBlood: 4.76,
            FBlood: 336.0,
            FFat: 28.56,
            FPoor: 40.32,
            FLiver: 90.72,
            FSkin: 16.8,
            FRich: 159.6,
            FSkin_e: 1.68,
            FSkin_u: 15.12,
            // Compartments
            Air: 1.0,
            Urine: 1.0,
            Fat: 14.63,
            Rich: 7.35,
            Liver: 1.68,
            Art: 1.58666666666667,
            Ven: 3.17333333333333,
            Skin_e: 0.2318,
            Skin_u: 2.0862,
            Skin_sc_e: 0.0019,
            Skin_sc_u: 0.0171,
            Poor: 32.243,
            Gut: 1.0,
            doses: [[0.0, 100.0]],  // Single dose of 100 at time 0
            final_time: 24.0
        };

        let result1, output1;
        try {
            result1 = run_simulation(JSON.stringify(testParams1));
            output1 = JSON.parse(result1);
        } catch (e) {
            console.error("Error running first simulation:");
            console.error(e);
            console.error("Parameters:", JSON.stringify(testParams1, null, 2));
            throw e;
        }

        console.log(`✅ Simulation completed`);
        console.log(`   Time points: ${output1.time ? output1.time.length : 0}`);
        console.log(`   Species tracked: ${output1.species ? Object.keys(output1.species).length : 0}`);
        if (output1.species && Object.keys(output1.species).length > 0) {
            console.log(`   Species names: ${Object.keys(output1.species).join(', ')}`);
        }
        if (output1.time && output1.time.length > 0) {
            console.log(`  Time range: ${output1.time[0].toFixed(2)} - ${output1.time[output1.time.length-1].toFixed(2)} hours\n`);
        } else {
            console.log("   ⚠️  No time data returned\n");
        }

        // Test 2: Multiple dose simulation
        console.log("Test 2: Multiple dose simulation");
        console.log("─".repeat(50));
        
        const testParams2 = {
            ...testParams1,
            doses: [
                [0.0, 100.0],
                [8.0, 50.0],
                [16.0, 50.0]
            ],
            final_time: 48.0
        };

        const result2 = run_simulation(JSON.stringify(testParams2));
        const output2 = JSON.parse(result2);

        console.log(`✅ Simulation completed`);
        console.log(`   Time points: ${output2.time.length}`);
        console.log(`   Time range: ${output2.time[0].toFixed(2)} - ${output2.time[output2.time.length-1].toFixed(2)} hours\n`);

        // Validation checks
        console.log("Validation Checks");
        console.log("─".repeat(50));
        
        let allPassed = true;

        // Check 1: Output has time data
        if (output1.time.length > 0) {
            console.log("✅ Time series data present");
        } else {
            console.log("❌ No time series data");
            allPassed = false;
        }

        // Check 2: Output has species data
        const speciesCount = Object.keys(output1.species).length;
        if (speciesCount > 0) {
            console.log(`✅ Species data present (${speciesCount} species)`);
        } else {
            console.log("❌ No species data");
            allPassed = false;
        }

        // Check 3: All species have same length as time
        let lengthMatch = true;
        for (const [species, values] of Object.entries(output1.species)) {
            if (values.length !== output1.time.length) {
                console.log(`❌ Length mismatch for ${species}: ${values.length} vs ${output1.time.length}`);
                lengthMatch = false;
                allPassed = false;
            }
        }
        if (lengthMatch) {
            console.log("✅ All species data lengths match time series");
        }

        // Check 4: Time is monotonically increasing
        let timeIncreasing = true;
        for (let i = 1; i < output1.time.length; i++) {
            if (output1.time[i] <= output1.time[i-1]) {
                timeIncreasing = false;
                allPassed = false;
                break;
            }
        }
        if (timeIncreasing) {
            console.log("✅ Time series is monotonically increasing");
        } else {
            console.log("❌ Time series is not monotonically increasing");
        }

        // Check 5: Multiple dose test has more time points
        if (output2.time.length > output1.time.length) {
            console.log("✅ Multiple dose simulation has extended timeline");
        } else {
            console.log("❌ Multiple dose simulation timeline issue");
            allPassed = false;
        }

        console.log("\n" + "═".repeat(50));
        if (allPassed) {
            console.log("🎉 All tests PASSED!");
        } else {
            console.log("⚠️  Some tests FAILED");
            process.exit(1);
        }
        console.log("═".repeat(50) + "\n");

    } catch (error) {
        console.error("❌ Test failed with error:");
        console.error(error);
        process.exit(1);
    }
}

testWASM();
