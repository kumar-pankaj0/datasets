import json
import re
import sys
from pathlib import Path
import importlib.util

# 1. Define the 20 samples
samples = [
    # Tier 1: Short (< 25 words, exactly 1 sentence, zero newlines) - Exactly 4 samples
    # Sample 1: Domain 3
    {
        "raw_asr": "um in pull request two hundred sixteen please call mutex unlock before returning the error",
        "refined_text": "In pull request 216, please call mutex unlock before returning the error."
    },
    # Sample 2: Domain 3
    {
        "raw_asr": "the database query in commit four hundred twenty requires an index buy user identifier",
        "refined_text": "The database query in commit 420 requires an index by user identifier."
    },
    # Sample 3: Domain 5
    {
        "raw_asr": "uh publish telemetry events two the telemetry stream using dot notation",
        "refined_text": "Publish telemetry events to the telemetry stream using dot notation."
    },
    # Sample 4: Domain 5
    {
        "raw_asr": "always terminat background worker threads during graceful shutdown of the service",
        "refined_text": "Always terminate background worker threads during graceful shutdown of the service."
    },

    # Tier 2: Medium (25-89 words, 1-3 sentences, natural \n\n paragraph break) - Exactly 6 samples
    # Sample 5: Domain 3
    {
        "raw_asr": "um in pull request three hundred twelve the goroutine spawns without a context cancel listener so it leaks when the client disconnects please pass the request context two the worker and wait buy selecting on done",
        "refined_text": "In pull request 312, the goroutine spawns without a context cancel listener so it leaks when the client disconnects.\n\nPlease pass the request context to the worker and wait by selecting on done."
    },
    # Sample 6: Domain 3
    {
        "raw_asr": "like in commit five hundred forty the json decoder allocat a new byte buffer inside the parse loop which causes heap churn preallocate the slice with capacity sixty four before starting the iteration",
        "refined_text": "In commit 540, the JSON decoder allocates a new byte buffer inside the parse loop which causes heap churn.\n\nPreallocate the slice with capacity 64 before starting the iteration."
    },
    # Sample 7: Domain 3
    {
        "raw_asr": "uh for the query handler in pr seven hundred sixteen please validate both limit and offset in the request payload reject negative values with a bad request status four hundred before executing the sql statement",
        "refined_text": "For the query handler in PR 716, please validate both limit and offset in the request payload.\n\nReject negative values with a bad request status 400 before executing the SQL statement."
    },
    # Sample 8: Domain 5
    {
        "raw_asr": "uh basically when configuring a circuit breaker the trip threshold monitors the failure rate over thirty consecutive requests if errors exceed fifty percent transition the breaker state from closed two open",
        "refined_text": "When configuring a circuit breaker, the trip threshold monitors the failure rate over 30 consecutive requests.\n\nIf errors exceed 50 percent, transition the breaker state from closed to open."
    },
    # Sample 9: Domain 5
    {
        "raw_asr": "um under the cache aside pattern the application reads from cache first and falls back two the primary datastore on a miss always right the updated record two the database before invalidating the stale cached key",
        "refined_text": "Under the cache-aside pattern, the application reads from cache first and falls back to the primary datastore on a miss.\n\nAlways write the updated record to the database before invalidating the stale cached key."
    },
    # Sample 10: Domain 5
    {
        "raw_asr": "for reliable message delivery the transactional outbox pattern persists events directly into an outbox table in the same transaction a relay process then polls the outbox and publishes the records two the message broker",
        "refined_text": "For reliable message delivery, the transactional outbox pattern persists events directly into an outbox table in the same transaction.\n\nA relay process then polls the outbox and publishes the records to the message broker."
    },

    # Tier 3: Long (90+ words, multi-paragraph separated by \n\n, zero checklist stereotypes) - Exactly 10 samples
    # Sample 11: Domain 3
    {
        "raw_asr": "okay so in pull request four hundred eighty eight looking at the distributed lock manager implementation the current lease renewal goroutine sleeps for thirty seconds without checking if the heartbeat failed or if the lease expired if network latency spikes past the ten second timeout the lock releases silently in the redis cluster while the worker continues processing assuming it still holds exclusive ownership we should refactor this loop two acquire an atomic lease with a five second ttl and spin up a background ticker that checks the cancellation channel on every tick also make sure you terminat the renewal routine immediately if the redis client returns a connection closed error",
        "refined_text": "In pull request 488, looking at the distributed lock manager implementation, the current lease renewal goroutine sleeps for 30 seconds without checking if the heartbeat failed or if the lease expired. If network latency spikes past the 10 second timeout, the lock releases silently in the Redis cluster while the worker continues processing assuming it still holds exclusive ownership.\n\nWe should refactor this loop to acquire an atomic lease with a 5 second TTL and spin up a background ticker that checks the cancellation channel on every tick. Also make sure you terminate the renewal routine immediately if the Redis client returns a connection closed error."
    },
    # Sample 12: Domain 3
    {
        "raw_asr": "um reviewing the changes in pr six hundred twelve regarding the async consumer group pipeline the batch offset commit logic currently commits every sixty records without tracking partial failures if deserialization fails on message forty two the entire batch gets marked as committed and the poison pill message drops without being routed two the dead letter topic instead we need two buffer incoming records inside an a sink queue and track the high water mark explicitly for each partition when an unrecoverable deserialization fault occurs pause the consumer partition commit offsets up two the last successful sequence and dispatch the failing payload directly two the error queue",
        "refined_text": "Reviewing the changes in PR 612 regarding the async consumer group pipeline, the batch offset commit logic currently commits every 60 records without tracking partial failures. If deserialization fails on message 42, the entire batch gets marked as committed and the poison pill message drops without being routed to the dead letter topic.\n\nInstead, we need to buffer incoming records inside an async queue and track the high water mark explicitly for each partition. When an unrecoverable deserialization fault occurs, pause the consumer partition, commit offsets up to the last successful sequence, and dispatch the failing payload directly to the error queue."
    },
    # Sample 13: Domain 3
    {
        "raw_asr": "so on pr eight hundred twenty four in the banking balance transfer handler i noticed that you wrapped the ledger update inside a serializable transaction block while this prevents write skew holding open row locks while awaiting downstream credit card verification exhausts the connection pool within thirty seconds under load notice how the pool max limit is capped at twenty connections so any delay in the third party http call stalls all pending settlement workers please extract the external verification call outside the transaction boundary and execute the balance check and debit atomically using a row level select four update lock instead",
        "refined_text": "On PR 824 in the banking balance transfer handler, I noticed that you wrapped the ledger update inside a serializable transaction block. While this prevents write skew, holding open row locks while awaiting downstream credit card verification exhausts the connection pool within 30 seconds under load.\n\nNotice how the pool max limit is capped at 20 connections, so any delay in the third-party HTTP call stalls all pending settlement workers. Please extract the external verification call outside the transaction boundary, and execute the balance check and debit atomically using a row-level select for update lock instead."
    },
    # Sample 14: Domain 3
    {
        "raw_asr": "uh looking at the rate limiter implementation in pr five hundred fifty six the token replenishment logic calculates available tokens buy subtracting the last timestamp from current time the issue is that multiple incoming requests mutate the remaining count concurrently without atomic operations which leads two race conditions and lost token refills under a test benchmark of eight hundred requests per second the limiter allowed twelve percent more traffic than the configured burst capacity of one hundred tokens we should replace the raw integer arithmetic with an atomic compare and swap loop or wrap the token replenishment in a sync mutex before updating the bucket state",
        "refined_text": "Looking at the rate limiter implementation in PR 556, the token replenishment logic calculates available tokens by subtracting the last timestamp from current time. The issue is that multiple incoming requests mutate the remaining count concurrently without atomic operations, which leads to race conditions and lost token refills.\n\nUnder a test benchmark of 800 requests per second, the limiter allowed 12 percent more traffic than the configured burst capacity of 100 tokens. We should replace the raw integer arithmetic with an atomic compare-and-swap loop, or wrap the token replenishment in a sync mutex before updating the bucket state."
    },
    # Sample 15: Domain 3
    {
        "raw_asr": "um in pull request three hundred ninety two the gRPC client interceptor attaches a fixed timeout of fifteen seconds two every outgoing remote call however when the parent web request already has a shorter deadline say five seconds the interceptor overrides it and keeps downstream connections hanging even after the client aborts you know this caused connection pool saturation during our staging load test where over two hundred zombie requests occupied worker threads please refactor the client interceptor two inspect the existing context deadline and only apply the fifteen second timeout if no earlier deadline is present on the incoming request context",
        "refined_text": "In pull request 392, the gRPC client interceptor attaches a fixed timeout of 15 seconds to every outgoing remote call. However, when the parent web request already has a shorter deadline, say 5 seconds, the interceptor overrides it and keeps downstream connections hanging even after the client aborts.\n\nThis caused connection pool saturation during our staging load test where over 200 zombie requests occupied worker threads. Please refactor the client interceptor to inspect the existing context deadline, and only apply the 15 second timeout if no earlier deadline is present on the incoming request context."
    },
    # Sample 16: Domain 5
    {
        "raw_asr": "okay so when pairing on command query responsibility segregation remember that the command handler mutates state and writes domain events directly two the append only event store the read projections do not update synchronously buy listening inline instead an asynchronous projector polls or receives events via stream consumers because projections are eventually consistent there is a window of twenty milliseconds up two fifty milliseconds where a user querying their account might see stale data immediately after submitting an order two manage this we can either return the newly generated event version two the client so the frontend polls until the projection catches up or route immediate post command queries through the write model",
        "refined_text": "When pairing on command query responsibility segregation, remember that the command handler mutates state and writes domain events directly to the append-only event store. The read projections do not update synchronously by listening inline; instead, an asynchronous projector polls or receives events via stream consumers.\n\nBecause projections are eventually consistent, there is a window of 20 milliseconds up to 50 milliseconds where a user querying their account might see stale data immediately after submitting an order. To manage this, we can either return the newly generated event version to the client so the frontend polls until the projection catches up, or route immediate post-command queries through the write model."
    },
    # Sample 17: Domain 5
    {
        "raw_asr": "let us walk through the trade offs between choreography and orchestration sagas four our order fulfillment pipeline in a choreographed flow each service listens two domain events like order created or payment processed and publishes the next event independently without central coordination this works well when you have three or four microservices but as the workflow expands towards twelve services tracking compensating transactions becomes extremely difficult during partial failures with an orchestration saga a dedicated state machine sends direct commands two each service and logs every transition in a durable database if payment fails the orchestrator deterministically triggers refund and inventory release compensating actions across all downstream participants",
        "refined_text": "Let us walk through the trade-offs between choreography and orchestration sagas for our order fulfillment pipeline. In a choreographed flow, each service listens to domain events like order created or payment processed and publishes the next event independently without central coordination.\n\nThis works well when you have 3 or 4 microservices, but as the workflow expands towards 12 services, tracking compensating transactions becomes extremely difficult during partial failures. With an orchestration saga, a dedicated state machine sends direct commands to each service and logs every transition in a durable database. If payment fails, the orchestrator deterministically triggers refund and inventory release compensating actions across all downstream participants."
    },
    # Sample 18: Domain 5
    {
        "raw_asr": "uh during our architecture review we evaluated database sharding strategies four user profile storage across sixty four partition nodes if you simply use modulo hashing on the user identifier adding four additional nodes requires redistributing nearly ninety percent of existing database records which overloads the network instead we should implement consistent hashing using a virtual ring with two hundred fifty six virtual knowed points per physical server this ensures that when a new database node joins the cluster only one divided buy the total node count of data keys gets migrated while the remaining partitions remain undisturbed",
        "refined_text": "During our architecture review, we evaluated database sharding strategies for user profile storage across 64 partition nodes. If you simply use modulo hashing on the user identifier, adding 4 additional nodes requires redistributing nearly 90 percent of existing database records which overloads the network.\n\nInstead, we should implement consistent hashing using a virtual ring with 256 virtual node points per physical server. This ensures that when a new database node joins the cluster, only 1 divided by the total node count of data keys gets migrated while the remaining partitions remain undisturbed."
    },
    # Sample 19: Domain 5
    {
        "raw_asr": "um let us review the leader election and log replication invariants in our raft consensus cluster of five servers when a candidate node initiates an election it increments the current term buy one and requests votes from peer nodes the node only grants its vote if the candidate log is at least as up two date as its own local commit sequence once elected leader the node appends client commands two its local log and broadcasts append entries RPCs two all follower nodes the entry is only marked as committed once a quorum of three nodes acknowledges and writes the record two persistent storage before applying the command two the state machine",
        "refined_text": "Let us review the leader election and log replication invariants in our Raft consensus cluster of 5 servers. When a candidate node initiates an election, it increments the current term by 1 and requests votes from peer nodes. The node only grants its vote if the candidate log is at least as up to date as its own local commit sequence.\n\nOnce elected leader, the node appends client commands to its local log and broadcasts append entries RPCs to all follower nodes. The entry is only marked as committed once a quorum of 3 nodes acknowledges and writes the record to persistent storage before applying the command to the state machine."
    },
    # Sample 20: Domain 5
    {
        "raw_asr": "so when pairing on reactive stream pipelines we need two discuss how backpressure prevents fast publishers from overwhelming slow database consumers in our current setup the ingestion worker pushes sixty thousand incoming records per second while the relational database writer caps out at twelve hundred writes per second without explicit backpressure signaling unread message buffers expand in heap memory until the virtual machine crashes with an out of memory error two resolve this we configure the subscription with a demand signal requesting batches of fifty items at a time the publisher halts transmiss until the consumer acknowledges completion of the batch and requests the next window of items",
        "refined_text": "When pairing on reactive stream pipelines, we need to discuss how backpressure prevents fast publishers from overwhelming slow database consumers. In our current setup, the ingestion worker pushes 60000 incoming records per second while the relational database writer caps out at 1200 writes per second. Without explicit backpressure signaling, unread message buffers expand in heap memory until the virtual machine crashes with an out of memory error.\n\nTo resolve this, we configure the subscription with a demand signal requesting batches of 50 items at a time. The publisher halts transmission until the consumer acknowledges completion of the batch and requests the next window of items."
    }
]

out_path = Path("scratch/subagent_batch_68.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)

print(f"Saved {len(samples)} samples to {out_path}")
