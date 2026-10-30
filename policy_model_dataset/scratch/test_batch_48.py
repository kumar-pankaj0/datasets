import json
import re
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

# Load eval set
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
    # Tier 1: Short (< 25 words) - Samples 1 to 4
    # Sample 1: Domain 9 (Mock Technical Interviews - LRU Cache)
    {
        "raw_asr": "um implement an l r u cache buy combin a hash map with a doubly linked list four constant time lookups",
        "refined_text": "Implement an LRU cache by combining a hash map with a doubly linked list for constant time lookups."
    },
    # Sample 2: Domain 9 (Mock Technical Interviews - CAP Theorem)
    {
        "raw_asr": "explain how network partitions force distributed systems two priorit either consistency or availability under the c a p theorem",
        "refined_text": "Explain how network partitions force distributed systems to prioritize either consistency or availability under the CAP theorem."
    },
    # Sample 3: Domain 1 (Sprint Standups & Jira Grooming - Blocker Escalation)
    {
        "raw_asr": "um escalate the broken c i c d pipeline blocker buy notifi the release team about failing pull request integration tests",
        "refined_text": "Escalate the broken CI/CD pipeline blocker by notifying the release team about failing pull request integration tests."
    },
    # Sample 4: Domain 1 (Sprint Standups & Jira Grooming - Story Point Estimation)
    {
        "raw_asr": "assign five story points two the authentication ticket buy migrat our session token verification logic",
        "refined_text": "Assign 5 story points to the authentication ticket by migrating our session token verification logic."
    },

    # Tier 2: Medium (25 to 89 words) - Samples 5 to 10
    # Sample 5: Domain 9 (Mock Technical Interviews - Inverted Index Search)
    {
        "raw_asr": "basically design an inverted index four document search buy tokeniz input strings and storing term postings lists wait use compression arrays instead um write query evaluation logic two intersect document identifiers across multiple search terms",
        "refined_text": "Design an inverted index for document search by tokenizing input strings and storing term postings lists, using compression arrays instead.\n\nWrite query evaluation logic to intersect document identifiers across multiple search terms."
    },
    # Sample 6: Domain 9 (Mock Technical Interviews - Distributed Rate Limiter)
    {
        "raw_asr": "explain a distributed rate limiter architecture buy evaluat incoming requests against a token bucket algorithm inside r e d i s wait maintain atomic bucket counters with lua scripts instead um configure eight worker nodes two share capacity limits across twelve tenant routes",
        "refined_text": "Explain a distributed rate limiter architecture by evaluating incoming requests against a token bucket algorithm inside Redis, maintaining atomic bucket counters with Lua scripts instead.\n\nConfigure 8 worker nodes to share capacity limits across 12 tenant routes."
    },
    # Sample 7: Domain 9 (Mock Technical Interviews - BFS vs DFS)
    {
        "raw_asr": "compare b f s and d f s algorithms four graph travers buy analyz path finding guarantees on unweighted graphs wait use queue structures instead of recursive call stacks um demonstrate that breadth first search returns the shortest path across sixteen graph nodes",
        "refined_text": "Compare BFS and DFS algorithms for graph traversal by analyzing path finding guarantees on unweighted graphs, using queue structures instead of recursive call stacks.\n\nDemonstrate that breadth-first search returns the shortest path across 16 graph nodes."
    },
    # Sample 8: Domain 1 (Sprint Standups & Jira Grooming - Standup Status Update)
    {
        "raw_asr": "in today standup our team resolved the database query latency blocker buy add a composite index on the orders table wait update query execution plans inside db stats dot sql instead um right three unit tests two validat frontend cache invalidation across four customer endpoints",
        "refined_text": "In today standup our team resolved the database query latency blocker by adding a composite index on the orders table, updating query execution plans inside db_stats.sql instead.\n\nWrite 3 unit tests to validate frontend cache invalidation across 4 customer endpoints."
    },
    # Sample 9: Domain 1 (Sprint Standups & Jira Grooming - Backlog Grooming)
    {
        "raw_asr": "during backlog grooming our squad split the user notification preferences epic into smaller actionable tickets wait scope ticket three zero one four email delivery and push alerts instead um estimat eight story points four the backend webhook worker inside notification service dot py",
        "refined_text": "During backlog grooming our squad split the user notification preferences epic into smaller actionable tickets, scoping ticket 301 for email delivery and push alerts instead.\n\nEstimate 8 story points for the backend webhook worker inside notification_service.py."
    },
    # Sample 10: Domain 1 (Sprint Standups & Jira Grooming - Sprint Retrospective)
    {
        "raw_asr": "basically our sprint retrospective identified code review turnaround delays as our primary delivery impediment buy review average pull request merge metrics wait establish a four hour review window instead um track six flaky integration test failures inside retro notes dot md four the next sprint cycle",
        "refined_text": "Our sprint retrospective identified code review turnaround delays as our primary delivery impediment by reviewing average pull request merge metrics, establishing a 4 hour review window instead.\n\nTrack 6 flaky integration test failures inside retro_notes.md for the next sprint cycle."
    },

    # Tier 3: Long (90+ words) - Samples 11 to 20
    # Sample 11: Domain 9 (Mock Technical Interviews - Sharding vs Replication)
    {
        "raw_asr": "in this system design interview session we evaluated scaling strategies four a high throughput write heavy telemetry database where single node instances bottleneck on disk i o operations our initial architecture relied on primary replica database replication but write traffic saturated the primary node resulting in replication lag exceeding forty five seconds across twelve read replicas basically we analyzed horizontal database sharding buy partition records using a consistent hash ring on device identifier keys wait route write requests through a lightweight proxy coordinator instead of querying database shards directly\n\nduring peak ingestion workloads our coordinator node maps incoming telemetry payloads across sixteen distributed database shards buy evaluat hash ranges on sixty four virtual nodes per physical host um our interview evaluation reviewed failover semantics when individual partition shards suffer hardware crashes wait trigger automated shard leader election buy implement a raft consensus group across three replica nodes per shard partition instead\n\nfinally we analyzed query routing trade offs four scatter gather queries that scan multiple database shards buy aggregat partition metrics inside memory buffers our proposed design maintains strict linearizable writes four individual device records while accepting eventual consistency across global analytical queries across twenty four storage clusters".replace("\n\n", " "),
        "refined_text": "In this system design interview session we evaluated scaling strategies for a high-throughput write-heavy telemetry database where single node instances bottleneck on disk I/O operations. Our initial architecture relied on primary replica database replication, but write traffic saturated the primary node, resulting in replication lag exceeding 45 seconds across 12 read replicas. We analyzed horizontal database sharding by partitioning records using a consistent hash ring on device identifier keys, routing write requests through a lightweight proxy coordinator instead of querying database shards directly.\n\nDuring peak ingestion workloads our coordinator node maps incoming telemetry payloads across 16 distributed database shards by evaluating hash ranges on 64 virtual nodes per physical host. Our interview evaluation reviewed failover semantics when individual partition shards suffer hardware crashes, triggering automated shard leader election by implementing a Raft consensus group across 3 replica nodes per shard partition instead.\n\nFinally we analyzed query routing trade-offs for scatter-gather queries that scan multiple database shards by aggregating partition metrics inside memory buffers. Our proposed design maintains strict linearizable writes for individual device records while accepting eventual consistency across global analytical queries across 24 storage clusters."
    },
    # Sample 12: Domain 9 (Mock Technical Interviews - Concurrent LRU Cache)
    {
        "raw_asr": "during this coding algorithmic interview we designed a thread safe l r u cache data structure capable of sustaining high concurrent read throughput under heavy cache churn our initial implementation synchronized every get and put operation behind a global mutex lock which created severe thread contention across thirty two worker threads basically we refactored the concurrency model buy protect the internal hash map with reader writer locks wait isolate doubly linked list node updates buy buffering evictions inside a lock free ring buffer instead\n\nso basically when the when the reader threads query existing cache keys they acquire shared read locks buy inspect hash table buckets without blocking parallel key lookups um our cache eviction worker periodically flushes the eviction ring buffer buy dequeu expired key references and updating head and tail pointers across eight memory partitions wait serialize node pointer adjustments buy hold a dedicated eviction lock during list reorganization instead\n\nto complete the technical interview solution we implemented memory bounds checking buy monitor cache entry allocations inside cache manager dot py our updated design guarantees constant time o of one cache access while bounding total memory usage two five hundred twelve megabytes across sixty four concurrent worker threads".replace("\n\n", " "),
        "refined_text": "During this coding algorithmic interview we designed a thread-safe LRU cache data structure capable of sustaining high concurrent read throughput under heavy cache churn. Our initial implementation synchronized every get and put operation behind a global mutex lock, which created severe thread contention across 32 worker threads. We refactored the concurrency model by protecting the internal hash map with reader-writer locks, isolating doubly linked list node updates by buffering evictions inside a lock-free ring buffer instead.\n\nWhen reader threads query existing cache keys they acquire shared read locks by inspecting hash table buckets without blocking parallel key lookups. Our cache eviction worker periodically flushes the eviction ring buffer by dequeuing expired key references and updating head and tail pointers across 8 memory partitions, serializing node pointer adjustments by holding a dedicated eviction lock during list reorganization instead.\n\nTo complete the technical interview solution we implemented memory bounds checking by monitoring cache entry allocations inside cache_manager.py. Our updated design guarantees constant time O(1) cache access while bounding total memory usage to 512 megabytes across 64 concurrent worker threads."
    },
    # Sample 13: Domain 9 (Mock Technical Interviews - Graph Cycle Detection)
    {
        "raw_asr": "in this technical screening interview we solved an algorithmic challenge buy detect cycles within directed dependency graphs representing software package compilation pipelines our baseline approach executed recursive depth first search buy tag graph vertices with visited boolean flags but recursion depth overflowed call stacks when processing deep graphs containing twenty thousand dependency edges basically we refactored the graph traversal buy implement kahn topological sorting algorithm wait count in degree values four all directed graph vertices instead\n\nso basically when the when the algorithm initializ vertex queues it pushes all nodes with in degree zero into an a sink i o processing queue um during each iteration the worker extracts a graph vertex appends the vertex identifier two the resolved build order array and decrements adjacent neighbor in degree counters across eight package modules wait abort graph traversal buy raise a cyclic dependency exception when processed nodes do not equal total graph vertices instead\n\nfinally we benchmarked topological sorting performance buy measur execution duration across one hundred twenty eight synthetic dependency graphs containing five hundred package nodes our iterative queue implementation successfully resolves dependency ordering in linear time without risking recursion stack exhaustion across sixteen compilation workers".replace("\n\n", " "),
        "refined_text": "In this technical screening interview we solved an algorithmic challenge by detecting cycles within directed dependency graphs representing software package compilation pipelines. Our baseline approach executed recursive depth-first search by tagging graph vertices with visited boolean flags, but recursion depth overflowed call stacks when processing deep graphs containing 20000 dependency edges. We refactored the graph traversal by implementing Kahn topological sorting algorithm, counting in-degree values for all directed graph vertices instead.\n\nWhen the algorithm initializes vertex queues it pushes all nodes with in-degree zero into an asyncio processing queue. During each iteration the worker extracts a graph vertex, appends the vertex identifier to the resolved build order array, and decrements adjacent neighbor in-degree counters across 8 package modules, aborting graph traversal by raising a cyclic dependency exception when processed nodes do not equal total graph vertices instead.\n\nFinally we benchmarked topological sorting performance by measuring execution duration across 128 synthetic dependency graphs containing 500 package nodes. Our iterative queue implementation successfully resolves dependency ordering in linear time without risking recursion stack exhaustion across 16 compilation workers."
    },
    # Sample 14: Domain 9 (Mock Technical Interviews - Distributed Message Queue)
    {
        "raw_asr": "during this system design interview we architected a distributed append only log message queue modeled after k a f k a four high throughput event streaming our primary requirement focused on sustaining persistent message writes while maintaining strict partition consumer ordering under node failure conditions our baseline architecture wrote events into relational database tables which choked on index maintenance under forty thousand writes per second basically we designed an append only commit log buy write incoming message batches sequentially onto disk segments wait flush memory mapped file buffers buy synchroniz page cache writes every two hundred milliseconds instead\n\nin our partition replication design each log topic divides into twelve partition segments distributed across six cluster brokers um partition leaders manage consumer read offsets buy commit progress indices into an internal offset topic wait transfer partition leadership buy trigger automated consensus election when heartbeats fail across three broker nodes instead\n\nfinally we evaluated consumer group rebalancing semantics buy assign partition leases across eight consumer instances our partition assignment strategy avoids message duplication buy enforce consumer lease epochs while sustaining thirty megabytes per second consumer throughput across sixteen parallel event streams".replace("\n\n", " "),
        "refined_text": "During this system design interview we architected a distributed append-only log message queue modeled after Kafka for high-throughput event streaming. Our primary requirement focused on sustaining persistent message writes while maintaining strict partition consumer ordering under node failure conditions. Our baseline architecture wrote events into relational database tables which choked on index maintenance under 40000 writes per second. We designed an append-only commit log by writing incoming message batches sequentially onto disk segments, flushing memory-mapped file buffers by synchronizing page cache writes every 200 milliseconds instead.\n\nIn our partition replication design each log topic divides into 12 partition segments distributed across 6 cluster brokers. Partition leaders manage consumer read offsets by committing progress indices into an internal offset topic, transferring partition leadership by triggering automated consensus election when heartbeats fail across 3 broker nodes instead.\n\nFinally we evaluated consumer group rebalancing semantics by assigning partition leases across 8 consumer instances. Our partition assignment strategy avoids message duplication by enforcing consumer lease epochs while sustaining 30 megabytes per second consumer throughput across 16 parallel event streams."
    },
    # Sample 15: Domain 9 (Mock Technical Interviews - Concurrency Deadlock Detection)
    {
        "raw_asr": "in this concurrency technical interview we investigated thread synchronization bugs and race conditions inside a multithreaded financial transaction processing engine our production ledger suffered periodic thread starvation and circular deadlocks when parallel transfer workers acquired account locks in arbitrary sequence basically our team analyzed thread dump traces buy reconstruct the resource allocation graph across sixty four blocked worker threads wait enforce strict global lock ordering buy sort unique account identifiers before lock acquisition instead\n\nso basically when the when the transfer worker processes debit and credit actions it acquires mutual exclusion locks on both accounts simultaneously um our updated locking protocol prevents circular waiting buy release previously acquired locks whenever an intermediate lock acquisition times out after twenty five milliseconds wait register failed lock attempts buy log warning telemetry inside deadlock monitor dot py instead\n\nto conclude the interview problem we demonstrated lock contention benchmarks buy run concurrent fund transfer simulations across eight worker threads our benchmarks confirmed that global lock ordering completely eliminates deadlock cycles while processing five thousand transactions per second across thirty two account partitions".replace("\n\n", " "),
        "refined_text": "In this concurrency technical interview we investigated thread synchronization bugs and race conditions inside a multithreaded financial transaction processing engine. Our production ledger suffered periodic thread starvation and circular deadlocks when parallel transfer workers acquired account locks in arbitrary sequence. Our team analyzed thread dump traces by reconstructing the resource allocation graph across 64 blocked worker threads, enforcing strict global lock ordering by sorting unique account identifiers before lock acquisition instead.\n\nWhen the transfer worker processes debit and credit actions it acquires mutual exclusion locks on both accounts simultaneously. Our updated locking protocol prevents circular waiting by releasing previously acquired locks whenever an intermediate lock acquisition times out after 25 milliseconds, registering failed lock attempts by logging warning telemetry inside deadlock_monitor.py instead.\n\nTo conclude the interview problem we demonstrated lock contention benchmarks by running concurrent fund transfer simulations across 8 worker threads. Our benchmarks confirmed that global lock ordering completely eliminates deadlock cycles while processing 5000 transactions per second across 32 account partitions."
    },
    # Sample 16: Domain 1 (Sprint Standups & Jira Grooming - Burndown & Blocker)
    {
        "raw_asr": "in this morning sprint standup our platform squad reviewed our current burndown velocity and analyzed progress toward our sprint commitment our burndown chart indicates that our engineering team completed thirty eight story points out of fifty planned points with four days remaining in the active sprint cycle basically our backend developers resolved the database query timeout blocker buy add missing composite indices on the billing ledger table wait update query plan benchmarks inside sprint tracker dot py instead of relying on legacy schema definitions\n\nhowever our team identified a new release blocker regarding elevated p ninety nine latency spikes across our payment gateway integration our staging metrics showed response latency jumping from forty milliseconds two three hundred milliseconds under peak synthetic load um our infrastructure lead traced the latency regression buy inspect connection pool saturation across sixteen database client connections wait increase the maximum connection limit two sixty four pool workers instead\n\nfour our final standup action item we reviewed the phased rollout of our new checkout feature flag across ten percent of production user traffic our gradual rollout plan monitors error rates across eight microservices and prepares automated rollback triggers before expanding traffic two fifty percent tomorrow".replace("\n\n", " "),
        "refined_text": "In this morning sprint standup our platform squad reviewed our current burndown velocity and analyzed progress toward our sprint commitment. Our burndown chart indicates that our engineering team completed 38 story points out of 50 planned points with 4 days remaining in the active sprint cycle. Our backend developers resolved the database query timeout blocker by adding missing composite indices on the billing ledger table, updating query plan benchmarks inside sprint_tracker.py instead of relying on legacy schema definitions.\n\nHowever our team identified a new release blocker regarding elevated P99 latency spikes across our payment gateway integration. Our staging metrics showed response latency jumping from 40 milliseconds to 300 milliseconds under peak synthetic load. Our infrastructure lead traced the latency regression by inspecting connection pool saturation across 16 database client connections, increasing the maximum connection limit to 64 pool workers instead.\n\nFor our final standup action item we reviewed the phased rollout of our new checkout feature flag across 10 percent of production user traffic. Our gradual rollout plan monitors error rates across 8 microservices and prepares automated rollback triggers before expanding traffic to 50 percent tomorrow."
    },
    # Sample 17: Domain 1 (Sprint Standups & Jira Grooming - Backlog Grooming)
    {
        "raw_asr": "during today backlog grooming session our cross functional engineering squad refined seven user stories scheduled four sprint twenty four our lead developer walked through ticket four zero two buy clarify acceptance criteria four the automated customer invoice generation workflow our initial scope contained ambiguous billing validation rules which risked significant scope creep basically our squad broke the invoice workflow into three distinct subtasks buy separate pdf generation from asynchronous email dispatching wait estimat five story points four the background worker inside invoice service dot py instead\n\nnext our team evaluated the technical complexity and migration risks associated with ticket four zero eight buy inspect foreign key constraints on the customer transactions table our data engineer warned that running synchronous schema migrations on production databases could lock tables four thirty minutes um our squad decided two execut an asynchronous online schema migration buy add columns with non blocking d d l scripts wait schedule database index creation buy run background scripts during off peak hours instead\n\nfinally our team finalized story point estimations four the remaining backlog items buy assign eight story points two the webhook retry handler and three story points two the audit logging filter across sixteen groomed issues our sprint backlog now contains forty two estimated points ready four sprint planning".replace("\n\n", " "),
        "refined_text": "During today backlog grooming session our cross-functional engineering squad refined 7 user stories scheduled for sprint 24. Our lead developer walked through ticket 402 by clarifying acceptance criteria for the automated customer invoice generation workflow. Our initial scope contained ambiguous billing validation rules which risked significant scope creep. Our squad broke the invoice workflow into 3 distinct subtasks by separating PDF generation from asynchronous email dispatching, estimating 5 story points for the background worker inside invoice_service.py instead.\n\nNext our team evaluated the technical complexity and migration risks associated with ticket 408 by inspecting foreign key constraints on the customer transactions table. Our data engineer warned that running synchronous schema migrations on production databases could lock tables for 30 minutes. Our squad decided to execute an asynchronous online schema migration by adding columns with non-blocking DDL scripts, scheduling database index creation by running background scripts during off-peak hours instead.\n\nFinally our team finalized story point estimations for the remaining backlog items by assigning 8 story points to the webhook retry handler and 3 story points to the audit logging filter across 16 groomed issues. Our sprint backlog now contains 42 estimated points ready for sprint planning."
    },
    # Sample 18: Domain 1 (Sprint Standups & Jira Grooming - Blocker Escalation)
    {
        "raw_asr": "in this emergency standup meeting our squad escalated a critical production blocker regarding third party payment gateway request timeouts that halted customer checkout workflows our error tracking dashboard reported five hundred four gateway errors spiking two twelve percent of all checkout attempts during morning traffic basically our checkout microservice stalled when remote payment api calls hung indefinitely without returning status payloads wait configure an aggressive five second socket read timeout inside payment client dot py instead of waiting two minutes four default provider responses\n\nour site reliability engineer investigated downstream dependency health and confirmed that the external payment processor suffered an unexpected outage across sixteen regional endpoints um our backend team implemented an automated circuit breaker pattern buy tripp the breaker when error rates exceed twenty percent across fifty consecutive requests wait route pending transaction requests two a secondary payment vendor fallback queue instead of dropping customer orders completely\n\nfour our next escalation step our engineering manager contacted the vendor support tier while our squad monitored queue draining telemetry across eight worker nodes our recovery plan verifies that cached payment tokens process successfully once gateway connectivity stabilizes across four thousand queued transactions".replace("\n\n", " "),
        "refined_text": "In this emergency standup meeting our squad escalated a critical production blocker regarding third-party payment gateway request timeouts that halted customer checkout workflows. Our error tracking dashboard reported 504 gateway errors spiking to 12 percent of all checkout attempts during morning traffic. Our checkout microservice stalled when remote payment API calls hung indefinitely without returning status payloads, configuring an aggressive 5 second socket read timeout inside payment_client.py instead of waiting 2 minutes for default provider responses.\n\nOur site reliability engineer investigated downstream dependency health and confirmed that the external payment processor suffered an unexpected outage across 16 regional endpoints. Our backend team implemented an automated circuit breaker pattern by tripping the breaker when error rates exceed 20 percent across 50 consecutive requests, routing pending transaction requests to a secondary payment vendor fallback queue instead of dropping customer orders completely.\n\nFor our next escalation step our engineering manager contacted the vendor support tier while our squad monitored queue draining telemetry across 8 worker nodes. Our recovery plan verifies that cached payment tokens process successfully once gateway connectivity stabilizes across 4000 queued transactions."
    },
    # Sample 19: Domain 1 (Sprint Standups & Jira Grooming - Sprint Retrospective)
    {
        "raw_asr": "during our biweekly sprint retrospective our distributed engineering team conducted a detailed analysis of our sprint spillover and release bottlenecks our burndown metrics revealed that three major tickets representing twenty four story points rolled over into the next sprint cycle because integration testing environments experienced continuous deployment failures basically our squad determined that manual staging environment deployments created an eight hour delay buy blocking pull request verifications wait automat staging releases buy implement a c i c d deployment trigger inside deploy pipeline dot yml instead\n\nin our retrospective discussion our quality assurance engineer highlighted that forty percent of staging deployment failures stemmed from undocumented configuration drift between development and testing environments um our team resolved two standardize environment variables buy generat container configuration schemas across twelve microservices wait validat configuration secrets buy enforce schema checks during pull request builds instead\n\nfinally our team reviewed code review response metrics buy track review turnaround times across sixteen team pull requests our agreed team action item establishes a dedicated daily review block which targets merging peer reviews within twenty four hours across eight engineering pods".replace("\n\n", " "),
        "refined_text": "During our biweekly sprint retrospective our distributed engineering team conducted a detailed analysis of our sprint spillover and release bottlenecks. Our burndown metrics revealed that 3 major tickets representing 24 story points rolled over into the next sprint cycle because integration testing environments experienced continuous deployment failures. Our squad determined that manual staging environment deployments created an 8 hour delay by blocking pull request verifications, automating staging releases by implementing a CI/CD deployment trigger inside deploy_pipeline.yml instead.\n\nIn our retrospective discussion our quality assurance engineer highlighted that 40 percent of staging deployment failures stemmed from undocumented configuration drift between development and testing environments. Our team resolved to standardize environment variables by generating container configuration schemas across 12 microservices, validating configuration secrets by enforcing schema checks during pull request builds instead.\n\nFinally our team reviewed code review response metrics by tracking review turnaround times across 16 team pull requests. Our agreed team action item establishes a dedicated daily review block which targets merging peer reviews within 24 hours across 8 engineering pods."
    },
    # Sample 20: Domain 1 (Sprint Standups & Jira Grooming - Standup & Feature Flags)
    {
        "raw_asr": "in this morning standup and backlog grooming session our infrastructure team reviewed the feature flag rollout four our new customer recommendation service our telemetry dashboards showed that feature flag evaluations reached ten thousand requests per second without increasing api error rates however our team observed memory utilization climbing two eighty percent on our primary r e d i s cache cluster across eight cluster nodes basically our backend team decided two optimiz cache eviction policies buy replac idle session keys with l r u eviction policies wait configure memory limits two four gigabytes per cache node inside redis config dot conf instead\n\nduring ticket grooming our tech lead reviewed ticket five hundred twelve which covers migrating legacy feature flag evaluations away from local configuration files into an automated feature management service um our squad estimated thirteen story points four the migration workflow buy breakdown the task into three separate subtasks wait schedule staging verification buy test fallback behavior when feature flag services timeout instead\n\nfour our final action item our squad scheduled a canary deployment across five percent of active web traffic buy monitor recommendation latency across twenty four canary instances our release plan requires maintaining p ninety five latency under thirty milliseconds before expanding traffic two one hundred percent next sprint".replace("\n\n", " "),
        "refined_text": "In this morning standup and backlog grooming session our infrastructure team reviewed the feature flag rollout for our new customer recommendation service. Our telemetry dashboards showed that feature flag evaluations reached 10000 requests per second without increasing API error rates. However our team observed memory utilization climbing to 80 percent on our primary Redis cache cluster across 8 cluster nodes. Our backend team decided to optimize cache eviction policies by replacing idle session keys with LRU eviction policies, configuring memory limits to 4 gigabytes per cache node inside redis_config.conf instead.\n\nDuring ticket grooming our tech lead reviewed ticket 512 which covers migrating legacy feature flag evaluations away from local configuration files into an automated feature management service. Our squad estimated 13 story points for the migration workflow by breaking down the task into 3 separate subtasks, scheduling staging verification by testing fallback behavior when feature flag services timeout instead.\n\nFor our final action item our squad scheduled a canary deployment across 5 percent of active web traffic by monitoring recommendation latency across 24 canary instances. Our release plan requires maintaining P95 latency under 30 milliseconds before expanding traffic to 100 percent next sprint."
    }
]

print(f"Total pairs generated: {len(pairs)}")

# Perform checks
tiers = {"short": 0, "medium": 0, "long": 0}
all_passed = True

for idx, pair in enumerate(pairs):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]
    
    # 1. Leakage check
    if raw.strip().lower() in eval_raws:
        print(f"Sample {idx+1} raw leaked into eval!")
        all_passed = False
    if ref.strip() in eval_refs:
        print(f"Sample {idx+1} ref leaked into eval!")
        all_passed = False

    # 2. Validator check
    val_ok, val_reason = val_mod.validate_pair(pair)
    if not val_ok:
        print(f"Sample {idx+1} failed validate_pair: {val_reason}")
        all_passed = False

    # 3. Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    if clean_obj is None:
        print(f"Sample {idx+1} dropped by clean_sample: {clean_reason}")
        all_passed = False

    # Word count and tier
    words = len(ref.split())
    raw_w = len(raw.split())
    ratio = words / max(1, raw_w)
    if words < 25:
        tiers["short"] += 1
        t_label = "Short"
    elif words < 90:
        tiers["medium"] += 1
        t_label = "Medium"
    else:
        tiers["long"] += 1
        t_label = "Long"
        
    print(f"Sample {idx+1:02d} [{t_label:6s}]: {words:3d} ref words, {raw_w:3d} raw words, ratio {ratio:.2f} | val={val_ok}, clean={'kept' if clean_obj else clean_reason}")

print("\nTier Counts:", tiers)

# Batch check
batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
print(f"Batch validate: {batch_ok} - {batch_msg} - {batch_tiers}")

if all_passed and batch_ok:
    print("\nSUCCESS: All 20 samples passed all checks!")
    out_path = Path("scratch/subagent_batch_48.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out_path}")
else:
    print("\nFAILURE: Some checks failed.")
