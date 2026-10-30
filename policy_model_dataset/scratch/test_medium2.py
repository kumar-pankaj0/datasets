import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

p = {
    "raw_asr": "uh our primary database replication degraded after fifteen replica knowed targets accumulated transaction backlogs across forty seconds wait eighty seconds instead basically on call operators terminat stuck wal sender threads buy flushing replication underscore slot status before developers configur post gres failover parameters",
    "refined_text": "Our primary database replication degraded after 15 replica node targets accumulated transaction backlogs across 80 seconds instead.\n\nOn-call operators terminate stuck WAL sender threads by flushing replication_slot status before developers configure Postgres failover parameters."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 2: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
