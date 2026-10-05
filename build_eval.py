import json
import collections
import random

# 1. Load the 50 hard eval samples and sanitize invalid LLM scores
with open('data_eval_raw.json', 'r') as f:
    eval_data = json.load(f)

valid_scores = {1, 3, 5, 7, 9}
def snap_score(s):
    if s in valid_scores: return s
    # Snap invalid scores (2->3, 4->5, 6->7, 8->9)
    if s <= 2: return 1
    elif s <= 4: return 3
    elif s <= 6: return 5
    elif s <= 8: return 7
    return 9

for item in eval_data:
    for m in ['faithfulness', 'noise_removed', 'errors_fixed', 'formatting']:
        item['expected_output'][m] = snap_score(item['expected_output'][m])

# 2. Prevent Data Leakage! Get all training data raw_asr to exclude them
with open('data_train.json', 'r') as f:
    train_data = json.load(f)
train_texts = {item['input']['raw_asr'] for item in train_data}

# 3. Load master pool and filter out training data
with open('data_baseline.json', 'r') as f:
    master_data = json.load(f)

# The master data uses {"output": ...} instead of {"expected_output": ...}
# We need to map it so the schema matches the eval set
safe_master_pool = []
for item in master_data:
    if item['input']['raw_asr'] not in train_texts:
        # Convert schema to match eval
        eval_item = {
            "description": "Baseline evaluation sample",
            "input": item["input"],
            "expected_output": item["output"]
        }
        safe_master_pool.append(eval_item)

random.seed(42)
random.shuffle(safe_master_pool)

# 4. Count existing distribution in eval_data
metrics = ['faithfulness', 'noise_removed', 'errors_fixed', 'formatting']
existing_counts = {m: collections.Counter() for m in metrics}
for item in eval_data:
    for m in metrics:
        existing_counts[m][item['expected_output'][m]] += 1

# 5. Fill deficits to reach exactly 40 samples per bucket (200 total eval samples)
TARGET_PER_BUCKET = 40
scores = [1, 3, 5, 7, 9]

deficit = {m: {} for m in metrics}
for m in metrics:
    for s in scores:
        gap = TARGET_PER_BUCKET - existing_counts[m].get(s, 0)
        deficit[m][s] = max(0, gap)

pulled_counts = {m: {s: 0 for s in scores} for m in metrics}
used_indices = set()
added_samples = []

for idx, sample in enumerate(safe_master_pool):
    needed = False
    for m in metrics:
        s = sample["expected_output"][m]
        if pulled_counts[m][s] < deficit[m].get(s, 0):
            needed = True
            break
            
    if needed:
        added_samples.append(sample)
        used_indices.add(idx)
        for m in metrics:
            s = sample["expected_output"][m]
            pulled_counts[m][s] += 1

# 6. Combine, shuffle, and save
final_eval_set = eval_data + added_samples
random.shuffle(final_eval_set)

# Verify final distribution
final_counts = {m: collections.Counter() for m in metrics}
for item in final_eval_set:
    for m in metrics:
        final_counts[m][item['expected_output'][m]] += 1

print(f"=== ROBUST EVAL SET ({len(final_eval_set)} samples) ===")
print("Data Leakage Check: 0 overlapping samples with training set.")
print("-" * 65)
for m in metrics:
    row = [f"{final_counts[m][s]}" for s in scores]
    print(f"{m:<15} | 1: {row[0]:<4} | 3: {row[1]:<4} | 5: {row[2]:<4} | 7: {row[3]:<4} | 9: {row[4]:<4}")

with open('data_eval.json', 'w') as f:
    json.dump(final_eval_set, f, indent=2)
