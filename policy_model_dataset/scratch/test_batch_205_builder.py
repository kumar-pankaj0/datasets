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
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

# Domain 4: Incident Management & Live RCA Narration
# Wave 33 Batch 205: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 complete sentence, 0 newlines, max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # Underscore identifiers, NO dotted filenames.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: CockroachDB range lease rebalancing
    {
        "raw_asr": "basically calibrat r p c lease rebalancing buy tuning lease underscore interval on storage knowed daemons instead",
        "refined_text": "Calibrate RPC lease rebalancing by tuning lease_interval on storage node daemons instead."
    },

    # Sample 2: HAProxy health check flapping
    {
        "raw_asr": "um deduplicat c p u health checking sweeps buy adjusting check underscore timeout on balancer knowed instances instead",
        "refined_text": "Deduplicate CPU health checking sweeps by adjusting check_timeout on balancer node instances instead."
    },

    # Sample 3: Memcached slab allocation churn
    {
        "raw_asr": "so basically configur r p c slab eviction buy tuning chunk underscore factor on caching knowed daemons instead",
        "refined_text": "Configure RPC slab eviction by tuning chunk_factor on caching node daemons instead."
    },

    # Sample 4: Kube-proxy IPVS table sync delays
    {
        "raw_asr": "uh initializ cube ctl packet forwarding tables buy tuning sync underscore period on routing knowed hosts instead",
        "refined_text": "Initialize kubectl packet forwarding tables by tuning sync_period on routing node hosts instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: Apache Pinot realtime ingestion segment completion lag
    {
        "raw_asr": "um our pinot analytics cluster suffered realtime ingestion stalls when twelve knowed servers delayed r p c commits across twenty seconds wait forty seconds instead basically incident responders restored server communicat buy adjusting segment underscore flush buy passing dash dash max segment size into pinot configur settings while platform engineers right two r p c commit probes",
        "refined_text": "Our Pinot analytics cluster suffered realtime ingestion stalls when 12 node servers delayed RPC commits across 40 seconds instead.\n\nIncident responders restored server communication by adjusting segment_flush by passing --max-segment-size into Pinot configuration settings while platform engineers write 2 RPC commit probes."
    },

    # Sample 6: ScyllaDB compaction backlog causing disk I/O queuing
    {
        "raw_asr": "basically our scylla cluster suffered high write latency when fourteen knowed daemons stalled background compaction across fifteen seconds wait thirty seconds instead um site reliability engineers restored daemon operat buy tuning compaction underscore bandwidth buy passing dash dash max compaction rate into scylla configur manifests while systems engineers right two c p u latency monitors",
        "refined_text": "Our Scylla cluster suffered high write latency when 14 node daemons stalled background compaction across 30 seconds instead.\n\nSite reliability engineers restored daemon operations by tuning compaction_bandwidth by passing --max-compaction-rate into Scylla configuration manifests while systems engineers write 2 CPU latency monitors."
    },

    # Sample 7: Thanos Querier gRPC timeout during store gateway fanout
    {
        "raw_asr": "um our metrics query engine encountered dashboard timeouts when sixteen knowed queriers dropped store gateway connections across eighteen seconds wait thirty six seconds instead basically incident responders restored querier communicat buy tuning timeout underscore limit buy passing dash dash query timeout into thanos configur parameters while reliability engineers right two r p c gateway probes",
        "refined_text": "Our metrics query engine encountered dashboard timeouts when 16 node queriers dropped store gateway connections across 36 seconds instead.\n\nIncident responders restored querier communication by tuning timeout_limit by passing --query-timeout into Thanos configuration parameters while reliability engineers write 2 RPC gateway probes."
    },

    # Sample 8: Cilium eBPF map pressure during endpoint churn
    {
        "raw_asr": "basically our networking mesh dropped pod packets when eighteen knowed routers overflowed bpf routing tables across twelve seconds wait twenty four seconds instead um cluster administrators restored router synchronizat buy tuning map underscore dynamic buy passing dash dash bpf map size into cube let configur manifests while platform operators right two cube let packet probes",
        "refined_text": "Our networking mesh dropped pod packets when 18 node routers overflowed BPF routing tables across 24 seconds instead.\n\nCluster administrators restored router synchronization by tuning map_dynamic by passing --bpf-map-size into kubelet configuration manifests while platform operators write 2 kubelet packet probes."
    },

    # Sample 9: PgBouncer transaction pooling starvation during connection burst
    {
        "raw_asr": "um our relational database proxy exhausted client slots when twenty knowed poolers rejected incoming transactions across ten seconds wait thirty seconds instead basically database administrators restored proxy operat buy adjusting pool underscore size buy passing dash dash default pool size into post gres configur commands while reliability engineers right two post gres client monitors",
        "refined_text": "Our relational database proxy exhausted client slots when 20 node poolers rejected incoming transactions across 30 seconds instead.\n\nDatabase administrators restored proxy operations by adjusting pool_size by passing --default-pool-size into Postgres configuration commands while reliability engineers write 2 Postgres client monitors."
    },

    # Sample 10: Linkerd service mesh proxy mTLS certificate rotation stall
    {
        "raw_asr": "basically our microservice mesh failed client m t l s handshakes when ten knowed proxies rejected expired identity certificates across fourteen seconds wait twenty eight seconds instead um infrastructure engineers restored proxy communicat buy refreshing cert underscore expiry buy passing dash dash tls reload interval into cube ctl configur parameters while systems engineers right two cube ctl cert monitors",
        "refined_text": "Our microservice mesh failed client mTLS handshakes when 10 node proxies rejected expired identity certificates across 28 seconds instead.\n\nInfrastructure engineers restored proxy communication by refreshing cert_expiry by passing --tls-reload-interval into kubectl configuration parameters while systems engineers write 2 kubectl cert monitors."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Apache Pulsar BookKeeper ledger ensemble read timeout and ledger fencing
    {
        "raw_asr": "basically during storage volume migration our distributed pulsar messaging cluster encountered read timeouts when bookkeeper ledger ensembles encountered fencing delays across twelve knowed bookies wait eighteen bookies instead um concurrent ledger recovery reads saturated storage transport buy driving broker c p u utiliz to ninety two percent across twenty four cluster nodes p ninety five read latency jumped from four milliseconds up through two two zero zero milliseconds buy stalling thirty five percent of telemetry r p c requests incident responders isolated the primary trigger inside pulsar underscore broker dot conf buy reviewing ledger recovery logs across slash var slash log platform reliability engineers restored ledger synchronizat buy adjusting ensemble underscore timeout buy passing dash dash ensemble size into broker configur settings while systems administrators right two r p c recovery latency monitors",
        "refined_text": "During storage volume migration, our distributed Pulsar messaging cluster encountered read timeouts when BookKeeper ledger ensembles encountered fencing delays across 18 node bookies instead. Concurrent ledger recovery reads saturated storage transport by driving broker CPU utilization to 92 percent across 24 cluster nodes.\n\nP95 read latency jumped from 4 milliseconds up through 2200 milliseconds by stalling 35 percent of telemetry RPC requests. Incident responders isolated the primary trigger inside pulsar_broker.conf by reviewing ledger recovery logs across /var/log.\n\nPlatform reliability engineers restored ledger synchronization by adjusting ensemble_timeout by passing --ensemble-size into broker configuration settings while systems administrators write 2 RPC recovery latency monitors."
    },

    # Sample 12: CockroachDB Raft log truncation and snapshot transfer congestion
    {
        "raw_asr": "um during scheduled storage disk compaction our distributed cockroachdb cluster suffered range transfer stalls when raft log truncation triggered concurrent snapshot replication across fourteen knowed store daemons wait twenty store daemons instead basically large snapshot streams saturated inter node network bandwidth buy driving storage c p u utiliz to ninety three percent across thirty database instances p ninety nine transaction commit latency spiked from five milliseconds up through two six zero zero milliseconds buy failing forty percent of customer billing queries incident responders isolated the underlying defect inside cockroach underscore cluster dot yaml buy evaluating raft transport frames across slash var slash log database reliability engineers restored range communicat buy tuning snapshot underscore throttle buy passing dash dash concurrent snapshot limit into daemon configur manifests while site reliability engineers right two wi re shark stream monitors",
        "refined_text": "During scheduled storage disk compaction, our distributed CockroachDB cluster suffered range transfer stalls when Raft log truncation triggered concurrent snapshot replication across 20 node store daemons instead. Large snapshot streams saturated inter node network bandwidth by driving storage CPU utilization to 93 percent across 30 database instances.\n\nP99 transaction commit latency spiked from 5 milliseconds up through 2600 milliseconds by failing 40 percent of customer billing queries. Incident responders isolated the underlying defect inside cockroach_cluster.yaml by evaluating Raft transport frames across /var/log.\n\nDatabase reliability engineers restored range communication by tuning snapshot_throttle by passing --concurrent-snapshot-limit into daemon configuration manifests while site reliability engineers write 2 Wireshark stream monitors."
    },

    # Sample 13: Envoy proxy upstream circuit breaking on local rate limiting filter
    {
        "raw_asr": "basically during midday checkout traffic surges our service mesh edge proxies dropped incoming api calls when token bucket exhaustion tripped local rate limit filters across sixteen knowed edge gateways wait twenty two edge gateways instead um rejected client connections flooded upstream circuit breakers buy driving gateway c p u utiliz to ninety one percent across twenty eight proxy instances p ninety five gateway response latency climbed from six milliseconds up through two four zero zero milliseconds buy rejecting twenty percent of incoming customer sessions incident responders isolated the primary trigger inside envoy underscore edge dot yaml buy inspecting rate limit filter metrics across slash var slash log platform infrastructure engineers restored gateway operat buy adjusting token underscore rate buy passing dash dash max tokens per second into proxy configur settings while reliability engineers right two r p c circuit breaker monitors",
        "refined_text": "During midday checkout traffic surges, our service mesh edge proxies dropped incoming API calls when token bucket exhaustion tripped local rate limit filters across 22 node edge gateways instead. Rejected client connections flooded upstream circuit breakers by driving gateway CPU utilization to 91 percent across 28 proxy instances.\n\nP95 gateway response latency climbed from 6 milliseconds up through 2400 milliseconds by rejecting 20 percent of incoming customer sessions. Incident responders isolated the primary trigger inside envoy_edge.yaml by inspecting rate limit filter metrics across /var/log.\n\nPlatform infrastructure engineers restored gateway operations by adjusting token_rate by passing --max-tokens-per-second into proxy configuration settings while reliability engineers write 2 RPC circuit breaker monitors."
    },

    # Sample 14: Elasticsearch cluster master pending tasks queue saturation during node join
    {
        "raw_asr": "um during rolling node lifecycle updates our search cluster marked index operations un responsive when cluster state publish tasks queued behind unassigned shard updates across twelve knowed master nodes wait eighteen master nodes instead basically pending task queues delayed cluster coordination updates buy driving master c p u utiliz to ninety four percent across twenty four cluster nodes p ninety nine task execution latency surged from three milliseconds up through two five zero zero milliseconds buy failing thirty percent of customer search r p c queries incident responders diagnosed the primary trigger inside elasticsearch underscore master dot yml buy tracking cluster state update traces across slash var slash log database reliability engineers stabilized shard allocat buy tuning publish underscore timeout buy passing dash dash cluster state timeout into master configur settings while systems administrators right two r p c pending task probes",
        "refined_text": "During rolling node lifecycle updates, our search cluster marked index operations un responsive when cluster state publish tasks queued behind unassigned shard updates across 18 node master nodes instead. Pending task queues delayed cluster coordination updates by driving master CPU utilization to 94 percent across 24 cluster nodes.\n\nP99 task execution latency surged from 3 milliseconds up through 2500 milliseconds by failing 30 percent of customer search RPC queries. Incident responders diagnosed the primary trigger inside elasticsearch_master.yml by tracking cluster state update traces across /var/log.\n\nDatabase reliability engineers stabilized shard allocation by tuning publish_timeout by passing --cluster-state-timeout into master configuration settings while systems administrators write 2 RPC pending task probes."
    },

    # Sample 15: Postgres write-ahead log (WAL) archiving backlog during cloud bucket rate limit
    {
        "raw_asr": "basically during bulk catalog data loading our postgres database cluster filled storage partitions when wal archiving scripts encountered s three upload rate limits across ten knowed primary replicas wait sixteen primary replicas instead um accumulated segment files threatened disk threshold limits buy driving database c p u utiliz to ninety three percent across thirty worker pods p ninety five archiving latency climbed from four milliseconds up through two eight zero zero milliseconds buy stalling forty five percent of data stream commits incident responders isolated the underlying defect inside postgres underscore archive dot conf buy evaluating wal archiving logs across slash var slash log database platform engineers restored archive synchronizat buy tuning archive underscore timeout buy passing dash dash max archive threads into database configur manifests while reliability engineers right two post gres archive lag monitors",
        "refined_text": "During bulk catalog data loading, our Postgres database cluster filled storage partitions when WAL archiving scripts encountered S 3 upload rate limits across 16 node primary replicas instead. Accumulated segment files threatened disk threshold limits by driving database CPU utilization to 93 percent across 30 worker pods.\n\nP95 archiving latency climbed from 4 milliseconds up through 2800 milliseconds by stalling 45 percent of data stream commits. Incident responders isolated the underlying defect inside postgres_archive.conf by evaluating WAL archiving logs across /var/log.\n\nDatabase platform engineers restored archive synchronization by tuning archive_timeout by passing --max-archive-threads into database configuration manifests while reliability engineers write 2 Postgres archive lag monitors."
    },

    # Sample 16: Kafka broker ISR shrinkage under unaligned replica fetch lag
    {
        "raw_asr": "um during network maintenance switches our kafka streaming brokers removed partition followers from in sync replica sets when socket buffer exhaustion delayed fetch responses across fourteen knowed broker pods wait twenty broker pods instead basically follower fetch timeouts triggered partition under replication buy driving broker c p u utiliz to ninety two percent across thirty two cluster instances p ninety nine replication lag jumped from two milliseconds up through two one zero zero milliseconds buy failing thirty five percent of telemetry stream messages incident responders diagnosed the primary trigger inside kafka underscore server dot conf buy analyzing replica fetch timeout logs across slash etc streaming reliability engineers restored replica communicat buy increasing fetch underscore max underscore wait buy passing dash dash replica fetch max bytes into cube ctl configur parameters while platform operators right two cube ctl replication lag probes",
        "refined_text": "During network maintenance switches, our Kafka streaming brokers removed partition followers from in sync replica sets when socket buffer exhaustion delayed fetch responses across 20 node broker pods instead. Follower fetch timeouts triggered partition under replication by driving broker CPU utilization to 92 percent across 32 cluster instances.\n\nP99 replication lag jumped from 2 milliseconds up through 2100 milliseconds by failing 35 percent of telemetry stream messages. Incident responders diagnosed the primary trigger inside kafka_server.conf by analyzing replica fetch timeout logs across /etc.\n\nStreaming reliability engineers restored replica communication by increasing fetch_max_wait by passing --replica-fetch-max-bytes into kubectl configuration parameters while platform operators write 2 kubectl replication lag probes."
    },

    # Sample 17: CoreDNS response cache eviction storm during wildcard DNS lookup surge
    {
        "raw_asr": "basically during microservice autoscaling events our kubernetes coredns pods dropped internal name resolutions when high cache misses exhausted memory caches across twelve knowed resolver pods wait eighteen resolver pods instead um cache lock contention delayed dns lookup responses buy driving dns c p u utiliz to ninety five percent across thirty six edge pods p ninety five resolution latency climbed from four milliseconds up through two seven zero zero milliseconds buy terminating twenty five percent of cluster dns requests incident responders isolated the underlying defect inside coredns underscore Corefile dot conf buy inspecting dns resolution error traces across slash var slash log site reliability engineers restored dns operat buy tuning cache underscore ttl buy passing dash dash max dns cache size into cube let configur manifests while systems engineers right two cube let lookup probes",
        "refined_text": "During microservice autoscaling events, our Kubernetes CoreDNS pods dropped internal name resolutions when high cache misses exhausted memory caches across 18 node resolver pods instead. Cache lock contention delayed DNS lookup responses by driving DNS CPU utilization to 95 percent across 36 edge pods.\n\nP95 resolution latency climbed from 4 milliseconds up through 2700 milliseconds by terminating 25 percent of cluster DNS requests. Incident responders isolated the underlying defect inside coredns_Corefile.conf by inspecting DNS resolution error traces across /var/log.\n\nSite reliability engineers restored DNS operations by tuning cache_ttl by passing --max-dns-cache-size into kubelet configuration manifests while systems engineers write 2 kubelet lookup probes."
    },

    # Sample 18: Redis Cluster replica disconnection during asynchronous replication buffer overflow
    {
        "raw_asr": "um during secondary database snapshot exports our redis caching cluster dropped replication links when large write volumes overflowed replication client output buffers across ten knowed slave instances wait sixteen slave instances instead basically continuous buffer disconnects forced full background sync resynchronization cycles buy driving cache c p u utiliz to ninety one percent across twenty database instances p ninety nine replication delay surged from six milliseconds up through two nine zero zero milliseconds buy failing forty percent of customer cache r p c queries incident responders isolated the primary trigger inside redis underscore replica dot conf buy analyzing replication buffer traces across slash var slash log caching platform engineers restored replication communicat buy adjusting buffer underscore limit buy passing dash dash client output buffer limit into redis configur parameters while reliability engineers right two r p c replication buffer monitors",
        "refined_text": "During secondary database snapshot exports, our Redis caching cluster dropped replication links when large write volumes overflowed replication client output buffers across 16 node slave instances instead. Continuous buffer disconnects forced full background sync resynchronization cycles by driving cache CPU utilization to 91 percent across 20 database instances.\n\nP99 replication delay surged from 6 milliseconds up through 2900 milliseconds by failing 40 percent of customer cache RPC queries. Incident responders isolated the primary trigger inside redis_replica.conf by analyzing replication buffer traces across /var/log.\n\nCaching platform engineers restored replication communication by adjusting buffer_limit by passing --client-output-buffer-limit into Redis configuration parameters while reliability engineers write 2 RPC replication buffer monitors."
    },

    # Sample 19: NGINX Ingress upstream keepalive connection pool exhaustion
    {
        "raw_asr": "basically during flash sale traffic bursts our ingress controller dropped incoming http connections when upstream keepalive connection pools emptied across fourteen knowed ingress pods wait twenty ingress pods instead um rapid connection closes forced repeated backend tcp handshakes buy driving proxy c p u utiliz to ninety four percent across twenty eight proxy instances p ninety five request queue latency climbed from five milliseconds up through two three zero zero milliseconds buy dropping thirty percent of checkout web sessions incident responders diagnosed the primary trigger inside nginx underscore ingress dot conf buy reviewing keepalive pool exhaustion metrics across slash var slash log edge platform administrators restored proxy synchronizat buy adjusting keepalive underscore requests buy passing dash dash upstream keepalive timeout into cube let configur manifests while site reliability engineers right two cube let socket latency probes",
        "refined_text": "During flash sale traffic bursts, our ingress controller dropped incoming HTTP connections when upstream keepalive connection pools emptied across 20 node ingress pods instead. Rapid connection closes forced repeated backend TCP handshakes by driving proxy CPU utilization to 94 percent across 28 proxy instances.\n\nP95 request queue latency climbed from 5 milliseconds up through 2300 milliseconds by dropping 30 percent of checkout web sessions. Incident responders diagnosed the primary trigger inside nginx_ingress.conf by reviewing keepalive pool exhaustion metrics across /var/log.\n\nEdge platform administrators restored proxy synchronization by adjusting keepalive_requests by passing --upstream-keepalive-timeout into kubelet configuration manifests while site reliability engineers write 2 kubelet socket latency probes."
    },

    # Sample 20: Vault token store lease expiration loop during consul backend storage latency
    {
        "raw_asr": "um during distributed microservice scale downs our vault identity cluster rejected token renewals when consul storage backend write latency stalled active lease cancellations across twelve knowed agent pods wait eighteen agent pods instead basically lease revocation backlogs locked credential storage locks buy driving consul c p u utiliz to ninety three percent across twenty storage instances p ninety nine auth revocation latency jumped from four milliseconds up through two seven zero zero milliseconds buy failing forty percent of application r p c tokens incident responders isolated the primary trigger inside vault underscore consul dot conf buy reviewing storage latency logs across slash var slash log security platform engineers stabilized lease terminat buy adjusting batch underscore revocation buy passing dash dash max revoke batch size into daemon configur parameters while infrastructure administrators right two r p c lease latency monitors",
        "refined_text": "During distributed microservice scale downs, our Vault identity cluster rejected token renewals when Consul storage backend write latency stalled active lease cancellations across 18 node agent pods instead. Lease revocation backlogs locked credential storage locks by driving Consul CPU utilization to 93 percent across 20 storage instances.\n\nP99 auth revocation latency jumped from 4 milliseconds up through 2700 milliseconds by failing 40 percent of application RPC tokens. Incident responders isolated the primary trigger inside vault_consul.conf by reviewing storage latency logs across /var/log.\n\nSecurity platform engineers stabilized lease termination by adjusting batch_revocation by passing --max-revoke-batch-size into daemon configuration parameters while infrastructure administrators write 2 RPC lease latency monitors."
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
        v_ok, v_reason = validate_pair(s, min_noise_layers=4)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        layers = count_active_noise_layers(s["raw_asr"])
        layer_count = get_noise_layer_count(s["raw_asr"])
        layer_counts.append(layer_count)
        words = len(s["refined_text"].split())

        if words < 25:
            tier = "Short"
            tier_counts["short"] += 1
        elif words < 90:
            tier = "Medium"
            tier_counts["medium"] += 1
        else:
            tier = "Long"
            tier_counts["long"] += 1

        active_layers_str = ", ".join([k for k, v in layers.items() if v])
        print(f"Sample {i+1:02d} [{tier}, {words}w, {layer_count} layers]: val={v_ok} ({v_reason}), clean={c_reason} | Active: {active_layers_str}")

        if not v_ok:
            print(f"  FAILED validate_pair: {v_reason}")
            all_valid = False
        if c_reason != "kept":
            print(f"  FAILED clean_sample: {c_reason}")
            all_valid = False

    # Batch validation
    b_ok, b_reason, b_tiers = validate_batch(
        samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    print(f"\nBatch validation: ok={b_ok}, reason={b_reason}")
    print(f"Tier counts: {tier_counts}")
    print(f"Batch metrics: {b_tiers}")

    if not all_valid or not b_ok:
        print("VALIDATION FAILED!")
        sys.exit(1)

    # Output to target file
    out_path = Path("scratch/subagent_batch_205.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS: Written 20 verified samples to {out_path}")

if __name__ == "__main__":
    main()
