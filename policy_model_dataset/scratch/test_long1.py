import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "um our transit gateway infrastructure experienced severe route flap after thirty edge knowed routers "
    "dropped peering sessions across forty seconds wait seventy seconds instead telemetry dashboards recorded "
    "packet drops across four transit backbones buy analyzing bgp session metrics while incident commanders "
    "communicat buy setting routing priority "
    "basically network reliability engineers terminat unstable bgp peers buy isolating edge interface configs "
    "before operators inspect c p u load on fifty core routers systems engineers calibrat keepalive intervals "
    "buy updating neighbor underscore timeout with wi re shark while infrastructure teams configur failover "
    "routing tables buy verifying path stability "
    "incident responders confirm packet loss mitigation buy monitoring transit metrics across twelve monitoring "
    "probes across sixty seconds"
)

ref = (
    "Our transit gateway infrastructure experienced severe route flap after 30 edge node routers "
    "dropped peering sessions across 70 seconds instead. Telemetry dashboards recorded packet drops "
    "across 4 transit backbones by analyzing BGP session metrics while incident commanders "
    "communicate by setting routing priority.\n\n"
    "Network reliability engineers terminate unstable BGP peers by isolating edge interface configs "
    "before operators inspect CPU load on 50 core routers. Systems engineers calibrate keepalive "
    "intervals by updating neighbor_timeout with Wireshark while infrastructure teams configure failover "
    "routing tables by verifying path stability.\n\n"
    "Incident responders confirm packet loss mitigation by monitoring transit metrics across 12 monitoring "
    "probes across 60 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 1: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
