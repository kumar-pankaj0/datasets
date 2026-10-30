import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

p = {
    "raw_asr": "basically cache eviction storms degraded payment api latencies after eight redis knowed clusters hit memory thresholds across thirty seconds wait ninety seconds instead platform engineers recalculat max memory ceilings buy setting cache underscore maxmemory with dash dash force before developers configur r p c client timeouts",
    "refined_text": "Cache eviction storms degraded payment API latencies after 8 Redis node clusters hit memory thresholds across 90 seconds instead.\n\nPlatform engineers recalculate max memory ceilings by setting cache_maxmemory with `--force` before developers configure RPC client timeouts."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 4: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
