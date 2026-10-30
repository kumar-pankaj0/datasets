import json
import re
import sys
import os

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch_12 = [
    # --- Short 1 (< 25 words) ---
    {
        "raw_asr": "ask cur sor to transform each call express knowed buy replacing the legacy fetch client with axios",
        "refined_text": "Ask Cursor to transform each call expression node by replacing the legacy fetch client with axios."
    },
    # --- Short 2 (< 25 words) ---
    {
        "raw_asr": "um generate p y test cases for the token refres handler wait for the session renew handler instead",
        "refined_text": "Generate pytest cases for the session renew handler instead."
    },
    # --- Medium 1 (25-90 words) ---
    {
        "raw_asr": "basically clawed the order checkout service crashed with an unhandled promise reject at line two hundred forty buy passing an undefined customer payload to the charge method um inspect the a sink call chain and right defensive validat checks around the payload deserializ logic",
        "refined_text": "Claude, the order checkout service crashed with an unhandled promise rejection at line 240 by passing an undefined customer payload to the charge method.\n\nInspect the async call chain and write defensive validation checks around the payload deserialization logic."
    },
    # --- Medium 2 (25-90 words) ---
    {
        "raw_asr": "ask cur sor to generat an a l e m b i c database migrat script four adding a composite index on the tenant id and created at columns in the audit events table wait add the index concurrently buy using post gres create index concurrently syntax",
        "refined_text": "Ask Cursor to generate an Alembic database migration script for adding a composite index on the tenant ID and created at columns in the audit events table.\n\nAdd the index concurrently by using Postgres `CREATE INDEX CONCURRENTLY` syntax."
    },
    # --- Medium 3 (25-90 words) ---
    {
        "raw_asr": "prompt co pilot to right unit tests covering rate limiter edge cases when the redis token bucket drops below zero wait when it drops to exactly zero tokens um mock the network socket timeout buy returning a status code five hundred four gateway error response",
        "refined_text": "Prompt Copilot to write unit tests covering rate limiter edge cases when the Redis token bucket drops to exactly zero tokens.\n\nMock the network socket timeout by returning a status code 504 gateway error response."
    },
    # --- Long 1 (90+ words) ---
    {
        "raw_asr": "ask clawed to write an a s t transformation script using j s code shift to refact legacy react class components into functional components buy visiting all class declar knowed types in the source file the codemod must scan every component method and convert component did mount into a use effect hook with an empty dependency array um inspect the render method return statement and extract nested inline callback functions into dedicated use callback hooks with proper dependency track we observed that the current codemod script breaks variable scoping when renaming state properties buy mutating parent lexical scope bindings directly wait make sure the visitor checks parent variable declar identifiers before applying the rename transform tell clawed to generat comprehensive test fixtures verifying that sixty four test cases pass buy comparing input source code against expected output a s t snapshots without syntax errors",
        "refined_text": "Ask Claude to write an AST transformation script using jscodeshift to refactor legacy React class components into functional components by visiting all class declaration node types in the source file. The codemod must scan every component method and convert `componentDidMount` into a `useEffect` hook with an empty dependency array.\n\nInspect the render method return statement and extract nested inline callback functions into dedicated `useCallback` hooks with proper dependency tracking. We observed that the current codemod script breaks variable scoping when renaming state properties by mutating parent lexical scope bindings directly. Make sure the visitor checks parent variable declaration identifiers before applying the rename transformation.\n\nTell Claude to generate comprehensive test fixtures verifying that 64 test cases pass by comparing input source code against expected output AST snapshots without syntax errors."
    },
    # --- Long 2 (90+ words) ---
    {
        "raw_asr": "prompt cur sor to analyze this heap dump stack trace from our node j s event streaming pipeline where worker processes crashed with a heap out of memory allocat error at line five hundred twelve the stack trace shows that the kafka message consumer retained eight thousand unacknowledged payload buffers in memory buy failing to deregister message event listeners on socket disconnect um inspect the event emitter subscrib logic inside the consumer stream handler where each incoming batch creates a new closure over the database connection pool we saw that memory consumption climbed from one hundred twenty eight megabytes to two gigabytes within twenty minutes wait actually within fifteen minutes under sustained traffic tell cur sor to refact the consumer buy replacing dynamic event listener attachment with a bounded object pool and adding explicit listener cleanup on error events also ask it to right an automated stress test reproducing the leak buy emitting ten thousand simulated events across fifty concurrent worker threads",
        "refined_text": "Prompt Cursor to analyze this heap dump stack trace from our Node.js event streaming pipeline where worker processes crashed with a heap out-of-memory allocation error at line 512. The stack trace shows that the Kafka message consumer retained 8000 unacknowledged payload buffers in memory by failing to deregister message event listeners on socket disconnect.\n\nInspect the event emitter subscription logic inside the consumer stream handler where each incoming batch creates a new closure over the database connection pool. We saw that memory consumption climbed from 128 megabytes to 2 gigabytes within 15 minutes under sustained traffic.\n\nTell Cursor to refactor the consumer by replacing dynamic event listener attachment with a bounded object pool and adding explicit listener cleanup on error events. Also ask it to write an automated stress test reproducing the leak by emitting 10000 simulated events across 50 concurrent worker threads."
    },
    # --- Long 3 (90+ words) ---
    {
        "raw_asr": "dictate to clawed a multi step post gres database migrat script for partitioning our billing invoices table buy tenant id and invoice year the current monolithic invoices table holds thirty two million records causing sequential table scans to degrade query latency past three seconds um the migrat must create the master partitioned table using range partitioning on the billing period column and hash partitioning on the tenant id column ask clawed to write a declarative d d l migration that creates twelve monthly partition tables for the year twenty twenty four with foreign key constraints referencing the accounts table we need the data migrat script to backfill historical invoices in batches of five thousand rows buy reading records with a cursor wait read records buy keyset pagination instead of offset pagination to avoid quadratic scan penalties make sure clawed includes transactional rollback blocks and sets lock timeout to two seconds buy executing alter table statements sequentially",
        "refined_text": "Dictate to Claude a multi-step Postgres database migration script for partitioning our billing invoices table by tenant ID and invoice year. The current monolithic invoices table holds 32000000 records, causing sequential table scans to degrade query latency past 3 seconds.\n\nThe migration must create the master partitioned table using range partitioning on the billing period column and hash partitioning on the tenant ID column. Ask Claude to write a declarative DDL migration that creates 12 monthly partition tables for the year 2024 with foreign key constraints referencing the accounts table.\n\nWe need the data migration script to backfill historical invoices in batches of 5000 rows by reading records by keyset pagination instead of offset pagination to avoid quadratic scan penalties. Make sure Claude includes transactional rollback blocks and sets lock timeout to 2 seconds by executing alter table statements sequentially."
    },
    # --- Long 4 (90+ words) ---
    {
        "raw_asr": "ask co pilot to implement a comprehensive test suite covering edge cases for our distributed lock manager module buy using pie test and pie test a sink i o the lock manager handles mutual exclusion across worker nodes buy acquiring redis key leases with a configurable time to live um we need tests simulating lock acquisition race conditions where three concurrent worker tasks attempt to acquire the same resource lock simultaneously at line ninety six the test harness must verify that exactly one worker succeeds while the other two tasks receive lock acquisition timeout exceptions within five hundred milliseconds wait also add a test case verifying lock heartbeats where a background coroutine extends the lease buy issuing p e x p i r e commands every two seconds before the ten second lease expires tell co pilot to mock redis server network partitions buy disconnecting the socket connection during lease renewal and confirming that the worker releases the lease buy executing the finally block without leaving orphaned keys",
        "refined_text": "Ask Copilot to implement a comprehensive test suite covering edge cases for our distributed lock manager module by using pytest and pytest-asyncio. The lock manager handles mutual exclusion across worker nodes by acquiring Redis key leases with a configurable time-to-live.\n\nWe need tests simulating lock acquisition race conditions where 3 concurrent worker tasks attempt to acquire the same resource lock simultaneously at line 96. The test harness must verify that exactly 1 worker succeeds while the other 2 tasks receive lock acquisition timeout exceptions within 500 milliseconds.\n\nAlso add a test case verifying lock heartbeats where a background coroutine extends the lease by issuing `PEXPIRE` commands every 2 seconds before the 10-second lease expires. Tell Copilot to mock Redis server network partitions by disconnecting the socket connection during lease renewal and confirming that the worker releases the lease by executing the finally block without leaving orphaned keys."
    },
    # --- Long 5 (90+ words) ---
    {
        "raw_asr": "instruct cur sor to write a custom type script compiler a s t transformation rule that detects unescaped string interpolat inside raw s q l query builders across our data access layer the linter rule must inspect binary express knowed types and tagged template literals passed to the query execution method um when the visitor traverses a tagged template express knowed it should verify whether dynamic parameters are bound buy parameterized query placeholders like dollar one instead of raw variable concatenat we noticed that the existing linter rule fails on multiline template strings buy traversing only the first child knowed in the syntax tree wait instruct cur sor to recursively traverse all child identifier knowed elements within template span containers ask cur sor to generat automated fix suggestions buy wrapping unescaped variables in query sanitiz helper functions and right twelve unit tests asserting that sixty four test fixtures pass without false positives",
        "refined_text": "Instruct Cursor to write a custom TypeScript compiler AST transformation rule that detects unescaped string interpolation inside raw SQL query builders across our data access layer. The linter rule must inspect binary expression node types and tagged template literals passed to the query execution method.\n\nWhen the visitor traverses a tagged template expression node, it should verify whether dynamic parameters are bound by parameterized query placeholders like $1 instead of raw variable concatenation. We noticed that the existing linter rule fails on multiline template strings by traversing only the first child node in the syntax tree. Instruct Cursor to recursively traverse all child identifier node elements within template span containers.\n\nAsk Cursor to generate automated fix suggestions by wrapping unescaped variables in query sanitization helper functions, and write 12 unit tests asserting that 64 test fixtures pass without false positives."
    }
]

def main():
    print("Testing batch_12 candidate samples...")
    all_ok = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for i, s in enumerate(batch_12, 1):
        v_ok, v_reason = validate_pair(s)
        c_res, c_reason = clean_sample(s["raw_asr"], s["refined_text"])

        words = len(s["refined_text"].split())
        raw_words = len(s["raw_asr"].split())
        ratio = words / max(1, raw_words)

        if words < 25:
            tier = "Short"
            tier_counts["short"] += 1
        elif words <= 90:
            tier = "Medium"
            tier_counts["medium"] += 1
        else:
            tier = "Long"
            tier_counts["long"] += 1

        status = "PASS" if (v_ok and c_res is not None) else "FAIL"
        if not (v_ok and c_res is not None):
            all_ok = False
        print(f"[{status}] Sample {i} ({tier}, {words} words, raw: {raw_words}, ratio: {ratio:.2f})")
        if not v_ok:
            print(f"  validator fail: {v_reason}")
        if c_res is None:
            print(f"  cleaner fail: {c_reason}")

    b_ok, b_reason, b_counts = validate_batch(batch_12, min_short=2, min_medium=3, min_long=5)
    print(f"\nBatch validation: {'PASS' if b_ok else 'FAIL'} - {b_reason}")
    print(f"Counts: {b_counts}")

    if all_ok and b_ok:
        out_path = "scratch/subagent_batch_12.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(batch_12, f, indent=2, ensure_ascii=False)
        print(f"\nSaved successfully to {out_path}")
    else:
        print("\nErrors detected, please fix before saving.")

if __name__ == "__main__":
    main()
