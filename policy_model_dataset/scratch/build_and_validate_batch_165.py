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
# Batch 165 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: Terminating leaking RPC connection sockets
    {
        "raw_asr": "um terminat leaking r p c connection sockets buy purging socket underscore backlog on worker knowed hosts instead",
        "refined_text": "Terminate leaking RPC connection sockets by purging socket_backlog on worker node hosts instead."
    },

    # Sample 2: Calibrating CPU throttling limit thresholds
    {
        "raw_asr": "basically calibrat c p u throttling limit thresholds buy tuning throttle underscore burst on worker knowed hosts instead",
        "refined_text": "Calibrate CPU throttling limit thresholds by tuning throttle_burst on worker node hosts instead."
    },

    # Sample 3: Configuring Postgres replication delay limits
    {
        "raw_asr": "uh configur post gres replication delay limits buy adjusting replica underscore timeout on primary knowed servers instead",
        "refined_text": "Configure Postgres replication delay limits by adjusting replica_timeout on primary node servers instead."
    },

    # Sample 4: Initializing kubelet liveness probe frequencies
    {
        "raw_asr": "um initializ cube let liveness probe frequencies buy updating probe underscore interval on gateway knowed instances instead",
        "refined_text": "Initialize kubelet liveness probe frequencies by updating probe_interval on gateway node instances instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: ClickHouse memory limit exhaustion during analytical query
    {
        "raw_asr": "um our clickhouse analytics cluster suffered query execution timeouts after thirty worker knowed hosts hit memory limits across twenty seconds wait forty seconds instead basically incident responders stabilized query operat buy tuning memory underscore tracker buy passing dash dash max memory into cluster configur manifests while reliability engineers right two c p u query monitors",
        "refined_text": "Our ClickHouse analytics cluster suffered query execution timeouts after 30 worker node hosts hit memory limits across 40 seconds instead.\n\nIncident responders stabilized query operations by tuning memory_tracker by passing --max-memory into cluster configuration manifests while reliability engineers write 2 CPU query monitors."
    },

    # Sample 6: Redis Sentinel failover deadlock during master partition
    {
        "raw_asr": "basically our distributed redis cache encountered write transaction stalls after twelve knowed replicas missed sentinel heartbeats across fifteen seconds wait thirty seconds instead um database administrators restored cache communicat buy adjusting failover underscore timeout buy passing dash dash sentinel into cluster configur parameters while systems engineers right two r p c sentinel probes",
        "refined_text": "Our distributed Redis cache encountered write transaction stalls after 12 node replicas missed sentinel heartbeats across 30 seconds instead.\n\nDatabase administrators restored cache communication by adjusting failover_timeout by passing --sentinel into cluster configuration parameters while systems engineers write 2 RPC sentinel probes."
    },

    # Sample 7: NGINX upstream keepalive buffer starvation under traffic spike
    {
        "raw_asr": "um our web ingress edge dropped client connections when twenty worker knowed instances exhausted socket connections across ten seconds wait twenty seconds instead basically site reliability engineers restored proxy operat buy increasing keepalive underscore timeout buy passing dash dash worker connections into nginx configur manifests while network engineers right two wi re shark traffic analyzers",
        "refined_text": "Our web ingress edge dropped client connections when 20 worker node instances exhausted socket connections across 20 seconds instead.\n\nSite reliability engineers restored proxy operations by increasing keepalive_timeout by passing --worker-connections into NGINX configuration manifests while network engineers write 2 Wireshark traffic analyzers."
    },

    # Sample 8: Consul catalog sync failure and health check flapping
    {
        "raw_asr": "basically our service discovery cluster suffered registration timeouts after sixteen knowed agents dropped raft sync across twenty seconds wait forty seconds instead um platform engineers restored mesh communicat buy adjusting sync underscore retry buy passing dash dash retry join into consul configur parameters while platform operators right two a sink sync probes",
        "refined_text": "Our service discovery cluster suffered registration timeouts after 16 node agents dropped Raft sync across 40 seconds instead.\n\nPlatform engineers restored mesh communication by adjusting sync_retry by passing --retry-join into Consul configuration parameters while platform operators write 2 async sync probes."
    },

    # Sample 9: Kubernetes CNI IPAM pool allocation exhaustion
    {
        "raw_asr": "um our container cluster failed pod scheduling when eighteen worker knowed hosts exhausted subnet ip addresses across thirty seconds wait sixty seconds instead basically cluster operators resolved address allocat buy expanding pod underscore cidr buy passing dash dash allocate node cidrs into cube let configur manifests while network administrators right two c p u latency monitors",
        "refined_text": "Our container cluster failed pod scheduling when 18 worker node hosts exhausted subnet IP addresses across 60 seconds instead.\n\nCluster operators resolved address allocation by expanding pod_cidr by passing --allocate-node-cidrs into kubelet configuration manifests while network administrators write 2 CPU latency monitors."
    },

    # Sample 10: PostgreSQL connection pool starvation under vacuum lock
    {
        "raw_asr": "basically our primary database experienced query latency surges after fourteen knowed workers encountered table lock contention across twenty seconds wait forty seconds instead um database administrators restored table operat buy tuning vacuum underscore cost underscore limit buy passing dash dash autovacuum into post gres configur files while site reliability engineers right two r p c lock probes",
        "refined_text": "Our primary database experienced query latency surges after 14 node workers encountered table lock contention across 40 seconds instead.\n\nDatabase administrators restored table operations by tuning vacuum_cost_limit by passing --autovacuum into Postgres configuration files while site reliability engineers write 2 RPC lock probes."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Sev-1 Incident Postmortem: Cassandra node read repair amplification storm
    {
        "raw_asr": "basically during our peak evening workload our cassandra database cluster suffered severe query execution stalls when background read repairs amplified disk io across sixteen knowed nodes wait twenty nodes instead um table compaction stalls delayed data synchronization buy driving c p u utiliz to ninety two percent across forty database instances p ninety five read latency jumped from eight milliseconds up through three two zero zero milliseconds buy dropping forty five percent of customer r p c queries incident responders isolated the primary trigger inside cassandra underscore cluster dot yaml buy evaluating disk read queues across slash var slash log platform engineers stabilized cluster synchronizat buy adjusting read underscore repair underscore chance buy passing dash dash compaction throughput into daemon configur settings while site reliability engineers right three automated disk latency probes",
        "refined_text": "During our peak evening workload, our Cassandra database cluster suffered severe query execution stalls when background read repairs amplified disk IO across 20 node nodes instead. Table compaction stalls delayed data synchronization by driving CPU utilization to 92 percent across 40 database instances.\n\nP95 read latency jumped from 8 milliseconds up through 3200 milliseconds by dropping 45 percent of customer RPC queries. Incident responders isolated the primary trigger inside cassandra_cluster.yaml by evaluating disk read queues across /var/log.\n\nPlatform engineers stabilized cluster synchronization by adjusting read_repair_chance by passing --compaction-throughput into daemon configuration settings while site reliability engineers write 3 automated disk latency probes."
    },

    # Sample 12: Incident Postmortem: Envoy edge proxy TLS handshake session timeout
    {
        "raw_asr": "um our edge ingress proxy tier dropped incoming user traffic when tls handshake sessions timed out across twelve knowed proxies wait eighteen proxies instead basically worker threads stalled on cryptographic key rotation buy exhausting available connection worker slots proxies returned status five zero three errors across fifteen thousand user requests over twenty minutes p ninety nine handshake latency surged from five milliseconds up through sixteen hundred milliseconds buy triggering widespread alert notifications incident responders diagnosed the underlying defect inside proxy underscore gateway dot yaml buy inspecting wi re shark packet dumps across slash etc platform engineers restored proxy communicat buy running cube ctl rollout restart buy passing dash dash max connections into envoy configur parameters while security engineers right two synthetic tls handshake monitors",
        "refined_text": "Our edge ingress proxy tier dropped incoming user traffic when TLS handshake sessions timed out across 18 node proxies instead. Worker threads stalled on cryptographic key rotation by exhausting available connection worker slots.\n\nProxies returned status 503 errors across 15000 user requests over 20 minutes. P99 handshake latency surged from 5 milliseconds up through 1600 milliseconds by triggering widespread alert notifications.\n\nIncident responders diagnosed the underlying defect inside proxy_gateway.yaml by inspecting Wireshark packet dumps across /etc. Platform engineers restored proxy communication by running kubectl rollout restart by passing --max-connections into Envoy configuration parameters while security engineers write 2 synthetic TLS handshake monitors."
    },

    # Sample 13: Live Incident Troubleshooting: Node.js worker event loop blocking on crypto hashing
    {
        "raw_asr": "basically our authentication microservice encountered high latency spikes when synchronous password hashing blocked event loop threads across eight knowed containers wait fourteen containers instead um synchronous cryptographic hashing halted a sink i o execution buy freezing thirty worker threads across four service instances p ninety nine transaction latency climbed from ten milliseconds up through two five zero zero milliseconds buy triggering status five zero four gateway timeouts on six thousand user logins incident responders diagnosed the primary trigger inside auth underscore worker dot py buy tracking thread contention metrics across slash proc software developers restored loop initializ buy offloading hash operations towards background worker pools buy passing dash dash worker threads into server configur parameters while platform reliability engineers right two r p c loop latency probes",
        "refined_text": "Our authentication microservice encountered high latency spikes when synchronous password hashing blocked event loop threads across 14 node containers instead. Synchronous cryptographic hashing halted asyncio execution by freezing 30 worker threads across 4 service instances.\n\nP99 transaction latency climbed from 10 milliseconds up through 2500 milliseconds by triggering status 504 gateway timeouts on 6000 user logins. Incident responders diagnosed the primary trigger inside auth_worker.py by tracking thread contention metrics across /proc.\n\nSoftware developers restored loop initialization by offloading hash operations towards background worker pools by passing --worker-threads into server configuration parameters while platform reliability engineers write 2 RPC loop latency probes."
    },

    # Sample 14: Sev-1 Outage RCA: Elasticsearch unassigned replica storm after master node network isolation
    {
        "raw_asr": "um our search cluster entered red status when a temporary network partition isolated the master node across ten knowed hosts wait sixteen hosts instead basically cluster state updates stalled while fifty indices entered unassigned states buy driving c p u utiliz to ninety four percent across thirty worker nodes p ninety five search query latency jumped from six milliseconds up through two two zero zero milliseconds buy dropping thirty percent of catalog queries incident responders isolated the underlying defect inside elasticsearch underscore cluster dot yaml buy evaluating shard routing logs across slash var slash log search platform engineers stabilized shard allocat buy executing cluster reroute commands buy passing dash dash cluster master into cluster configur parameters while site reliability engineers right two r p c shard status monitors",
        "refined_text": "Our search cluster entered red status when a temporary network partition isolated the master node across 16 node hosts instead. Cluster state updates stalled while 50 indices entered unassigned states by driving CPU utilization to 94 percent across 30 worker nodes.\n\nP95 search query latency jumped from 6 milliseconds up through 2200 milliseconds by dropping 30 percent of catalog queries. Incident responders isolated the underlying defect inside elasticsearch_cluster.yaml by evaluating shard routing logs across /var/log.\n\nSearch platform engineers stabilized shard allocation by executing cluster reroute commands by passing --cluster-master into cluster configuration parameters while site reliability engineers write 2 RPC shard status monitors."
    },

    # Sample 15: Production Incident RCA: TiKV Raft consensus leader election loop
    {
        "raw_asr": "basically our distributed transactional database suffered write transaction pauses when raft leader heartbeats dropped across eight knowed regions wait twelve regions instead um frequent leader reelections triggered raft consensus deadlock buy driving node c p u utiliz to ninety one percent across twenty database instances p ninety nine transaction commit latency spiked from five milliseconds up through eighteen hundred milliseconds buy causing status five zero three errors across nine thousand customer checkout requests incident responders isolated the primary trigger inside tikv underscore engine dot toml buy reviewing consensus election logs across slash proc database reliability engineers restored consensus synchronizat buy increasing raft underscore election underscore timeout buy passing dash dash sync log into engine configur settings while infrastructure platform engineers right two r p c election probes",
        "refined_text": "Our distributed transactional database suffered write transaction pauses when Raft leader heartbeats dropped across 12 node regions instead. Frequent leader reelections triggered Raft consensus deadlock by driving node CPU utilization to 91 percent across 20 database instances.\n\nP99 transaction commit latency spiked from 5 milliseconds up through 1800 milliseconds by causing status 503 errors across 9000 customer checkout requests. Incident responders isolated the primary trigger inside tikv_engine.toml by reviewing consensus election logs across /proc.\n\nDatabase reliability engineers restored consensus synchronization by increasing raft_election_timeout by passing --sync-log into engine configuration settings while infrastructure platform engineers write 2 RPC election probes."
    },

    # Sample 16: Live Incident Troubleshooting: Linux eBPF socket filter memory allocation failure
    {
        "raw_asr": "um our edge gateway fleet experienced packet loss anomalies when ebpf socket programs failed kernel memory allocation across fourteen knowed gateways wait twenty gateways instead basically incoming connection bursts exceeded locked memory limits buy forcing the kernel to drop forty thousand connection requests p ninety nine connection handshake latency climbed from four milliseconds up through fourteen hundred milliseconds buy generating status five zero four gateway timeouts across thirty downstream microservices incident responders diagnosed the primary trigger inside filter underscore program dot c buy evaluating wi re shark packet traces across slash proc system administrators resolved memory allocat buy expanding max underscore locked underscore memory buy passing dash dash filter program into host network configur parameters while infrastructure engineers right two c p u packet drop monitors",
        "refined_text": "Our edge gateway fleet experienced packet loss anomalies when eBPF socket programs failed kernel memory allocation across 20 node gateways instead. Incoming connection bursts exceeded locked memory limits by forcing the kernel to drop 40000 connection requests.\n\nP99 connection handshake latency climbed from 4 milliseconds up through 1400 milliseconds by generating status 504 gateway timeouts across 30 downstream microservices. Incident responders diagnosed the primary trigger inside filter_program.c by evaluating Wireshark packet traces across /proc.\n\nSystem administrators resolved memory allocation by expanding max_locked_memory by passing --filter-program into host network configuration parameters while infrastructure engineers write 2 CPU packet drop monitors."
    },

    # Sample 17: Incident Postmortem: Pulsar BookKeeper journal disk write latency
    {
        "raw_asr": "basically our real time event streaming cluster suffered message publish delays when journal disk writes encountered io contention across eight knowed bookies wait sixteen bookies instead um synchronous journal flush latency blocked message append operations buy driving broker c p u utiliz to ninety three percent across forty message queues p ninety five publish latency jumped from seven milliseconds up through twenty one hundred milliseconds wait two four zero zero milliseconds instead buy dropping thirty five thousand telemetry events incident responders isolated the primary trigger inside bookkeeper underscore storage dot conf buy analyzing storage error logs across slash var slash log streaming platform engineers restored ledger synchronizat buy adjusting journal underscore sync underscore data buy passing dash dash journal dir into daemon configur parameters while reliability engineers right two r p c publish latency probes",
        "refined_text": "Our real-time event streaming cluster suffered message publish delays when journal disk writes encountered IO contention across 16 node bookies instead. Synchronous journal flush latency blocked message append operations by driving broker CPU utilization to 93 percent across 40 message queues.\n\nP95 publish latency jumped from 7 milliseconds up through 2400 milliseconds instead by dropping 35000 telemetry events. Incident responders isolated the primary trigger inside bookkeeper_storage.conf by analyzing storage error logs across /var/log.\n\nStreaming platform engineers restored ledger synchronization by adjusting journal_sync_data by passing --journal-dir into daemon configuration parameters while reliability engineers write 2 RPC publish latency probes."
    },

    # Sample 18: Live Incident Troubleshooting: Docker containerd shim memory leak
    {
        "raw_asr": "um our worker node compute fleet entered degraded states when orphan container shims accumulated process table entries across ten knowed hosts wait eighteen hosts instead basically leaking worker shims consumed sixty thousand kernel pids buy causing cube let process monitoring checks to timeout across thirty worker pods node controllers marked eighteen hosts as unready buy failing cube ctl workload scheduling with status five zero zero errors across forty containers incident responders diagnosed the underlying defect inside containerd underscore runtime dot toml buy evaluating process table metrics across slash proc systems administrators resolved process terminat buy killing defunct shim processes buy passing dash dash max pids into containerd configur parameters while infrastructure engineers right two automated pid consumption probes",
        "refined_text": "Our worker node compute fleet entered degraded states when orphan container shims accumulated process table entries across 18 node hosts instead. Leaking worker shims consumed 60000 kernel PIDs by causing kubelet process monitoring checks to timeout across 30 worker pods.\n\nNode controllers marked 18 hosts as unready by failing kubectl workload scheduling with status 500 errors across 40 containers. Incident responders diagnosed the underlying defect inside containerd_runtime.toml by evaluating process table metrics across /proc.\n\nSystems administrators resolved process termination by killing defunct shim processes by passing --max-pids into containerd configuration parameters while infrastructure engineers write 2 automated PID consumption probes."
    },

    # Sample 19: Sev-1 Incident RCA: BGP Anycast route withdrawal
    {
        "raw_asr": "basically during network edge maintenance our global anycast routing tier encountered traffic blackholing when bgp route advertisements withdrew prefixes across six knowed edge sites wait ten edge sites instead um misconfigured route filters dropped core transit paths buy driving c p u utiliz to ninety percent across forty border routers p ninety nine transit latency climbed from three milliseconds up through fifteen hundred milliseconds buy generating status five zero three errors across twenty five thousand edge requests incident responders isolated the primary trigger inside bgp underscore router dot conf buy evaluating wi re shark routing packet traces across slash etc network reliability engineers restored path communicat buy reapplying prefix underscore filter buy passing dash dash route map into router configur settings while infrastructure operators right two r p c transit health monitors",
        "refined_text": "During network edge maintenance, our global Anycast routing tier encountered traffic blackholing when BGP route advertisements withdrew prefixes across 10 node edge sites instead. Misconfigured route filters dropped core transit paths by driving CPU utilization to 90 percent across 40 border routers.\n\nP99 transit latency climbed from 3 milliseconds up through 1500 milliseconds by generating status 503 errors across 25000 edge requests. Incident responders isolated the primary trigger inside bgp_router.conf by evaluating Wireshark routing packet traces across /etc.\n\nNetwork reliability engineers restored path communication by reapplying prefix_filter by passing --route-map into router configuration settings while infrastructure operators write 2 RPC transit health monitors."
    },

    # Sample 20: Sev-1 Incident RCA: Envoy gRPC streaming buffer overflow
    {
        "raw_asr": "um our payments authorization tier suffered transaction timeouts when streaming g r p c buffers overflowed across twelve knowed proxies wait eighteen proxies instead basically unacknowledged payment receipts exhausted flow control windows buy freezing thirty worker threads across six gateway instances p ninety five payment authorization latency surged from nine milliseconds up through two six zero zero milliseconds buy triggering status five zero four gateway timeout errors on seven thousand customer checkout transactions incident responders diagnosed the primary trigger inside payment underscore gateway dot yaml buy inspecting proxy error logs across slash var slash log platform engineers stabilized proxy communicat buy increasing initial underscore stream underscore window buy passing dash dash concurrency into envoy configur parameters while site reliability engineers right two a sink buffer queue monitors",
        "refined_text": "Our payments authorization tier suffered transaction timeouts when streaming gRPC buffers overflowed across 18 node proxies instead. Unacknowledged payment receipts exhausted flow control windows by freezing 30 worker threads across 6 gateway instances.\n\nP95 payment authorization latency surged from 9 milliseconds up through 2600 milliseconds by triggering status 504 gateway timeout errors on 7000 customer checkout transactions. Incident responders diagnosed the primary trigger inside payment_gateway.yaml by inspecting proxy error logs across /var/log.\n\nPlatform engineers stabilized proxy communication by increasing initial_stream_window by passing --concurrency into Envoy configuration parameters while site reliability engineers write 2 async buffer queue monitors."
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
        out_path = Path("scratch/subagent_batch_165.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
