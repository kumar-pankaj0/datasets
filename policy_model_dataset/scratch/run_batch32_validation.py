import json
import sys
sys.path.insert(0, "code")
sys.path.insert(0, "scratch")
from test_batch_32 import samples
from validator import validate_pair, validate_batch
from cleaner import clean_sample

output_path = "scratch/subagent_batch_32.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Saved {len(samples)} samples to {output_path}")

# Run independent audit
all_ok = True
tier_counts = {"short": 0, "medium": 0, "long": 0}
for i, s in enumerate(samples, 1):
    v_ok, v_reason = validate_pair(s)
    c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
    w_count = len(s["refined_text"].split())
    
    if w_count < 25:
        tier_counts["short"] += 1
    elif w_count < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1
        
    if not v_ok or c_res is None:
        all_ok = False
        print(f"FAILED Sample {i}: val={v_reason}, clean={c_reason}")

b_ok, b_msg, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"Audit Result: all_ok={all_ok and b_ok}, tier_counts={tier_counts}, b_msg={b_msg}")
