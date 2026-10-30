import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
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

# Domain 4: Incident Management & Live Troubleshooting RCA
# Batch 185 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Active gerund ("by <action>"). Zero backticks.
    # Underscore identifiers, NO dotted filenames.
    # At least 3 noise layers active (target 5-6).
    # =========================================================================

    # Sample 1: RabbitMQ queue mirroring unsynchronized mirrors
    {
        "raw_asr": "basically synchronizat r p c queue mirroring buffers buy purging queue underscore mirrors on broker knowed instances instead",
        "refined_text": "Synchronize RPC queue mirroring buffers by purging queue_mirrors on broker node instances instead."
    },

    # Sample 2: OpenTelemetry collector memory queue limit
    {
        "raw_asr": "um allocat c p u worker queue buffers buy tuning memory underscore limiter on collector knowed daemons instead",
        "refined_text": "Allocate CPU worker queue buffers by tuning memory_limiter on collector node daemons instead."
    },

    # Sample 3: CoreDNS caching parameters
    {
        "raw_asr": "so basically configur cube let dns caching parameters buy tuning cache underscore ttl on cluster knowed pods instead",
        "refined_text": "Configure kubelet DNS caching parameters by tuning cache_ttl on cluster node pods instead."
    },

    # Sample 4: Envoy TLS certificate validation timers
    {
        "raw_asr": "uh initializ r p c certificate validation timers buy tuning cert underscore refresh on envoy knowed proxies instead",
        "refined_text": "Initialize RPC certificate validation timers by tuning cert_refresh on Envoy node proxies instead."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Zero backticks. Zero purpose patterns. At least 4 noise layers active (target 6).
    # =========================================================================

    # Sample 5: Kafka broker partition replication lag during disk controller failure
    {
        "raw_asr": "um our kafka streaming cluster suffered consumer lag surges after sixteen knowed brokers missed follower fetch requests across twenty seconds wait forty seconds instead basically incident responders stabilized cluster operat buy tuning replica underscore lag buy passing dash dash max partition fetch bytes into broker configur settings while reliability engineers right two c p u fetch monitors",
        "refined_text": "Our Kafka streaming cluster suffered consumer lag surges after 16 node brokers missed follower fetch requests across 40 seconds instead.\n\nIncident responders stabilized cluster operations by tuning replica_lag by passing --max-partition-fetch-bytes into broker configuration settings while reliability engineers write 2 CPU fetch monitors."
    },

    # Sample 6: RabbitMQ memory alarm blocking publisher connections
    {
        "raw_asr": "basically our message broker tier halted client publishing when twelve knowed queues hit high watermark alarms across fifteen seconds wait thirty seconds instead um platform engineers restored queue communicat buy adjusting disk underscore free underscore limit buy passing dash dash vm memory high watermark into rabbitmq configur manifests while systems engineers right two r p c connection monitors",
        "refined_text": "Our message broker tier halted client publishing when 12 node queues hit high watermark alarms across 30 seconds instead.\n\nPlatform engineers restored queue communication by adjusting disk_free_limit by passing --vm-memory-high-watermark into RabbitMQ configuration manifests while systems engineers write 2 RPC connection monitors."
    },

    # Sample 7: OpenSearch cluster degraded state after GC pause
    {
        "raw_asr": "um our analytics cluster entered degraded state when ten knowed data nodes missed master ping intervals across twenty seconds wait fifty seconds instead basically search operators stabilized cluster synchronizat buy adjusting search underscore queue buy passing dash dash cluster routing allocation into opensearch configur manifests while infrastructure engineers right two wi re shark latency probes",
        "refined_text": "Our analytics cluster entered degraded state when 10 node data nodes missed master ping intervals across 50 seconds instead.\n\nSearch operators stabilized cluster synchronization by adjusting search_queue by passing --cluster-routing-allocation into OpenSearch configuration manifests while infrastructure engineers write 2 Wireshark latency probes."
    },

    # Sample 8: Envoy sidecar circuit breaker tripping under upstream latency
    {
        "raw_asr": "basically our service mesh proxies returned status five zero three errors when fourteen knowed sidecars exhausted pending request pools across ten seconds wait thirty seconds instead um site reliability engineers restored proxy communicat buy increasing max underscore pending underscore requests buy passing dash dash circuit breakers into envoy configur manifests while network engineers right two a sink proxy probes",
        "refined_text": "Our service mesh proxies returned status 503 errors when 14 node sidecars exhausted pending request pools across 30 seconds instead.\n\nSite reliability engineers restored proxy communication by increasing max_pending_requests by passing --circuit-breakers into Envoy configuration manifests while network engineers write 2 async proxy probes."
    },

    # Sample 9: PostgreSQL connection pooler PgBouncer client timeout storm
    {
        "raw_asr": "um our database proxy tier rejected incoming web connections when twenty knowed clients exhausted server connection pools across twenty seconds wait forty seconds instead basically database administrators restored pool operat buy expanding pool underscore size buy passing dash dash default pool size into pgbouncer configur parameters while site reliability engineers right two post gres query probes",
        "refined_text": "Our database proxy tier rejected incoming web connections when 20 node clients exhausted server connection pools across 40 seconds instead.\n\nDatabase administrators restored pool operations by expanding pool_size by passing --default-pool-size into PgBouncer configuration parameters while site reliability engineers write 2 Postgres query probes."
    },

    # Sample 10: Kubernetes etcd database space alarm during snapshot compaction failure
    {
        "raw_asr": "basically our control plane cluster rejected resource write mutations when eight knowed masters hit storage quota alarms across thirty seconds wait sixty seconds instead um cluster administrators restored storage allocat buy adjusting quota underscore backend underscore bytes buy passing dash dash auto compaction retention into cube let configur settings while systems engineers right two cube ctl status probes",
        "refined_text": "Our control plane cluster rejected resource write mutations when 8 node masters hit storage quota alarms across 60 seconds instead.\n\nCluster administrators restored storage allocation by adjusting quota_backend_bytes by passing --auto-compaction-retention into kubelet configuration settings while systems engineers write 2 kubectl status probes."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklist stereotypes.
    # Spoken engineer narration. Zero backticks. Zero purpose patterns.
    # At least 4 noise layers active (target 6 layers active).
    # =========================================================================

    # Sample 11: Ceph storage cluster OSD peering deadlock and write stall
    {
        "raw_asr": "basically during storage disk maintenance our distributed ceph storage cluster suffered block device write stalls when osd peering operations delayed heartbeat acknowledgments across twelve knowed storage hosts wait eighteen storage hosts instead um synchronous peering transactions blocked client io requests buy driving storage c p u utiliz to ninety one percent across thirty six osd daemons p ninety five block write latency surged from four milliseconds up through two four zero zero milliseconds buy stalling forty percent of persistent volume write queries incident responders isolated the underlying defect inside ceph underscore cluster dot conf buy analyzing peering queues across slash var slash log storage reliability engineers restored cluster synchronizat buy adjusting osd underscore heartbeat underscore interval buy passing dash dash osd max backfills into daemon configur parameters while systems administrators right three automated disk latency probes",
        "refined_text": "During storage disk maintenance, our distributed Ceph storage cluster suffered block device write stalls when OSD peering operations delayed heartbeat acknowledgments across 18 node storage hosts instead. Synchronous peering transactions blocked client IO requests by driving storage CPU utilization to 91 percent across 36 OSD daemons.\n\nP95 block write latency surged from 4 milliseconds up through 2400 milliseconds by stalling 40 percent of persistent volume write queries. Incident responders isolated the underlying defect inside ceph_cluster.conf by analyzing peering queues across /var/log.\n\nStorage reliability engineers restored cluster synchronization by adjusting osd_heartbeat_interval by passing --osd-max-backfills into daemon configuration parameters while systems administrators write 3 automated disk latency probes."
    },

    # Sample 12: HashiCorp Vault token lease revocation storm locking storage backend
    {
        "raw_asr": "um during credential lifecycle rotation our secret management cluster suffered authentication request timeouts when lease revocation tasks locked the storage backend across ten knowed vault instances wait sixteen vault instances instead basically bulk revocation workers blocked client authentication buy driving consul c p u utiliz to ninety four percent across twenty service containers p ninety nine token validation latency jumped from six milliseconds up through two eight zero zero milliseconds buy failing fifty percent of microservice r p c queries incident responders isolated the primary trigger inside vault underscore server dot conf buy reviewing storage locking traces across slash var slash log platform security engineers stabilized lease terminat buy adjusting max underscore lease underscore ttl buy passing dash dash max lease ttl into daemon configur settings while site reliability engineers right two synthetic token authentication probes",
        "refined_text": "During credential lifecycle rotation, our secret management cluster suffered authentication request timeouts when lease revocation tasks locked the storage backend across 16 node Vault instances instead. Bulk revocation workers blocked client authentication by driving Consul CPU utilization to 94 percent across 20 service containers.\n\nP99 token validation latency jumped from 6 milliseconds up through 2800 milliseconds by failing 50 percent of microservice RPC queries. Incident responders isolated the primary trigger inside vault_server.conf by reviewing storage locking traces across /var/log.\n\nPlatform security engineers stabilized lease termination by adjusting max_lease_ttl by passing --max-lease-ttl into daemon configuration settings while site reliability engineers write 2 synthetic token authentication probes."
    },

    # Sample 13: HAProxy dynamic backend health check flapping and connection queue spillover
    {
        "raw_asr": "basically during midday traffic peak our load balancing tier dropped incoming customer sessions when health check timeouts caused backend server flapping across fourteen knowed gateways wait twenty gateways instead um rapid state transitions depleted socket connections buy driving load balancer c p u utiliz to eighty nine percent across forty edge instances p ninety five proxy connection latency climbed from five milliseconds up through eighteen hundred milliseconds buy returning status five zero two errors across thirty thousand edge requests incident responders diagnosed the primary trigger inside haproxy underscore edge dot cfg buy inspecting wi re shark packet traces across slash etc network reliability engineers restored connection communicat buy tuning check underscore interval buy passing dash dash max conn into proxy configur parameters while infrastructure operators right two automated backend health probes",
        "refined_text": "During midday traffic peak, our load balancing tier dropped incoming customer sessions when health check timeouts caused backend server flapping across 20 node gateways instead. Rapid state transitions depleted socket connections by driving load balancer CPU utilization to 89 percent across 40 edge instances.\n\nP95 proxy connection latency climbed from 5 milliseconds up through 1800 milliseconds by returning status 502 errors across 30000 edge requests. Incident responders diagnosed the primary trigger inside haproxy_edge.cfg by inspecting Wireshark packet traces across /etc.\n\nNetwork reliability engineers restored connection communication by tuning check_interval by passing --max-conn into proxy configuration parameters while infrastructure operators write 2 automated backend health probes."
    },

    # Sample 14: Kubernetes CNI Calico BGP route reflector mesh connection drops
    {
        "raw_asr": "um during cluster node autoscaling our pod overlay network suffered intermittent packet drops when bgp peer sessions disconnected across twelve knowed worker hosts wait eighteen worker hosts instead basically routing table sync stalls halted inter pod packet forwarding buy driving node c p u utiliz to ninety three percent across thirty worker instances p ninety nine pod network latency surged from three milliseconds up through two two zero zero milliseconds buy failing twenty percent of internal r p c requests incident responders isolated the underlying defect inside calico underscore network dot yaml buy analyzing bgp routing logs across slash var slash log cluster network administrators restored routing synchronizat buy tuning bgp underscore keepalive buy passing dash dash node mesh into cube let configur manifests while site reliability engineers right two a sink network latency probes",
        "refined_text": "During cluster node autoscaling, our pod overlay network suffered intermittent packet drops when BGP peer sessions disconnected across 18 node worker hosts instead. Routing table sync stalls halted inter-pod packet forwarding by driving node CPU utilization to 93 percent across 30 worker instances.\n\nP99 pod network latency surged from 3 milliseconds up through 2200 milliseconds by failing 20 percent of internal RPC requests. Incident responders isolated the underlying defect inside calico_network.yaml by analyzing BGP routing logs across /var/log.\n\nCluster network administrators restored routing synchronization by tuning bgp_keepalive by passing --node-mesh into kubelet configuration manifests while site reliability engineers write 2 async network latency probes."
    },

    # Sample 15: ZooKeeper ephemeral node session expiration storm during JVM GC
    {
        "raw_asr": "basically during scheduled batch indexing our distributed coordination cluster lost leader leases when long garbage collection pauses triggered session expirations across eight knowed ensemble hosts wait fourteen ensemble hosts instead um cascading lease expirations caused storming client reconnects buy driving ensemble c p u utiliz to ninety two percent across twenty instances p ninety five coordination latency jumped from four milliseconds up through two six zero zero milliseconds buy triggering status five zero three errors across eight thousand consumer r p c queries incident responders isolated the primary trigger inside zookeeper underscore quorum dot cfg buy inspecting session expiration logs across slash proc platform engineers stabilized session initializ buy increasing max underscore session underscore timeout buy passing dash dash sync limit into server configur files while infrastructure reliability engineers right two ensemble health monitors",
        "refined_text": "During scheduled batch indexing, our distributed coordination cluster lost leader leases when long garbage collection pauses triggered session expirations across 14 node ensemble hosts instead. Cascading lease expirations caused storming client reconnects by driving ensemble CPU utilization to 92 percent across 20 instances.\n\nP95 coordination latency jumped from 4 milliseconds up through 2600 milliseconds by triggering status 503 errors across 8000 consumer RPC queries. Incident responders isolated the primary trigger inside zookeeper_quorum.cfg by inspecting session expiration logs across /proc.\n\nPlatform engineers stabilized session initialization by increasing max_session_timeout by passing --sync-limit into server configuration files while infrastructure reliability engineers write 2 ensemble health monitors."
    },

    # Sample 16: MongoDB replica set election pause and write concern timeout
    {
        "raw_asr": "um during database replica set maintenance our document storage tier suffered unacknowledged write timeouts when network packet drops caused election pauses across ten knowed replica members wait sixteen replica members instead basically primary step down events stalled incoming document updates buy driving database c p u utiliz to ninety percent across twenty four database instances p ninety nine document commit latency climbed from six milliseconds up through two five zero zero milliseconds buy generating status five zero four gateway timeouts across forty downstream services incident responders diagnosed the primary trigger inside mongodb underscore replica dot conf buy evaluating replication oplog traces across slash var slash log database platform engineers restored replica synchronizat buy adjusting election underscore timeout buy passing dash dash repl set into mongod configur settings while site reliability engineers right two r p c replica delay probes",
        "refined_text": "During database replica set maintenance, our document storage tier suffered unacknowledged write timeouts when network packet drops caused election pauses across 16 node replica members instead. Primary step-down events stalled incoming document updates by driving database CPU utilization to 90 percent across 24 database instances.\n\nP99 document commit latency climbed from 6 milliseconds up through 2500 milliseconds by generating status 504 gateway timeouts across 40 downstream services. Incident responders diagnosed the primary trigger inside mongodb_replica.conf by evaluating replication oplog traces across /var/log.\n\nDatabase platform engineers restored replica synchronization by adjusting election_timeout by passing --repl-set into mongod configuration settings while site reliability engineers write 2 RPC replica delay probes."
    },

    # Sample 17: Memcached slab allocation eviction storm during cached payload increase
    {
        "raw_asr": "basically our distributed caching tier encountered severe hit rate degradation when increased payload sizes triggered aggressive slab evictions across twelve knowed cache hosts wait twenty cache hosts instead um rapid memory slab allocations exhausted available page buffers buy driving cache c p u utiliz to ninety four percent across thirty instances p ninety five cache lookup latency climbed from two milliseconds up through sixteen hundred milliseconds buy overwhelming primary post gres databases with fifty thousand fallback queries incident responders isolated the underlying defect inside memcached underscore server dot conf buy reviewing slab allocation metrics across slash proc site reliability engineers stabilized cache allocat buy tuning slab underscore factor buy passing dash dash max memory into cache daemon configur parameters while performance engineers right two r p c hit rate probes",
        "refined_text": "Our distributed caching tier encountered severe hit rate degradation when increased payload sizes triggered aggressive slab evictions across 20 node cache hosts instead. Rapid memory slab allocations exhausted available page buffers by driving cache CPU utilization to 94 percent across 30 instances.\n\nP95 cache lookup latency climbed from 2 milliseconds up through 1600 milliseconds by overwhelming primary Postgres databases with 50000 fallback queries. Incident responders isolated the underlying defect inside memcached_server.conf by reviewing slab allocation metrics across /proc.\n\nSite reliability engineers stabilized cache allocation by tuning slab_factor by passing --max-memory into cache daemon configuration parameters while performance engineers write 2 RPC hit rate probes."
    },

    # Sample 18: ClickHouse MergeTree background mutation thread deadlock during ALTER UPDATE
    {
        "raw_asr": "um during columnar analytical processing our clickhouse reporting cluster encountered table insert rejections when concurrent table mutations exhausted background merge threads across eight knowed analytical hosts wait fourteen analytical hosts instead basically accumulated part mutations halted data ingestion buy driving server c p u utiliz to ninety one percent across twenty database instances p ninety nine ingestion commit latency spiked from five milliseconds up through two seven zero zero milliseconds buy dropping thirty percent of telemetry batch write requests incident responders diagnosed the primary trigger inside clickhouse underscore server dot conf buy analyzing part merge logs across slash var slash log data platform engineers restored table operat buy adjusting max underscore parts underscore in underscore total buy passing dash dash max insert block size into clickhouse configur parameters while systems reliability engineers right two a sink merge queue probes",
        "refined_text": "During columnar analytical processing, our ClickHouse reporting cluster encountered table insert rejections when concurrent table mutations exhausted background merge threads across 14 node analytical hosts instead. Accumulated part mutations halted data ingestion by driving server CPU utilization to 91 percent across 20 database instances.\n\nP99 ingestion commit latency spiked from 5 milliseconds up through 2700 milliseconds by dropping 30 percent of telemetry batch write requests. Incident responders diagnosed the primary trigger inside clickhouse_server.conf by analyzing part merge logs across /var/log.\n\nData platform engineers restored table operations by adjusting max_parts_in_total by passing --max-insert-block-size into ClickHouse configuration parameters while systems reliability engineers write 2 async merge queue probes."
    },

    # Sample 19: PostgreSQL WAL archive failure causing disk saturation on primary database
    {
        "raw_asr": "basically during morning transactional spikes our primary postgresql cluster halted write operations when wal archiving scripts failed storage uploads across six knowed standby replicas wait twelve standby replicas instead um accumulated transaction log files saturated the primary disk volume buy driving database c p u utiliz to ninety two percent across twenty instances p ninety five transaction commit latency jumped from four milliseconds up through two three zero zero milliseconds buy blocking forty thousand customer purchase queries incident responders isolated the underlying defect inside postgresql underscore cluster dot conf buy inspecting archive error logs across slash var slash log database administrators restored wal synchronizat buy adjusting archive underscore timeout buy passing dash dash archive command into post gres configur files while site reliability engineers right two cube ctl disk usage probes",
        "refined_text": "During morning transactional spikes, our primary PostgreSQL cluster halted write operations when WAL archiving scripts failed storage uploads across 12 node standby replicas instead. Accumulated transaction log files saturated the primary disk volume by driving database CPU utilization to 92 percent across 20 instances.\n\nP95 transaction commit latency jumped from 4 milliseconds up through 2300 milliseconds by blocking 40000 customer purchase queries. Incident responders isolated the underlying defect inside postgresql_cluster.conf by inspecting archive error logs across /var/log.\n\nDatabase administrators restored WAL synchronization by adjusting archive_timeout by passing --archive-command into Postgres configuration files while site reliability engineers write 2 kubectl disk usage probes."
    },

    # Sample 20: CoreDNS DNS resolution loop causing upstream UDP socket exhaustion
    {
        "raw_asr": "um during service mesh traffic rerouting our cluster dns resolvers dropped upstream lookups when recursive forwarding loops exhausted udp sockets across ten knowed resolver pods wait sixteen resolver pods instead basically recursive query storms saturated socket buffers buy driving coredns c p u utiliz to ninety three percent across thirty instances p ninety nine name resolution latency climbed from two milliseconds up through nineteen hundred milliseconds buy triggering status five zero four gateway timeouts across sixty downstream services incident responders diagnosed the primary trigger inside coredns underscore corefile dot conf buy tracking socket contention traces across slash proc platform network engineers restored query communicat buy adjusting forward underscore timeout buy passing dash dash upstream resolvers into cube let configur manifests while site reliability engineers right two wi re shark query monitors",
        "refined_text": "During service mesh traffic rerouting, our cluster DNS resolvers dropped upstream lookups when recursive forwarding loops exhausted UDP sockets across 16 node resolver pods instead. Recursive query storms saturated socket buffers by driving CoreDNS CPU utilization to 93 percent across 30 instances.\n\nP99 name resolution latency climbed from 2 milliseconds up through 1900 milliseconds by triggering status 504 gateway timeouts across 60 downstream services. Incident responders diagnosed the primary trigger inside coredns_corefile.conf by tracking socket contention traces across /proc.\n\nPlatform network engineers restored query communication by adjusting forward_timeout by passing --upstream-resolvers into kubelet configuration manifests while site reliability engineers write 2 Wireshark query monitors."
    }
]

def main():
    print(f"Total samples defined: {len(samples)}")
    
    # Check eval set leakage
    leakage = False
    for i, s in enumerate(samples):
        r = s["raw_asr"].strip().lower()
        rf = s["refined_text"].strip()
        if r in eval_raws:
            print(f"ERROR: Sample {i+1} raw_asr leaks into eval set!")
            leakage = True
        if rf in eval_refs:
            print(f"ERROR: Sample {i+1} refined_text leaks into eval set!")
            leakage = True
    if not leakage:
        print("PASS: Eval leakage check clean (0 overlaps).")
    else:
        sys.exit(1)

    # Validate each pair
    all_valid = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []

    for i, s in enumerate(samples):
        v_ok, v_reason = validate_pair(s, min_noise_layers=4)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])
        layers = count_active_noise_layers(s["raw_asr"])
        layer_count = get_noise_layer_count(s["raw_asr"])
        layer_counts.append(layer_count)
        words = len(s["refined_text"].split())

        if words < 25:
            tier_counts["short"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', s["refined_text"]) if sent.strip()]
            if len(sentences) != 1:
                print(f"Sample {i+1}: Sentence count mismatch for short tier: {len(sentences)} != 1")
                all_valid = False
            if "\n" in s["refined_text"]:
                print(f"Sample {i+1}: Newline in short tier")
                all_valid = False
        elif words < 90:
            tier_counts["medium"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', s["refined_text"]) if sent.strip()]
            if not (1 <= len(sentences) <= 3):
                print(f"Sample {i+1}: Sentence count mismatch for medium tier: {len(sentences)}")
                all_valid = False
            if "\n\n" not in s["refined_text"]:
                print(f"Sample {i+1}: Missing \\n\\n in medium tier")
                all_valid = False
        else:
            tier_counts["long"] += 1
            if "\n\n" not in s["refined_text"]:
                print(f"Sample {i+1}: Missing \\n\\n in long tier")
                all_valid = False
        
        status = "OK" if (v_ok and c_reason == "kept") else "FAIL"
        if status == "FAIL":
            all_valid = False
            print(f"Sample {i+1} (tier: {words} words, layers: {layer_count}): {status}")
            if not v_ok:
                print(f"  Validator: {v_reason}")
            if c_reason != "kept":
                print(f"  Cleaner: {c_reason}")
        else:
            active = [k for k, v in layers.items() if v]
            print(f"Sample {i+1:02d} (tier words: {words:3d}, layers: {layer_count} [{', '.join(active)}]): PASS")

    # Batch validation
    batch_ok, batch_reason, metrics = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
    print("\nBatch Validation Result:")
    print("  Status:", "PASS" if batch_ok else "FAIL")
    print("  Reason:", batch_reason)
    print("  Tier Counts:", tier_counts)
    print("  Average Noise Layers:", f"{sum(layer_counts)/len(layer_counts):.2f}")
    print("  Metrics:", json.dumps(metrics, indent=2))

    if all_valid and batch_ok:
        out_path = Path("scratch/subagent_batch_185.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"\nWROTE {len(samples)} verified samples to {out_path}")
    else:
        print("\nCANNOT WRITE: Fix errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
