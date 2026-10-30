import json
import re
import sys
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("validator", "code/validator.py")
validator = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(validator)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("cleaner", "code/cleaner.py")
cleaner = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(cleaner)

pairs = [
    # =========================================================================
    # TIER 1: SHORT (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence, 0 newlines, max 1 cut-word. Content words >= 6-8.
    # =========================================================================

    # Sample 1: Ceph OSD peering heartbeat failure / drive controller timeout
    {
        "raw_asr": "basically ceph storage daemon eight marked its pool unhealth after thirty consecutive drive controller timeouts buy dropping sixteen placement groups",
        "refined_text": "Ceph storage daemon 8 marked its pool unhealthy after 30 consecutive drive controller timeouts by dropping 16 placement groups."
    },

    # Sample 2: ZooKeeper ensemble follower sync drop / tick pulse loss
    {
        "raw_asr": "um zookeeper ensemble knowed two declar a quorum drop after twenty missed follower tick pulses buy rejecting nine client sessions",
        "refined_text": "ZooKeeper ensemble node 2 declared a quorum drop after 20 missed follower tick pulses by rejecting 9 client sessions."
    },

    # Sample 3: RabbitMQ mirror queue desynchronization / heartbeat drop
    {
        "raw_asr": "uh rabbit m q mirror queue synchronizat stalled across knowed four after network heartbeat loss buy dropping twelve worker connections",
        "refined_text": "RabbitMQ mirror queue synchronization stalled across node 4 after network heartbeat loss by dropping 12 worker connections."
    },

    # Sample 4: Couchbase cluster vBucket partition migration abort
    {
        "raw_asr": "basically couchbase cluster knowed six trigger partition rebalance abort after five disk write failures buy ejecting eight active v buckets",
        "refined_text": "Couchbase cluster node 6 triggered partition rebalance abort after 5 disk write failures by ejecting 8 active vBuckets."
    },

    # =========================================================================
    # TIER 2: MEDIUM (25-89 words) - Exactly 6 samples (Samples 5-10)
    # 1-3 sentences, natural \n\n break between distinct thoughts.
    # Max \n\n breaks: len(words) // 25.
    # =========================================================================

    # Sample 5: MySQL InnoDB deadlock cascade during concurrent ledger updates
    {
        "raw_asr": "um the my s q l transaction engine encountered an inno d b deadlock cascade when concurrent ledger updates clashed on account tables thirty worker threads stalled buy locking four hundred index rows until the dead lock detector aborted ten transactions",
        "refined_text": "The MySQL transaction engine encountered an InnoDB deadlock cascade when concurrent ledger updates clashed on account tables.\n\nThirty worker threads stalled by locking 400 index rows until the deadlock detector aborted 10 transactions."
    },

    # Sample 6: Envoy ingress rate limiter Redis latency spike
    {
        "raw_asr": "basically envoy gateway proxies dropped incoming checkout requests after redis rate limit lookups exceeded forty milliseconds wait seventy milliseconds instead the proxy tier rejected twenty percent of customer traffic buy emitting status four hundred twenty nine responses across twelve worker pods",
        "refined_text": "Envoy gateway proxies dropped incoming checkout requests after Redis rate limit lookups exceeded 70 milliseconds instead.\n\nThe proxy tier rejected 20 percent of customer traffic by emitting status 429 responses across 12 worker pods."
    },

    # Sample 7: Prometheus TSDB block compaction OOM termination
    {
        "raw_asr": "uh the prometheus monitoring server suffered an out of memory crash when t s d b block compaction exceeded sixty four gigabytes of memory allocat the host operating system terminated the scraper daemon buy sending kill signals after thirty minutes of continuous compaction activity",
        "refined_text": "The Prometheus monitoring server suffered an out of memory crash when TSDB block compaction exceeded 64 gigabytes of memory allocation.\n\nThe host operating system terminated the scraper daemon by sending kill signals after 30 minutes of continuous compaction activity."
    },

    # Sample 8: NGINX ingress header buffer overflow dropping RPC traffic
    {
        "raw_asr": "um edge n g i n x ingress proxies encountered memory exhaustion when incoming cookie headers exceeded sixteen kilobytes wait thirty two kilobytes instead worker daemons dropped fifteen thousand r p c connections buy generating status five hundred two bad gateway responses across ten ingress pods",
        "refined_text": "Edge nginx-ingress proxies encountered memory exhaustion when incoming cookie headers exceeded 32 kilobytes instead.\n\nWorker daemons dropped 15000 RPC connections by generating status 502 bad gateway responses across 10 ingress pods."
    },

    # Sample 9: HAProxy load balancer backend health check timeouts
    {
        "raw_asr": "basically h a proxy load balancer knowed four marked downstream authentication workers unhealth after twelve consecutive health check timeouts the proxy daemon dropped thirty percent of customer login requests buy returning status five hundred three responses towards eight frontend instances",
        "refined_text": "HAProxy load balancer node 4 marked downstream authentication workers unhealthy after 12 consecutive health check timeouts.\n\nThe proxy daemon dropped 30 percent of customer login requests by returning status 503 responses towards 8 frontend instances."
    },

    # Sample 10: Memcached slab allocation pressure under flash sale traffic
    {
        "raw_asr": "uh memcached worker instances entered severe memory pressure when flash sale traffic drove slab allocat beyond forty eight gigabytes the caching daemon evicted eighty thousand catalog keys buy degrading p ninety five read latency from two milliseconds to ninety milliseconds across sixteen client threads",
        "refined_text": "Memcached worker instances entered severe memory pressure when flash sale traffic drove slab allocation beyond 48 gigabytes.\n\nThe caching daemon evicted 80000 catalog keys by degrading P95 read latency from 2 milliseconds to 90 milliseconds across 16 client threads."
    },

    # =========================================================================
    # TIER 3: LONG (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph \n\n structure (2-3 solid paragraphs).
    # Zero numbered checklist stereotypes. Natural spoken engineer narration.
    # =========================================================================

    # Sample 11: Kafka consumer group partition rebalance storm under ZooKeeper session timeout
    {
        "raw_asr": "uh at zero three twenty the streaming ingest pipeline experienced an originating flaw when zookeeper session timeouts triggered a partition rebalance storm across twelve kafka broker instances the underlying defect was a forty second garbage collection stall on the zookeeper leader which caused false heartbeat expirations on broker knowed five because broker knowed five dropped off the cluster registry the partition coordinator initiated concurrent leader elections buy migrating eight hundred partitions simultaneously which drove broker c p u utilization towards ninety eight percent producers and consumers encountered widespread timeout errors buy emitting status five hundred and status five hundred three responses across sixty application pods telemetry showed that p ninety nine publish latency spiked from four milliseconds to twenty five seconds while five million event records accumulated in ingestion buffers incident responders resolved the cluster instability buy isolating knowed five increasing zookeeper tick time towards four thousand milliseconds and staggering partition leadership migrations across sixteen worker instances",
        "refined_text": "At 0320 the streaming ingest pipeline experienced an originating flaw when ZooKeeper session timeouts triggered a partition rebalance storm across 12 Kafka broker instances. The underlying defect was a 40-second garbage collection stall on the ZooKeeper leader which caused false heartbeat expirations on broker node 5.\n\nBecause broker node 5 dropped off the cluster registry, the partition coordinator initiated concurrent leader elections by migrating 800 partitions simultaneously which drove broker CPU utilization towards 98 percent. Producers and consumers encountered widespread timeout errors by emitting status 500 and status 503 responses across 60 application pods. Telemetry showed that P99 publish latency spiked from 4 milliseconds to 25 seconds while 5000000 event records accumulated in ingestion buffers.\n\nIncident responders resolved the cluster instability by isolating node 5, increasing ZooKeeper tick time towards 4000 milliseconds, and staggering partition leadership migrations across 16 worker instances."
    },

    # Sample 12: PostgreSQL write-ahead log disk exhaustion caused by abandoned logical replication slot
    {
        "raw_asr": "um at zero seven fifteen the primary database cluster suffered an originating flaw when disk storage reached one hundred percent capacity on primary post gres knowed two the underlying defect was an abandoned logical replication slot from an offline analytics consumer which retained write ahead log segments across four days without reporting acknowledgment markers eighty gigabytes of unpurged w a l records saturated the local file system buy forcing the database engine into read only panic mode upstream checkout services failed buy generating status five hundred and status five hundred two errors towards forty web workers while p ninety nine transaction commit latency climbed from eight milliseconds to thirty seconds site reliability engineers remediated the storage outage buy dropping the abandoned replication slot via administrative s q l commands reclaiming seventy five gigabytes of disk space and resuming normal write operations across twenty database connections",
        "refined_text": "At 0715 the primary database cluster suffered an originating flaw when disk storage reached 100 percent capacity on primary Postgres node 2. The underlying defect was an abandoned logical replication slot from an offline analytics consumer which retained write-ahead log segments across 4 days without reporting acknowledgment markers.\n\nEighty gigabytes of unpurged WAL records saturated the local filesystem by forcing the database engine into read-only panic mode. Upstream checkout services failed by generating status 500 and status 502 errors towards 40 web workers while P99 transaction commit latency climbed from 8 milliseconds to 30 seconds.\n\nSite reliability engineers remediated the storage outage by dropping the abandoned replication slot via administrative SQL commands, reclaiming 75 gigabytes of disk space, and resuming normal write operations across 20 database connections."
    },

    # Sample 13: Kubernetes CNI IPAM IP exhaustion during cluster autoscaling event
    {
        "raw_asr": "basically at eleven forty five our application orchestration tier experienced an originating flaw when worker pods failed scheduling during a planned traffic burst the underlying defect was subnet address exhaustion inside the c n i i p a m plugin which depleted all two thousand allocated private addresses across three availability zones coober netties cluster autoscaler provisioned fifty new worker nodes but pods remained stuck in pending state buy failing network sandbox allocat twenty downstream microservices were unable two scale buy dropping sixty percent of incoming api calls with status five hundred three responses edge telemetry recorded p ninety five connection establishment delays of fifteen seconds while three hundred pods waited four network interfaces systems engineers mitigated the pod scheduling outage buy assigning two supplementary class c subnets towards the cluster virtual private cloud expanding address allocat towards eight thousand ips and restarting the c n i daemon across eighty nodes",
        "refined_text": "At 1145 our application orchestration tier experienced an originating flaw when worker pods failed scheduling during a planned traffic burst. The underlying defect was subnet address exhaustion inside the CNI IPAM plugin which depleted all 2000 allocated private addresses across 3 availability zones.\n\nKubernetes cluster autoscaler provisioned 50 new worker nodes but pods remained stuck in pending state by failing network sandbox allocation. Twenty downstream microservices were unable to scale by dropping 60 percent of incoming API calls with status 503 responses.\n\nEdge telemetry recorded P95 connection establishment delays of 15 seconds while 300 pods waited for network interfaces. Systems engineers mitigated the pod scheduling outage by assigning 2 supplementary Class C subnets towards the cluster virtual private cloud, expanding address allocation towards 8000 IPs, and restarting the CNI daemon across 80 nodes."
    },

    # Sample 14: HashiCorp Vault token renewal thundering herd overwhelming Consul storage backend
    {
        "raw_asr": "uh at fourteen ten the identity and secret management tier suffered an originating flaw when automated token renewal requests overwhelmed the storage backend the primary trigger was twenty thousand batch worker instances attempting two renew dynamic database leases simultaneously after an hourly cron execution lease renewal traffic generated twelve thousand write queries per second against the consul storage cluster buy driving disk fsync latency towards eight hundred milliseconds as consul became unresponsive vault worker daemons dropped eighty percent of client requests buy emitting status five hundred and status five hundred three errors towards fifty microservices telemetry alerted when p ninety nine token lookup latency jumped from five milliseconds to eighteen seconds while fifteen hundred auth requests queued in memory site reliability engineers resolved the secrets outage buy activating rate limiting on token renew endpoints staggering batch worker renewal intervals across thirty minutes and clearing four thousand expired lease entries",
        "refined_text": "At 1410 the identity and secret management tier suffered an originating flaw when automated token renewal requests overwhelmed the storage backend. The primary trigger was 20000 batch worker instances attempting to renew dynamic database leases simultaneously after an hourly cron execution.\n\nLease renewal traffic generated 12000 write queries per second against the Consul storage cluster by driving disk fsync latency towards 800 milliseconds. As Consul became unresponsive, Vault worker daemons dropped 80 percent of client requests by emitting status 500 and status 503 errors towards 50 microservices.\n\nTelemetry alerted when P99 token lookup latency jumped from 5 milliseconds to 18 seconds while 1500 auth requests queued in memory. Site reliability engineers resolved the secrets outage by activating rate limiting on token renew endpoints, staggering batch worker renewal intervals across 30 minutes, and clearing 4000 expired lease entries."
    },

    # Sample 15: Redis cluster split-brain failover oscillation under network jitter
    {
        "raw_asr": "um at zero six thirty the distributed session caching layer experienced an originating flaw when network packet loss caused split brain failover oscillation across three redis cluster shards the underlying defect was an asymmetric thirty percent packet drop between availability zone one and availability zone two which disrupted cluster gossip heartbeat communicat sentinel daemons on knowed seven and knowed nine concurrently promoted conflicting replica nodes towards master roles buy splitting transaction write streams fifteen thousand active user checkout sessions failed buy emitting status five hundred and status five hundred two responses across forty application workers telemetry indicated that p ninety five cache lookup latency rose from one millisecond to six seconds while fifty cluster failover votes were cast within twelve minutes infrastructure engineers restored cluster stabilit buy resetting sentinel leader quorum requirements isolating knowed nine from the cluster topology and resynchronizing replica data across six storage nodes",
        "refined_text": "At 0630 the distributed session caching layer experienced an originating flaw when network packet loss caused split-brain failover oscillation across 3 Redis cluster shards. The underlying defect was an asymmetric 30 percent packet drop between availability zone 1 and availability zone 2 which disrupted cluster gossip heartbeat communication.\n\nSentinel daemons on node 7 and node 9 concurrently promoted conflicting replica nodes towards master roles by splitting transaction write streams. 15000 active user checkout sessions failed by emitting status 500 and status 502 responses across 40 application workers.\n\nTelemetry indicated that P95 cache lookup latency rose from 1 millisecond to 6 seconds while 50 cluster failover votes were cast within 12 minutes. Infrastructure engineers restored cluster stability by resetting Sentinel leader quorum requirements, isolating node 9 from the cluster topology, and resynchronizing replica data across 6 storage nodes."
    },

    # Sample 16: ClickHouse merge tree part mutation explosion stalling analytical ingestion
    {
        "raw_asr": "basically at sixteen forty our real time telemetry warehouse suffered an originating flaw when table part mutations overwhelmed the storage engine on clickhouse worker knowed three the underlying defect was an unthrottled alter update query executed across forty million telemetry rows which spawned twelve thousand unmerged data parts on disk storage clickhouse background merge threads saturated all twenty four c p u cores buy attempting two merge fragmented parts simultaneously while disk queue depth climbed towards ninety requests concurrent insert queries failed buy throwing table part limit exceeded exceptions and returning status five hundred errors towards thirty data collectors p ninety nine ingestion delay climbed from three seconds to forty five minutes while eighty gigabytes of metrics buffered on edge forwarders data platform engineers mitigated the analytical pipeline outage buy pausing asynchronous part mutations setting maximum parts in alter part towards one hundred and restarting merge threads across eight storage workers",
        "refined_text": "At 1640 our real-time telemetry warehouse suffered an originating flaw when table part mutations overwhelmed the storage engine on ClickHouse worker node 3. The underlying defect was an unthrottled alter update query executed across 40000000 telemetry rows which spawned 12000 unmerged data parts on disk storage.\n\nClickHouse background merge threads saturated all 24 CPU cores by attempting to merge fragmented parts simultaneously while disk queue depth climbed towards 90 requests. Concurrent insert queries failed by throwing table part limit exceeded exceptions and returning status 500 errors towards 30 data collectors.\n\nP99 ingestion delay climbed from 3 seconds to 45 minutes while 80 gigabytes of metrics buffered on edge forwarders. Data platform engineers mitigated the analytical pipeline outage by pausing asynchronous part mutations, setting maximum parts in alter part towards 100, and restarting merge threads across 8 storage workers."
    },

    # Sample 17: Elasticsearch circuit breaker parent exception tripping during concurrent aggregations on unindexed fields
    {
        "raw_asr": "uh at ten twenty our search and discovery cluster experienced an originating flaw when parent circuit breaker exceptions tripped across six elasticsearch data nodes the underlying defect was a batch of ten concurrent nested aggregation queries targeting unindexed string fields which allocated thirty two gigabytes of j v m heap within four seconds the parent circuit breaker halted further query processing buy triggering memory limit exceeded exceptions on knowed four and knowed six because indexing threads shared the saturated heap bulk ingestion pipelines stalled buy dropping forty thousand document indexing requests with status four hundred twenty nine and status five hundred errors p ninety five search response time surged from twenty milliseconds to twelve seconds across fifty customer search endpoints site reliability engineers restored cluster health buy canceling the long running aggregation requests resetting cluster circuit breaker limits towards eighty five percent and adding fielddata disabled configurations across eight search indices",
        "refined_text": "At 1020 our search and discovery cluster experienced an originating flaw when parent circuit breaker exceptions tripped across 6 Elasticsearch data nodes. The underlying defect was a batch of 10 concurrent nested aggregation queries targeting unindexed string fields which allocated 32 gigabytes of JVM heap within 4 seconds.\n\nThe parent circuit breaker halted further query processing by triggering memory limit exceeded exceptions on node 4 and node 6. Because indexing threads shared the saturated heap, bulk ingestion pipelines stalled by dropping 40000 document indexing requests with status 429 and status 500 errors.\n\nP95 search response time surged from 20 milliseconds to 12 seconds across 50 customer search endpoints. Site reliability engineers restored cluster health by canceling the long-running aggregation requests, resetting cluster circuit breaker limits towards 85 percent, and adding fielddata disabled configurations across 8 search indices."
    },

    # Sample 18: Apache Flink checkpoint barrier alignment timeout in stream processing pipeline
    {
        "raw_asr": "um at twelve fifty our stream processing pipeline suffered an originating flaw when distributed checkpoint alignments timed out across eight flink task managers the underlying defect was an unhandled data skew condition in partition stream seven where one worker received thirty thousand events per second while remaining workers processed five hundred events per second downstream alignment buffers became saturated buy delaying checkpoint barrier acknowledgments past the configured sixty second timeout when five consecutive checkpoints failed flink cluster master terminat the streaming job buy triggering crash restart loops across twenty worker containers ingestion lag accumulated towards sixty million records buy causing status five hundred three responses across thirty event producers operations engineers remediated the streaming failure buy increasing checkpoint timeout towards five minutes adding backpressure throttling on stream seven and scaling task manager instances towards sixteen workers",
        "refined_text": "At 1250 our stream processing pipeline suffered an originating flaw when distributed checkpoint alignments timed out across 8 Flink task managers. The underlying defect was an unhandled data skew condition in partition stream 7 where one worker received 30000 events per second while remaining workers processed 500 events per second.\n\nDownstream alignment buffers became saturated by delaying checkpoint barrier acknowledgments past the configured 60-second timeout. When 5 consecutive checkpoints failed, Flink cluster master terminated the streaming job by triggering crash restart loops across 20 worker containers.\n\nIngestion lag accumulated towards 60000000 records by causing status 503 responses across 30 event producers. Operations engineers remediated the streaming failure by increasing checkpoint timeout towards 5 minutes, adding backpressure throttling on stream 7, and scaling task manager instances towards 16 workers."
    },

    # Sample 19: Linux kernel epoll file descriptor table exhaustion on API gateway
    {
        "raw_asr": "basically at fifteen thirty five our edge api gateway encountered an originating flaw when linux kernel file descriptor tables exhausted maximum limits on gateway knowed two and knowed four the underlying defect was an unclosed t c p connection leak inside the upstream r p c connection pool which accumulated one hundred twenty thousand abandoned file descriptors over six hours because the operating system could not allocat new sockets the kernel silently rejected incoming connection requests buy triggering connection reset errors towards thirty downstream clients edge telemetry recorded an eighty percent drop in gateway throughput while status five hundred two and status five hundred four errors surged across forty public endpoints p ninety nine handshake latency spiked from five milliseconds to twenty seconds during the connection dropouts systems engineers resolved the gateway outage buy raising the system wide file max limit towards five hundred twelve thousand restarting gateway worker daemons and implementing socket timeout recycling across twelve proxy processes",
        "refined_text": "At 1535 our edge API gateway encountered an originating flaw when Linux kernel file descriptor tables exhausted maximum limits on gateway node 2 and node 4. The underlying defect was an unclosed TCP connection leak inside the upstream RPC connection pool which accumulated 120000 abandoned file descriptors over 6 hours.\n\nBecause the operating system could not allocate new sockets, the kernel silently rejected incoming connection requests by triggering connection reset errors towards 30 downstream clients. Edge telemetry recorded an 80 percent drop in gateway throughput while status 502 and status 504 errors surged across 40 public endpoints.\n\nP99 handshake latency spiked from 5 milliseconds to 20 seconds during the connection dropouts. Systems engineers resolved the gateway outage by raising the system-wide file-max limit towards 512000, restarting gateway worker daemons, and implementing socket timeout recycling across 12 proxy processes."
    },

    # Sample 20: gRPC connection pool starvation under HTTP/2 stream multiplexing stall
    {
        "raw_asr": "uh at nineteen zero five our internal microservice fabric suffered an originating flaw when g r p c transport channels stalled under heavy payload contention on knowed six the underlying defect was an unhandled h t t p two stream window exhaustion bug where large serialization payloads filled sixty four kilobyte flow control windows without replenishing window update frames because concurrent r p c calls shared a single multiplexed channel forty client worker pods blocked waiting four transport buffers buy driving thread pool utilization towards one hundred percent downstream checkout services failed buy returning status five hundred and status five hundred three responses across twenty five public apis p ninety five r p c response time climbed from twelve milliseconds to sixteen seconds while ten thousand requests backed up in client queues infrastructure engineers remediated the transport stall buy increasing the h t t p two initial window size towards one megabyte configuring four independent subchannels per backend knowed and restarting client daemons across thirty worker nodes",
        "refined_text": "At 1905 our internal microservice fabric suffered an originating flaw when gRPC transport channels stalled under heavy payload contention on node 6. The underlying defect was an unhandled HTTP 2 stream window exhaustion bug where large serialization payloads filled 64-kilobyte flow control windows without replenishing window update frames.\n\nBecause concurrent RPC calls shared a single multiplexed channel, 40 client worker pods blocked waiting for transport buffers by driving thread pool utilization towards 100 percent. Downstream checkout services failed by returning status 500 and status 503 responses across 25 public APIs.\n\nP95 RPC response time climbed from 12 milliseconds to 16 seconds while 10000 requests backed up in client queues. Infrastructure engineers remediated the transport stall by increasing the HTTP 2 initial window size towards 1 megabyte, configuring 4 independent subchannels per backend node, and restarting client daemons across 30 worker nodes."
    }
]

print(f"Total pairs: {len(pairs)}")
assert len(pairs) == 20

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

tiers = {"short": 0, "medium": 0, "long": 0}

for idx, p in enumerate(pairs):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json"

    # Validator pair check
    val_ok, val_reason = validator.validate_pair(p)
    if not val_ok:
        print(f"FAILED validate_pair at sample {idx+1}: {val_reason}")
        print("RAW:", raw)
        print("REF:", ref)
        sys.exit(1)

    # Cleaner check
    clean_res, clean_status = cleaner.clean_sample(raw, ref)
    if not clean_res or clean_status != "kept":
        print(f"FAILED clean_sample at sample {idx+1}: {clean_status}")
        print("RAW:", raw)
        print("REF:", ref)
        sys.exit(1)

    # Tier check
    w_count = len(ref.split())
    if w_count < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} short has newline"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} short has {len(sentences)} sentences, expected 1"
    elif w_count < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} medium has {len(sentences)} sentences, expected 1-3"
        assert "\n\n" in ref, f"Sample {idx+1} medium missing \\n\\n"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} long missing \\n\\n"

print(f"Tier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

# Validator batch check
batch_ok, batch_reason, batch_tiers = validator.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
if not batch_ok:
    print(f"FAILED validate_batch: {batch_reason}")
    sys.exit(1)

print("Batch check passed:", batch_tiers)

# Write to scratch/subagent_batch_85.json
out_path = Path("scratch/subagent_batch_85.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"Successfully saved 20 pairs to {out_path}")
