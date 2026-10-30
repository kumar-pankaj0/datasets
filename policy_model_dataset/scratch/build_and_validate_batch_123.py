import json
import os
import re
import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Avoid dotted filenames and internal periods.
    # Avoid backticks.
    # =========================================================================

    # Sample 1: Domain 3 (PR Code Review) - Atomic pointer CAS loop
    {
        "raw_asr": "um advis the contributor two replac heavy mutex locks buy using atomic compare and swap across eight buffer slots",
        "refined_text": "Advise the contributor to replace heavy mutex locks by using atomic compare and swap across 8 buffer slots."
    },

    # Sample 2: Domain 3 (PR Code Review) - SQL connection timeout configuration
    {
        "raw_asr": "uh instruct the author two configur connection idle timeouts buy setting max lifetime at thirty minutes",
        "refined_text": "Instruct the author to configure connection idle timeouts by setting max lifetime at 30 minutes."
    },

    # Sample 3: Domain 5 (Technical Mentoring) - Semaphore concurrency throttling
    {
        "raw_asr": "basically guid the mentee two restrict concurrent background tasks buy wrapping worker dispatch inside a semaphore with four permits",
        "refined_text": "Guide the mentee to restrict concurrent background tasks by wrapping worker dispatch inside a semaphore with 4 permits."
    },

    # Sample 4: Domain 5 (Technical Mentoring) - Exponential backoff jitter
    {
        "raw_asr": "um teach the apprentice two decorrelat retry spikes buy adding full jitter across five retry attempts",
        "refined_text": "Teach the apprentice to decorrelate retry spikes by adding full jitter across 5 retry attempts."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Avoid backticks.
    # =========================================================================

    # Sample 5: Domain 3 (PR Code Review) - Go slice memory leak
    {
        "raw_asr": "in buffer underscore parser dot py the pull request leaks memory buy keeping large backing arrays inside small sub slices wait copy the slice elements buy allocating a fresh buffer across thirty two bytes instead um right three unit tests validating that garbage collection reclaims unused heap memory",
        "refined_text": "In buffer_parser.py, the pull request leaks memory by keeping large backing arrays inside small sub slices, copying the slice elements by allocating a fresh buffer across 32 bytes instead.\n\nWrite 3 unit tests validating that garbage collection reclaims unused heap memory."
    },

    # Sample 6: Domain 3 (PR Code Review) - SQL transaction isolation level
    {
        "raw_asr": "the proposed ledger update in billing underscore ledger dot py uses read committed isolation which permits phantom reads during balance recalculat wait elevat the transaction isolation level towards serializable isolation instead um right two integration tests verifying that concurrent balance debits abort with retryable serialization errors",
        "refined_text": "The proposed ledger update in billing_ledger.py uses read committed isolation which permits phantom reads during balance recalculation, elevating the transaction isolation level towards serializable isolation instead.\n\nWrite 2 integration tests verifying that concurrent balance debits abort with retryable serialization errors."
    },

    # Sample 7: Domain 3 (PR Code Review) - Rust request router lifetime annotation
    {
        "raw_asr": "reviewing request underscore router dot py shows excessive string cloning inside the dispatch handler buy copying header keys on every incoming request wait pass borrowed string slices buy annotating the request struct with explicit lifetimes instead uh right four performance benchmarks demonstrating zero heap allocations across sixty sample requests",
        "refined_text": "Reviewing request_router.py shows excessive string cloning inside the dispatch handler by copying header keys on every incoming request, passing borrowed string slices by annotating the request struct with explicit lifetimes instead.\n\nWrite 4 performance benchmarks demonstrating 0 heap allocations across 60 sample requests."
    },

    # Sample 8: Domain 5 (Technical Mentoring) - Idempotent consumer message deduplication
    {
        "raw_asr": "mentor the junior engineer on event deduplicat inside consumer underscore service dot py buy persisting incoming message uuid keys inside redis with a twelve hour expiry wait reject duplicate events buy checking key presence before executing the business logic instead um right three test cases validating that retransmitted messages produce zero side effects",
        "refined_text": "Mentor the junior engineer on event deduplication inside consumer_service.py by persisting incoming message UUID keys inside Redis with a 12 hour expiry, rejecting duplicate events by checking key presence before executing the business logic instead.\n\nWrite 3 test cases validating that retransmitted messages produce 0 side effects."
    },

    # Sample 9: Domain 5 (Technical Mentoring) - Write-through caching vs cache-aside
    {
        "raw_asr": "explain two the new team member how stale cache entries occur during high write throughput inside catalog underscore cache dot py buy failing two invalidate cache keys after product updates wait replac cache aside buy implementing write through caching across four inventory nodes instead uh right two unit tests confirming that updated prices reflect immediately across all cache reads",
        "refined_text": "Explain to the new team member how stale cache entries occur during high write throughput inside catalog_cache.py by failing to invalidate cache keys after product updates, replacing cache aside by implementing write through caching across 4 inventory nodes instead.\n\nWrite 2 unit tests confirming that updated prices reflect immediately across all cache reads."
    },

    # Sample 10: Domain 5 (Technical Mentoring) - Graceful shutdown and socket draining
    {
        "raw_asr": "walk the mentee through graceful shutdown handling inside server underscore runner dot py buy catching sig term signals and waiting twenty seconds while active requests finish wait drain incoming connection sockets buy closing listeners before terminating worker routines instead um right three unit tests verifying that pending requests finish without connection resets",
        "refined_text": "Walk the mentee through graceful shutdown handling inside server_runner.py by catching SIGTERM signals and waiting 20 seconds while active requests finish, draining incoming connection sockets by closing listeners before terminating worker routines instead.\n\nWrite 3 unit tests verifying that pending requests finish without connection resets."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2-3 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Avoid backticks.
    # =========================================================================

    # Sample 11: Domain 3 (PR Code Review) - Distributed lock lease renewal
    {
        "raw_asr": "in this pull request the distributed lock implement inside lock underscore manager dot py uses a fixed thirty second lease duration without automatic renewal buy inspecting production traces we observed that batch processing jobs frequently take ninety seconds which allows redis lock keys two expire while the job is still mutating records this flaw permits concurrent workers two acquire the same lock buy causing data corruption across five hundred accounts wait refactor the lock client buy launching a background heartbeat routine that renews the lease key every ten seconds while the worker context remains active instead um the review also highlights that the release method lacks ownership verificat which allows a delayed worker two delete a lock acquired buy another node advise the contributor two execute a lua script comparing the lock token before deleting the key finally right four concurrency tests inside lock underscore test dot py simulating ten slow workers buy verifying that lease renewal maintains mutual exclusion across one hundred twenty seconds without unexpected lock releases",
        "refined_text": "In this pull request, the distributed lock implementation inside lock_manager.py uses a fixed 30 second lease duration without automatic renewal. By inspecting production traces, we observed that batch processing jobs frequently take 90 seconds, which allows Redis lock keys to expire while the job is still mutating records. This flaw permits concurrent workers to acquire the same lock by causing data corruption across 500 accounts, refactoring the lock client by launching a background heartbeat routine that renews the lease key every 10 seconds while the worker context remains active instead.\n\nThe review also highlights that the release method lacks ownership verification, which allows a delayed worker to delete a lock acquired by another node. Advise the contributor to execute a Lua script comparing the lock token before deleting the key.\n\nFinally, write 4 concurrency tests inside lock_test.py simulating 10 slow workers by verifying that lease renewal maintains mutual exclusion across 120 seconds without unexpected lock releases."
    },

    # Sample 12: Domain 3 (PR Code Review) - Database deadlocks in batch settlement
    {
        "raw_asr": "the pull request in settlement underscore processor dot py causes frequent database deadlocks during batch payment execution buy locking invoice rows in arbitrary hash table iteration order when twelve concurrent worker threads process overlapping customer invoices post gres detects circular lock dependencies buy aborting up through forty transactions every hour wait sort incoming invoice identifiers in ascending numerical sequence before acquiring row level locks instead um furthermore the transaction boundary wraps external credit card gateway calls which holds database locks open across three seconds during each external network request tell the author two move credit card charging outside the database transaction buy acquiring row locks only during final ledger balance updates lastly right five integration tests inside settlement underscore test dot py executing twenty concurrent settlement batches buy verifying that zero deadlock errors occur across one thousand processed invoices",
        "refined_text": "The pull request in settlement_processor.py causes frequent database deadlocks during batch payment execution by locking invoice rows in arbitrary hash table iteration order. When 12 concurrent worker threads process overlapping customer invoices, Postgres detects circular lock dependencies by aborting up through 40 transactions every hour, sorting incoming invoice identifiers in ascending numerical sequence before acquiring row level locks instead.\n\nFurthermore, the transaction boundary wraps external credit card gateway calls, which holds database locks open across 3 seconds during each external network request. Tell the author to move credit card charging outside the database transaction by acquiring row locks only during final ledger balance updates.\n\nLastly, write 5 integration tests inside settlement_test.py executing 20 concurrent settlement batches by verifying that 0 deadlock errors occur across 1000 processed invoices."
    },

    # Sample 13: Domain 3 (PR Code Review) - Bounded channels and backpressure
    {
        "raw_asr": "reviewing metrics underscore pipeline dot py reveals a severe memory consumption defect buy buffering incoming telemetry records inside an unbounded channel without backpressure when the consumer pipeline stalls during network blips memory footprints spike from two hundred megabytes up through eight gigabytes within five minutes causing kernel out of memory kills wait replac the unbounded channel buy establishing a bounded ring buffer sized at sixteen thousand slots with explicit drop on full policies instead um the author should also add drop counter telemetry buy recording discarded metrics when the buffer saturates instruct the developer two expose a dropped events counter metric across prometheus monitoring endpoints finally right four load tests inside metrics underscore test dot py injecting fifty thousand events per second buy confirming that memory consumption stabilizes below four hundred megabytes while dropped count metrics increment accurately",
        "refined_text": "Reviewing metrics_pipeline.py reveals a severe memory consumption defect by buffering incoming telemetry records inside an unbounded channel without backpressure. When the consumer pipeline stalls during network blips, memory footprints spike from 200 megabytes up through 8 gigabytes within 5 minutes, causing kernel out of memory kills, replacing the unbounded channel by establishing a bounded ring buffer sized at 16000 slots with explicit drop on full policies instead.\n\nThe author should also add drop counter telemetry by recording discarded metrics when the buffer saturates. Instruct the developer to expose a dropped events counter metric across Prometheus monitoring endpoints.\n\nFinally, write 4 load tests inside metrics_test.py injecting 50000 events per second by confirming that memory consumption stabilizes below 400 megabytes while dropped count metrics increment accurately."
    },

    # Sample 14: Domain 3 (PR Code Review) - Constant-time cryptographic token verification
    {
        "raw_asr": "the pull request in auth underscore validator dot py introduces a critical security vulnerability buy comparing secret session tokens using standard string equality operators standard string comparisons return false upon the first mismatching byte which leaks token prefixes two attackers buy measuring microsecond timing variations across twenty network probes wait replac standard equality checks buy using constant time comparison functions like crypto dot subtle dot constant time compare instead um additionally the author omitted signature length verificat which allows empty signature strings two trigger unexpected zero length comparison matches tell the contributor two validate that incoming signatures match exactly thirty two bytes before executing the constant time check lastly right three security test cases inside auth underscore test dot py testing fifty valid and fifty invalid signatures buy confirming uniform response latencies without timing discrepancies",
        "refined_text": "The pull request in auth_validator.py introduces a critical security vulnerability by comparing secret session tokens using standard string equality operators. Standard string comparisons return false upon the first mismatching byte, which leaks token prefixes to attackers by measuring microsecond timing variations across 20 network probes, replacing standard equality checks by using constant time comparison functions like crypto.subtle.constant_time_compare instead.\n\nAdditionally, the author omitted signature length verification, which allows empty signature strings to trigger unexpected 0 length comparison matches. Tell the contributor to validate that incoming signatures match exactly 32 bytes before executing the constant time check.\n\nLastly, write 3 security test cases inside auth_test.py testing 50 valid and 50 invalid signatures by confirming uniform response latencies without timing discrepancies."
    },

    # Sample 15: Domain 3 (PR Code Review) - Connection pool starvation in gateway client
    {
        "raw_asr": "in gateway underscore client dot py the author implemented an http client using default connection settings without explicit socket timeouts when the upstream billing partner experienced network latency twenty concurrent worker threads blocked indefinitely on socket reads buy exhausting the thread pool across eighty server workers and failing health check probes wait configur explicit connection timeouts buy setting connect timeout at two seconds and read timeout at five seconds instead um the code also creates a fresh transport adapter on each outbound request buy leaking open sockets under high load advise the developer two reuse a single shared client session with a connection pool capped at sixty four connections finally right four stress tests inside gateway underscore test dot py simulating slow upstream responses buy confirming that client requests abort cleanly upon timeout expiration without thread pool starvation",
        "refined_text": "In gateway_client.py, the author implemented an HTTP client using default connection settings without explicit socket timeouts. When the upstream billing partner experienced network latency, 20 concurrent worker threads blocked indefinitely on socket reads by exhausting the thread pool across 80 server workers and failing health check probes, configuring explicit connection timeouts by setting connect timeout at 2 seconds and read timeout at 5 seconds instead.\n\nThe code also creates a fresh transport adapter on each outbound request by leaking open sockets under high load. Advise the developer to reuse a single shared client session with a connection pool capped at 64 connections.\n\nFinally, write 4 stress tests inside gateway_test.py simulating slow upstream responses by confirming that client requests abort cleanly upon timeout expiration without thread pool starvation."
    },

    # Sample 16: Domain 5 (Technical Mentoring) - LSM-Tree compaction mechanics
    {
        "raw_asr": "mentor the new systems engineer on l s m tree storage mechanics inside storage underscore engine dot py buy explaining how memtables flush immutable s s tables down into level zero storage when write throughput spikes frequent flushes create twelve level zero files which triggers aggressive compaction runs buy amplifying disk right operations across sixty megabytes per second wait instruct the mentee two tune the level zero compaction trigger buy raising write buffer capacity up through sixty four megabytes instead um walk through read amplification trade offs buy showing how point lookups must search multiple bloom filters when s s tables accumulate instruct the apprentice two configure block cache sizing at five hundred twelve megabytes buy caching hot data blocks lastly right three benchmark scripts inside storage underscore benchmark dot py measuring write amplification ratios across one hundred thousand sequential writes buy validating that write throughput remains stable",
        "refined_text": "Mentor the new systems engineer on LSM-tree storage mechanics inside storage_engine.py by explaining how memtables flush immutable SSTables down into level 0 storage. When write throughput spikes, frequent flushes create 12 level 0 files, which triggers aggressive compaction runs by amplifying disk write operations across 60 megabytes per second, instructing the mentee to tune the level 0 compaction trigger by raising write buffer capacity up through 64 megabytes instead.\n\nWalk through read amplification trade-offs by showing how point lookups must search multiple bloom filters when SSTables accumulate. Instruct the apprentice to configure block cache sizing at 512 megabytes by caching hot data blocks.\n\nLastly, write 3 benchmark scripts inside storage_benchmark.py measuring write amplification ratios across 100000 sequential writes by validating that write throughput remains stable."
    },

    # Sample 17: Domain 5 (Technical Mentoring) - Circuit breaker state transitions
    {
        "raw_asr": "teach the mentee how circuit breakers protect downstream services inside circuit underscore breaker dot py buy walking through state transitions between closed open and half open states when error rates exceed fifty percent across a rolling window of one hundred requests the breaker trips open buy rejecting incoming traffic immediately without invoking downstream endpoints wait demonstrate the recovery cycle buy holding the breaker in open state during thirty seconds before permitting three probe requests into the half open state instead um explain how consecutive successful responses transition the breaker back into normal closed operat advise the engineer two configure fallback handlers buy returning cached responses during open states finally right four unit tests inside circuit underscore test dot py simulating twenty consecutive network errors followed buy five successful probes buy verifying clean state transitions without request drops",
        "refined_text": "Teach the mentee how circuit breakers protect downstream services inside circuit_breaker.py by walking through state transitions between closed, open, and half open states. When error rates exceed 50 percent across a rolling window of 100 requests, the breaker trips open by rejecting incoming traffic immediately without invoking downstream endpoints, demonstrating the recovery cycle by holding the breaker in open state during 30 seconds before permitting 3 probe requests into the half open state instead.\n\nExplain how consecutive successful responses transition the breaker back into normal closed operation. Advise the engineer to configure fallback handlers by returning cached responses during open states.\n\nFinally, write 4 unit tests inside circuit_test.py simulating 20 consecutive network errors followed by 5 successful probes by verifying clean state transitions without request drops."
    },

    # Sample 18: Domain 5 (Technical Mentoring) - Optimistic concurrency control (OCC)
    {
        "raw_asr": "guide the apprentice through optimistic concurrency control inside document underscore repository dot py buy demonstrating how version counters prevent lost updates without pessimistic row locks each document record maintains an integer version stamp which increments upon every mutation when two concurrent sessions update the same document post gres checks that the version matches the read state buy aborting the second transaction when version numbers diverge wait instruct the mentee two wrap update mutations inside a retry loop buy attempting re read and re apply logic up through five attempts instead um explain how exponential backoff jitter decorrelates retry storms across thirty concurrent workers advise the developer two record collision rate metrics buy monitoring optimistic lock contention lastly right four integration tests inside document underscore test dot py launching ten parallel writers against five shared documents buy verifying that all updates commit successfully without lost updates",
        "refined_text": "Guide the apprentice through optimistic concurrency control inside document_repository.py by demonstrating how version counters prevent lost updates without pessimistic row locks. Each document record maintains an integer version stamp which increments upon every mutation. When 2 concurrent sessions update the same document, Postgres checks that the version matches the read state by aborting the second transaction when version numbers diverge, instructing the mentee to wrap update mutations inside a retry loop by attempting re-read and re-apply logic up through 5 attempts instead.\n\nExplain how exponential backoff jitter decorrelates retry storms across 30 concurrent workers. Advise the developer to record collision rate metrics by monitoring optimistic lock contention.\n\nLastly, write 4 integration tests inside document_test.py launching 10 parallel writers against 5 shared documents by verifying that all updates commit successfully without lost updates."
    },

    # Sample 19: Domain 5 (Technical Mentoring) - Kafka cooperative sticky assignor
    {
        "raw_asr": "mentor the junior platform developer on kafka partition rebalancing mechanics inside stream underscore consumer dot py buy explaining why the default eager partition assignor causes consumer lag spikes during rolling restarts eager assignors revoke all sixteen partitions simultaneously buy halting event processing across forty worker instances during twenty seconds wait show the mentee how two configure the cooperative sticky assignor buy enabling incremental partition reassignment without stopping untouched consumers instead um explain how cooperative rebalancing preserves partition state and reduces rebalance durations down from fifteen seconds down into two seconds instruct the engineer two tune max poll interval ms buy preventing false consumer evictions lastly right three simulation tests inside stream underscore test dot py triggering rolling node restarts across eight consumers buy confirming that message throughput sustains ten thousand events per second without complete consumer stalls",
        "refined_text": "Mentor the junior platform developer on Kafka partition rebalancing mechanics inside stream_consumer.py by explaining why the default eager partition assignor causes consumer lag spikes during rolling restarts. Eager assignors revoke all 16 partitions simultaneously by halting event processing across 40 worker instances during 20 seconds, showing the mentee how to configure the cooperative sticky assignor by enabling incremental partition reassignment without stopping untouched consumers instead.\n\nExplain how cooperative rebalancing preserves partition state and reduces rebalance durations down from 15 seconds down into 2 seconds. Instruct the engineer to tune max poll interval ms by preventing false consumer evictions.\n\nLastly, write 3 simulation tests inside stream_test.py triggering rolling node restarts across 8 consumers by confirming that message throughput sustains 10000 events per second without complete consumer stalls."
    },

    # Sample 20: Domain 5 (Technical Mentoring) - Raft consensus log compaction
    {
        "raw_asr": "walk the distributed systems apprentice through raft consensus log compaction inside consensus underscore node dot py buy explaining how unbounded append only logs consume disk storage and prolong node recovery times when log entries exceed sixty four thousand records the state machine serializes a consistent memory snapshot down into disk buy truncating committed log entries up through index thirty two thousand wait teach the mentee how two stream snapshot chunks towards lagging follower nodes buy using chunked r p c calls when follower indices lag behind the compaction boundary instead um discuss how snapshot install handlers atomical replac follower state while resetting match index pointers advise the engineer two configure snapshot compaction thresholds buy monitoring disk utilization lastly right four verification tests inside consensus underscore test dot py simulating three lagging followers buy validating that snapshot streaming restores cluster consensus across five hundred client requests",
        "refined_text": "Walk the distributed systems apprentice through Raft consensus log compaction inside consensus_node.py by explaining how unbounded append only logs consume disk storage and prolong node recovery times. When log entries exceed 64000 records, the state machine serializes a consistent memory snapshot down into disk by truncating committed log entries up through index 32000, teaching the mentee how to stream snapshot chunks towards lagging follower nodes by using chunked RPC calls when follower indices lag behind the compaction boundary instead.\n\nDiscuss how snapshot install handlers atomically replace follower state while resetting match index pointers. Advise the engineer to configure snapshot compaction thresholds by monitoring disk utilization.\n\nLastly, write 4 verification tests inside consensus_test.py simulating 3 lagging followers by validating that snapshot streaming restores cluster consensus across 500 client requests."
    },
]

print(f"Total samples: {len(batch)}")

# 1. Check leakage against eval set
leak_count = 0
for idx, s in enumerate(batch):
    raw = s["raw_asr"].strip().lower()
    ref = s["refined_text"].strip()
    if raw in eval_raws:
        print(f"LEAK ERROR: sample {idx+1} raw_asr found in eval set!")
        leak_count += 1
    if ref in eval_refs:
        print(f"LEAK ERROR: sample {idx+1} refined_text found in eval set!")
        leak_count += 1
if leak_count == 0:
    print("Zero eval leakage confirmed.")

# 2. Check validate_pair & clean_sample
all_valid = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, s in enumerate(batch):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    
    if words < 25:
        tier = "short"
    elif words < 90:
        tier = "medium"
    else:
        tier = "long"
    tier_counts[tier] += 1

    valid, reason = validate_pair(s)
    if not valid:
        print(f"FAILED validate_pair on sample {idx+1} ({tier}, {words}w): {reason}")
        all_valid = False

    cleaned, status = clean_sample(raw, ref)
    if status != "kept":
        print(f"FAILED clean_sample on sample {idx+1} ({tier}, {words}w): {status}")
        all_valid = False

print(f"Tier counts: {tier_counts}")

# 3. Check validate_batch
batch_valid, batch_reason, batch_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
print(f"validate_batch: valid={batch_valid}, reason={batch_reason}, tiers={batch_tiers}")

if all_valid and batch_valid and leak_count == 0:
    out_path = Path("scratch/subagent_batch_123.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(batch)} samples to {out_path}")
else:
    print("Validation failed. Please review errors.")
    sys.exit(1)
