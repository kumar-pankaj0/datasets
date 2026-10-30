import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def main():
    json_path = "scratch/subagent_batch_27.json"
    with open(json_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    print(f"Auditing {len(batch)} samples from {json_path}...\n")
    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for i, s in enumerate(batch, 1):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])

        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier = "Short"
            tier_counts["short"] += 1
        elif words <= 90:
            tier = "Medium"
            tier_counts["medium"] += 1
        else:
            tier = "Long"
            tier_counts["long"] += 1

        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"Sample {i:02d}: [{status}] Tier={tier:6s} ({words:3d}w ref, {raw_words:3d}w raw, ratio {ratio:.2f})")
        if not v_ok:
            print(f"  Validator failure: {v_reason}")
        if c_res is None:
            print(f"  Cleaner failure: {c_reason}")

    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"\nBatch Tier Validation: {b_ok} ({b_reason}) -> {b_tiers}")

    if all_ok and b_ok:
        print("\nALL 20 SAMPLES PASSED 100% VALIDATION!")
    else:
        print("\nVALIDATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
