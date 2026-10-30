import json
from pathlib import Path
import importlib.util
import re

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

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. Zero newlines. Max 1 cut-word. Min 3 active noise layers.
    # =========================================================================

    # Sample 1: Domain 3 (PR Review) - RPC client idle timeout
    {
        "raw_asr": "um instruct the author two configur r p c client idle timeouts buy setting connection limits at fifteen seconds",
        "refined_text": "Instruct the author to configure RPC client idle timeouts by setting connection limits at 15 seconds."
    },

    # Sample 2: Domain 3 (PR Review) - CPU spinlock allocation
    {
        "raw_asr": "uh tell the contributor two allocat c p u spinlocks buy wrapping lock acquisitions inside deferred releases across eight worker routines",
        "refined_text": "Tell the contributor to allocate CPU spinlocks by wrapping lock acquisitions inside deferred releases across 8 worker routines."
    },

    # Sample 3: Domain 5 (Technical Mentoring) - Async task termination
    {
        "raw_asr": "basically coach the apprentice two terminat a sink task groups buy attaching cancellation signals across four consumer loops",
        "refined_text": "Coach the apprentice to terminate async task groups by attaching cancellation signals across 4 consumer loops."
    },

    # Sample 4: Domain 5 (Technical Mentoring) - Sync pool deduplication
    {
        "raw_asr": "um guide the mentee two deduplicat payload buffers buy configuring shared sync underscore pool instances across twelve ingestion streams",
        "refined_text": "Guide the mentee to deduplicate payload buffers by configuring shared sync_pool instances across 12 ingestion streams."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 sentences. Natural \n\n breaks. Max \n\n: words // 25. Min 4 noise layers.
    # =========================================================================

    # Sample 5: Domain 3 (PR Review) - Database statement cursor leak
    {
        "raw_asr": "the pull request inside query underscore executor dot py leaks database cursors when transactions abort on r p c errors wait refactor the handler buy closing active statements inside deferred blocks instead um right two unit tests validating that cursor allocat drops down towards zero across sixteen concurrent database sessions",
        "refined_text": "The pull request inside query_executor.py leaks database cursors when transactions abort on RPC errors, refactoring the handler by closing active statements inside deferred blocks instead.\n\nWrite 2 unit tests validating that cursor allocation drops down towards 0 across 16 concurrent database sessions."
    },

    # Sample 6: Domain 3 (PR Review) - Background task leak on streaming disconnect
    {
        "raw_asr": "the changes in stream underscore handler dot py spawn detached background tasks that continue running after client disconnects buy consuming excessive c p u cycles wait terminat orphaned workers buy binding task cancellation two request context instead um right three regression tests confirming that active worker threads stay below eight across thirty two dropped connections",
        "refined_text": "The changes in stream_handler.py spawn detached background tasks that continue running after client disconnects by consuming excessive CPU cycles, terminating orphaned workers by binding task cancellation to request context instead.\n\nWrite 3 regression tests confirming that active worker threads stay below 8 across 32 dropped connections."
    },

    # Sample 7: Domain 3 (PR Review) - Striped lock synchronization on cache
    {
        "raw_asr": "reviewing cache underscore manager dot py shows severe lock contention when multiple worker routines access a single global mutex buy stalling concurrent r p c requests wait refactor the synchronizat buy partitioning the cache table across sixteen striped mutex buckets instead um right four benchmark tests proving that lock hold times decrease buy seventy percent across forty parallel worker routines",
        "refined_text": "Reviewing cache_manager.py shows severe lock contention when multiple worker routines access a single global mutex by stalling concurrent RPC requests, refactoring the synchronization by partitioning the cache table across 16 striped mutex buckets instead.\n\nWrite 4 benchmark tests proving that lock hold times decrease by 70 percent across 40 parallel worker routines."
    },

    # Sample 8: Domain 5 (Technical Mentoring) - Postgres connection pool statement timeouts
    {
        "raw_asr": "coach the mentee on tuning database reliability inside pool underscore config dot py buy explaining how unbounded queries exhaust active client slots inside post gres wait guid the apprentice two configur statement timeouts at five seconds buy enforcing strict deadline boundaries instead um right two load tests verifying that connection pool usage remains stable across sixty concurrent transactions",
        "refined_text": "Coach the mentee on tuning database reliability inside pool_config.py by explaining how unbounded queries exhaust active client slots inside Postgres, guiding the apprentice to configure statement timeouts at 5 seconds by enforcing strict deadline boundaries instead.\n\nWrite 2 load tests verifying that connection pool usage remains stable across 60 concurrent transactions."
    },

    # Sample 9: Domain 5 (Technical Mentoring) - Event loop blocking offload
    {
        "raw_asr": "mentor the junior engineer on identifying event loop stalls inside event underscore dispatcher dot py buy demonstrating how intensive hashing routines block incoming a sink operations wait advis the contributor two initializ worker thread pools buy delegating work towards eight background worker processes instead um right three verification tests ensuring that event loop latency remains under ten milliseconds across fifty queued events",
        "refined_text": "Mentor the junior engineer on identifying event loop stalls inside event_dispatcher.py by demonstrating how intensive hashing routines block incoming async operations, advising the contributor to initialize worker thread pools by delegating work towards 8 background worker processes instead.\n\nWrite 3 verification tests ensuring that event loop latency remains under 10 milliseconds across 50 queued events."
    },

    # Sample 10: Domain 5 (Technical Mentoring) - RPC message deduplication
    {
        "raw_asr": "teach the apprentice how message retransmissions produce duplicate financial records inside queue underscore consumer dot py buy explaining message broker delivery guarantees wait guid the mentee two deduplicat incoming records buy verifying r p c message identifiers against sixteen cache partitions instead um right four integration tests proving that duplicate message deliveries receive status two hundred without secondary processing",
        "refined_text": "Teach the apprentice how message retransmissions produce duplicate financial records inside queue_consumer.py by explaining message broker delivery guarantees, guiding the mentee to deduplicate incoming records by verifying RPC message identifiers against 16 cache partitions instead.\n\nWrite 4 integration tests proving that duplicate message deliveries receive status 200 without secondary processing."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n. Zero numbered lists/bullets. Spoken narration.
    # Min 4 active noise layers (target 5-6).
    # =========================================================================

    # Sample 11: Domain 3 (PR Review) - Rate limiter token bucket race condition
    {
        "raw_asr": "in this pull request the rate limiting middleware in rate underscore limiter dot py introduces a critical race condition during burst traffic processing the author updates token bucket capacities buy using non atomic integer reads and writes which allows thirty concurrent worker threads two bypass rate limits wait instruct the contributor two refactor bucket updates buy using atomic compare and swap operations instead um the pull request also sets global burst thresholds without accounting four distributed cluster knowed boundaries which leads two c p u throttling across eight downstream r p c services guide the author two configur per instance burst quotas buy partitioning the global limit across active instances lastly right four stress test cases inside limiter underscore test dot py simulating five thousand requests across sixteen client threads verify that rejected requests return status four hundred twenty nine without leaking ungrounded token allocat beyond sixty requests per second you know",
        "refined_text": "In this pull request, the rate limiting middleware in rate_limiter.py introduces a critical race condition during burst traffic processing. The author updates token bucket capacities by using non-atomic integer reads and writes, which allows 30 concurrent worker threads to bypass rate limits, instructing the contributor to refactor bucket updates by using atomic compare-and-swap operations instead.\n\nThe pull request also sets global burst thresholds without accounting for distributed cluster node boundaries, which leads to CPU throttling across 8 downstream RPC services. Guide the author to configure per-instance burst quotas by partitioning the global limit across active instances.\n\nLastly, write 4 stress test cases inside limiter_test.py simulating 5000 requests across 16 client threads. Verify that rejected requests return status 429 without leaking ungrounded token allocation beyond 60 requests per second."
    },

    # Sample 12: Domain 3 (PR Review) - Phased schema migration
    {
        "raw_asr": "reviewing the database schema update inside table underscore migration dot py shows an unsafe column removal that causes downtime during rolling application updates the developer drops the legacy billing address column inside a single transactional block buy causing immediate post gres errors across twenty four active application instances wait teach the contributor two implement an expand contract phased migrat buy marking the column as deprecated during phase one instead um the pull request also alters foreign key constraints without concurrent index creation which locks the payments table four twelve minutes during peak r p c traffic tell the author two execute index validation concurrently buy scheduling background schema synchronizat across sixteen worker sessions finally right three automated migration tests inside migration underscore test dot py simulating live traffic across eight client connections verify that database query error rates stay at zero percent throughout the schema update",
        "refined_text": "Reviewing the database schema update inside table_migration.py shows an unsafe column removal that causes downtime during rolling application updates. The developer drops the legacy billing address column inside a single transactional block by causing immediate Postgres errors across 24 active application instances, teaching the contributor to implement an expand-contract phased migration by marking the column as deprecated during phase 1 instead.\n\nThe pull request also alters foreign key constraints without concurrent index creation, which locks the payments table for 12 minutes during peak RPC traffic. Tell the author to execute index validation concurrently by scheduling background schema synchronization across 16 worker sessions.\n\nFinally, write 3 automated migration tests inside migration_test.py simulating live traffic across 8 client connections. Verify that database query error rates stay at 0 percent throughout the schema update."
    },

    # Sample 13: Domain 3 (PR Review) - TLS session ticket key rotation
    {
        "raw_asr": "the pull request in tls underscore config dot py weakens cryptographic forward secrecy buy enabling static session ticket keys across forty web server instances when server keys remain constant an attacker intercepting network traffic can decrypt historical sessions wait instruct the engineer two configur automatic ticket key rotation buy regenerating keys every twenty four hours instead um the contributor also enables deprecated ciphers four backward compatibility which increases c p u overhead during incoming r p c handshakes tell the author two initializ modern cipher suites buy restricting negotiations towards authenticated encryption ciphers lastly right three security regression tests inside tls underscore test dot py testing fifty handshake handoffs across sixteen worker threads verify that session renegotiation completes within eight milliseconds with zero cipher downgrade vulnerabilities",
        "refined_text": "The pull request in tls_config.py weakens cryptographic forward secrecy by enabling static session ticket keys across 40 web server instances. When server keys remain constant, an attacker intercepting network traffic can decrypt historical sessions, instructing the engineer to configure automatic ticket key rotation by regenerating keys every 24 hours instead.\n\nThe contributor also enables deprecated ciphers for backward compatibility, which increases CPU overhead during incoming RPC handshakes. Tell the author to initialize modern cipher suites by restricting negotiations towards authenticated encryption ciphers.\n\nLastly, write 3 security regression tests inside tls_test.py testing 50 handshake handoffs across 16 worker threads. Verify that session renegotiation completes within 8 milliseconds with zero cipher downgrade vulnerabilities."
    },

    # Sample 14: Domain 3 (PR Review) - Bounded task buffer in metric collector
    {
        "raw_asr": "uh reviewing the queue ingestion architecture in metric underscore collector dot py shows unbounded task buffers that trigger out of memory crashes during network degradation the contributor queues incoming telemetry payloads inside an unbounded list buy consuming over four gigabytes of heap memory within twelve minutes wait instruct the developer two enforce bounded memory allocat buy configuring backpressure thresholds at five hundred buffer slots instead um the pull request also lacks worker heartbeat checks four dropped connections which causes c p u starvation when worker routines hang on unresolved r p c timeouts tell the author two terminat stalled worker threads buy enforcing thirty second deadline contexts you know lastly right four benchmark tests inside collector underscore test dot py simulating ten thousand telemetry events across eight producer routines verify that queue memory usage remains below sixty megabytes throughout sustained ingestion bursts",
        "refined_text": "Reviewing the queue ingestion architecture in metric_collector.py shows unbounded task buffers that trigger out-of-memory crashes during network degradation. The contributor queues incoming telemetry payloads inside an unbounded list by consuming over 4 gigabytes of heap memory within 12 minutes, instructing the developer to enforce bounded memory allocation by configuring backpressure thresholds at 500 buffer slots instead.\n\nThe pull request also lacks worker heartbeat checks for dropped connections, which causes CPU starvation when worker routines hang on unresolved RPC timeouts. Tell the author to terminate stalled worker threads by enforcing 30-second deadline contexts.\n\nLastly, write 4 benchmark tests inside collector_test.py simulating 10000 telemetry events across 8 producer routines. Verify that queue memory usage remains below 60 megabytes throughout sustained ingestion bursts."
    },

    # Sample 15: Domain 3 (PR Review) - Circuit breaker flapping recovery
    {
        "raw_asr": "in this pull request the fault tolerance logic in resilience underscore filter dot py exhibits flapping transitions between open and closed circuit states the author transitions the circuit breaker from open back towards closed immediately upon a single successful probe buy exposing downstream services two sudden request overloads wait guide the contributor two configur a gradual half open recovery buy requiring ten consecutive successful probes before closing the circuit instead um the pull request also lacks exponential backoff four failed r p c probes which floods failing downstream endpoints buy generating twenty retry attempts every second tell the author two suppress probe transmiss buy multiplying retry delay buy two after each consecutive failure lastly right three integration tests inside filter underscore test dot py simulating fifty failed requests across twelve worker routines verify that the breaker remains open until ten consecutive healthy probes succeed",
        "refined_text": "In this pull request, the fault tolerance logic in resilience_filter.py exhibits flapping transitions between open and closed circuit states. The author transitions the circuit breaker from open back towards closed immediately upon a single successful probe by exposing downstream services to sudden request overloads, guiding the contributor to configure a gradual half-open recovery by requiring 10 consecutive successful probes before closing the circuit instead.\n\nThe pull request also lacks exponential backoff for failed RPC probes, which floods failing downstream endpoints by generating 20 retry attempts every second. Tell the author to suppress probe transmission by multiplying retry delay by 2 after each consecutive failure.\n\nLastly, write 3 integration tests inside filter_test.py simulating 50 failed requests across 12 worker routines. Verify that the breaker remains open until 10 consecutive healthy probes succeed."
    },

    # Sample 16: Domain 5 (Technical Mentoring) - WAL group commit synchronization
    {
        "raw_asr": "during our database systems mentoring session i coached the apprentice on tuning durability trade offs inside wal underscore manager dot py our storage engine experienced severe write bottlenecks when every write transaction invoked fsync synchronously buy dropping throughput down towards thirty operations per second wait guide the mentee two implement group commit disk synchronizat buy batching pending writes every ten milliseconds instead um we also analyzed how post gres balances transaction durability against c p u overhead four high throughput ingestion pipelines pair with the developer two initializ an asynchronous wal flush ring buffer buy buffering four megabytes of dirty log blocks before committing writes towards disk lastly right four load tests inside wal underscore test dot py measuring transaction latencies across twenty four concurrent writers verify that disk write throughput scales up from thirty operations up into fifteen hundred operations per second while maintaining zero data loss on simulated engine restarts",
        "refined_text": "During our database systems mentoring session, I coached the apprentice on tuning durability trade-offs inside wal_manager.py. Our storage engine experienced severe write bottlenecks when every write transaction invoked fsync synchronously by dropping throughput down towards 30 operations per second, guiding the mentee to implement group commit disk synchronization by batching pending writes every 10 milliseconds instead.\n\nWe also analyzed how Postgres balances transaction durability against CPU overhead for high-throughput ingestion pipelines. Pair with the developer to initialize an asynchronous WAL flush ring buffer by buffering 4 megabytes of dirty log blocks before committing writes towards disk.\n\nLastly, write 4 load tests inside wal_test.py measuring transaction latencies across 24 concurrent writers. Verify that disk write throughput scales up from 30 operations up into 1500 operations per second while maintaining zero data loss on simulated engine restarts."
    },

    # Sample 17: Domain 5 (Technical Mentoring) - Raft consensus leader election
    {
        "raw_asr": "in our distributed systems mentoring session i reviewed raft consensus mechanics with the junior developer inside consensus underscore node dot py our experimental cluster suffered repeated election collisions when election timers expired simultaneously across three replica knowed instances buy triggering continuous term increments without establishing a stable leader wait coach the mentee two initializ randomized election timeouts between one hundred fifty and three hundred milliseconds buy staggering election attempts instead um we also examined how split brain partitions occur when network delays block heartbeat r p c messages four active followers pair with the engineer two terminat stale leader leases buy enforcing minimum quorum acknowledgments across four out of seven cluster members you know lastly right three cluster chaos tests inside consensus underscore test dot py simulating dropped packets across five follower instances verify that a single leader is elected within five hundred milliseconds and holds leadership across twenty simulated partition rounds",
        "refined_text": "In our distributed systems mentoring session, I reviewed Raft consensus mechanics with the junior developer inside consensus_node.py. Our experimental cluster suffered repeated election collisions when election timers expired simultaneously across 3 replica node instances by triggering continuous term increments without establishing a stable leader, coaching the mentee to initialize randomized election timeouts between 150 and 300 milliseconds by staggering election attempts instead.\n\nWe also examined how split-brain partitions occur when network delays block heartbeat RPC messages for active followers. Pair with the engineer to terminate stale leader leases by enforcing minimum quorum acknowledgments across 4 out of 7 cluster members.\n\nLastly, write 3 cluster chaos tests inside consensus_test.py simulating dropped packets across 5 follower instances. Verify that a single leader is elected within 500 milliseconds and holds leadership across 20 simulated partition rounds."
    },

    # Sample 18: Domain 5 (Technical Mentoring) - Heap escape analysis & zero-copy DMA
    {
        "raw_asr": "i paired with the network engineer two investigate garbage collection pressure inside packet underscore parser dot py our packet processing pipeline experienced recurring latency spikes when temporary byte slices escaped two the heap buy generating four hundred megabytes of garbage per minute wait mentor the apprentice two avoid heap allocat buy passing fixed size byte arrays by value instead um we also analyzed how d m a ring buffers interact with c p u cache lines four zero copy ingestion pair with the mentee two deduplicat header metadata buy utilizing shared slice pointers across sixteen worker threads without dynamic resizing lastly right three memory benchmark tests inside parser underscore test dot py measuring allocation rates across ten thousand simulated packet payloads verify that heap allocations drop down from forty allocations down into zero allocations per packet across eight parallel worker routines",
        "refined_text": "I paired with the network engineer to investigate garbage collection pressure inside packet_parser.py. Our packet processing pipeline experienced recurring latency spikes when temporary byte slices escaped to the heap by generating 400 megabytes of garbage per minute, mentoring the apprentice to avoid heap allocation by passing fixed-size byte arrays by value instead.\n\nWe also analyzed how DMA ring buffers interact with CPU cache lines for zero-copy ingestion. Pair with the mentee to deduplicate header metadata by utilizing shared slice pointers across 16 worker threads without dynamic resizing.\n\nLastly, write 3 memory benchmark tests inside parser_test.py measuring allocation rates across 10000 simulated packet payloads. Verify that heap allocations drop down from 40 allocations down into 0 allocations per packet across 8 parallel worker routines."
    },

    # Sample 19: Domain 5 (Technical Mentoring) - Graceful service shutdown
    {
        "raw_asr": "in our architecture mentoring session i guided the mentee through implementing graceful termination inside service underscore lifecycle dot py our application server dropped active client requests during rolling deployments when the main process exited immediately upon receiving sigterm buy causing forty connection reset errors across active clients wait coach the developer two stop accepting incoming requests buy deregistering health endpoints from discovery registries first instead um we also discussed managing in flight a sink operations four outstanding r p c calls pair with the apprentice two configur a shutdown grace period of thirty seconds buy waiting four worker thread pools two complete pending requests before socket closure lastly right four integration tests inside lifecycle underscore test dot py simulating rolling restart signals across sixteen active client connections verify that zero in flight requests abort during shutdown while all twenty pending requests complete successfully",
        "refined_text": "In our architecture mentoring session, I guided the mentee through implementing graceful termination inside service_lifecycle.py. Our application server dropped active client requests during rolling deployments when the main process exited immediately upon receiving SIGTERM by causing 40 connection reset errors across active clients, coaching the developer to stop accepting incoming requests by deregistering health endpoints from discovery registries first instead.\n\nWe also discussed managing in-flight async operations for outstanding RPC calls. Pair with the apprentice to configure a shutdown grace period of 30 seconds by waiting for worker thread pools to complete pending requests before socket closure.\n\nLastly, write 4 integration tests inside lifecycle_test.py simulating rolling restart signals across 16 active client connections. Verify that zero in-flight requests abort during shutdown while all 20 pending requests complete successfully."
    },

    # Sample 20: Domain 5 (Technical Mentoring) - Singleflight query deduplication
    {
        "raw_asr": "during our backend mentoring session i explained single flight request coalescing two the junior developer inside query underscore cache dot py our user service experienced severe cache stampede spikes when hot user profile keys expired buy sending twelve hundred identical queries towards the post gres knowed within five seconds wait teach the mentee two deduplicat simultaneous queries buy using single flight mutex groups instead um we examined how in flight request deduplication collapses redundant queries four identical keys into a single backend fetch pair with the engineer two implement background cache synchronizat buy warming expiring keys thirty seconds before ttl expiration you know lastly right three concurrency benchmark tests inside cache underscore test dot py simulating eight hundred concurrent requests across sixteen client workers verify that backend database fetches drop down from twelve hundred queries down into exactly one query during key refresh cycles",
        "refined_text": "During our backend mentoring session, I explained single flight request coalescing to the junior developer inside query_cache.py. Our user service experienced severe cache stampede spikes when hot user profile keys expired by sending 1200 identical queries towards the Postgres node within 5 seconds, teaching the mentee to deduplicate simultaneous queries by using single flight mutex groups instead.\n\nWe examined how in-flight request deduplication collapses redundant queries for identical keys into a single backend fetch. Pair with the engineer to implement background cache synchronization by warming expiring keys 30 seconds before TTL expiration.\n\nLastly, write 3 concurrency benchmark tests inside cache_test.py simulating 800 concurrent requests across 16 client workers. Verify that backend database fetches drop down from 1200 queries down into exactly 1 query during key refresh cycles."
    }
]

print(f"Total samples defined: {len(samples)}")
assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

# 1. Check each pair with validate_pair and clean_sample
all_passed = True
tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(samples, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    try:
        raw.encode("ascii")
        ref.encode("ascii")
    except UnicodeEncodeError as e:
        print(f"Sample {idx} non-ASCII character: {e}")
        all_passed = False

    # Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"Sample {idx} LEAKAGE: raw_asr in eval set!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {idx} LEAKAGE: refined_text in eval set!")
        all_passed = False

    # Noise layers
    nl = val_mod.get_noise_layer_count(raw)
    layer_counts.append(nl)
    words = len(ref.split())

    # Tier tracking and invariants
    if words < 25:
        tiers["short"] += 1
        if "\n" in ref:
            print(f"Sample {idx} has newline in short tier!")
            all_passed = False
        if nl < 3:
            print(f"Sample {idx} short tier active layers < 3 ({nl})")
            all_passed = False
    elif words < 90:
        tiers["medium"] += 1
        if nl < 4:
            print(f"Sample {idx} medium tier active layers < 4 ({nl})")
            all_passed = False
    else:
        tiers["long"] += 1
        if "\n\n" not in ref:
            print(f"Sample {idx} missing paragraph break in long tier!")
            all_passed = False
        if nl < 4:
            print(f"Sample {idx} long tier active layers < 4 ({nl})")
            all_passed = False

    # Validator check with min_noise_layers=4 (allows 3 for short)
    val_ok, val_reason = val_mod.validate_pair(pair, min_noise_layers=4)
    if not val_ok:
        print(f"Sample {idx} failed validate_pair: {val_reason}")
        all_passed = False

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    if clean_obj is None or clean_reason != "kept":
        print(f"Sample {idx} failed clean_sample: {clean_reason}")
        all_passed = False

    layers_active = val_mod.count_active_noise_layers(raw)
    active_str = ", ".join(k for k, v in layers_active.items() if v)
    print(f"Sample {idx:02d}: words={words:3d}, layers={nl} [{active_str}], val={val_ok}, clean={clean_reason}")

# Batch validation
batch_ok, batch_reason, batch_stats = val_mod.validate_batch(
    samples,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
if not batch_ok:
    print(f"Batch validation failed: {batch_reason}")
    all_passed = False
else:
    print(f"validate_batch OK: {batch_reason}, stats={batch_stats}")

avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Tiers: {tiers}")
print(f"Average noise layers: {avg_layers:.2f}")

assert all_passed, "Some validation checks failed!"

# Write out to scratch/subagent_batch_173.json
out_file = Path("scratch/subagent_batch_173.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Successfully generated and validated 20 samples to {out_file}")
