import json
import sys
import re

sys.path.insert(0, '.')
from code.validator import validate_pair, validate_batch
from code.cleaner import clean_sample

samples = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples
    # Sample 1: Domain 9 (Coding Interview)
    {
        "raw_asr": "um basically travers the binary tree buy using breadth first search while tracking depth four each knowed",
        "refined_text": "Traverse the binary tree by using breadth-first search while tracking depth for each node."
    },
    # Sample 2: Domain 5 (Mentoring Onboarding)
    {
        "raw_asr": "okay so configur local environment variables four post gres database authentication before starting the dev container",
        "refined_text": "Configure local environment variables for Postgres database authentication before starting the dev container."
    },
    # Sample 3: Domain 9 (System Design Interview)
    {
        "raw_asr": "uh estimat partition boundaries buy mapping user identifier hashes across thirty two storage shards",
        "refined_text": "Estimate partition boundaries by mapping user identifier hashes across 32 storage shards."
    },
    # Sample 4: Domain 5 (Mentoring Code Review / Database)
    {
        "raw_asr": "terminat pending worker transactions buy rolling back uncommitted database mutations during batch execution",
        "refined_text": "Terminate pending worker transactions by rolling back uncommitted database mutations during batch execution."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples
    # Sample 5: Domain 9 (System Design Interview: Rate Limiter)
    {
        "raw_asr": "basically implement the distributed rate limiter using a redis token bucket algorithm with five hundred millisecond refill intervals tracking client tenant quotas okay so configur forty wait configur sixty request tokens per client bucket four burst traffic handling buy dropping unauthorized requests immediately",
        "refined_text": "Implement the distributed rate limiter using a Redis token bucket algorithm with 500 millisecond refill intervals tracking client tenant quotas.\n\nConfigure 60 request tokens per client bucket for burst traffic handling by dropping unauthorized requests immediately."
    },
    # Sample 6: Domain 5 (Mentoring: Service Architecture)
    {
        "raw_asr": "um when navigating our service architecture place core business logic inside domain handlers while isolating database persistence logic into separate repository modules we isolat raw database queries buy using prepared statements across each transaction context",
        "refined_text": "When navigating our service architecture, place core business logic inside domain handlers while isolating database persistence logic into separate repository modules.\n\nWe isolate raw database queries by using prepared statements across each transaction context."
    },
    # Sample 7: Domain 9 (Coding Interview: Min-Heap)
    {
        "raw_asr": "okay so maintain a min heap of size eight wait size ten four tracking top elements across the stream instead of sorting the entire array buy keeping the heap bounded we achieve order of n log k runtime complexity while bounding memory consumption",
        "refined_text": "Maintain a min-heap of size 10 for tracking top elements across the stream instead of sorting the entire array.\n\nBy keeping the heap bounded, we achieve order of N log K runtime complexity while bounding memory consumption."
    },
    # Sample 8: Domain 5 (Mentoring: Distributed Tracing)
    {
        "raw_asr": "uh inspect the distributed trace context headers whenever debugging asynchronous background worker latency across message queues inject the trace identifier into each outbound message payload buy propagating context metadata across service boundaries",
        "refined_text": "Inspect the distributed trace context headers whenever debugging asynchronous background worker latency across message queues.\n\nInject the trace identifier into each outbound message payload by propagating context metadata across service boundaries."
    },
    # Sample 9: Domain 9 (Candidate Debrief: Concurrency & DP)
    {
        "raw_asr": "the candidate demonstrated strong algorithmic reasoning during the dynamic programming exercise buy identifying the overlapping subproblems quickly they also addressed race conditions during concurrent cache mutations buy proposing distributed locks across four worker nodes",
        "refined_text": "The candidate demonstrated strong algorithmic reasoning during the dynamic programming exercise by identifying the overlapping subproblems quickly.\n\nThey also addressed race conditions during concurrent cache mutations by proposing distributed locks across 4 worker nodes."
    },
    # Sample 10: Domain 5 (Mentoring: PR Best Practices)
    {
        "raw_asr": "um keep your pull requests focused on a single responsibility buy breaking large refactors into smaller reviews under three hundred lines of changes rebase your feature branch against main before requesting review buy resolving merge conflicts locally",
        "refined_text": "Keep your pull requests focused on a single responsibility by breaking large refactors into smaller reviews under 300 lines of changes.\n\nRebase your feature branch against main before requesting review by resolving merge conflicts locally."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples
    # Sample 11: Domain 9 (System Design: Distributed URL Shortener)
    {
        "raw_asr": "basically design the distributed url shortener buy separating the ingestion write path from the high throughput read path instead of computing md five hashes and handling collision retries our architecture provisions unique integer identifiers using a centralized ticket service running across three dedicated instances each ticket service instance reserves an integer range block of one million keys into local memory buy eliminating synchronous database locks during token generation okay so convert the assigned integer identifier into a compact seven character token buy applying base sixty four wait base sixty two encoding four clean alphanumeric characters we route incoming read requests through an in memory redis cluster caching the top twenty percent of active links buy serving eighty percent of read requests directly from cache memory we keep p ninety nine read latency under five milliseconds while database replicas handle cache misses",
        "refined_text": "Design the distributed URL shortener by separating the ingestion write path from the high-throughput read path. Instead of computing MD5 hashes and handling collision retries, our architecture provisions unique integer identifiers using a centralized ticket service running across 3 dedicated instances. Each ticket service instance reserves an integer range block of 1000000 keys into local memory by eliminating synchronous database locks during token generation.\n\nConvert the assigned integer identifier into a compact 7 character token by applying Base62 encoding for clean alphanumeric characters. We route incoming read requests through an in-memory Redis cluster caching the top 20 percent of active links. By serving 80 percent of read requests directly from cache memory, we keep P99 read latency under 5 milliseconds while database replicas handle cache misses."
    },
    # Sample 12: Domain 5 (Mentoring: Kafka & Dead-Letter Queue)
    {
        "raw_asr": "um when integrating kafka consumer groups four order processing walk through the message lifecycle carefully each consumer worker polls a batch of records from assigned topic partitions and processes individual order payloads sequentially committing consumer offsets only after the database transaction completes successfully buy committing offsets post processing we block uncommitted data loss during worker crash restarts okay so handle transient network timeouts buy wrapping outbound payment gateway calls in exponential backoff retries with randomized jitter bounded at five seconds whenever a malformed poison pill message triggers an unrecoverable deserialization fault avoid crashing the consumer loop buy catching schema validation exceptions route the failed payload into a dedicated dead letter topic after three failed execution attempts buy publishing corrupted messages into the dead letter queue our consumer group preserves steady partition throughput without dropping problematic messages",
        "refined_text": "When integrating Kafka consumer groups for order processing, walk through the message lifecycle carefully. Each consumer worker polls a batch of records from assigned topic partitions and processes individual order payloads sequentially, committing consumer offsets only after the database transaction completes successfully. By committing offsets post processing, we block uncommitted data loss during worker crash restarts.\n\nHandle transient network timeouts by wrapping outbound payment gateway calls in exponential backoff retries with randomized jitter bounded at 5 seconds. Whenever a malformed poison pill message triggers an unrecoverable deserialization fault, avoid crashing the consumer loop by catching schema validation exceptions. Route the failed payload into a dedicated dead-letter topic after 3 failed execution attempts. By publishing corrupted messages into the dead-letter queue, our consumer group preserves steady partition throughput without dropping problematic messages."
    },
    # Sample 13: Domain 9 (Coding Interview: LRU Cache Design)
    {
        "raw_asr": "basically design the least recently used cache buy combining an in memory hash map with a doubly linked list data structure the hash map indexes string keys directly to node pointers providing constant order of one lookup efficiency whenever a key is accessed or updated our logic detaches the corresponding node from its current position and splices it directly to the head of the linked list buy keeping the most recently used items at the head of the list the tail pointer consistently identifies the ideal candidate four eviction okay so address thread safety requirements under high concurrent read traffic instead of wrapping the entire data structure inside a coarse global mutex lock partition the cache into sixteen independent shards each containing its own read write lock buy assigning keys across shards using a murmur hash modulo sixteen multiple reader threads access distinct buckets concurrently without thread contention whenever cache capacity reaches ten thousand entries per shard evict the tail node buy updating neighbor node pointers directly",
        "refined_text": "Design the least recently used cache by combining an in-memory hash map with a doubly linked list data structure. The hash map indexes string keys directly to node pointers, providing constant order of 1 lookup efficiency. Whenever a key is accessed or updated, our logic detaches the corresponding node from its current position and splices it directly to the head of the linked list. By keeping the most recently used items at the head of the list, the tail pointer consistently identifies the ideal candidate for eviction.\n\nAddress thread safety requirements under high concurrent read traffic. Instead of wrapping the entire data structure inside a coarse global mutex lock, partition the cache into 16 independent shards, each containing its own read-write lock. By assigning keys across shards using a Murmur hash modulo 16, multiple reader threads access distinct buckets concurrently without thread contention. Whenever cache capacity reaches 10000 entries per shard, evict the tail node by updating neighbor node pointers directly."
    },
    # Sample 14: Domain 5 (Mentoring: Postgres Indexing)
    {
        "raw_asr": "uh walk through relational database indexing fundamentals buy analyzing how post gres stores b tree index pages on disk when an index query runs the database engine traverses tree pages starting from the root down through intermediate nodes to locate matching leaf entries each leaf entry holds a tuple identifier referencing the physical heap page location buy creating compound indexes on tenant id and created at timestamps our queries satisfy filtering criteria without scanning table blocks sequentially okay so inspect the query execution plan buy running explain analyze across slow endpoint queries whenever the planner indicates a sequential scan on a table containing four hundred thousand rows look closely at the filtering predicate buy ordering composite index columns matching the exact equality filters first followed buy range operators the engine utilizes index condition scans directly buy eliminating unnecessary heap page lookups our endpoint response time drops from six hundred milliseconds down into twenty milliseconds",
        "refined_text": "Walk through relational database indexing fundamentals by analyzing how Postgres stores B-Tree index pages on disk. When an index query runs, the database engine traverses tree pages starting from the root down through intermediate nodes to locate matching leaf entries. Each leaf entry holds a tuple identifier referencing the physical heap page location. By creating compound indexes on tenant ID and created at timestamps, our queries satisfy filtering criteria without scanning table blocks sequentially.\n\nInspect the query execution plan by running EXPLAIN ANALYZE across slow endpoint queries. Whenever the planner indicates a sequential scan on a table containing 400000 rows, look closely at the filtering predicate. By ordering composite index columns matching the exact equality filters first followed by range operators, the engine utilizes index condition scans directly. By eliminating unnecessary heap page lookups, our endpoint response time drops from 600 milliseconds down into 20 milliseconds."
    },
    # Sample 15: Domain 9 (System Design: Distributed Consensus with Raft)
    {
        "raw_asr": "basically evaluate distributed consensus trade offs buy examining the raft log replication protocol across a cluster of five server nodes each node operates in one of three states follower candidate or leader election timers use randomized durations between one hundred fifty milliseconds and three hundred milliseconds preventing split vote conditions whenever a follower misses heartbeats it transitions to candidate state buy incrementing the current term and requesting votes across peers okay so replicate client state machine mutations buy requiring the leader node to broadcast append entries rpc messages containing newly proposed log entries a log entry is safely committed once written and acknowledged buy a majority quorum of three nodes during network partitions minority leader nodes reject client writes buy enforcing lease check verifications against the quorum buy isolating partitioned minority nodes the cluster maintains strict linearizable consistency across all state machine transitions",
        "refined_text": "Evaluate distributed consensus trade-offs by examining the Raft log replication protocol across a cluster of 5 server nodes. Each node operates in one of 3 states: follower, candidate, or leader. Election timers use randomized durations between 150 milliseconds and 300 milliseconds, preventing split-vote conditions. Whenever a follower misses heartbeats, it transitions to candidate state by incrementing the current term and requesting votes across peers.\n\nReplicate client state machine mutations by requiring the leader node to broadcast AppendEntries RPC messages containing newly proposed log entries. A log entry is safely committed once written and acknowledged by a majority quorum of 3 nodes. During network partitions, minority leader nodes reject client writes by enforcing lease check verifications against the quorum. By isolating partitioned minority nodes, the cluster maintains strict linearizable consistency across all state machine transitions."
    },
    # Sample 16: Domain 5 (Mentoring: gRPC API Contracts)
    {
        "raw_asr": "um guide new engineers through microservice communication buy establishing clean g r p c service contracts defined with protocol buffers client and server teams generate type safe stubs directly from proto schema definitions buy avoiding manual json parsing and string serialization bugs when evolving existing message definitions never reuse or renumber retired field tags buy assigning unique field tag numbers between one through twenty tag identifiers four future message extensions okay so implement g r p c interceptors four cross cutting concerns across service boundaries register authentication interceptors buy validating incoming json web tokens before forwarding requests to business handlers inject distributed trace context into outbound metadata headers buy maintaining request lineage across microservice hops buy setting explicit dead line timeouts of three seconds on inter service rpc calls downstream network stalls do not exhaust upstream thread pools",
        "refined_text": "Guide new engineers through microservice communication by establishing clean gRPC service contracts defined with Protocol Buffers. Client and server teams generate type-safe stubs directly from proto schema definitions by avoiding manual JSON parsing and string serialization bugs. When evolving existing message definitions, never reuse or renumber retired field tags by assigning unique field tag numbers between 1 through 20 tag identifiers for future message extensions.\n\nImplement gRPC interceptors for cross-cutting concerns across service boundaries. Register authentication interceptors by validating incoming JSON Web Tokens before forwarding requests to business handlers. Inject distributed trace context into outbound metadata headers by maintaining request lineage across microservice hops. By setting explicit deadline timeouts of 3 seconds on inter-service RPC calls, downstream network stalls do not exhaust upstream thread pools."
    },
    # Sample 17: Domain 9 (Candidate Debrief: Senior Infrastructure)
    {
        "raw_asr": "basically debrief the candidate performance across our senior infrastructure system design interview the candidate demonstrated exceptional architectural maturity buy breaking down the global distributed counter problem into regional aggregation layers they clearly articulated cap theorem trade offs buy choosing eventual consistency four metrics ingestion while maintaining strict linearizable consistency four financial ledger entries uh evaluate their fault tolerance discussion during simulated network partitions the candidate identified potential split brain failure modes buy proposing fencing tokens and epoch numbers across distributed lease holders they also addressed database replica lag buy routing fresh read operations to primary nodes four thirty seconds after write mutations buy displaying deep mastery across distributed coordination and practical capacity planning the candidate meets our senior staff engineering bar",
        "refined_text": "Debrief the candidate performance across our senior infrastructure system design interview. The candidate demonstrated exceptional architectural maturity by breaking down the global distributed counter problem into regional aggregation layers. They clearly articulated CAP theorem trade-offs by choosing eventual consistency for metrics ingestion while maintaining strict linearizable consistency for financial ledger entries.\n\nEvaluate their fault tolerance discussion during simulated network partitions. The candidate identified potential split-brain failure modes by proposing fencing tokens and epoch numbers across distributed lease holders. They also addressed database replica lag by routing fresh read operations to primary nodes for 30 seconds after write mutations. By displaying deep mastery across distributed coordination and practical capacity planning, the candidate meets our senior staff engineering bar."
    },
    # Sample 18: Domain 5 (Mentoring: CI/CD Build Caching)
    {
        "raw_asr": "okay so mentor developers on optimizing continuous integration build pipelines buy eliminating slow redundant test stages when analyzing our containerized build step notice that un cached package manager installations download five hundred dependencies on every git push buy reordering docker file instructions to copy dependency lock files before copying application source code docker caches the intermediate package layer between builds um address flaky asynchronous integration tests that fail intermittently during pull request validation instead of adding arbitrary sleep delays of ten seconds inside test blocks rewrite the assertion logic buy polling service health endpoints with explicit retry loops bounded at fifteen seconds buy waiting directly on asynchronous event state changes test run duration drops from twelve minutes down into three minutes while eliminating false positive alert noise",
        "refined_text": "Mentor developers on optimizing continuous integration build pipelines by eliminating slow redundant test stages. When analyzing our containerized build step, notice that uncached package manager installations download 500 dependencies on every git push. By reordering Dockerfile instructions to copy dependency lock files before copying application source code, Docker caches the intermediate package layer between builds.\n\nAddress flaky asynchronous integration tests that fail intermittently during pull request validation. Instead of adding arbitrary sleep delays of 10 seconds inside test blocks, rewrite the assertion logic by polling service health endpoints with explicit retry loops bounded at 15 seconds. By waiting directly on asynchronous event state changes, test run duration drops from 12 minutes down into 3 minutes while eliminating false positive alert noise."
    },
    # Sample 19: Domain 9 (System Design: Consistent Hashing)
    {
        "raw_asr": "basically design a scalable distributed caching layer buy implementing consistent hashing with virtual nodes across sixty physical storage machines consistent hashing maps both cached object keys and cache nodes onto a shared circular thirty two bit hash ring buy distributing keys clockwise along the ring each cache server manages a balanced slice of the total keyspace okay so mitigate hash skew and hot spot imbalances buy allocating one hundred virtual nodes per physical machine across the ring when a single node experiences elevated query volume virtual nodes distribute traffic evenly across multiple physical neighbors whenever adding twenty new storage machines only a small fraction of keys migrate between adjacent nodes buy preventing massive cache invalidation storms during cluster resizing our cache hit ratio remains stable above ninety five percent",
        "refined_text": "Design a scalable distributed caching layer by implementing consistent hashing with virtual nodes across 60 physical storage machines. Consistent hashing maps both cached object keys and cache nodes onto a shared circular 32-bit hash ring. By distributing keys clockwise along the ring, each cache server manages a balanced slice of the total keyspace.\n\nMitigate hash skew and hot-spot imbalances by allocating 100 virtual nodes per physical machine across the ring. When a single node experiences elevated query volume, virtual nodes distribute traffic evenly across multiple physical neighbors. Whenever adding 20 new storage machines, only a small fraction of keys migrate between adjacent nodes. By preventing massive cache invalidation storms during cluster resizing, our cache hit ratio remains stable above 95 percent."
    },
    # Sample 20: Domain 5 (Mentoring: Observability & OpenTelemetry)
    {
        "raw_asr": "uh mentor the platform engineering team on implementing distributed observability using open telemetry sdk instrumentation across our go services differentiate between counter metrics four error rates gauge metrics four active worker threads and latency histograms four endpoint durations buy establishing standardized metric naming conventions across all microservices our dashboard alerts trigger consistently without false alarms okay so configur structured json logging buy injecting trace identifiers tenant codes and http route attributes into every log record whenever p ninety nine latency spikes exceed five hundred milliseconds on customer checkout routes engineers filter logs buy trace identifier to correlate downstream database queries buy pairing distributed traces with histogram latency metrics our team reduces mean time to resolution from forty five minutes down into five minutes",
        "refined_text": "Mentor the platform engineering team on implementing distributed observability using OpenTelemetry SDK instrumentation across our Go services. Differentiate between counter metrics for error rates, gauge metrics for active worker threads, and latency histograms for endpoint durations. By establishing standardized metric naming conventions across all microservices, our dashboard alerts trigger consistently without false alarms.\n\nConfigure structured JSON logging by injecting trace identifiers, tenant codes, and HTTP route attributes into every log record. Whenever P99 latency spikes exceed 500 milliseconds on customer checkout routes, engineers filter logs by trace identifier to correlate downstream database queries. By pairing distributed traces with histogram latency metrics, our team reduces mean time to resolution from 45 minutes down into 5 minutes."
    }
]

def main():
    print(f"Total samples: {len(samples)}")
    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for idx, s in enumerate(samples):
        words = len(s["refined_text"].split())
        tier = "short" if words < 25 else ("medium" if words < 90 else "long")
        tier_counts[tier] += 1
        
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        
        passed = v_ok and (c_res is not None)
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_ok = False
            print(f"[{status}] Sample {idx+1} ({tier}, {words} words):")
            if not v_ok:
                print(f"  Validator: {v_reason}")
            if c_res is None:
                print(f"  Cleaner: {c_reason}")
        else:
            print(f"[{status}] Sample {idx+1} ({tier}, {words} words)")

    print(f"\nTier counts: {tier_counts}")
    b_ok, b_reason, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
    print(f"Batch validation: ok={b_ok}, reason='{b_reason}', tiers={b_tiers}")

    if all_ok and b_ok:
        out_path = "scratch/subagent_batch_103.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)
        print(f"\nSUCCESS! Saved {len(samples)} samples to {out_path}")
    else:
        print("\nFAILURE! Fix failing samples.")

if __name__ == "__main__":
    main()
