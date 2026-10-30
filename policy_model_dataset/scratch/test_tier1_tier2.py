import json
import re
import sys
import os

sys.path.insert(0, os.path.abspath("code"))
from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
from cleaner import clean_sample

test_samples = [
    # Sample 1: WAL disk sync mode
    {
        "raw_asr": "um technical r f c three one two limits post gres write allocat buy setting wal underscore sync across eight knowed instances",
        "refined_text": "Technical RFC 312 limits Postgres write allocation by setting wal_sync across 8 node instances."
    },
    # Sample 2: Circuit breaker threshold bounds
    {
        "raw_asr": "uh architectural decision record three two four calibrat r p c failure thresholds buy setting failure underscore rate across twelve knowed clusters",
        "refined_text": "Architectural Decision Record 324 calibrates RPC failure thresholds by setting failure_rate across 12 node clusters."
    },
    # Sample 3: Partition rebalancing heartbeat intervals
    {
        "raw_asr": "basically technical r f c three three five mandates a sink heartbeats buy configur ping underscore interval across six knowed brokers",
        "refined_text": "Technical RFC 335 mandates async heartbeats by configuring ping_interval across 6 node brokers."
    },
    # Sample 4: Async message acknowledgment buffer bounds
    {
        "raw_asr": "you know architectural decision record three four six restricts c p u thread exhaustion buy terminat stalled queue underscore workers four twenty instances",
        "refined_text": "Architectural Decision Record 346 restricts CPU thread exhaustion by terminating stalled queue_workers for 20 instances."
    },
    # Sample 5: Message delivery semantics RFC - At-least-once vs 2PC
    {
        "raw_asr": "our messaging architecture working group evaluated distributed two phase commit across forty microservices wait adopt at least once delivery with idempotent deduplication instead um technical r f c three five two mandates message deduplicat buy tracking message underscore uuid keys across twenty dedicated r p c consumer knowed instances",
        "refined_text": "Our messaging architecture working group evaluated distributed two-phase commit across 40 microservices, adopting at-least-once delivery with idempotent deduplication instead.\n\nTechnical RFC 352 mandates message deduplication by tracking message_uuid keys across 20 dedicated RPC consumer node instances."
    },
    # Sample 6: API Gateway architecture ADR - GraphQL vs BFF
    {
        "raw_asr": "our platform architecture council evaluated separate backend for frontend proxies across fifty client applications wait choose unified graph q l schema federation instead uh architectural decision record three six zero directs gateway routing buy allocat thirty two query parsing threads inside federation underscore router dot py across sixteen c p u knowed hosts",
        "refined_text": "Our platform architecture council evaluated separate backend-for-frontend proxies across 50 client applications, choosing unified GraphQL schema federation instead.\n\nArchitectural Decision Record 360 directs gateway routing by allocating 32 query parsing threads inside federation_router.py across 16 CPU node hosts."
    },
    # Sample 7: Distributed caching coherence RFC - Cache-aside vs Write-through
    {
        "raw_asr": "our caching tier technical r f c evaluated write through caching with distributed leases across sixty cache clusters wait implement cache aside with event invalidation instead basically technical r f c three seven four standardizes cache consistency buy synchronizat purge underscore topic events across twenty four post gres consumer knowed instances",
        "refined_text": "Our caching tier technical RFC evaluated write-through caching with distributed leases across 60 cache clusters, implementing cache-aside with event invalidation instead.\n\nTechnical RFC 374 standardizes cache consistency by synchronizing purge_topic events across 24 Postgres consumer node instances."
    },
    # Sample 8: Database partitioning ADR - Hash partitioning vs List partitioning
    {
        "raw_asr": "our database architecture council evaluated tenant list partitioning across thirty database shards wait adopt dynamic hash partitioning instead you know architectural decision record three eight eight regulates tenant data placement buy arbitrat partition underscore hash keys across eighteen dedicated c p u knowed workers",
        "refined_text": "Our database architecture council evaluated tenant list partitioning across 30 database shards, adopting dynamic hash partitioning instead.\n\nArchitectural Decision Record 388 regulates tenant data placement by arbitrating partition_hash keys across 18 dedicated CPU node workers."
    },
    # Sample 9: RPC serialization protocol RFC - FlatBuffers vs Protobuf
    {
        "raw_asr": "our serialization technical r f c evaluated standard protocol buffer decoding across eighty high throughput microservices wait switch to flat buffers zero copy serialization instead um technical r f c three nine five accelerates payload parsing buy configur buffer underscore offset pointers across twelve high performance r p c knowed gateways",
        "refined_text": "Our serialization technical RFC evaluated standard Protocol Buffer decoding across 80 high-throughput microservices, switching to FlatBuffers zero-copy serialization instead.\n\nTechnical RFC 395 accelerates payload parsing by configuring buffer_offset pointers across 12 high-performance RPC node gateways."
    },
    # Sample 10: Cluster membership protocol ADR - Gossip vs ZooKeeper
    {
        "raw_asr": "our distributed infrastructure architecture working group evaluated centralized zookeeper heartbeating across one hundred cluster instances wait choose gossip based s w i m membership protocols instead uh architectural decision record four zero two establishes node failure detection buy communicat probe underscore ping packets across thirty two dedicated a sink knowed processes",
        "refined_text": "Our distributed infrastructure architecture working group evaluated centralized ZooKeeper heartbeating across 100 cluster instances, choosing gossip-based SWIM membership protocols instead.\n\nArchitectural Decision Record 402 establishes node failure detection by communicating probe_ping packets across 32 dedicated async node processes."
    }
]

for i, s in enumerate(test_samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    v_ok, v_msg = validate_pair(s, min_noise_layers=4)
    c_res, c_msg = clean_sample(raw, ref)
    cnt = get_noise_layer_count(raw)
    layers = [k for k, v in count_active_noise_layers(raw).items() if v]
    words = len(ref.split())
    print(f"Sample {i+1:02d}: {words:2d} words | Layers ({cnt}): {layers} | Val: {v_ok} ({v_msg}) | Clean: {c_msg}")
