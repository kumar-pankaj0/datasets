import json
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

validator = load_module("validator", "code/validator.py")
cleaner = load_module("cleaner", "code/cleaner.py")

eval_data = json.load(open("sft_eval.json"))
eval_rawe = {x["raw_asr"].strip().lower() for x in eval_data}
eval_ref = {x["refined_text"].strip().lower() for x in eval_data}

batches = [74, 75, 76, 77, 78]
all_samples = []

for b_id in batches:
    fname = f"scratch/subagent_batch_{b_id}.json"
    with open(fname, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n--- Batch {b_id}: {len(data)} samples ---")
    assert len(data) == 20, f"Batch {b_id} does not have 20 samples!"
    
    # Batch validation
    is_valid, msg, stats = validator.validate_batch(data, min_short=4, min_medium=6, min_long=10)
    print("Batch distribution:", is_valid, msg, stats)
    assert is_valid, f"Batch {b_id} distribution invalid: {msg}"
    
    # Pair & cleaner validation
    for i, s in enumerate(data):
        raw = s["raw_asr"]
        ref = s["refined_text"]
        v_is_valid, v_msg = validator.validate_pair(s)
        assert v_is_valid, f"Batch {b_id} sample {i} invalid: {v_msg}"
        
        c_sample, c_msg = cleaner.clean_sample(raw, ref)
        assert c_sample is not None and c_msg == "kept", f"Batch {b_id} sample {i} cleaner status {c_msg}"
        
        # Leakage check
        assert raw.strip().lower() not in eval_rawe, f"Batch {b_id} sample {i} leaked raw into eval!"
        assert ref.strip().lower() not in eval_ref, f"Batch {b_id} sample {i} leaked ref into eval!"
        
        all_samples.append(s)

print(f"\nAll {len(all_samples)} samples in Wave 16 verified successfully with 0 drops!")
