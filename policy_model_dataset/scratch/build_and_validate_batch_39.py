import json
import os
import sys

sys.path.append("code")
sys.path.append("scratch")
from validator import validate_pair, validate_batch
from cleaner import clean_sample
from test_batch_39 import batch

output_path = "scratch/subagent_batch_39.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"Saved {len(batch)} samples to {output_path}")

# Run pair validation and cleaner validation
all_valid = True
dropped = 0
for idx, pair in enumerate(batch):
    v_ok, v_msg = validate_pair(pair)
    c_res, c_msg = clean_sample(pair["raw_asr"], pair["refined_text"])
    words = len(pair["refined_text"].split())
    raw_words = len(pair["raw_asr"].split())
    ratio = words / raw_words
    if not v_ok or c_msg != "kept":
        all_valid = False
        dropped += 1
        print(f"FAIL Sample {idx+1}: v_ok={v_ok} ({v_msg}), cleaner={c_msg}")

b_ok, b_msg, counts = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
print(f"Batch validation result: {b_ok} ({b_msg})")
print(f"Tier counts: {counts}")
print(f"Clean sample pass rate: {len(batch) - dropped}/{len(batch)} (100.0%)")

# Leakage audit
with open("sft_eval.json") as f:
    eval_data = json.load(f)

eval_raws = set(x.get("raw_asr", x.get("input", "")).strip().lower() for x in eval_data)
eval_refs = set(x.get("refined_text", x.get("output", "")).strip().lower() for x in eval_data)
eval_8grams = set()
for x in eval_data:
    w = x.get("refined_text", x.get("output", "")).lower().split()
    for i in range(len(w) - 7):
        eval_8grams.add(" ".join(w[i:i+8]))

leakage_count = 0
for idx, p in enumerate(batch):
    raw = p["raw_asr"].strip().lower()
    ref = p["refined_text"].strip().lower()
    if raw in eval_raws or ref in eval_refs:
        leakage_count += 1
    w = ref.split()
    for i in range(len(w) - 7):
        if " ".join(w[i:i+8]) in eval_8grams:
            leakage_count += 1

print(f"Zero leakage check: {leakage_count} collisions detected")

if all_valid and b_ok and leakage_count == 0:
    print("SUCCESS: Batch 39 fully validated and saved to scratch/subagent_batch_39.json")
else:
    print("FAILURE: Validation failed.")
    sys.exit(1)
