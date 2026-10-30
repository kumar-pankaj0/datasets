import sys
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

val_mod = load_module("validator", "code/validator.py")
clean_mod = load_module("cleaner", "code/cleaner.py")

validate_pair = val_mod.validate_pair
validate_batch = val_mod.validate_batch
clean_sample = clean_mod.clean_sample

def test_samples(samples):
    all_ok = True
    print(f"Testing {len(samples)} samples...")
    for i, s in enumerate(samples):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)
        tier = "Short" if words < 25 else ("Medium" if words <= 90 else "Long")
        
        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"[{status}] Sample {i+1} ({tier}, {words} words, raw: {raw_words}, ratio: {ratio:.2f})")
        if not v_ok:
            print(f"  validator fail: {v_reason}")
        if c_res is None:
            print(f"  cleaner fail: {c_reason}")

    b_ok, b_reason, b_counts = validate_batch(samples, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Counts: {b_counts}")
    return all_ok and b_ok
