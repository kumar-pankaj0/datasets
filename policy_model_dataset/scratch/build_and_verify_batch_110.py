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

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
    # ----------------------------------------------------
    # TIER 1: SHORT (< 25 words, exactly 1 sentence, 0 newlines)
    # ----------------------------------------------------
    # Sample 1 (Short 1)
    {
        "raw_asr": "um cube ctl drain knowed worker five buy terminat stuck pods immediately",
        "refined_text": "Kubectl drain node worker 5 by terminating stuck pods immediately."
    },
    # Sample 2 (Short 2)
    {
        "raw_asr": "uh drain idle connections on post gres port five four three two buy terminat leaking client sessions",
        "refined_text": "Drain idle connections on Postgres port 5432 by terminating leaking client sessions."
    },
    # Sample 3 (Short 3)
    {
        "raw_asr": "inspect incoming network traffic with wi re shark buy capturing s y n packets on interface eth zero",
        "refined_text": "Inspect incoming network traffic with Wireshark by capturing SYN packets on interface eth0."
    },
    # Sample 4 (Short 4)
    {
        "raw_asr": "adjust c group v two memory limits buy writing five hundred twelve megabytes into the memory max controller",
        "refined_text": "Adjust cgroupv2 memory limits by writing 512 megabytes into the memory max controller."
    },

    # ----------------------------------------------------
    # TIER 2: MEDIUM (25-89 words, 1-3 sentences, natural \n\n)
    # ----------------------------------------------------
    # Sample 5 (Medium 1)
    {
        "raw_asr": "our kafka consumer group billing workers triggered a rebalance storm buy exceeding max poll interval milliseconds during batch updates we set the poll timeout to twenty wait we set it into thirty seconds instead across twelve consumer pods",
        "refined_text": "Our Kafka consumer group billing workers triggered a rebalance storm by exceeding max poll interval milliseconds during batch updates.\n\nWe set the poll timeout into 30 seconds instead across 12 consumer pods."
    },
    # Sample 6 (Medium 2)
    {
        "raw_asr": "the n g i n x ingress controller reported five zero two bad gateway spikes buy exhausting backend keepalive sockets during peak traffic we mitigated the connection drops buy enabling upstream keepalive with two five six idle connections",
        "refined_text": "The NGINX ingress controller reported 502 bad gateway spikes by exhausting backend keepalive sockets during peak traffic.\n\nWe mitigated the connection drops by enabling upstream keepalive with 256 idle connections."
    },
    # Sample 7 (Medium 3)
    {
        "raw_asr": "um the redis cache knowed hit c group memory limits buy buffering large replication streams during snapshot persistence the orchestrator failed over traffic towards replica three after sixty seconds of master knowed heartbeat loss",
        "refined_text": "The Redis cache node hit cgroup memory limits by buffering large replication streams during snapshot persistence.\n\nThe orchestrator failed over traffic towards replica 3 after 60 seconds of master node heartbeat loss."
    },
    # Sample 8 (Medium 4)
    {
        "raw_asr": "post gres reported severe row lock contention on the ledger accounts table buy running concurrent batch settlements without row ordering we eliminated deadlocks buy applying explicit advisory locks across sixteen worker processes",
        "refined_text": "Postgres reported severe row lock contention on the ledger accounts table by running concurrent batch settlements without row ordering.\n\nWe eliminated deadlocks by applying explicit advisory locks across 16 worker processes."
    },
    # Sample 9 (Medium 5)
    {
        "raw_asr": "dns lookup latency spiked buy exceeding fifteen hundred milliseconds inside coober netties worker nodes the engineering team stabilized name resolution buy configur local coredns cache daemons on all forty nodes",
        "refined_text": "DNS lookup latency spiked by exceeding 1500 milliseconds inside Kubernetes worker nodes.\n\nThe engineering team stabilized name resolution by configuring local CoreDNS cache daemons on all 40 nodes."
    },
    # Sample 10 (Medium 6)
    {
        "raw_asr": "the elasticsearch cluster marked twelve shards unassigned buy pausing query execution during garbage collection pauses we restored index health buy allocat eight gigabytes of j v m heap across five data nodes",
        "refined_text": "The Elasticsearch cluster marked 12 shards unassigned by pausing query execution during garbage collection pauses.\n\nWe restored index health by allocating 8 gigabytes of JVM heap across 5 data nodes."
    },

    # ----------------------------------------------------
    # TIER 3: LONG (90+ words, multi-paragraph separated by \n\n)
    # ----------------------------------------------------
    # Sample 11 (Long 1)
    {
        "raw_asr": "our checkout payment gateway experienced an incident buy returning five zero three service unavailable errors during the afternoon flash sale client requests backed up rapidly pushing p ninety nine latency from two hundred milliseconds through four two zero zero milliseconds across eight gateway instances the connection pool became saturated buy exhausting all two hundred database client connections within four minutes the originating flaw stemmed from unindexed customer ledger lookups holding transaction locks during external banking verification calls the database worker threads stalled while waiting on row level write locks which forced the upstream circuit breaker into an open failure state blocking further incoming transactions the on call engineers mitigated the outage buy scaling the connection pool from two hundred through four hundred connections and deploying pgbouncer poolers across all eight gateway hosts latency stabilized at one four zero milliseconds after draining stuck transactions",
        "refined_text": "Our checkout payment gateway experienced an incident by returning 503 service unavailable errors during the afternoon flash sale. Client requests backed up rapidly, pushing P99 latency from 200 milliseconds through 4200 milliseconds across 8 gateway instances. The connection pool became saturated by exhausting all 200 database client connections within 4 minutes.\n\nThe originating flaw stemmed from unindexed customer ledger lookups holding transaction locks during external banking verification calls. The database worker threads stalled while waiting on row-level write locks, which forced the upstream circuit breaker into an open failure state, blocking further incoming transactions.\n\nThe on-call engineers mitigated the outage by scaling the connection pool from 200 through 400 connections and deploying PgBouncer poolers across all 8 gateway hosts. Latency stabilized at 140 milliseconds after draining stuck transactions."
    },
    # Sample 12 (Long 2)
    {
        "raw_asr": "the api routing service suffered event loop starvation under a load of five thousand requests per second a sink i o event loop latency spiked from two milliseconds through eight five zero milliseconds across eight gateway pods the health check endpoints timed out buy exceeding the three second gateway timeout threshold profiling logs revealed a blocking synchronous disk read inside the request token verification middleware instead of delegating file checks towards an async thread worker the middleware executed blocking input output directly on the primary event loop thread which stalled all scheduled socket tasks across the runtime the site reliability team mitigated the incident buy moving token reading into background thread executors and restarting the deployment across sixteen worker pods normal event loop latency recovered below five milliseconds after traffic resumed",
        "refined_text": "The API routing service suffered event loop starvation under a load of 5000 requests per second. Asyncio event loop latency spiked from 2 milliseconds through 850 milliseconds across 8 gateway pods. The health check endpoints timed out by exceeding the 3 second gateway timeout threshold.\n\nProfiling logs revealed a blocking synchronous disk read inside the request token verification middleware. Instead of delegating file checks towards an async thread worker, the middleware executed blocking input output directly on the primary event loop thread, which stalled all scheduled socket tasks across the runtime.\n\nThe site reliability team mitigated the incident by moving token reading into background thread executors and restarting the deployment across 16 worker pods. Normal event loop latency recovered below 5 milliseconds after traffic resumed."
    },
    # Sample 13 (Long 3)
    {
        "raw_asr": "during peak data streaming our telemetry consumer pods experienced repeated o o m killer terminations inside coober netties container memory usage increased steadily across six hours until hitting the c group limit of four zero nine six megabytes which caused frequent pod crash loops investigation of the heap dump confirmed uncommitted payload buffers were retained in memory during consumer partition rebalance events the primary defect occurred when consumer offset commits timed out during large batch transformations leaving thirty thousand stale event references pinned inside memory we stabilized the pipeline buy draining stalled consumer instances and configur explicit buffer flush cycles after every poll interval across twenty four worker instances memory consumption leveled off at eight hundred megabytes without further terminations",
        "refined_text": "During peak data streaming, our telemetry consumer pods experienced repeated OOM killer terminations inside Kubernetes. Container memory usage increased steadily across 6 hours until hitting the cgroup limit of 4096 megabytes, which caused frequent pod crash loops.\n\nInvestigation of the heap dump confirmed uncommitted payload buffers were retained in memory during consumer partition rebalance events. The primary defect occurred when consumer offset commits timed out during large batch transformations, leaving 30000 stale event references pinned inside memory.\n\nWe stabilized the pipeline by draining stalled consumer instances and configuring explicit buffer flush cycles after every poll interval across 24 worker instances. Memory consumption leveled off at 800 megabytes without further terminations."
    },
    # Sample 14 (Long 4)
    {
        "raw_asr": "edge reverse proxies reported widespread five zero four gateway timeouts during a sudden inbound traffic surge packet capture analysis with wi re shark on interface eth zero revealed fifteen percent t c p s y n drops at the network boundary with thousands of connection resets kernel socket buffers were overwhelmed buy lacking socket reuse between edge proxies and downstream backend services the originating flaw was an unconfigured keepalive timeout holding one zero zero zero zero sockets in time wait state which exhausted the ephemeral port range across all four proxy nodes the infrastructure team restored normal traffic buy enabling persistent upstream connection pools with one two eight idle sockets and increasing the kernel somaxconn backlog into four zero nine six connections drop rates dropped to zero within three minutes",
        "refined_text": "Edge reverse proxies reported widespread 504 gateway timeouts during a sudden inbound traffic surge. Packet capture analysis with Wireshark on interface eth0 revealed 15 percent TCP SYN drops at the network boundary with thousands of connection resets.\n\nKernel socket buffers were overwhelmed by lacking socket reuse between edge proxies and downstream backend services. The originating flaw was an unconfigured keepalive timeout holding 10000 sockets in TIME_WAIT state, which exhausted the ephemeral port range across all 4 proxy nodes.\n\nThe infrastructure team restored normal traffic by enabling persistent upstream connection pools with 128 idle sockets and increasing the kernel somaxconn backlog into 4096 connections. Drop rates dropped to 0 within 3 minutes."
    },
    # Sample 15 (Long 5)
    {
        "raw_asr": "the primary post gres database instance encountered severe write stalls when write ahead log flush duration increased from four milliseconds through six five zero milliseconds write transactions backed up rapidly buy blocking three hundred concurrent client connections across the application tier telemetry from the cloud infrastructure revealed the database storage volume exhausted its burst i o p s credit balance during an unthrottled index rebuilding job disk queue depth escalated to sixty four pending requests halting sequential journal flushes and causing cascaded query lock timeouts we resolved the database stall buy throttling background maintenance workers and provisioning dedicated storage throughput at three thousand i o p s across the database volume write latency returned to six milliseconds within five minutes of the volume modification",
        "refined_text": "The primary Postgres database instance encountered severe write stalls when write-ahead log flush duration increased from 4 milliseconds through 650 milliseconds. Write transactions backed up rapidly by blocking 300 concurrent client connections across the application tier.\n\nTelemetry from the cloud infrastructure revealed the database storage volume exhausted its burst IOPS credit balance during an unthrottled index rebuilding job. Disk queue depth escalated to 64 pending requests, halting sequential journal flushes and causing cascaded query lock timeouts.\n\nWe resolved the database stall by throttling background maintenance workers and provisioning dedicated storage throughput at 3000 IOPS across the database volume. Write latency returned to 6 milliseconds within 5 minutes of the volume modification."
    },
    # Sample 16 (Long 6)
    {
        "raw_asr": "distributed tracing with jaeger identified severe latency amplification propagating across the catalog and cart microservices p ninety five latency jumped from forty five milliseconds through eighteen hundred milliseconds across all customer facing endpoints the originating flaw was located inside the centralized authentication service where a cache eviction storm forced each incoming request to query the underlying database the master auth redis knowed reached ninety eight percent processor utilization while handling forty five thousand requests per second the engineering team stabilized system operations buy extending cache time to live durations into three hundred seconds and enabling client side circuit breakers blocking redundant token queries downstream service latency recovered below fifty milliseconds after fifteen minutes",
        "refined_text": "Distributed tracing with Jaeger identified severe latency amplification propagating across the catalog and cart microservices. P95 latency jumped from 45 milliseconds through 1800 milliseconds across all customer-facing endpoints.\n\nThe originating flaw was located inside the centralized authentication service, where a cache eviction storm forced each incoming request to query the underlying database. The master auth Redis node reached 98 percent processor utilization while handling 45000 requests per second.\n\nThe engineering team stabilized system operations by extending cache time-to-live durations into 300 seconds and enabling client-side circuit breakers blocking redundant token queries. Downstream service latency recovered below 50 milliseconds after 15 minutes."
    },
    # Sample 17 (Long 7)
    {
        "raw_asr": "automated certificate renewal caused connection disruptions across four edge load balancer instances during scheduled maintenance incoming client sessions failed with handshake timeout errors buy elevating total connection failures to twenty two percent live inspection showed the certificate manager daemon failed to reload t l s keys buy encountering a permission denied error on the mounted secret directory the orchestrator kept serving expired cryptographic credentials because the reload script terminat before updating active proxy worker threads we mitigated the incident buy rolling back to the previous certificate secret fixing directory permissions and performing a clean graceful reload across all eight proxy daemons edge handshake failure rates declined to zero after four minutes",
        "refined_text": "Automated certificate renewal caused connection disruptions across 4 edge load balancer instances during scheduled maintenance. Incoming client sessions failed with handshake timeout errors by elevating total connection failures to 22 percent.\n\nLive inspection showed the certificate manager daemon failed to reload TLS keys by encountering a permission denied error on the mounted secret directory. The orchestrator kept serving expired cryptographic credentials because the reload script terminated before updating active proxy worker threads.\n\nWe mitigated the incident by rolling back to the previous certificate secret, fixing directory permissions, and performing a clean graceful reload across all 8 proxy daemons. Edge handshake failure rates declined to 0 after 4 minutes."
    },
    # Sample 18 (Long 8)
    {
        "raw_asr": "the asynchronous notification pipeline halted completely when the rabbitmq cluster triggered a memory alarm buy blocking all inbound publisher connections the message backlog grew rapidly to five hundred thousand unacknowledged messages within twenty minutes diagnostic logs revealed worker consumer processes crashed buy encountering unhandled serialization exceptions in email formatting tasks the message broker consumed twelve gigabytes of memory which crossed the eighty percent safety threshold and halted socket reads across all producers we restored message ingestion buy purging invalid task messages into a dead letter exchange and restarting eighteen worker pods with validated schema parsing logic the queue backlog cleared within thirty five minutes without message loss",
        "refined_text": "The asynchronous notification pipeline halted completely when the RabbitMQ cluster triggered a memory alarm by blocking all inbound publisher connections. The message backlog grew rapidly to 500000 unacknowledged messages within 20 minutes.\n\nDiagnostic logs revealed worker consumer processes crashed by encountering unhandled serialization exceptions in email formatting tasks. The message broker consumed 12 gigabytes of memory, which crossed the 80 percent safety threshold and halted socket reads across all producers.\n\nWe restored message ingestion by purging invalid task messages into a dead-letter exchange and restarting 18 worker pods with validated schema parsing logic. The queue backlog cleared within 35 minutes without message loss."
    },
    # Sample 19 (Long 9)
    {
        "raw_asr": "worker nodes across the coober netties cluster experienced intermittent connection timeouts and five zero three errors between internal services internal d n s resolution latency increased from three milliseconds through twelve hundred milliseconds during high deployment turnover system analysis revealed u d p socket buffer drops inside the c n i network namespace caused buy single threaded forwarder throughput constraints coredns instances suffered c group cpu throttling after hitting two zero zero millicores of usage which delayed recursive upstream query responses the platform team resolved the degradation buy scaling coredns from two through ten replicas and enabling node local d n s caching daemons across all sixty cluster nodes query response latency dropped below two milliseconds across all namespaces",
        "refined_text": "Worker nodes across the Kubernetes cluster experienced intermittent connection timeouts and 503 errors between internal services. Internal DNS resolution latency increased from 3 milliseconds through 1200 milliseconds during high deployment turnover.\n\nSystem analysis revealed UDP socket buffer drops inside the CNI network namespace caused by single-threaded forwarder throughput constraints. CoreDNS instances suffered cgroup CPU throttling after hitting 200 millicores of usage, which delayed recursive upstream query responses.\n\nThe platform team resolved the degradation by scaling CoreDNS from 2 through 10 replicas and enabling node-local DNS caching daemons across all 60 cluster nodes. Query response latency dropped below 2 milliseconds across all namespaces."
    },
    # Sample 20 (Long 10)
    {
        "raw_asr": "the go event processing daemon suffered severe request queuing and p ninety nine latency degradation during concurrent batch ingestion data ingestion throughput dropped from eight thousand events per second down into twelve hundred events per second across all worker instances operating system telemetry showed the linux kernel throttled container c p u execution buy sixty five percent due to restrictive c f s quota allocations the go runtime scheduler experienced operating system thread starvation while scheduling five hundred active worker goroutines on restricted cpu time slices we eliminated the execution stalls buy expanding container c p u limits from two through eight cores and configur the gomaxprocs runtime parameter into eight threads across all fifteen worker pods processing throughput recovered to eight thousand events per second within two minutes",
        "refined_text": "The Go event processing daemon suffered severe request queuing and P99 latency degradation during concurrent batch ingestion. Data ingestion throughput dropped from 8000 events per second down into 1200 events per second across all worker instances.\n\nOperating system telemetry showed the Linux kernel throttled container CPU execution by 65 percent due to restrictive CFS quota allocations. The Go runtime scheduler experienced operating system thread starvation while scheduling 500 active worker goroutines on restricted CPU time slices.\n\nWe eliminated the execution stalls by expanding container CPU limits from 2 through 8 cores and configuring the GOMAXPROCS runtime parameter into 8 threads across all 15 worker pods. Processing throughput recovered to 8000 events per second within 2 minutes."
    }
]

print(f"Total pairs: {len(pairs)}")
assert len(pairs) == 20

tiers = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(pairs):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = val_mod.validate_pair(pair)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"
    assert clean_reason == "kept", f"Sample {idx+1} clean status: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    if words < 25:
        tiers["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1! Got: {sentences}"
    elif words < 90:
        tiers["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3! Got: {sentences}"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
    else:
        tiers["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

    print(f"Sample {idx+1:2d} passed: {words:3d} words, tier: {('short' if words < 25 else 'medium' if words < 90 else 'long')}")

print(f"\nTier counts: {tiers}")
assert tiers["short"] == 4, f"Expected 4 short, got {tiers['short']}"
assert tiers["medium"] == 6, f"Expected 6 medium, got {tiers['medium']}"
assert tiers["long"] == 10, f"Expected 10 long, got {tiers['long']}"

batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"Batch validation failed: {batch_msg}"
print(f"validate_batch: {batch_msg}")

output_path = Path("scratch/subagent_batch_110.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2, ensure_ascii=False)

print(f"\nSaved 20 validated pairs to {output_path}")
print("ALL CHECKS PASSED DETERMINISTICALLY WITH 0 ERRORS!")
