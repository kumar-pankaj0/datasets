import json
import re
import sys
import os

sys.path.append("code")
import validator
import cleaner

def test_single_sample(idx, s):
    raw = s.get("raw_asr", "")
    ref = s.get("refined_text", "")
    
    # 1. Cleaner
    res, status = cleaner.clean_sample(raw, ref)
    if not res:
        print(f"Sample {idx} FAILED cleaner: {status}")
        return False
        
    # 2. Pair validator
    words = len(ref.split())
    # min_layers: 3 for short (<25), 4 for medium/long
    min_layers = 4
    ok, reason = validator.validate_pair(s, min_noise_layers=min_layers)
    if not ok:
        print(f"Sample {idx} FAILED validator: {reason}")
        return False
        
    layers = validator.count_active_noise_layers(raw)
    count = sum(layers.values())
    active_names = [k for k, v in layers.items() if v]
    print(f"Sample {idx}: {words} words, {count} layers ({', '.join(active_names)}) - PASSED")
    return True

print("Test harness loaded.")
