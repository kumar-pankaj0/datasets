import json
from pathlib import Path
import sys
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)
validate_pair = val_mod.validate_pair
validate_batch = val_mod.validate_batch

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)
clean_sample = clean_mod.clean_sample

pairs = [
    # 4 Short Samples (< 25 words)
    {
        "raw_asr": "um flush the in memory mem table two level zero s s table buy triggering background compact",
        "refined_text": "Flush the in-memory memtable to Level 0 SSTable by triggering background compaction."
    },
    {
        "raw_asr": "basically renew the p a x o s leader lease buy broadcasting heartbeats every fifty milliseconds",
        "refined_text": "Renew the Paxos leader lease by broadcasting heartbeats every 50 milliseconds."
    },
    {
        "raw_asr": "our schema evolution guideline reserv field tags one hundred and one hundred twenty buy deprecating unmapped identifiers",
        "refined_text": "Our schema evolution guideline reserves field tags 100 and 120 by deprecating unmapped identifiers."
    },
    {
        "raw_asr": "um the distributed lock service terminates the lease buy dropping the zoo keeper ephemeral knowed session after ten seconds",
        "refined_text": "The distributed lock service terminates the lease by dropping the ZooKeeper ephemeral node session after 10 seconds."
    },

    # 6 Medium Samples (25 - 89 words)
    {
        "raw_asr": "our multi region technical design document specifi range lease transfers across three geographical regions buy prioritizing local knowed replicas um the raft leader grants an epoch lease four six wait ten seconds before relinquishing leaseholder authority across the secondary availability zone",
        "refined_text": "Our multi-region technical design document specified range lease transfers across 3 geographical regions by prioritizing local node replicas.\n\nThe Raft leader grants an epoch lease for 10 seconds before relinquishing leaseholder authority across the secondary availability zone."
    },
    {
        "raw_asr": "um our storage engine r f c compared rocks d b against in no d b four write heavy telemetry workloads with forty thousand transactions per second uh rocks d b reduced write amplification factor from twenty eight down two four buy appending mutations two write ahead logs and sequential s s table levels",
        "refined_text": "Our storage engine RFC compared RocksDB against InnoDB for write-heavy telemetry workloads with 40000 transactions per second.\n\nRocksDB reduced write amplification factor from 28 down to 4 by appending mutations to write-ahead logs and sequential SSTable levels."
    },
    {
        "raw_asr": "our c q r s technical design specifi an asynchronous synchronizat pipeline buy capturing post gres write ahead log segments with de bez i um connectors um the synchronizer publishes json event payloads two a dedicated k af ka topic partitioned across eight brokers four downstream consumer lag monitoring",
        "refined_text": "Our CQRS technical design specified an asynchronous synchronization pipeline by capturing Postgres write-ahead log segments with Debezium connectors.\n\nThe synchronizer publishes JSON event payloads to a dedicated Kafka topic partitioned across 8 brokers for downstream consumer lag monitoring."
    },
    {
        "raw_asr": "basically our schema evolution r f c mandates full backward compatibility checks buy registering avro schemas against a centralized registry um the validation pipeline rejects field renumbering or type mutations across thirty five microservice contracts before deploying version two definitions",
        "refined_text": "Our schema evolution RFC mandates full backward compatibility checks by registering Avro schemas against a centralized registry.\n\nThe validation pipeline rejects field renumbering or type mutations across 35 microservice contracts before deploying version 2 definitions."
    },
    {
        "raw_asr": "uh the distributed lock r f c mandates validating monotonic fencing tokens during storage layer write operations buy checking lease generation numbers um our consensus backend rejects write attempts whenever an incoming lease token carries a value below five hundred wait eight hundred instead",
        "refined_text": "The distributed lock RFC mandates validating monotonic fencing tokens during storage layer write operations by checking lease generation numbers.\n\nOur consensus backend rejects write attempts whenever an incoming lease token carries a value below 800 instead."
    },
    {
        "raw_asr": "our r a f t consensus architecture design defin log compact thresholds buy taking memory snapshots every ten thousand committed entries um the leader streams snapshot chunks across four network sockets buy limiting individual chunk transmission size two sixty four megabytes",
        "refined_text": "Our Raft consensus architecture design defined log compaction thresholds by taking memory snapshots every 10000 committed entries.\n\nThe leader streams snapshot chunks across 4 network sockets by limiting individual chunk transmission size to 64 megabytes."
    },

    # 10 Long Samples (90+ words)
    {
        "raw_asr": "our distributed storage architecture r f c evaluat multi paxos against multi r a f t four state machine replicat across forty eight storage partitions multi paxos reduces proposal commit round trips buy allowing out of order log proposals without constant leader lease renewals but introduces substantial recovery complexity during leader failover scenarios under simulated network partit faults our multi paxos prototype required three hundred lines of custom reconciliation logic two resolve gaps in non contiguous transaction logs um the r f c recommended multi r a f t buy enforcing strong leader invariants and contiguous log matching rules each partition executes an independent r a f t consensus group with three replicas allowing cluster knowed instances two share leader and follower roles across separate shards uh during automated failover drills involving two abrupt worker knowed terminations multi r a f t re elected partition leaders within one hundred twenty milliseconds while maintaining a p nine nine commit latency of eighteen milliseconds across eighty concurrent client connections",
        "refined_text": "Our distributed storage architecture RFC evaluated Multi-Paxos against Multi-Raft for state machine replication across 48 storage partitions. Multi-Paxos reduces proposal commit round trips by allowing out-of-order log proposals without constant leader lease renewals, but introduces substantial recovery complexity during leader failover scenarios. Under simulated network partition faults, our Multi-Paxos prototype required 300 lines of custom reconciliation logic to resolve gaps in non-contiguous transaction logs.\n\nThe RFC recommended Multi-Raft by enforcing strong leader invariants and contiguous log matching rules. Each partition executes an independent Raft consensus group with 3 replicas, allowing cluster node instances to share leader and follower roles across separate shards. During automated failover drills involving 2 abrupt worker node terminations, Multi-Raft re-elected partition leaders within 120 milliseconds while maintaining a P99 commit latency of 18 milliseconds across 80 concurrent client connections."
    },
    {
        "raw_asr": "our telemetry storage architecture design document evaluated rocks d b against in no d b four high throughput metric ingestion workloads generating sixty thousand right events per second under in no d b random write mutations triggered repeated sixteen kilobyte b tree leaf page splits and heavy double write buffer traffic driving the write amplification factor two thirty four and causing storage controller queue saturation um the r f c approved migrating the timeseries ingest engine two rocks d b buy leveraging append only write ahead logs and leveled s s table compact in staging stress tests rocks d b absorbed sixty thousand inserts per second while restricting write amplification factor two five buy batching in memory mem table flushes across eight wait four background compact threads instead uh during forty eight hour soak tests p nine five write latency dropped from seventy five milliseconds down two six milliseconds across twenty storage knowed instances",
        "refined_text": "Our telemetry storage architecture design document evaluated RocksDB against InnoDB for high-throughput metric ingestion workloads generating 60000 write events per second. Under InnoDB, random write mutations triggered repeated 16-kilobyte B-tree leaf page splits and heavy doublewrite buffer traffic, driving the write amplification factor to 34 and causing storage controller queue saturation.\n\nThe RFC approved migrating the timeseries ingest engine to RocksDB by leveraging append-only write-ahead logs and leveled SSTable compaction. In staging stress tests, RocksDB absorbed 60000 inserts per second while restricting write amplification factor to 5 by batching in-memory memtable flushes across 4 background compaction threads instead. During 48-hour soak tests, P95 write latency dropped from 75 milliseconds down to 6 milliseconds across 20 storage node instances."
    },
    {
        "raw_asr": "our global cloud platform council drafted an r f c evaluat multi region database topologies across north america and europe data centers the document compared cock roach d b hybrid logical clocks against span ner true time synchronized atomic clocks span ner guarantees external consistency across continental distances buy relying on specialized atomic clock hardware appliances with bounded clock uncertainty under seven milliseconds however our bare metal data centers lack dedicated atomic hardware um the r f c recommended cock roach d b buy deploying geo partitioned ranges with local leaseholders each regional cluster knowed serves read requests locally within four milliseconds buy maintaining quorum leases on adjacent replicas cross region write consensus executes across three availability zones requiring sixty milliseconds round trip latency uh during simulated transatlantic fiber cut drills the surviving regional clusters automatically elected new range leaders within two seconds preserving strict serializable isolat across twenty thousand active tenant sessions",
        "refined_text": "Our global cloud platform council drafted an RFC evaluating multi-region database topologies across North America and Europe data centers. The document compared CockroachDB hybrid logical clocks against Spanner TrueTime synchronized atomic clocks. Spanner guarantees external consistency across continental distances by relying on specialized atomic clock hardware appliances with bounded clock uncertainty under 7 milliseconds. However, our bare-metal data centers lack dedicated atomic hardware.\n\nThe RFC recommended CockroachDB by deploying geo-partitioned ranges with local leaseholders. Each regional cluster node serves read requests locally within 4 milliseconds by maintaining quorum leases on adjacent replicas. Cross-region write consensus executes across 3 availability zones requiring 60 milliseconds round-trip latency. During simulated transatlantic fiber cut drills, the surviving regional clusters automatically elected new range leaders within 2 seconds, preserving strict serializable isolation across 20000 active tenant sessions."
    },
    {
        "raw_asr": "our payments architecture group authored a technical design document addressing consistency anomalies between our command right model and query read models previously our order service executed dual writes two post gres q l and an elasticsearch cluster whenever elasticsearch network calls failed or timed out the read projection diverged from the authoritative ledger requiring manual reconciliation scripts um the design document mandate implementing the transactional outbox pattern order transactions right business entities and outbox events into a single database transaction block de bez i um connectors tail the post gres transaction log and stream envelope records two a partitioned k af ka topic within twelve milliseconds uh downstream projection workers consume the outbox topic and update elasticsearch document stores with monotonic sequence validation in staging canary benchmarks this asynchronous synchronizat pipeline sustained five thousand mutations per second with a p nine nine replication lag under forty milliseconds across sixteen consumer partitions",
        "refined_text": "Our payments architecture group authored a technical design document addressing consistency anomalies between our command write model and query read models. Previously, our order service executed dual writes to PostgreSQL and an Elasticsearch cluster. Whenever Elasticsearch network calls failed or timed out, the read projection diverged from the authoritative ledger, requiring manual reconciliation scripts.\n\nThe design document mandated implementing the transactional outbox pattern. Order transactions write business entities and outbox events into a single database transaction block. Debezium connectors tail the PostgreSQL transaction log and stream envelope records to a partitioned Kafka topic within 12 milliseconds. Downstream projection workers consume the outbox topic and update Elasticsearch document stores with monotonic sequence validation. In staging canary benchmarks, this asynchronous synchronization pipeline sustained 5000 mutations per second with a P99 replication lag under 40 milliseconds across 16 consumer partitions."
    },
    {
        "raw_asr": "our core infrastructure platform r f c evaluated distributed lock implementations four orchestrating batch settlement jobs across forty worker instances our initial deployment utilized redis redlock with five second time two live leases during high load periods j v m full garbage collection pauses halted worker threads four six seconds exceeding the lease expiration threshold the paused worker awakened and executed storage mutations concurrently with the newly elected lock owner creating severe database record corruption um the r f c approved replacing redlock with et see dee distributed leases coupled with monotonic fencing tokens the et see dee lock provider issues an incrementing sixty four bit integer counter alongside every granted lease target post gres database tables validate the fencing token buy verifying that the incoming lease value is greater than the last recorded transaction counter uh during twenty four hour chaos testing with synthetic thread freeze events the storage validation logic rejected eighteen stale write attempts without incurring data corruption across fifty thousand financial transactions",
        "refined_text": "Our core infrastructure platform RFC evaluated distributed lock implementations for orchestrating batch settlement jobs across 40 worker instances. Our initial deployment utilized Redis Redlock with 5-second time to live leases. During high-load periods, JVM full garbage collection pauses halted worker threads for 6 seconds, exceeding the lease expiration threshold. The paused worker awakened and executed storage mutations concurrently with the newly elected lock owner, creating severe database record corruption.\n\nThe RFC approved replacing Redlock with etcd distributed leases coupled with monotonic fencing tokens. The etcd lock provider issues an incrementing 64-bit integer counter alongside every granted lease. Target Postgres database tables validate the fencing token by verifying that the incoming lease value is greater than the last recorded transaction counter. During 24-hour chaos testing with synthetic thread freeze events, the storage validation logic rejected 18 stale write attempts without incurring data corruption across 50000 financial transactions."
    },
    {
        "raw_asr": "our service mesh architecture committee released a technical design standard establishing protocol buffer schema evolution rules across one hundred twenty internal g r p c services previously engineering teams removed deprecated message fields without reserving field tags causing binary wire decode panics when older services deserialized payloads containing reused integer identifiers um the technical standard mandate strict wire compatibility buy requiring the reserved keyword four all retired tag indices and field names engineers must never alter existing tag numbers or mutate primitive types such as changing int thirty two two int sixty four because varint decoding behaviors diverge across language runtimes uh the continuous integration pipeline now executes automated schema linting across sixty pull requests daily buy comparing branch definitions against the central repository tag registry rejecting any breaking schema modification before binary compilation",
        "refined_text": "Our service mesh architecture committee released a technical design standard establishing Protocol Buffer schema evolution rules across 120 internal gRPC services. Previously, engineering teams removed deprecated message fields without reserving field tags, causing binary wire decode panics when older services deserialized payloads containing reused integer identifiers.\n\nThe technical standard mandated strict wire compatibility by requiring the reserved keyword for all retired tag indices and field names. Engineers must never alter existing tag numbers or mutate primitive types, such as changing int32 to int64, because varint decoding behaviors diverge across language runtimes. The continuous integration pipeline now executes automated schema linting across 60 pull requests daily by comparing branch definitions against the central repository tag registry, rejecting any breaking schema modification before binary compilation."
    },
    {
        "raw_asr": "our checkout domain architecture team published an r f c comparing two phase commit protocols against orchestrated sagas four multi service commerce transactions under two phase commit coordinating services held distributed row locks across post gres q l tables four up two twelve seconds whenever downstream shipping endpoints suffered network partitions this blocking coordinator behavior exhausted database connection pools and caused cascading timeouts across sixty web frontend instances um the r f c approved migrating two an orchestrated saga architecture coordinated buy a lightweight workflow engine each participant service executes a local database transaction and commits state changes immediately buy emitting domain events two k af ka if payment authorization fails the orchestrator dispatches compensating transactions across inventory and voucher services within two hundred milliseconds uh in staging load tests with twenty percent synthetic network drops the saga implementation maintained ninety five wait ninety nine percent transaction completion rates without holding blocking locks on primary tables",
        "refined_text": "Our checkout domain architecture team published an RFC comparing two-phase commit protocols against orchestrated sagas for multi-service commerce transactions. Under two-phase commit, coordinating services held distributed row locks across PostgreSQL tables for up to 12 seconds whenever downstream shipping endpoints suffered network partitions. This blocking coordinator behavior exhausted database connection pools and caused cascading timeouts across 60 web frontend instances.\n\nThe RFC approved migrating to an orchestrated saga architecture coordinated by a lightweight workflow engine. Each participant service executes a local database transaction and commits state changes immediately by emitting domain events to Kafka. If payment authorization fails, the orchestrator dispatches compensating transactions across inventory and voucher services within 200 milliseconds. In staging load tests with 20% synthetic network drops, the saga implementation maintained 99% transaction completion rates without holding blocking locks on primary tables."
    },
    {
        "raw_asr": "our consensus infrastructure group authored an r f c evaluat linearizable read optimizations across our distributed key value metadata cluster previously the leader knowed executed full quorum write rounds four all read requests incurring thirty milliseconds latency on every configuration check the team evaluated leader leases which serve reads locally based on bounded physical clock assumptions however staging chaos drills with twenty millisecond clock skew caused stale read anomalies during network partit events where a deposed leader continued answering reads um the r f c adopted the read index protocol instead four absolute linearizability without clock dependencies under read index the leader records its internal commit index and broadcasts lightweight heartbeat pings two a follower quorum confirming its active leadership before returning data uh benchmarks on fifteen knowed clusters showed that read index reduced p nine nine read latency from thirty milliseconds down two four milliseconds while maintaining strict linearizability across eighty thousand concurrent read queries",
        "refined_text": "Our consensus infrastructure group authored an RFC evaluating linearizable read optimizations across our distributed key-value metadata cluster. Previously, the leader node executed full quorum write rounds for all read requests, incurring 30 milliseconds latency on every configuration check. The team evaluated leader leases, which serve reads locally based on bounded physical clock assumptions. However, staging chaos drills with 20 milliseconds clock skew caused stale read anomalies during network partition events, where a deposed leader continued answering reads.\n\nThe RFC adopted the ReadIndex protocol instead for absolute linearizability without clock dependencies. Under ReadIndex, the leader records its internal commit index and broadcasts lightweight heartbeat pings to a follower quorum, confirming its active leadership before returning data. Benchmarks on 15 node clusters showed that ReadIndex reduced P99 read latency from 30 milliseconds down to 4 milliseconds, while maintaining strict linearizability across 80000 concurrent read queries."
    },
    {
        "raw_asr": "our distributed search indexing engineering team published a technical design document addressing severe read amplification in our rocks d b storage backend our point query benchmarks revealed that single key lookups touched up two eight separate s s table files across leveled storage tiers generating eleven disk seeks per read request and elevating p nine nine read latency two forty milliseconds under heavy concurrent load um the design document specifi configuring ten bits per key bloom filters across all level zero through level six s s table layers buy filtering out ninety nine percent of non existent key checks before hitting block storage additionally the team allocated sixty four gigabytes of physical r a m two an uncompressed block cache buy caching index and filter blocks in dedicated memory partitions uh in staging validation runs with two million synthetic keys the bloom filter tuning reduced disk seeks from eleven down two one seek per lookup instead while cutting p nine five read latency from twenty five milliseconds down two two milliseconds",
        "refined_text": "Our distributed search indexing engineering team published a technical design document addressing severe read amplification in our RocksDB storage backend. Our point query benchmarks revealed that single key lookups touched up to 8 separate SSTable files across leveled storage tiers, generating 11 disk seeks per read request and elevating P99 read latency to 40 milliseconds under heavy concurrent load.\n\nThe design document specified configuring 10 bits per key Bloom filters across all Level 0 through Level 6 SSTable layers by filtering out 99% of non-existent key checks before hitting block storage. Additionally, the team allocated 64 gigabytes of physical RAM to an uncompressed block cache by caching index and filter blocks in dedicated memory partitions. In staging validation runs with 2000000 synthetic keys, the Bloom filter tuning reduced disk seeks from 11 down to 1 seek per lookup instead, while cutting P95 read latency from 25 milliseconds down to 2 milliseconds."
    },
    {
        "raw_asr": "our database reliability engineering team authored an r f c establishing zero downtime schema migration protocols across our production post gres q l clusters previous direct alter table migrations acquired exclusive access exclusive locks four up two forty seconds blocking incoming transactions and exhausting connection pools across forty frontend services um the r f c mandate the expand and contract pattern four all structural table changes during the expand phase engineers add nullable columns or dual write triggers without taking table locks an asynchronous background worker backfills historical records in batches of five hundred wait batches of one thousand rows instead buy throttling update queries two ten millisecond pauses uh once the shadow backfill reaches one hundred percent completion read paths switch two the new column and an automated deprecation timer marks legacy columns four drops after a thirty day sunset window in staging canary runs this migration standard executed sixty column alterations without experiencing any query timeouts",
        "refined_text": "Our database reliability engineering team authored an RFC establishing zero-downtime schema migration protocols across our production PostgreSQL clusters. Previous direct alter table migrations acquired exclusive ACCESS EXCLUSIVE locks for up to 40 seconds, blocking incoming transactions and exhausting connection pools across 40 frontend services.\n\nThe RFC mandated the expand and contract pattern for all structural table changes. During the expand phase, engineers add nullable columns or dual-write triggers without taking table locks. An asynchronous background worker backfills historical records in batches of 1000 rows instead by throttling update queries to 10-millisecond pauses. Once the shadow backfill reaches 100% completion, read paths switch to the new column, and an automated deprecation timer marks legacy columns for drops after a 30-day sunset window. In staging canary runs, this migration standard executed 60 column alterations without experiencing any query timeouts."
    }
]

assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

# Leakage check against sft_eval.json
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

tiers = {"short": 0, "medium": 0, "long": 0}
for i, p in enumerate(pairs):
    raw = p["raw_asr"]
    ref = p["refined_text"]

    # 1. Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {i+1} raw leaked into eval!"
    assert ref.strip() not in eval_refs, f"Sample {i+1} ref leaked into eval!"

    # 2. validate_pair
    v_ok, v_reason = validate_pair(p)
    assert v_ok, f"Sample {i+1} failed validate_pair: {v_reason}"

    # 3. clean_sample
    c_res, c_reason = clean_sample(raw, ref)
    assert c_res is not None, f"Sample {i+1} failed clean_sample: {c_reason}"

    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
    elif words < 90:
        tiers["medium"] += 1
    else:
        tiers["long"] += 1

# 4. validate_batch
b_ok, b_msg, returned_tiers = validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
assert b_ok, f"Batch validation failed: {b_msg} (tiers: {returned_tiers})"

output_path = Path("scratch/subagent_batch_51.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"Successfully validated and saved Batch 51 to {output_path}")
print(f"Tier Breakdown: {tiers}")
print(f"Batch Validation: {b_msg}")
print("All 20 samples passed 100% clean and verified with 0 errors!")
