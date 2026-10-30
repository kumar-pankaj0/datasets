import json
import importlib.util
from pathlib import Path

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batches = [44, 45, 46, 47, 48]
total_samples = 0
global_tier_counts = {"short": 0, "medium": 0, "long": 0}

for b_id in batches:
    batch_path = Path(f"scratch/subagent_batch_{b_id}.json")
    assert batch_path.exists(), f"Batch file {batch_path} missing!"
    with open(batch_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)
    
    assert len(pairs) == 20, f"Batch {b_id} has {len(pairs)} pairs, expected 20!"
    
    b_tiers = {"short": 0, "medium": 0, "long": 0}
    for idx, pair in enumerate(pairs):
        raw = pair.get("raw_asr", "")
        ref = pair.get("refined_text", "")
        
        # Leakage check
        assert raw.strip().lower() not in eval_raws, f"Batch {b_id} sample {idx+1} raw leaked into eval!"
        assert ref.strip() not in eval_refs, f"Batch {b_id} sample {idx+1} ref leaked into eval!"
        
        # Validator check
        is_val, reason = val_mod.validate_pair(pair)
        assert is_val, f"Batch {b_id} sample {idx+1} failed validate_pair: {reason}"
        
        # Cleaner check
        cleaned_obj, drop_reason = clean_mod.clean_sample(raw, ref)
        assert cleaned_obj is not None, f"Batch {b_id} sample {idx+1} dropped by cleaner: {drop_reason}"
        
        words = len(ref.split())
        if words < 25:
            b_tiers["short"] += 1
        elif words < 90:
            b_tiers["medium"] += 1
        else:
            b_tiers["long"] += 1

    # Batch distribution check
    is_batch_val, msg, returned_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
    assert is_batch_val, f"Batch {b_id} failed validate_batch: {msg} (tiers: {returned_tiers})"
    
    print(f"Batch {b_id}: 20/20 PASS, Tiers: {b_tiers}")
    total_samples += 20
    for k in b_tiers:
        global_tier_counts[k] += b_tiers[k]

print(f"\nWave 10 Total: {total_samples} samples, Global Tiers: {global_tier_counts}")
print("ALL WAVE 10 BATCHES VERIFIED 100% CLEAN AND LEAKAGE-FREE!")
