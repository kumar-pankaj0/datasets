import json
import random
import collections

# Load the original 2,917 samples
with open("dataset.json", "r") as f:
    original_data = json.load(f)

# Load the curated hard-negatives
with open("second_face_dataset.json", "r") as f:
    new_data = json.load(f)

# Step 1: Count what already exists in the hard-negatives
metrics = ["faithfulness", "noise_removed", "errors_fixed", "formatting"]
existing_counts = {m: collections.Counter() for m in metrics}

for sample in new_data:
    for m in metrics:
        existing_counts[m][sample["output"][m]] += 1

print("=== Existing counts in second_face_dataset.json ===")
for m in metrics:
    print(f"  {m}: {dict(sorted(existing_counts[m].items()))}")

# Step 2: Calculate target and deficit
# We want the final incremental_replay_dataset to have roughly equal distribution
# Target: ~200 samples per bucket across all metrics (for a ~1000 sample dataset)
TARGET_PER_BUCKET = 200
scores = [1, 3, 5, 7, 9]

# Calculate how many we need from the original dataset per metric per bucket
deficit = {m: {} for m in metrics}
for m in metrics:
    for s in scores:
        gap = TARGET_PER_BUCKET - existing_counts[m].get(s, 0)
        deficit[m][s] = max(0, gap)

print("\n=== Deficit (how many we need from original data) ===")
for m in metrics:
    print(f"  {m}: {deficit[m]}")

# Step 3: Deficit-based stratified sampling
# We use a greedy multi-label approach (like the user's original logic)
# but now the bucket caps are set by the deficit, not a flat number
random.seed(42)
random.shuffle(original_data)

# Track how many we've pulled per metric per score
pulled_counts = {m: {s: 0 for s in scores} for m in metrics}
replay_memory = []
used_indices = set()

for idx, sample in enumerate(original_data):
    if idx in used_indices:
        continue

    # Check if this sample helps fill any deficit
    needed = False
    for m in metrics:
        s = sample["output"][m]
        if pulled_counts[m][s] < deficit[m].get(s, 0):
            needed = True
            break

    if needed:
        replay_memory.append(sample)
        used_indices.add(idx)
        for m in metrics:
            s = sample["output"][m]
            pulled_counts[m][s] += 1

print(f"\n=== Pulled {len(replay_memory)} samples from original data ===")
print("Pulled distribution:")
for m in metrics:
    print(f"  {m}: {dict(sorted(pulled_counts[m].items()))}")

# Step 4: Combine and shuffle
incremental_dataset = new_data + replay_memory
random.shuffle(incremental_dataset)

# Step 5: Verify final distribution
final_counts = {m: collections.Counter() for m in metrics}
for sample in incremental_dataset:
    for m in metrics:
        final_counts[m][sample["output"][m]] += 1

print(f"\n=== FINAL incremental_replay_dataset.json ({len(incremental_dataset)} samples) ===")
total = len(incremental_dataset)
print(f"{'Metric':<16} | {'1':<12} | {'3':<12} | {'5':<12} | {'7':<12} | {'9':<12}")
print("-" * 82)
for m in metrics:
    row = [f"{final_counts[m][s]} ({final_counts[m][s]/total*100:4.1f}%)" for s in scores]
    print(f"{m:<16} | " + " | ".join(row))

# Save
with open("incremental_replay_dataset.json", "w") as f:
    json.dump(incremental_dataset, f, indent=2)

print(f"\nSaved incremental_replay_dataset.json with {len(incremental_dataset)} samples.")
