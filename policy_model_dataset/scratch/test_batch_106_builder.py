import json
import sys
from pathlib import Path

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
    # ==========================================
    # TIER 1: SHORT (< 25 words) - 4 samples
    # Exactly 1 sentence, 0 newlines, max 1 cut-word
    # ==========================================
    # Sample 1: Raft consensus election timeout
    {
        "raw_asr": "basically the distributed consensus r f c prefers longer election timeouts buy reducing leader arbitrat conflicts across three knowed clusters",
        "refined_text": "The distributed consensus RFC prefers longer election timeouts by reducing leader arbitration conflicts across 3 node clusters."
    },
    # Sample 2: 3-phase commit vs Saga pattern
    {
        "raw_asr": "uh our distributed billing proposal replaces three phase commit buy isolating transaction terminat inside five local service sagas",
        "refined_text": "Our distributed billing proposal replaces 3-phase commit by isolating transaction termination inside 5 local service sagas."
    },
    # Sample 3: LSM-tree vs B-tree storage engine
    {
        "raw_asr": "um the storage engine trade off favors l s m trees buy reducing right amplification during continuous log allocat",
        "refined_text": "The storage engine trade-off favors LSM-trees by reducing write amplification during continuous log allocation."
    },
    # Sample 4: Token bucket vs sliding window rate limiting
    {
        "raw_asr": "okay so our rate limiter r f c adopts sliding window counters buy bounding memory configur across each proxy knowed",
        "refined_text": "Our rate limiter RFC adopts sliding window counters by bounding memory configuration across each proxy node."
    },

    # ==========================================
    # TIER 2: MEDIUM (25-89 words) - 6 samples
    # 1-3 sentences, natural \n\n break
    # ==========================================
    # Sample 5: CQRS and Event Sourcing throughput vs lock contention
    {
        "raw_asr": "basically our architecture r f c introduces command query responsibility segregation buy decoupling right operations from read queries the legacy monolithic relational database stalled twenty queries wait fifty queries instead buy contending on account table row locks um the proposed event store handles append operat buy publishing order updates towards event stream subscribers",
        "refined_text": "Our architecture RFC introduces Command Query Responsibility Segregation by decoupling write operations from read queries.\n\nThe legacy monolithic relational database stalled 50 queries instead by contending on account table row locks. The proposed event store handles append operations by publishing order updates towards event stream subscribers."
    },
    # Sample 6: Multi-leader replication conflict resolution (CRDTs vs Last-Write-Wins)
    {
        "raw_asr": "uh our global datastore design r f c rejects last write wins buy adopting state based conflict free replicated data types concurrent record updates caused silent data loss across four replicas wait eight replicas instead during cross region link latency spikes basically conflict free types guarantee deterministic record synchronizat across twelve edge data centers buy merging concurrent mutations without central lock coordination",
        "refined_text": "Our global datastore design RFC rejects Last-Write-Wins by adopting state-based Conflict-free Replicated Data Types.\n\nConcurrent record updates caused silent data loss across 8 replicas instead during cross-region link latency spikes. Conflict-free types guarantee deterministic record synchronization across 12 edge data centers by merging concurrent mutations without central lock coordination."
    },
    # Sample 7: Consistent hashing ring with virtual nodes
    {
        "raw_asr": "um the caching tier architecture r f c resolves key hotspot imbalances buy implementing consistent hashing with virtual knowed partitions assigning sixty tokens per server caused uneven traffic skew across four cache clusters wait eight cache clusters instead okay so allocating two hundred virtual nodes per physical knowed balances key distribut buy maintaining uniform request loads during cluster resizing",
        "refined_text": "The caching tier architecture RFC resolves key hotspot imbalances by implementing consistent hashing with virtual node partitions.\n\nAssigning 60 tokens per server caused uneven traffic skew across 8 cache clusters instead. Allocating 200 virtual nodes per physical node balances key distribution by maintaining uniform request loads during cluster resizing."
    },
    # Sample 8: Transactional outbox pattern vs dual writes
    {
        "raw_asr": "basically our event driven integration r f c replaces dual right architectures buy introducing the transactional outbox pattern writing directly to message brokers caused state inconsistencies across sixteen microservices wait thirty two microservices instead during network outages uh persisting domain events into outbox database tables guarantees reliable message transmiss buy relaying records through dedicated change data capture workers",
        "refined_text": "Our event-driven integration RFC replaces dual write architectures by introducing the transactional outbox pattern.\n\nWriting directly to message brokers caused state inconsistencies across 32 microservices instead during network outages. Persisting domain events into outbox database tables guarantees reliable message transmission by relaying records through dedicated change data capture workers."
    },
    # Sample 9: Circuit breaker fallback vs cascading failure
    {
        "raw_asr": "uh our upstream gateway architecture r f c introduces adaptive circuit breakers buy isolating slow downstream dependencies failing remote service calls triggered thread exhaustion across sixty gateway instances during database degradat basically setting error rate thresholds at twenty percent with twenty five pending requests instead protects upstream services buy returning immediate cached fallback responses",
        "refined_text": "Our upstream gateway architecture RFC introduces adaptive circuit breakers by isolating slow downstream dependencies.\n\nFailing remote service calls triggered thread exhaustion across 60 gateway instances during database degradation. Setting error rate thresholds at 20 percent with 25 pending requests instead protects upstream services by returning immediate cached fallback responses."
    },
    # Sample 10: Read-your-writes consistency using session tokens
    {
        "raw_asr": "okay so our distributed profile datastore r f c implements read your writes consistency buy propagating monotonic session tokens to read replicas stale replica reads caused user confusion when replication lag exceeded five seconds wait two seconds instead after profile updates um routing recent mutation requests buy verifying session token timestamps enforces read consistency without saturating master database write capacity",
        "refined_text": "Our distributed profile datastore RFC implements read-your-writes consistency by propagating monotonic session tokens to read replicas.\n\nStale replica reads caused user confusion when replication lag exceeded 2 seconds instead after profile updates. Routing recent mutation requests by verifying session token timestamps enforces read consistency without saturating master database write capacity."
    },

    # ==========================================
    # TIER 3: LONG (90+ words) - 10 samples
    # Multi-paragraph \n\n, zero checklist stereotypes, natural narration
    # ==========================================
    # Sample 11: Raft Leader Leases vs Quorum Reads
    {
        "raw_asr": "uh our consensus architecture r f c analyzes trade offs between quorum reads and bounded leader leases in r a f t clusters quorum read operations enforce linearizability buy querying a majority of three knowed wait five knowed clusters instead but each read incurs round trip r p c network latency bounded leader leases allow the leader to serve reads locally buy assuming synchronized monotonic hardware clocks however clock drift across twenty nodes can cause stale reads if a deposed leader serves requests during network partitions basically the proposal approves bounded leader leases buy enforcing fifty millisecond lease intervals and verifying leader connectivity before each lease renewal operat",
        "refined_text": "Our consensus architecture RFC analyzes trade-offs between quorum reads and bounded leader leases in Raft clusters. Quorum read operations enforce linearizability by querying a majority of 5 node clusters instead, but each read incurs round-trip RPC network latency.\n\nBounded leader leases allow the leader to serve reads locally by assuming synchronized monotonic hardware clocks. Clock drift across 20 nodes can cause stale reads if a deposed leader serves requests during network partitions.\n\nThe proposal approves bounded leader leases by enforcing 50-millisecond lease intervals and verifying leader connectivity before each lease renewal operation."
    },
    # Sample 12: Two-Phase Commit vs Choreographed Saga Pattern
    {
        "raw_asr": "basically our distributed payment r f c evaluates atomic commit protocols across microservice boundaries two phase commit guarantees serializable isolation across databases buy holding distributed row locks during prepare and commit phases however coordinator failure blocks active resources indefinitely buy triggering cascading connection pool exhaustion across eight microservices wait sixteen microservices instead choreographed sagas resolve coordinator bottlenecks buy coordinating asynchronous domain events and compensating actions across five hundred payment workflows each participating service persists local transactions inside independent datastores and emits forward progress events over message queues um the architecture team recommends choreographed sagas with idempotency keys buy accepting eventual consistency and bounding transaction terminat latency down into three seconds",
        "refined_text": "Our distributed payment RFC evaluates atomic commit protocols across microservice boundaries. Two-phase commit guarantees serializable isolation across databases by holding distributed row locks during prepare and commit phases.\n\nCoordinator failure blocks active resources indefinitely by triggering cascading connection pool exhaustion across 16 microservices instead. Choreographed sagas resolve coordinator bottlenecks by coordinating asynchronous domain events and compensating actions across 500 payment workflows.\n\nEach participating service persists local transactions inside independent datastores and emits forward progress events over message queues. The architecture team recommends choreographed sagas with idempotency keys by accepting eventual consistency and bounding transaction termination latency down into 3 seconds."
    },
    # Sample 13: LSM-Tree vs B-Tree Storage Engine
    {
        "raw_asr": "um our time series ingestion r f c compares log structured merge trees against b trees under heavy right workloads b trees suffer from frequent random disk writes and high right amplification buy triggering in place page splits across storage partitions the sequential commit log writes data directly into persistent storage buffers buy eliminating expensive disk head movement l s m trees optimize ingestion throughput buy appending incoming metrics sequentially into memory buffers and flushing immutable s s tables across four storage knowed wait eight storage knowed instead however background compaction consumes disk bandwidth and causes read degradat under sustained traffic uh the storage committee selects l s m trees with tiered compaction buy allocating one hundred megabytes for write buffers and bounding background compaction into four dedicated worker threads",
        "refined_text": "Our time-series ingestion RFC compares log-structured merge trees against B-trees under heavy write workloads. B-trees suffer from frequent random disk writes and high write amplification by triggering in-place page splits across storage partitions.\n\nThe sequential commit log writes data directly into persistent storage buffers by eliminating expensive disk head movement. LSM-trees optimize ingestion throughput by appending incoming metrics sequentially into memory buffers and flushing immutable SSTables across 8 storage node instances instead.\n\nBackground compaction consumes disk bandwidth and causes read degradation under sustained traffic. The storage committee selects LSM-trees with tiered compaction by allocating 100 megabytes for write buffers and bounding background compaction into 4 dedicated worker threads."
    },
    # Sample 14: WebSocket Push vs HTTP Long Polling
    {
        "raw_asr": "uh our fleet telemetry streaming r f c reviews transport protocol alternatives for vehicle tracking gateways pull based http long polling creates excessive connection handshake overhead buy exhausting gateway socket tables during high frequency metric delivery push based web socket connections maintain persistent bidirectional t c p channels buy reducing header payload overhead and eliminating repeated connection setup across twelve gateway pods wait twenty four gateway pods instead fleet vehicles transmit continuous engine diagnostics and speed telemetry over established socket connections maintaining stateful connections requires distributed connection tracking across memory stores okay so the gateway r f c approves web socket streaming buy configuring distributed session stores across twenty four proxy instances and enforcing sixty second keepalive ping intervals buy bounding idle connection drops",
        "refined_text": "Our fleet telemetry streaming RFC reviews transport protocol alternatives for vehicle tracking gateways. Pull-based HTTP long polling creates excessive connection handshake overhead by exhausting gateway socket tables during high-frequency metric delivery.\n\nPush-based WebSocket connections maintain persistent bidirectional TCP channels by reducing header payload overhead and eliminating repeated connection setup across 24 gateway pods instead. Fleet vehicles transmit continuous engine diagnostics and speed telemetry over established socket connections.\n\nMaintaining stateful connections requires distributed connection tracking across memory stores. The gateway RFC approves WebSocket streaming by configuring distributed session stores across 24 proxy instances and enforcing 60-second keepalive ping intervals by bounding idle connection drops."
    },
    # Sample 15: Range-Based vs Hash-Based Partitioning
    {
        "raw_asr": "basically our database partitioning r f c investigates data distribution trade offs across multi tenant analytics clusters range based partitioning enables efficient time interval scans buy clustering contiguous tenant timestamps together but creates severe right hotspots when large tenants write into active partitions hash based partitioning distributes records uniformly across sixteen database shards wait thirty two database shards instead buy eliminating write amplification hotspots across five hundred tenants however hash distribution degrades date range queries buy requiring scatter gather coordination across all active shards routing layer dispatchers broadcast analytical requests towards every partition which saturates network bandwidth um the data infrastructure group adopts composite partitioning buy combining hash based tenant routing with internal range partitions across thirty two cluster partitions",
        "refined_text": "Our database partitioning RFC investigates data distribution trade-offs across multi-tenant analytics clusters. Range-based partitioning enables efficient time-interval scans by clustering contiguous tenant timestamps together, but creates severe write hotspots when large tenants write into active partitions.\n\nHash-based partitioning distributes records uniformly across 32 database shards instead by eliminating write amplification hotspots across 500 tenants. Hash distribution degrades date-range queries by requiring scatter-gather coordination across all active shards.\n\nRouting layer dispatchers broadcast analytical requests towards every partition which saturates network bandwidth. The data infrastructure group adopts composite partitioning by combining hash-based tenant routing with internal range partitions across 32 cluster partitions."
    },
    # Sample 16: Write-Through Redis vs Event-Driven CDC Invalidation
    {
        "raw_asr": "uh our catalog caching r f c addresses cache consistency challenges under concurrent catalog mutations application level right through caching updates the database and cache within the same request pipeline buy introducing data drift whenever dual right operations fail partially database replication agents parse internal write ahead logs without adding query overhead towards active transactions change data capture tailing database transaction logs guarantees reliable cache invalidat buy streaming commit events into kafka topics across six catalog partitions wait twelve catalog partitions instead asynchronous processing introduces fifty milliseconds of replication lag buy exposing temporary stale reads okay so the catalog team selects change data capture buy isolating invalidation logic inside twenty stream consumers and bounding cache stale windows",
        "refined_text": "Our catalog caching RFC addresses cache consistency challenges under concurrent catalog mutations. Application-level write-through caching updates the database and cache within the same request pipeline by introducing data drift whenever dual write operations fail partially.\n\nDatabase replication agents parse internal write-ahead logs without adding query overhead towards active transactions. Change data capture tailing database transaction logs guarantees reliable cache invalidation by streaming commit events into Kafka topics across 12 catalog partitions instead.\n\nAsynchronous processing introduces 50 milliseconds of replication lag by exposing temporary stale reads. The catalog team selects change data capture by isolating invalidation logic inside 20 stream consumers and bounding cache stale windows."
    },
    # Sample 17: Centralized Redis Token Bucket vs Local Sliding Window with Gossip
    {
        "raw_asr": "um our edge rate limiting r f c evaluates centralized enforcement against decentralized memory algorithms centralized token buckets in r e d i s provide globally accurate rate limits across all gateway pods but add two milliseconds of network latency and introduce a single point of failure during cluster failovers local sliding window limiters track request rates inside local memory buy achieving sub millisecond execution across twenty gateway knowed wait forty gateway knowed instead peer gossip protocols synchronize counter approximations buy tolerating minor rate limit bursts during traffic spikes basically the security team adopts local sliding window limiters buy configuring cluster gossip across forty gateway instances and bounding rate deviations below five percent",
        "refined_text": "Our edge rate limiting RFC evaluates centralized enforcement against decentralized memory algorithms. Centralized token buckets in Redis provide globally accurate rate limits across all gateway pods, but add 2 milliseconds of network latency and introduce a single point of failure during cluster failovers.\n\nLocal sliding window limiters track request rates inside local memory by achieving sub-millisecond execution across 40 gateway node instances instead. Peer gossip protocols synchronize counter approximations by tolerating minor rate limit bursts during traffic spikes.\n\nThe security team adopts local sliding window limiters by configuring cluster gossip across 40 gateway instances and bounding rate deviations below 5 percent."
    },
    # Sample 18: Strong Linearizability vs Causal Consistency
    {
        "raw_asr": "basically our global datastore r f c examines trade offs between strong linearizability and causal consistency across multi region deployments strong linearizability requires atomic clock synchronizat or consensus round trips buy adding forty milliseconds of write latency across three regions wait six regions instead causal consistency tracks causal dependencies using vector clocks buy allowing local writes without inter region coordination during network partitions each datastore knowed attaches vector timestamps to outgoing mutations which increases network payload size by sixteen bytes however causal consistency tolerates concurrent conflicting writes buy requiring application level resolution during data reconciliation um our architecture council approves causal consistency buy implementing vector clocks across six global regions and enforcing deterministic conflict resolution rules",
        "refined_text": "Our global datastore RFC examines trade-offs between strong linearizability and causal consistency across multi-region deployments. Strong linearizability requires atomic clock synchronization or consensus round trips by adding 40 milliseconds of write latency across 6 regions instead.\n\nCausal consistency tracks causal dependencies using vector clocks by allowing local writes without inter-region coordination during network partitions. Each datastore node attaches vector timestamps to outgoing mutations which increases network payload size by 16 bytes.\n\nCausal consistency tolerates concurrent conflicting writes by requiring application-level resolution during data reconciliation. Our architecture council approves causal consistency by implementing vector clocks across 6 global regions and enforcing deterministic conflict resolution rules."
    },
    # Sample 19: Modular Monolith vs Microservices
    {
        "raw_asr": "uh our core banking platform r f c evaluates architecture migration trade offs between microservices and a modular monolith deploying independent microservices immediately introduces distributed network latency and complex transaction boundaries across fifty database connections modular monolith architectures enforce strict module boundaries and package level encapsulation buy preventing cross domain queries while operating within a single deployment artifact across four bounded contexts wait eight bounded contexts instead engineers refactor domain logic buy extracting distinct billing and account boundaries into isolated packages this architecture eliminates remote network overhead buy keeping method invocations within process memory okay so our engineering leadership adopts the modular monolith r f c buy isolating domain modules across eight bounded contexts and enforcing interface contracts",
        "refined_text": "Our core banking platform RFC evaluates architecture migration trade-offs between microservices and a modular monolith. Deploying independent microservices immediately introduces distributed network latency and complex transaction boundaries across 50 database connections.\n\nModular monolith architectures enforce strict module boundaries and package-level encapsulation by preventing cross-domain queries while operating within a single deployment artifact across 8 bounded contexts instead. Engineers refactor domain logic by extracting distinct billing and account boundaries into isolated packages.\n\nThis architecture eliminates remote network overhead by keeping method invocations within process memory. Our engineering leadership adopts the modular monolith RFC by isolating domain modules across 8 bounded contexts and enforcing interface contracts."
    },
    # Sample 20: Layer 4 TCP Multiplexing vs Layer 7 HTTP/2 Reverse Proxy
    {
        "raw_asr": "um our edge routing r f c analyzes performance trade offs between layer four transport proxies and layer seven application proxies layer four t c p multiplexing routes raw packets with minimal c p u overhead buy forwarding connections without t l s termination but lacks inspection of request paths or authentication headers layer seven reverse proxies terminate t l s and inspect http headers buy enabling granular path root and canary traffic splitting across eight edge clusters wait sixteen edge clusters instead however layer seven proxies require substantial memory configur under high connection concurrency basically the platform team selects a hybrid topology buy deploying layer four load balancers in front of sixteen layer seven proxy clusters",
        "refined_text": "Our edge routing RFC analyzes performance trade-offs between Layer 4 transport proxies and Layer 7 application proxies. Layer 4 TCP multiplexing routes raw packets with minimal CPU overhead by forwarding connections without TLS termination, but lacks inspection of request paths or authentication headers.\n\nLayer 7 reverse proxies terminate TLS and inspect HTTP headers by enabling granular path route and canary traffic splitting across 16 edge clusters instead. Layer 7 proxies require substantial memory configuration under high connection concurrency.\n\nThe platform team selects a hybrid topology by deploying Layer 4 load balancers in front of 16 Layer 7 proxy clusters."
    }
]

print(f"Total samples: {len(batch)}")
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, s in enumerate(batch):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    if words < 25:
        tier = "short"
    elif words < 90:
        tier = "medium"
    else:
        tier = "long"
    tier_counts[tier] += 1

    v_ok, v_msg = validate_pair(s)
    c_res, c_msg = clean_sample(raw, ref)

    status = "PASS" if v_ok and c_res else "FAIL"
    print(f"Sample {i+1:02d} [{tier.upper():6s}] ({words:3d} words): {status} | Val: {v_msg} | Clean: {c_msg}")

b_ok, b_msg, counts = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: {b_ok} -> {b_msg}")
print(f"Tier counts: {counts}")

if b_ok and all(clean_sample(s["raw_asr"], s["refined_text"])[0] is not None for s in batch):
    out_path = Path("scratch/subagent_batch_106.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote verified batch to {out_path}")
else:
    print("\nBatch NOT saved due to errors.")
