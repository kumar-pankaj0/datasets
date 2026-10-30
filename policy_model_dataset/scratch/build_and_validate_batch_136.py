import json
import sys
import os
from pathlib import Path

# Insert current working directory for imports
sys.path.insert(0, os.path.abspath("."))

from code.validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from code.cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e.get("raw_asr", e.get("input", "")).strip().lower() for e in eval_data}
eval_refs = {e.get("refined_text", e.get("output", "")).strip().lower() for e in eval_data}

batch_136 = [
  # =========================================================================
  # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
  # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
  # Content words >= 6-8. Rationale with active gerunds ("by <action>").
  # Zero backticks. No dotted filenames or internal periods.
  # Min 3 noise layers active.
  # =========================================================================

  # Sample 1: Kubelet sync frequency adjustment
  {
    "raw_asr": "um configur the cube let sync frequency buy extending node probe intervals across eight worker knowed instances",
    "refined_text": "Configure the kubelet sync frequency by extending node probe intervals across 8 worker node instances."
  },

  # Sample 2: Flannel overlay MTU allocation
  {
    "raw_asr": "uh allocat fourteen hundred byte packets buy setting dash dash mtu four flannel daemon pods",
    "refined_text": "Allocate 1400 byte packets by setting --mtu for Flannel daemon pods."
  },

  # Sample 3: Kubectl drain node migration
  {
    "raw_asr": "um migrat active workloads buy running cube ctl drain worker knowed dash dash delete emptydir data",
    "refined_text": "Migrate active workloads by running kubectl drain worker node --delete-emptydir-data."
  },

  # Sample 4: Kubelet eviction hard threshold termination
  {
    "raw_asr": "basically terminat memory hog pods buy configuring cube let dash dash eviction hard thresholds towards two gigabytes",
    "refined_text": "Terminate memory hog pods by configuring kubelet --eviction-hard thresholds towards 2 gigabytes."
  },

  # =========================================================================
  # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
  # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
  # Zero dividers. Arabic numerals for cardinal numbers.
  # Min 4 noise layers active.
  # =========================================================================

  # Sample 5: Kube-proxy IPVS table cleanup
  {
    "raw_asr": "basically our kube proxy daemons suffered high latenc after ipvs tables accumulated forty thousand stale connection entries wait sixty thousand stale connection entries instead buy blocking packet routing across sixteen worker knowed hosts um site reliability engineers restored cluster operat buy running cube ctl exec dash dash ipvsadm dash capital c while developers right two validation scripts",
    "refined_text": "Our kube-proxy daemons suffered high latency after IPVS tables accumulated 60000 stale connection entries instead by blocking packet routing across 16 worker node hosts.\n\nSite reliability engineers restored cluster operations by running kubectl exec --ipvsadm -C while developers write 2 validation scripts."
  },

  # Sample 6: Validating admission webhook failure policy
  {
    "raw_asr": "basically our validating admission webhook timed out during heavy deployment rollouts buy blocking pod admissions across ten namespaces wait twenty namespaces instead four twenty minutes uh cluster operators restored deployment scheduling buy updating coober netties webhook configur with dash dash timeout five seconds while engineers right three automated webhook probes",
    "refined_text": "Our validating admission webhook timed out during heavy deployment rollouts by blocking pod admissions across 20 namespaces instead for 20 minutes.\n\nCluster operators restored deployment scheduling by updating Kubernetes webhook configuration with --timeout 5 seconds while engineers write 3 automated webhook probes."
  },

  # Sample 7: CoreDNS query resolver cache allocation
  {
    "raw_asr": "um our core d n s deployment exhausted upstream resolver capacity when microservices initiated thirty thousand lookups per second wait fifty thousand lookups per second instead buy saturating c p u buffers across six worker knowed hosts you know incident responders stabilized resolving latenc buy allocat custom cache blocks inside slash etc coredns dot yaml while platform engineers right four query latency alerts",
    "refined_text": "Our CoreDNS deployment exhausted upstream resolver capacity when microservices initiated 50000 lookups per second instead by saturating CPU buffers across 6 worker node hosts.\n\nIncident responders stabilized resolving latency by allocating custom cache blocks inside /etc/coredns.yaml while platform engineers write 4 query latency alerts."
  },

  # Sample 8: Cilium eBPF connection tracking table overflow
  {
    "raw_asr": "basically cilium e b p f connection tracking tables saturated after high churn grpc traffic exceeded one hundred thousand active flows wait two hundred thousand active flows instead buy causing silent packet drops across twelve worker knowed hosts uh cluster operators resolved the connection drops buy running cube ctl exec dash dash cilium bpf conntrack and terminat idle flows towards two seconds",
    "refined_text": "Cilium eBPF connection tracking tables saturated after high churn gRPC traffic exceeded 200000 active flows instead by causing silent packet drops across 12 worker node hosts.\n\nCluster operators resolved the connection drops by running kubectl exec --cilium-bpf-conntrack and terminating idle flows towards 2 seconds."
  },

  # Sample 9: Calico BGP route reflector session synchronization
  {
    "raw_asr": "um calico border gateway routing sessions flapped repeatedly when route reflector daemons encountered memory leaks across sixteen routers wait twenty four routers instead buy disrupting pod network synchronizat across three coober netties clusters you know network engineers restored stable route propagation buy deploying updated daemon binaries into slash opt calico while developers right two routing health checks four each peer",
    "refined_text": "Calico border gateway routing sessions flapped repeatedly when route reflector daemons encountered memory leaks across 24 routers instead by disrupting pod network synchronization across 3 Kubernetes clusters.\n\nNetwork engineers restored stable route propagation by deploying updated daemon binaries into /opt/calico while developers write 2 routing health checks for each peer."
  },

  # Sample 10: CSI persistent volume attachment force unlock
  {
    "raw_asr": "uh persistent volume attachments deadlocked on six storage knowed hosts after c s i driver pods crashed during workload migrat wait eight storage knowed hosts instead buy freezing twenty database pods basically platform administrators unlocked stuck block attachments buy running cube ctl delete volumeattachment dash dash force while storage engineers right three reconciliation monitors",
    "refined_text": "Persistent volume attachments deadlocked on 8 storage node hosts instead after CSI driver pods crashed during workload migration by freezing 20 database pods.\n\nPlatform administrators unlocked stuck block attachments by running kubectl delete volumeattachment --force while storage engineers write 3 reconciliation monitors."
  },

  # =========================================================================
  # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
  # Multi-paragraph structure separated by \n\n (2 to 3 paragraphs).
  # Natural spoken engineer narration. Zero numbered checklist stereotypes.
  # Min 4 noise layers active.
  # =========================================================================

  # Sample 11: NGINX Ingress controller buffer saturation and worker connection exhaustion
  {
    "raw_asr": "basically during morning traffic surges our n g i n x ingress controller proxies encountered severe buffer saturat across sixteen ingress knowed instances um upstream microservices returned large response payloads which filled default proxy memory buffers buy forcing nginx worker processes to spill temporary buffers onto disk storage under sustained load ingress worker connections saturated at sixteen thousand connections buy dropping twelve thousand requests per second wait eighteen thousand requests per second instead across thirty endpoints proxy latency spiked from twenty milliseconds up through twelve hundred milliseconds buy triggering widespread client connection resets incident responders stabilized edge routing buy updating ingress proxy configur with dash dash proxy buffer size thirty two kilobytes and increasing worker connection limits to thirty two thousand connections through coober netties config maps while platform engineers right four prometheus alerts tracking ingress connection exhaustion",
    "refined_text": "During morning traffic surges our NGINX ingress controller proxies encountered severe buffer saturation across 16 ingress node instances. Upstream microservices returned large response payloads which filled default proxy memory buffers by forcing NGINX worker processes to spill temporary buffers onto disk storage. Under sustained load ingress worker connections saturated at 16000 connections by dropping 18000 requests per second instead across 30 endpoints.\n\nProxy latency spiked from 20 milliseconds up through 1200 milliseconds by triggering widespread client connection resets.\n\nIncident responders stabilized edge routing by updating ingress proxy configuration with --proxy-buffer-size 32 kilobytes and increasing worker connection limits to 32000 connections through Kubernetes config maps while platform engineers write 4 Prometheus alerts tracking ingress connection exhaustion."
  },

  # Sample 12: Etcd raft fsync latency and historical revision compaction backlog
  {
    "raw_asr": "um our production coober netties control plane operat stalled when our three knowed e t c d cluster reached the storage quota ceiling of eight one nine two megabytes buy triggering read only alarms across all master nodes historical revision compact was disabled which caused boltdb backend freelist pages to fragment heavily over forty eight days the master knowed instances experienced severe raft disk fsync latency exceeding one hundred twenty milliseconds buy triggering repeated leader election flappings kube api server instances lost quorum consensus causing cube ctl resource creation commands to fail with internal server errors across fifty worker knowed hosts platform engineers recovered the cluster buy compacting historical revisions past forty thousand generations through e t c d administrative tools incident responders cleared dead space buy executing offline defragmentat across all three cluster members within twenty five minutes wait thirty five minutes instead the maintenance run reduced backend file sizes down towards twelve hundred megabytes while cluster reliability engineers right three automated cron maintenance scripts buy scheduling recurring database compaction every twenty four hours",
    "refined_text": "Our production Kubernetes control plane operations stalled when our 3 node etcd cluster reached the storage quota ceiling of 8192 megabytes by triggering read-only alarms across all master nodes. Historical revision compaction was disabled, which caused boltdb backend freelist pages to fragment heavily over 48 days. The master node instances experienced severe Raft disk fsync latency exceeding 120 milliseconds by triggering repeated leader election flappings.\n\nKube api server instances lost quorum consensus, causing kubectl resource creation commands to fail with internal server errors across 50 worker node hosts.\n\nPlatform engineers recovered the cluster by compacting historical revisions past 40000 generations through etcd administrative tools. Incident responders cleared dead space by executing offline defragmentation across all 3 cluster members within 35 minutes instead. The maintenance run reduced backend file sizes down towards 1200 megabytes while cluster reliability engineers write 3 automated cron maintenance scripts by scheduling recurring database compaction every 24 hours."
  },

  # Sample 13: Pod Topology Spread Constraints causing scheduling pending deadlocks
  {
    "raw_asr": "basically our batch compute cluster experienced scheduling deadlocks when one hundred twenty processing pods remained stuck in pending state across twenty four compute knowed instances um workloads specified strict pod topology configur requiring a max skew of one across three availability zones because worker knowed memory utiliz was unevenly distributed the coober netties scheduler could not find hosts satisfying both spread rules and pod anti affinity policies pending queue evaluation latencies jumped from forty milliseconds up through twelve hundred milliseconds buy freezing batch job execution four forty five minutes wait sixty minutes instead cluster administrators resolved the scheduling block buy relaxing max skew constraints from one up through two in the deployment specification buy allowing pods to distribute across available capacity operators drained two overloaded hosts through cube ctl with dash dash ignore daemon sets buy rebalancing zone capacity while scheduler engineers right three integration tests verifying pod distribution across diverse failure domains",
    "refined_text": "Our batch compute cluster experienced scheduling deadlocks when 120 processing pods remained stuck in pending state across 24 compute node instances. Workloads specified strict pod topology configuration requiring a max skew of 1 across 3 availability zones. Because worker node memory utilization was unevenly distributed, the Kubernetes scheduler could not find hosts satisfying both spread rules and pod anti-affinity policies.\n\nPending queue evaluation latencies jumped from 40 milliseconds up through 1200 milliseconds by freezing batch job execution for 60 minutes instead.\n\nCluster administrators resolved the scheduling block by relaxing max skew constraints from 1 up through 2 in the deployment specification by allowing pods to distribute across available capacity. Operators drained 2 overloaded hosts through kubectl with --ignore-daemonsets by rebalancing zone capacity while scheduler engineers write 3 integration tests verifying pod distribution across diverse failure domains."
  },

  # Sample 14: Service Mesh Envoy proxy mTLS SDS certificate rotation failure
  {
    "raw_asr": "um our service mesh ingress layer experienced severe client connectivity loss after automated m t l s certifi rotat failed across forty eight envoy proxy sidecars basically the secret discovery service timed out when fetching updated x five zero nine credentials during control plane leader failover envoy proxies rejected incoming t c p connections buy returning five hundred three service unavailable responses on twenty thousand customer requests over thirty minutes wait forty five minutes instead distributed tracing dashboards showed client error rates surging from zero percent up through sixty five percent across twelve microservices incident responders diagnosed expired leaf certificates in envoy memory after discovery streams broke during an istio control plane restart operators restored proxy communicat buy restarting the control plane controller pods and triggering manual certificate injection through cube ctl secrets edge traffic recovered within ten minutes of certificate refresh while security engineers right four automated cert expiration probes buy alerting teams fourteen days before credential expiration",
    "refined_text": "Our service mesh ingress layer experienced severe client connectivity loss after automated mTLS certificate rotation failed across 48 Envoy proxy sidecars. The secret discovery service timed out when fetching updated X.509 credentials during control plane leader failover. Envoy proxies rejected incoming TCP connections by returning 503 Service Unavailable responses on 20000 customer requests over 45 minutes instead.\n\nDistributed tracing dashboards showed client error rates surging from 0 percent up through 65 percent across 12 microservices. Incident responders diagnosed expired leaf certificates in Envoy memory after discovery streams broke during an Istio control plane restart.\n\nOperators restored proxy communication by restarting the control plane controller pods and triggering manual certificate injection through kubectl secrets. Edge traffic recovered within 10 minutes of certificate refresh while security engineers write 4 automated cert expiration probes by alerting teams 14 days before credential expiration."
  },

  # Sample 15: DaemonSet rolling update deadlock with unschedulable node taints
  {
    "raw_asr": "uh our c n i daemonset rolling update deadlocked across thirty two worker knowed hosts when platform engineers initiated cluster node pool upgrades buy applying maintenance taints across worker pools worker nodes were tainted with knowed dot coober netties dot i o slash unschedulable which blocked replacement c n i daemon pods from scheduling because the daemonset template lacked tolerations four unschedulable taints without active network pods thirty worker knowed instances lost network connectivity buy failing pod health probes across forty microservices platform engineers resolved the rollout stall buy patching the daemonset configur with tolerations four unschedulable knowed taints wait fifty nodes instead of thirty nodes suffered connectivity loss before operators deployed the patch cluster administrators restarted cube let daemons across all affected nodes buy re establishing c n i networking while reliability engineers right three automated admission checks buy validating daemonset configur with dash dash dry run before node upgrades",
    "refined_text": "Our CNI DaemonSet rolling update deadlocked across 32 worker node hosts when platform engineers initiated cluster node pool upgrades by applying maintenance taints across worker pools. Worker nodes were tainted with node.kubernetes.io/unschedulable which blocked replacement CNI daemon pods from scheduling because the DaemonSet template lacked tolerations for unschedulable taints.\n\nWithout active network pods 50 nodes instead of 30 nodes suffered connectivity loss before operators deployed the patch by failing pod health probes across 40 microservices.\n\nPlatform engineers resolved the rollout stall by patching the DaemonSet configuration with tolerations for unschedulable node taints. Cluster administrators restarted kubelet daemons across all affected nodes by re-establishing CNI networking while reliability engineers write 3 automated admission checks by validating DaemonSet configuration with --dry-run before node upgrades."
  },

  # Sample 16: Kube-scheduler priority and preemption starvation
  {
    "raw_asr": "basically our production cluster experienced severe workload starvation when an unthrottled batch analytics pipeline submitted five hundred high priority pods configured with priority class one million across eighteen compute knowed instances um the coober netties scheduler preemption engine repeatedly evicted lower priority customer facing services buy generating two hundred fifty eviction events per minute critical web microservices entered crash loop backoff states when evicted pods exhausted node memory limits buy triggering cascading restarts across thirty namespaces platform administrators stabilized cluster scheduling buy applying resource quotas on batch priority classes and reducing batch pod priority towards zero wait one hundred instead cluster operators terminat rogue batch jobs through cube ctl with dash dash cascade orphan buy freeing compute resources while scheduling engineers right three admission webhooks buy restricting priority class assignments to authorized system namespaces",
    "refined_text": "Our production cluster experienced severe workload starvation when an unthrottled batch analytics pipeline submitted 500 high-priority pods configured with PriorityClass 1000000 across 18 compute node instances. The Kubernetes scheduler preemption engine repeatedly evicted lower-priority customer-facing services by generating 250 eviction events per minute. Critical web microservices entered CrashLoopBackOff states when evicted pods exhausted node memory limits by triggering cascading restarts across 30 namespaces.\n\nPlatform administrators stabilized cluster scheduling by applying resource quotas on batch priority classes and reducing batch pod priority towards 100 instead.\n\nCluster operators terminated rogue batch jobs through kubectl with --cascade orphan by freeing compute resources while scheduling engineers write 3 admission webhooks by restricting PriorityClass assignments to authorized system namespaces."
  },

  # Sample 17: Helm release rollback after failed post-install hook
  {
    "raw_asr": "um our automated deployment pipeline halted when a helm release of our logging operator failed during post install validation across six staging clusters buy blocking subsequent microservice updates the post install validation job timed out after three hundred seconds waiting four custom resource definition open a p i schema initializ buy leaving the helm release in a pending upgrade lock state helm rejected subsequent deployment commands across twelve application teams buy throwing release status conflict errors platform engineers recovered the release state buy running helm rollback logging operator zero dash dash cleanup on fail wait rollback to revision one instead cluster operators deleted the stalled hook pod through cube ctl buy unlocking cluster state while infrastructure engineers right three automated pipeline checks buy extending hook timeout thresholds towards six hundred seconds",
    "refined_text": "Our automated deployment pipeline halted when a Helm release of our logging operator failed during post-install validation across 6 staging clusters by blocking subsequent microservice updates. The post-install validation job timed out after 300 seconds waiting for Custom Resource Definition OpenAPI schema initialization by leaving the Helm release in a pending-upgrade lock state. Helm rejected subsequent deployment commands across 12 application teams by throwing release status conflict errors.\n\nPlatform engineers recovered the release state by running Helm rollback logging operator 1 instead with --cleanup-on-fail.\n\nCluster operators deleted the stalled hook pod through kubectl by unlocking cluster state while infrastructure engineers write 3 automated pipeline checks by extending hook timeout thresholds towards 600 seconds."
  },

  # Sample 18: Kube-state-metrics memory limit OOMKilled
  {
    "raw_asr": "basically our cluster observability infrastructure failed when kube state metrics was o o m killed after the cluster expanded to one hundred twenty namespaces and four thousand pods across forty worker knowed instances um informer cache memory consumption jumped from five hundred twelve megabytes up through two zero four eight megabytes during full cache synchronizat buy exhausting pod memory limits prometheus scraping jobs failed with five hundred internal server errors buy blinding monitoring dashboards across eighteen engineering squads platform engineers mitigated the metric outage buy doubling kube state metrics memory allocat from two zero four eight megabytes up through four zero nine six megabytes wait six one four four megabytes instead operators configured metric filtering buy passing dash dash metric denylist arguments in deployment specs while monitoring engineers right four alert rules tracking informer cache memory saturation",
    "refined_text": "Our cluster observability infrastructure failed when kube-state-metrics was OOMKilled after the cluster expanded to 120 namespaces and 4000 pods across 40 worker node instances. Informer cache memory consumption jumped from 512 megabytes up through 2048 megabytes during full cache synchronization by exhausting pod memory limits. Prometheus scraping jobs failed with 500 internal server errors by blinding monitoring dashboards across 18 engineering squads.\n\nPlatform engineers mitigated the metric outage by doubling kube-state-metrics memory allocation from 2048 megabytes up through 6144 megabytes instead.\n\nOperators configured metric filtering by passing --metric-denylist arguments in deployment specs while monitoring engineers write 4 alert rules tracking informer cache memory saturation."
  },

  # Sample 19: Kubelet cgroup memory pressure and eviction manager
  {
    "raw_asr": "uh our compute cluster suffered widespread container restarts when fourteen worker knowed hosts entered memory pressure states during an uncoordinated memory burst buy triggering kube let eviction routines across fifty namespaces available node memory dropped below five hundred megabytes buy forcing the kube let eviction manager to terminat eighty best effort pods within four minutes cgroup v two memory controllers reported heavy page cache thrashing buy spiking c p u utilizat to ninety percent across affected nodes platform operators relieved node memory stress buy setting dash dash eviction hard thresholds to one zero two four megabytes and restarting containerd daemons across all fourteen nodes wait sixteen nodes instead of fourteen nodes incident responders adjusted pod quality of service buy converting sixty best effort workloads into burstable workloads with memory limits while system engineers right three automated memory saturation monitors",
    "refined_text": "Our compute cluster suffered widespread container restarts when 14 worker node hosts entered memory pressure states during an uncoordinated memory burst by triggering kubelet eviction routines across 50 namespaces. Available node memory dropped below 500 megabytes by forcing the kubelet eviction manager to terminate 80 best-effort pods within 4 minutes. Cgroup v2 memory controllers reported heavy page cache thrashing by spiking CPU utilization to 90 percent across affected nodes.\n\nPlatform operators relieved node memory stress by setting --eviction-hard thresholds to 1024 megabytes and restarting containerd daemons across 16 nodes instead of 14 nodes.\n\nIncident responders adjusted pod quality of service by converting 60 best-effort workloads into burstable workloads with memory limits while system engineers write 3 automated memory saturation monitors."
  },

  # Sample 20: PodDisruptionBudget blocking node drain during upgrades
  {
    "raw_asr": "basically our automated cluster node pool upgrade stalled across eight worker knowed hosts four ninety minutes when pod disruption budget configur blocked voluntary node drains um the ingress gateway pod disruption budget specified min available three across three replica pods buy preventing cluster autoscaler eviction workers from evicting gateway instances automated node drain calls failed with four two nine too many requests errors buy stalling maintenance workflows across forty microservices platform engineers resolved the eviction deadlock buy temporarily scaling the ingress gateway deployment to five replicas wait six replicas instead buy providing headroom four maintenance evictions cluster administrators executed cube ctl drain on the eight stalled knowed instances with dash dash delete emptydir data buy rebalancing ingress workloads while reliability engineers right four integration policies buy validating that pod disruption budgets allow at least one voluntary eviction during cluster upgrades",
    "refined_text": "Our automated cluster node pool upgrade stalled across 8 worker node hosts for 90 minutes when PodDisruptionBudget configuration blocked voluntary node drains. The ingress gateway PodDisruptionBudget specified min available 3 across 3 replica pods by preventing cluster autoscaler eviction workers from evicting gateway instances. Automated node drain calls failed with 429 Too Many Requests errors by stalling maintenance workflows across 40 microservices.\n\nPlatform engineers resolved the eviction deadlock by temporarily scaling the ingress gateway deployment to 6 replicas instead by providing headroom for maintenance evictions.\n\nCluster administrators executed kubectl drain on the 8 stalled node instances with --delete-emptydir-data by rebalancing ingress workloads while reliability engineers write 4 integration policies by validating that PodDisruptionBudgets allow at least 1 voluntary eviction during cluster upgrades."
  }
]

# Validation
print(f"Total samples: {len(batch_136)}")
assert len(batch_136) == 20, f"Expected 20 samples, got {len(batch_136)}"

# Leakage check
for i, s in enumerate(batch_136, 1):
    raw = s["raw_asr"].strip().lower()
    ref = s["refined_text"].strip().lower()
    if raw in eval_raws:
        raise ValueError(f"Sample {i} raw leaked in eval set!")
    if ref in eval_refs:
        raise ValueError(f"Sample {i} ref leaked in eval set!")
print("Eval set leakage check: PASSED (0 leaks)")

# Pair checks
all_pairs_ok = True
layer_counts = []
for i, s in enumerate(batch_136, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    ok, msg = validate_pair(s, min_noise_layers=4)
    if not ok:
        print(f"Sample {i} FAILED validate_pair: {msg}")
        all_pairs_ok = False
    
    c_res, c_msg = clean_sample(raw, ref)
    if c_msg != "kept":
        print(f"Sample {i} FAILED clean_sample: {c_msg}")
        all_pairs_ok = False

    nl = get_noise_layer_count(raw)
    layer_counts.append(nl)
    layers = [k for k, v in count_active_noise_layers(raw).items() if v]
    words = len(ref.split())
    tier = "Short" if words < 25 else ("Medium" if words < 90 else "Long")
    print(f"Sample {i:02d} [{tier} {words:3d}w]: layers={nl} {layers} - pair_ok={ok}, clean={c_msg}")

# Batch validation
b_ok, b_msg, b_counts = validate_batch(batch_136, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
print(f"\nBatch validation: {b_ok} ({b_msg})")
print(f"Counts & Tiers: {b_counts}")

if all_pairs_ok and b_ok:
    out_path = "scratch/subagent_batch_136.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch_136, f, indent=2, ensure_ascii=False)
    print(f"\nSUCCESSFULLY written verified batch to {out_path}")
else:
    print("\nVALIDATION FAILED - aborting write")
    sys.exit(1)
