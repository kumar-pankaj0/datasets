import json
import sys
import os

sys.path.insert(0, "code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

BATCH_98 = [
  # --- Tier 1: Short Utterances (< 25 words) - Exactly 4 samples ---
  # Sample 1: Domain 1 (Sprint Planning)
  {
    "raw_asr": "basically allocat five story points four ticket c a c h e dash four two across our sprint backlog",
    "refined_text": "Allocate 5 story points for ticket CACHE-42 across our sprint backlog."
  },
  # Sample 2: Domain 1 (Story Grooming)
  {
    "raw_asr": "um estimat ticket b i l l dash eight eight buy dividing billing checkout into three granular user stories",
    "refined_text": "Estimate ticket BILL-88 by dividing billing checkout into three granular user stories."
  },
  # Sample 3: Domain 2 (Daily Standup)
  {
    "raw_asr": "okay so resolv the pending code review on p r dash two one four four authentication middleware updates",
    "refined_text": "Resolve the pending code review on PR-214 for authentication middleware updates."
  },
  # Sample 4: Domain 2 (Async Sync)
  {
    "raw_asr": "basically post the async standup status update confirming staging database schema synchronizat right after migration checks complete",
    "refined_text": "Post the async standup status update confirming staging database schema synchronization right after migration checks complete."
  },

  # --- Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples ---
  # Sample 5: Domain 1 (Sprint Planning)
  {
    "raw_asr": "um calibrat sprint capacity buy adjusting our velocity target forty five wait target thirty eight story points across our ten day iteration window we allocat twenty points four backend services and eighteen points four frontend components tracking ticket f r o n t dash five zero",
    "refined_text": "Calibrate sprint capacity by adjusting our velocity target to 38 story points across our 10 day iteration window.\n\nWe allocate 20 points for backend services and 18 points for frontend components, tracking ticket FRONT-50."
  },
  # Sample 6: Domain 1 (Story Grooming)
  {
    "raw_asr": "okay so validat acceptance criteria four ticket a p i dash one one zero buy defining cursor pagination rules across user query results wait return fifty records per page while asserting response payloads match our j son schema definition",
    "refined_text": "Validate acceptance criteria for ticket API-110 by defining cursor pagination rules across user query results.\n\nReturn 50 records per page while asserting response payloads match our JSON schema definition."
  },
  # Sample 7: Domain 1 (Sprint Planning)
  {
    "raw_asr": "basically prioritiz technical debt ticket s e c dash two zero five inside sprint thirty four buy removing deprecated session cookies wait right unit test assertions covering session renewal from one through three retry cycles",
    "refined_text": "Prioritize technical debt ticket SEC-205 inside sprint 34 by removing deprecated session cookies.\n\nWrite unit test assertions covering session renewal from 1 through 3 retry cycles."
  },
  # Sample 8: Domain 2 (Daily Standup)
  {
    "raw_asr": "um unblock staging integration tests buy addressing connection timeouts on database read knowed replicas wait ticket d a t a dash six five wait ticket d a t a dash seven zero tracks the slow query pool reaching eighty percent connection saturation",
    "refined_text": "Unblock staging integration tests by addressing connection timeouts on database read node replicas.\n\nTicket DATA-70 tracks the slow query pool reaching 80 percent connection saturation."
  },
  # Sample 9: Domain 2 (Async Sync)
  {
    "raw_asr": "okay so hand off secondary on call triage duties two the european engineering squad buy posting incident notes into the operations channel wait review p r dash three zero five which resolves four hundred bad request responses across authentication endpoints",
    "refined_text": "Hand off secondary on-call triage duties to the European engineering squad by posting incident notes into the operations channel.\n\nReview PR-305, which resolves 400 bad request responses across authentication endpoints."
  },
  # Sample 10: Domain 2 (Daily Standup)
  {
    "raw_asr": "basically isolat flaky end two end checkout tests four ticket t e s t dash four one two buy stabilizing asynchronous redis locking mechanisms across staging clusters wait fourteen test suite runs now pass cleanly without encountering race conditions or execution timeouts in our c i pipeline",
    "refined_text": "Isolate flaky end-to-end checkout tests for ticket TEST-412 by stabilizing asynchronous Redis locking mechanisms across staging clusters.\n\nFourteen test suite runs now pass cleanly without encountering race conditions or execution timeouts in our CI pipeline."
  },

  # --- Tier 3: Long Utterances (90+ words) - Exactly 10 samples ---
  # Sample 11: Domain 1 (Sprint Planning)
  {
    "raw_asr": "basically break down the billing reconciliation epic buy splitting ticket b i l l dash three zero zero into three discrete engineering tasks during sprint planning our team reviews historical invoice generation failures where asynchronous ledger synchronization stalled across previous billing cycles we allocat three story points four ticket c o r e dash one zero one covering read only database transaction locks and five story points four ticket c o r e dash one zero two implementing idempotent stripe webhook handlers okay so estimat five wait estimat eight story points four ticket c o r e dash one zero three covering automated reconciliation scripts and telemetry error alerts buy establishing clear definition of done acceptance criteria the squad commits sixteen total story points across the upcoming two week iteration window maintaining steady delivery momentum without exceeding our scheduled capacity budget",
    "refined_text": "Break down the billing reconciliation epic by splitting ticket BILL-300 into three discrete engineering tasks during sprint planning. Our team reviews historical invoice generation failures where asynchronous ledger synchronization stalled across previous billing cycles. We allocate 3 story points for ticket CORE-101 covering read-only database transaction locks, and 5 story points for ticket CORE-102 implementing idempotent Stripe webhook handlers.\n\nEstimate 8 story points for ticket CORE-103 covering automated reconciliation scripts and telemetry error alerts. By establishing clear definition of done acceptance criteria, the squad commits 16 total story points across the upcoming two-week iteration window, maintaining steady delivery momentum without exceeding our scheduled capacity budget."
  },
  # Sample 12: Domain 1 (Story Grooming)
  {
    "raw_asr": "um groom cross team dependencies four ticket g a t e dash five zero one buy establishing explicit open a p i contract definitions between frontend and backend squads the mobile client requires predictable nested json responses during product catalog searches buy validating schemas early we unblock ticket f r o n t dash two two zero and eliminate downstream integration bottlenecks across staging clusters basically configur gateway timeout boundaries target three hundred wait target two hundred milliseconds four product search queries returning fifty items per page backend engineers commit five story points towards mock server implementations buy deploying synthetic endpoints within forty eight hours four frontend test verification both teams establish strict error schema contracts returning status four hundred bad request and status four zero four not found with uniform debugging payloads",
    "refined_text": "Groom cross-team dependencies for ticket GATE-501 by establishing explicit OpenAPI contract definitions between frontend and backend squads. The mobile client requires predictable nested JSON responses during product catalog searches. By validating schemas early, we unblock ticket FRONT-220 and eliminate downstream integration bottlenecks across staging clusters.\n\nConfigure gateway timeout boundaries towards 200 milliseconds for product search queries returning 50 items per page. Backend engineers commit 5 story points towards mock server implementations by deploying synthetic endpoints within 48 hours for frontend test verification. Both teams establish strict error schema contracts, returning status 400 Bad Request and status 404 Not Found with uniform debugging payloads."
  },
  # Sample 13: Domain 1 (Sprint Planning)
  {
    "raw_asr": "okay so assess deployment risk four ticket d b dash six two zero buy grooming table partitioning steps across our post gres audit logs table storing eighty million historical rows large table writes during peak traffic hours cause connection lock exhaustion on database master replicas we allocat eight wait allocat thirteen story points divided across two phased sprint milestones phase one tackles five story points buy creating monthly partition tables and backfilling indexes during a four hour scheduled maintenance window phase two covers eight story points buy executing continuous background worker sync and validating data integrity using automated checksum assertions buy maintaining shadow table writes we preserve live read traffic without introducing application query downtime",
    "refined_text": "Assess deployment risk for ticket DB-620 by grooming table partitioning steps across our Postgres audit logs table storing 80000000 historical rows. Large table writes during peak traffic hours cause connection lock exhaustion on database master replicas. We allocate 13 story points divided across two phased sprint milestones.\n\nPhase 1 tackles 5 story points by creating monthly partition tables and backfilling indexes during a 4 hour scheduled maintenance window. Phase 2 covers 8 story points by executing continuous background worker sync and validating data integrity using automated checksum assertions. By maintaining shadow table writes, we preserve live read traffic without introducing application query downtime."
  },
  # Sample 14: Domain 1 (Story Grooming)
  {
    "raw_asr": "basically refine acceptance criteria four security hardening ticket s e c dash seven one zero during story grooming our infrastructure squad must configur automated o auth two token rotation across internal microservice communication channels storing refresh secrets inside encrypted vaults rather than environment variables we establish explicit definition of done guidelines requiring integration tests four token expiration scenarios and automated vulnerability scans across dependencies um enforce code coverage standards target ninety wait target ninety five percent before merging branches into production releases and updating security architecture documentat backend engineers size this story at eight story points buy carving out three points four mock identity provider harnesses and five points four production middleware interceptors",
    "refined_text": "Refine acceptance criteria for security hardening ticket SEC-710 during story grooming. Our infrastructure squad must configure automated OAuth2 token rotation across internal microservice communication channels, storing refresh secrets inside encrypted vaults rather than environment variables. We establish explicit definition of done guidelines requiring integration tests for token expiration scenarios and automated vulnerability scans across dependencies.\n\nEnforce code coverage standards towards 95 percent before merging branches into production releases and updating security architecture documentation. Backend engineers size this story at 8 story points by carving out 3 points for mock identity provider harnesses and 5 points for production middleware interceptors."
  },
  # Sample 15: Domain 1 (Sprint Planning)
  {
    "raw_asr": "okay so calibrat team velocity and capacity boundaries four sprint forty eight during our sprint planning session with six active software engineers our gross velocity averages sixty four story points across normal two week iterations accounting four scheduled holidays and planned paid time off we reserve sixteen story points as dedicated buffer four on call operational triage and unbudgeted production bug fixes um prioritiz remaining delivery capacity target fifty wait target forty eight story points dedicated towards roadmap commitments we allocat thirty points towards search ranking improvements and eighteen points towards merchant invoicing workflows establishing clear sprint goals buy protecting the team against mid sprint scope creep",
    "refined_text": "Calibrate team velocity and capacity boundaries for sprint 48 during our sprint planning session. With 6 active software engineers, our gross velocity averages 64 story points across normal two-week iterations. Accounting for scheduled holidays and planned paid time off, we reserve 16 story points as dedicated buffer for on-call operational triage and unbudgeted production bug fixes.\n\nPrioritize remaining delivery capacity towards 48 story points dedicated towards roadmap commitments. We allocate 30 points towards search ranking improvements and 18 points towards merchant invoicing workflows, establishing clear sprint goals by protecting the team against mid-sprint scope creep."
  },
  # Sample 16: Domain 2 (Daily Standup)
  {
    "raw_asr": "basically report a critical blocker during today standup regarding staging merge queue failures following deployment of p r dash eight zero one automated smoke tests failed across our ingress gateway buy triggering five zero two bad gateway status errors on authentication requests twelve downstream pull requests remain stalled behind this failed release candidate um unblock the staging merge queue buy executing an immediate rollback revert commit seven zero eight wait revert commit seven one nine which restores stable proxy routing configurations we investigat the underlying defect inside staging logs where misconfigured upstream timeouts terminated active client connections during container initialization once the staging cluster recovers the q a team will rerun automated integration suites across all waiting branches",
    "refined_text": "Report a critical blocker during today's standup regarding staging merge queue failures following deployment of PR-801. Automated smoke tests failed across our ingress gateway by triggering 502 Bad Gateway status errors on authentication requests. Twelve downstream pull requests remain stalled behind this failed release candidate.\n\nUnblock the staging merge queue by executing an immediate rollback: revert commit 719, which restores stable proxy routing configurations. We investigate the underlying defect inside staging logs where misconfigured upstream timeouts terminated active client connections during container initialization. Once the staging cluster recovers, the QA team will rerun automated integration suites across all waiting branches."
  },
  # Sample 17: Domain 2 (Async Sync)
  {
    "raw_asr": "okay so publish an async engineering handoff update regarding production incident i n c dash four zero nine inside our global operations channel the ingress gateway proxy experienced progressive memory leaks triggering out of memory container kills whenever client connections reached eighty five percent capacity we stabilized cluster operations buy executing rolling restarts restart eight wait restart twelve worker pods across regional availability zones mitigating immediate latency degradation um document active follow up action items four the incoming a p a c engineering squad buy assigning four post incident remediation tasks our primary focus is right unit assertions validating buffer releases during truncated client requests and scheduling a detailed retrospective meeting tomorrow morning at nine hundred hours",
    "refined_text": "Publish an async engineering handoff update regarding production incident INC-409 inside our global operations channel. The ingress gateway proxy experienced progressive memory leaks, triggering out-of-memory container kills whenever client connections reached 85 percent capacity. We stabilized cluster operations by executing rolling restarts: restart 12 worker pods across regional availability zones, mitigating immediate latency degradation.\n\nDocument active follow-up action items for the incoming APAC engineering squad by assigning 4 post-incident remediation tasks. Our primary focus is to write unit assertions validating buffer releases during truncated client requests, and scheduling a detailed retrospective meeting tomorrow morning at 900 hours."
  },
  # Sample 18: Domain 2 (Daily Standup)
  {
    "raw_asr": "basically deliver today standup progress update on the authentication microservice refactoring under ticket a u t h dash three three zero yesterday we completed the migration of json web token validation pipelines from legacy monolith nodes into our dedicated auth service buy eliminating redundant database lookups on authenticated requests we reduced token verification latency buy fifty percent across five hundred concurrent requests per second um unblock the mobile platform squad buy publishing updated token verification client libraries on p r dash five one two today i will address four wait address two remaining review comments regarding cryptographic key rotation timeouts before requesting final approval from our security lead and scheduling production deployment four tomorrow afternoon",
    "refined_text": "Deliver today's standup progress update on the authentication microservice refactoring under ticket AUTH-330. Yesterday, we completed the migration of JSON Web Token validation pipelines from legacy monolith nodes into our dedicated auth service. By eliminating redundant database lookups on authenticated requests, we reduced token verification latency by 50 percent across 500 concurrent requests per second.\n\nUnblock the mobile platform squad by publishing updated token verification client libraries on PR-512. Today, I will address 2 remaining review comments regarding cryptographic key rotation timeouts before requesting final approval from our security lead and scheduling production deployment for tomorrow afternoon."
  },
  # Sample 19: Domain 2 (Async Sync)
  {
    "raw_asr": "okay so post an async triage summary regarding regional latency regressions tracked under ticket p e r f dash nine zero two across our engineering channels telemetry monitors alerted on p ninety nine query response times degrading from eighty five milliseconds up through two hundred forty milliseconds in the us east cluster during peak morning traffic distributed tracing revealed database connection pool starvation across read knowed instances buy investigating slow transaction locks we identified an unindexed tenant filtering query um deploy a targeted hotfix hotfix commit six one zero wait hotfix commit six two five which introduces composite database indexes and raises connection pool limits from twenty through forty connections backend engineers will monitor performance dashboards through one six zero zero hours before declaring incident resolution",
    "refined_text": "Post an async triage summary regarding regional latency regressions tracked under ticket PERF-902 across our engineering channels. Telemetry monitors alerted on P99 query response times degrading from 85 milliseconds up through 240 milliseconds in the US-East cluster during peak morning traffic. Distributed tracing revealed database connection pool starvation across read node instances. By investigating slow transaction locks, we identified an unindexed tenant filtering query.\n\nDeploy a targeted hotfix: hotfix commit 625, which introduces composite database indexes and raises connection pool limits from 20 through 40 connections. Backend engineers will monitor performance dashboards through 1600 hours before declaring incident resolution."
  },
  # Sample 20: Domain 2 (Daily Standup)
  {
    "raw_asr": "basically outline our daily standup status regarding event stream processing delays logged under ticket s t r e a m dash four five zero during night batch processing heavy ingestion spikes caused consumer partition lag two reach fifteen thousand pending records on our clickstream telemetry topic serialization timeouts stalled downstream database ingestion buy locking worker threads across event processing knowed instances um mitigat consumer group lag buy scaling worker pods scale consumer replicas from four through eight wait from four through twelve replicas while optimizing batch commit intervals down into five zero zero milliseconds within twenty minutes total partition lag dropped down into zero records restoring normal real time pipeline processing without dropping user events",
    "refined_text": "Outline our daily standup status regarding event stream processing delays logged under ticket STREAM-450. During night batch processing, heavy ingestion spikes caused consumer partition lag to reach 15000 pending records on our clickstream telemetry topic. Serialization timeouts stalled downstream database ingestion by locking worker threads across event processing node instances.\n\nMitigate consumer group lag by scaling worker pods: scale consumer replicas from 4 through 12 replicas while optimizing batch commit intervals down into 500 milliseconds. Within 20 minutes, total partition lag dropped down into 0 records, restoring normal real-time pipeline processing without dropping user events."
  }
]

def main():
    print(f"Total candidate pairs: {len(BATCH_98)}")
    assert len(BATCH_98) == 20, f"Expected 20 samples, got {len(BATCH_98)}"

    pair_errors = 0
    clean_errors = 0

    for idx, pair in enumerate(BATCH_98):
        raw = pair["raw_asr"]
        ref = pair["refined_text"]
        w_count = len(ref.split())

        val_ok, val_reason = validate_pair(pair)
        if not val_ok:
            print(f"Sample {idx+1} failed validate_pair: {val_reason}")
            pair_errors += 1

        clean_res, clean_status = clean_sample(raw, ref)
        if clean_status != "kept":
            print(f"Sample {idx+1} failed clean_sample: {clean_status}")
            clean_errors += 1

        tier = "short" if w_count < 25 else ("medium" if w_count < 90 else "long")
        print(f"Sample {idx+1:02d}: tier={tier:<6} words={w_count:<3} val={'OK' if val_ok else 'FAIL'} clean={clean_status}")

    batch_ok, batch_msg, tier_counts = validate_batch(BATCH_98, min_short=4, min_medium=6, min_long=10)
    print("\n--- Batch Validation Summary ---")
    print(f"Batch validation status: {batch_ok} ({batch_msg})")
    print(f"Tier counts: {tier_counts}")
    print(f"Pair errors: {pair_errors}, Cleaner errors: {clean_errors}")

    if pair_errors == 0 and clean_errors == 0 and batch_ok:
        output_path = "scratch/subagent_batch_98.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(BATCH_98, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully wrote 20 verified samples to {output_path}")
    else:
        print("\nValidation failed! Please fix errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
