import json
import re
import sys
import os

sys.path.insert(0, os.path.abspath("code"))
import validator
import cleaner

with open("sft_eval.json", "r") as f:
    eval_data = json.load(f)
eval_targets = {item["refined_text"].strip().lower() for item in eval_data}

def audit_pair(idx, raw, ref):
    pair = {"raw_asr": raw, "refined_text": ref}
    words = len(ref.split())
    raw_words = len(raw.split())
    ratio = words / max(1, raw_words)
    
    if words < 25:
        tier = "SHORT"
        min_layers = 3
    elif words < 90:
        tier = "MEDIUM"
        min_layers = 4
    else:
        tier = "LONG"
        min_layers = 4
        
    layers_dict = validator.count_active_noise_layers(raw)
    layer_count = sum(layers_dict.values())
    
    v_ok, v_err = validator.validate_pair(pair, min_noise_layers=min_layers)
    cleaned, c_status = cleaner.clean_sample(raw, ref)
    leakage = ref.strip().lower() in eval_targets
    
    print(f"Sample {idx+1}: [{tier}] Words={words} RawWords={raw_words} Ratio={ratio:.2f} Layers={layer_count} ({[k for k, v in layers_dict.items() if v]})")
    if not v_ok:
        print(f"  VALIDATOR ERROR: {v_err}")
    if c_status != "kept":
        print(f"  CLEANER ERROR: {c_status}")
    if leakage:
        print(f"  LEAKAGE ERROR: Refined text matches sft_eval.json!")
        
    return v_ok and c_status == "kept" and not leakage

print("Test harness ready.")
