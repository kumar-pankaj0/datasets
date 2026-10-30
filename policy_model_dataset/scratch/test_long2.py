import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "uh our payment processing service encountered complete thread starvation after forty worker knowed instances "
    "exhausted database connection pools across twenty seconds wait ninety seconds instead telemetry pipelines "
    "registered latency spikes across eight api gateways buy parsing transaction latency metrics while incident "
    "responders communicat buy isolating failing services "
    "basically database administrators terminat blocking lock processes buy inspecting transaction underscore log "
    "on post gres hosts before platform engineers inspect c p u saturation on sixty server clusters systems engineers "
    "calibrat connection pool limits buy setting max underscore pool with cube ctl while telemetry monitors "
    "configur alert thresholds "
    "incident response teams restore payment processing buy releasing stuck locks across twenty worker threads "
    "across eighty seconds"
)

ref = (
    "Our payment processing service encountered complete thread starvation after 40 worker node instances "
    "exhausted database connection pools across 90 seconds instead. Telemetry pipelines registered latency "
    "spikes across 8 API gateways by parsing transaction latency metrics while incident responders communicate "
    "by isolating failing services.\n\n"
    "Database administrators terminate blocking lock processes by inspecting transaction_log on Postgres hosts "
    "before platform engineers inspect CPU saturation on 60 server clusters. Systems engineers calibrate "
    "connection pool limits by setting max_pool with kubectl while telemetry monitors configure alert thresholds.\n\n"
    "Incident response teams restore payment processing by releasing stuck locks across 20 worker threads "
    "across 80 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 2: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
