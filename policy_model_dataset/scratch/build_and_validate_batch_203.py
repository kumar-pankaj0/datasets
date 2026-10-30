import json
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
    # --- SHORT SAMPLES (4) ---
    {
        "raw_asr": "um instruct the contributor two configur idle timeouts buy setting max lifetime inside connection underscore pool wait instead of leaving sockets open",
        "refined_text": "Instruct the contributor to configure idle timeouts by setting max lifetime inside connection_pool instead of leaving sockets open."
    },
    {
        "raw_asr": "uh mentor the apprentice buy wrapping a sink r p c worker dispatch inside queue underscore manager wait instead of blocking threads",
        "refined_text": "Mentor the apprentice by wrapping async RPC worker dispatch inside queue_manager instead of blocking threads."
    },
    {
        "raw_asr": "basically advise the author two allocat buffer memory buy using atomic compare and swap slots instead inside ring underscore buffer",
        "refined_text": "Advise the author to allocate buffer memory by using atomic compare and swap slots instead inside ring_buffer."
    },
    {
        "raw_asr": "uh ask the engineer two deduplicat c p u profiling records buy batching trace spans instead inside trace underscore collector",
        "refined_text": "Ask the engineer to deduplicate CPU profiling records by batching trace spans instead inside trace_collector."
    },

    # --- MEDIUM SAMPLES (6) ---
    {
        "raw_asr": "in packet underscore decoder dot py the author allocat fresh byte slices on every incoming packet which triggers aggressive garbage collection pauses under high c p u throughput wait replac heap allocations buy recycling buffers through sync dot pool instead um right two unit tests validating that buffer reuse generates zero heap allocations across four thousand network frames",
        "refined_text": "In packet_decoder.py, the author allocates fresh byte slices on every incoming packet which triggers aggressive garbage collection pauses under high CPU throughput, replacing heap allocations by recycling buffers through sync.Pool instead.\n\nWrite 2 unit tests validating that buffer reuse generates 0 heap allocations across 4000 network frames."
    },
    {
        "raw_asr": "mentor the apprentice on query execution plans inside query underscore optimizer dot py buy explaining how full table scans degrade post gres performance when querying active user records when ninety percent of rows contain soft deleted records standard indexes waste memory buy caching obsolete entries wait instruct the mentee two configur a partial index buy appending a where deleted at is null filter instead uh right three query benchmarks confirming single digit millisecond latencies",
        "refined_text": "Mentor the apprentice on query execution plans inside query_optimizer.py by explaining how full table scans degrade Postgres performance when querying active user records. When 90 percent of rows contain soft deleted records, standard indexes waste memory by caching obsolete entries, instructing the mentee to configure a partial index by appending a where deleted at is null filter instead.\n\nWrite 3 query benchmarks confirming single digit millisecond latencies."
    },
    {
        "raw_asr": "reviewing telemetry underscore proxy dot py indicates that streaming r p c handlers buffer outgoing spans without window flow control when downstream collectors slow down memory consumption climbs from fifty megabytes up through two gigabytes within four minutes buy triggering out of memory crashes wait configur stream flow control buy honoring client read acknowledgments instead um tell the developer two synchronizat chunk delivery across eight worker channels",
        "refined_text": "Reviewing telemetry_proxy.py indicates that streaming RPC handlers buffer outgoing spans without window flow control. When downstream collectors slow down, memory consumption climbs from 50 megabytes up through 2 gigabytes within 4 minutes by triggering out of memory crashes, configuring stream flow control by honoring client read acknowledgments instead.\n\nTell the developer to synchronize chunk delivery across 8 worker channels."
    },
    {
        "raw_asr": "walk the junior systems engineer through epoll socket events inside network underscore poller dot py buy explaining why edge triggered mode requires non blocking loops until e again occurs when twenty concurrent sockets receive data level triggered polling causes redundant wakeups buy consuming forty percent of c p u capacity wait switch to edge triggered notifications buy reading until buffer exhaustion instead uh right two load simulations verifying clean socket drain operat",
        "refined_text": "Walk the junior systems engineer through epoll socket events inside network_poller.py by explaining why edge triggered mode requires non blocking loops until EAGAIN occurs. When 20 concurrent sockets receive data, level triggered polling causes redundant wakeups by consuming 40 percent of CPU capacity, switching to edge triggered notifications by reading until buffer exhaustion instead.\n\nWrite 2 load simulations verifying clean socket drain operation."
    },
    {
        "raw_asr": "in session underscore authenticator dot py the author validates j w t signatures but skips token expiration checks during distributed r p c authentication when node clocks drift buy twelve seconds expired tokens remain accepted across four cluster services wait configur strict clock skew tolerance buy adding a thirty second leeway window instead um tell the contributor two terminat invalid sessions buy revoking expired claims immediately",
        "refined_text": "In session_authenticator.py, the author validates JWT signatures but skips token expiration checks during distributed RPC authentication. When node clocks drift by 12 seconds, expired tokens remain accepted across 4 cluster services, configuring strict clock skew tolerance by adding a 30 second leeway window instead.\n\nTell the contributor to terminate invalid sessions by revoking expired claims immediately."
    },
    {
        "raw_asr": "mentor the mentee two initializ redis pipelining inside cache underscore warmer dot py buy explaining how individual command round trips degrade network throughput under high load when warming fifty thousand keys sequential get commands spend ninety percent of execution time waiting on r p c network latency wait batch command execution buy using redis pipelines across one hundred key batches instead uh right three throughput tests verifying ten fold latency reductions",
        "refined_text": "Mentor the mentee to initialize Redis pipelining inside cache_warmer.py by explaining how individual command round trips degrade network throughput under high load. When warming 50000 keys, sequential get commands spend 90 percent of execution time waiting on RPC network latency, batching command execution by using Redis pipelines across 100 key batches instead.\n\nWrite 3 throughput tests verifying ten fold latency reductions."
    },

    # --- LONG SAMPLES (10) ---
    {
        "raw_asr": "in worker underscore pool dot py the pull request implements a custom thread pool but introduces race conditions buy accessing the task counter without mutex synchronizat when twelve worker threads process incoming jobs concurrent increments clobber shared integer state buy reporting seventy completed jobs instead of one hundred wait refactor counter updates buy using atomic fetch and add operations across all thirty two worker threads instead um furthermore worker routines fail two inspect thread termination flags which causes worker threads two hang indefinitely when the server initiates shutdown tell the contributor two configur graceful shutdown timeouts buy waiting fifteen seconds before terminating worker threads during high c p u utilization finally right four concurrency stress tests inside pool underscore test dot py launching fifty threads buy confirming that task counters remain accurate across ten thousand scheduled tasks",
        "refined_text": "In worker_pool.py, the pull request implements a custom thread pool but introduces race conditions by accessing the task counter without mutex synchronization. When 12 worker threads process incoming jobs, concurrent increments clobber shared integer state by reporting 70 completed jobs instead of 100, refactoring counter updates by using atomic fetch and add operations across all 32 worker threads instead.\n\nFurthermore, worker routines fail to inspect thread termination flags which causes worker threads to hang indefinitely when the server initiates shutdown. Tell the contributor to configure graceful shutdown timeouts by waiting 15 seconds before terminating worker threads during high CPU utilization.\n\nFinally, write 4 concurrency stress tests inside pool_test.py launching 50 threads by confirming that task counters remain accurate across 10000 scheduled tasks."
    },
    {
        "raw_asr": "mentor the database apprentice on physical replication lag inside replication underscore monitor dot py buy explaining how physical replication slots hold write ahead log segments on primary servers when standby replicas disconnect during network maintenance post gres accumulates ten gigabytes of w a l files within two hours buy exhausting host storage partitions across four database nodes wait teach the mentee two configur max slot wal keep size buy capping retained log segments at thirty two gigabytes instead um explain how monitoring pg stat replication provides visibility into replay byte lag advise the engineer two configur prometheus alerting buy tracking replication byte lag above five hundred megabytes during heavy c p u write operations lastly right three integration tests inside replication underscore test dot py simulating standby disconnects across sixty seconds buy verifying that log retention safeguards prevent primary storage exhaustion",
        "refined_text": "Mentor the database apprentice on physical replication lag inside replication_monitor.py by explaining how physical replication slots hold write ahead log segments on primary servers. When standby replicas disconnect during network maintenance, Postgres accumulates 10 gigabytes of WAL files within 2 hours by exhausting host storage partitions across 4 database nodes, teaching the mentee to configure max slot wal keep size by capping retained log segments at 32 gigabytes instead.\n\nExplain how monitoring pg stat replication provides visibility into replay byte lag. Advise the engineer to configure Prometheus alerting by tracking replication byte lag above 500 megabytes during heavy CPU write operations.\n\nLastly, write 3 integration tests inside replication_test.py simulating standby disconnects across 60 seconds by verifying that log retention safeguards prevent primary storage exhaustion."
    },
    {
        "raw_asr": "in upstream underscore gateway dot py the author implemented an outbound proxy client but omitted d n s caching which forces a synchronous d n s resolution on every outbound r p c call under thirty thousand requests per second synchronous name lookups exhaust udp sockets buy triggering connection drop spikes across eight gateway pods wait configur an in memory d n s cache buy caching resolved addresses across a sixty second t t l window instead um the pull request also sets default connect timeouts at twenty seconds which holds worker threads open when upstream targets become unreachable tell the author two terminat stalling connections buy setting connect timeouts at two seconds during c p u throttling lastly right four load tests inside gateway underscore test dot py simulating intermittent d n s timeouts buy verifying that cached lookups sustain twenty thousand requests per second without socket starvation",
        "refined_text": "In upstream_gateway.py, the author implemented an outbound proxy client but omitted DNS caching which forces a synchronous DNS resolution on every outbound RPC call. Under 30000 requests per second, synchronous name lookups exhaust UDP sockets by triggering connection drop spikes across 8 gateway pods, configuring an in memory DNS cache by caching resolved addresses across a 60 second TTL window instead.\n\nThe pull request also sets default connect timeouts at 20 seconds which holds worker threads open when upstream targets become unreachable. Tell the author to terminate stalling connections by setting connect timeouts at 2 seconds during CPU throttling.\n\nLastly, write 4 load tests inside gateway_test.py simulating intermittent DNS timeouts by verifying that cached lookups sustain 20000 requests per second without socket starvation."
    },
    {
        "raw_asr": "walk the backend apprentice through zero copy serialization inside message underscore encoder dot py buy explaining how traditional serialization formats like json require object parsing during data deserialization when processing forty thousand telemetry packets per second json decoding consumes sixty percent of c p u time buy causing GC pause spikes across twelve cluster workers wait teach the mentee two allocat flatbuffers binary payloads buy accessing serialized fields directly without unpacking memory buffers instead um discuss how byte alignment guarantees direct memory pointer access across sixty four bit architectures advise the engineer two configur buffer reuse buy pooling memory allocators during event transmiss lastly right three benchmark suites inside encoder underscore test dot py comparing json against zero copy encoding across one hundred thousand records buy demonstrating a five fold reduction in memory allocations",
        "refined_text": "Walk the backend apprentice through zero copy serialization inside message_encoder.py by explaining how traditional serialization formats like JSON require object parsing during data deserialization. When processing 40000 telemetry packets per second, JSON decoding consumes 60 percent of CPU time by causing GC pause spikes across 12 cluster workers, teaching the mentee to allocate FlatBuffers binary payloads by accessing serialized fields directly without unpacking memory buffers instead.\n\nDiscuss how byte alignment guarantees direct memory pointer access across 64 bit architectures. Advise the engineer to configure buffer reuse by pooling memory allocators during event transmission.\n\nLastly, write 3 benchmark suites inside encoder_test.py comparing JSON against zero copy encoding across 100000 records by demonstrating a five fold reduction in memory allocations."
    },
    {
        "raw_asr": "the pull request in order underscore settler dot py attempts distributed reconciliation buy locking individual ledger rows across multiple tables but causes frequent deadlock aborts when twelve background jobs process overlapping accounts post gres detects cyclic dependency graphs buy terminat up through thirty transactions every hour wait replac row level locking buy acquiring application level advisory locks using customer hash keys instead um the review also notes that the contributor forgets two release advisory locks on error paths which leaks held locks across eighty database worker connections advise the author two wrap lock execution inside a try finally block buy releasing advisory locks unconditionally upon transaction completion during r p c calls finally right five integration tests inside settler underscore test dot py running twenty concurrent settlement workers buy confirming zero deadlock aborts across five hundred transactions",
        "refined_text": "The pull request in order_settler.py attempts distributed reconciliation by locking individual ledger rows across multiple tables but causes frequent deadlock aborts. When 12 background jobs process overlapping accounts, Postgres detects cyclic dependency graphs by terminating up through 30 transactions every hour, replacing row level locking by acquiring application level advisory locks using customer hash keys instead.\n\nThe review also notes that the contributor forgets to release advisory locks on error paths which leaks held locks across 80 database worker connections. Advise the author to wrap lock execution inside a try finally block by releasing advisory locks unconditionally upon transaction completion during RPC calls.\n\nFinally, write 5 integration tests inside settler_test.py running 20 concurrent settlement workers by confirming 0 deadlock aborts across 500 transactions."
    },
    {
        "raw_asr": "mentor the distributed systems apprentice on saga pattern execution inside workflow underscore engine dot py buy explaining how distributed transactions maintain eventual consistency across microservices when multi step checkout workflows fail at payment authorization step three previous reservations remain uncommitted buy creating orphan resource locks across sixteen inventory nodes wait instruct the mentee two implement compensating transactions buy executing reverse cancellations upon workflow failure instead um explain why idempotency keys prevent duplicate compensation during network retries advise the developer two synchronizat compensation steps buy persisting step state inside a durable outbox table during r p c calls lastly right four failure injection tests inside workflow underscore test dot py simulating payment gateway timeouts buy validating that all reserved items release cleanly across fifty workflow instances",
        "refined_text": "Mentor the distributed systems apprentice on saga pattern execution inside workflow_engine.py by explaining how distributed transactions maintain eventual consistency across microservices. When multi step checkout workflows fail at payment authorization step 3, previous reservations remain uncommitted by creating orphan resource locks across 16 inventory nodes, instructing the mentee to implement compensating transactions by executing reverse cancellations upon workflow failure instead.\n\nExplain why idempotency keys prevent duplicate compensation during network retries. Advise the developer to synchronize compensation steps by persisting step state inside a durable outbox table during RPC calls.\n\nLastly, write 4 failure injection tests inside workflow_test.py simulating payment gateway timeouts by validating that all reserved items release cleanly across 50 workflow instances."
    },
    {
        "raw_asr": "in stream underscore pipeline dot py the pull request introduces streaming response processing buy reading large files with python generators but fails two ensure generator cleanup when client connections terminate early when consumers abort requests mid stream generator finally blocks never execute buy leaking open file descriptors across two hundred concurrent streams wait refactor the stream handler buy wrapping generator consumption inside context managers with explicit close methods instead um the author also omitted backpressure handling which causes memory allocations two spike across four gigabytes when downstream consumers read slowly instruct the contributor two configur bounded chunks buy buffering sixteen kilobytes per yield during c p u streaming finally right three stress tests inside stream underscore test dot py simulating early client cancellations buy verifying that file descriptors close immediately",
        "refined_text": "In stream_pipeline.py, the pull request introduces streaming response processing by reading large files with Python generators but fails to ensure generator cleanup when client connections terminate early. When consumers abort requests mid stream, generator finally blocks never execute by leaking open file descriptors across 200 concurrent streams, refactoring the stream handler by wrapping generator consumption inside context managers with explicit close methods instead.\n\nThe author also omitted backpressure handling which causes memory allocations to spike across 4 gigabytes when downstream consumers read slowly. Instruct the contributor to configure bounded chunks by buffering 16 kilobytes per yield during CPU streaming.\n\nFinally, write 3 stress tests inside stream_test.py simulating early client cancellations by verifying that file descriptors close immediately."
    },
    {
        "raw_asr": "walk the database mentee through b tree index page splits inside index underscore manager dot py buy explaining how frequent row updates cause index bloat in post gres when update heavy tables reach one hundred percent page fillfactor any row expansion forces physical page splits buy dividing data blocks across two separate pages and increasing disk right operations wait teach the apprentice two configur table fillfactor at eighty percent buy leaving free space for heap only tuple updates instead um explain how h o t updates avoid touching index pages completely when updated columns lack indexing instruct the developer two monitor index fragmentation buy tracking leaf page split statistics during c p u write bursts lastly right four simulation scripts inside index underscore test dot py executing fifty thousand updates buy confirming that index bloat remains below ten percent",
        "refined_text": "Walk the database mentee through B-tree index page splits inside index_manager.py by explaining how frequent row updates cause index bloat in Postgres. When update heavy tables reach 100 percent page fillfactor, any row expansion forces physical page splits by dividing data blocks across 2 separate pages and increasing disk write operations, teaching the apprentice to configure table fillfactor at 80 percent by leaving free space for heap only tuple updates instead.\n\nExplain how HOT updates avoid touching index pages completely when updated columns lack indexing. Instruct the developer to monitor index fragmentation by tracking leaf page split statistics during CPU write bursts.\n\nLastly, write 4 simulation scripts inside index_test.py executing 50000 updates by confirming that index bloat remains below 10 percent."
    },
    {
        "raw_asr": "reviewing ring underscore queue dot py reveals a severe multi threaded performance bottleneck buy placing head and tail queue pointers on adjacent memory locations when four producer threads and four consumer threads access the queue simultaneously c p u cores invalidate shared l one cache lines across sixty four byte cache boundaries buy degrading throughput from two million down into two hundred thousand operations per second wait separ head and tail pointers buy adding sixty four bytes of cache line padding between queue fields instead um the contributor also used plain load operations without acquire release memory semantics which permits out of order memory reads advise the author two configur atomic memory orderings buy applying release semantics on enqueue and acquire semantics on dequeue finally right four high contention benchmarks inside queue underscore test dot py running eight threads buy confirming that padded queues sustain two million operations per second",
        "refined_text": "Reviewing ring_queue.py reveals a severe multi threaded performance bottleneck by placing head and tail queue pointers on adjacent memory locations. When 4 producer threads and 4 consumer threads access the queue simultaneously, CPU cores invalidate shared L1 cache lines across 64 byte cache boundaries by degrading throughput from 2000000 down into 200000 operations per second, separating head and tail pointers by adding 64 bytes of cache line padding between queue fields instead.\n\nThe contributor also used plain load operations without acquire release memory semantics which permits out of order memory reads. Advise the author to configure atomic memory orderings by applying release semantics on enqueue and acquire semantics on dequeue.\n\nFinally, write 4 high contention benchmarks inside queue_test.py running 8 threads by confirming that padded queues sustain 2000000 operations per second."
    },
    {
        "raw_asr": "teach the platform apprentice how distributed tracing propagates request context inside tracer underscore agent dot py buy explaining how asynchronous coroutines lose context when spawning detached tasks when worker routines launch thirty detached background jobs without context propagation post gres and r p c child spans lose their trace parent headers buy creating disconnected trace graphs in jaeger wait instruct the mentee two capture current trace context buy passing explicit trace carrier structs into worker routines instead um explain how the w three c trace context standard encodes trace id and parent id fields advise the engineer two configur automatic header injection buy registering middleware interceptors across all outbound requests during c p u spikes lastly right three propagation tests inside tracer underscore test dot py verifying that child spans retain parent trace identifiers across five nested async operations",
        "refined_text": "Teach the platform apprentice how distributed tracing propagates request context inside tracer_agent.py by explaining how asynchronous coroutines lose context when spawning detached tasks. When worker routines launch 30 detached background jobs without context propagation, Postgres and RPC child spans lose their traceparent headers by creating disconnected trace graphs in Jaeger, instructing the mentee to capture current trace context by passing explicit trace carrier structs into worker routines instead.\n\nExplain how the W3C trace context standard encodes trace ID and parent ID fields. Advise the engineer to configure automatic header injection by registering middleware interceptors across all outbound requests during CPU spikes.\n\nLastly, write 3 propagation tests inside tracer_test.py verifying that child spans retain parent trace identifiers across 5 nested async operations."
    }
]

print(f"Total candidate pairs: {len(pairs)}")
assert len(pairs) == 20

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, p in enumerate(pairs, 1):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Word count and tier check
    w = len(ref.split())
    nl = val_mod.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if w < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx} short tier contains newline!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
    elif w < 90:
        tiers["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} long tier missing \\n\\n"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"

    # Validator check
    v_ok, v_reason = val_mod.validate_pair(p, min_noise_layers=4)
    assert v_ok, f"Sample {idx} failed validate_pair: {v_reason}"

    # Cleaner check
    c_res, c_reason = clean_mod.clean_sample(raw, ref)
    assert c_res is not None, f"Sample {idx} failed clean_sample: {c_reason}"
    assert c_reason == "kept", f"Sample {idx} cleaner status not kept: {c_reason}"

# Batch validation
b_ok, b_reason, b_stats = val_mod.validate_batch(
    pairs,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert b_ok, f"Batch validation failed: {b_reason}"

# Save to target file
target_path = Path("scratch/subagent_batch_203.json")
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"Successfully generated and validated {len(pairs)} pairs!")
print(f"Saved to: {target_path}")
print(f"Tier counts: {tiers}")
print(f"Average active noise layers: {sum(layer_counts)/len(layer_counts):.2f}")
print(f"Noise layer distribution: {b_stats.get('noise_layer_distribution')}")
