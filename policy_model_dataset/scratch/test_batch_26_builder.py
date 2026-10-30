import json
import sys
sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
  # --- TIER 1: SHORT (<25 words, exactly 1 sentence, 0 newlines) ---
  # Sample 1: Distributed caching (write-through vs write-back)
  {
    "raw_asr": "basically right through caching updates the database and cache synchronizat in ten wait five milliseconds",
    "refined_text": "Write-through caching updates the database and cache synchronization in 5 milliseconds."
  },
  # Sample 2: Database sharding key selection
  {
    "raw_asr": "um hashing tenant identifiers distributes database partit load evenly across four wait eight database knowed instances buy request volume",
    "refined_text": "Hashing tenant identifiers distributes database partition load evenly across 8 database node instances by request volume."
  },
  # Sample 3: Raft consensus
  {
    "raw_asr": "basically r a f t consensus protocols arbitrat leader election timeouts buy incrementing terms every fifty wait one hundred milliseconds",
    "refined_text": "Raft consensus protocols arbitrate leader election timeouts by incrementing terms every 100 milliseconds."
  },
  # Sample 4: gRPC streaming
  {
    "raw_asr": "uh bidirectional g r p c streaming cuts packet transmiss overhead four telemetry pipelines buy multiplexing two wait four channels",
    "refined_text": "Bidirectional gRPC streaming cuts packet transmission overhead for telemetry pipelines by multiplexing 4 channels."
  },

  # --- TIER 2: MEDIUM (25-90 words, 1-3 sentences, \n\n break) ---
  # Sample 5: Kafka vs RabbitMQ
  {
    "raw_asr": "basically our event sourcing r f c compared k a f k a against rabbit m q four financial audit logs k a f k a retains immutable event streams four ten wait thirty days buy storing ordered partition logs um in contrast rabbit m q deletes messages immediately after consumer acknowledgement which breaks asynchronous event replayability across downstream reporting services",
    "refined_text": "Our event-driven RFC compared Kafka against RabbitMQ for financial audit logs. Kafka retains immutable event streams for 30 days by storing ordered partition logs.\n\nIn contrast, RabbitMQ deletes messages immediately after consumer acknowledgement, which breaks asynchronous event replayability across downstream reporting services."
  },
  # Sample 6: Distributed caching (write-through vs write-back)
  {
    "raw_asr": "basically our distributed caching evaluation rejected right back caching four user profile data because dirty cache entries risk data loss during knowed crashes um configur right through caching updates redis and post gres synchronously buy holding database locks four five wait sixty milliseconds which stabilizes data integrity across web tiers",
    "refined_text": "Our distributed caching evaluation rejected write-back caching for user profile data because dirty cache entries risk data loss during node crashes.\n\nConfiguring write-through caching updates Redis and PostgreSQL synchronously by holding database locks for 60 milliseconds, which stabilizes data integrity across web tiers."
  },
  # Sample 7: GraphQL federation vs REST gateways
  {
    "raw_asr": "okay so our a p i architecture working group evaluat graph q l federation against centralized r e s t gateways four mobile client queries uh graph q l subgraph composition reduced network round trips buy resolving complex user entities in a single graph request dropping client latency from two hundred wait eighty milliseconds",
    "refined_text": "Our API architecture working group evaluated GraphQL federation against centralized REST gateways for mobile client queries.\n\nGraphQL subgraph composition reduced network round trips by resolving complex user entities in a single graph request, dropping client latency from 80 milliseconds."
  },
  # Sample 8: Database sharding key selection
  {
    "raw_asr": "basically selecting raw tenant uuid as the primary database sharding key caused severe hot partition bottlenecks on large enterprise accounts um migrating two a composite sharding key combining tenant id and creation date distributes records across sixteen wait thirty two database shards buy balancing write traffic evenly",
    "refined_text": "Selecting raw tenant UUID as the primary database sharding key caused severe hot partition bottlenecks on large enterprise accounts.\n\nMigrating to a composite sharding key combining tenant ID and creation date distributes records across 32 database shards by balancing write traffic evenly."
  },
  # Sample 9: Raft consensus
  {
    "raw_asr": "basically the distributed storage r f c mandated r a f t consensus across five wait three control plane replicas two maintain state machine consistency um the leader election protocol arbitrat split brain partitions buy requiring a strict majority quorum before committing append entries log updates",
    "refined_text": "The distributed storage RFC mandated Raft consensus across 3 control plane replicas to maintain state machine consistency.\n\nThe leader election protocol arbitrates split-brain partitions by requiring a strict majority quorum before committing append entries log updates."
  },
  # Sample 10: Tiered data lifecycles
  {
    "raw_asr": "okay so our telemetry storage a d r defined automated lifecycle policies moving cold observability metrics from local n v m e drives two s three object buckets after thirty wait ninety days um automated background jobs compress historical chunks buy merging columnar files without interrupting active analytical queries",
    "refined_text": "Our telemetry storage ADR defined automated lifecycle policies moving cold observability metrics from local NVMe drives to S3 object buckets after 90 days.\n\nAutomated background jobs compress historical chunks by merging columnar files without interrupting active analytical queries."
  }
]

print(f"Testing {len(samples)} samples...")
for i, s in enumerate(samples, 1):
    v_ok, v_err = validate_pair(s)
    c_res, c_err = clean_sample(s["raw_asr"], s["refined_text"])
    w = len(s["refined_text"].split())
    raw_w = len(s["raw_asr"].split())
    status = "OK" if v_ok and c_res else "FAIL"
    print(f"Sample {i:02d}: {status} (words: {w}, raw: {raw_w}) v: {v_ok} ({v_err}) c: {c_res is not None} ({c_err})")

