import json
from pathlib import Path
import importlib.util
import re

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

batch_path = Path("scratch/subagent_batch_199.json")
with open(batch_path, "r", encoding="utf-8") as f:
    pairs = json.load(f)

print(f"Loaded {len(pairs)} pairs from {batch_path}")
assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(pairs, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    words = len(ref.split())
    min_l = 3 if words < 25 else 4
    val_ok, val_reason = val_mod.validate_pair(pair, min_noise_layers=min_l)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    nl = val_mod.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx} has newline in short tier!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
        cut_words_found = val_mod.CUT_WORD_REGEX.findall(raw)
        assert len(cut_words_found) <= 1, f"Sample {idx} has >1 cut word: {cut_words_found}"
        sentences = [s for s in re.split(r'[.!?]+', ref.strip()) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx} short tier has {len(sentences)} sentences: {sentences}"
    elif words < 90:
        tiers["medium"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in medium tier!"
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
        sentences = [s for s in re.split(r'[.!?]+', ref.strip()) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx} medium tier has {len(sentences)} sentences: {sentences}"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"
        assert not re.search(r'(^|\n)\s*[-*]\s+', ref), f"Sample {idx} has markdown bullets!"
        assert not re.search(r'(^|\n)\s*\d+\.\s+', ref), f"Sample {idx} has numbered list!"

# Batch validation
batch_ok, batch_reason, batch_stats = val_mod.validate_batch(
    pairs,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

avg_layers = sum(layer_counts) / len(layer_counts)
assert avg_layers >= 4.0, f"Average noise layers {avg_layers:.2f} < 4.0"

print("All 20 samples passed strict independent verification!")
print(f"Tier counts: {tiers}")
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")
