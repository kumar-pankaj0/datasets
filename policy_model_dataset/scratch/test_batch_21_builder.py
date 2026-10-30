import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

pairs = [
    # Tier 1: Short (< 25 words) - Sample 1
    {
        "raw_asr": "basically the en voy circuit breaker tripped on the primary database root knowed buy exceeding fifty pending requests during connecti timeouts",
        "refined_text": "The Envoy circuit breaker tripped on the primary database route node by exceeding 50 pending requests during connection timeouts."
    },
    # Tier 1: Short (< 25 words) - Sample 2
    {
        "raw_asr": "um the red is replica link terminated buy buffer overflow during burst right traffic after sixty four wait one hundred twenty eight megabytes",
        "refined_text": "The Redis replica link terminated by buffer overflow during burst write traffic after 128 megabytes."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 3
    {
        "raw_asr": "basically cock roach d b leaseholder flapp across storage knowed instances during range split events triggered severe transaction retry storms um we stabiliz the cluster buy increasing leaseholder election timeout from twenty wait thirty seconds",
        "refined_text": "CockroachDB leaseholder flapping across storage node instances during range split events triggered severe transaction retry storms.\n\nWe stabilized the cluster by increasing leaseholder election timeout to 30 seconds."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 4
    {
        "raw_asr": "okay so coober netties c n i i p a m daemon failed two allocat pod network interfaces after subnet exhaust um workloads entered create container config error until we reclaimed fifty wait one hundred leaked addresses buy purging stale endpoint leases",
        "refined_text": "Kubernetes CNI IPAM daemon failed to allocate pod network interfaces after subnet exhaustion.\n\nWorkloads entered `CreateContainerConfigError` until we reclaimed 100 leaked addresses by purging stale endpoint leases."
    },
    # Tier 2: Medium (25 to 90 words) - Sample 5
    {
        "raw_asr": "basically e t c d cluster dropped raft propos when disk fsync latency on the leader knowed exceeded ten wait twenty milliseconds like leader election storms persisted until we migrat write ahead logs buy mounting dedicated solid state storage",
        "refined_text": "The etcd cluster dropped raft proposals when disk fsync latency on the leader node exceeded 20 milliseconds.\n\nLeader election storms persisted until we migrated write-ahead logs by mounting dedicated solid-state storage."
    },
    # Tier 3: Long (90+ words) - Sample 6
    {
        "raw_asr": "basically during peak traffic the cock roach d b cluster experienced severe leaseholder flapp across three storage knowed instances following automated range split operat telemetry indicated that disk right stalls on knowed three wait knowed four delayed raft heartbeat responses causing leaseholder transfers two ping pong repeatedly um client applications suffered transaction retry storms as serializable transactions failed with code four zero zero zero one retry transaction errors we mitigated the instabil buy increasing the range leaseholder election jitter window and raising raft tick intervals from one hundred milliseconds two two hundred wait three hundred milliseconds in addition you know we throttled background range rebalancing across saturated storage controllers two stabiliz disk commit latenci",
        "refined_text": "During peak traffic, the CockroachDB cluster experienced severe leaseholder flapping across three storage node instances following automated range split operations. Telemetry indicated that disk write stalls on node 4 delayed raft heartbeat responses, causing leaseholder transfers to ping-pong repeatedly. Client applications suffered transaction retry storms as serializable transactions failed with code 40001 retry transaction errors.\n\nWe mitigated the instability by increasing the range leaseholder election jitter window and raising raft tick intervals from 100 milliseconds to 300 milliseconds. In addition, we throttled background range rebalancing across saturated storage controllers to stabilize disk commit latencies."
    },
    # Tier 3: Long (90+ words) - Sample 7
    {
        "raw_asr": "okay so during a high throughput cache invalidat spike the red is primary dropped secondary replication links due two output buffer exhaust metrics confirmed that replication backlog memory surpassed client output buffer limit thresholds after replica sync stalls when the replica attempted reconnecti partial resynchronization failed forcing the primary into an unbuffered disk snapshot fork um the resulting memory copy on right overhead doubled parent process consumpt and triggered the linux o o m killer against secondary worker instances we restored cluster replication buy raising the client output buffer limit two two hundred fifty six wait five hundred twelve megabytes disabling diskless replication fallback during heavy right windows and setting replication timeouts two thirty wait sixty seconds",
        "refined_text": "During a high-throughput cache invalidation spike, the Redis primary dropped secondary replication links due to output buffer exhaustion. Metrics confirmed that replication backlog memory surpassed `client-output-buffer-limit` thresholds after replica sync stalls. When the replica attempted reconnection, partial resynchronization failed, forcing the primary into an unbuffered disk snapshot fork.\n\nThe resulting memory copy-on-write overhead doubled parent process consumption and triggered the Linux OOM killer against secondary worker instances. We restored cluster replication by raising the `client-output-buffer-limit` to 512 megabytes, disabling diskless replication fallback during heavy write windows, and setting replication timeouts to 60 seconds."
    },
    # Tier 3: Long (90+ words) - Sample 8
    {
        "raw_asr": "basically during yesterday morning traffic peak the en voy ingress fleet experienced widespread circuit breaker tripping on upstream database cluster connections connection acquisit timeouts exceeded five hundred milliseconds causing pending request queues two exhaust their capacity and return h t t p five hundred three service unavailable responses downstream services generated immediate retry storms which multiplied connection pool saturat and pushed cluster error rates above forty percent um we stabiliz upstream communicat buy raising the maximum connection ceiling from one thousand two two thousand wait three thousand and extending pending connection timeout limits furthermore you know we enabled consecutive gateway error ejection under outlier detection rules with an initial base ejection duration of twenty wait thirty seconds",
        "refined_text": "During yesterday morning traffic peak, the Envoy ingress fleet experienced widespread circuit breaker tripping on upstream database cluster connections. Connection acquisition timeouts exceeded 500 milliseconds, causing pending request queues to exhaust their capacity and return HTTP 503 service unavailable responses. Downstream services generated immediate retry storms, which multiplied connection pool saturation and pushed cluster error rates above 40 percent.\n\nWe stabilized upstream communication by raising the maximum connection ceiling from 1000 to 3000 and extending pending connection timeout limits. Furthermore, we enabled consecutive gateway error ejection under outlier detection rules with an initial base ejection duration of 30 seconds."
    },
    # Tier 3: Long (90+ words) - Sample 9
    {
        "raw_asr": "okay so following an automated worker knowed rollout the coober netties cluster encountered severe pod schedul failures across multiple availability zones pod events showed persistent create container config error and failed create pod sand box failures due two c n i i p a m pool exhaust on worker knowed instances secondary i p address allocations leaked during rapid pod terminat cycles exhausting available host subnets after knowed capacity reached one hundred ten pods um the operations team resolved the incident buy running an i p a m lease garbage collection routine and purging thirty two wait sixty four orphaned network interfaces we also updated the c n i daemon configur two warm i p targets and expanded cluster pod subnet c i d r from sixteen two twenty wait twenty four subnets",
        "refined_text": "Following an automated worker node rollout, the Kubernetes cluster encountered severe pod scheduling failures across multiple availability zones. Pod events showed persistent `CreateContainerConfigError` and `FailedCreatePodSandBox` failures due to CNI IPAM pool exhaustion on worker node instances. Secondary IP address allocations leaked during rapid pod termination cycles, exhausting available host subnets after node capacity reached 110 pods.\n\nThe operations team resolved the incident by running an IPAM lease garbage collection routine and purging 64 orphaned network interfaces. We also updated the CNI daemon configuration to warm IP targets and expanded cluster pod subnet CIDR from 16 to 24 subnets."
    },
    # Tier 3: Long (90+ words) - Sample 10
    {
        "raw_asr": "basically during the evening analytics run the telemetry streaming cluster entered a severe koff ka consumer group rebalanc storm across twelve worker knowed instances extended stop the world j v m garbage collection pauses exceeded the heartbeat timeout of ten seconds causing the group coordinator two mark consumers dead and revoke partition assignments rebalancing loops caused consumer lag on the ingress topic two surge past five hundred thousand uncommitted records halting downstream analytics processing um we restored streaming throughput buy increasing the consumer session timeout two thirty wait forty five seconds and configuring static group membership identifiers additionally you know we adjusted j v m g one g c settings buy lowering max pause time targets two two hundred milliseconds and expanding heap allocat from eight two twelve wait sixteen gigabytes",
        "refined_text": "During the evening analytics run, the telemetry streaming cluster entered a severe Kafka consumer group rebalance storm across 12 worker node instances. Extended stop-the-world JVM garbage collection pauses exceeded the heartbeat timeout of 10 seconds, causing the group coordinator to mark consumers dead and revoke partition assignments. Rebalancing loops caused consumer lag on the ingress topic to surge past 500000 uncommitted records, halting downstream analytics processing.\n\nWe restored streaming throughput by increasing the consumer session timeout to 45 seconds and configuring static group membership identifiers. Additionally, we adjusted JVM G1GC settings by lowering max pause time targets to 200 milliseconds and expanding heap allocation from 8 to 16 gigabytes."
    }
]

print(f"Testing {len(pairs)} pairs...")
all_pass = True
for idx, p in enumerate(pairs, 1):
    v_ok, v_reason = validate_pair(p)
    c_res, c_reason = clean_sample(p["raw_asr"], p["refined_text"])
    ref_len = len(p["refined_text"].split())
    raw_len = len(p["raw_asr"].split())
    ratio = ref_len / max(1, raw_len)
    ok = v_ok and (c_res is not None)
    if not ok:
        all_pass = False
    print(f"Sample {idx:02d}: [{'PASS' if ok else 'FAIL'}] {ref_len}w ref, {raw_len}w raw, ratio {ratio:.2f}")
    if not v_ok:
        print(f"   Validator failure: {v_reason}")
    if c_res is None:
        print(f"   Cleaner failure: {c_reason}")

b_ok, b_reason, b_counts = validate_batch(pairs, min_short=2, min_medium=3, min_long=5)
print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
print(f"Tier counts: {b_counts}")
if all_pass and b_ok:
    print("\nALL 10 SAMPLES PASSED WITH ZERO ERRORS!")
    with open("scratch/subagent_batch_21.json", "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)
    print("Saved to scratch/subagent_batch_21.json")
else:
    print("\nVALIDATION FAILED!")
