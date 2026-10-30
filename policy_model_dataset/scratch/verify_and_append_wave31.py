import json
import os
import sys

sys.path.insert(0, os.path.abspath("code"))
import cleaner
import validator

BATCH_FILES = [
    "scratch/subagent_batch_179.json",
    "scratch/subagent_batch_180.json",
    "scratch/subagent_batch_181.json",
    "scratch/subagent_batch_182.json",
    "scratch/subagent_batch_183.json",
    "scratch/subagent_batch_184.json",
    "scratch/subagent_batch_185.json",
    "scratch/subagent_batch_186.json",
    "scratch/subagent_batch_187.json",
    "scratch/subagent_batch_188.json",
]

EVAL_PATH = "sft_eval.json"
DATASET_PATH = "combined_dataset.jsonl"

def load_eval_targets():
    with open(EVAL_PATH, "r") as f:
        data = json.load(f)
    return {item["refined_text"].strip().lower() for item in data}

def main():
    eval_targets = load_eval_targets()
    all_wave_samples = []
    
    total_short = 0
    total_medium = 0
    total_long = 0
    total_layers = 0

    print("=== Validating Wave 31 Batches ===")
    for b_file in BATCH_FILES:
        if not os.path.exists(b_file):
            print(f"ERROR: Missing file {b_file}")
            sys.exit(1)
            
        with open(b_file, "r") as f:
            samples = json.load(f)
            
        if len(samples) != 20:
            print(f"ERROR: {b_file} has {len(samples)} samples, expected 20")
            sys.exit(1)
            
        batch_layers = 0
        b_short = 0
        b_medium = 0
        b_long = 0
        
        for idx, sample in enumerate(samples):
            raw = sample.get("raw_asr", "")
            refined = sample.get("refined_text", "")
            
            # Check keys
            if not raw or not refined:
                print(f"ERROR in {b_file} sample {idx}: missing raw_asr or refined_text")
                sys.exit(1)
                
            # Eval leakage check
            if refined.strip().lower() in eval_targets:
                print(f"ERROR: Leakage in {b_file} sample {idx}: '{refined}' matches sft_eval.json")
                sys.exit(1)
                
            # Word count & tier
            w_count = len(refined.split())
            if w_count < 25:
                b_short += 1
                min_layers = 3
            elif w_count < 90:
                b_medium += 1
                min_layers = 4
            else:
                b_long += 1
                min_layers = 4
                
            # Pair validation
            ok, err = validator.validate_pair(sample, min_noise_layers=min_layers)
            if not ok:
                print(f"ERROR in {b_file} sample {idx} (validator): {err}")
                sys.exit(1)
                
            # Cleaner verification
            cleaned_text, status = cleaner.clean_sample(raw, refined)
            if status != "kept":
                print(f"ERROR in {b_file} sample {idx} (cleaner): status={status}")
                sys.exit(1)
                
            layers = validator.get_noise_layer_count(raw)
            batch_layers += layers
            
        avg_batch_layers = batch_layers / len(samples)
        print(f"{b_file}: 20 samples valid | Short: {b_short}, Med: {b_medium}, Long: {b_long} | Avg Noise Layers: {avg_batch_layers:.2f}")
        
        total_short += b_short
        total_medium += b_medium
        total_long += b_long
        total_layers += batch_layers
        all_wave_samples.extend(samples)

    total_samples = len(all_wave_samples)
    overall_avg_layers = total_layers / total_samples
    print(f"\n--- Wave 31 Summary ---")
    print(f"Total Validated: {total_samples}")
    print(f"Tiers: Short={total_short} ({total_short/total_samples*100:.1f}%), Med={total_medium} ({total_medium/total_samples*100:.1f}%), Long={total_long} ({total_long/total_samples*100:.1f}%)")
    print(f"Overall Avg Noise Layers: {overall_avg_layers:.2f}")
    
    if total_samples != 200:
        print(f"ERROR: Wave 31 count {total_samples} != 200")
        sys.exit(1)
        
    # Read existing combined_dataset.jsonl
    with open(DATASET_PATH, "r") as f:
        existing_lines = [line.strip() for line in f if line.strip()]
        
    print(f"Current {DATASET_PATH} row count: {len(existing_lines)}")
    
    # Append wave samples
    with open(DATASET_PATH, "a") as f:
        for s in all_wave_samples:
            f.write(json.dumps(s) + "\n")
            
    # Verify new row count
    with open(DATASET_PATH, "r") as f:
        updated_lines = [line.strip() for line in f if line.strip()]
        
    print(f"Updated {DATASET_PATH} row count: {len(updated_lines)}")
    if len(updated_lines) != len(existing_lines) + 200:
        print("ERROR: Row count mismatch after append!")
        sys.exit(1)
        
    print(f"SUCCESS: Wave 31 appended. Target progress: {len(updated_lines)} / 7500 clean samples.")

if __name__ == "__main__":
    main()
