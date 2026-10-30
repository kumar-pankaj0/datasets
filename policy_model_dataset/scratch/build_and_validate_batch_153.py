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
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Content words >= 6-8.
    # =========================================================================

    # Sample 1: Domain 3 (PR Review) - Async try-lock inside connection_pool.rs
    {
        "raw_asr": "um please synchronizat lock acquisition buy switching two a sink try lock inside connection underscore pool dot rs",
        "refined_text": "Please synchronize lock acquisition by switching to async try-lock inside connection_pool.rs."
    },

    # Sample 2: Domain 5 (Mentoring) - CPU cache padding inside cache_line.rs
    {
        "raw_asr": "uh initializ c p u cache padding buy eight bytes four each worker slot inside cache underscore line dot rs",
        "refined_text": "Initialize CPU cache padding by 8 bytes for each worker slot inside cache_line.rs."
    },

    # Sample 3: Domain 3 (PR Review) - Postgres connection retry intervals inside database_client.rs
    {
        "raw_asr": "basically configur four connection retry intervals buy updating post gres driver limits inside database underscore client dot rs",
        "refined_text": "Configure 4 connection retry intervals by updating Postgres driver limits inside database_client.rs."
    },

    # Sample 4: Domain 5 (Mentoring) - Asyncio worker threads inside runtime_scheduler.py
    {
        "raw_asr": "um allocat two worker threads four the a sink i o event loop inside runtime underscore scheduler dot py",
        "refined_text": "Allocate 2 worker threads for the asyncio event loop inside runtime_scheduler.py."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Domain 3 (PR Review) - Lock-free queue atomic compare-and-swap
    {
        "raw_asr": "in your pull request review on queue underscore node dot rs the head pointer swap creates a data race across eight c p u threads wait switch to atomic compare and swap instead um please synchronizat memory ordering buy using sequentially consistent operations across four worker channels",
        "refined_text": "In your pull request review on queue_node.rs, the head pointer swap creates a data race across 8 CPU threads, switching to atomic compare-and-swap instead.\n\nPlease synchronize memory ordering by using sequentially consistent operations across 4 worker channels."
    },

    # Sample 6: Domain 5 (Mentoring) - Borrow checker lifetime errors and Arc wrappers
    {
        "raw_asr": "when mentoring our new engineer on borrow checker lifetime errors we identified dangling reference faults across six session structs wait change that to reference counted wrappers instead basically configur twelve shared buffers buy passing an arc clone four each r p c worker thread inside session underscore cache dot rs",
        "refined_text": "When mentoring our new engineer on borrow checker lifetime errors, we identified dangling reference faults across 6 session structs, changing that to reference-counted wrappers instead.\n\nConfigure 12 shared buffers by passing an Arc clone for each RPC worker thread inside session_cache.rs."
    },

    # Sample 7: Domain 3 (PR Review) - Batch upsert deadlocks in Postgres
    {
        "raw_asr": "in this pull request review our batch upsert queries trigger deadlocks across sixteen concurrent transactions buy acquiring row locks in non deterministic order wait sort row keys deterministically instead um please deduplicat thirty two batch payloads four the post gres persistence layer inside inventory underscore repository dot py",
        "refined_text": "In this pull request review, our batch upsert queries trigger deadlocks across 16 concurrent transactions by acquiring row locks in non-deterministic order, sorting row keys deterministically instead.\n\nPlease deduplicate 32 batch payloads for the Postgres persistence layer inside inventory_repository.py."
    },

    # Sample 8: Domain 5 (Mentoring) - Goroutine leaks and asyncio pipeline sync
    {
        "raw_asr": "during pair programming mentoring we resolved goroutine leak crashes across twenty background workers buy attaching context cancellation handlers wait switch to buffered channel selects instead uh please synchronizat eight consumer routines four the a sink i o pipeline inside pipeline underscore worker dot py",
        "refined_text": "During pair programming mentoring, we resolved goroutine leak crashes across 20 background workers by attaching context cancellation handlers, switching to buffered channel selects instead.\n\nPlease synchronize 8 consumer routines for the asyncio pipeline inside pipeline_worker.py."
    },

    # Sample 9: Domain 3 (PR Review) - gRPC RPC streaming flow control
    {
        "raw_asr": "in your code review on stream underscore collector dot py the streaming response handler causes memory bloat across fourteen r p c connections buy buffering frames without backpressure limits wait switch to bounded flow control channels instead basically allocat six chunk buffers four the ingestion stream",
        "refined_text": "In your code review on stream_collector.py, the streaming response handler causes memory bloat across 14 RPC connections by buffering frames without backpressure limits, switching to bounded flow control channels instead.\n\nAllocate 6 chunk buffers for the ingestion stream."
    },

    # Sample 10: Domain 5 (Mentoring) - CPU thread pool bounds and context switching
    {
        "raw_asr": "when coaching our backend engineer on thread pool tuning we noticed high context switching overhead across forty worker threads buy exceeding core capacity wait reduce thread count to eight instead um please recalculat c p u thread pool bounds four the dispatch service inside thread underscore manager dot py",
        "refined_text": "When coaching our backend engineer on thread pool tuning, we noticed high context switching overhead across 40 worker threads by exceeding core capacity, reducing thread count to 8 instead.\n\nPlease recalculate CPU thread pool bounds for the dispatch service inside thread_manager.py."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: Domain 3 (PR Review) - LSM-Tree memtable WAL flush race condition
    {
        "raw_asr": "in this pull request review on storage underscore engine dot rs the memtable rotation logic introduces a critical race condition between active write buffers and disk flush threads buy holding locks during sync operations across sixteen c p u writer tasks wait release the read lock before syncing to disk instead uh the current implementation allows incoming puts to overwrite uncommitted entries when wal truncation triggers during checkpoint intervals so basically synchronizat the snapshot sequence numbers buy pinning active generation counters across thirty two segment blocks wait no wait switch to an atomic fence barrier instead um configur eight dedicated flush workers four the background persistence loop inside wal underscore writer dot rs resolving disk contention across sixty four partitions",
        "refined_text": "In this pull request review on storage_engine.rs, the memtable rotation logic introduces a critical race condition between active write buffers and disk flush threads by holding locks during sync operations across 16 CPU writer tasks, releasing the read lock before syncing to disk instead. The current implementation allows incoming puts to overwrite uncommitted entries when WAL truncation triggers during checkpoint intervals.\n\nSynchronize the snapshot sequence numbers by pinning active generation counters across 32 segment blocks, switching to an atomic fence barrier instead. Configure 8 dedicated flush workers for the background persistence loop inside wal_writer.rs, resolving disk contention across 64 partitions."
    },

    # Sample 12: Domain 5 (Mentoring) - AsyncIO event loop blocking vs thread pool offloading
    {
        "raw_asr": "during our technical mentoring session on asynchronous architecture we examined why heavy cryptographic hashing blocks the single threaded event loop across twenty four worker tasks buy executing synchronous routines directly on the main thread wait offload compute tasks to a worker pool instead uh when blocking calls monopolize the event loop incoming r p c requests experience severe latency spikes exceeding two hundred milliseconds across forty client channels so basically allocat twelve thread pool workers buy wrapping intensive operations with run in executor calls wait switch to process pool executor instead um configur six worker subprocesses four the cryptographic batch pipeline inside crypto underscore worker dot py isolating c p u intensive hashing from network event polling",
        "refined_text": "During our technical mentoring session on asynchronous architecture, we examined why heavy cryptographic hashing blocks the single-threaded event loop across 24 worker tasks by executing synchronous routines directly on the main thread, offloading compute tasks to a worker pool instead. When blocking calls monopolize the event loop, incoming RPC requests experience severe latency spikes exceeding 200 milliseconds across 40 client channels.\n\nAllocate 12 thread pool workers by wrapping intensive operations with run_in_executor calls, switching to ProcessPoolExecutor instead. Configure 6 worker subprocesses for the cryptographic batch pipeline inside crypto_worker.py, isolating CPU intensive hashing from network event polling."
    },

    # Sample 13: Domain 3 (PR Review) - Postgres prepared statement leak and connection pool starvation
    {
        "raw_asr": "in this pull request review on transaction underscore repository dot py the database connection pooling logic leaks prepared statements across forty active client handles buy omitting explicit deallocation before pool return wait deallocate statement handles on close instead um under burst traffic this unmanaged statement accumulation exhausts post gres shared memory across sixteen pool shards causing connection drops across eighty production services so basically configur thirty two maximum pooled connections buy tuning idle timeout thresholds wait adjust pool capacity to twenty instead uh please terminat inactive client sessions buy enforcing strict lifecycle validation four every database checkout inside connection underscore pool dot py isolating tenant workloads across sixty four application hosts",
        "refined_text": "In this pull request review on transaction_repository.py, the database connection pooling logic leaks prepared statements across 40 active client handles by omitting explicit deallocation before pool return, deallocating statement handles on close instead. Under burst traffic, this unmanaged statement accumulation exhausts Postgres shared memory across 16 pool shards, causing connection drops across 80 production services.\n\nConfigure 32 maximum pooled connections by tuning idle timeout thresholds, adjusting pool capacity to 20 instead. Terminate inactive client sessions by enforcing strict lifecycle validation for every database checkout inside connection_pool.py, isolating tenant workloads across 64 application hosts."
    },

    # Sample 14: Domain 5 (Mentoring) - Zero-copy DMA and memory-mapped ring buffers
    {
        "raw_asr": "during our systems mentoring walk through we reviewed kernel packet ingress mechanics and explained why standard read system calls waste memory bandwidth buy copying payload bytes between kernel buffers and user space buffers across twelve stream channels wait map packet rings directly with mmap instead uh zero copy ring buffers eliminate redundant copies buy allowing network adapters two transfer frames directly via d m a into shared user space memory so basically initializ eight receive ring buffers buy configuring ring descriptor pointers wait switch to sixteen descriptors instead um please synchronizat buffer head and tail pointers four packet ingestion workers inside ring underscore driver dot c avoiding c p u cache invalidation across thirty two worker threads",
        "refined_text": "During our systems mentoring walk-through, we reviewed kernel packet ingress mechanics and explained why standard read system calls waste memory bandwidth by copying payload bytes between kernel buffers and user space buffers across 12 stream channels, mapping packet rings directly with mmap instead. Zero-copy ring buffers eliminate redundant copies by allowing network adapters to transfer frames directly via DMA into shared user space memory.\n\nInitialize 8 receive ring buffers by configuring ring descriptor pointers, switching to 16 descriptors instead. Synchronize buffer head and tail pointers for packet ingestion workers inside ring_driver.c, avoiding CPU cache invalidation across 32 worker threads."
    },

    # Sample 15: Domain 3 (PR Review) - Raft consensus log compaction and snapshot chunk RPC streaming
    {
        "raw_asr": "in this pull request review on consensus underscore raft dot rs the snapshot streaming implementation blocks incoming client proposals across twenty knowed replicas buy executing log compaction synchronously on the main state machine loop wait stream snapshot chunks in background tasks instead uh during leader transfers large snapshot transfers monopolize r p c channels causing heartbeat timeouts across four quorum groups and triggering cascading election rounds across sixty cluster instances so basically allocat sixteen streaming chunk buffers buy throttling network throughput wait switch to eight chunk buffers instead um please synchronizat raft term transitions buy persisting vote records four each election epoch inside metadata underscore log dot rs preserving state consistency across eight clusters",
        "refined_text": "In this pull request review on consensus_raft.rs, the snapshot streaming implementation blocks incoming client proposals across 20 node replicas by executing log compaction synchronously on the main state machine loop, streaming snapshot chunks in background tasks instead. During leader transfers, large snapshot transfers monopolize RPC channels, causing heartbeat timeouts across 4 quorum groups and triggering cascading election rounds across 60 cluster instances.\n\nAllocate 16 streaming chunk buffers by throttling network throughput, switching to 8 chunk buffers instead. Synchronize Raft term transitions by persisting vote records for each election epoch inside metadata_log.rs, preserving state consistency across 8 clusters."
    },

    # Sample 16: Domain 5 (Mentoring) - B-Tree latch crabbing and optimistic lock coupling
    {
        "raw_asr": "when mentoring our database contributor on index concurrency control we analyzed why holding an exclusive latch on the index root page causes severe throughput bottlenecks across thirty two worker threads buy serializing all tree descents wait use latch crabbing down through leaf nodes instead uh latch crabbing releases parent page latches as soon as child pages are acquired buy maintaining safe traversal invariant across eight levels so basically initializ optimistic lock coupling buy validating page version counters wait verify generation tags instead um please deduplicat sixteen leaf search iterations four concurrent readers inside btree underscore index dot rs reducing c p u stall cycles across sixty four query workers",
        "refined_text": "When mentoring our database contributor on index concurrency control, we analyzed why holding an exclusive latch on the index root page causes severe throughput bottlenecks across 32 worker threads by serializing all tree descents, using latch crabbing down through leaf nodes instead. Latch crabbing releases parent page latches as soon as child pages are acquired by maintaining safe traversal invariant across 8 levels.\n\nInitialize optimistic lock coupling by validating page version counters, verifying generation tags instead. Deduplicate 16 leaf search iterations for concurrent readers inside btree_index.rs, reducing CPU stall cycles across 64 query workers."
    },

    # Sample 17: Domain 3 (PR Review) - Distributed saga compensations and idempotency keys
    {
        "raw_asr": "in this pull request review on payment underscore saga dot py the compensation handler lacks idempotency verification across twenty payment gateway workflows buy processing refund messages without checking previous state flags wait verify authorization state before triggering compensation instead uh out of order delivery causes duplicate refund dispatches across eight r p c merchant channels and creates balance discrepancies across forty accounts so basically configur twelve event deduplication windows buy caching idempotency tokens in post gres wait set retention to twenty four hours instead um please terminat stale compensation workflows buy invalidating expired saga contexts four all pending orders inside saga underscore coordinator dot py protecting ledger integrity across sixteen billing regions",
        "refined_text": "In this pull request review on payment_saga.py, the compensation handler lacks idempotency verification across 20 payment gateway workflows by processing refund messages without checking previous state flags, verifying authorization state before triggering compensation instead. Out-of-order delivery causes duplicate refund dispatches across 8 RPC merchant channels and creates balance discrepancies across 40 accounts.\n\nConfigure 12 event deduplication windows by caching idempotency tokens in Postgres, setting retention to 24 hours instead. Terminate stale compensation workflows by invalidating expired saga contexts for all pending orders inside saga_coordinator.py, protecting ledger integrity across 16 billing regions."
    },

    # Sample 18: Domain 5 (Mentoring) - C++ memory model, acquire-release barriers, and store buffers
    {
        "raw_asr": "during our technical mentoring session on the c plus plus memory model we investigated why relaxed atomic load operations cause data corruption across sixteen worker cores buy allowing out of order instruction reordering in hardware store buffers wait insert acquire release memory barriers instead uh relaxed memory ordering guarantees atomicity buy failing two guarantee synchronized visibility four dependent data structures across twenty memory banks so basically synchronizat consumer pointer reads buy applying memory order acquire semantics wait switch to sequential consistency instead um please allocat eight cache line padded slots four the lock free ring buffer inside atomic underscore queue dot rs shielding c p u cores from store buffer stalls across sixty four concurrent producers",
        "refined_text": "During our technical mentoring session on the C++ memory model, we investigated why relaxed atomic load operations cause data corruption across 16 worker cores by allowing out-of-order instruction reordering in hardware store buffers, inserting acquire-release memory barriers instead. Relaxed memory ordering guarantees atomicity by failing to guarantee synchronized visibility for dependent data structures across 20 memory banks.\n\nSynchronize consumer pointer reads by applying memory order acquire semantics, switching to sequential consistency instead. Allocate 8 cache-line padded slots for the lock-free ring buffer inside atomic_queue.rs, shielding CPU cores from store buffer stalls across 64 concurrent producers."
    },

    # Sample 19: Domain 3 (PR Review) - Kafka consumer group rebalance storms and commit offset throttling
    {
        "raw_asr": "in this pull request review on consumer underscore group dot py the message processing loop triggers consumer group rebalance storms across twelve subscriber partitions buy executing long database queries inside synchronous commit handlers wait commit consumer offsets asynchronously in batches instead uh when partition processing exceeds max poll interval limits coordinator brokers trigger partition reassignments across four knowed instances disrupting message ingestion across sixty pipeline clients so basically configur eight background worker routines buy separating fetch loops from execution pools wait assign sixteen workers instead um please recalculat partition batch fetch sizes four the a sink consumer inside kafka underscore dispatcher dot py stabilizing message delivery across twenty four brokers",
        "refined_text": "In this pull request review on consumer_group.py, the message processing loop triggers consumer group rebalance storms across 12 subscriber partitions by executing long database queries inside synchronous commit handlers, committing consumer offsets asynchronously in batches instead. When partition processing exceeds max poll interval limits, coordinator brokers trigger partition reassignments across 4 node instances, disrupting message ingestion across 60 pipeline clients.\n\nConfigure 8 background worker routines by separating fetch loops from execution pools, assigning 16 workers instead. Recalculate partition batch fetch sizes for the async consumer inside kafka_dispatcher.py, stabilizing message delivery across 24 brokers."
    },

    # Sample 20: Domain 5 (Mentoring) - Go GC pause reduction and memory allocation profiling
    {
        "raw_asr": "when mentoring our software engineer on runtime memory profiling we analyzed why excessive heap allocations cause garbage collection latency spikes across twenty four microservices buy forcing frequent mark and sweep scan cycles wait replace heap pointers with stack allocated values instead uh allocating structs containing pointers escapes two the heap buy increasing garbage collector c p u utilization by thirty percent across forty host servers so basically initializ object pooling buy recycling request context buffers wait switch to sync pool instead um please deduplicat twelve serialization buffers four the r p c payload pipeline inside buffer underscore pool dot rs slashing memory allocation rates and eliminating garbage collector pauses across sixty four worker routines",
        "refined_text": "When mentoring our software engineer on runtime memory profiling, we analyzed why excessive heap allocations cause garbage collection latency spikes across 24 microservices by forcing frequent mark-and-sweep scan cycles, replacing heap pointers with stack-allocated values instead. Allocating structs containing pointers escapes to the heap by increasing garbage collector CPU utilization by 30% across 40 host servers.\n\nInitialize object pooling by recycling request context buffers, switching to sync pool instead. Deduplicate 12 serialization buffers for the RPC payload pipeline inside buffer_pool.rs, slashing memory allocation rates and eliminating garbage collector pauses across 64 worker routines."
    }
]

print(f"Total candidate samples: {len(samples)}")

# Verify each sample
passed_validator = 0
passed_cleaner = 0
noise_counts = []

for idx, s in enumerate(samples, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    tier = "short" if words < 25 else ("medium" if words < 90 else "long")
    layers = count_active_noise_layers(raw)
    n_layers = sum(layers.values())
    noise_counts.append(n_layers)

    # Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"SAMPLE {idx} FAILED: Raw ASR exact match in eval set!")
        sys.exit(1)
    if ref.strip() in eval_refs:
        print(f"SAMPLE {idx} FAILED: Refined text exact match in eval set!")
        sys.exit(1)

    # Validate pair
    # For short utterances target_min is 3, for medium/long target_min is 4
    min_layers = 3 if words < 25 else 4
    is_valid, reason = validate_pair(s, min_noise_layers=4)
    if not is_valid:
        print(f"SAMPLE {idx} ({tier}, {words} words, {n_layers} layers) VALIDATOR FAIL: {reason}")
    else:
        passed_validator += 1

    # Clean sample
    res, status = clean_sample(raw, ref)
    if status != "kept":
        print(f"SAMPLE {idx} ({tier}, {words} words, {n_layers} layers) CLEANER FAIL: {status}")
    else:
        passed_cleaner += 1

    print(f"Sample {idx:02d} [{tier.upper():6s}]: {words:3d} words, {n_layers} noise layers -> Validator: {'PASS' if is_valid else 'FAIL'}, Cleaner: {status}")

print("\n--- Batch Validation Summary ---")
batch_valid, batch_msg, batch_stats = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print(f"validate_batch: {batch_valid} ({batch_msg})")
print(f"batch_stats: {batch_stats}")
print(f"Average noise layers: {sum(noise_counts)/len(noise_counts):.2f}")
print(f"Validator pass: {passed_validator}/20, Cleaner pass: {passed_cleaner}/20")

if batch_valid and passed_validator == 20 and passed_cleaner == 20:
    out_path = Path("scratch/subagent_batch_153.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"\nSUCCESS! Written verified batch to {out_path}")
else:
    print("\nFAILURES detected. Please fix issues before saving.")
    sys.exit(1)
