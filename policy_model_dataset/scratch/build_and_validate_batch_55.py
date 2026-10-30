import json
import sys
import os

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
    # --- SHORT TIER (4 samples, <25 words, exactly 1 sentence, 0 newlines) ---
    {
        # S1: Redis connection pool exhaustion
        "raw_asr": "uh the redis connection pool exhaust all available client sockets during peak checkout traffic",
        "refined_text": "The Redis connection pool exhausted all available client sockets during peak checkout traffic."
    },
    {
        # S2: Intermediate certificate expiration
        "raw_asr": "basically upstream edge proxies rejected client requests buy dropping expired intermediate certificates",
        "refined_text": "Upstream edge proxies rejected client requests by dropping expired intermediate certificates."
    },
    {
        # S3: Billing consumer group lag
        "raw_asr": "um the billing consumer group accrued lag after database write locks blocked worker threads",
        "refined_text": "The billing consumer group accrued lag after database write locks blocked worker threads."
    },
    {
        # S4: OOM killer termination on node 6
        "raw_asr": "linux out of memory killer terminat the background analytics worker process on knowed six",
        "refined_text": "Linux out of memory killer terminated the background analytics worker process on node 6."
    },

    # --- MEDIUM TIER (6 samples, 25-89 words, 1-3 sentences, natural \n\n breaks) ---
    {
        # M1: PostgreSQL replica replication lag
        "raw_asr": "uh post gres q l read replica lag climbed two forty five seconds during the reporting run an unindexed sequential scan against the ledger entries table locked sixty active database worker connections",
        "refined_text": "PostgreSQL read replica lag climbed to 45 seconds during the reporting run.\n\nAn unindexed sequential scan against the ledger entries table locked 60 active database worker connections."
    },
    {
        # M2: CDN cache stampede
        "raw_asr": "basically an edge c d n cache stampede flooded origin backend clusters with five zero two bad gateway errors after catalog cache keys expir simultaneously three hundred concurrent requests bypassed the edge caching layer and saturat upstream application pools",
        "refined_text": "An edge CDN cache stampede flooded origin backend clusters with 502 Bad Gateway errors after catalog cache keys expired simultaneously.\n\n300 concurrent requests bypassed the edge caching layer and saturated upstream application pools."
    },
    {
        # M3: Kubelet disk pressure and eviction
        "raw_asr": "um worker knowed four entered disk pressure status after container runtime log directories filled ninety gigabytes of host storage cube let evicted twelve batch pods buy terminating processes with exit code one hundred thirty seven",
        "refined_text": "Worker node 4 entered disk pressure status after container runtime log directories filled 90 gigabytes of host storage.\n\nKubelet evicted 12 batch pods by terminating processes with exit code 137."
    },
    {
        # M4: RabbitMQ message queue buildup
        "raw_asr": "basically rabbit m q message queues in the notifications cluster backed up two forty thousand pending tasks after dead letter exchange consumers encountered unhandled json parsing exceptions the broker throttl publisher channels buy enforcing memory alarms",
        "refined_text": "RabbitMQ message queues in the notifications cluster backed up to 40000 pending tasks after dead letter exchange consumers encountered unhandled JSON parsing exceptions.\n\nThe broker throttled publisher channels by enforcing memory alarms."
    },
    {
        # M5: Elasticsearch shard reallocation
        "raw_asr": "uh elasticsearch cluster health degraded two yellow after primary shard five failed on knowed eight wait knowed nine instead the cluster coordinator allocat replicas across remaining nodes buy replaying transaction logs four fifteen minutes",
        "refined_text": "Elasticsearch cluster health degraded to yellow after primary shard 5 failed on node 9 instead.\n\nThe cluster coordinator allocated replicas across remaining nodes by replaying transaction logs for 15 minutes."
    },
    {
        # M6: Envoy proxy circuit breaker
        "raw_asr": "um the envoy proxy sidecar triggered circuit breaking after downstream checkout response latenc exceeded two seconds edge routers returned status five hundred three service unavailable four eighty requests until connection pools reset",
        "refined_text": "The Envoy proxy sidecar triggered circuit breaking after downstream checkout response latency exceeded 2 seconds.\n\nEdge routers returned status 503 Service Unavailable for 80 requests until connection pools reset."
    },

    # --- LONG TIER (10 samples, 90+ words, multi-paragraph \n\n, zero checklist stereotypes) ---
    {
        # L1: Payment Gateway Outage Postmortem
        "raw_asr": "uh at zero nine thirty the checkout microservice experienced an abrupt surge in error rates during the morning sale downstream payment partner endpoints increased p ninety nine response latenc from one hundred milliseconds two four thousand milliseconds which caused local connection pools two exhaust all sixty worker threads basically incoming checkout requests accumulated in edge reverse proxy buffers until five zero four gateway timeout errors reached eight hundred failures per second the incident response squad identified thread starvation inside the payment connector container runtime worker threads were blocked waiting on synchronous socket reads without an explicit read timeout buy zero nine forty five engineers applied a hotfix buy setting socket read timeouts two eight hundred milliseconds and enabling connection pooling circuit breakers the mitigation immediately isolated the stalled partner traffic and dropped error rates back two zero by ten zero zero the postmortem action items require migrating the synchronous payment connector two an a sink non blocking client model and configuring fallback responses four downstream partner degradation",
        "refined_text": "At 0930 the checkout microservice experienced an abrupt surge in error rates during the morning sale. Downstream payment partner endpoints increased P99 response latency from 100 milliseconds to 4000 milliseconds, which caused local connection pools to exhaust all 60 worker threads. Incoming checkout requests accumulated in edge reverse proxy buffers until 504 gateway timeout errors reached 800 failures per second.\n\nThe incident response squad identified thread starvation inside the payment connector container runtime. Worker threads were blocked waiting on synchronous socket reads without an explicit read timeout. By 0945 engineers applied a hotfix by setting socket read timeouts to 800 milliseconds and enabling connection pooling circuit breakers.\n\nThe mitigation immediately isolated the stalled partner traffic and dropped error rates back to zero by 1000. The postmortem action items require migrating the synchronous payment connector to an async non-blocking client model and configuring fallback responses for downstream partner degradation."
    },
    {
        # L2: Distributed Cache Invalidation Storm
        "raw_asr": "basically at fourteen twenty during a rolling deployment of the product catalog service an unverified cache invalidation routine purged all redis session keys rather than the target category namespace downstream post gres primary and replica nodes experienced fifteen thousand cache misses per second which drove database c p u utilization two ninety eight percent p ninety five query latenc climbed from fifteen milliseconds two twelve hundred milliseconds within four minutes the database connection pool on six catalog worker pods exhaust all fifty available connections causing edge gateways two return status five hundred internal server errors on thirty percent of incoming browsing requests the incident team executed an immediate rollback of the deployment buy running cube ctl rollout undo deployment product catalog dash service two version two dot four dot zero wait version two dot four dot zero instead after rolling back the release operators recycled the saturated database connections and increased post gres read replicas from four two eight nodes normal response latenc returned buy fourteen forty five follow up action items include implementing rigorous integration tests four cache invalidation patterns and setting query execution timeout limits two five hundred milliseconds",
        "refined_text": "At 1420 during a rolling deployment of the product catalog service, an unverified cache invalidation routine purged all Redis session keys rather than the target category namespace. Downstream Postgres primary and replica nodes experienced 15000 cache misses per second, which drove database CPU utilization to 98 percent. P95 query latency climbed from 15 milliseconds to 1200 milliseconds within 4 minutes.\n\nThe database connection pool on 6 catalog worker pods exhausted all 50 available connections, causing edge gateways to return status 500 Internal Server Errors on 30 percent of incoming browsing requests. The incident team executed an immediate rollback of the deployment by running `kubectl rollout undo deployment product-catalog-service` to version 2.4.0 instead.\n\nAfter rolling back the release, operators recycled the saturated database connections and increased Postgres read replicas from 4 to 8 nodes. Normal response latency returned by 1445. Follow-up action items include implementing rigorous integration tests for cache invalidation patterns and setting query execution timeout limits to 500 milliseconds."
    },
    {
        # L3: Identity Provider Key Rotation Misconfiguration
        "raw_asr": "uh at zero six hundred during scheduled credential rotation the identity provider service generated a new r s a private key but failed two publish the updated public key two the j w k s endpoint as a result forty microservices failed token validation and emitted status four hundred one unauthorized responses on twenty thousand incoming user requests the authorization gateway thread pool saturated within five minutes as client applications initiated immediate retry loops without exponential backoff the incident team determined that the public key distribution task encountered an invalid file permiss error on the shared s three bucket buy zero six thirty engineers manually updated the j w k s certificate file and rotat the secret keys traffic stabilized buy zero six forty five after engineers cleared edge token verification caches and restarted six authentication pods downstream error rates dropped back two baseline postmortem remedial actions involve automating j w k s health checks before initiating key rotat and enforcing exponential backoff across all internal r p c clients",
        "refined_text": "At 0600 during scheduled credential rotation, the identity provider service generated a new RSA private key but failed to publish the updated public key to the JWKS endpoint. As a result, 40 microservices failed token validation and emitted status 401 Unauthorized responses on 20000 incoming user requests.\n\nThe authorization gateway thread pool saturated within 5 minutes as client applications initiated immediate retry loops without exponential backoff. The incident team determined that the public key distribution task encountered an invalid file permission error on the shared S3 bucket. By 0630 engineers manually updated the JWKS certificate file and rotated the secret keys.\n\nTraffic stabilized by 0645 after engineers cleared edge token verification caches and restarted 6 authentication pods. Downstream error rates dropped back to baseline. Postmortem remedial actions involve automating JWKS health checks before initiating key rotation and enforcing exponential backoff across all internal RPC clients."
    },
    {
        # L4: Streaming Telemetry Checkpoint Timeout
        "raw_asr": "basically the streaming analytics cluster suffered checkpoint timeouts across eighteen task manager pods during peak ingestion at eleven fifteen heavy network congestion on the shared object storage gateway caused checkpoint write latenc two exceed sixty seconds triggering automatic job cancellation the flink job manager attempted four restarts within ten minutes buy each restart triggered an immediate crash loop back off condition the primary investigation revealed that unaligned checkpoints were disabled in flink configur which caused checkpoint barriers two get stuck behind sixty thousand pending event buffers in the netty transport pipeline task manager j v m heaps exceeded eight gigabytes as uncommitted state accumulated until linux c group limits killed forty processes with exit code one hundred thirty seven at eleven forty five operators applied a mitigation buy enabling unaligned checkpoints in the flink deployment manifest and increasing the checkpoint timeout parameter two one hundred twenty seconds the cluster resumed steady state consumption buy twelve zero zero without further data loss engineering teams scheduled follow up tasks two isolate telemetry checkpoint traffic on dedicated object storage prefixes",
        "refined_text": "Basically the streaming analytics cluster suffered checkpoint timeouts across 18 task manager pods during peak ingestion at 1115. Heavy network congestion on the shared object storage gateway caused checkpoint write latency to exceed 60 seconds, triggering automatic job cancellation. The Flink job manager attempted 4 restarts within 10 minutes, but each restart triggered an immediate crash loop back-off condition.\n\nThe primary investigation revealed that unaligned checkpoints were disabled in Flink configuration, which caused checkpoint barriers to get stuck behind 60000 pending event buffers in the Netty transport pipeline. Task manager JVM heaps exceeded 8 gigabytes as uncommitted state accumulated until Linux cgroup limits killed 40 processes with exit code 137.\n\nAt 1145 operators applied a mitigation by enabling unaligned checkpoints in the Flink deployment manifest and increasing the checkpoint timeout parameter to 120 seconds. The cluster resumed steady-state consumption by 1200 without further data loss. Engineering teams scheduled follow-up tasks to isolate telemetry checkpoint traffic on dedicated object storage prefixes."
    },
    {
        # L5: Network Partition and Consul Split-Brain
        "raw_asr": "uh at zero two zero zero network telemetry observed b g p route flapping between primary and secondary datacenter links the consul quorum lost synchronizat when inter datacenter packet loss rose two thirty five percent consul servers on knowed three and knowed four partitioned themselves into an isolated raft group electing a split leader service discovery clients received stale health catalogs routing forty percent of internal r p c traffic two terminat backend pods the incident team declared severity one at zero two fifteen as microservice connection timeouts escalated two six hundred errors per second on the billing api engineers inspected consul leader status buy querying raft metrics over port eight five zero zero and discovered divergent raft commit indices between the separated server peers at zero two thirty network operations stabilized the core transit links and forced raft peer reconciliation across five surviving server nodes buy removing unreachable members normal service discovery registration recovered buy zero two fifty the postmortem team prioritiz deploying w a n gossip pool encryption and increasing raft election timeouts two two thousand milliseconds",
        "refined_text": "At 0200 network telemetry observed BGP route flapping between primary and secondary datacenter links. The Consul quorum lost synchronization when inter-datacenter packet loss rose to 35 percent. Consul servers on node 3 and node 4 partitioned themselves into an isolated Raft group, electing a split leader. Service discovery clients received stale health catalogs, routing 40 percent of internal RPC traffic to terminated backend pods.\n\nThe incident team declared severity 1 at 0215 as microservice connection timeouts escalated to 600 errors per second on the billing API. Engineers inspected Consul leader status by querying Raft metrics over port 8500 and discovered divergent Raft commit indices between the separated server peers.\n\nAt 0230 network operations stabilized the core transit links and forced Raft peer reconciliation across 5 surviving server nodes by removing unreachable members. Normal service discovery registration recovered by 0250. The postmortem team prioritized deploying WAN gossip pool encryption and increasing Raft election timeouts to 2000 milliseconds."
    },
    {
        # L6: Cassandra Commitlog I/O Saturation
        "raw_asr": "basically at sixteen forty the cassandra cluster experienced severe disk write stalls across eight storage nodes commitlog write latenc jumped from two milliseconds two eighty five milliseconds during concurrent table compaction unthrottled compaction tasks saturated n v m e storage write queues causing thirty percent of incoming write mutations two time out knowed seven and knowed eight dropped out of the gossip ring after missing gossiper heartbeats four thirty seconds the incident commander directed database operators two inspect compaction backlog buy running nodetool compactionstats operators discovered that concurrent compaction threads were saturating the host file system i o quota buy seventeen zero zero engineers mitigated write contention buy throttling concurrent compactors from eight two four wait two four threads instead and executing nodetool stop compaction across the affected hosts normal write latenc returned buy seventeen twenty the postmortem action items call four migrating two size tiered compaction on high write column families and setting disk write bandwidth caps",
        "refined_text": "Basically at 1640 the Cassandra cluster experienced severe disk write stalls across 8 storage nodes. Commitlog write latency jumped from 2 milliseconds to 85 milliseconds during concurrent table compaction. Unthrottled compaction tasks saturated NVMe storage write queues, causing 30 percent of incoming write mutations to time out.\n\nNode 7 and node 8 dropped out of the gossip ring after missing gossiper heartbeats for 30 seconds. The incident commander directed database operators to inspect compaction backlog by running `nodetool compactionstats`. Operators discovered that concurrent compaction threads were saturating the host file system I/O quota.\n\nBy 1700 engineers mitigated write contention by throttling concurrent compactors from 8 to 4 threads instead and executing `nodetool stop compaction` across the affected hosts. Normal write latency returned by 1720. The postmortem action items call for migrating to size-tiered compaction on high-write column families and setting disk write bandwidth caps."
    },
    {
        # L7: CoreDNS UDP Query Packet Drops
        "raw_asr": "uh at zero eight fifteen internal microservices experienced widespread d n s look up failures across the production coober netties cluster core d n s pods on worker knowed eleven and knowed fourteen became unresponsive as u d p query processing saturated one hundred percent of the c p u quota investigation revealed that a newly deployed catalog service set ndots five in the pod resolv dot conf template causing client containers two emit five sequential domain search queries four every single outbound h t t p call cluster query volume spiked from four thousand queries per second two eighty five thousand queries per second buy zero eight thirty causing local resolvers two drop sixty percent of network packets the incident squad mitigated the name resolut storm buy scaling core d n s from four two twenty replicas across independent worker nodes and deploying nodelocal d n s cache daemons on all active hosts normal query latenc was restored buy zero eight fifty engineering teams scheduled postmortem follow up items two enforce ndots two as a default pod policy and configure query rate limiting on core d n s servers",
        "refined_text": "At 0815 internal microservices experienced widespread DNS lookup failures across the production Kubernetes cluster. CoreDNS pods on worker node 11 and worker node 14 became unresponsive as UDP query processing saturated 100 percent of the CPU quota.\n\nInvestigation revealed that a newly deployed catalog service set ndots 5 in the pod `resolv.conf` template, causing client containers to emit 5 sequential domain search queries for every single outbound HTTP call. Cluster query volume spiked from 4000 queries per second to 85000 queries per second by 0830, causing local resolvers to drop 60 percent of network packets.\n\nThe incident squad mitigated the name resolution storm by scaling CoreDNS from 4 to 20 replicas across independent worker nodes and deploying NodeLocal DNSCache daemons on all active hosts. Normal query latency was restored by 0850. Engineering teams scheduled postmortem follow-up items to enforce ndots 2 as a default pod policy and configure query rate limiting on CoreDNS servers."
    },
    {
        # L8: GraphQL Federation Gateway Event Loop Lag
        "raw_asr": "basically at twenty one ten the graph q l federation gateway experienced severe event loop lag during evening user traffic an unauthenticated client executed deeply nested relational queries that bypassed depth limit middleware the node j s event loop lag spiked from five milliseconds two four thousand milliseconds blocking a sink i o operations and causing edge load balancers two drop four hundred fifty connections per second with five zero four gateway timeouts investigation showed that resolver functions executed unbatched database queries across four downstream subgraphs without using data loader instances gateway worker pods reached ninety five percent memory saturat as thousands of pending promise objects accumulated in the heap buy twenty one thirty engineers deployed a hotfix configur that enforced query depth limits at six levels and capped query complexity score two two hundred wait two two hundred points instead they restarted twelve gateway pods buy running cube ctl rollout restart deployment graphql dash gateway normal gateway responsiveness returned buy twenty one forty postmortem action items require mandating data loaders across all federated entities and configuring persistent query whitelisting",
        "refined_text": "Basically at 2110 the GraphQL federation gateway experienced severe event loop lag during evening user traffic. An unauthenticated client executed deeply nested relational queries that bypassed depth limit middleware. The Node.js event loop lag spiked from 5 milliseconds to 4000 milliseconds, blocking async I/O operations and causing edge load balancers to drop 450 connections per second with 504 gateway timeouts.\n\nInvestigation showed that resolver functions executed unbatched database queries across 4 downstream subgraphs without using data loader instances. Gateway worker pods reached 95 percent memory saturation as thousands of pending promise objects accumulated in the heap.\n\nBy 2130 engineers deployed a hotfix configuration that enforced query depth limits at 6 levels and capped query complexity score to 200 points instead. They restarted 12 gateway pods by running `kubectl rollout restart deployment graphql-gateway`. Normal gateway responsiveness returned by 2140. Postmortem action items require mandating data loaders across all federated entities and configuring persistent query whitelisting."
    },
    {
        # L9: Microservice Cascading Timeout and Database Lock
        "raw_asr": "uh at zero five fifteen the settlement processing pipeline experienced cascading connection timeouts during an online database schema migration an exclusive lock on the transactions table blocked query execution four forty five seconds causing worker thread pools two saturate across thirty consumer pods because upstream services lacked circuit breaker protection and exponential backoff eighty client instances initiated aggressive retries every five hundred milliseconds the resulting retry storm drove database connection demand two eighteen hundred sessions which exceeded the post gres max connections ceiling and rejected new client connections at zero five forty database administrators terminated the blocking migration query buy executing select pg cancel backend wait pg terminate backend instead on server knowed two and configured a statement timeout limit of five seconds the connection pooler shed stale client sockets allowing normal settlement transactions two resume buy zero six zero zero follow up action items require mandating distributed tracing on all migration scripts and enforcing retry jitter across client libraries",
        "refined_text": "At 0515 the settlement processing pipeline experienced cascading connection timeouts during an online database schema migration. An exclusive lock on the transactions table blocked query execution for 45 seconds, causing worker thread pools to saturate across 30 consumer pods.\n\nBecause upstream services lacked circuit breaker protection and exponential backoff, 80 client instances initiated aggressive retries every 500 milliseconds. The resulting retry storm drove database connection demand to 1800 sessions, which exceeded the Postgres max connections ceiling and rejected new client connections.\n\nAt 0540 database administrators terminated the blocking migration query by executing `SELECT pg_terminate_backend` instead on server node 2 and configured a statement timeout limit of 5 seconds. The connection pooler shed stale client sockets, allowing normal settlement transactions to resume by 0600. Follow-up action items require mandating distributed tracing on all migration scripts and enforcing retry jitter across client libraries."
    },
    {
        # L10: Netty Direct Memory Leak in gRPC Proxy
        "raw_asr": "basically at eighteen thirty the telemetry ingestion gateway suffered rolling pod evictions across twenty four proxy instances during high volume sensor streaming the g r p c edge proxies developed a direct memory leak in netty byte buffer allocations when handling client stream cancellations direct memory consumption climbed past twelve gigabytes per container triggering linux c group limit violations that terminat proxy processes with exit code one hundred thirty seven as proxy pods restarted simultaneously cold connection storms flooded edge load balancers causing three hundred dropped connections per second with five zero two bad gateway responses the incident commander coordinated an emergency configur update buy eighteen fifty five wait nineteen ten instead operators enabled netty heap allocations buy applying dash d io dot netty dot noPreferDirect equals true in j v m arguments and increased container memory limits two sixteen gigabytes proxy memory consumption stabilized buy nineteen thirty without further container evictions postmortem remediation items mandate adding netty leak detection monitors in continuous integration and configuring proactive memory threshold alerts",
        "refined_text": "Basically at 1830 the telemetry ingestion gateway suffered rolling pod evictions across 24 proxy instances during high-volume sensor streaming. The gRPC edge proxies developed a direct memory leak in Netty byte buffer allocations when handling client stream cancellations. Direct memory consumption climbed past 12 gigabytes per container, triggering Linux cgroup limit violations that terminated proxy processes with exit code 137.\n\nAs proxy pods restarted simultaneously, cold connection storms flooded edge load balancers, causing 300 dropped connections per second with 502 Bad Gateway responses. The incident commander coordinated an emergency configuration update by 1910 instead.\n\nOperators enabled Netty heap allocations by applying `-Dio.netty.noPreferDirect=true` in JVM arguments and increased container memory limits to 16 gigabytes. Proxy memory consumption stabilized by 1930 without further container evictions. Postmortem remediation items mandate adding Netty leak detection monitors in continuous integration and configuring proactive memory threshold alerts."
    }
]

print(f"Total samples defined: {len(samples)}")

all_valid = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(samples, 1):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]
    v_ok, v_msg = validate_pair(pair)
    c_res, c_msg = clean_sample(raw, ref)
    words = len(ref.split())
    raw_words = len(raw.split())
    ratio = words / max(1, raw_words)

    if words < 25:
        tier = "SHORT"
        tier_counts["short"] += 1
    elif words < 90:
        tier = "MEDIUM"
        tier_counts["medium"] += 1
    else:
        tier = "LONG"
        tier_counts["long"] += 1

    status = "OK" if (v_ok and c_msg == "kept") else "FAIL"
    if status == "FAIL":
        all_valid = False
        print(f"Sample {idx:02d} [{tier}] FAIL: validator='{v_msg}', cleaner='{c_msg}'")
    else:
        print(f"Sample {idx:02d} [{tier}] PASS: words={words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

b_ok, b_msg, b_tiers = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: {b_ok} - {b_msg} (tiers: {b_tiers})")

if all_valid and b_ok:
    out_path = "scratch/subagent_batch_55.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote 20 verified samples to {out_path}!")
else:
    print("\nValidation failed! Please review errors above.")
    sys.exit(1)
