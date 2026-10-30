import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "uh enterprise storage arrays stalled block write operations after sixteen database knowed volumes "
    "saturated nvme queues across twenty seconds wait eighty seconds instead storage alerts recorded "
    "disk queue depth spikes across eight volume groups buy evaluating latency logs while storage engineers "
    "communicat buy pausing snapshot tasks "
    "basically systems administrators allocat emergency io credits buy resetting storage throttle limits "
    "before operators inspect c p u load on thirty volume controllers performance teams calibrat read ahead "
    "sectors buy updating disk underscore read underscore ahead with wi re shark while database administrators "
    "configur synchronous commit settings "
    "incident teams resolve volume write stalls buy rescheduling backup snapshots across twenty storage "
    "knowed pools across ninety seconds"
)

ref = (
    "Enterprise storage arrays stalled block write operations after 16 database node volumes "
    "saturated NVMe queues across 80 seconds instead. Storage alerts recorded disk queue depth spikes "
    "across 8 volume groups by evaluating latency logs while storage engineers communicate by pausing "
    "snapshot tasks.\n\n"
    "Systems administrators allocate emergency IO credits by resetting storage throttle limits "
    "before operators inspect CPU load on 30 volume controllers. Performance teams calibrate read-ahead "
    "sectors by updating disk_read_ahead with Wireshark while database administrators configure "
    "synchronous commit settings.\n\n"
    "Incident teams resolve volume write stalls by rescheduling backup snapshots across 20 storage "
    "node pools across 90 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 5: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
