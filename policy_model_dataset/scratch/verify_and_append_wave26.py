import json
import os
import sys

# Ensure local code directory is prioritized
sys.path.insert(0, os.path.abspath("code"))
import cleaner
import validator

batch_ids = [129, 130, 131, 132, 133, 134, 135, 136, 137, 138]
combined_path = "combined_dataset.jsonl"
eval_path = "sft_eval.json"

# Load eval set targets for leakage audit
with open(eval_path, "r") as f:
    eval_set = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_set}
eval_refs = {e["refined_text"].strip().lower() for e in eval_set}

all_new_samples = []
tier_totals = {"short": 0, "medium": 0, "long": 0}
noise_layer_totals = []

print("=== Starting Deterministic Verification for Wave 26 (200 High-Density Samples) ===")

for bid in batch_ids:
    batch_file = f"scratch/subagent_batch_{bid}.json"
    if not os.path.exists(batch_file):
        print(f"Error: Missing batch file {batch_file}")
        sys.exit(1)

    with open(batch_file, "r") as f:
        batch = json.load(f)

    if len(batch) != 20:
        print(f"Error: Batch {bid} has {len(batch)} samples instead of 20")
        sys.exit(1)

    # Validate batch distribution and density
    valid_batch, b_msg, stats = validator.validate_batch(
        batch, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    if not valid_batch:
        print(f"Error: Batch {bid} distribution/density failed: {b_msg}")
        sys.exit(1)

    tier_totals["short"] += stats["short"]
    tier_totals["medium"] += stats["medium"]
    tier_totals["long"] += stats["long"]

    # Validate each pair individually
    for idx, sample in enumerate(batch):
        raw = sample["raw_asr"]
        ref = sample["refined_text"]

        # Deterministic validator check with min_noise_layers=4
        is_valid, reason = validator.validate_pair(sample, min_noise_layers=4)
        if not is_valid:
            print(f"Error: Batch {bid} Sample {idx+1} failed validate_pair: {reason}")
            sys.exit(1)

        # Cleaner check
        cleaned, status = cleaner.clean_sample(raw, ref)
        if status != "kept":
            print(f"Error: Batch {bid} Sample {idx+1} failed cleaner: {status}")
            sys.exit(1)

        # Leakage check
        if raw.strip().lower() in eval_raws:
            print(f"Error: Batch {bid} Sample {idx+1} leaked into eval raw ASR!")
            sys.exit(1)
        if ref.strip().lower() in eval_refs:
            print(f"Error: Batch {bid} Sample {idx+1} leaked into eval refined text!")
            sys.exit(1)

        layers = validator.get_noise_layer_count(raw)
        noise_layer_totals.append(layers)

        all_new_samples.append({"raw_asr": raw, "refined_text": ref})

    print(f"Batch {bid} (20 samples): PASSED (Avg layers: {stats.get('avg_noise_layers', 'N/A')})")

avg_layers = sum(noise_layer_totals) / len(noise_layer_totals)
print(f"\nAll 200 samples passed validation perfectly!")
print(f"Tier Breakdown: {tier_totals}")
print(f"Average Noise Layers across Wave 26: {avg_layers:.2f}")

# Count existing lines
with open(combined_path, "r") as f:
    existing_count = sum(1 for line in f if line.strip())

print(f"\nCurrent samples in {combined_path}: {existing_count}")

# Append samples to combined_dataset.jsonl
with open(combined_path, "a") as f:
    for s in all_new_samples:
        f.write(json.dumps(s) + "\n")

# Verify new count
with open(combined_path, "r") as f:
    new_count = sum(1 for line in f if line.strip())

print(f"New samples in {combined_path}: {new_count}")
expected_count = existing_count + len(all_new_samples)
if new_count != expected_count:
    print(f"Error: Expected {expected_count} rows, found {new_count}")
    sys.exit(1)

print(f"Successfully appended {len(all_new_samples)} samples. Target parity: {new_count} / 7500.")
