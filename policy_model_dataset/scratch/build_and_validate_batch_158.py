import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. 0 newlines. Max 1 cut-word. Noise layers >= 3.
    # =========================================================================

    # Sample 1: Moving Postgres ticket to done on sprint board
    {
        "raw_asr": "um configur the sprint board buy moving the post gres ticket jira two zero four eight two done",
        "refined_text": "Configure the sprint board by moving the Postgres ticket JIRA-2048 to done."
    },

    # Sample 2: Allocating story points for RPC gateway timeout flag
    {
        "raw_asr": "uh allocat three story points buy passing dash dash timeout two the r p c gateway",
        "refined_text": "Allocate 3 story points by passing --timeout to the RPC gateway."
    },

    # Sample 3: Terminating sprint task by deploying v2 deployment with kubectl
    {
        "raw_asr": "um terminat the sprint task buy rolling out deployment dash v two with cube ctl",
        "refined_text": "Terminate the sprint task by rolling out deployment-v2 with kubectl."
    },

    # Sample 4: Communicating CPU roadmap milestone update
    {
        "raw_asr": "basically communicat the c p u roadmap milestone buy updating slash docs slash roadmap dot md four sprint four",
        "refined_text": "Communicate the CPU roadmap milestone by updating /docs/roadmap.md for sprint 4."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 sentences. Natural \n\n breaks. Max \n\n: words // 25. Noise layers >= 4.
    # =========================================================================

    # Sample 5: Standup triage on database migration blocker
    {
        "raw_asr": "um during morning standup our squad triaged the post gres migrat blocker on ticket jira three one zero four buy reviewing the locked index creation wait change that to jira three one zero eight instead basically the dba team agreed two communicat the new migration plan buy passing dash dash skip dash lock four the billing table schema update",
        "refined_text": "During morning standup our squad triaged the Postgres migration blocker on ticket JIRA-3108 instead by reviewing the locked index creation.\n\nThe DBA team agreed to communicate the new migration plan by passing --skip-lock for the billing table schema update."
    },

    # Sample 6: Sprint planning on async telemetry ingestion
    {
        "raw_asr": "uh four sprint planning we sized the a sink telemetry worker backlog buy estimating eight story points four ticket jira four two zero zero wait switch to five story points instead basically we plan two allocat two engineers buy merging the worker loop inside slash services slash worker dot py before Friday",
        "refined_text": "For sprint planning we sized the async telemetry worker backlog by estimating 5 story points for ticket JIRA-4200 instead.\n\nWe plan to allocate 2 engineers by merging the worker loop inside /services/worker.py before Friday."
    },

    # Sample 7: Daily standup on RPC client retry threshold refactoring
    {
        "raw_asr": "basically in today standup we resolved our cross team blocker buy reviewing ticket jira one eight four zero four the auth service r p c timeouts wait change that to ticket jira one eight four five instead um our team will configur client retry thresholds buy passing dash dash max dash retries equals three two the gateway client",
        "refined_text": "In today standup we resolved our cross-team blocker by reviewing ticket JIRA-1845 instead for the auth service RPC timeouts.\n\nOur team will configure client retry thresholds by passing --max-retries=3 to the gateway client."
    },

    # Sample 8: Sprint retrospective on CPU profiling tech debt
    {
        "raw_asr": "um our sprint retrospective identified high c p u throttling across worker nodes buy tracking metrics inside slash var slash log slash audit dot log wait change that to slash audit dot json instead you know our squad will recalculat node capacity buy updating ticket jira five five one zero four forty story points",
        "refined_text": "Our sprint retrospective identified high CPU throttling across worker nodes by tracking metrics inside /var/log/audit.json instead.\n\nOur squad will recalculate node capacity by updating ticket JIRA-5510 for 40 story points."
    },

    # Sample 9: Standup release coordination with kubectl rollout
    {
        "raw_asr": "uh during morning sync we coordinated the staging release buy deploying ticket jira six one two zero with cube ctl wait scratch that deployment failed on cluster alpha so we will switch to cluster beta instead basically we will synchronizat release manifests buy running dash dash dry dash run four verification",
        "refined_text": "During morning sync we coordinated the staging release by deploying ticket JIRA-6120 with kubectl, switching to cluster beta instead after failure on cluster alpha.\n\nWe will synchronize release manifests by running --dry-run for verification."
    },

    # Sample 10: Roadmap planning on Postgres database partition pruning
    {
        "raw_asr": "um four our quarterly roadmap milestone we scheduled ticket jira seven three zero zero buy planning post gres table partitioning across twelve audit tables wait no wait change that to sixteen audit tables instead basically we will terminat legacy table queries buy committing the roadmap file slash docs slash roadmap dot md",
        "refined_text": "For our quarterly roadmap milestone we scheduled ticket JIRA-7300 by planning Postgres table partitioning across 16 audit tables instead of 12 tables.\n\nWe will terminate legacy table queries by committing the roadmap file /docs/roadmap.md."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph with \n\n. Zero numbered checklists. Spoken engineer narration.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: Daily Standup & SRE handoff on Postgres pool starvation blocker
    {
        "raw_asr": "um during our daily standup the platform squad triaged the production database blocker on ticket jira eight one zero zero buy analyzing connection pool starvation across thirty two backend replicas wait change that to forty eight replicas instead basically the primary post gres instance reached max connections because idle client sessions were not terminated buy the gateway pooler uh we agreed two communicat our mitigation plan buy passing dash dash idle dash timeout equals sixty seconds inside slash etc slash pgpool slash pgpool dot conf four immediate deployment we reallocated our sprint capacity buy moving ticket jira eight one zero five into active progress and assigning two senior database engineers buy midday our squad will synchronizat connection monitoring metrics buy tracking pool saturation inside slash monitoring slash pool dot json four the upcoming release train so our remaining sprint velocity forecast remains on track at forty two story points buy Friday",
        "refined_text": "During our daily standup the platform squad triaged the production database blocker on ticket JIRA-8100 by analyzing connection pool starvation across 48 replicas instead of 32 backend replicas. The primary Postgres instance reached max connections because idle client sessions were not terminated by the gateway pooler. We agreed to communicate our mitigation plan by passing --idle-timeout=60 inside /etc/pgpool/pgpool.conf for immediate deployment.\n\nWe reallocated our sprint capacity by moving ticket JIRA-8105 into active progress and assigning 2 senior database engineers by midday. Our squad will synchronize connection monitoring metrics by tracking pool saturation inside /monitoring/pool.json for the upcoming release train, keeping our remaining sprint velocity forecast on track at 42 story points by Friday."
    },

    # Sample 12: Sprint Planning on async worker refactoring and velocity commitments
    {
        "raw_asr": "basically during sprint planning our distributed telemetry squad reviewed historical velocity across the last three sprints where completed output ranged from thirty five story points through forty story points um ticket jira two two nine zero covers optimizing the a sink worker pool buy replacing thread based polling with event loop callbacks inside slash app slash ingestion dot py wait switch to ticket jira two two nine five instead uh we agreed two allocat three backend engineers buy dedicating twenty four story points four the async migration work the remaining sprint capacity will cover tech debt refactoring across our message deduplicat pipeline buy running dash dash benchmark inside our staging environment four seventy two hours our team will communicat daily progress during morning standups buy tracking ticket progress on our board so our committed velocity target of fifty story points remains achievable buy the end of sprint fourteen",
        "refined_text": "During sprint planning our distributed telemetry squad reviewed historical velocity across the last 3 sprints where completed output ranged from 35 story points through 40 story points. Ticket JIRA-2295 covers optimizing the async worker pool by replacing thread-based polling with event loop callbacks inside /app/ingestion.py instead of ticket JIRA-2290. We agreed to allocate 3 backend engineers by dedicating 24 story points for the async migration work.\n\nThe remaining sprint capacity will cover tech-debt refactoring across our message deduplication pipeline by running --benchmark inside our staging environment for 72 hours. Our team will communicate daily progress during morning standups by tracking ticket progress on our board, keeping our committed velocity target of 50 story points achievable by the end of sprint 14."
    },

    # Sample 13: Cross-squad standup on RPC interface migration and keepalive tuning
    {
        "raw_asr": "um in our cross squad standup between payments and core banking we coordinated the r p c interface migration scheduled on ticket jira three four five zero buy reviewing protobuf schema revisions wait change that to ticket jira three four five eight instead uh the payments service was blocked buy connection resets when requesting account balances across thirty two internal endpoints basically we will configur grpc client keepalive probes buy setting dash dash keepalive dash time equals ten seconds inside slash proto slash payment dot proto our squad will terminat deprecated v one endpoints buy the end of sprint twelve freeing up sixteen story points four ledger reconciliation tech debt we agreed two communicat contract updates across squads buy publishing generated bindings into our internal registry so our release milestone remains aligned with the third quarter roadmap commitments buy Friday",
        "refined_text": "In our cross-squad standup between payments and core banking we coordinated the RPC interface migration scheduled on ticket JIRA-3458 instead of ticket JIRA-3450 by reviewing protobuf schema revisions. The payments service was blocked by connection resets when requesting account balances across 32 internal endpoints. We will configure gRPC client keepalive probes by setting --keepalive-time=10 inside /proto/payment.proto.\n\nOur squad will terminate deprecated v1 endpoints by the end of sprint 12, freeing up 16 story points for ledger reconciliation tech debt. We agreed to communicate contract updates across squads by publishing generated bindings into our internal registry, keeping our release milestone aligned with the third quarter roadmap commitments by Friday."
    },

    # Sample 14: Engineering roadmap review on migrating cron jobs to Kubernetes jobs with kubectl
    {
        "raw_asr": "basically during our quarterly roadmap sync the platform reliability team evaluated milestone four which details migrating twelve legacy cron jobs into containerized batch workloads buy issuing cube ctl apply dash f slash deploy slash batch dot yaml wait switch to slash deploy slash jobs dot yaml instead um ticket jira five one zero zero was sized at twenty story points buy our infrastructure engineers four automated job scheduling we encountered an operational blocker buy exhausting pod memory limits during peak billing runs across eight worker nodes so our squad will allocat twelve gigabytes per job container buy passing dash dash requests equals memory eight gigabytes inside our job templates we will synchronizat deploy manifests across both staging and production clusters buy next sprint so the legacy host decommission milestone remains on schedule buy November",
        "refined_text": "During our quarterly roadmap sync the platform reliability team evaluated milestone 4 which details migrating 12 legacy cron jobs into containerized batch workloads by issuing kubectl apply -f /deploy/jobs.yaml instead of /deploy/batch.yaml. Ticket JIRA-5100 was sized at 20 story points by our infrastructure engineers for automated job scheduling.\n\nWe encountered an operational blocker by exhausting pod memory limits during peak billing runs across 8 worker nodes, so our squad will allocate 12 gigabytes per job container by passing --requests=memory8gigabytes inside our job templates. We will synchronize deploy manifests across both staging and production clusters by next sprint, keeping the legacy host decommission milestone on schedule by November."
    },

    # Sample 15: Daily standup on search pod CPU throttling and resource tuning
    {
        "raw_asr": "um in our morning standup the search squad reviewed production alerts regarding excessive c p u throttling across sixteen ingestion pods buy analyzing latency spikes inside slash var slash log slash latency dot json wait change that to slash latency dot log instead basically ticket jira six four two zero was escalated buy our tech lead four immediate mitigation because queries were degrading buy forty percent we plan two communicat with DevOps buy applying resource adjustments with cube ctl patch deployment search dash ingest dash dash patch slash k eight s slash patch dot yaml four the ingest cluster our squad will recalculat container limits from two cores up through four cores buy this afternoon so our sprint velocity remains unimpacted and our roadmap delivery milestone of sixty story points stays intact buy Friday",
        "refined_text": "In our morning standup the search squad reviewed production alerts regarding excessive CPU throttling across 16 ingestion pods by analyzing latency spikes inside /var/log/latency.log instead of latency.json. Ticket JIRA-6420 was escalated by our tech lead for immediate mitigation because queries were degrading by 40 percent.\n\nWe plan to communicate with DevOps by applying resource adjustments with kubectl patch deployment search-ingest --patch /k8s/patch.yaml for the ingest cluster. Our squad will recalculate container limits from 2 cores up through 4 cores by this afternoon, keeping our sprint velocity unimpacted and our roadmap delivery milestone of 60 story points intact by Friday."
    },

    # Sample 16: Sprint retrospective on flaky CI tests and test suite deduplication
    {
        "raw_asr": "basically during our sprint retrospective our testing guild analyzed execution bottlenecks inside our continuous integration pipeline four the post gres backend buy reviewing build run logs wait change that to slash var slash ci slash build dot log instead um ticket jira seven eight one zero was sized at thirty story points buy our qa engineers four flaky test remediation because test runs exceeded forty five minutes across twenty test nodes we will deduplicat redundant integration test suites buy consolidating sixty overlapping test cases inside slash tests slash test underscore suite dot py uh our squad will allocat twelve story points buy passing dash dash shard equals four two our test runner so execution time drops from forty five minutes down through fifteen minutes buy next sprint our velocity will recover buy ten story points four feature work",
        "refined_text": "During our sprint retrospective our testing guild analyzed execution bottlenecks inside our continuous integration pipeline for the Postgres backend by reviewing build run logs inside /var/log/ci/build.log instead. Ticket JIRA-7810 was sized at 30 story points by our QA engineers for flaky test remediation because test runs exceeded 45 minutes across 20 test nodes.\n\nWe will deduplicate redundant integration test suites by consolidating 60 overlapping test cases inside /tests/test_suite.py. Our squad will allocate 12 story points by passing --shard=4 to our test runner so execution time drops from 45 minutes down through 15 minutes, allowing our velocity to recover by 10 story points for feature work by next sprint."
    },

    # Sample 17: Morning standup on billing async worker memory leak
    {
        "raw_asr": "um in our morning standup the billing squad escalated an urgent blocker on ticket jira eight nine zero zero regarding memory exhaustion inside our a sink worker pool wait switch to ticket jira eight nine zero five instead basically thirty two background workers crashed during the monthly invoice run buy consuming six gigabytes per process uh our team will communicat the issue across squads buy opening an incident report inside slash docs slash incidents dot md we will configur queue throttling buy passing dash dash concurrency equals four two the worker process inside slash app slash billing dot py our engineers plan two terminat idle connections buy midday which will prevent memory spikes across seventy five thousand customer accounts our remaining sprint velocity of thirty eight story points remains realistic buy next Tuesday",
        "refined_text": "In our morning standup the billing squad escalated an urgent blocker on ticket JIRA-8905 instead of ticket JIRA-8900 regarding memory exhaustion inside our async worker pool. Thirty-two background workers crashed during the monthly invoice run by consuming 6 gigabytes per process. Our team will communicate the issue across squads by opening an incident report inside /docs/incidents.md.\n\nWe will configure queue throttling by passing --concurrency=4 to the worker process inside /app/billing.py. Our engineers plan to terminate idle connections by midday, preventing memory spikes across 75000 customer accounts, keeping our remaining sprint velocity of 38 story points realistic by next Tuesday."
    },

    # Sample 18: Product and engineering roadmap sync on Postgres partition migration
    {
        "raw_asr": "basically during our roadmap review with product leadership our data platform squad evaluated milestone six which covers migrating our analytics store two post gres partitioned tables wait change that to milestone seven instead um ticket jira nine one five zero defines the table schema partitioning across twelve regional clusters sized at forty story points buy our database architects we encountered a replication lag blocker buy transferring thirty million rows across staging environments four query validation uh our squad will configur batch stream replication buy passing dash dash chunk dash size equals five thousand inside slash opt slash db slash migrate dot py our team will synchronizat partition creation buy the end of sprint sixteen so we maintain our ninety nine percent query latency commitment buy the fourth quarter release",
        "refined_text": "During our roadmap review with product leadership our data platform squad evaluated milestone 7 instead of milestone 6, which covers migrating our analytics store to Postgres partitioned tables. Ticket JIRA-9150 defines the table schema partitioning across 12 regional clusters, sized at 40 story points by our database architects.\n\nWe encountered a replication lag blocker by transferring 30000000 rows across staging environments for query validation. Our squad will configure batch stream replication by passing --chunk-size=5000 inside /opt/db/migrate.py. Our team will synchronize partition creation by the end of sprint 16, maintaining our 99 percent query latency commitment by the fourth quarter release."
    },

    # Sample 19: Architecture standup on RPC cascading timeouts and circuit breaker commitments
    {
        "raw_asr": "um during daily standup our architecture guild reviewed r p c timeout propagation across our edge gateway and inventory services on ticket jira one zero six zero wait scratch that ticket was superseded buy ticket jira one zero six five instead basically upstream client retries caused cascading thread starvation when backend latency surged beyond five hundred milliseconds across twenty endpoints uh our squad agreed two communicat our retry circuit breaking pattern buy documenting slash api slash rpc dot md we will terminat unbounded retry loops buy passing dash dash max dash retries equals two inside the service mesh proxy configuration four sprint eighteen our platform squad will allocat fourteen story points buy delivering the updated client sdk so our service level objective of ninety nine percent uptime remains protected buy the end of the sprint cycle",
        "refined_text": "During daily standup our architecture guild reviewed RPC timeout propagation across our edge gateway and inventory services on ticket JIRA-1065, superseding ticket JIRA-1060. Upstream client retries caused cascading thread starvation when backend latency surged beyond 500 milliseconds across 20 endpoints. Our squad agreed to communicate our retry circuit breaking pattern by documenting /api/rpc.md.\n\nWe will terminate unbounded retry loops by passing --max-retries=2 inside the service mesh proxy configuration for sprint 18. Our platform squad will allocate 14 story points by delivering the updated client SDK, keeping our service level objective of 99 percent uptime protected by the end of the sprint cycle."
    },

    # Sample 20: Sprint planning on edge ingress rate limiting migration and burn-down forecast
    {
        "raw_asr": "basically in our sprint planning session our edge traffic team committed two forty story points four migrating our ingress rate limiting rules onto Envoy filters buy reviewing ticket jira nine four two zero wait switch to ticket jira nine four two five instead um we identified a major cross squad dependency with the security team who must approve policy updates buy Thursday our engineers plan two configur rate limiting filters buy deploying cube ctl apply dash f slash k eight s slash ingress dot yaml across four edge namespaces we will terminat legacy iptables rules buy running dash dash prune on our ingress daemon sets four twenty cluster nodes our team will synchronizat deployment verification buy running end two end smoke tests inside our staging cluster so our burn down forecast predicts completing all forty committed story points buy the end of sprint twenty",
        "refined_text": "In our sprint planning session our edge traffic team committed to 40 story points for migrating our ingress rate limiting rules onto Envoy filters by reviewing ticket JIRA-9425 instead of ticket JIRA-9420. We identified a major cross-squad dependency with the security team who must approve policy updates by Thursday. Our engineers plan to configure rate limiting filters by deploying kubectl apply -f /k8s/ingress.yaml across 4 edge namespaces.\n\nWe will terminate legacy iptables rules by running --prune on our ingress daemon sets for 20 cluster nodes. Our team will synchronize deployment verification by running end-to-end smoke tests inside our staging cluster, predicting our burn-down forecast will complete all 40 committed story points by the end of sprint 20."
    }
]

def main():
    print("=== Validating Batch 158 ===")
    assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []

    for idx, s in enumerate(samples, start=1):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        # Eval leakage check
        if raw.lower().strip() in eval_raws:
            raise ValueError(f"Sample {idx} raw ASR leaked into eval set!")
        if ref.strip() in eval_refs:
            raise ValueError(f"Sample {idx} refined text leaked into eval set!")

        # Cleaner check
        cleaned, status = clean_sample(raw, ref)
        if not cleaned or status != "kept":
            raise ValueError(f"Sample {idx} failed clean_sample: {status}")

        # Pair validator check
        is_valid, reason = validate_pair(s, min_noise_layers=4)
        if not is_valid:
            raise ValueError(f"Sample {idx} failed validate_pair: {reason}")

        # Word count tier
        words = len(ref.split())
        nl = get_noise_layer_count(raw)
        layer_counts.append(nl)

        if words < 25:
            tier = "Short"
            tier_counts["short"] += 1
            if nl < 3:
                raise ValueError(f"Sample {idx} (Short) has {nl} noise layers (< 3)")
        elif words < 90:
            tier = "Medium"
            tier_counts["medium"] += 1
            if nl < 4:
                raise ValueError(f"Sample {idx} (Medium) has {nl} noise layers (< 4)")
        else:
            tier = "Long"
            tier_counts["long"] += 1
            if nl < 4:
                raise ValueError(f"Sample {idx} (Long) has {nl} noise layers (< 4)")

        print(f"Sample {idx:02d} [{tier}]: words={words}, noise_layers={nl} -> PASS")

    # Batch validator check
    b_valid, b_reason, b_stats = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
    if not b_valid:
        raise ValueError(f"Batch validation failed: {b_reason}")

    avg_layers = sum(layer_counts) / len(layer_counts)
    print(f"\nBatch validation summary:")
    print(f"- Total samples: {len(samples)}")
    print(f"- Short (<25w): {tier_counts['short']}")
    print(f"- Medium (25-89w): {tier_counts['medium']}")
    print(f"- Long (90+w): {tier_counts['long']}")
    print(f"- Average noise layers: {avg_layers:.2f}")
    print(f"- Layer distribution: {b_stats.get('noise_layer_distribution')}")

    assert tier_counts["short"] == 4, f"Expected 4 short, got {tier_counts['short']}"
    assert tier_counts["medium"] == 6, f"Expected 6 medium, got {tier_counts['medium']}"
    assert tier_counts["long"] == 10, f"Expected 10 long, got {tier_counts['long']}"
    assert avg_layers >= 4.0, f"Expected avg noise layers >= 4.0, got {avg_layers}"

    output_path = Path("scratch/subagent_batch_158.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote 20 verified samples to {output_path}")

if __name__ == "__main__":
    main()
