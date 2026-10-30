import json
import re
import sys
from pathlib import Path

# Add code directory to path
sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def build_batch():
    batch = [
        # Domain 2 - Short 1 (Staging environment downtime)
        {
            "raw_asr": "um staging cluster worker knowed is down because the memory allocat hit ninety five percent",
            "refined_text": "Staging cluster worker node is down because the memory allocation hit 95 percent."
        },
        # Domain 2 - Short 2 (Vendor API rate limits)
        {
            "raw_asr": "uh vendor payment api returned status four hundred twenty nine buy hitting the request limit",
            "refined_text": "Vendor payment API returned status 429 by hitting the request limit."
        },
        # Domain 2 - Medium 1 (Database replication lag)
        {
            "raw_asr": "um our secondary post gres replica has a replicat lag of three hundred wait four hundred fifty seconds right now buy delayed wal replay we need infrastructure assistance two inspect the replica disk throughput and clear the pending backlog",
            "refined_text": "Our secondary Postgres replica has a replication lag of 450 seconds right now by delayed WAL replay.\n\nWe need infrastructure assistance to inspect the replica disk throughput and clear the pending backlog."
        },
        # Domain 2 - Medium 2 (Flaky end-to-end tests)
        {
            "raw_asr": "the end two end checkout test suite failed three wait five times on the staging runner buy timing out during stripe callback validat we must isolat the flaky payment test into a quarantine runner before unblocking the release",
            "refined_text": "The end to end checkout test suite failed 5 times on the staging runner by timing out during Stripe callback validation.\n\nWe must isolate the flaky payment test into a quarantine runner before unblocking the release."
        },
        # Domain 2 - Medium 3 (Credential rotation blockers)
        {
            "raw_asr": "automated secret rotat failed in the staging environment buy rejecting the new vault token during role authenticat the continuous integration pipeline remains blocked for twenty wait twenty four hours until security updates the primary secret config dot yaml",
            "refined_text": "Automated secret rotation failed in the staging environment by rejecting the new Vault token during role authentication.\n\nThe continuous integration pipeline remains blocked for 24 hours until security updates the primary secret `config.yaml`."
        },
        # Domain 2 - Long 1 (Staging environment downtime & ingress failure)
        {
            "raw_asr": "um basically our entire staging environment has been inaccessible since eight this morning buy reason of a cascading ingress crash the ingress controller knowed entered crash loop back off after an invalid default root configur was pushed buy automated deployment which returned http status five zero three on every service call we used cube ctl two inspect the pods in the coober netties staging namespace and observed memory exhaustion on the proxy container forty wait fifty pods were dropped during pod terminat before the worker pool could recover until the infrastructure team rolls back the deployment and restores the valid root table in ingress dot yaml the frontend development team remains completely blocked from running manual verification on the sprint release candidate",
            "refined_text": "Our entire staging environment has been inaccessible since 8 this morning by reason of a cascading ingress crash. The ingress controller node entered crash loop back off after an invalid default route configuration was pushed by automated deployment, which returned HTTP status 503 on every service call.\n\nWe used kubectl to inspect the pods in the Kubernetes staging namespace and observed memory exhaustion on the proxy container. 50 pods were dropped during pod termination before the worker pool could recover.\n\nUntil the infrastructure team rolls back the deployment and restores the valid route table in `ingress.yaml`, the frontend development team remains completely blocked from running manual verification on the sprint release candidate."
        },
        # Domain 2 - Long 2 (Database replication lag & WAL accumulation)
        {
            "raw_asr": "um we have a critical blocker on the billing database cluster right now buy reason of an escalating post gres replicat lag between the primary database and standby replicas the standby replica fell behind buy twelve minutes during morning batch processing which caused wal segments two accumulat on the primary disk volume disk usage reached eighty five percent on the primary knowed buy unconsumed write logs telemetry indicates that write latency at p ninety five increased significantly while network transmiss throttled the replica stream the database operations team attempted two restart the replica process but the standby connection hung on socket timeout one hundred wait two hundred gigabytes of pending transaction logs remain backlog until devops increases the volume size or flushes dead slots the team cannot proceed with running the daily customer invoice jobs",
            "refined_text": "We have a critical blocker on the billing database cluster right now by reason of an escalating Postgres replication lag between the primary database and standby replicas. The standby replica fell behind by 12 minutes during morning batch processing, which caused WAL segments to accumulate on the primary disk volume. Disk usage reached 85 percent on the primary node by unconsumed write logs.\n\nTelemetry indicates that write latency at P95 increased significantly while network transmission throttled the replica stream. The database operations team attempted to restart the replica process, but the standby connection hung on socket timeout. 200 gigabytes of pending transaction logs remain backlog.\n\nUntil DevOps increases the volume size or flushes dead slots, the team cannot proceed with running the daily customer invoice jobs."
        },
        # Domain 2 - Long 3 (Flaky end-to-end test suite race conditions)
        {
            "raw_asr": "uh our pull request pipeline is currently blocked buy flaky end two end tests in the integration suite fourteen tests failed intermittently across three consecutive test runs buy timing out during dom element synchronizat the root cause appears two be an unhandled a sink promise inside the checkout page component where hydration finishes after click dispatch the test runner terminated the test worker buy socket reset when waiting for the payment confirmation modal thirty wait forty milliseconds was insufficient during headless browser execut on shared runners we need two temporarily disable the four flaky test scenarios in tests slash checkout dot spec dot ts or quarantine the suite so feature engineers can merge critical bug fixes today",
            "refined_text": "Our pull request pipeline is currently blocked by flaky end to end tests in the integration suite. 14 tests failed intermittently across 3 consecutive test runs by timing out during DOM element synchronization. The root cause appears to be an unhandled async promise inside the checkout page component where hydration finishes after click dispatch.\n\nThe test runner terminated the test worker by socket reset when waiting for the payment confirmation modal. 40 milliseconds was insufficient during headless browser execution on shared runners.\n\nWe need to temporarily disable the 4 flaky test scenarios in `tests/checkout.spec.ts` or quarantine the suite so feature engineers can merge critical bug fixes today."
        },
        # Domain 2 - Long 4 (Vendor API rate limits & webhook retry backoff)
        {
            "raw_asr": "um our customer onboarding flow is currently halted buy aggressive vendor rate limits on the identity verification provider api the vendor throttl our client credentials after our morning batch job exceeded their quota returning status four hundred twenty nine on all verification requests latency at p ninety nine spiked beyond eight seconds buy unhandled connection retries our background webhook worker queue backed up with four thousand pending events buy lacking an exponential backoff strategy the worker kept retrying against the exhausted quota one hundred wait sixty requests per minute is their hard tier ceiling we are blocked until the vendor representative increases our account rate limit or our team deploys a token bucket rate limiter in api slash verification dot py two throttle outbound requests",
            "refined_text": "Our customer onboarding flow is currently halted by aggressive vendor rate limits on the identity verification provider API. The vendor throttled our client credentials after our morning batch job exceeded their quota, returning status 429 on all verification requests. Latency at P99 spiked beyond 8 seconds by unhandled connection retries.\n\nOur background webhook worker queue backed up with 4000 pending events by lacking an exponential backoff strategy. The worker kept retrying against the exhausted quota. 60 requests per minute is their hard tier ceiling.\n\nWe are blocked until the vendor representative increases our account rate limit or our team deploys a token bucket rate limiter in `api/verification.py` to throttle outbound requests."
        },
        # Domain 2 - Long 5 (Credential rotation blockers & Vault lease expiration)
        {
            "raw_asr": "uh automated credential rotat broke database access across all microservices in the staging environment this morning buy generating incompatible post gres user permissions during scheduled lease expiration the vault agent renewed the database role lease but failed two update the active connection pool credentials in config slash database dot yaml services running on staging worker knowed could not authenticate buy reason of invalid user passwords which terminated thirty background processing jobs twelve wait twenty four hours remain on the token lease but all active application pods are in crash loop back off we need cube ctl access two restart the deployment pods and trigger a manual secret sync buy reloading the vault injector agent before developers can resume testing the checkout release",
            "refined_text": "Automated credential rotation broke database access across all microservices in the staging environment this morning by generating incompatible Postgres user permissions during scheduled lease expiration. The Vault agent renewed the database role lease, but failed to update the active connection pool credentials in `config/database.yaml`.\n\nServices running on staging worker node could not authenticate by reason of invalid user passwords, which terminated 30 background processing jobs. 24 hours remain on the token lease, but all active application pods are in crash loop back off.\n\nWe need kubectl access to restart the deployment pods and trigger a manual secret sync by reloading the Vault injector agent before developers can resume testing the checkout release."
        },
        # Domain 3 - Short 1 (Algorithmic complexity)
        {
            "raw_asr": "um replacing the nested loops reduces algorithmic complex from quadratic two linear lookup time",
            "refined_text": "Replacing the nested loops reduces algorithmic complexity from quadratic to linear lookup time."
        },
        # Domain 3 - Short 2 (SQL injection vulnerabilities)
        {
            "raw_asr": "uh right parameterized queries instead of string concatenat two eliminate s q l injection vulnerabilities",
            "refined_text": "Write parameterized queries instead of string concatenation to eliminate SQL injection vulnerabilities."
        },
        # Domain 3 - Medium 1 (Interface segregation principle)
        {
            "raw_asr": "this repository interface violates the interface segregat principle buy combining read query methods with right mutators in a single definition we should split the fat interface into smaller reader and writer interfaces two allow mock implement in unit tests",
            "refined_text": "This repository interface violates the interface segregation principle by combining read query methods with write mutators in a single definition.\n\nWe should split the fat interface into smaller reader and writer interfaces to allow mock implementation in unit tests."
        },
        # Domain 3 - Medium 2 (Race conditions in goroutines)
        {
            "raw_asr": "the pull request introduces a race condition buy launching twenty background g o routine workers that right two the same shared statistics map without a mutex lock running the race detector flags concurrent read and right access on line forty five",
            "refined_text": "The pull request introduces a race condition by launching 20 background goroutine workers that write to the same shared statistics map without a mutex lock.\n\nRunning the race detector flags concurrent read and write access on line 45."
        },
        # Domain 3 - Medium 3 (Resource leak prevention in database connections)
        {
            "raw_asr": "the database transaction helper does not close rows after query execut buy omitting the defer call buy holding forty active connections open the pool exhausts available connections under high concurrency we need two right a defer call immediately after s q l query execut",
            "refined_text": "The database transaction helper does not close rows after query execution by omitting the defer call.\n\nBy holding 40 active connections open, the pool exhausts available connections under high concurrency, so we need to write a defer call immediately after SQL query execution."
        },
        # Domain 3 - Long 1 (Algorithmic complexity quadratic nested loops refactor)
        {
            "raw_asr": "in this pull request the order match algorithm in services slash reconciler dot py exhibits quadratic algorithmic complex buy comparing every pending invoice against all historical settlements in nested loops with ten thousand records the processing duration escalates two over forty five seconds buy causing severe c p u starvation on worker knowed we should refactor the lookup buy building an in memory hash table indexed buy settlement identifier before iterating over the invoices this reduces lookup time from quadratic two linear time and drops overall latency at p ninety five two under three hundred milliseconds please update the benchmark tests in tests slash reconciler underscore benchmark dot py two verify memory allocat before we approve this pull request",
            "refined_text": "In this pull request, the order match algorithm in `services/reconciler.py` exhibits quadratic algorithmic complexity by comparing every pending invoice against all historical settlements in nested loops. With 10000 records, the processing duration escalates to over 45 seconds by causing severe CPU starvation on worker node.\n\nWe should refactor the lookup by building an in-memory hash table indexed by settlement identifier before iterating over the invoices. This reduces lookup time from quadratic to linear time and drops overall latency at P95 to under 300 milliseconds.\n\nPlease update the benchmark tests in `tests/reconciler_benchmark.py` to verify memory allocation before we approve this pull request."
        },
        # Domain 3 - Long 2 (Interface segregation & decoupling monolithic storage adapter)
        {
            "raw_asr": "this pull request touches the storage package where the storage manager interface has grown two sixty methods violating the interface segregat principle consumers that only read cached blobs are forced two implement unused write delete and permission methods buy coupling unrelated dependencies we should decompose this monolithic contract into smaller focused interfaces such as blob reader blob writer and metadata provider callers can then accept only the minimal interface required buy their business logic which simplifies unit test mock implement take a look at internal slash storage slash reader dot go where we already started separating blob streaming methods buy applying this pattern across all subpackages we improve modularity and avoid breaking downstream consumers",
            "refined_text": "This pull request touches the storage package where the storage manager interface has grown to 60 methods, violating the interface segregation principle. Consumers that only read cached blobs are forced to implement unused write, delete, and permission methods by coupling unrelated dependencies.\n\nWe should decompose this monolithic contract into smaller focused interfaces, such as blob reader, blob writer, and metadata provider. Callers can then accept only the minimal interface required by their business logic, which simplifies unit test mock implementation.\n\nTake a look at `internal/storage/reader.go` where we already started separating blob streaming methods. By applying this pattern across all subpackages, we improve modularity and avoid breaking downstream consumers."
        },
        # Domain 3 - Long 3 (Goroutine data races on shared map & sync map migration)
        {
            "raw_asr": "the race detector flagged a critical data race during integration test execut in telemetry slash collector dot go the collector spawns twenty background g o routine workers that right incoming telemetry samples two a raw standard map without synchronizat when high traffic bursts hit the collector simultaneous map writes trigger a fatal c p u runtime panic thirty wait fifty events were corrupted during benchmark load testing we should protect the map buy using a sync r w mutex or replace the standard map buy adopting sync dot map for concurrent operations please also ensure that worker termination waits for active g o routine channels two flush buy adding a sync wait group before closing the listener channel in the shutdown handler",
            "refined_text": "The race detector flagged a critical data race during integration test execution in `telemetry/collector.go`. The collector spawns 20 background goroutine workers that write incoming telemetry samples to a raw standard map without synchronization.\n\nWhen high traffic bursts hit the collector, simultaneous map writes trigger a fatal CPU runtime panic. 50 events were corrupted during benchmark load testing. We should protect the map by using a sync RWMutex or replace the standard map by adopting `sync.Map` for concurrent operations.\n\nPlease also ensure that worker termination waits for active goroutine channels to flush by adding a sync WaitGroup before closing the listener channel in the shutdown handler."
        },
        # Domain 3 - Long 4 (Resource leaks in HTTP client response body handling & connection pool starvation)
        {
            "raw_asr": "we observed a steady socket leak during sustained load tests buy reason of unclosed http client response bodies in client slash gateway dot py when outbound requests fail with status five zero zero or time out the error handler returns early without closing the response stream this leaks underlying tcp sockets buy leaving eighty four idle file descriptors open until the operating system drops the connection pool socket starvation then blocks all subsequent outbound api calls buy causing p ninety nine latency two spike beyond five seconds please ensure that response body close is guaranteed buy using a try finally block immediately following request dispatch and make sure the response payload is drained buy reading remaining bytes before closing the transport",
            "refined_text": "We observed a steady socket leak during sustained load tests by reason of unclosed HTTP client response bodies in `client/gateway.py`. When outbound requests fail with status 500 or time out, the error handler returns early without closing the response stream.\n\nThis leaks underlying TCP sockets by leaving 84 idle file descriptors open until the operating system drops the connection pool. Socket starvation then blocks all subsequent outbound API calls by causing P99 latency to spike beyond 5 seconds.\n\nPlease ensure that response body close is guaranteed by using a try finally block immediately following request dispatch, and make sure the response payload is drained by reading remaining bytes before closing the transport."
        },
        # Domain 3 - Long 5 (SQL injection mitigation using parameterized queries & AST validation)
        {
            "raw_asr": "this pull request introduces a severe security vulnerability in repository slash search dot py buy building dynamic s q l filters using raw string format concatenat an attacker can supply malicious input through the search query parameter buy escaping the single quote delimiter and executing arbitrary database statements string interpolat in database queries must never be merged into production buy complying with our secure coding standards we need two replace all dynamic string concatenat buy using parameterized placeholder bindings supported buy post gres q l driver furthermore please add automated static analysis checks buy running bandit on the pull request pipeline two detect dangerous query construction before code review approval",
            "refined_text": "This pull request introduces a severe security vulnerability in `repository/search.py` by building dynamic SQL filters using raw string format concatenation. An attacker can supply malicious input through the search query parameter by escaping the single quote delimiter and executing arbitrary database statements.\n\nString interpolation in database queries must never be merged into production by complying with our secure coding standards. We need to replace all dynamic string concatenation by using parameterized placeholder bindings supported by PostgreSQL driver.\n\nFurthermore, please add automated static analysis checks by running Bandit on the pull request pipeline to detect dangerous query construction before code review approval."
        }
    ]
    return batch

def main():
    batch = build_batch()
    print(f"Total samples built: {len(batch)}")
    assert len(batch) == 20, f"Expected 20 samples, got {len(batch)}"

    # Save to scratch/subagent_batch_53.json
    out_path = Path("scratch/subagent_batch_53.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Saved batch to {out_path}\n")

    # Load sft_eval.json for leakage check
    with open("sft_eval.json", "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip() for e in eval_data}

    tier_counts = {"short": 0, "medium": 0, "long": 0}
    all_ok = True

    for idx, s in enumerate(batch, 1):
        raw = s["raw_asr"]
        ref = s["refined_text"]

        # ASCII check
        try:
            raw.encode("ascii")
            ref.encode("ascii")
        except UnicodeEncodeError as e:
            print(f"Sample {idx:02d}: UnicodeEncodeError: {e}")
            all_ok = False
            continue

        # Leakage check
        if raw.strip().lower() in eval_raws:
            print(f"Sample {idx:02d}: LEAKAGE FAIL (raw_asr in sft_eval.json)")
            all_ok = False
        if ref.strip() in eval_refs:
            print(f"Sample {idx:02d}: LEAKAGE FAIL (refined_text in sft_eval.json)")
            all_ok = False

        # Validator check
        v_ok, v_reason = validate_pair(s)
        # Cleaner check
        c_res, c_reason = clean_sample(raw, ref)

        ref_words = len(ref.split())
        raw_words = len(raw.split())
        ratio = ref_words / max(1, raw_words)

        if ref_words < 25:
            tier = "SHORT"
            tier_counts["short"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', ref) if sent.strip()]
            if len(sentences) != 1:
                print(f"Sample {idx:02d} [SHORT]: Sentence count mismatch: {len(sentences)} != 1")
                all_ok = False
            if "\n" in ref:
                print(f"Sample {idx:02d} [SHORT]: Unexpected newline in short sample")
                all_ok = False
        elif ref_words < 90:
            tier = "MEDIUM"
            tier_counts["medium"] += 1
            sentences = [sent for sent in re.split(r'[.!?]+', ref) if sent.strip()]
            if not (1 <= len(sentences) <= 3):
                print(f"Sample {idx:02d} [MEDIUM]: Sentence count mismatch: {len(sentences)} not in [1, 3]")
                all_ok = False
            if "\n\n" not in ref:
                print(f"Sample {idx:02d} [MEDIUM]: Missing \\n\\n in medium sample")
                all_ok = False
        else:
            tier = "LONG"
            tier_counts["long"] += 1
            if "\n\n" not in ref:
                print(f"Sample {idx:02d} [LONG]: Missing \\n\\n in long sample")
                all_ok = False

        if not (v_ok and c_res is not None):
            all_ok = False
            print(f"Sample {idx:02d} [{tier:6s}]: FAIL - validator: {v_reason}, cleaner: {c_reason}")
        else:
            print(f"Sample {idx:02d} [{tier:6s}]: PASS - words={ref_words:3d}, raw_words={raw_words:3d}, ratio={ratio:.2f}")

    print("\n--- Summary Tier Counts ---")
    print(f"Short:  {tier_counts['short']} / 4")
    print(f"Medium: {tier_counts['medium']} / 6")
    print(f"Long:   {tier_counts['long']} / 10")

    b_ok, b_reason, b_tiers = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
    print(f"\nvalidate_batch: {b_reason} (passed={b_ok})")

    if all_ok and b_ok and tier_counts == {"short": 4, "medium": 6, "long": 10}:
        print("\nAll 20 samples in Batch 53 passed ALL checks 100% cleanly!")
    else:
        print("\nBatch 53 failed some checks. Please inspect errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
