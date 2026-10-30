import json
import re
import sys

sys.path.append("code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

samples = [
    # ----------------------------------------------------
    # Tier 1: Short Utterances (< 25 words) - Exactly 4
    # ----------------------------------------------------
    # Sample 1: Kubernetes pod crash loops
    {
        "raw_asr": "um inspect the pod crash loop backoff state using cube ctl when the process terminat with exit code one three seven",
        "refined_text": "Inspect the pod crash loop backoff state using kubectl when the process terminates with exit code 137."
    },
    # Sample 2: Database deadlocks
    {
        "raw_asr": "uh isolat the database deadlock transaction buy inspecting active locks in the post gres catalog",
        "refined_text": "Isolate the database deadlock transaction by inspecting active locks in the PostgreSQL catalog."
    },
    # Sample 3: Envoy proxy connection timeouts
    {
        "raw_asr": "basically envoy returned status five zero four upstream request timeout when contacting the payment service knowed",
        "refined_text": "Envoy returned status 504 upstream request timeout when contacting the payment service node."
    },
    # Sample 4: Redis cluster partitions
    {
        "raw_asr": "restor redis cluster quorum buy connecting replica two master on port six three seven nine",
        "refined_text": "Restore Redis cluster quorum by connecting replica to master on port 6379."
    },

    # ----------------------------------------------------
    # Tier 2: Medium Utterances (25 to 90 words) - Exactly 6
    # ----------------------------------------------------
    # Sample 5: OOMKilled events & cgroup limits
    {
        "raw_asr": "basically the kernel oom killer terminat the analytics container under c group v two after resident memory exceeded the ceiling of two gigabytes wait four gigabytes instead we allocat additional memory limits in the pod manifest buy updating the memory request to four gigabytes",
        "refined_text": "The kernel OOM killer terminated the analytics container under cgroupv2 after resident memory exceeded the ceiling of 4 gigabytes instead.\n\nWe allocate additional memory limits in the pod manifest by updating the memory request to 4 gigabytes."
    },
    # Sample 6: DNS resolution timeouts
    {
        "raw_asr": "um the payment worker pods suffered intermittent d n s timeouts because coredns dropped requests under heavy query load configur the resolv conf ndots option to two wait one instead root the external domain queries through node local dns cache",
        "refined_text": "The payment worker pods suffered intermittent DNS timeouts because CoreDNS dropped requests under heavy query load. Configure the resolv conf ndots option to 1 instead.\n\nRoute the external domain queries through node local DNS cache."
    },
    # Sample 7: Memory leaks
    {
        "raw_asr": "the inventory service experienced a steady heap memory leak buy failing to close idle client connections before each request terminat inspect the memory profile buy analyzing heap allocat over eight hundred megabytes",
        "refined_text": "The inventory service experienced a steady heap memory leak by failing to close idle client connections before each request terminates.\n\nInspect the memory profile by analyzing heap allocations over 800 megabytes."
    },
    # Sample 8: Rollback procedures
    {
        "raw_asr": "okay so the automated canary rollout failed when error rates jumped to fifteen percent after deploying release candidate four execute a rollback buy running cube ctl rollout undo to revision four wait revision three instead restor the previous stable image tag across the cluster",
        "refined_text": "The automated canary rollout failed when error rates jumped to 15 percent after deploying release candidate 4. Execute a rollback by running kubectl rollout undo to revision 3 instead.\n\nRestore the previous stable image tag across the cluster."
    },
    # Sample 9: Database deadlocks
    {
        "raw_asr": "the catalog checkout service encountered transaction deadlocks under heavy concurrent write operat across multiple database worker knowed the post gres engine aborted the offending query with error code four zero zero zero one serialize the update statements across both tables to maintain consistent row lock ordering",
        "refined_text": "The catalog checkout service encountered transaction deadlocks under heavy concurrent write operation across multiple database worker nodes. The PostgreSQL engine aborted the offending query with error code 40001.\n\nSerialize the update statements across both tables to maintain consistent row lock ordering."
    },
    # Sample 10: Cascade failures
    {
        "raw_asr": "uh downstream payment gateway latency triggered a cascade failure across upstream api services buy exhausting available connection pools the ingress proxy terminat pending connections after queue utilization reached fifty percent wait seventy percent instead adjust the circuit breaker threshold to drop failing requests early",
        "refined_text": "Downstream payment gateway latency triggered a cascade failure across upstream API services by exhausting available connection pools. The ingress proxy terminated pending connections after queue utilization reached 70 percent instead.\n\nAdjust the circuit breaker threshold to drop failing requests early."
    },
]

print(f"Loaded {len(samples)} samples so far.")
for i, s in enumerate(samples, 1):
    v_ok, v_msg = validate_pair(s)
    c_res, c_msg = clean_sample(s["raw_asr"], s["refined_text"])
    w = len(s["refined_text"].split())
    raw_w = len(s["raw_asr"].split())
    ratio = w / max(1, raw_w)
    print(f"Sample {i:02d}: words={w:2d}, raw={raw_w:2d}, ratio={ratio:.2f}, val={v_ok} ({v_msg}), clean={c_res is not None} ({c_msg})")
