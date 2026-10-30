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
# Wave 32 Batch 195: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 complete sentence, 0 newlines, max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # Underscore identifiers, NO dotted filenames.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: Alertmanager notification dispatch throttling
    {
        "raw_asr": "basically calibrat r p c notification throttling buy tuning dispatch underscore rate on paging knowed daemons instead",
        "refined_text": "Calibrate RPC notification throttling by tuning dispatch_rate on paging node daemons instead."
    },

    # Sample 2: Envoy access log buffer flushing
    {
        "raw_asr": "um deduplicat c p u access logging buffers buy adjusting flush underscore interval on gateway knowed instances instead",
        "refined_text": "Deduplicate CPU access logging buffers by adjusting flush_interval on gateway node instances instead."
    },

    # Sample 3: Kubernetes kubelet container runtime CRI sync timeout
    {
        "raw_asr": "so basically configur cube let runtime synchronization buy tuning sync underscore timeout on cluster knowed daemons instead",
        "refined_text": "Configure kubelet runtime synchronization by tuning sync_timeout on cluster node daemons instead."
    },

    # Sample 4: PostgreSQL read replica streaming replication socket buffers
    {
        "raw_asr": "uh initializ post gres streaming replication buffers buy tuning socket underscore buffer on replica knowed hosts instead",
        "refined_text": "Initialize Postgres streaming replication buffers by tuning socket_buffer on replica node hosts instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: Ceph object gateway connection backlog saturation
    {
        "raw_asr": "um our ceph gateway cluster suffered object upload stalls when fourteen knowed gateways delayed r p c requests across eighteen seconds wait thirty six seconds instead basically incident responders restored gateway communicat buy adjusting sync underscore threads buy passing dash dash max connections into gateway configur settings while reliability engineers right two r p c backlog probes",
        "refined_text": "Our Ceph gateway cluster suffered object upload stalls when 14 node gateways delayed RPC requests across 36 seconds instead.\n\nIncident responders restored gateway communication by adjusting sync_threads by passing --max-connections into gateway configuration settings while reliability engineers write 2 RPC backlog probes."
    },

    # Sample 6: Consul service discovery catalog sync latency
    {
        "raw_asr": "basically our consul discovery cluster experienced catalog sync delays when sixteen knowed agents dropped leader heartbeats across twelve seconds wait twenty four seconds instead um cluster administrators restored agent operat buy tuning sync underscore rate buy passing dash dash sync threshold into cube let configur manifests while systems engineers right two cube let catalog probes",
        "refined_text": "Our Consul discovery cluster experienced catalog sync delays when 16 node agents dropped leader heartbeats across 24 seconds instead.\n\nCluster administrators restored agent operations by tuning sync_rate by passing --sync-threshold into kubelet configuration manifests while systems engineers write 2 kubelet catalog probes."
    },

    # Sample 7: Vector log forwarding pipeline backpressure
    {
        "raw_asr": "um our log aggregation cluster dropped telemetry events when twenty knowed forwarders encountered downstream socket backpressure across fifteen seconds wait thirty seconds instead basically site reliability engineers restored pipeline synchronizat buy tuning batch underscore timeout buy passing dash dash batch size into vector configur parameters while reliability engineers right two c p u throughput probes",
        "refined_text": "Our log aggregation cluster dropped telemetry events when 20 node forwarders encountered downstream socket backpressure across 30 seconds instead.\n\nSite reliability engineers restored pipeline synchronization by tuning batch_timeout by passing --batch-size into Vector configuration parameters while reliability engineers write 2 CPU throughput probes."
    },

    # Sample 8: Redis Sentinel quorum loss and master failover oscillation
    {
        "raw_asr": "basically our redis cache tier suffered master failover loops when twelve knowed sentinels disagreed on leader health across twenty seconds wait forty five seconds instead um database administrators restored sentinel communicat buy increasing down underscore after underscore milliseconds buy passing dash dash failover timeout into redis configur manifests while platform engineers right two r p c election monitors",
        "refined_text": "Our Redis cache tier suffered master failover loops when 12 node sentinels disagreed on leader health across 45 seconds instead.\n\nDatabase administrators restored sentinel communication by increasing down_after_milliseconds by passing --failover-timeout into Redis configuration manifests while platform engineers write 2 RPC election monitors."
    },

    # Sample 9: Elasticsearch cluster unassigned shards during disk watermark breach
    {
        "raw_asr": "um our search cluster marked primary shards unassigned when ten knowed data nodes hit disk capacity limits across ten seconds wait thirty seconds instead basically infrastructure operators restored shard allocat buy adjusting watermark underscore high buy passing dash dash cluster routing allocation into cube ctl configur commands while platform engineers right two cube ctl disk monitors",
        "refined_text": "Our search cluster marked primary shards unassigned when 10 node data nodes hit disk capacity limits across 30 seconds instead.\n\nInfrastructure operators restored shard allocation by adjusting watermark_high by passing --cluster-routing-allocation into kubectl configuration commands while platform engineers write 2 kubectl disk monitors."
    },

    # Sample 10: NGINX Ingress controller reload storm causing worker CPU spikes
    {
        "raw_asr": "basically our edge ingress proxies dropped incoming client connections when twenty four knowed gateways triggered continuous configuration reloads across twenty seconds wait fifty seconds instead um network administrators restored proxy operat buy adjusting worker underscore connections buy passing dash dash worker shutdown timeout into ingress configur manifests while systems engineers right two wi re shark latency probes",
        "refined_text": "Our edge ingress proxies dropped incoming client connections when 24 node gateways triggered continuous configuration reloads across 50 seconds instead.\n\nNetwork administrators restored proxy operations by adjusting worker_connections by passing --worker-shutdown-timeout into ingress configuration manifests while systems engineers write 2 Wireshark latency probes."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: RabbitMQ quorum queue leader rebalancing during network partition healing
    {
        "raw_asr": "basically during network partition healing our distributed rabbitmq messaging cluster encountered delivery pauses when quorum queue election timeouts triggered leader revocations across twelve knowed brokers wait eighteen brokers instead um concurrent raft leader elections saturated message transport buy driving broker c p u utiliz to ninety two percent across twenty four cluster nodes p ninety five message publish latency jumped from four milliseconds up through two two zero zero milliseconds buy stalling thirty five percent of customer order r p c queries incident responders isolated the primary trigger inside rabbitmq underscore quorum dot conf buy reviewing consensus election logs across slash var slash log platform reliability engineers restored queue synchronizat buy adjusting raft underscore heartbeat buy passing dash dash raft election timeout into broker configur settings while systems administrators right two r p c delivery latency monitors",
        "refined_text": "During network partition healing, our distributed RabbitMQ messaging cluster encountered delivery pauses when quorum queue election timeouts triggered leader revocations across 18 node brokers instead. Concurrent Raft leader elections saturated message transport by driving broker CPU utilization to 92 percent across 24 cluster nodes.\n\nP95 message publish latency jumped from 4 milliseconds up through 2200 milliseconds by stalling 35 percent of customer order RPC queries. Incident responders isolated the primary trigger inside rabbitmq_quorum.conf by reviewing consensus election logs across /var/log.\n\nPlatform reliability engineers restored queue synchronization by adjusting raft_heartbeat by passing --raft-election-timeout into broker configuration settings while systems administrators write 2 RPC delivery latency monitors."
    },

    # Sample 12: Envoy gRPC client stream resets on HTTP/2 connection window exhaustion
    {
        "raw_asr": "um during midday analytics ingestion our service mesh ingress proxies suffered g r p c stream cancellations when initial stream buffers exhausted http two flow control windows across fourteen knowed proxies wait twenty proxies instead basically buffer starvation stalled upstream r p c message transmission buy driving proxy c p u utiliz to ninety three percent across thirty edge instances p ninety nine stream completion latency spiked from five milliseconds up through two six zero zero milliseconds buy failing forty percent of sensor ingest events incident responders isolated the underlying defect inside envoy underscore ingress dot yaml buy evaluating flow control frames across slash var slash log network reliability engineers restored stream communicat buy increasing stream underscore buffer buy passing dash dash initial connection window into proxy configur manifests while site reliability engineers right two wi re shark stream monitors",
        "refined_text": "During midday analytics ingestion, our service mesh ingress proxies suffered gRPC stream cancellations when initial stream buffers exhausted HTTP 2 flow control windows across 20 node proxies instead. Buffer starvation stalled upstream RPC message transmission by driving proxy CPU utilization to 93 percent across 30 edge instances.\n\nP99 stream completion latency spiked from 5 milliseconds up through 2600 milliseconds by failing 40 percent of sensor ingest events. Incident responders isolated the underlying defect inside envoy_ingress.yaml by evaluating flow control frames across /var/log.\n\nNetwork reliability engineers restored stream communication by increasing stream_buffer by passing --initial-connection-window into proxy configuration manifests while site reliability engineers write 2 Wireshark stream monitors."
    },

    # Sample 13: Cassandra commitlog sync latency causing mutation drops
    {
        "raw_asr": "basically during evening transactional processing our cassandra database cluster suffered mutation write timeouts when commitlog disk writes blocked concurrent memtable flushes across sixteen knowed storage daemons wait twenty two storage daemons instead um queued mutation threads delayed database updates buy driving database c p u utiliz to ninety one percent across twenty eight node instances p ninety five write latency climbed from six milliseconds up through two four zero zero milliseconds buy rejecting twenty percent of incoming customer records incident responders isolated the primary trigger inside cassandra underscore storage dot yaml buy inspecting commitlog sync traces across slash var slash log database platform engineers restored database operat buy adjusting sync underscore window buy passing dash dash commitlog sync batch window into cassandra configur settings while reliability engineers right two r p c mutation queue monitors",
        "refined_text": "During evening transactional processing, our Cassandra database cluster suffered mutation write timeouts when commitlog disk writes blocked concurrent memtable flushes across 22 node storage daemons instead. Queued mutation threads delayed database updates by driving database CPU utilization to 91 percent across 28 node instances.\n\nP95 write latency climbed from 6 milliseconds up through 2400 milliseconds by rejecting 20 percent of incoming customer records. Incident responders isolated the primary trigger inside cassandra_storage.yaml by inspecting commitlog sync traces across /var/log.\n\nDatabase platform engineers restored database operations by adjusting sync_window by passing --commitlog-sync-batch-window into Cassandra configuration settings while reliability engineers write 2 RPC mutation queue monitors."
    },

    # Sample 14: Redis cluster cross-slot hash tags causing memory imbalance
    {
        "raw_asr": "um during peak shopping cart checkouts our redis cluster tier rejected client writes when uneven slot distribution concentrated keys across twelve knowed masters wait eighteen masters instead basically skewed memory allocations exhausted local cache space buy driving master c p u utiliz to ninety four percent across twenty four cluster nodes p ninety nine command latency surged from three milliseconds up through two five zero zero milliseconds buy failing thirty percent of customer session r p c requests incident responders diagnosed the primary trigger inside redis underscore cluster dot conf buy tracking memory usage traces across slash var slash log database reliability engineers stabilized memory allocat buy tuning maxmemory underscore samples buy passing dash dash maxmemory policy into redis configur settings while systems administrators right two r p c slot allocation probes",
        "refined_text": "During peak shopping cart checkouts, our Redis cluster tier rejected client writes when uneven slot distribution concentrated keys across 18 node masters instead. Skewed memory allocations exhausted local cache space by driving master CPU utilization to 94 percent across 24 cluster nodes.\n\nP99 command latency surged from 3 milliseconds up through 2500 milliseconds by failing 30 percent of customer session RPC requests. Incident responders diagnosed the primary trigger inside redis_cluster.conf by tracking memory usage traces across /var/log.\n\nDatabase reliability engineers stabilized memory allocation by tuning maxmemory_samples by passing --maxmemory-policy into Redis configuration settings while systems administrators write 2 RPC slot allocation probes."
    },

    # Sample 15: Kafka consumer group rebalance storm on heartbeat thread starvation
    {
        "raw_asr": "basically during heavy event stream processing our kafka consumer tier halted partition consumption when long payload processing triggered coordinator heartbeat timeouts across ten knowed consumer pods wait sixteen consumer pods instead um repeated group rebalances revoked active partition assignments buy driving consumer c p u utiliz to ninety three percent across thirty worker pods p ninety five consumer lag climbed from four milliseconds up through two eight zero zero milliseconds buy stalling forty five percent of data stream records incident responders isolated the underlying defect inside kafka underscore consumer dot conf buy evaluating rebalance logs across slash var slash log streaming platform engineers restored partition synchronizat buy increasing max underscore poll underscore interval buy passing dash dash max poll interval ms into worker configur manifests while reliability engineers right two cube let consumer lag monitors",
        "refined_text": "During heavy event stream processing, our Kafka consumer tier halted partition consumption when long payload processing triggered coordinator heartbeat timeouts across 16 node consumer pods instead. Repeated group rebalances revoked active partition assignments by driving consumer CPU utilization to 93 percent across 30 worker pods.\n\nP95 consumer lag climbed from 4 milliseconds up through 2800 milliseconds by stalling 45 percent of data stream records. Incident responders isolated the underlying defect inside kafka_consumer.conf by evaluating rebalance logs across /var/log.\n\nStreaming platform engineers restored partition synchronization by increasing max_poll_interval by passing --max-poll-interval-ms into worker configuration manifests while reliability engineers write 2 kubelet consumer lag monitors."
    },

    # Sample 16: CoreDNS plugin latency and upstream UDP socket pool starvation
    {
        "raw_asr": "um during external cloud provider network degradation our cluster coredns service dropped domain resolution lookups when upstream forwarding delays exhausted udp socket pools across fourteen knowed resolvers wait twenty resolvers instead basically socket pool contention stalled internal service discovery queries buy driving resolver c p u utiliz to ninety two percent across thirty two cluster instances p ninety nine resolution latency jumped from two milliseconds up through two one zero zero milliseconds buy failing thirty five percent of internal domain lookups incident responders diagnosed the primary trigger inside coredns underscore upstream dot conf buy analyzing packet timeout logs across slash etc network reliability engineers restored resolver communicat buy increasing forward underscore timeout buy passing dash dash upstream timeout into cube ctl configur parameters while platform operators right two cube ctl resolver latency probes",
        "refined_text": "During external cloud provider network degradation, our cluster CoreDNS service dropped domain resolution lookups when upstream forwarding delays exhausted UDP socket pools across 20 node resolvers instead. Socket pool contention stalled internal service discovery queries by driving resolver CPU utilization to 92 percent across 32 cluster instances.\n\nP99 resolution latency jumped from 2 milliseconds up through 2100 milliseconds by failing 35 percent of internal domain lookups. Incident responders diagnosed the primary trigger inside coredns_upstream.conf by analyzing packet timeout logs across /etc.\n\nNetwork reliability engineers restored resolver communication by increasing forward_timeout by passing --upstream-timeout into kubectl configuration parameters while platform operators write 2 kubectl resolver latency probes."
    },

    # Sample 17: Traefik edge proxy TLS handshake timeout under SNI routing storm
    {
        "raw_asr": "basically during sudden promotional traffic spikes our traefik edge proxy layer dropped incoming user connections when tls handshake negotiations exhausted cryptographic worker threads across twelve knowed edge gateways wait eighteen edge gateways instead um pending tls session handshakes locked ingress connection queues buy driving gateway c p u utiliz to ninety five percent across thirty six edge pods p ninety five handshake completion latency climbed from four milliseconds up through two seven zero zero milliseconds buy terminating twenty five percent of client web sessions incident responders isolated the underlying defect inside traefik underscore proxy dot toml buy inspecting tls handshake error traces across slash var slash log site reliability engineers restored proxy operat buy tuning handshake underscore timeout buy passing dash dash max idle conns into gateway configur manifests while systems engineers right two wi re shark handshake probes",
        "refined_text": "During sudden promotional traffic spikes, our Traefik edge proxy layer dropped incoming user connections when TLS handshake negotiations exhausted cryptographic worker threads across 18 node edge gateways instead. Pending TLS session handshakes locked ingress connection queues by driving gateway CPU utilization to 95 percent across 36 edge pods.\n\nP95 handshake completion latency climbed from 4 milliseconds up through 2700 milliseconds by terminating 25 percent of client web sessions. Incident responders isolated the underlying defect inside traefik_proxy.toml by inspecting TLS handshake error traces across /var/log.\n\nSite reliability engineers restored proxy operations by tuning handshake_timeout by passing --max-idle-conns into gateway configuration manifests while systems engineers write 2 Wireshark handshake probes."
    },

    # Sample 18: ClickHouse distributed table query execution hang during remote replica fetch timeout
    {
        "raw_asr": "um during batch reporting job execution our clickhouse analytical cluster encountered query hang states when distributed subqueries waited on unassigned storage parts across ten knowed analytical nodes wait sixteen analytical nodes instead basically unacknowledged part transfers blocked concurrent pipeline threads buy driving server c p u utiliz to ninety one percent across twenty database instances p ninety nine query execution latency surged from six milliseconds up through two nine zero zero milliseconds buy failing forty percent of customer analytics r p c queries incident responders isolated the primary trigger inside clickhouse underscore cluster dot conf buy analyzing remote fetch traces across slash var slash log data platform engineers restored query communicat buy adjusting connect underscore timeout buy passing dash dash max execution time into clickhouse configur parameters while reliability engineers right two r p c query execution monitors",
        "refined_text": "During batch reporting job execution, our ClickHouse analytical cluster encountered query hang states when distributed subqueries waited on unassigned storage parts across 16 node analytical nodes instead. Unacknowledged part transfers blocked concurrent pipeline threads by driving server CPU utilization to 91 percent across 20 database instances.\n\nP99 query execution latency surged from 6 milliseconds up through 2900 milliseconds by failing 40 percent of customer analytics RPC queries. Incident responders isolated the primary trigger inside clickhouse_cluster.conf by analyzing remote fetch traces across /var/log.\n\nData platform engineers restored query communication by adjusting connect_timeout by passing --max-execution-time into ClickHouse configuration parameters while reliability engineers write 2 RPC query execution monitors."
    },

    # Sample 19: OpenSearch shard indexing queue rejection under thread pool saturation
    {
        "raw_asr": "basically during midday telemetry ingestion spikes our opensearch indexing cluster rejected bulk document writes when thread pool capacities overflowed on primary shards across fourteen knowed data nodes wait twenty data nodes instead um saturated write queues blocked downstream indexing requests buy driving cluster c p u utiliz to ninety four percent across twenty eight data instances p ninety five bulk indexing latency climbed from five milliseconds up through two three zero zero milliseconds buy dropping thirty percent of incoming monitoring batches incident responders diagnosed the primary trigger inside opensearch underscore cluster dot yml buy reviewing thread pool rejection metrics across slash var slash log search platform administrators restored shard synchronizat buy adjusting write underscore queue buy passing dash dash thread pool write queue size into cube let configur manifests while site reliability engineers right two cube let indexing delay probes",
        "refined_text": "During midday telemetry ingestion spikes, our OpenSearch indexing cluster rejected bulk document writes when thread pool capacities overflowed on primary shards across 20 node data nodes instead. Saturated write queues blocked downstream indexing requests by driving cluster CPU utilization to 94 percent across 28 data instances.\n\nP95 bulk indexing latency climbed from 5 milliseconds up through 2300 milliseconds by dropping 30 percent of incoming monitoring batches. Incident responders diagnosed the primary trigger inside opensearch_cluster.yml by reviewing thread pool rejection metrics across /var/log.\n\nSearch platform administrators restored shard synchronization by adjusting write_queue by passing --thread-pool-write-queue-size into kubelet configuration manifests while site reliability engineers write 2 kubelet indexing delay probes."
    },

    # Sample 20: Vault dynamic secrets lease renewal lock contention during database failover
    {
        "raw_asr": "um during database secondary failover events our secret management cluster suffered request timeouts when service containers thrashed database lease renewal queries across twelve knowed vault agents wait eighteen vault agents instead basically heavy token renewal queries blocked storage engine locks buy driving post gres c p u utiliz to ninety three percent across twenty database instances p ninety nine credential renewal latency jumped from four milliseconds up through two seven zero zero milliseconds buy failing forty percent of application r p c authorizations incident responders isolated the primary trigger inside vault underscore server dot conf buy reviewing storage contention logs across slash var slash log security reliability engineers stabilized lease terminat buy adjusting lease underscore renewal buy passing dash dash max lease ttl into daemon configur parameters while infrastructure administrators right two post gres lock monitors",
        "refined_text": "During database secondary failover events, our secret management cluster suffered request timeouts when service containers thrashed database lease renewal queries across 18 node vault agents instead. Heavy token renewal queries blocked storage engine locks by driving Postgres CPU utilization to 93 percent across 20 database instances.\n\nP99 credential renewal latency jumped from 4 milliseconds up through 2700 milliseconds by failing 40 percent of application RPC authorizations. Incident responders isolated the primary trigger inside vault_server.conf by reviewing storage contention logs across /var/log.\n\nSecurity reliability engineers stabilized lease termination by adjusting lease_renewal by passing --max-lease-ttl into daemon configuration parameters while infrastructure administrators write 2 Postgres lock monitors."
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
    out_path = Path("scratch/subagent_batch_195.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESS: Written 20 verified samples to {out_path}")

if __name__ == "__main__":
    main()
