import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count, CUT_WORD_REGEX
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

# Domain 4: Incident Management & Live Troubleshooting RCA
# Batch 190 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # Underscore identifiers, NO dotted filenames.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: Pulsar broker ledger compaction buffers
    {
        "raw_asr": "basically deduplicat r p c ledger compaction buffers buy purging ledger underscore rollover on broker knowed clusters instead",
        "refined_text": "Deduplicate RPC ledger compaction buffers by purging ledger_rollover on broker node clusters instead."
    },

    # Sample 2: Cassandra read repair speculative retry thresholds
    {
        "raw_asr": "um calibrat c p u speculative retry thresholds buy tuning speculative underscore retry on coordinator knowed servers instead",
        "refined_text": "Calibrate CPU speculative retry thresholds by tuning speculative_retry on coordinator node servers instead."
    },

    # Sample 3: Cilium connection tracking tables
    {
        "raw_asr": "uh allocat cube let connection tracking tables buy expanding conntrack underscore max on worker knowed routers instead",
        "refined_text": "Allocate kubelet connection tracking tables by expanding conntrack_max on worker node routers instead."
    },

    # Sample 4: HAProxy session ticket pools
    {
        "raw_asr": "basically initializ r p c session ticket pools buy clearing tls underscore tickets on gateway knowed instances instead",
        "refined_text": "Initialize RPC session ticket pools by clearing tls_tickets on gateway node instances instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: ScyllaDB coordinator commitlog write stall
    {
        "raw_asr": "um our scylladb database cluster suffered commitlog write stalls when sixteen knowed coordinators missed sync intervals across twenty seconds wait forty seconds instead basically database operators restored cluster operat buy adjusting commitlog underscore sync buy passing dash dash max commitlog size into scylladb configur manifests while reliability engineers right two c p u write monitors",
        "refined_text": "Our ScyllaDB database cluster suffered commitlog write stalls when 16 node coordinators missed sync intervals across 40 seconds instead.\n\nDatabase operators restored cluster operations by adjusting commitlog_sync by passing --max-commitlog-size into ScyllaDB configuration manifests while reliability engineers write 2 CPU write monitors."
    },

    # Sample 6: Jaeger distributed tracing collector span buffer drop
    {
        "raw_asr": "basically our tracing collection tier dropped trace batches when fourteen knowed collectors exhausted memory queues across fifteen seconds wait thirty five seconds instead um tracing platform engineers restored collector communicat buy adjusting queue underscore size buy passing dash dash collector queue capacity into jaeger configur manifests while telemetry engineers right two r p c buffer monitors",
        "refined_text": "Our tracing collection tier dropped trace batches when 14 node collectors exhausted memory queues across 35 seconds instead.\n\nTracing platform engineers restored collector communication by adjusting queue_size by passing --collector-queue-capacity into Jaeger configuration manifests while telemetry engineers write 2 RPC buffer monitors."
    },

    # Sample 7: Redis Sentinel split-brain failover stall
    {
        "raw_asr": "um our redis caching tier failed master promotion elections when twelve knowed sentinels dropped consensus votes across twenty seconds wait forty five seconds instead basically database administrators restored cluster synchronizat buy tuning down underscore after underscore milliseconds buy passing dash dash sentinel down after into sentinel configur manifests while site reliability engineers right two wi re shark failover probes",
        "refined_text": "Our Redis caching tier failed master promotion elections when 12 node sentinels dropped consensus votes across 45 seconds instead.\n\nDatabase administrators restored cluster synchronization by tuning down_after_milliseconds by passing --sentinel-down-after into Sentinel configuration manifests while site reliability engineers write 2 Wireshark failover probes."
    },

    # Sample 8: Consul service mesh mTLS certificate renewal latency
    {
        "raw_asr": "basically our service mesh proxies delayed certificate renewals when eighteen knowed agents encountered storage write locks across twenty seconds wait fifty seconds instead um platform security engineers stabilized service communicat buy tuning leaf underscore cert underscore ttl buy passing dash dash cert ttl into consul configur manifests while infrastructure engineers right two a sink renewal monitors",
        "refined_text": "Our service mesh proxies delayed certificate renewals when 18 node agents encountered storage write locks across 50 seconds instead.\n\nPlatform security engineers stabilized service communication by tuning leaf_cert_ttl by passing --cert-ttl into Consul configuration manifests while infrastructure engineers write 2 async renewal monitors."
    },

    # Sample 9: OpenTelemetry Collector batch processor memory queue backup
    {
        "raw_asr": "um our telemetry collection cluster dropped telemetry metrics when twenty knowed collectors exhausted buffer queues across fifteen seconds wait thirty seconds instead basically reliability engineers restored telemetry allocat buy tuning send underscore batch underscore max underscore size buy passing dash dash send batch size into collector configur manifests while systems engineers right two post gres ingestion probes",
        "refined_text": "Our telemetry collection cluster dropped telemetry metrics when 20 node collectors exhausted buffer queues across 30 seconds instead.\n\nReliability engineers restored telemetry allocation by tuning send_batch_max_size by passing --send-batch-size into collector configuration manifests while systems engineers write 2 Postgres ingestion probes."
    },

    # Sample 10: Prometheus Alertmanager notification pipeline throttling
    {
        "raw_asr": "basically our alert routing cluster queued notification dispatches when ten knowed dispatchers hit upstream timeout limits across thirty seconds wait sixty seconds instead um observability engineers restored dispatch operat buy adjusting group underscore wait buy passing dash dash cluster peer timeout into alertmanager configur manifests while systems administrators right two cube ctl webhook probes",
        "refined_text": "Our alert routing cluster queued notification dispatches when 10 node dispatchers hit upstream timeout limits across 60 seconds instead.\n\nObservability engineers restored dispatch operations by adjusting group_wait by passing --cluster-peer-timeout into Alertmanager configuration manifests while systems administrators write 2 kubectl webhook probes."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Apache Pulsar BookKeeper write quorum ledger write latency surge
    {
        "raw_asr": "basically during messaging throughput spikes our bookkeeper storage cluster suffered ledger write stalls when journal flush delays blocked quorum replication across twelve knowed bookie hosts wait eighteen bookie hosts instead um synchronous ledger syncs delayed message publishing buy driving bookie c p u utiliz to ninety two percent across thirty six bookie instances p ninety five bookie write latency surged from four milliseconds up through two four zero zero milliseconds buy stalling forty percent of event pipeline write queries incident responders isolated the underlying defect inside bookkeeper underscore server dot conf buy reviewing journal sync metrics across slash var slash log streaming platform engineers restored cluster synchronizat buy adjusting journal underscore sync underscore interval buy passing dash dash bookie journal flush into daemon configur parameters while site reliability engineers right three automated storage latency probes",
        "refined_text": "During messaging throughput spikes, our BookKeeper storage cluster suffered ledger write stalls when journal flush delays blocked quorum replication across 18 node bookie hosts instead. Synchronous ledger syncs delayed message publishing by driving bookie CPU utilization to 92 percent across 36 bookie instances.\n\nP95 bookie write latency surged from 4 milliseconds up through 2400 milliseconds by stalling 40 percent of event pipeline write queries. Incident responders isolated the underlying defect inside bookkeeper_server.conf by reviewing journal sync metrics across /var/log.\n\nStreaming platform engineers restored cluster synchronization by adjusting journal_sync_interval by passing --bookie-journal-flush into daemon configuration parameters while site reliability engineers write 3 automated storage latency probes."
    },

    # Sample 12: CockroachDB Raft log replication stall under cross-region network partitioning
    {
        "raw_asr": "um during inter region network failover our distributed database cluster suffered transactional write timeouts when raft log replication stalls delayed range consensus across ten knowed storage hosts wait sixteen storage hosts instead basically delayed consensus rounds blocked client transactions buy driving coordinator c p u utiliz to ninety four percent across twenty four database instances p ninety nine commit execution latency jumped from five milliseconds up through two eight zero zero milliseconds buy returning status five zero four gateway timeouts across thirty downstream services incident responders diagnosed the primary trigger inside cockroach underscore cluster dot conf buy reviewing consensus election logs across slash var slash log database administrators stabilized range synchronizat buy adjusting raft underscore tick underscore interval buy passing dash dash raft heartbeat ticks into engine configur settings while reliability engineers right two automated r p c consensus probes",
        "refined_text": "During inter-region network failover, our distributed database cluster suffered transactional write timeouts when Raft log replication stalls delayed range consensus across 16 node storage hosts instead. Delayed consensus rounds blocked client transactions by driving coordinator CPU utilization to 94 percent across 24 database instances.\n\nP99 commit execution latency jumped from 5 milliseconds up through 2800 milliseconds by returning status 504 gateway timeouts across 30 downstream services. Incident responders diagnosed the primary trigger inside cockroach_cluster.conf by reviewing consensus election logs across /var/log.\n\nDatabase administrators stabilized range synchronization by adjusting raft_tick_interval by passing --raft-heartbeat-ticks into engine configuration settings while reliability engineers write 2 automated RPC consensus probes."
    },

    # Sample 13: Envoy gRPC stream multiplexing exhaustion and upstream connection resets
    {
        "raw_asr": "basically during evening traffic ramp up our ingress service mesh dropped upstream g r p c connections when concurrent stream limits caused connection multiplexing stalls across fourteen knowed gateway proxies wait twenty gateway proxies instead um socket exhaustion stalled request dispatching buy driving proxy c p u utiliz to eighty nine percent across forty edge instances p ninety five downstream stream latency surged from three milliseconds up through nineteen hundred milliseconds buy returning status five zero three errors across twenty five thousand client queries incident responders diagnosed the primary trigger inside envoy underscore ingress dot yaml buy analyzing packet traces across slash etc network reliability engineers restored proxy communicat buy increasing max underscore concurrent underscore streams buy passing dash dash max requests per connection into proxy configur parameters while systems engineers right two wi re shark packet capture probes",
        "refined_text": "During evening traffic ramp-up, our ingress service mesh dropped upstream gRPC connections when concurrent stream limits caused connection multiplexing stalls across 20 node gateway proxies instead. Socket exhaustion stalled request dispatching by driving proxy CPU utilization to 89 percent across 40 edge instances.\n\nP95 downstream stream latency surged from 3 milliseconds up through 1900 milliseconds by returning status 503 errors across 25000 client queries. Incident responders diagnosed the primary trigger inside envoy_ingress.yaml by analyzing packet traces across /etc.\n\nNetwork reliability engineers restored proxy communication by increasing max_concurrent_streams by passing --max-requests-per-connection into proxy configuration parameters while systems engineers write 2 Wireshark packet capture probes."
    },

    # Sample 14: Cilium eBPF map overflow and conntrack table eviction drop storm
    {
        "raw_asr": "um during kubernetes node autoscaling our container network overlay encountered pod communication drops when conntrack e b p f map limits delayed packet address translation across twelve knowed worker hosts wait eighteen worker hosts instead basically connection tracking evictions halted inter service packet routing buy driving node c p u utiliz to ninety three percent across thirty worker instances p ninety nine container packet latency jumped from two milliseconds up through two two zero zero milliseconds buy dropping twenty percent of internal service requests incident responders isolated the underlying defect inside cilium underscore daemon dot yaml buy evaluating conntrack metrics across slash proc cluster network engineers restored packet synchronizat buy expanding bpf underscore ct underscore global underscore any underscore max buy passing dash dash bpf ct max into cube let configur manifests while site reliability engineers right two a sink packet delivery monitors",
        "refined_text": "During Kubernetes node autoscaling, our container network overlay encountered pod communication drops when conntrack eBPF map limits delayed packet address translation across 18 node worker hosts instead. Connection tracking evictions halted inter-service packet routing by driving node CPU utilization to 93 percent across 30 worker instances.\n\nP99 container packet latency jumped from 2 milliseconds up through 2200 milliseconds by dropping 20 percent of internal service requests. Incident responders isolated the underlying defect inside cilium_daemon.yaml by evaluating conntrack metrics across /proc.\n\nCluster network engineers restored packet synchronization by expanding bpf_ct_global_any_max by passing --bpf-ct-max into kubelet configuration manifests while site reliability engineers write 2 async packet delivery monitors."
    },

    # Sample 15: Redis Cluster hash slot migration stall during cluster reshuffling
    {
        "raw_asr": "basically during scheduled database partition rebalancing our distributed cache tier suffered command execution stalls when key migration timeouts locked hash slots across eight knowed master hosts wait fourteen master hosts instead um unfinished slot migrations blocked key lookup requests buy driving cache c p u utiliz to ninety one percent across twenty eight cluster instances p ninety five key retrieval latency jumped from three milliseconds up through two six zero zero milliseconds buy returning status five zero zero errors across twelve thousand client requests incident responders diagnosed the primary trigger inside redis underscore cluster dot conf buy inspecting replication slot sync traces across slash var slash log cache platform engineers restored cluster operat buy adjusting cluster underscore node underscore timeout buy passing dash dash cluster migration barrier into daemon configur files while infrastructure reliability engineers right two automated r p c latency probes",
        "refined_text": "During scheduled database partition rebalancing, our distributed cache tier suffered command execution stalls when key migration timeouts locked hash slots across 14 node master hosts instead. Unfinished slot migrations blocked key lookup requests by driving cache CPU utilization to 91 percent across 28 cluster instances.\n\nP95 key retrieval latency jumped from 3 milliseconds up through 2600 milliseconds by returning status 500 errors across 12000 client requests. Incident responders diagnosed the primary trigger inside redis_cluster.conf by inspecting replication slot sync traces across /var/log.\n\nCache platform engineers restored cluster operations by adjusting cluster_node_timeout by passing --cluster-migration-barrier into daemon configuration files while infrastructure reliability engineers write 2 automated RPC latency probes."
    },

    # Sample 16: ScyllaDB compaction backlog causing read latency spikes
    {
        "raw_asr": "um during large batch data ingestion our distributed database experienced read query timeouts when background compaction delays caused read amplification across ten knowed replica hosts wait sixteen replica hosts instead basically concurrent disk read requests depleted storage bandwidth buy driving database c p u utiliz to ninety five percent across twenty four database instances p ninety nine read execution latency climbed from six milliseconds up through two seven zero zero milliseconds buy triggering status five zero four gateway timeouts across thirty five downstream services incident responders diagnosed the primary trigger inside scylladb underscore storage dot conf buy inspecting compaction backlog metrics across slash var slash log database reliability engineers restored storage communicat buy adjusting compaction underscore throughput buy passing dash dash max compaction threshold into scylladb configur settings while site reliability engineers right two r p c read latency probes",
        "refined_text": "During large batch data ingestion, our distributed database experienced read query timeouts when background compaction delays caused read amplification across 16 node replica hosts instead. Concurrent disk read requests depleted storage bandwidth by driving database CPU utilization to 95 percent across 24 database instances.\n\nP99 read execution latency climbed from 6 milliseconds up through 2700 milliseconds by triggering status 504 gateway timeouts across 35 downstream services. Incident responders diagnosed the primary trigger inside scylladb_storage.conf by inspecting compaction backlog metrics across /var/log.\n\nDatabase reliability engineers restored storage communication by adjusting compaction_throughput by passing --max-compaction-threshold into ScyllaDB configuration settings while site reliability engineers write 2 RPC read latency probes."
    },

    # Sample 17: Elasticsearch bulk indexing rejection during translog flush contention
    {
        "raw_asr": "basically during telemetry logging surges our analytics cluster suffered index write rejections when primary shard flushes delayed translog flush operations across twelve knowed indexing hosts wait twenty indexing hosts instead um queue backlog exhaustion blocked incoming telemetry events buy driving indexing c p u utiliz to ninety two percent across thirty analytical instances p ninety five document indexing latency surged from four milliseconds up through two one zero zero milliseconds buy dropping thirty percent of incoming audit payloads incident responders isolated the underlying defect inside elasticsearch underscore node dot yml buy reviewing shard flush thread traces across slash proc observability platform engineers stabilized data allocat buy increasing index underscore buffer underscore size buy passing dash dash indices memory index buffer size into cluster configur parameters while performance engineers right two post gres streaming probes",
        "refined_text": "During telemetry logging surges, our analytics cluster suffered index write rejections when primary shard flushes delayed translog flush operations across 20 node indexing hosts instead. Queue backlog exhaustion blocked incoming telemetry events by driving indexing CPU utilization to 92 percent across 30 analytical instances.\n\nP95 document indexing latency surged from 4 milliseconds up through 2100 milliseconds by dropping 30 percent of incoming audit payloads. Incident responders isolated the underlying defect inside elasticsearch_node.yml by reviewing shard flush thread traces across /proc.\n\nObservability platform engineers stabilized data allocation by increasing index_buffer_size by passing --indices-memory-index-buffer-size into cluster configuration parameters while performance engineers write 2 Postgres streaming probes."
    },

    # Sample 18: Kafka Kraft controller metadata log compaction stall
    {
        "raw_asr": "um during microservice deployment spikes our event streaming cluster encountered metadata commit timeouts when controller compaction delays locked partition metadata across eight knowed broker hosts wait fourteen broker hosts instead basically suspended metadata synchronization halted new topic allocations buy driving broker c p u utiliz to ninety percent across twenty cluster instances p ninety nine partition assignment latency jumped from five milliseconds up through two five zero zero milliseconds buy failing twenty five percent of deployment pipeline jobs incident responders diagnosed the primary trigger inside kafka underscore kraft dot properties buy inspecting controller log replication traces across slash var slash log event platform engineers restored cluster operat buy adjusting metadata underscore max underscore idle underscore ms buy passing dash dash metadata log segment bytes into broker configur parameters while systems reliability engineers right two a sink controller queue probes",
        "refined_text": "During microservice deployment spikes, our event streaming cluster encountered metadata commit timeouts when controller compaction delays locked partition metadata across 14 node broker hosts instead. Suspended metadata synchronization halted new topic allocations by driving broker CPU utilization to 90 percent across 20 cluster instances.\n\nP99 partition assignment latency jumped from 5 milliseconds up through 2500 milliseconds by failing 25 percent of deployment pipeline jobs. Incident responders diagnosed the primary trigger inside kafka_kraft.properties by inspecting controller log replication traces across /var/log.\n\nEvent platform engineers restored cluster operations by adjusting metadata_max_idle_ms by passing --metadata-log-segment-bytes into broker configuration parameters while systems reliability engineers write 2 async controller queue probes."
    },

    # Sample 19: NATS JetStream stream replication stall on disk block allocation delay
    {
        "raw_asr": "basically during transactional message delivery our message broker tier suffered write acknowledgement timeouts when storage engines delayed message persistence across six knowed storage hosts wait twelve storage hosts instead um block device write stalls halted consumer message dispatching buy driving broker c p u utiliz to ninety three percent across twenty four messaging instances p ninety five message publish latency jumped from three milliseconds up through two three zero zero milliseconds buy blocking thirty five thousand customer order events incident responders isolated the underlying defect inside nats underscore jetstream dot conf buy inspecting block storage write logs across slash var slash log messaging reliability engineers restored message synchronizat buy adjusting max underscore file underscore store buy passing dash dash jetstream max bytes into server configur files while site reliability engineers right two cube ctl disk usage probes",
        "refined_text": "During transactional message delivery, our message broker tier suffered write acknowledgement timeouts when storage engines delayed message persistence across 12 node storage hosts instead. Block device write stalls halted consumer message dispatching by driving broker CPU utilization to 93 percent across 24 messaging instances.\n\nP95 message publish latency jumped from 3 milliseconds up through 2300 milliseconds by blocking 35000 customer order events. Incident responders isolated the underlying defect inside nats_jetstream.conf by inspecting block storage write logs across /var/log.\n\nMessaging reliability engineers restored message synchronization by adjusting max_file_store by passing --jetstream-max-bytes into server configuration files while site reliability engineers write 2 kubectl disk usage probes."
    },

    # Sample 20: CoreDNS cache plugin concurrency contention under recursive DNS storms
    {
        "raw_asr": "um during internal service discovery failovers our cluster dns resolvers dropped domain lookup requests when recursive forwarder lock contention exhausted query worker pools across ten knowed resolver pods wait sixteen resolver pods instead basically worker pool starvation blocked name lookups buy driving coredns c p u utiliz to ninety four percent across thirty instances p ninety nine domain lookup latency climbed from two milliseconds up through nineteen hundred milliseconds buy triggering status five zero four gateway timeouts across fifty downstream services incident responders diagnosed the primary trigger inside coredns underscore config dot conf buy tracking upstream query lock contention across slash proc platform network engineers restored query communicat buy tuning cache underscore prefetch buy passing dash dash max concurrent queries into cube let configur manifests while site reliability engineers right two wi re shark query monitors",
        "refined_text": "During internal service discovery failovers, our cluster DNS resolvers dropped domain lookup requests when recursive forwarder lock contention exhausted query worker pools across 16 node resolver pods instead. Worker pool starvation blocked name lookups by driving CoreDNS CPU utilization to 94 percent across 30 instances.\n\nP99 domain lookup latency climbed from 2 milliseconds up through 1900 milliseconds by triggering status 504 gateway timeouts across 50 downstream services. Incident responders diagnosed the primary trigger inside coredns_config.conf by tracking upstream query lock contention across /proc.\n\nPlatform network engineers restored query communication by tuning cache_prefetch by passing --max-concurrent-queries into kubelet configuration manifests while site reliability engineers write 2 Wireshark query monitors."
    }
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
    else:
        sys.exit(1)

    # Validate each pair
    all_valid = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []

    for i, s in enumerate(samples):
        words = len(s["refined_text"].split())
        min_l = 3 if words < 25 else 4
        v_ok, v_reason = validate_pair(s, min_noise_layers=min_l)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        layers = count_active_noise_layers(s["raw_asr"])
        layer_count = get_noise_layer_count(s["raw_asr"])
        layer_counts.append(layer_count)

        if words < 25:
            tier_counts["short"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', s["refined_text"]) if sent.strip()]
            if len(sentences) != 1:
                print(f"Sample {i+1}: Sentence count mismatch for short tier: {len(sentences)} != 1")
                all_valid = False
            if "\n" in s["refined_text"]:
                print(f"Sample {i+1}: Newline in short tier")
                all_valid = False
            # Check cut words <= 1
            cut_words_found = CUT_WORD_REGEX.findall(s["raw_asr"])
            if len(cut_words_found) > 1:
                print(f"Sample {i+1}: Short tier has >1 cut word: {cut_words_found}")
                all_valid = False
        elif words < 90:
            tier_counts["medium"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', s["refined_text"]) if sent.strip()]
            if not (1 <= len(sentences) <= 3):
                print(f"Sample {i+1}: Sentence count mismatch for medium tier: {len(sentences)}")
                all_valid = False
            if "\n\n" not in s["refined_text"]:
                print(f"Sample {i+1}: Missing \\n\\n in medium tier")
                all_valid = False
        else:
            tier_counts["long"] += 1
            if "\n\n" not in s["refined_text"]:
                print(f"Sample {i+1}: Missing \\n\\n in long tier")
                all_valid = False
            if re.search(r'(^|\n)\s*[-*]\s+', s["refined_text"]):
                print(f"Sample {i+1}: Long tier has bullet list")
                all_valid = False
            if re.search(r'(^|\n)\s*\d+\.\s+', s["refined_text"]):
                print(f"Sample {i+1}: Long tier has numbered list")
                all_valid = False
        
        status = "OK" if (v_ok and c_reason == "kept") else "FAIL"
        if status == "FAIL":
            all_valid = False
            print(f"Sample {i+1:02d} (tier words: {words:3d}, layers: {layer_count}): {status}")
            if not v_ok:
                print(f"  Validator: {v_reason}")
            if c_reason != "kept":
                print(f"  Cleaner: {c_reason}")
        else:
            active = [k for k, v in layers.items() if v]
            print(f"Sample {i+1:02d} (tier words: {words:3d}, layers: {layer_count} [{', '.join(active)}]): PASS")

    # Batch validation
    batch_ok, batch_reason, metrics = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
    print("\nBatch Validation Result:")
    print("  Status:", "PASS" if batch_ok else "FAIL")
    print("  Reason:", batch_reason)
    print("  Tier Counts:", tier_counts)
    print("  Average Noise Layers:", f"{sum(layer_counts)/len(layer_counts):.2f}")
    print("  Metrics:", json.dumps(metrics, indent=2))

    if all_valid and batch_ok:
        out_path = Path("scratch/subagent_batch_190.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
