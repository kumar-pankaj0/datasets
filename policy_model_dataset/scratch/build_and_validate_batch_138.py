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

    # Sample 1: Standup - Allocating story points for async queue worker
    {
        "raw_asr": "um allocat eight story points four the a sink queue worker inside queue underscore manager dot py",
        "refined_text": "Allocate 8 story points for the async queue worker inside queue_manager.py."
    },

    # Sample 2: Standup / Sprint - Recalculating sprint velocity for CPU profiling
    {
        "raw_asr": "uh recalculat sprint capacity buy five story points four the c p u profiling investigation",
        "refined_text": "Recalculate sprint capacity by 5 story points for the CPU profiling investigation."
    },

    # Sample 3: Standup / Roadmap - Migrating ticket JIRA-1042 for Postgres failover drill
    {
        "raw_asr": "basically migrat ticket jira one zero four two four the post gres cluster failover drill across staging knowed hosts",
        "refined_text": "Migrate ticket JIRA-1042 for the Postgres cluster failover drill across staging node hosts."
    },

    # Sample 4: Standup - Configuring retry policies for RPC gateway
    {
        "raw_asr": "um configur three retry policies four the r p c gateway service ticket",
        "refined_text": "Configure 3 retry policies for the RPC gateway service ticket."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Standup - Core Banking Squad gRPC / RPC connection pool blocker
    {
        "raw_asr": "in morning standup our core banking squad investigated connection pool starvation inside connection underscore pool dot py buy tracking connection leaks across thirty worker routines wait switch to ticket jira two one eight four instead um allocat eight story points four implementing r p c circuit breaker timeouts across our payment gateways",
        "refined_text": "In morning standup our core banking squad investigated connection pool starvation inside connection_pool.py by tracking connection leaks across 30 worker routines, switching to ticket JIRA-2184 instead.\n\nAllocate 8 story points for implementing RPC circuit breaker timeouts across our payment gateways."
    },

    # Sample 6: Sprint Planning - Platform Squad capacity and Postgres schema migrations
    {
        "raw_asr": "during sprint planning our platform squad committed forty story points across six backlog items four sprint forty two wait adjust team velocity buy accounting four three engineer vacations instead um configur ticket jira three three zero five covering post gres partition migrations inside schema underscore migrator dot py across twelve tables",
        "refined_text": "During sprint planning our platform squad committed 40 story points across 6 backlog items for sprint 42, adjusting team velocity by accounting for 3 engineer vacations instead.\n\nConfigure ticket JIRA-3305 covering Postgres partition migrations inside schema_migrator.py across 12 tables."
    },

    # Sample 7: Team Roadmap - Observability Squad telemetry roadmap
    {
        "raw_asr": "our quarterly roadmap review established deliverables four telemetry modernization buy transitioning legacy metric daemons towards open telemetry collectors wait scratch that switch to ticket jira four one nine zero instead basically allocat thirteen story points four exporting c p u throttle metrics inside telemetry underscore collector dot py",
        "refined_text": "Our quarterly roadmap review established deliverables for telemetry modernization by transitioning legacy metric daemons towards OpenTelemetry collectors, switching to ticket JIRA-4190 instead.\n\nAllocate 13 story points for exporting CPU throttle metrics inside telemetry_collector.py."
    },

    # Sample 8: Standup - Search & Discovery Squad index rebalancing blocker
    {
        "raw_asr": "in morning standup our search squad addressed index allocation thrashing across eight knowed instances during c p u spikes buy adjusting shard limits inside index underscore coordinator dot py wait no wait assign ticket jira five five one two instead um initializ twenty background recovery workers two restore cluster health",
        "refined_text": "In morning standup our search squad addressed index allocation thrashing across 8 node instances during CPU spikes by adjusting shard limits inside index_coordinator.py, assigning ticket JIRA-5512 instead.\n\nInitialize 20 background recovery workers to restore cluster health."
    },

    # Sample 9: Sprint Planning - Billing Infrastructure Squad webhook retry commitments
    {
        "raw_asr": "during sprint planning our billing squad committed forty five story points across seven user stories four sprint fifty six wait recalculat team velocity buy accounting four two engineer training days instead um allocat eight story points four ticket jira six zero seven one covering a sink invoice webhook retries inside webhook underscore worker dot py across twenty merchant accounts",
        "refined_text": "During sprint planning our billing squad committed 45 story points across 7 user stories for sprint 56, recalculating team velocity by accounting for 2 engineer training days instead.\n\nAllocate 8 story points for ticket JIRA-6071 covering async invoice webhook retries inside webhook_worker.py across 20 merchant accounts."
    },

    # Sample 10: Async Standup / Slack Sync - Security & Identity Squad token validation
    {
        "raw_asr": "posting our async standup update four the identity squad where r p c authentication latency increased buy fifty milliseconds across twenty services wait switch to ticket jira seven four two nine instead um configur local cache invalidation inside auth underscore filter dot py resolving token verification bottlenecks four forty thousand active sessions",
        "refined_text": "Posting our async standup update for the identity squad where RPC authentication latency increased by 50 milliseconds across 20 services, switching to ticket JIRA-7429 instead.\n\nConfigure local cache invalidation inside auth_filter.py, resolving token verification bottlenecks for 40000 active sessions."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2-3 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: Sprint Planning & Team Capacity - Platform Squad sprint 50 planning session
    {
        "raw_asr": "in sprint planning our platform squad evaluated team velocity and established sprint commitments four sprint fifty our historical velocity over the last three sprints averaged fifty four story points but our team agreed two commit forty eight story points accounting four three engineer on call rotations across twenty days we reviewed sprint velocity metrics inside sprint underscore metrics dot json buy identifying five carryover tasks from sprint forty nine where r p c connection timeouts caused delays wait scratch that prioritize ticket jira seven four two nine covering load shedding filters inside proxy underscore handler dot py instead um our squad decomposed the remaining scope of ticket jira seven four two nine into three discrete subtasks estimating eight story points four configur exponential backoff and five story points four exporting telemetry counters into prometheus additionally we groomed ticket eight one four covering automated cube ctl rollout restarts buy allocat five story points four canary health verification scripts our technical lead confirmed that resolving load shedding edge cases unblocks the core banking squad from deploying their payment service our completed backlog contains forty eight story points distributed across eight engineering tickets ready four sprint execution",
        "refined_text": "In sprint planning our platform squad evaluated team velocity and established sprint commitments for sprint 50. Our historical velocity over the last 3 sprints averaged 54 story points, but our team agreed to commit 48 story points accounting for 3 engineer on-call rotations across 20 days. We reviewed sprint velocity metrics inside sprint_metrics.json by identifying 5 carryover tasks from sprint 49 where RPC connection timeouts caused delays, prioritizing ticket JIRA-7429 covering load shedding filters inside proxy_handler.py instead.\n\nOur squad decomposed the remaining scope of ticket JIRA-7429 into 3 discrete subtasks, estimating 8 story points for configuring exponential backoff and 5 story points for exporting telemetry counters into Prometheus. Additionally we groomed ticket 814 covering automated kubectl rollout restarts by allocating 5 story points for canary health verification scripts. Our technical lead confirmed that resolving load shedding edge cases unblocks the core banking squad from deploying their payment service. Our completed backlog contains 48 story points distributed across 8 engineering tickets ready for sprint execution."
    },

    # Sample 12: Daily Standup & Cross-Squad Blocker Triage - Core Banking Squad
    {
        "raw_asr": "in morning standup our core banking squad triaged a critical blocker involving payment settlement delays across four thousand active accounts during yesterday evening batch processing we observed that post gres database replication lag climbed from twelve milliseconds up into four hundred fifty milliseconds under heavy write volumes our database administrator identified unindexed foreign key lookups as the primary driver of c p u saturation on the primary node reaching ninety two percent c p u utilization buy analyzing query plans inside transaction underscore log dot py wait change that focus on ticket jira eight eight three zero covering index creation across payment tables instead um our engineers coordinated cross team dependencies with the site reliability engineering squad two update alert thresholds inside alert underscore rules dot yaml buy allocat five story points four automated index build verification our team agreed that adding concurrent b tree indexes on customer reference columns resolves the replication backlog without interrupting incoming merchant transactions we plan two deploy the migration scripts across our staging environment buy twelve hundred today verifying that replication lag drops below twenty milliseconds before requesting production sign off",
        "refined_text": "In morning standup our core banking squad triaged a critical blocker involving payment settlement delays across 4000 active accounts. During yesterday evening batch processing we observed that Postgres database replication lag climbed from 12 milliseconds up into 450 milliseconds under heavy write volumes. Our database administrator identified unindexed foreign key lookups as the primary driver of CPU saturation on the primary node, reaching 92 percent CPU utilization by analyzing query plans inside transaction_log.py, focusing on ticket JIRA-8830 covering index creation across payment tables instead.\n\nOur engineers coordinated cross-team dependencies with the site reliability engineering squad to update alert thresholds inside alert_rules.yaml by allocating 5 story points for automated index build verification. Our team agreed that adding concurrent B-tree indexes on customer reference columns resolves the replication backlog without interrupting incoming merchant transactions. We plan to deploy the migration scripts across our staging environment by 1200 today, verifying that replication lag drops below 20 milliseconds before requesting production sign off."
    },

    # Sample 13: Quarterly Architecture Roadmap - Data Platform H2 streaming architecture roadmap
    {
        "raw_asr": "in our quarterly architecture roadmap planning session the data platform squad established delivery milestones four transitioning our telemetry pipelines towards a sink event streaming across twelve microservices our current architecture relies on nightly batch jobs that load raw events into post gres tables creating severe storage contention and six hour reporting delays we defined three key roadmap objectives inside roadmap underscore spec dot yaml buy decomposing monolithic ingestion routines into lightweight consumer workers wait switch to ticket jira nine one five four covering kafka partition balancing instead um our engineering lead presented resource allocat plans estimating twenty one story points four building backpressure controls inside event underscore ingest dot py and thirteen story points four implementing schema registry validation across forty event types our squad agreed that maintaining backward compatibility with legacy analytics consumers represents our biggest technical risk we scheduled phased canary rollouts beginning in quarter three buy routing five percent of real time events through the new pipeline our roadmap commitment delivers twenty four story points across four engineering epics ensuring reliable data delivery across eighty production services",
        "refined_text": "In our quarterly architecture roadmap planning session the data platform squad established delivery milestones for transitioning our telemetry pipelines towards async event streaming across 12 microservices. Our current architecture relies on nightly batch jobs that load raw events into Postgres tables, creating severe storage contention and 6 hour reporting delays. We defined 3 key roadmap objectives inside roadmap_spec.yaml by decomposing monolithic ingestion routines into lightweight consumer workers, switching to ticket JIRA-9154 covering Kafka partition balancing instead.\n\nOur engineering lead presented resource allocation plans, estimating 21 story points for building backpressure controls inside event_ingest.py and 13 story points for implementing schema registry validation across 40 event types. Our squad agreed that maintaining backward compatibility with legacy analytics consumers represents our biggest technical risk. We scheduled phased canary rollouts beginning in quarter 3 by routing 5 percent of real-time events through the new pipeline. Our roadmap commitment delivers 24 story points across 4 engineering epics, ensuring reliable data delivery across 80 production services."
    },

    # Sample 14: Sprint Backlog Refinement & Story Decomposition - Search & Discovery Squad
    {
        "raw_asr": "during our backlog refinement session the search and discovery squad groomed ticket jira one two zero five regarding semantic vector document retrieval across four embedding models our current in memory cache struggles during peak traffic periods because concurrent worker routines contend four memory bandwidth driving up query latencies buy seventy milliseconds we analyzed performance bottlenecks inside vector underscore cache dot py buy tracing thread contention across sixty worker pools wait change that focus on ticket jira two three four zero covering tiered cache invalidation instead um our squad decomposed the implementation scope into three distinct engineering tasks estimating eight story points four building an l r u cache eviction policy and five story points four exporting c p u saturation telemetry into prometheus our principal engineer established strict acceptance criteria requiring that cache lookups complete within five milliseconds across ninety nine percent of requests while preventing worker thread starvation we allocat thirteen story points four ticket two three four zero during our sprint planning session providing sufficient capacity four thorough load testing across thirty test partitions",
        "refined_text": "During our backlog refinement session the search and discovery squad groomed ticket JIRA-1205 regarding semantic vector document retrieval across 4 embedding models. Our current in-memory cache struggles during peak traffic periods because concurrent worker routines contend for memory bandwidth, driving up query latencies by 70 milliseconds. We analyzed performance bottlenecks inside vector_cache.py by tracing thread contention across 60 worker pools, focusing on ticket JIRA-2340 covering tiered cache invalidation instead.\n\nOur squad decomposed the implementation scope into 3 distinct engineering tasks, estimating 8 story points for building an LRU cache eviction policy and 5 story points for exporting CPU saturation telemetry into Prometheus. Our principal engineer established strict acceptance criteria requiring that cache lookups complete within 5 milliseconds across 99 percent of requests while preventing worker thread starvation. We allocated 13 story points for ticket 2340 during our sprint planning session, providing sufficient capacity for thorough load testing across 30 test partitions."
    },

    # Sample 15: Daily Standup & Incident Blocker Post-Sync - Reliability Squad
    {
        "raw_asr": "in morning standup the reliability engineering squad addressed staging cluster stability following an overnight network partition that impacted twenty four backend microservices our gateway proxy pods encountered rollout failures when cube ctl restart commands timed out during peak health check reconciliation we investigated connection reset errors inside gateway underscore config dot yaml buy analyzing envoy route listener configurations across forty worker pods wait switch to ticket jira three four five zero covering circuit breaker timeout overrides instead um our engineers identified that stale health check endpoints blocked gateway pods from completing graceful restarts under incoming traffic loads we allocat eight story points four patching ingress health probe intervals and five story points four deploying automated canary rollback routines our team confirmed that updating health check deadlines two ten seconds eliminates connection reset spikes across ninety five percent of synthetic probes unblocking the frontend squad from completing their integration tests before this afternoon release cut",
        "refined_text": "In morning standup the reliability engineering squad addressed staging cluster stability following an overnight network partition that impacted 24 backend microservices. Our gateway proxy pods encountered rollout failures when kubectl restart commands timed out during peak health check reconciliation. We investigated connection reset errors inside gateway_config.yaml by analyzing Envoy route listener configurations across 40 worker pods, switching to ticket JIRA-3450 covering circuit breaker timeout overrides instead.\n\nOur engineers identified that stale health check endpoints blocked gateway pods from completing graceful restarts under incoming traffic loads. We allocate 8 story points for patching ingress health probe intervals and 5 story points for deploying automated canary rollback routines. Our team confirmed that updating health check deadlines to 10 seconds eliminates connection reset spikes across 95 percent of synthetic probes, unblocking the frontend squad from completing their integration tests before this afternoon release cut."
    },

    # Sample 16: Sprint Planning & Tech-Debt Backlog Grooming - Developer Experience Squad
    {
        "raw_asr": "during sprint planning our developer experience squad established sprint goals four sprint thirty eight allocating thirty five percent of our forty story point budget two technical debt remediation across continuous integration pipelines our average build duration increased from twelve minutes up into twenty eight minutes due two redundant dependency re downloads we investigated caching bottlenecks inside build underscore pipeline dot py buy profiling network transfer latencies across sixteen runner hosts wait no wait switch to ticket jira four five eight zero covering artifact cache invalidation instead um our engineers groomed ticket jira four five eight zero into two implementation tasks allocat eight story points four implementing a sink artifact uploads and five story points four deduplicat test reports inside test runner scripts our technical lead highlighted that optimizing cache retention reduces pipeline queue times buy sixty percent across all engineering squads our completed sprint backlog commits thirty eight story points across seven technical debt stories ensuring that continuous integration runners maintain consistent throughput throughout next week release freeze",
        "refined_text": "During sprint planning our developer experience squad established sprint goals for sprint 38, allocating 35 percent of our 40 story point budget to technical debt remediation across continuous integration pipelines. Our average build duration increased from 12 minutes up into 28 minutes due to redundant dependency re-downloads. We investigated caching bottlenecks inside build_pipeline.py by profiling network transfer latencies across 16 runner hosts, switching to ticket JIRA-4580 covering artifact cache invalidation instead.\n\nOur engineers groomed ticket JIRA-4580 into 2 implementation tasks, allocating 8 story points for implementing async artifact uploads and 5 story points for deduplicating test reports inside test runner scripts. Our technical lead highlighted that optimizing cache retention reduces pipeline queue times by 60 percent across all engineering squads. Our completed sprint backlog commits 38 story points across 7 technical debt stories, ensuring that continuous integration runners maintain consistent throughput throughout next week release freeze."
    },

    # Sample 17: Team Roadmap & Multi-Quarter Cloud Migration - Infrastructure Squad
    {
        "raw_asr": "in our quarterly architecture sync the infrastructure squad presented the technical roadmap four transitioning thirty legacy services towards coober netties across four availability zones our current monolithic deployment setup suffers from noisy neighbor interference and uneven c p u utilization during peak traffic bursts we structured our multi quarter delivery milestones inside migration underscore plan dot yaml buy grouping services buy network dependency and database affinity wait scratch that prioritize ticket jira five six two zero covering stateful post gres replication validation instead um our platform engineers allocat twenty one story points four building automated failover verification operators and thirteen story points four configuring pod disruption budgets across twelve stateful clusters our staff engineer emphasized that establishing automated disaster recovery testing mitigates cluster failover risks before migrating tier one transaction processors our engineering roadmap allocates sixty story points across quarter three buy delivering robust infrastructure foundation four eighty production services",
        "refined_text": "In our quarterly architecture sync the infrastructure squad presented the technical roadmap for transitioning 30 legacy services towards Kubernetes across 4 availability zones. Our current monolithic deployment setup suffers from noisy neighbor interference and uneven CPU utilization during peak traffic bursts. We structured our multi-quarter delivery milestones inside migration_plan.yaml by grouping services by network dependency and database affinity, prioritizing ticket JIRA-5620 covering stateful Postgres replication validation instead.\n\nOur platform engineers allocate 21 story points for building automated failover verification operators and 13 story points for configuring pod disruption budgets across 12 stateful clusters. Our staff engineer emphasized that establishing automated disaster recovery testing mitigates cluster failover risks before migrating tier 1 transaction processors. Our engineering roadmap allocates 60 story points across quarter 3 by delivering robust infrastructure foundation for 80 production services."
    },

    # Sample 18: Daily Standup & Release Train Coordination - Mobile Client Squad
    {
        "raw_asr": "in morning standup our mobile engineering squad tracked release train blockers four version four client deployment across two million mobile devices during pre release testing we uncovered an application crash occurring when backend services returned empty json payload arrays our engineers traced the deserialization exception inside client underscore parser dot py buy analyzing stack traces from fifty automated ui regression runs wait change that focus on ticket jira six one eight zero covering defensive payload decoding instead um our mobile engineers collaborated with the r p c gateway team two verify schema contracts buy allocat eight story points four null safety validation and five story points four automated unit tests across twenty client endpoints our engineering manager confirmed that merging defensive parser patches resolves client crashes without degrading payload parsing performance we scheduled end two end canary validation buy fourteen hundred today unblocking the release train four staged production rollout across our user base",
        "refined_text": "In morning standup our mobile engineering squad tracked release train blockers for version 4 client deployment across 2000000 mobile devices. During pre-release testing we uncovered an application crash occurring when backend services returned empty JSON payload arrays. Our engineers traced the deserialization exception inside client_parser.py by analyzing stack traces from 50 automated UI regression runs, focusing on ticket JIRA-6180 covering defensive payload decoding instead.\n\nOur mobile engineers collaborated with the RPC gateway team to verify schema contracts by allocating 8 story points for null safety validation and 5 story points for automated unit tests across 20 client endpoints. Our engineering manager confirmed that merging defensive parser patches resolves client crashes without degrading payload parsing performance. We scheduled end-to-end canary validation by 1400 today, unblocking the release train for staged production rollout across our user base."
    },

    # Sample 19: Sprint Planning & Capacity Rebalancing - Machine Learning Platform Squad
    {
        "raw_asr": "during sprint planning our machine learning platform squad rebalanced sprint commitments four sprint sixty four our historical sprint velocity averages fifty four story points but our squad agreed two commit forty two story points buy accounting four scheduled cluster maintenance across twenty gpu nodes we reviewed carryover tickets from sprint sixty three where worker node preemptions caused training job failures buy analyzing scheduler logs inside scheduler underscore policy dot py wait switch to ticket jira seven two five zero covering preemptible node retry handlers instead um our squad groomed ticket jira seven two five zero into three discrete tasks allocat eight story points four implementing checkpoint validation hooks and five story points four exporting c p u saturation metrics into prometheus we also scoped ticket nine two zero allocating five story points four local artifact caching across forty worker machines our staff engineer confirmed that adding automated retry handling mitigates training run disruptions during spot instance evictions our completed backlog contains forty two story points across eight engineering tasks ready four immediate execution",
        "refined_text": "During sprint planning our machine learning platform squad rebalanced sprint commitments for sprint 64. Our historical sprint velocity averages 54 story points, but our squad agreed to commit 42 story points by accounting for scheduled cluster maintenance across 20 GPU nodes. We reviewed carryover tickets from sprint 63 where worker node preemptions caused training job failures by analyzing scheduler logs inside scheduler_policy.py, switching to ticket JIRA-7250 covering preemptible node retry handlers instead.\n\nOur squad groomed ticket JIRA-7250 into 3 discrete tasks, allocating 8 story points for implementing checkpoint validation hooks and 5 story points for exporting CPU saturation metrics into Prometheus. We also scoped ticket 920, allocating 5 story points for local artifact caching across 40 worker machines. Our staff engineer confirmed that adding automated retry handling mitigates training run disruptions during spot instance evictions. Our completed backlog contains 42 story points across 8 engineering tasks ready for immediate execution."
    },

    # Sample 20: Team Roadmap & Enterprise Security Compliance - Enterprise Identity Squad
    {
        "raw_asr": "in our quarterly engineering sync the enterprise identity squad presented the security hardening roadmap four quarter four across eighty production microservices our current mutual transport layer security architecture relies on manual certificate provisioning that creates renewal delays and compliance audit risks we outlined phased modernization milestones inside security underscore roadmap dot yaml buy automating certificate lifecycle management through vault integration wait scratch that prioritize ticket jira eight four one zero covering automated m t l s rotation policies instead um our security engineers allocat twenty one story points four building an automated cert manager webhook and thirteen story points four implementing a sink revocation verification across thirty api gateways our security architect emphasized that automating certificate rotation mitigates expiration outages before our external security audit in quarter four our engineering roadmap allocates sixty four story points across quarter four buy establishing robust cryptographic boundaries four eighty microservices",
        "refined_text": "In our quarterly engineering sync the enterprise identity squad presented the security hardening roadmap for quarter 4 across 80 production microservices. Our current mutual transport layer security architecture relies on manual certificate provisioning that creates renewal delays and compliance audit risks. We outlined phased modernization milestones inside security_roadmap.yaml by automating certificate lifecycle management through Vault integration, prioritizing ticket JIRA-8410 covering automated mTLS rotation policies instead.\n\nOur security engineers allocate 21 story points for building an automated cert-manager webhook and 13 story points for implementing async revocation verification across 30 API gateways. Our security architect emphasized that automating certificate rotation mitigates expiration outages before our external security audit in quarter 4. Our engineering roadmap allocates 64 story points across quarter 4 by establishing robust cryptographic boundaries for 80 microservices."
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
    out_path = Path("scratch/subagent_batch_138.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS! 20 verified samples saved to {out_path}")
else:
    print("\nFAILURE! Fix reported errors.")
    sys.exit(1)
