import json
import sys
from pathlib import Path

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
    # ==========================================
    # TIER 1: SHORT (< 25 words) - 4 samples
    # ==========================================
    # Sample 1: Saga vs 2PC
    {
        "raw_asr": "adopt saga orchestrat instead of two phase commit two eliminate distributed lock stalls across thirty microservices",
        "refined_text": "Adopt Saga orchestration instead of two-phase commit to eliminate distributed lock stalls across 30 microservices."
    },
    # Sample 2: Rate Limiting Token Bucket
    {
        "raw_asr": "our r f c selected the token bucket algorithm two manage burst traffic buy allocat twenty tokens per second",
        "refined_text": "Our RFC selected the token bucket algorithm to manage burst traffic by allocating 20 tokens per second."
    },
    # Sample 3: Storage Engine LSM-tree
    {
        "raw_asr": "uh our storage a d r recommended an l s m tree engine two reduce write amplificat under twelve thousand writes per second",
        "refined_text": "Our storage ADR recommended an LSM-tree engine to reduce write amplification under 12000 writes per second."
    },
    # Sample 4: PgBouncer Connection Pooling
    {
        "raw_asr": "basically configur post gres connection pooling in transaction mode two handle eight hundred concurrent client connections",
        "refined_text": "Configure Postgres connection pooling in transaction mode to handle 800 concurrent client connections."
    },

    # ==========================================
    # TIER 2: MEDIUM (25-89 words) - 6 samples
    # ==========================================
    # Sample 5: Idempotency Keys ADR
    {
        "raw_asr": "our payment gateway a d r mandat an idempotency key header on all mutation endpoints two prevent duplicate charge submissions buy verifying payload hashes um redis caches the initial transaction response four twenty four hours and rejects concurrent replay attempts within a three second window",
        "refined_text": "Our payment gateway ADR mandated an idempotency key header on all mutation endpoints to prevent duplicate charge submissions by verifying payload hashes.\n\nRedis caches the initial transaction response for 24 hours and rejects concurrent replay attempts within a 3-second window."
    },
    # Sample 6: Debezium CDC RFC
    {
        "raw_asr": "our data pipeline r f c evaluat debezium change data capture against scheduled polling queries across fifty production database tables uh polling caused persistent lock contention on high volume audit logs while debezium streams w a l events directly into k af ka within ten milliseconds",
        "refined_text": "Our data pipeline RFC evaluated Debezium change data capture against scheduled polling queries across 50 production database tables.\n\nPolling caused persistent lock contention on high-volume audit logs, while Debezium streams WAL events directly into Kafka within 10 milliseconds."
    },
    # Sample 7: Consistent Hashing Ring ADR
    {
        "raw_asr": "basically our distributed caching design document adopted consistent hashing with two hundred fifty six virtual nodes per cache host two balance key distributions um when adding or removing a cluster knowed wait adding a cache host consistent hashing migrat only four percent of cached keys instead of invalidating the entire fleet",
        "refined_text": "Our distributed caching design document adopted consistent hashing with 256 virtual nodes per cache host to balance key distributions.\n\nWhen adding a cache host, consistent hashing migrates only 4 percent of cached keys instead of invalidating the entire fleet."
    },
    # Sample 8: Circuit Breaker RFC
    {
        "raw_asr": "our resilience architecture r f c specifi automated circuit breakers across forty g r p c downstream clients buy tracking consecutive connection failures uh the circuit opens after five failed attempts immediately failing calls four fifteen seconds before transitioning two half open state four health probing",
        "refined_text": "Our resilience architecture RFC specified automated circuit breakers across 40 gRPC downstream clients by tracking consecutive connection failures.\n\nThe circuit opens after 5 failed attempts, immediately failing calls for 15 seconds before transitioning to half-open state for health probing."
    },
    # Sample 9: Hybrid Logical Clocks ADR
    {
        "raw_asr": "basically our distributed transaction a d r adopted hybrid logical clocks instead of physical n t p timestamps across twelve distributed datacenters um hybrid clocks combine physical time with monotonic logical counters bounding causal drift within fifty milliseconds without requiring atomic hardware clocks",
        "refined_text": "Our distributed transaction ADR adopted Hybrid Logical Clocks instead of physical NTP timestamps across 12 distributed datacenters.\n\nHybrid clocks combine physical time with monotonic logical counters, bounding causal drift within 50 milliseconds without requiring atomic hardware clocks."
    },
    # Sample 10: Tail-Based Tracing Sampling RFC
    {
        "raw_asr": "our observability r f c replaced head based tracing sampling with tail based sampling across thirty two open telemetry collector instances uh collectors buffer all span traces in memory four thirty seconds retaining one hundred percent of traces that contain h t t p error codes or exceed five hundred milliseconds latency",
        "refined_text": "Our observability RFC replaced head-based tracing sampling with tail-based sampling across 32 OpenTelemetry collector instances.\n\nCollectors buffer all span traces in memory for 30 seconds, retaining 100 percent of traces that contain HTTP error codes or exceed 500 milliseconds latency."
    },

    # ==========================================
    # TIER 3: LONG (90+ words) - 10 samples
    # ==========================================
    # Sample 11: Storage Engine Selection: RocksDB vs InnoDB
    {
        "raw_asr": "our metrics platform storage r f c evaluat rocks d b against inno d b four ingesting five hundred thousand metric data points per second across our telemetry cluster in baseline benchmarks with thirty two ingestion workers inno d b suffered heavy random disk i o and write lock stalls during b plus tree page splits elevating p nine nine write latency two one hundred eighty milliseconds um the r f c recommended rocks d b using an l s m tree storage engine with tiered compaction workers append incoming telemetry records two an in memory memtable and sequential right ahead log before flushing immutable s s tables two disk storage canary evaluations on eight storage knowed instances demonstrated that rocks d b reduced write amplificat from twenty eight down two four sustaining six hundred thousand writes per second while reducing s s d wear buy sixty five percent",
        "refined_text": "Our metrics platform storage RFC evaluated RocksDB against InnoDB for ingesting 500000 metric data points per second across our telemetry cluster. In baseline benchmarks with 32 ingestion workers, InnoDB suffered heavy random disk I/O and write lock stalls during B+ tree page splits, elevating p99 write latency to 180 milliseconds.\n\nThe RFC recommended RocksDB using an LSM-tree storage engine with tiered compaction. Workers append incoming telemetry records to an in-memory memtable and sequential write-ahead log before flushing immutable SSTables to disk storage. Canary evaluations on 8 storage node instances demonstrated that RocksDB reduced write amplification from 28 down to 4, sustaining 600000 writes per second while reducing SSD wear by 65%."
    },
    # Sample 12: Distributed Consensus: Raft vs EPaxos
    {
        "raw_asr": "our distributed consensus architecture committee drafted an r f c evaluat egalitarian paxos against multi r a f t four cross region data coordination across three geographic datacenters standard r a f t consensus funneled all state machine proposals through a single leader knowed imposing a one hundred forty millisecond round trip penalty on transactions originating outside the leader datacenter egalitarian paxos allowed any replica knowed two propose transactions concurrently without designating a central leader resolving ordering dependencies through consensus graph traversal um during canary testing under twenty percent conflicting write contention egalitarian paxos experienced cascading dependency cycles increasing p nine nine commit latency two three hundred twenty milliseconds the architecture committee selected multi r a f t with localized partition leaders instead maintaining p nine nine write latencies under forty five milliseconds across sixty four consensus shards without dependency deadlock cycles",
        "refined_text": "Our distributed consensus architecture committee drafted an RFC evaluating Egalitarian Paxos against Multi-Raft for cross-region data coordination across 3 geographic datacenters. Standard Raft consensus funneled all state machine proposals through a single leader node, imposing a 140-millisecond round-trip penalty on transactions originating outside the leader datacenter. Egalitarian Paxos allowed any replica node to propose transactions concurrently without designating a central leader, resolving ordering dependencies through consensus graph traversal.\n\nDuring canary testing under 20% conflicting write contention, Egalitarian Paxos experienced cascading dependency cycles, increasing p99 commit latency to 320 milliseconds. The architecture committee selected Multi-Raft with localized partition leaders instead, maintaining p99 write latencies under 45 milliseconds across 64 consensus shards without dependency deadlock cycles."
    },
    # Sample 13: Database Sharding: Vitess vs Citus
    {
        "raw_asr": "our core platform data architecture team authored an architecture decision record reviewing horizontal database sharding strategies four our four terabyte order database the team evaluat vitess against citus distributed tables on post gres vitess required migrating eighty microservices away from post gres native json b indexing and custom stored procedures introducing extensive application refactoring overhead um the architecture decision record adopted citus on post gres with tenant hash sharding across sixteen worker knowed instances a distributed coordinator knowed routes incoming queries buy tenant identifier while reference tables are replicated two all worker nodes four localized join execution staging load simulations with ten thousand concurrent checkout transactions demonstrated that citus achieved p nine five query latencies of twelve milliseconds without cross shard lock deadlocks",
        "refined_text": "Our core platform data architecture team authored an architecture decision record reviewing horizontal database sharding strategies for our 4-terabyte order database. The team evaluated Vitess against Citus distributed tables on Postgres. Vitess required migrating 80 microservices away from Postgres native JSONB indexing and custom stored procedures, introducing extensive application refactoring overhead.\n\nThe architecture decision record adopted Citus on Postgres with tenant hash sharding across 16 worker node instances. A distributed coordinator node routes incoming queries by tenant identifier, while reference tables are replicated to all worker nodes for localized join execution. Staging load simulations with 10000 concurrent checkout transactions demonstrated that Citus achieved p95 query latencies of 12 milliseconds without cross-shard lock deadlocks."
    },
    # Sample 14: API Gateway: Envoy vs Kong
    {
        "raw_asr": "our edge infrastructure engineering group published an r f c evaluat envoy against kong four our next generation api gateway managing two hundred thousand requests per second across sixty backend services kong with open resty lua plugins suffered from frequent garbage collection pauses during peak traffic and consumed forty eight gigabytes of memory under t l s renegotiation load um the r f c selected envoy proxy buy leveraging its event driven non blocking architecture with c p u core thread affinity custom authentication and rate limiting filters compile into web assembly modules running inside the request pipeline canary benchmarks on twelve gateway instances demonstrated that envoy reduced p nine nine proxy latency from eighteen milliseconds down two two milliseconds while decreasing memory footprint buy fifty percent during peak traffic spikes",
        "refined_text": "Our edge infrastructure engineering group published an RFC evaluating Envoy against Kong for our next-generation API gateway managing 200000 requests per second across 60 backend services. Kong with OpenResty Lua plugins suffered from frequent garbage collection pauses during peak traffic and consumed 48 gigabytes of memory under TLS renegotiation load.\n\nThe RFC selected Envoy proxy by leveraging its event-driven non-blocking architecture with CPU core thread affinity. Custom authentication and rate limiting filters compile into WebAssembly modules running inside the request pipeline. Canary benchmarks on 12 gateway instances demonstrated that Envoy reduced p99 proxy latency from 18 milliseconds down to 2 milliseconds, while decreasing memory footprint by 50% during peak traffic spikes."
    },
    # Sample 15: Event Sourcing: EventStoreDB vs Apache Pulsar
    {
        "raw_asr": "our financial ledger engineering council drafted an architecture decision record defining our event store persistence technology four core banking ledgers upstream teams evaluated apache pulsar topics as an append only event store but pulsar lacked optimistic concurrency checks based on stream revision numbers permitting concurrent transfer commands two commit conflicting ledger balance records um the architecture decision record selected event store d b four the authoritative immutable event log enforcing monotonic revision numbers on stream writes two prevent concurrent overdraft state overwrites downstream projection consumers read event streams asynchronously two update post gres read models within twenty five milliseconds during chaos testing with eight thousand concurrent transfer operations event store d b rejected one hundred fifty conflicting writes with zero phantom ledger balance inconsistencies",
        "refined_text": "Our financial ledger engineering council drafted an architecture decision record defining our event store persistence technology for core banking ledgers. Upstream teams evaluated Apache Pulsar topics as an append-only event store, but Pulsar lacked optimistic concurrency checks based on stream revision numbers, permitting concurrent transfer commands to commit conflicting ledger balance records.\n\nThe architecture decision record selected EventStoreDB for the authoritative immutable event log, enforcing monotonic revision numbers on stream writes to prevent concurrent overdraft state overwrites. Downstream projection consumers read event streams asynchronously to update Postgres read models within 25 milliseconds. During chaos testing with 8000 concurrent transfer operations, EventStoreDB rejected 150 conflicting writes with zero phantom ledger balance inconsistencies."
    },
    # Sample 16: Distributed Caching: Two-Tier Cache Architecture
    {
        "raw_asr": "our application performance team authored an architecture decision record establishing a two tier caching architecture four high throughput catalog services during flash sale events one hundred fifty thousand read requests per second targeted hot product records saturating network bandwidth across four redis cluster nodes and introducing four milliseconds p nine five latency um the architecture decision record implemented a two tier caching design pairing local caffeine in memory caches with a central redis cluster local caches store hot entries with a five second time two live while redis maintains a one hour time two live with redis pub sub invalidation channels purging expired entries on updates staging stress testing showed that the two tier pattern handled eighty eight percent of catalog queries locally in memory reducing redis network ingress buy seventy five percent and sustaining one hundred eighty thousand requests per second",
        "refined_text": "Our application performance team authored an architecture decision record establishing a two-tier caching architecture for high-throughput catalog services. During flash sale events, 150000 read requests per second targeted hot product records, saturating network bandwidth across 4 Redis cluster nodes and introducing 4 milliseconds p95 latency.\n\nThe architecture decision record implemented a two-tier caching design pairing local Caffeine in-memory caches with a central Redis cluster. Local caches store hot entries with a 5-second time to live, while Redis maintains a 1-hour time to live with Redis Pub/Sub invalidation channels purging expired entries on updates. Staging stress testing showed that the two-tier pattern handled 88% of catalog queries locally in memory, reducing Redis network ingress by 75% and sustaining 180000 requests per second."
    },
    # Sample 17: Microservices Communication: gRPC vs GraphQL Federation
    {
        "raw_asr": "our platform architecture council released an r f c standardizing inter service communication protocols across one hundred twenty internal microservices service teams debated graphql federation against g r p c with protocol buffers four backend service calls graphql federation introduced substantial parsing overhead and complex query planning when traversing nested entity graphs across five microservice boundaries um the r f c mandated g r p c with protocol buffers four all internal communication reserving graphql exclusively four external client aggregation layers protocol buffers provide strict schema typing backward compatibility via tag numbers and binary serialization over h t t p two multiplexed streams staging benchmarks across twenty services revealed that g r p c decreased payload size buy sixty percent and lowered internal p nine nine r p c latency from thirty five milliseconds down two six milliseconds",
        "refined_text": "Our platform architecture council released an RFC standardizing inter-service communication protocols across 120 internal microservices. Service teams debated GraphQL federation against gRPC with Protocol Buffers for backend service calls. GraphQL federation introduced substantial parsing overhead and complex query planning when traversing nested entity graphs across 5 microservice boundaries.\n\nThe RFC mandated gRPC with Protocol Buffers for all internal communication, reserving GraphQL exclusively for external client aggregation layers. Protocol Buffers provide strict schema typing, backward compatibility via tag numbers, and binary serialization over HTTP/2 multiplexed streams. Staging benchmarks across 20 services revealed that gRPC decreased payload size by 60% and lowered internal p99 RPC latency from 35 milliseconds down to 6 milliseconds."
    },
    # Sample 18: Secrets Management: SPIFFE/SPIRE vs Vault
    {
        "raw_asr": "our cloud security architecture team authored an architecture decision record defining workload identity across fifty coober netties clusters hosting four hundred microservices long lived static tokens managed buy vault required intricate rotation sidecars and caused service authentication outages when credential leases expired during network partitions um the architecture decision record adopted s p i f f e and s p i r e four cryptographic workload identity buy issuing short lived x five zero nine certificates with one hour validity over mutual t l s envoy sidecars receive x five zero nine certificates directly through the secret discovery service a p i without writing static secrets two disk canary validation across ten clusters verified that s p i r e automated one hundred percent of certificate renewals without application downtime reducing credential issuance latency two fifteen milliseconds",
        "refined_text": "Our cloud security architecture team authored an architecture decision record defining workload identity across 50 Kubernetes clusters hosting 400 microservices. Long-lived static tokens managed by Vault required intricate rotation sidecars and caused service authentication outages when credential leases expired during network partitions.\n\nThe architecture decision record adopted SPIFFE and SPIRE for cryptographic workload identity by issuing short-lived X.509 certificates with 1-hour validity over mutual TLS. Envoy sidecars receive X.509 certificates directly through the Secret Discovery Service API without writing static secrets to disk. Canary validation across 10 clusters verified that SPIRE automated 100% of certificate renewals without application downtime, reducing credential issuance latency to 15 milliseconds."
    },
    # Sample 19: Distributed Transactions: Saga Orchestration vs 2PC
    {
        "raw_asr": "our distributed systems architecture committee drafted an r f c addressing transaction coordination across payment inventory and shipping microservices traditional two phase commit protocols held distributed database locks across remote services causing cascading timeouts whenever the shipping service experienced latency spikes um the r f c rejected two phase commit in favor of saga orchestrat implemented on the temporal workflow engine the orchestrator executes local database transactions sequentially and dispatches compensating transactions if any downstream step fails during simulated network failure drills where payment succeeded but shipping failed after ten seconds temporal executed compensating inventory releases within two hundred milliseconds across fifteen worker knowed instances preventing locked inventory records without distributed database locks",
        "refined_text": "Our distributed systems architecture committee drafted an RFC addressing transaction coordination across payment, inventory, and shipping microservices. Traditional two-phase commit protocols held distributed database locks across remote services, causing cascading timeouts whenever the shipping service experienced latency spikes.\n\nThe RFC rejected two-phase commit in favor of Saga orchestration implemented on the Temporal workflow engine. The orchestrator executes local database transactions sequentially and dispatches compensating transactions if any downstream step fails. During simulated network failure drills where payment succeeded but shipping failed after 10 seconds, Temporal executed compensating inventory releases within 200 milliseconds across 15 worker node instances, preventing locked inventory records without distributed database locks."
    },
    # Sample 20: Asynchronous Task Processing: Temporal vs Celery
    {
        "raw_asr": "our background processing platform group published an architecture decision record replacing legacy celery worker fleets with temporal four mission critical order workflows celery backed buy redis lacked durable execution state and deterministic retry policies resulting in two hundred lost background jobs per week during worker restarts or network partitions um the architecture decision record adopted temporal paired with k af ka four asynchronous workflow execution workers poll temporal server clusters using long polling g r p c connections recording heartbeats every five seconds two detect failed worker instances chaos testing with abrupt termination of six worker knowed hosts showed that temporal recovered one hundred percent of in flight workflows within eight seconds without duplicate task executions eliminating dropped background jobs entirely",
        "refined_text": "Our background processing platform group published an architecture decision record replacing legacy Celery worker fleets with Temporal for mission-critical order workflows. Celery backed by Redis lacked durable execution state and deterministic retry policies, resulting in 200 lost background jobs per week during worker restarts or network partitions.\n\nThe architecture decision record adopted Temporal paired with Kafka for asynchronous workflow execution. Workers poll Temporal server clusters using long-polling gRPC connections, recording heartbeats every 5 seconds to detect failed worker instances. Chaos testing with abrupt termination of 6 worker node hosts showed that Temporal recovered 100% of in-flight workflows within 8 seconds without duplicate task executions, eliminating dropped background jobs entirely."
    }
]

print(f"Total samples: {len(batch)}")
assert len(batch) == 20

# Run pair validation
for idx, p in enumerate(batch):
    raw = p["raw_asr"]
    ref = p["refined_text"]
    v_ok, v_msg = validate_pair(p)
    if not v_ok:
        print(f"FAIL validate_pair sample {idx+1}: {v_msg}")
    c_res, c_msg = clean_sample(raw, ref)
    if c_res is None:
        print(f"FAIL clean_sample sample {idx+1}: {c_msg}")

b_ok, b_msg, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
print(f"validate_batch: {b_ok}, {b_msg}, {b_tiers}")
