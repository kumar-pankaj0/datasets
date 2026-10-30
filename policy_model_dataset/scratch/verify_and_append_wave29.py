import json
import os
import sys

sys.path.insert(0, os.path.abspath("code"))
import cleaner
import validator

BATCH_FILES = [
    "scratch/subagent_batch_159.json",
    "scratch/subagent_batch_160.json",
    "scratch/subagent_batch_161.json",
    "scratch/subagent_batch_162.json",
    "scratch/subagent_batch_163.json",
    "scratch/subagent_batch_164.json",
    "scratch/subagent_batch_165.json",
    "scratch/subagent_batch_166.json",
    "scratch/subagent_batch_167.json",
    "scratch/subagent_batch_168.json",
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

    print("=== Validating Wave 29 Batches ===")
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

    avg_wave_layers = total_layers / len(all_wave_samples)
    print(f"\nWave 29 Summary: {len(all_wave_samples)} samples verified.")
    print(f"Short: {total_short} ({total_short/len(all_wave_samples):.1%})")
    print(f"Medium: {total_medium} ({total_medium/len(all_wave_samples):.1%})")
    print(f"Long: {total_long} ({total_long/len(all_wave_samples):.1%})")
    print(f"Average Noise Layers: {avg_wave_layers:.2f} (Required >= 4.0)")

    # Read existing combined_dataset.jsonl
    with open(DATASET_PATH, "r") as f:
        existing_lines = [line.strip() for line in f if line.strip()]
    initial_count = len(existing_lines)
    print(f"\nInitial corpus rows: {initial_count}")

    # Append to combined_dataset.jsonl
    with open(DATASET_PATH, "a") as f:
        for s in all_wave_samples:
            f.write(json.dumps(s) + "\n")
            
    # Verify new count
    with open(DATASET_PATH, "r") as f:
        new_lines = [line.strip() for line in f if line.strip()]
    final_count = len(new_lines)
    print(f"New corpus rows: {final_count} (+{final_count - initial_count})")
    
    if final_count != initial_count + 200:
        print(f"ERROR: Expected {initial_count + 200} rows, got {final_count}")
        sys.exit(1)
        
    print("SUCCESS: Wave 29 appended cleanly!")

if __name__ == "__main__":
    main()
