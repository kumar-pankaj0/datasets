import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

# Domain 2: High-Throughput Data Engineering & Stream Processing
# Batch 137 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 noise layers active.
    # =========================================================================

    # Sample 1: Kafka partition consumer lag deduplication
    {
        "raw_asr": "um deduplicat event payloads buy matching partition underscore id across the r p c ingest pipeline",
        "refined_text": "Deduplicate event payloads by matching partition_id across the RPC ingest pipeline."
    },

    # Sample 2: Stream watermark delay recalculation
    {
        "raw_asr": "uh recalculat window watermarks buy checking watermark underscore delay while c p u metrics stabilize",
        "refined_text": "Recalculate window watermarks by checking watermark_delay while CPU metrics stabilize."
    },

    # Sample 3: RocksDB direct memory allocation for streaming state store
    {
        "raw_asr": "basically allocat six d m a ring buffers buy mounting slash data state storage volumes",
        "refined_text": "Allocate 6 DMA ring buffers by mounting /data state storage volumes."
    },

    # Sample 4: Postgres write-ahead log logical decoding replication termination
    {
        "raw_asr": "um terminat stalled post gres logical replication slots buy dropping slot underscore name instead",
        "refined_text": "Terminate stalled Postgres logical replication slots by dropping slot_name instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active.
    # =========================================================================

    # Sample 5: Kafka consumer group partition rebalance and cooperative sticky assignor
    {
        "raw_asr": "um basically our kafka stream ingestion encountered severe rebalance storms after eight consumers wait twelve consumers instead triggered frequent heartbeat expirations at group underscore coordinator knowed brokers you know cluster operators stabilized consumer group membership buy passing dash dash partition assignment strategy into worker configur scripts while engineers right two synthetic rebalance monitors tracking c p u load",
        "refined_text": "Our Kafka stream ingestion encountered severe rebalance storms after 12 consumers instead triggered frequent heartbeat expirations at group_coordinator node brokers.\n\nCluster operators stabilized consumer group membership by passing --partition-assignment-strategy into worker configuration scripts while engineers write 2 synthetic rebalance monitors tracking CPU load."
    },

    # Sample 6: Apache Flink RocksDB checkpoint barrier alignment timeout and backpressure
    {
        "raw_asr": "basically our flink stream processing job failed checkpoint barrier synchronizat when network buffer backpressure delayed alignment across thirty seconds wait sixty seconds instead uh operators recovered checkpoint completion buy writing snapshot state into slash checkpoint storage buy tuning checkpoint underscore interval while streaming pipeline operators inspect r p c barrier latencies across the network",
        "refined_text": "Our Flink stream processing job failed checkpoint barrier synchronization when network buffer backpressure delayed alignment across 60 seconds instead.\n\nOperators recovered checkpoint completion by writing snapshot state into /checkpoint storage by tuning checkpoint_interval while streaming pipeline operators inspect RPC barrier latencies across the network."
    },

    # Sample 7: Debezium PostgreSQL WAL CDC replication slot saturation
    {
        "raw_asr": "um our change data capture pipeline stalled post gres logical decoding after write ahead log accumulation reached twenty gigabytes wait thirty gigabytes instead you know database administrators unblocked schema migrat buy expanding wal underscore keep underscore size parameters buy passing dash dash wal sender timeout into connector specifications clearing backlog accumulation across the replication stream",
        "refined_text": "Our change data capture pipeline stalled Postgres logical decoding after write-ahead log accumulation reached 30 gigabytes instead.\n\nDatabase administrators unblocked schema migration by expanding wal_keep_size parameters by passing --wal-sender-timeout into connector specifications, clearing backlog accumulation across the replication stream."
    },

    # Sample 8: Spark Structured Streaming micro-batch offset commit lag and Delta Lake compaction
    {
        "raw_asr": "basically spark streaming micro batch commits lagged behind when partition compaction merged four hundred small files wait eight hundred files instead into slash data delta tables uh data engineers accelerated d m a vector caching buy recalculat partition batch underscore id watermarks while developers right two parquet read validation probes",
        "refined_text": "Spark streaming micro-batch commits lagged behind when partition compaction merged 800 small files instead into /data delta tables.\n\nData engineers accelerated DMA vector caching by recalculating partition batch_id watermarks while developers write 2 Parquet read validation probes."
    },

    # Sample 9: Kafka Streams state store changelog restore and standby replicas
    {
        "raw_asr": "um our stream processing workers delayed application initializ after local state recovery replayed two standby replicas wait four standby replicas instead basically site reliability engineers alleviated c p u saturation buy setting changelog underscore topic replication factors buy specifying dash dash state dir on worker mount paths while engineers right two standby sync health checks",
        "refined_text": "Our stream processing workers delayed application initialization after local state recovery replayed 4 standby replicas instead.\n\nSite reliability engineers alleviated CPU saturation by setting changelog_topic replication factors by specifying --state-dir on worker mount paths while engineers write 2 standby sync health checks."
    },

    # Sample 10: Async I/O operator enrichment timeout and connection pool starvation
    {
        "raw_asr": "uh our stream enrichment pipeline dropped events during peak ingest when external key value lookups exceeded two hundred requests wait five hundred concurrent requests instead you know stream architects optimized a sink i o lookup operat buy configuring timeout underscore ms buy setting dash dash capacity into twenty worker threads while developers right three async connection test suites",
        "refined_text": "Our stream enrichment pipeline dropped events during peak ingest when external key-value lookups exceeded 500 concurrent requests instead.\n\nStream architects optimized asyncio lookup operations by configuring timeout_ms by setting --capacity into 20 worker threads while developers write 3 async connection test suites."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # At least 4 noise layers active.
    # =========================================================================

    # Sample 11: Apache Flink unaligned checkpoints during high-throughput network buffer debloating
    {
        "raw_asr": "basically during our morning peak ingest wave rapid message bursts triggered severe checkpoint timeouts across sixteen flink task manager instances um our stateful stream joins accumulated forty thousand records per second which exhausted local network buffer pools because operators defaulted to aligned checkpointing barriers stalled behind in flight buffers for ninety seconds buy causing checkpoint cancellations across twelve subtasks metric graphs revealed that task worker c p u utiliz reached ninety percent while buffer debounce timers delayed snapshot creation past twelve minutes incident responders mitigated the stall buy enabling unaligned checkpoints buy passing dash dash enable unaligned checkpoints into flink configur files system engineers adjusted checkpoint storage buy setting checkpoint underscore timeout towards three minutes into slash checkpoint volumes while site reliability engineers inspect four r p c health probes tracking upstream barrier alignment latency",
        "refined_text": "During our morning peak ingest wave, rapid message bursts triggered severe checkpoint timeouts across 16 Flink task manager instances. Our stateful stream joins accumulated 40000 records per second, which exhausted local network buffer pools. Because operators defaulted to aligned checkpointing, barriers stalled behind in-flight buffers for 90 seconds by causing checkpoint cancellations across 12 subtasks.\n\nMetric graphs revealed that task worker CPU utilization reached 90 percent while buffer debounce timers delayed snapshot creation past 12 minutes.\n\nIncident responders mitigated the stall by enabling unaligned checkpoints by passing --enable-unaligned-checkpoints into Flink configuration files. System engineers adjusted checkpoint storage by setting checkpoint_timeout towards 3 minutes into /checkpoint volumes while site reliability engineers inspect 4 RPC health probes tracking upstream barrier alignment latency."
    },

    # Sample 12: Kafka transactional producer epoch bumping and zombie fencing under GC pauses
    {
        "raw_asr": "okay so our exactly once stream processor experienced repeated transaction aborts when four producer instances encountered long garbage collection pauses across eight broker knowed hosts um parallel worker threads were paused for forty seconds exceeding the thirty second transaction coordinator lease wait forty five seconds instead buy causing the coordinator to bump producer epoch values zombie producers attempted commits buy sending stale transactional ids which resulted in fencing exceptions across twenty four topic partitions site reliability engineers resolved the fencing storm buy increasing transaction underscore timeout underscore ms towards sixty seconds buy passing dash dash transaction timeout into producer worker configur files platform engineers adjusted heap allocat buy tuning generational garbage collection threads while developers right three automated validation scripts verifying transaction commit completion without duplicates",
        "refined_text": "Our exactly-once stream processor experienced repeated transaction aborts when 4 producer instances encountered long garbage collection pauses across 8 broker node hosts. Parallel worker threads were paused for 45 seconds instead, exceeding the 30-second transaction coordinator lease by causing the coordinator to bump producer epoch values.\n\nZombie producers attempted commits by sending stale transactional IDs, which resulted in fencing exceptions across 24 topic partitions.\n\nSite reliability engineers resolved the fencing storm by increasing transaction_timeout_ms towards 60 seconds by passing --transaction-timeout into producer worker configuration files. Platform engineers adjusted heap allocations by tuning generational garbage collection threads while developers write 3 automated validation scripts verifying transaction commit completion without duplicates."
    },

    # Sample 13: Apache Iceberg small-file metadata compaction and manifest rewrite storm
    {
        "raw_asr": "basically our continuous streaming lakehouse pipeline suffered write latency spikes when micro batch flushes generated fifty thousand small parquet files across six storage knowed partitions um commit intervals were configured at ten seconds which bloated metadata manifests over eighteen gigabytes table commit operations failed when catalog r p c handlers timed out after sixty seconds buy blocking eighteen downstream ingestion workers data platform engineers mitigated the commit failure buy triggering background manifest compaction buy passing dash dash target manifest size bytes into table configur properties operators cleared dead files buy rewriting data manifests through maintenance procedures buy consolidating twenty small files into five hundred megabyte chunks while data reliability engineers right four automated iceberg commit probes tracking snapshot expiration lag",
        "refined_text": "Our continuous streaming lakehouse pipeline suffered write latency spikes when micro-batch flushes generated 50000 small Parquet files across 6 storage node partitions. Commit intervals were configured at 10 seconds, which bloated metadata manifests over 18 gigabytes. Table commit operations failed when catalog RPC handlers timed out after 60 seconds by blocking 18 downstream ingestion workers.\n\nData platform engineers mitigated the commit failure by triggering background manifest compaction by passing --target-manifest-size-bytes into table configuration properties.\n\nOperators cleared dead files by rewriting data manifests through maintenance procedures by consolidating 20 small files into 500 megabyte chunks while data reliability engineers write 4 automated Iceberg commit probes tracking snapshot expiration lag."
    },

    # Sample 14: Kafka partition key skew, hot-spotting, and salted re-partitioning
    {
        "raw_asr": "um our fraud detection stream pipeline experienced extreme partition skew when high volume merchant transactions overloaded partition zero across twelve broker knowed instances um single key transaction volumes reached thirty thousand events per second while remaining partitions processed four hundred events per second buy causing consumer lag to climb towards eight hundred thousand records stream task workers assigned to the hot partition experienced c p u thread saturation buy dropping twelve socket connections stream engineers eliminated the skew buy adding salted hashes to incoming merchant keys buy expanding stream repartitioning into sixteen partitions instead data platform operators tuned consumer fetch buffer limits buy specifying dash dash max poll records into worker configur parameters while operations engineers monitor three partition lag metrics tracking offset distribution",
        "refined_text": "Our fraud detection stream pipeline experienced extreme partition skew when high-volume merchant transactions overloaded partition 0 across 12 broker node instances. Single key transaction volumes reached 30000 events per second while remaining partitions processed 400 events per second by causing consumer lag to climb towards 800000 records.\n\nStream task workers assigned to the hot partition experienced CPU thread saturation by dropping 12 socket connections.\n\nStream engineers eliminated the skew by adding salted hashes to incoming merchant keys by expanding stream repartitioning into 16 partitions instead. Data platform operators tuned consumer fetch buffer limits by specifying --max-poll-records into worker configuration parameters while operations engineers monitor 3 partition lag metrics tracking offset distribution."
    },

    # Sample 15: Debezium PostgreSQL CDC connector schema evolution and replication slot failover
    {
        "raw_asr": "basically our change data capture streaming connectors broke during an online table alter operat on fifteen post gres databases um an unannounced column drop invalidated cached avro schema registry definitions buy causing kafka connect tasks to crash on parsing errors logical replication slots accumulated forty gigabytes wait seventy gigabytes of write ahead logs instead buy pushing primary database disk utiliz towards ninety two percent database administrators restored replication streaming buy manually updating the avro schema history topic buy skipping the invalid d d l revision through connector configur updates platform engineers stabilized log retention buy configuring max underscore slot underscore wal underscore keep underscore size buy passing dash dash slot config into debezium workers while site reliability engineers right three replication lag alarms verifying schema synchronizat",
        "refined_text": "Our change data capture streaming connectors broke during an online table alter operation on 15 Postgres databases. An unannounced column drop invalidated cached Avro schema registry definitions by causing Kafka Connect tasks to crash on parsing errors. Logical replication slots accumulated 70 gigabytes of write-ahead logs instead by pushing primary database disk utilization towards 92 percent.\n\nDatabase administrators restored replication streaming by manually updating the Avro schema history topic by skipping the invalid DDL revision through connector configuration updates.\n\nPlatform engineers stabilized log retention by configuring max_slot_wal_keep_size by passing --slot-config into Debezium workers while site reliability engineers write 3 replication lag alarms verifying schema synchronization."
    },

    # Sample 16: Apache Flink RocksDB off-heap memory leak and Linux cgroup OOM kill
    {
        "raw_asr": "okay so our stateful stream aggregation jobs suffered sudden worker crashes when four flink task managers were terminated buy kernel cgroup out of memory killers across eight compute knowed hosts um rocksdb off heap memtables exceeded configured buffer boundaries buy consuming eight gigabytes wait twelve gigabytes of untracked native memory instead task manager processes were killed every forty minutes buy triggering continuous job graph restarts and state recovery cascades platform engineers eliminated the off heap memory leak buy enabling managed off heap memory bounds in flink configur settings buy setting state underscore backend underscore rocksdb underscore memory underscore managed to true operators constrained native block caches buy writing slash data storage limits while site reliability engineers right three c p u and memory utilization monitors tracking resident set size growth",
        "refined_text": "Our stateful stream aggregation jobs suffered sudden worker crashes when 4 Flink task managers were terminated by kernel cgroup out-of-memory killers across 8 compute node hosts. RocksDB off-heap memtables exceeded configured buffer boundaries by consuming 12 gigabytes of untracked native memory instead. Task manager processes were killed every 40 minutes by triggering continuous job graph restarts and state recovery cascades.\n\nPlatform engineers eliminated the off-heap memory leak by enabling managed off-heap memory bounds in Flink configuration settings by setting state_backend_rocksdb_memory_managed to true.\n\nOperators constrained native block caches by writing /data storage limits while site reliability engineers write 3 CPU and memory utilization monitors tracking resident set size growth."
    },

    # Sample 17: ClickHouse streaming ingestion buffer flushing and part merging saturation
    {
        "raw_asr": "basically our real time metrics ingestion pipeline failed when downstream clickhouse storage rejected high frequency stream inserts with too many parts errors um streaming ingestion daemons inserted twenty thousand records every two seconds buy creating sixty active data parts across twelve partition knowed disks merge tree background engines saturated c p u threads attempting continuous part merging buy falling three hundred merges behind schedule ingestion pipelines dropped fifteen thousand telemetry points over twenty minutes data engineers resolved the part saturation buy deploying an intermediate buffer queue buy accumulating batches up towards one hundred thousand rows instead before flushing buy specifying dash dash max insert block size rows into client configur parameters while developers right three async ingest monitors validating table write throughput",
        "refined_text": "Our real-time metrics ingestion pipeline failed when downstream ClickHouse storage rejected high-frequency stream inserts with too many parts errors. Streaming ingestion daemons inserted 20000 records every 2 seconds by creating 60 active data parts across 12 partition node disks. MergeTree background engines saturated CPU threads attempting continuous part merging by falling 300 merges behind schedule.\n\nIngestion pipelines dropped 15000 telemetry points over 20 minutes.\n\nData engineers resolved the part saturation by deploying an intermediate buffer queue by accumulating batches up towards 100000 rows instead before flushing by specifying --max-insert-block-size-rows into client configuration parameters while developers write 3 async ingest monitors validating table write throughput."
    },

    # Sample 18: Distributed watermark skew and late-arriving event drops in multi-source join
    {
        "raw_asr": "um our streaming analytics engine experienced severe data loss when an event join between click streams and transaction logs dropped eighteen percent of late arriving records across twelve stream workers um network routing jitter delayed transaction event partitions by fifteen minutes buy advancing the global watermark based on the faster click stream alone watermark generators emitted watermarks prematurely buy causing state cleanup routines to purge join windows before matching records arrived incident responders recovered event completeness buy extending allowed lateness from five minutes up towards twenty minutes instead buy recalculat watermark generation thresholds across both input streams system engineers tuned watermark underscore lag parameters buy specifying dash dash watermark delay into job configur specifications while developers right four stream validation tests verifying join completeness",
        "refined_text": "Our streaming analytics engine experienced severe data loss when an event join between click streams and transaction logs dropped 18 percent of late-arriving records across 12 stream workers. Network routing jitter delayed transaction event partitions by 15 minutes by advancing the global watermark based on the faster click stream alone. Watermark generators emitted watermarks prematurely by causing state cleanup routines to purge join windows before matching records arrived.\n\nIncident responders recovered event completeness by extending allowed lateness from 5 minutes up towards 20 minutes instead by recalculating watermark generation thresholds across both input streams.\n\nSystem engineers tuned watermark_lag parameters by specifying --watermark-delay into job configuration specifications while developers write 4 stream validation tests verifying join completeness."
    },

    # Sample 19: Kafka consumer cooperative rebalance and static group membership under rolling deploy
    {
        "raw_asr": "okay so our stream processing clusters suffered widespread message processing halts during rolling deployments across forty eight consumer knowed instances um dynamic consumer rebalances revoked all partition assignments on every worker pod restart buy creating sixteen sequential rebalance waves over thirty five minutes downstream consumers experienced ninety percent c p u utiliz spikes while the group underscore coordinator broker reassigned partitions incident responders resolved deployment rebalance storms buy enabling cooperative sticky assignors and static group membership buy assigning unique group underscore instance underscore id values to worker pods platform operators tuned session underscore timeout underscore ms towards sixty seconds buy passing dash dash session timeout into consumer configur files while site reliability engineers monitor three rebalance duration metrics verifying zero partition reassignments during updates",
        "refined_text": "Our stream processing clusters suffered widespread message processing halts during rolling deployments across 48 consumer node instances. Dynamic consumer rebalances revoked all partition assignments on every worker pod restart by creating 16 sequential rebalance waves over 35 minutes. Downstream consumers experienced 90 percent CPU utilization spikes while the group_coordinator broker reassigned partitions.\n\nIncident responders resolved deployment rebalance storms by enabling cooperative sticky assignors and static group membership by assigning unique group_instance_id values to worker pods.\n\nPlatform operators tuned session_timeout_ms towards 60 seconds by passing --session-timeout into consumer configuration files while site reliability engineers monitor 3 rebalance duration metrics verifying zero partition reassignments during updates."
    },

    # Sample 20: Apache Arrow Flight streaming RPC zero-copy memory transfer bottleneck
    {
        "raw_asr": "basically our real time feature store ingestion stalled when arrow flight r p c streaming endpoints exhausted kernel socket memory across sixteen worker knowed hosts um microservice consumers requested forty thousand columnar vectors per second which triggered direct memory allocat bottlenecks when zero copy buffers failed to release off heap pointers task workers experienced heavy c p u spin lock contention buy dropping twenty five r p c connections while client request latency jumped from two milliseconds up through twelve hundred milliseconds system architects eliminated the socket memory exhaustion buy enabling d m a buffer pool reuse buy capping flight batch underscore size to four thousand records instead engineers passed dash dash flight buffer size into daemon configur parameters while developers right four streaming r p c integration tests validating memory reclamation health",
        "refined_text": "Our real-time feature store ingestion stalled when Arrow Flight RPC streaming endpoints exhausted kernel socket memory across 16 worker node hosts. Microservice consumers requested 40000 columnar vectors per second, which triggered direct memory allocation bottlenecks when zero-copy buffers failed to release off-heap pointers. Task workers experienced heavy CPU spin lock contention by dropping 25 RPC connections while client request latency jumped from 2 milliseconds up through 1200 milliseconds.\n\nSystem architects eliminated the socket memory exhaustion by enabling DMA buffer pool reuse by capping flight batch_size to 4000 records instead.\n\nEngineers passed --flight-buffer-size into daemon configuration parameters while developers write 4 streaming RPC integration tests validating memory reclamation health."
    },
]

def main():
    print(f"Total samples defined: {len(samples)}")
    
    # Check eval set leakage
    leakage = False
    for i, s in enumerate(samples):
        r = s["raw_asr"].strip().lower()
        rf = s["refined_text"].strip()
        if r in eval_raws:
            print(f"ERROR: Sample {i+1} raw_asr leaks into eval set!")
            leakage = True
        if rf in eval_refs:
            print(f"ERROR: Sample {i+1} refined_text leaks into eval set!")
            leakage = True
    if not leakage:
        print("PASS: Eval leakage check clean (0 overlaps).")

    # Validate each pair
    all_valid = True
    for i, s in enumerate(samples):
        v_ok, v_reason = validate_pair(s, min_noise_layers=4)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        layers = count_active_noise_layers(s["raw_asr"])
        layer_count = get_noise_layer_count(s["raw_asr"])
        words = len(s["refined_text"].split())
        
        status = "OK" if (v_ok and c_reason == "kept") else "FAIL"
        if status == "FAIL":
            all_valid = False
            print(f"Sample {i+1} (words: {words}, layers: {layer_count}): {status}")
            if not v_ok:
                print(f"  Validator: {v_reason}")
            if c_reason != "kept":
                print(f"  Cleaner: {c_reason}")
        else:
            print(f"Sample {i+1} (words: {words}, layers: {layer_count}): PASS")

    # Batch validation
    batch_ok, batch_reason, metrics = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
    print("\nBatch Validation Result:")
    print("  Status:", "PASS" if batch_ok else "FAIL")
    print("  Reason:", batch_reason)
    print("  Metrics:", json.dumps(metrics, indent=2))

    if all_valid and batch_ok:
        out_path = Path("scratch/subagent_batch_137.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")

if __name__ == "__main__":
    main()
