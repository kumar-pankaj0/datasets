import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

p = {
    "raw_asr": "uh database clusters dropped read traffic after ten storage knowed instances scanned excessive tombstones across twenty seconds wait fifty seconds instead telemetry engineers calibrat query execution timeouts buy setting tombstone underscore limit with wi re shark before operators deduplicat query filters",
    "refined_text": "Database clusters dropped read traffic after 10 storage node instances scanned excessive tombstones across 50 seconds instead.\n\nTelemetry engineers calibrate query execution timeouts by setting tombstone_limit with Wireshark before operators deduplicate query filters."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 6: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
