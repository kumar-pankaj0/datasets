import json
import re
from pathlib import Path
import importlib.util

# Load validator
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

# Load cleaner
clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

pairs = [
    # Tier 1: Short (< 25 words) - Exactly 4 samples
    # Sample 1: Postgres connection pool drain
    {
        "raw_asr": "um terminat all idle client connections on the primary post gres database cluster",
        "refined_text": "Terminate all idle client connections on the primary Postgres database cluster."
    },
    # Sample 2: Canary rollback after HTTP 503
    {
        "raw_asr": "uh roll back canary deployment forty two buy reverting our ingress gateway configuration",
        "refined_text": "Roll back canary deployment 42 by reverting our ingress gateway configuration."
    },
    # Sample 3: Kafka consumer worker restart and offset reset
    {
        "raw_asr": "restart the failed kaff kah consumer worker buy resetting partition offset five hundred twelve",
        "refined_text": "Restart the failed Kafka consumer worker by resetting partition offset 512."
    },
    # Sample 4: Prometheus latency alert rule silence on staging node
    {
        "raw_asr": "um silence latency alert rules inside pro mee thee us four staging knowed sixty four",
        "refined_text": "Silence latency alert rules inside Prometheus for staging node 64."
    },

    # Tier 2: Medium (25 to 89 words) - Exactly 6 samples
    # Sample 5: Redis sentinel failover and split-brain recovery
    {
        "raw_asr": "during the redis sentinel failover our cluster experienced a split brain state across knowed four and knowed five basically sentinel promoted replica one wait promote replica two instead after quorum loss severed network communicat with the primary node buy reconfiguring sentinel heartbeat timeouts to six seconds our team restored cluster synchronization",
        "refined_text": "During the Redis sentinel failover our cluster experienced a split-brain state across node 4 and node 5. Sentinel promoted replica 2 instead after quorum loss severed network communication with the primary node.\n\nBy reconfiguring sentinel heartbeat timeouts to 6 seconds our team restored cluster synchronization."
    },
    # Sample 6: API gateway worker thread starvation from unindexed Elasticsearch queries
    {
        "raw_asr": "our api gateway reported severe worker thread exhausti during the morning traffic peak because unindexed queries into e lastic search pushed p ninety nine response latency to twelve hundred milliseconds basically the gateway stopped accepting connections wait restart worker pool three instead buy killing stalled request threads our engineers recovered proxy throughput",
        "refined_text": "Our API gateway reported severe worker thread exhaustion during the morning traffic peak because unindexed queries into Elasticsearch pushed P99 response latency to 1200 milliseconds.\n\nRestart worker pool 3 instead by killing stalled request threads, and our engineers recovered proxy throughput."
    },
    # Sample 7: Cascading retry storm on auth service tripping circuit breaker
    {
        "raw_asr": "okay so during the downstream database outage client applications initiated an aggressive retry storm against our auth service returning status five hundred and status five hundred three errors uh the ingress h a proxy load balancer experienced heavy degrad wait trip the circuit breaker on endpoint four instead buy rejecting unauthenticated retries at the edge",
        "refined_text": "During the downstream database outage client applications initiated an aggressive retry storm against our auth service, returning status 500 and status 503 errors.\n\nThe ingress HAProxy load balancer experienced heavy degradation, tripping the circuit breaker on endpoint 4 instead by rejecting unauthenticated retries at the edge."
    },
    # Sample 8: Kubelet OOM killer termination on billing pods
    {
        "raw_asr": "um the cube let on worker knowed seven terminat three billing pods with exit code status one three seven because memory consumption exceeded five hundred twelve megabytes basically the runtime ran out of heap space wait inspect memory limits on worker knowed eight instead buy applying revised resource allocations using cube ctl",
        "refined_text": "The kubelet on worker node 7 terminated 3 billing pods with exit code status 137 because memory consumption exceeded 512 megabytes.\n\nInspect memory limits on worker node 8 instead by applying revised resource allocations using kubectl."
    },
    # Sample 9: DNS resolution flap inside CoreDNS causing upstream timeout cascade
    {
        "raw_asr": "uh core d n s instances experienced request throttling when upstream queries exceeded internal cache limits pushing packet resolution latency above two hundred milliseconds you know the cluster lost name resolution across four internal services wait scale core d n s replicas to six instead buy rolling out revised cache configur parameters",
        "refined_text": "CoreDNS instances experienced request throttling when upstream queries exceeded internal cache limits, pushing packet resolution latency above 200 milliseconds.\n\nThe cluster lost name resolution across 4 internal services, scaling CoreDNS replicas to 6 instead by rolling out revised cache configuration parameters."
    },
    # Sample 10: Ingress proxy buffer saturation returning HTTP 504
    {
        "raw_asr": "um the ingress en jin ex controller dropped incoming payload streams and returned status five zero four gateway timeout because default proxy buffer allocat reached capacity across sixteen client connections basically worker processes blocked on socket writes wait increase client body buffer size on proxy knowed two instead buy adjusting buffer settings",
        "refined_text": "The ingress nginx controller dropped incoming payload streams and returned status 504 gateway timeout because default proxy buffer allocations reached capacity across 16 client connections.\n\nIncrease client body buffer size on proxy node 2 instead by adjusting buffer settings."
    },

    # Tier 3: Long (90+ words) - Exactly 10 samples
    # Sample 11: Global checkout incident post-mortem: Database connection pool saturation
    {
        "raw_asr": "okay so during this incident post mortem our platform team reviewed the global checkout outage that occurred yesterday afternoon the primary trigger was connection pool exhausti on our primary post gres database instance when concurrent transactions exceeded twelve hundred connections basically client checkout requests backed up across forty application pods causing p ninety nine latency to spike above eight hundred milliseconds downstream services began receiving status five hundred and status five hundred three errors which triggered an aggressive retry storm against our checkout service wait inspect pool size inside db config dot yml instead of restarting the database nodes directly our on call engineer intervened buy enabling circuit breakers on the edge gateway which shed thirty percent of incoming traffic and stabilized downstream communication right incident documentation inside post mortem dot yml buy recording the timeline across eight incident responders our action items include lowering client retry budgets to three attempts and configuring connection pooling limits across sixteen backend services",
        "refined_text": "During this incident post-mortem our platform team reviewed the global checkout outage that occurred yesterday afternoon. The primary trigger was connection pool exhaustion on our primary Postgres database instance when concurrent transactions exceeded 1200 connections. Client checkout requests backed up across 40 application pods, causing P99 latency to spike above 800 milliseconds, and downstream services began receiving status 500 and status 503 errors which triggered an aggressive retry storm against our checkout service.\n\nInspect pool size inside db_config.yml instead of restarting the database nodes directly. Our on-call engineer intervened by enabling circuit breakers on the edge gateway, which shed 30 percent of incoming traffic and stabilized downstream communication.\n\nWrite incident documentation inside post_mortem.yml by recording the timeline across 8 incident responders. Our action items include lowering client retry budgets to 3 attempts and configuring connection pooling limits across 16 backend services."
    },
    # Sample 12: Kafka poison pill message causing consumer crash loops
    {
        "raw_asr": "in our post mortem analysis of the billing ingestion failure our pipeline squad investigated consumer lag across twelve billing topics basically an unvalidated payload with missing transaction metadata entered kaff kah topic payments partition sixteen which caused worker processes to throw deserialization exceptions and crash loop repeatedly worker pods on knowed six and knowed seven terminat after exhausting memory across twenty four consumer threads this failure cascade caused topic consumer lag to exceed ten thousand unread messages within thirty minutes wait isolate the malformed payload on dead letter queue four instead buy modifying consumer offset parameters inside worker config dot yml our incident responders recovered pipeline processing buy routing invalid records into dead letter storage after consumer workers initializ fresh offsets our engineers verified message throughput across four ingestion clusters our post mortem preventive steps require schema validation enforcement at the producer boundary and automated alerts when consumer lag exceeds two thousand records",
        "refined_text": "In our post-mortem analysis of the billing ingestion failure our pipeline squad investigated consumer lag across 12 billing topics. An unvalidated payload with missing transaction metadata entered Kafka topic payments partition 16, which caused worker processes to throw deserialization exceptions and crash loop repeatedly. Worker pods on node 6 and node 7 terminated after exhausting memory across 24 consumer threads, and this failure cascade caused topic consumer lag to exceed 10000 unread messages within 30 minutes.\n\nIsolate the malformed payload on dead letter queue 4 instead by modifying consumer offset parameters inside worker_config.yml. Our incident responders recovered pipeline processing by routing invalid records into dead letter storage.\n\nAfter consumer workers initialized fresh offsets our engineers verified message throughput across 4 ingestion clusters. Our post-mortem preventive steps require schema validation enforcement at the producer boundary and automated alerts when consumer lag exceeds 2000 records."
    },
    # Sample 13: Cache stampede and thundering herd after key expiration
    {
        "raw_asr": "okay so reviewing the technical failure analysis for our catalog service outage revealed that a synchronized ttl expiration across four cache keys triggered a severe thundering herd event basically when product metadata keys expired at three hundred seconds over six hundred queries per second bypassed the redis cluster on knowed nine and hit the primary database directly database cpu utilization spiked to ninety eight percent while lock contention degrad query performance across twenty replicas downstream clients observed p ninety five latency climb to fourteen hundred milliseconds and received status five zero four gateway timeouts wait apply probabilistic early expiration inside cache service dot py instead buy modifying cache warming routines our on call team mitigated database lock contention buy injecting jitter into key expirations and pre warming popular product records across eight edge proxy instances our follow up action items include configuring mutual exclusion locks during cache misses and deploying graf ah nah dashboards two monitor cache hit ratios across forty worker threads",
        "refined_text": "Reviewing the technical failure analysis for our catalog service outage revealed that a synchronized TTL expiration across 4 cache keys triggered a severe thundering herd event. When product metadata keys expired at 300 seconds, over 600 queries per second bypassed the Redis cluster on node 9 and hit the primary database directly. Database CPU utilization spiked to 98 percent while lock contention degraded query performance across 20 replicas, and downstream clients observed P95 latency climb to 1400 milliseconds and received status 504 gateway timeouts.\n\nApply probabilistic early expiration inside cache_service.py instead by modifying cache warming routines. Our on-call team mitigated database lock contention by injecting jitter into key expirations and pre-warming popular product records across 8 edge proxy instances.\n\nOur follow-up action items include configuring mutual exclusion locks during cache misses and deploying Grafana dashboards to monitor cache hit ratios across 40 worker threads."
    },
    # Sample 14: Identity provider outage: Expired TLS certificate
    {
        "raw_asr": "in our post mortem debrief regarding the identity service outage our security engineers traced the underlying defect two an expired internal x five zero nine certificate on our service mesh gateway basically the leaf certificate expired after twenty four hours causing mutual t l s handshakes two fail across twelve authentication proxies internal microservices could not communicat with the auth authority which returned status four hundred three forbidden responses across forty thousand client requests our engineers analyzed packet captures using wi re shark and observed certificate validat rejections during t l s negotiation wait renew intermediate certificates on knowed twelve instead buy deploying automated certificate rotation scripts inside cert manager dot yml our incident responders restored authentication buy pushing rotated certificates across sixteen proxy clusters our preventive post mortem actions include deploying alert rules four certificate expiration inside alert config dot yml thirty days in advance and conducting quarterly rotation tests across all production environments",
        "refined_text": "In our post-mortem debrief regarding the identity service outage our security engineers traced the underlying defect to an expired internal X.509 certificate on our service mesh gateway. The leaf certificate expired after 24 hours, causing mutual TLS handshakes to fail across 12 authentication proxies. Internal microservices could not communicate with the auth authority, which returned status 403 forbidden responses across 40000 client requests. Our engineers analyzed packet captures using Wireshark and observed certificate validation rejections during TLS negotiation.\n\nRenew intermediate certificates on node 12 instead by deploying automated certificate rotation scripts inside cert_manager.yml. Our incident responders restored authentication by pushing rotated certificates across 16 proxy clusters.\n\nOur preventive post-mortem actions include deploying alert rules for certificate expiration inside alert_config.yml 30 days in advance and conducting quarterly rotation tests across all production environments."
    },
    # Sample 15: Cloud storage volume IOPS throttling triggering etcd leader flap
    {
        "raw_asr": "okay so during this engineering post mortem our infrastructure squad reviewed the coober netties control plane outage where persistent write latency throttled cloud storage volumes basically the underlying et see dee cluster exceeded its disk quota of three thousand iops causing write timeouts during raft log syncs across five member nodes the et see dee cluster lost quorum and entered an election flap which triggered widespread api server disconnects the controller manager mistakenly assumed worker knowed three and knowed four had failed and terminat over sixty pods across the staging namespace wait adjust leader election timeout in etcd conf dot yml instead buy provisioning provisioned iops storage volumes our on call engineers recovered cluster stability buy restoring et see dee snapshots across three control plane nodes using cube ctl our future corrective measures include provisioning dedicated storage disks with twelve thousand iops and configuring proactive latency alarms when disk sync exceeds ten milliseconds",
        "refined_text": "During this engineering post-mortem our infrastructure squad reviewed the Kubernetes control plane outage where persistent write latency throttled cloud storage volumes. The underlying etcd cluster exceeded its disk quota of 3000 IOPS, causing write timeouts during Raft log syncs across 5 member nodes. The etcd cluster lost quorum and entered an election flap which triggered widespread API server disconnects, and the controller manager mistakenly assumed worker node 3 and node 4 had failed and terminated over 60 pods across the staging namespace.\n\nAdjust leader election timeout in etcd_conf.yml instead by provisioning provisioned IOPS storage volumes. Our on-call engineers recovered cluster stability by restoring etcd snapshots across 3 control plane nodes using kubectl.\n\nOur future corrective measures include provisioning dedicated storage disks with 12000 IOPS and configuring proactive latency alarms when disk sync exceeds 10 milliseconds."
    },
    # Sample 16: Distributed transaction failure: Saga coordinator timeout
    {
        "raw_asr": "in our post mortem discussion regarding the payment settlement incident our team analyzed a distributed saga coordinator failure that created ledger discrepancies basically a transient network partition delayed acknowledgment from downstream banking partners pushing coordination latency past fifteen hundred milliseconds the saga coordinator timed out returning status four zero eight request timeout and aborted the multi phase workflow without executing compensating transactions across six database shards this defect left eighty five transactions in an inconsistent state where customer balances were debited without issuing settlement receipts wait inspect compensating transactions inside saga worker dot py instead buy running manual reconciliation scripts our data team restored balance synchronizat buy executing idempotent ledger adjustments across twelve accounts right audit records inside reconciliation log dot json buy tracking transaction timestamps our post mortem remediation involves implementing two phase saga arbitration with durable state persistence and alerting when uncommitted sagas persist longer than sixty seconds",
        "refined_text": "In our post-mortem discussion regarding the payment settlement incident our team analyzed a distributed saga coordinator failure that created ledger discrepancies. A transient network partition delayed acknowledgment from downstream banking partners, pushing coordination latency past 1500 milliseconds. The saga coordinator timed out returning status 408 request timeout and aborted the multi-phase workflow without executing compensating transactions across 6 database shards, and this defect left 85 transactions in an inconsistent state where customer balances were debited without issuing settlement receipts.\n\nInspect compensating transactions inside saga_worker.py instead by running manual reconciliation scripts. Our data team restored balance synchronization by executing idempotent ledger adjustments across 12 accounts.\n\nWrite audit records inside reconciliation_log.json by tracking transaction timestamps. Our post-mortem remediation involves implementing two-phase saga arbitration with durable state persistence and alerting when uncommitted sagas persist longer than 60 seconds."
    },
    # Sample 17: Edge routing incident: BGP route flap and ingress proxy connection exhaustion
    {
        "raw_asr": "okay so analyzing the incident timeline for our edge network degradation our networking engineers reviewed an upstream bgp root flap during an automated ddos scrubbing failover basically an edge provider withdrew prefix announcements causing traffic across four edge routers two fluctuate wildly between upstream transit providers the rapid oscillation overwhelmed our edge ingress cluster where h a proxy connection tables filled completely returning status five zero two bad gateway errors across twenty thousand requests network telemetry showed packet loss reaching eighteen percent while p ninety nine handshake latency exceeded nine hundred milliseconds wait reroute upstream transit traffic through peering link four instead buy shedding non critical traffic at the perimeter our on call engineers used wi re shark two verifi packet communicat and stabilized external ingress routes our permanent post mortem action items require establishing bgp root flap damping timers inside bgp config dot conf and expanding edge proxy connection pool limits two forty thousand sockets",
        "refined_text": "Analyzing the incident timeline for our edge network degradation our networking engineers reviewed an upstream BGP route flap during an automated DDoS scrubbing failover. An edge provider withdrew prefix announcements, causing traffic across 4 edge routers to fluctuate wildly between upstream transit providers. The rapid oscillation overwhelmed our edge ingress cluster where HAProxy connection tables filled completely, returning status 502 bad gateway errors across 20000 requests. Network telemetry showed packet loss reaching 18 percent while P99 handshake latency exceeded 900 milliseconds.\n\nReroute upstream transit traffic through peering link 4 instead by shedding non-critical traffic at the perimeter. Our on-call engineers used Wireshark to verify packet communication and stabilized external ingress routes.\n\nOur permanent post-mortem action items require establishing BGP route flap damping timers inside bgp_config.conf and expanding edge proxy connection pool limits to 40000 sockets."
    },
    # Sample 18: Log pipeline backpressure saturating local file descriptors
    {
        "raw_asr": "in our post mortem review of the logging cluster incident our infrastructure squad investigated how disk backpressure crashed our telemetry agents basically an unbuffered output plugin blocked on network acknowledgments which caused log buffers two accumulate over thirty gigabytes of uncommitted logs on local ephemeral disks the operating system exhausted available file descriptors after worker processes opened more than ten thousand files across eight worker nodes this file descriptor exhaustion crashed our audit daemons on knowed eleven and knowed twelve leaving microservices unable two flush access records and returning status five hundred errors wait purge uncompressed audit archives inside log worker dot sh instead buy redirecting logs two secondary storage partitions our incident responders cleared local disk space buy restarting the logging daemons across sixteen servers our corrective post mortem deliverables mandate enforcing file descriptor quotas inside daemon config dot yml and enabling disk based ring buffers with automatic rotation",
        "refined_text": "In our post-mortem review of the logging cluster incident our infrastructure squad investigated how disk backpressure crashed our telemetry agents. An unbuffered output plugin blocked on network acknowledgments, which caused log buffers to accumulate over 30 gigabytes of uncommitted logs on local ephemeral disks. The operating system exhausted available file descriptors after worker processes opened more than 10000 files across 8 worker nodes. This file descriptor exhaustion crashed our audit daemons on node 11 and node 12, leaving microservices unable to flush access records and returning status 500 errors.\n\nPurge uncompressed audit archives inside log_worker.sh instead by redirecting logs to secondary storage partitions. Our incident responders cleared local disk space by restarting the logging daemons across 16 servers.\n\nOur corrective post-mortem deliverables mandate enforcing file descriptor quotas inside daemon_config.yml and enabling disk-based ring buffers with automatic rotation."
    },
    # Sample 19: Search cluster JVM heap memory leak and shard timeouts
    {
        "raw_asr": "okay so during this incident post mortem our search squad examined the query timeout spike in our primary e lastic search cluster the underlying failure mode was a memory leak in custom aggregation plugins which saturated j v m heap allocat up two thirty two gigabytes across four data nodes garbage collection threads initiated stop the world pauses lasting over twenty seconds which caused cluster master nodes two declare data knowed five unresponsive twelve shards entered unassigned state while client search queries experienced status five zero four gateway timeouts uh telemetry from pro mee thee us highlighted recurring out of memory events across twelve index partitions wait restart search node four instead buy triggering a rolling restart across data pods our engineering team restored cluster health buy reallocating unassigned shards and purging long running aggregation queries our post mortem action plan includes setting query circuit breaker limits inside elasticsearch dot yml and enforcing memory bounds on nested search requests",
        "refined_text": "During this incident post-mortem our search squad examined the query timeout spike in our primary Elasticsearch cluster. The underlying failure mode was a memory leak in custom aggregation plugins which saturated JVM heap allocation up to 32 gigabytes across 4 data nodes. Garbage collection threads initiated stop-the-world pauses lasting over 20 seconds which caused cluster master nodes to declare data node 5 unresponsive, and 12 shards entered unassigned state while client search queries experienced status 504 gateway timeouts.\n\nTelemetry from Prometheus highlighted recurring out-of-memory events across 12 index partitions. Restart search node 4 instead by triggering a rolling restart across data pods, and our engineering team restored cluster health by reallocating unassigned shards and purging long-running aggregation queries.\n\nOur post-mortem action plan includes setting query circuit breaker limits inside elasticsearch.yml and enforcing memory bounds on nested search requests."
    },
    # Sample 20: Asynchronous worker pool deadlock during transaction rollback
    {
        "raw_asr": "in our incident debrief regarding the asynchronous job processing stall our platform squad identified a database transaction deadlock inside the background worker pool basically when downstream payment verifications failed worker threads attempted two roll back nested transactions while holding row level locks on the account ledger table another concurrent batch job attempted two acquire those same table locks causing sixty worker threads two enter an unrecoverable deadlock state the worker pool stopped consuming messages which resulted in a backlog of over five thousand jobs within forty minutes application health checks failed and returned status five zero zero internal server error across eight database connections wait restart worker process six instead buy issuing terminat signals two deadlocked thread pools our responders cleared the task backlog buy scaling worker replicas across twelve instances right deadlock mitigation guidelines inside worker runbook dot md buy documenting query execution order our post mortem remediation establishes strict lock ordering rules inside worker task dot py and enforces statement timeout thresholds across all transaction rollbacks",
        "refined_text": "In our incident debrief regarding the asynchronous job processing stall our platform squad identified a database transaction deadlock inside the background worker pool. When downstream payment verifications failed worker threads attempted to roll back nested transactions while holding row-level locks on the account ledger table, and another concurrent batch job attempted to acquire those same table locks, causing 60 worker threads to enter an unrecoverable deadlock state. The worker pool stopped consuming messages which resulted in a backlog of over 5000 jobs within 40 minutes, and application health checks failed and returned status 500 internal server error across 8 database connections.\n\nRestart worker process 6 instead by issuing terminate signals to deadlocked thread pools. Our responders cleared the task backlog by scaling worker replicas across 12 instances.\n\nWrite deadlock mitigation guidelines inside worker_runbook.md by documenting query execution order. Our post-mortem remediation establishes strict lock ordering rules inside worker_task.py and enforces statement timeout thresholds across all transaction rollbacks."
    }
]

print(f"Total samples: {len(pairs)}")
tiers = {"short": 0, "medium": 0, "long": 0}

for idx, p in enumerate(pairs):
    raw = p["raw_asr"]
    ref = p["refined_text"]
    wc = len(ref.split())

    val_ok, val_reason = val_mod.validate_pair(p)
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)

    if not val_ok:
        print(f"FAILED validate_pair sample {idx+1}: {val_reason}")
    if clean_obj is None:
        print(f"FAILED clean_sample sample {idx+1}: {clean_reason}")

    if wc < 25:
        tiers["short"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        if len(sentences) != 1:
            print(f"Short sample {idx+1} sentence count: {len(sentences)}")
        if "\n" in ref:
            print(f"Short sample {idx+1} has newline!")
    elif wc < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        if not (1 <= len(sentences) <= 3):
            print(f"Medium sample {idx+1} sentence count: {len(sentences)}")
        if "\n\n" not in ref:
            print(f"Medium sample {idx+1} missing paragraph break!")
    else:
        tiers["long"] += 1
        if "\n\n" not in ref:
            print(f"Long sample {idx+1} missing paragraph break!")

    print(f"Sample {idx+1:02d}: wc={wc:3d}, val={val_ok}, clean={clean_obj is not None} ({clean_reason})")

batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
print(f"Batch validation: ok={batch_ok}, msg={batch_msg}, tiers={batch_tiers}")
print(f"Computed tiers: {tiers}")

