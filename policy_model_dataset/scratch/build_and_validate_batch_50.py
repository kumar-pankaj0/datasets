import json
import re
from pathlib import Path
import importlib.util

# Load validator and cleaner
val_spec = importlib.util.spec_from_file_location("val_mod", "code/validator.py")
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)

clean_spec = importlib.util.spec_from_file_location("clean_mod", "code/cleaner.py")
clean_mod = importlib.util.module_from_spec(clean_spec)
clean_spec.loader.exec_module(clean_mod)

# Load sft_eval.json to verify zero leakage
with open("sft_eval.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

pairs = [
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples
    {
        "raw_asr": "um the payment service dropped incoming checkout requests buy redis connection pool exhaust during the traffic surge",
        "refined_text": "The payment service dropped incoming checkout requests by Redis connection pool exhaustion during the traffic surge."
    },
    {
        "raw_asr": "basically netfilter con n track table overflow dropped incoming t c p syn packets on gateway knowed instances",
        "refined_text": "Netfilter conntrack table overflow dropped incoming TCP SYN packets on gateway node instances."
    },
    {
        "raw_asr": "uh the ingress gateway rejected external client handshakes buy expired internal t l s certifi chain",
        "refined_text": "The ingress gateway rejected external client handshakes by expired internal TLS certificate chain."
    },
    {
        "raw_asr": "um the telemetry consumer group triggered continuous rebalanc after missing session timeouts buy three hundred milliseconds",
        "refined_text": "The telemetry consumer group triggered continuous rebalancing after missing session timeouts by 300 milliseconds."
    },

    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples
    {
        "raw_asr": "our incident postmortem revealed synchronous h t t p billing calls caused tomcat thread pool exhaust during checkout peaks um the on call engineer increased active worker threads from thirty wait fifty workers instead buy deploying the hotfix within twelve minutes",
        "refined_text": "Our incident postmortem revealed synchronous HTTP billing calls caused Tomcat thread pool exhaustion during checkout peaks.\n\nThe on-call engineer increased active worker threads to 50 workers instead by deploying the hotfix within 12 minutes."
    },
    {
        "raw_asr": "the checkout proxy cluster experienced cascading circuit breaker trips buy upstream database latency reaching eight hundred milliseconds um e n voy tripped circuit breakers across every edge knowed when error rates exceeded ten wait twenty percent instead",
        "refined_text": "The checkout proxy cluster experienced cascading circuit breaker trips by upstream database latency reaching 800 milliseconds.\n\nEnvoy tripped circuit breakers across every edge node when error rates exceeded 20 percent instead."
    },
    {
        "raw_asr": "basically unbuffered d n s lookups created query amplificat across internal coober netties worker knowed clusters during microservice discovery um core d n s pods dropped thirty thousand udp requests buy reaching upstream rate limits within five minutes",
        "refined_text": "Unbuffered DNS lookups created query amplification across internal Kubernetes worker node clusters during microservice discovery.\n\nCoreDNS pods dropped 30000 UDP requests by reaching upstream rate limits within 5 minutes."
    },
    {
        "raw_asr": "uh the linux netfilter kernel module dropped inbound connections after con n track table limit reached sixty wait eighty thousand entries during port scanning traffic um the perimeter router terminated twenty thousand invalid sessions buy flushing stale tracking state",
        "refined_text": "The Linux netfilter kernel module dropped inbound connections after conntrack table limit reached 80000 entries during port scanning traffic.\n\nThe perimeter router terminated 20000 invalid sessions by flushing stale tracking state."
    },
    {
        "raw_asr": "um the authentication gateway encountered redis connection starvat when active client pool leases exhausted four hundred sockets buy burst traffic spikes um the session cache returned five hundred gateway errors across forty thousand user requests",
        "refined_text": "The authentication gateway encountered Redis connection starvation when active client pool leases exhausted 400 sockets by burst traffic spikes.\n\nThe session cache returned 500 gateway errors across 40000 user requests."
    },
    {
        "raw_asr": "basically a k af ka partition rebalanc storm cascaded through the payment settlement consumers when message processing time exceeded session timeout buy sixty seconds um three consumer knowed instances left the consumer group triggering unassigned partitions across one hundred workers",
        "refined_text": "A Kafka partition rebalancing storm cascaded through the payment settlement consumers when message processing time exceeded session timeout by 60 seconds.\n\nThree consumer node instances left the consumer group triggering unassigned partitions across 100 workers."
    },

    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples
    {
        "raw_asr": "our incident postmortem analyzed the k af ka partition rebalanc storm affecting the telemetry ingestion pipeline during peak traffic hours unhandled schema variations caused schema deserializ failures inside the consumer loop driving j v m garbage collection pauses beyond thirty seconds because the consumer heartbeat thread shared execution context with the message worker the broker coordinator marked consumer knowed instances dead after missing the session timeout window of forty wait sixty seconds instead um this triggered an eager consumer group rebalance across sixty four partitions revoking active leases and halting consumption across thirty worker instances each rebalance round took twenty seconds during which incoming messages accumulated in the broker write log creating a consumer lag of five hundred thousand records uh the engineering team remediated the outage buy decoupling heartbeats into a dedicated background daemon thread and increasing max poll interval two thousand records while stabilizing p ninety nine processing latency at fourteen milliseconds",
        "refined_text": "Our incident postmortem analyzed the Kafka partition rebalancing storm affecting the telemetry ingestion pipeline during peak traffic hours. Unhandled schema variations caused schema deserialization failures inside the consumer loop, driving JVM garbage collection pauses beyond 30 seconds. Because the consumer heartbeat thread shared execution context with the message worker, the broker coordinator marked consumer node instances dead after missing the session timeout window of 60 seconds instead.\n\nThis triggered an eager consumer group rebalance across 64 partitions, revoking active leases and halting consumption across 30 worker instances. Each rebalance round took 20 seconds, during which incoming messages accumulated in the broker write log, creating a consumer lag of 500000 records. The engineering team remediated the outage by decoupling heartbeats into a dedicated background daemon thread and increasing max poll interval 2000 records while stabilizing P99 processing latency at 14 milliseconds."
    },
    {
        "raw_asr": "the root cause analysis investigated the tomcat thread pool exhaust incident that paralyzed our customer order gateway during morning flash sales downstream post gres connection starvat occurred when a slow analytical query held exclusive table locks four forty seconds incoming h t t p requests occupied all two hundred worker threads while waiting on available database connections from the connection pool with no available worker threads the inbound request queue overflowed and dropped five thousand checkout attempts buy returning five hundred four gateway timeouts um the incident team mitigated active failure modes buy killing the offending lock holding database process and restarting three tomcat knowed instances restoring operational health the engineering lead revised the runtime pool configur from one hundred wait two hundred workers instead and set a maximum connection acquisition timeout of three seconds uh during post incident load testing p ninety five request latency recovered two forty five milliseconds across sixty concurrent workers",
        "refined_text": "The root cause analysis investigated the Tomcat thread pool exhaustion incident that paralyzed our customer order gateway during morning flash sales. Downstream Postgres connection starvation occurred when a slow analytical query held exclusive table locks for 40 seconds. Incoming HTTP requests occupied all 200 worker threads while waiting on available database connections from the connection pool. With no available worker threads, the inbound request queue overflowed and dropped 5000 checkout attempts by returning 504 gateway timeouts.\n\nThe incident team mitigated active failure modes by killing the offending lock-holding database process and restarting 3 Tomcat node instances restoring operational health. The engineering lead revised the runtime pool configuration to 200 workers instead and set a maximum connection acquisition timeout of 3 seconds. During post-incident load testing, P95 request latency recovered to 45 milliseconds across 60 concurrent workers."
    },
    {
        "raw_asr": "our platform reliability postmortem reviewed the internal d n s resolution collapse observed across the coober netties production cluster during morning traffic ramp unbuffered search domain appending generated extreme query amplificat buy issuing eight queries four every external endpoint resolution the core d n s upstream u d p listener dropped forty percent of incoming queries when packet rate exceeded fifty thousand packets per second this packet drop triggered cascading socket timeouts across twenty dependent microservices escalating client retry storms buy flooding cluster knowed endpoints with redundant queries um the infrastructure team halted query degradation buy deploying a node local d n s cache daemonset across worker knowed instances and scaling core d n s replicas from five wait ten pods instead the updated configur disabled recursive search domain expansion four external hostnames uh following the rollout cluster wide p ninety nine d n s lookup latency dropped from eight hundred milliseconds down two four milliseconds across forty worker knowed instances",
        "refined_text": "Our platform reliability postmortem reviewed the internal DNS resolution collapse observed across the Kubernetes production cluster during morning traffic ramp. Unbuffered search domain appending generated extreme query amplification by issuing 8 queries for every external endpoint resolution. The CoreDNS upstream UDP listener dropped 40 percent of incoming queries when packet rate exceeded 50000 packets per second. This packet drop triggered cascading socket timeouts across 20 dependent microservices, escalating client retry storms by flooding cluster node endpoints with redundant queries.\n\nThe infrastructure team halted query degradation by deploying a node-local DNS cache daemonset across worker node instances and scaling CoreDNS replicas to 10 pods instead. The updated configuration disabled recursive search domain expansion for external hostnames. Following the rollout, cluster-wide P99 DNS lookup latency dropped from 800 milliseconds down to 4 milliseconds across 40 worker node instances."
    },
    {
        "raw_asr": "the networking postmortem documented edge gateway connection drop anomalies caused buy kernel netfilter con n track table exhaustion rapid connection allocat from asynchronous health check probes and incoming port scanning saturated the kernel state table reaching its limit of two hundred thousand tracked flows when the table filled the kernel dropped new incoming t c p syn packets buy emitting kernel table full warnings in the system log client applications experienced persistent connection timeouts and packet loss across sixty edge knowed proxies um the network team restored packet routing buy tuning the kernel netfilter parameters to increase max entries from one hundred wait two hundred fifty thousand sessions instead the sysctl update also reduced tcp time wait timeout from one hundred twenty seconds down two thirty seconds allowing rapid reclamation of dead sessions uh subsequent load verification sustained one hundred thousand concurrent active connections without incurring con n track drops across twelve gateway instances",
        "refined_text": "The networking postmortem documented edge gateway connection drop anomalies caused by kernel netfilter conntrack table exhaustion. Rapid connection allocation from asynchronous health check probes and incoming port scanning saturated the kernel state table, reaching its limit of 200000 tracked flows. When the table filled, the kernel dropped new incoming TCP SYN packets by emitting kernel table full warnings in the system log. Client applications experienced persistent connection timeouts and packet loss across 60 edge node proxies.\n\nThe network team restored packet routing by tuning the kernel netfilter parameters to increase max entries to 250000 sessions instead. The sysctl update also reduced TCP TIME_WAIT timeout from 120 seconds down to 30 seconds, allowing rapid reclamation of dead sessions. Subsequent load verification sustained 100000 concurrent active connections without incurring conntrack drops across 12 gateway instances."
    },
    {
        "raw_asr": "the incident review documented cascading circuit breaker trips across our microservice mesh triggered buy redis cache cluster knowed failure during primary knowed failover read traffic flooded the database layer creating query backlog and connection starvat the e n voy sidecar proxies detected latency spikes and tripped circuit breakers buy transitioning into open state across forty downstream services with circuit breakers open e n voy rejected incoming h t t p requests buy returning five hundred three service unavailable errors causing customer facing transaction drop rates of eighty percent um the site reliability team stabilized the service mesh buy adjusting e n voy circuit breaker thresholds to allow higher pending request queues and setting connection timeout to fifty wait eighty milliseconds instead the team terminated the unresponsive redis replica and promoted a healthy follower knowed uh after the failover completed p ninety nine latency dropped back two fifteen milliseconds and e n voy closed circuit breakers across thirty active service deployments",
        "refined_text": "The incident review documented cascading circuit breaker trips across our microservice mesh triggered by Redis cache cluster node failure. During primary node failover, read traffic flooded the database layer, creating query backlog and connection starvation. The Envoy sidecar proxies detected latency spikes and tripped circuit breakers by transitioning into open state across 40 downstream services. With circuit breakers open, Envoy rejected incoming HTTP requests by returning 503 Service Unavailable errors, causing customer-facing transaction drop rates of 80 percent.\n\nThe site reliability team stabilized the service mesh by adjusting Envoy circuit breaker thresholds to allow higher pending request queues and setting connection timeout to 80 milliseconds instead. The team terminated the unresponsive Redis replica and promoted a healthy follower node. After the failover completed, P99 latency dropped back to 15 milliseconds and Envoy closed circuit breakers across 30 active service deployments."
    },
    {
        "raw_asr": "our postmortem investigated the production ingress outage caused buy unexpected t l s certifi expirat across customer facing endpoints an automated renew failed when the cert manager webhook could not communicate across worker knowed subnets due to network policy rules the internal x five zero nine certificate expired at midnight causing edge load balancers to reject incoming t c p connections buy failing t l s handshakes external web clients and mobile applications received ssl handshake failed alerts resulting in twenty thousand dropped sessions across eighty ingress routes um the security operations team resolved the outage buy applying an emergency cert manager secret update using cube ctl to deploy renewed certificates directly the engineering team revised webhook timeout policies from twenty four wait forty eight hours instead and established multi channel alerts triggering thirty days before certifi expirat uh post incident validation confirmed valid x five zero nine chains across all fifty edge endpoints without handshake errors",
        "refined_text": "Our postmortem investigated the production ingress outage caused by unexpected TLS certificate expiration across customer-facing endpoints. An automated renewal failed when the cert-manager webhook could not communicate across worker node subnets due to network policy rules. The internal X.509 certificate expired at midnight, causing edge load balancers to reject incoming TCP connections by failing TLS handshakes. External web clients and mobile applications received SSL handshake failed alerts, resulting in 20000 dropped sessions across 80 ingress routes.\n\nThe security operations team resolved the outage by applying an emergency cert-manager secret update using kubectl to deploy renewed certificates directly. The engineering team revised webhook timeout policies to 48 hours instead and established multi-channel alerts triggering 30 days before certificate expiration. Post-incident validation confirmed valid X.509 chains across all 50 edge endpoints without handshake errors."
    },
    {
        "raw_asr": "the site reliability postmortem examined the g r p c service degradation caused buy thread pool starvat across our identity validation service during morning peak hours a custom json logging framework executed blocking synchronous disk right operations on every incoming r p c request when the local disk controller experienced write queue saturation the logging appender blocked worker threads one buy one until all worker threads suffered exhaust with no available threads to process incoming connections the netty transport layer backed up buy dropping twelve thousand r p c requests across twenty five knowed instances um the on call engineer mitigated the outage buy switching the logging framework configuration to an a sink appender and expanding the worker thread pool from one hundred wait two hundred fifty threads instead the team also configured bounded queue rejection four telemetry events uh load testing confirmed p ninety nine latency recovered two eighteen milliseconds while sustaining ten thousand requests per second across twenty worker knowed instances",
        "refined_text": "The site reliability postmortem examined the gRPC service degradation caused by thread pool starvation across our identity validation service during morning peak hours. A custom JSON logging framework executed blocking synchronous disk write operations on every incoming RPC request. When the local disk controller experienced write queue saturation, the logging appender blocked worker threads one by one until all worker threads suffered exhaustion. With no available threads to process incoming connections, the Netty transport layer backed up by dropping 12000 RPC requests across 25 node instances.\n\nThe on-call engineer mitigated the outage by switching the logging framework configuration to an async appender and expanding the worker thread pool to 250 threads instead. The team also configured bounded queue rejection for telemetry events. Load testing confirmed P99 latency recovered to 18 milliseconds while sustaining 10000 requests per second across 20 worker node instances."
    },
    {
        "raw_asr": "the payment platform postmortem detailed the severe service brownout caused buy redis client connection starvat during weekend transaction volumes an unhandled exception branch inside the authorization handler failed to return borrowed connections back to the connection pool over several hours active socket leaks consumed all available connection handles across fifteen application knowed instances when new checkout requests arrived the client connection pool blocked indefinitely waiting four free sockets triggering widespread timeout failures across forty microservices incoming h t t p traffic experienced persistent failures buy returning five hundred internal server errors on thirty thousand checkout transactions um the incident commander initiated mitigation buy cycling all application pods and purging leaked tcp sockets the database team increased max total pool connections from two hundred wait five hundred sockets instead and enforced a strict connection borrow timeout of two seconds uh following the patch p ninety five checkout latency returned two twenty milliseconds across twenty thousand transactions per minute",
        "refined_text": "The payment platform postmortem detailed the severe service brownout caused by Redis client connection starvation during weekend transaction volumes. An unhandled exception branch inside the authorization handler failed to return borrowed connections back to the connection pool. Over several hours, active socket leaks consumed all available connection handles across 15 application node instances. When new checkout requests arrived, the client connection pool blocked indefinitely waiting for free sockets, triggering widespread timeout failures across 40 microservices. Incoming HTTP traffic experienced persistent failures by returning 500 internal server errors on 30000 checkout transactions.\n\nThe incident commander initiated mitigation by cycling all application pods and purging leaked TCP sockets. The database team increased max total pool connections to 500 sockets instead and enforced a strict connection borrow timeout of 2 seconds. Following the patch, P95 checkout latency returned to 20 milliseconds across 20000 transactions per minute."
    },
    {
        "raw_asr": "the media ingestion incident postmortem reviewed the continuous k af ka partition rebalanc storm affecting document o c r processing large multi megabyte pdf files caused heavy c p u compute and memory allocat extending per record processing duration beyond five minutes because the poll interval was exceeded the group coordinator inferred consumer knowed failure and revoked partition assignments across twenty workers the resulting rebalance evicted healthy consumers buy resetting committed offsets and creating partition lockups throughout the cluster consumer lag expanded buy fifty thousand unprocessed tasks across thirty partitions um the operations group stabilized pipeline processing buy isolating heavy document processing into an asynchronous task queue and increasing consumer max poll interval to fifteen minutes the infrastructure team scaled worker capacity from ten wait twenty worker instances instead with dynamic thread scaling uh after rebalancing ceased partition assignment stabilized within ten seconds and p ninety nine processing time dropped back two twenty five milliseconds",
        "refined_text": "The media ingestion incident postmortem reviewed the continuous Kafka partition rebalancing storm affecting document OCR processing. Large multi-megabyte PDF files caused heavy CPU compute and memory allocation, extending per-record processing duration beyond 5 minutes. Because the poll interval was exceeded, the group coordinator inferred consumer node failure and revoked partition assignments across 20 workers. The resulting rebalance evicted healthy consumers by resetting committed offsets and creating partition lockups throughout the cluster. Consumer lag expanded by 50000 unprocessed tasks across 30 partitions.\n\nThe operations group stabilized pipeline processing by isolating heavy document processing into an asynchronous task queue and increasing consumer max poll interval to 15 minutes. The infrastructure team scaled worker capacity to 20 worker instances instead with dynamic thread scaling. After rebalancing ceased, partition assignment stabilized within 10 seconds and P99 processing time dropped back to 25 milliseconds."
    },
    {
        "raw_asr": "the network operations postmortem analyzed the multi zone connection outage caused buy cross zone link flapping and con n track table saturation across gateway edge routers intermittent fiber flap degraded communicat across three availability zones causing high socket retransmission rates and piling up half open t c p state entries the netfilter tracking table reached its ceiling of three hundred thousand flows triggering kernel packet drops buy discarding new incoming syn packets simultaneously cluster internal d n s resolution degraded when worker knowed lookups timed out under heavy packet loss driving twenty thousand cascading service connection failures um the infrastructure network team restored normal transit buy routing cross zone traffic through a redundant direct connect circuit and raising con n track max size from two hundred wait five hundred thousand entries instead the systems engineering group also enabled tcp selective acknowledgments to improve recovery from dropped segments uh during post incident traffic verification p ninety nine link latency returned two six milliseconds without any recorded con n track drop events across fifty edge routers",
        "refined_text": "The network operations postmortem analyzed the multi-zone connection outage caused by cross-zone link flapping and conntrack table saturation across gateway edge routers. Intermittent fiber flap degraded communication across 3 availability zones, causing high socket retransmission rates and piling up half-open TCP state entries. The netfilter tracking table reached its ceiling of 300000 flows, triggering kernel packet drops by discarding new incoming SYN packets. Simultaneously, cluster internal DNS resolution degraded when worker node lookups timed out under heavy packet loss, driving 20000 cascading service connection failures.\n\nThe infrastructure network team restored normal transit by routing cross-zone traffic through a redundant direct connect circuit and raising conntrack max size to 500000 entries instead. The systems engineering group also enabled TCP selective acknowledgments to improve recovery from dropped segments. During post-incident traffic verification, P99 link latency returned to 6 milliseconds without any recorded conntrack drop events across 50 edge routers."
    }
]

# Validation
print(f"Total samples: {len(pairs)}")
assert len(pairs) == 20, f"Expected 20 pairs, got {len(pairs)}"

tier_counts = {"short": 0, "medium": 0, "long": 0}

for idx, pair in enumerate(pairs):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]

    # ASCII check
    raw.encode("ascii")
    ref.encode("ascii")

    # Leakage check against sft_eval.json
    assert raw.strip().lower() not in eval_raws, f"Sample {idx+1} raw leaked into sft_eval.json!"
    assert ref.strip() not in eval_refs, f"Sample {idx+1} ref leaked into sft_eval.json!"

    # Validator check
    val_ok, val_reason = val_mod.validate_pair(pair)
    assert val_ok, f"Sample {idx+1} failed validate_pair: {val_reason}"

    # Cleaner check
    clean_obj, clean_reason = clean_mod.clean_sample(raw, ref)
    assert clean_obj is not None, f"Sample {idx+1} failed clean_sample: {clean_reason}"

    # Tier invariants
    words = len(ref.split())
    if words < 25:
        tier_counts["short"] += 1
        assert "\n" not in ref, f"Sample {idx+1} has newline in short tier!"
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert len(sentences) == 1, f"Sample {idx+1} has {len(sentences)} sentences, expected 1!"
    elif words < 90:
        tier_counts["medium"] += 1
        sentences = [s for s in re.split(r'[.!?]+', ref) if s.strip()]
        assert 1 <= len(sentences) <= 3, f"Sample {idx+1} has {len(sentences)} sentences, expected 1-3!"
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in medium tier!"
    else:
        tier_counts["long"] += 1
        assert "\n\n" in ref, f"Sample {idx+1} missing paragraph break in long tier!"

# Batch distribution check
batch_ok, batch_msg, batch_tiers = val_mod.validate_batch(pairs, min_short=4, min_medium=6, min_long=10)
assert batch_ok, f"Batch validation failed: {batch_msg}"
assert tier_counts == {"short": 4, "medium": 6, "long": 10}, f"Tier mismatch: {tier_counts}"

print("All 20 samples PASSED deterministic checks!")
print(f"Tier counts: {tier_counts}")
print(f"Batch validation result: {batch_msg}")

# Save to scratch/subagent_batch_50.json
out_path = Path("scratch/subagent_batch_50.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print(f"Successfully saved 20 samples to {out_path}")
