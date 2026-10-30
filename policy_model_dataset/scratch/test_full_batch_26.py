import json
import sys
sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
  # --- TIER 1: SHORT (<25 words, exactly 1 sentence, 0 newlines) --- Exactly 4 samples
  # Sample 1: Distributed caching (write-through vs write-back)
  {
    "raw_asr": "basically right through caching updates the database and cache synchronizat in ten wait five milliseconds",
    "refined_text": "Write-through caching updates the database and cache synchronization in 5 milliseconds."
  },
  # Sample 2: Database sharding key selection
  {
    "raw_asr": "um hashing tenant identifiers distributes database partit load evenly across four wait eight database knowed instances buy request volume",
    "refined_text": "Hashing tenant identifiers distributes database partition load evenly across 8 database node instances by request volume."
  },
  # Sample 3: Raft consensus
  {
    "raw_asr": "basically r a f t consensus protocols arbitrat leader election timeouts buy incrementing terms every fifty wait one hundred milliseconds",
    "refined_text": "Raft consensus protocols arbitrate leader election timeouts by incrementing terms every 100 milliseconds."
  },
  # Sample 4: gRPC streaming
  {
    "raw_asr": "uh bidirectional g r p c streaming cuts packet transmiss overhead four telemetry pipelines buy multiplexing two wait four channels",
    "refined_text": "Bidirectional gRPC streaming cuts packet transmission overhead for telemetry pipelines by multiplexing 4 channels."
  },

  # --- TIER 2: MEDIUM (25-90 words, 1-3 sentences, natural \n\n) --- Exactly 6 samples
  # Sample 5: Kafka vs RabbitMQ
  {
    "raw_asr": "basically our event sourcing r f c compared k a f k a against rabbit m q four financial audit logs k a f k a retains immutable event streams four ten wait thirty days buy storing ordered partition logs um in contrast rabbit m q deletes messages immediately after consumer acknowledgement which breaks asynchronous event replayability across downstream reporting services",
    "refined_text": "Our event-driven RFC compared Kafka against RabbitMQ for financial audit logs. Kafka retains immutable event streams for 30 days by storing ordered partition logs.\n\nIn contrast, RabbitMQ deletes messages immediately after consumer acknowledgement, which breaks asynchronous event replayability across downstream reporting services."
  },
  # Sample 6: Distributed caching (write-through vs write-back)
  {
    "raw_asr": "basically our distributed caching evaluation rejected right back caching four user profile data because dirty cache entries risk data loss during knowed crashes um configur right through caching updates redis and post gres synchronously buy holding database locks four five wait sixty milliseconds which stabilizes data integrity across web tiers",
    "refined_text": "Our distributed caching evaluation rejected write-back caching for user profile data because dirty cache entries risk data loss during node crashes.\n\nConfiguring write-through caching updates Redis and PostgreSQL synchronously by holding database locks for 60 milliseconds, which stabilizes data integrity across web tiers."
  },
  # Sample 7: GraphQL federation vs REST gateways
  {
    "raw_asr": "okay so our a p i architecture working group evaluat graph q l federation against centralized r e s t gateways four mobile client queries uh graph q l subgraph composition reduced network round trips buy resolving complex user entities in a single graph request dropping client latency from two hundred wait eighty milliseconds",
    "refined_text": "Our API architecture working group evaluated GraphQL federation against centralized REST gateways for mobile client queries.\n\nGraphQL subgraph composition reduced network round trips by resolving complex user entities in a single graph request, dropping client latency from 80 milliseconds."
  },
  # Sample 8: Database sharding key selection
  {
    "raw_asr": "basically selecting raw tenant uuid as the primary database sharding key caused severe hot partition bottlenecks on large enterprise accounts um migrating two a composite sharding key combining tenant identifier and creation date distributes records across sixteen wait thirty two database shards buy balancing write traffic evenly",
    "refined_text": "Selecting raw tenant UUID as the primary database sharding key caused severe hot partition bottlenecks on large enterprise accounts.\n\nMigrating to a composite sharding key combining tenant identifier and creation date distributes records across 32 database shards by balancing write traffic evenly."
  },
  # Sample 9: Raft consensus
  {
    "raw_asr": "basically the distributed storage r f c mandated r a f t consensus across five wait three control plane replicas two maintain state machine consistency um the leader election protocol arbitrat split brain partitions buy requiring a strict majority quorum before committing append entries log updates",
    "refined_text": "The distributed storage RFC mandated Raft consensus across 3 control plane replicas to maintain state machine consistency.\n\nThe leader election protocol arbitrates split-brain partitions by requiring a strict majority quorum before committing append entries log updates."
  },
  # Sample 10: Tiered data lifecycles
  {
    "raw_asr": "okay so our telemetry storage a d r defined automated lifecycle policies moving cold observability metrics from local n v m e drives two s three object buckets after thirty wait ninety days um automated background jobs compress historical chunks buy merging columnar files without interrupting active analytical queries",
    "refined_text": "Our telemetry storage ADR defined automated lifecycle policies moving cold observability metrics from local NVMe drives to S3 object buckets after 90 days.\n\nAutomated background jobs compress historical chunks by merging columnar files without interrupting active analytical queries."
  },

  # --- TIER 3: LONG (90+ words, multi-paragraph \n\n) --- Exactly 10 samples
  # Sample 11: Kafka vs RabbitMQ
  {
    "raw_asr": "basically our architecture review evaluat k a f k a against rabbit m q four our immutable ledger event store rabbit m q provides flexible topic exchange routing and transient queueing but lacks persistent append only event logs financial compliance requires deterministic event playback from any arbitrary offset um k a f k a partitions store immutable commit logs with configurable retent windows benchmarking consumer replay throughput showed k a f k a processed one hundred thousand events per second during failure recovery under peak transact load across distributed ledger knowed instances whereas rabbit m q required manual dead letter queue reprocessing okay so the architecture committee approved k a f k a four event sourcing core transactions while retaining rabbit m q four transient notificat delivery across customer notification workers",
    "refined_text": "Our architecture review evaluated Kafka against RabbitMQ for our immutable ledger event store. RabbitMQ provides flexible topic exchange routing and transient queueing, but lacks persistent append-only event logs. Financial compliance requires deterministic event playback from any arbitrary offset.\n\nKafka partitions store immutable commit logs with configurable retention windows. Benchmarking consumer replay throughput showed Kafka processed 100000 events per second during failure recovery under peak transaction load across distributed ledger node instances, whereas RabbitMQ required manual dead-letter queue reprocessing.\n\nThe architecture committee approved Kafka for event sourcing core transactions, while retaining RabbitMQ for transient notification delivery across customer notification workers."
  },
  # Sample 12: Write-through vs write-back caching
  {
    "raw_asr": "basically evaluat caching strategies four high frequency inventory counters across our e commerce catalog during peak traffic hours right back caching absorbs massive write spikes buy deferring database updates two asynchronous background flushes however unexpected cache knowed failures risk silent loss of uncommitted inventory deductions um right through caching updates redis and our post gres database synchronously inside a single transactional block while this adds ten wait fifteen milliseconds of latency two checkout requests it guarantees consistent inventory counts across distributed read replicas okay so the architectural board approved right through caching four checkout reservations while adopting right around caching four high volume read only product descriptions across edge knowed clusters",
    "refined_text": "Evaluating caching strategies for high-frequency inventory counters across our e-commerce catalog during peak traffic hours, write-back caching absorbs massive write spikes by deferring database updates to asynchronous background flushes. However, unexpected cache node failures risk silent loss of uncommitted inventory deductions.\n\nWrite-through caching updates Redis and our PostgreSQL database synchronously inside a single transactional block. While this adds 15 milliseconds of latency to checkout requests, it guarantees consistent inventory counts across distributed read replicas.\n\nThe architectural board approved write-through caching for checkout reservations, while adopting write-around caching for high-volume read-only product descriptions across edge node clusters."
  },
  # Sample 13: Database sharding key selection
  {
    "raw_asr": "basically investigating database sharding key strategies across our distributed billing platform sharding solely buy tenant identifier caused severe read hotspots because our three largest enterprise tenants generated sixty percent of all analytical queries on shard one um we evaluat range based sharding against composite hash sharding range sharding partit records buy billing cycle dates but directed all recent invoice writes two a single active database shard a composite key combining tenant identifier with account creation year distributes query volume uniformly across thirty two wait sixty four database shards okay so the infrastructure team implemented composite hash sharding with virtual partitions reducing peak shard c p u utiliz from eighty five percent two twenty five percent during end of month invoicing",
    "refined_text": "Investigating database sharding key strategies across our distributed billing platform, sharding solely by tenant identifier caused severe read hotspots because our 3 largest enterprise tenants generated 60% of all analytical queries on Shard 1.\n\nWe evaluated range-based sharding against composite hash sharding. Range sharding partitioned records by billing cycle dates, but directed all recent invoice writes to a single active database shard. A composite key combining tenant identifier with account creation year distributes query volume uniformly across 64 database shards.\n\nThe infrastructure team implemented composite hash sharding with virtual partitions, reducing peak shard CPU utilization from 85% to 25% during end-of-month invoicing."
  },
  # Sample 14: Raft consensus
  {
    "raw_asr": "basically reviewing distributed consensus performance across our distributed key value metadata store a single r a f t consensus group encountered disk input output bottlenecks when synchronizing write ahead logs across five control plane knowed instances serializing all cluster operations through one r a f t leader capped cluster throughput at four thousand operations per second um we transitioned two a multi r a f t partition architecture where independent r a f t consensus groups manage dedicated key ranges tuning leader election heartbeat intervals two one hundred fifty milliseconds and lease timeouts two four hundred fifty milliseconds eliminated spurious leader step downs during temporary network blips okay so this multi r a f t design scaled cluster throughput two fifty thousand operations per second while maintaining strong linearizable consistency across cross region network partitions",
    "refined_text": "Reviewing distributed consensus performance across our distributed key-value metadata store, a single Raft consensus group encountered disk input-output bottlenecks when synchronizing write-ahead logs across 5 control plane node instances. Serializing all cluster operations through one Raft leader capped cluster throughput at 4000 operations per second.\n\nWe transitioned to a multi-Raft partition architecture where independent Raft consensus groups manage dedicated key ranges. Tuning leader election heartbeat intervals to 150 milliseconds and lease timeouts to 450 milliseconds eliminated spurious leader step-downs during temporary network blips.\n\nThis multi-Raft design scaled cluster throughput to 50000 operations per second while maintaining strong linearizable consistency across cross-region network partitions."
  },
  # Sample 15: GraphQL federation vs REST gateways
  {
    "raw_asr": "basically comparing graph q l federation against monolithic r e s t gateways four our mobile client backend the existing r e s t gateway had two root client requests across eight downstream microservices producing over three hundred fifty milliseconds of network latency on mobile networks um graph q l federation delegates client queries two an apollo gateway that composes individual service subgraphs into a unified schema the federated gateway resolves nested entity dependencies in parallel using dataloader batching which eliminates n plus one query cascades across user profile services okay so the r f c working group adopted graph q l federation cutting median mobile response times two ninety milliseconds and reducing payload transfer size buy forty five percent through client specified field select",
    "refined_text": "Comparing GraphQL federation against monolithic REST gateways for our mobile client backend, the existing REST gateway had to route client requests across 8 downstream microservices, producing over 350 milliseconds of network latency on mobile networks.\n\nGraphQL federation delegates client queries to an Apollo gateway that composes individual service subgraphs into a unified schema. The federated gateway resolves nested entity dependencies in parallel using dataloader batching, which eliminates N plus 1 query cascades across user profile services.\n\nThe RFC working group adopted GraphQL federation, cutting median mobile response times to 90 milliseconds and reducing payload transfer size by 45% through client-specified field selection."
  },
  # Sample 16: gRPC streaming
  {
    "raw_asr": "basically benchmarking g r p c communicat streaming protocols against periodic h t t p polling four real time telemetry pipelines the legacy architecture polled r e s t endpoints every five hundred milliseconds across ten thousand connected gateway knowed instances creating excessive t l s handshake overhead and server connection churn um bidirectional g r p c streaming multiplexes continuous sensor telemetry over long lived h t t p two t c p transport connections binary protocol buffer serialization reduced telemetry payload size buy sixty percent compared two j s o n encoding while server streaming enabled instant push delivery of remote configur updates okay so the architecture review approved bidirectional g r p c streaming lowering gateway bandwidth consumpt two twenty megabytes per hour and sustaining eighty thousand concurrent streaming connections per ingest cluster",
    "refined_text": "Benchmarking gRPC communication streaming protocols against periodic HTTP polling for real-time telemetry pipelines, the legacy architecture polled REST endpoints every 500 milliseconds across 10000 connected gateway node instances, creating excessive TLS handshake overhead and server connection churn.\n\nBidirectional gRPC streaming multiplexes continuous sensor telemetry over long-lived HTTP/2 TCP transport connections. Binary protocol buffer serialization reduced telemetry payload size by 60% compared to JSON encoding, while server streaming enabled instant push delivery of remote configuration updates.\n\nThe architecture review approved bidirectional gRPC streaming, lowering gateway bandwidth consumption to 20 megabytes per hour and sustaining 80000 concurrent streaming connections per ingest cluster."
  },
  # Sample 17: Tiered data lifecycles
  {
    "raw_asr": "basically designing tiered data lifecycle policies across our distributed observability log platform retaining thirty days of raw log indices on local n v m e solid state storage exhausted hardware capacity and forced premature storage hardware expansions across our forty knowed cluster um under the approved storage tiering policy hot log partitions remain on local n v m e disks four seven days two deliver sub second query latency four active incident troubleshooting background worker threads compress older partition parts into columnar parquet files and transfer them two cold s three object storage tiers okay so this automated lifecycle policy reduced n v m e storage consumpt buy seventy percent while keeping historical analytical query latency under three seconds using local columnar mark index caching",
    "refined_text": "Designing tiered data lifecycle policies across our distributed observability log platform, retaining 30 days of raw log indices on local NVMe solid-state storage exhausted hardware capacity and forced premature storage hardware expansions across our 40 node cluster.\n\nUnder the approved storage tiering policy, hot log partitions remain on local NVMe disks for 7 days to deliver sub-second query latency for active incident troubleshooting. Background worker threads compress older partition parts into columnar parquet files and transfer them to cold S3 object storage tiers.\n\nThis automated lifecycle policy reduced NVMe storage consumption by 70%, while keeping historical analytical query latency under 3 seconds using local columnar mark index caching."
  },
  # Sample 18: Multi-Paxos vs Raft consensus
  {
    "raw_asr": "basically evaluat multi paxos against r a f t consensus protocols four our cross region metadata coordination service r a f t enforces strict leader driven log sequencing which incurs round trip cross region network latency whenever clients submit write requests two non leader follower knowed instances um multi paxos allows decentralized proposals from local replica knowed instances reducing write latency in stable state deployments however recovering from complex multi knowed network partitions in multi paxos introduced subtle state machine edge cases and extensive operational debugging overhead compared two r a f t deterministic leader election okay so the distributed systems team selected multi r a f t with localized follower reads establishing predictable failover recovery in three hundred milliseconds while keeping engineering maintenance complexity manageable",
    "refined_text": "Evaluating multi-Paxos against Raft consensus protocols for our cross-region metadata coordination service, Raft enforces strict leader-driven log sequencing, which incurs round-trip cross-region network latency whenever clients submit write requests to non-leader follower node instances.\n\nMulti-Paxos allows decentralized proposals from local replica node instances, reducing write latency in stable state deployments. However, recovering from complex multi-node network partitions in multi-Paxos introduced subtle state machine edge cases and extensive operational debugging overhead compared to Raft's deterministic leader election.\n\nThe distributed systems team selected multi-Raft with localized follower reads, establishing predictable failover recovery in 300 milliseconds while keeping engineering maintenance complexity manageable."
  },
  # Sample 19: Event-driven architecture (Transactional Outbox Debezium vs RabbitMQ)
  {
    "raw_asr": "basically resolving distributed consistency challenges in our order checkout processing pipeline the original implement attempted dual writes writing checkout records two the relational database while publishing message payloads directly two rabbit m q network timeouts during message publishing frequently produced phantom orders and ledger discrepancies um we adopted the transactional outbox pattern paired with debezium change data capture the checkout service inserts order states and outbox events within a single local database transact debezium reads the database transact log directly and streams verified events into k a f k a topic partitions okay so this architectural design eliminated dual write inconsistencies delivering guaranteed at least once message delivery across downstream inventory reservat and billing services without distributed two phase commit overhead",
    "refined_text": "Resolving distributed consistency challenges in our order checkout processing pipeline, the original implementation attempted dual writes, writing checkout records to the relational database while publishing message payloads directly to RabbitMQ. Network timeouts during message publishing frequently produced phantom orders and ledger discrepancies.\n\nWe adopted the transactional outbox pattern paired with Debezium change data capture. The checkout service inserts order states and outbox events within a single local database transaction. Debezium reads the database transaction log directly and streams verified events into Kafka topic partitions.\n\nThis architectural design eliminated dual-write inconsistencies, delivering guaranteed at-least-once message delivery across downstream inventory reservation and billing services without distributed 2-phase commit overhead."
  },
  # Sample 20: Consistent hashing vs range sharding
  {
    "raw_asr": "basically assessing consistent hashing against directory based sharding four our global user session database directory based range sharding mapped user identifier prefixes two specific database instances but required frequent manual schema migrations and routing table reconfigurations whenever user registrations spiked in particular geographic regions um consistent hashing with two hundred fifty six virtual knowed points per physical database shard distributes session partitions across our sixteen knowed database cluster when provisioning additional database knowed instances during traffic growth consistent hash ring topologies only rebalance ten percent of existing user session keys rather than redistributing the entire dataset okay so the database steering committee approved consistent hashing with deterministic murmur three hash rings reducing shard rebalancing migration times from twelve hours two forty minutes without service downtime",
    "refined_text": "Assessing consistent hashing against directory-based sharding for our global user session database, directory-based range sharding mapped user identifier prefixes to specific database instances, but required frequent manual schema migrations and routing table reconfigurations whenever user registrations spiked in particular geographic regions.\n\nConsistent hashing with 256 virtual node points per physical database shard distributes session partitions across our 16 node database cluster. When provisioning additional database node instances during traffic growth, consistent hash ring topologies only rebalance 10% of existing user session keys rather than redistributing the entire dataset.\n\nThe database steering committee approved consistent hashing with deterministic Murmur3 hash rings, reducing shard rebalancing migration times from 12 hours to 40 minutes without service downtime."
  }
]

print(f"Auditing {len(batch)} samples...\n")
all_ok = True
for i, s in enumerate(batch, 1):
    v_ok, v_err = validate_pair(s)
    c_res, c_err = clean_sample(s["raw_asr"], s["refined_text"])
    w = len(s["refined_text"].split())
    raw_w = len(s["raw_asr"].split())
    ratio = w / max(1, raw_w)
    status = "PASS" if v_ok and c_res is not None else "FAIL"
    if not (v_ok and c_res is not None):
        all_ok = False
    print(f"Sample {i:02d}: [{status}] ({w}w ref, {raw_w}w raw, ratio {ratio:.2f})")
    if not v_ok:
        print(f"  Validator failure: {v_err}")
    if c_res is None:
        print(f"  Cleaner failure: {c_err}")

b_ok, b_err, b_counts = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_err}")
print(f"Tier counts: {b_counts}")
print(f"Overall status: {'ALL PASS (20/20)' if all_ok and b_ok else 'AUDIT FAILED'}")

if all_ok and b_ok:
    with open("scratch/subagent_batch_26.json", "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print("Saved batch to scratch/subagent_batch_26.json")
