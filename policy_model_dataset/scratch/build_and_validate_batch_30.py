import json
import sys
import re

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def build_batch():
    batch = [
        # =====================================================================
        # SHORT SAMPLES (Exactly 4: < 25 words, exactly 1 sentence, 0 newlines)
        # =====================================================================
        {
            "raw_asr": "inspect the crash loop back off event on the knowed buy running cube ctl describe pod",
            "refined_text": "Inspect the CrashLoopBackOff event on the node by running kubectl describe pod."
        },
        {
            "raw_asr": "um increase the envoy route timeout to sixty seconds buy updating the cluster communicat timeout",
            "refined_text": "Increase the Envoy route timeout to 60 seconds by updating the cluster communication timeout."
        },
        {
            "raw_asr": "basically terminat the blocking transaction in post gres buy issuing pg terminate backend for pid eight four",
            "refined_text": "Terminate the blocking transaction in Postgres by issuing pg_terminate_backend for PID 84."
        },
        {
            "raw_asr": "rollback the failed deployment to revision three wait revision two buy running cube ctl rollout undo",
            "refined_text": "Rollback the failed deployment to revision 2 by running kubectl rollout undo."
        },

        # =====================================================================
        # MEDIUM SAMPLES (Exactly 6: 25 to 90 words, 1-3 sentences, natural \n\n)
        # =====================================================================
        {
            "raw_asr": "um the payment worker pod was terminat buy the kernel o o m killer due to memory pressure on the knowed check the c group memory current metric to inspect peak heap usage before the failure occurred",
            "refined_text": "The payment worker pod was terminated by the kernel OOM killer due to memory pressure on the node.\n\nCheck the cgroup memory.current metric to inspect peak heap usage before the failure occurred."
        },
        {
            "raw_asr": "dns queries to core dns timed out after five seconds wait thirty seconds during the burst traffic phase um configur the local dns cache on the worker knowed buy enabling node local dns to reduce lookup latency",
            "refined_text": "DNS queries to CoreDNS timed out after 30 seconds during the burst traffic phase.\n\nConfigure the local DNS cache on the worker node by enabling NodeLocal DNS to reduce lookup latency."
        },
        {
            "raw_asr": "basically a network partition isolated three redis master knowed instances from the remaining cluster members the cluster entered a fail state because the partitioned master knowed could not arbitrat quorum during failover",
            "refined_text": "A network partition isolated 3 Redis master node instances from the remaining cluster members.\n\nThe cluster entered a fail state because the partitioned master node could not arbitrate quorum during failover."
        },
        {
            "raw_asr": "envoy reported upstream connection failure errors with status code five zero three during the cascade overload right the ingress route configur to reject excess requests buy lowering the connect timeout to two seconds instead this change isolates degraded backends before worker thread starvation occurs",
            "refined_text": "Envoy reported upstream connection failure errors with status code 503 during the cascade overload. Write the ingress route configuration to reject excess requests by lowering the connect timeout to 2 seconds.\n\nThis change isolates degraded backends before worker thread starvation occurs."
        },
        {
            "raw_asr": "concurrent catalog update queries caused database deadlocks in post gres buy locking rows in reverse order terminat the blocked transaction sessions buy running pg cancel backend for pid forty two and verify active locks in pg locks",
            "refined_text": "Concurrent catalog update queries caused database deadlocks in Postgres by locking rows in reverse order.\n\nTerminate the blocked transaction sessions by running pg_cancel_backend for PID 42 and verify active locks in pg_locks."
        },
        {
            "raw_asr": "um the checkout service heap usage grew continuously buy forty megabytes per hour until the process exhausted memory allocat a profiling session buy capturing a heap dump with jcmd and analyze surviving object graphs",
            "refined_text": "The checkout service heap usage grew continuously by 40 megabytes per hour until the process exhausted memory.\n\nAllocate a profiling session by capturing a heap dump with jcmd and analyze surviving object graphs."
        },

        # =====================================================================
        # LONG SAMPLES (Exactly 10: 90+ words, multi-paragraph \n\n)
        # =====================================================================
        {
            "raw_asr": "okay so the billing service entered a crash loop back off state immediately after the release rollout buy examining the container log stream with cube ctl logs we identified that the application failed during startup initializ because the liveness probe started checking port eight zero eight zero before the application finished loading the cache configur the probe was sending requests after ten seconds but the initialization sequence took thirty seconds causing coober netties to restart the container repeatedly we updated the container probe timing in the deployment manifest set the initial delay seconds to ten wait set initial delay seconds to forty five instead and right a failure threshold of six attempts before the container is marked unhealthy after applying the new manifest buy running cube ctl apply the container completed startup cleanly and the knowed remained in a ready state",
            "refined_text": "The billing service entered a CrashLoopBackOff state immediately after the release rollout. By examining the container log stream with kubectl logs, we identified that the application failed during startup initialization because the liveness probe started checking port 8080 before the application finished loading the cache configuration. The probe was sending requests after 10 seconds, but the initialization sequence took 30 seconds, causing Kubernetes to restart the container repeatedly.\n\nWe updated the container probe timing in the deployment manifest. Set initial delay seconds to 45 and write a failure threshold of 6 attempts before the container is marked unhealthy. After applying the new manifest by running kubectl apply, the container completed startup cleanly and the node remained in a ready state."
        },
        {
            "raw_asr": "basically during the peak lunch traffic spike the edge envoy proxy cluster started returning five zero four gateway timeout errors to mobile clients we investigated the envoy access log lines and observed that upstream response flags indicated connection timeout events when communicat with the inventory backend the cluster configur had a connect timeout of two hundred fifty milliseconds wait five hundred milliseconds instead which was too aggressive during high backend database contention um additionally the circuit breaker max pending requests limit was reached causing envoy to shed load prematurely right the cluster configuration buy setting the connection timeout to two seconds and increase the maximum pending requests limit from one zero two four requests to four zero nine six requests in envoy dot yaml after reloading the proxy process buy triggering the configuration dynamic reload the five zero four errors dropped to zero and upstream latency stabilized across all knowed endpoints",
            "refined_text": "During the peak lunch traffic spike, the edge Envoy proxy cluster started returning 504 gateway timeout errors to mobile clients. We investigated the Envoy access log lines and observed that upstream response flags indicated connection timeout events when communicating with the inventory backend. The cluster configuration had a connect timeout of 500 milliseconds, which was too aggressive during high backend database contention.\n\nAdditionally, the circuit breaker max pending requests limit was reached, causing Envoy to shed load prematurely. Write the cluster configuration by setting the connection timeout to 2 seconds and increase the maximum pending requests limit from 1024 requests to 4096 requests in envoy.yaml.\n\nAfter reloading the proxy process by triggering the configuration dynamic reload, the 504 errors dropped to 0 and upstream latency stabilized across all node endpoints."
        },
        {
            "raw_asr": "okay so during nightly batch processing the primary post gres database experienced repeated deadlock aborts that exhausted the backend connection pool we inspected the post gres lock telemetry using the pg stat activity catalog and identified two background jobs attempting to lock customer account records in opposite sequence job alpha locked the account balance row first while job beta locked the transaction ledger row first creating a cyclic dependency graph um the database deadlock detector automatically aborted the lower priority transaction after one second wait after five hundred milliseconds instead but the application connection pool saturated because failed queries repeatedly retried without backoff we resolved the issue buy modifying the batch query transaction logic to lock rows in ascending order of customer identifier and terminat idle in transaction sessions older than sixty seconds after tuning the connection pool max size to eighty connections and enabling exponential retry jitter database deadlocks ceased completely",
            "refined_text": "During nightly batch processing, the primary Postgres database experienced repeated deadlock aborts that exhausted the backend connection pool. We inspected the Postgres lock telemetry using the pg_stat_activity catalog and identified 2 background jobs attempting to lock customer account records in opposite sequence. Job Alpha locked the account balance row first while Job Beta locked the transaction ledger row first, creating a cyclic dependency graph.\n\nThe database deadlock detector automatically aborted the lower priority transaction after 500 milliseconds, but the application connection pool saturated because failed queries repeatedly retried without backoff.\n\nWe resolved the issue by modifying the batch query transaction logic to lock rows in ascending order of customer identifier and terminate idle in transaction sessions older than 60 seconds. After tuning the connection pool max size to 80 connections and enabling exponential retry jitter, database deadlocks ceased completely."
        },
        {
            "raw_asr": "basically the notification dispatcher service suffered from a gradual memory leak that consumed all container memory over forty eight hours we analyzed the resident set size growth and observed memory climbing buy roughly fifty megabytes each hour until triggering container eviction profiling the running process using pprof revealed that an unbounded event subscription map retained references to disconnected client contexts preventing garbage collection um the retention graph grew because the cleanup callback failed to unregister client channels when the network socket dropped unexpectedly we configur the notification manager buy replacing the global subscription map with an expiring cache keyed buy client session identifier and calibrat a five minute idle eviction threshold we also updated the socket disconnect handler to terminat orphaned channel references immediately upon socket closure after deploying this fix heap consumption stabilized at two hundred fifty six megabytes during steady state operat",
            "refined_text": "The notification dispatcher service suffered from a gradual memory leak that consumed all container memory over 48 hours. We analyzed the resident set size growth and observed memory climbing by roughly 50 megabytes each hour until triggering container eviction. Profiling the running process using pprof revealed that an unbounded event subscription map retained references to disconnected client contexts, preventing garbage collection.\n\nThe retention graph grew because the cleanup callback failed to unregister client channels when the network socket dropped unexpectedly. We configure the notification manager by replacing the global subscription map with an expiring cache keyed by client session identifier and calibrate a 5 minute idle eviction threshold.\n\nWe also updated the socket disconnect handler to terminate orphaned channel references immediately upon socket closure. After deploying this fix, heap consumption stabilized at 256 megabytes during steady state operation."
        },
        {
            "raw_asr": "okay so the report generation pod was terminat with exit code one three seven indicating an o o m killed event buy the linux kernel under c group v two memory management we inspected the pod status using cube ctl describe pod and saw the termination reason was o o m killed because memory usage reached the configured limit of five hundred twelve megabytes wait one zero two four megabytes instead the worker process loaded large customer export archives into memory without streaming which triggered instantaneous allocation spikes that exceeded the c group hard limit um examining the knowed kernel journal with journalctl confirmed that the o o m killer invoked memory cgroup out of memory killing the process to protect host stability we updated the deployment specification buy increasing the memory limit from one zero two four megabytes to two zero four eight megabytes and right the export worker logic to stream records directly to object storage in chunks of sixty four megabytes after testing the updated pod under peak load the container operated stably without further memory evictions",
            "refined_text": "The report generation pod was terminated with exit code 137, indicating an OOMKilled event by the Linux kernel under cgroupv2 memory management. We inspected the pod status using kubectl describe pod and saw the termination reason was OOMKilled because memory usage reached the configured limit of 1024 megabytes. The worker process loaded large customer export archives into memory without streaming, which triggered instantaneous allocation spikes that exceeded the cgroup hard limit.\n\nExamining the node kernel journal with journalctl confirmed that the OOM killer invoked memory cgroup out of memory, killing the process to protect host stability.\n\nWe updated the deployment specification by increasing the memory limit from 1024 megabytes to 2048 megabytes and write the export worker logic to stream records directly to object storage in chunks of 64 megabytes. After testing the updated pod under peak load, the container operated stably without further memory evictions."
        },
        {
            "raw_asr": "basically production microservices experienced intermittent five second dns resolution timeouts when communicat across namespaces we captured network packet traces using tcpdump and wi re shark on the worker knowed and identified dropped udp packets on port five three the root cause was linux connection tracking table race conditions where simultaneous a and a a a a queries buy glibc triggered conntrack drops in the c n i network stack um the five second latency penalty happened because the resolver client waited for the default timeout before retrying over tcp to mitigate the lookup failures we configur node local dns buy deploying a daemonset on each worker knowed and adjusted the resolve configur to route dns lookups to the local loopback cache address at one six nine dot two five four dot twenty dot ten we also updated the deployment pod dns configur buy setting ndots to two wait setting ndots to one instead reducing iterative search domain traversals and stabilizing resolution latency under forty milliseconds",
            "refined_text": "Production microservices experienced intermittent 5 second DNS resolution timeouts when communicating across namespaces. We captured network packet traces using tcpdump and wireshark on the worker node and identified dropped UDP packets on port 53. The root cause was Linux connection tracking table race conditions where simultaneous A and AAAA queries by glibc triggered conntrack drops in the CNI network stack.\n\nThe 5 second latency penalty happened because the resolver client waited for the default timeout before retrying over TCP. To mitigate the lookup failures, we configure NodeLocal DNS by deploying a DaemonSet on each worker node and adjusted the resolve configuration to route DNS lookups to the local loopback cache address at 169.254.20.10.\n\nWe also updated the deployment pod DNS configuration by setting ndots to 1, reducing iterative search domain traversals and stabilizing resolution latency under 40 milliseconds."
        },
        {
            "raw_asr": "okay so an upstream payment provider outage caused a cascade failure that overwhelmed the api gateway and auth services when the third party payment endpoint became unresponsive incoming checkout requests accumulated waiting for the default thirty second timeout this backlog exhausted the api gateway worker pool causing subsequent requests to fail with status code five zero three um microservice clients responded buy immediately retrying failed requests without exponential backoff creating a thundering herd that saturated downstream database connections to halt the cascade failure we deployed emergency rate limiting buy setting the gateway per client request limit to ten requests per second wait fifty requests per second instead and enabled adaptive circuit breaking on the payment route we also configur active request shedding to terminat unauthenticated requests immediately before thread pool allocat after deploying these protective controls the gateway recovered and request queue depth returned to normal",
            "refined_text": "An upstream payment provider outage caused a cascade failure that overwhelmed the API gateway and auth services. When the third-party payment endpoint became unresponsive, incoming checkout requests accumulated waiting for the default 30 second timeout. This backlog exhausted the API gateway worker pool, causing subsequent requests to fail with status code 503.\n\nMicroservice clients responded by immediately retrying failed requests without exponential backoff, creating a thundering herd that saturated downstream database connections. To halt the cascade failure, we deployed emergency rate limiting by setting the gateway per-client request limit to 50 requests per second and enabled adaptive circuit breaking on the payment route.\n\nWe also configure active request shedding to terminate unauthenticated requests immediately before thread pool allocation. After deploying these protective controls, the gateway recovered and request queue depth returned to normal."
        },
        {
            "raw_asr": "basically a transient cross availability zone network partition caused a split brain condition in our six knowed redis cluster zone b lost communicat with zone a where the majority of master instances resided when heartbeats failed for fifteen seconds wait thirty seconds instead the two isolated replicas in zone b attempted failover but could not arbitrat quorum because the majority partition remained unreachable um however clients in zone b continued sending write commands to the isolated master knowed resulting in silent data drift between the partitions we stabilized the cluster buy updating the redis cluster configur setting min replicas to write to one and min replicas max lag to ten seconds in redis dot conf this change ensures that partitioned masters reject writes when replica synchronizat drops below quorum after connectivity between availability zones recovered cluster state cleared and replica synchronizat completed cleanly",
            "refined_text": "A transient cross-availability-zone network partition caused a split-brain condition in our 6 node Redis cluster. Zone B lost communication with Zone A, where the majority of master instances resided. When heartbeats failed for 30 seconds, the 2 isolated replicas in Zone B attempted failover but could not arbitrate quorum because the majority partition remained unreachable.\n\nHowever, clients in Zone B continued sending write commands to the isolated master node, resulting in silent data drift between the partitions. We stabilized the cluster by updating the Redis cluster configuration, setting min-replicas-to-write to 1 and min-replicas-max-lag to 10 seconds in redis.conf.\n\nThis change ensures that partitioned masters reject writes when replica synchronization drops below quorum. After connectivity between availability zones recovered, cluster state cleared and replica synchronization completed cleanly."
        },
        {
            "raw_asr": "okay so our canary release of the order service triggered a severe production regression when the new binary attempted to write records using a non backward compatible database schema we noticed error rates spiking on the checkout route within two minutes of shifting ten percent wait twenty percent of traffic to the canary deployment buy inspecting application logs with cube ctl logs we saw database migration exceptions indicating missing column definitions on legacy records the on call team initiated an immediate rollback procedure buy executing cube ctl rollout undo deployment order service to revert the running pods to revision twelve wait revision eleven instead um simultaneously the database administrator executed the schema rollback migration script to restore the previous table constraints once the rollback completed cube ctl rollout status verified all replicas running revision eleven successfully and end to end transaction processing resumed without data loss",
            "refined_text": "Our canary release of the order service triggered a severe production regression when the new binary attempted to write records using a non-backward-compatible database schema. We noticed error rates spiking on the checkout route within 2 minutes of shifting 20 percent of traffic to the canary deployment. By inspecting application logs with kubectl logs, we saw database migration exceptions indicating missing column definitions on legacy records.\n\nThe on-call team initiated an immediate rollback procedure by executing kubectl rollout undo deployment order service to revert the running pods to revision 11.\n\nSimultaneously, the database administrator executed the schema rollback migration script to restore the previous table constraints. Once the rollback completed, kubectl rollout status verified all replicas running revision 11 successfully, and end-to-end transaction processing resumed without data loss."
        },
        {
            "raw_asr": "basically worker knowed ten zero two fifteen entered disk pressure status causing cube let to initiate aggressive pod evictions across multiple namespaces we investigated the knowed storage utilization using df and identified that container image layers filled the image filesystem to ninety percent wait ninety five percent capacity instead the cube let eviction threshold was configur at eighty five percent triggering automatic pod eviction of lower priority batch workloads um the sudden eviction storm forced thirty batch pods into terminat state simultaneously which placed heavy scheduling burden on the control plane we resolved the disk pressure buy running crictl rmi prune to purge unused dangling container images and adjusted the cube let garbage collection thresholds buy setting image minimum garbage collection percent to seventy and image maximum garbage collection percent to eighty in kubelet dot conf after garbage collection freed thirty gigabytes of disk space the knowed returned to ready state and scheduled workloads resumed normal operat",
            "refined_text": "Worker node 10.0.2.15 entered disk pressure status, causing kubelet to initiate aggressive pod evictions across multiple namespaces. We investigated the node storage utilization using df and identified that container image layers filled the image filesystem to 95 percent capacity. The kubelet eviction threshold was configured at 85 percent, triggering automatic pod eviction of lower priority batch workloads.\n\nThe sudden eviction storm forced 30 batch pods into terminate state simultaneously, which placed heavy scheduling burden on the control plane. We resolved the disk pressure by running crictl rmi prune to purge unused dangling container images and adjusted the kubelet garbage collection thresholds by setting image minimum garbage collection percent to 70 and image maximum garbage collection percent to 80 in kubelet.conf.\n\nAfter garbage collection freed 30 gigabytes of disk space, the node returned to ready state and scheduled workloads resumed normal operation."
        }
    ]
    return batch

def main():
    batch = build_batch()
    output_path = "scratch/subagent_batch_30.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(batch)} samples to {output_path}")

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    all_pairs_valid = True

    print("\n" + "="*70)
    print("INDIVIDUAL SAMPLE VALIDATION (validate_pair & clean_sample)")
    print("="*70)

    for i, s in enumerate(batch, 1):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(raw, ref)

        ref_words = len(ref.split())
        raw_words = len(raw.split())
        ratio = ref_words / max(1, raw_words)

        if ref_words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
        elif ref_words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
        else:
            tier = "LONG"
            tier_counts["long"] += 1

        passed = v_ok and (c_res is not None)
        if not passed:
            all_pairs_valid = False
            print(f"Sample {i:02d} [{tier:6s}]: FAIL | val={v_reason} | clean={c_reason}")
        else:
            print(f"Sample {i:02d} [{tier:6s}]: PASS | words={ref_words:3d} (raw={raw_words:3d}, ratio={ratio:.2f})")

    print("\n" + "="*70)
    print("BATCH-LEVEL VALIDATION (validate_batch)")
    print("="*70)
    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"Status: {'PASS' if b_ok else 'FAIL'}")
    print(f"Message: {b_reason}")
    print(f"Tier counts: {b_tiers}")

    if all_pairs_valid and b_ok:
        print("\nSUCCESS: All 20 samples passed all deterministic validations cleanly!")
    else:
        print("\nFAILURE: One or more validations failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
