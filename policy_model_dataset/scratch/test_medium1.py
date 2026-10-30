import sys
import os

sys.path.insert(0, os.path.abspath("code"))
import validator
import cleaner

p = {
    "raw_asr": "um during the broker failover twenty worker knowed instances triggered rebalance storms across thirty seconds wait sixty seconds instead incident engineers communicat buy analyzing consumer underscore lag with wi re shark while systems teams right two c p u throttling profiles",
    "refined_text": "During the broker failover, 20 worker node instances triggered rebalance storms across 60 seconds instead.\n\nIncident engineers communicate by analyzing consumer_lag with Wireshark while systems teams write 2 CPU throttling profiles."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 1: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
