import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "um asynchronous message processing systems experienced split write races after fourteen "
    "coordination knowed hosts dropped distributed lock leases across twenty seconds wait sixty "
    "seconds instead database monitoring services detected concurrent transaction collisions "
    "across four queue workers buy parsing transaction conflict rates while incident responders "
    "communicat buy isolating consumer groups "
    "basically backend engineers allocat emergency lock ttl buffers buy adjusting lease parameters "
    "with post gres before systems teams inspect c p u load on thirty database hosts platform "
    "reliability engineers calibrat heartbeat frequencies buy setting lock underscore lease underscore "
    "timeout with wi re shark while infrastructure teams configur redis lock managers "
    "incident responders restore data consistency buy terminating conflicting queue workers across "
    "twenty worker knowed instances across eighty seconds"
)

ref = (
    "Asynchronous message processing systems experienced split write races after 14 coordination "
    "node hosts dropped distributed lock leases across 60 seconds instead. Database monitoring "
    "services detected concurrent transaction collisions across 4 queue workers by parsing "
    "transaction conflict rates while incident responders communicate by isolating consumer groups.\n\n"
    "Backend engineers allocate emergency lock TTL buffers by adjusting lease parameters with Postgres "
    "before systems teams inspect CPU load on 30 database hosts. Platform reliability engineers "
    "calibrate heartbeat frequencies by setting lock_lease_timeout with Wireshark while infrastructure "
    "teams configure Redis lock managers.\n\n"
    "Incident responders restore data consistency by terminating conflicting queue workers across "
    "20 worker node instances across 80 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 10: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
