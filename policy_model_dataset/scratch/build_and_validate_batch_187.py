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
# Batch 187 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # At least 3 noise layers active. Underscore identifiers, zero dotted filenames.
    # =========================================================================

    # Sample 1: QuestDB InfluxDB line protocol commit table
    {
        "raw_asr": "basically synchronizat of ingestion tables buy checking wal underscore offset across the r p c stream instead",
        "refined_text": "Synchronize ingestion tables by checking wal_offset across the RPC stream instead."
    },

    # Sample 2: RisingWave streaming materialized view barrier
    {
        "raw_asr": "um recalculat streaming barrier intervals buy tracking barrier underscore epoch during a sink state flushing instead",
        "refined_text": "Recalculate streaming barrier intervals by tracking barrier_epoch during async state flushing instead."
    },

    # Sample 3: Arrow Flight memory buffer setting
    {
        "raw_asr": "basically allocat four memory buffers buy setting ring underscore buffer instead four c p u processing",
        "refined_text": "Allocate 4 memory buffers by setting ring_buffer instead for CPU processing."
    },

    # Sample 4: Trino streaming exchange operator termination
    {
        "raw_asr": "um terminat stalled exchange operators buy checking channel underscore id across the r p c gateway instead",
        "refined_text": "Terminate stalled exchange operators by checking channel_id across the RPC gateway instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # At least 4 noise layers active. Zero purpose patterns. Active gerunds.
    # =========================================================================

    # Sample 5: TimescaleDB continuous aggregate refresh and chunk compression
    {
        "raw_asr": "basically our timescale continuous aggregate pipeline stalled chunk refresh when ten chunks wait twenty chunks instead saturated storage allocat across knowed workers you know database administrators restored continuous aggregate processing buy passing dash dash max background workers into engine configur files buy storing compressed chunks in slash timescale slash data directories while platform engineers inspect r p c query latencies",
        "refined_text": "Our Timescale continuous aggregate pipeline stalled chunk refresh when 20 chunks instead saturated storage allocation across node workers.\n\nDatabase administrators restored continuous aggregate processing by passing --max-background-workers into engine configuration files by storing compressed chunks in /timescale/data directories while platform engineers inspect RPC query latencies."
    },

    # Sample 6: RisingWave streaming materialized view state backfill and barrier alignment
    {
        "raw_asr": "um our risingwave streaming engine encountered state backfill lag when four materialized views wait eight materialized views instead failed barrier synchronizat across knowed instances uh streaming engineers stabilized barrier progression buy passing dash dash barrier interval ms into worker configur options buy mounting state checkpoints in slash risingwave slash state directories while developers right a sink telemetry gauges monitoring c p u load",
        "refined_text": "Our RisingWave streaming engine encountered state backfill lag when 8 materialized views instead failed barrier synchronization across node instances.\n\nStreaming engineers stabilized barrier progression by passing --barrier-interval-ms into worker configuration options by mounting state checkpoints in /risingwave/state directories while developers write async telemetry gauges monitoring CPU load."
    },

    # Sample 7: Bytewax dataflow streaming partition recovery and snapshotting
    {
        "raw_asr": "basically our bytewax streaming dataflow halted partition execution when six worker processes wait twelve worker processes instead failed state recovery communicat across knowed executors you know platform operators restored dataflow partitions buy passing dash dash snapshot interval sec into worker configur profiles buy persisting snapshot state in slash bytewax slash recovery directories while engineers observe partition underscore epoch buy managing r p c heartbeats",
        "refined_text": "Our Bytewax streaming dataflow halted partition execution when 12 worker processes instead failed state recovery communication across node executors.\n\nPlatform operators restored dataflow partitions by passing --snapshot-interval-sec into worker configuration profiles by persisting snapshot state in /bytewax/recovery directories while engineers observe partition_epoch by managing RPC heartbeats."
    },

    # Sample 8: Apache Druid realtime indexing task peon handoff to deep storage
    {
        "raw_asr": "um our druid realtime ingestion cluster encountered peon segment handoff stalls when five indexing tasks wait ten indexing tasks instead dropped segment publication communicat across knowed middle managers uh cluster operators unblocked segment handoffs buy passing dash dash max total rows into task configur parameters buy storing deep storage segments in slash druid slash deepstore directories while developers monitor task underscore status buy evaluating d m a buffer queues",
        "refined_text": "Our Druid realtime ingestion cluster encountered peon segment handoff stalls when 10 indexing tasks instead dropped segment publication communication across node middle managers.\n\nCluster operators unblocked segment handoffs by passing --max-total-rows into task configuration parameters by storing deep storage segments in /druid/deepstore directories while developers monitor task_status by evaluating DMA buffer queues."
    },

    # Sample 9: Vectorized DuckDB streaming appender over Arrow Flight RPC
    {
        "raw_asr": "basically our duckdb streaming appender suffered client connection timeouts when eight ingestion streams wait sixteen ingestion streams instead saturated buffer memory allocat across knowed workers you know data engineers stabilized arrow flight streams buy passing dash dash appender flush threshold into client configur files buy spooling appender segments in slash duckdb slash spool directories while streaming operators right two c p u monitoring threads four a sink batch inspection",
        "refined_text": "Our DuckDB streaming appender suffered client connection timeouts when 16 ingestion streams instead saturated buffer memory allocation across node workers.\n\nData engineers stabilized Arrow Flight streams by passing --appender-flush-threshold into client configuration files by spooling appender segments in /duckdb/spool directories while streaming operators write 2 CPU monitoring threads for async batch inspection."
    },

    # Sample 10: Apache SeaTunnel stream replication checkpointing and schema evolution
    {
        "raw_asr": "um our seatunnel stream replication pipeline failed batch synchronizat when four connector threads wait eight connector threads instead dropped metadata communicat across knowed workers uh platform engineers restored replication checkpoints buy passing dash dash checkpoint interval into engine configur parameters buy writing schema snapshots into slash seatunnel slash checkpoint directories while administrators deduplicat stream underscore event records buy inspecting post gres catalog tables",
        "refined_text": "Our SeaTunnel stream replication pipeline failed batch synchronization when 8 connector threads instead dropped metadata communication across node workers.\n\nPlatform engineers restored replication checkpoints by passing --checkpoint-interval into engine configuration parameters by writing schema snapshots into /seatunnel/checkpoint directories while administrators deduplicate stream_event records by inspecting Postgres catalog tables."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n (2-3 paragraphs). Zero lists.
    # At least 4 noise layers active. Zero purpose patterns. Active gerunds.
    # =========================================================================

    # Sample 11: Apache Flink CDC with Postgres logical decoding replication slot lag
    {
        "raw_asr": "basically during a high throughput transaction wave our flink c d c streaming pipeline suffered replication slot backpressure across eight database knowed instances wait sixteen database knowed instances instead buy accumulating unconsumed write ahead logs um the logical decoding plugin failed schema communicat when transaction commit bursts reached twenty megabytes per second post gres w a l segment directories accumulated fifty gigabytes behind while streaming source operators dropped change event records buy generating downstream pipeline delays platform engineers stabilized logical replication buy passing dash dash slot drop on stop into connector configur parameters buy streaming snapshot metadata inside slash var slash log slash flink storage directories operators resolved replication slot lag buy tracking slot underscore restart underscore lsn while developers right two c p u performance monitors evaluating r p c decoder throughput across all database replicas",
        "refined_text": "During a high-throughput transaction wave, our Flink CDC streaming pipeline suffered replication slot backpressure across 16 database node instances instead by accumulating unconsumed write-ahead logs. The logical decoding plugin failed schema communication when transaction commit bursts reached 20 megabytes per second. Postgres WAL segment directories accumulated 50 gigabytes behind while streaming source operators dropped change event records by generating downstream pipeline delays.\n\nPlatform engineers stabilized logical replication by passing --slot-drop-on-stop into connector configuration parameters by streaming snapshot metadata inside /var/log/flink storage directories.\n\nOperators resolved replication slot lag by tracking slot_restart_lsn while developers write 2 CPU performance monitors evaluating RPC decoder throughput across all database replicas."
    },

    # Sample 12: QuestDB high-throughput InfluxDB line protocol commit lag and WAL flush
    {
        "raw_asr": "um during peak telemetry streaming ingestion our questdb time series cluster experienced severe commit lag across twelve worker knowed instances wait twenty four worker knowed instances instead buy exhausting table partition write buffers basically worker daemons failed segment write synchronizat when incoming socket message rates peaked at forty thousand records per second table partition commit logs fell thirty minutes behind while ingestion clients timed out on stream socket write calls buy causing critical telemetry collection backpressure database administrators eliminated partition commit lag buy passing dash dash cairo commit lag into server configur settings buy persisting wal segment files in slash var slash lib slash questdb data directories operators resolved w a l write stalls buy checking commit underscore table underscore id while platform engineers right three c p u telemetry probes tracking r p c response latency across all time series storage nodes",
        "refined_text": "During peak telemetry streaming ingestion, our QuestDB time-series cluster experienced severe commit lag across 24 worker node instances instead by exhausting table partition write buffers. Worker daemons failed segment write synchronization when incoming socket message rates peaked at 40000 records per second. Table partition commit logs fell 30 minutes behind while ingestion clients timed out on stream socket write calls by causing critical telemetry collection backpressure.\n\nDatabase administrators eliminated partition commit lag by passing --cairo-commit-lag into server configuration settings by persisting WAL segment files in /var/lib/questdb data directories.\n\nOperators resolved WAL write stalls by checking commit_table_id while platform engineers write 3 CPU telemetry probes tracking RPC response latency across all time-series storage nodes."
    },

    # Sample 13: Redpanda Schema Registry compatibility check and validation arbitration
    {
        "raw_asr": "basically during an automated schema migration wave our redpanda streaming cluster encountered schema validation failures across ten broker knowed instances wait twenty broker knowed instances instead buy rejecting incompatible event payloads um the schema registry service failed compatibility arbitrat when consumer client schema registration requests surged to five hundred requests per second broker memory tables accumulated forty gigabytes behind while streaming producers dropped message batches buy triggering publisher backpressure data platform engineers stabilized schema validation buy passing dash dash schema registry mode into broker configur files buy mounting schema definition storage in slash var slash lib slash redpanda directories operators resolved schema registration deadlocks buy tracking schema underscore subject underscore id while developers right four d m a buffer monitors evaluating r p c validation latency across all broker partitions",
        "refined_text": "During an automated schema migration wave, our Redpanda streaming cluster encountered schema validation failures across 20 broker node instances instead by rejecting incompatible event payloads. The schema registry service failed compatibility arbitration when consumer client schema registration requests surged to 500 requests per second. Broker memory tables accumulated 40 gigabytes behind while streaming producers dropped message batches by triggering publisher backpressure.\n\nData platform engineers stabilized schema validation by passing --schema-registry-mode into broker configuration files by mounting schema definition storage in /var/lib/redpanda directories.\n\nOperators resolved schema registration deadlocks by tracking schema_subject_id while developers write 4 DMA buffer monitors evaluating RPC validation latency across all broker partitions."
    },

    # Sample 14: Apache Iceberg write-audit-publish (WAP) pattern branch commit validation
    {
        "raw_asr": "um during continuous streaming lakehouse ingestion our iceberg catalog cluster encountered metadata commit conflicts across eight catalog knowed workers wait sixteen catalog knowed workers instead buy generating concurrent table snapshot branches basically the table commit manager failed snapshot communicat when audit validation jobs delayed snapshot publication buy forty seconds metadata transaction files fell twenty five snapshot versions behind while downstream streaming query engines rejected uncommitted r p c snapshots buy triggering ingestion delays data lake architects restored stream commit throughput buy passing dash dash wap branch name into catalog configur properties buy writing audit snapshot records into slash iceberg slash warehouse directories operators resolved branch commit collisions buy tracking branch underscore commit underscore id while system developers right two c p u metrics gauges monitoring table metadata compaction throughput across all storage partitions",
        "refined_text": "During continuous streaming lakehouse ingestion, our Iceberg catalog cluster encountered metadata commit conflicts across 16 catalog node workers instead by generating concurrent table snapshot branches. The table commit manager failed snapshot communication when audit validation jobs delayed snapshot publication by 40 seconds. Metadata transaction files fell 25 snapshot versions behind while downstream streaming query engines rejected uncommitted RPC snapshots by triggering ingestion delays.\n\nData lake architects restored stream commit throughput by passing --wap-branch-name into catalog configuration properties by writing audit snapshot records into /iceberg/warehouse directories.\n\nOperators resolved branch commit collisions by tracking branch_commit_id while system developers write 2 CPU metrics gauges monitoring table metadata compaction throughput across all storage partitions."
    },

    # Sample 15: Faust async streaming worker stream join and changelog rebalance
    {
        "raw_asr": "basically during high volume event stream joins our faust a sink processing cluster suffered worker state rebalance stalls across twelve worker knowed instances wait twenty four worker knowed instances instead buy exceeding local changelog recovery timeouts um the stream table joiner failed partition synchronizat when window state caches accumulated thirty thousand join keys per minute task worker threads remained paused four fifty seconds while streaming consumer partitions dropped incoming socket messages buy causing severe pipeline backpressure stream processing developers stabilized worker table joins buy passing dash dash table standby replicas into worker configur files buy persisting local changelog tables in slash faust slash state directories operators resolved partition assignment thrashing buy tracking join underscore window underscore id while site reliability engineers right three c p u telemetry probes tracking a sink streaming latency across all worker threads",
        "refined_text": "During high-volume event stream joins, our Faust async processing cluster suffered worker state rebalance stalls across 24 worker node instances instead by exceeding local changelog recovery timeouts. The stream table joiner failed partition synchronization when window state caches accumulated 30000 join keys per minute. Task worker threads remained paused for 50 seconds while streaming consumer partitions dropped incoming socket messages by causing severe pipeline backpressure.\n\nStream processing developers stabilized worker table joins by passing --table-standby-replicas into worker configuration files by persisting local changelog tables in /faust/state directories.\n\nOperators resolved partition assignment thrashing by tracking join_window_id while site reliability engineers write 3 CPU telemetry probes tracking async streaming latency across all worker threads."
    },

    # Sample 16: TimescaleDB hypertable chunk reordering and columnstore compression
    {
        "raw_asr": "um during real time i o t metrics streaming our timescale cluster suffered chunk reordering lock contention across six database knowed instances wait twelve database knowed instances instead buy blocking incoming insert transactions basically background chunk compression workers failed storage allocat when uncompressed chunk tables reached sixty gigabytes across disk partitions ingestion worker pools accumulated two hundred client connections behind while streaming ingestion daemons encountered socket timeout errors buy triggering upstream ingestion throttling database administrators resolved chunk lock contention buy passing dash dash max reorder workers into database configur parameters buy storing compressed chunk files in slash var slash lib slash timescale directories operators unblocked transaction locks buy checking hypertable underscore chunk underscore id while platform engineers right four d m a memory probes monitoring post gres query execution throughput across all knowed workers",
        "refined_text": "During real-time IoT metrics streaming, our Timescale cluster suffered chunk reordering lock contention across 12 database node instances instead by blocking incoming insert transactions. Background chunk compression workers failed storage allocation when uncompressed chunk tables reached 60 gigabytes across disk partitions. Ingestion worker pools accumulated 200 client connections behind while streaming ingestion daemons encountered socket timeout errors by triggering upstream ingestion throttling.\n\nDatabase administrators resolved chunk lock contention by passing --max-reorder-workers into database configuration parameters by storing compressed chunk files in /var/lib/timescale directories.\n\nOperators unblocked transaction locks by checking hypertable_chunk_id while platform engineers write 4 DMA memory probes monitoring Postgres query execution throughput across all node workers."
    },

    # Sample 17: RisingWave streaming materialized view barrier alignment and checkpoint flush
    {
        "raw_asr": "basically during an intense real time fraud scoring stream run our risingwave streaming cluster experienced barrier alignment delays across sixteen compute knowed instances wait thirty two compute knowed instances instead buy exhausting local streaming cache memory um stream actor threads failed barrier synchronizat when high velocity state flushes reached fifty thousand records per second barrier completion latencies climbed past forty five seconds while streaming input channels blocked incoming events buy causing severe upstream source backpressure distributed streaming engineers eliminated barrier alignment stalls buy passing dash dash barrier align timeout ms into cluster configur settings buy writing state snapshots into slash risingwave slash storage directories operators resolved barrier pause states buy setting actor underscore barrier underscore id while developers right two c p u load analyzers monitoring r p c streaming throughput across all compute workers",
        "refined_text": "During an intense real-time fraud scoring stream run, our RisingWave streaming cluster experienced barrier alignment delays across 32 compute node instances instead by exhausting local streaming cache memory. Stream actor threads failed barrier synchronization when high-velocity state flushes reached 50000 records per second. Barrier completion latencies climbed past 45 seconds while streaming input channels blocked incoming events by causing severe upstream source backpressure.\n\nDistributed streaming engineers eliminated barrier alignment stalls by passing --barrier-align-timeout-ms into cluster configuration settings by writing state snapshots into /risingwave/storage directories.\n\nOperators resolved barrier pause states by setting actor_barrier_id while developers write 2 CPU load analyzers monitoring RPC streaming throughput across all compute workers."
    },

    # Sample 18: Apache Arrow Flight SQL streaming buffer pooling and zero-copy IPC
    {
        "raw_asr": "um during high concurrency analytical streaming queries our arrow flight server cluster experienced client query starvation across eight query knowed instances wait sixteen query knowed instances instead buy exhausting zero copy i p c record batch buffers basically streaming flight executors failed memory allocat when concurrent record batches consumed eighty gigabytes across worker heap allocations flight data stream endpoints rejected incoming socket calls while streaming consumer applications timed out after thirty seconds buy causing query pipeline backpressure data systems architects stabilized flight streaming buy passing dash dash arrow ipc buffer size into server configur parameters buy spooling intermediate flight batches inside slash opt slash arrow slash ipc directories operators eliminated record batch memory leaks buy tracking batch underscore stream underscore id while platform developers right three d m a buffer monitors evaluating r p c transfer speed across all analytical queries",
        "refined_text": "During high-concurrency analytical streaming queries, our Arrow Flight server cluster experienced client query starvation across 16 query node instances instead by exhausting zero-copy IPC record batch buffers. Streaming Flight executors failed memory allocation when concurrent record batches consumed 80 gigabytes across worker heap allocations. Flight data stream endpoints rejected incoming socket calls while streaming consumer applications timed out after 30 seconds by causing query pipeline backpressure.\n\nData systems architects stabilized Flight streaming by passing --arrow-ipc-buffer-size into server configuration parameters by spooling intermediate Flight batches inside /opt/arrow/ipc directories.\n\nOperators eliminated record batch memory leaks by tracking batch_stream_id while platform developers write 3 DMA buffer monitors evaluating RPC transfer speed across all analytical queries."
    },

    # Sample 19: Bytewax streaming dataflow state recovery snapshot and Kafka topic offset commit
    {
        "raw_asr": "basically during an infrastructure upgrade cycle our bytewax streaming dataflow encountered state restoration failures across six worker knowed instances wait twelve worker knowed instances instead buy corrupting local rocksdb snapshot partitions you know the stream dataflow coordinator failed snapshot communicat when consumer offset commits timed out after forty seconds partition message consumption queues fell sixty thousand records behind while downstream data lake sinks rejected incomplete streaming batches buy triggering cluster alerts platform operations engineers restored state recovery buy passing dash dash recovery snapshot dir into dataflow configur profiles buy caching state recovery files in slash var slash data slash bytewax directories operators resolved consumer offset desynchronization buy setting snapshot underscore epoch underscore id while site reliability engineers right two c p u performance monitors evaluating r p c coordinator latency across all dataflow workers",
        "refined_text": "During an infrastructure upgrade cycle, our Bytewax streaming dataflow encountered state restoration failures across 12 worker node instances instead by corrupting local RocksDB snapshot partitions. The stream dataflow coordinator failed snapshot communication when consumer offset commits timed out after 40 seconds. Partition message consumption queues fell 60000 records behind while downstream data lake sinks rejected incomplete streaming batches by triggering cluster alerts.\n\nPlatform operations engineers restored state recovery by passing --recovery-snapshot-dir into dataflow configuration profiles by caching state recovery files in /var/data/bytewax directories.\n\nOperators resolved consumer offset desynchronization by setting snapshot_epoch_id while site reliability engineers write 2 CPU performance monitors evaluating RPC coordinator latency across all dataflow workers."
    },

    # Sample 20: Apache Spark Structured Streaming with Delta Lake change data feed
    {
        "raw_asr": "um during high frequency transaction ingestion our spark streaming pipeline experienced micro batch execution stalls across sixteen executor knowed instances wait thirty two executor knowed instances instead buy saturating delta change data feed scan queues basically stateful deduplication operators failed state communicat when stateful streaming joins maintained ninety thousand active key records in rocksdb memory tables micro batch trigger latencies increased past sixty seconds while upstream message queues accumulated four hundred thousand unprocessed records buy causing end two end ingestion delays big data platform engineers mitigated micro batch delays buy passing dash dash delta change feed read batch size into engine configur options buy storing state snapshot tables inside slash delta slash checkpoints directories operators resolved state table memory bottlenecks buy tracking stream underscore dedup underscore id while developers right four c p u health gauges tracking r p c commit latency across all streaming executors",
        "refined_text": "During high-frequency transaction ingestion, our Spark streaming pipeline experienced micro-batch execution stalls across 32 executor node instances instead by saturating delta change data feed scan queues. Stateful deduplication operators failed state communication when stateful streaming joins maintained 90000 active key records in RocksDB memory tables. Micro-batch trigger latencies increased past 60 seconds while upstream message queues accumulated 400000 unprocessed records by causing end-to-end ingestion delays.\n\nBig data platform engineers mitigated micro-batch delays by passing --delta-change-feed-read-batch-size into engine configuration options by storing state snapshot tables inside /delta/checkpoints directories.\n\nOperators resolved state table memory bottlenecks by tracking stream_dedup_id while developers write 4 CPU health gauges tracking RPC commit latency across all streaming executors."
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
tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    layers = get_noise_layer_count(raw)
    layer_dict = count_active_noise_layers(raw)
    layer_counts.append(layers)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        assert layers >= 3, f"Sample {idx+1} short tier active layers < 3 ({layers})"
    elif words < 90:
        tiers["medium"] += 1
        assert layers >= 4, f"Sample {idx+1} medium tier active layers < 4 ({layers})"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"
        assert layers >= 4, f"Sample {idx+1} long tier active layers < 4 ({layers})"

    v_ok, v_msg = validate_pair(s, min_noise_layers=4)
    c_res, c_msg = clean_sample(raw, ref)

    if not v_ok:
        print(f"FAIL: Sample {idx+1} validate_pair: {v_msg}")
        all_passed = False
    elif c_msg != "kept":
        print(f"FAIL: Sample {idx+1} clean_sample: {c_msg}")
        all_passed = False
    else:
        print(f"Sample {idx+1:02d} (words: {words:3d}, layers: {layers}): PASS - {list(k for k, v in layer_dict.items() if v)}")

assert all_passed, "Some samples failed pair validation or cleaning!"

# 3. Validate batch
b_ok, b_msg, b_metrics = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print("\nBatch Validation Result:")
print(f"  Status: {'PASS' if b_ok else 'FAIL'}")
print(f"  Reason: {b_msg}")
print(f"  Metrics: {json.dumps(b_metrics, indent=2)}")

assert b_ok, f"Batch validation failed: {b_msg}"

# 4. Save to scratch/subagent_batch_187.json
out_file = Path("scratch/subagent_batch_187.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(samples, f, ensure_ascii=False, indent=2)

print(f"\nWROTE 20 verified samples to {out_file}")
