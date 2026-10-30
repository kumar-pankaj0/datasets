import json
import re
import sys
from pathlib import Path

# Import validator and cleaner
sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

pairs = [
    # --- DOMAIN 3: CODE REVIEWS & PR DISCUSSIONS (Samples 1 - 10) ---
    # Sample 1 (Short < 25 words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "um please replac the raw pointer with an atomic reference buy using compare exchange weak instead",
        "refined_text": "Please replace the raw pointer with an atomic reference by using compare exchange weak instead."
    },
    # Sample 2 (Short < 25 words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "uh check the boundary index operat four off buy one errors when reading buffer capacity sixteen",
        "refined_text": "Check the boundary index operation for off-by-one errors when reading buffer capacity 16."
    },
    # Sample 3 (Medium 25 - 89 words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "in the payment service lock acquisition order causes a potential deadlock between account mutex and ledger mutex wait sort lock keys alphabetically before acquiring locks buy using key ordering two maintain consistent synchronizat across both transfer handlers",
        "refined_text": "In the payment service, lock acquisition order causes a potential deadlock between account mutex and ledger mutex.\n\nSort lock keys alphabetically before acquiring locks by using key ordering to maintain consistent synchronization across both transfer handlers."
    },
    # Sample 4 (Medium 25 - 89 words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "this nested iteration over user permissions introduces quadratic time complexity because each iteration triggers a linear search over role bindings buy replacing the inner loop with a hash set lookup you reduce time complexity two linear time post gres query logs already show latency spikes exceeding sixty four milliseconds four one thousand records",
        "refined_text": "This nested iteration over user permissions introduces quadratic time complexity because each iteration triggers a linear search over role bindings. By replacing the inner loop with a hash set lookup, you reduce time complexity to linear time.\n\nPostgres query logs already show latency spikes exceeding 64 milliseconds for 1000 records."
    },
    # Sample 5 (Medium 25 - 89 words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "the worker interface violates interface segregation buy coupling job execution with socket connection lifecycle terminat methods should move two a dedicated channel manager wait split the interface into runnable worker and channel closer so consumers do not depend on unused network methods",
        "refined_text": "The worker interface violates interface segregation by coupling job execution with socket connection lifecycle.\n\nTerminate methods should move to a dedicated channel manager. Split the interface into runnable worker and channel closer so consumers do not depend on unused network methods."
    },
    # Sample 6 (Long 90+ words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "okay so looking at pull request four eight two the websocket connection handler registers an event listener four incoming message frames on the global event bus but never unregisters the listener during client disconnect wait this creates a steady memory leak because each disconnected client retains its session context in the heap um over twenty four hours staging telemetry shows heap allocat climbing from two hundred megabytes two one thousand megabytes buy leaking stale socket references please refactor the teardown callback two call remove listener on both error and close events before destroying the connection knowed configur an integration test that establishes two hundred concurrent connections and asserts that active listener counts return two zero after clients disconnect",
        "refined_text": "Looking at pull request 482, the WebSocket connection handler registers an event listener for incoming message frames on the global event bus but never unregisters the listener during client disconnect. This creates a steady memory leak because each disconnected client retains its session context in the heap.\n\nOver 24 hours, staging telemetry shows heap allocation climbing from 200 megabytes to 1000 megabytes by leaking stale socket references. Please refactor the teardown callback to call remove listener on both error and close events before destroying the connection node.\n\nConfigure an integration test that establishes 200 concurrent connections and asserts that active listener counts return to 0 after clients disconnect."
    },
    # Sample 7 (Long 90+ words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "in this pull request review four the payment webhook service the idempotency check reads the cache key and then sets key value in two separate redis operations without an atomic lock this creates a critical race condition where two simultaneous webhook retries buy pass the check and charge the customer card twice um the fix here is two replac the read then set sequence with a single atomic set n x command with a thirty second expiration ttl wait set sixty seconds instead furthermore the response payload should be serialized into cache storage before returning http two zero zero so duplicate processing stops when downstream partner services retry on gateway timeouts please add a concurrency test reproducing fifty parallel requests four the same idempotency key",
        "refined_text": "In this pull request review for the payment webhook service, the idempotency check reads the cache key and then sets key value in two separate Redis operations without an atomic lock. This creates a critical race condition where two simultaneous webhook retries bypass the check and charge the customer card twice.\n\nThe fix here is to replace the read-then-set sequence with a single atomic SETNX command with a 60 seconds expiration TTL instead. Furthermore, the response payload should be serialized into cache storage before returning HTTP 200 so duplicate processing stops when downstream partner services retry on gateway timeouts.\n\nPlease add a concurrency test reproducing 50 parallel requests for the same idempotency key."
    },
    # Sample 8 (Long 90+ words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "reviewing the transaction manager diff in pull request one zero four shows that the batch update routine acquires row locks on the inventory table and order table in reverse order relative two the checkout workflow this inconsistent ordering triggers circular wait deadlocks under high database write concurrency where worker threads wait indefinitely buy holding contested row locks um please standardiz the locking sequence buy enforcing a strict ascending sort buy table id and record primary key before calling lock row wait sort buy entity key instead additionally wrap the transaction inside a retry loop with exponential backoff capped at five retries and three hundred milliseconds delay so transient deadlocks resolve cleanly without failing customer checkouts",
        "refined_text": "Reviewing the transaction manager diff in pull request 104 shows that the batch update routine acquires row locks on the inventory table and order table in reverse order relative to the checkout workflow. This inconsistent ordering triggers circular wait deadlocks under high database write concurrency where worker threads wait indefinitely by holding contested row locks.\n\nPlease standardize the locking sequence by enforcing a strict ascending sort by entity key instead before calling lock row. Additionally, wrap the transaction inside a retry loop with exponential backoff capped at 5 retries and 300 milliseconds delay so transient deadlocks resolve cleanly without failing customer checkouts."
    },
    # Sample 9 (Long 90+ words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "looking at the binary frame decoder in pull request seven one nine the parser reads variable length payload slices without checking if remaining byte buffer capacity matches the stated length header when payload length exceeds available slice capacity the decoder causes a slice bounds out of range panic or triggers an unprompted memory reallocat on every frame um you should validat the frame length field against buffer length before slicing into raw packet bytes wait verify header magic bytes first then check slice capacity furthermore write a table driven unit test with sixty four malformed frames including zero length payloads and oversized length fields exceeding four zero nine six bytes so the parser handles corrupt packets buy returning descriptive error codes",
        "refined_text": "Looking at the binary frame decoder in pull request 719, the parser reads variable-length payload slices without checking if remaining byte buffer capacity matches the stated length header. When payload length exceeds available slice capacity, the decoder causes a slice bounds out of range panic or triggers an unprompted memory reallocation on every frame.\n\nYou should verify header magic bytes first, then check slice capacity against buffer length before slicing into raw packet bytes. Furthermore, write a table-driven unit test with 64 malformed frames including 0 length payloads and oversized length fields exceeding 4096 bytes so the parser handles corrupt packets by returning descriptive error codes."
    },
    # Sample 10 (Long 90+ words)
    {
        "domain": "Domain 3: Code Reviews & PR Discussions",
        "raw_asr": "in this pull request the metrics collector struct directly instantiates the concrete prometheus exporter and file sink rather than depending on an abstracted metrics writer interface this tight coupling violates the dependency inversion principle and makes unit testing impossible without starting a real http metrics endpoint buy abstracting the recording contract into a small metrics recorder interface consumers only depend on record counter and record gauge methods wait omit record gauge four now and keep counter recording minimal um please refactor the collector constructor two accept recorder dependencies via constructor injection and configur a mock recorder in the test suite that captures thirty two test samples without touching external network sockets",
        "refined_text": "In this pull request, the metrics collector struct directly instantiates the concrete Prometheus exporter and file sink rather than depending on an abstracted metrics writer interface. This tight coupling violates the dependency inversion principle and makes unit testing impossible without starting a real HTTP metrics endpoint.\n\nBy abstracting the recording contract into a small metrics recorder interface, consumers only depend on record counter methods, omitting record gauge for now and keeping counter recording minimal.\n\nPlease refactor the collector constructor to accept recorder dependencies via constructor injection. Configure a mock recorder in the test suite that captures 32 test samples without touching external network sockets."
    },

    # --- DOMAIN 5: TECHNICAL MENTORING & ARCHITECTURE EXPLANATIONS (Samples 11 - 20) ---
    # Sample 11 (Short < 25 words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "uh the kernel page fault handler will initializ thirty two memory pages four each worker knowed",
        "refined_text": "The kernel page fault handler will initialize 32 memory pages for each worker node."
    },
    # Sample 12 (Short < 25 words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "the event loop runtime drains microtasks two completion buy executing promises before pulling macrotasks from the timer queue",
        "refined_text": "The event loop runtime drains microtasks to completion by executing promises before pulling macrotasks from the timer queue."
    },
    # Sample 13 (Medium 25 - 89 words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "when mentoring junior engineers on database indexing explain that b tree indexes organize table keys into a balanced tree hierarchy buy sorting page entries this structure supports efficient range scans and prefix matching whereas hash indexes only accelerate exact point lookups um each index knowed page is typically sized at sixteen kilobytes two align with disk blocks",
        "refined_text": "When mentoring junior engineers on database indexing, explain that B-tree indexes organize table keys into a balanced tree hierarchy by sorting page entries. This structure supports efficient range scans and prefix matching, whereas hash indexes only accelerate exact point lookups.\n\nEach index node page is typically sized at 16 kilobytes to align with disk blocks."
    },
    # Sample 14 (Medium 25 - 89 words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "in modern garbage collection runtimes the generational hypothesis states that most allocated objects die young right after creation um the collector divides the managed heap into nursery and tenured spaces buy moving surviving objects after two collection cycles this reduces sweep pauses because nursery collections only scan active references rather than inspecting sixty four gigabytes of tenured memory",
        "refined_text": "In modern garbage collection runtimes, the generational hypothesis states that most allocated objects die young right after creation.\n\nThe collector divides the managed heap into nursery and tenured spaces by moving surviving objects after 2 collection cycles. This reduces sweep pauses because nursery collections only scan active references rather than inspecting 64 gigabytes of tenured memory."
    },
    # Sample 15 (Medium 25 - 89 words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "in distributed consensus algorithms like raft leader knoweds maintain authority buy broadcasting heartbeat r p c messages every fifty milliseconds if followers do not receive a heartbeat within an election timeout between one hundred fifty and three hundred milliseconds election timeout triggers randomized backoff before requesting votes and followers transition two candidate state",
        "refined_text": "In distributed consensus algorithms like Raft, leader nodes maintain authority by broadcasting heartbeat RPC messages every 50 milliseconds.\n\nIf followers do not receive a heartbeat within an election timeout between 150 and 300 milliseconds, election timeout triggers randomized backoff before requesting votes and followers transition to candidate state."
    },
    # Sample 16 (Long 90+ words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "when explaining the event loop architecture two new systems engineers emphasize that asynchronous non blocking execution relies on operating system multiplexing rather than spawning a thread four every socket the runtime delegates socket polling two kernel mechanisms like epoll or kqueue buy registering file descriptors in an interest list when network events occur the kernel awakens the event loop poll phase which pushes ready callbacks into the task queue um execution follows a strict phase order traversing timers pending callbacks poll check and close handlers between each phase the engine drains the microtask queue which handles promise resolutions before moving two the next phase wait microtasks run immediately after current javascript execution completes mentoring sessions should highlight that blocking the event loop with synchronous computation starves all concurrent connections and spikes p ninety nine latency beyond five hundred milliseconds",
        "refined_text": "When explaining the event loop architecture to new systems engineers, emphasize that asynchronous non-blocking execution relies on operating system multiplexing rather than spawning a thread for every socket. The runtime delegates socket polling to kernel mechanisms like epoll or kqueue by registering file descriptors in an interest list. When network events occur, the kernel awakens the event loop poll phase, which pushes ready callbacks into the task queue.\n\nExecution follows a strict phase order traversing timers, pending callbacks, poll, check, and close handlers. Between each phase, the engine drains the microtask queue, which handles promise resolutions before moving to the next phase, running microtasks immediately after current JavaScript execution completes.\n\nMentoring sessions should highlight that blocking the event loop with synchronous computation starves all concurrent connections and spikes p99 latency beyond 500 milliseconds."
    },
    # Sample 17 (Long 90+ words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "when teaching storage engine architecture contrast write heavy l s m trees with read optimized b tree indexes log structured merge trees append all incoming writes two an in memory memtable backed buy an on disk write ahead log so disk writes remain strictly sequential once the memtable reaches its threshold typically sixty four megabytes the engine flushes it two disk as an immutable sorted string table um background threads then perform compaction buy merging multiple s s tables and removing deleted records which amortizes write amplification wait leveled compaction merges tables across fixed size tiers instead of universal compaction explaining this trade off helps engineers understand why l s m engines achieve ten times higher write throughput than traditional b trees while requiring bloom filters and block caches two maintain sub ten millisecond point read performance",
        "refined_text": "When teaching storage engine architecture, contrast write-heavy LSM trees with read-optimized B-tree indexes. Log-structured merge trees append all incoming writes to an in-memory memtable backed by an on-disk write-ahead log, so disk writes remain strictly sequential. Once the memtable reaches its threshold, typically 64 megabytes, the engine flushes it to disk as an immutable sorted string table.\n\nBackground threads then perform compaction by merging multiple SSTables and removing deleted records, which amortizes write amplification. Leveled compaction merges tables across fixed size tiers instead of universal compaction.\n\nExplaining this trade-off helps engineers understand why LSM engines achieve 10 times higher write throughput than traditional B-trees, while requiring Bloom filters and block caches to maintain sub-10 millisecond point read performance."
    },
    # Sample 18 (Long 90+ words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "in systems architecture mentoring sessions walk engineers through tri color marking algorithms two demystify concurrent garbage collection objects start marked white meaning unvisited gray objects have been visited but retain white references and black objects have no outgoing white pointers um during concurrent marking the application mutator continues running and modifying object references buy creating edges from black objects two white objects which risks sweeping live data the collector deploys a write barrier that intercepts reference modifications and colors modified targets gray wait use a satb write barrier four incremental update instead explaining write barrier overhead clarifies why concurrent collectors trade slight c p u throughput penalties two keep stop the world pauses below one millisecond across thirty two gigabytes of live heap",
        "refined_text": "In systems architecture mentoring sessions, walk engineers through tri-color marking algorithms to demystify concurrent garbage collection. Objects start marked white, meaning unvisited. Gray objects have been visited but retain white references, and black objects have no outgoing white pointers.\n\nDuring concurrent marking, the application mutator continues running and modifying object references by creating edges from black objects to white objects, which risks sweeping live data. The collector deploys a write barrier that intercepts reference modifications and colors modified targets gray, using a SATB write barrier for incremental update instead.\n\nExplaining write barrier overhead clarifies why concurrent collectors trade slight CPU throughput penalties to keep stop-the-world pauses below 1 millisecond across 32 gigabytes of live heap."
    },
    # Sample 19 (Long 90+ words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "when mentoring engineers on distributed consensus contrast classic multi paxos with raft two explain state machine replication foundations raft decomposes consensus into explicit sub problems leader election log replication and safety which makes mental models much easier two verify than paxos roles during steady state operations the leader receives client proposals appends entries two its local replicated log and broadcasts append entries r p c messages two all cluster knoweds um an entry achieves commit status once written buy a majority quorum of replicas such as three out of five knoweds wait quorum requires majority acknowledgment before replying two the client explaining quorum math and term based epoch counters shows how distributed systems maintain linearizability and survive up two two knowed failures without split brain anomalies",
        "refined_text": "When mentoring engineers on distributed consensus, contrast classic Multi-Paxos with Raft to explain state machine replication foundations. Raft decomposes consensus into explicit sub-problems: leader election, log replication, and safety, which makes mental models much easier to verify than Paxos roles.\n\nDuring steady state operations, the leader receives client proposals, appends entries to its local replicated log, and broadcasts AppendEntries RPC messages to all cluster nodes. An entry achieves commit status once written by a majority quorum of replicas, such as 3 out of 5 nodes, requiring majority acknowledgment before replying to the client.\n\nExplaining quorum math and term-based epoch counters shows how distributed systems maintain linearizability and survive up to 2 node failures without split-brain anomalies."
    },
    # Sample 20 (Long 90+ words)
    {
        "domain": "Domain 5: Technical Mentoring & Architecture Explanations",
        "raw_asr": "when guiding teams through architectural evolution evaluate the trade offs between a modular monolith and distributed microservices monoliths provide zero network latency four in process function calls and guarantee atomic database transactions buy enforcing foreign key constraints across domain tables in contrast decomposing into microservices replaces in memory method calls with network r p c or message broker queues which introduces latency serialization overhead and partial failure modes um distributed transactions then require complex saga patterns rather than simple database rollbacks wait start with a modular monolith and extract services only when team autonomy requires independent deployment pipelines illustrating this operational overhead helps engineers avoid premature microservice adoption four teams under twenty engineers",
        "refined_text": "When guiding teams through architectural evolution, evaluate the trade-offs between a modular monolith and distributed microservices. Monoliths provide 0 network latency for in-process function calls and guarantee atomic database transactions by enforcing foreign key constraints across domain tables.\n\nIn contrast, decomposing into microservices replaces in-memory method calls with network RPC or message broker queues, which introduces latency, serialization overhead, and partial failure modes. Distributed transactions then require complex saga patterns rather than simple database rollbacks. Start with a modular monolith and extract services only when team autonomy requires independent deployment pipelines.\n\nIllustrating this operational overhead helps engineers avoid premature microservice adoption for teams under 20 engineers."
    }
]

# Run tests
def run_audit():
    print(f"Auditing {len(pairs)} candidate pairs...\n")

    # Load sft_eval for leakage
    eval_file = Path("sft_eval.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    all_ok = True

    for i, p in enumerate(pairs, 1):
        raw = p["raw_asr"]
        ref = p["refined_text"]

        # Leakage check
        if raw.strip().lower() in eval_raws:
            print(f"Sample {i:02d}: LEAKAGE in raw_asr!")
            all_ok = False
        if ref.strip() in eval_refs:
            print(f"Sample {i:02d}: LEAKAGE in refined_text!")
            all_ok = False

        v_ok, v_reason = validate_pair(p)
        c_res, c_reason = clean_sample(raw, ref)

        words = len(ref.split())
        raw_words = len(raw.split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
        elif words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
        else:
            tier = "LONG"
            tier_counts["long"] += 1

        if not v_ok or c_res is None:
            all_ok = False
            print(f"Sample {i:02d} [{tier:6s}]: FAIL - validator: {v_reason}, cleaner: {c_reason}")
        else:
            print(f"Sample {i:02d} [{tier:6s}]: PASS - words={words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

    print("\n--- Tier Counts ---")
    print(f"Short:  {tier_counts['short']} / 4")
    print(f"Medium: {tier_counts['medium']} / 6")
    print(f"Long:   {tier_counts['long']} / 10")

    b_ok, b_reason, b_tiers = validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
    print(f"\nvalidate_batch: {b_reason} (passed={b_ok}, returned_tiers={b_tiers})")

    if all_ok and b_ok:
        print("\nAll 20 candidate pairs passed all checks!")
        # Save to scratch/subagent_batch_43.json
        clean_pairs = [{"raw_asr": p["raw_asr"], "refined_text": p["refined_text"]} for p in pairs]
        with open("scratch/subagent_batch_43.json", "w", encoding="utf-8") as out_f:
            json.dump(clean_pairs, out_f, indent=2, ensure_ascii=False)
        print("Saved to scratch/subagent_batch_43.json")
    else:
        print("\nValidation failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
