import json
import re
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("validator", "code/validator.py")
validator = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(validator)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("cleaner", "code/cleaner.py")
cleaner = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(cleaner)

pairs = [
    # Tier 1: Short (< 25 words, exactly 1 sentence, zero newlines, max 1 cut-word)
    # Pair 1: Domain 2 - Daily Standups
    {
        "raw_asr": "um yesterday i finished the session store migr wait the session store migration and today ticket four hundred twelve is blocked buy the network policy",
        "refined_text": "Yesterday I finished the session store migration, and today ticket 412 is blocked by the network policy."
    },
    # Pair 2: Domain 2 - Daily Standups
    {
        "raw_asr": "uh i am still investigat the timeout in the gateway service after setting the request deadline at thirty seconds",
        "refined_text": "I am still investigating the timeout in the gateway service after setting the request deadline at 30 seconds."
    },
    # Pair 3: Domain 3 - PR Code Reviews
    {
        "raw_asr": "um please inspect the mutex lock ordering in the worker dispatcher because this synchronizat call can cause deadlocks",
        "refined_text": "Please inspect the mutex lock ordering in the worker dispatcher because this synchronization call can cause deadlocks."
    },
    # Pair 4: Domain 3 - PR Code Reviews
    {
        "raw_asr": "uh please right this error status directly by propagat the wrapped error code",
        "refined_text": "Please write this error status directly by propagating the wrapped error code."
    },

    # Tier 2: Medium (25-89 words, 1-3 sentences, natural paragraph break)
    # Pair 5: Domain 2 - Daily Standups
    {
        "raw_asr": "um yesterday we observed elevated consumer lag across partition four and partition five during peak ingest uh thirty thousand messages backed up in the ingest topic today i am tuning the max poll interval setting at sixty seconds so the consumer group stops triggering partition rebalanc loops",
        "refined_text": "Yesterday we observed elevated consumer lag across partition 4 and partition 5 during peak ingest, when 30000 messages backed up in the ingest topic.\n\nToday I am tuning the max poll interval setting at 60 seconds so the consumer group stops triggering partition rebalance loops."
    },
    # Pair 6: Domain 2 - Daily Standups
    {
        "raw_asr": "uh on the session service our redis cache invalidat job failed twice overnight due to a lock contention error in the worker knowed today ticket eight hundred sixteen is ready for verification after flushing the stale keys",
        "refined_text": "On the session service, our Redis cache invalidation job failed twice overnight due to a lock contention error in the worker node.\n\nToday ticket 816 is ready for verification after flushing the stale keys."
    },
    # Pair 7: Domain 2 - Daily Standups
    {
        "raw_asr": "um the staging deployment completed late last night for release two hundred ten but post gres replica lag spiked at forty milliseconds my only blocker today is coordinat with the platform team to verify replication health",
        "refined_text": "The staging deployment completed late last night for release 210, but Postgres replica lag spiked at 40 milliseconds.\n\nMy only blocker today is coordinating with the platform team to verify replication health."
    },
    # Pair 8: Domain 3 - PR Code Reviews
    {
        "raw_asr": "uh in pull request one hundred five this background goroutine spawns without inherit the request context which leaks worker threads please cancel the context explicitly using the defer cancel pattern",
        "refined_text": "In pull request 105, this background goroutine spawns without inheriting the request context, which leaks worker threads.\n\nPlease cancel the context explicitly using the defer cancel pattern."
    },
    # Pair 9: Domain 3 - PR Code Reviews
    {
        "raw_asr": "um reviewing pull request three hundred four the new account lookup query performs a sequential table scan across fifty thousand records please update the index configur on tenant id and status so query latency drops",
        "refined_text": "Reviewing pull request 304, the new account lookup query performs a sequential table scan across 50000 records.\n\nPlease update the index configuration on tenant id and status so query latency drops."
    },
    # Pair 10: Domain 3 - PR Code Reviews
    {
        "raw_asr": "uh looking at pull request five hundred twenty the database pool size is hardcoded at eighty connections without an idle timeout communicat errors will occur when post gres drops idle sockets after five minutes",
        "refined_text": "Looking at pull request 520, the database pool size is hardcoded at 80 connections without an idle timeout.\n\nCommunication errors will occur when Postgres drops idle sockets after 5 minutes."
    },

    # Tier 3: Long (90+ words, multi-paragraph narration separated by \n\n)
    # Pair 11: Domain 2 - Daily Standups
    {
        "raw_asr": "um yesterday our team finished deploying the open telemetry sidecars across forty pods in the payment cluster uh however the jaeger collector experienced severe memory pressure when ingest spiked at twelve thousand spans per second so we temporarily dropped the trace sampling rate down at five percent today i am updating the head based sampling configur in the collector daemon to discard health check traces and keep only error status five hundred spans my primary blocker is coordinat with the platform squad to verify that the collector buffer pool does not exhaust socket descriptors during the evening traffic peak",
        "refined_text": "Yesterday our team finished deploying the OpenTelemetry sidecars across 40 pods in the payment cluster. However, the Jaeger collector experienced severe memory pressure when ingest spiked at 12000 spans per second, so we temporarily dropped the trace sampling rate down at 5 percent.\n\nToday I am updating the head based sampling configuration in the collector daemon to discard health check traces and keep only error status 500 spans.\n\nMy primary blocker is coordinating with the platform squad to verify that the collector buffer pool does not exhaust socket descriptors during the evening traffic peak."
    },
    # Pair 12: Domain 2 - Daily Standups
    {
        "raw_asr": "uh yesterday our auth squad investigated intermittent logout reports from mobile clients during session renewal we discovered that token refresh requests were invalidat prematurely buy the redis cluster when key expiration occurred after three hundred seconds instead of the expected session window today ticket six hundred fourteen is assigned to me to increase the session store ttl at eighteen hundred seconds and implement atomic token rotat in the authentication service i am also adding structured debug logs around the refresh token validation path no hard blockers remain on my side today i need an asynchronous review buy the security team on our revised token revocat logic before we promote this release into the staging environment",
        "refined_text": "Yesterday our auth squad investigated intermittent logout reports from mobile clients during session renewal. We discovered that token refresh requests were invalidated prematurely by the Redis cluster when key expiration occurred after 300 seconds instead of the expected session window.\n\nToday ticket 614 is assigned to me to increase the session store TTL at 1800 seconds and implement atomic token rotation in the authentication service. I am also adding structured debug logs around the refresh token validation path.\n\nNo hard blockers remain on my side today. I need an asynchronous review by the security team on our revised token revocation logic before we promote this release into the staging environment."
    },
    # Pair 13: Domain 2 - Daily Standups
    {
        "raw_asr": "um yesterday we triaged a retry storm in our inventory gateway where downstream g r p c calls exhausted the worker thread pool across twelve instances wait sixteen instances spikes reached four thousand concurrent connection requests when upstream network latency degraded today i am adding exponential backoff with full jitter to the client interceptor and capping maximum retries at three attempts this stabiliz the dispatch queue during transient network blips uh my current blocker is waiting on the load testing cluster so we can simulate eight thousand requests per second and verify thread saturation metrics we also need signoff from the infrastructure lead on the thread pool limits",
        "refined_text": "Yesterday we triaged a retry storm in our inventory gateway where downstream gRPC calls exhausted the worker thread pool across 16 instances. Spikes reached 4000 concurrent connection requests when upstream network latency degraded.\n\nToday I am adding exponential backoff with full jitter to the client interceptor and capping maximum retries at 3 attempts. This stabilizes the dispatch queue during transient network blips.\n\nMy current blocker is waiting on the load testing cluster so we can simulate 8000 requests per second and verify thread saturation metrics. We also need signoff from the infrastructure lead on the thread pool limits."
    },
    # Pair 14: Domain 2 - Daily Standups
    {
        "raw_asr": "um yesterday during the coober netties ingress controller rollout across our production cluster we tracked intermittent status five zero two bad gateway responses on twenty four endpoints the core problem stemmed from short pod grace periods terminat connections before the proxy drained active keepalive sockets uh today i am adjusting the pre stop hook in the deployment manifest and setting the termination grace period at forty five seconds i will also deploy this patch across our canary environment to monitor status five zero two error counts under steady traffic my main blocker is coordinat with the networking team to inspect proxy connection metrics across cluster nodes we want to confirm that traffic draining completes cleanly before promoting the change",
        "refined_text": "Yesterday during the Kubernetes ingress controller rollout across our production cluster, we tracked intermittent status 502 bad gateway responses on 24 endpoints. The core problem stemmed from short pod grace periods terminating connections before the proxy drained active keepalive sockets.\n\nToday I am adjusting the pre stop hook in the deployment manifest and setting the termination grace period at 45 seconds. I will also deploy this patch across our canary environment to monitor status 502 error counts under steady traffic.\n\nMy main blocker is coordinating with the networking team to inspect proxy connection metrics across cluster nodes. We want to confirm that traffic draining completes cleanly before promoting the change."
    },
    # Pair 15: Domain 2 - Daily Standups
    {
        "raw_asr": "uh yesterday our search cluster entered red status after twelve shards became unassigned following a disk watermarks alert on data knowed five bulk indexing jobs stalled when write queues rejected incoming document batches today i am reallocat the unassigned primary shards manually and adjusting the index refresh interval at thirty seconds across the analytics indices this reduces disk write contention while the cluster finishes shard rebalancing um i am blocked on approval from the operations lead to temporarily double the heap allocation on three ingest nodes once approved we will resume bulk ingestion and clear the accumulated backlog across our queue",
        "refined_text": "Yesterday our search cluster entered red status after 12 shards became unassigned following a disk watermarks alert on data node 5. Bulk indexing jobs stalled when write queues rejected incoming document batches.\n\nToday I am reallocating the unassigned primary shards manually and adjusting the index refresh interval at 30 seconds across the analytics indices. This reduces disk write contention while the cluster finishes shard rebalancing.\n\nI am blocked on approval from the operations lead to temporarily double the heap allocation on 3 ingest nodes. Once approved, we will resume bulk ingestion and clear the accumulated backlog across our queue."
    },
    # Pair 16: Domain 3 - PR Code Reviews
    {
        "raw_asr": "um in pull request four hundred eighteen the proposed zero copy byte slice parser allocat a new backing array inside the tight packet decode loop when parsing high throughput streams exceeding ten thousand frames per second this triggers continuous garbage collection pauses that degrade tail latency uh please refactor the packet header parser to slice directly buy reading from the existing buffer view without reallocating underlying memory using a fixed sized scratch buffer of sixty four bytes on the stack avoids heap allocations during payload extract additionally please add a benchmark test asserting zero allocations per operation across the decode path we should verify throughput on one thousand sample packets before approving this diff",
        "refined_text": "In pull request 418, the proposed zero copy byte slice parser allocates a new backing array inside the tight packet decode loop. When parsing high throughput streams exceeding 10000 frames per second, this triggers continuous garbage collection pauses that degrade tail latency.\n\nPlease refactor the packet header parser to slice directly by reading from the existing buffer view without reallocating underlying memory. Using a fixed sized scratch buffer of 64 bytes on the stack avoids heap allocations during payload extraction.\n\nAdditionally, please add a benchmark test asserting zero allocations per operation across the decode path. We should verify throughput on 1000 sample packets before approving this diff."
    },
    # Pair 17: Domain 3 - PR Code Reviews
    {
        "raw_asr": "uh reviewing pull request five hundred twelve the lock free enqueue routine uses relaxed memory ordering on the tail pointer store under heavy concurrent contention with sixteen wait thirty two producer threads consumer threads observe stale knowed pointers and dereference uninitialized memory please change the compare and swap memory order from relaxed to release ordering on the tail pointer update and use acquire ordering on the queue head load this establishes a proper synchroniz with relationship between producer and consumer threads um furthermore the spin retry loop spins without thread pause instructions causing c p u core saturation during contention spikes please insert a c p u relax hint inside the retry loop after ten failed swap attempts",
        "refined_text": "Reviewing pull request 512, the lock free enqueue routine uses relaxed memory ordering on the tail pointer store. Under heavy concurrent contention with 32 producer threads, consumer threads observe stale node pointers and dereference uninitialized memory.\n\nPlease change the compare and swap memory order from relaxed to release ordering on the tail pointer update, and use acquire ordering on the queue head load. This establishes a proper synchronizes with relationship between producer and consumer threads.\n\nFurthermore, the spin retry loop spins without thread pause instructions, causing CPU core saturation during contention spikes. Please insert a CPU relax hint inside the retry loop after 10 failed swap attempts."
    },
    # Pair 18: Domain 3 - PR Code Reviews
    {
        "raw_asr": "um in pull request six hundred twenty eight the web socket session manager does not track ping and pong heartbeat acknowledgments from active client channels when clients disconnect ungracefully during network partition events stale connection objects remain pinned in the session hash map indefinitely uh please configure a read deadline of sixty seconds on the underlying t c p socket and update the ping handler to refresh connection timestamps on incoming pong packets dropping unacknowledged sockets after two consecutive missed heartbeats terminat dead connections promptly also please add a unit test simulating connection timeouts buy injecting synthetic socket read errors into the event loop we need to verify that connection counters drop back to zero",
        "refined_text": "In pull request 628, the WebSocket session manager does not track ping and pong heartbeat acknowledgments from active client channels. When clients disconnect ungracefully during network partition events, stale connection objects remain pinned in the session hash map indefinitely.\n\nPlease configure a read deadline of 60 seconds on the underlying TCP socket and update the ping handler to refresh connection timestamps on incoming pong packets. Dropping unacknowledged sockets after 2 consecutive missed heartbeats terminates dead connections promptly.\n\nAlso, please add a unit test simulating connection timeouts by injecting synthetic socket read errors into the event loop. We need to verify that connection counters drop back to 0."
    },
    # Pair 19: Domain 3 - PR Code Reviews
    {
        "raw_asr": "uh looking at pull request seven hundred thirty five the order fulfillment checkout transaction executes under read committed isolation concurrent order placement workflows can introduce phantom reads when two workers deduct stock from inventory rows simultaneously leading to negative quantity balances please elevate the transaction isolation level to serializable or acquire an explicit select for update right lock during inventory balance checks holding the right lock until transaction commit guarantees sequential deduct across competing customer orders um in addition please wrap the retry logic with exponential backoff when serialization conflict status four hundred nine occurs we should log serialized conflict counts across our telemetry dashboard",
        "refined_text": "Looking at pull request 735, the order fulfillment checkout transaction executes under read committed isolation. Concurrent order placement workflows can introduce phantom reads when two workers deduct stock from inventory rows simultaneously, leading to negative quantity balances.\n\nPlease elevate the transaction isolation level to serializable, or acquire an explicit select for update write lock during inventory balance checks. Holding the write lock until transaction commit guarantees sequential deduction across competing customer orders.\n\nIn addition, please wrap the retry logic with exponential backoff when serialization conflict status 409 occurs. We should log serialized conflict counts across our telemetry dashboard."
    },
    # Pair 20: Domain 3 - PR Code Reviews
    {
        "raw_asr": "um in pull request eight hundred forty the proposed h t t p request duration histogram registers raw user i d strings as a metric label in production with fifty thousand active users this unbounded label cardinality creates severe memory pressure on the telemetry collector agent uh please remove the user i d label from the histogram vector and group latency metrics buy h t t p route and status code instead keeping metric cardinality bounded under two hundred distinct series protects collector scrape endpoints from memory exhaustion additionally please check that histogram buckets align with standard latency distribut between ten milliseconds and five thousand milliseconds we should verify scraped metric payloads in the staging environment before merging",
        "refined_text": "In pull request 840, the proposed HTTP request duration histogram registers raw user ID strings as a metric label. In production with 50000 active users, this unbounded label cardinality creates severe memory pressure on the telemetry collector agent.\n\nPlease remove the user ID label from the histogram vector and group latency metrics by HTTP route and status code instead. Keeping metric cardinality bounded under 200 distinct series protects collector scrape endpoints from memory exhaustion.\n\nAdditionally, please check that histogram buckets align with standard latency distributions between 10 milliseconds and 5000 milliseconds. We should verify scraped metric payloads in the staging environment before merging."
    }
]

# Leakage check against sft_eval.json
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

print(f"Total pairs to test: {len(pairs)}")
assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, p in enumerate(pairs):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = validator.validate_pair(p)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_status = cleaner.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_status}"
    assert clean_status == "kept", f"Sample {idx+1} clean status was not 'kept': {clean_status}"

    # Tier analysis
    words = len(ref.split())
    if words < 25:
        tier_counts["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
    elif words < 90:
        tier_counts["medium"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
    else:
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

    print(f"Sample {idx+1:02d}: Tier={'Short' if words<25 else 'Medium' if words<90 else 'Long'}, Words={words}, Status=PASS")

print(f"\nFinal Tier Counts: {tier_counts}")
assert tier_counts["short"] == 4, f"Expected 4 short, got {tier_counts['short']}"
assert tier_counts["medium"] == 6, f"Expected 6 medium, got {tier_counts['medium']}"
assert tier_counts["long"] == 10, f"Expected 10 long, got {tier_counts['long']}"

batch_ok, batch_msg, batch_tiers = validator.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"validate_batch failed: {batch_msg}"
print(f"Batch validation result: {batch_msg}")

# Save verified output to target file
out_path = Path("scratch/subagent_batch_78.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(pairs)} verified pairs to {out_path}")
print("ALL DETERMINISTIC TESTS PASSED PERFECTLY!")
