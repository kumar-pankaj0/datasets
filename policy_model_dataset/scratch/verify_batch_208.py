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

# Pairs for Batch 208
pairs = [
    # Short 1 (< 25 words)
    {
        "raw_asr": "um during sprint planning our database engineers track sprint underscore velocity across post gres clusters buy allocat story points four release milestones",
        "refined_text": "During sprint planning our database engineers track sprint_velocity across Postgres clusters by allocating story points for release milestones."
    },
    # Short 2 (< 25 words)
    {
        "raw_asr": "basically in morning standup platform leads verify cube ctl knowed health buy inspecting release underscore cadence wait switch to deployment underscore status instead four cluster synchronizat",
        "refined_text": "In morning standup platform leads verify kubectl node health by inspecting deployment_status instead for cluster synchronization."
    },
    # Medium 1 (25-89 words)
    {
        "raw_asr": "um during morning standup our backend squad triaged gateway latency tickets across twelve knowed instances while developers initially flagged ticket gate three zero two wait switch to ticket gate three zero eight instead buy analyzing error rate spikes you know site reliability engineers will configur gateway limits buy passing dash dash timeout and dash dash retries inside slash etc slash gateway dot conf and sprint engineers track r p c failure budgets four the release cycle buy recalculat request timeout thresholds",
        "refined_text": "During morning standup our backend squad triaged gateway latency tickets across 12 node instances, while developers initially flagged ticket GATE-308 instead by analyzing error rate spikes.\n\nSite reliability engineers will configure gateway limits by passing --timeout and --retries inside /etc/gateway.conf, and sprint engineers track RPC failure budgets for the release cycle by recalculating request timeout thresholds."
    },
    # Medium 2 (25-89 words)
    {
        "raw_asr": "basically during sprint planning our database leads prioritized read replica synchronizat across fourteen knowed targets and developers initially estimated ticket data four one zero wait scratch that use ticket data four one five instead buy evaluating replication lag charts you know database administrators will deploy post gres pool options buy passing dash dash max dash connections inside slash app slash db dot conf four the upcoming sprint cycle buy allocat dedicated worker threads",
        "refined_text": "During sprint planning our database leads prioritized read replica synchronization across 14 node targets, and developers initially estimated ticket DATA-415 instead by evaluating replication lag charts.\n\nDatabase administrators will deploy Postgres pool options by passing --max-connections inside /app/db.conf for the upcoming sprint cycle by allocating dedicated worker threads."
    },
    # Medium 3 (25-89 words)
    {
        "raw_asr": "um in daily standup our build team reviewed pipeline stalls across sixteen knowed runners and developers initially triaged ticket pipe five two zero wait change that to ticket pipe five two four instead buy checking execution traces platform engineers will run cube ctl commands buy passing dash dash concurrency inside slash opt slash runner dot yaml like four the next deployment milestone buy configur worker pools and terminat hanging containers",
        "refined_text": "In daily standup our build team reviewed pipeline stalls across 16 node runners, and developers initially triaged ticket PIPE-524 instead by checking execution traces.\n\nPlatform engineers will run kubectl commands by passing --concurrency inside /opt/runner.yaml for the next deployment milestone by configuring worker pools and terminating hanging containers."
    },
    # Long 1 (90+ words)
    {
        "raw_asr": "um during sprint planning our ingestion squad reviewed queue processing delays across eighteen worker knowed instances the primary bottleneck occurred when consumer partition lag grew during peak ingestion hours developers initially estimated backlog ticket queue six zero one wait switch to ticket queue six zero seven instead buy reviewing consumer lag dashboards you know platform engineers will configur ingestion worker parameters buy passing dash dash batch dash size and dash dash max dash workers inside slash opt slash queue dot conf across worker pools background a sink consumers handle payload ingestion four the upcoming roadmap release buy allocat dedicated partition buffers basically our squad will finalize queue state synchronizat across active cluster workers sprint engineers track two c p u utilization thresholds buy recalculat partition processing intervals across fourteen ingestion channels",
        "refined_text": "During sprint planning our ingestion squad reviewed queue processing delays across 18 worker node instances. The primary bottleneck occurred when consumer partition lag grew during peak ingestion hours. Developers initially estimated backlog ticket QUEUE-607 instead by reviewing consumer lag dashboards.\n\nPlatform engineers will configure ingestion worker parameters by passing --batch-size and --max-workers inside /opt/queue.conf across worker pools. Background async consumers handle payload ingestion for the upcoming roadmap release by allocating dedicated partition buffers.\n\nOur squad will finalize queue state synchronization across active cluster workers. Sprint engineers track 2 CPU utilization thresholds by recalculating partition processing intervals across 14 ingestion channels."
    },
    # Long 2 (90+ words)
    {
        "raw_asr": "basically in morning standup our networking squad examined inter service r p c communicat failures across sixteen mesh knowed instances downstream services experienced repeated connection timeouts during high throughput spikes developers initially triaged ticket mesh seven zero three wait change that to ticket mesh seven zero nine instead buy inspecting telemetry traces you know site reliability engineers execute cube ctl commands buy passing dash dash max dash retries and dash dash connect dash timeout inside slash etc slash proxy dot conf across proxy sidecars squad architects will arbitrat routing priorities four the sprint milestone buy communicat traffic limits across cluster namespaces um platform operators will terminat stale client connections buy dropping hanging proxy sockets sprint engineers evaluate two latency metrics buy recalculat timeout limits across twenty mesh routes",
        "refined_text": "In morning standup our networking squad examined inter-service RPC communication failures across 16 mesh node instances. Downstream services experienced repeated connection timeouts during high throughput spikes. Developers initially triaged ticket MESH-709 instead by inspecting telemetry traces.\n\nSite reliability engineers execute kubectl commands by passing --max-retries and --connect-timeout inside /etc/proxy.conf across proxy sidecars. Squad architects will arbitrate routing priorities for the sprint milestone by communicating traffic limits across cluster namespaces.\n\nPlatform operators will terminate stale client connections by dropping hanging proxy sockets. Sprint engineers evaluate 2 latency metrics by recalculating timeout limits across 20 mesh routes."
    },
    # Long 3 (90+ words)
    {
        "raw_asr": "um in our sprint retrospective our data infrastructure team analyzed connection exhaustion across eighteen database knowed hosts client applications experienced pool saturation when sudden query spikes flooded primary database connections engineers initially reviewed ticket pool eight one one wait scratch that use ticket pool eight one six instead buy inspecting connection pool telemetry you know database administrators will configur pooling options buy passing dash dash pool dash size and dash dash max dash overflow inside slash etc slash postgres dot conf across replica knowed workers the database squad will initializ pooled client handles four the upcoming sprint release buy synchronizat replica health checks sprint engineers monitor two c p u saturation thresholds across post gres instances like buy recalculat connection timeout budgets across fourteen database clusters",
        "refined_text": "In our sprint retrospective our data infrastructure team analyzed connection exhaustion across 18 database node hosts. Client applications experienced pool saturation when sudden query spikes flooded primary database connections. Engineers initially reviewed ticket POOL-816 instead by inspecting connection pool telemetry.\n\nDatabase administrators will configure pooling options by passing --pool-size and --max-overflow inside /etc/postgres.conf across replica node workers. The database squad will initialize pooled client handles for the upcoming sprint release by synchronizing replica health checks.\n\nSprint engineers monitor 2 CPU saturation thresholds across Postgres instances by recalculating connection timeout budgets across 14 database clusters."
    },
    # Long 4 (90+ words)
    {
        "raw_asr": "basically during roadmap planning our messaging team reviewed notification dispatch stalls across sixteen worker knowed machines notification workers dropped outbound webhook payloads when upstream delivery channels experienced elevated network jitter developers initially prioritized roadmap ticket notify two zero one wait change that to ticket notify two zero seven instead buy reviewing dispatch latency graphs you know platform engineers will configur notification dispatchers buy passing dash dash max dash retries and dash dash dead dash letter dash queue inside slash opt slash notify dot conf across active worker pools background a sink consumers handle retry processing four the upcoming quarter buy allocat dedicated delivery queues um squad operators will terminat hanging dispatcher processes buy resetting dead worker sockets sprint engineers monitor two c p u consumption counters buy recalculat retry backoff parameters across twelve delivery regions",
        "refined_text": "During roadmap planning our messaging team reviewed notification dispatch stalls across 16 worker node machines. Notification workers dropped outbound webhook payloads when upstream delivery channels experienced elevated network jitter. Developers initially prioritized roadmap ticket NOTIFY-207 instead by reviewing dispatch latency graphs.\n\nPlatform engineers will configure notification dispatchers by passing --max-retries and --dead-letter-queue inside /opt/notify.conf across active worker pools. Background async consumers handle retry processing for the upcoming quarter by allocating dedicated delivery queues.\n\nSquad operators will terminate hanging dispatcher processes by resetting dead worker sockets. Sprint engineers monitor 2 CPU consumption counters by recalculating retry backoff parameters across 12 delivery regions."
    },
    # Long 5 (90+ words)
    {
        "raw_asr": "um in morning standup our release engineering squad investigated deployment rollout stalls across eighteen compute knowed clusters production ingress controllers rejected incoming client traffic when deployment updates terminated active pod replicas prematurely developers initially triaged ticket deploy nine one two wait switch to ticket deploy nine one eight instead buy reviewing rollout event traces you know site reliability engineers execute cube ctl commands buy passing dash dash max dash surge and dash dash max dash unavailable inside slash opt slash deploy dot yaml across target clusters squad leads will configur rolling update policies four the sprint release buy synchronizat replica availability checks across cluster namespaces platform operators will terminat unstable container revisions like buy rolling back broken deployment workloads sprint engineers monitor two c p u allocat limits across pods buy recalculat container scaling thresholds across sixteen workload namespaces",
        "refined_text": "In morning standup our release engineering squad investigated deployment rollout stalls across 18 compute node clusters. Production ingress controllers rejected incoming client traffic when deployment updates terminated active pod replicas prematurely. Developers initially triaged ticket DEPLOY-918 instead by reviewing rollout event traces.\n\nSite reliability engineers execute kubectl commands by passing --max-surge and --max-unavailable inside /opt/deploy.yaml across target clusters. Squad leads will configure rolling update policies for the sprint release by synchronizing replica availability checks across cluster namespaces.\n\nPlatform operators will terminate unstable container revisions by rolling back broken deployment workloads. Sprint engineers monitor 2 CPU allocation limits across pods by recalculating container scaling thresholds across 16 workload namespaces."
    }
]

# Write to scratch/subagent_batch_208.json
target_file = Path("scratch/subagent_batch_208.json")
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"Saved {len(pairs)} pairs to {target_file}")

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

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

    # Validator check
    val_ok, val_reason = val_mod.validate_pair(pair, min_noise_layers=4)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

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
    min_short=2,
    min_medium=3,
    min_long=5,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

avg_layers = sum(layer_counts) / len(layer_counts)
print("All 10 samples passed strict validation!")
print(f"Tier counts: {tiers}")
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")
