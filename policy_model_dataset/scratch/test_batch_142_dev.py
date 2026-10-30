import sys
import os

sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

def test_pair(raw, ref, min_noise=4):
    pair = {"raw_asr": raw, "refined_text": ref}
    v_ok, v_msg = validate_pair(pair, min_noise_layers=min_noise)
    c_res, c_status = clean_sample(raw, ref)
    layers = count_active_noise_layers(raw)
    layer_cnt = sum(layers.values())
    words = len(ref.split())
    print(f"Words: {words} | Layers ({layer_cnt}): {layers}")
    print(f"Validator: {v_ok} ({v_msg})")
    print(f"Cleaner: {c_status}")
    if not v_ok or c_status != "kept":
        print("FAILED!")
        return False
    return True

if __name__ == "__main__":
    print("Test harness loaded.")
