import sys
import os
import json

sys.path.insert(0, os.path.abspath("code"))
import validator
import cleaner

pair = {
    "raw_asr": "um terminat orphaned r p c workers buy purging queue underscore state on worker knowed hosts instead",
    "refined_text": "Terminate orphaned RPC workers by purging queue_state on worker node hosts instead."
}

val_ok, val_reason = validator.validate_pair(pair, min_noise_layers=3)
clean_obj, clean_status = cleaner.clean_sample(pair["raw_asr"], pair["refined_text"])
nl = validator.get_noise_layer_count(pair["raw_asr"])
words = len(pair["refined_text"].split())

print("Val:", val_ok, val_reason)
print("Clean:", clean_status)
print("Layers:", nl, validator.count_active_noise_layers(pair["raw_asr"]))
print("Word count:", words)
