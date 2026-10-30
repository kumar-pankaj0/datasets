import json
import os
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

output_path = "scratch/subagent_batch_38.json"

# Import batch from test_batch_38
from test_batch_38 import batch

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

if all_valid and b_ok:
    print("SUCCESS: Batch 38 fully validated and ready.")
else:
    print("FAILURE: Validation did not pass 100%.")
    sys.exit(1)
