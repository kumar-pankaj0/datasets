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

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
    # ----------------------------------------------------
    # Tier 1: Short (< 25 words) - 4 samples
    # ----------------------------------------------------
    {
        "raw_asr": "um deduplicat stream records buy reading partition underscore id across the r p c gateway",
        "refined_text": "Deduplicate stream records by reading partition_id across the RPC gateway."
    },
    {
        "raw_asr": "basically allocat four memory buffers buy setting buffer underscore size four a sink flushing",
        "refined_text": "Allocate 4 memory buffers by setting buffer_size for async flushing."
    },
    {
        "raw_asr": "uh recalculat partition event latency buy checking watermark underscore lag while c p u metrics stabilize",
        "refined_text": "Recalculate partition event latency by checking watermark_lag while CPU metrics stabilize."
    },
    {
        "raw_asr": "um terminat hanging consumer sessions buy resetting commit underscore offset inside knowed storage",
        "refined_text": "Terminate hanging consumer sessions by resetting commit_offset inside node storage."
    },

    # ----------------------------------------------------
    # Tier 2: Medium (25 - 89 words) - 6 samples
    # ----------------------------------------------------
    {
        "raw_asr": "basically our flink stream job encountered checkpoint barrier alignment delays after ten workers wait twenty workers instead failed state synchronizat across knowed tasks you know streaming engineers restored checkpoint throughput buy passing dash dash unaligned checkpoints into job configur parameters buy storing state in slash checkpoint state directories while developers monitor r p c commit latencies",
        "refined_text": "Our Flink stream job encountered checkpoint barrier alignment delays after 20 workers instead failed state synchronization across node tasks.\n\nStreaming engineers restored checkpoint throughput by passing --unaligned-checkpoints into job configuration parameters by storing state in /checkpoint state directories while developers monitor RPC commit latencies."
    },
    {
        "raw_asr": "um our kraft stream cluster suffered partition leader election delays when four broker replicas wait eight broker replicas instead dropped heartbeat communicat across knowed voters basically platform operators stabilized raft quorum arbitrat buy setting fetch session limits buy passing dash dash max poll interval ms into consumer configur files buy mounting slash data kafka directories while engineers right two c p u latency alerts",
        "refined_text": "Our KRaft stream cluster suffered partition leader election delays when 8 broker replicas instead dropped heartbeat communication across node voters.\n\nPlatform operators stabilized Raft quorum arbitration by setting fetch session limits by passing --max-poll-interval-ms into consumer configuration files by mounting /data kafka directories while engineers write 2 CPU latency alerts."
    },
    {
        "raw_asr": "basically our clickhouse ingestion pipeline stalled part merges when memory tables exhausted d m a buffers across twelve worker knowed instances uh stream engineers restored insert throughput buy passing dash dash max insert block size into client configur parameters buy tracking insert underscore block underscore id while operators wait five hundred batches instead to deduplicat raw event payloads before triggering c p u compression",
        "refined_text": "Our ClickHouse ingestion pipeline stalled part merges when memory tables exhausted DMA buffers across 12 worker node instances.\n\nStream engineers restored insert throughput by passing --max-insert-block-size into client configuration parameters by tracking insert_block_id while operators wait 500 batches instead to deduplicate raw event payloads before triggering CPU compression."
    },
    {
        "raw_asr": "um our iceberg streaming sink encountered snapshot conflicts when six concurrent writer tasks wait twelve writer tasks instead exceeded catalog commit retry limits across knowed workers basically data engineers stabilized catalog communicat buy passing dash dash commit retry num into table configur properties buy storing snapshot metadata in post gres catalogs while developers track r p c retry latency",
        "refined_text": "Our Iceberg streaming sink encountered snapshot conflicts when 12 writer tasks instead exceeded catalog commit retry limits across node workers.\n\nData engineers stabilized catalog communication by passing --commit-retry-num into table configuration properties by storing snapshot metadata in Postgres catalogs while developers track RPC retry latency."
    },
    {
        "raw_asr": "uh our pulsar broker cluster saturated journal write queues when four bookies wait eight bookies instead exceeded write cache allocat limits across storage knowed drives you know stream operators restored message throughput buy passing dash dash ledger rollover size into bookie configur files buy mounting slash mnt journal directories while developers right three a sink batching flusher threads",
        "refined_text": "Our Pulsar broker cluster saturated journal write queues when 8 bookies instead exceeded write cache allocation limits across storage node drives.\n\nStream operators restored message throughput by passing --ledger-rollover-size into bookie configuration files by mounting /mnt journal directories while developers write 3 async batching flusher threads."
    },
    {
        "raw_asr": "basically our debezium c d c connector paused change event streaming when the replication slot accumulated twelve gigabytes wait twenty four gigabytes instead across database knowed disks um data engineers restored slot synchronizat buy passing dash dash max batch size into connector configur options buy persisting l s n position inside post gres tables while operators right two c p u monitoring queries",
        "refined_text": "Our Debezium CDC connector paused change event streaming when the replication slot accumulated 24 gigabytes instead across database node disks.\n\nData engineers restored slot synchronization by passing --max-batch-size into connector configuration options by persisting LSN position inside Postgres tables while operators write 2 CPU monitoring queries."
    },

    # ----------------------------------------------------
    # Tier 3: Long (90+ words) - 10 samples
    # ----------------------------------------------------
    {
        "raw_asr": "basically during our morning peak stream traffic wave a network spike isolated three consumer group workers across twelve partition knowed instances um the stream consumers failed heartbeat communicat when heartbeat timeouts reached twenty seconds wait thirty seconds instead buy triggering a cascading partition rebalance storm across sixty streaming partitions partition consumer lag spiked forty thousand messages behind while upstream broker leaders rejected client r p c requests buy causing severe ingestion backpressure platform site reliability engineers stabilized consumer group arbitrat buy passing dash dash session timeout ms into consumer configur files buy mounting slash var kafka storage directories operators resolved partition flapping buy setting consumer underscore group underscore id while developers right two c p u latency monitors tracking consumer rebalance intervals across the cluster",
        "refined_text": "During our morning peak stream traffic wave, a network spike isolated 3 consumer group workers across 12 partition node instances. The stream consumers failed heartbeat communication when heartbeat timeouts reached 30 seconds instead by triggering a cascading partition rebalance storm across 60 streaming partitions. Partition consumer lag spiked 40000 messages behind while upstream broker leaders rejected client RPC requests by causing severe ingestion backpressure.\n\nPlatform site reliability engineers stabilized consumer group arbitration by passing --session-timeout-ms into consumer configuration files by mounting /var/kafka storage directories.\n\nOperators resolved partition flapping by setting consumer_group_id while developers write 2 CPU latency monitors tracking consumer rebalance intervals across the cluster."
    },
    {
        "raw_asr": "um during an intensive streaming backfill operation our flink stream cluster encountered checkpoint barrier timeouts across sixteen task workers wait thirty two task workers instead buy exhausting write buffer memory across stateful stream knowed instances checkpoint synchronizat failed when rocksdb memtable flushing stalled across forty managed operator state tables stream checkpoint lag reached fifteen minutes while downstream sinks rejected uncommitted r p c batches buy triggering pipeline stalls streaming engineers stabilized checkpoint write throughput buy passing dash dash state backend into cluster configur options buy persisting incremental state in slash checkpoint slash flink storage directories operators resolved memtable contention buy tracking operator underscore state underscore id while developers right three c p u execution gauges evaluating checkpoint duration across stateful tasks",
        "refined_text": "During an intensive streaming backfill operation, our Flink stream cluster encountered checkpoint barrier timeouts across 32 task workers instead by exhausting write buffer memory across stateful stream node instances. Checkpoint synchronization failed when RocksDB memtable flushing stalled across 40 managed operator state tables. Stream checkpoint lag reached 15 minutes while downstream sinks rejected uncommitted RPC batches by triggering pipeline stalls.\n\nStreaming engineers stabilized checkpoint write throughput by passing --state-backend into cluster configuration options by persisting incremental state in /checkpoint/flink storage directories.\n\nOperators resolved memtable contention by tracking operator_state_id while developers write 3 CPU execution gauges evaluating checkpoint duration across stateful tasks."
    },
    {
        "raw_asr": "basically during a sustained event burst our clickhouse streaming cluster halted batch insertions when memory parts exceeded table limits across eight ingestion knowed instances um the database failed asynchronous part merging when d m a buffer allocat stalled across twenty table partitions wait forty table partitions instead buy exhausting disk write queues unmerged data parts accumulated six hundred parts behind while ingestion clients received batch rejection r p c errors buy triggering producer backpressure database administrators stabilized table write availability buy passing dash dash max parts in total into server configur parameters buy storing wide parts in slash var slash clickhouse data directories operators resolved buffer starvation buy checking partition underscore merge underscore id while developers right two c p u compression probes tracking part merge speed across all disks",
        "refined_text": "During a sustained event burst, our ClickHouse streaming cluster halted batch insertions when memory parts exceeded table limits across 8 ingestion node instances. The database failed asynchronous part merging when DMA buffer allocation stalled across 40 table partitions instead by exhausting disk write queues. Unmerged data parts accumulated 600 parts behind while ingestion clients received batch rejection RPC errors by triggering producer backpressure.\n\nDatabase administrators stabilized table write availability by passing --max-parts-in-total into server configuration parameters by storing wide parts in /var/clickhouse data directories.\n\nOperators resolved buffer starvation by checking partition_merge_id while developers write 2 CPU compression probes tracking part merge speed across all disks."
    },
    {
        "raw_asr": "um during an automated streaming table maintenance pass our iceberg streaming engine suffered commit conflict aborts across six writer knowed tasks wait twelve writer tasks instead buy generating hundreds of small parquet files across thirty partitioned datasets metadata commit synchronizat failed when concurrent writers collided on table snapshot files table metadata versions fell eight commits behind while downstream stream consumers rejected invalid snapshot r p c responses buy causing read stalls data platform engineers stabilized metadata commit throughput buy passing dash dash commit num retries into catalog configur settings buy writing snapshot metadata into post gres database catalogs operators resolved commit aborts buy setting snapshot underscore commit underscore id while developers right four c p u health checks evaluating manifest rewrite duration across all partitions",
        "refined_text": "During an automated streaming table maintenance pass, our Iceberg streaming engine suffered commit conflict aborts across 12 writer tasks instead by generating hundreds of small Parquet files across 30 partitioned datasets. Metadata commit synchronization failed when concurrent writers collided on table snapshot files. Table metadata versions fell 8 commits behind while downstream stream consumers rejected invalid snapshot RPC responses by causing read stalls.\n\nData platform engineers stabilized metadata commit throughput by passing --commit-num-retries into catalog configuration settings by writing snapshot metadata into Postgres database catalogs.\n\nOperators resolved commit aborts by setting snapshot_commit_id while developers write 4 CPU health checks evaluating manifest rewrite duration across all partitions."
    },
    {
        "raw_asr": "basically during peak ingest rates our pulsar streaming brokers encountered entry log garbage collection lag across four storage bookies wait eight storage bookies instead buy exhausting journal write buffers across knowed drives bookkeeper journal allocat failed when concurrent ledger flushes saturated entry log disk space ledger sync delays accumulated two thousand milliseconds behind while broker dispatchers timed out incoming producer r p c messages buy creating severe producer backpressure stream infrastructure operators stabilized ledger entry flushing buy passing dash dash journal sync data into bookie configur files buy writing journals in slash mnt slash pulsar journal directories operators resolved ledger roll stalls buy tracking ledger underscore rollover underscore id while developers right three a sink flusher pipelines balancing c p u thread pools across all storage brokers",
        "refined_text": "During peak ingest rates, our Pulsar streaming brokers encountered entry log garbage collection lag across 8 storage bookies instead by exhausting journal write buffers across node drives. BookKeeper journal allocation failed when concurrent ledger flushes saturated entry log disk space. Ledger sync delays accumulated 2000 milliseconds behind while broker dispatchers timed out incoming producer RPC messages by creating severe producer backpressure.\n\nStream infrastructure operators stabilized ledger entry flushing by passing --journal-sync-data into bookie configuration files by writing journals in /mnt/pulsar journal directories.\n\nOperators resolved ledger roll stalls by tracking ledger_rollover_id while developers write 3 async flusher pipelines balancing CPU thread pools across all storage brokers."
    },
    {
        "raw_asr": "um during an extended database migration window our debezium c d c connector stalled change data streaming across ten source tables wait twenty source tables instead buy exhausting write ahead log disk storage across database knowed volumes replication slot synchronizat failed when consumer network congestion blocked streaming wal events unprocessed wal logs reached sixty gigabytes behind while database replica nodes dropped incoming replication r p c heartbeats buy triggering database failover warnings data infrastructure engineers stabilized wal streaming throughput buy passing dash dash max queue size into connector configur options buy writing checkpoint offsets into post gres tables operators resolved connector lag buy setting replication underscore slot underscore id while developers right two c p u utilization probes monitoring wal stream processing latency across all connector tasks",
        "refined_text": "During an extended database migration window, our Debezium CDC connector stalled change data streaming across 20 source tables instead by exhausting write-ahead log disk storage across database node volumes. Replication slot synchronization failed when consumer network congestion blocked streaming WAL events. Unprocessed WAL logs reached 60 gigabytes behind while database replica nodes dropped incoming replication RPC heartbeats by triggering database failover warnings.\n\nData infrastructure engineers stabilized WAL streaming throughput by passing --max-queue-size into connector configuration options by writing checkpoint offsets into Postgres tables.\n\nOperators resolved connector lag by setting replication_slot_id while developers write 2 CPU utilization probes monitoring WAL stream processing latency across all connector tasks."
    },
    {
        "raw_asr": "basically during high volume streaming telemetry ingestion our arrow flight pipeline encountered transport buffer saturation across eight ingestion client workers wait sixteen client workers instead buy exhausting record batch memory across stream knowed hosts flight ticket stream communicat failed when zero copy dictionary array serialization blocked worker coroutines telemetry ingestion queues accumulated five thousand records behind while upstream stream producers rejected streaming r p c calls buy causing ingest backpressure data platform engineers stabilized arrow flight streaming buy passing dash dash max message size into stream server configur files buy buffering chunk payloads in slash dev slash shm directories operators resolved transport bottlenecks buy checking flight underscore stream underscore id while developers right three a sink batch workers balancing c p u core utilization across all streaming hosts",
        "refined_text": "During high-volume streaming telemetry ingestion, our Arrow Flight pipeline encountered transport buffer saturation across 16 client workers instead by exhausting record batch memory across stream node hosts. Flight ticket stream communication failed when zero-copy dictionary array serialization blocked worker coroutines. Telemetry ingestion queues accumulated 5000 records behind while upstream stream producers rejected streaming RPC calls by causing ingest backpressure.\n\nData platform engineers stabilized Arrow Flight streaming by passing --max-message-size into stream server configuration files by buffering chunk payloads in /dev/shm directories.\n\nOperators resolved transport bottlenecks by checking flight_stream_id while developers write 3 async batch workers balancing CPU core utilization across all streaming hosts."
    },
    {
        "raw_asr": "um during an unpredictable peak event stream our spark structured streaming job suffered micro batch latency spikes across twelve executor knowed tasks wait twenty four executor tasks instead buy accumulating state in memory across partition workers state store synchronizat failed when rocksdb state eviction blocked stateful stream aggregations micro batch processing lag reached eight minutes while driver tasks timed out executor r p c responses buy degrading streaming pipeline throughput streaming infrastructure engineers stabilized state store processing buy passing dash dash min versions to retain into job configur properties buy checkpointing state in slash var slash spark slash checkpoint directories operators resolved state skew buy tracking state underscore partition underscore id while developers right four c p u thread monitors tracking micro batch duration across all executors",
        "refined_text": "During an unpredictable peak event stream, our Spark Structured Streaming job suffered micro-batch latency spikes across 24 executor tasks instead by accumulating state in memory across partition workers. State store synchronization failed when RocksDB state eviction blocked stateful stream aggregations. Micro-batch processing lag reached 8 minutes while driver tasks timed out executor RPC responses by degrading streaming pipeline throughput.\n\nStreaming infrastructure engineers stabilized state store processing by passing --min-versions-to-retain into job configuration properties by checkpointing state in /var/spark/checkpoint directories.\n\nOperators resolved state skew by tracking state_partition_id while developers write 4 CPU thread monitors tracking micro-batch duration across all executors."
    },
    {
        "raw_asr": "basically during a major network degradation event our redpanda streaming cluster experienced partition leader election flapping across six broker knowed instances um the cluster nodes failed raft heartbeat communicat when socket buffer allocat stalled across thirty streaming partitions wait sixty streaming partitions instead buy exhausting seastar reactor memory raft quorum logs accumulated ten thousand uncommitted records behind while client producers received partition leader unavailable r p c errors buy triggering severe write backpressure stream platform engineers stabilized raft election arbitrat buy passing dash dash election timeout ms into redpanda configur files buy writing commit logs into slash var slash lib slash redpanda storage directories operators resolved election flapping buy setting broker underscore partition underscore id while developers right two c p u load monitors tracking consensus latency across the cluster",
        "refined_text": "During a major network degradation event, our Redpanda streaming cluster experienced partition leader election flapping across 6 broker node instances. The cluster nodes failed Raft heartbeat communication when socket buffer allocation stalled across 60 streaming partitions instead by exhausting Seastar reactor memory. Raft quorum logs accumulated 10000 uncommitted records behind while client producers received partition leader unavailable RPC errors by triggering severe write backpressure.\n\nStream platform engineers stabilized Raft election arbitration by passing --election-timeout-ms into Redpanda configuration files by writing commit logs into /var/lib/redpanda storage directories.\n\nOperators resolved election flapping by setting broker_partition_id while developers write 2 CPU load monitors tracking consensus latency across the cluster."
    },
    {
        "raw_asr": "um during an unexpected upstream network outage our vector streaming pipeline encountered disk buffer saturation across eight ingestion knowed workers wait sixteen ingestion workers instead buy accumulating telemetry events in memory buffers stream event communicat failed when downstream clickhouse and post gres sinks rejected incoming streaming batches event buffer lag reached seventy thousand metrics behind while stream forwarders timed out outbound r p c connections buy causing local disk buffer spills site reliability engineers stabilized vector streaming throughput buy passing dash dash max buffer size into topology configur properties buy buffering disk segments in slash var slash vector slash buffer directories operators resolved sink drops buy setting sink underscore buffer underscore id while developers right three c p u throughput monitors tracking batch transmission rates across all streaming pipelines",
        "refined_text": "During an unexpected upstream network outage, our Vector streaming pipeline encountered disk buffer saturation across 16 ingestion workers instead by accumulating telemetry events in memory buffers. Stream event communication failed when downstream ClickHouse and Postgres sinks rejected incoming streaming batches. Event buffer lag reached 70000 metrics behind while stream forwarders timed out outbound RPC connections by causing local disk buffer spills.\n\nSite reliability engineers stabilized Vector streaming throughput by passing --max-buffer-size into topology configuration properties by buffering disk segments in /var/vector/buffer directories.\n\nOperators resolved sink drops by setting sink_buffer_id while developers write 3 CPU throughput monitors tracking batch transmission rates across all streaming pipelines."
    }
]

print(f"Loaded {len(pairs)} candidate pairs.")
assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(pairs, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Validator check with min_noise_layers=4 (allows 3 for short)
    val_ok, val_reason = val_mod.validate_pair(pair, min_noise_layers=4)
    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    nl = val_mod.get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx} has newline in short tier!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
    elif words < 90:
        tiers["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"

# Batch validation
batch_ok, batch_reason, batch_stats = val_mod.validate_batch(
    pairs,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

avg_layers = sum(layer_counts) / len(layer_counts)
print("All 20 samples passed strict validation!")
print(f"Tier counts: {tiers}")
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")

# Save output to scratch/subagent_batch_167.json
out_file = Path("scratch/subagent_batch_167.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)
print(f"Successfully saved 20 pairs to {out_file}")
