import json
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Gerund rationale ("by <action>"). No decimals, no dotted filenames.
    # =========================================================================

    # Sample 1: Terminating unresponsive worker pods
    {
        "raw_asr": "um terminat unresponsive worker pods buy issuing graceful drain signals across eight failing containers",
        "refined_text": "Terminate unresponsive worker pods by issuing graceful drain signals across 8 failing containers."
    },

    # Sample 2: Mitigating database connection pool starvation
    {
        "raw_asr": "uh mitigat database connection pool starvation buy raising max client connections towards ninety active sessions",
        "refined_text": "Mitigate database connection pool starvation by raising max client connections towards 90 active sessions."
    },

    # Sample 3: Restoring flapping BGP network sessions
    {
        "raw_asr": "basically restor flapping bgp network sessions buy clearing routing neighbor state across four border routers",
        "refined_text": "Restore flapping BGP network sessions by clearing routing neighbor state across 4 border routers."
    },

    # Sample 4: Recovering exhausted disk storage volumes
    {
        "raw_asr": "um recov exhausted disk storage volumes buy purging stale segment logs across twelve database partitions",
        "refined_text": "Recover exhausted disk storage volumes by purging stale segment logs across 12 database partitions."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # =========================================================================

    # Sample 5: Kafka consumer heartbeat timeout and rebalance mitigation
    {
        "raw_asr": "uh configur our streaming consumer watchdog inside consumer underscore monitor dot py buy extending heartbeat timeout thresholds across five seconds wait fifteen seconds instead uh mitigat partition rebalance storms buy pausing polling loops across thirty consumer threads um right four unit tests validating stable group membership",
        "refined_text": "Configure our streaming consumer watchdog inside consumer_monitor.py by extending heartbeat timeout thresholds across 15 seconds instead.\n\nMitigate partition rebalance storms by pausing polling loops across 30 consumer threads. Write 4 unit tests validating stable group membership."
    },

    # Sample 6: Redis probabilistic early expiration against cache stampede
    {
        "raw_asr": "um initializ probabilistic early expiration inside session underscore cache dot py buy computing delta refresh intervals across fifty milliseconds wait eighty milliseconds instead okay so damp cache dogpiling spikes buy caching computed token locks across twenty key partitions um right five unit tests confirming zero database stampede queries",
        "refined_text": "Initialize probabilistic early expiration inside session_cache.py by computing delta refresh intervals across 80 milliseconds instead.\n\nDamp cache dogpiling spikes by caching computed token locks across 20 key partitions. Write 5 unit tests confirming zero database stampede queries."
    },

    # Sample 7: NodeLocal DNS cache resolver to relieve conntrack table exhaustion
    {
        "raw_asr": "basically operat local node caching resolvers inside resolver underscore daemon dot py buy forwarding dns requests directly towards twelve node agents wait twenty node agents instead uh reliev conntrack table exhaustion buy caching upstream responses across sixty seconds um right three unit tests verifying sub millisecond dns resolution",
        "refined_text": "Operate local node caching resolvers inside resolver_daemon.py by forwarding DNS requests directly towards 20 node agents instead.\n\nRelieve conntrack table exhaustion by caching upstream responses across 60 seconds. Write 3 unit tests verifying sub-millisecond DNS resolution."
    },

    # Sample 8: Upstream keepalive connection pool sizing in reverse proxy
    {
        "raw_asr": "uh allocat extra upstream connection pools inside proxy underscore router dot py buy bumping keepalive connection quotas from one hundred sessions up into three hundred sessions wait five hundred sessions instead basically terminat hanging upstream sockets buy enforcing forty millisecond read timeouts um right four unit tests confirming clean socket teardown",
        "refined_text": "Allocate extra upstream connection pools inside proxy_router.py by bumping keepalive connection quotas from 100 sessions up into 500 sessions instead.\n\nTerminate hanging upstream sockets by enforcing 40 millisecond read timeouts. Write 4 unit tests confirming clean socket teardown."
    },

    # Sample 9: Distributed lock lease expiration heartbeat coordinator
    {
        "raw_asr": "um communicat lease expiration heartbeats inside lease underscore coordinator dot py buy broadcasting session renewal signals across four worker nodes wait eight worker nodes instead uh resolv distributed lock deadlocks buy clearing orphaned lease records older than thirty seconds um right five unit tests confirming immediate lock acquisition",
        "refined_text": "Communicate lease expiration heartbeats inside lease_coordinator.py by broadcasting session renewal signals across 8 worker nodes instead.\n\nResolve distributed lock deadlocks by clearing orphaned lease records older than 30 seconds. Write 5 unit tests confirming immediate lock acquisition."
    },

    # Sample 10: Postgres autovacuum worker throttling and table bloat recovery
    {
        "raw_asr": "basically calibrat autovacuum worker throttling inside storage underscore vacuum dot py buy lowering vacuum cost delay from twenty milliseconds down into ten milliseconds wait five milliseconds instead okay so recov disk table pages buy launching concurrent vacuum tasks across four bloated tables um right six unit tests verifying rapid dead tuple cleanup",
        "refined_text": "Calibrate autovacuum worker throttling inside storage_vacuum.py by lowering vacuum cost delay from 20 milliseconds down into 5 milliseconds instead.\n\nRecover disk table pages by launching concurrent vacuum tasks across 4 bloated tables. Write 6 unit tests verifying rapid dead tuple cleanup."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # =========================================================================

    # Sample 11: JVM Garbage Collection Pauses in Payment Gateway
    {
        "raw_asr": "basically our payment platform reliability team investigated severe payment latency spikes inside payment underscore cache dot py buy analyzing transaction telemetry during peak checkout traffic previously the payment service experienced fifteen second latency spikes and health check timeouts affecting twenty four thousand transactions across sixteen worker instances um the reliability engineers determined that the underlying defect was an unbounded hash map retaining token validations across twenty four thousand transaction records causing stop the world garbage collection pauses wait deploy an explicit least recently used cache buy setting an eviction ceiling of four zero nine six entries instead uh the team stabilized heap consumption across twelve worker shards buy purging expired transaction tokens okay so instruct the reliability engineers two benchmark cache eviction under eight thousand simulated payment requests and right four unit tests verifying that heap allocation stays under five one two megabytes without garbage collection stalls",
        "refined_text": "Our payment platform reliability team investigated severe payment latency spikes inside payment_cache.py by analyzing transaction telemetry during peak checkout traffic. Previously the payment service experienced 15-second latency spikes and health check timeouts affecting 24000 transactions across 16 worker instances.\n\nThe reliability engineers determined that the underlying defect was an unbounded hash map retaining token validations across 24000 transaction records, causing stop-the-world garbage collection pauses. Deploy an explicit least recently used cache by setting an eviction ceiling of 4096 entries instead.\n\nThe team stabilized heap consumption across 12 worker shards by purging expired transaction tokens. Instruct the reliability engineers to benchmark cache eviction under 8000 simulated payment requests, and write 4 unit tests verifying that heap allocation stays under 512 megabytes without garbage collection stalls."
    },

    # Sample 12: CoreDNS UDP Packet Drop under Kubernetes Pod Scale-out
    {
        "raw_asr": "uh our cluster infrastructure team triaged widespread gateway timeouts inside dns underscore triage dot py buy inspecting core dns pod telemetry during a batch deployment previously downstream api proxies logged five zero four gateway timeout errors across forty microservices when concurrent dns query rates surged past eighteen thousand queries per second um the platform engineers used cube ctl two inspect c group v two socket buffers finding severe udp packet drops across eight core dns pods uh the team resolved socket starvation buy deploying local node caching daemons and raising socket receive buffers from two five six kilobytes up into one zero two four kilobytes across thirty two cluster nodes instead of adding pod replicas okay so ask the operations team two benchmark dns resolution under thirty thousand synthetic queries and right five unit tests validating that query lookup latency remains below two milliseconds",
        "refined_text": "Our cluster infrastructure team triaged widespread gateway timeouts inside dns_triage.py by inspecting CoreDNS pod telemetry during a batch deployment. Previously downstream API proxies logged 504 gateway timeout errors across 40 microservices when concurrent DNS query rates surged past 18000 queries per second.\n\nThe platform engineers used kubectl to inspect cgroupv2 socket buffers, finding severe UDP packet drops across 8 CoreDNS pods. The team resolved socket starvation by deploying local node caching daemons and raising socket receive buffers from 256 kilobytes up into 1024 kilobytes across 32 cluster nodes instead of adding pod replicas.\n\nAsk the operations team to benchmark DNS resolution under 30000 synthetic queries, and write 5 unit tests validating that query lookup latency remains below 2 milliseconds."
    },

    # Sample 13: Postgres Connection Pool Starvation and Leaked Prepared Statements
    {
        "raw_asr": "basically our database operations group resolved connection pool exhaustion inside checkout underscore pool dot py buy auditing active client sessions during morning checkout spikes previously client applications exhausted available connection pools reaching the maximum limit of six hundred connections across twelve application pods um the database administrators used post gres system queries two inspect active threads discovering forty five idle in transaction sessions holding prepared statement locks across nine hundred seconds uh the team cleared blocked connections buy enforcing thirty second statement timeout ceilings inside pool configurations and draining stalled sessions across four read replicas instead of restarting the primary database instance okay so tell developers two run connection pool saturation stress tests under twelve hundred concurrent checkout queries and right four unit tests confirming that connection leases terminate properly upon statement timeout",
        "refined_text": "Our database operations group resolved connection pool exhaustion inside checkout_pool.py by auditing active client sessions during morning checkout spikes. Previously client applications exhausted available connection pools, reaching the maximum limit of 600 connections across 12 application pods.\n\nThe database administrators used Postgres system queries to inspect active threads, discovering 45 idle in transaction sessions holding prepared statement locks across 900 seconds. The team cleared blocked connections by enforcing 30-second statement timeout ceilings inside pool configurations and draining stalled sessions across 4 read replicas instead of restarting the primary database instance.\n\nTell developers to run connection pool saturation stress tests under 1200 concurrent checkout queries, and write 4 unit tests confirming that connection leases terminate properly upon statement timeout."
    },

    # Sample 14: Kafka Poison Pill Message and Deserialization Crash Loop
    {
        "raw_asr": "uh our streaming infrastructure team resolved partition consumption stalls inside order underscore consumer dot py buy analyzing consumer group offsets during an ingestion halt previously consumer lag spiked beyond one hundred fifty thousand messages across four event brokers when unescaped null characters crashed record deserializers across sixteen consumer containers um the event streaming engineers traced the failure two a poisoned payload structure which forced continuous partition rebalances across thirty two partition streams uh the team restored message flow buy adding dead letter queue routing inside consumer deserializers and redirecting malformed payloads into a quarantine stream across six partition workers instead of skipping offsets manually okay so direct the data team two replay five thousand quarantined messages through updated schema filters and right five unit tests confirming that deserializer exceptions route records cleanly into the dead letter topic",
        "refined_text": "Our streaming infrastructure team resolved partition consumption stalls inside order_consumer.py by analyzing consumer group offsets during an ingestion halt. Previously consumer lag spiked beyond 150000 messages across 4 event brokers when unescaped null characters crashed record deserializers across 16 consumer containers.\n\nThe event streaming engineers traced the failure to a poisoned payload structure which forced continuous partition rebalances across 32 partition streams. The team restored message flow by adding dead letter queue routing inside consumer deserializers and redirecting malformed payloads into a quarantine stream across 6 partition workers instead of skipping offsets manually.\n\nDirect the data team to replay 5000 quarantined messages through updated schema filters, and write 5 unit tests confirming that deserializer exceptions route records cleanly into the dead letter topic."
    },

    # Sample 15: Redis Replication Buffer Overflow and Continuous Resynchronization
    {
        "raw_asr": "basically our storage platform engineers stabilized cache node replication inside redis underscore sync dot py buy reviewing cluster synchronization metrics during high throughput batch writes previously the cache cluster suffered cascading master node failovers affecting eighteen percent of read requests when bulk updates overflowed replication buffers across three master instances um the systems engineers discovered that the primary defect was client output buffer limits set at one two eight megabytes which terminated replication links during heavy write bursts across six replica nodes uh the infrastructure developers eliminated failover storms buy expanding client output buffer allocations from one two eight megabytes up into five one two megabytes across six cache nodes instead of repartitioning the cluster okay so instruct site reliability engineers two simulate burst traffic of twenty thousand session keys and right four unit tests validating that replication links maintain sync without triggering node failovers",
        "refined_text": "Our storage platform engineers stabilized cache node replication inside redis_sync.py by reviewing cluster synchronization metrics during high-throughput batch writes. Previously the cache cluster suffered cascading master node failovers affecting 18 percent of read requests when bulk updates overflowed replication buffers across 3 master instances.\n\nThe systems engineers discovered that the primary defect was client output buffer limits set at 128 megabytes, which terminated replication links during heavy write bursts across 6 replica nodes. The infrastructure developers eliminated failover storms by expanding client output buffer allocations from 128 megabytes up into 512 megabytes across 6 cache nodes instead of repartitioning the cluster.\n\nInstruct site reliability engineers to simulate burst traffic of 20000 session keys, and write 4 unit tests validating that replication links maintain sync without triggering node failovers."
    },

    # Sample 16: NGINX Ingress Controller 502 Bad Gateway Keep-Alive Race Condition
    {
        "raw_asr": "um our edge networking engineers resolved ingress gateway failures inside ingress underscore proxy dot py buy inspecting reverse proxy connection logs during midday traffic surges previously the n g i n x ingress controller emitted four two zero zero bad gateway errors per minute across fourteen proxy instances when backend services closed idle connections unexpectedly uh the networking engineers used wi re shark two analyze tcp connection resets discovering that upstream containers closed idle sockets after sixty seconds while proxy workers reused connections after sixty five seconds wait align idle socket timers buy configuring keepalive timeouts at fifty seconds inside upstream profiles across eight backend pools instead uh the team eliminated gateway resets buy enabling automatic connection retries upon tcp socket close events okay so ask the edge team two execute load tests with ten thousand persistent http connections and right five unit tests verifying zero gateway errors during socket reuse",
        "refined_text": "Our edge networking engineers resolved ingress gateway failures inside ingress_proxy.py by inspecting reverse proxy connection logs during midday traffic surges. Previously the NGINX ingress controller emitted 4200 Bad Gateway errors per minute across 14 proxy instances when backend services closed idle connections unexpectedly.\n\nThe networking engineers used Wireshark to analyze TCP connection resets, discovering that upstream containers closed idle sockets after 60 seconds while proxy workers reused connections after 65 seconds. Align idle socket timers by configuring keepalive timeouts at 50 seconds inside upstream profiles across 8 backend pools instead.\n\nThe team eliminated gateway resets by enabling automatic connection retries upon TCP socket close events. Ask the edge team to execute load tests with 10000 persistent HTTP connections, and write 5 unit tests verifying zero gateway errors during socket reuse."
    },

    # Sample 17: etcd Space Quota Exhaustion and Cluster Write Lockout
    {
        "raw_asr": "basically our platform core team recovered the etcd storage cluster inside etcd underscore maintenance dot py buy analyzing control plane write failures during a cluster upgrade previously the kubernetes control plane became completely read only causing cube ctl resource creation two fail across fifty worker nodes when storage reached the quota limit of eight one nine two megabytes um the infrastructure engineers investigated cluster alarms finding that historical revision compaction was disabled across three etcd nodes which filled the backend bolt database uh the team restored control plane writes buy compacting revisions older than ten thousand generations and triggering offline database defragmentation across three cluster members instead of provisioning new volumes okay so instruct platform engineers two run recurring compaction every one thousand revisions and right four unit tests confirming that defragmentation routines run cleanly without dropping cluster consensus",
        "refined_text": "Our platform core team recovered the etcd storage cluster inside etcd_maintenance.py by analyzing control plane write failures during a cluster upgrade. Previously the Kubernetes control plane became completely read-only, causing kubectl resource creation to fail across 50 worker nodes when storage reached the quota limit of 8192 megabytes.\n\nThe infrastructure engineers investigated cluster alarms, finding that historical revision compaction was disabled across 3 etcd nodes, which filled the backend bolt database. The team restored control plane writes by compacting revisions older than 10000 generations and triggering offline database defragmentation across 3 cluster members instead of provisioning new volumes.\n\nInstruct platform engineers to run recurring compaction every 1000 revisions, and write 4 unit tests confirming that defragmentation routines run cleanly without dropping cluster consensus."
    },

    # Sample 18: Linux Kernel Conntrack Table Saturation during Flash Sale
    {
        "raw_asr": "uh our security operations team mitigated connection drop surges inside conntrack underscore tuner dot py buy analyzing packet drop telemetry during a product launch campaign previously the perimeter gateway dropped thirty five percent of incoming tcp syn handshakes across ten gateway nodes when client connections saturated the kernel state table um the systems engineers examined kernel diagnostics using d mesg discovering that active connection tracking entries reached the hard ceiling of two six two one four four entries uh the team eliminated connection drops buy doubling the conntrack maximum ceiling from two six two one four four entries up into five two four two eight eight entries and reducing tcp time wait timers from one hundred twenty seconds down into thirty seconds across sixteen firewall nodes instead of provisioning additional gateways okay so tell the security engineers two test network throughput with forty thousand simulated client sessions and right four unit tests validating that connection tracking tables stay below seventy percent utilization",
        "refined_text": "Our security operations team mitigated connection drop surges inside conntrack_tuner.py by analyzing packet drop telemetry during a product launch campaign. Previously the perimeter gateway dropped 35 percent of incoming TCP SYN handshakes across 10 gateway nodes when client connections saturated the kernel state table.\n\nThe systems engineers examined kernel diagnostics using dmesg, discovering that active connection tracking entries reached the hard ceiling of 262144 entries. The team eliminated connection drops by doubling the conntrack maximum ceiling from 262144 entries up into 524288 entries and reducing TCP TIME_WAIT timers from 120 seconds down into 30 seconds across 16 firewall nodes instead of provisioning additional gateways.\n\nTell the security engineers to test network throughput with 40000 simulated client sessions, and write 4 unit tests validating that connection tracking tables stay below 70 percent utilization."
    },

    # Sample 19: Elasticsearch Unassigned Shards and Disk Watermark Breach
    {
        "raw_asr": "um our search infrastructure team recovered unassigned indexes inside shard underscore recovery dot py buy inspecting cluster allocation states after an unexpected node failure previously search logging turned red and halted document indexing across twenty eight data nodes leaving one hundred twenty unassigned shards in a suspended state um the search reliability engineers reviewed cluster allocation health discovering that dual node crashes forced remaining nodes beyond the eighty five percent disk watermark ceiling which halted automated shard migrations across fifty search indices uh the team stabilized cluster health buy updating allocation thresholds from eighty five percent up into ninety percent and executing targeted shard reroutes across twelve priority indices instead of purging historical index data okay so instruct the search team two monitor replica recovery across sixty background shard transfers and right five unit tests confirming that cluster allocation recovers green status without manual reroute overrides",
        "refined_text": "Our search infrastructure team recovered unassigned indexes inside shard_recovery.py by inspecting cluster allocation states after an unexpected node failure. Previously search logging turned red and halted document indexing across 28 data nodes, leaving 120 unassigned shards in a suspended state.\n\nThe search reliability engineers reviewed cluster allocation health, discovering that dual node crashes forced remaining nodes beyond the 85 percent disk watermark ceiling, which halted automated shard migrations across 50 search indices. The team stabilized cluster health by updating allocation thresholds from 85 percent up into 90 percent and executing targeted shard reroutes across 12 priority indices instead of purging historical index data.\n\nInstruct the search team to monitor replica recovery across 60 background shard transfers, and write 5 unit tests confirming that cluster allocation recovers green status without manual reroute overrides."
    },

    # Sample 20: AWS EBS IOPS Throttling and Database Checkpoint Stall
    {
        "raw_asr": "basically our database platform team resolved checkpoint stall spikes inside storage underscore scaler dot py buy analyzing cloud volume metrics during high write activity previously our core reporting database suffered query stalls and client timeout spikes exceeding forty five seconds across eight analytics dashboards when heavy checkpoints exhausted disk io credits um the infrastructure engineers examined cloud storage telemetry finding that gp three volumes suffered storage throttling which dropped disk throughput down into one thousand io operations per second across four storage volumes uh the team eliminated database stalls buy increasing baseline provisioned io capacity from three thousand io operations per second up into twelve thousand io operations per second and raising throughput towards five hundred megabytes per second across four volume arrays instead of upgrading database instance types okay so ask reliability engineers two run checkpoint stress tests with fifteen thousand concurrent write operations and right four unit tests validating that disk queue latency remains below five milliseconds during checkpoint flushes",
        "refined_text": "Our database platform team resolved checkpoint stall spikes inside storage_scaler.py by analyzing cloud volume metrics during high write activity. Previously our core reporting database suffered query stalls and client timeout spikes exceeding 45 seconds across 8 analytics dashboards when heavy checkpoints exhausted disk IO credits.\n\nThe infrastructure engineers examined cloud storage telemetry, finding that GP3 volumes suffered storage throttling which dropped disk throughput down into 1000 IO operations per second across 4 storage volumes. The team eliminated database stalls by increasing baseline provisioned IO capacity from 3000 IO operations per second up into 12000 IO operations per second and raising throughput towards 500 megabytes per second across 4 volume arrays instead of upgrading database instance types.\n\nAsk reliability engineers to run checkpoint stress tests with 15000 concurrent write operations, and write 4 unit tests validating that disk queue latency remains below 5 milliseconds during checkpoint flushes."
    }
]

# Validation checks
print(f"Total samples: {len(batch)}")
assert len(batch) == 20, f"Expected 20 samples, got {len(batch)}"

# Check evaluation set leakage
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e.get("raw_asr", e.get("input", "")).strip().lower() for e in eval_data}
    eval_refs = {e.get("refined_text", e.get("output", "")).strip() for e in eval_data}
    for idx, s in enumerate(batch, 1):
        raw_test = s["raw_asr"].strip().lower()
        ref_test = s["refined_text"].strip()
        if raw_test in eval_raws:
            raise ValueError(f"Sample {idx} raw_asr leaked into evaluation set!")
        if ref_test in eval_refs:
            raise ValueError(f"Sample {idx} refined_text leaked into evaluation set!")
    print("Eval leakage check passed: 0 leaks.")

# Check individual validation and cleaning
for idx, s in enumerate(batch, 1):
    is_valid, reason = validate_pair(s)
    if not is_valid:
        raise ValueError(f"Sample {idx} failed validate_pair: {reason}")
    res, status = clean_sample(s["raw_asr"], s["refined_text"])
    if status != "kept":
        raise ValueError(f"Sample {idx} failed clean_sample: {status}")

print("Individual validation & cleaner checks passed: 20/20 kept.")

# Batch validation
batch_valid, batch_reason, tier_counts = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
if not batch_valid:
    raise ValueError(f"Batch validation failed: {batch_reason}")

print(f"Batch validation passed: {batch_reason}")
print(f"Tier counts: {tier_counts}")

# Save verified batch to scratch/subagent_batch_115.json
output_path = Path("scratch/subagent_batch_115.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"Saved {len(batch)} verified samples to {output_path}")
