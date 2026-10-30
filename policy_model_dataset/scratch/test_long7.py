import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "um distributed search clusters encountered cluster partition states after eighteen master knowed nodes "
    "triggered ping timeouts across twenty seconds wait ninety seconds instead telemetry pipelines detected "
    "split brain index errors across six search indices buy inspecting cluster health status while incident "
    "commanders communicat buy pausing data indexing "
    "basically database reliability engineers terminat isolated master instances buy executing cluster isolation "
    "scripts with post gres before systems teams inspect c p u load on forty search servers operations teams "
    "calibrat quorum election parameters buy setting discovery underscore zen underscore minimum underscore "
    "master underscore nodes with wi re shark while infrastructure engineers configur heartbeat intervals "
    "incident responders restore search cluster synchronization buy electing single master instances across "
    "twenty master knowed hosts across eighty seconds"
)

ref = (
    "Distributed search clusters encountered cluster partition states after 18 master node nodes "
    "triggered ping timeouts across 90 seconds instead. Telemetry pipelines detected split-brain "
    "index errors across 6 search indices by inspecting cluster health status while incident commanders "
    "communicate by pausing data indexing.\n\n"
    "Database reliability engineers terminate isolated master instances by executing cluster isolation "
    "scripts with Postgres before systems teams inspect CPU load on 40 search servers. Operations teams "
    "calibrate quorum election parameters by setting discovery_zen_minimum_master_nodes with Wireshark "
    "while infrastructure engineers configure heartbeat intervals.\n\n"
    "Incident responders restore search cluster synchronization by electing single master instances "
    "across 20 master node hosts across 80 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 7: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
