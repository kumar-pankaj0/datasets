import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path.cwd()))

from code.validator import validate_pair, validate_batch
from code.cleaner import clean_sample

from scratch.test_batch_71 import samples

out_file = Path("scratch/subagent_batch_71.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Written {len(samples)} samples to {out_file}")

# Verify directly from written file
with open(out_file, "r", encoding="utf-8") as f:
    loaded_samples = json.load(f)

assert len(loaded_samples) == 20, f"Expected 20 samples, got {len(loaded_samples)}"

tier_counts = {"short": 0, "medium": 0, "long": 0}
for i, s in enumerate(loaded_samples):
    v_ok, v_msg = validate_pair(s)
    assert v_ok, f"Sample {i+1} failed validate_pair: {v_msg}"
    
    c_res, c_msg = clean_sample(s["raw_asr"], s["refined_text"])
    assert c_msg == "kept", f"Sample {i+1} failed clean_sample: {c_msg}"
    assert c_res is not None
    
    words = len(s["refined_text"].split())
    if words < 25:
        tier_counts["short"] += 1
    elif words < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1

b_ok, b_msg, counts = validate_batch(loaded_samples, min_short=4, min_medium=6, min_long=10)
assert b_ok, f"Batch validation failed: {b_msg}"
assert tier_counts == {"short": 4, "medium": 6, "long": 10}, f"Unexpected tier counts: {tier_counts}"

print("All 20 samples successfully verified on disk!")
print(f"Final tier counts: {tier_counts}")
