import json
import sys
from pathlib import Path

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def main():
    json_path = "scratch/subagent_batch_43.json"
    with open(json_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    print(f"Auditing {len(batch)} samples from {json_path}...\n")

    # Load eval set for leakage check
    eval_file = Path("sft_eval.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}

    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for i, s in enumerate(batch, 1):
        raw = s.get("raw_asr", "")
        ref = s.get("refined_text", "")

        # Check leakage
        if raw.strip().lower() in eval_raws:
            print(f"Sample {i:02d}: LEAKAGE detected against sft_eval (raw_asr)!")
            all_ok = False
        if ref.strip() in eval_refs:
            print(f"Sample {i:02d}: LEAKAGE detected against sft_eval (refined_text)!")
            all_ok = False

        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(raw, ref)

        words = len(ref.split())
        raw_words = len(raw.split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
        elif words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
        else:
            tier = "LONG"
            tier_counts["long"] += 1

        if not (v_ok and c_res is not None):
            all_ok = False
            print(f"Sample {i:02d} [{tier:6s}]: FAIL - validator: {v_reason}, cleaner: {c_reason}")
        else:
            print(f"Sample {i:02d} [{tier:6s}]: PASS - words={words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

    print("\n--- Tier Counts ---")
    print(f"Short:  {tier_counts['short']} / 4")
    print(f"Medium: {tier_counts['medium']} / 6")
    print(f"Long:   {tier_counts['long']} / 10")

    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"\nvalidate_batch: {b_reason} (passed={b_ok}, returned_tiers={b_tiers})")

    if all_ok and b_ok:
        print("\nAll 20 samples in Batch 43 passed all validation checks cleanly.")
    else:
        print("\nBatch 43 failed validation checks.")
        sys.exit(1)

if __name__ == "__main__":
    main()
