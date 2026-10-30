import sys
import json
import re
from pathlib import Path

sys.path.append("code")
import validator
import cleaner

def test_pair(raw, ref, tier_expected):
    pair = {"raw_asr": raw, "refined_text": ref}
    v_ok, v_msg = validator.validate_pair(pair)
    c_res, c_msg = cleaner.clean_sample(raw, ref)
    words = len(ref.split())
    raw_words = len(raw.split())
    ratio = words / max(1, raw_words)
    
    tier = "short" if words < 25 else ("medium" if words < 90 else "long")
    status = "PASS" if (v_ok and c_res and tier == tier_expected) else "FAIL"
    
    print(f"[{status}] Tier: {tier} (words: {words}, raw: {raw_words}, ratio: {ratio:.2f})")
    if not v_ok:
        print(f"  Validator ERROR: {v_msg}")
    if not c_res:
        print(f"  Cleaner ERROR: {c_msg}")
    return status == "PASS"

print("Validator & Cleaner harness loaded.")
