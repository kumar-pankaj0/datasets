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
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

# Domain 1: Cloud-Native Kubernetes & Distributed Infrastructure
# Batch 166 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Noise layers >= 3. Rationale with "by <action>".
    # =========================================================================

    # Sample 1: CNI network configuration update via kubectl
    {
        "raw_asr": "um configur the knowed network policy buy passing dash dash timeout with cube ctl instead",
        "refined_text": "Configure the node network policy by passing --timeout with kubectl instead."
    },

    # Sample 2: Evicting unready pods from worker node via kubelet
    {
        "raw_asr": "basically terminat stuck worker pods buy draining knowed traffic inside slash var slash log with cube let instead",
        "refined_text": "Terminate stuck worker pods by draining node traffic inside /var/log with kubelet instead."
    },

    # Sample 3: Allocating host CPU limits in cgroupv2 for Postgres pods
    {
        "raw_asr": "uh allocat host c p u limits buy setting memory underscore max inside c group v two four post gres containers instead",
        "refined_text": "Allocate host CPU limits by setting memory_max inside cgroupv2 for Postgres containers instead."
    },

    # Sample 4: Cluster initialization via kubeadm
    {
        "raw_asr": "so um initializ cluster control planes buy running cube adm inside slash etc slash kubernetes instead",
        "refined_text": "Initialize cluster control planes by running kubeadm inside /etc/kubernetes instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 5: Ingress controller keepalive timeout and buffer tuning
    {
        "raw_asr": "um configur ingress buffer limits inside proxy underscore config dot yaml buy raising connection keepalive timers across twelve wait twenty four worker pods instead you know inspect upstream latency metrics with wi re shark buy capturing raw packet streams right two unit tests validating buffer retention",
        "refined_text": "Configure ingress buffer limits inside proxy_config.yaml by raising connection keepalive timers across 24 worker pods instead.\n\nInspect upstream latency metrics with Wireshark by capturing raw packet streams. Write 2 unit tests validating buffer retention."
    },

    # Sample 6: Cilium eBPF connection tracking table limits calibration
    {
        "raw_asr": "basically calibrat b p f connection tracking table limits inside cni underscore values dot yaml buy scaling hash table allocations across eight wait sixteen worker knowed instances instead uh apply updated network parameters with cube ctl buy passing dash dash timeout right three unit tests confirming map allocation limits",
        "refined_text": "Calibrate BPF connection tracking table limits inside cni_values.yaml by scaling hash table allocations across 16 worker node instances instead.\n\nApply updated network parameters with kubectl by passing --timeout. Write 3 unit tests confirming map allocation limits."
    },

    # Sample 7: etcd defragmentation and snapshot synchronization
    {
        "raw_asr": "um initializ database maintenance routines inside etcd underscore policy dot yaml buy triggering offline defragmentation across four wait six cluster members instead you know synchronizat of storage revisions proceeds buy pruning historical keys across post gres tables right four integration tests verifying snapshot durability",
        "refined_text": "Initialize database maintenance routines inside etcd_policy.yaml by triggering offline defragmentation across 6 cluster members instead.\n\nSynchronization of storage revisions proceeds by pruning historical keys across Postgres tables. Write 4 integration tests verifying snapshot durability."
    },

    # Sample 8: Kubelet runtime synchronization and probe worker recovery
    {
        "raw_asr": "uh operat container runtime synchronization inside kubelet underscore config dot yaml buy adjusting runtime request timeouts across thirty wait sixty seconds instead basically terminat unresponsive probe workers buy restarting daemon processes with cube ctl right three unit tests validating runtime sync recovery",
        "refined_text": "Operate container runtime synchronization inside kubelet_config.yaml by adjusting runtime request timeouts across 60 seconds instead.\n\nTerminate unresponsive probe workers by restarting daemon processes with kubectl. Write 3 unit tests validating runtime sync recovery."
    },

    # Sample 9: Karpenter node consolidation and workload migration
    {
        "raw_asr": "basically migrat unscheduled workload pods inside scheduler underscore policy dot yaml buy tightening consolidation rules across four wait eight worker knowed instances instead you know evict preempted containers buy invoking r p c dispatch handlers right two integration tests confirming graceful pod termination",
        "refined_text": "Migrate unscheduled workload pods inside scheduler_policy.yaml by tightening consolidation rules across 8 worker node instances instead.\n\nEvict preempted containers by invoking RPC dispatch handlers. Write 2 integration tests confirming graceful pod termination."
    },

    # Sample 10: Rook-Ceph distributed storage CRUSH map balancing and scrubbing
    {
        "raw_asr": "um recalculat storage placement group distributions inside storage underscore profile dot yaml buy balancing crush map weights across sixteen wait thirty two disk targets instead so um deduplicat stale object chunks buy triggering background scrub jobs with cube ctl right four verification checks monitoring replica recovery",
        "refined_text": "Recalculate storage placement group distributions inside storage_profile.yaml by balancing CRUSH map weights across 32 disk targets instead.\n\nDeduplicate stale object chunks by triggering background scrub jobs with kubectl. Write 4 verification checks monitoring replica recovery."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 11: CoreDNS scale-out and UDP connection tracking exhaustion
    {
        "raw_asr": "um our cloud platform team investigated recurring dns resolution timeouts inside coredns underscore deployment dot yaml buy analyzing worker knowed socket metrics during traffic surges previously worker pods experienced transient lookup failures across sixty wait ninety service endpoints instead buy exhausting available socket buffers basically systems engineers configur dns cache parameters buy raising cache size from two thousand records up towards five thousand records buy passing dash dash cache into coredns instances uh our operations staff stabilized upstream packet flow buy allocat concurrency limits across eight c p u cores with cube ctl right four integration tests validating dns query throughput under high concurrency buy inspecting resolver latency across staging pods",
        "refined_text": "Our cloud platform team investigated recurring DNS resolution timeouts inside coredns_deployment.yaml by analyzing worker node socket metrics during traffic surges. Previously worker pods experienced transient lookup failures across 90 service endpoints instead by exhausting available socket buffers.\n\nSystems engineers configured DNS cache parameters by raising cache size from 2000 records up towards 5000 records by passing --cache into CoreDNS instances. Our operations staff stabilized upstream packet flow by allocating concurrency limits across 8 CPU cores with kubectl.\n\nWrite 4 integration tests validating DNS query throughput under high concurrency by inspecting resolver latency across staging pods."
    },

    # Sample 12: Kubernetes API server Priority and Fairness (APF) flow control
    {
        "raw_asr": "basically our platform reliability engineers resolved api server throttling inside apf underscore config dot yaml buy adjusting flow schema priority queues across fifty wait seventy admission controllers instead unthrottled list requests saturated api server memory buffers buy exhausting thirty two worker threads across the cluster control plane so um infrastructure operators configur concurrency shares buy allocating sixty execution seats buy passing dash dash priority into api server startup flags uh engineers terminat rogue controller connections buy restarting unresponsive pods with cube ctl and clearing stale watch streams you know the cluster engineers calibrated queue depth thresholds buy tuning queue length bounds inside slash etc slash kubernetes right four unit tests confirming flow control queue isolation under burst traffic",
        "refined_text": "Our platform reliability engineers resolved API server throttling inside apf_config.yaml by adjusting flow schema priority queues across 70 admission controllers instead. Unthrottled list requests saturated API server memory buffers by exhausting 32 worker threads across the cluster control plane.\n\nInfrastructure operators configured concurrency shares by allocating 60 execution seats by passing --priority into API server startup flags. Engineers terminated rogue controller connections by restarting unresponsive pods with kubectl and clearing stale watch streams.\n\nThe cluster engineers calibrated queue depth thresholds by tuning queue length bounds inside /etc/kubernetes. Write 4 unit tests confirming flow control queue isolation under burst traffic."
    },

    # Sample 13: StatefulSet PersistentVolumeClaim attach-detach deadlock remediation
    {
        "raw_asr": "um our distributed storage operations squad addressed volume attachment deadlocks inside stateful underscore volume dot yaml buy unmounting dangling block devices across sixteen wait twenty four storage volumes instead previously crashed worker knowed hosts held volume locks buy blocking pod scheduling across forty minutes so um infrastructure engineers initializ automated force detach routines buy passing dash dash force into volume management tools uh the platform team configur volume timeout parameters inside slash var slash lib buy verifying device detachment with cube ctl you know operators resolved persistent volume errors buy reattaching clean storage volumes towards twelve healthy knowed targets across the storage network right four integration tests verifying volume detachment timeout handling and pod recovery metrics",
        "refined_text": "Our distributed storage operations squad addressed volume attachment deadlocks inside stateful_volume.yaml by unmounting dangling block devices across 24 storage volumes instead. Previously crashed worker node hosts held volume locks by blocking pod scheduling across 40 minutes.\n\nInfrastructure engineers initialized automated force detach routines by passing --force into volume management tools. The platform team configured volume timeout parameters inside /var/lib by verifying device detachment with kubectl.\n\nOperators resolved persistent volume errors by reattaching clean storage volumes towards 12 healthy node targets across the storage network. Write 4 integration tests verifying volume detachment timeout handling and pod recovery metrics."
    },

    # Sample 14: Cert-manager ACME DNS-01 challenge validation and X.509 renewal
    {
        "raw_asr": "basically our security operations team audited certificate renewal failures inside cert underscore issuer dot yaml buy reviewing x five zero nine validation logs across forty wait sixty ingress endpoints instead expired intermediate certificates blocked customer access buy triggering security handshake warnings across seventy service instances so um security engineers configur acme dns challenge credentials inside slash etc slash certs buy passing dash dash renew into cert manager controllers uh the infrastructure squad terminat stale challenge pods buy isolating failed validation orders with cube ctl you know engineers restored active certificates buy rotating cryptographic keys across thirty cluster namespaces while monitoring ingress gateway status right five integration tests confirming automated x five zero nine certificate renewal and tls secret generation",
        "refined_text": "Our security operations team audited certificate renewal failures inside cert_issuer.yaml by reviewing X.509 validation logs across 60 ingress endpoints instead. Expired intermediate certificates blocked customer access by triggering security handshake warnings across 70 service instances.\n\nSecurity engineers configured ACME DNS challenge credentials inside /etc/certs by passing --renew into cert-manager controllers. The infrastructure squad terminated stale challenge pods by isolating failed validation orders with kubectl.\n\nEngineers restored active certificates by rotating cryptographic keys across 30 cluster namespaces while monitoring ingress gateway status. Write 5 integration tests confirming automated X.509 certificate renewal and TLS secret generation."
    },

    # Sample 15: Calico CNI BPF data plane routing and iptables rule explosion
    {
        "raw_asr": "um our cloud networking squad diagnosed cluster routing degradation inside calico underscore values dot yaml buy inspecting kernel packet drops across thirty wait fifty worker knowed hosts instead iptables rule synchronization saturated host c p u cycles buy introducing network latency across eighty microservices so um network architects configur b p f data plane parameters buy allocating sixteen thousand connection entries buy passing dash dash bpf into calico daemons uh the engineering team terminat legacy iptables proxy rules buy updating cgroup routing filters with cube ctl you know engineers restored network throughput buy refreshing pod routing tables across sixty cluster namespaces right four integration tests verifying b p f routing map stability",
        "refined_text": "Our cloud networking squad diagnosed cluster routing degradation inside calico_values.yaml by inspecting kernel packet drops across 50 worker node hosts instead. The iptables rule synchronization saturated host CPU cycles by introducing network latency across 80 microservices.\n\nNetwork architects configured BPF data plane parameters by allocating 16000 connection entries by passing --bpf into Calico daemons. The engineering team terminated legacy iptables proxy rules by updating cgroup routing filters with kubectl.\n\nEngineers restored network throughput by refreshing pod routing tables across 60 cluster namespaces. Write 4 integration tests verifying BPF routing map stability."
    },

    # Sample 16: Container runtime containerd overlay2 storage garbage collection
    {
        "raw_asr": "basically our platform infrastructure squad resolved container launch failures inside containerd underscore config dot toml buy analyzing overlay storage errors across twenty wait thirty five worker knowed instances instead concurrent image pulling operations exhausted filesystem inodes buy triggering disk allocation errors across forty pods so um infrastructure engineers initializ automated image garbage collection buy setting high watermark thresholds towards eighty percent inside slash etc slash containerd uh the operations staff terminat corrupted image snapshot layers buy removing dangling layer directories with cube let you know engineers restored container creation throughput buy pruning unused container images across forty namespaces while monitoring worker knowed storage metrics right five integration tests confirming clean container layer extraction",
        "refined_text": "Our platform infrastructure squad resolved container launch failures inside containerd_config.toml by analyzing overlay storage errors across 35 worker node instances instead. Concurrent image pulling operations exhausted filesystem inodes by triggering disk allocation errors across 40 pods.\n\nInfrastructure engineers initialized automated image garbage collection by setting high watermark thresholds towards 80 percent inside /etc/containerd. The operations staff terminated corrupted image snapshot layers by removing dangling layer directories with kubelet.\n\nEngineers restored container creation throughput by pruning unused container images across 40 namespaces while monitoring worker node storage metrics. Write 5 integration tests confirming clean container layer extraction."
    },

    # Sample 17: Istio service mesh mTLS certificate rotation and sidecar drain timeout
    {
        "raw_asr": "um our service mesh operations team investigated proxy connection resets inside mesh underscore config dot yaml buy reviewing envoy access logs across forty wait sixty proxy sidecars instead out of synchronization mtls certificates rejected service calls buy triggering five zero three connection errors across eighty microservice endpoints so um mesh architects configur sidecar drain timeouts buy extending termination grace periods towards forty five seconds buy passing dash dash drain into proxy daemons uh engineers terminat desynchronized proxy instances buy restarting gateway pods with cube ctl you know the operations team restored secure r p c traffic buy redistributing active certificates across fifty mesh services right four unit tests validating mtls certificate rotation",
        "refined_text": "Our service mesh operations team investigated proxy connection resets inside mesh_config.yaml by reviewing Envoy access logs across 60 proxy sidecars instead. Out of synchronization mTLS certificates rejected service calls by triggering 503 connection errors across 80 microservice endpoints.\n\nMesh architects configured sidecar drain timeouts by extending termination grace periods towards 45 seconds by passing --drain into proxy daemons. Engineers terminated desynchronized proxy instances by restarting gateway pods with kubectl.\n\nThe operations team restored secure RPC traffic by redistributing active certificates across 50 mesh services. Write 4 unit tests validating mTLS certificate rotation."
    },

    # Sample 18: OpenTelemetry collector queue buffer overflow and Prometheus export
    {
        "raw_asr": "basically our observability infrastructure squad investigated telemetry drop spikes inside collector underscore values dot yaml buy analyzing exporter queue depth across twelve wait twenty collector pods instead sudden trace volume bursts saturated memory queues buy dropping eighty thousand spans across thirty minutes so um telemetry architects configur batch processor limits buy increasing queue capacity towards five thousand items buy passing dash dash queue into collector configurations uh the observability engineers terminat hanging export sessions buy restarting buffer workers with cube ctl you know engineers stabilized telemetry transmission buy routing metrics into remote post gres partitions while tracking memory buffers inside slash var slash log right four verification tests measuring queue throughput under sustained ingestion load",
        "refined_text": "Our observability infrastructure squad investigated telemetry drop spikes inside collector_values.yaml by analyzing exporter queue depth across 20 collector pods instead. Sudden trace volume bursts saturated memory queues by dropping 80000 spans across 30 minutes.\n\nTelemetry architects configured batch processor limits by increasing queue capacity towards 5000 items by passing --queue into collector configurations. The observability engineers terminated hanging export sessions by restarting buffer workers with kubectl.\n\nEngineers stabilized telemetry transmission by routing metrics into remote Postgres partitions while tracking memory buffers inside /var/log. Write 4 verification tests measuring queue throughput under sustained ingestion load."
    },

    # Sample 19: Falco eBPF security daemon syscall drop rate and audit buffer tuning
    {
        "raw_asr": "um our security runtime monitoring team investigated event ring buffer drops inside falco underscore rules dot yaml buy reviewing b p f syscall buffer logs across thirty wait forty five worker knowed hosts instead high container churn rates saturated kernel ring buffers buy dropping ten thousand security events across twenty minutes so um security engineers initializ expanded ring buffer sizes buy allocating eight megabytes per c p u core buy passing dash dash buffer into falco daemon flags uh the monitoring engineers terminat stale event dispatcher threads buy resetting audit workers with cube ctl you know operators restored continuous security monitoring buy streaming verified audit events towards central log collectors inside slash var slash log right four integration tests confirming zero syscall event drops under container deployment bursts",
        "refined_text": "Our security runtime monitoring team investigated event ring buffer drops inside falco_rules.yaml by reviewing BPF syscall buffer logs across 45 worker node hosts instead. High container churn rates saturated kernel ring buffers by dropping 10000 security events across 20 minutes.\n\nSecurity engineers initialized expanded ring buffer sizes by allocating 8 megabytes per CPU core by passing --buffer into Falco daemon flags. The monitoring engineers terminated stale event dispatcher threads by resetting audit workers with kubectl.\n\nOperators restored continuous security monitoring by streaming verified audit events towards central log collectors inside /var/log. Write 4 integration tests confirming zero syscall event drops under container deployment bursts."
    },

    # Sample 20: Kube-proxy IPVS mode connection tracking table exhaustion
    {
        "raw_asr": "basically our cluster networking infrastructure squad resolved connection reset storms inside proxy underscore daemon dot yaml buy analyzing netfilter connection tracking tables across sixty wait ninety worker knowed instances instead rapid tcp connection churn exhausted netfilter conntrack entries buy dropping twelve thousand network packets across fifteen minutes so um network architects configur ipvs connection tracking table maximum limits buy setting table capacity towards two hundred thousand entries buy passing dash dash conntrack into proxy daemon parameters uh the operations staff terminat stale connection sockets buy flushing expired ipvs routing tables with cube ctl you know engineers stabilized cluster service routing buy adjusting tcp close wait timeouts inside slash proc slash sys right four unit tests validating ipvs connection state recovery under connection surges",
        "refined_text": "Our cluster networking infrastructure squad resolved connection reset storms inside proxy_daemon.yaml by analyzing Netfilter connection tracking tables across 90 worker node instances instead. Rapid TCP connection churn exhausted Netfilter conntrack entries by dropping 12000 network packets across 15 minutes.\n\nNetwork architects configured IPVS connection tracking table maximum limits by setting table capacity towards 200000 entries by passing --conntrack into proxy daemon parameters. The operations staff terminated stale connection sockets by flushing expired IPVS routing tables with kubectl.\n\nEngineers stabilized cluster service routing by adjusting TCP close wait timeouts inside /proc/sys. Write 4 unit tests validating IPVS connection state recovery under connection surges."
    }
]

print(f"Total candidate samples: {len(batch)}")
assert len(batch) == 20, f"Expected 20 samples, got {len(batch)}"

tiers = {"short": 0, "medium": 0, "long": 0}
layer_counts = []

for idx, pair in enumerate(batch, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx} ref leaked into sft_eval.json!"

    # Word count and tier check
    words = len(ref.split())
    nl = get_noise_layer_count(raw)
    layer_counts.append(nl)

    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx} has newline in short tier!"
        assert nl >= 3, f"Sample {idx} short tier active layers < 3 ({nl})"
        val_ok, val_reason = validate_pair(pair, min_noise_layers=3)
    elif words < 90:
        tiers["medium"] += 1
        assert nl >= 4, f"Sample {idx} medium tier active layers < 4 ({nl})"
        val_ok, val_reason = validate_pair(pair, min_noise_layers=4)
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx} missing paragraph break in long tier!"
        assert nl >= 4, f"Sample {idx} long tier active layers < 4 ({nl})"
        val_ok, val_reason = validate_pair(pair, min_noise_layers=4)

    assert val_ok, f"Sample {idx} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx} clean status: {clean_reason}"

    print(f"Sample {idx:02d} [{words:3d} words | {nl}/6 layers]: PASS (clean: {clean_reason}, validate: OK)")

# Batch validation
batch_ok, batch_reason, batch_stats = validate_batch(
    batch,
    min_short=4,
    min_medium=6,
    min_long=10,
    min_noise_layers=4
)
assert batch_ok, f"Batch validation failed: {batch_reason}"

print("\n--- Summary Verification ---")
print(f"Tier counts: {tiers}")
avg_layers = sum(layer_counts) / len(layer_counts)
print(f"Average noise layers: {avg_layers:.2f}")
print(f"Noise layer distribution: {batch_stats.get('noise_layer_distribution')}")

# Save verified samples to output file
out_path = Path("scratch/subagent_batch_166.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully wrote 20 verified samples to {out_path}")
