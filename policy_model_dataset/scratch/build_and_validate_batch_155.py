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

# Domain 4: Incident Management & Live Troubleshooting RCA
# Batch 155 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: RPC worker thread stall termination
    {
        "raw_asr": "um terminat unresponsive r p c socket connections buy purging socket underscore timeout on worker knowed hosts instead",
        "refined_text": "Terminate unresponsive RPC socket connections by purging socket_timeout on worker node hosts instead."
    },

    # Sample 2: Wireshark packet capture buffer calibration
    {
        "raw_asr": "basically calibrat packet capture buffer thresholds buy tuning capture underscore buffer with wi re shark instead",
        "refined_text": "Calibrate packet capture buffer thresholds by tuning capture_buffer with Wireshark instead."
    },

    # Sample 3: Postgres replication health check configuration
    {
        "raw_asr": "uh configur post gres replication health checks buy monitoring replica underscore delay across knowed instances instead",
        "refined_text": "Configure Postgres replication health checks by monitoring replica_delay across node instances instead."
    },

    # Sample 4: Kubelet pod eviction grace period initialization
    {
        "raw_asr": "um initializ cube let container eviction limits buy setting eviction underscore grace on worker knowed hosts instead",
        "refined_text": "Initialize kubelet container eviction limits by setting eviction_grace on worker node hosts instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: RabbitMQ connection queue credit stall
    {
        "raw_asr": "um our rabbitmq cluster suffered connection stalls after forty consumer knowed instances exceeded credit limits across twenty seconds wait forty seconds instead basically incident responders stabilized queue operat buy tuning channel underscore max buy passing dash dash max message size into cluster configur files while platform engineers right two heartbeat probes tracking c p u load",
        "refined_text": "Our RabbitMQ cluster suffered connection stalls after 40 consumer node instances exceeded credit limits across 40 seconds instead.\n\nIncident responders stabilized queue operations by tuning channel_max by passing --max-message-size into cluster configuration files while platform engineers write 2 heartbeat probes tracking CPU load."
    },

    # Sample 6: CockroachDB range leaseholder heartbeat starvation
    {
        "raw_asr": "basically our distributed cockroachdb cluster suffered query stalls after sixteen knowed leaseholders missed heartbeat checks across thirty seconds wait fifty seconds instead um incident responders restored range communicat buy extending lease underscore holder underscore timeout buy passing dash dash election timeout into cluster configur settings while database engineers right two r p c probe monitors",
        "refined_text": "Our distributed CockroachDB cluster suffered query stalls after 16 node leaseholders missed heartbeat checks across 50 seconds instead.\n\nIncident responders restored range communication by extending lease_holder_timeout by passing --election-timeout into cluster configuration settings while database engineers write 2 RPC probe monitors."
    },

    # Sample 7: HAProxy backend health-check flapping and connection queue saturation
    {
        "raw_asr": "um our edge load balancer dropped incoming web sessions when thirty proxy workers reached connection saturation across six knowed backends wait eight backends instead basically site reliability engineers restored proxy operat buy adjusting timeout underscore connect buy passing dash dash max conn into proxy configur manifests while network engineers right two wi re shark traffic analyzers",
        "refined_text": "Our edge load balancer dropped incoming web sessions when 30 proxy workers reached connection saturation across 8 backends instead.\n\nSite reliability engineers restored proxy operations by adjusting timeout_connect by passing --max-conn into proxy configuration manifests while network engineers write 2 Wireshark traffic analyzers."
    },

    # Sample 8: Elasticsearch write thread pool saturation and indexing rejections
    {
        "raw_asr": "basically our search cluster suffered indexing write rejections after eight worker knowed instances saturated write thread pools across twenty seconds wait forty seconds instead um incident responders stabilized indexing operat buy tuning write underscore queue underscore size buy passing dash dash thread pool into search configur files while systems engineers right two c p u saturation monitors",
        "refined_text": "Our search cluster suffered indexing write rejections after 8 worker node instances saturated write thread pools across 40 seconds instead.\n\nIncident responders stabilized indexing operations by tuning write_queue_size by passing --thread-pool into search configuration files while systems engineers write 2 CPU saturation monitors."
    },

    # Sample 9: Envoy proxy circuit breaker trip and connection pool collapse
    {
        "raw_asr": "um our service mesh proxies triggered circuit breaker trips after twelve upstream services exceeded pending requests across fifteen seconds wait thirty seconds instead basically platform engineers restored mesh communicat buy adjusting max underscore pending underscore requests buy passing dash dash cluster name into envoy configur manifests while site reliability engineers right two a sink metrics probes",
        "refined_text": "Our service mesh proxies triggered circuit breaker trips after 12 upstream services exceeded pending requests across 30 seconds instead.\n\nPlatform engineers restored mesh communication by adjusting max_pending_requests by passing --cluster-name into Envoy configuration manifests while site reliability engineers write 2 async metrics probes."
    },

    # Sample 10: Ceph storage OSD peer latency stall
    {
        "raw_asr": "basically our storage cluster encountered blocked io operations after sixteen osd knowed daemons suffered disk sync latency across thirty seconds wait forty five seconds instead um storage operators resolved volume allocat buy increasing osd underscore op underscore timeout buy passing dash dash cluster network into ceph configur settings while infrastructure engineers right two r p c recovery monitors",
        "refined_text": "Our storage cluster encountered blocked IO operations after 16 OSD node daemons suffered disk sync latency across 45 seconds instead.\n\nStorage operators resolved volume allocations by increasing osd_op_timeout by passing --cluster-network into Ceph configuration settings while infrastructure engineers write 2 RPC recovery monitors."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Sev-1 Outage RCA: ClickHouse distributed query memory limit exhaustion
    {
        "raw_asr": "basically during our analytics peak traffic wave our clickhouse cluster encountered query execution timeouts across sixteen downstream reporting dashboards after worker processes exceeded memory limits across eight knowed hosts wait twelve hosts instead um complex analytical aggregations exhausted physical server ram buy driving c p u utiliz to ninety percent while query workers crashed repeatedly p ninety five query latency jumped from forty milliseconds up through three five zero zero milliseconds buy dropping forty percent of client r p c requests incident responders diagnosed the primary trigger inside query underscore pipeline dot py buy checking server error logs across slash var slash log platform operators mitigated the memory crash buy raising max underscore server underscore memory buy passing dash dash max threads into daemon configur parameters while site reliability engineers right three automated memory pressure monitors",
        "refined_text": "During our analytics peak traffic wave, our ClickHouse cluster encountered query execution timeouts across 16 downstream reporting dashboards after worker processes exceeded memory limits across 12 node hosts instead. Complex analytical aggregations exhausted physical server RAM by driving CPU utilization to 90 percent while query workers crashed repeatedly.\n\nP95 query latency jumped from 40 milliseconds up through 3500 milliseconds by dropping 40 percent of client RPC requests. Incident responders diagnosed the primary trigger inside query_pipeline.py by checking server error logs across /var/log.\n\nPlatform operators mitigated the memory crash by raising max_server_memory by passing --max-threads into daemon configuration parameters while site reliability engineers write 3 automated memory pressure monitors."
    },

    # Sample 12: Incident Postmortem: Envoy edge proxy TLS certificate handshake timeout
    {
        "raw_asr": "um our edge ingress proxy tier dropped client https sessions when incoming tls handshakes timed out across twenty knowed proxies wait thirty two proxies instead basically worker threads blocked on cryptographic key parsing during certificate rotation buy exhausting available event loop slots proxies returned status five zero three errors across twenty thousand client sessions over twenty minutes p ninety nine connection latency surged from six milliseconds up through sixteen hundred milliseconds buy triggering widespread client timeout alarms incident responders diagnosed the underlying defect inside ingress underscore gateway dot yaml buy analyzing wi re shark packet traces across slash etc platform engineers restored proxy communicat buy executing cube ctl rollout restart buy passing dash dash concurrency into envoy configur parameters while security engineers right two synthetic tls handshake health probes",
        "refined_text": "Our edge ingress proxy tier dropped client HTTPS sessions when incoming TLS handshakes timed out across 32 node proxies instead. Worker threads blocked on cryptographic key parsing during certificate rotation by exhausting available event loop slots.\n\nProxies returned status 503 errors across 20000 client sessions over 20 minutes. P99 connection latency surged from 6 milliseconds up through 1600 milliseconds by triggering widespread client timeout alarms.\n\nIncident responders diagnosed the underlying defect inside ingress_gateway.yaml by analyzing Wireshark packet traces across /etc. Platform engineers restored proxy communication by executing kubectl rollout restart by passing --concurrency into Envoy configuration parameters while security engineers write 2 synthetic TLS handshake health probes."
    },

    # Sample 13: Live Incident Troubleshooting: Redis Cluster slot migration deadlock
    {
        "raw_asr": "basically our production caching tier encountered key routing lockups when online cluster resharding stalled across sixteen knowed shards wait twenty four shards instead um hash slot rebalancing blocked master write execution buy driving c p u utiliz to ninety five percent across forty worker nodes p ninety five write latency jumped from two milliseconds up through twelve hundred milliseconds buy triggering status five zero four gateway timeouts on eight thousand database transactions incident responders isolated the underlying defect inside redis underscore cluster dot conf buy inspecting memory telemetry across slash proc database administrators restored cluster migrat buy adjusting slot underscore migration underscore timeout buy passing dash dash cluster timeout into redis configur parameters while platform reliability engineers right two r p c cluster health monitors",
        "refined_text": "Our production caching tier encountered key routing lockups when online cluster resharding stalled across 24 node shards instead. Hash slot rebalancing blocked master write execution by driving CPU utilization to 95 percent across 40 worker nodes.\n\nP95 write latency jumped from 2 milliseconds up through 1200 milliseconds by triggering status 504 gateway timeouts on 8000 database transactions. Incident responders isolated the underlying defect inside redis_cluster.conf by inspecting memory telemetry across /proc.\n\nDatabase administrators restored cluster migration by adjusting slot_migration_timeout by passing --cluster-timeout into Redis configuration parameters while platform reliability engineers write 2 RPC cluster health monitors."
    },

    # Sample 14: Incident Postmortem: PgBouncer connection pooler FD exhaustion
    {
        "raw_asr": "um our database access layer suffered severe query queuing when connection poolers exhausted client socket descriptors across eight knowed proxies wait twelve proxies instead basically long running analytical transactions held backend post gres sessions open buy preventing forty web services from acquiring database connections p ninety nine transaction latency surged from eight milliseconds up through two thousand milliseconds buy generating status five zero two bad gateway errors on fifteen thousand client requests incident responders diagnosed the primary trigger inside pgbouncer underscore pool dot conf buy evaluating wi re shark connection traces across slash var slash log platform engineers stabilized socket allocat buy raising max underscore client underscore conn buy passing dash dash default pool size into daemon configur files while database administrators right three pool saturation probes",
        "refined_text": "Our database access layer suffered severe query queuing when connection poolers exhausted client socket descriptors across 12 node proxies instead. Long-running analytical transactions held backend Postgres sessions open by preventing 40 web services from acquiring database connections.\n\nP99 transaction latency surged from 8 milliseconds up through 2000 milliseconds by generating status 502 bad gateway errors on 15000 client requests. Incident responders diagnosed the primary trigger inside pgbouncer_pool.conf by evaluating Wireshark connection traces across /var/log.\n\nPlatform engineers stabilized socket allocation by raising max_client_conn by passing --default-pool-size into daemon configuration files while database administrators write 3 pool saturation probes."
    },

    # Sample 15: Sev-1 Incident Postmortem: Kafka partition leader rebalance storm
    {
        "raw_asr": "basically our event streaming pipeline suffered partition rebalancing storms after broker heartbeats dropped across ten knowed brokers wait sixteen brokers instead um repeated leader reelections triggered partition desynchronization buy driving broker c p u utiliz to ninety four percent across sixty consumer groups p ninety five producer publish latency jumped from twelve milliseconds up through eighteen hundred milliseconds buy dropping sixty thousand sensor telemetry events incident responders isolated the primary trigger inside kafka underscore broker dot properties buy tracking network socket metrics across slash proc streaming platform engineers restored partition synchronizat buy extending replica underscore lag underscore max buy passing dash dash zookeeper connect into broker configur manifests while site reliability engineers right two r p c consumer lag probes",
        "refined_text": "Our event streaming pipeline suffered partition rebalancing storms after broker heartbeats dropped across 16 node brokers instead. Repeated leader reelections triggered partition desynchronization by driving broker CPU utilization to 94 percent across 60 consumer groups.\n\nP95 producer publish latency jumped from 12 milliseconds up through 1800 milliseconds by dropping 60000 sensor telemetry events. Incident responders isolated the primary trigger inside kafka_broker.properties by tracking network socket metrics across /proc.\n\nStreaming platform engineers restored partition synchronization by extending replica_lag_max by passing --zookeeper-connect into broker configuration manifests while site reliability engineers write 2 RPC consumer lag probes."
    },

    # Sample 16: Live Troubleshooting RCA: Kubernetes Kubelet PIDs limit exhaustion
    {
        "raw_asr": "um our worker clusters entered degraded states when uncollected child processes exhausted kernel thread limits across twelve knowed hosts wait twenty hosts instead basically rogue background tasks spawned twenty thousand processes buy causing cube let health checks to timeout across forty worker pods node controllers marked twenty hosts as not ready buy causing cube ctl pod scheduling to fail with status five zero zero errors across thirty worker containers incident responders diagnosed the underlying defect inside kubelet underscore config dot yaml buy reviewing host process counts across slash etc systems administrators resolved process terminat buy killing runaway worker trees buy passing dash dash pod max pids into kubelet configur parameters while platform engineers right two automated pid consumption probes",
        "refined_text": "Our worker clusters entered degraded states when uncollected child processes exhausted kernel thread limits across 20 node hosts instead. Rogue background tasks spawned 20000 processes by causing kubelet health checks to timeout across 40 worker pods.\n\nNode controllers marked 20 hosts as not ready by causing kubectl pod scheduling to fail with status 500 errors across 30 worker containers. Incident responders diagnosed the underlying defect inside kubelet_config.yaml by reviewing host process counts across /etc.\n\nSystems administrators resolved process termination by killing runaway worker trees by passing --pod-max-pids into kubelet configuration parameters while platform engineers write 2 automated PID consumption probes."
    },

    # Sample 17: Incident Postmortem: PHP-FPM process pool worker starvation
    {
        "raw_asr": "basically our web application tier dropped incoming customer requests when dynamic process pools exhausted execution workers across twenty knowed servers wait thirty servers instead um slow third party api responses locked worker processes buy driving host c p u utiliz to ninety percent and starving incoming connections p ninety five response latency surged from fifteen milliseconds up through two thousand milliseconds buy triggering status five zero two bad gateway errors across ten thousand customer sessions incident responders isolated the primary trigger inside php underscore fpm dot conf buy evaluating wi re shark traffic dumps across slash var slash log platform engineers stabilized application operat buy increasing pm underscore max underscore children buy passing dash dash process control into pool configur settings while site reliability engineers right two worker pool health monitors",
        "refined_text": "Our web application tier dropped incoming customer requests when dynamic process pools exhausted execution workers across 30 node servers instead. Slow third-party API responses locked worker processes by driving host CPU utilization to 90 percent and starving incoming connections.\n\nP95 response latency surged from 15 milliseconds up through 2000 milliseconds by triggering status 502 bad gateway errors across 10000 customer sessions. Incident responders isolated the primary trigger inside php_fpm.conf by evaluating Wireshark traffic dumps across /var/log.\n\nPlatform engineers stabilized application operations by increasing pm_max_children by passing --process-control into pool configuration settings while site reliability engineers write 2 worker pool health monitors."
    },

    # Sample 18: Live Incident Troubleshooting: FastAPI asyncio event loop blocking on disk IO
    {
        "raw_asr": "um our checkout microservice suffered transaction execution delays after synchronous disk writes blocked asynchronous event loops across eight knowed containers wait twelve containers instead basically unbuffered receipt generation halted a sink i o scheduling buy freezing thirty worker threads across four service instances p ninety nine request latency climbed from ten milliseconds up through two four zero zero milliseconds buy triggering status five zero four gateway timeout errors on five thousand transactions incident responders diagnosed the primary trigger inside checkout underscore api dot py buy tracking thread contention metrics across slash proc software engineers restored loop initializ buy offloading file writes towards executor threads buy passing dash dash worker class into web server configur files while platform engineers right two r p c event loop latency probes",
        "refined_text": "Our checkout microservice suffered transaction execution delays after synchronous disk writes blocked asynchronous event loops across 12 node containers instead. Unbuffered receipt generation halted asyncio scheduling by freezing 30 worker threads across 4 service instances.\n\nP99 request latency climbed from 10 milliseconds up through 2400 milliseconds by triggering status 504 gateway timeout errors on 5000 transactions. Incident responders diagnosed the primary trigger inside checkout_api.py by tracking thread contention metrics across /proc.\n\nSoftware engineers restored loop initialization by offloading file writes towards executor threads by passing --worker-class into web server configuration files while platform engineers write 2 RPC event loop latency probes."
    },

    # Sample 19: Incident Postmortem: CoreDNS upstream DNS query throttling
    {
        "raw_asr": "basically internal service discovery degraded when cluster dns forwarders reached upstream rate limits across six knowed pods wait ten pods instead um dropped udp packets triggered exponential dns retry storms buy pushing c p u utiliz to ninety two percent across fifty cluster nodes p ninety five resolution latency surged from three milliseconds up through fifteen hundred milliseconds buy generating status five zero three service unavailable errors on twelve thousand service calls incident responders isolated the primary trigger inside coredns underscore config dot yaml buy reviewing forwarding logs across slash etc cluster operators restored domain communicat buy increasing cache underscore ttl underscore seconds buy passing dash dash dns policy into cube ctl deployment configur files while reliability engineers right three synthetic dns resolution monitors",
        "refined_text": "Internal service discovery degraded when cluster DNS forwarders reached upstream rate limits across 10 node pods instead. Dropped UDP packets triggered exponential DNS retry storms by pushing CPU utilization to 92 percent across 50 cluster nodes.\n\nP95 resolution latency surged from 3 milliseconds up through 1500 milliseconds by generating status 503 service unavailable errors on 12000 service calls. Incident responders isolated the primary trigger inside coredns_config.yaml by reviewing forwarding logs across /etc.\n\nCluster operators restored domain communication by increasing cache_ttl_seconds by passing --dns-policy into kubectl deployment configuration files while reliability engineers write 3 synthetic DNS resolution monitors."
    },

    # Sample 20: Live Troubleshooting RCA: Linux NIC RX ring buffer packet drop
    {
        "raw_asr": "um our edge routing cluster experienced packet loss anomalies when network interface receive buffers overflowed across fourteen knowed servers wait twenty servers instead basically bursty ingress traffic exceeded driver queue depths buy forcing the kernel to drop fifty thousand network packets p ninety nine packet latency climbed from four milliseconds up through sixteen hundred milliseconds buy causing status five zero four gateway timeouts across forty downstream services incident responders diagnosed the primary trigger inside interface underscore setup dot sh buy analyzing wi re shark packet traces across slash proc network engineers executed buffer calibrat buy expanding rx underscore ring underscore size to four zero nine six buy passing dash dash ring buffer into host network configur parameters while infrastructure administrators right two c p u packet drop monitors",
        "refined_text": "Our edge routing cluster experienced packet loss anomalies when network interface receive buffers overflowed across 20 node servers instead. Bursty ingress traffic exceeded driver queue depths by forcing the kernel to drop 50000 network packets.\n\nP99 packet latency climbed from 4 milliseconds up through 1600 milliseconds by causing status 504 gateway timeouts across 40 downstream services. Incident responders diagnosed the primary trigger inside interface_setup.sh by analyzing Wireshark packet traces across /proc.\n\nNetwork engineers executed buffer calibration by expanding rx_ring_size to 4096 by passing --ring-buffer into host network configuration parameters while infrastructure administrators write 2 CPU packet drop monitors."
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
            print(f"Sample {i+1} (tier: {words} words, layers: {layer_count}): {status}")
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
        out_path = Path("scratch/subagent_batch_155.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
