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
    # Sample 1: Distributed locks - etcd leader lease renewal
    {
        "raw_asr": "basically renew the et see dee lease buy incrementing the monotonic fencing token every four wait two seconds instead",
        "refined_text": "Renew the etcd lease by incrementing the monotonic fencing token every 2 seconds instead."
    },
    # Sample 2: CQRS - read projection synchronization lag
    {
        "raw_asr": "uh our c q r s read projection synchroniz lagged buy twelve milliseconds during high write throughput",
        "refined_text": "Our CQRS read projection synchronization lagged by 12 milliseconds during high write throughput."
    },
    # Sample 3: API versioning - deprecation sunset header
    {
        "raw_asr": "um configure the api deprecation sunset header two terminat legacy version one routes in thirty days",
        "refined_text": "Configure the API deprecation sunset header to terminate legacy version 1 routes in 30 days."
    },
    # Sample 4: Edge caching - surrogate key purge invalidation
    {
        "raw_asr": "basically invalidat edge cache entries buy purging the surrogate key header across sixteen edge pops",
        "refined_text": "Invalidate edge cache entries by purging the surrogate key header across 16 edge POPs."
    },

    # ==========================================
    # TIER 2: MEDIUM (25-89 words) - 6 samples
    # ==========================================
    # Sample 5: Distributed locks - Redis mutex lease with fencing tokens
    {
        "raw_asr": "our distributed lock design specifi a redis mutex lease with five seconds time two live buy issuing an incrementing fencing token with each acquisit um when a paused client attempts a write operation the storage layer inspects the token value and rejects any request containing an older fencing token",
        "refined_text": "Our distributed lock design specified a Redis mutex lease with 5 seconds time to live by issuing an incrementing fencing token with each acquisition.\n\nWhen a paused client attempts a write operation, the storage layer inspects the token value and rejects any request containing an older fencing token."
    },
    # Sample 6: Consensus algorithms - Raft leader lease renewal
    {
        "raw_asr": "our r a f t consensus r f c evaluat leader lease renewals four serving linearizable read requests without quorum round trips the leader knowed renews its read lease buy receiving heartbeats from three wait four followers every one hundred milliseconds uh if a heartbeat drops the leader falls back two standard log replication before returning data",
        "refined_text": "Our Raft consensus RFC evaluated leader lease renewals for serving linearizable read requests without quorum round trips. The leader node renews its read lease by receiving heartbeats from 4 followers every 100 milliseconds.\n\nIf a heartbeat drops, the leader falls back to standard log replication before returning data."
    },
    # Sample 7: Multi-tenant database partitioning - Row-level security vs schemas
    {
        "raw_asr": "basically our multi tenant database r f c compar row level security policies against isolated schema partit four ten thousand enterprise tenants um row level security applies tenant identifier filters on every post gres table query buy leveraging connection session variables instead of maintaining sixty distinct database schemas",
        "refined_text": "Our multi-tenant database RFC compared row-level security policies against isolated schema partitions for 10000 enterprise tenants.\n\nRow-level security applies tenant identifier filters on every Postgres table query by leveraging connection session variables instead of maintaining 60 distinct database schemas."
    },
    # Sample 8: Distributed tracing propagation - W3C traceparent headers across gRPC
    {
        "raw_asr": "our distributed tracing design document mandates injecting w three c traceparent headers across incoming g r p c transport boundaries buy propagat span context in metadata keys uh downstream microservices extract the traceparent header and propagate sampling decisions across five internal r p c hops without losing parent span continuity",
        "refined_text": "Our distributed tracing design document mandates injecting W3C traceparent headers across incoming gRPC transport boundaries by propagating span context in metadata keys.\n\nDownstream microservices extract the traceparent header and propagate sampling decisions across 5 internal RPC hops without losing parent span continuity."
    },
    # Sample 9: Event sourcing - Snapshotting aggregate root state
    {
        "raw_asr": "um our event sourcing r f c specifi snapshotting rules four the order aggregate root buy persisting event streams into an append only table the snapshot worker generat a state checkpoint every two hundred wait five hundred events instead uh replaying aggregate state during recovery reads forty events rather than four thousand raw log records",
        "refined_text": "Our event sourcing RFC specified snapshotting rules for the order aggregate root by persisting event streams into an append-only table. The snapshot worker generated a state checkpoint every 500 events instead.\n\nReplaying aggregate state during recovery reads 40 events rather than 4000 raw log records."
    },
    # Sample 10: Edge caching - Stale-while-revalidate with edge worker caching
    {
        "raw_asr": "basically our edge caching architecture design adopt stale while revalidate cache control headers across thirty edge points of presence um edge nodes serve cached response payloads within two milliseconds while dispatching asynchronous revalidation fetches two origin post gres backends buy throttling background revalidation concurrency two eight workers",
        "refined_text": "Our edge caching architecture design adopted stale-while-revalidate cache-control headers across 30 edge points of presence.\n\nEdge nodes serve cached response payloads within 2 milliseconds while dispatching asynchronous revalidation fetches to origin Postgres backends by throttling background revalidation concurrency to 8 workers."
    },

    # ==========================================
    # TIER 3: LONG (90+ words) - 10 samples
    # ==========================================
    # Sample 11: Distributed locks - Redlock vs etcd monotonic fencing tokens
    {
        "raw_asr": "our distributed systems infrastructure r f c evaluat redlock against et see dee four coordinating cluster wide data ingestion locks in high concurrency staging benchmarks with fifty worker processes redlock exhibited split brain race conditions when unsynchronized physical clocks skewed lease expiration buy two hundred milliseconds a paused worker resumed execution after its redis lease expired writing corrupted records two the storage tier alongside the newly elected lock owner um the r f c rejected redlock in favor of et see dee leases paired with sixty four bit monotonic fencing tokens under this architecture the lock manager issues an incrementing generation counter with every granted lease target database tables reject write transactions whenever the incoming fencing token is lower than the last committed transaction counter uh during canary testing across eight worker knowed instances monotonic fencing tokens blocked twelve out of order write requests during prolonged j v m garbage collection pauses maintaining one hundred percent data integrity without clock synchronizat dependencies",
        "refined_text": "Our distributed systems infrastructure RFC evaluated Redlock against etcd for coordinating cluster-wide data ingestion locks. In high-concurrency staging benchmarks with 50 worker processes, Redlock exhibited split-brain race conditions when unsynchronized physical clocks skewed lease expiration by 200 milliseconds. A paused worker resumed execution after its Redis lease expired, writing corrupted records to the storage tier alongside the newly elected lock owner.\n\nThe RFC rejected Redlock in favor of etcd leases paired with 64-bit monotonic fencing tokens. Under this architecture, the lock manager issues an incrementing generation counter with every granted lease. Target database tables reject write transactions whenever the incoming fencing token is lower than the last committed transaction counter. During canary testing across 8 worker node instances, monotonic fencing tokens blocked 12 out-of-order write requests during prolonged JVM garbage collection pauses, maintaining 100% data integrity without clock synchronization dependencies."
    },
    # Sample 12: Consensus algorithms - Paxos vs Multi-Raft state machine replication
    {
        "raw_asr": "our consensus architecture team authored an r f c evaluat multi r a f t against multi paxos four state machine replicat across sixty four storage shards multi paxos provides lower commit latency buy pipelining consensus proposals without leader lease renewal overhead but requires complex recovery logic during leader changeovers under network partit simulations our prototype multi paxos implementat produced subtle state diverge between non contiguous transaction logs requiring four hundred lines of custom reconciliation code um the r f c recommended multi r a f t because its strong leader invariant and strict log matching property simplify replica verification each storage partit runs an independent r a f t consensus group with three replicas allowing cluster knowed instances two host leader and follower roles concurrently across different shards uh during failure injection drills involving two abrupt knowed terminat events multi r a f t re elected partit leaders within one hundred fifty milliseconds and replicated uncommitted entries two a majority quorum without data corruption reducing overall operat complexity buy thirty five percent",
        "refined_text": "Our consensus architecture team authored an RFC evaluating Multi-Raft against Multi-Paxos for state machine replication across 64 storage shards. Multi-Paxos provides lower commit latency by pipelining consensus proposals without leader lease renewal overhead, but requires complex recovery logic during leader changeovers. Under network partitioning simulations, our prototype Multi-Paxos implementation produced subtle state diverge between non-contiguous transaction logs, requiring 400 lines of custom reconciliation code.\n\nThe RFC recommended Multi-Raft because its strong leader invariant and strict log matching property simplify replica verification. Each storage partition runs an independent Raft consensus group with 3 replicas, allowing cluster node instances to host leader and follower roles concurrently across different shards. During failure injection drills involving 2 abrupt node termination events, Multi-Raft re-elected partition leaders within 150 milliseconds and replicated uncommitted entries to a majority quorum without data corruption, reducing overall operational complexity by 35%."
    },
    # Sample 13: Event sourcing - Kafka vs PostgreSQL transactional outbox pattern
    {
        "raw_asr": "our core banking architecture council published an architecture decision record defining our event sourcing persistence model upstream microservices initially attempted direct writes two apache k af ka topics as the authoritative event store however k af ka lacked optimistic concurrency controls based on aggregate entity version numbers allowing concurrent bank transfer commands two commit conflicting account ledger entries without atomic c a s validation um the architecture decision record adopted the transactional outbox pattern backed buy post gres q l paired with debezium change data capture four streaming downstream events aggregate mutations right domain events and outbox records in a single database transaction enforcing monotonic sequence numbers and rejecting stale concurrent updates uh in staging stress tests generating ten thousand concurrent deposit commands this transactional pattern eliminated one hundred percent of phantom balance corruptions while maintaining a p nine five right latency of fourteen milliseconds across sixteen worker partit instances",
        "refined_text": "Our core banking architecture council published an architecture decision record defining our event sourcing persistence model. Upstream microservices initially attempted direct writes to Apache Kafka topics as the authoritative event store. However, Kafka lacked optimistic concurrency controls based on aggregate entity version numbers, allowing concurrent bank transfer commands to commit conflicting account ledger entries without atomic CAS validation.\n\nThe architecture decision record adopted the transactional outbox pattern backed by PostgreSQL, paired with Debezium change data capture for streaming downstream events. Aggregate mutations write domain events and outbox records in a single database transaction, enforcing monotonic sequence numbers and rejecting stale concurrent updates. In staging stress tests generating 10000 concurrent deposit commands, this transactional pattern eliminated 100% of phantom balance corruptions while maintaining a p95 write latency of 14 milliseconds across 16 worker partition instances."
    },
    # Sample 14: CQRS - Elasticsearch read projection pipeline
    {
        "raw_asr": "our product search platform team authored an r f c proposing an asynchronous projection pipeline four our c q r s read models in our previous architecture synchronous materialized view refreshes in post gres q l blocked product update transactions four three hundred fifty milliseconds under high right volume furthermore complex multi attribute catalog queries degraded primary database c p u utilizat two eighty five percent impacting checkout transactions during peak flash sales um the r f c proposed streaming event streams from k af ka directly into an elasticsearch cluster configured with twelve read shards an asynchronous projection consumer group validates schema versions and updates de normalized catalog documents within a fifty millisecond eventual consistency window uh canary benchmarks demonstrated that decoupling read queries from our primary transactional database reduced p nine nine search latency from two hundred forty milliseconds down two eighteen milliseconds while increasing sustained query throughput buy three hundred percent",
        "refined_text": "Our product search platform team authored an RFC proposing an asynchronous projection pipeline for our CQRS read models. In our previous architecture, synchronous materialized view refreshes in PostgreSQL blocked product update transactions for 350 milliseconds under high write volume. Furthermore, complex multi-attribute catalog queries degraded primary database CPU utilization to 85%, impacting checkout transactions during peak flash sales.\n\nThe RFC proposed streaming event streams from Kafka directly into an Elasticsearch cluster configured with 12 read shards. An asynchronous projection consumer group validates schema versions and updates de-normalized catalog documents within a 50-millisecond eventual consistency window. Canary benchmarks demonstrated that decoupling read queries from our primary transactional database reduced p99 search latency from 240 milliseconds down to 18 milliseconds, while increasing sustained query throughput by 300%."
    },
    # Sample 15: Multi-tenant partitioning - Citus tenant-keyed sharding
    {
        "raw_asr": "our enterprise platform data architecture group released a technical design document addressing database scalability across five thousand multi tenant organizations our initial prototype assigned dedicated post gres q l schemas per tenant organizat however maintaining five thousand schemas caused severe metadata lock contention during routine table schema migrations while idle connection memory pools consumed twenty four gigabytes of host r a m um the design document established a tenant keyed sharding strategy using citus distributed tables with hash partit across sixteen worker knowed instances all core tables include a mandatory sixty four bit tenant identifier column routing queries through distributed query planners that eliminate cross shard joins uh staging load simulations showed that co locating tenant data across thirty two distributed shards reduced migration execution time from four hours down two twelve minutes while maintaining strict data isolat across enterprise tenants",
        "refined_text": "Our enterprise platform data architecture group released a technical design document addressing database scalability across 5000 multi-tenant organizations. Our initial prototype assigned dedicated PostgreSQL schemas per tenant organization. However, maintaining 5000 schemas caused severe metadata lock contention during routine table schema migrations, while idle connection memory pools consumed 24 gigabytes of host RAM.\n\nThe design document established a tenant-keyed sharding strategy using Citus distributed tables with hash partitioning across 16 worker node instances. All core tables include a mandatory 64-bit tenant identifier column, routing queries through distributed query planners that eliminate cross-shard joins. Staging load simulations showed that co-locating tenant data across 32 distributed shards reduced migration execution time from 4 hours down to 12 minutes, while maintaining strict data isolation across enterprise tenants."
    },
    # Sample 16: API versioning - Path prefix vs Accept header deprecation window
    {
        "raw_asr": "our developer platform standards committee drafted an r f c standardizing our external api versioning strategy across forty customer facing services upstream client s d k teams debated url path prefix versioning against mime type content negotiat using h t t p accept headers in customer testing with two hundred external enterprise developers custom accept headers caused frequent caching bypasses at edge proxies and complicated client integrat in standard web browsers um the r f c adopted explicit major version path prefixes in u r i routes combined with r f c eight five nine four sunset response headers four scheduled deprecations minor non breaking schema enhancements add optional protobuf payload fields without bumping path versions when a major version enters deprecation edge gateways inject sunset date timestamps and deprecation links into all downstream h t t p response headers across a one hundred eighty day transition window giving integrators clear migration schedules while maintaining backward compatibility",
        "refined_text": "Our developer platform standards committee drafted an RFC standardizing our external API versioning strategy across 40 customer-facing services. Upstream client SDK teams debated URL path prefix versioning against MIME type content negotiation using HTTP Accept headers. In customer testing with 200 external enterprise developers, custom Accept headers caused frequent caching bypasses at edge proxies and complicated client integration in standard web browsers.\n\nThe RFC adopted explicit major version path prefixes in URI routes, combined with RFC 8594 Sunset response headers for scheduled deprecations. Minor non-breaking schema enhancements add optional protobuf payload fields without bumping path versions. When a major version enters deprecation, edge gateways inject sunset date timestamps and deprecation links into all downstream HTTP response headers across a 180-day transition window, giving integrators clear migration schedules while maintaining backward compatibility."
    },
    # Sample 17: Distributed tracing - W3C Trace Context and OpenTelemetry baggage
    {
        "raw_asr": "our observability infrastructure team completed a technical design document standardizing distributed tracing context propagat across eighty polyglot microservices legacy tracing implementations relied on disparate zipkin b three headers and jaeger native metadata causing frequent context loss whenever requests traversed heterogeneous service mesh boundaries trace spans frequently detached at asynchronous worker boundaries leaving forty five percent of distributed traces incomplete during incident triage um the technical design document established the w three c trace context specification as our universal standard using open telemetry collectors deployed alongside envoy service mesh sidecars edge ingress proxies generat unique one hundred twenty eight bit trace identifiers and inject traceparent headers into all incoming h t t p requests under our head based sampling policy ingress proxies sample five percent of normal traffic and one hundred percent of error responses while propagat interceptors preserve open telemetry baggage across six internal r p c hops without introducing observable latency overhead",
        "refined_text": "Our observability infrastructure team completed a technical design document standardizing distributed tracing context propagation across 80 polyglot microservices. Legacy tracing implementations relied on disparate Zipkin B3 headers and Jaeger native metadata, causing frequent context loss whenever requests traversed heterogeneous service mesh boundaries. Trace spans frequently detached at asynchronous worker boundaries, leaving 45% of distributed traces incomplete during incident triage.\n\nThe technical design document established the W3C Trace Context specification as our universal standard, using OpenTelemetry collectors deployed alongside Envoy service mesh sidecars. Edge ingress proxies generate unique 128-bit trace identifiers and inject traceparent headers into all incoming HTTP requests. Under our head-based sampling policy, ingress proxies sample 5% of normal traffic and 100% of error responses, while propagation interceptors preserve OpenTelemetry baggage across 6 internal RPC hops without introducing observable latency overhead."
    },
    # Sample 18: Edge caching - Surrogate key purge invalidation
    {
        "raw_asr": "our content delivery engineering team authored an r f c defining our next generation edge caching architecture across forty eight worldwide edge points of presence serving real time product inventory directly from centralized origin databases generated thirty five thousand origin queries per second during peak promotion events previous time two live expiration policies forced edge caches two discard valid catalog responses every sixty seconds resulting in repetitive origin cache stampedes and elevating database c p u load above ninety percent um the r f c implemented surrogate key tagging paired with stale while revalidate directives two achieve sub second content fresh while maintaining high edge offload origin services tag cached h t t p responses with category and product surrogate keys when an item update occurs an event bus emits purge requests that invalidat matching surrogate keys across all forty eight edge pops within one hundred fifty milliseconds uh canary validation demonstrated this invalidat model increased global edge cache hit rates from seventy two percent up two ninety eight percent while decreasing p nine nine origin query latency buy one hundred twenty milliseconds",
        "refined_text": "Our content delivery engineering team authored an RFC defining our next-generation edge caching architecture across 48 worldwide edge points of presence. Serving real-time product inventory directly from centralized origin databases generated 35000 origin queries per second during peak promotion events. Previous time-to-live expiration policies forced edge caches to discard valid catalog responses every 60 seconds, resulting in repetitive origin cache stampedes and elevating database CPU load above 90%.\n\nThe RFC implemented surrogate key tagging paired with stale-while-revalidate directives to achieve sub-second content fresh while maintaining high edge offload. Origin services tag cached HTTP responses with category and product surrogate keys. When an item update occurs, an event bus emits purge requests that invalidate matching surrogate keys across all 48 edge POPs within 150 milliseconds. Canary validation demonstrated this invalidation model increased global edge cache hit rates from 72% up to 98%, while decreasing p99 origin query latency by 120 milliseconds."
    },
    # Sample 19: Consensus & Locks - Chandy-Lamport distributed snapshots
    {
        "raw_asr": "our distributed storage infrastructure group published an architecture decision record reviewing snapshotting and compaction mechanisms four high frequency inventory state machines as transactional event volumes reached twenty eight thousand state mutations per second r a f t right ahead logs accumulated five hundred thousand uncompacted entries per knowed every two hours halting the state machine two right disk snapshots introduced six hundred millisecond lock freeze pauses causing upstream api clients two experience connection timeouts and retry storms um the architecture decision record adopted an asynchronous chandy lamport distributed snapshotting algorithm coupled with copy on right memory forks marker messages propagat through state machine channels without halting concurrent client mutations recording localized channel states while background threads stream compacted snapshot segments two object storage uh staging evaluations demonstrated that asynchronous marker propagat eliminated stop the world consensus pauses entirely maintaining p nine nine commit latency at six milliseconds and reducing disk storage footprint across ten cluster knowed instances buy sixty five percent",
        "refined_text": "Our distributed storage infrastructure group published an architecture decision record reviewing snapshotting and compaction mechanisms for high-frequency inventory state machines. As transactional event volumes reached 28000 state mutations per second, Raft write-ahead logs accumulated 500000 uncompacted entries per node every 2 hours. Halting the state machine to write disk snapshots introduced 600-millisecond lock freeze pauses, causing upstream API clients to experience connection timeouts and retry storms.\n\nThe architecture decision record adopted an asynchronous Chandy-Lamport distributed snapshotting algorithm coupled with copy-on-write memory forks. Marker messages propagate through state machine channels without halting concurrent client mutations, recording localized channel states while background threads stream compacted snapshot segments to object storage. Staging evaluations demonstrated that asynchronous marker propagation eliminated stop-the-world consensus pauses entirely, maintaining p99 commit latency at 6 milliseconds and reducing disk storage footprint across 10 cluster node instances by 65%."
    },
    # Sample 20: CQRS - Bloom filter deduplication window
    {
        "raw_asr": "our asynchronous integrat architecture committee drafted an r f c addressing eventual consistency anomalies and out of order message delivery in c q r s projection consumers during high throughput order processing spikes of twenty thousand events per second network retries from upstream message brokers caused duplicate event dispatches and out of order state overwrites naive database unique constraint checks saturated primary post gres q l connection pools pushing transaction rollback rates two eighteen percent um the r f c mandated deterministic idempotency keys combined with redis bloom filters two intercept duplicate message deliveries before database execution projection workers maintain a seven day sliding deduplication window using one hundred twenty eight bit u u i d hashes stored in distributed redis filter sets if an event passes the bloom filter the worker verifies the monotonic sequence counter against the projection entity table uh canary evaluat across twenty four consumer instances demonstrated that bloom filter pre checks filtered out one hundred percent of duplicate event deliveries reducing projection update latency from forty five milliseconds down two four milliseconds without database lock contention",
        "refined_text": "Our asynchronous integration architecture committee drafted an RFC addressing eventual consistency anomalies and out-of-order message delivery in CQRS projection consumers. During high-throughput order processing spikes of 20000 events per second, network retries from upstream message brokers caused duplicate event dispatches and out-of-order state overwrites. Naive database unique constraint checks saturated primary PostgreSQL connection pools, pushing transaction rollback rates to 18%.\n\nThe RFC mandated deterministic idempotency keys combined with Redis Bloom filters to intercept duplicate message deliveries before database execution. Projection workers maintain a 7-day sliding deduplication window using 128-bit UUID hashes stored in distributed Redis filter sets. If an event passes the Bloom filter, the worker verifies the monotonic sequence counter against the projection entity table. Canary evaluation across 24 consumer instances demonstrated that Bloom filter pre-checks filtered out 100% of duplicate event deliveries, reducing projection update latency from 45 milliseconds down to 4 milliseconds without database lock contention."
    }
]

assert len(batch) == 20, f"Expected 20 samples, got {len(batch)}"

# Check leakage
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, p in enumerate(batch):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into eval!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into eval!"

    # Validator check
    v_ok, v_msg = validate_pair(p)
    assert v_ok, f"Sample {idx+1} failed validate_pair: {v_msg}"

    # Cleaner check
    c_res, c_msg = clean_sample(raw, ref)
    assert c_res is not None, f"Sample {idx+1} failed cleaner: {c_msg}"

    words = len(ref.split())
    if words < 25:
        tier_counts["short"] += 1
    elif words < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1

print(f"Individual pair validation & cleaner: 20/20 PASS")
print(f"Tier counts: {tier_counts}")

# Batch diversity check
b_ok, b_msg, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
assert b_ok, f"Batch diversity failed: {b_msg}"
print(f"Batch diversity check: PASS ({b_tiers})")

# Write to scratch/subagent_batch_46.json
out_path = Path("scratch/subagent_batch_46.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"Successfully saved 20 pairs to {out_path}")
