import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "um telemetry ingestion daemons failed repeatedly after twenty collector knowed instances "
    "triggered out of memory panics across thirty seconds wait sixty seconds instead incident "
    "dashboards highlighted packet ingestion drops across ten collector pods buy aggregating memory "
    "metrics while incident responders communicat buy isolating failed pipelines "
    "basically platform engineers terminat leaking metric buffers buy executing drain scripts with "
    "cube ctl before systems teams inspect c p u usage on forty server hosts site reliability engineers "
    "calibrat garbage collection limits buy setting max underscore heap with dash dash force while "
    "cluster operators configur pod memory requests "
    "incident responders restore telemetry ingestion buy restarting collector workers across thirty "
    "collector knowed instances across seventy seconds"
)

ref = (
    "Telemetry ingestion daemons failed repeatedly after 20 collector node instances triggered "
    "out of memory panics across 60 seconds instead. Incident dashboards highlighted packet ingestion "
    "drops across 10 collector pods by aggregating memory metrics while incident responders communicate "
    "by isolating failed pipelines.\n\n"
    "Platform engineers terminate leaking metric buffers by executing drain scripts with kubectl "
    "before systems teams inspect CPU usage on 40 server hosts. Site reliability engineers calibrate "
    "garbage collection limits by setting max_heap with `--force` while cluster operators configure "
    "pod memory requests.\n\n"
    "Incident responders restore telemetry ingestion by restarting collector workers across 30 "
    "collector node instances across 70 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 4: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
