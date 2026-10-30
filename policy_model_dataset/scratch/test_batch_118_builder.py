import json
import re
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
    # --- Short Samples (1 to 4: < 25 words, exactly 1 sentence, 0 newlines) ---
    # Sample 1: Domain 9 (Coding Interview)
    {
        "raw_asr": "um the candidate solved the maximum subarray problem buy implement a sliding window across sixteen array elements",
        "refined_text": "The candidate solved the maximum subarray problem by implementing a sliding window across 16 array elements."
    },
    # Sample 2: Domain 5 (Mentoring / Onboarding)
    {
        "raw_asr": "uh mount the local development directory into the container buy configur eight persistent volume mounts",
        "refined_text": "Mount the local development directory into the container by configuring 8 persistent volume mounts."
    },
    # Sample 3: Domain 9 (System Design)
    {
        "raw_asr": "basically distribut keys evenly across sixty four virtual nodes buy hashing partition identifiers",
        "refined_text": "Distribute keys evenly across 64 virtual nodes by hashing partition identifiers."
    },
    # Sample 4: Domain 5 (Mentoring / Database)
    {
        "raw_asr": "um adjust the pool timeout buy configur thirty worker connections inside the database client",
        "refined_text": "Adjust the pool timeout by configuring 30 worker connections inside the database client."
    },

    # --- Medium Samples (5 to 10: 25 to 89 words, 1-3 sentences, with \n\n) ---
    # Sample 5: Domain 9 (Coding Interview Debrief)
    {
        "raw_asr": "the candidate solved the next greater element problem buy maintaining a monotonic stack across fifty array inputs wait evaluat the worst case time complexity inside stack underscore analyzer dot py instead um confirm that the algorithm runs in linear time buy processing each element exactly once",
        "refined_text": "The candidate solved the next greater element problem by maintaining a monotonic stack across 50 array inputs, evaluating the worst-case time complexity inside stack_analyzer.py instead.\n\nConfirm that the algorithm runs in linear time by processing each element exactly once."
    },
    # Sample 6: Domain 5 (Onboarding - Database Seeding)
    {
        "raw_asr": "four local onboarding run the initial schema migrations across twelve relational tables wait seed sixty sample records buy executing seed underscore fixtures dot py instead um verify that the local post gres instance accepts connections across eight testing databases without errors",
        "refined_text": "For local onboarding run the initial schema migrations across 12 relational tables, seeding 60 sample records by executing seed_fixtures.py instead.\n\nVerify that the local Postgres instance accepts connections across 8 testing databases without errors."
    },
    # Sample 7: Domain 9 (System Design - Distributed Locks)
    {
        "raw_asr": "the candidate designed a distributed locking mechanism buy acquiring key leases across five redis nodes wait handl lease expiration buy checking renewal heartbeats inside lock underscore manager dot py instead um confirm that lock releases execute buy matching ownership tokens across twenty worker threads",
        "refined_text": "The candidate designed a distributed locking mechanism by acquiring key leases across 5 Redis nodes, handling lease expiration by checking renewal heartbeats inside lock_manager.py instead.\n\nConfirm that lock releases execute by matching ownership tokens across 20 worker threads."
    },
    # Sample 8: Domain 5 (Mentoring - Mutex & Race Condition)
    {
        "raw_asr": "in our mentoring session we examined a race condition occurring across sixteen concurrent request handlers wait synchroniz counter mutations buy acquiring a mutual exclusion lock inside counter underscore state dot py instead um observ that data corruption drops down into zero errors across forty test iterations",
        "refined_text": "In our mentoring session we examined a race condition occurring across 16 concurrent request handlers, synchronizing counter mutations by acquiring a mutual exclusion lock inside counter_state.py instead.\n\nObserve that data corruption drops down into 0 errors across 40 test iterations."
    },
    # Sample 9: Domain 9 (Interview Evaluation - Topological Sort)
    {
        "raw_asr": "our interview debrief evaluated the candidate approach two cycle detection across seventy package dependency nodes wait determin build orders buy executing a depth first search inside dependency underscore graph dot py instead um measur that graph traversal completes across twenty five milliseconds without recursion overflow",
        "refined_text": "Our interview debrief evaluated the candidate approach to cycle detection across 70 package dependency nodes, determining build orders by executing a depth-first search inside dependency_graph.py instead.\n\nMeasure that graph traversal completes across 25 milliseconds without recursion overflow."
    },
    # Sample 10: Domain 5 (Mentoring - Replication Lag & Cache Sync)
    {
        "raw_asr": "when mentoring new hires we explain replication lag across four database read replicas wait invalidat stale cache entries buy emitting event notifications inside cache underscore sync dot py instead um confirm that cache consistency recovers within thirty seconds across all read queries",
        "refined_text": "When mentoring new hires we explain replication lag across 4 database read replicas, invalidating stale cache entries by emitting event notifications inside cache_sync.py instead.\n\nConfirm that cache consistency recovers within 30 seconds across all read queries."
    },

    # --- Long Samples (11 to 20: 90+ words, multi-paragraph with \n\n) ---
    # Sample 11: Domain 9 (System Design - Timeline Feed Fan-Out)
    {
        "raw_asr": "in today system design interview we evaluated the candidate architecture four generating timeline feeds across twenty million active users the candidate proposed a fan out on write model where publishing a post delivers identifiers directly into timeline inboxes across five thousand followers our panel discussed how celebrity accounts with millions of followers cause severe write amplification spikes when pushing updates buy analyzing storage trade offs the candidate introduced a hybrid approach storing posts in memory and fetching updates dynamically four high follower accounts um the candidate structured the message ingestion pipeline buy delegating fan out tasks two asynchronous background workers inside feed underscore distributor dot py we examined latency bottlenecks when redis caches experience network partitions and the candidate demonstrated solid understanding buy implementing client circuit breakers finally the interview debrief highlighted that the candidate justified trade offs clearly buy keeping p ninety nine latency under eighty milliseconds across four regional clusters our panel recommended hiring at the senior backend engineer level",
        "refined_text": "In today system design interview we evaluated the candidate architecture for generating timeline feeds across 20000000 active users. The candidate proposed a fan-out on write model where publishing a post delivers identifiers directly into timeline inboxes across 5000 followers. Our panel discussed how celebrity accounts with millions of followers cause severe write amplification spikes when pushing updates by analyzing storage trade-offs.\n\nThe candidate structured the message ingestion pipeline by delegating fan-out tasks to asynchronous background workers inside feed_distributor.py. We examined latency bottlenecks when Redis caches experience network partitions, and the candidate demonstrated solid understanding by implementing client circuit breakers.\n\nFinally the interview debrief highlighted that the candidate justified trade-offs clearly by keeping P99 latency under 80 milliseconds across 4 regional clusters. Our panel recommended hiring at the senior backend engineer level."
    },
    # Sample 12: Domain 5 (Mentoring - Microservice gRPC & Protobuf)
    {
        "raw_asr": "during our technical mentoring session today i walked our new engineer through our microservice communication layer our platform relies on g r p c over h t t p two four synchronous inter service calls across thirty distinct services we reviewed the protobuf contract definitions buy examining message serialization and backwards compatibility rules inside order underscore service dot py our discussion covered schema evolution verifying that adding fields preserves field tag numbers between one through twelve buy maintaining backward compatibility with older clients um we then inspected our shared client interceptor implementation which manages automatic retry attempts and contextual tracing headers across fifty worker processes i explained how interceptors attach distributed trace identifiers two outbound requests allowing jaeger collectors two assemble end two end request traces we also addressed transient error handling buy configuring exponential backoff with jitter across three retry attempts avoiding thundering herd effects on downstream database servers finally we walked through local testing procedures buy running mock g r p c servers across four docker containers our new hire successfully deployed a test service and verified that p ninety five response latency remained below fifteen milliseconds across one thousand synthetic test queries",
        "refined_text": "During our technical mentoring session today I walked our new engineer through our microservice communication layer. Our platform relies on gRPC over HTTP2 for synchronous inter-service calls across 30 distinct services. We reviewed the Protobuf contract definitions by examining message serialization and backwards compatibility rules inside order_service.py.\n\nOur discussion covered schema evolution, verifying that adding fields preserves field tag numbers between 1 through 12 by maintaining backward compatibility with older clients. We then inspected our shared client interceptor implementation which manages automatic retry attempts and contextual tracing headers across 50 worker processes. I explained how interceptors attach distributed trace identifiers to outbound requests, allowing Jaeger collectors to assemble end-to-end request traces.\n\nWe also addressed transient error handling by configuring exponential backoff with jitter across 3 retry attempts, avoiding thundering herd effects on downstream database servers. Finally we walked through local testing procedures by running mock gRPC servers across 4 Docker containers. Our new hire successfully deployed a test service and verified that P95 response latency remained below 15 milliseconds across 1000 synthetic test queries."
    },
    # Sample 13: Domain 9 (Coding Interview Debrief - Trie Autocomplete)
    {
        "raw_asr": "in our candidate debrief session we reviewed the technical coding interview four a platform candidate who implemented an autocomplete prefix search the problem required returning top five matching search terms four arbitrary prefix strings across a vocabulary of one hundred thousand terms the candidate evaluated two approaches comparing a trie data structure against a flattened hash map of prefixes buy analyzing memory and lookup complexity the candidate chose a trie with child node pointers storing top search frequencies at each node um during the implementation phase the candidate wrote clean recursive traversal logic inside prefix underscore search dot py handling edge cases including empty strings and missing prefix branches with minimal overhead we discussed space complexity trade offs where allocating child pointer arrays across twenty six character alphabets increases heap consumption significantly the candidate resolved this concern buy switching child node storage two dynamic hash tables inside node representations finally the candidate demonstrated strong testing practices buy writing eight unit tests covering unicode input and deep prefix paths our debrief concluded with a unanimous recommendation two hire the candidate as a senior software engineer",
        "refined_text": "In our candidate debrief session we reviewed the technical coding interview for a platform candidate who implemented an autocomplete prefix search. The problem required returning top 5 matching search terms for arbitrary prefix strings across a vocabulary of 100000 terms. The candidate evaluated 2 approaches comparing a Trie data structure against a flattened hash map of prefixes by analyzing memory and lookup complexity.\n\nDuring the implementation phase the candidate wrote clean recursive traversal logic inside prefix_search.py, handling edge cases including empty strings and missing prefix branches with minimal overhead. We discussed space complexity trade-offs where allocating child pointer arrays across 26 character alphabets increases heap consumption significantly. The candidate resolved this concern by switching child node storage to dynamic hash tables inside node representations.\n\nFinally the candidate demonstrated strong testing practices by writing 8 unit tests covering Unicode input and deep prefix paths. Our debrief concluded with a unanimous recommendation to hire the candidate as a senior software engineer."
    },
    # Sample 14: Domain 5 (Mentoring - Database MVCC & Isolation)
    {
        "raw_asr": "in today architecture mentoring session we discussed database transaction isolation levels and concurrency anomalies with our onboarding engineers our application handles concurrent financial ledger updates where dirty reads and non repeatable reads cause account balance discrepancies we examined how post gres implements multi version concurrency control buy maintaining row versions identified buy transaction numbers instead of locking entire tables um i walked through an example inside transaction underscore manager dot py showing how repeatable read isolation prevents lost updates across sixty concurrent checkout transactions we demonstrated that repeatable read guarantees a snapshot view based on the transaction start time buy rejecting conflicting commits with serialization failures we also analyzed write skew anomalies where two transactions modify separate records based on overlapping query predicates finally we reviewed our retry helper which catches post gres serialization errors and retries failed transactions with exponential backoff across five attempts our engineers configured automated tests validating that forty concurrent balance transfers complete without ledger imbalances",
        "refined_text": "In today architecture mentoring session we discussed database transaction isolation levels and concurrency anomalies with our onboarding engineers. Our application handles concurrent financial ledger updates where dirty reads and non-repeatable reads cause account balance discrepancies. We examined how Postgres implements multi-version concurrency control by maintaining row versions identified by transaction numbers instead of locking entire tables.\n\nI walked through an example inside transaction_manager.py showing how repeatable read isolation prevents lost updates across 60 concurrent checkout transactions. We demonstrated that repeatable read guarantees a snapshot view based on the transaction start time by rejecting conflicting commits with serialization failures. We also analyzed write skew anomalies where 2 transactions modify separate records based on overlapping query predicates.\n\nFinally we reviewed our retry helper which catches Postgres serialization errors and retries failed transactions with exponential backoff across 5 attempts. Our engineers configured automated tests validating that 40 concurrent balance transfers complete without ledger imbalances."
    },
    # Sample 15: Domain 9 (System Design - Distributed Snowflake IDs)
    {
        "raw_asr": "in our system design interview we asked the candidate two design a globally unique distributed identification generator capable of producing ten thousand identifiers per second across eight worker nodes the candidate proposed a sixty four bit integer layout inspired buy the snowflake algorithm allocating forty one bits four millisecond timestamps ten bits four worker node identifiers and twelve bits four per millisecond sequence counters our interview panel discussed clock drift challenges where system clocks step backward during network time protocol synchronization um the candidate addressed clock skew buy rejecting id generation requests whenever local wall clock time moves behind the last generated timestamp inside generator underscore core dot py we explored high availability strategies when single worker nodes crash and the candidate explained how zookeeper coordinates worker node allocation across thirty two active instances without duplicate sequence collisions finally our debrief session noted that the candidate calculated throughput boundaries accurately buy proving that twelve bit sequence numbers allow up two four zero nine six unique identifiers per millisecond on each node our hiring committee gave a strong recommendation four a staff engineer position",
        "refined_text": "In our system design interview we asked the candidate to design a globally unique distributed identification generator capable of producing 10000 identifiers per second across 8 worker nodes. The candidate proposed a 64-bit integer layout inspired by the Snowflake algorithm, allocating 41 bits for millisecond timestamps, 10 bits for worker node identifiers, and 12 bits for per-millisecond sequence counters. Our interview panel discussed clock drift challenges where system clocks step backward during network time protocol synchronization.\n\nThe candidate addressed clock skew by rejecting ID generation requests whenever local wall-clock time moves behind the last generated timestamp inside generator_core.py. We explored high availability strategies when single worker nodes crash, and the candidate explained how ZooKeeper coordinates worker node allocation across 32 active instances without duplicate sequence collisions.\n\nFinally our debrief session noted that the candidate calculated throughput boundaries accurately by proving that 12-bit sequence numbers allow up to 4096 unique identifiers per millisecond on each node. Our hiring committee gave a strong recommendation for a staff engineer position."
    },
    # Sample 16: Domain 5 (Onboarding - Service Mesh & mTLS)
    {
        "raw_asr": "during developer onboarding today i explained our service mesh architecture and traffic encryption policies two our junior platform engineers our production kubernetes clusters deploy envoy sidecar proxies alongside every application pod managing ingress and egress communication across seventy microservices we reviewed mutual transport layer security configuration buy inspecting x five zero nine certificates and cryptographic identity validation inside mesh underscore gateway dot py our discussion covered how envoy sidecars enforce strict m t l s buy verifying client certificates against trusted cluster authority pools um we then walked through local debugging workflows using proxy access logs two diagnose connection drops across sixteen upstream endpoints i demonstrated how developers configure header routing rules buy matching custom user tier cookies inside routing underscore rules dot yaml we also examined distributed tracing propagation where envoy automatically generates trace headers across twenty downstream service calls finally our onboarding session concluded with a hands on exercise where the engineer configured traffic splitting rules buy directing ten percent of staging requests towards canary containers across twelve test executions",
        "refined_text": "During developer onboarding today I explained our service mesh architecture and traffic encryption policies to our junior platform engineers. Our production Kubernetes clusters deploy Envoy sidecar proxies alongside every application pod, managing ingress and egress communication across 70 microservices. We reviewed mutual transport layer security configuration by inspecting X.509 certificates and cryptographic identity validation inside mesh_gateway.py.\n\nOur discussion covered how Envoy sidecars enforce strict mTLS by verifying client certificates against trusted cluster authority pools. We then walked through local debugging workflows using proxy access logs to diagnose connection drops across 16 upstream endpoints. I demonstrated how developers configure header routing rules by matching custom user tier cookies inside routing_rules.yaml.\n\nWe also examined distributed tracing propagation where Envoy automatically generates trace headers across 20 downstream service calls. Finally our onboarding session concluded with a hands-on exercise where the engineer configured traffic splitting rules by directing 10 percent of staging requests towards canary containers across 12 test executions."
    },
    # Sample 17: Domain 9 (Candidate Debrief - Raft Consensus)
    {
        "raw_asr": "in our candidate evaluation debrief we analyzed the candidate responses during our distributed consensus interview round the candidate was asked two implement leader election and log compaction four a raft consensus cluster comprising five participant nodes we examined how the candidate handled randomized election timeouts between one hundred fifty milliseconds through three hundred milliseconds buy preventing recurring split vote deadlocks the candidate demonstrated deep knowledge of quorum mechanics buy requiring agreement across three nodes before committing log entries um we then evaluated the candidate design four log truncation and snapshot transfer inside consensus underscore state dot py the candidate explained how leader nodes transmit snapshot chunks whenever lagging follower nodes fall more than five hundred log entries behind the committed index our panel questioned the candidate on network partition scenarios where split brain conditions could emerge and the candidate showed how term numbers enforce strict monotonicity across twelve partitioned nodes finally our hiring debrief noted that the candidate communicated edge cases clearly buy identifying uncommitted log overwrites during leader transitions our panel unanimously recommended extending an offer four a principal infrastructure engineer",
        "refined_text": "In our candidate evaluation debrief we analyzed the candidate responses during our distributed consensus interview round. The candidate was asked to implement leader election and log compaction for a Raft consensus cluster comprising 5 participant nodes. We examined how the candidate handled randomized election timeouts between 150 milliseconds through 300 milliseconds by preventing recurring split-vote deadlocks.\n\nThe candidate demonstrated deep knowledge of quorum mechanics by requiring agreement across 3 nodes before committing log entries. We then evaluated the candidate design for log truncation and snapshot transfer inside consensus_state.py. The candidate explained how leader nodes transmit snapshot chunks whenever lagging follower nodes fall more than 500 log entries behind the committed index.\n\nOur panel questioned the candidate on network partition scenarios where split-brain conditions could emerge, and the candidate showed how term numbers enforce strict monotonicity across 12 partitioned nodes. Finally our hiring debrief noted that the candidate communicated edge cases clearly by identifying uncommitted log overwrites during leader transitions. Our panel unanimously recommended extending an offer for a principal infrastructure engineer."
    },
    # Sample 18: Domain 5 (Mentoring - Memory Profiling & GC Tuning)
    {
        "raw_asr": "in today performance mentoring session i paired with our backend engineer two investigate heap memory growth in our streaming worker service our telemetry showed that garbage collection pauses exceeded eighty milliseconds during sustained event processing across sixteen worker threads we analyzed heap allocation profiles buy capturing memory dumps with p prof inside memory underscore profiler dot py our investigation revealed that high throughput deserialization allocated sixty thousand temporary buffer objects per second causing severe garbage collection pressure um i guided the engineer through implementing an object pool buy reusing byte buffers across twenty concurrent subscriber routines we configured sync pool allocations buy pre sizing buffers two sixty four kilobytes avoiding repeated heap reallocation during payload processing our profiling run confirmed that memory allocation rates dropped buy seventy percent across forty benchmark iterations we also reviewed memory limits inside our container deployment definitions buy setting container memory thresholds two five hundred twelve megabytes finally we verified that p ninety nine latency decreased down into twelve milliseconds across eighteen simulated customer workloads giving our engineer hands on experience with production performance profiling",
        "refined_text": "In today performance mentoring session I paired with our backend engineer to investigate heap memory growth in our streaming worker service. Our telemetry showed that garbage collection pauses exceeded 80 milliseconds during sustained event processing across 16 worker threads. We analyzed heap allocation profiles by capturing memory dumps with pprof inside memory_profiler.py.\n\nOur investigation revealed that high-throughput deserialization allocated 60000 temporary buffer objects per second, causing severe garbage collection pressure. I guided the engineer through implementing an object pool by reusing byte buffers across 20 concurrent subscriber routines. We configured sync pool allocations by pre-sizing buffers to 64 kilobytes, avoiding repeated heap reallocation during payload processing.\n\nOur profiling run confirmed that memory allocation rates dropped by 70 percent across 40 benchmark iterations. We also reviewed memory limits inside our container deployment definitions by setting container memory thresholds to 512 megabytes. Finally we verified that P99 latency decreased down into 12 milliseconds across 18 simulated customer workloads, giving our engineer hands-on experience with production performance profiling."
    },
    # Sample 19: Domain 9 (System Design - Rate Limiting with Redis)
    {
        "raw_asr": "in our system design interview we evaluated the candidate architecture four building a distributed a p i rate limiting service protecting twelve public microservices the candidate compared three rate limiting algorithms contrasting token bucket leaky bucket and sliding window counter models buy analyzing memory and burst traffic behavior the candidate selected a redis based sliding window log buy recording timestamped request entries in sorted sets across eight cache shards our interviewers asked how the system enforces a quota of one thousand requests per minute across fifty concurrent tenant a p i keys um the candidate detailed the atomic execution model buy writing lua scripts inside rate underscore evaluator dot py ensuring that token checks and decrements execute within a single round trip we explored fail open versus fail closed strategies during redis cluster degradation and the candidate recommended falling back two local in memory token buckets buy preserving upstream service availability our debrief session highlighted that the candidate measured p ninety five evaluation latency under five milliseconds across thirty synthetic load runs our committee agreed that the candidate met all hiring bars four a staff systems engineer",
        "refined_text": "In our system design interview we evaluated the candidate architecture for building a distributed API rate limiting service protecting 12 public microservices. The candidate compared 3 rate limiting algorithms contrasting token bucket, leaky bucket, and sliding window counter models by analyzing memory and burst traffic behavior. The candidate selected a Redis-based sliding window log by recording timestamped request entries in sorted sets across 8 cache shards.\n\nOur interviewers asked how the system enforces a quota of 1000 requests per minute across 50 concurrent tenant API keys. The candidate detailed the atomic execution model by writing Lua scripts inside rate_evaluator.py, guaranteeing that token checks and decrements execute within a single round trip. We explored fail-open versus fail-closed strategies during Redis cluster degradation, and the candidate recommended falling back to local in-memory token buckets by preserving upstream service availability.\n\nOur debrief session highlighted that the candidate measured P95 evaluation latency under 5 milliseconds across 30 synthetic load runs. Our committee agreed that the candidate met all hiring bars for a staff systems engineer."
    },
    # Sample 20: Domain 5 (Mentoring - Kafka Partition Rebalancing)
    {
        "raw_asr": "during our architecture mentoring session i paired with an onboarding engineer two resolve consumer lag spikes across twelve kafka event partitions our payment processing consumer group experienced extended processing pauses during partition rebalancing whenever individual worker pods restarted we analyzed consumer group coordination logs buy inspecting heartbeat intervals and session timeouts inside partition underscore consumer dot py our session revealed that default eager rebalance assignors revoked all partition assignments across eight active workers causing processing pipelines two halt completely um i explained how switching two cooperative sticky partition assignors enables incremental rebalancing buy allowing unaffected consumer workers two continue processing messages we adjusted session timeouts two forty five seconds and heartbeat intervals two fifteen seconds buy preventing premature consumer evictions during heavy payload processing we also reviewed consumer lag monitoring metrics buy setting alerts whenever partition lag exceeds five thousand unread records across ten consecutive check intervals finally our mentoring session concluded with a chaos test where we terminated two consumer pods across six test iterations verifying that message processing continued across remaining workers without consumer group stalls",
        "refined_text": "During our architecture mentoring session I paired with an onboarding engineer to resolve consumer lag spikes across 12 Kafka event partitions. Our payment processing consumer group experienced extended processing pauses during partition rebalancing whenever individual worker pods restarted. We analyzed consumer group coordination logs by inspecting heartbeat intervals and session timeouts inside partition_consumer.py.\n\nOur session revealed that default eager rebalance assignors revoked all partition assignments across 8 active workers, causing processing pipelines to halt completely. I explained how switching to cooperative sticky partition assignors enables incremental rebalancing by allowing unaffected consumer workers to continue processing messages. We adjusted session timeouts to 45 seconds and heartbeat intervals to 15 seconds by preventing premature consumer evictions during heavy payload processing.\n\nWe also reviewed consumer lag monitoring metrics by setting alerts whenever partition lag exceeds 5000 unread records across 10 consecutive check intervals. Finally our mentoring session concluded with a chaos test where we terminated 2 consumer pods across 6 test iterations, verifying that message processing continued across remaining workers without consumer group stalls."
    }
]

print(f"Total candidate pairs: {len(pairs)}")
assert len(pairs) == 20

tiers = {"short": 0, "medium": 0, "long": 0}
all_passed = True

for idx, p in enumerate(pairs):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # ASCII check
    try:
        raw.encode("ascii")
        ref.encode("ascii")
    except UnicodeEncodeError as e:
        print(f"Sample {idx+1} Non-ASCII: {e}")
        all_passed = False

    # Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"Sample {idx+1} raw leaked into sft_eval.json!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {idx+1} ref leaked into sft_eval.json!")
        all_passed = False

    # Validator check
    val_ok, val_msg = val_mod.validate_pair(p)
    if not val_ok:
        print(f"Sample {idx+1} failed validate_pair: {val_msg}")
        all_passed = False

    # Cleaner check
    clean_res, clean_status = clean_mod.clean_sample(raw, ref)
    if clean_res is None or clean_status != "kept":
        print(f"Sample {idx+1} failed clean_sample: {clean_status}")
        all_passed = False

    # Tier check
    w_count = len(ref.split())
    if w_count < 25:
        tiers["short"] += 1
        if "\n" in ref:
            print(f"Sample {idx+1} has newline in short tier!")
            all_passed = False
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        if len(sentences) != 1:
            print(f"Sample {idx+1} has {len(sentences)} sentences, expected 1! ({sentences})")
            all_passed = False
    elif w_count < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        if not (1 <= len(sentences) <= 3):
            print(f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3! ({sentences})")
            all_passed = False
        if "\n\n" not in ref:
            print(f"Sample {idx+1} missing paragraph break in medium tier!")
            all_passed = False
    else:
        tiers["long"] += 1
        if "\n\n" not in ref:
            print(f"Sample {idx+1} missing paragraph break in long tier!")
            all_passed = False

print(f"Tiers: {tiers}")
if tiers["short"] != 4 or tiers["medium"] != 6 or tiers["long"] != 10:
    print(f"Tier mismatch! Expected 4 short, 6 medium, 10 long. Got {tiers}")
    all_passed = False

batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
if not batch_ok:
    print(f"Batch validation failed: {batch_msg}")
    all_passed = False

if all_passed:
    print("SUCCESS: All 20 samples passed all deterministic validations!")
    out_file = Path("scratch/subagent_batch_118.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)
    print(f"Saved to {out_file}")
else:
    print("FAILED some checks.")
