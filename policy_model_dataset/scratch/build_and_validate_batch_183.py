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
# Batch 183 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3 (target 5-6).
    # =========================================================================

    # Sample 1: Domain 3 (PR Review) - Atomic reference counter decrement in sync_counter
    {
        "raw_asr": "um please synchronizat atomic decrement passes buy updating c p u memory barriers inside sync underscore counter instead",
        "refined_text": "Please synchronize atomic decrement passes by updating CPU memory barriers inside sync_counter instead."
    },

    # Sample 2: Domain 5 (Mentoring) - Async channel buffer sizing in channel_buffer
    {
        "raw_asr": "basically configur sixteen slot allocations four a sink queue handlers inside channel underscore buffer instead",
        "refined_text": "Configure 16 slot allocations for async queue handlers inside channel_buffer instead."
    },

    # Sample 3: Domain 3 (PR Review) - RPC payload validation in rpc_dispatcher
    {
        "raw_asr": "uh please recalculat maximum message payload limits buy inspecting r p c header metadata inside rpc underscore dispatcher instead",
        "refined_text": "Please recalculate maximum message payload limits by inspecting RPC header metadata inside rpc_dispatcher instead."
    },

    # Sample 4: Domain 5 (Mentoring) - Thread pool initialization with CLI flag --worker-threads
    {
        "raw_asr": "um initializ eight worker routines buy binding two c p u cores with dash dash worker threads instead",
        "refined_text": "Initialize 8 worker routines by binding to CPU cores with `--worker-threads` instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4 (target 5-6).
    # =========================================================================

    # Sample 5: Domain 3 (PR Review) - Database connection pooling and socket leak in connection_pool.py
    {
        "raw_asr": "in this pull request review on connection underscore pool dot py leaking database socket handles across twenty four worker tasks occurs buy omitting rollback calls on transaction failures wait switch to transactional context managers instead um please synchronizat sixteen client connection slots four the post gres driver resolving socket starvation you know",
        "refined_text": "In this pull request review on connection_pool.py, leaking database socket handles across 24 worker tasks occurs by omitting rollback calls on transaction failures, switching to transactional context managers instead.\n\nPlease synchronize 16 client connection slots for the Postgres driver, resolving socket starvation."
    },

    # Sample 6: Domain 5 (Mentoring) - Rust async executor task starvation in runtime_scheduler.rs
    {
        "raw_asr": "during our technical mentoring discussion on runtime scheduling we analyzed why synchronous file operations block executor threads across eight worker routines buy executing read calls inside a sink tasks wait switch to background thread offloading instead uh please configur thirty two asynchronous task queues four r p c message dispatching inside runtime underscore scheduler dot rs eliminating c p u thread starvation basically",
        "refined_text": "During our technical mentoring discussion on runtime scheduling, we analyzed why synchronous file operations block executor threads across 8 worker routines by executing read calls inside async tasks, switching to background thread offloading instead.\n\nPlease configure 32 asynchronous task queues for RPC message dispatching inside runtime_scheduler.rs, eliminating CPU thread starvation."
    },

    # Sample 7: Domain 3 (PR Review) - Cache invalidation stampede in cache_layer.py
    {
        "raw_asr": "in your pull request review on cache underscore layer dot py concurrent read misses trigger thundering herds across sixteen worker tasks buy fetching expired keys simultaneously wait change that to probabilistic early expiration instead um please deduplicat eight cache retrieval passes four the post gres query pipeline resolving backend latency spikes you know",
        "refined_text": "In your pull request review on cache_layer.py, concurrent read misses trigger thundering herds across 16 worker tasks by fetching expired keys simultaneously, changing that to probabilistic early expiration instead.\n\nPlease deduplicate 8 cache retrieval passes for the Postgres query pipeline, resolving backend latency spikes."
    },

    # Sample 8: Domain 5 (Mentoring) - Zero-copy ring buffer parsing in packet_decoder.c
    {
        "raw_asr": "when coaching our junior systems programmer on network socket performance we observed how copying network payloads degrades throughput across twelve worker processes buy allocating duplicate memory buffers wait switch to zero copy ring buffers instead uh please initializ sixty four packet ring descriptors four d m a receive queues inside packet underscore decoder dot c cutting c p u memory bandwidth overhead basically",
        "refined_text": "When coaching our junior systems programmer on network socket performance, we observed how copying network payloads degrades throughput across 12 worker processes by allocating duplicate memory buffers, switching to zero-copy ring buffers instead.\n\nPlease initialize 64 packet ring descriptors for DMA receive queues inside packet_decoder.c, cutting CPU memory bandwidth overhead."
    },

    # Sample 9: Domain 3 (PR Review) - gRPC deadline propagation in grpc_interceptor.py
    {
        "raw_asr": "in this pull request review on grpc underscore interceptor dot py downstream service invocations hang across twenty client handlers buy dropping deadline timestamps from context headers wait switch to explicit deadline propagation instead um please terminat twelve orphaned r p c transport streams four the telemetry collector restoring socket health you know",
        "refined_text": "In this pull request review on grpc_interceptor.py, downstream service invocations hang across 20 client handlers by dropping deadline timestamps from context headers, switching to explicit deadline propagation instead.\n\nPlease terminate 12 orphaned RPC transport streams for the telemetry collector, restoring socket health."
    },

    # Sample 10: Domain 5 (Mentoring) - Rust atomic ordering in metric_counter.rs
    {
        "raw_asr": "during our concurrency mentoring session we demonstrated why sequential consistency ordering creates memory bus stalls across sixteen c p u cores buy forcing full fence synchronization wait change that to acquire release ordering instead uh please allocat eight atomic metric counters four a sink event pipelines inside metric underscore counter dot rs reducing memory synchronization latency so basically",
        "refined_text": "During our concurrency mentoring session, we demonstrated why sequential consistency ordering creates memory bus stalls across 16 CPU cores by forcing full fence synchronization, changing that to acquire-release ordering instead.\n\nPlease allocate 8 atomic metric counters for async event pipelines inside metric_counter.rs, reducing memory synchronization latency."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Noise layers >= 4 (target 5-6).
    # =========================================================================

    # Sample 11: Domain 3 (PR Review) - Redis/Postgres Distributed Lock Lease Management in distributed_lock.py
    {
        "raw_asr": "in this pull request review on distributed underscore lock dot py the synchronization module uses unbuffered lease renewal loops across twenty four worker instances buy executing synchronous ttl updates on the main event thread wait switch to dedicated renewal timers instead uh under high database load delayed heartbeat probes cause premature lock expirations across sixteen post gres worker sessions buy blocking concurrent job coordinators across forty tables and triggering split brain writes across eight cluster knowed hosts so basically synchronizat lease renewal intervals buy decoupling heartbeat flushes from c p u intensive transaction workers wait change that to monotonic timer ticks instead um please configur eight lock retry attempts four the scheduled task runner resolving lease expiration races you know",
        "refined_text": "In this pull request review on distributed_lock.py, the synchronization module uses unbuffered lease renewal loops across 24 worker instances by executing synchronous TTL updates on the main event thread, switching to dedicated renewal timers instead. Under high database load, delayed heartbeat probes cause premature lock expirations across 16 Postgres worker sessions by blocking concurrent job coordinators across 40 tables and triggering split-brain writes across 8 cluster node hosts.\n\nSynchronize lease renewal intervals by decoupling heartbeat flushes from CPU intensive transaction workers, changing that to monotonic timer ticks instead. Configure 8 lock retry attempts for the scheduled task runner, resolving lease expiration races."
    },

    # Sample 12: Domain 5 (Mentoring) - Raft Consensus Heartbeat vs Election Timeouts in raft_coordinator.rs
    {
        "raw_asr": "during our technical mentoring session on distributed consensus protocols we analyzed why fixed election timeouts trigger split vote storms across twelve knowed instances buy synchronizing election timers across all peer replicas wait change that to randomized election windows instead uh when network latency spikes delayed heartbeat acknowledgments trigger cascading candidate transitions across sixteen cluster groups buy flooding r p c channels with duplicate request vote payloads and consuming excess c p u cycles across eight leader processes so basically initializ twenty four randomized timer bounds buy adding random jitter offsets between one hundred fifty and three hundred milliseconds wait switch to monotonic instant tracking instead um please deduplicat eight election vote requests four quorum consistency inside raft underscore coordinator dot rs resolving candidate election thrashing you know",
        "refined_text": "During our technical mentoring session on distributed consensus protocols, we analyzed why fixed election timeouts trigger split-vote storms across 12 node instances by synchronizing election timers across all peer replicas, changing that to randomized election windows instead. When network latency spikes, delayed heartbeat acknowledgments trigger cascading candidate transitions across 16 cluster groups by flooding RPC channels with duplicate request-vote payloads and consuming excess CPU cycles across 8 leader processes.\n\nInitialize 24 randomized timer bounds by adding random jitter offsets between 150 and 300 milliseconds, switching to monotonic instant tracking instead. Deduplicate 8 election vote requests for quorum consistency inside raft_coordinator.rs, resolving candidate election thrashing."
    },

    # Sample 13: Domain 3 (PR Review) - Async IO Event Loop Starvation from Synchronous Regex in route_matcher.py
    {
        "raw_asr": "in this pull request review on route underscore matcher dot py evaluating uncompiled regular expressions blocks the a sink i o event loop across twenty four worker threads buy running backtracking match evaluations directly on incoming url routes wait switch to compiled prefix trees instead uh during peak request surges synchronous regex evaluations stall socket polling cycles buy holding the event loop across sixteen client connections and amplifying tail latency across eight gateway services so basically allocat thirty two trie node structures buy replacing quadratic regex patterns with linear state machines wait change that to direct path lookups instead um please recalculat path matching timeouts four incoming ingress requests resolving c p u event stalls you know",
        "refined_text": "In this pull request review on route_matcher.py, evaluating uncompiled regular expressions blocks the asyncio event loop across 24 worker threads by running backtracking match evaluations directly on incoming URL routes, switching to compiled prefix trees instead. During peak request surges, synchronous regex evaluations stall socket polling cycles by holding the event loop across 16 client connections and amplifying tail latency across 8 gateway services.\n\nAllocate 32 trie node structures by replacing quadratic regex patterns with linear state machines, changing that to direct path lookups instead. Recalculate path matching timeouts for incoming ingress requests, resolving CPU event stalls."
    },

    # Sample 14: Domain 5 (Mentoring) - Linux Epoll Edge-Triggered Socket Draining in socket_poll.c
    {
        "raw_asr": "during our systems programming mentoring on linux event multiplexing we investigated why edge triggered epoll loops trigger socket starvation across sixteen worker connections buy failing two drain kernel receive buffers completely on readiness events wait switch to tight non blocking read loops until eagain is returned instead uh level triggered polling wakes the dispatcher continuously buy burning excess c p u cycles whenever buffer data remains unread across eight socket streams so basically synchronizat socket receive handling buy consuming pending payload bytes in chunked read iterations wait change that to batch read passes instead um please configur thirty two socket descriptors four the event dispatcher inside socket underscore poll dot c eliminating thread contention you know",
        "refined_text": "During our systems programming mentoring on Linux event multiplexing, we investigated why edge-triggered epoll loops trigger socket starvation across 16 worker connections by failing to drain kernel receive buffers completely on readiness events, switching to tight non-blocking read loops until EAGAIN is returned instead. Level-triggered polling wakes the dispatcher continuously by burning excess CPU cycles whenever buffer data remains unread across 8 socket streams.\n\nSynchronize socket receive handling by consuming pending payload bytes in chunked read iterations, changing that to batch read passes instead. Configure 32 socket descriptors for the event dispatcher inside socket_poll.c, eliminating thread contention."
    },

    # Sample 15: Domain 3 (PR Review) - Postgres Concurrent Index Deadlocks in schema_migrator.py
    {
        "raw_asr": "in this pull request review on schema underscore migrator dot py creating standard b tree indexes holds table exclusive locks across twenty four production tables buy blocking read and right transactions during table migration scripts wait switch to create index concurrently instead uh under concurrent database activity unindexed foreign keys escalate row locks into table level locks buy delaying query completion across sixteen post gres worker processes and triggering transaction rollbacks across eight cluster knowed hosts so basically terminat orphan lock waiter transactions buy applying aggressive lock timeout thresholds wait change that to statement timeouts instead um please initializ eight concurrent index builds four partition tables resolving c p u lock thrashing you know",
        "refined_text": "In this pull request review on schema_migrator.py, creating standard B-tree indexes holds table exclusive locks across 24 production tables by blocking read and write transactions during table migration scripts, switching to CREATE INDEX CONCURRENTLY instead. Under concurrent database activity, unindexed foreign keys escalate row locks into table-level locks by delaying query completion across 16 Postgres worker processes and triggering transaction rollbacks across 8 cluster node hosts.\n\nTerminate orphan lock waiter transactions by applying aggressive lock timeout thresholds, changing that to statement timeouts instead. Initialize 8 concurrent index builds for partition tables, resolving CPU lock thrashing."
    },

    # Sample 16: Domain 5 (Mentoring) - Lock-Free MPSC Ring Buffer Cache Line Padding in ring_channel.rs
    {
        "raw_asr": "during our technical mentoring session on lock free data structures we examined why adjacent ring buffer pointer updates degrade throughput across thirty two worker cores buy placing head and tail pointers on the same sixty four byte cache line wait change that to cache line padded boundaries instead uh when multiple producer threads write two adjacent memory locations cache coherency protocols invalidate l one cache lines across sixteen c p u cores buy forcing expensive bus snooping cycles across eight processor sockets so basically allocat sixty four byte padding offsets buy applying struct alignment attributes wait switch to crossbeam cache padded wrappers instead um please deduplicat eight pointer synchronizations four atomic queue consumers inside ring underscore channel dot rs eliminating cache contention you know",
        "refined_text": "During our technical mentoring session on lock-free data structures, we examined why adjacent ring buffer pointer updates degrade throughput across 32 worker cores by placing head and tail pointers on the same 64 byte cache line, changing that to cache-line padded boundaries instead. When multiple producer threads write to adjacent memory locations, cache coherency protocols invalidate L1 cache lines across 16 CPU cores by forcing expensive bus snooping cycles across 8 processor sockets.\n\nAllocate 64 byte padding offsets by applying struct alignment attributes, switching to crossbeam cache padded wrappers instead. Deduplicate 8 pointer synchronizations for atomic queue consumers inside ring_channel.rs, eliminating cache contention."
    },

    # Sample 17: Domain 3 (PR Review) - Unbounded Task Queue Starvation in task_executor.py
    {
        "raw_asr": "in this pull request review on task underscore executor dot py queuing unbounded background tasks exhausts heap memory across twenty four worker processes buy appending incoming jobs without backpressure limits wait switch to bounded task queues instead uh under sudden traffic bursts unbounded queues trigger memory saturation buy buffering thousands of unexecuted callables across sixteen worker pools and causing c p u thrashing across eight server instances so basically configur thirty two bounded task partitions buy setting maximum queue capacity limits wait change that to dropping oldest tasks instead um please synchronizat task dispatch boundaries four a sink job consumers across thirty two worker threads resolving executor thread exhaustion you know",
        "refined_text": "In this pull request review on task_executor.py, queuing unbounded background tasks exhausts heap memory across 24 worker processes by appending incoming jobs without backpressure limits, switching to bounded task queues instead. Under sudden traffic bursts, unbounded queues trigger memory saturation by buffering thousands of unexecuted callables across 16 worker pools and causing CPU thrashing across 8 server instances.\n\nConfigure 32 bounded task partitions by setting maximum queue capacity limits, changing that to dropping oldest tasks instead. Synchronize task dispatch boundaries for async job consumers across 32 worker threads, resolving executor thread exhaustion."
    },

    # Sample 18: Domain 5 (Mentoring) - Zero-Copy Protobuf Arena Lifetimes in proto_handler.rs
    {
        "raw_asr": "during our mentoring on systems memory safety we reviewed why borrowing byte slices from temporary protobuf message buffers creates memory safety violations across sixteen worker routines buy retaining message references past arena lifetimes wait switch to persistent arena pools instead uh when transient r p c transport buffers are reset by underlying socket workers referencing borrowed slices triggers use after free faults across forty client sessions and causes c p u faults across eight stream pipelines so basically initializ twenty four dedicated message arenas buy reserving contiguous chunk allocations wait change that to bump pointer allocations instead um please allocat twelve arena reset handlers four high throughput streams inside proto underscore handler dot rs eliminating memory corruption you know",
        "refined_text": "During our mentoring on systems memory safety, we reviewed why borrowing byte slices from temporary Protobuf message buffers creates memory safety violations across 16 worker routines by retaining message references past arena lifetimes, switching to persistent arena pools instead. When transient RPC transport buffers are reset by underlying socket workers, referencing borrowed slices triggers use-after-free faults across 40 client sessions and causes CPU faults across 8 stream pipelines.\n\nInitialize 24 dedicated message arenas by reserving contiguous chunk allocations, changing that to bump pointer allocations instead. Allocate 12 arena reset handlers for high-throughput streams inside proto_handler.rs, eliminating memory corruption."
    },

    # Sample 19: Domain 3 (PR Review) - HTTP/2 Client Transport Socket Reset in client_transport.py
    {
        "raw_asr": "in this pull request review on client underscore transport dot py the connection pooling manager leaves multiplexed http two streams hanging across twenty four proxy instances buy omitting stream cancellation handlers on socket timeouts wait switch to explicit rst stream frame handling instead uh unmanaged socket resets exhaust active stream identifiers across sixteen knowed servers buy keeping idle stream contexts open across forty minutes and degrading c p u multiplexing efficiency across eight cluster regions so basically terminat orphaned stream handles buy dispatching immediate stream resets wait change that to closing underlying tcp connections instead um please configur twelve keepalive probe checks four the a sink i o transport engine resolving gateway stream leaks you know",
        "refined_text": "In this pull request review on client_transport.py, the connection pooling manager leaves multiplexed HTTP/2 streams hanging across 24 proxy instances by omitting stream cancellation handlers on socket timeouts, switching to explicit RST_STREAM frame handling instead. Unmanaged socket resets exhaust active stream identifiers across 16 node servers by keeping idle stream contexts open across 40 minutes and degrading CPU multiplexing efficiency across 8 cluster regions.\n\nTerminate orphaned stream handles by dispatching immediate stream resets, changing that to closing underlying TCP connections instead. Configure 12 keepalive probe checks for the asyncio transport engine, resolving gateway stream leaks."
    },

    # Sample 20: Domain 5 (Mentoring) - WAL Fsync Batching & Group Commit in wal_logger.rs
    {
        "raw_asr": "when coaching our storage team member on write ahead log durability we analyzed why calling fsync after every transaction serializes disk writes across twenty worker threads buy locking disk controllers on storage devices wait change that to group commit flush loops instead uh individual disk sync calls amplify flash storage write wear buy incurring high disk latency four every write across forty r p c requests and stalling c p u execution across eight storage pipelines so basically synchronizat transaction commit queues buy grouping concurrent log records into sixteen batch buffers wait switch to twenty four batch buffers instead um please recalculat flush interval timers four the storage engine inside wal underscore logger dot rs scaling transaction throughput you know",
        "refined_text": "When coaching our storage team member on write-ahead log durability, we analyzed why calling fsync after every transaction serializes disk writes across 20 worker threads by locking disk controllers on storage devices, changing that to group commit flush loops instead. Individual disk sync calls amplify flash storage write wear by incurring high disk latency for every write across 40 RPC requests and stalling CPU execution across 8 storage pipelines.\n\nSynchronize transaction commit queues by grouping concurrent log records into 16 batch buffers, switching to 24 batch buffers instead. Recalculate flush interval timers for the storage engine inside wal_logger.rs, scaling transaction throughput."
    }
]

print(f"Total samples: {len(samples)}")

print("\nValidating individual pairs...")
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
    print(f"Sample {idx+1:02d} [{tier:6s}, {words:3d} words, {layer_count} layers]: {layer_count} active layers -> OK={ok and (c_res is not None)}")

# Validate batch
b_ok, b_msg, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print("\nBatch Validation Result:")
print("Status:", b_ok, b_msg)
print("Tier stats:", b_tiers)

if all_passed and b_ok:
    out_path = Path("scratch/subagent_batch_183.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote {len(samples)} verified pairs to {out_path}")
else:
    print("\nValidation failed! Please review errors above.")
    sys.exit(1)
