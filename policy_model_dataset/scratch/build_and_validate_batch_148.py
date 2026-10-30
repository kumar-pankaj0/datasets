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
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Content words >= 6-8.
    # =========================================================================

    # Sample 1: Standup - Allocating story points for GraphQL Apollo schema stitching
    {
        "raw_asr": "um allocat six story points four the a sink schema stitching worker inside federation underscore gateway dot py",
        "refined_text": "Allocate 6 story points for the async schema stitching worker inside federation_gateway.py."
    },

    # Sample 2: Standup / Sprint - Recalculating sprint velocity for ClickHouse CPU profiling
    {
        "raw_asr": "uh recalculat sprint capacity buy seven story points four the c p u profiling investigation inside rollup underscore aggregator dot py",
        "refined_text": "Recalculate sprint capacity by 7 story points for the CPU profiling investigation inside rollup_aggregator.py."
    },

    # Sample 3: Standup / Blocker - Migrating ticket JIRA-3840 for Postgres shard failover
    {
        "raw_asr": "basically migrat ticket jira three eight four zero four the post gres shard failover verification across staging knowed hosts",
        "refined_text": "Migrate ticket JIRA-3840 for the Postgres shard failover verification across staging node hosts."
    },

    # Sample 4: Standup - Configuring retry policies for WebSocket RPC broker
    {
        "raw_asr": "um configur five retry policies four the r p c message broker inside socket underscore broker dot py",
        "refined_text": "Configure 5 retry policies for the RPC message broker inside socket_broker.py."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Standup - Real-time WebSockets Squad connection pooling & RPC keepalive
    {
        "raw_asr": "in morning standup our messaging squad triaged web socket drop storms across twenty worker routines buy inspecting connection underscore manager dot py wait switch to ticket jira two eight five zero instead um allocat five story points four implementing r p c keepalive timeouts across eight gateway instances",
        "refined_text": "In morning standup our messaging squad triaged WebSocket drop storms across 20 worker routines by inspecting connection_manager.py, switching to ticket JIRA-2850 instead.\n\nAllocate 5 story points for implementing RPC keepalive timeouts across 8 gateway instances."
    },

    # Sample 6: Sprint Planning - Database Reliability Squad Postgres autovacuum limits
    {
        "raw_asr": "during sprint planning our database reliability squad committed thirty six story points across five backlog items four sprint forty eight wait adjust team velocity buy accounting four two engineer conference days instead um configur ticket jira three five six zero covering post gres autovacuum limits inside vacuum underscore monitor dot py across sixteen tables",
        "refined_text": "During sprint planning our database reliability squad committed 36 story points across 5 backlog items for sprint 48, adjusting team velocity by accounting for 2 engineer conference days instead.\n\nConfigure ticket JIRA-3560 covering Postgres autovacuum limits inside vacuum_monitor.py across 16 tables."
    },

    # Sample 7: Team Roadmap - Telemetry Pipeline Squad distributed tracing & CPU exporter
    {
        "raw_asr": "our quarterly roadmap sync scheduled milestones four distributed tracing modernization buy replacing legacy statsd agents with open telemetry collectors wait scratch that switch to ticket jira seven one nine zero instead basically allocat eight story points four exporting c p u saturation metrics inside collector underscore pipeline dot yaml",
        "refined_text": "Our quarterly roadmap sync scheduled milestones for distributed tracing modernization by replacing legacy StatsD agents with OpenTelemetry collectors, switching to ticket JIRA-7190 instead.\n\nAllocate 8 story points for exporting CPU saturation metrics inside collector_pipeline.yaml."
    },

    # Sample 8: Standup - Search Infrastructure Squad Lucene segment merge CPU spikes
    {
        "raw_asr": "in morning standup our search infrastructure squad investigated segment merge thrashing across six knowed instances during c p u saturation bursts buy tuning merge thresholds inside segment underscore merger dot py wait no wait assign ticket jira four nine three zero instead um initializ ten background index workers two restore query throughput",
        "refined_text": "In morning standup our search infrastructure squad investigated segment merge thrashing across 6 node instances during CPU saturation bursts by tuning merge thresholds inside segment_merger.py, assigning ticket JIRA-4930 instead.\n\nInitialize 10 background index workers to restore query throughput."
    },

    # Sample 9: Sprint Planning - Notification Delivery Squad async push token sync
    {
        "raw_asr": "during sprint planning our notification squad committed thirty eight story points across six backlog items four sprint fifty six wait adjust team velocity buy accounting four two engineer training sessions instead um allocat eight story points four ticket jira five four one zero covering a sink push token sync inside push underscore dispatcher dot py across fourteen regional clusters",
        "refined_text": "During sprint planning our notification squad committed 38 story points across 6 backlog items for sprint 56, adjusting team velocity by accounting for 2 engineer training sessions instead.\n\nAllocate 8 story points for ticket JIRA-5410 covering async push token sync inside push_dispatcher.py across 14 regional clusters."
    },

    # Sample 10: Async Standup - Identity & SSO Squad Okta SAML assertion cache
    {
        "raw_asr": "in our async standup update the identity squad reported saml assertion validation latency spikes buy thirty milliseconds across twelve services wait switch to ticket jira eight two three zero instead um configur local token cache eviction inside token underscore validator dot py resolving r p c auth verification bottlenecks four twenty thousand active sessions",
        "refined_text": "In our async standup update the identity squad reported SAML assertion validation latency spikes by 30 milliseconds across 12 services, switching to ticket JIRA-8230 instead.\n\nConfigure local token cache eviction inside token_validator.py, resolving RPC auth verification bottlenecks for 20000 active sessions."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: Sprint Planning & Team Capacity - MinIO / Ceph Distributed Storage Squad
    {
        "raw_asr": "in sprint planning our object storage squad reviewed team velocity and finalized sprint commitments four sprint fifty four our rolling velocity over the preceding three sprints averaged forty eight story points but our squad agreed two commit forty two story points buy accounting four two engineer on call rotations across fourteen days we audited sprint velocity metrics inside storage underscore metrics dot json buy identifying three carryover tasks from sprint fifty three where post gres metadata synchronization lag caused pipeline delays wait scratch that prioritize ticket jira five one eight zero covering s three bucket notification throttling inside bucket underscore notifier dot py instead um our engineers decomposed the remaining implementation scope of ticket jira five one eight zero into three concrete tasks estimating eight story points four configur backpressure queues and five story points four exporting telemetry counters into prometheus additionally our squad groomed ticket four one zero covering automated cube ctl stateful restart hooks buy allocat five story points four health probe validation scripts our principal engineer confirmed that resolving bucket notification backpressure unblocks the data ingestion squad from running daily export pipelines our final sprint backlog commits forty two story points across seven engineering tickets ready four sprint execution",
        "refined_text": "In sprint planning our object storage squad reviewed team velocity and finalized sprint commitments for sprint 54. Our rolling velocity over the preceding 3 sprints averaged 48 story points, but our squad agreed to commit 42 story points by accounting for 2 engineer on-call rotations across 14 days. We audited sprint velocity metrics inside storage_metrics.json by identifying 3 carryover tasks from sprint 53 where Postgres metadata synchronization lag caused pipeline delays, prioritizing ticket JIRA-5180 covering S3 bucket notification throttling inside bucket_notifier.py instead.\n\nOur engineers decomposed the remaining implementation scope of ticket JIRA-5180 into 3 concrete tasks, estimating 8 story points for configuring backpressure queues and 5 story points for exporting telemetry counters into Prometheus. Additionally our squad groomed ticket 410 covering automated kubectl stateful restart hooks by allocating 5 story points for health probe validation scripts. Our principal engineer confirmed that resolving bucket notification backpressure unblocks the data ingestion squad from running daily export pipelines. Our final sprint backlog commits 42 story points across 7 engineering tickets ready for sprint execution."
    },

    # Sample 12: Daily Standup & Cross-Squad Blocker Triage - High-Frequency Settlement Squad
    {
        "raw_asr": "in morning standup our settlement platform squad triaged an operational blocker involving clearing execution delays across eight thousand active merchant accounts during yesterday evening batch clearing runs we observed that post gres database replication lag climbed from ten milliseconds up into four hundred eighty milliseconds under peak insert volumes our database administrator identified unindexed foreign key lookups on settlement logs as the primary driver of c p u saturation on the primary database reaching ninety three percent c p u utilization buy examining query execution plans inside settlement underscore ledger dot py wait change that focus on ticket jira six four seven zero covering concurrent b tree index creation across settlement tables instead um our engineers coordinated cross team dependencies with the infrastructure operations squad two revise replication lag alert thresholds inside alert underscore configs dot yaml buy allocat five story points four automated index build verification our team agreed that deploying concurrent indexes on merchant transaction identifiers resolves the replication delay without interrupting incoming payment flows we plan two execute the migration scripts across our staging environment buy eleven hundred today verifying that replication lag drops below fifteen milliseconds before requesting production change approval",
        "refined_text": "In morning standup our settlement platform squad triaged an operational blocker involving clearing execution delays across 8000 active merchant accounts. During yesterday evening batch clearing runs we observed that Postgres database replication lag climbed from 10 milliseconds up into 480 milliseconds under peak insert volumes. Our database administrator identified unindexed foreign key lookups on settlement logs as the primary driver of CPU saturation on the primary database, reaching 93 percent CPU utilization by examining query execution plans inside settlement_ledger.py, focusing on ticket JIRA-6470 covering concurrent B-tree index creation across settlement tables instead.\n\nOur engineers coordinated cross-team dependencies with the infrastructure operations squad to revise replication lag alert thresholds inside alert_configs.yaml by allocating 5 story points for automated index build verification. Our team agreed that deploying concurrent indexes on merchant transaction identifiers resolves the replication delay without interrupting incoming payment flows. We plan to execute the migration scripts across our staging environment by 1100 today, verifying that replication lag drops below 15 milliseconds before requesting production change approval."
    },

    # Sample 13: Quarterly Architecture Roadmap - ClickHouse Real-time Analytics Squad
    {
        "raw_asr": "in our quarterly architecture roadmap planning session the analytics platform squad established technical milestones four transitioning our reporting infrastructure towards a sink event streaming across sixteen microservices our existing architecture relies on nightly cron batch jobs that dump raw event tables into post gres creating severe disk contention and seven hour reporting lag we established three strategic roadmap goals inside roadmap underscore initiatives dot yaml buy replacing monolithic batch exports with continuous streaming consumer workers wait switch to ticket jira seven five eight zero covering clickhouse partition balancing instead um our principal architect outlined resource allocat schedules estimating twenty one story points four building backpressure controls inside event underscore streamer dot py and thirteen story points four implementing schema registry validation across forty five event streams our squad agreed that maintaining backward compatibility with legacy business intelligence dashboards represents our biggest delivery risk we scheduled phased canary testing beginning in quarter three buy routing six percent of production telemetry through the new streaming pipeline our committed roadmap delivers thirty story points across five engineering epics providing resilient data pipelines four ninety production services",
        "refined_text": "In our quarterly architecture roadmap planning session the analytics platform squad established technical milestones for transitioning our reporting infrastructure towards async event streaming across 16 microservices. Our existing architecture relies on nightly cron batch jobs that dump raw event tables into Postgres, creating severe disk contention and 7 hour reporting lag. We established 3 strategic roadmap goals inside roadmap_initiatives.yaml by replacing monolithic batch exports with continuous streaming consumer workers, switching to ticket JIRA-7580 covering ClickHouse partition balancing instead.\n\nOur principal architect outlined resource allocation schedules, estimating 21 story points for building backpressure controls inside event_streamer.py and 13 story points for implementing schema registry validation across 45 event streams. Our squad agreed that maintaining backward compatibility with legacy business intelligence dashboards represents our biggest delivery risk. We scheduled phased canary testing beginning in quarter 3 by routing 6 percent of production telemetry through the new streaming pipeline. Our committed roadmap delivers 30 story points across 5 engineering epics, providing resilient data pipelines for 90 production services."
    },

    # Sample 14: Sprint Backlog Refinement & Story Decomposition - Vector Search Platform Squad
    {
        "raw_asr": "during our backlog refinement session the vector search squad groomed ticket jira two one six zero regarding approximate nearest neighbor index caching across eight embedding spaces our current in memory cache struggles during query surges because concurrent worker routines contend four memory bandwidth driving up p ninety nine retrieval latency buy sixty five milliseconds we analyzed thread contention bottlenecks inside vector underscore search dot py buy profiling thread locks across forty worker pools wait change that focus on ticket jira three four eight zero covering tiered cache invalidation instead um our squad decomposed the feature scope into three discrete engineering tasks estimating eight story points four building an l r u eviction policy and five story points four exporting c p u saturation telemetry into prometheus our lead engineer set strict acceptance criteria requiring that cache hits return within four milliseconds across ninety nine percent of queries while preventing worker routine starvation we allocat thirteen story points four ticket three four eight zero during our sprint planning session providing ample capacity four load verification across twenty four test shards",
        "refined_text": "During our backlog refinement session the vector search squad groomed ticket JIRA-2160 regarding approximate nearest neighbor index caching across 8 embedding spaces. Our current in-memory cache struggles during query surges because concurrent worker routines contend for memory bandwidth, driving up P99 retrieval latency by 65 milliseconds. We analyzed thread contention bottlenecks inside vector_search.py by profiling thread locks across 40 worker pools, focusing on ticket JIRA-3480 covering tiered cache invalidation instead.\n\nOur squad decomposed the feature scope into 3 discrete engineering tasks, estimating 8 story points for building an LRU eviction policy and 5 story points for exporting CPU saturation telemetry into Prometheus. Our lead engineer set strict acceptance criteria requiring that cache hits return within 4 milliseconds across 99 percent of queries while preventing worker routine starvation. We allocated 13 story points for ticket 3480 during our sprint planning session, providing ample capacity for load verification across 24 test shards."
    },

    # Sample 15: Daily Standup & Incident Blocker Post-Sync - Edge Envoy Proxy Squad
    {
        "raw_asr": "in morning standup the edge gateway squad addressed staging cluster stability following an overnight route reconfiguration that impacted twenty eight backend services our envoy proxy instances encountered deployment stalls when cube ctl restart commands timed out during dynamic route filter reconciliation we investigated connection reset errors inside envoy underscore gateway dot yaml buy inspecting route filter chains across forty four worker pods wait switch to ticket jira four eight five zero covering circuit breaker timeout overrides instead um our engineers discovered that stale health check endpoints blocked proxy pods from completing graceful restarts under incoming traffic loads we allocat eight story points four updating upstream health check intervals and five story points four implementing automated rollback verification our team confirmed that extending probe timeout thresholds two ten seconds eliminates connection drop spikes across ninety four percent of synthetic tests unblocking the mobile client squad from validating their staging builds before this afternoon deployment cut",
        "refined_text": "In morning standup the edge gateway squad addressed staging cluster stability following an overnight route reconfiguration that impacted 28 backend services. Our Envoy proxy instances encountered deployment stalls when kubectl restart commands timed out during dynamic route filter reconciliation. We investigated connection reset errors inside envoy_gateway.yaml by inspecting route filter chains across 44 worker pods, switching to ticket JIRA-4850 covering circuit breaker timeout overrides instead.\n\nOur engineers discovered that stale health check endpoints blocked proxy pods from completing graceful restarts under incoming traffic loads. We allocate 8 story points for updating upstream health check intervals and 5 story points for implementing automated rollback verification. Our team confirmed that extending probe timeout thresholds to 10 seconds eliminates connection drop spikes across 94 percent of synthetic tests, unblocking the mobile client squad from validating their staging builds before this afternoon deployment cut."
    },

    # Sample 16: Sprint Planning & Tech-Debt Backlog Grooming - Developer Experience Squad
    {
        "raw_asr": "during sprint planning our developer experience squad established sprint deliverables four sprint forty six dedicating thirty percent of our forty two story point budget two continuous integration build optimizations our average pipeline execution duration increased from nine minutes up into twenty four minutes due two duplicate toolchain downloads across pipeline stages we investigated cache eviction patterns inside bazel underscore builder dot py buy analyzing network latency traces across eighteen runner nodes wait no wait switch to ticket jira five nine two zero covering remote artifact cache retention instead um our engineers scoped ticket jira five nine two zero into two implementation tasks allocat eight story points four building a sink artifact upload workers and five story points four deduplicat test output logs inside test runner scripts our staff engineer noted that optimizing remote cache hit rates decreases pipeline queue wait times buy fifty percent across all development squads our completed sprint plan commits forty story points across six technical debt stories ensuring that build runners maintain high throughput throughout next week release freeze",
        "refined_text": "During sprint planning our developer experience squad established sprint deliverables for sprint 46, dedicating 30 percent of our 42 story point budget to continuous integration build optimizations. Our average pipeline execution duration increased from 9 minutes up into 24 minutes due to duplicate toolchain downloads across pipeline stages. We investigated cache eviction patterns inside bazel_builder.py by analyzing network latency traces across 18 runner nodes, switching to ticket JIRA-5920 covering remote artifact cache retention instead.\n\nOur engineers scoped ticket JIRA-5920 into 2 implementation tasks, allocating 8 story points for building async artifact upload workers and 5 story points for deduplicating test output logs inside test runner scripts. Our staff engineer noted that optimizing remote cache hit rates decreases pipeline queue wait times by 50 percent across all development squads. Our completed sprint plan commits 40 story points across 6 technical debt stories, ensuring that build runners maintain high throughput throughout next week release freeze."
    },

    # Sample 17: Team Roadmap & Multi-Quarter Cloud Migration - Platform Infrastructure Squad
    {
        "raw_asr": "in our quarterly architecture roadmap sync the platform infrastructure squad outlined the technical roadmap four migrating thirty four stateful services towards coober netties across four availability regions our existing virtual machine deployment topology exhibits noisy neighbor interference and volatile c p u utilization during daily traffic peaks we organized our delivery schedule inside infrastructure underscore roadmap dot yaml buy grouping services buy storage dependency and database replication topology wait scratch that prioritize ticket jira six eight one zero covering stateful post gres operator automated failover instead um our platform engineers allocat twenty one story points four implementing automated failover verification routines and thirteen story points four standardizing pod disruption budgets across sixteen database clusters our staff architect highlighted that automating database failover drills minimizes operational risk before migrating tier one transaction databases our infrastructure roadmap allocates fifty eight story points across quarter three buy delivering solid foundational platforms four seventy five production services",
        "refined_text": "In our quarterly architecture roadmap sync the platform infrastructure squad outlined the technical roadmap for migrating 34 stateful services towards Kubernetes across 4 availability regions. Our existing virtual machine deployment topology exhibits noisy neighbor interference and volatile CPU utilization during daily traffic peaks. We organized our delivery schedule inside infrastructure_roadmap.yaml by grouping services by storage dependency and database replication topology, prioritizing ticket JIRA-6810 covering stateful Postgres operator automated failover instead.\n\nOur platform engineers allocate 21 story points for implementing automated failover verification routines and 13 story points for standardizing pod disruption budgets across 16 database clusters. Our staff architect highlighted that automating database failover drills minimizes operational risk before migrating tier 1 transaction databases. Our infrastructure roadmap allocates 58 story points across quarter 3 by delivering solid foundational platforms for 75 production services."
    },

    # Sample 18: Daily Standup & Release Train Coordination - Mobile Core Architecture Squad
    {
        "raw_asr": "in morning standup our mobile core engineering squad tracked release train blockers four version six mobile client rollout across four million active devices during pre release smoke testing we identified an application launch crash occurring whenever backend responses omitted mandatory schema fields our engineers isolated the parsing fault inside payload underscore parser dot py buy reviewing crash stack traces from seventy automated device lab runs wait change that focus on ticket jira seven seven two zero covering defensive payload parsing instead um our mobile architects partnered with the r p c gateway team two validate response schemas buy allocat eight story points four null check guards and five story points four automated unit tests across twenty two client endpoints our technical director confirmed that shipping defensive schema validation prevents startup crashes without adding serialization latency we scheduled end two end verification runs buy fifteen hundred today unblocking the mobile release train four staged production rollout across our user base",
        "refined_text": "In morning standup our mobile core engineering squad tracked release train blockers for version 6 mobile client rollout across 4000000 active devices. During pre-release smoke testing we identified an application launch crash occurring whenever backend responses omitted mandatory schema fields. Our engineers isolated the parsing fault inside payload_parser.py by reviewing crash stack traces from 70 automated device lab runs, focusing on ticket JIRA-7720 covering defensive payload parsing instead.\n\nOur mobile architects partnered with the RPC gateway team to validate response schemas by allocating 8 story points for null check guards and 5 story points for automated unit tests across 22 client endpoints. Our technical director confirmed that shipping defensive schema validation prevents startup crashes without adding serialization latency. We scheduled end-to-end verification runs by 1500 today, unblocking the mobile release train for staged production rollout across our user base."
    },

    # Sample 19: Sprint Planning & Capacity Rebalancing - ML Training Infrastructure Squad
    {
        "raw_asr": "during sprint planning our distributed training squad adjusted sprint commitments four sprint sixty eight our historical velocity over previous sprints averaged fifty story points but our squad agreed two commit thirty eight story points buy factoring in scheduled compute cluster maintenance across twenty eight gpu worker nodes we reviewed incomplete tickets from sprint sixty seven where spot instance preemptions caused distributed model training checkpoint failures buy analyzing scheduler log files inside training underscore scheduler dot py wait switch to ticket jira eight five four zero covering automated checkpoint retry operators instead um our engineers groomed ticket jira eight five four zero into three implementation tasks allocat eight story points four implementing checkpoint validation hooks and five story points four exporting c p u saturation metrics into prometheus we also groomed ticket eight six zero allocating five story points four distributed model weight caching across thirty six worker instances our principal engineer confirmed that adding automated checkpoint recovery shields large model training runs from node evictions our finalized sprint backlog commits thirty eight story points across seven engineering tasks ready four active execution",
        "refined_text": "During sprint planning our distributed training squad adjusted sprint commitments for sprint 68. Our historical velocity over previous sprints averaged 50 story points, but our squad agreed to commit 38 story points by factoring in scheduled compute cluster maintenance across 28 GPU worker nodes. We reviewed incomplete tickets from sprint 67 where spot instance preemptions caused distributed model training checkpoint failures by analyzing scheduler log files inside training_scheduler.py, switching to ticket JIRA-8540 covering automated checkpoint retry operators instead.\n\nOur squad groomed ticket JIRA-8540 into 3 implementation tasks, allocating 8 story points for implementing checkpoint validation hooks and 5 story points for exporting CPU saturation metrics into Prometheus. We also groomed ticket 860, allocating 5 story points for distributed model weight caching across 36 worker instances. Our principal engineer confirmed that adding automated checkpoint recovery shields large model training runs from node evictions. Our finalized sprint backlog commits 38 story points across 7 engineering tasks ready for active execution."
    },

    # Sample 20: Team Roadmap & Zero Trust Network Compliance - Zero Trust Security Squad
    {
        "raw_asr": "in our quarterly engineering sync the zero trust security squad presented the network hardening roadmap four quarter four across ninety production microservices our existing service authentication model relies on static pre shared keys that create secret leakage vulnerabilities and compliance audit findings we outlined structured delivery milestones inside mesh underscore roadmap dot yaml buy automating certificate lifecycle management using hashicorp vault wait scratch that prioritize ticket jira nine three two zero covering automated m t l s rotation policies instead um our platform security engineers allocat twenty one story points four building an automated cert manager controller and thirteen story points four implementing a sink revocation verification across thirty six ingress gateways our chief information security officer emphasized that automating cryptographic rotations eliminates certificate expiration outages before our compliance assessment in quarter four our security roadmap allocates sixty two story points across quarter four buy establishing authenticated service perimeters four ninety production microservices",
        "refined_text": "In our quarterly engineering sync the zero trust security squad presented the network hardening roadmap for quarter 4 across 90 production microservices. Our existing service authentication model relies on static pre-shared keys that create secret leakage vulnerabilities and compliance audit findings. We outlined structured delivery milestones inside mesh_roadmap.yaml by automating certificate lifecycle management using HashiCorp Vault, prioritizing ticket JIRA-9320 covering automated mTLS rotation policies instead.\n\nOur platform security engineers allocate 21 story points for building an automated cert-manager controller and 13 story points for implementing async revocation verification across 36 ingress gateways. Our chief information security officer emphasized that automating cryptographic rotations eliminates certificate expiration outages before our compliance assessment in quarter 4. Our security roadmap allocates 62 story points across quarter 4 by delivering authenticated service perimeters for 90 production microservices."
    }
]

print(f"Total samples defined: {len(samples)}")

# Validation checks
all_passed = True
tier_counts = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, p in enumerate(samples, 1):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # 1. Leakage check
    if raw.lower() in eval_raws:
        print(f"ERROR: Sample {idx} raw leaked into eval set!")
        all_passed = False
    if ref in eval_refs:
        print(f"ERROR: Sample {idx} ref leaked into eval set!")
        all_passed = False

    # 2. validate_pair with min_noise_layers=4
    v_ok, v_msg = validate_pair(p, min_noise_layers=4)
    if not v_ok:
        print(f"ERROR: Sample {idx} failed validate_pair: {v_msg}")
        all_passed = False

    # 3. clean_sample
    c_res, c_msg = clean_sample(raw, ref)
    if c_msg != "kept":
        print(f"ERROR: Sample {idx} failed clean_sample: {c_msg}")
        all_passed = False

    # Metrics
    words = len(ref.split())
    if words < 25:
        tier = "short"
    elif words < 90:
        tier = "medium"
    else:
        tier = "long"
    tier_counts[tier] += 1

    layers_cnt = get_noise_layer_count(raw)
    layer_counts.append(layers_cnt)
    breaks = ref.count("\n\n")

    print(f"Sample {idx:02d} [{tier.upper():6s}]: words={words:3d}, breaks={breaks}, layers={layers_cnt} | Val: {v_msg} | Clean: {c_msg}")

avg_noise_layers = round(sum(layer_counts) / len(layer_counts), 2)
print("\n--- Validation Summary ---")
print(f"Tier counts: {tier_counts}")
print(f"Average noise layers: {avg_noise_layers}")
print(f"Noise layer distribution: {[layer_counts.count(i) for i in range(7)]}")

# Batch validation
b_ok, b_msg, b_stats = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print(f"Batch validation: {b_ok} ({b_msg})")
if not b_ok:
    all_passed = False

if all_passed:
    out_path = Path("scratch/subagent_batch_148.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS! 20 verified samples saved to {out_path}")
else:
    print("\nFAILURE! Fix reported errors.")
    sys.exit(1)
