import sys, os
sys.path.insert(0, os.path.abspath("code"))
import validator, cleaner

raw = (
    "basically ingress proxy clusters rejected incoming tls handshakes after twenty five edge knowed hosts "
    "exhausted ssl session caches across forty seconds wait seventy seconds instead monitoring pipelines "
    "flagged handshake drop surges across twelve gateway zones buy analyzing error status codes while "
    "security engineers communicat buy distributing fallback certificates "
    "so um infrastructure operators terminat stale ssl sessions buy executing cache flush commands with "
    "cube ctl before network engineers inspect c p u spikes on sixty proxy instances platform teams calibrat "
    "tls ticket lifetimes buy setting ssl underscore session underscore timeout with dash dash force while "
    "systems teams configur proxy keepalive settings "
    "incident response engineers stabilize edge ingress traffic buy reloading gateway certificates across "
    "thirty edge knowed gateways across sixty seconds"
)

ref = (
    "Ingress proxy clusters rejected incoming TLS handshakes after 25 edge node hosts exhausted "
    "SSL session caches across 70 seconds instead. Monitoring pipelines flagged handshake drop surges "
    "across 12 gateway zones by analyzing error status codes while security engineers communicate by "
    "distributing fallback certificates.\n\n"
    "Infrastructure operators terminate stale SSL sessions by executing cache flush commands with kubectl "
    "before network engineers inspect CPU spikes on 60 proxy instances. Platform teams calibrate TLS "
    "ticket lifetimes by setting ssl_session_timeout with `--force` while systems teams configure proxy "
    "keepalive settings.\n\n"
    "Incident response engineers stabilize edge ingress traffic by reloading gateway certificates across "
    "30 edge node gateways across 60 seconds."
)

p = {"raw_asr": raw, "refined_text": ref}
val_ok, val_reason = validator.validate_pair(p, min_noise_layers=4)
clean_obj, clean_status = cleaner.clean_sample(raw, ref)
nl = validator.get_noise_layer_count(raw)
words = len(ref.split())
print(f"Long 6: Val={val_ok} ({val_reason}), Clean={clean_status}, Layers={nl}, Words={words}")
