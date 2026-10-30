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
# Batch 147 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 noise layers active.
    # =========================================================================

    # Sample 1: Pulsar streaming cursor offset deduplication
    {
        "raw_asr": "um deduplicat streaming cursor offsets buy reading ledger underscore id across the r p c broker topic",
        "refined_text": "Deduplicate streaming cursor offsets by reading ledger_id across the RPC broker topic."
    },

    # Sample 2: Stream partition event latency recalculation
    {
        "raw_asr": "uh recalculat partition event latency buy checking watermark underscore lag while c p u metrics stabilize",
        "refined_text": "Recalculate partition event latency by checking watermark_lag while CPU metrics stabilize."
    },

    # Sample 3: Redpanda direct I/O memory allocation
    {
        "raw_asr": "basically allocat four d m a chunk buffers buy mounting slash data streaming segment files",
        "refined_text": "Allocate 4 DMA chunk buffers by mounting /data streaming segment files."
    },

    # Sample 4: Kafka consumer group session termination
    {
        "raw_asr": "um terminat stalled consumer group sessions buy resetting commit underscore offset instead",
        "refined_text": "Terminate stalled consumer group sessions by resetting commit_offset instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active.
    # =========================================================================

    # Sample 5: Apache Flink two-phase commit sink transaction timeout
    {
        "raw_asr": "basically our flink stream pipeline suffered sink transaction timeouts after fifteen task workers wait thirty workers instead failed commit synchronizat at broker knowed checkpoints you know operators resolved sink commits buy passing dash dash transaction timeout into connector configur parameters buy mounting slash checkpoint state storage while engineers inspect r p c commit latencies across the network",
        "refined_text": "Our Flink stream pipeline suffered sink transaction timeouts after 30 workers instead failed commit synchronization at broker node checkpoints.\n\nOperators resolved sink commits by passing --transaction-timeout into connector configuration parameters by mounting /checkpoint state storage while engineers inspect RPC commit latencies across the network."
    },

    # Sample 6: Apache Pulsar BookKeeper ledger rollover and write cache allocation
    {
        "raw_asr": "um our stream ingestion cluster stalled bookkeeper ledger rollover when four bookies wait eight bookies instead saturated write cache allocat across broker knowed storage volumes you know stream operators restored journal write throughput buy passing dash dash ledger rollover size into bookie configur files buy tracking ledger underscore id offsets while site reliability engineers right two c p u throttling probes",
        "refined_text": "Our stream ingestion cluster stalled BookKeeper ledger rollover when 8 bookies instead saturated write cache allocation across broker node storage volumes.\n\nStream operators restored journal write throughput by passing --ledger-rollover-size into bookie configuration files by tracking ledger_id offsets while site reliability engineers write 2 CPU throttling probes."
    },

    # Sample 7: Redpanda Raft leader election flapping and quorum arbitration
    {
        "raw_asr": "basically our redpanda stream cluster encountered frequent leader election flapping when four partition leaders wait eight partition leaders instead dropped heartbeat packets across knowed brokers uh cluster operators stabilized raft quorum arbitrat buy setting election timeout values buy passing dash dash election timeout into broker configur files buy storing segments in slash var data directories while engineers right two synthetic r p c latency monitors",
        "refined_text": "Our Redpanda stream cluster encountered frequent leader election flapping when 8 partition leaders instead dropped heartbeat packets across node brokers.\n\nCluster operators stabilized Raft quorum arbitration by setting election timeout values by passing --election-timeout into broker configuration files by storing segments in /var data directories while engineers write 2 synthetic RPC latency monitors."
    },

    # Sample 8: ClickHouse stream ingestion buffer flushing and ReplacingMergeTree dedup
    {
        "raw_asr": "um our clickhouse stream ingestion failed batch buffer flushing when memory tables exhausted d m a page buffers across twelve worker knowed instances basically engineers restored stream write throughput buy passing dash dash max insert block size into ingestion client configur parameters buy tracking insert underscore block underscore id while operators wait five hundred rows instead to deduplicat raw telemetry before triggering c p u intensive part merges",
        "refined_text": "Our ClickHouse stream ingestion failed batch buffer flushing when memory tables exhausted DMA page buffers across 12 worker node instances.\n\nEngineers restored stream write throughput by passing --max-insert-block-size into ingestion client configuration parameters by tracking insert_block_id while operators wait 500 rows instead to deduplicate raw telemetry before triggering CPU intensive part merges."
    },

    # Sample 9: Apache Iceberg streaming metadata commit conflict and catalog initialization
    {
        "raw_asr": "basically our iceberg streaming ingestion crashed on metadata snapshot conflicts when ten concurrent writer tasks wait twenty retries instead timed out table catalog initializ across knowed workers uh platform engineers stabilized catalog communicat buy passing dash dash commit retry num into table configur properties buy recording snapshot underscore id metadata into post gres catalogs while streaming operators monitor commit latencies",
        "refined_text": "Our Iceberg streaming ingestion crashed on metadata snapshot conflicts when 20 retries instead timed out table catalog initialization across node workers.\n\nPlatform engineers stabilized catalog communication by passing --commit-retry-num into table configuration properties by recording snapshot_id metadata into Postgres catalogs while streaming operators monitor commit latencies."
    },

    # Sample 10: Ray Core streaming actor plasma object store spill
    {
        "raw_asr": "um our streaming ray cluster suffered worker halts when plasma object store allocat spilled sixteen gigabytes wait thirty gigabytes instead across worker knowed instances so um platform operators stabilized worker memory buy passing dash dash object store memory into cluster configur files buy spilling temporary batches into slash tmp storage while developers right two a sink batching pipelines balancing c p u thread queues",
        "refined_text": "Our streaming Ray cluster suffered worker halts when plasma object store allocation spilled 30 gigabytes instead across worker node instances.\n\nPlatform operators stabilized worker memory by passing --object-store-memory into cluster configuration files by spilling temporary batches into /tmp storage while developers write 2 async batching pipelines balancing CPU thread queues."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # At least 4 noise layers active.
    # =========================================================================

    # Sample 11: Kafka KRaft metadata quorum election and split-brain recovery
    {
        "raw_asr": "basically during our morning peak ingest wave a network partition isolated three kraft metadata controllers across nine broker knowed instances um the quorum voters failed leader election arbitrat when heartbeat packet drops reached twenty seconds wait thirty seconds instead buy causing metadata split brain warnings across twenty four streaming partitions metadata logs fell six thousand records behind while downstream partition leaders rejected client r p c requests buy triggering severe ingest backpressure site reliability engineers stabilized the kraft cluster buy passing dash dash controller quorum voters into broker configur files buy synchronizat of metadata log files inside slash data kraft storage volumes operators resolved election flapping buy setting broker underscore id mapping while developers right three c p u health probes tracking election latency across the cluster",
        "refined_text": "During our morning peak ingest wave, a network partition isolated 3 KRaft metadata controllers across 9 broker node instances. The quorum voters failed leader election arbitration when heartbeat packet drops reached 30 seconds instead by causing metadata split-brain warnings across 24 streaming partitions. Metadata logs fell 6000 records behind while downstream partition leaders rejected client RPC requests by triggering severe ingest backpressure.\n\nSite reliability engineers stabilized the KRaft cluster by passing --controller-quorum-voters into broker configuration files by synchronization of metadata log files inside /data kraft storage volumes.\n\nOperators resolved election flapping by setting broker_id mapping while developers write 3 CPU health probes tracking election latency across the cluster."
    },

    # Sample 12: Apache Flink broadcast state pattern matching memory spill
    {
        "raw_asr": "um our stateful stream processing job suffered out of memory crashes when dynamic rule evaluation broadcasted forty thousand fraud detection rules across sixty four task manager knowed slots basically local broadcast state memory tables exceeded configured limits when rule updates spiked buy consuming twenty megabytes wait forty megabytes of heap memory instead buy triggering severe garbage collection pauses across worker processes task manager threads were paused for forty five seconds buy causing checkpoint barrier alignment timeouts across twenty subtasks data streaming engineers mitigated memory exhaustion buy passing dash dash broadcast state memory into worker configur parameters buy recalculat of rule memory footprint buy tuning rule underscore id eviction policies operators constrained state snapshots buy writing checkpoint records into slash checkpoint storage while developers right two d m a memory probes monitoring worker c p u saturation",
        "refined_text": "Our stateful stream processing job suffered out-of-memory crashes when dynamic rule evaluation broadcasted 40000 fraud detection rules across 64 task manager node slots. Local broadcast state memory tables exceeded configured limits when rule updates spiked by consuming 40 megabytes of heap memory instead by triggering severe garbage collection pauses across worker processes. Task manager threads were paused for 45 seconds by causing checkpoint barrier alignment timeouts across 20 subtasks.\n\nData streaming engineers mitigated memory exhaustion by passing --broadcast-state-memory into worker configuration parameters by recalculation of rule memory footprint by tuning rule_id eviction policies.\n\nOperators constrained state snapshots by writing checkpoint records into /checkpoint storage while developers write 2 DMA memory probes monitoring worker CPU saturation."
    },

    # Sample 13: Delta Lake streaming liquid clustering and write amplification
    {
        "raw_asr": "basically our streaming lakehouse ingestion encountered severe write amplification when micro batch commits generated five hundred small parquet files wait eight hundred files instead across twelve storage knowed partitions um continuous streaming flushes wrote twenty thousand rows per second buy creating heavy metadata commit contention at table catalog endpoints background clustering jobs saturated disk throughput while streaming write tasks failed schema validation buy stalling downstream analytics for twenty minutes data engineers resolved the write amplification buy enabling liquid clustering buy passing dash dash cluster columns into table configur options buy grouping events buy partition key attributes data platform operators deduplicat event records buy matching batch underscore id and commit underscore version metadata buy storing optimized tables inside slash data delta storage while developers right four c p u telemetry monitors verifying compaction throughput",
        "refined_text": "Our streaming lakehouse ingestion encountered severe write amplification when micro-batch commits generated 800 small Parquet files instead across 12 storage node partitions. Continuous streaming flushes wrote 20000 rows per second by creating heavy metadata commit contention at table catalog endpoints. Background clustering jobs saturated disk throughput while streaming write tasks failed schema validation by stalling downstream analytics for 20 minutes.\n\nData engineers resolved the write amplification by enabling liquid clustering by passing --cluster-columns into table configuration options by grouping events by partition key attributes.\n\nData platform operators deduplicate event records by matching batch_id and commit_version metadata by storing optimized tables inside /data delta storage while developers write 4 CPU telemetry monitors verifying compaction throughput."
    },

    # Sample 14: Apache Pulsar tiered storage offloading to S3 and BookKeeper ledger compaction stall
    {
        "raw_asr": "um our enterprise message broker cluster faced catastrophic disk saturation when bookkeeper ledger offloading stalled across sixteen broker knowed hosts basically local journal volumes reached ninety percent disk allocat when tiered storage offloaders encountered s three request throttling after ledgers accumulated twenty gigabytes wait thirty gigabytes instead bookie storage daemons began entering read only mode buy blocking incoming streaming writes across forty topic partitions site reliability engineers mitigated the ledger backlog buy passing dash dash managed ledger offload threshold into broker configur parameters buy enabling parallel ledger offload workers buy tracking ledger underscore id progress operators terminat stalled offload tasks buy mounting journal directories inside slash var pulsar storage while platform engineers right two synthetic r p c health monitors tracking write latency recovery",
        "refined_text": "Our enterprise message broker cluster faced catastrophic disk saturation when BookKeeper ledger offloading stalled across 16 broker node hosts. Local journal volumes reached 90 percent disk allocation when tiered storage offloaders encountered S3 request throttling after ledgers accumulated 30 gigabytes instead. Bookie storage daemons began entering read-only mode by blocking incoming streaming writes across 40 topic partitions.\n\nSite reliability engineers mitigated the ledger backlog by passing --managed-ledger-offload-threshold into broker configuration parameters by enabling parallel ledger offload workers by tracking ledger_id progress.\n\nOperators terminate stalled offload tasks by mounting journal directories inside /var pulsar storage while platform engineers write 2 synthetic RPC health monitors tracking write latency recovery."
    },

    # Sample 15: Debezium MySQL binlog connector GTID purge and replication slot desynchronization
    {
        "raw_asr": "basically our change data capture streaming infrastructure suffered critical pipeline desynchronization when upstream database maintenance purged binary logs across eight database knowed instances um the connector worker crashed during schema initializ after network disconnects delayed replication buy forty seconds wait sixty seconds instead buy causing missing gtid events across fifteen streaming tables kafka connect tasks failed with unrecoverable binlog position exceptions buy halting real time table synchronizat across our data warehouse data platform engineers recovered the c d c pipeline buy passing dash dash database server id into connector configur definitions buy resetting gtid underscore set and binlog underscore position coordinates operators restored schema snapshot communicat buy caching metadata inside slash tmp cdc storage while site reliability engineers right two c p u utilization monitors verifying replication stream stability",
        "refined_text": "Our change data capture streaming infrastructure suffered critical pipeline desynchronization when upstream database maintenance purged binary logs across 8 database node instances. The connector worker crashed during schema initialization after network disconnects delayed replication by 60 seconds instead by causing missing GTID events across 15 streaming tables. Kafka Connect tasks failed with unrecoverable binlog position exceptions by halting real-time table synchronization across our data warehouse.\n\nData platform engineers recovered the CDC pipeline by passing --database-server-id into connector configuration definitions by resetting gtid_set and binlog_position coordinates.\n\nOperators restored schema snapshot communication by caching metadata inside /tmp cdc storage while site reliability engineers write 2 CPU utilization monitors verifying replication stream stability."
    },

    # Sample 16: ScyllaDB streaming write commitlog fsync latency and token-aware driver shard saturation
    {
        "raw_asr": "um our high throughput telemetry ingestion cluster experienced severe write rejection when scylladb storage engines saturated commitlog disk write queues across twelve database knowed instances basically streaming client write latencies climbed from two milliseconds up through twenty milliseconds wait thirty milliseconds instead buy causing token aware driver pools to exhaust socket connections across forty client workers worker threads experienced heavy memory allocat stalls while commitlog fsync operations delayed mutation writes past five seconds site reliability engineers eliminated write queuing buy passing dash dash commitlog sync into database configur parameters buy switching commitlog batching to periodic mode buy tracking shard underscore id assignments database operators unblocked disk queues buy mounting nvme volumes under slash data scylla storage while data platform engineers right three d m a throughput probes monitoring client timeout metrics",
        "refined_text": "Our high-throughput telemetry ingestion cluster experienced severe write rejection when ScyllaDB storage engines saturated commitlog disk write queues across 12 database node instances. Streaming client write latencies climbed from 2 milliseconds up through 30 milliseconds instead by causing token-aware driver pools to exhaust socket connections across 40 client workers. Worker threads experienced heavy memory allocation stalls while commitlog fsync operations delayed mutation writes past 5 seconds.\n\nSite reliability engineers eliminated write queuing by passing --commitlog-sync into database configuration parameters by switching commitlog batching to periodic mode by tracking shard_id assignments.\n\nDatabase operators unblocked disk queues by mounting NVMe volumes under /data scylla storage while data platform engineers write 3 DMA throughput probes monitoring client timeout metrics."
    },

    # Sample 17: Milvus vector streaming ingest segment WAL replay and HNSW index queue saturation
    {
        "raw_asr": "basically our real time vector search ingestion stalled when high dimensional embedding streams overloaded segment write ahead logs across sixteen query knowed instances um streaming indexer daemons attempted continuous hnsw graph construction buy consuming twenty gigabytes of memory allocat across eight worker nodes when unindexed segment buffers expanded to two hundred megabytes wait five hundred megabytes instead index building queues accumulated four hundred thousand unprocessed vectors buy driving query p ninety nine latency from ten milliseconds up through eight hundred milliseconds platform engineers stabilized streaming ingest buy passing dash dash segment max size into indexer configur settings buy tuning segment underscore id flushing intervals system operators optimized raw vector storage buy mounting slash data milvus volumes while developers right four c p u thread monitors validating vector dim consistency during ingestion",
        "refined_text": "Our real-time vector search ingestion stalled when high-dimensional embedding streams overloaded segment write-ahead logs across 16 query node instances. Streaming indexer daemons attempted continuous HNSW graph construction by consuming 20 gigabytes of memory allocation across 8 worker nodes when unindexed segment buffers expanded to 500 megabytes instead. Index building queues accumulated 400000 unprocessed vectors by driving query P99 latency from 10 milliseconds up through 800 milliseconds.\n\nPlatform engineers stabilized streaming ingest by passing --segment-max-size into indexer configuration settings by tuning segment_id flushing intervals.\n\nSystem operators optimized raw vector storage by mounting /data milvus volumes while developers write 4 CPU thread monitors validating vector dim consistency during ingestion."
    },

    # Sample 18: Apache Arrow DataFusion streaming query pipeline memory exhaustion and spill bottleneck
    {
        "raw_asr": "um our distributed stream analytics engine suffered critical task failures when in memory hash aggregation operators exhausted heap memory across eight streaming knowed workers basically high cardinality telemetry group buy operations generated sixty thousand distinct state keys per second buy triggering direct memory allocat spills across worker processes when task memory usage climbed beyond four gigabytes wait eight gigabytes instead the engine began uncompressed spill to disk operations buy saturating local drive bandwidth and delaying stream responses for forty seconds data streaming architects mitigated worker crashes buy passing dash dash memory limit into executor configur options buy recalculat of streaming hash partition boundaries buy tuning batch underscore size and memory underscore fraction parameters engineers redirected spilled intermediate files buy configuring slash tmp datafusion mount points while developers right three d m a streaming probes tracking r p c serialization health",
        "refined_text": "Our distributed stream analytics engine suffered critical task failures when in-memory hash aggregation operators exhausted heap memory across 8 streaming node workers. High-cardinality telemetry group-by operations generated 60000 distinct state keys per second by triggering direct memory allocation spills across worker processes when task memory usage climbed beyond 8 gigabytes instead. The engine began uncompressed spill-to-disk operations by saturating local drive bandwidth and delaying stream responses for 40 seconds.\n\nData streaming architects mitigated worker crashes by passing --memory-limit into executor configuration options by recalculation of streaming hash partition boundaries by tuning batch_size and memory_fraction parameters.\n\nEngineers redirected spilled intermediate files by configuring /tmp datafusion mount points while developers write 3 DMA streaming probes tracking RPC serialization health."
    },

    # Sample 19: ClickHouse Kafka engine table consumer rebalance and materialized view deadlock
    {
        "raw_asr": "basically our clickhouse real time ingestion cluster experienced repeated consumer stalls when kafka engine tables failed background stream synchronizat across sixteen worker knowed instances um materialized view triggers attempted parallel table inserts across twenty partitions which locked target table partitions when consumer polling exceeded fifteen seconds wait thirty seconds instead buy causing kafka brokers to revoke partition assignments rebalance storms terminated sixty streaming consumer threads buy leaving four hundred thousand raw events buffered in memory database administrators resolved the insertion deadlocks buy passing dash dash kafka max block size into engine configur scripts buy deduplicat of incoming event blocks buy setting consumer underscore group and topic underscore name parameters platform engineers cleared corrupt consumer offsets inside slash var clickhouse directories while site reliability engineers right three c p u thread latency monitors verifying stream ingestion continuity",
        "refined_text": "Our ClickHouse real-time ingestion cluster experienced repeated consumer stalls when Kafka engine tables failed background stream synchronization across 16 worker node instances. Materialized view triggers attempted parallel table inserts across 20 partitions, which locked target table partitions when consumer polling exceeded 30 seconds instead by causing Kafka brokers to revoke partition assignments. Rebalance storms terminated 60 streaming consumer threads by leaving 400000 raw events buffered in memory.\n\nDatabase administrators resolved the insertion deadlocks by passing --kafka-max-block-size into engine configuration scripts by deduplication of incoming event blocks by setting consumer_group and topic_name parameters.\n\nPlatform engineers cleared corrupt consumer offsets inside /var clickhouse directories while site reliability engineers write 3 CPU thread latency monitors verifying stream ingestion continuity."
    },

    # Sample 20: Apache Spark Structured Streaming RocksDB state store changelog checkpoint lag
    {
        "raw_asr": "um our stateful spark streaming pipeline experienced severe micro batch execution delays when rocksdb state store changelog uploads lagged behind trigger intervals across thirty two executor knowed slots basically continuous session window aggregations maintained eighty thousand active customer sessions buy creating sixty megabytes of write ahead changelogs on every micro batch commit when cloud storage upload latencies increased from five seconds up through twenty seconds wait sixty seconds instead streaming executors missed consecutive trigger schedules buy causing consumer lag to climb towards five hundred thousand records data platform architects eliminated state commit lag buy passing dash dash checkpoint location into spark configur parameters buy recalculat of state store memtable flush thresholds buy tracking state underscore store underscore id and commit underscore offset metadata streaming engineers mounted snapshot backup targets inside slash checkpoint spark storage while developers right two post gres metrics probes tracking executor c p u saturation",
        "refined_text": "Our stateful Spark streaming pipeline experienced severe micro-batch execution delays when RocksDB state store changelog uploads lagged behind trigger intervals across 32 executor node slots. Continuous session window aggregations maintained 80000 active customer sessions by creating 60 megabytes of write-ahead changelogs on every micro-batch commit. When cloud storage upload latencies increased from 5 seconds up through 60 seconds instead, streaming executors missed consecutive trigger schedules by causing consumer lag to climb towards 500000 records.\n\nData platform architects eliminated state commit lag by passing --checkpoint-location into Spark configuration parameters by recalculation of state store memtable flush thresholds by tracking state_store_id and commit_offset metadata.\n\nStreaming engineers mounted snapshot backup targets inside /checkpoint spark storage while developers write 2 Postgres metrics probes tracking executor CPU saturation."
    }
]

print(f"Total samples defined: {len(samples)}")
assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

# 1. Check eval leakage
leakage = False
for idx, s in enumerate(samples):
    r = s["raw_asr"].strip().lower()
    o = s["refined_text"].strip()
    if r in eval_raws:
        print(f"LEAKAGE in sample {idx+1} raw_asr!")
        leakage = True
    if o in eval_refs:
        print(f"LEAKAGE in sample {idx+1} refined_text!")
        leakage = True
assert not leakage, "Found eval set leakage!"
print("PASS: Eval leakage check clean (0 overlaps).")

# 2. Validate individual pairs and cleaners
all_passed = True
for idx, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    layers = get_noise_layer_count(raw)
    layer_dict = count_active_noise_layers(raw)

    v_ok, v_msg = validate_pair(s, min_noise_layers=4)
    c_res, c_msg = clean_sample(raw, ref)

    if not v_ok:
        print(f"FAIL: Sample {idx+1} validate_pair: {v_msg}")
        all_passed = False
    elif c_msg != "kept":
        print(f"FAIL: Sample {idx+1} clean_sample: {c_msg}")
        all_passed = False
    else:
        print(f"Sample {idx+1} (words: {words}, layers: {layers}): PASS")

assert all_passed, "Some samples failed pair validation or cleaning!"

# 3. Validate batch
b_ok, b_msg, b_metrics = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print("\nBatch Validation Result:")
print(f"  Status: {'PASS' if b_ok else 'FAIL'}")
print(f"  Reason: {b_msg}")
print(f"  Metrics: {json.dumps(b_metrics, indent=2)}")

assert b_ok, f"Batch validation failed: {b_msg}"

# 4. Save to scratch/subagent_batch_147.json
out_file = Path("scratch/subagent_batch_147.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(samples, f, ensure_ascii=False, indent=2)

print(f"\nWROTE 20 verified samples to {out_file}")
