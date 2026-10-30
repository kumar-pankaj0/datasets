import sys
import json
import re

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

def test_single(idx, raw, ref):
    pair = {"raw_asr": raw, "refined_text": ref}
    v_ok, v_msg = validate_pair(pair)
    c_res, c_msg = clean_sample(raw, ref)
    words = len(ref.split())
    raw_words = len(raw.split())
    ratio = words / max(1, raw_words)
    print(f"Sample {idx}: words={words}, raw={raw_words}, ratio={ratio:.2f}")
    if not v_ok:
        print(f"  [VALIDATOR FAIL] {v_msg}")
    else:
        print(f"  [VALIDATOR OK]")
    if c_msg != "kept":
        print(f"  [CLEANER FAIL] {c_msg}")
    else:
        print(f"  [CLEANER OK]")
    return v_ok and (c_msg == "kept")

raw_s1 = "uh the redis connection pool exhaust all available client sockets during peak checkout traffic"
ref_s1 = "The Redis connection pool exhausted all available client sockets during peak checkout traffic."
test_single(1, raw_s1, ref_s1)

raw_l1 = ("uh at zero nine thirty the checkout microservice experienced an abrupt surge in error rates during the morning sale "
          "downstream payment partner endpoints increased p ninety nine response latenc from one hundred milliseconds two four thousand milliseconds "
          "which caused local connection pools two exhaust all sixty worker threads basically incoming checkout requests accumulated in edge reverse proxy buffers "
          "until five zero four gateway timeout errors reached eight hundred failures per second\n\n"
          "the incident response squad identified thread starvation inside the payment connector container runtime worker threads were blocked waiting on synchronous socket reads "
          "without an explicit read timeout buy zero nine forty five engineers applied a hotfix buy setting socket read timeouts two eight hundred milliseconds "
          "and enabling connection pooling circuit breakers\n\n"
          "the mitigation immediately isolated the stalled partner traffic and dropped error rates back two zero by ten zero zero "
          "the postmortem action items require migrating the synchronous payment connector two an a sink non blocking client model "
          "and configuring fallback responses four downstream partner degradation").replace("\n\n", " ")

ref_l1 = ("At 0930 the checkout microservice experienced an abrupt surge in error rates during the morning sale. "
          "Downstream payment partner endpoints increased P99 response latency from 100 milliseconds to 4000 milliseconds, "
          "which caused local connection pools to exhaust all 60 worker threads. "
          "Incoming checkout requests accumulated in edge reverse proxy buffers until 504 gateway timeout errors reached 800 failures per second.\n\n"
          "The incident response squad identified thread starvation inside the payment connector container runtime. "
          "Worker threads were blocked waiting on synchronous socket reads without an explicit read timeout. "
          "By 0945 engineers applied a hotfix by setting socket read timeouts to 800 milliseconds and enabling connection pooling circuit breakers.\n\n"
          "The mitigation immediately isolated the stalled partner traffic and dropped error rates back to zero by 1000. "
          "The postmortem action items require migrating the synchronous payment connector to an async non-blocking client model "
          "and configuring fallback responses for downstream partner degradation.")

test_single("L1", raw_l1, ref_l1)

raw_l2 = ("basically at fourteen twenty during a rolling deployment of the product catalog service an unverified cache invalidation routine purged all redis session keys rather than the target category namespace downstream post gres primary and replica nodes experienced fifteen thousand cache misses per second which drove database c p u utilization two ninety eight percent p ninety five query latenc climbed from fifteen milliseconds two one thousand two hundred milliseconds within four minutes "
          "the database connection pool on six catalog worker pods exhaust all fifty available connections causing edge gateways two return status five hundred internal server errors on thirty percent of incoming browsing requests the incident team executed an immediate rollback of the deployment buy running cube ctl rollout undo deployment product catalog dash service two version two dot four dot zero wait version two dot four dot zero instead "
          "after rolling back the release operators recycled the saturated database connections and increased post gres read replicas from four two eight nodes normal response latenc returned buy fourteen forty five follow up action items include implementing rigorous integration tests four cache invalidation patterns and setting query execution timeout limits two five hundred milliseconds")

ref_l2 = ("At 1420 during a rolling deployment of the product catalog service, an unverified cache invalidation routine purged all Redis session keys rather than the target category namespace. Downstream Postgres primary and replica nodes experienced 15000 cache misses per second, which drove database CPU utilization to 98 percent. P95 query latency climbed from 15 milliseconds to 1200 milliseconds within 4 minutes.\n\n"
          "The database connection pool on 6 catalog worker pods exhausted all 50 available connections, causing edge gateways to return status 500 Internal Server Errors on 30 percent of incoming browsing requests. The incident team executed an immediate rollback of the deployment by running `kubectl rollout undo deployment product-catalog-service` to version 2.4.0 instead.\n\n"
          "After rolling back the release, operators recycled the saturated database connections and increased Postgres read replicas from 4 to 8 nodes. Normal response latency returned by 1445. Follow-up action items include implementing rigorous integration tests for cache invalidation patterns and setting query execution timeout limits to 500 milliseconds.")

test_single("L2", raw_l2, ref_l2)
