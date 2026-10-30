import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
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

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. 0 newlines. Max 1 cut-word. Noise layers >= 3.
    # =========================================================================

    # Sample 1: RPC multiplexing / connection limits (RFC 201)
    # Layers: homophone (buy, knowed), tool (r p c), syntax (underscore), disfluency (um), cut-word (configur) -> 5 layers
    {
        "raw_asr": "um technical r f c two zero one evaluates r p c multiplexing buy configur max underscore streams across eight knowed workers",
        "refined_text": "Technical RFC 201 evaluates RPC multiplexing by configuring max_streams across 8 node workers."
    },

    # Sample 2: Async event consumer deduplication leases (ADR 204)
    # Layers: homophone (buy, four), tool (a sink), syntax (underscore), disfluency (uh), cut-word (terminat) -> 5 layers
    {
        "raw_asr": "uh architectural decision record two zero four mandates a sink lease renewal buy terminat stale consumer leases after four retries",
        "refined_text": "Architectural Decision Record 204 mandates async lease renewal by terminating stale consumer leases after 4 retries."
    },

    # Sample 3: Postgres write-ahead log buffer sizing (RFC 208)
    # Layers: homophone (buy, four), tool (post gres), syntax (underscore), disfluency (basically), cut-word (allocat) -> 5 layers
    {
        "raw_asr": "basically technical r f c two zero eight restricts post gres replication lag buy allocat shared underscore buffers across sixteen database shards",
        "refined_text": "Technical RFC 208 restricts Postgres replication lag by allocating shared_buffers across 16 database shards."
    },

    # Sample 4: CPU core pin affinity and thread masks (ADR 212)
    # Layers: homophone (buy, knowed), tool (c p u), syntax (underscore), disfluency (you know), cut-word (communicat) -> 5 layers
    {
        "raw_asr": "you know architectural decision record two one two standardizes c p u pin affinity buy communicat task underscore masks across eight knowed sockets",
        "refined_text": "Architectural Decision Record 212 standardizes CPU pin affinity by communicating task_masks across 8 node sockets."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 sentences. Natural \n\n breaks. Max \n\n: words // 25. Noise layers >= 4.
    # =========================================================================

    # Sample 5: Distributed lock manager ADR: Redis Redlock vs Chubby-style consensus lock with etcd
    # Layers: homophone (buy, knowed, four), tool (r p c), syntax (underscore, slash), correction (wait switch to... instead), disfluency (um), cut-word (arbitrat) -> 6 layers
    {
        "raw_asr": "um our distributed coordination architecture decision record evaluated multi master redis locking across twelve knowed instances wait switch to etcd consensus leases instead basically storage engines arbitrat lock ownership buy verifying lease underscore id tokens inside slash var slash log slash locks dot log four twenty r p c clients",
        "refined_text": "Our distributed coordination architecture decision record evaluated multi-master Redis locking across 12 node instances, switching to etcd consensus leases instead.\n\nStorage engines arbitrate lock ownership by verifying lease_id tokens inside /var/log/locks.log for 20 RPC clients."
    },

    # Sample 6: Distributed tracing context propagation RFC: W3C Trace Context vs B3 propagation headers
    # Layers: homophone (buy, knowed, four), tool (c p u), syntax (underscore, slash), correction (wait choose... instead), disfluency (uh), cut-word (synchronizat) -> 6 layers
    {
        "raw_asr": "uh technical r f c seventy four evaluated legacy b three baggage headers across thirty microservices wait choose w three c trace context standards instead ingress gateways synchronizat distributed traces buy injecting trace underscore parent headers inside slash etc slash proxy slash tracing dot conf four sixteen c p u worker knowed pools",
        "refined_text": "Technical RFC 74 evaluated legacy B3 baggage headers across 30 microservices, choosing W3C trace context standards instead.\n\nIngress gateways synchronize distributed traces by injecting trace_parent headers inside /etc/proxy/tracing.conf for 16 CPU worker node pools."
    },

    # Sample 7: Consensus read optimization ADR: Quorum reads vs Leader lease reads in Raft
    # Layers: homophone (buy, knowed, four), tool (r p c), syntax (underscore, slash), correction (wait select... instead), disfluency (basically), cut-word (configur) -> 6 layers
    {
        "raw_asr": "basically our consensus architecture decision record evaluated quorum read heartbeats across twenty four knowed replicas wait select leader lease reads instead consensus followers configur local read verification buy checking leader underscore lease timers inside slash etc slash raft slash cluster dot conf four thirty two r p c gateway services",
        "refined_text": "Our consensus architecture decision record evaluated quorum read heartbeats across 24 node replicas, selecting leader lease reads instead.\n\nConsensus followers configure local read verification by checking leader_lease timers inside /etc/raft/cluster.conf for 32 RPC gateway services."
    },

    # Sample 8: API Gateway rate limiting algorithm RFC: Sliding window counter vs Token bucket
    # Layers: homophone (buy, knowed, four), tool (c p u), syntax (underscore, slash), correction (wait change that to... instead), disfluency (um), cut-word (terminat) -> 6 layers
    {
        "raw_asr": "um our edge traffic technical r f c evaluated sliding window counters across forty gateway pods wait change that to token bucket rate limiters instead edge proxies terminat abusive burst requests buy enforcing bucket underscore capacity limits inside slash opt slash envoy slash ratelimit dot conf four fifty c p u knowed workers",
        "refined_text": "Our edge traffic technical RFC evaluated sliding window counters across 40 gateway pods, changing that to token bucket rate limiters instead.\n\nEdge proxies terminate abusive burst requests by enforcing bucket_capacity limits inside /opt/envoy/ratelimit.conf for 50 CPU node workers."
    },

    # Sample 9: Event stream storage compaction ADR: Key-based tombstone compaction vs TTL retention in Kafka topics
    # Layers: homophone (buy, knowed, four), tool (a sink), syntax (underscore, slash), correction (wait adopt... instead), disfluency (you know), cut-word (deduplicat) -> 6 layers
    {
        "raw_asr": "you know our event streaming architecture decision record evaluated time based segment deletion across twenty broker knowed instances wait adopt key tombstone compaction instead a sink ingestion brokers deduplicat event stream state buy persisting segment underscore index checkpoints inside slash var slash kafka slash storage dot conf four sixty partitions",
        "refined_text": "Our event streaming architecture decision record evaluated time-based segment deletion across 20 broker node instances, adopting key tombstone compaction instead.\n\nAsync ingestion brokers deduplicate event stream state by persisting segment_index checkpoints inside /var/kafka/storage.conf for 60 partitions."
    },

    # Sample 10: Relational database horizontal scaling RFC: Application-level sharding vs Citus distributed tables for Postgres
    # Layers: homophone (buy, knowed, four), tool (post gres), syntax (underscore, slash), correction (wait switch to... instead), disfluency (uh), cut-word (allocat) -> 6 layers
    {
        "raw_asr": "uh our database architecture working group evaluated application sharding logic across thirty two customer accounts wait switch to distributed table partitions instead database coordinators allocat tenant records buy routing partition underscore key ranges inside slash etc slash post gres slash sharding dot conf four sixteen knowed clusters",
        "refined_text": "Our database architecture working group evaluated application sharding logic across 32 customer accounts, switching to distributed table partitions instead.\n\nDatabase coordinators allocate tenant records by routing partition_key ranges inside /etc/postgres/sharding.conf for 16 node clusters."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph with \n\n. Zero numbered checklists. Spoken engineer narration.
    # Noise layers >= 4 (target 6).
    # =========================================================================

    # Sample 11: Multi-Raft consensus partitioning trade-offs (RFC 301)
    {
        "raw_asr": "our distributed storage working group evaluated consensus scaling strategies across sixty four storage knowed instances buy comparing a single global raft ring against multi raft consensus groups our initial deployment ran a single global consensus ring across thirty two knowed servers where all partition metadata updates were serialized buy a single leader during high throughput ingestion bursts of seventy thousand write transactions per second the global consensus leader experienced severe r p c thread starvation and heartbeats timed out buy triggering spurious leader elections across the cluster wait we rejected the single raft architecture and selected multi raft partitioning instead um technical r f c three zero one approves multi raft partitioning buy dividing the key range into independent consensus ranges consensus daemons inspect range underscore descriptor metadata buy configur background heartbeat batches inside slash etc slash storage slash raft dot conf four twenty four c p u cores when an individual range experiences write skew consensus workers arbitrat leadership locally buy isolating state transitions across thirty two independent knowed groups chaos testing simulating twenty second network cuts across two regions proved that multi raft maintained steady p ninety nine write latency below twelve milliseconds across eighty thousand transactional operations",
        "refined_text": "Our distributed storage working group evaluated consensus scaling strategies across 64 storage node instances by comparing a single global Raft ring against multi-Raft consensus groups. Our initial deployment ran a single global consensus ring across 32 node servers, where all partition metadata updates were serialized by a single leader. During high-throughput ingestion bursts of 70000 write transactions per second, the global consensus leader experienced severe RPC thread starvation and heartbeats timed out, triggering spurious leader elections across the cluster, which led us to reject the single Raft architecture and select multi-Raft partitioning instead.\n\nTechnical RFC 301 approves multi-Raft partitioning by dividing the key range into independent consensus ranges. Consensus daemons inspect range_descriptor metadata by configuring background heartbeat batches inside /etc/storage/raft.conf for 24 CPU cores. When an individual range experiences write skew, consensus workers arbitrate leadership locally by isolating state transitions across 32 independent node groups. Chaos testing simulating 20 second network cuts across 2 regions proved that multi-Raft maintained steady P99 write latency below 12 milliseconds across 80000 transactional operations."
    },

    # Sample 12: Distributed Cache Invalidation Architecture (ADR 305)
    {
        "raw_asr": "our caching architecture committee authored an architecture decision record evaluating cache consistency models across eighty microservices our legacy deployment implemented two phase synchronous write through caching where database writers updated both the cache and post gres in a single transaction during peak traffic surges synchronous two phase commits increased p ninety nine write latency from twenty milliseconds up into two hundred milliseconds because slow cache replicas held database row locks buy blocking concurrent order checkouts wait we discarded synchronous write through caching and selected asynchronous write ahead log tailing with cache aside invalidation instead uh architectural decision record three zero five mandates log based cache invalidation buy capturing database changes directly through replication streams cache invalidation workers inspect commit underscore log offsets buy synchronizat cache evictions inside slash opt slash cache slash invalidator dot py four forty knowed instances when database transactions commit invalidators publish lightweight invalidation tokens buy terminat stale cache keys across sixteen c p u worker pools stress testing across sixty storage knowed servers demonstrated ninety nine point nine percent cache consistency while reducing p ninety nine write latency down into fifteen milliseconds across fifty thousand order operations",
        "refined_text": "Our caching architecture committee authored an architecture decision record evaluating cache consistency models across 80 microservices. Our legacy deployment implemented two-phase synchronous write-through caching, where database writers updated both the cache and Postgres in a single transaction. During peak traffic surges synchronous two-phase commits increased P99 write latency from 20 milliseconds up into 200 milliseconds because slow cache replicas held database row locks, blocking concurrent order checkouts, leading us to discard synchronous write-through caching and select asynchronous write-ahead log tailing with cache-aside invalidation instead.\n\nArchitectural Decision Record 305 mandates log-based cache invalidation by capturing database changes directly through replication streams. Cache invalidation workers inspect commit_log offsets by synchronizing cache evictions inside /opt/cache/invalidator.py for 40 node instances. When database transactions commit, invalidators publish lightweight invalidation tokens by terminating stale cache keys across 16 CPU worker pools. Stress testing across 60 storage node servers demonstrated 99.9 percent cache consistency while reducing P99 write latency down into 15 milliseconds across 50000 order operations."
    },

    # Sample 13: Service Mesh Data Plane Ingress Routing (RFC 312)
    {
        "raw_asr": "our infrastructure platforms guild authored a technical r f c evaluating data plane routing mechanisms across one hundred microservices our baseline architecture routed all service traffic through user space envoy sidecar proxies deployed buy cube ctl across sixty worker knowed servers during benchmark evaluations with one hundred twenty thousand requests per second each network packet incurred four user space context switches buy consuming thirty five percent of total c p u capacity on proxy overhead alone wait we rejected user space sidecar proxying and adopted kernel e b p f socket redirection instead basically technical r f c three one two standardizes e b p f sockops redirection buy bypassing tcp stack traversals kernel programs inspect socket underscore cookie metadata buy configur direct socket routing inside slash etc slash ebpf slash router dot conf four twenty four c p u cores when services communicat over local sockets the kernel redirects packets directly between socket buffers buy terminat intermediate network hops latency profiling across forty cluster knowed instances confirmed that e b p f redirection reduced p ninety nine latency buy forty five percent while freeing sixteen c p u cores across each host machine",
        "refined_text": "Our infrastructure platforms guild authored a technical RFC evaluating data plane routing mechanisms across 100 microservices. Our baseline architecture routed all service traffic through user-space Envoy sidecar proxies deployed by kubectl across 60 worker node servers. During benchmark evaluations with 120000 requests per second, each network packet incurred 4 user-space context switches by consuming 35 percent of total CPU capacity on proxy overhead alone, leading us to reject user-space sidecar proxying and adopt kernel eBPF socket redirection instead.\n\nTechnical RFC 312 standardizes eBPF sockops redirection by bypassing TCP stack traversals. Kernel programs inspect socket_cookie metadata by configuring direct socket routing inside /etc/ebpf/router.conf for 24 CPU cores. When services communicate over local sockets, the kernel redirects packets directly between socket buffers by terminating intermediate network hops. Latency profiling across 40 cluster node instances confirmed that eBPF redirection reduced P99 latency by 45 percent, while freeing 16 CPU cores across each host machine."
    },

    # Sample 14: Storage Engine Compaction Trade-offs (ADR 318)
    {
        "raw_asr": "our database storage working group reviewed an architecture decision record evaluating log structured merge tree compaction strategies across forty eight knowed instances our initial storage tier ran size tiered compaction across twenty four knowed servers where storage files were merged into progressively larger tiers during peak telemetry ingestion of ninety thousand writes per second size tiered compaction triggered massive disk write stalls buy requiring fifty percent free disk headroom during compaction merges this write amplification saturated solid state disk write limits and spiked write latencies from twelve milliseconds up into one hundred sixty milliseconds wait we discarded size tiered compaction and selected leveled compaction instead um architectural decision record three one eight mandates leveled compaction buy organizing immutable data into fixed sixty four megabyte files arranged across seven levels compaction threads inspect table underscore level markers buy allocat background merge tasks inside slash opt slash db slash compaction dot py four sixteen c p u cores when level zero exceeds four files compaction daemons merge overlapping key ranges into level one buy terminat superseded record keys production testing across thirty two storage knowed instances confirmed that leveled compaction reduced write amplification from twenty eight down into eight while maintaining stable p ninety nine latency below sixteen milliseconds",
        "refined_text": "Our database storage working group reviewed an architecture decision record evaluating log-structured merge-tree compaction strategies across 48 node instances. Our initial storage tier ran size-tiered compaction across 24 node servers, where storage files were merged into progressively larger tiers. During peak telemetry ingestion of 90000 writes per second, size-tiered compaction triggered massive disk write stalls by requiring 50 percent free disk headroom during compaction merges. This write amplification saturated solid-state disk write limits and spiked write latencies from 12 milliseconds up into 160 milliseconds, leading us to discard size-tiered compaction and select leveled compaction instead.\n\nArchitectural Decision Record 318 mandates leveled compaction by organizing immutable data into fixed 64 megabyte files arranged across 7 levels. Compaction threads inspect table_level markers by allocating background merge tasks inside /opt/db/compaction.py for 16 CPU cores. When Level 0 exceeds 4 files, compaction daemons merge overlapping key ranges into Level 1 by terminating superseded record keys. Production testing across 32 storage node instances confirmed that leveled compaction reduced write amplification from 28 down into 8, while maintaining stable P99 latency below 16 milliseconds."
    },

    # Sample 15: Event Sourcing & CQRS Snapshotting Frequency (RFC 325)
    {
        "raw_asr": "our banking architecture council evaluated aggregate reconstruction performance in our event sourcing core across thirty two account services our legacy implementation replayed every historical domain event from event zero whenever an account aggregate was loaded from storage four active business accounts with over fifty thousand events event replay took more than six hundred milliseconds buy causing severe r p c read timeout cascades across upstream checkout services wait we rejected pure event replay and adopted periodic delta snapshotting instead basically technical r f c three two five mandates state snapshotting buy writing aggregate snapshots every one hundred domain events snapshot daemons inspect sequence underscore number markers buy configur fast delta projections inside slash app slash ledger slash snapshot dot py four twenty c p u knowed workers when loading an aggregate readers fetch the latest snapshot and replay only subsequent events buy terminat unnecessary historical scans stress testing across forty knowed servers reduced aggregate hydration time from six hundred milliseconds down into four milliseconds while preserving full audit history",
        "refined_text": "Our banking architecture council evaluated aggregate reconstruction performance in our event sourcing core across 32 account services. Our legacy implementation replayed every historical domain event from event 0 whenever an account aggregate was loaded from storage. For active business accounts with over 50000 events, event replay took more than 600 milliseconds by causing severe RPC read timeout cascades across upstream checkout services, leading us to reject pure event replay and adopt periodic delta snapshotting instead.\n\nTechnical RFC 325 mandates state snapshotting by writing aggregate snapshots every 100 domain events. Snapshot daemons inspect sequence_number markers by configuring fast delta projections inside /app/ledger/snapshot.py for 20 CPU node workers. When loading an aggregate, readers fetch the latest snapshot and replay only subsequent events by terminating unnecessary historical scans. Stress testing across 40 node servers reduced aggregate hydration time from 600 milliseconds down into 4 milliseconds, while preserving full audit history."
    },

    # Sample 16: Analytical Database Indexing Trade-offs (ADR 330)
    {
        "raw_asr": "our analytics infrastructure team evaluated indexing strategies four multi tenant query filtering across sixty four post gres analytical shards our existing schema maintained standard b tree indexes across eight separate filter columns which consumed over four hundred gigabytes of memory across thirty two knowed instances during complex multi predicate queries query planners performed multiple index scans followed buy expensive bitmap and merges buy exhausting memory limits and causing query latencies of four hundred fifty milliseconds wait we rejected wide b tree indexing and selected compressed roaring bitmap indexes instead uh architectural decision record three three zero mandates compressed bitmap indexing buy encoding sparse tenant identifiers into roaring bitmaps query engines inspect bitmap underscore chunk headers buy allocat bitmap union operations inside slash etc slash db slash indexes dot conf four twenty four c p u cores when executing multi column filter predicates the engine intersects bitmap containers directly in c p u registers buy terminat uncompressed index scans benchmark tests across forty analytical knowed instances demonstrated that roaring bitmaps reduced index memory consumption buy sixty five percent and accelerated query execution from four hundred fifty milliseconds down into eighteen milliseconds",
        "refined_text": "Our analytics infrastructure team evaluated indexing strategies for multi-tenant query filtering across 64 Postgres analytical shards. Our existing schema maintained standard B-tree indexes across 8 separate filter columns, which consumed over 400 gigabytes of memory across 32 node instances. During complex multi-predicate queries, query planners performed multiple index scans followed by expensive bitmap AND merges by exhausting memory limits and causing query latencies of 450 milliseconds, leading us to reject wide B-tree indexing and select compressed Roaring Bitmap indexes instead.\n\nArchitectural Decision Record 330 mandates compressed bitmap indexing by encoding sparse tenant identifiers into Roaring Bitmaps. Query engines inspect bitmap_chunk headers by allocating bitmap union operations inside /etc/db/indexes.conf for 24 CPU cores. When executing multi-column filter predicates, the engine intersects bitmap containers directly in CPU registers by terminating uncompressed index scans. Benchmark tests across 40 analytical node instances demonstrated that Roaring Bitmaps reduced index memory consumption by 65 percent and accelerated query execution from 450 milliseconds down into 18 milliseconds."
    },

    # Sample 17: Service Wire Protocols & Serialization Trade-offs (RFC 338)
    {
        "raw_asr": "our high throughput telemetry working group evaluated serialization wire formats across eighty microservices our initial data pipeline serialized all inter service messages using protocol buffers over synchronous r p c connections during peak message bursts of one hundred fifty thousand events per second c p u profiling showed that object allocation and serialization decoding consumed twenty two percent of total c p u cycles across sixty knowed workers wait we rejected standard protobuf decoding and adopted flatbuffers zero copy binary serialization instead um technical r f c three three eight mandates zero copy serialization buy encoding structured telemetry records directly into contiguous byte buffers consumer processes inspect message underscore offset headers buy configur memory mapped buffers inside slash opt slash telemetry slash schema dot conf four thirty two c p u cores because flatbuffers enables reading fields directly from raw network buffers without intermediate object allocations worker daemons decode records buy terminat memory copy overhead load testing across forty eight knowed instances showed zero copy serialization saved fourteen c p u cores per host while cutting p ninety nine end two end latency buy thirty percent",
        "refined_text": "Our high-throughput telemetry working group evaluated serialization wire formats across 80 microservices. Our initial data pipeline serialized all inter-service messages using Protocol Buffers over synchronous RPC connections. During peak message bursts of 150000 events per second, CPU profiling showed that object allocation and serialization decoding consumed 22 percent of total CPU cycles across 60 node workers, leading us to reject standard Protobuf decoding and adopt FlatBuffers zero-copy binary serialization instead.\n\nTechnical RFC 338 mandates zero-copy serialization by encoding structured telemetry records directly into contiguous byte buffers. Consumer processes inspect message_offset headers by configuring memory-mapped buffers inside /opt/telemetry/schema.conf for 32 CPU cores. Because FlatBuffers enables reading fields directly from raw network buffers without intermediate object allocations, worker daemons decode records by terminating memory copy overhead. Load testing across 48 node instances showed zero-copy serialization saved 14 CPU cores per host, while cutting P99 end-to-end latency by 30 percent."
    },

    # Sample 18: Cross-Region Consistency Models (ADR 344)
    {
        "raw_asr": "our core platform architecture council authored an architecture decision record evaluating cross region replication models across three continental zones our previous architecture implemented synchronous three region raft consensus where every state mutation required cross region quorum acknowledgments across sixty storage knowed servers because inter region round trip latency exceeded ninety milliseconds synchronous quorum commits caused p ninety nine write latencies two spike above one hundred forty milliseconds buy blocking local checkout transactions during transatlantic fiber cuts wait we discarded synchronous cross region raft and selected asynchronous conflict free replicated data types instead basically architectural decision record three four four mandates state based c r d t replication buy tracking observed remove sets across regional clusters replication workers inspect state underscore vector clocks buy synchronizat partition deltas inside slash var slash lib slash crdt slash cluster dot conf four twenty four c p u cores when regional networks partition local services continue writing two local state stores buy resolving concurrent updates deterministically upon reconnection chaos injection across seventy knowed instances proved that c r d t replication maintained local p ninety nine write latencies below five milliseconds while achieving guaranteed state convergence across all regions",
        "refined_text": "Our core platform architecture council authored an architecture decision record evaluating cross-region replication models across 3 continental zones. Our previous architecture implemented synchronous 3-region Raft consensus, where every state mutation required cross-region quorum acknowledgments across 60 storage node servers. Because inter-region round-trip latency exceeded 90 milliseconds, synchronous quorum commits caused P99 write latencies to spike above 140 milliseconds by blocking local checkout transactions during transatlantic fiber cuts, leading us to discard synchronous cross-region Raft and select asynchronous Conflict-Free Replicated Data Types instead.\n\nArchitectural Decision Record 344 mandates state-based CRDT replication by tracking observed-remove sets across regional clusters. Replication workers inspect state_vector clocks by synchronizing partition deltas inside /var/lib/crdt/cluster.conf for 24 CPU cores. When regional networks partition, local services continue writing to local state stores by resolving concurrent updates deterministically upon reconnection. Chaos injection across 70 node instances proved that CRDT replication maintained local P99 write latencies below 5 milliseconds, while achieving guaranteed state convergence across all regions."
    },

    # Sample 19: Message Queue Architecture & Partitioning Models (RFC 352)
    {
        "raw_asr": "our distributed messaging team published a technical r f c evaluating message consumption models across fifty order fulfillment services our legacy queue architecture used push based rabbit m q exchanges with competing consumers across thirty worker knowed servers during promotional flash sales uneven message processing speeds caused head of line blocking where slow worker nodes held unacknowledged messages buy stalling downstream order dispatching across forty queues wait we rejected push based competing queues and selected pull based partitioned commit logs instead uh technical r f c three five two standardizes pull based partitioned logs buy organizing event streams into thirty two immutable partitions consumer instances inspect partition underscore offset markers buy communicat fetch requests inside slash etc slash kafka slash consumer dot conf four sixteen c p u cores by allowing each consumer two pull messages at its own pace and track progress through committed offsets worker daemons process streams buy deduplicat order IDs across twenty four knowed instances stress testing with ninety thousand messages per second showed zero head of line stalls while preserving strict per partition ordering across all consumer groups",
        "refined_text": "Our distributed messaging team published a technical RFC evaluating message consumption models across 50 order fulfillment services. Our legacy queue architecture used push-based RabbitMQ exchanges with competing consumers across 30 worker node servers. During promotional flash sales, uneven message processing speeds caused head-of-line blocking where slow worker nodes held unacknowledged messages, stalling downstream order dispatching across 40 queues, leading us to reject push-based competing queues and select pull-based partitioned commit logs instead.\n\nTechnical RFC 352 standardizes pull-based partitioned logs by organizing event streams into 32 immutable partitions. Consumer instances inspect partition_offset markers by communicating fetch requests inside /etc/kafka/consumer.conf for 16 CPU cores. By allowing each consumer to pull messages at its own pace and track progress through committed offsets, worker daemons process streams by deduplicating order IDs across 24 node instances. Stress testing with 90000 messages per second showed zero head-of-line stalls while preserving strict per-partition ordering across all consumer groups."
    },

    # Sample 20: Distributed Transaction Coordination (ADR 360)
    {
        "raw_asr": "our commerce architecture steering committee evaluated transaction coordination patterns across twelve checkout microservices our existing payment flow used synchronous two phase commit protocols across forty database knowed instances during network latency fluctuations two phase commit transactions held row locks on inventory and payment tables buy causing cascading connection pool exhaustion and transaction aborts across twenty microservices wait we abandoned synchronous two phase commit and adopted saga orchestration with compensating transactions instead basically architectural decision record three six zero mandates orchestrated sagas buy executing distributed workflows through a central state orchestrator workflow engines inspect transaction underscore state markers buy allocat step executions inside slash opt slash saga slash orchestrator dot py four twenty four c p u cores if a downstream payment or inventory step fails the orchestrator executes backward compensating transactions buy terminat partial resource allocations across sixteen knowed clusters production verification across sixty thousand checkout workflows demonstrated ninety nine point nine nine percent transactional success without holding distributed locks",
        "refined_text": "Our commerce architecture steering committee evaluated transaction coordination patterns across 12 checkout microservices. Our existing payment flow used synchronous two-phase commit protocols across 40 database node instances. During network latency fluctuations, two-phase commit transactions held row locks on inventory and payment tables by causing cascading connection pool exhaustion and transaction aborts across 20 microservices, leading us to abandon synchronous two-phase commit and adopt Saga orchestration with compensating transactions instead.\n\nArchitectural Decision Record 360 mandates orchestrated Sagas by executing distributed workflows through a central state orchestrator. Workflow engines inspect transaction_state markers by allocating step executions inside /opt/saga/orchestrator.py for 24 CPU cores. If a downstream payment or inventory step fails, the orchestrator executes backward compensating transactions by terminating partial resource allocations across 16 node clusters. Production verification across 60000 checkout workflows demonstrated 99.99 percent transactional success without holding distributed locks."
    }
]

def main():
    print("=== Validating and Writing Batch 161 ===")
    assert len(samples) == 20, f"Expected 20 samples, got {len(samples)}"

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []

    for idx, s in enumerate(samples, start=1):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        # Eval leakage check
        if raw.lower().strip() in eval_raws:
            raise ValueError(f"Sample {idx} raw ASR leaked into eval set!")
        if ref.strip() in eval_refs:
            raise ValueError(f"Sample {idx} refined text leaked into eval set!")

        # Cleaner check
        cleaned, status = clean_sample(raw, ref)
        if not cleaned or status != "kept":
            raise ValueError(f"Sample {idx} failed clean_sample: {status}")

        words = len(ref.split())
        nl = get_noise_layer_count(raw)
        layer_counts.append(nl)

        target_min = 3 if words < 25 else 4

        # Pair validator check
        is_valid, reason = validate_pair(s, min_noise_layers=target_min)
        if not is_valid:
            raise ValueError(f"Sample {idx} failed validate_pair: {reason}")

        if words < 25:
            tier = "Short"
            tier_counts["short"] += 1
            if nl < 3:
                raise ValueError(f"Sample {idx} (Short) has {nl} noise layers (< 3)")
        elif words < 90:
            tier = "Medium"
            tier_counts["medium"] += 1
            if nl < 4:
                raise ValueError(f"Sample {idx} (Medium) has {nl} noise layers (< 4)")
        else:
            tier = "Long"
            tier_counts["long"] += 1
            if nl < 4:
                raise ValueError(f"Sample {idx} (Long) has {nl} noise layers (< 4)")

        print(f"Sample {idx:02d} [{tier}]: words={words}, noise_layers={nl} -> PASS")

    # Batch validator check
    b_valid, b_reason, b_stats = validate_batch(samples, min_short=4, min_medium=6, min_long=10, min_noise_layers=4)
    if not b_valid:
        raise ValueError(f"Batch validation failed: {b_reason}")

    avg_layers = sum(layer_counts) / len(layer_counts)
    print(f"\nBatch validation summary:")
    print(f"- Total samples: {len(samples)}")
    print(f"- Short (<25w): {tier_counts['short']}")
    print(f"- Medium (25-89w): {tier_counts['medium']}")
    print(f"- Long (90+w): {tier_counts['long']}")
    print(f"- Average noise layers: {avg_layers:.2f}")
    print(f"- Layer distribution: {b_stats.get('noise_layer_distribution')}")

    assert tier_counts["short"] == 4, f"Expected 4 short, got {tier_counts['short']}"
    assert tier_counts["medium"] == 6, f"Expected 6 medium, got {tier_counts['medium']}"
    assert tier_counts["long"] == 10, f"Expected 10 long, got {tier_counts['long']}"
    assert avg_layers >= 4.0, f"Expected avg noise layers >= 4.0, got {avg_layers}"

    output_path = Path("scratch/subagent_batch_161.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote 20 verified samples to {output_path}")

if __name__ == "__main__":
    main()
