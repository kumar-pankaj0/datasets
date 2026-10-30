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

# Domain 4: Incident Management & Live Troubleshooting RCA
# Batch 180 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: Calibrating Redis memory eviction limits
    {
        "raw_asr": "basically calibrat redis memory eviction limits buy tuning maxmemory underscore policy on worker knowed hosts instead",
        "refined_text": "Calibrate Redis memory eviction limits by tuning maxmemory_policy on worker node hosts instead."
    },

    # Sample 2: Terminating deadlocked Postgres vacuum worker threads
    {
        "raw_asr": "um terminat deadlocked post gres vacuum worker threads buy killing backend underscore pid on database knowed servers instead",
        "refined_text": "Terminate deadlocked Postgres vacuum worker threads by killing backend_pid on database node servers instead."
    },

    # Sample 3: Configuring Envoy proxy connection keepalive timeouts
    {
        "raw_asr": "uh configur envoy proxy connection keepalive timeouts buy tuning idle underscore timeout on ingress knowed gateways instead",
        "refined_text": "Configure Envoy proxy connection keepalive timeouts by tuning idle_timeout on ingress node gateways instead."
    },

    # Sample 4: Initializing kubelet worker eviction thresholds
    {
        "raw_asr": "basically initializ cube let worker eviction thresholds buy setting initial underscore delay on cluster knowed workers instead",
        "refined_text": "Initialize kubelet worker eviction thresholds by setting initial_delay on cluster node workers instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: RabbitMQ cluster partition and message acknowledgement queue stall
    {
        "raw_asr": "um our rabbitmq messaging cluster suffered queue ingestion stalls when sixteen knowed brokers split across twenty seconds wait forty seconds instead basically cluster operators restored broker communicat buy adjusting heartbeat underscore timeout buy passing dash dash cluster partition into rabbitmq configur manifests while systems engineers right two c p u socket monitors",
        "refined_text": "Our RabbitMQ messaging cluster suffered queue ingestion stalls when 16 node brokers split across 40 seconds instead.\n\nCluster operators restored broker communication by adjusting heartbeat_timeout by passing --cluster-partition into RabbitMQ configuration manifests while systems engineers write 2 CPU socket monitors."
    },

    # Sample 6: Cassandra read repair thrashing on tombstone overflow
    {
        "raw_asr": "basically our cassandra database cluster experienced read query timeouts when twenty knowed storage daemons scanned excessive tombstones across thirty seconds wait fifty seconds instead um database administrators restored storage operat buy tuning tombstone underscore threshold buy passing dash dash repair timeout into cassandra configur manifests while reliability engineers right two r p c read latency probes",
        "refined_text": "Our Cassandra database cluster experienced read query timeouts when 20 node storage daemons scanned excessive tombstones across 50 seconds instead.\n\nDatabase administrators restored storage operations by tuning tombstone_threshold by passing --repair-timeout into Cassandra configuration manifests while reliability engineers write 2 RPC read latency probes."
    },

    # Sample 7: ClickHouse merge tree part mutation locking query execution
    {
        "raw_asr": "um our clickhouse analytics cluster suffered ingestion stalls when fourteen knowed replicas locked table mutations across twenty seconds wait sixty seconds instead basically analytics engineers restored pipeline communicat buy adjusting mutation underscore limit buy passing dash dash max parts into clickhouse configur manifests while site engineers right two c p u lock monitors",
        "refined_text": "Our ClickHouse analytics cluster suffered ingestion stalls when 14 node replicas locked table mutations across 60 seconds instead.\n\nAnalytics engineers restored pipeline communication by adjusting mutation_limit by passing --max-parts into ClickHouse configuration manifests while site engineers write 2 CPU lock monitors."
    },

    # Sample 8: NATS JetStream consensus raft heartbeat loss during metadata compaction
    {
        "raw_asr": "basically our nats messaging cluster encountered stream election failures when twelve knowed brokers dropped raft heartbeats across fifteen seconds wait forty five seconds instead um messaging platform operators restored cluster operat buy tuning heartbeat underscore interval buy passing dash dash raft timeout into nats configur parameters while reliability engineers right two r p c consensus probes",
        "refined_text": "Our NATS messaging cluster encountered stream election failures when 12 node brokers dropped Raft heartbeats across 45 seconds instead.\n\nMessaging platform operators restored cluster operations by tuning heartbeat_interval by passing --raft-timeout into NATS configuration parameters while reliability engineers write 2 RPC consensus probes."
    },

    # Sample 9: Traefik edge proxy TLS handshake thread exhaustion
    {
        "raw_asr": "um our traefik edge gateway experienced connection reset errors when twenty two knowed proxies exhausted thread pools across twenty seconds wait thirty five seconds instead basically platform engineers restored gateway communicat buy updating connection underscore limit buy passing dash dash max idle into traefik configur manifests while reliability engineers right two wi re shark handshake probes",
        "refined_text": "Our Traefik edge gateway experienced connection reset errors when 22 node proxies exhausted thread pools across 35 seconds instead.\n\nPlatform engineers restored gateway communication by updating connection_limit by passing --max-idle into Traefik configuration manifests while reliability engineers write 2 Wireshark handshake probes."
    },

    # Sample 10: CockroachDB range leaseholder rebalancing thrashing under disk IO pressure
    {
        "raw_asr": "basically our cockroachdb cluster suffered transaction commit latencies when eighteen knowed coordinators thrashed range leases across twenty seconds wait fifty seconds instead um database administrators restored storage operat buy tuning rebalance underscore rate buy passing dash dash lease timeout into cockroachdb configur manifests while infrastructure operators right two r p c lease probes",
        "refined_text": "Our CockroachDB cluster suffered transaction commit latencies when 18 node coordinators thrashed range leases across 50 seconds instead.\n\nDatabase administrators restored storage operations by tuning rebalance_rate by passing --lease-timeout into CockroachDB configuration manifests while infrastructure operators write 2 RPC lease probes."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Production Incident RCA: Elasticsearch index rate throttling on translog sync latency
    {
        "raw_asr": "basically during morning data ingestion spikes our elasticsearch logging cluster encountered write rejection errors when primary shards blocked bulk index requests across sixteen knowed indexing nodes wait twenty four indexing nodes instead um heavy translog flushes to disk saturated storage queues buy driving node c p u utiliz to ninety two percent across thirty cluster nodes p ninety five write latency jumped from five milliseconds up through eighteen hundred milliseconds buy dropping twenty five percent of incoming audit events incident responders isolated the primary trigger inside elasticsearch underscore storage dot yml buy analyzing shard thread dump traces across slash var slash log platform engineers stabilized storage synchronizat buy tuning translog underscore sync buy passing dash dash flush threshold into cluster configur parameters while site reliability engineers right two r p c indexing queue monitors",
        "refined_text": "During morning data ingestion spikes, our Elasticsearch logging cluster encountered write rejection errors when primary shards blocked bulk index requests across 24 node indexing nodes instead. Heavy translog flushes to disk saturated storage queues by driving node CPU utilization to 92 percent across 30 cluster nodes.\n\nP95 write latency jumped from 5 milliseconds up through 1800 milliseconds by dropping 25 percent of incoming audit events. Incident responders isolated the primary trigger inside elasticsearch_storage.yml by analyzing shard thread dump traces across /var/log.\n\nPlatform engineers stabilized storage synchronization by tuning translog_sync by passing --flush-threshold into cluster configuration parameters while site reliability engineers write 2 RPC indexing queue monitors."
    },

    # Sample 12: Live Troubleshooting RCA: Envoy gRPC multiplexed stream reset flood on HTTP/2 GOAWAY
    {
        "raw_asr": "um during backend service deployments our ingress edge proxies suffered request termination errors when downstream g r p c streams encountered premature goaway frames across twelve knowed proxies wait eighteen proxies instead basically asynchronous connection pool resets dropped active client connections buy driving gateway c p u utiliz to ninety four percent across twenty five proxy instances p ninety nine request latency spiked from four milliseconds up through two two zero zero milliseconds buy failing status five zero three errors across six thousand user transactions incident responders diagnosed the primary trigger inside envoy underscore ingress dot yaml buy evaluating stream trace events across slash var slash log networking engineers restored proxy communicat buy adjusting stream underscore idle buy passing dash dash connection timeout into envoy configur manifests while platform operators right two r p c gateway health probes",
        "refined_text": "During backend service deployments, our ingress edge proxies suffered request termination errors when downstream gRPC streams encountered premature GOAWAY frames across 18 node proxies instead. Asynchronous connection pool resets dropped active client connections by driving gateway CPU utilization to 94 percent across 25 proxy instances.\n\nP99 request latency spiked from 4 milliseconds up through 2200 milliseconds by failing status 503 errors across 6000 user transactions. Incident responders diagnosed the primary trigger inside envoy_ingress.yaml by evaluating stream trace events across /var/log.\n\nNetworking engineers restored proxy communication by adjusting stream_idle by passing --connection-timeout into Envoy configuration manifests while platform operators write 2 RPC gateway health probes."
    },

    # Sample 13: Sev-1 Incident Postmortem: Kafka broker controller partition leader election deadlock
    {
        "raw_asr": "basically our kafka streaming tier encountered publish acknowledge timeouts when partition leader elections stalled across ten knowed brokers wait sixteen brokers instead um high volume metadata queue serialization blocked controller consensus threads buy driving host c p u utiliz to ninety one percent across twenty cluster nodes cluster partitions entered offline states buy dropping thirty thousand telemetry events across fifteen minutes p ninety five publish latency climbed from six milliseconds up through twenty six hundred milliseconds wait three zero zero zero milliseconds instead buy triggering incident alarms incident responders diagnosed the failure mechanism inside kafka underscore server dot conf buy inspecting controller log dumps across slash proc platform engineers stabilized broker synchronizat buy adjusting leader underscore grace buy passing dash dash controller timeout into kafka configur settings while site reliability engineers right two a sink queue throughput monitors",
        "refined_text": "Our Kafka streaming tier encountered publish acknowledge timeouts when partition leader elections stalled across 16 node brokers instead. High-volume metadata queue serialization blocked controller consensus threads by driving host CPU utilization to 91 percent across 20 cluster nodes.\n\nCluster partitions entered offline states by dropping 30000 telemetry events across 15 minutes. P95 publish latency climbed from 6 milliseconds up through 3000 milliseconds instead by triggering incident alarms.\n\nIncident responders diagnosed the failure mechanism inside kafka_server.conf by inspecting controller log dumps across /proc. Platform engineers stabilized broker synchronization by adjusting leader_grace by passing --controller-timeout into Kafka configuration settings while site reliability engineers write 2 async queue throughput monitors."
    },

    # Sample 14: Production Incident RCA: Redis Cluster slot migration lockup causing client redirection storm
    {
        "raw_asr": "um our distributed caching tier experienced client redirection storms when cluster slot migration stalled across twelve knowed masters wait twenty masters instead basically uncommitted key migration batches blocked redis event loops buy driving master c p u utiliz to ninety five percent across thirty cache instances client connection pools exhausted available sockets buy generating status five zero zero errors across eight thousand session lookups p ninety nine cache query latency climbed from three milliseconds up through sixteen hundred milliseconds incident responders isolated the primary trigger inside redis underscore cluster dot conf buy analyzing memory migration logs across slash var slash log cache platform administrators restored cluster operat buy tuning migration underscore batch buy passing dash dash slot timeout into redis configur manifests while site engineers right two r p c slot migration probes",
        "refined_text": "Our distributed caching tier experienced client redirection storms when cluster slot migration stalled across 20 node masters instead. Uncommitted key migration batches blocked Redis event loops by driving master CPU utilization to 95 percent across 30 cache instances.\n\nClient connection pools exhausted available sockets by generating status 500 errors across 8000 session lookups. P99 cache query latency climbed from 3 milliseconds up through 1600 milliseconds.\n\nIncident responders isolated the primary trigger inside redis_cluster.conf by analyzing memory migration logs across /var/log. Cache platform administrators restored cluster operations by tuning migration_batch by passing --slot-timeout into Redis configuration manifests while site engineers write 2 RPC slot migration probes."
    },

    # Sample 15: Live Incident Troubleshooting: Kubelet PIDs cgroup exhaustion triggering pod eviction storm
    {
        "raw_asr": "basically our container compute cluster suffered widespread workload terminations when worker hosts exhausted kernel process identifiers across fourteen knowed compute nodes wait twenty compute nodes instead um rogue worker tasks spawned runaway threads buy driving host c p u utiliz to ninety percent across twenty five worker hosts cube let daemon threads failed to fork container health checks buy triggering status five zero three scheduling evictions across fifty application pods p ninety five pod startup latency surged from eight milliseconds up through two four zero zero milliseconds incident responders diagnosed the primary trigger inside kubelet underscore config dot yaml buy reviewing cgroup event traces across slash proc systems engineers stabilized node operat buy updating max underscore pids buy passing dash dash pid limit into cube let configur settings while site reliability engineers right two c p u process table probes",
        "refined_text": "Our container compute cluster suffered widespread workload terminations when worker hosts exhausted kernel process identifiers across 20 node compute nodes instead. Rogue worker tasks spawned runaway threads by driving host CPU utilization to 90 percent across 25 worker hosts.\n\nKubelet daemon threads failed to fork container health checks by triggering status 503 scheduling evictions across 50 application pods. P95 pod startup latency surged from 8 milliseconds up through 2400 milliseconds.\n\nIncident responders diagnosed the primary trigger inside kubelet_config.yaml by reviewing cgroup event traces across /proc. Systems engineers stabilized node operations by updating max_pids by passing --pid-limit into kubelet configuration settings while site reliability engineers write 2 CPU process table probes."
    },

    # Sample 16: Sev-1 Outage Postmortem: Consul Service Mesh intentions sync lag causing access denial storm
    {
        "raw_asr": "um our service mesh interconnect suffered critical authorization failures when intentions synchronization lagged across ten knowed agents wait sixteen agents instead basically high frequency access policy updates starved consensus replication threads buy driving server c p u utiliz to ninety three percent across twenty mesh coordinators downstream microservices rejected incoming r p c traffic buy dropping forty thousand api calls across twenty minutes p ninety nine authorization latency spiked from four milliseconds up through eighteen hundred milliseconds incident responders diagnosed the underlying defect inside consul underscore mesh dot json buy evaluating policy replication logs across slash var slash log security engineers restored service communicat buy adjusting sync underscore rate buy passing dash dash sync interval into consul configur parameters while infrastructure operators right two wi re shark traffic inspection probes",
        "refined_text": "Our service mesh interconnect suffered critical authorization failures when intentions synchronization lagged across 16 node agents instead. High-frequency access policy updates starved consensus replication threads by driving server CPU utilization to 93 percent across 20 mesh coordinators.\n\nDownstream microservices rejected incoming RPC traffic by dropping 40000 API calls across 20 minutes. P99 authorization latency spiked from 4 milliseconds up through 1800 milliseconds.\n\nIncident responders diagnosed the underlying defect inside consul_mesh.json by evaluating policy replication logs across /var/log. Security engineers restored service communication by adjusting sync_rate by passing --sync-interval into Consul configuration parameters while infrastructure operators write 2 Wireshark traffic inspection probes."
    },

    # Sample 17: Production Incident RCA: Ceph OSD peering deadlock on PG log truncation under network flap
    {
        "raw_asr": "basically our distributed object storage cluster experienced IO freezes when object storage daemons entered peering deadlocks across twelve knowed storage hosts wait eighteen storage hosts instead um transient top of rack switch drops corrupted recovery log records buy driving storage c p u utiliz to ninety one percent across twenty four storage nodes unpeered placement groups blocked write admissions buy causing status five zero three gateway timeouts across five thousand storage requests p ninety five write latency jumped from seven milliseconds up through two two zero zero milliseconds incident responders isolated the primary trigger inside ceph underscore cluster dot conf buy analyzing peering event logs across slash var slash log storage platform engineers stabilized storage synchronizat buy adjusting pg underscore log buy passing dash dash peering timeout into ceph configur manifests while site reliability engineers right two r p c recovery status monitors",
        "refined_text": "Our distributed object storage cluster experienced IO freezes when object storage daemons entered peering deadlocks across 18 node storage hosts instead. Transient top-of-rack switch drops corrupted recovery log records by driving storage CPU utilization to 91 percent across 24 storage nodes.\n\nUnpeered placement groups blocked write admissions by causing status 503 gateway timeouts across 5000 storage requests. P95 write latency jumped from 7 milliseconds up through 2200 milliseconds.\n\nIncident responders isolated the primary trigger inside ceph_cluster.conf by analyzing peering event logs across /var/log. Storage platform engineers stabilized storage synchronization by adjusting pg_log by passing --peering-timeout into Ceph configuration manifests while site reliability engineers write 2 RPC recovery status monitors."
    },

    # Sample 18: Live Troubleshooting RCA: Postgres connection pool exhaustion on long-running advisory locks
    {
        "raw_asr": "um our relational database fleet suffered severe connection pool exhaustion when unreleased advisory locks blocked client threads across sixteen knowed database replicas wait twenty two database replicas instead basically orphaned transaction sessions held exclusive table locks buy driving database c p u utiliz to ninety four percent across thirty database instances post gres connection pools filled to maximum capacity buy rejecting incoming customer payments with status five zero four gateway timeouts p ninety nine transaction latency climbed from five milliseconds up through twenty eight hundred milliseconds wait three zero zero zero milliseconds instead incident responders isolated the failure mechanism inside pgbouncer underscore pool dot conf buy inspecting connection queue traces across slash proc database administrators restored connection communicat buy tuning lock underscore timeout buy passing dash dash pool size into pgbouncer configur manifests while site reliability engineers right two r p c connection pool probes",
        "refined_text": "Our relational database fleet suffered severe connection pool exhaustion when unreleased advisory locks blocked client threads across 22 node database replicas instead. Orphaned transaction sessions held exclusive table locks by driving database CPU utilization to 94 percent across 30 database instances.\n\nPostgres connection pools filled to maximum capacity by rejecting incoming customer payments with status 504 gateway timeouts. P99 transaction latency climbed from 5 milliseconds up through 3000 milliseconds instead.\n\nIncident responders isolated the failure mechanism inside pgbouncer_pool.conf by inspecting connection queue traces across /proc. Database administrators restored connection communication by tuning lock_timeout by passing --pool-size into pgBouncer configuration manifests while site reliability engineers write 2 RPC connection pool probes."
    },

    # Sample 19: Sev-1 Incident Postmortem: Argo Workflows controller rate-limiter thrashing on CRD watch flood
    {
        "raw_asr": "basically our workflow orchestration tier suffered job scheduling freezes when controller watch streams encountered excessive event bursts across fourteen knowed orchestrators wait twenty orchestrators instead um rapid state transition events triggered kubernetes client rate limits buy driving controller c p u utiliz to ninety two percent across twenty five controller pods automated pipeline dispatches failed buy dropping forty five workflow jobs across twenty minutes p ninety five dispatch latency climbed from six milliseconds up through sixteen hundred milliseconds incident responders diagnosed the primary trigger inside argo underscore controller dot yaml buy analyzing client rate limit traces across slash var slash log platform engineers restored controller operat buy tuning qps underscore limit buy passing dash dash burst limit into argo configur parameters while site reliability engineers right two automated cube ctl workflow monitors",
        "refined_text": "Our workflow orchestration tier suffered job scheduling freezes when controller watch streams encountered excessive event bursts across 20 node orchestrators instead. Rapid state transition events triggered Kubernetes client rate limits by driving controller CPU utilization to 92 percent across 25 controller pods.\n\nAutomated pipeline dispatches failed by dropping 45 workflow jobs across 20 minutes. P95 dispatch latency climbed from 6 milliseconds up through 1600 milliseconds.\n\nIncident responders diagnosed the primary trigger inside argo_controller.yaml by analyzing client rate limit traces across /var/log. Platform engineers restored controller operations by tuning qps_limit by passing --burst-limit into Argo configuration parameters while site reliability engineers write 2 automated kubectl workflow monitors."
    },

    # Sample 20: Live Troubleshooting RCA: Istio Citadel certificate rotation deadlock under Envoy SDS reconnects
    {
        "raw_asr": "um during cluster security updates our service mesh ingress suffered mutual tls handshake failures when certificate secret rotation deadlocked across twelve knowed gateways wait eighteen gateways instead basically concurrent secret discovery requests blocked citadel issuance queues buy driving mesh c p u utiliz to ninety five percent across thirty ingress instances proxy sidecars rejected incoming application traffic buy generating status five zero three errors across nine thousand customer requests p ninety nine ingress latency spiked from four milliseconds up through two four zero zero milliseconds incident responders isolated the primary trigger inside istio underscore citadel dot yaml buy analyzing sds authentication logs across slash var slash log security platform engineers stabilized certificate synchronizat buy adjusting rotation underscore grace buy passing dash dash cert timeout into istio configur manifests while reliability engineers right two wi re shark certificate exchange probes",
        "refined_text": "During cluster security updates, our service mesh ingress suffered mutual TLS handshake failures when certificate secret rotation deadlocked across 18 node gateways instead. Concurrent secret discovery requests blocked Citadel issuance queues by driving mesh CPU utilization to 95 percent across 30 ingress instances.\n\nProxy sidecars rejected incoming application traffic by generating status 503 errors across 9000 customer requests. P99 ingress latency spiked from 4 milliseconds up through 2400 milliseconds.\n\nIncident responders isolated the primary trigger inside istio_citadel.yaml by analyzing SDS authentication logs across /var/log. Security platform engineers stabilized certificate synchronization by adjusting rotation_grace by passing --cert-timeout into Istio configuration manifests while reliability engineers write 2 Wireshark certificate exchange probes."
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
            tier_counts["short"] += 1
        elif words < 90:
            tier_counts["medium"] += 1
        else:
            tier_counts["long"] += 1
        
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
        out_path = Path("scratch/subagent_batch_180.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
