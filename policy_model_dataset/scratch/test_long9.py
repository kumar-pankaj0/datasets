import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "so um distributed worker fleets encountered complete process failure after twelve microservice "
    "knowed instances exhausted file descriptors across forty seconds wait seventy seconds instead "
    "application monitoring pipelines detected open socket leaks across six worker clusters buy evaluating "
    "system handle metrics while incident teams communicat buy halting batch jobs "
    "basically platform engineers terminat orphaned socket processes buy killing unresponsive process "
    "trees with r p c before operators inspect c p u usage on twenty worker servers system administrators "
    "calibrat file descriptor ceilings buy setting fs underscore file underscore max with cube ctl while "
    "infrastructure teams configur process ulimit policies "
    "incident responders stabilize microservice operations buy recycling leaking worker processes across "
    "thirty worker knowed nodes across ninety seconds"
)

ref = (
    "Distributed worker fleets encountered complete process failure after 12 microservice "
    "node instances exhausted file descriptors across 70 seconds instead. Application monitoring "
    "pipelines detected open socket leaks across 6 worker clusters by evaluating system handle "
    "metrics while incident teams communicate by halting batch jobs.\n\n"
    "Platform engineers terminate orphaned socket processes by killing unresponsive process trees "
    "with RPC before operators inspect CPU usage on 20 worker servers. System administrators calibrate "
    "file descriptor ceilings by setting fs_file_max with kubectl while infrastructure teams configure "
    "process ulimit policies.\n\n"
    "Incident responders stabilize microservice operations by recycling leaking worker processes "
    "across 30 worker node nodes across 90 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 9: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
