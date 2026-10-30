import json
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def build_batch():
    batch = [
        # =========================================================================
        # TIER 1: SHORT UTTERANCES (< 25 words) - Exactly 4 samples
        # Exactly 1 sentence, 0 newlines, max 1 cut-word restoration.
        # =========================================================================
        {
            # Sample 1: Rate limiting / Token bucket
            "raw_asr": "basically configur token bucket rate limiting buy setting bucket capacity two one hundred tokens with five tokens refilled per second",
            "refined_text": "Configure token bucket rate limiting by setting bucket capacity to 100 tokens with 5 tokens refilled per second."
        },
        {
            # Sample 2: CQRS / Materialized view
            "raw_asr": "uh synchroniz the c q r s read projection buy polling post gres change records every fifty milliseconds",
            "refined_text": "Synchronize the CQRS read projection by polling Postgres change records every 50 milliseconds."
        },
        {
            # Sample 3: Consensus / etcd lease
            "raw_asr": "um renew the e t c d leader lease buy sending heartbeat messages every three wait two seconds instead",
            "refined_text": "Renew the etcd leader lease by sending heartbeat messages every 2 seconds instead."
        },
        {
            # Sample 4: Distributed caching / Cache stampede mutex
            "raw_asr": "basically suppress cache stampede storms buy acquiring a distributed redis mutex with four seconds time two live",
            "refined_text": "Suppress cache stampede storms by acquiring a distributed Redis mutex with 4 seconds time to live."
        },

        # =========================================================================
        # TIER 2: MEDIUM UTTERANCES (25 to 89 words) - Exactly 6 samples
        # 1 to 3 sentences, natural \n\n paragraph breaks.
        # =========================================================================
        {
            # Sample 5: Multi-region replication / CRDTs
            "raw_asr": "um our multi region replication r f c evaluat state based c r d t sets against operation based c r d t sets four shopping cart synchronizat state based sets transfer complete state payloads across regions buy consuming twelve megabytes of network egress per batch uh operation based sets transmit only delta mutations buy streaming lightweight add and remove operations in twenty milliseconds",
            "refined_text": "Our multi-region replication RFC evaluated state-based CRDT sets against operation-based CRDT sets for shopping cart synchronization. State-based sets transfer complete state payloads across regions by consuming 12 megabytes of network egress per batch.\n\nOperation-based sets transmit only delta mutations by streaming lightweight add and remove operations in 20 milliseconds."
        },
        {
            # Sample 6: Schema migration / Expand and contract pattern
            "raw_asr": "basically our database migration r f c defin the expand and contract pattern four splitting user address columns into a normalized table the expand phase writes address records two both legacy and new tables buy buffering shadow writes through a worker pool uh after backfilling forty thousand historical rows background validation workers verify parity before dropping legacy columns",
            "refined_text": "Our database migration RFC defined the expand and contract pattern for splitting user address columns into a normalized table. The expand phase writes address records to both legacy and new tables by buffering shadow writes through a worker pool.\n\nAfter backfilling 40000 historical rows, background validation workers verify parity before dropping legacy columns."
        },
        {
            # Sample 7: Event streaming / DLQ retry policy
            "raw_asr": "okay so our event streaming r f c specifi exponential backoff retry parameters four poisoned webhook messages consumers retry unacknowledged message deliveries three wait five times buy doubling backoff intervals from one hundred milliseconds up two sixteen hundred milliseconds um exhausted messages route directly two a dead letter queue four manual forensic analysis",
            "refined_text": "Our event streaming RFC specified exponential backoff retry parameters for poisoned webhook messages. Consumers retry unacknowledged message deliveries 5 times by doubling backoff intervals from 100 milliseconds up to 1600 milliseconds.\n\nExhausted messages route directly to a dead letter queue for manual forensic analysis."
        },
        {
            # Sample 8: Rate limiting / Sliding window counter
            "raw_asr": "basically our api gateway r f c defin a sliding window counter algorithm four protecting authentication routes the algorithm divides each one minute window into six sub windows buy recording request timestamps in redis sorted sets um when a client exceeds one hundred requests per minute the gateway drops incoming traffic with an http four two nine status code",
            "refined_text": "Our API gateway RFC defined a sliding window counter algorithm for protecting authentication routes. The algorithm divides each 1-minute window into 6 sub-windows by recording request timestamps in Redis sorted sets.\n\nWhen a client exceeds 100 requests per minute, the gateway drops incoming traffic with an HTTP 429 status code."
        },
        {
            # Sample 9: Microservice decomposition / Saga orchestrator vs choreography
            "raw_asr": "um our order fulfillment design evaluat an orchestrat saga against choreography four managing distributed transactions an orchestrator workflow coordinates payment stock reservation and delivery buy dispatching asynchronous g r p c commands uh when payment fails the orchestrator triggers compensating transactions buy releasing reserved stock across five microservices",
            "refined_text": "Our order fulfillment design evaluated an orchestrated saga against choreography for managing distributed transactions. An orchestrator workflow coordinates payment, stock reservation, and delivery by dispatching asynchronous gRPC commands.\n\nWhen payment fails, the orchestrator triggers compensating transactions by releasing reserved stock across 5 microservices."
        },
        {
            # Sample 10: Consensus protocols / Zab vs Raft
            "raw_asr": "basically our metadata coordination r f c evaluat z a b against r a f t four managing configuration locks across five server knowed instances z a b couples atomic broadcast directly two transaction logging buy enforcing primary order through epoch identifiers um r a f t decouples log replication from membership changes buy executing joint consensus quorums in fifty milliseconds",
            "refined_text": "Our metadata coordination RFC evaluated Zab against Raft for managing configuration locks across 5 server node instances. Zab couples atomic broadcast directly to transaction logging by enforcing primary order through epoch identifiers.\n\nRaft decouples log replication from membership changes by executing joint consensus quorums in 50 milliseconds."
        },

        # =========================================================================
        # TIER 3: LONG UTTERANCES (90+ words) - Exactly 10 samples
        # Multi-paragraph \n\n natural structure, zero checklists, natural narration.
        # =========================================================================
        {
            # Sample 11: Event Sourcing & Schema Evolution with Protobuf
            "raw_asr": "our ledger platform architecture team authored an r f c defining schema evolution rules four our k a f k a event store legacy financial event schemas used j s o n payloads without strict typing which caused deserialization failures whenever upstream producers introduced optional metadata fields um the r f c mandates protocol buffers with an automated schema registry four all domain event definitions field tags replace positional attributes requiring new schema iterations two retain existing tag numbers and mark retired fields as reserved under our compatibility rules consumer services validate payload contracts against registry version four before committing read offsets okay so during staging verification across twelve consumer groups the schema validation proxy intercepted two unversioned payloads without pipeline disruption end two end replay benchmarks demonstrated schema serialization throughput increased buy forty percent while payload byte size dropped from eight hundred fifty bytes down two one hundred eighty bytes",
            "refined_text": "Our ledger platform architecture team authored an RFC defining schema evolution rules for our Kafka event store. Legacy financial event schemas used JSON payloads without strict typing, which caused deserialization failures whenever upstream producers introduced optional metadata fields.\n\nThe RFC mandates Protocol Buffers with an automated schema registry for all domain event definitions. Field tags replace positional attributes, requiring new schema iterations to retain existing tag numbers and mark retired fields as reserved. Under our compatibility rules, consumer services validate payload contracts against registry version 4 before committing read offsets.\n\nDuring staging verification across 12 consumer groups, the schema validation proxy intercepted 2 unversioned payloads without pipeline disruption. End-to-end replay benchmarks demonstrated schema serialization throughput increased by 40% while payload byte size dropped from 850 bytes down to 180 bytes."
        },
        {
            # Sample 12: Distributed Cache Stampede & XFetch Probabilistic Expiration
            "raw_asr": "our catalog caching infrastructure group published a technical design document addressing cache stampede outages during flash sale events under heavy read traffic exceeding fifty thousand requests per second popular product catalog keys expiring from redis caused simultaneous cache misses saturating backend post gres connection pools um the design document evaluat distributed mutex locking against the x fetch probabilistic early expiration algorithm distributed mutexes forced concurrent reader threads two spin on redis lock keys which increased tail request latency two three hundred twenty milliseconds under thread contention basically the committee selected the x fetch algorithm buy computing early recomputation probabilities based on key delta compute time and remaining time two live in benchmark simulations background cache recomputations triggered four seconds before key expiry eliminating cache misses entirely and keeping p nine nine database latency below eighteen milliseconds",
            "refined_text": "Our catalog caching infrastructure group published a technical design document addressing cache stampede outages during flash sale events. Under heavy read traffic exceeding 50000 requests per second, popular product catalog keys expiring from Redis caused simultaneous cache misses, saturating backend Postgres connection pools.\n\nThe design document evaluated distributed mutex locking against the XFetch probabilistic early expiration algorithm. Distributed mutexes forced concurrent reader threads to spin on Redis lock keys, which increased tail request latency to 320 milliseconds under thread contention.\n\nThe committee selected the XFetch algorithm by computing early recomputation probabilities based on key delta compute time and remaining time to live. In benchmark simulations, background cache recomputations triggered 4 seconds before key expiry, eliminating cache misses entirely and keeping p99 database latency below 18 milliseconds."
        },
        {
            # Sample 13: CQRS & Read Projection Synchronization Lag
            "raw_asr": "our search architecture r f c defin synchronization invariants between our transactional post gres write store and elasticsearch read projections high write volumes of fifteen thousand order updates per second created a six second projection lag which caused customers two observe stale order statuses immediately following checkout completion um the architecture team evaluat synchronous projection updates against asynchronous change data capture streaming using debezium synchronous writes coupled transaction commit latency directly two elasticsearch indexing speed which degraded write throughput buy sixty five percent basically the r f c established an asynchronous pipeline using debezium two stream write ahead log records into k a f k a topics partitioned buy order identifier read gateways now compare the entity version on query requests against projection metadata routing clients two the primary post gres store whenever replication lag exceeds five hundred milliseconds",
            "refined_text": "Our search architecture RFC defined synchronization invariants between our transactional Postgres write store and Elasticsearch read projections. High write volumes of 15000 order updates per second created a 6-second projection lag, which caused customers to observe stale order statuses immediately following checkout completion.\n\nThe architecture team evaluated synchronous projection updates against asynchronous change data capture streaming using Debezium. Synchronous writes coupled transaction commit latency directly to Elasticsearch indexing speed, which degraded write throughput by 65%.\n\nThe RFC established an asynchronous pipeline using Debezium to stream write-ahead log records into Kafka topics partitioned by order identifier. Read gateways now compare the entity version on query requests against projection metadata, routing clients to the primary Postgres store whenever replication lag exceeds 500 milliseconds."
        },
        {
            # Sample 14: Consensus Protocols / Raft Log Compaction & Snapshotting
            "raw_asr": "our distributed storage r f c reviewed snapshotting mechanisms four r a f t consensus metadata clusters when replication logs grew beyond one hundred thousand uncompacted entries follower knowed recovery required streaming millions of delta log entries over the network consuming four hundred megabytes of cluster bandwidth and delaying leader election failover um the r f c proposed decoupled background snapshotting two replace blocking inline compaction instead of freezing consensus state machine writes during disk flushes the leader forks an in memory copy on write snapshot while appending new transactions two a temporary delta log okay so staging validation demonstrated this non blocking snapshot design maintained consensus write throughput at twenty five thousand operations per second during active snapshot creation tail commit latency dropped from ninety five milliseconds down two eight milliseconds and cluster recovery time four lagging followers decreased two three seconds",
            "refined_text": "Our distributed storage RFC reviewed snapshotting mechanisms for Raft consensus metadata clusters. When replication logs grew beyond 100000 uncompacted entries, follower node recovery required streaming millions of delta log entries over the network, consuming 400 megabytes of cluster bandwidth and delaying leader election failover.\n\nThe RFC proposed decoupled background snapshotting to replace blocking inline compaction. Instead of freezing consensus state machine writes during disk flushes, the leader forks an in-memory copy-on-write snapshot while appending new transactions to a temporary delta log.\n\nStaging validation demonstrated this non-blocking snapshot design maintained consensus write throughput at 25000 operations per second during active snapshot creation. Tail commit latency dropped from 95 milliseconds down to 8 milliseconds, and cluster recovery time for lagging followers decreased to 3 seconds."
        },
        {
            # Sample 15: Multi-Region Replication / Hybrid Logical Clocks
            "raw_asr": "our multi region database engineering team published an r f c standardizing transaction ordering across three cloud regions relying solely on physical n t p server clocks resulted in clock skew up two one hundred fifty milliseconds between regions which caused write conflicts and silent data loss under last write wins resolution rules um the r f c evaluat true time hardware g p s clocks against hybrid logical clocks combining physical timestamps with monotonic logical counters hybrid logical clocks maintain strict causal consistency buy advancing logical counter ticks whenever a local knowed receives a remote mutation with a higher timestamp basically production canary deployments across sixteen database partitions proved that hybrid logical clocks correctly resolved one hundred percent of concurrent cross region updates without requiring external atomic clock hardware cross region conflict reconciliation overhead added only four milliseconds of c p u processing time per replication transaction",
            "refined_text": "Our multi-region database engineering team published an RFC standardizing transaction ordering across 3 cloud regions. Relying solely on physical NTP server clocks resulted in clock skew up to 150 milliseconds between regions, which caused write conflicts and silent data loss under last-write-wins resolution rules.\n\nThe RFC evaluated TrueTime hardware GPS clocks against Hybrid Logical Clocks combining physical timestamps with monotonic logical counters. Hybrid Logical Clocks maintain strict causal consistency by advancing logical counter ticks whenever a local node receives a remote mutation with a higher timestamp.\n\nProduction canary deployments across 16 database partitions proved that Hybrid Logical Clocks correctly resolved 100% of concurrent cross-region updates without requiring external atomic clock hardware. Cross-region conflict reconciliation overhead added only 4 milliseconds of CPU processing time per replication transaction."
        },
        {
            # Sample 16: Zero-Downtime Schema Migration with gh-ost
            "raw_asr": "our database operations r f c detailed our migration strategy four altering large my s q l tables without triggering table lock downtime running native alter table statements on a four hundred gigabyte payment transaction table previously held exclusive metadata locks four forty five minutes rejecting customer payment authorizations and breaching service level agreements um the r f c adopted the ghost table pattern using g h ost two execute non blocking schema transformations the tool creates an empty ghost table with the target schema alteration binlog stream listeners copy incremental changes and an asynchronous worker copies historical row chunks in batches of two thousand rows basically staging validation verified that g h ost migrated eighty thousand payment records with zero query blocking during the final cutover phase an atomic double table rename completed in forty milliseconds without dropping any client connections",
            "refined_text": "Our database operations RFC detailed our migration strategy for altering large MySQL tables without triggering table lock downtime. Running native alter table statements on a 400-gigabyte payment transaction table previously held exclusive metadata locks for 45 minutes, rejecting customer payment authorizations and breaching service level agreements.\n\nThe RFC adopted the ghost table pattern using gh-ost to execute non-blocking schema transformations. The tool creates an empty ghost table with the target schema alteration, binlog stream listeners copy incremental changes, and an asynchronous worker copies historical row chunks in batches of 2000 rows.\n\nStaging validation verified that gh-ost migrated 80000 payment records with zero query blocking. During the final cutover phase, an atomic double table rename completed in 40 milliseconds without dropping any client connections."
        },
        {
            # Sample 17: Microservice Decomposition / Strangler Fig Pattern
            "raw_asr": "our architecture review board ratified an r f c outlining the strangler fig decomposition of our legacy core billing monolith the monolith handled customer subscriptions invoicing and payment processing within a single codebase creating deployment coupling where a failure in tax calculation crashed subscription renewals um the r f c established an envoy reverse proxy at the network edge two intercept incoming http routes the team extracted subscription management into an independent go microservice with its own dedicated post gres database while leaving invoicing and payments within the monolith basically routing rules dynamically migrate traffic buy evaluating customer account ids routing ten percent of traffic two the new subscription service during canary validation performance telemetry confirmed the new microservice reduced invoice generation latency from six hundred twenty milliseconds two ninety five milliseconds while completely isolating subscription failures from core billing flows",
            "refined_text": "Our architecture review board ratified an RFC outlining the Strangler Fig decomposition of our legacy core billing monolith. The monolith handled customer subscriptions, invoicing, and payment processing within a single codebase, creating deployment coupling where a failure in tax calculation crashed subscription renewals.\n\nThe RFC established an Envoy reverse proxy at the network edge to intercept incoming HTTP routes. The team extracted subscription management into an independent Go microservice with its own dedicated Postgres database, while leaving invoicing and payments within the monolith.\n\nRouting rules dynamically migrate traffic by evaluating customer account IDs, routing 10% of traffic to the new subscription service during canary validation. Performance telemetry confirmed the new microservice reduced invoice generation latency from 620 milliseconds to 95 milliseconds while completely isolating subscription failures from core billing flows."
        },
        {
            # Sample 18: Rate Limiting / Distributed Redis Lua Token Bucket
            "raw_asr": "our edge networking r f c evaluat distributed rate limiting algorithms two safeguard authentication apis against credential stuffing attacks in memory rate limiting within gateway workers failed under autoscaling events because adding thirty new gateway instances inflated the global request limit buy a factor of thirty um the r f c introduced a centralized redis token bucket algorithm executed through an atomic lua script storing the token count and last refill timestamp in redis hash keys enables the lua script two calculate token replenishment and consume capacity in a single round trip basically benchmark evaluations proved the atomic lua implementation sustained seventy five thousand rate check evaluations per second with two milliseconds of median redis latency when tested against simulated denial of service attacks the rate limiter throttled abusive traffic at five hundred requests per minute without dropping legitimate user logins",
            "refined_text": "Our edge networking RFC evaluated distributed rate limiting algorithms to safeguard authentication APIs against credential stuffing attacks. In-memory rate limiting within gateway workers failed under autoscaling events because adding 30 new gateway instances inflated the global request limit by a factor of 30.\n\nThe RFC introduced a centralized Redis token bucket algorithm executed through an atomic Lua script. Storing the token count and last refill timestamp in Redis hash keys enables the Lua script to calculate token replenishment and consume capacity in a single round trip.\n\nBenchmark evaluations proved the atomic Lua implementation sustained 75000 rate check evaluations per second with 2 milliseconds of median Redis latency. When tested against simulated denial of service attacks, the rate limiter throttled abusive traffic at 500 requests per minute without dropping legitimate user logins."
        },
        {
            # Sample 19: Outbox Pattern & CDC vs Polling Publisher
            "raw_asr": "our platform architecture team published an r f c defining the transactional outbox pattern across our order processing microservices dual writing directly two both the post gres database and k a f k a brokers created dual write inconsistencies whenever network partitions caused k a f k a publish calls two fail after database commits succeeded um the r f c evaluat database polling workers against debezium change data capture the legacy polling worker scanned the outbox table every two hundred milliseconds using relational select queries which created table lock contention and consumed twenty five percent of database c p u capacity basically the team selected debezium two stream committed events directly from the post gres write ahead log into k a f k a topics this c d c design eliminated database query polling overhead completely guaranteed at least once message delivery and reduced end two end event propagation latency from three hundred fifty milliseconds down two fifteen milliseconds",
            "refined_text": "Our platform architecture team published an RFC defining the transactional outbox pattern across our order processing microservices. Dual-writing directly to both the Postgres database and Kafka brokers created dual-write inconsistencies whenever network partitions caused Kafka publish calls to fail after database commits succeeded.\n\nThe RFC evaluated database polling workers against Debezium change data capture. The legacy polling worker scanned the outbox table every 200 milliseconds using relational select queries, which created table lock contention and consumed 25% of database CPU capacity.\n\nThe team selected Debezium to stream committed events directly from the Postgres write-ahead log into Kafka topics. This CDC design eliminated database query polling overhead completely, guaranteed at-least-once message delivery, and reduced end-to-end event propagation latency from 350 milliseconds down to 15 milliseconds."
        },
        {
            # Sample 20: Kafka Partition Assignment & Cooperative Sticky Assignor
            "raw_asr": "our streaming data infrastructure r f c addressed consumer group rebalance storms across our real time telemetry pipeline under the eager rebalance protocol whenever a single consumer knowed crashed or joined the group k a f k a revoked all two hundred forty partition assignments across the entire cluster halting stream processing four thirty five seconds um the r f c mandated migrating consumer groups two the cooperative sticky assignor protocol cooperative rebalancing utilizes an incremental two phase rebalance process where unaffected consumers continue processing partitions while only revoked partitions undergo reassignment okay so production stress testing with forty consumer instances demonstrated that the cooperative protocol eliminated stop the world rebalance pauses entirely maximum rebalance partition handover latency dropped from thirty five seconds two four hundred fifty milliseconds maintaining continuous telemetry ingestion throughput of one hundred twenty thousand events per second",
            "refined_text": "Our streaming data infrastructure RFC addressed consumer group rebalance storms across our real-time telemetry pipeline. Under the eager rebalance protocol, whenever a single consumer node crashed or joined the group, Kafka revoked all 240 partition assignments across the entire cluster, halting stream processing for 35 seconds.\n\nThe RFC mandated migrating consumer groups to the Cooperative Sticky Assignor protocol. Cooperative rebalancing utilizes an incremental two-phase rebalance process where unaffected consumers continue processing partitions while only revoked partitions undergo reassignment.\n\nProduction stress testing with 40 consumer instances demonstrated that the cooperative protocol eliminated stop-the-world rebalance pauses entirely. Maximum rebalance partition handover latency dropped from 35 seconds to 450 milliseconds, maintaining continuous telemetry ingestion throughput of 120000 events per second."
        }
    ]
    return batch

def main():
    batch = build_batch()
    print(f"Loaded {len(batch)} candidate samples.")

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    all_ok = True

    for idx, pair in enumerate(batch, 1):
        v_ok, v_reason = validate_pair(pair)
        c_res, c_reason = clean_sample(pair["raw_asr"], pair["refined_text"])

        ref_words = len(pair["refined_text"].split())
        raw_words = len(pair["raw_asr"].split())
        ratio = ref_words / max(1, raw_words)

        if ref_words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
        elif ref_words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
        else:
            tier = "LONG"
            tier_counts["long"] += 1

        is_pair_ok = v_ok and (c_res is not None)
        if not is_pair_ok:
            all_ok = False
            print(f"Sample {idx:02d} [{tier:6s}]: FAIL")
            if not v_ok:
                print(f"  Validator: {v_reason}")
            if c_res is None:
                print(f"  Cleaner:   {c_reason}")
        else:
            print(f"Sample {idx:02d} [{tier:6s}]: PASS (ref_words={ref_words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f})")

    print("\n--- Tier Counts ---")
    print(f"Short:  {tier_counts['short']} / 4")
    print(f"Medium: {tier_counts['medium']} / 6")
    print(f"Long:   {tier_counts['long']} / 10")

    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"\nvalidate_batch: {b_reason} (passed={b_ok})")

    if all_ok and b_ok:
        print("\nAll 20 samples in Batch 41 passed validation cleanly.")
        with open("scratch/subagent_batch_41.json", "w", encoding="utf-8") as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)
        print("Saved to scratch/subagent_batch_41.json")
    else:
        print("\nBatch 41 validation FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
