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
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e.get("raw_asr", "").strip().lower() for e in eval_data}
    eval_refs = {e.get("refined_text", "").strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 complete sentence. 0 newlines. Max 1 cut-word. Min 3 noise layers.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # =========================================================================

    # Sample 1: Domain 3 (PR Review) - Async worker routine allocation
    {
        "raw_asr": "um allocat eight a sink worker routines buy setting pool underscore size inside slash src slash pool dot py",
        "refined_text": "Allocate 8 async worker routines by setting pool_size inside /src/pool.py."
    },

    # Sample 2: Domain 3 (PR Review) - Postgres connection timeout configuration
    {
        "raw_asr": "uh configur post gres connection timeouts buy updating database underscore config inside slash db slash client dot go",
        "refined_text": "Configure Postgres connection timeouts by updating database_config inside /db/client.go."
    },

    # Sample 3: Domain 5 (Technical Mentoring) - RPC retry limit initialization
    {
        "raw_asr": "basically initializ r p c client retries buy setting retry underscore limit towards four attempts",
        "refined_text": "Initialize RPC client retries by setting retry_limit towards 4 attempts."
    },

    # Sample 4: Domain 5 (Technical Mentoring) - CPU thread affinity allocation
    {
        "raw_asr": "you know allocat c p u thread affinity buy setting mask inside slash sys slash cpu dot c",
        "refined_text": "Allocate CPU thread affinity by setting mask inside /sys/cpu.c."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Min 4 noise layers. Zero purpose patterns.
    # =========================================================================

    # Sample 5: Domain 3 (PR Review) - HTTP response body memory leak and buffer pool
    {
        "raw_asr": "um in slash net slash client dot go the author creates memory leaks buy omitting response body closure across worker routines wait switch to reusable buffers buy storing slices inside buffer underscore pool instead basically failing at terminat unread response bodies exhausts c p u cache lines across eight connections right two integration tests confirming zero memory growth",
        "refined_text": "In /net/client.go, the author creates memory leaks by omitting response body closure across worker routines, switching to reusable buffers by storing slices inside buffer_pool instead.\n\nFailing at terminating unread response bodies exhausts CPU cache lines across 8 connections. Write 2 integration tests confirming zero memory growth."
    },

    # Sample 6: Domain 3 (PR Review) - Postgres migration table locks and concurrent indexing
    {
        "raw_asr": "in slash db slash migration dot py the pull request adds column indexes buy blocking table writes across fifty tables wait execut concurrent migrat buy passing dash dash concurrent flags instead basically post gres acquires exclusive table locks stalling thirty query workers right two migration scripts validating non blocking operat",
        "refined_text": "In /db/migration.py, the pull request adds column indexes by blocking table writes across 50 tables, executing concurrent migration by passing --concurrent flags instead.\n\nBasically Postgres acquires exclusive table locks stalling 30 query workers. Write 2 migration scripts validating non blocking operations."
    },

    # Sample 7: Domain 3 (PR Review) - Cache dictionary data race and lock guard synchronization
    {
        "raw_asr": "in slash pkg slash cache dot go the code mutates shared dictionary structures buy reading keys without mutex locking wait protect map access buy wrapping calls inside lock underscore guard instead um failing at synchronizat triggers race panics across four c p u cores right two concurrent stress tests verifying thread safety",
        "refined_text": "In /pkg/cache.go, the code mutates shared dictionary structures by reading keys without mutex locking, protecting map access by wrapping calls inside lock_guard instead.\n\nFailing at synchronization triggers race panics across 4 CPU cores. Write 2 concurrent stress tests verifying thread safety."
    },

    # Sample 8: Domain 5 (Technical Mentoring) - RPC streaming backpressure and flow control
    {
        "raw_asr": "so basically explain r p c stream backpressure towards the apprentice buy regulating message transmiss inside slash rpc slash stream dot go wait buffer packets buy setting window underscore size towards sixty four chunks instead um omitting flow control exhausts six thousand bytes of memory right two load benchmarks measuring channel stability",
        "refined_text": "So basically explain RPC stream backpressure towards the apprentice by regulating message transmission inside /rpc/stream.go, buffering packets by setting window_size towards 64 chunks instead.\n\nOmitting flow control exhausts 6000 bytes of memory. Write 2 load benchmarks measuring channel stability."
    },

    # Sample 9: Domain 5 (Technical Mentoring) - Postgres connection pool binding and socket exhaustion
    {
        "raw_asr": "uh mentor the junior developer on post gres connection pooling buy binding client handles inside slash db slash pool dot py wait prevent socket exhaustion buy setting max underscore connections towards twenty workers instead basically failing at initializ pools causes query latency across forty routines right three benchmark tests evaluating database throughput",
        "refined_text": "Mentor the junior developer on Postgres connection pooling by binding client handles inside /db/pool.py, preventing socket exhaustion by setting max_connections towards 20 workers instead.\n\nBasically failing at initializing pools causes query latency across 40 routines. Write 3 benchmark tests evaluating database throughput."
    },

    # Sample 10: Domain 5 (Technical Mentoring) - Asyncio event loop non-blocking task offloading
    {
        "raw_asr": "so um instruct the engineer on a sink i o event loop concurrency buy offloading blocking disk operations inside slash app slash file dot py change that schedule background tasks buy configuring thread underscore pool workers instead failing at synchronizat stalls twelve tasks across four c p u cores right two regression tests verifying async responsiveness",
        "refined_text": "So instruct the engineer on asyncio event loop concurrency by offloading blocking disk operations inside /app/file.py, scheduling background tasks by configuring thread_pool workers instead.\n\nFailing at synchronization stalls 12 tasks across 4 CPU cores. Write 2 regression tests verifying async responsiveness."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n. Max \n\n: words // 25.
    # Min 4 noise layers. Natural spoken narration. Zero checklist stereotypes.
    # =========================================================================

    # Sample 11: Domain 3 (PR Review) - Redis distributed lock lease renewal and context cancellation
    {
        "raw_asr": "reviewing the pull request inside slash pkg slash lock underscore manager dot py the author implements distributed lock leasing buy setting redis keys without background heartbeats wait refresh active leases buy spawning background renewal routines inside lease underscore worker dot py instead um failing at synchronizat during network partitions drops lock ownership across twelve knowed instances basically post gres transactions conflict with stale leases when client clocks drift buy fifty milliseconds furthermore the current implementation terminates lock leases prematurely buy acquiring locks without retry timeouts across twenty payment workers wait handle lock acquisition failures buy passing dash dash retry count equal five instead this defect stalls fifty database transactions across four c p u cores developers should right four integration tests validating context cancellation and renewal termination",
        "refined_text": "Reviewing the pull request inside /pkg/lock_manager.py, the author implements distributed lock leasing by setting Redis keys without background heartbeats, refreshing active leases by spawning background renewal routines inside lease_worker.py instead.\n\nFailing at synchronization during network partitions drops lock ownership across 12 node instances. Basically Postgres transactions conflict with stale leases when client clocks drift by 50 milliseconds. Furthermore the current implementation terminates lock leases prematurely by acquiring locks without retry timeouts across 20 payment workers, handling lock acquisition failures by passing --retry-count equal 5 instead.\n\nThis defect stalls 50 database transactions across 4 CPU cores. Developers should write 4 integration tests validating context cancellation and renewal termination."
    },

    # Sample 12: Domain 3 (PR Review) - gRPC interceptor context deadline and connection pool exhaustion
    {
        "raw_asr": "inspecting the code review inside slash api slash grpc underscore interceptor dot go the author creates r p c connection leaks buy omitting context deadline timeouts across client calls wait propagat request deadlines buy setting context with timeout inside client underscore wrapper dot go instead um failing at terminat dead transport channels leaks six hundred socket descriptors across twenty knowed endpoints basically omitting keep alive pings buy disabling client heartbeats causes gateway timeouts across four c p u cores in addition the interceptor drops metadata headers buy parsing incoming contexts without mutex synchronizat wait protect header serialization buy using sync underscore map instead this race condition corrupts thirty session tokens across fifty gateway workers developers must right three load tests validating channel recycling and token integrity under eight thousand concurrent requests",
        "refined_text": "Inspecting the code review inside /api/grpc_interceptor.go, the author creates RPC connection leaks by omitting context deadline timeouts across client calls, propagating request deadlines by setting context with timeout inside client_wrapper.go instead.\n\nFailing at terminating dead transport channels leaks 600 socket descriptors across 20 node endpoints. Basically omitting keep alive pings by disabling client heartbeats causes gateway timeouts across 4 CPU cores. In addition the interceptor drops metadata headers by parsing incoming contexts without mutex synchronization, protecting header serialization by using sync_map instead.\n\nThis race condition corrupts 30 session tokens across 50 gateway workers. Developers must write 3 load tests validating channel recycling and token integrity under 8000 concurrent requests."
    },

    # Sample 13: Domain 3 (PR Review) - Postgres transaction isolation level and deadlocks in batch settlement
    {
        "raw_asr": "reviewing pull request ninety four inside slash db slash settlement underscore worker dot py the author processes financial transfers buy locking ledger rows in arbitrary order wait eliminat deadlock cycles buy sorting account keys prior towards lock acquisition inside ledger underscore model dot py instead um post gres acquires exclusive row locks stalling sixty payment transactions across twenty worker threads furthermore the author executes queries under serializable isolation buy omitting retry loops across failed transactions change that implement exponential backoff buy configuring retry underscore limit towards five attempts instead failing at terminat deadlocked sessions exhausts database connection pools across four c p u cores developers should right four regression tests verifying deadlock free settlements under one thousand concurrent batches",
        "refined_text": "Reviewing pull request 94 inside /db/settlement_worker.py, the author processes financial transfers by locking ledger rows in arbitrary order, eliminating deadlock cycles by sorting account keys prior towards lock acquisition inside ledger_model.py instead.\n\nPostgres acquires exclusive row locks stalling 60 payment transactions across 20 worker threads. Furthermore the author executes queries under serializable isolation by omitting retry loops across failed transactions, implementing exponential backoff by configuring retry_limit towards 5 attempts instead.\n\nFailing at terminating deadlocked sessions exhausts database connection pools across 4 CPU cores. Developers should write 4 regression tests verifying deadlock free settlements under 1000 concurrent batches."
    },

    # Sample 14: Domain 3 (PR Review) - Kafka partitioner key hashing and rebalance storm
    {
        "raw_asr": "inspecting the pull request inside slash pkg slash event underscore publisher dot go the author publishes telemetry events buy omitting partition keys across topic streams wait allocat messages evenly buy hashing tenant identifiers inside partition underscore router dot go instead um null keys route eighty thousand messages towards partition zero creating severe consumer lag across six knowed hosts basically the downstream consumer group triggers rebalance storms buy failing at synchronizat during partition reassignment change that configure cooperative sticky assignment buy passing dash dash assignor flag instead omitting key hashes also prevents message deduplicat across downstream workers stalling four c p u cores developers must right two benchmark tests confirming uniform partition distribution and balanced consumer throughput",
        "refined_text": "Inspecting the pull request inside /pkg/event_publisher.go, the author publishes telemetry events by omitting partition keys across topic streams, allocating messages evenly by hashing tenant identifiers inside partition_router.go instead.\n\nNull keys route 80000 messages towards partition 0 creating severe consumer lag across 6 node hosts. Basically the downstream consumer group triggers rebalance storms by failing at synchronization during partition reassignment, configuring cooperative sticky assignment by passing --assignor flag instead.\n\nOmitting key hashes also prevents message deduplication across downstream workers stalling 4 CPU cores. Developers must write 2 benchmark tests confirming uniform partition distribution and balanced consumer throughput."
    },

    # Sample 15: Domain 3 (PR Review) - Zero-copy packet parser memory allocation and DMA buffer overrun
    {
        "raw_asr": "in slash internal slash packet underscore parser dot c the pull request parses incoming telemetry frames buy executing dynamic buffer allocat inside the receive loop wait eliminate heap fragmentation buy reserving static ring buffers inside buffer underscore pool dot c instead um failing at synchronizat between interrupt routines and user threads corrupts zero x four zero byte headers across eight network interfaces basically reading packets without bounds checks overwrites sixteen memory registers stalling the c p u pipeline furthermore the driver terminates d m a descriptors prematurely buy writing invalid control flags change that enforce descriptor boundaries buy passing dash dash ring size equal one zero two four instead developers must right three unit benchmarks validating zero copy latency across sixty four thousand packets",
        "refined_text": "In /internal/packet_parser.c, the pull request parses incoming telemetry frames by executing dynamic buffer allocation inside the receive loop, eliminating heap fragmentation by reserving static ring buffers inside buffer_pool.c instead.\n\nFailing at synchronization between interrupt routines and user threads corrupts 0x40 byte headers across 8 network interfaces. Basically reading packets without bounds checks overwrites 16 memory registers stalling the CPU pipeline.\n\nFurthermore the driver terminates DMA descriptors prematurely by writing invalid control flags, enforcing descriptor boundaries by passing --ring-size equal 1024 instead. Developers must write 3 unit benchmarks validating zero copy latency across 64000 packets."
    },

    # Sample 16: Domain 5 (Technical Mentoring) - LSM-Tree vs B-Tree storage engines and compaction storms
    {
        "raw_asr": "so basically explain log structured merge tree storage engines towards the mentee buy comparing append only write ahead logs against b tree in place updates inside slash storage slash engine dot go wait explain memtable flushes buy tracing immutable data structures inside sstable underscore writer dot go instead um failing at synchronizat during background compaction triggers write amplification storms buy saturating disk i o across twelve knowed instances post gres uses b trees four relational indexing whereas lsm engines buffer writes into sixty four megabyte blocks change that configure leveled compaction thresholds buy setting max underscore background flushes towards four threads instead this bottleneck stalls eight thousand write queries across four c p u cores developers must right two profiling benchmarks measuring write throughput under heavy ingest",
        "refined_text": "So basically explain log structured merge tree storage engines towards the mentee by comparing append only write ahead logs against B-tree in place updates inside /storage/engine.go, explaining memtable flushes by tracing immutable data structures inside sstable_writer.go instead.\n\nFailing at synchronization during background compaction triggers write amplification storms by saturating disk I/O across 12 node instances. Postgres uses B-trees for relational indexing whereas LSM engines buffer writes into 64 megabyte blocks, configuring leveled compaction thresholds by setting max_background_flushes towards 4 threads instead.\n\nThis bottleneck stalls 8000 write queries across 4 CPU cores. Developers must write 2 profiling benchmarks measuring write throughput under heavy ingest."
    },

    # Sample 17: Domain 5 (Technical Mentoring) - Circuit Breaker state transitions and exponential backoff
    {
        "raw_asr": "in technical mentoring explain circuit breaker state transitions towards the apprentice buy walking through state machines inside slash pkg slash circuit underscore breaker dot py wait demonstrate half open canary probes buy sending five test requests inside probe underscore manager dot py instead um when consecutive r p c failures reach ten consecutive errors the breaker transitions from closed towards open buy rejecting incoming traffic across eight payment gateways basically omitting exponential backoff with randomized jitter triggers thundering herd storms buy flooding upstream services with sixty thousand retries change that configur backoff intervals buy setting max underscore retry window towards thirty seconds instead this defect exhausts thread pools across four c p u cores developers must right three simulated fault tests validating graceful degradation and recovery",
        "refined_text": "In technical mentoring explain circuit breaker state transitions towards the apprentice by walking through state machines inside /pkg/circuit_breaker.py, demonstrating half open canary probes by sending 5 test requests inside probe_manager.py instead.\n\nWhen consecutive RPC failures reach 10 consecutive errors the breaker transitions from closed towards open by rejecting incoming traffic across 8 payment gateways. Basically omitting exponential backoff with randomized jitter triggers thundering herd storms by flooding upstream services with 60000 retries, configuring backoff intervals by setting max_retry_window towards 30 seconds instead.\n\nThis defect exhausts thread pools across 4 CPU cores. Developers must write 3 simulated fault tests validating graceful degradation and recovery."
    },

    # Sample 18: Domain 5 (Technical Mentoring) - Optimistic Concurrency Control OCC vs Pessimistic Locking
    {
        "raw_asr": "so um guid the mentee on optimistic concurrency control buy explaining version column increments inside slash db slash inventory dot py wait contrast with pessimistic locking buy evaluating select four update semantics inside lock underscore helper dot py instead under high contention fifty worker routines collide on identical row versions triggering repeat transaction rollbacks across post gres tables basically failing at synchronizat during write retries wastes c p u cycles buy executing unbounded loops change that configur bounded backoff buy setting max underscore retries towards four attempts instead this strategy maintains throughput across eight knowed instances without table locks developers must right two concurrency benchmarks comparing optimistic commits against pessimistic transactions",
        "refined_text": "So guide the mentee on optimistic concurrency control by explaining version column increments inside /db/inventory.py, contrasting with pessimistic locking by evaluating select for update semantics inside lock_helper.py instead.\n\nUnder high contention 50 worker routines collide on identical row versions triggering repeat transaction rollbacks across Postgres tables. Basically failing at synchronization during write retries wastes CPU cycles by executing unbounded loops, configuring bounded backoff by setting max_retries towards 4 attempts instead.\n\nThis strategy maintains throughput across 8 node instances without table locks. Developers must write 2 concurrency benchmarks comparing optimistic commits against pessimistic transactions."
    },

    # Sample 19: Domain 5 (Technical Mentoring) - Golang pprof heap profiling and goroutine leak detection
    {
        "raw_asr": "in technical mentoring coach the developer on memory leak profiling buy analyzing heap allocations inside slash cmd slash profiler dot go wait inspect goroutine stacks buy capturing profiles via pprof endpoint inside debug underscore handler dot go instead um unclosed channels cause twenty thousand goroutines two remain blocked buy waiting on nil channel sends failing at terminat dormant worker routines pins four hundred megabytes of memory across eight knowed hosts basically the garbage collector consumes c p u cycles buy repeatedly scanning leaked objects change that configur context cancellation buy passing dash dash timeout equal ten seconds instead this defect stalls thirty r p c handlers developers must right two memory leak tests validating zero goroutine growth",
        "refined_text": "In technical mentoring coach the developer on memory leak profiling by analyzing heap allocations inside /cmd/profiler.go, inspecting goroutine stacks by capturing profiles via pprof endpoint inside debug_handler.go instead.\n\nUnclosed channels cause 20000 goroutines to remain blocked by waiting on nil channel sends. Failing at terminating dormant worker routines pins 400 megabytes of memory across 8 node hosts. Basically the garbage collector consumes CPU cycles by repeatedly scanning leaked objects, configuring context cancellation by passing --timeout equal 10 seconds instead.\n\nThis defect stalls 30 RPC handlers. Developers must write 2 memory leak tests validating zero goroutine growth."
    },

    # Sample 20: Domain 5 (Technical Mentoring) - Distributed Tracing context injection and W3C traceparent
    {
        "raw_asr": "basically instruct the apprentice on distributed tracing buy propagating span context inside slash middleware slash trace dot py wait inject traceparent headers buy formatting w three c headers inside context underscore injector dot py instead um when microservices drop trace metadata r p c spans fail at synchronizat across twelve knowed instances this defect fragments thirty thousand distributed requests buy obscuring latency bottlenecks across eight downstream services furthermore high trace sampling saturates c p u utilization buy emitting spans towards the collector without filtering change that configur head based sampling buy setting sample underscore rate towards ten percent instead this defect exhausts four worker threads developers must right two tracing benchmarks validating end to end span continuity across four microservices",
        "refined_text": "Basically instruct the apprentice on distributed tracing by propagating span context inside /middleware/trace.py, injecting traceparent headers by formatting W3C headers inside context_injector.py instead.\n\nWhen microservices drop trace metadata RPC spans fail at synchronization across 12 node instances. This defect fragments 30000 distributed requests by obscuring latency bottlenecks across 8 downstream services. Furthermore high trace sampling saturates CPU utilization by emitting spans towards the collector without filtering, configuring head based sampling by setting sample_rate towards 10 percent instead.\n\nThis defect exhausts 4 worker threads. Developers must write 2 tracing benchmarks validating end to end span continuity across 4 microservices."
    }
]

# Validation
all_passed = True
noise_counts = []
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, s in enumerate(samples, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]

    # Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"Sample {i} FAILED: raw_asr leaked into eval set!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {i} FAILED: refined_text leaked into eval set!")
        all_passed = False

    # Noise layer count
    n_count = get_noise_layer_count(raw)
    noise_counts.append(n_count)

    # Validate pair
    v_ok, v_msg = validate_pair(s, min_noise_layers=4)
    if not v_ok:
        print(f"Sample {i} FAILED validate_pair: {v_msg}")
        all_passed = False

    # Validate cleaner
    c_res, c_msg = clean_sample(raw, ref)
    if not c_res or c_msg != "kept":
        print(f"Sample {i} FAILED clean_sample: {c_msg}")
        all_passed = False

    words = len(ref.split())
    if words < 25:
        tier = "short"
    elif words < 90:
        tier = "medium"
    else:
        tier = "long"
    tier_counts[tier] += 1

    breaks = ref.count("\n\n")
    print(f"Sample {i:02d} [{tier.upper():6s}]: {words:3d} words, {breaks} breaks, {n_count} noise layers | Val: {v_msg} | Clean: {c_msg}")

print("\n--- Summary ---")
print(f"Total: {len(samples)} samples")
print(f"Tier counts: {tier_counts}")
avg_noise = sum(noise_counts) / len(noise_counts)
print(f"Avg noise layers: {avg_noise:.2f}")

b_ok, b_msg, b_stats = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print(f"Batch validation: {b_ok} ({b_msg})")
print(f"Batch stats: {b_stats}")

if not b_ok:
    all_passed = False

if all_passed:
    output_path = Path("scratch/subagent_batch_143.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS! Saved {len(samples)} verified samples to {output_path}")
else:
    print("\nFAILURE! Some checks failed.")
    sys.exit(1)
