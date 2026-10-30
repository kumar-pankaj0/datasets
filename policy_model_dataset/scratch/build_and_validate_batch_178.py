import json
import os
import sys

sys.path.insert(0, os.path.abspath("code"))
import validator
import cleaner

samples = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples
    {
        "raw_asr": "um allocat five story points buy assigning ticket underscore id two the a sink backend worker",
        "refined_text": "Allocate 5 story points by assigning ticket_id to the async backend worker."
    },
    {
        "raw_asr": "uh configur the sprint backlog buy passing dash dash timeout two the r p c gateway team",
        "refined_text": "Configure the sprint backlog by passing --timeout to the RPC gateway team."
    },
    {
        "raw_asr": "basically terminat the stalled sprint deployment buy running cube ctl dash dash grace dash period two clear pod state",
        "refined_text": "Terminate the stalled sprint deployment by running kubectl --grace-period to clear pod state."
    },
    {
        "raw_asr": "you know synchronizat quarterly roadmap milestones buy tracking release underscore status four our c p u platform team",
        "refined_text": "Synchronize quarterly roadmap milestones by tracking release_status for our CPU platform team."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples
    {
        "raw_asr": "um during morning standup our squad reviewed post gres migrat ticket jira four two zero one wait switch to ticket jira four two zero eight instead buy checking connection pool limits basically the team agreed two communicat the pool settings buy passing dash dash max dash connections inside slash etc slash pool dot conf four the upcoming sprint cycle",
        "refined_text": "During morning standup our squad reviewed Postgres migration ticket JIRA-4208 instead by checking connection pool limits.\n\nThe team agreed to communicate the pool settings by passing --max-connections inside /etc/pool.conf for the upcoming sprint cycle."
    },
    {
        "raw_asr": "uh four sprint planning our team estimated ticket jira five three zero one wait change that to ticket jira five three zero nine instead buy reviewing queue backpressure across eight a sink consumers you know we agreed two allocat six story points buy passing dash dash workers inside slash app slash worker dot py basically our squad will synchronizat consumer group offsets four tomorrow release",
        "refined_text": "For sprint planning our team estimated ticket JIRA-5309 instead by reviewing queue backpressure across 8 async consumers.\n\nWe agreed to allocate 6 story points by passing --workers inside /app/worker.py while our squad will synchronize consumer group offsets for tomorrow release."
    },
    {
        "raw_asr": "basically during standup the squad triaged ticket jira six one one zero wait switch to ticket jira six one one four instead buy analyzing c p u spikes on the ingestion knowed um site reliability engineers will terminat hanging ingestion jobs buy passing dash dash timeout inside slash app slash ingest dot py buy tracking consumer lag four the sprint",
        "refined_text": "During standup the squad triaged ticket JIRA-6114 instead by analyzing CPU spikes on the ingestion node.\n\nSite reliability engineers will terminate hanging ingestion jobs by passing --timeout inside /app/ingest.py by tracking consumer lag for the sprint."
    },
    {
        "raw_asr": "um four sprint planning our engineers evaluated r p c gateway refactoring ticket jira seven two two zero wait scratch that use ticket jira seven two two five instead buy calculating request latency you know developers will configur the service buy passing dash dash concurrency inside slash etc slash gateway dot conf buy stabilizing thread allocat four the release",
        "refined_text": "For sprint planning our engineers evaluated RPC gateway refactoring ticket JIRA-7225 instead by calculating request latency.\n\nDevelopers will configure the service by passing --concurrency inside /etc/gateway.conf by stabilizing thread allocation for the release."
    },
    {
        "raw_asr": "uh during standup our platform squad reviewed rollout ticket jira eight three three zero wait change that to ticket jira eight three three six instead buy inspecting memory pressure across cluster knowed pods basically operators execute cube ctl dash dash grace dash period inside slash var slash deploy dot sh buy recalculat container limits four the roadmap milestone",
        "refined_text": "During standup our platform squad reviewed rollout ticket JIRA-8336 instead by inspecting memory pressure across cluster node pods.\n\nOperators execute kubectl --grace-period inside /var/deploy.sh by recalculating container limits for the roadmap milestone."
    },
    {
        "raw_asr": "basically in the sprint retrospective our squad analyzed a sink worker ticket jira nine four four zero wait switch to ticket jira nine four four seven instead buy measuring message retry rates um engineers agreed two communicat worker parameters buy passing dash dash batch dash size inside slash etc slash worker dot conf buy deduplicat payload records four the next sprint",
        "refined_text": "In the sprint retrospective our squad analyzed async worker ticket JIRA-9447 instead by measuring message retry rates.\n\nEngineers agreed to communicate worker parameters by passing --batch-size inside /etc/worker.conf by deduplicating payload records for the next sprint."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples
    {
        "raw_asr": "basically during morning standup our backend squad triaged connection timeouts on the post gres database knowed cluster um the primary trigger involved connection pool saturation when forty active services exceeded client limits across twelve database instances developers initially prioritized ticket jira one zero one one wait change that to ticket jira one zero one nine instead buy reviewing connection pool exhaustion metrics you know site reliability engineers will configur pool settings buy passing dash dash idle dash timeout and dash dash max dash connections inside slash etc slash pool dot conf our platform operators will terminat dead connections buy resetting idle client sessions four the upcoming sprint cycle database administrators inspect query execution locks sprint engineers right two c p u latency monitors tracking database connection health",
        "refined_text": "During morning standup our backend squad triaged connection timeouts on the Postgres database node cluster. The primary trigger involved connection pool saturation when 40 active services exceeded client limits across 12 database instances. Developers initially prioritized ticket JIRA-1019 instead by reviewing connection pool exhaustion metrics.\n\nSite reliability engineers will configure pool settings by passing --idle-timeout and --max-connections inside /etc/pool.conf.\n\nOur platform operators will terminate dead connections by resetting idle client sessions for the upcoming sprint cycle. Database administrators inspect query execution locks. Sprint engineers write 2 CPU latency monitors tracking database connection health."
    },
    {
        "raw_asr": "um during sprint planning our platform squad evaluated consumer lag across sixteen event worker tasks on the streaming cluster knowed instances the primary impediment involved consumer offset drift when twenty partition queues accumulated message backpressure developers initially scoped ticket jira two one two zero wait switch to ticket jira two one two eight instead buy analyzing queue processing bottlenecks you know our squad agreed two allocat eight story points buy passing dash dash batch dash size and dash dash workers inside slash app slash consumer dot py basically the a sink workers will communicat partition state across consumer threads our team will synchronizat partition offset commits four the upcoming release sprint engineers right two r p c health probes evaluating consumer throughput",
        "refined_text": "During sprint planning our platform squad evaluated consumer lag across 16 event worker tasks on the streaming cluster node instances. The primary impediment involved consumer offset drift when 20 partition queues accumulated message backpressure. Developers initially scoped ticket JIRA-2128 instead by analyzing queue processing bottlenecks.\n\nOur squad agreed to allocate 8 story points by passing --batch-size and --workers inside /app/consumer.py.\n\nThe async workers will communicate partition state across consumer threads. Our team will synchronize partition offset commits for the upcoming release. Sprint engineers write 2 RPC health probes evaluating consumer throughput."
    },
    {
        "raw_asr": "basically during quarterly roadmap review our platform squad analyzed c p u throttling across thirty microservices on cluster knowed workers the main defect involved horizontal pod autoscaler thrashing when workload utilization reached ninety percent across eight namespace deployments platform engineers triaged ticket jira three two three zero wait scratch that use ticket jira three two three seven instead buy recalculat autoscaling target thresholds you know cluster operators execute cube ctl dash dash grace dash period and dash dash target dash cpu inside slash var slash deploy dot sh across active deployment pods site reliability engineers will calibrat container scaling thresholds buy adjusting pod replica bounds our infrastructure squad will terminat unneeded staging pods four the milestone release sprint engineers right two c p u metrics monitors tracking node utilization",
        "refined_text": "During quarterly roadmap review our platform squad analyzed CPU throttling across 30 microservices on cluster node workers. The main defect involved horizontal pod autoscaler thrashing when workload utilization reached 90 percent across 8 namespace deployments. Platform engineers triaged ticket JIRA-3237 instead by recalculating autoscaling target thresholds.\n\nCluster operators execute kubectl --grace-period and --target-cpu inside /var/deploy.sh across active deployment pods.\n\nSite reliability engineers will calibrate container scaling thresholds by adjusting pod replica bounds. Our infrastructure squad will terminate unneeded staging pods for the milestone release. Sprint engineers write 2 CPU metrics monitors tracking node utilization."
    },
    {
        "raw_asr": "um during morning standup our edge squad addressed packet drops on camera telemetry streams across eight knowed units the primary defect involved d m a buffer allocation failure during continuous packet transmiss over ethernet interfaces developers initially investigated ticket jira four three four zero wait change that to ticket jira four three four six instead buy measuring memory allocat latency you know firmware engineers will configur streaming parameters buy passing dash dash buffer dash size and dash dash ring dash depth inside slash etc slash stream dot conf firmware specialists calibrat ring buffer indexes across hardware channels telemetry engineers track transmiss error rates basically operators will terminat legacy socket streams buy resetting stale client descriptors four the upcoming sprint cycle developers right two r p c latency probes evaluating packet delivery",
        "refined_text": "During morning standup our edge squad addressed packet drops on camera telemetry streams across 8 node units. The primary defect involved DMA buffer allocation failure during continuous packet transmission over Ethernet interfaces. Developers initially investigated ticket JIRA-4346 instead by measuring memory allocation latency.\n\nFirmware engineers will configure streaming parameters by passing --buffer-size and --ring-depth inside /etc/stream.conf. Firmware specialists calibrate ring buffer indexes across hardware channels. Telemetry engineers track transmission error rates.\n\nOperators will terminate legacy socket streams by resetting stale client descriptors for the upcoming sprint cycle. Developers write 2 RPC latency probes evaluating packet delivery."
    },
    {
        "raw_asr": "basically during sprint planning our security and platform squads reviewed service mesh migrat across twenty four microservices on cluster knowed pods the main impediment involved mutual handshake timeouts when client proxy requests collided on routing tables platform engineers initially scoped ticket jira five four five zero wait switch to ticket jira five four five eight instead buy reviewing proxy handshake latency you know site reliability engineers will configur mesh properties buy passing dash dash handshake dash timeout and dash dash retry dash count inside slash app slash mesh dot yaml security specialists will synchronizat proxy certificates with post gres secret tables our team will terminat outdated cipher suites buy updating tls policies four the upcoming release sprint developers right two r p c gateway tests evaluating routing latency",
        "refined_text": "During sprint planning our security and platform squads reviewed service mesh migration across 24 microservices on cluster node pods. The main impediment involved mutual handshake timeouts when client proxy requests collided on routing tables. Platform engineers initially scoped ticket JIRA-5458 instead by reviewing proxy handshake latency.\n\nSite reliability engineers will configure mesh properties by passing --handshake-timeout and --retry-count inside /app/mesh.yaml.\n\nSecurity specialists will synchronize proxy certificates with Postgres secret tables. Our team will terminate outdated cipher suites by updating TLS policies for the upcoming release. Sprint developers write 2 RPC gateway tests evaluating routing latency."
    },
    {
        "raw_asr": "um during morning standup our backend squad triaged memory leaks in background a sink batch workers across eighteen knowed instances the primary trigger involved uncollected task descriptors when continuous batch jobs saturated heap allocation developers initially prioritized ticket jira six five six zero wait scratch that use ticket jira six five six nine instead buy analyzing memory profiling dumps you know site reliability engineers will configur worker limits buy passing dash dash max dash tasks and dash dash memory dash limit inside slash etc slash worker dot conf basically operators will terminat leaking worker processes buy resetting hung worker sessions data engineers will deduplicat batch task payload records our team will synchronizat task state four the upcoming sprint cycle sprint engineers right two c p u metrics monitors tracking worker memory stabilization",
        "refined_text": "During morning standup our backend squad triaged memory leaks in background async batch workers across 18 node instances. The primary trigger involved uncollected task descriptors when continuous batch jobs saturated heap allocation. Developers initially prioritized ticket JIRA-6569 instead by analyzing memory profiling dumps.\n\nSite reliability engineers will configure worker limits by passing --max-tasks and --memory-limit inside /etc/worker.conf.\n\nOperators will terminate leaking worker processes by resetting hung worker sessions. Data engineers will deduplicate batch task payload records. Our team will synchronize task state for the upcoming sprint cycle. Sprint engineers write 2 CPU metrics monitors tracking worker memory stabilization."
    },
    {
        "raw_asr": "basically during quarterly roadmap planning our data infrastructure squad reviewed cache invalidation lag across fourteen knowed instances the main defect involved stale cache reads when post gres read replica synchronizat fell thirty seconds behind primary database transactions developers evaluated roadmap ticket jira seven six seven zero wait change that to ticket jira seven six seven four instead buy recalculat cache expiration intervals you know data engineers will configur caching properties buy passing dash dash sync dash interval and dash dash cache dash ttl inside slash app slash cache dot py site reliability engineers will communicat invalidation events across active consumer threads our squad will synchronizat replication slot offsets buy purging dead transaction logs four the milestone delivery sprint developers right two c p u execution gauges tracking replica lag",
        "refined_text": "During quarterly roadmap planning our data infrastructure squad reviewed cache invalidation lag across 14 node instances. The main defect involved stale cache reads when Postgres read replica synchronization fell 30 seconds behind primary database transactions. Developers evaluated roadmap ticket JIRA-7674 instead by recalculating cache expiration intervals.\n\nData engineers will configure caching properties by passing --sync-interval and --cache-ttl inside /app/cache.py.\n\nSite reliability engineers will communicate invalidation events across active consumer threads. Our squad will synchronize replication slot offsets by purging dead transaction logs for the milestone delivery. Sprint developers write 2 CPU execution gauges tracking replica lag."
    },
    {
        "raw_asr": "um in the sprint retrospective our devops squad investigated pipeline execution timeouts across sixteen runner knowed pods the main impediment involved runner resource starvation when concurrent integration test builds exceeded executor queue capacity developers initially evaluated retrospective ticket jira eight seven eight zero wait switch to ticket jira eight seven eight five instead buy analyzing pipeline retry logs you know devops specialists will configur execution parameters buy passing dash dash retry dash limit and dash dash concurrency inside slash var slash pipeline dot sh quality assurance engineers will arbitrat flaky test quarantine decisions our platform squad will initializ isolated test namespaces buy isolating runner state four the upcoming sprint cycle sprint engineers right two r p c test harness probes evaluating runner duration",
        "refined_text": "In the sprint retrospective our DevOps squad investigated pipeline execution timeouts across 16 runner node pods. The main impediment involved runner resource starvation when concurrent integration test builds exceeded executor queue capacity. Developers initially evaluated retrospective ticket JIRA-8785 instead by analyzing pipeline retry logs.\n\nDevOps specialists will configure execution parameters by passing --retry-limit and --concurrency inside /var/pipeline.sh.\n\nQuality assurance engineers will arbitrate flaky test quarantine decisions. Our platform squad will initialize isolated test namespaces by isolating runner state for the upcoming sprint cycle. Sprint engineers write 2 RPC test harness probes evaluating runner duration."
    },
    {
        "raw_asr": "basically during morning standup our api platform squad triaged request throttling spikes across twelve gateway knowed instances the main defect involved edge token bucket exhaustion when incoming burst traffic exceeded rate limits developers initially triaged ticket jira nine eight nine zero wait scratch that use ticket jira nine eight nine three instead buy measuring edge request rejection rates you know gateway specialists will calibrat token bucket parameters buy passing dash dash rate dash limit and dash dash burst dash size inside slash etc slash gateway dot conf site reliability engineers will recalculat client quota allocations buy adjusting consumer tier bounds our team will terminat rogue scraping connections buy blocking offending source ips four the upcoming sprint cycle sprint engineers right two c p u metrics monitors evaluating request latency",
        "refined_text": "During morning standup our API platform squad triaged request throttling spikes across 12 gateway node instances. The main defect involved edge token bucket exhaustion when incoming burst traffic exceeded rate limits. Developers initially triaged ticket JIRA-9893 instead by measuring edge request rejection rates.\n\nGateway specialists will calibrate token bucket parameters by passing --rate-limit and --burst-size inside /etc/gateway.conf.\n\nSite reliability engineers will recalculate client quota allocations by adjusting consumer tier bounds. Our team will terminate rogue scraping connections by blocking offending source IPs for the upcoming sprint cycle. Sprint engineers write 2 CPU metrics monitors evaluating request latency."
    },
    {
        "raw_asr": "um during sprint planning our data engineering squad estimated delivery milestones four audit event streaming across ten knowed workers the main defect involved duplicate event persistence when network retries caused repeated batch deliveries developers initially estimated ticket jira one zero nine zero wait change that to ticket jira one zero nine eight instead buy reviewing event replay metrics you know data specialists will configur audit streaming options buy passing dash dash flush dash interval and dash dash batch dash limit inside slash app slash audit dot py basically data engineers will deduplicat incoming audit records buy evaluating unique event identifiers our team will synchronizat partition offset commits with post gres audit tables four the release sprint engineers right two r p c health probes evaluating stream commit rates",
        "refined_text": "During sprint planning our data engineering squad estimated delivery milestones for audit event streaming across 10 node workers. The main defect involved duplicate event persistence when network retries caused repeated batch deliveries. Developers initially estimated ticket JIRA-1098 instead by reviewing event replay metrics.\n\nData specialists will configure audit streaming options by passing --flush-interval and --batch-limit inside /app/audit.py.\n\nData engineers will deduplicate incoming audit records by evaluating unique event identifiers. Our team will synchronize partition offset commits with Postgres audit tables for the release. Sprint engineers write 2 RPC health probes evaluating stream commit rates."
    }
]

def main():
    print(f"Total samples: {len(samples)}")
    assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

    # 1. Check leakage against sft_eval.json
    with open("sft_eval.json", "r") as f:
        eval_data = json.load(f)
    eval_refined = {item["refined_text"].strip().lower() for item in eval_data}
    eval_raw = {item["raw_asr"].strip().lower() for item in eval_data}

    for i, s in enumerate(samples):
        ref_norm = s["refined_text"].strip().lower()
        raw_norm = s["raw_asr"].strip().lower()
        if ref_norm in eval_refined:
            print(f"ERROR: Sample {i+1} refined_text leaked into sft_eval.json!")
            sys.exit(1)
        if raw_norm in eval_raw:
            print(f"ERROR: Sample {i+1} raw_asr leaked into sft_eval.json!")
            sys.exit(1)
    print("Leakage check: PASSED (0 overlaps with sft_eval.json)")

    # 2. Validate each pair
    total_layers = 0
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for i, s in enumerate(samples):
        raw = s["raw_asr"]
        ref = s["refined_text"]
        ref_words = len(ref.split())
        raw_words = len(raw.split())

        if ref_words < 25:
            tier_counts["short"] += 1
            min_layers = 3
        elif ref_words < 90:
            tier_counts["medium"] += 1
            min_layers = 4
        else:
            tier_counts["long"] += 1
            min_layers = 4

        val_ok, val_reason = validator.validate_pair(s, min_noise_layers=min_layers)
        if not val_ok:
            print(f"ERROR: Sample {i+1} failed validator: {val_reason}")
            sys.exit(1)

        cln_res, cln_reason = cleaner.clean_sample(raw, ref)
        if cln_reason != "kept":
            print(f"ERROR: Sample {i+1} failed cleaner: {cln_reason}")
            sys.exit(1)

        layers = validator.get_noise_layer_count(raw)
        total_layers += layers
        print(f"Sample {i+1:02d}: Tier={'Short' if ref_words < 25 else 'Medium' if ref_words < 90 else 'Long':6s} | "
              f"Words: ref={ref_words:2d}, raw={raw_words:3d}, ratio={ref_words/raw_words:.2f} | "
              f"Layers: {layers}/6 | Validator: OK | Cleaner: {cln_reason}")

    # 3. Validate batch
    batch_ok, batch_reason, b_tiers = validator.validate_batch(
        samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    if not batch_ok:
        print(f"ERROR: Batch validation failed: {batch_reason}")
        sys.exit(1)

    avg_layers = total_layers / len(samples)
    print("\n=== Validation Summary ===")
    print(f"Batch validation: PASSED ({batch_reason})")
    print(f"Tier distribution: Short={tier_counts['short']}, Medium={tier_counts['medium']}, Long={tier_counts['long']}")
    print(f"Average active noise layers: {avg_layers:.2f} (Required: >= 4.0)")
    print(f"Noise layer distribution: {b_tiers.get('noise_layer_distribution')}")

    # 4. Save to target output file
    out_path = "scratch/subagent_batch_178.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"Successfully written {len(samples)} verified pairs to {out_path}")

if __name__ == "__main__":
    main()
