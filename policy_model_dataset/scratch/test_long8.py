import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "uh our edge firewall clusters dropped inbound tcp connections after sixteen ingress knowed hosts "
    "filled syn backlogs across thirty seconds wait eighty seconds instead telemetry dashboards reported "
    "dropped syn packet spikes across eight edge network regions buy tracking socket queue statistics "
    "while security incident responders communicat buy isolating attack sources "
    "basically network infrastructure teams allocat expanded syn cookie tables buy modifying kernel "
    "parameters with cube ctl before systems engineers inspect c p u load on thirty firewall hosts "
    "platform reliability engineers calibrat tcp backlog thresholds buy setting net underscore ipv4 "
    "underscore tcp underscore max underscore syn underscore backlog with wi re shark while network "
    "operators configur syn flood mitigation rules "
    "incident responders restore edge connection throughput buy clearing invalid half open connections "
    "across twenty edge knowed servers across sixty seconds"
)

ref = (
    "Our edge firewall clusters dropped inbound TCP connections after 16 ingress node hosts "
    "filled SYN backlogs across 80 seconds instead. Telemetry dashboards reported dropped SYN "
    "packet spikes across 8 edge network regions by tracking socket queue statistics while "
    "security incident responders communicate by isolating attack sources.\n\n"
    "Network infrastructure teams allocate expanded SYN cookie tables by modifying kernel "
    "parameters with kubectl before systems engineers inspect CPU load on 30 firewall hosts. "
    "Platform reliability engineers calibrate TCP backlog thresholds by setting "
    "net_ipv4_tcp_max_syn_backlog with Wireshark while network operators configure SYN flood "
    "mitigation rules.\n\n"
    "Incident responders restore edge connection throughput by clearing invalid half-open "
    "connections across 20 edge node servers across 60 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 8: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
