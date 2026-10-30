import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("code"))
import validator as val
import cleaner as cl

samples = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples
    {
        "raw_asr": "basically recalculat the team velocity buy setting sprint underscore limit two eight a sink tasks",
        "refined_text": "Recalculate the team velocity by setting sprint_limit to 8 async tasks."
    },
    {
        "raw_asr": "um configur the release roadmap buy passing dash dash profile four the c p u telemetry service",
        "refined_text": "Configure the release roadmap by passing --profile for the CPU telemetry service."
    },
    {
        "raw_asr": "you know unblock the staging deployment buy scheduling post gres migrat under change underscore id",
        "refined_text": "Unblock the staging deployment by scheduling Postgres migration under change_id."
    },
    {
        "raw_asr": "uh synchronizat the sprint deliverable buy updating r p c schema bindings four team underscore board",
        "refined_text": "Synchronize the sprint deliverable by updating RPC schema bindings for team_board."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples
    {
        "raw_asr": "basically during morning standup our backend squad triaged r p c outage remediation ticket roadmap one zero one wait switch to ticket roadmap one zero seven instead buy reviewing service degradation logs um developers agreed two configur circuit breaker limits buy passing dash dash timeout inside slash etc slash rpc dot conf buy recalculat client retry intervals four the sprint",
        "refined_text": "During morning standup our backend squad triaged RPC outage remediation ticket ROADMAP-107 instead by reviewing service degradation logs.\n\nDevelopers agreed to configure circuit breaker limits by passing --timeout inside /etc/rpc.conf by recalculating client retry intervals for the sprint."
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
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples
    {
        "raw_asr": "basically during morning standup our backend squad triaged connection pool saturation across our post gres database knowed cluster um the primary impediment occurred when active client requests exceeded pool capacity across twelve database replicas developers initially reviewed sprint ticket db one one zero wait change that to ticket db one one eight instead buy reviewing connection latency charts you know site reliability engineers will configur pooling parameters buy passing dash dash pool dash size and dash dash idle dash timeout inside slash etc slash pgbouncer dot conf across active database worker knowed instances our platform operators will terminat dead client sockets buy resetting abandoned application sessions four the upcoming release database administrators inspect transaction locks sprint engineers right two c p u utilization monitors buy recalculat connection acquisition latency",
        "refined_text": "During morning standup our backend squad triaged connection pool saturation across our Postgres database node cluster. The primary impediment occurred when active client requests exceeded pool capacity across 12 database replicas. Developers initially reviewed sprint ticket DB-118 instead by reviewing connection latency charts.\n\nSite reliability engineers will configure pooling parameters by passing --pool-size and --idle-timeout inside /etc/pgbouncer.conf across active database worker node instances.\n\nOur platform operators will terminate dead client sockets by resetting abandoned application sessions for the upcoming release. Database administrators inspect transaction locks. Sprint engineers write 2 CPU utilization monitors by recalculating connection acquisition latency."
    },
    {
        "raw_asr": "um during sprint planning our platform squad evaluated message backlog accumulation across sixteen event stream knowed instances the primary blocker involved partition offset lag when twenty consumer queues experienced processing stalls developers initially scoped backlog ticket queue two two zero wait switch to ticket queue two two six instead buy reviewing queue consumption rates you know our team decided two allocat eight story points buy passing dash dash batch dash size and dash dash max dash workers inside slash app slash consumer dot py basically background a sink consumers will communicat partition states across worker threads our engineers will synchronizat consumer group offsets buy committing transaction batches four tomorrow deployment sprint developers right two r p c throughput metrics evaluating event delivery",
        "refined_text": "During sprint planning our platform squad evaluated message backlog accumulation across 16 event stream node instances. The primary blocker involved partition offset lag when 20 consumer queues experienced processing stalls. Developers initially scoped backlog ticket QUEUE-226 instead by reviewing queue consumption rates.\n\nOur team decided to allocate 8 story points by passing --batch-size and --max-workers inside /app/consumer.py.\n\nBackground async consumers will communicate partition states across worker threads. Our engineers will synchronize consumer group offsets by committing transaction batches for tomorrow deployment. Sprint developers write 2 RPC throughput metrics evaluating event delivery."
    },
    {
        "raw_asr": "basically during quarterly roadmap review our platform squad addressed container throttling alerts across twenty four cluster knowed instances the main defect involved horizontal autoscaler flapping when application utilization reached eighty percent across eight namespace pods infrastructure engineers triaged scaling ticket scale three three zero wait scratch that use ticket scale three three five instead buy reviewing autoscaler events you know cluster operators execute cube ctl dash dash target dash cpu and dash dash grace dash period inside slash var slash deploy dot sh across production deployments site reliability engineers will calibrat pod scaling bounds buy adjusting replica thresholds our squad will terminat unneeded staging pods four the milestone release sprint engineers right two c p u telemetry gauges buy recalculat target metric utilization",
        "refined_text": "During quarterly roadmap review our platform squad addressed container throttling alerts across 24 cluster node instances. The main defect involved horizontal autoscaler flapping when application utilization reached 80 percent across 8 namespace pods. Infrastructure engineers triaged scaling ticket SCALE-335 instead by reviewing autoscaler events.\n\nCluster operators execute kubectl --target-cpu and --grace-period inside /var/deploy.sh across production deployments.\n\nSite reliability engineers will calibrate pod scaling bounds by adjusting replica thresholds. Our squad will terminate unneeded staging pods for the milestone release. Sprint engineers write 2 CPU telemetry gauges by recalculating target metric utilization."
    },
    {
        "raw_asr": "um in our morning standup our api platform squad reviewed upstream request timeouts across fourteen gateway knowed instances the primary trigger involved downstream socket starvation when incoming traffic spikes collided with post gres query locks developers initially investigated gateway ticket gateway four four zero wait change that to ticket gateway four four eight instead buy measuring response distribution curves you know platform engineers will configur edge proxy routes buy passing dash dash retry dash count and dash dash connection dash timeout inside slash etc slash gateway dot conf quality assurance engineers will arbitrat client retry limits across testing environments basically our team will initializ isolated routing caches buy purging expired gateway entries four the sprint cycle sprint developers right two r p c latency monitors evaluating route performance",
        "refined_text": "In our morning standup our API platform squad reviewed upstream request timeouts across 14 gateway node instances. The primary trigger involved downstream socket starvation when incoming traffic spikes collided with Postgres query locks. Developers initially investigated gateway ticket GATEWAY-448 instead by measuring response distribution curves.\n\nPlatform engineers will configure edge proxy routes by passing --retry-count and --connection-timeout inside /etc/gateway.conf.\n\nQuality assurance engineers will arbitrate client retry limits across testing environments. Our team will initialize isolated routing caches by purging expired gateway entries for the sprint cycle. Sprint developers write 2 RPC latency monitors evaluating route performance."
    },
    {
        "raw_asr": "basically during our sprint retrospective our backend team analyzed memory retention in background a sink batch tasks across eighteen knowed workers the main defect involved unreleased task contexts when continuous batch processing exhausted allocated heap memory developers initially examined worker ticket worker five five zero wait switch to ticket worker five five seven instead buy reviewing memory allocation traces you know site reliability engineers will configur worker limits buy passing dash dash max dash tasks and dash dash memory dash limit inside slash etc slash worker dot conf data engineers will deduplicat incoming batch payload entries buy validating transaction keys platform operators will terminat hanging worker routines buy recycling stagnant worker processes four the sprint milestone sprint engineers right two c p u profiling gauges buy synchronizat memory garbage collection cycles",
        "refined_text": "During our sprint retrospective our backend team analyzed memory retention in background async batch tasks across 18 node workers. The main defect involved unreleased task contexts when continuous batch processing exhausted allocated heap memory. Developers initially examined worker ticket WORKER-557 instead by reviewing memory allocation traces.\n\nSite reliability engineers will configure worker limits by passing --max-tasks and --memory-limit inside /etc/worker.conf.\n\nData engineers will deduplicate incoming batch payload entries by validating transaction keys. Platform operators will terminate hanging worker routines by recycling stagnant worker processes for the sprint milestone. Sprint engineers write 2 CPU profiling gauges by synchronizing memory garbage collection cycles."
    },
    {
        "raw_asr": "um during quarterly roadmap planning our telemetry squad addressed packet drop spikes across ten ingestion knowed servers the primary impediment involved d m a memory ring exhaustion during high throughput packet transmiss across network interfaces developers initially scoped pipeline ticket road six six zero wait scratch that use ticket road six six four instead buy analyzing packet drop graphs you know infrastructure specialists will configur streaming limits buy passing dash dash ring dash size and dash dash buffer dash limit inside slash etc slash pipeline dot conf our engineers will allocat dedicated memory segments buy isolating high priority event streams basically platform operators will calibrat buffer thresholds buy monitoring socket error counts four the roadmap milestone sprint developers right two r p c diagnostic probes evaluating packet transmiss latency",
        "refined_text": "During quarterly roadmap planning our telemetry squad addressed packet drop spikes across 10 ingestion node servers. The primary impediment involved DMA memory ring exhaustion during high throughput packet transmission across network interfaces. Developers initially scoped pipeline ticket ROAD-664 instead by analyzing packet drop graphs.\n\nInfrastructure specialists will configure streaming limits by passing --ring-size and --buffer-limit inside /etc/pipeline.conf.\n\nOur engineers will allocate dedicated memory segments by isolating high priority event streams. Platform operators will calibrate buffer thresholds by monitoring socket error counts for the roadmap milestone. Sprint developers write 2 RPC diagnostic probes evaluating packet transmission latency."
    },
    {
        "raw_asr": "basically in morning standup our security and networking teams reviewed mutual handshake failures across twenty two proxy knowed instances the primary defect involved client certificate expiration during our service mesh migrat rollout developers initially scoped security ticket mesh seven seven zero wait change that to ticket mesh seven seven three instead buy examining proxy error distributions you know site reliability engineers will configur proxy settings buy passing dash dash cert dash path and dash dash handshake dash timeout inside slash app slash mesh dot yaml security specialists will synchronizat renewed client credentials with post gres authentication tables our squad will terminat deprecated cryptographic handshakes buy enforcing modern cipher suites four the sprint release sprint developers right two r p c security verifiers tracking proxy connection integrity",
        "refined_text": "In morning standup our security and networking teams reviewed mutual handshake failures across 22 proxy node instances. The primary defect involved client certificate expiration during our service mesh migration rollout. Developers initially scoped security ticket MESH-773 instead by examining proxy error distributions.\n\nSite reliability engineers will configure proxy settings by passing --cert-path and --handshake-timeout inside /app/mesh.yaml.\n\nSecurity specialists will synchronize renewed client credentials with Postgres authentication tables. Our squad will terminate deprecated cryptographic handshakes by enforcing modern cipher suites for the sprint release. Sprint developers write 2 RPC security verifiers tracking proxy connection integrity."
    },
    {
        "raw_asr": "um during sprint planning our database squad evaluated cache consistency lag across fifteen cache knowed workers the main defect involved stale object reads when post gres read replica synchronizat lagged thirty seconds behind primary database writes developers initially estimated cache ticket cache eight eight zero wait switch to ticket cache eight eight five instead buy analyzing cache hit ratios you know data engineers will configur caching properties buy passing dash dash cache dash ttl and dash dash sync dash interval inside slash app slash cache dot py our squad will initializ clean key namespaces buy purging obsolete cache entries developers will communicat cache invalidation events across worker threads four the upcoming sprint sprint engineers right two c p u execution gauges buy recalculat cache expiration boundaries",
        "refined_text": "During sprint planning our database squad evaluated cache consistency lag across 15 cache node workers. The main defect involved stale object reads when Postgres read replica synchronization lagged 30 seconds behind primary database writes. Developers initially estimated cache ticket CACHE-885 instead by analyzing cache hit ratios.\n\nData engineers will configure caching properties by passing --cache-ttl and --sync-interval inside /app/cache.py.\n\nOur squad will initialize clean key namespaces by purging obsolete cache entries. Developers will communicate cache invalidation events across worker threads for the upcoming sprint. Sprint engineers write 2 CPU execution gauges by recalculating cache expiration boundaries."
    },
    {
        "raw_asr": "basically during morning standup our devops squad triaged test execution stalls across sixteen runner knowed instances the primary impediment involved worker thread starvation when parallel test suites exceeded container limits developers initially reviewed pipeline ticket build nine nine zero wait scratch that use ticket build nine nine two instead buy analyzing test duration histograms you know platform operators execute cube ctl dash dash concurrency and dash dash timeout inside slash var slash runner dot sh across runner pods quality assurance leads will arbitrat test quarantine decisions buy identifying unstable integration suites our devops team will terminat abandoned runner jobs buy clearing hanging test containers four the sprint deployment sprint engineers right two r p c test monitors buy recalculat test execution latency",
        "refined_text": "During morning standup our DevOps squad triaged test execution stalls across 16 runner node instances. The primary impediment involved worker thread starvation when parallel test suites exceeded container limits. Developers initially reviewed pipeline ticket BUILD-992 instead by reviewing test duration histograms.\n\nPlatform operators execute kubectl --concurrency and --timeout inside /var/runner.sh across runner pods.\n\nQuality assurance leads will arbitrate test quarantine decisions by identifying unstable integration suites. Our DevOps team will terminate abandoned runner jobs by clearing hanging test containers for the sprint deployment. Sprint engineers write 2 RPC test monitors by recalculating test execution latency."
    },
    {
        "raw_asr": "um in our sprint retrospective our edge squad investigated unexpected traffic shedding across twelve edge knowed instances the primary trigger involved token bucket exhaustion when incoming client traffic bursts exceeded capacity developers initially triaged ticket limit one two zero wait change that to ticket limit one two four instead buy evaluating request drop graphs you know edge specialists will configur bucket options buy passing dash dash rate dash limit and dash dash burst dash size inside slash etc slash limiter dot conf background a sink workers will calibrat consumer token allocations buy adjusting client quota weights site reliability engineers will terminat rogue connection attempts buy dropping malicious request streams four the milestone delivery sprint engineers right two c p u latency probes buy recalculat edge token replenishment intervals",
        "refined_text": "In our sprint retrospective our edge squad investigated unexpected traffic shedding across 12 edge node instances. The primary trigger involved token bucket exhaustion when incoming client traffic bursts exceeded capacity. Developers initially triaged ticket LIMIT-124 instead by evaluating request drop graphs.\n\nEdge specialists will configure bucket options by passing --rate-limit and --burst-size inside /etc/limiter.conf.\n\nBackground async workers will calibrate consumer token allocations by adjusting client quota weights. Site reliability engineers will terminate rogue connection attempts by dropping malicious request streams for the milestone delivery. Sprint engineers write 2 CPU latency probes by recalculating edge token replenishment intervals."
    }
]

output_path = Path("scratch/subagent_batch_188.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)
print(f"Wrote {len(samples)} samples to {output_path}")

# Full audit
with open(output_path, "r", encoding="utf-8") as f:
    loaded = json.load(f)

assert len(loaded) == 20

# 1. Leakage check against sft_eval.json
with open("sft_eval.json", "r") as f:
    eval_data = json.load(f)
eval_refined = {item["refined_text"].strip().lower() for item in eval_data}
eval_raw = {item["raw_asr"].strip().lower() for item in eval_data}

for i, s in enumerate(loaded):
    ref_norm = s["refined_text"].strip().lower()
    raw_norm = s["raw_asr"].strip().lower()
    assert ref_norm not in eval_refined, f"Sample {i+1} ref leaked into sft_eval.json"
    assert raw_norm not in eval_raw, f"Sample {i+1} raw leaked into sft_eval.json"
print("Leakage check: PASSED (0 overlaps with sft_eval.json)")

# 2. Individual validation
tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []
for i, s in enumerate(loaded, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]

    raw.encode("ascii")
    ref.encode("ascii")

    words = len(ref.split())
    nl = val.get_noise_layer_count(raw)
    layer_counts.append(nl)

    min_nl = 3 if words < 25 else 4
    v_ok, v_msg = val.validate_pair(s, min_noise_layers=min_nl)
    assert v_ok, f"Sample {i} validate_pair failed: {v_msg}"

    c_res, c_msg = cl.clean_sample(raw, ref)
    assert c_msg == "kept", f"Sample {i} clean_sample failed: {c_msg}"

    if words < 25:
        tier_counts["short"] += 1
        assert "\n" not in ref, f"Sample {i} newline in short"
        sentences = [sen for sen in re.split(r'[.!?]+', ref) if sen.strip()]
        assert len(sentences) == 1, f"Sample {i} short has {len(sentences)} sentences"
    elif words < 90:
        tier_counts["medium"] += 1
        assert "\n\n" in ref, f"Sample {i} missing paragraph break in medium"
        sentences = [sen for sen in re.split(r'[.!?]+', ref) if sen.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {i} medium has {len(sentences)} sentences"
    else:
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {i} missing paragraph break in long"

avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Tier counts: {tier_counts}")
print(f"Average noise layers: {avg_layers:.2f}")

assert tier_counts["short"] == 4
assert tier_counts["medium"] == 6
assert tier_counts["long"] == 10
assert avg_layers >= 4.0

b_ok, b_msg, b_meta = val.validate_batch(loaded, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
assert b_ok, f"Batch validation failed: {b_msg}"
print(f"Batch metadata: {b_meta}")
print("ALL INVARIANTS SATISFIED! ZERO ERRORS.")
