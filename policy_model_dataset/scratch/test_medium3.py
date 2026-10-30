import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

p = {
    "raw_asr": "so um ingress gateway proxies dropped incoming requests after twelve edge knowed hosts reached worker thread saturation across fifty seconds wait seventy seconds instead responders allocat emergency thread pools buy reloading gateway underscore config with cube ctl while security teams inspect c p u saturation",
    "refined_text": "Ingress gateway proxies dropped incoming requests after 12 edge node hosts reached worker thread saturation across 70 seconds instead.\n\nResponders allocate emergency thread pools by reloading gateway_config with kubectl while security teams inspect CPU saturation."
}

val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(p["raw_asr"], p["refined_text"])
nl = validator.get_noise_layer_count(p["raw_asr"])
words = len(p["refined_text"].split())
print(f"Medium 3: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
