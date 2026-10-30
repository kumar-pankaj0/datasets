import json
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
  # --- Tier 1: Short (< 25 words, exactly 1 sentence, 0 newlines, max 1 cut-word, >= 3 noise layers) ---
  {
    "raw_asr": "basically recalculat the sprint velocity buy setting sprint underscore quota two six a sink tasks",
    "refined_text": "Recalculate the sprint velocity by setting sprint_quota to 6 async tasks."
  },
  {
    "raw_asr": "um configur the team roadmap buy passing dash dash profile four the c p u telemetry collector",
    "refined_text": "Configure the team roadmap by passing --profile for the CPU telemetry collector."
  },
  {
    "raw_asr": "you know unblock the standup backlog buy scheduling post gres migrat under release underscore batch",
    "refined_text": "Unblock the standup backlog by scheduling Postgres migration under release_batch."
  },
  {
    "raw_asr": "uh synchronizat the roadmap schedule buy updating r p c endpoint descriptors four worker underscore nodes",
    "refined_text": "Synchronize the roadmap schedule by updating RPC endpoint descriptors for worker_nodes."
  },

  # --- Tier 2: Medium (25-89 words, 1-3 sentences, \n\n breaks, >= 4 noise layers) ---
  {
    "raw_asr": "basically during morning standup our backend squad triaged r p c timeout remediation ticket rpc one zero one wait switch to ticket rpc one zero eight instead buy reviewing service degradation logs um developers agreed two configur circuit breaker limits buy passing dash dash timeout inside slash etc slash grpc dot conf buy recalculat client retry intervals four the sprint",
    "refined_text": "During morning standup our backend squad triaged RPC timeout remediation ticket RPC-108 instead by reviewing service degradation logs.\n\nDevelopers agreed to configure circuit breaker limits by passing --timeout inside /etc/grpc.conf by recalculating client retry intervals for the sprint."
  },
  {
    "raw_asr": "uh four sprint planning our team estimated queue consumer ticket queue two zero three wait change that to ticket queue two zero nine instead buy inspecting message backlog depth across six a sink workers you know our squad decided two allocat nine story points buy passing dash dash concurrency inside slash app slash worker dot py buy synchronizat partition commit intervals",
    "refined_text": "For sprint planning our team estimated queue consumer ticket QUEUE-209 instead by inspecting message backlog depth across 6 async workers.\n\nOur squad decided to allocate 9 story points by passing --concurrency inside /app/worker.py by synchronizing partition commit intervals."
  },
  {
    "raw_asr": "basically during standup the infrastructure squad triaged canary deployment ticket deploy three one zero wait scratch that use ticket deploy three one six instead buy analyzing c p u utilization spikes um site reliability engineers agreed two calibrat throttling thresholds buy passing dash dash limit inside slash etc slash canary dot conf buy terminat degraded worker pods",
    "refined_text": "During standup the infrastructure squad triaged canary deployment ticket DEPLOY-316 instead by analyzing CPU utilization spikes.\n\nSite reliability engineers agreed to calibrate throttling thresholds by passing --limit inside /etc/canary.conf by terminating degraded worker pods."
  },
  {
    "raw_asr": "um in our sprint retrospective developers reviewed database replication ticket retro four zero two wait switch to ticket retro four zero seven instead buy tracking replica delay on the primary post gres knowed you know engineers will configur streaming parameters buy passing dash dash wal dash keep inside slash etc slash postgres dot conf buy synchronizat replica states four tomorrow release",
    "refined_text": "In our sprint retrospective developers reviewed database replication ticket RETRO-407 instead by tracking replica delay on the primary Postgres node.\n\nEngineers will configure streaming parameters by passing --wal-keep inside /etc/postgres.conf by synchronizing replica states for tomorrow release."
  },
  {
    "raw_asr": "uh four quarterly roadmap alignment our platform team evaluated cluster upgrade ticket board five one zero wait change that to ticket board five one eight instead buy checking namespace quotas across cluster knowed instances basically operators will execute cube ctl dash dash dry dash run inside slash var slash cluster dot sh buy communicat release milestones two engineering leads",
    "refined_text": "For quarterly roadmap alignment our platform team evaluated cluster upgrade ticket BOARD-518 instead by checking namespace quotas across cluster node instances.\n\nOperators will execute kubectl --dry-run inside /var/cluster.sh by communicating release milestones to engineering leads."
  },
  {
    "raw_asr": "basically in morning standup our data platform engineers triaged a sink event ingestion ticket ingest six two zero wait switch to ticket ingest six two five instead buy monitoring duplicate event warnings um our team decided two configur pipeline filters buy passing dash dash deduplication inside slash app slash stream dot py buy deduplicat incoming telemetry records four the sprint delivery",
    "refined_text": "In morning standup our data platform engineers triaged async event ingestion ticket INGEST-625 instead by monitoring duplicate event warnings.\n\nOur team decided to configure pipeline filters by passing --deduplication inside /app/stream.py by deduplicating incoming telemetry records for the sprint delivery."
  },

  # --- Tier 3: Long (90+ words, multi-paragraph \n\n structure, >= 4 noise layers) ---
  {
    "raw_asr": "basically during morning standup our backend squad triaged connection pool exhaustion across our post gres database knowed cluster um the primary impediment occurred when active client requests exceeded pool capacity across fourteen database replicas developers initially reviewed sprint ticket data one one zero wait change that to ticket data one one seven instead buy reviewing connection latency charts you know site reliability engineers will configur pooling parameters buy passing dash dash pool dash size and dash dash idle dash timeout inside slash etc slash pgbouncer dot conf across active database worker knowed instances our platform operators will terminat dead client sockets buy resetting abandoned application sessions four the upcoming release database administrators inspect transaction locks sprint engineers right two c p u utilization monitors buy recalculat connection acquisition latency",
    "refined_text": "During morning standup our backend squad triaged connection pool exhaustion across our Postgres database node cluster. The primary impediment occurred when active client requests exceeded pool capacity across 14 database replicas. Developers initially reviewed sprint ticket DATA-117 instead by reviewing connection latency charts.\n\nSite reliability engineers will configure pooling parameters by passing --pool-size and --idle-timeout inside /etc/pgbouncer.conf across active database worker node instances.\n\nOur platform operators will terminate dead client sockets by resetting abandoned application sessions for the upcoming release. Database administrators inspect transaction locks. Sprint engineers write 2 CPU utilization monitors by recalculating connection acquisition latency."
  },
  {
    "raw_asr": "um during sprint planning our platform squad evaluated message backlog accumulation across eighteen event stream knowed instances the primary blocker involved partition offset lag when twenty two consumer queues experienced processing stalls developers initially scoped backlog ticket stream two two zero wait switch to ticket stream two two eight instead buy reviewing queue consumption rates you know our team decided two allocat nine story points buy passing dash dash batch dash size and dash dash max dash workers inside slash app slash consumer dot py basically background a sink consumers will communicat partition states across worker threads our engineers will synchronizat consumer group offsets buy committing transaction batches four tomorrow deployment sprint developers right two r p c throughput metrics evaluating event delivery across six active partitions",
    "refined_text": "During sprint planning our platform squad evaluated message backlog accumulation across 18 event stream node instances. The primary blocker involved partition offset lag when 22 consumer queues experienced processing stalls. Developers initially scoped backlog ticket STREAM-228 instead by reviewing queue consumption rates.\n\nOur team decided to allocate 9 story points by passing --batch-size and --max-workers inside /app/consumer.py.\n\nBackground async consumers will communicate partition states across worker threads. Our engineers will synchronize consumer group offsets by committing transaction batches for tomorrow deployment. Sprint developers write 2 RPC throughput metrics evaluating event delivery across 6 active partitions."
  },
  {
    "raw_asr": "basically during quarterly roadmap review our platform squad addressed container throttling alerts across twenty six cluster knowed instances the main defect involved horizontal autoscaler flapping when application utilization reached eighty percent across ten namespace pods infrastructure engineers triaged scaling ticket auto three three zero wait scratch that use ticket auto three three six instead buy reviewing autoscaler events you know cluster operators execute cube ctl dash dash target dash cpu and dash dash grace dash period inside slash var slash deploy dot sh across production deployments site reliability engineers will calibrat pod scaling bounds buy adjusting replica thresholds our squad will terminat unneeded staging pods four the milestone release sprint engineers right two c p u telemetry gauges buy recalculat target metric utilization across twelve replica sets",
    "refined_text": "During quarterly roadmap review our platform squad addressed container throttling alerts across 26 cluster node instances. The main defect involved horizontal autoscaler flapping when application utilization reached 80 percent across 10 namespace pods. Infrastructure engineers triaged scaling ticket AUTO-336 instead by reviewing autoscaler events.\n\nCluster operators execute kubectl --target-cpu and --grace-period inside /var/deploy.sh across production deployments.\n\nSite reliability engineers will calibrate pod scaling bounds by adjusting replica thresholds. Our squad will terminate unneeded staging pods for the milestone release. Sprint engineers write 2 CPU telemetry gauges by recalculating target metric utilization across 12 replica sets."
  },
  {
    "raw_asr": "um in our morning standup our api platform squad reviewed upstream request timeouts across sixteen gateway knowed instances the primary trigger involved downstream socket starvation when incoming traffic spikes collided with post gres query locks developers initially investigated gateway ticket gateway four five zero wait change that to ticket gateway four five six instead buy measuring response distribution curves you know platform engineers will configur edge proxy routes buy passing dash dash retry dash count and dash dash connection dash timeout inside slash etc slash proxy dot conf quality assurance engineers will arbitrat client retry limits across testing environments basically our team will initializ isolated routing caches buy purging expired gateway entries four the sprint cycle sprint developers right two r p c latency monitors evaluating route performance across eight upstream clusters",
    "refined_text": "In our morning standup our API platform squad reviewed upstream request timeouts across 16 gateway node instances. The primary trigger involved downstream socket starvation when incoming traffic spikes collided with Postgres query locks. Developers initially investigated gateway ticket GATEWAY-456 instead by measuring response distribution curves.\n\nPlatform engineers will configure edge proxy routes by passing --retry-count and --connection-timeout inside /etc/proxy.conf.\n\nQuality assurance engineers will arbitrate client retry limits across testing environments. Our team will initialize isolated routing caches by purging expired gateway entries for the sprint cycle. Sprint developers write 2 RPC latency monitors evaluating route performance across 8 upstream clusters."
  },
  {
    "raw_asr": "basically during our sprint retrospective our backend team analyzed memory retention in background a sink batch tasks across twenty knowed workers the main defect involved unreleased task contexts when continuous batch processing exhausted allocated heap memory developers initially examined worker ticket worker five six zero wait switch to ticket worker five six eight instead buy reviewing memory allocation traces you know site reliability engineers will configur worker limits buy passing dash dash max dash tasks and dash dash memory dash limit inside slash etc slash worker dot conf data engineers will deduplicat incoming batch payload entries buy validating transaction keys platform operators will terminat hanging worker routines buy recycling stagnant worker processes four the sprint milestone sprint engineers right two c p u profiling gauges buy synchronizat memory garbage collection cycles across ten processing pools",
    "refined_text": "During our sprint retrospective our backend team analyzed memory retention in background async batch tasks across 20 node workers. The main defect involved unreleased task contexts when continuous batch processing exhausted allocated heap memory. Developers initially examined worker ticket WORKER-568 instead by reviewing memory allocation traces.\n\nSite reliability engineers will configure worker limits by passing --max-tasks and --memory-limit inside /etc/worker.conf.\n\nData engineers will deduplicate incoming batch payload entries by validating transaction keys. Platform operators will terminate hanging worker routines by recycling stagnant worker processes for the sprint milestone. Sprint engineers write 2 CPU profiling gauges by synchronizing memory garbage collection cycles across 10 processing pools."
  },
  {
    "raw_asr": "um during quarterly roadmap planning our telemetry squad addressed packet drop spikes across twelve ingestion knowed servers the primary impediment involved d m a memory ring exhaustion during high throughput packet transmiss across network interfaces developers initially scoped pipeline ticket route six seven zero wait scratch that use ticket route six seven five instead buy analyzing packet drop graphs you know infrastructure specialists will configur streaming limits buy passing dash dash ring dash size and dash dash buffer dash limit inside slash etc slash pipeline dot conf our engineers will allocat dedicated memory segments buy isolating high priority event streams basically platform operators will calibrat buffer thresholds buy monitoring socket error counts four the roadmap milestone sprint developers right two r p c diagnostic probes evaluating packet transmiss latency across eight network adapters",
    "refined_text": "During quarterly roadmap planning our telemetry squad addressed packet drop spikes across 12 ingestion node servers. The primary impediment involved DMA memory ring exhaustion during high throughput packet transmission across network interfaces. Developers initially scoped pipeline ticket ROUTE-675 instead by analyzing packet drop graphs.\n\nInfrastructure specialists will configure streaming limits by passing --ring-size and --buffer-limit inside /etc/pipeline.conf.\n\nOur engineers will allocate dedicated memory segments by isolating high priority event streams. Platform operators will calibrate buffer thresholds by monitoring socket error counts for the roadmap milestone. Sprint developers write 2 RPC diagnostic probes evaluating packet transmission latency across 8 network adapters."
  },
  {
    "raw_asr": "basically in morning standup our security and networking teams reviewed mutual handshake failures across twenty four proxy knowed instances the primary defect involved client certificate expiration during our service mesh migrat rollout developers initially scoped security ticket auth seven eight zero wait change that to ticket auth seven eight six instead buy examining proxy error distributions you know site reliability engineers will configur proxy settings buy passing dash dash cert dash path and dash dash handshake dash timeout inside slash app slash mesh dot yaml security specialists will synchronizat renewed client credentials with post gres authentication tables our squad will terminat deprecated cryptographic handshakes buy enforcing modern cipher suites four the sprint release sprint developers right two r p c security verifiers tracking proxy connection integrity across twelve ingress gateways",
    "refined_text": "In morning standup our security and networking teams reviewed mutual handshake failures across 24 proxy node instances. The primary defect involved client certificate expiration during our service mesh migration rollout. Developers initially scoped security ticket AUTH-786 instead by examining proxy error distributions.\n\nSite reliability engineers will configure proxy settings by passing --cert-path and --handshake-timeout inside /app/mesh.yaml.\n\nSecurity specialists will synchronize renewed client credentials with Postgres authentication tables. Our squad will terminate deprecated cryptographic handshakes by enforcing modern cipher suites for the sprint release. Sprint developers write 2 RPC security verifiers tracking proxy connection integrity across 12 ingress gateways."
  },
  {
    "raw_asr": "um during sprint planning our database squad evaluated cache consistency lag across eighteen cache knowed workers the main defect involved stale object reads when post gres read replica synchronizat lagged thirty seconds behind primary database writes developers initially estimated cache ticket sync eight nine zero wait switch to ticket sync eight nine four instead buy analyzing cache hit ratios you know data engineers will configur caching properties buy passing dash dash cache dash ttl and dash dash sync dash interval inside slash app slash cache dot py our squad will initializ clean key namespaces buy purging obsolete cache entries developers will communicat cache invalidation events across worker threads four the upcoming sprint sprint engineers right two c p u execution gauges buy recalculat cache expiration boundaries across sixteen tenant partitions",
    "refined_text": "During sprint planning our database squad evaluated cache consistency lag across 18 cache node workers. The main defect involved stale object reads when Postgres read replica synchronization lagged 30 seconds behind primary database writes. Developers initially estimated cache ticket SYNC-894 instead by analyzing cache hit ratios.\n\nData engineers will configure caching properties by passing --cache-ttl and --sync-interval inside /app/cache.py.\n\nOur squad will initialize clean key namespaces by purging obsolete cache entries. Developers will communicate cache invalidation events across worker threads for the upcoming sprint. Sprint engineers write 2 CPU execution gauges by recalculating cache expiration boundaries across 16 tenant partitions."
  },
  {
    "raw_asr": "basically during morning standup our devops squad triaged test execution stalls across eighteen runner knowed instances the primary impediment involved worker thread starvation when parallel test suites exceeded container limits developers initially reviewed pipeline ticket runner nine zero zero wait scratch that use ticket runner nine zero eight instead buy analyzing test duration histograms you know platform operators execute cube ctl dash dash concurrency and dash dash timeout inside slash var slash test dot sh across runner pods quality assurance leads will arbitrat test quarantine decisions buy identifying unstable integration suites our devops team will terminat abandoned runner jobs buy clearing hanging test containers four the sprint deployment sprint engineers right two r p c test monitors buy recalculat test execution latency across fourteen build agents",
    "refined_text": "During morning standup our DevOps squad triaged test execution stalls across 18 runner node instances. The primary impediment involved worker thread starvation when parallel test suites exceeded container limits. Developers initially reviewed pipeline ticket RUNNER-908 instead by reviewing test duration histograms.\n\nPlatform operators execute kubectl --concurrency and --timeout inside /var/test.sh across runner pods.\n\nQuality assurance leads will arbitrate test quarantine decisions by identifying unstable integration suites. Our DevOps team will terminate abandoned runner jobs by clearing hanging test containers for the sprint deployment. Sprint engineers write 2 RPC test monitors by recalculating test execution latency across 14 build agents."
  },
  {
    "raw_asr": "um in our sprint retrospective our edge squad investigated unexpected traffic shedding across fourteen edge knowed instances the primary trigger involved token bucket exhaustion when incoming client traffic bursts exceeded capacity developers initially triaged ticket quota one zero zero wait change that to ticket quota one zero six instead buy evaluating request drop graphs you know edge specialists will configur bucket options buy passing dash dash rate dash limit and dash dash burst dash size inside slash etc slash rate dot conf background a sink workers will calibrat consumer token allocations buy adjusting client quota weights site reliability engineers will terminat rogue connection attempts buy dropping malicious request streams four the milestone delivery sprint engineers right two c p u latency probes buy recalculat edge token replenishment intervals across twenty gateway zones",
    "refined_text": "In our sprint retrospective our edge squad investigated unexpected traffic shedding across 14 edge node instances. The primary trigger involved token bucket exhaustion when incoming client traffic bursts exceeded capacity. Developers initially triaged ticket QUOTA-106 instead by evaluating request drop graphs.\n\nEdge specialists will configure bucket options by passing --rate-limit and --burst-size inside /etc/rate.conf.\n\nBackground async workers will calibrate consumer token allocations by adjusting client quota weights. Site reliability engineers will terminate rogue connection attempts by dropping malicious request streams for the milestone delivery. Sprint engineers write 2 CPU latency probes by recalculating edge token replenishment intervals across 20 gateway zones."
  }
]

out_file = Path("scratch/subagent_batch_198.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"Saved {len(pairs)} pairs to {out_file}")

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(pairs, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Validator check with min_noise_layers=4 (allows 3 for short)
    val_ok, val_reason = val_mod.validate_pair(pair, min_noise_layers=4)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    nl = val_mod.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx} has newline in short tier!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
    elif words < 90:
        tiers["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"

# Batch validation
batch_ok, batch_reason, batch_stats = val_mod.validate_batch(
    pairs,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

avg_layers = sum(layer_counts) / len(layer_counts)
print("All 20 samples passed strict validation!")
print(f"Tier counts: {tiers}")
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")
