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

batch_75 = [
    # ==========================================
    # TIER 1: SHORT (< 25 words) - Exactly 4 samples
    # Exactly 1 sentence, 0 newlines, max 1 cut-word
    # ==========================================
    # Sample 1: Database connection pool exhaustion incident
    {
        "raw_asr": "uh the post gres connection pool exhaust available worker slots four forty seconds",
        "refined_text": "The Postgres connection pool exhausted available worker slots for 40 seconds."
    },
    # Sample 2: CoreDNS query socket buffer depletion
    {
        "raw_asr": "um worker knowed six deplet available socket buffers during thirty seconds of peak ingress",
        "refined_text": "Worker node 6 depleted available socket buffers during 30 seconds of peak ingress."
    },
    # Sample 3: Container cgroup termination by kubelet
    {
        "raw_asr": "basically the cube let terminat eight ingestion pods after c group memory limits were reached",
        "refined_text": "The kubelet terminated 8 ingestion pods after cgroup memory limits were reached."
    },
    # Sample 4: Edge gateway TLS handshake escalation
    {
        "raw_asr": "uh the edge gateway escalat error counts buy dropping twelve client handshakes",
        "refined_text": "The edge gateway escalated error counts by dropping 12 client handshakes."
    },

    # ==========================================
    # TIER 2: MEDIUM (25-89 words) - Exactly 6 samples
    # 1-3 sentences, natural \n\n break
    # ==========================================
    # Sample 5: Redis cluster shard failover latency
    {
        "raw_asr": "basically the caching cluster experienced an automatic failov when shard master four stopped responding four twenty seconds wait thirty seconds instead uh replica promotion stalled buy queuing write buffers across six replica nodes",
        "refined_text": "The caching cluster experienced an automatic failover when shard master 4 stopped responding for 30 seconds instead.\n\nReplica promotion stalled by queuing write buffers across 6 replica nodes."
    },
    # Sample 6: Kafka consumer group partition rebalance lag
    {
        "raw_asr": "um the event consumer group triggered an unexpected partition rebalanc after worker knowed eighteen missed consecutive heartbeat intervals p ninety nine message processing latency increased four four minutes across twenty active topics",
        "refined_text": "The event consumer group triggered an unexpected partition rebalance after worker node 18 missed consecutive heartbeat intervals.\n\nP99 message processing latency increased for 4 minutes across 20 active topics."
    },
    # Sample 7: PostgreSQL deadlocks during batch reconciliation
    {
        "raw_asr": "in this database incident two concurrent reconciliation jobs created deadlock cycles inside post gres q l buy locking the billing table wait twelve transactions instead um query coordinators terminat eight blocked worker sessions after waiting two hundred forty seconds",
        "refined_text": "In this database incident 2 concurrent reconciliation jobs created deadlock cycles inside PostgreSQL by locking the billing table, involving 12 transactions instead.\n\nQuery coordinators terminated 8 blocked worker sessions after waiting 240 seconds."
    },
    # Sample 8: RabbitMQ queue memory saturation triggering publisher flow control
    {
        "raw_asr": "uh the message broker activated publisher flow control after queue memory hit eighty percent of total node capacity this memory congest throttl incoming deliveries buy holding five hundred client sockets in sleep state",
        "refined_text": "The message broker activated publisher flow control after queue memory hit 80 percent of total node capacity.\n\nThis memory congestion throttled incoming deliveries by holding 500 client sockets in sleep state."
    },
    # Sample 9: Upstream proxy connection pool starvation emitting HTTP 504 gateway timeouts
    {
        "raw_asr": "basically the reverse proxy emitted status five hundred four gateway timeouts after backend connection pools were exhaust four sixteen seconds um the originating flaw stemmed from stale keep alive settings across thirty upstream targets",
        "refined_text": "The reverse proxy emitted status 504 gateway timeouts after backend connection pools were exhausted for 16 seconds.\n\nThe originating flaw stemmed from stale keep-alive settings across 30 upstream targets."
    },
    # Sample 10: Elasticsearch indexing backpressure causing ingest pipeline queue overflow
    {
        "raw_asr": "uh our post mortem identified a primary trigger in the log ingestion pipeline buy tracing unindexed bulk requests that deplet cluster heap buffers p ninety five indexing latency jumped past four seconds across twenty ingest nodes",
        "refined_text": "Our post-mortem identified a primary trigger in the log ingestion pipeline by tracing unindexed bulk requests that depleted cluster heap buffers.\n\nP95 indexing latency jumped past 4 seconds across 20 ingest nodes."
    },

    # ==========================================
    # TIER 3: LONG (90+ words) - Exactly 10 samples
    # Multi-paragraph \n\n, zero checklist stereotypes, natural narration
    # ==========================================
    # Sample 11: Multi-AZ payment gateway outage triggered by cascading timeouts and unhedged retries
    {
        "raw_asr": "uh at zero eight hundred our payment processing gateway experienced a major outage across three availability zones p ninety nine transaction latency escalated past twelve seconds and downstream billing clients encountered status five zero three errors across twenty minutes wait twenty five minutes instead basically edge proxies exhaust their thread pools because backend merchant acquirers were slow to respond the post mortem revealed that the underlying defect was an aggressive client retry policy buy client applications when initial calls timed out after four seconds client libraries issued four immediate retries without exponential backoff this amplification deplet connection buffers across forty gateway instances and overwhelmed the primary billing dispatcher engineers mitigated the incident buy enabling adaptive rate limiting and lowering circuit breaker trip thresholds towards fifty concurrent failures traffic stabilized after operators drained stalled connections across eight worker nodes buy restarting proxy services",
        "refined_text": "At 0800 our payment processing gateway experienced a major outage across 3 availability zones. P99 transaction latency escalated past 12 seconds and downstream billing clients encountered status 503 errors across 25 minutes instead. Edge proxies exhausted their thread pools because backend merchant acquirers were slow to respond.\n\nThe post-mortem revealed that the underlying defect was an aggressive client retry policy by client applications. When initial calls timed out after 4 seconds client libraries issued 4 immediate retries without exponential backoff. This amplification depleted connection buffers across 40 gateway instances and overwhelmed the primary billing dispatcher.\n\nEngineers mitigated the incident by enabling adaptive rate limiting and lowering circuit breaker trip thresholds towards 50 concurrent failures. Traffic stabilized after operators drained stalled connections across 8 worker nodes by restarting proxy services."
    },
    # Sample 12: Distributed consensus latency spike in etcd cluster causing leader election churn
    {
        "raw_asr": "um during the morning peak our control plane cluster experienced severe et see dee latency spikes buy reaching disk write wait times of three hundred milliseconds wait five hundred milliseconds instead p ninety five raft proposal commit duration spiked and triggered leader electi churn across five control plane members basically the api server began throttling incoming cube ctl requests and dropped sixty percent of incoming admission webhooks our incident review identified an originating flaw inside the storage tier where write ahead log disk volumes shared i o bandwidth with node logging daemons during heavy log rotations disk access queues blocked fsync calls four ten seconds which forced et see dee followers two drop out of consensus membership repeatedly site reliability engineers restored cluster stability buy segregating the et see dee write ahead log onto dedicated solid state storage volumes with high throughput allowances operators also restarted stalled cube let daemons across eight worker knowed instances two restore node status reporting",
        "refined_text": "During the morning peak our control plane cluster experienced severe etcd latency spikes by reaching disk write wait times of 500 milliseconds instead. P95 Raft proposal commit duration spiked and triggered leader election churn across 5 control plane members. The API server began throttling incoming kubectl requests and dropped 60 percent of incoming admission webhooks.\n\nOur incident review identified an originating flaw inside the storage tier where write-ahead log disk volumes shared I/O bandwidth with node logging daemons. During heavy log rotations disk access queues blocked fsync calls for 10 seconds, which forced etcd followers to drop out of consensus membership repeatedly.\n\nSite reliability engineers restored cluster stability by segregating the etcd write-ahead log onto dedicated solid-state storage volumes with high throughput allowances. Operators also restarted stalled kubelet daemons across 8 worker node instances to restore node status reporting."
    },
    # Sample 13: Ephemeral port exhaustion in ingress controller causing connection establishment failures
    {
        "raw_asr": "basically on monday afternoon our edge ingress proxies began failing outgoing upstream connections buy emitting status five zero two bad gateway errors internal packet captures taken with wi re shark showed failed t c p sync handshakes across four core proxy hosts connection metrics indicated that active connections reached twenty thousand concurrent sockets wait thirty thousand concurrent sockets instead which completely exhaust the local ephemeral port range investigation during the post incident audit isolated the primary trigger as a misconfigured c n i network plugin setting upstream connection pooling was disabled in the edge proxy configuration which forced proxy processes two allocat a new socket four every client request without reusing active connections this behavior flooded linux connection tracking tables and kept closed sockets trapped in time wait state four sixty seconds the on call engineers restored operational service buy enabling upstream keep alive connection pools with six hundred idle targets operators also tuned kernel networking parameters inside coober netties worker knowed templates buy increasing the local port range boundaries",
        "refined_text": "On Monday afternoon our edge ingress proxies began failing outgoing upstream connections by emitting status 502 bad gateway errors. Internal packet captures taken with Wireshark showed failed TCP SYN handshakes across 4 core proxy hosts. Connection metrics indicated that active connections reached 30000 concurrent sockets instead, which completely exhausted the local ephemeral port range.\n\nInvestigation during the post-incident audit isolated the primary trigger as a misconfigured CNI network plugin setting. Upstream connection pooling was disabled in the edge proxy configuration, which forced proxy processes to allocate a new socket for every client request without reusing active connections. This behavior flooded Linux connection tracking tables and kept closed sockets trapped in TIME_WAIT state for 60 seconds.\n\nThe on-call engineers restored operational service by enabling upstream keep-alive connection pools with 600 idle targets. Operators also tuned kernel networking parameters inside Kubernetes worker node templates by increasing the local port range boundaries."
    },
    # Sample 14: PostgreSQL autovacuum freeze lock incident stalling transaction commits
    {
        "raw_asr": "uh our primary transactional database halted transaction processing when autovacuum freeze workers acquired exclusive relation locks on the order ledger table p ninety nine transaction commit latency spiked from twelve milliseconds to forty five seconds client connection pools saturat within five minutes buy exceeding three hundred concurrent connections wait four hundred concurrent connections instead basically application pods received connection pool timeout errors across all checkout services post mortem analysis traced the originating flaw to delayed autovacuum execution during the previous weekend data migration transaction age on the core ledger table exceeded two hundred million transactions which triggered aggressive autovacuum wraparound protection workers this background lock held back concurrent table modifications and queued eighty incoming schema locks database administrators relieved lock contention buy cancelling the background vacuum worker and setting the autovacuum freeze max age threshold towards three hundred million transactions operators scheduled maintenance windows two perform vacuum freeze operations with manual cost limits",
        "refined_text": "Our primary transactional database halted transaction processing when autovacuum freeze workers acquired exclusive relation locks on the order ledger table. P99 transaction commit latency spiked from 12 milliseconds to 45 seconds. Client connection pools saturated within 5 minutes by exceeding 400 concurrent connections instead. Application pods received connection pool timeout errors across all checkout services.\n\nPost-mortem analysis traced the originating flaw to delayed autovacuum execution during the previous weekend data migration. Transaction age on the core ledger table exceeded 200000000 transactions, which triggered aggressive autovacuum wraparound protection workers. This background lock held back concurrent table modifications and queued 80 incoming schema locks.\n\nDatabase administrators relieved lock contention by cancelling the background vacuum worker and setting the autovacuum freeze max age threshold towards 300000000 transactions. Operators scheduled maintenance windows to perform vacuum freeze operations with manual cost limits."
    },
    # Sample 15: Memory leak in WebSocket gateway workers triggering node cgroup evictions
    {
        "raw_asr": "um on thursday evening our real time notification cluster degraded after websocket connection gateways consumed available host memory worker knowed memory pressure alerts triggered when heap allocations exceeded eight gigabytes the cube let on worker knowed twelve terminat fifty gateway pods wait seventy worker instances instead under c group out of memory protection basically disconnected mobile clients initiated a thundering herd reconnection storm that pushed p ninety five handshake latency past eight seconds the underlying defect resided inside an a sink event dispatcher where disconnected socket channels failed two unregister event listeners during network reconnect cycles uncollected subscriber objects accumulat inside process memory and deplet available buffers across all active gateway pods engineers contained the incident buy temporarily scaling the gateway deployment to one hundred replicas and routing incoming client handshakes through rate limited ingress queues developers deployed an updated binary that explicitly dereferenced socket listeners during client disconnect events",
        "refined_text": "On Thursday evening our real-time notification cluster degraded after WebSocket connection gateways consumed available host memory. Worker node memory pressure alerts triggered when heap allocations exceeded 8 gigabytes. The kubelet on worker node 12 terminated 70 worker instances instead under cgroup out-of-memory protection. Disconnected mobile clients initiated a thundering herd reconnection storm that pushed P95 handshake latency past 8 seconds.\n\nThe underlying defect resided inside an async event dispatcher where disconnected socket channels failed to unregister event listeners during network reconnect cycles. Uncollected subscriber objects accumulated inside process memory and depleted available buffers across all active gateway pods.\n\nEngineers contained the incident by temporarily scaling the gateway deployment to 100 replicas and routing incoming client handshakes through rate-limited ingress queues. Developers deployed an updated binary that explicitly dereferenced socket listeners during client disconnect events."
    },
    # Sample 16: Disk I/O saturation on WAL volumes causing Kafka broker acknowledgment timeouts
    {
        "raw_asr": "uh our distributed streaming message pipeline degraded when broker knowed four stopped acknowledging incoming batch productions p ninety nine message publish latency jumped from five milliseconds to twenty seconds wait thirty seconds instead consumer groups stalled across twenty four analytics topics because the broker missed zookeeper heartbeats basically the cluster coordinator declared broker knowed four dead and initiated an emergency partition rebalanc across six remaining cluster brokers incident investigation identified the primary trigger as severe disk write queue saturation on the broker commit log volume a background compaction process was triggered during peak ingestion hours which consumed all available disk bandwidth disk write latency spiked to two thousand milliseconds and starved operating system page cache flushes operations engineers recovered cluster throughput buy throttling the background log cleaner threads and raising the broker session timeout towards ninety seconds the engineering team also updated deployment templates buy provisioning dedicated nvme drives four kafka log segments",
        "refined_text": "Our distributed streaming message pipeline degraded when broker node 4 stopped acknowledging incoming batch productions. P99 message publish latency jumped from 5 milliseconds to 30 seconds instead. Consumer groups stalled across 24 analytics topics because the broker missed ZooKeeper heartbeats. The cluster coordinator declared broker node 4 dead and initiated an emergency partition rebalance across 6 remaining cluster brokers.\n\nIncident investigation identified the primary trigger as severe disk write queue saturation on the broker commit log volume. A background compaction process was triggered during peak ingestion hours, which consumed all available disk bandwidth. Disk write latency spiked to 2000 milliseconds and starved operating system page cache flushes.\n\nOperations engineers recovered cluster throughput by throttling the background log cleaner threads and raising the broker session timeout towards 90 seconds. The engineering team also updated deployment templates by provisioning dedicated NVMe drives for Kafka log segments."
    },
    # Sample 17: BGP route flap between cloud regions causing transit link saturation
    {
        "raw_asr": "um on tuesday morning cross region database replication stalled after transit gateway b g p root flaps saturated backbone network interfaces interconnect monitors detected twenty percent packet loss wait thirty percent packet loss instead across inter region links database replicas accumulated fourteen minutes of replication lag and edge routers emitted status five zero four gateway timeouts four incoming customer sessions the originating flaw was an unannounced transit provider link maintenance window that triggered repeated b g p path reconvergences fluctuating border gateway advertisements caused routing loops that overloaded backup optical links and triggered severe queue congest on core edge routers network engineers mitigated the outage buy manually pinning inter region traffic towards dedicated direct connect paths and suppressing unstable b g p announcements operators monitored packet drop rates across eight hundred edge interfaces until regional replication caught up completely",
        "refined_text": "On Tuesday morning cross-region database replication stalled after transit gateway BGP route flaps saturated backbone network interfaces. Interconnect monitors detected 30 percent packet loss instead across inter-region links. Database replicas accumulated 14 minutes of replication lag and edge routers emitted status 504 gateway timeouts for incoming customer sessions.\n\nThe originating flaw was an unannounced transit provider link maintenance window that triggered repeated BGP path reconvergences. Fluctuating border gateway advertisements caused routing loops that overloaded backup optical links and triggered severe queue congestion on core edge routers.\n\nNetwork engineers mitigated the outage by manually pinning inter-region traffic towards dedicated direct connect paths and suppressing unstable BGP announcements. Operators monitored packet drop rates across 800 edge interfaces until regional replication caught up completely."
    },
    # Sample 18: Cassandra node token range repair overhead causing JVM GC pauses
    {
        "raw_asr": "uh our cassandra distributed storage cluster suffered major client read degradation when j v m garbage collector pauses exceeded twelve seconds on core ring instances p ninety nine read request latency climbed past four seconds across twenty four nodes wait thirty two nodes instead basically client coordinator nodes experienced read timeouts and dropped sixty percent of incoming point lookups our post mortem team discovered the underlying defect inside an automated token range repair script scheduled across the cluster the automated utility launched concurrent repairs on sixteen token ranges without checking pending sstable compaction queues this high repair volume deplet available heap buffers and forced the j v m into continuous concurrent mark sweep stop the world cycles systems engineers resolved the cluster disruption buy pausing the automated repair schedule and increasing client query timeout parameters operators also tuned heap garbage collection settings buy migrating ring member configurations towards the g one collector engine",
        "refined_text": "Our Cassandra distributed storage cluster suffered major client read degradation when JVM garbage collector pauses exceeded 12 seconds on core ring instances. P99 read request latency climbed past 4 seconds across 32 nodes instead. Client coordinator nodes experienced read timeouts and dropped 60 percent of incoming point lookups.\n\nOur post-mortem team discovered the underlying defect inside an automated token range repair script scheduled across the cluster. The automated utility launched concurrent repairs on 16 token ranges without checking pending SSTable compaction queues. This high repair volume depleted available heap buffers and forced the JVM into continuous concurrent mark-sweep stop-the-world cycles.\n\nSystems engineers resolved the cluster disruption by pausing the automated repair schedule and increasing client query timeout parameters. Operators also tuned heap garbage collection settings by migrating ring member configurations towards the G1 collector engine."
    },
    # Sample 19: Asynchronous task queue worker pool exhaustion during scheduled billing export job
    {
        "raw_asr": "um during end of month invoicing our asynchronous task queue fell behind buy forty five minutes on outbound webhook dispatches task processing latency escalated sharply and p ninety five webhook delivery delays exceeded twelve minutes task dispatchers exhaust their available concurrency slots across fifty worker instances wait seventy worker instances instead basically downstream third party payment notification endpoints received status four hundred twenty nine rate limit errors engineering investigation isolated the primary trigger within an unbatched billing export job scheduled at midnight the export cron job submitted fifty thousand webhook tasks into the queue without concurrency throttling which saturated the shared worker pool and delayed high priority payment notifications the operations squad resolved the backlog buy spinning up thirty dedicated high priority queue consumers and configuring exponential backoff with jitter on outgoing webhook dispatchers engineers also partitioned task queues inside post gres buy separating low priority batch exports from synchronous payment notifications",
        "refined_text": "During end-of-month invoicing our asynchronous task queue fell behind by 45 minutes on outbound webhook dispatches. Task processing latency escalated sharply and P95 webhook delivery delays exceeded 12 minutes. Task dispatchers exhausted their available concurrency slots across 70 worker instances instead. Downstream third-party payment notification endpoints received status 429 rate-limit errors.\n\nEngineering investigation isolated the primary trigger within an unbatched billing export job scheduled at midnight. The export cron job submitted 50000 webhook tasks into the queue without concurrency throttling, which saturated the shared worker pool and delayed high-priority payment notifications.\n\nThe operations squad resolved the backlog by spinning up 30 dedicated high-priority queue consumers and configuring exponential backoff with jitter on outgoing webhook dispatchers. Engineers also partitioned task queues inside Postgres by separating low-priority batch exports from synchronous payment notifications."
    },
    # Sample 20: Ingress NGINX upstream buffer overflow incident dropping HTTP chunked transfer responses
    {
        "raw_asr": "uh our edge ingress tier experienced widespread client download failures when nginx proxy pods began truncat large binary payloads downstream clients received status five zero two bad gateway errors when downloading container images larger than sixteen megabytes wait thirty two megabytes instead ingress metrics recorded elevated buffer spill events buy writing intermediate chunks to slow host disk storage basically proxy workers exhaust available temporary disk space across forty worker knowed instances the originating flaw stemmed from default proxy buffer settings inside the coober netties ingress configuration upstream buffering was enabled with restrictive memory limits which forced proxy daemons two buffer streaming responses onto disk rather than streaming directly two clients when concurrent downloads surged disk write queues stalled and caused upstream read timeouts site reliability engineers applied an emergency hotfix buy updating the ingress configmap using cube ctl operators increased proxy buffer size towards sixty four megabytes and enabled chunked transfer pass through four binary download routes traffic stabilized immediately across eight hundred edge clients",
        "refined_text": "Our edge ingress tier experienced widespread client download failures when NGINX proxy pods began truncating large binary payloads. Downstream clients received status 502 bad gateway errors when downloading container images larger than 32 megabytes instead. Ingress metrics recorded elevated buffer spill events by writing intermediate chunks to slow host disk storage. Proxy workers exhausted available temporary disk space across 40 worker node instances.\n\nThe originating flaw stemmed from default proxy buffer settings inside the Kubernetes ingress configuration. Upstream buffering was enabled with restrictive memory limits, which forced proxy daemons to buffer streaming responses onto disk rather than streaming directly to clients. When concurrent downloads surged disk write queues stalled and caused upstream read timeouts.\n\nSite reliability engineers applied an emergency hotfix by updating the ingress ConfigMap using kubectl. Operators increased proxy buffer size towards 64 megabytes and enabled chunked transfer pass-through for binary download routes. Traffic stabilized immediately across 800 edge clients."
    }
]

out_file = Path("scratch/subagent_batch_75.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(batch_75, f, indent=2)

print(f"Wrote {len(batch_75)} pairs to {out_file}")

# Verify
tiers = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(batch_75):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator
    val_ok, val_reason = validator.validate_pair(pair)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner
    clean_obj, clean_reason = cleaner.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx+1} clean status: {clean_reason}"

    # Tier invariants
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

batch_ok, batch_msg, batch_tiers = validator.validate_batch(batch_75, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"Batch validation failed: {batch_msg}"

print("ALL CHECKS PASSED DETERMINISTICALLY WITH 0 ERRORS!")
