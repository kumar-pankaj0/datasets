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

# Domain 3 & 5: Pull Request Code Reviews & Technical Mentoring
# Batch 163 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3 (target 5-6).
    # =========================================================================

    # Sample 1: Domain 3 (PR Review) - Async semaphore lock acquisition in pool_manager.rs
    {
        "raw_asr": "um please synchronizat lock acquisition buy switching two an a sink semaphore inside pool underscore manager dot rs instead",
        "refined_text": "Please synchronize lock acquisition by switching to an async semaphore inside pool_manager.rs instead."
    },

    # Sample 2: Domain 5 (Mentoring) - CPU branch prediction cost in bit_ops.rs
    {
        "raw_asr": "basically recalculat c p u branch cost buy replacing conditional branches with bitwise masks inside bit underscore ops dot rs instead",
        "refined_text": "Recalculate CPU branch cost by replacing conditional branches with bitwise masks inside bit_ops.rs instead."
    },

    # Sample 3: Domain 3 (PR Review) - RPC query depth limit recursion in query_validator.py
    {
        "raw_asr": "uh configur r p c query depth limits buy restricting four circular fragment recursions inside query underscore validator dot py instead",
        "refined_text": "Configure RPC query depth limits by restricting 4 circular fragment recursions inside query_validator.py instead."
    },

    # Sample 4: Domain 5 (Mentoring) - Async channel backpressure buffering in queue_channel.py
    {
        "raw_asr": "um initializ a sink channel backpressure buy buffering sixteen message slots inside queue underscore channel dot py instead",
        "refined_text": "Initialize async channel backpressure by buffering 16 message slots inside queue_channel.py instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4 (target 5-6).
    # =========================================================================

    # Sample 5: Domain 3 (PR Review) - Tiered cache eviction mutex contention in cache_tiered.rs
    {
        "raw_asr": "in your pull request review on cache underscore tiered dot rs the eviction lock causes thread contention across sixteen c p u cores buy synchronizing metadata updates synchronously wait switch to lock striped segment tables instead um please synchronizat cache eviction queues buy assigning four partition buckets inside eviction underscore table dot rs",
        "refined_text": "In your pull request review on cache_tiered.rs, the eviction lock causes thread contention across 16 CPU cores, switching to lock-striped segment tables instead.\n\nPlease synchronize cache eviction queues by assigning 4 partition buckets inside eviction_table.rs."
    },

    # Sample 6: Domain 5 (Mentoring) - Rust borrow checker mutable aliasing in linked_deque.rs
    {
        "raw_asr": "during mentoring on rust memory safety we reviewed why raw pointer dereferences in doubly linked nodes create aliasing bugs across eight worker threads wait change that to slot indices instead basically allocat sixty four deque nodes buy indexing into preallocated vectors inside linked underscore deque dot rs resolving lifetime errors four r p c queue consumers",
        "refined_text": "During mentoring on Rust memory safety, we reviewed why raw pointer dereferences in doubly linked nodes create aliasing bugs across 8 worker threads, changing that to slot indices instead.\n\nAllocate 64 deque nodes by indexing into preallocated vectors inside linked_deque.rs, resolving lifetime errors for RPC queue consumers."
    },

    # Sample 7: Domain 3 (PR Review) - N+1 query problem with eager batch loading in order_repository.py
    {
        "raw_asr": "in this pull request review our order retrieval handler triggers n plus one query storms across thirty two customer records buy executing separate selects inside loops wait replace individual lookups with joined batch queries instead uh please deduplicat sixteen eager loading lookups four the post gres database driver inside order underscore repository dot py",
        "refined_text": "In this pull request review, our order retrieval handler triggers N+1 query storms across 32 customer records by executing separate selects inside loops, replacing individual lookups with joined batch queries instead.\n\nPlease deduplicate 16 eager loading lookups for the Postgres database driver inside order_repository.py."
    },

    # Sample 8: Domain 5 (Mentoring) - Goroutine context propagation and timeout deadlines in context_helper.go
    {
        "raw_asr": "when mentoring our junior backend developer on context propagation we diagnosed orphaned goroutines hanging across twenty worker routines buy ignoring cancellation signals on parent contexts wait propagate context deadlines explicitly instead um please configur twelve timeout handlers four a sink worker channels inside context underscore helper dot go",
        "refined_text": "When mentoring our junior backend developer on context propagation, we diagnosed orphaned goroutines hanging across 20 worker routines by ignoring cancellation signals on parent contexts, propagating context deadlines explicitly instead.\n\nPlease configure 12 timeout handlers for async worker channels inside context_helper.go."
    },

    # Sample 9: Domain 3 (PR Review) - Unclosed gRPC stream channels in stream_client.py
    {
        "raw_asr": "in your code review on stream underscore client dot py the response reader leaks streaming socket channels across twenty four active sessions buy failing two close connection streams on cancellation wait invoke channel close on abort instead basically terminat eight unclosed r p c stream handles four the telemetry transport service",
        "refined_text": "In your code review on stream_client.py, the response reader leaks streaming socket channels across 24 active sessions by failing to close connection streams on cancellation, invoking channel close on abort instead.\n\nTerminate 8 unclosed RPC stream handles for the telemetry transport service."
    },

    # Sample 10: Domain 5 (Mentoring) - Structure padding and CPU cache alignment in memory_layout.c
    {
        "raw_asr": "during systems mentoring on structure padding we showed how placing unaligned fields wastes sixteen bytes buy inserting internal padding bytes across sixty four struct instances wait sort struct fields by descending size instead uh please initializ eight byte field alignments four c p u cache efficiency inside memory underscore layout dot c",
        "refined_text": "During systems mentoring on structure padding, we showed how placing unaligned fields wastes 16 bytes by inserting internal padding bytes across 64 struct instances, sorting struct fields by descending size instead.\n\nPlease initialize 8 byte field alignments for CPU cache efficiency inside memory_layout.c."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Noise layers >= 4 (target 5-6).
    # =========================================================================

    # Sample 11: Domain 3 (PR Review) - Atomic spinlock contention in mpsc_buffer.rs
    {
        "raw_asr": "in this pull request review on mpsc underscore buffer dot rs the atomic spinlock implementation creates extreme thread contention across thirty two writer tasks buy executing busy wait loops during buffer full states wait replace spinlocks with futex wait queues instead uh under peak ingestion workloads multiple producer threads burn excessive c p u cycles buy repeatedly reading head pointers across sixteen ring slots causing severe tail latency spikes across eight streaming pipelines so basically synchronizat producer queue transitions buy using atomic compare and exchange loops wait switch to fetch add sequence numbers instead um configur twelve bounded ring partitions four high throughput message passing inside producer underscore queue dot rs isolating contention across sixty four producer threads",
        "refined_text": "In this pull request review on mpsc_buffer.rs, the atomic spinlock implementation creates extreme thread contention across 32 writer tasks by executing busy-wait loops during buffer full states, replacing spinlocks with futex wait queues instead. Under peak ingestion workloads, multiple producer threads burn excessive CPU cycles by repeatedly reading head pointers across 16 ring slots, causing severe tail latency spikes across 8 streaming pipelines.\n\nSynchronize producer queue transitions by using atomic compare-and-exchange loops, switching to fetch-add sequence numbers instead. Configure 12 bounded ring partitions for high-throughput message passing inside producer_queue.rs, isolating contention across 64 producer threads."
    },

    # Sample 12: Domain 5 (Mentoring) - Raft consensus leader election and monotonic heartbeats in raft_consensus.rs
    {
        "raw_asr": "during our technical mentoring session on distributed consensus we analyzed why leader lease expiration triggers false election alarms across five knowed instances buy relying on local system clock skew wait use monotonic tick intervals instead uh when network jitter delays election heartbeats follower replicas trigger unnecessary election rounds across three quorum groups buy flooding r p c channels with duplicate vote requests across sixteen candidate terms so basically initializ twelve monotonic timer checks buy decoupling lease verification from wall clock timers wait switch to monotonic instant tracking instead um please deduplicat eight election timeout checks four quorum consistency inside raft underscore consensus dot rs preserving state machine stability across thirty two cluster knowed replicas",
        "refined_text": "During our technical mentoring session on distributed consensus, we analyzed why leader lease expiration triggers false election alarms across 5 node instances by relying on local system clock skew, using monotonic tick intervals instead. When network jitter delays election heartbeats, follower replicas trigger unnecessary election rounds across 3 quorum groups by flooding RPC channels with duplicate vote requests across 16 candidate terms.\n\nInitialize 12 monotonic timer checks by decoupling lease verification from wall-clock timers, switching to monotonic instant tracking instead. Deduplicate 8 election timeout checks for quorum consistency inside raft_consensus.rs, preserving state machine stability across 32 cluster node replicas."
    },

    # Sample 13: Domain 3 (PR Review) - Event loop starvation from synchronous JSON parsing in worker_dispatcher.py
    {
        "raw_asr": "in this pull request review on worker underscore dispatcher dot py the message handler blocks the a sink i o event loop across twenty four worker tasks buy executing heavy json deserialization directly on the main event thread wait offload parsing routines to background worker pools instead um under high ingress traffic synchronous payload parsing starves network socket polling buy stalling heartbeat probes across forty client connections and triggering connection timeout drops across twelve services so basically allocat sixteen thread pool workers buy wrapping payload parsing in run in executor calls wait switch to process pools instead uh please recalculat task queue buffer sizes four ingestion channels inside message underscore parser dot py eliminating c p u stalls across thirty two dispatch pipelines",
        "refined_text": "In this pull request review on worker_dispatcher.py, the message handler blocks the asyncio event loop across 24 worker tasks by executing heavy JSON deserialization directly on the main event thread, offloading parsing routines to background worker pools instead. Under high ingress traffic, synchronous payload parsing starves network socket polling by stalling heartbeat probes across 40 client connections and triggering connection timeout drops across 12 services.\n\nAllocate 16 thread pool workers by wrapping payload parsing in run_in_executor calls, switching to process pools instead. Recalculate task queue buffer sizes for ingestion channels inside message_parser.py, eliminating CPU stalls across 32 dispatch pipelines."
    },

    # Sample 14: Domain 5 (Mentoring) - Linux epoll edge-triggered vs level-triggered socket polling in poll_loop.py
    {
        "raw_asr": "during mentoring on network systems programming we investigated why edge triggered epoll loops encounter socket starvation across sixteen worker connections buy failing two drain receive buffers completely on readiness events wait loop non blocking reads until eagain is returned instead uh level triggered polling wakes up the event loop continuously buy consuming excess c p u cycles when buffers remain non empty across eight socket streams so basically synchronizat event loop wakeups buy consuming all pending socket bytes in a tight read loop wait switch to batch reads instead um configur thirty two socket descriptors four the event dispatcher inside poll underscore loop dot py eliminating thread contention across twenty four worker streams",
        "refined_text": "During mentoring on network systems programming, we investigated why edge-triggered epoll loops encounter socket starvation across 16 worker connections by failing to drain receive buffers completely on readiness events, looping non-blocking reads until EAGAIN is returned instead. Level-triggered polling wakes up the event loop continuously by consuming excess CPU cycles when buffers remain non-empty across 8 socket streams.\n\nSynchronize event loop wakeups by consuming all pending socket bytes in a tight read loop, switching to batch reads instead. Configure 32 socket descriptors for the event dispatcher inside poll_loop.py, eliminating thread contention across 24 worker streams."
    },

    # Sample 15: Domain 3 (PR Review) - Postgres advisory lock transaction scope leaks in distributed_lock.py
    {
        "raw_asr": "in this pull request review on distributed underscore lock dot py the synchronization module uses session level advisory locks across twenty worker instances buy calling pg advisory lock without explicit unlock statements on error wait use transaction scoped advisory xact lock instead um when unhandled exceptions terminate client connections session locks persist across sixteen post gres worker pools buy blocking concurrent job executors across forty database tables and triggering transaction deadlocks across eight coordinator knowed instances so basically terminat orphan session locks buy enforcing automatic transaction scope release wait set session timeouts to thirty seconds instead uh configur eight lock acquisition retries four scheduled task runners inside lock underscore manager dot py isolating tenant workloads across sixty four application hosts",
        "refined_text": "In this pull request review on distributed_lock.py, the synchronization module uses session-level advisory locks across 20 worker instances by calling pg_advisory_lock without explicit unlock statements on error, using transaction-scoped advisory_xact_lock instead. When unhandled exceptions terminate client connections, session locks persist across 16 Postgres worker pools by blocking concurrent job executors across 40 database tables and triggering transaction deadlocks across 8 coordinator node instances.\n\nTerminate orphan session locks by enforcing automatic transaction scope release, setting session timeouts to 30 seconds instead. Configure 8 lock acquisition retries for scheduled task runners inside lock_manager.py, isolating tenant workloads across 64 application hosts."
    },

    # Sample 16: Domain 5 (Mentoring) - Postgres partial index selectivity in index_optimizer.py
    {
        "raw_asr": "when mentoring our database engineer on query plan optimization we discovered why full table scans occur across twelve million ledger rows buy querying active status flags without index selectivity wait build a partial index on status active instead uh the post gres query planner ignores wide composite indexes buy choosing sequential scans when column correlations exceed ninety percent across forty table partitions and triggering disk io spikes across eight cluster knowed hosts so basically initializ eight partial indexes buy indexing filter predicates directly wait filter by tenant id instead um please recalculat table statistics four the query planner inside index underscore optimizer dot py cutting disk io latency across thirty two query worker threads",
        "refined_text": "When mentoring our database engineer on query plan optimization, we discovered why full table scans occur across 12000000 ledger rows by querying active status flags without index selectivity, building a partial index on status active instead. The Postgres query planner ignores wide composite indexes by choosing sequential scans when column correlations exceed 90% across 40 table partitions and triggering disk IO spikes across 8 cluster node hosts.\n\nInitialize 8 partial indexes by indexing filter predicates directly, filtering by tenant ID instead. Recalculate table statistics for the query planner inside index_optimizer.py, cutting disk IO latency across 32 query worker threads."
    },

    # Sample 17: Domain 3 (PR Review) - Zero-copy Protobuf arena lifetimes in proto_decoder.rs
    {
        "raw_asr": "in this pull request review on proto underscore decoder dot rs the protobuf decoding pipeline introduces memory safety violations across sixteen worker routines buy borrowing byte slices past arena allocator lifespans wait pin arena memory chunks during decode passes instead um when transient message buffers get recycled by underlying r p c transports referencing borrowed fields triggers use after free faults across forty client sessions and corrupts deserialization buffers across eight stream pipelines so basically allocat twenty four dedicated arena pools buy reserving contiguous memory regions wait switch to bump allocation instead uh please synchronizat arena reset phases four high throughput streaming inside message underscore arena dot rs preventing c p u faults across thirty two reader tasks",
        "refined_text": "In this pull request review on proto_decoder.rs, the Protobuf decoding pipeline introduces memory safety violations across 16 worker routines by borrowing byte slices past arena allocator lifespans, pinning arena memory chunks during decode passes instead. When transient message buffers get recycled by underlying RPC transports, referencing borrowed fields triggers use-after-free faults across 40 client sessions and corrupts deserialization buffers across 8 stream pipelines.\n\nAllocate 24 dedicated arena pools by reserving contiguous memory regions, switching to bump allocation instead. Synchronize arena reset phases for high-throughput streaming inside message_arena.rs, preventing CPU faults across 32 reader tasks."
    },

    # Sample 18: Domain 5 (Mentoring) - CPU false sharing on 64-byte cache lines in thread_metrics.rs
    {
        "raw_asr": "during technical mentoring on multicore performance profiling we demonstrated how adjacent thread counter updates degrade throughput across thirty two worker cores buy sharing the same sixty four byte cache line wait align counter structs to cache line boundaries instead uh when multiple c p u cores write two adjacent memory addresses hardware cache coherency protocols invalidate l one cache lines across twenty host sockets buy forcing expensive bus arbitration cycles so basically initializ sixty four byte padding offsets buy applying sixty four byte alignment directives wait use crossbeam cache padded wrappers instead um please deduplicat twelve metric aggregation loops four telemetry monitoring inside thread underscore metrics dot rs cutting memory bus stalls across forty threads",
        "refined_text": "During technical mentoring on multicore performance profiling, we demonstrated how adjacent thread counter updates degrade throughput across 32 worker cores by sharing the same 64 byte cache line, aligning counter structs to cache-line boundaries instead. When multiple CPU cores write to adjacent memory addresses, hardware cache coherency protocols invalidate L1 cache lines across 20 host sockets by forcing expensive bus arbitration cycles.\n\nInitialize 64 byte padding offsets by applying 64 byte alignment directives, using crossbeam cache padded wrappers instead. Deduplicate 12 metric aggregation loops for telemetry monitoring inside thread_metrics.rs, cutting memory bus stalls across 40 threads."
    },

    # Sample 19: Domain 3 (PR Review) - TCP FIN_WAIT_2 socket accumulation in socket_transport.py
    {
        "raw_asr": "in this pull request review on socket underscore transport dot py the connection pooling manager leaves half closed sockets lingering across forty proxy gateways buy omitting explicit tcp keepalive timeouts wait configure socket tcp keepalive options on connection initialization instead um unmanaged socket accumulation exhausts file descriptors across sixteen knowed servers buy keeping thousands of connections in fin wait two state across thirty minutes and exhausting network socket handles across eight cluster regions so basically configur eight keepalive probe intervals buy passing socket option flags wait set probe intervals to five seconds instead uh please terminat abandoned socket connections four the a sink gateway inside gateway underscore session dot py freeing socket resources across twenty four client routes",
        "refined_text": "In this pull request review on socket_transport.py, the connection pooling manager leaves half-closed sockets lingering across 40 proxy gateways by omitting explicit TCP keepalive timeouts, configuring socket TCP keepalive options on connection initialization instead. Unmanaged socket accumulation exhausts file descriptors across 16 node servers by keeping thousands of connections in FIN_WAIT_2 state across 30 minutes and exhausting network socket handles across 8 cluster regions.\n\nConfigure 8 keepalive probe intervals by passing socket option flags, setting probe intervals to 5 seconds instead. Terminate abandoned socket connections for the async gateway inside gateway_session.py, freeing socket resources across 24 client routes."
    },

    # Sample 20: Domain 5 (Mentoring) - WAL group commit batching and fsync latency in wal_manager.rs
    {
        "raw_asr": "when coaching our storage contributor on database durability trade offs we analyzed why calling fsync after every single transaction throttles throughput across twenty worker threads buy serializing disk write heads on storage volumes wait batch concurrent writes using group commit loops instead uh individual disk sync calls amplify flash storage write wear buy incurring two millisecond disk latencies four every write across forty r p c requests so basically synchronizat transaction commit buffers buy grouping pending log records across sixteen batch slots wait switch to twenty four slots instead um please configur eight group commit flush workers four the storage engine inside wal underscore manager dot rs scaling transaction throughput across sixty four concurrent clients",
        "refined_text": "When coaching our storage contributor on database durability trade-offs, we analyzed why calling fsync after every single transaction throttles throughput across 20 worker threads by serializing disk write heads on storage volumes, batching concurrent writes using group commit loops instead. Individual disk sync calls amplify flash storage write wear by incurring 2 millisecond disk latencies for every write across 40 RPC requests.\n\nSynchronize transaction commit buffers by grouping pending log records across 16 batch slots, switching to 24 slots instead. Configure 8 group commit flush workers for the storage engine inside wal_manager.rs, scaling transaction throughput across 64 concurrent clients."
    }
]

print("Validating individual pairs...")
all_passed = True
for idx, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    target_min_layers = 3 if words < 25 else 4
    
    # 1. validate_pair
    ok, msg = validate_pair(s, min_noise_layers=target_min_layers)
    if not ok:
        print(f"Sample {idx+1} failed validate_pair: {msg}")
        all_passed = False
    
    # 2. clean_sample
    c_res, c_msg = clean_sample(raw, ref)
    if not c_res:
        print(f"Sample {idx+1} failed clean_sample: {c_msg}")
        all_passed = False
        
    # 3. Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"Sample {idx+1} exact match in eval raws!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {idx+1} exact match in eval refs!")
        all_passed = False

    active_layers = count_active_noise_layers(raw)
    layer_count = get_noise_layer_count(raw)
    tier = "Short" if words < 25 else ("Medium" if words < 90 else "Long")
    print(f"Sample {idx+1:02d} [{tier}, {words:3d} words, {layer_count} layers]: {layer_count} active layers -> OK={ok and (c_res is not None)}")

# Validate batch
b_ok, b_msg, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print("\nBatch Validation Result:")
print("Status:", b_ok, b_msg)
print("Tier stats:", b_tiers)

if all_passed and b_ok:
    out_path = Path("scratch/subagent_batch_163.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote {len(samples)} verified pairs to {out_path}")
else:
    print("\nValidation failed! Please review errors above.")
    sys.exit(1)
