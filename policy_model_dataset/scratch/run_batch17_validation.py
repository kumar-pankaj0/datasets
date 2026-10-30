import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def main():
    json_path = "scratch/subagent_batch_17.json"
    with open(json_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    print(f"Auditing {len(batch)} samples from {json_path}...\n")
    all_ok = True
    for i, s in enumerate(batch, 1):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])

        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)

        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"Sample {i:02d}: [{status}] ({words}w ref, {raw_words}w raw, ratio {ratio:.2f})")
        if not v_ok:
            print(f"  Validator failure: {v_reason}")
        if c_res is None:
            print(f"  Cleaner failure: {c_reason}")

    b_ok, b_reason, b_counts = validate_batch(batch, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Tier counts: {b_counts}")
    print(f"Overall status: {'ALL PASS (10/10)' if all_ok and b_ok else 'AUDIT FAILED'}")

if __name__ == "__main__":
    main()
