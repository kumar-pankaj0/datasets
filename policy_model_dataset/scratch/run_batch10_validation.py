import sys
import json

sys.path.append("scratch")
from test_batch import test_samples, validate_pair, validate_batch, clean_sample

batch_10 = [
  # Short 1 (< 25 words)
  {
    "raw_asr": "um the executive summary four a d r twelve recommends migrating twenty four internal services from rest two g r p c buy next quarter",
    "refined_text": "The executive summary for ADR 12 recommends migrating 24 internal services from REST to `gRPC` by next quarter."
  },
  # Short 2 (< 25 words)
  {
    "raw_asr": "the cross region database replicat topology must keep p ninety nine synchronizat lag below fifty milliseconds buy using asynchronous log shipping",
    "refined_text": "The cross-region database replication topology must keep p99 synchronization lag below 50 milliseconds by using asynchronous log shipping."
  },
  # Medium 1 (25 to 90 words)
  {
    "raw_asr": "basically our r f c benchmark shows that g r p c reduces p ninety nine serializ latency buy forty percent compared two rest over h t t p two um the microservice cluster should adopt protocol buffers four internal inter service communicat while preserving rest endpoints four external client access",
    "refined_text": "Our RFC benchmark shows that `gRPC` reduces p99 serialization latency by 40% compared to REST over HTTP/2.\n\nThe microservice cluster should adopt protocol buffers for internal inter-service communication while preserving REST endpoints for external client access."
  },
  # Medium 2 (25 to 90 words)
  {
    "raw_asr": "the consensus r f c evaluates raft versus paxos four state machine replicat across five availability zones knowed heartbeat failures during network partitions favor raft due two deterministic leader elect um we recommend adopting raft because the protocol simplifies cluster membership changes and log compact",
    "refined_text": "The consensus RFC evaluates Raft versus Paxos for state machine replication across 5 availability zones.\n\nNode heartbeat failures during network partitions favor Raft due to deterministic leader election. We recommend adopting Raft because the protocol simplifies cluster membership changes and log compaction."
  },
  # Medium 3 (25 to 90 words)
  {
    "raw_asr": "a d r eight establishes our cold storage policy buy transitioning transaction audit logs older than sixty wait older than ninety days from solid state drives two amazon s three glacier flexible retrieve um the cold archive tier drops monthly retain cost buy sixty percent while maintaining a twelve hour retrieval time limit",
    "refined_text": "ADR 8 establishes our cold storage policy by transitioning transaction audit logs older than 90 days from solid-state drives to Amazon S3 Glacier Flexible Retrieval.\n\nThe cold archive tier drops monthly retention costs by 60% while maintaining a 12-hour retrieval time limit."
  },
  # Long 1 (90+ words)
  {
    "raw_asr": "basically the telemetry ingestion r f c compares event driven streaming buy apache kaf ka against batch processing buy apache spark four processing thirty thousand sensor events per second our legacy batch pipeline loads events into postgres every fifteen minutes but suffers from high memory spikes and stale analytics dashboard views during peak loads the benchmark confirms that kaf ka streaming delivers p ninety nine end two end latency below two hundred milliseconds whereas spark micro batching averages four seconds wait spark micro batching averages eight seconds buy adopting kaf ka event streams the ingestion worker can publish events directly two downstream alert consumers without waiting four batch window complet um we recommend transitioning our telemetry pipeline two event streaming while retaining hourly batch jobs four cold data aggregate",
    "refined_text": "The telemetry ingestion RFC compares event-driven streaming by Apache Kafka against batch processing by Apache Spark for processing 30000 sensor events per second. Our legacy batch pipeline loads events into Postgres every 15 minutes, but suffers from high memory spikes and stale analytics dashboard views during peak loads.\n\nThe benchmark confirms that Kafka streaming delivers p99 end-to-end latency below 200 milliseconds, whereas Spark micro-batching averages 8 seconds. By adopting Kafka event streams, the ingestion worker can publish events directly to downstream alert consumers without waiting for batch window completion.\n\nWe recommend transitioning our telemetry pipeline to event streaming while retaining hourly batch jobs for cold data aggregation."
  },
  # Long 2 (90+ words)
  {
    "raw_asr": "a d r fourteen documents the consensus protocol select four our multi region transaction catalog we evaluated multi paxos versus raft across three geographically distributed data centers with eighty milliseconds of round trip ping latency between replica node servers raft provides straightforward leader elect and simplified log replicat but requires two network round trips when requests hit follower node machines in contrast multi paxos allows any replica two coordinate proposals buy maintaining stable lease agreements which reduces write commit latency buy thirty five percent during peak traffic um we decided two adopt raft wait scratch that we decided two adopt multi paxos four cross region replication despite higher implement complex because shaving twenty eight milliseconds off write commit latency meets our strict p ninety nine service level agreement",
    "refined_text": "ADR 14 documents the consensus protocol selection for our multi-region transaction catalog. We evaluated Multi-Paxos versus Raft across 3 geographically distributed data centers with 80 milliseconds of round-trip ping latency between replica node servers.\n\nRaft provides straightforward leader election and simplified log replication, but requires 2 network round trips when requests hit follower node machines. In contrast, Multi-Paxos allows any replica to coordinate proposals by maintaining stable lease agreements, which reduces write commit latency by 35% during peak traffic.\n\nWe decided to adopt Multi-Paxos for cross-region replication despite higher implementation complexity, because shaving 28 milliseconds off write commit latency meets our strict p99 service level agreement."
  },
  # Long 3 (90+ words)
  {
    "raw_asr": "basically the database topology r f c evaluates active active versus active passive replicat between our primary data center in virginia and the secondary site in oregon our benchmark simulations showed that multi master active active replicat introduces distributed write conflicts on fifteen percent of concurrent customer checkout records resolving cross region conflicts required complex last right wins timestamps which caused silent data overwrites during simulated network splits buy switching our architecture two an active passive topology with asynchronous stream replicat we drop cross region synchronization overhead completely the secondary database maintains a standby replica with read only access and replication lag under twenty wait replication lag under forty milliseconds um we recommend adopting active passive replicat four the initial production rollout buy provisioning automated failover tooling that promotes the standby replica within sixty seconds",
    "refined_text": "The database topology RFC evaluates active-active versus active-passive replication between our primary data center in Virginia and the secondary site in Oregon. Our benchmark simulations showed that multi-master active-active replication introduces distributed write conflicts on 15% of concurrent customer checkout records.\n\nResolving cross-region conflicts required complex last-write-wins timestamps, which caused silent data overwrites during simulated network splits. By switching our architecture to an active-passive topology with asynchronous stream replication, we drop cross-region synchronization overhead completely.\n\nThe secondary database maintains a standby replica with read-only access and replication lag under 40 milliseconds. We recommend adopting active-passive replication for the initial production rollout by provisioning automated failover tooling that promotes the standby replica within 60 seconds."
  },
  # Long 4 (90+ words)
  {
    "raw_asr": "a d r twenty one analyzes internal communicat latency across our payment orchestration cluster buy comparing rest over json against g r p c binary streams profiling traces gathered during load tests at forty thousand wait load tests at fifty thousand requests per second demonstrated that json serializ consumed thirty two percent of total c p u cycles inside the gateway worker in contrast g r p c using compact protocol buffer messages reduced message payload size buy sixty five percent and lowered tail latency significantly our p ninety nine inter service transit time dropped from eighty five milliseconds down two twelve milliseconds buy eliminating text parsing overhead um we recommend standardizing all internal microservice endpoints on g r p c while retaining json schema validators only at the perimeter api gateway",
    "refined_text": "ADR 21 analyzes internal communication latency across our payment orchestration cluster by comparing REST over JSON against `gRPC` binary streams. Profiling traces gathered during load tests at 50000 requests per second demonstrated that JSON serialization consumed 32% of total CPU cycles inside the gateway worker.\n\nIn contrast, `gRPC` using compact protocol buffer messages reduced message payload size by 65% and lowered tail latency significantly. Our p99 inter-service transit time dropped from 85 milliseconds down to 12 milliseconds by eliminating text parsing overhead.\n\nWe recommend standardizing all internal microservice endpoints on `gRPC` while retaining JSON schema validators only at the perimeter API gateway."
  },
  # Long 5 (90+ words)
  {
    "raw_asr": "a d r twenty seven defines the cold data tiering lifecycle four petabyte scale compliance records stored in amazon s three under current operat policies all audit logs reside in standard s three buckets which costs over thirty thousand wait costs over forty five thousand dollars each month our capacity forecasts project data volume expanding buy two hundred terabytes every quarter without automated archive rules buy configuring an automated lifecycle policy logs transition two s three standard infrequent access after ninety days and migrate two s three glacier flexible retrieve after one hundred eighty days um this lifecycle transition drops average monthly storage expense buy seventy two percent while maintaining an access window of four hours buy approving this policy the infrastructure group automates compliance log retain without requiring manual bucket cleanup scripts",
    "refined_text": "ADR 27 defines the cold data tiering lifecycle for petabyte-scale compliance records stored in Amazon S3. Under current operational policies, all audit logs reside in standard S3 buckets, which costs over 45000 dollars each month. Our capacity forecasts project data volume expanding by 200 terabytes every quarter without automated archive rules.\n\nBy configuring an automated lifecycle policy, logs transition to S3 Standard-Infrequent Access after 90 days and migrate to S3 Glacier Flexible Retrieval after 180 days. This lifecycle transition drops average monthly storage expense by 72% while maintaining an access window of 4 hours.\n\nBy approving this policy, the infrastructure group automates compliance log retention without requiring manual bucket cleanup scripts."
  }
]

ok = test_samples(batch_10)

if ok:
    with open("scratch/subagent_batch_10.json", "w", encoding="utf-8") as f:
        json.dump(batch_10, f, indent=2, ensure_ascii=False)
    print("Successfully wrote scratch/subagent_batch_10.json")
else:
    print("Validation failed!")
    sys.exit(1)
