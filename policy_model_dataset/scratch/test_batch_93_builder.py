import json
import re
import sys
import os
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

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Avoid dotted filenames and internal periods.
    # Avoid backticks.
    # =========================================================================

    # Sample 1: Domain 3 (PR Code Review) - Hash set lookup optimization
    {
        "raw_asr": "um instruct the contributor two replac linear array scans buy using a hash set with sixteen preallocated buckets",
        "refined_text": "Instruct the contributor to replace linear array scans by using a hash set with 16 preallocated buckets."
    },

    # Sample 2: Domain 3 (PR Code Review) - Mutex lock scope narrowing
    {
        "raw_asr": "uh tell the author two narrow the critical section buy moving buffer serializat outside the mutex lock",
        "refined_text": "Tell the author to narrow the critical section by moving buffer serialization outside the mutex lock."
    },

    # Sample 3: Domain 5 (Technical Mentoring) - Connection pool sizing
    {
        "raw_asr": "basically advis the mentee two limit database connection pool size buy setting max open connections at thirty two",
        "refined_text": "Advise the mentee to limit database connection pool size by setting max open connections at 32."
    },

    # Sample 4: Domain 5 (Technical Mentoring) - Context cancellation signal
    {
        "raw_asr": "um guid the apprentice two coordinat worker termination buy passing a context cancellation signal across eight concurrent tasks",
        "refined_text": "Guide the apprentice to coordinate worker termination by passing a context cancellation signal across 8 concurrent tasks."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Avoid backticks.
    # =========================================================================

    # Sample 5: Domain 3 (PR Code Review) - N+1 query batch preload
    {
        "raw_asr": "the pull request introduces an n plus one query defect inside account underscore repository dot py buy fetching billing profiles individually within a loop over user records wait replac the single row queries buy using a batch preload query spanning one hundred accounts instead um right three pie test assertions confirming that database round trips drop down into two query executions",
        "refined_text": "The pull request introduces an N plus 1 query defect inside account_repository.py by fetching billing profiles individually within a loop over user records, replacing the single-row queries by using a batch preload query spanning 100 accounts instead.\n\nWrite 3 pytest assertions confirming that database round trips drop down into 2 query executions."
    },

    # Sample 6: Domain 3 (PR Code Review) - HTTP response body leak
    {
        "raw_asr": "reviewing client underscore transport dot py shows unclosed http response payloads during non two zero zero responses buy failing two read and close the response stream under error conditions wait wrap the response handling inside a try finally block buy invoking stream close upon every request outcome instead um right two unit tests validating that active socket counts remain constant across fifty failed requests",
        "refined_text": "Reviewing client_transport.py shows unclosed HTTP response payloads during non 200 responses by failing to read and close the response stream under error conditions, wrapping the response handling inside a try finally block by invoking stream close upon every request outcome instead.\n\nWrite 2 unit tests validating that active socket counts remain constant across 50 failed requests."
    },

    # Sample 7: Domain 3 (PR Code Review) - Interface segregation decoupling
    {
        "raw_asr": "the service client interface in storage underscore service dot py violates the interface segregat principle buy combining object upload methods with tenant credential rotat methods in one monolithic class wait segregat the contract into independent storage reader and credential manager interfaces instead um this change allows downstream mock implement across sixteen unit tests without stubbing unused auth methods",
        "refined_text": "The service client interface in storage_service.py violates the interface segregation principle by combining object upload methods with tenant credential rotation methods in one monolithic class, segregating the contract into independent storage reader and credential manager interfaces instead.\n\nThis change allows downstream mock implementation across 16 unit tests without stubbing unused auth methods."
    },

    # Sample 8: Domain 5 (Technical Mentoring) - Replication lag & primary routing
    {
        "raw_asr": "basically explain two the mentee how asynchronous database replication causes read after right inconsistencies when querying post gres read replicas immediately following user profile updates wait instruct the engineer two route critical read requests towards the primary database instance four sixty seconds following any mutation instead um right two verification tests checking that updated user metadata displays without replication lag",
        "refined_text": "Explain to the mentee how asynchronous database replication causes read-after-write inconsistencies when querying Postgres read replicas immediately following user profile updates, instructing the engineer to route critical read requests towards the primary database instance for 60 seconds following any mutation instead.\n\nWrite 2 verification tests checking that updated user metadata displays without replication lag."
    },

    # Sample 9: Domain 5 (Technical Mentoring) - Trace context propagation
    {
        "raw_asr": "walk the junior developer through trace context propagat inside telemetry underscore handler dot py buy injecting w three c traceparent headers into outgoing amqp message attributes wait extract the trace identifiers inside the consumer pipeline before processing each message instead um right three integration tests confirming that distributed span trees link parent and child spans across four microservices",
        "refined_text": "Walk the junior developer through trace context propagation inside telemetry_handler.py by injecting W3C traceparent headers into outgoing AMQP message attributes, extracting the trace identifiers inside the consumer pipeline before processing each message instead.\n\nWrite 3 integration tests confirming that distributed span trees link parent and child spans across 4 microservices."
    },

    # Sample 10: Domain 5 (Technical Mentoring) - Lock acquisition hierarchy
    {
        "raw_asr": "mentor the new engineer on lock acquisit hierarchies inside account underscore transfer dot py buy enforcing a strict lexicographical ordering on account lock identifiers wait acquire locks in ascending order buy comparing account keys before starting the balance transfer instead um verify that twenty concurrent transfer operations execute without encountering circular deadlock conditions",
        "refined_text": "Mentor the new engineer on lock acquisition hierarchies inside account_transfer.py by enforcing a strict lexicographical ordering on account lock identifiers, acquiring locks in ascending order by comparing account keys before starting the balance transfer instead.\n\nVerify that 20 concurrent transfer operations execute without encountering circular deadlock conditions."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph separated by \n\n (2-3 solid paragraphs). Max \n\n: words // 25.
    # Natural spoken engineer narration. Zero numbered checklist stereotypes.
    # Avoid backticks.
    # =========================================================================

    # Sample 11: Domain 3 (PR Code Review) - Serialization memory allocations
    {
        "raw_asr": "in this pull request the batch export serializer inside export underscore pipeline dot py allocates temporary byte buffers inside the tight record iteration loop buy inspecting memory profiles we observed over four hundred megabytes of heap garbage generated during a single export run of ten thousand records wait refactor the serialization loop buy reusing a sync dot pool buffer across worker iterations instead um the pull request also misses buffer bounds checking when appending serialized fields which causes unexpected slice reallocation when row sizes exceed two zero four eight bytes tell the author two preallocate the destination slice capacity based on the average record length from previous batches finally right four benchmark tests inside export underscore benchmark dot py comparing allocations per operation before and after the change verify that heap allocations drop down from sixteen thousand allocations down into two hundred allocations across eight parallel export routines",
        "refined_text": "In this pull request, the batch export serializer inside export_pipeline.py allocates temporary byte buffers inside the tight record iteration loop. By inspecting memory profiles, we observed over 400 megabytes of heap garbage generated during a single export run of 10000 records, refactoring the serialization loop by reusing a sync.Pool buffer across worker iterations instead.\n\nThe pull request also misses buffer bounds checking when appending serialized fields, which causes unexpected slice reallocation when row sizes exceed 2048 bytes. Tell the author to preallocate the destination slice capacity based on the average record length from previous batches.\n\nFinally, write 4 benchmark tests inside export_benchmark.py comparing allocations per operation before and after the change. Verify that heap allocations drop down from 16000 allocations down into 200 allocations across 8 parallel export routines."
    },

    # Sample 12: Domain 3 (PR Code Review) - LRU cache eviction concurrency
    {
        "raw_asr": "reviewing the cache eviction logic in cache underscore manager dot py reveals a data race when multiple worker threads execute eviction under memory pressure the author used a standard double linked list without synchronizat when fifty concurrent workers call evict simultaneously node pointers become corrupted buy causing nil pointer dereferences during tail lookup wait replac the shared doubly linked list buy wrapping the eviction queue inside an r w mutex lock with fine grained segment partitioning instead um in addition the cache eviction worker holds the exclusive write lock while performing synchronous disk flushes which blocks cache read hits across one thousand application clients advise the contributor two separate the in memory eviction from background disk write operat buy pushing evicted entries into a buffered channel finally right five pie test concurrency tests inside cache underscore test dot py simulating sixty concurrent readers and twenty writers verify that cache throughput sustains forty thousand operations per second without deadlocks or pointer corruption",
        "refined_text": "Reviewing the cache eviction logic in cache_manager.py reveals a data race when multiple worker threads execute eviction under memory pressure. The author used a standard double linked list without synchronization, where when 50 concurrent workers call evict simultaneously, node pointers become corrupted by causing nil pointer dereferences during tail lookup, replacing the shared doubly linked list by wrapping the eviction queue inside an RW Mutex lock with fine-grained segment partitioning instead.\n\nIn addition, the cache eviction worker holds the exclusive write lock while performing synchronous disk flushes, which blocks cache read hits across 1000 application clients. Advise the contributor to separate the in-memory eviction from background disk write operation by pushing evicted entries into a buffered channel.\n\nFinally, write 5 pytest concurrency tests inside cache_test.py simulating 60 concurrent readers and 20 writers. Verify that cache throughput sustains 40000 operations per second without deadlocks or pointer corruption."
    },

    # Sample 13: Domain 3 (PR Code Review) - Database migration index lock
    {
        "raw_asr": "the database migration script in migration underscore v four dot py adds an unindexed foreign key column on the orders table with an immediate default value constraint this migration acquires an exclusive access exclusive lock on a table containing three million rows which blocks incoming customer transactions and exhausts connection pool capacity across thirty web application nodes wait tell the developer two drop the immediate default constraint and add the column as nullable instead um we also need two address the index creation step because the current script calls create index directly on the active transaction table instruct the author two execute create index concurrently inside a separate migration step buy setting commit transaction mode outside the main migration transaction lastly right four verification scripts checking that column backfill proceeds in chunks of two thousand records with fifty milliseconds pause between batches verify that replica lag remains under three seconds across four read replicas during migration execution",
        "refined_text": "The database migration script in migration_v4.py adds an unindexed foreign key column on the orders table with an immediate default value constraint. This migration acquires an exclusive access exclusive lock on a table containing 3000000 rows, which blocks incoming customer transactions and exhausts connection pool capacity across 30 web application nodes, telling the developer to drop the immediate default constraint and add the column as nullable instead.\n\nWe also need to address the index creation step because the current script calls create index directly on the active transaction table. Instruct the author to execute create index concurrently inside a separate migration step by setting commit transaction mode outside the main migration transaction.\n\nLastly, write 4 verification scripts checking that column backfill proceeds in chunks of 2000 records with 50 milliseconds pause between batches. Verify that replica lag remains under 3 seconds across 4 read replicas during migration execution."
    },

    # Sample 14: Domain 3 (PR Code Review) - gRPC backpressure handling
    {
        "raw_asr": "examining stream underscore server dot py in this pull request reveals an absence of backpressure handling during bulk telemetry streaming when downstream consumers slow down the g r p c server continues pushing message chunks into an unbounded in memory buffer which drives heap memory usage beyond eight gigabytes and triggers out of memory kills across twelve worker instances wait instruct the author two adopt flow control buy checking stream ready status before dispatching each telemetry frame instead um the pull request also sets the g r p c message receive size limit two sixty four megabytes without validating payload boundaries tell the contributor two restrict maximum message size two four megabytes and implement client side chunking across stream partitions finally right six pie test integration tests simulating high latency client receivers with ninety percent simulated packet loss verify that stream write operations pause when the client window fills and resume transmission when window credits arrive across sixteen concurrent streams",
        "refined_text": "Examining stream_server.py in this pull request reveals an absence of backpressure handling during bulk telemetry streaming. When downstream consumers slow down, the gRPC server continues pushing message chunks into an unbounded in-memory buffer, which drives heap memory usage beyond 8 gigabytes and triggers out-of-memory kills across 12 worker instances, instructing the author to adopt flow control by checking stream ready status before dispatching each telemetry frame instead.\n\nThe pull request also sets the gRPC message receive size limit to 64 megabytes without validating payload boundaries. Tell the contributor to restrict maximum message size to 4 megabytes and implement client-side chunking across stream partitions.\n\nFinally, write 6 pytest integration tests simulating high-latency client receivers with 90 percent simulated packet loss. Verify that stream write operations pause when the client window fills and resume transmission when window credits arrive across 16 concurrent streams."
    },

    # Sample 15: Domain 3 (PR Code Review) - Token bucket rate limiter precision
    {
        "raw_asr": "in this pull request the rate limiter implementation in limiter underscore service dot py exhibits token drift when calculating bucket refills the author computes elapsed time using wall clock seconds rather than a monotonic clock which allows n t p clock synchronizat adjustments two corrupt available token balances across twenty four gateway instances wait modify the time computation buy calling monotonic clock timestamps with nanosecond precision instead um furthermore the token refill function updates the bucket capacity and the last update timestamp in two separate operations without atomic synchronizat under concurrent traffic bursts forty parallel requests read stale token counts buy bypassing rate limiting thresholds advise the developer two combine token deduction inside an atomic compare and swap operat lastly right five unit tests validating that burst requests exceeding one hundred tokens receive http status four hundred twenty nine verify that bucket refill accurately restores twenty tokens per second without counter drift across ten test worker threads",
        "refined_text": "In this pull request, the rate limiter implementation in limiter_service.py exhibits token drift when calculating bucket refills. The author computes elapsed time using wall clock seconds rather than a monotonic clock, which allows NTP clock synchronization adjustments to corrupt available token balances across 24 gateway instances, modifying the time computation by calling monotonic clock timestamps with nanosecond precision instead.\n\nFurthermore, the token refill function updates the bucket capacity and the last update timestamp in two separate operations without atomic synchronization. Under concurrent traffic bursts, 40 parallel requests read stale token counts by bypassing rate limiting thresholds, advising the developer to combine token deduction inside an atomic compare-and-swap operation.\n\nLastly, write 5 unit tests validating that burst requests exceeding 100 tokens receive HTTP status 429. Verify that bucket refill accurately restores 20 tokens per second without counter drift across 10 test worker threads."
    },

    # Sample 16: Domain 5 (Technical Mentoring) - Kafka consumer group rebalances
    {
        "raw_asr": "during our architecture mentoring session i walked the junior engineer through resolving frequent consumer group rebalances inside consumer underscore worker dot py our message processing loop took longer than thirty seconds two process batches of five hundred telemetry records which triggered max poll interval timeouts and forced the coordinator two revoke partition assignments wait advise the mentee two reduce max poll records from five hundred down into one hundred records instead um we then discussed consumer offset commit strategies buy contrasting synchronous commits with asynchronous commits synchronous commits block the consumer loop upon every batch buy adding eighty milliseconds of latency whereas unconditional async commits risk duplicate processing during unexpected worker crashes pair with the engineer two implement asynchronous commits with a synchronous commit during graceful consumer shutdown finally right four unit tests validating that partition revocation listeners commit active offsets before reassignments take effect verify that consumer lag metrics remain below two hundred messages across thirty two partition consumers",
        "refined_text": "During our architecture mentoring session, I walked the junior engineer through resolving frequent consumer group rebalances inside consumer_worker.py. Our message processing loop took longer than 30 seconds to process batches of 500 telemetry records, which triggered max poll interval timeouts and forced the coordinator to revoke partition assignments, advising the mentee to reduce max poll records from 500 down into 100 records instead.\n\nWe then discussed consumer offset commit strategies by contrasting synchronous commits with asynchronous commits. Synchronous commits block the consumer loop upon every batch by adding 80 milliseconds of latency, whereas unconditional async commits risk duplicate processing during unexpected worker crashes, pairing with the engineer to implement asynchronous commits with a synchronous commit during graceful consumer shutdown.\n\nFinally, write 4 unit tests validating that partition revocation listeners commit active offsets before reassignments take effect. Verify that consumer lag metrics remain below 200 messages across 32 partition consumers."
    },

    # Sample 17: Domain 5 (Technical Mentoring) - Optimistic concurrency control
    {
        "raw_asr": "i paired with the backend mentee two diagnose database lock contention issues on our inventory reservation service inside inventory underscore service dot py our original checkout flow acquired pessimistic select for update row locks on product inventory rows which caused transaction lock queues two back up across fifty application workers when flash sales launched on popular items wait mentor the developer two replac pessimistic locks buy adopting optimistic concurrency control with an integer version column instead um we explored how optimistic locking eliminates blocking database locks buy checking the expected version number in the update predicate when concurrent checkout requests conflict only the first transaction commits while subsequent transactions detect the version mismatch and retry pair with the engineer two implement an exponential backoff retry loop with three attempts lastly right six pie test test cases verifying that fifty concurrent checkout requests decrement stock quantities accurately without overselling verify that failed transactions receive clear conflict errors when retry attempts exhaust across twenty simulated client threads",
        "refined_text": "I paired with the backend mentee to diagnose database lock contention issues on our inventory reservation service inside inventory_service.py. Our original checkout flow acquired pessimistic select for update row locks on product inventory rows, which caused transaction lock queues to back up across 50 application workers when flash sales launched on popular items, mentoring the developer to replace pessimistic locks by adopting optimistic concurrency control with an integer version column instead.\n\nWe explored how optimistic locking eliminates blocking database locks by checking the expected version number in the update predicate. When concurrent checkout requests conflict, only the first transaction commits while subsequent transactions detect the version mismatch and retry, pairing with the engineer to implement an exponential backoff retry loop with 3 attempts.\n\nLastly, write 6 pytest test cases verifying that 50 concurrent checkout requests decrement stock quantities accurately without overselling. Verify that failed transactions receive clear conflict errors when retry attempts exhaust across 20 simulated client threads."
    },

    # Sample 18: Domain 5 (Technical Mentoring) - LSM-tree vs B-tree storage
    {
        "raw_asr": "basically during a technical mentoring session i explained two the apprentice why our event logging service migrated from a traditional b tree relational database two an l s m tree based key value storage engine in b tree engines every row insert produces random disk i o operations and page splits which saturates disk write bandwidth when ingestion throughput exceeds ten thousand events per second wait explain how log structured merge trees sequentialize incoming writes inside an in memory memtable before flushing sorted s s table files two disk instead um we then discussed write amplification trade offs during compaction cycles buy examining how leveled compaction repeatedly rewrites data blocks two maintain sorted levels clarify how background compaction can consume sixty percent of disk i o bandwidth during sustained ingestion bursts and discuss tuning memtable buffer sizes towards sixty four megabytes finally right four benchmark validation tests simulating fifty thousand writes per second verify that write throughput remains stable and confirm that p ninety nine commit latencies stay below five milliseconds across sixteen storage worker threads",
        "refined_text": "During a technical mentoring session, I explained to the apprentice why our event logging service migrated from a traditional B-tree relational database to an LSM-tree based key-value storage engine. In B-tree engines, every row insert produces random disk I/O operations and page splits, which saturates disk write bandwidth when ingestion throughput exceeds 10000 events per second, explaining how log-structured merge trees sequentialize incoming writes inside an in-memory memtable before flushing sorted SSTable files to disk instead.\n\nWe then discussed write amplification trade-offs during compaction cycles by examining how leveled compaction repeatedly rewrites data blocks to maintain sorted levels. Clarify how background compaction can consume 60 percent of disk I/O bandwidth during sustained ingestion bursts, and discuss tuning memtable buffer sizes towards 64 megabytes.\n\nFinally, write 4 benchmark validation tests simulating 50000 writes per second. Verify that write throughput remains stable, and confirm that P99 commit latencies stay below 5 milliseconds across 16 storage worker threads."
    },

    # Sample 19: Domain 5 (Technical Mentoring) - Circuit breaker state transitions
    {
        "raw_asr": "i walked the junior platform engineer through implementing circuit breaker resilience patterns inside resilience underscore client dot py our microservice was repeatedly overloading a failing payment gateway buy sending continuous retry requests without backoff wait advise the mentee two track failure counts across a sliding window of sixty seconds buy transitioning the circuit state from closed into open when error rates exceed fifty percent instead um we reviewed the three circuit breaker states closed open and half open explain how the half open state probes downstream health buy permitting a canary batch of five test requests through towards the downstream service after a thirty second cooling duration if the canary requests succeed the circuit resets towards the closed state lastly right five unit test assertions verifying that requests fail fast with status five zero three during the open state verify that retry intervals incorporate random full jitter across ten concurrent worker clients",
        "refined_text": "I walked the junior platform engineer through implementing circuit breaker resilience patterns inside resilience_client.py. Our microservice was repeatedly overloading a failing payment gateway by sending continuous retry requests without backoff, advising the mentee to track failure counts across a sliding window of 60 seconds by transitioning the circuit state from closed into open when error rates exceed 50 percent instead.\n\nWe reviewed the three circuit breaker states: closed, open, and half open. Explain how the half open state probes downstream health by permitting a canary batch of 5 test requests through towards the downstream service after a 30 second cooling duration. If the canary requests succeed, the circuit resets towards the closed state.\n\nLastly, write 5 unit test assertions verifying that requests fail fast with status 503 during the open state. Verify that retry intervals incorporate random full jitter across 10 concurrent worker clients."
    },

    # Sample 20: Domain 5 (Technical Mentoring) - CQRS read projection consistency
    {
        "raw_asr": "basically during our system design mentoring session i paired with the data engineer two address out of order event delivery inside projection underscore worker dot py our c q r s read models displayed inconsistent state because network retransmissions caused event consumer instances two process order updated events prior two processing order created events wait instruct the engineer two attach a monotonically increasing sequence version number two every event payload instead um we drafted an idempotency check inside the projection consumer buy recording the highest processed sequence version in post gres table projection underscore offsets explain how discarding events with lower sequence versions prevents duplicate mutations and eliminates data corruption during consumer failover across eight worker partitions finally right six pie test integration tests verifying that duplicate and delayed event messages discard cleanly without throwing unhandled exceptions verify that the read projection model reaches eventual consistency across one thousand simulated events",
        "refined_text": "During our system design mentoring session, I paired with the data engineer to address out-of-order event delivery inside projection_worker.py. Our CQRS read models displayed inconsistent state because network retransmissions caused event consumer instances to process order updated events prior to processing order created events, instructing the engineer to attach a monotonically increasing sequence version number to every event payload instead.\n\nWe drafted an idempotency check inside the projection consumer by recording the highest processed sequence version in Postgres table projection_offsets. Explain how discarding events with lower sequence versions prevents duplicate mutations and eliminates data corruption during consumer failover across 8 worker partitions.\n\nFinally, write 6 pytest integration tests verifying that duplicate and delayed event messages discard cleanly without throwing unhandled exceptions. Verify that the read projection model reaches eventual consistency across 1000 simulated events."
    }
]

print(f"Total candidate samples: {len(samples)}")

all_passed = True
for idx, pair in enumerate(samples):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # Check leakage
    if raw.lower().strip() in eval_raws:
        print(f"Sample {idx+1} LEAKAGE ERROR: raw_asr found in sft_eval.json!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {idx+1} LEAKAGE ERROR: refined_text found in sft_eval.json!")
        all_passed = False

    # Validator check
    v_ok, v_reason = validate_pair(pair)
    if not v_ok:
        print(f"Sample {idx+1} VALIDATOR FAIL: {v_reason}")
        all_passed = False

    # Cleaner check
    c_res, c_status = clean_sample(raw, ref)
    if c_status != "kept":
        print(f"Sample {idx+1} CLEANER FAIL: {c_status}")
        all_passed = False

    words = len(ref.split())
    tier = "Short" if words < 25 else ("Medium" if words < 90 else "Long")
    print(f"Sample {idx+1:02d}: Tier={tier:<6} Words={words:<3} Valid={v_ok} Clean={c_status}")

# Batch validation
b_ok, b_reason, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: ok={b_ok}, reason='{b_reason}', tiers={b_tiers}")

if all_passed and b_ok:
    print("\nSUCCESS: All 20 samples passed all checks!")
    output_path = Path("scratch/subagent_batch_93.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"Saved verified dataset to {output_path}")
else:
    print("\nFAILURE: One or more checks failed.")
