import json
import re
import sys
from pathlib import Path

# Add code directory to path
sys.path.append("code")
import validator
import cleaner

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch_70 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Sample 1: Database connection timeout adjustment
    {
        "raw_asr": "um configur the database connection timeout buy setting twelve seconds on worker knowed three",
        "refined_text": "Configure the database connection timeout by setting 12 seconds on worker node 3."
    },
    # Sample 2: Redis cache cluster replica failover promotion
    {
        "raw_asr": "uh promot the read only cache replica buy triggering failover on cluster instance forty eight",
        "refined_text": "Promote the read-only cache replica by triggering failover on cluster instance 48."
    },
    # Sample 3: Ingress traffic rate limiting worker thread allocation
    {
        "raw_asr": "basically allocat sixteen worker threads four processing inbound api requests during peak traffic",
        "refined_text": "Allocate 16 worker threads for processing inbound API requests during peak traffic."
    },
    # Sample 4: Kafka consumer group partition lag commit
    {
        "raw_asr": "terminat stalled consumer channel seven buy resetting partition offset twenty four on broker two",
        "refined_text": "Terminate stalled consumer channel 7 by resetting partition offset 24 on broker 2."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # Sample 5: HAProxy load balancer 504 gateway timeout and upstream keepalive pool exhaustion
    {
        "raw_asr": "our h a proxy load balancer dropped incoming checkout requests during an upstream saturation incident where the p ninety nine response time spiked two sixteen seconds wait set upstream timeout two thirty seconds instead four degraded payment gateways as the load balancer reestablished upstream sessions buy opening sixty four persistent keepalive connections",
        "refined_text": "Our HAProxy load balancer dropped incoming checkout requests during an upstream saturation incident where the P99 response time spiked to 16 seconds.\n\nSet upstream timeout to 30 seconds instead for degraded payment gateways, as the load balancer reestablished upstream sessions by opening 64 persistent keepalive connections."
    },
    # Sample 6: PostgreSQL connection pool starvation and deadlock aborts
    {
        "raw_asr": "our post gres primary database rejected transaction queries after connection pool exhaust on worker knowed four we checked active sessions where twenty four client threads blocked on table locks so increase pool size into ninety six connections instead four backend workers as the database orchestrat cleared blocked sessions buy terminating five idle backend transactions",
        "refined_text": "Our Postgres primary database rejected transaction queries after connection pool exhaustion on worker node 4.\n\nWe checked active sessions where 24 client threads blocked on table locks, so increase pool size into 96 connections instead for backend workers as the database orchestrator cleared blocked sessions by terminating 5 idle backend transactions."
    },
    # Sample 7: Kafka partition consumer lag and consumer group rebalance storm
    {
        "raw_asr": "uh kafka ingestion topic telemetry suffered consumer lag across partition eight during peak streaming traffic we examined broker consumer group metrics where partition lag exceeded twelve thousand messages so assign consumer partition balance into four workers instead four parallel consumption as the stream processor resumed message processing buy committing offset forty eight across partition eight",
        "refined_text": "Kafka ingestion topic telemetry suffered consumer lag across partition 8 during peak streaming traffic.\n\nWe examined broker consumer group metrics where partition lag exceeded 12000 messages, so assign consumer partition balance into 4 workers instead for parallel consumption as the stream processor resumed message processing by committing offset 48 across partition 8."
    },
    # Sample 8: Kubernetes pod eviction and memory limit breach
    {
        "raw_asr": "basically coober netties worker knowed six terminated backend pods after c group memory limit exhaust we inspected kernel metrics where active pod memory reached sixteen gigabytes so adjust container memory limit into thirty two gigabytes instead four high memory services as the orchestrat restored pod scheduling buy uncordoning worker knowed six",
        "refined_text": "Kubernetes worker node 6 terminated backend pods after cgroup memory limit exhaustion.\n\nWe inspected kernel metrics where active pod memory reached 16 gigabytes, so adjust container memory limit into 32 gigabytes instead for high memory services as the orchestrator restored pod scheduling by uncordoning worker node 6."
    },
    # Sample 9: Redis cluster cache stampede and CPU saturation
    {
        "raw_asr": "um redis cache cluster instance twelve experienced high processor utilization during hot key invalidat we analyzed query telemetry where key lookup frequency reached forty thousand calls per second so enable request collapsing on proxy knowed seven instead four cache stampede defense as the cluster mitigat processor load buy caching serialized responses across eight shards",
        "refined_text": "Redis cache cluster instance 12 experienced high processor utilization during hot key invalidation.\n\nWe analyzed query telemetry where key lookup frequency reached 40000 calls per second, so enable request collapsing on proxy node 7 instead for cache stampede defense as the cluster mitigated processor load by caching serialized responses across 8 shards."
    },
    # Sample 10: Elasticsearch cluster unassigned shards and JVM garbage collection pause
    {
        "raw_asr": "uh elasticsearch cluster node five entered red cluster status after prolonged garbage collection pause we captured heap memory profiles where old generation heap reached twenty eight gigabytes so expand j v m heap limit into thirty two gigabytes instead four index recovery as the storage cluster completed shard recovery buy allocating sixteen primary shards across cluster knowed nine",
        "refined_text": "Elasticsearch cluster node 5 entered red cluster status after prolonged garbage collection pause.\n\nWe captured heap memory profiles where old generation heap reached 28 gigabytes, so expand JVM heap limit into 32 gigabytes instead for index recovery as the storage cluster completed shard recovery by allocating 16 primary shards across cluster node 9."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Sample 11: Distributed database lock contention and isolation failure
    {
        "raw_asr": "our distributed database cluster suffered severe query degradation during monthly billing settlement where checkout workers encountered status five hundred and status five hundred three we examined telemetry dashboards where the p ninety nine query latency jumped from forty milliseconds into eight seconds the primary trigger was transaction lock contention across the customer balance table after concurrent settlement jobs updated account balances without predictable row ordering we inspected the transaction coordinator log inside billing underscore trans dot log where sixty four distributed threads entered lock wait timeout inspect the isolation level inside config underscore db dot yaml instead configur transaction lock timeout buy setting four seconds on coordinator knowed two right twenty four into the maximum retry counter on worker knowed five the originating flaw stemmed from unindexed row lookups during batch balance debits where database workers executed table scans across twelve hundred customer partitions after enforcing deterministic row lock ordering and applying index hotfixes the distributed database processed five thousand settlement transactions across sixteen shards without lock timeouts or elevated error rates",
        "refined_text": "Our distributed database cluster suffered severe query degradation during monthly billing settlement where checkout workers encountered status 500 and status 503. We examined telemetry dashboards where the P99 query latency jumped from 40 milliseconds into 8 seconds. The primary trigger was transaction lock contention across the customer balance table after concurrent settlement jobs updated account balances without predictable row ordering.\n\nWe inspected the transaction coordinator log inside billing_trans.log where 64 distributed threads entered lock wait timeout, inspecting the isolation level inside config_db.yaml instead. Configure transaction lock timeout by setting 4 seconds on coordinator node 2. Write 24 into the maximum retry counter on worker node 5.\n\nThe originating flaw stemmed from unindexed row lookups during batch balance debits where database workers executed table scans across 1200 customer partitions. After enforcing deterministic row lock ordering and applying index hotfixes, the distributed database processed 5000 settlement transactions across 16 shards without lock timeouts or elevated error rates."
    },
    # Sample 12: Ingress controller HTTP/2 rapid reset DDoS
    {
        "raw_asr": "our edge ingress gateway dropped public api traffic after rapid stream resets saturated reverse proxy worker processes where frontend services reported status five hundred two and status five hundred four we analyzed edge access logs where incoming multiplexed streams spiked into eighty thousand requests per second the primary trigger was unbounded stream allocation where malicious clients opened hundreds of concurrent streams and immediately sent reset frames before payloads arrived we inspected reverse proxy memory profiles inside ingress underscore proxy dot log where worker memory consumption reached fourteen gigabytes inspect concurrent stream limits inside gateway underscore settings dot yaml instead configur the maximum concurrent streams buy setting one hundred twenty eight on edge knowed six right thirty two into the reset frame rate limit on gateway knowed eight the originating flaw existed in default stream multiplexing settings where ingress workers buffered connection state without rate limiting reset control frames after applying strict stream reset thresholds and deploying patched gateway binaries the edge ingress gateway sustained twelve thousand requests per second across eight gateway instances without memory bloat or connection drops",
        "refined_text": "Our edge ingress gateway dropped public API traffic after rapid stream resets saturated reverse proxy worker processes where frontend services reported status 502 and status 504. We analyzed edge access logs where incoming multiplexed streams spiked into 80000 requests per second. The primary trigger was unbounded stream allocation where malicious clients opened hundreds of concurrent streams and immediately sent reset frames before payloads arrived.\n\nWe inspected reverse proxy memory profiles inside ingress_proxy.log where worker memory consumption reached 14 gigabytes, inspecting concurrent stream limits inside gateway_settings.yaml instead. Configure the maximum concurrent streams by setting 128 on edge node 6. Write 32 into the reset frame rate limit on gateway node 8.\n\nThe originating flaw existed in default stream multiplexing settings where ingress workers buffered connection state without rate limiting reset control frames. After applying strict stream reset thresholds and deploying patched gateway binaries, the edge ingress gateway sustained 12000 requests per second across 8 gateway instances without memory bloat or connection drops."
    },
    # Sample 13: Redis Sentinel split-brain and consensus stall
    {
        "raw_asr": "our in memory caching tier experienced data divergence and intermittent cluster partitions when network flapping separated master knowed three from secondary replicas frontend payment services reported status five hundred and status five hundred three we analyzed sentinel consensus logs where the p ninety five failover duration exceeded forty five seconds the primary trigger was asymmetric packet loss across the inter datacenter backbone that prevented quorum agreement between five sentinel nodes we inspected failover event traces inside sentinel underscore cluster dot log where three sentinel instances failed two establish majority vote inspect consensus quorum parameters inside cache underscore quorum dot conf instead configur the sentinel failover timeout buy setting five seconds on sentinel knowed one right three into the minimum quorum replica count on instance knowed four the underlying defect was an aggressive down after milliseconds setting combined with missing replica acknowledgement checks before promotion after adjusting sentinel failover timeouts and enforcing strict replica write acknowledgements the caching cluster achieved stable consensus across ten failover simulations without split brain anomalies or dropped session writes",
        "refined_text": "Our in-memory caching tier experienced data divergence and intermittent cluster partitions when network flapping separated master node 3 from secondary replicas. Frontend payment services reported status 500 and status 503. We analyzed Sentinel consensus logs where the P95 failover duration exceeded 45 seconds. The primary trigger was asymmetric packet loss across the inter-datacenter backbone that prevented quorum agreement between 5 Sentinel nodes.\n\nWe inspected failover event traces inside sentinel_cluster.log where 3 Sentinel instances failed to establish majority vote, inspecting consensus quorum parameters inside cache_quorum.conf instead. Configure the Sentinel failover timeout by setting 5 seconds on Sentinel node 1. Write 3 into the minimum quorum replica count on instance node 4.\n\nThe underlying defect was an aggressive down-after-milliseconds setting combined with missing replica acknowledgement checks before promotion. After adjusting Sentinel failover timeouts and enforcing strict replica write acknowledgements, the caching cluster achieved stable consensus across 10 failover simulations without split-brain anomalies or dropped session writes."
    },
    # Sample 14: Kafka broker disk IOPS throttling and log flush stall
    {
        "raw_asr": "our event streaming backbone suffered persistent producer message drops during high volume metric ingestion where upstream ingestion workers encountered status five hundred three and status five hundred four we monitored broker disk telemetry where the p ninety nine disk write latency surged from five milliseconds into twelve hundred milliseconds the primary trigger was log segment flush saturation when uncompressed event streams overwhelmed solid state drive write burst credits we inspected storage write queues inside broker underscore storage dot log where twenty four partition threads stalled on synchronous disk commits inspect log flush intervals inside server underscore kafka dot conf instead configur the log flush interval messages buy setting ten thousand on broker knowed seven right sixteen into the background flush thread pool on broker knowed nine the originating flaw was unthrottled producer batch sizes combined with immediate physical disk flush requests on every batch commit after enabling producer l z four compression and increasing operating system dirty background ratios the streaming broker sustained forty thousand messages per second across twelve partitions without storage throttling or producer write rejections",
        "refined_text": "Our event streaming backbone suffered persistent producer message drops during high volume metric ingestion where upstream ingestion workers encountered status 503 and status 504. We monitored broker disk telemetry where the P99 disk write latency surged from 5 milliseconds into 1200 milliseconds. The primary trigger was log segment flush saturation when uncompressed event streams overwhelmed solid state drive write burst credits.\n\nWe inspected storage write queues inside broker_storage.log where 24 partition threads stalled on synchronous disk commits, inspecting log flush intervals inside server_kafka.conf instead. Configure the log flush interval messages by setting 10000 on broker node 7. Write 16 into the background flush thread pool on broker node 9.\n\nThe originating flaw was unthrottled producer batch sizes combined with immediate physical disk flush requests on every batch commit. After enabling producer LZ4 compression and increasing operating system dirty background ratios, the streaming broker sustained 40000 messages per second across 12 partitions without storage throttling or producer write rejections."
    },
    # Sample 15: BGP routing flap and anycast DNS edge degradation
    {
        "raw_asr": "our global anycast authoritative dns infrastructure suffered severe query packet drops when transit link flapping triggered repeated border gateway protocol path updates edge recursive resolvers observed query timeouts and status five hundred two responses we analyzed edge routing telemetry where the p ninety nine resolution time spiked from twelve milliseconds into four seconds the primary trigger was route flap damping oscillation across tier one transit links that isolated three point of presence clusters we inspected border router session logs inside bgp underscore edge dot log where four peering sessions alternated between active and idle states inspect route dampening timers inside edge underscore routing dot conf instead configur the bgp keepalive timer buy setting ten seconds on border router knowed two right thirty into the hold time register on peer knowed four the originating flaw was overly aggressive route flap dampening thresholds configured on core border routers without withdrawal suppression timers after widening flap penalty thresholds and deploying prefix filtering policies the authoritative dns network answered ninety thousand queries per second across eighteen regions without packet drops or routing flaps",
        "refined_text": "Our global anycast authoritative DNS infrastructure suffered severe query packet drops when transit link flapping triggered repeated Border Gateway Protocol path updates. Edge recursive resolvers observed query timeouts and status 502 responses. We analyzed edge routing telemetry where the P99 resolution time spiked from 12 milliseconds into 4 seconds. The primary trigger was route flap damping oscillation across Tier 1 transit links that isolated 3 point-of-presence clusters.\n\nWe inspected border router session logs inside bgp_edge.log where 4 peering sessions alternated between active and idle states, inspecting route dampening timers inside edge_routing.conf instead. Configure the BGP keepalive timer by setting 10 seconds on border router node 2. Write 30 into the hold time register on peer node 4.\n\nThe originating flaw was overly aggressive route flap dampening thresholds configured on core border routers without withdrawal suppression timers. After widening flap penalty thresholds and deploying prefix filtering policies, the authoritative DNS network answered 90000 queries per second across 18 regions without packet drops or routing flaps."
    },
    # Sample 16: EBS volume burst exhaustion and database checkpoint stall
    {
        "raw_asr": "our primary relational database stalled during intensive batch data imports where customer facing microservices experienced status five hundred and status five hundred four we analyzed cloud storage performance metrics where the p ninety nine write latency jumped from two milliseconds into sixteen hundred milliseconds the primary trigger was elastic block store burst balance depletion on the database data volume after continuous random write operations exhausted accumulated i o p s credits we inspected database checkpoint timings inside storage underscore perf dot log where thirty two worker backends waited on physical block writes inspect volume provisioning parameters inside db underscore volume dot yaml instead configur the baseline volume throughput buy setting two hundred fifty megabytes per second on storage volume knowed five right three thousand into the provisioned i o p s allocation on pool knowed eight the originating flaw was relying on burstable general purpose storage volumes four high write transaction workloads without provisioned baseline performance after migrating the cluster database volume into provisioned i o p s storage and tuning checkpoint completion targets the database processed eight thousand write transactions per second across four volumes without storage stalls or latency degradation",
        "refined_text": "Our primary relational database stalled during intensive batch data imports where customer facing microservices experienced status 500 and status 504. We analyzed cloud storage performance metrics where the P99 write latency jumped from 2 milliseconds into 1600 milliseconds. The primary trigger was Elastic Block Store burst balance depletion on the database data volume after continuous random write operations exhausted accumulated IOPS credits.\n\nWe inspected database checkpoint timings inside storage_perf.log where 32 worker backends waited on physical block writes, inspecting volume provisioning parameters inside db_volume.yaml instead. Configure the baseline volume throughput by setting 250 megabytes per second on storage volume node 5. Write 3000 into the provisioned IOPS allocation on pool node 8.\n\nThe originating flaw was relying on burstable general purpose storage volumes for high write transaction workloads without provisioned baseline performance. After migrating the cluster database volume into provisioned IOPS storage and tuning checkpoint completion targets, the database processed 8000 write transactions per second across 4 volumes without storage stalls or latency degradation."
    },
    # Sample 17: Service mesh mutual TLS authentication failure
    {
        "raw_asr": "our internal service mesh experienced widespread communication breakdowns when inter service requests failed across thirty two backend microservices where api gateways returned status five hundred two and status five hundred three we analyzed envoy proxy connection traces where mutual t l s handshakes aborted with certificate verification alerts the primary trigger was an expired intermediate certificate authority certificate that was omitted from the automated certificate renewal pipeline we inspected service mesh proxy logs inside mesh underscore tls dot log where sixty four proxy sidecars rejected upstream endpoints inspect certificate rotation configurations inside cert underscore manager dot yaml instead configur the certificate renewal threshold buy setting twenty four hours on cluster knowed one right seven into the renewal retry schedule on mesh knowed six the underlying defect was hardcoded leaf certificate validation paths inside legacy sidecar injection templates that bypassed automated secret sync jobs after issuing updated x five zero nine certificate bundles and restarting proxy instances the service mesh handled twenty thousand authenticated calls per second across forty clusters without handshake failures or authorization errors",
        "refined_text": "Our internal service mesh experienced widespread communication breakdowns when inter service requests failed across 32 backend microservices where API gateways returned status 502 and status 503. We analyzed Envoy proxy connection traces where mutual TLS handshakes aborted with certificate verification alerts. The primary trigger was an expired intermediate certificate authority certificate that was omitted from the automated certificate renewal pipeline.\n\nWe inspected service mesh proxy logs inside mesh_tls.log where 64 proxy sidecars rejected upstream endpoints, inspecting certificate rotation configurations inside cert_manager.yaml instead. Configure the certificate renewal threshold by setting 24 hours on cluster node 1. Write 7 into the renewal retry schedule on mesh node 6.\n\nThe underlying defect was hardcoded leaf certificate validation paths inside legacy sidecar injection templates that bypassed automated secret sync jobs. After issuing updated X.509 certificate bundles and restarting proxy instances, the service mesh handled 20000 authenticated calls per second across 40 clusters without handshake failures or authorization errors."
    },
    # Sample 18: CFS CPU quota throttling and thread pool exhaustion
    {
        "raw_asr": "our checkout orchestration microservice ceased responding during flash sales where client applications received status five hundred three and status five hundred four we analyzed container performance metrics where the p ninety nine request duration escalated from thirty milliseconds into fifteen seconds the primary trigger was severe completely fair scheduler c p u quota throttling under high concurrency that caused thread pool worker starvation we inspected thread stack dumps inside service underscore thread dot log where two hundred sixteen application threads blocked in pool execution queues inspect container cgroup limits inside deployment underscore checkout dot yaml instead configur the c p u quota allocation buy setting four hundred percent on compute knowed three right forty into the maximum thread queue capacity on worker knowed seven the originating flaw was setting rigid c group c p u bandwidth limits without disabling CFS quota enforcement on bursty multi threaded runtimes after disabling CFS quota throttling and increasing thread pool executor limits the checkout microservice processed six thousand orders per second across eight container replicas without thread pool starvation or latency spikes",
        "refined_text": "Our checkout orchestration microservice ceased responding during flash sales where client applications received status 503 and status 504. We analyzed container performance metrics where the P99 request duration escalated from 30 milliseconds into 15 seconds. The primary trigger was severe completely fair scheduler CPU quota throttling under high concurrency that caused thread pool worker starvation.\n\nWe inspected thread stack dumps inside service_thread.log where 216 application threads blocked in pool execution queues, inspecting container cgroup limits inside deployment_checkout.yaml instead. Configure the CPU quota allocation by setting 400 percent on compute node 3. Write 40 into the maximum thread queue capacity on worker node 7.\n\nThe originating flaw was setting rigid cgroup CPU bandwidth limits without disabling CFS quota enforcement on bursty multi-threaded runtimes. After disabling CFS quota throttling and increasing thread pool executor limits, the checkout microservice processed 6000 orders per second across 8 container replicas without thread pool starvation or latency spikes."
    },
    # Sample 19: RabbitMQ unacknowledged message build-up and channel memory alarm
    {
        "raw_asr": "our asynchronous notification pipeline stalled during bulk customer campaign dispatches where worker publishers encountered status five hundred and status five hundred three we analyzed message broker telemetry where unacknowledged message backlogs exceeded eighty thousand messages the primary trigger was consumer prefetch buffer overflow where slow email delivery workers accumulated unacknowledged messages until broker memory alarms tripped and blocked publishing channels we inspected queue channel metrics inside rabbitmq underscore cluster dot log where sixteen publisher connections entered channel blocked status inspect consumer prefetch configurations inside queue underscore policy dot conf instead configur the consumer prefetch count buy setting twenty on worker knowed four right twelve into the channel max uncommitted batch count on broker knowed six the originating flaw was configuring infinite prefetch counts on consumer workers that allowed individual nodes two hoard messages without timely acknowledgements after capping prefetch counts and enabling lazy queue paging the messaging cluster cleared thirty thousand pending notifications across six queues without triggering broker memory alarms or producer channel blocks",
        "refined_text": "Our asynchronous notification pipeline stalled during bulk customer campaign dispatches where worker publishers encountered status 500 and status 503. We analyzed message broker telemetry where unacknowledged message backlogs exceeded 80000 messages. The primary trigger was consumer prefetch buffer overflow where slow email delivery workers accumulated unacknowledged messages until broker memory alarms tripped and blocked publishing channels.\n\nWe inspected queue channel metrics inside rabbitmq_cluster.log where 16 publisher connections entered channel blocked status, inspecting consumer prefetch configurations inside queue_policy.conf instead. Configure the consumer prefetch count by setting 20 on worker node 4. Write 12 into the channel max uncommitted batch count on broker node 6.\n\nThe originating flaw was configuring infinite prefetch counts on consumer workers that allowed individual nodes to hoard messages without timely acknowledgements. After capping prefetch counts and enabling lazy queue paging, the messaging cluster cleared 30000 pending notifications across 6 queues without triggering broker memory alarms or producer channel blocks."
    },
    # Sample 20: Jaeger distributed tracing span drop and UDP buffer overflow
    {
        "raw_asr": "our distributed tracing platform lost observability during core billing service incidents where telemetry agents reported status five hundred two and status five hundred four we monitored trace ingestion dashboards where trace dropped counts surged from zero into fifty thousand spans per second the primary trigger was collector u d p socket buffer overflow when thousands of microservice sidecars pushed uncompressed trace spans simultaneously over the local network we inspected ingestion worker queues inside jaeger underscore collector dot log where thirty two collector threads dropped trace batches inspect socket buffer sizes inside tracing underscore agent dot yaml instead configur the collector socket receive buffer buy setting sixteen megabytes on collector knowed five right twenty four into the queue worker thread count on ingestion knowed eight the underlying defect was reliance on lossy u d p transport with fixed kernel receive buffers under bursty network telemetry conditions after transitioning ingestion agents two g r p c transport and tuning linux kernel socket memory buffers the distributed tracing cluster processed seventy thousand spans per second across twelve collectors without packet loss or truncated traces",
        "refined_text": "Our distributed tracing platform lost observability during core billing service incidents where telemetry agents reported status 502 and status 504. We monitored trace ingestion dashboards where trace dropped counts surged from 0 into 50000 spans per second. The primary trigger was collector UDP socket buffer overflow when thousands of microservice sidecars pushed uncompressed trace spans simultaneously over the local network.\n\nWe inspected ingestion worker queues inside jaeger_collector.log where 32 collector threads dropped trace batches, inspecting socket buffer sizes inside tracing_agent.yaml instead. Configure the collector socket receive buffer by setting 16 megabytes on collector node 5. Write 24 into the queue worker thread count on ingestion node 8.\n\nThe underlying defect was reliance on lossy UDP transport with fixed kernel receive buffers under bursty network telemetry conditions. After transitioning ingestion agents to gRPC transport and tuning Linux kernel socket memory buffers, the distributed tracing cluster processed 70000 spans per second across 12 collectors without packet loss or truncated traces."
    }
]

print(f"Total samples: {len(batch_70)}")
assert len(batch_70) == 20, f"Expected 20 samples, got {len(batch_70)}"

tiers = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(batch_70):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = validator.validate_pair(pair)
    if not val_ok:
        print(f"FAILED validate_pair on sample {idx+1}: {val_reason}")
        sys.exit(1)

    # Cleaner check
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    if clean_obj is None or clean_reason != "kept":
        print(f"FAILED clean_sample on sample {idx+1}: {clean_reason}")
        sys.exit(1)

    # Word count and tier check
    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

print(f"Tier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

# Batch distribution check
batch_ok, batch_msg, batch_tiers = validator.validate_batch(batch_70, min_short=4, min_medium=6, min_long=10)
if not batch_ok:
    print(f"FAILED validate_batch: {batch_msg}")
    sys.exit(1)

print("Batch check OK:", batch_msg, batch_tiers)

# Write to scratch/subagent_batch_70.json
out_path = Path("scratch/subagent_batch_70.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch_70, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(batch_70)} pairs to {out_path}")
