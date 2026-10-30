import json
import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
  # Sample 1: Short (< 25 words, exactly 1 sentence, 0 newlines)
  {
    "raw_asr": "the post gres database pool reached max communicat capacity buy rejecting fifty two client requests during peak traffic",
    "refined_text": "The `Postgres` database pool reached max communication capacity by rejecting 52 client requests during peak traffic."
  },
  # Sample 2: Short (< 25 words, exactly 1 sentence, 0 newlines)
  {
    "raw_asr": "um roll back the billing knowed deployment buy reverting container release twenty four after configur panic crashes",
    "refined_text": "Roll back the billing node deployment by reverting container release 24 after configuration panic crashes."
  },
  # Sample 3: Medium (25-90 words, 1-3 sentences, natural \n\n break)
  {
    "raw_asr": "the redis session cache suffered a thundering herd when sixty wait eighty key leases expired buy midnight causing severe degradat um we mitigated the latency spike buy adding twenty millisecond jitter to lease renewals and warming keys before terminat",
    "refined_text": "The `redis` session cache suffered a thundering herd when 80 key leases expired by midnight, causing severe degradation.\n\nWe mitigated the latency spike by adding 20 millisecond jitter to lease renewals and warming keys before termination."
  },
  # Sample 4: Medium (25-90 words, 1-3 sentences, natural \n\n break)
  {
    "raw_asr": "basically the telemetry pipeline accumulated fifty wait seventy thousand unread messages buy noon because kafka partition consumers stalled during broker rebalanc um we restored throughput buy clearing the offset commit error and scaling the consumer group to four replicas",
    "refined_text": "The telemetry pipeline accumulated 70000 unread messages by noon because `kafka` partition consumers stalled during broker rebalancing.\n\nWe restored throughput by clearing the offset commit error and scaling the consumer group to 4 replicas."
  },
  # Sample 5: Medium (25-90 words, 1-3 sentences, natural \n\n break)
  {
    "raw_asr": "the ingress controller knowed failed liveness probes because c group v two memory limits throttl the envoy proxy process um we inspected the event log buy running cube ctl describe on the host knowed and adjusted the container memory request to five hundred megabytes",
    "refined_text": "The ingress controller node failed liveness probes because `cgroupv2` memory limits throttled the `envoy` proxy process.\n\nWe inspected the event log by running `kubectl describe` on the host node and adjusted the container memory request to 500 megabytes."
  },
  # Sample 6: Long (90+ words, multi-paragraph \n\n, zero checklist stereotypes)
  {
    "raw_asr": "basically at fourteen twenty wait at fourteen thirty the checkout gateway started failing customer payments buy returning h t t p five hundred four gateway timeout errors to the mobile client telemetry dashboards alerted on a sudden spike in payment latency exceeding ten seconds which caused twenty worker threads to stall while waiting for bank authorization responses the edge proxy exhausted available t c p sockets within three minutes because client retries overwhelmed the front door load balancer um our triage team traced the communicat bottleneck to the authorization microservice where thread pool allocat reached one hundred percent capacity the authorization service failed to terminat dead socket sessions which held database connection handles open across all active nodes audit logs confirmed that an unannounced upstream provider network degradat delayed payment webhook acknowledgments buy twelve seconds per transaction we mitigated the cascading failure buy redirecting checkout transactions to the secondary payment provider root we also terminated all hung t c p sessions buy reloading the edge proxy upstream targets and scaling the checkout worker deployment to sixteen pods transaction error rates dropped back to zero buy fifteen ten and payment processing resumed normal operat",
    "refined_text": "At 14:30, the checkout gateway started failing customer payments by returning `HTTP` 504 gateway timeout errors to the mobile client. Telemetry dashboards alerted on a sudden spike in payment latency exceeding 10 seconds, which caused 20 worker threads to stall while waiting for bank authorization responses. The edge proxy exhausted available `TCP` sockets within 3 minutes because client retries overwhelmed the front door load balancer.\n\nOur triage team traced the communication bottleneck to the authorization microservice, where thread pool allocation reached 100% capacity. The authorization service failed to terminate dead socket sessions, which held database connection handles open across all active nodes. Audit logs confirmed that an unannounced upstream provider network degradation delayed payment webhook acknowledgments by 12 seconds per transaction.\n\nWe mitigated the cascading failure by redirecting checkout transactions to the secondary payment provider route. We also terminated all hung `TCP` sessions by reloading the edge proxy upstream targets and scaling the checkout worker deployment to 16 pods. Transaction error rates dropped back to 0 by 15:10, and payment processing resumed normal operation."
  },
  # Sample 7: Long (90+ words, multi-paragraph \n\n, zero checklist stereotypes)
  {
    "raw_asr": "basically border router three wait border router four initiated a rapid b g p session flap buy dropping keepalive beacons every thirty seconds network telemetry showed severe packet transmiss loss across the core datacenter fabric because the border knowed repeatedly announced and withdrew the default root to external peers the flapping root table triggered high c p u utilization in the control plane processor which delayed border telemetry buy forty milliseconds uh the site reliability engineering team investigated the routing table flap buy examining syslog alerts on the router console diagnostic traces revealed that an automated interface configur script applied an incorrect keepalive hold timer of four seconds instead of ninety seconds because the hold timer expired before the neighbor router could send a keepalive response the b g p peer declared the link down and flushed thirty thousand prefixes from the forward table we stabilized the border router buy reverting the keepalive timer to ninety seconds and enabling b g p root dampening across the external interface we verified peer synchronizat buy inspecting the prefix advertisement count and monitoring link stability for twenty minutes normal network operat resumed without further packet loss",
    "refined_text": "Border router 4 initiated a rapid `BGP` session flap by dropping keepalive beacons every 30 seconds. Network telemetry showed severe packet transmission loss across the core datacenter fabric because the border node repeatedly announced and withdrew the default route to external peers. The flapping route table triggered high `CPU` utilization in the control plane processor, which delayed border telemetry by 40 milliseconds.\n\nThe site reliability engineering team investigated the routing table flap by examining syslog alerts on the router console. Diagnostic traces revealed that an automated interface configuration script applied an incorrect keepalive hold timer of 4 seconds instead of 90 seconds. Because the hold timer expired before the neighbor router could send a keepalive response, the `BGP` peer declared the link down and flushed 30000 prefixes from the forward table.\n\nWe stabilized the border router by reverting the keepalive timer to 90 seconds and enabling `BGP` route dampening across the external interface. We verified peer synchronization by inspecting the prefix advertisement count and monitoring link stability for 20 minutes. Normal network operation resumed without further packet loss."
  },
  # Sample 8: Long (90+ words, multi-paragraph \n\n, zero checklist stereotypes)
  {
    "raw_asr": "the post gres primary database cluster experienced severe connection pool exhaust when a background invoice audit job executed an unindexed join query across thirty million billing ledger records query execution time jumped from fifty milliseconds to twelve seconds buy locking the invoice balance table telemetry metrics indicated that sixty wait eighty database connections became saturated buy idle in transaction states which blocked all incoming payment right operations from the checkout api um the database engineering team diagnosed the query lockup buy inspecting active backend processes in post gres pg stat activity diagnostic logs revealed that the invoice audit worker lacked an explicit statement timeout allowing long running table scans to hold exclusive row locks across the primary knowed the pooler exhausted all one hundred allocated client connections causing four hundred twenty backend requests to fail with connection timeout errors we resolved the database outage buy terminating the blocked audit queries and setting statement timeout to five seconds across all audit worker roles we also added an index on the ledger account identifier buy executing create index concurrently and scaled read traffic to three read replicas database c p u utilization returned to normal within four minutes",
    "refined_text": "The `Postgres` primary database cluster experienced severe connection pool exhaustion when a background invoice audit job executed an unindexed join query across 30000000 billing ledger records. Query execution time jumped from 50 milliseconds to 12 seconds by locking the invoice balance table. Telemetry metrics indicated that 80 database connections became saturated by idle in transaction states, which blocked all incoming payment write operations from the checkout api.\n\nThe database engineering team diagnosed the query lockup by inspecting active backend processes in `Postgres` `pg_stat_activity`. Diagnostic logs revealed that the invoice audit worker lacked an explicit statement timeout, allowing long-running table scans to hold exclusive row locks across the primary node. The pooler exhausted all 100 allocated client connections, causing 420 backend requests to fail with connection timeout errors.\n\nWe resolved the database outage by terminating the blocked audit queries and setting statement timeout to 5 seconds across all audit worker roles. We also added an index on the ledger account identifier by executing create index concurrently and scaled read traffic to 3 read replicas. Database `CPU` utilization returned to normal within 4 minutes."
  },
  # Sample 9: Long (90+ words, multi-paragraph \n\n, zero checklist stereotypes)
  {
    "raw_asr": "basically the clickstream event ingestion pipeline suffered a severe kafka consumer rebalance storm when eight partition workers triggered heart beat timeouts buy exceeding max poll interval during burst traffic consumer lag spiked to fifty thousand unread events within five minutes causing downstream analytics dashboards to show stale telemetry the repeated rebalancing cycle degraded event root throughput because consumer group members spent more time in join group synchronizat states than processing active partition messages um our infrastructure team investigated the rebalance storm buy analyzing consumer thread dumps and c group memory metrics the logs indicated that intensive deserializat tasks consumed excessive c p u cycles which starved the heartbeat background thread buy twenty seconds because heartbeat pulses failed to reach the kafka coordinator knowed the broker repeatedly evicted healthy consumers and reassigned partition ownership across remaining pods we eliminated the rebalance storm buy increasing max poll interval to five minutes and configuring a dedicated heartbeat thread in the consumer runtime we also capped consumer batch fetch sizes to two hundred records buy tuning the ingestion configur and scaled the consumer group to twelve worker pods consumer lag cleared completely within ten minutes and partition assignment remained stable",
    "refined_text": "The clickstream event ingestion pipeline suffered a severe `Kafka` consumer rebalance storm when 8 partition workers triggered heartbeat timeouts by exceeding max poll interval during burst traffic. Consumer lag spiked to 50000 unread events within 5 minutes, causing downstream analytics dashboards to show stale telemetry. The repeated rebalancing cycle degraded event route throughput because consumer group members spent more time in join group synchronization states than processing active partition messages.\n\nOur infrastructure team investigated the rebalance storm by analyzing consumer thread dumps and `cgroup` memory metrics. The logs indicated that intensive deserialization tasks consumed excessive `CPU` cycles, which starved the heartbeat background thread by 20 seconds. Because heartbeat pulses failed to reach the `Kafka` coordinator node, the broker repeatedly evicted healthy consumers and reassigned partition ownership across remaining pods.\n\nWe eliminated the rebalance storm by increasing max poll interval to 5 minutes and configuring a dedicated heartbeat thread in the consumer runtime. We also capped consumer batch fetch sizes to 200 records by tuning the ingestion configuration and scaled the consumer group to 12 worker pods. Consumer lag cleared completely within 10 minutes, and partition assignment remained stable."
  },
  # Sample 10: Long (90+ words, multi-paragraph \n\n, zero checklist stereotypes)
  {
    "raw_asr": "the order fulfillment backend entered an o o m killed crashloop cascade when four pods wait six worker pods exhausted c group memory limits buy buffering unbounded order notification payloads customer order status updates stalled across three retail regions buy accumulating over five hundred unacknowledged webhooks inside heap buffers telemetry graphs revealed a steep memory leak profile where resident set size climbed continuously buy fifty megabytes per minute until the linux kernel killed the process um the platform operations team diagnosed the crashloop buy inspecting pod termination reasons with cube ctl describe pod and examining java heap dumps the diagnostic trace confirmed that the notification dispatcher accumulated unclosed h t t p response bodies in an unbounded static array list whenever external webhook endpoints timed out because memory allocat exceeded two gigabytes the container runtime terminated each pod with exit code one hundred thirty seven we resolved the crashloop failure buy deploying hotfix release zero x five a which properly wraps response streams in try with resources blocks we also enforced a strict queue depth limit of one thousand pending notifications buy adjusting the service configur and increased container memory limits to two gigabytes across all six knowed instances the fulfillment deployment stabilized immediately buy clearing pending backlog queues",
    "refined_text": "The order fulfillment backend entered an OOMKilled crashloop cascade when 6 worker pods exhausted `cgroup` memory limits by buffering unbounded order notification payloads. Customer order status updates stalled across 3 retail regions by accumulating over 500 unacknowledged webhooks inside heap buffers. Telemetry graphs revealed a steep memory leak profile where resident set size climbed continuously by 50 megabytes per minute until the Linux kernel killed the process.\n\nThe platform operations team diagnosed the crashloop by inspecting pod termination reasons with `kubectl describe pod` and examining Java heap dumps. The diagnostic trace confirmed that the notification dispatcher accumulated unclosed `HTTP` response bodies in an unbounded static array list whenever external webhook endpoints timed out. Because memory allocation exceeded 2 gigabytes, the container runtime terminated each pod with exit code 137.\n\nWe resolved the crashloop failure by deploying hotfix release 0x5a, which properly wraps response streams in try with resources blocks. We also enforced a strict queue depth limit of 1000 pending notifications by adjusting the service configuration and increased container memory limits to 2 gigabytes across all 6 node instances. The fulfillment deployment stabilized immediately by clearing pending backlog queues."
  }
]

print(f"Total samples: {len(samples)}")

all_valid = True
for idx, pair in enumerate(samples):
    raw = pair["raw_asr"]
    ref = pair["refined_text"]
    
    # 1. validate_pair
    val_ok, val_reason = validate_pair(pair)
    
    # 2. clean_sample
    cleaned, clean_reason = clean_sample(raw, ref)
    clean_ok = cleaned is not None
    
    words = len(ref.split())
    raw_words = len(raw.split())
    ratio = words / raw_words
    
    print(f"Sample {idx+1}: words={words}, raw_words={raw_words}, ratio={ratio:.2f}")
    if not val_ok:
        print(f"  FAILED validate_pair: {val_reason}")
        all_valid = False
    else:
        print("  PASSED validate_pair")
        
    if not clean_ok:
        print(f"  FAILED clean_sample: {clean_reason}")
        all_valid = False
    else:
        print("  PASSED clean_sample")

batch_ok, batch_reason, tier_counts = validate_batch(samples, min_short=2, min_medium=3, min_long=5)
print("\nBatch Validation:")
print(f"  Batch OK: {batch_ok}")
print(f"  Reason: {batch_reason}")
print(f"  Tiers: {tier_counts}")

if all_valid and batch_ok:
    print("\nALL SAMPLES PASSED 100%!")
    with open("scratch/subagent_batch_9.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print("Saved to scratch/subagent_batch_9.json")
else:
    print("\nSOME SAMPLES FAILED!")
