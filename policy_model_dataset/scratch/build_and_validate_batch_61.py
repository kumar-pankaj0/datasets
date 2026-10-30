import json
import os
import sys

sys.path.insert(0, './code')
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch_61 = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4
    {
        "raw_asr": "our architectural decision record selects kafka topic compact buy preserving the latest state key",
        "refined_text": "Our architectural decision record selects Kafka topic compaction by preserving the latest state key."
    },
    {
        "raw_asr": "this technical r f c rejects post gres in favor of clickhouse four telemetry ingest",
        "refined_text": "This technical RFC rejects Postgres in favor of ClickHouse for telemetry ingestion."
    },
    {
        "raw_asr": "we standardiz inter service r p c payloads on protocol buffers buy deprecating j son",
        "refined_text": "We standardize inter-service RPC payloads on Protocol Buffers by deprecating JSON."
    },
    {
        "raw_asr": "the consensus r f c specifi an election timeout of three hundred milliseconds",
        "refined_text": "The consensus RFC specifies an election timeout of 300 milliseconds."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6
    {
        "raw_asr": "our caching architecture a d r evaluat redis cluster against redis sentinel four distributed lock coordination buy examining multi key transaction support um redis cluster shards keys across one six three eight four hash slots which complicates atomic multi key execution uh the final decision selects redis sentinel buy maintaining master failover within two seconds",
        "refined_text": "Our caching architecture ADR evaluated Redis Cluster against Redis Sentinel for distributed lock coordination by examining multi-key transaction support. Redis Cluster shards keys across 16384 hash slots which complicates atomic multi-key execution.\n\nThe final decision selects Redis Sentinel by maintaining master failover within 2 seconds."
    },
    {
        "raw_asr": "this data synchronizat r f c details the transactional outbox pattern buy writing event payloads directly two an outbox table in post gres during the primary write transaction um debezium captures write ahead log changes buy publishing each record two kafka within fifty milliseconds which eliminates distributed two phase commit overhead",
        "refined_text": "This data synchronization RFC details the transactional outbox pattern by writing event payloads directly to an outbox table in Postgres during the primary write transaction.\n\nDebezium captures write-ahead log changes by publishing each record to Kafka within 50 milliseconds, which eliminates distributed two-phase commit overhead."
    },
    {
        "raw_asr": "our observability a d r adopts an open telemetry collector gateway cluster rather than direct client egress two external backends um the central gateway pools connections buy batching trace spans and strips sensitive credential headers uh each collector instance scales horizontally when memory reaches eighty percent capacity",
        "refined_text": "Our observability ADR adopts an OpenTelemetry collector gateway cluster rather than direct client egress to external backends.\n\nThe central gateway pools connections by batching trace spans and strips sensitive credential headers. Each collector instance scales horizontally when memory reaches 80% capacity."
    },
    {
        "raw_asr": "this database infrastructure r f c mandates transaction pooling mode in p g bouncer instead of session pooling four our core api services um transaction pooling reallocates backend server connections immediately after each transaction block finishes uh this design limits total active connections two post gres at two hundred while serving over three thousand client connections",
        "refined_text": "This database infrastructure RFC mandates transaction pooling mode in PgBouncer instead of session pooling for our core API services.\n\nTransaction pooling reallocates backend server connections immediately after each transaction block finishes. This design limits total active connections to Postgres at 200 while serving over 3000 client connections."
    },
    {
        "raw_asr": "our storage evaluation a d r selects scylla d b over apache cassandra four high throughput sensor ingest um scylla d b uses a c plus plus thread per core seastar engine which eliminates j v m garbage collection pauses uh our benchmarks sustained fifty thousand write requests per second with p ninety nine tail latency remaining below four milliseconds",
        "refined_text": "Our storage evaluation ADR selects ScyllaDB over Apache Cassandra for high-throughput sensor ingestion. ScyllaDB uses a C++ thread-per-core Seastar engine which eliminates JVM garbage collection pauses.\n\nOur benchmarks sustained 50000 write requests per second with P99 tail latency remaining below 4 milliseconds."
    },
    {
        "raw_asr": "our zero trust security r f c standardiz m t l s certificate distribution across the service mesh buy integrating spire agent daemons um spire rotates cryptographic x five zero nine identity certificates locally every twelve hours uh this eliminates static credential distribution while enforcing mutual authentication across five hundred backend microservice instances",
        "refined_text": "Our zero-trust security RFC standardizes mTLS certificate distribution across the service mesh by integrating SPIRE agent daemons.\n\nSPIRE rotates cryptographic X.509 identity certificates locally every 12 hours. This eliminates static credential distribution while enforcing mutual authentication across 500 backend microservice instances."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10
    {
        "raw_asr": "this architectural r f c evaluat database scaling options buy comparing citus distributed tables against application level sharding four our primary tenancy tier um our current monolithic post gres instance contains over two million tenant records where write contention on hot index pages causes p ninety nine commit latencies exceeding four hundred milliseconds uh the r f c recommends deploying citus extension knowed clusters with eight worker knowed instances and one central coordinat knowed under this architecture the coordinat knowed distributes tenant tables across shards using a hash of the organization identifier buy routing queries transparently without rewriting application o r m logic staging load tests demonstrated that query routing overhead added less than fifteen milliseconds while write throughput scaled linearly two twenty thousand transactions per second across the cluster without data loss",
        "refined_text": "This architectural RFC evaluated database scaling options by comparing Citus distributed tables against application-level sharding for our primary tenancy tier. Our current monolithic Postgres instance contains over 2000000 tenant records where write contention on hot index pages causes P99 commit latencies exceeding 400 milliseconds. The RFC recommends deploying Citus extension node clusters with 8 worker node instances and one central coordinator node.\n\nUnder this architecture, the coordinator node distributes tenant tables across shards using a hash of the organization identifier by routing queries transparently without rewriting application ORM logic. Staging load tests demonstrated that query routing overhead added less than 15 milliseconds while write throughput scaled linearly to 20000 transactions per second across the cluster without data loss."
    },
    {
        "raw_asr": "our distributed control plane a d r evaluat et see dee against apache zookeeper four managing service registry state and leader election um zookeeper requires running a dedicated j v m cluster with complex garbage collection tuning and substantial operat overhead in memory constrained environments uh the decision record selects et see dee using a seven wait five knowed raft consensus cluster buy taking advantage of its lightweight go runtime and native g r p c watch stream api under this design the consensus engine synchronizes distributed key leases with snapshot intervals set at two thousand transactions heartbeat timers trigger elections within three hundred milliseconds of leader silence during network partition failure tests across two availability zones the five knowed raft quorum maintained continuous consensus without experiencing split brain states or stale reads",
        "refined_text": "Our distributed control plane ADR evaluated etcd against Apache ZooKeeper for managing service registry state and leader election. ZooKeeper requires running a dedicated JVM cluster with complex garbage collection tuning and substantial operational overhead in memory-constrained environments.\n\nThe decision record selects etcd using a 5 node Raft consensus cluster by taking advantage of its lightweight Go runtime and native gRPC watch stream API. Under this design, the consensus engine synchronizes distributed key leases with snapshot intervals set at 2000 transactions. Heartbeat timers trigger elections within 300 milliseconds of leader silence. During network partition failure tests across 2 availability zones, the 5 node Raft quorum maintained continuous consensus without experiencing split-brain states or stale reads."
    },
    {
        "raw_asr": "this event streaming r f c standardiz message fault tolerance across our core messaging topology buy defining dead letter queue forwarding rules four consumer groups um previously malformed payloads caused consumer lag spikes buy stalling consumer threads on unparseable records uh the proposed r f c specifies thirty two partitions four the payments topic and isolates poison pill events into dedicated dead letter topics after five wait three retry attempts with exponential backoff starting at five hundred milliseconds under this architecture consumer workers isolate deserializat failures without blocking sequential event delivery on healthy partitions a secondary reconciliation service monitors the dead letter queue buy inspecting error headers and replaying corrected events after manual verification which reduced pipeline stall incidents two zero during staged stress tests",
        "refined_text": "This event streaming RFC standardizes message fault tolerance across our core messaging topology by defining dead-letter queue forwarding rules for consumer groups. Previously, malformed payloads caused consumer lag spikes by stalling consumer threads on unparseable records.\n\nThe proposed RFC specifies 32 partitions for the payments topic and isolates poison-pill events into dedicated dead-letter topics after 3 retry attempts with exponential backoff starting at 500 milliseconds. Under this architecture, consumer workers isolate deserialization failures without blocking sequential event delivery on healthy partitions. A secondary reconciliation service monitors the dead-letter queue by inspecting error headers and replaying corrected events after manual verification, which reduced pipeline stall incidents to 0 during staged stress tests."
    },
    {
        "raw_asr": "our edge networking a d r evaluat envoy proxy against engine x four ingress traffic management and api gateway capabilities um engine x relies on configuration reloads which introduce connection drop spikes during frequent deployment rollouts uh the architectural decision adopts envoy buy implementing dynamic discovery through the x d s api which stream cluster updates without dropping active tcp connections envoy executes dynamic root matching and native g r p c json transcoding four fifty microservices with connection draining times capped at twenty wait ten milliseconds benchmark results demonstrated that envoy handled eighty thousand concurrent http two connections with p ninety nine latencies remaining stable under dynamic backend registration changes",
        "refined_text": "Our edge networking ADR evaluated Envoy proxy against Nginx for ingress traffic management and API gateway capabilities. Nginx relies on configuration reloads which introduce connection drop spikes during frequent deployment rollouts.\n\nThe architectural decision adopts Envoy by implementing dynamic discovery through the xDS API, which streams cluster updates without dropping active TCP connections. Envoy executes dynamic route matching and native gRPC JSON transcoding for 50 microservices with connection draining times capped at 10 milliseconds. Benchmark results demonstrated that Envoy handled 80000 concurrent HTTP/2 connections with P99 latencies remaining stable under dynamic backend registration changes."
    },
    {
        "raw_asr": "this caching infrastructure r f c specifies a two tier hybrid cache architecture four high traffic product catalog queries um direct redis lookups four every read request created network serialization bottlenecks during flash sales uh the proposal pairs an in memory caffeine cache as tier one with a centralized redis cluster as tier two tier one caches frequent read keys locally with sixteen gigabytes allocated memory buy applying window tiny l f u eviction policies when a cache miss occurs worker threads synchronize buy executing singleflight mutex locks four redis lookups which mitigates stampede spikes against the database tier benchmarks recorded a ninety eight percent local hit ratio which reduced p ninety five catalog latency from six hundred wait four hundred milliseconds down two twelve milliseconds",
        "refined_text": "This caching infrastructure RFC specifies a two-tier hybrid cache architecture for high-traffic product catalog queries. Direct Redis lookups for every read request created network serialization bottlenecks during flash sales.\n\nThe proposal pairs an in-memory Caffeine cache as tier one with a centralized Redis cluster as tier two. Tier one caches frequent read keys locally with 16 gigabytes allocated memory by applying Window TinyLFU eviction policies. When a cache miss occurs, worker threads synchronize by executing singleflight mutex locks for Redis lookups, which mitigates stampede spikes against the database tier. Benchmarks recorded a 98% local hit ratio, which reduced P95 catalog latency from 400 milliseconds down to 12 milliseconds."
    },
    {
        "raw_asr": "this security analytics a d r evaluat clickhouse against elasticsearch four audit event ingest and compliance query retention um elasticsearch indexing incurred extreme memory pressure buy requiring JVM heap allocations exceeding thirty two gigabytes per knowed along with steep disk footprint overhead uh the decision selects clickhouse buy utilizing its columnar merge tree engine paired with z s t d compress clickhouse executes vectorized queries across audit logs without maintaining expensive inverted indices on high cardinality timestamp fields during ingestion load tests clickhouse sustained three hundred thousand wait five hundred thousand records per second across four storage nodes storage consumption dropped buy seventy percent compared two elasticsearch while ninety day audit query execution completed under eight hundred milliseconds",
        "refined_text": "This security analytics ADR evaluated ClickHouse against Elasticsearch for audit event ingestion and compliance query retention. Elasticsearch indexing incurred extreme memory pressure by requiring JVM heap allocations exceeding 32 gigabytes per node along with steep disk footprint overhead.\n\nThe decision selects ClickHouse by utilizing its columnar MergeTree engine paired with ZSTD compression. ClickHouse executes vectorized queries across audit logs without maintaining expensive inverted indices on high-cardinality timestamp fields. During ingestion load tests, ClickHouse sustained 500000 records per second across 4 storage nodes. Storage consumption dropped by 70% compared to Elasticsearch while 90 day audit query execution completed under 800 milliseconds."
    },
    {
        "raw_asr": "this commerce infrastructure r f c propos command query responsibility segregat four our checkout ordering pipeline buy separating relational right commands from read query projections um combining transactional order writes with complex dashboard read aggregations inside a single post gres cluster caused severe lock contention during promotional campaigns uh the proposed architecture delegates all order state mutations two an optimized transactional post gres database while publishing domain change events two kafka streaming topics four worker replicas consume order events buy building denormalized read views in mongo d b with projection lag bounded under two hundred milliseconds benchmark evaluations verified that isolating right operations preserved sub ten millisecond commit times while read throughput handled five thousand queries per second across distributed read replicas",
        "refined_text": "This commerce infrastructure RFC proposes Command Query Responsibility Segregation for our checkout ordering pipeline by separating relational write commands from read query projections. Combining transactional order writes with complex dashboard read aggregations inside a single Postgres cluster caused severe lock contention during promotional campaigns.\n\nThe proposed architecture delegates all order state mutations to an optimized transactional Postgres database while publishing domain change events to Kafka streaming topics. 4 worker replicas consume order events by building denormalized read views in MongoDB with projection lag bounded under 200 milliseconds. Benchmark evaluations verified that isolating write operations preserved sub-10 millisecond commit times while read throughput handled 5000 queries per second across distributed read replicas."
    },
    {
        "raw_asr": "our public api architecture a d r evaluat graph q l federation against g r p c gateway four unifying external client access across distributed backend domains um graph q l federation simplifies mobile client data fetching but introduces significant query planning latency and n plus one resolver waterfall overhead during nested entity resolution uh the architectural decision record adopts g r p c gateway buy compiling protocol buffer contracts directly into open api compliant h t t p json endpoints this architecture terminates client h t t p requests at a stateless gateway knowed buy forwarding binary g r p c streams two twelve backend microservices across the mesh load testing revealed that g r p c gateway reduced p ninety nine external request latency from fifty wait twenty milliseconds while sustaining ten thousand requests per second with minimal cpu utilization",
        "refined_text": "Our public API architecture ADR evaluated GraphQL federation against gRPC gateway for unifying external client access across distributed backend domains. GraphQL federation simplifies mobile client data fetching, but introduces significant query planning latency and N+1 resolver waterfall overhead during nested entity resolution.\n\nThe architectural decision record adopts gRPC gateway by compiling Protocol Buffer contracts directly into OpenAPI-compliant HTTP JSON endpoints. This architecture terminates client HTTP requests at a stateless gateway node by forwarding binary gRPC streams to 12 backend microservices across the mesh. Load testing revealed that gRPC gateway reduced P99 external request latency from 20 milliseconds while sustaining 10000 requests per second with minimal CPU utilization."
    },
    {
        "raw_asr": "this api gateway r f c propos a distributed rate limiting architecture buy implementing the token bucket algorithm inside redis lua scripts um basic fixed window counters allowed double traffic bursts around window boundaries which overloaded downstream auth services uh the r f c standardiz on atomic redis lua token bucket evaluat buy tracking bucket capacity and fractional token refills in a single network roundtrip when client requests arrive the gateway executes the lua script against redis with bucket capacity set at ten wait five hundred tokens and refill rates of fifty tokens per second if available tokens fall below one the proxy rejects the incoming request buy returning status four hundred twenty nine with retry after headers staging benchmarks proved that this rate limiter processed sixty thousand requests per second with execution latency remaining below one millisecond",
        "refined_text": "This API gateway RFC proposes a distributed rate-limiting architecture by implementing the token bucket algorithm inside Redis Lua scripts. Basic fixed-window counters allowed double traffic bursts around window boundaries which overloaded downstream auth services.\n\nThe RFC standardizes on atomic Redis Lua token bucket evaluation by tracking bucket capacity and fractional token refills in a single network roundtrip. When client requests arrive, the gateway executes the Lua script against Redis with bucket capacity set at 500 tokens and refill rates of 50 tokens per second. If available tokens fall below 1, the proxy rejects the incoming request by returning status 429 with retry-after headers. Staging benchmarks proved that this rate limiter processed 60000 requests per second with execution latency remaining below 1 millisecond."
    },
    {
        "raw_asr": "our telemetry architecture a d r evaluat tail based sampling against head based sampling four distributed trace collection across forty microservices um head based sampling makes sampling decisions at the originating span which dropped valuable anomaly traces during intermittent staging outages uh the decision record selects tail based sampling buy deploying open telemetry collector gateway knowed clusters with trace sampling buffers under this design collector gateway instances buffer trace spans in memory until full traces complete buy inspecting trace status codes and total duration collectors preserve one hundred percent of traces containing error status codes and any trace exceeding two hundred milliseconds latency while retaining ten percent wait five percent of successful requests canary testing confirmed that tail based sampling reduced backend trace storage volume buy eighty percent while guaranteeing complete visibility into critical failures",
        "refined_text": "Our telemetry architecture ADR evaluated tail-based sampling against head-based sampling for distributed trace collection across 40 microservices. Head-based sampling makes sampling decisions at the originating span, which dropped valuable anomaly traces during intermittent staging outages.\n\nThe decision record selects tail-based sampling by deploying OpenTelemetry collector gateway node clusters with trace sampling buffers. Under this design, collector gateway instances buffer trace spans in memory until full traces complete by inspecting trace status codes and total duration. Collectors preserve 100% of traces containing error status codes and any trace exceeding 200 milliseconds latency while retaining 5% of successful requests. Canary testing confirmed that tail-based sampling reduced backend trace storage volume by 80% while guaranteeing complete visibility into critical failures."
    }
]

# Output path
output_path = "scratch/subagent_batch_61.json"

# Write JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(batch_61, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(batch_61)} pairs to {output_path}")

# Run pair validation and cleaner validation on each sample
pair_failures = 0
cleaner_failures = 0
tier_distribution = {"Short": 0, "Medium": 0, "Long": 0}

for idx, sample in enumerate(batch_61):
    raw = sample["raw_asr"]
    ref = sample["refined_text"]
    words = len(ref.split())

    if words < 25:
        tier = "Short"
    elif words < 90:
        tier = "Medium"
    else:
        tier = "Long"
    tier_distribution[tier] += 1

    # validate_pair
    v_ok, v_msg = validate_pair(sample)
    if not v_ok:
        print(f"FAILED validate_pair on sample {idx+1}: {v_msg}")
        pair_failures += 1

    # clean_sample
    c_res, c_msg = clean_sample(raw, ref)
    if c_res is None or c_msg != "kept":
        print(f"FAILED clean_sample on sample {idx+1}: {c_msg}")
        cleaner_failures += 1

# Run batch validation
b_ok, b_msg, counts = validate_batch(batch_61, min_short=4, min_medium=6, min_long=10)
if not b_ok:
    print(f"FAILED validate_batch: {b_msg}")
else:
    print(f"PASSED validate_batch: {b_msg}")

print(f"Summary:")
print(f"Total pairs: {len(batch_61)}")
print(f"Tier counts: {tier_distribution} (validator counts: {counts})")
print(f"Pair failures: {pair_failures}")
print(f"Cleaner failures: {cleaner_failures}")
print(f"Batch validation: {'PASS' if b_ok else 'FAIL'}")

if pair_failures == 0 and cleaner_failures == 0 and b_ok:
    print("\nALL 20 SAMPLES PERFECTLY PASSED DETERMINISTIC VALIDATION!")
else:
    sys.exit(1)
