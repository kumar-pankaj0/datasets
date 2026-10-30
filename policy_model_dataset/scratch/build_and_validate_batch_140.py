import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

batch_140 = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Content words >= 6-8.
    # =========================================================================

    # Sample 1: Kubernetes live triage - terminating hung worker pods
    {
        "raw_asr": "um terminat hung payment pods through cube ctl buy evicting eighteen unresponsive worker instances",
        "refined_text": "Terminate hung payment pods through kubectl by evicting 18 unresponsive worker instances."
    },

    # Sample 2: Postgres connection pool starvation during live incident
    {
        "raw_asr": "basically allocat twenty connection slots four the post gres replica buy raising pool limits",
        "refined_text": "Allocate 20 connection slots for the Postgres replica by raising pool limits."
    },

    # Sample 3: Investigating network latency drops with Wireshark
    {
        "raw_asr": "uh inspect ingress drop counters buy capturing network packets through wi re shark inside slash tmp",
        "refined_text": "Inspect ingress drop counters by capturing network packets through Wireshark inside /tmp."
    },

    # Sample 4: CPU throttling alert remediation
    {
        "raw_asr": "so um configur container throttling thresholds four the c p u limiter buy adjusting thirty worker limits",
        "refined_text": "Configure container throttling thresholds for the CPU limiter by adjusting 30 worker limits."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 5: Kubelet PLEG event latency and container runtime freeze
    {
        "raw_asr": "um during the live cluster incident our on call team analyzed cube let event latency inside node underscore monitor dot py buy checking node heartbeats wait inspect ten worker hosts instead you know the team resolved container operat stalls through cube ctl buy streaming container logs with dash dash tail four twenty hung pods",
        "refined_text": "During the live cluster incident our on-call team analyzed kubelet event latency inside node_monitor.py by checking node heartbeats, inspecting 10 worker hosts instead.\n\nThe team resolved container operating stalls through kubectl by streaming container logs with --tail for 20 hung pods."
    },

    # Sample 6: Database transaction lock contention during flash sale spike
    {
        "raw_asr": "uh our database site reliability team investigated post gres lock contention inside lock underscore trace dot py buy inspecting active table locks across fifteen worker sessions wait check twenty queries instead you know high c p u utilization caused transaction synchronizat delays buy holding row locks inside slash var slash log",
        "refined_text": "Our database site reliability team investigated Postgres lock contention inside lock_trace.py by inspecting active table locks across 15 worker sessions, checking 20 queries instead.\n\nHigh CPU utilization caused transaction synchronization delays by holding row locks inside /var/log."
    },

    # Sample 7: Microservice RPC cascade and circuit breaker trip RCA
    {
        "raw_asr": "um basically the checkout service triggered cascading r p c timeouts inside rpc underscore client dot py buy exhausting forty connection worker handles no wait raise timeout to five seconds instead the gateway logged error code zero x five zero four fifteen downstream hosts buy restoring inter service communicat channels",
        "refined_text": "Basically the checkout service triggered cascading RPC timeouts inside rpc_client.py by exhausting 40 connection worker handles, raising timeout to 5 seconds instead.\n\nThe gateway logged error code 0x50 for 15 downstream hosts by restoring inter-service communication channels."
    },

    # Sample 8: Ingress network packet drops triage with Wireshark
    {
        "raw_asr": "uh our live triage team tracked gateway packet drops inside packet underscore capture dot py buy analyzing tcp handshakes with wi re shark wait inspect forty packets instead engineers stabilized network transmiss buy running the capture command with dash dash count four twenty incoming socket streams",
        "refined_text": "Our live triage team tracked gateway packet drops inside packet_capture.py by analyzing TCP handshakes with Wireshark, inspecting 40 packets instead.\n\nEngineers stabilized network transmission by running the capture command with --count for 20 incoming socket streams."
    },

    # Sample 9: Redis session cache partition and memory eviction RCA
    {
        "raw_asr": "so basically memory eviction spikes impacted our session cache inside cache underscore cluster dot py buy evicting sixty thousand session keys wait restart eight replica pods instead you know high c p u churn delayed cache memory allocat four thirty worker processes buy clearing expired socket records in slash var slash run",
        "refined_text": "Memory eviction spikes impacted our session cache inside cache_cluster.py by evicting 60000 session keys, restarting 8 replica pods instead.\n\nHigh CPU churn delayed cache memory allocation for 30 worker processes by clearing expired socket records in /var/run."
    },

    # Sample 10: Kafka streaming pipeline consumer group rebalance storm
    {
        "raw_asr": "um i mean the streaming ingest pipeline suffered consumer rebalance loops inside consumer underscore lag dot py buy stalling forty queue partitions wait pause twelve consumer threads instead engineers restored message deduplicat buy checking lag metrics with dash dash group four fifteen r p c client consumers",
        "refined_text": "The streaming ingest pipeline suffered consumer rebalance loops inside consumer_lag.py by stalling 40 queue partitions, pausing 12 consumer threads instead.\n\nEngineers restored message deduplication by checking lag metrics with --group for 15 RPC client consumers."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero checklists.
    # Noise layers >= 4.
    # =========================================================================

    # Sample 11: Production Outage RCA - CoreDNS throttling & CNI IP pool exhaustion
    {
        "raw_asr": "um during the postmortem investigation of our cluster incident our infrastructure team identified c n i ip pool exhaustion as the primary trigger four cascading dns resolution failures inside dns underscore resolver dot py basically twenty worker nodes exhausted local address blocks buy rejecting thirty container scheduling requests wait check twenty pods instead you know elevated c p u load on core dns pods increased p ninety nine query latency beyond five seconds causing inter service communicat timeouts across forty client endpoints the incident commander stabilized internal traffic buy deploying additional resolver replicas through cube ctl with dash dash namespace kube dash system buy applying twenty connection pool limits while platform engineers cleared stale socket records in slash var slash log platform engineers allocat sixteen secondary subnets four resolving network bottlenecks",
        "refined_text": "During the postmortem investigation of our cluster incident our infrastructure team identified CNI IP pool exhaustion as the primary trigger for cascading DNS resolution failures inside dns_resolver.py, with 20 worker nodes exhausting local address blocks by rejecting 30 container scheduling requests, checking 20 pods instead. Elevated CPU load on CoreDNS pods increased P99 query latency beyond 5 seconds, causing inter-service communication timeouts across 40 client endpoints.\n\nThe incident commander stabilized internal traffic by deploying additional resolver replicas through kubectl with --namespace kube-system, applying 20 connection pool limits while platform engineers cleared stale socket records in /var/log. Platform engineers allocate 16 secondary subnets for resolving network bottlenecks."
    },

    # Sample 12: Database Postgres Write-Ahead Log (WAL) disk saturation RCA
    {
        "raw_asr": "uh our database incident response team diagnosed write ahead log disk saturation inside wal underscore monitor dot py buy tracking uncommitted storage transactions across five primary database volumes basically twenty write sessions filled disk blocks buy stalling archive processes wait check twelve replica nodes instead you know severe c p u throttling delayed post gres replica synchronizat buy blocking twenty streaming replication channels four thirty minutes on call engineers mitigated database backpressure buy archiving stale wal segments inside slash var slash log buy executing the maintenance script with dash dash status four forty active tables platform teams terminat eight idle analytics connections while database administrators right storage checkpoints four stabilizing write throughput across the primary database node",
        "refined_text": "Our database incident response team diagnosed write-ahead log disk saturation inside wal_monitor.py by tracking uncommitted storage transactions across 5 primary database volumes, with 20 write sessions filling disk blocks by stalling archive processes, checking 12 replica nodes instead. Severe CPU throttling delayed Postgres replica synchronization by blocking 20 streaming replication channels for 30 minutes.\n\nOn-call engineers mitigated database backpressure by archiving stale WAL segments inside /var/log, executing the maintenance script with --status for 40 active tables. Platform teams terminate 8 idle analytics connections while database administrators write storage checkpoints for stabilizing write throughput across the primary database node."
    },

    # Sample 13: Auth gateway thread pool exhaustion cascading failure RCA
    {
        "raw_asr": "um during the war room troubleshooting session our platform squad discovered that auth gateway thread pool exhaustion was the underlying defect triggering cascading failures inside thread underscore pool dot py basically the service rejected four thousand requests buy returning status error code zero x four zero four fifteen backend microservices wait expand pool size to sixty workers instead you know excessive c p u context switching delayed thread allocat across thirty worker threads buy starving incoming r p c requests platform engineers stabilized service throughput buy tuning worker queue capacities with dash dash threads four twenty gateway instances buy restarting unresponsive tasks operational teams restored normal gateway operat four eighty downstream microservices while engineering leads tracked p ninety five response latency across forty edge clusters",
        "refined_text": "During the war room troubleshooting session our platform squad discovered that auth gateway thread pool exhaustion was the underlying defect triggering cascading failures inside thread_pool.py. The service rejected 4000 requests by returning status error code 0x40 for 15 backend microservices, expanding pool size to 60 workers instead. Excessive CPU context switching delayed thread allocation across 30 worker threads by starving incoming RPC requests.\n\nPlatform engineers stabilized service throughput by tuning worker queue capacities with --threads for 20 gateway instances, restarting unresponsive tasks. Operational teams restored normal gateway operation for 80 downstream microservices while engineering leads tracked P95 response latency across 40 edge clusters."
    },

    # Sample 14: Cross-region VPC peering MTU black hole drop RCA
    {
        "raw_asr": "uh our network operations engineering squad identified path m t u black hole drops as the primary trigger inside mtu underscore audit dot py buy capturing fragmented packets with wi re shark basically thirty cross region gateway streams dropped packets buy enforcing nine thousand byte jumbo frames no wait adjust packet size to fifteen hundred bytes instead you know high c p u packet reassembly stalls delayed network transmiss across twenty router interfaces network engineers mitigated connection timeouts buy saving diagnostic capture files inside slash tmp buy running the probe script with dash dash interface eth zero four sixty tunnel endpoints network specialists calibrat interface buffer parameters buy enforcing path discovery flags across forty border gateways",
        "refined_text": "Our network operations engineering squad identified path MTU black hole drops as the primary trigger inside mtu_audit.py by capturing fragmented packets with Wireshark. Thirty cross-region gateway streams dropped packets by enforcing 9000 byte jumbo frames, adjusting packet size to 1500 bytes instead. High CPU packet reassembly stalls delayed network transmission across 20 router interfaces.\n\nNetwork engineers mitigated connection timeouts by saving diagnostic capture files inside /tmp, running the probe script with --interface eth0 for 60 tunnel endpoints. Network specialists calibrate interface buffer parameters by enforcing path discovery flags across 40 border gateways."
    },

    # Sample 15: Kubernetes pod eviction storm during node memory pressure
    {
        "raw_asr": "um our site reliability operations team reviewed the node eviction cascade inside eviction underscore handler dot py buy analyzing memory pressure thresholds across eight worker instances basically forty pods were terminated buy the kernel memory killer causing pod eviction loops wait drain twelve worker nodes instead you know elevated c p u usage delayed cube let node heartbeats buy marking thirty healthy nodes unready in cluster metrics the operations lead restored cluster capacity buy removing stuck pods through cube ctl with dash dash force four fifty affected deployments platform engineers cleared kernel cgroup dump traces in slash var slash log platform specialists configur higher eviction reservation thresholds four seventy production applications buy preventing cascading memory reclaim stalls across the cluster",
        "refined_text": "Our site reliability operations team reviewed the node eviction cascade inside eviction_handler.py by analyzing memory pressure thresholds across 8 worker instances. Forty pods were terminated by the kernel memory killer, causing pod eviction loops, draining 12 worker nodes instead. Elevated CPU usage delayed kubelet node heartbeats by marking 30 healthy nodes unready in cluster metrics.\n\nThe operations lead restored cluster capacity by removing stuck pods through kubectl with --force for 50 affected deployments. Platform engineers cleared kernel cgroup dump traces in /var/log. Platform specialists configure higher eviction reservation thresholds for 70 production applications by preventing cascading memory reclaim stalls across the cluster."
    },

    # Sample 16: Kafka broker disk IOPS throttling and consumer lag spike postmortem
    {
        "raw_asr": "uh our data streaming platform team conducted an incident postmortem on broker storage saturation inside broker underscore latency dot py buy analyzing storage write queues across four cluster brokers basically broker three exhausted storage burst credits buy delaying fifty thousand write operations wait inspect eight broker partitions instead you know high c p u scheduling delays stalled broker r p c processing buy triggering thirty consumer rebalances across fifty payment topics storage engineers resolved cluster backpressure buy archiving old partition segment logs inside slash var slash log buy executing the rebalance utility with dash dash partition zero four twenty target queues streaming platform engineers recalculat partition replication quotas buy restoring inter cluster communicat channels four eighty downstream consumers",
        "refined_text": "Our data streaming platform team conducted an incident postmortem on broker storage saturation inside broker_latency.py by analyzing storage write queues across 4 cluster brokers. Broker 3 exhausted storage burst credits by delaying 50000 write operations, inspecting 8 broker partitions instead. High CPU scheduling delays stalled broker RPC processing by triggering 30 consumer rebalances across 50 payment topics.\n\nStorage engineers resolved cluster backpressure by archiving old partition segment logs inside /var/log, executing the rebalance utility with --partition 0 for 20 target queues. Streaming platform engineers recalculate partition replication quotas by restoring inter-cluster communication channels for 80 downstream consumers."
    },

    # Sample 17: API Gateway 502 Bad Gateway spike keep-alive mismatch RCA
    {
        "raw_asr": "um during our live triage call platform engineers tracked gateway five zero two spikes inside gateway underscore proxy dot py buy evaluating upstream keep alive mismatches basically the proxy attempted reuse of closed connection handles buy triggering five hundred dropped requests wait check thirty gateway endpoints instead you know high c p u churn delayed connection pool synchronizat buy stalling active http streams across twenty upstream service containers the infrastructure response team stabilized client traffic buy restarting stale gateway pods through cube ctl with dash dash timeout thirty four forty target deployments platform engineers analyzed proxy error logs inside slash var slash log platform engineers terminat twelve dangling socket connections buy enforcing sixty second idle timeout policies across thirty backend servers",
        "refined_text": "During our live triage call platform engineers tracked gateway 502 spikes inside gateway_proxy.py by evaluating upstream keep-alive mismatches. The proxy attempted reuse of closed connection handles by triggering 500 dropped requests, checking 30 gateway endpoints instead. High CPU churn delayed connection pool synchronization by stalling active HTTP streams across 20 upstream service containers.\n\nThe infrastructure response team stabilized client traffic by restarting stale gateway pods through kubectl with --timeout 30 for 40 target deployments. Platform engineers analyzed proxy error logs inside /var/log. Platform engineers terminate 12 dangling socket connections by enforcing 60 second idle timeout policies across 30 backend servers."
    },

    # Sample 18: Distributed lease expiration and split-brain partition RCA
    {
        "raw_asr": "uh our site reliability team conducted an incident retrospective on distributed lease expiration inside lease underscore coordinator dot py buy reviewing consensus heartbeat drops basically sixty network packet stalls caused false leader step downs buy triggering twenty concurrent election rounds wait inspect ten replica instances instead you know severe c p u scheduling latency delayed node arbitrat buy causing state split brain across fifteen consensus members cluster operators stabilized consensus state buy isolating failing nodes through cube ctl with dash dash leader election four thirty cluster components site reliability engineers saved debug dumps inside slash var slash log database administrators initializ clean cluster election parameters while distributed systems engineers right consistent lease timestamps four maintaining quorum stability across forty worker instances",
        "refined_text": "Our site reliability team conducted an incident retrospective on distributed lease expiration inside lease_coordinator.py by reviewing consensus heartbeat drops. Sixty network packet stalls caused false leader step-downs by triggering 20 concurrent election rounds, inspecting 10 replica instances instead. Severe CPU scheduling latency delayed node arbitration by causing state split-brain across 15 consensus members.\n\nCluster operators stabilized consensus state by isolating failing nodes through kubectl with --leader election for 30 cluster components. Site reliability engineers saved debug dumps inside /var/log. Database administrators initialize clean cluster election parameters while distributed systems engineers write consistent lease timestamps for maintaining quorum stability across 40 worker instances."
    },

    # Sample 19: Search cluster JVM garbage collection pause & ingestion drop RCA
    {
        "raw_asr": "um during the search cluster degradation incident our operations team evaluated garbage collection pause metrics inside gc underscore analyzer dot py buy inspecting jvm heap allocation profiles basically sixty search workers experienced twelve second stop the world pauses buy rejecting fifteen thousand write requests wait check twelve search indices instead you know high c p u churn during mark sweep cycles stalled memory allocat across twenty datanodes buy causing cluster health state transitions infrastructure specialists mitigated node disconnects buy restarting hung data pods through cube ctl with dash dash verbose four thirty production instances site reliability engineers reviewed jvm heap logs inside slash var slash log platform teams restored search cluster operat while database administrators right adjusted garbage collection parameters four thirty index shards",
        "refined_text": "During the search cluster degradation incident our operations team evaluated garbage collection pause metrics inside gc_analyzer.py by inspecting JVM heap allocation profiles. Sixty search workers experienced 12 second stop-the-world pauses by rejecting 15000 write requests, checking 12 search indices instead. High CPU churn during mark-sweep cycles stalled memory allocation across 20 datanodes by causing cluster health state transitions.\n\nInfrastructure specialists mitigated node disconnects by restarting hung data pods through kubectl with --verbose for 30 production instances. Site reliability engineers reviewed JVM heap logs inside /var/log. Platform teams restored search cluster operation while database administrators write adjusted garbage collection parameters for 30 index shards."
    },

    # Sample 20: Asynchronous task queue backpressure & worker starvation RCA
    {
        "raw_asr": "uh our platform reliability team analyzed task queue backpressure inside queue underscore dispatcher dot py buy reviewing background worker processing delays basically slow third party webhook responses stalled twenty five thousand asynchronous queue tasks buy exhausting worker execution pools wait scale worker capacity to forty pods instead you know elevated c p u usage delayed a sink job synchronizat buy creating backpressure across thirty Redis queue partitions incident response engineers stabilized queue latency buy provisioning additional runner instances with dash dash workers eight four fifty background pipelines platform engineers archived hung task execution traces inside slash var slash log platform specialists terminat sixteen stuck worker processes while reliability engineers right tuned task timeout limits four restoring steady job processing rates",
        "refined_text": "Our platform reliability team analyzed task queue backpressure inside queue_dispatcher.py by reviewing background worker processing delays. Slow third-party webhook responses stalled 25000 asynchronous queue tasks by exhausting worker execution pools, scaling worker capacity to 40 pods instead. Elevated CPU usage delayed async job synchronization by creating backpressure across 30 Redis queue partitions.\n\nIncident response engineers stabilized queue latency by provisioning additional runner instances with --workers 8 for 50 background pipelines. Platform engineers archived hung task execution traces inside /var/log. Platform specialists terminate 16 stuck worker processes while reliability engineers write tuned task timeout limits for restoring steady job processing rates."
    }
]

def main():
    print(f"Total samples: {len(batch_140)}")
    assert len(batch_140) == 20, f"Expected exactly 20 samples, got {len(batch_140)}"

    # Leakage check against eval set
    leak_count = 0
    for idx, s in enumerate(batch_140):
        raw = s["raw_asr"].strip().lower()
        ref = s["refined_text"].strip()
        if raw in eval_raws:
            print(f"Sample {idx+1} raw leaked into sft_eval.json!")
            leak_count += 1
        if ref in eval_refs:
            print(f"Sample {idx+1} ref leaked into sft_eval.json!")
            leak_count += 1
    assert leak_count == 0, f"Leakage detected: {leak_count} samples leaked"
    print("Zero eval leakage confirmed.")

    # Validate individual pairs
    cleaner_drops = 0
    validator_drops = 0
    layer_counts = []
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for idx, s in enumerate(batch_140):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        # Cleaner check
        res, clean_status = clean_sample(raw, ref)
        if clean_status != "kept":
            print(f"Sample {idx+1} cleaner failed: {clean_status}")
            cleaner_drops += 1

        # Validator pair check (with min_noise_layers=4)
        v_ok, v_msg = validate_pair(s, min_noise_layers=4)
        if not v_ok:
            print(f"Sample {idx+1} validator failed: {v_msg}")
            validator_drops += 1

        # Tier counting
        w_count = len(ref.split())
        if w_count < 25:
            tier_counts["short"] += 1
        elif w_count < 90:
            tier_counts["medium"] += 1
        else:
            tier_counts["long"] += 1

        nl_count = get_noise_layer_count(raw)
        layer_counts.append(nl_count)
        layers_active = count_active_noise_layers(raw)
        print(f"Sample {idx+1:02d}: words={w_count:3d}, breaks={ref.count(chr(10)*2)}, layers={nl_count} {layers_active}, clean={clean_status}")

    print("\n--- Summary ---")
    print(f"Tier counts: {tier_counts}")
    avg_layers = sum(layer_counts) / len(layer_counts)
    print(f"Average noise layers: {avg_layers:.2f}")
    print(f"Cleaner drops: {cleaner_drops}")
    print(f"Validator drops: {validator_drops}")

    assert cleaner_drops == 0, f"Cleaner drops: {cleaner_drops}"
    assert validator_drops == 0, f"Validator drops: {validator_drops}"
    assert tier_counts["short"] == 4, f"Short tier mismatch: {tier_counts['short']}"
    assert tier_counts["medium"] == 6, f"Medium tier mismatch: {tier_counts['medium']}"
    assert tier_counts["long"] == 10, f"Long tier mismatch: {tier_counts['long']}"
    assert avg_layers >= 4.0, f"Average noise layers too low: {avg_layers}"

    # Batch validator check
    batch_ok, batch_msg, batch_meta = validate_batch(
        batch_140, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    print(f"validate_batch: {batch_ok} - {batch_msg}")
    print(f"batch_meta: {batch_meta}")
    assert batch_ok, f"Batch validation failed: {batch_msg}"

    # Save to scratch/subagent_batch_140.json
    output_path = Path("scratch/subagent_batch_140.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch_140, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully written 20 verified samples to {output_path}")

if __name__ == "__main__":
    main()
