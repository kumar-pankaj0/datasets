import json
import re
from pathlib import Path
import importlib.util

val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val)

clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
cl = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(cl)

batch_path = Path("scratch/subagent_batch_185.json")
with open(batch_path, "r", encoding="utf-8") as f:
    pairs = json.load(f)

print(f"Loaded {len(pairs)} pairs from {batch_path}")
assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(pairs):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    raw.encode("ascii")
    ref.encode("ascii")

    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    val_ok, val_reason = val.validate_pair(pair, min_noise_layers=4)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    clean_obj, clean_reason = cl.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx+1} clean status: {clean_reason}"

    words = len(ref.split())
    nl = val.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
        assert nl >= 3, f"Sample {idx+1} has {nl} noise layers, expected >= 3!"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
        assert nl >= 4, f"Sample {idx+1} has {nl} noise layers, expected >= 4!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx+1} has {nl} noise layers, expected >= 4!"

print(f"Tier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

batch_ok, batch_msg, batch_meta = val.validate_batch(pairs, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
assert batch_ok, f"Batch validation failed: {batch_msg}"
print(f"Batch metadata: {batch_meta}")
print("ALL 20 SAMPLES PASSED ALL VALIDATION INVARIANTS WITH 0 ERRORS!")
