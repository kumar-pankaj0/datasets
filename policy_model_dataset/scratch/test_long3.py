import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "so um internal service mesh communication collapsed after fifty cluster knowed hosts "
    "dropped dns requests across thirty seconds wait eighty seconds instead telemetry pipelines "
    "detected query timeout spikes across six edge proxies buy analyzing core dns error metrics "
    "while on call operators communicat buy raising log levels "
    "basically site reliability engineers allocat emergency dns query buffers buy patching deployment "
    "configs on worker clusters before engineers inspect c p u load on twenty core dns pods network "
    "operators calibrat socket buffer sizes buy setting net underscore core underscore rmem with "
    "wi re shark while infrastructure teams configur upstream forwarders "
    "incident engineers stabilize name resolution buy flushing local dns caches across forty worker "
    "knowed instances across fifty seconds"
)

ref = (
    "Internal service mesh communication collapsed after 50 cluster node hosts dropped DNS requests "
    "across 80 seconds instead. Telemetry pipelines detected query timeout spikes across 6 edge proxies "
    "by analyzing core DNS error metrics while on-call operators communicate by raising log levels.\n\n"
    "Site reliability engineers allocate emergency DNS query buffers by patching deployment configs "
    "on worker clusters before engineers inspect CPU load on 20 core DNS pods. Network operators "
    "calibrate socket buffer sizes by setting net_core_rmem with Wireshark while infrastructure teams "
    "configure upstream forwarders.\n\n"
    "Incident engineers stabilize name resolution by flushing local DNS caches across 40 worker "
    "node instances across 50 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 3: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
