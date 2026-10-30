import json
import os
import sys

sys.path.insert(0, os.path.abspath("code"))
import validator as val
import cleaner as cl

medium_samples = [
    {
        "raw_asr": "basically during morning standup our backend squad triaged outage remediation ticket roadmap one zero one wait switch to ticket roadmap one zero seven instead buy reviewing service degradation logs um developers agreed two configur circuit breaker limits buy passing dash dash timeout inside slash etc slash rpc dot conf buy recalculat client retry intervals four the sprint",
        "refined_text": "During morning standup our backend squad triaged outage remediation ticket ROADMAP-107 instead by reviewing service degradation logs.\n\nDevelopers agreed to configure circuit breaker limits by passing --timeout inside /etc/rpc.conf by recalculating client retry intervals for the sprint."
    },
    {
        "raw_asr": "uh four sprint planning our team estimated queue consumer ticket sprint two zero one wait change that to ticket sprint two zero six instead buy inspecting message backlog depth across five a sink workers you know our squad decided two allocat seven story points buy passing dash dash concurrency inside slash app slash queue dot py buy synchronizat partition commit intervals",
        "refined_text": "For sprint planning our team estimated queue consumer ticket SPRINT-206 instead by inspecting message backlog depth across 5 async workers.\n\nOur squad decided to allocate 7 story points by passing --concurrency inside /app/queue.py by synchronizing partition commit intervals."
    },
    {
        "raw_asr": "basically during standup the infrastructure squad triaged canary ticket deploy three zero two wait scratch that use ticket deploy three zero eight instead buy analyzing c p u utilization charts um site reliability engineers agreed two calibrat throttling thresholds buy passing dash dash limit inside slash etc slash deploy dot conf buy terminat degraded worker pods",
        "refined_text": "During standup the infrastructure squad triaged canary ticket DEPLOY-308 instead by analyzing CPU utilization charts.\n\nSite reliability engineers agreed to calibrate throttling thresholds by passing --limit inside /etc/deploy.conf by terminating degraded worker pods."
    },
    {
        "raw_asr": "um in our sprint retrospective developers reviewed database replication ticket retro four one zero wait switch to ticket retro four one five instead buy tracking replica delay on the primary post gres knowed you know engineers will configur streaming parameters buy passing dash dash wal dash keep inside slash etc slash replica dot conf buy synchronizat replica states four tomorrow release",
        "refined_text": "In our sprint retrospective developers reviewed database replication ticket RETRO-415 instead by tracking replica delay on the primary Postgres node.\n\nEngineers will configure streaming parameters by passing --wal-keep inside /etc/replica.conf by synchronizing replica states for tomorrow release."
    },
    {
        "raw_asr": "uh four quarterly roadmap alignment our platform team evaluated cluster upgrade ticket board five two zero wait change that to ticket board five two four instead buy checking namespace quotas across cluster knowed instances basically operators will execute cube ctl dash dash dry dash run inside slash var slash cluster dot sh buy communicat release milestones two engineering leads",
        "refined_text": "For quarterly roadmap alignment our platform team evaluated cluster upgrade ticket BOARD-524 instead by checking namespace quotas across cluster node instances.\n\nOperators will execute kubectl --dry-run inside /var/cluster.sh by communicating release milestones to engineering leads."
    },
    {
        "raw_asr": "basically in morning standup our data platform engineers triaged a sink event ingestion ticket ops six three zero wait switch to ticket ops six three seven instead buy monitoring duplicate event warnings um our team decided two configur pipeline filters buy passing dash dash deduplication inside slash app slash ingest dot py buy deduplicat incoming telemetry records four the sprint delivery",
        "refined_text": "In morning standup our data platform engineers triaged async event ingestion ticket OPS-637 instead by monitoring duplicate event warnings.\n\nOur team decided to configure pipeline filters by passing --deduplication inside /app/ingest.py by deduplicating incoming telemetry records for the sprint delivery."
    }
]

for i, s in enumerate(medium_samples, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    v_ok, v_msg = val.validate_pair(s, min_noise_layers=4)
    c_res, c_msg = cl.clean_sample(raw, ref)
    nl = val.get_noise_layer_count(raw)
    words = len(ref.split())
    print(f"Medium {i}: words={words}, layers={nl}, val={v_ok} ({v_msg}), clean={c_msg}")
    assert v_ok, f"Medium {i} val fail: {v_msg}"
    assert c_msg == "kept", f"Medium {i} clean fail: {c_msg}"
    assert 25 <= words < 90, f"Medium {i} words out of range: {words}"
    assert "\n\n" in ref, f"Medium {i} missing paragraph break"

print("All medium samples passed!")
