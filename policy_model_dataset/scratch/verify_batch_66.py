import json
import sys
import re
from pathlib import Path

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample, normalize_raw

from test_batch_66_builder import batch

print("Running deep verification of Batch 66...")

# 1. Eval leakage check
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

# 2. Check each sample
tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, p in enumerate(batch):
    raw = p["raw_asr"]
    ref = p["refined_text"]
    
    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into eval!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into eval!"

    # Validator check
    v_ok, v_msg = validate_pair(p)
    assert v_ok, f"Sample {idx+1} failed validate_pair: {v_msg}"

    # Cleaner check
    c_res, c_msg = clean_sample(raw, ref)
    assert c_res is not None, f"Sample {idx+1} failed cleaner: {c_msg}"
    assert c_msg == "kept", f"Sample {idx+1} cleaner status: {c_msg}"

    raw_words = len(raw.split())
    ref_words = len(ref.split())
    ratio = ref_words / max(1, raw_words)

    # Sentence count
    # Split on sentence terminals . ! ?
    sentences = [s.strip() for s in re.split(r'[.!?]+', ref) if s.strip()]

    if ref_words < 25:
        tier = "short"
        tier_counts["short"] += 1
        assert len(sentences) == 1, f"Sample {idx+1} (short) must have exactly 1 sentence, got {len(sentences)}"
        assert "\n" not in ref, f"Sample {idx+1} (short) has newline"
    elif ref_words < 90:
        tier = "medium"
        tier_counts["medium"] += 1
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} (medium) must have 1-3 sentences, got {len(sentences)}"
        assert "\n\n" in ref, f"Sample {idx+1} (medium) should have paragraph break"
    else:
        tier = "long"
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} (long) must have paragraph break"

    print(f"Sample {idx+1:02d} [{tier.upper()}]: raw_w={raw_words}, ref_w={ref_words}, ratio={ratio:.2f}, sentences={len(sentences)}, breaks={ref.count(chr(10)*2)}")

assert tier_counts["short"] == 4, f"Expected 4 short, got {tier_counts['short']}"
assert tier_counts["medium"] == 6, f"Expected 6 medium, got {tier_counts['medium']}"
assert tier_counts["long"] == 10, f"Expected 10 long, got {tier_counts['long']}"

# Batch diversity check
b_ok, b_msg, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
assert b_ok, f"Batch validation failed: {b_msg}"

# Save to scratch/subagent_batch_66.json
out_file = Path("scratch/subagent_batch_66.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"\nAll 20 samples verified and saved successfully to {out_file}!")
