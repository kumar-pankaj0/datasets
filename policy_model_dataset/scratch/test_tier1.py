import sys
import os
import json

sys.path.insert(0, os.path.abspath("code"))
import validator
import cleaner

shorts = [
    {
        "raw_asr": "um terminat orphaned r p c workers buy purging queue underscore state on worker knowed hosts instead",
        "refined_text": "Terminate orphaned RPC workers by purging queue_state on worker node hosts instead."
    },
    {
        "raw_asr": "uh calibrat packet drop thresholds buy adjusting socket underscore buffer on post gres knowed instances instead",
        "refined_text": "Calibrate packet drop thresholds by adjusting socket_buffer on Postgres node instances instead."
    },
    {
        "raw_asr": "basically configur c p u throttling alerts buy inspecting node underscore metrics on worker knowed hosts instead",
        "refined_text": "Configure CPU throttling alerts by inspecting node_metrics on worker node hosts instead."
    },
    {
        "raw_asr": "so um initializ r p c retry budgets buy setting client underscore config on worker knowed servers instead",
        "refined_text": "Initialize RPC retry budgets by setting client_config on worker node servers instead."
    }
]

for idx, p in enumerate(shorts, 1):
    val_ok, val_reason = validator.validate_pair(p, min_noise_layers=3)
    clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
    nl = validator.get_noise_layer_count(p["raw_asr"])
    words = len(p["refined_text"].split())
    print(f"Short {idx}: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
