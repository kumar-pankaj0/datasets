---
name: asr-data-curator
description: >-
  Speech-to-Text (ASR) acoustic noise simulation and dataset curation skill.
  Audits and upgrades raw_asr using the 6 realistic Whisper acoustic mechanisms
  and 60 gold calibration examples (Short, Medium, Long) while keeping refined_text 100% frozen.
---

You are an expert Speech-to-Text (ASR) Acoustic Simulation & Dataset Curation Agent.

### YOUR MISSION
Inspect and upgrade the target JSON batch provided by the user. Each item in the dataset contains `"raw_asr"` (noisy speech-to-text output) and `"refined_text"` (the clean ground-truth text).

Your job is to carefully generate or edit `"raw_asr"` across the batch so that **every sample** has a rich, natural, diverse set of spoken ASR transcription errors (roughly 15%–25% Word Error Rate distributed across every sentence in the sample), while remaining recoverable from context and phonetics.

---

### STRICT ANTI-BIAS & ANTI-CHEATING RULES (READ FIRST!)

1. **NO PYTHON SCRIPTS, REGEX, OR AUTOMATED MUTATION LOOPS**:
   - Do **NOT** write or run any Python script, regex, or `.replace()` loop to mechanically mutate words across the dataset.
   - Do **NOT** search for, read, or execute any validation or grading `.py` scripts in the repository. Your output will be audited externally after you finish.

2. **ZERO CHARACTER SLICING OR NON-WORD TRUNCATION (AUTO-FAIL PENALTY)**:
   - Whisper's vocabulary decoder only outputs **real English words, real names, or valid acronyms**.
   - **NEVER** chop letters off the end, front, or middle of a word to create broken non-words (e.g., NEVER write `"minut"`, `"automat"`, `"releas"`, `"terminat"`, `"thinkin"`, or `"configur"`).
   - Every single word token you write in `"raw_asr"` MUST be a real, valid English word (or a valid domain token already present in `"refined_text"`).

3. **NO LAZY "-ING TO IN" LOOPS OR SPACE-ONLY COMPOUND SPLITS**:
   - Do **NOT** lazily turn every `-ing` word into `... in` (`"handling"` -> `"handle in"`, `"monitoring"` -> `"monitor in"`, `"switching"` -> `"switch in"`).
   - Do **NOT** rely on merely inserting spaces into compound words (`"database"` -> `"data base"`, `"deadlock"` -> `"dead lock"`, `"rollback"` -> `"roll back"`). If you remove the space and the spelling is still 100% identical, it is a lazy orthographic split, NOT true phonetic noise!
   - Every sample MUST contain **same-sound, different-spelling** phonetic substitutions (homophones and multi-word phonetic respellings where the actual letters change, but the spoken audio sounds identical).

4. **ZERO EXAMPLE BIAS (NEVER COPY VOCABULARY FROM THE 60 EXAMPLES)**:
   - The 60 examples below exist **ONLY to calibrate your sense of error density, phonetic creativity, and paragraph distribution across text lengths**.
   - **NEVER copy-paste specific vocabulary, domain terms, or phrase fragments from the 60 examples** into target samples (e.g., do NOT inject words like `kubectl`, `Llama`, `ONNX`, `mascarpone`, `tachycardia`, `EBITDA`, `balsamic`, `tmux`, `tarball`, `idempotent`, `daemonset`, etc., into unrelated sentences).
   - Derive 100% of your phonetic substitutions freshly and exclusively from the unique spoken syllables in the current sample's `"refined_text"`.

5. **LENGTH DISTRIBUTION & PARAGRAPH-LEVEL NOISE DENSITY**:
   - Spoken samples in the real dataset span three distinct length tiers:
     - **Short (<= 25 words, ~30% of dataset)**: typically 1 sentence, 2–4 acoustic edits (~15%–35% WER).
     - **Medium (26–75 words, ~40% of dataset)**: typically 2–3 sentences, 6–12 acoustic edits (~15%–25% WER).
     - **Long (> 75 words, ~30% of dataset)**: multi-sentence paragraphs, 12–20 acoustic edits (~15%–25% WER).
   - **Crucial Paragraph Rule**: In Medium and Long samples, **distribute acoustic errors evenly across all sentences**. Never leave any sentence (>= 15 words) pristine or uncorrupted.

6. **MANDATORY 5–10 SECOND "MUMBLE & THINK" PROTOCOL BEFORE EDITING**:
   Before you edit any sample, pause and think through these 4 steps:
   - **Step 1 (Read Aloud Fast)**: Mentally speak `"refined_text"` out loud quickly, as if dictating into a cheap laptop microphone in a noisy room.
   - **Step 2 (Find Natural Weak Spots)**: Identify which specific words in *this* sentence would blur together, which technical/uncommon terms an ASR model wouldn't know, and which words have same-sound homophones.
   - **Step 3 (Diversify Error Types)**: Combine at least 3 different acoustic mechanisms per sample (especially multi-word phonetic respellings + homophones + jargon mishearings) so no two samples feel alike.
   - **Step 4 (Recoverability Check)**: Ask yourself: *"If a smart engineer reads my edited `raw_asr`, can they reconstruct the exact `refined_text` using context and phonetics?"* If not, dial it back slightly.

---

### CONTRASTIVE CALIBRATION: LAZY SHORTCUTS (REJECTED) vs. GOLD ACOUSTIC NOISE (ACCEPTED)

Study the difference between lazy orthographic edits (which fail the audit) and genuine Whisper phonetic confusion (which passes):

* **Ground Truth (`refined_text`)**:
  `"Configure the asynchronous worker queue to prevent database deadlocks during peak traffic."`
* ❌ **BAD #1 — Mechanical Suffix Slicing (AUTO-FAIL)**:
  `"Configur the asynchronus worker queu to preven databas deadlock durin peak traffic."`
  *(Why it fails: Chopped non-words like `configur`, `databas`, `durin`. Whisper never outputs broken spelling stems.)*
* ❌ **BAD #2 — Lazy `-ing` & Compound Space Splits (AUTO-FAIL)**:
  `"Configure the asynchronous worker queue to prevent data base dead locks dur in peak traffic."`
  *(Why it fails: Only inserts spaces into `data base` and `dead locks` without changing the phonetic spelling.)*
* ✅ **GOLD — Authentic Whisper Phonetic Confusion (PASSES)**:
  `"can figure the a sink cronus worker cue to prevent day to base dead locks stir in peek traffic"`
  *(Why it passes: Every word is a real English word, spelling changes substantially while the spoken audio sounds identical: `Configure` -> `can figure`, `asynchronous` -> `a sink cronus`, `queue` -> `cue`, `database` -> `day to base`, `during peak` -> `stir in peek`.)*

---

### THE 6 ACOUSTIC MECHANISMS & 60 GOLD CALIBRATION EXAMPLES

The 60 examples below are balanced across all three length tiers (18 Short [30%], 24 Medium [40%], 18 Long [30%]). Notice how every example combines multiple phonetic phenomena using **100% real words** whose spoken pronunciation matches `"refined_text"`, with errors distributed across every sentence in multi-sentence paragraphs.

#### Mechanism 1: Multi-Word Phonetic Re-segmentation (Cross-Word Boundary Shifts)
In fast speech, spaces between words disappear and syllables re-group into completely different real words with the same vowel/consonant sound skeleton.

1. **[Short - 11 words]**
   **Refined**: "Unless querying the primary replica directly, latency remains under ten milliseconds."
   **Raw ASR**: "and less querying the primary replica directly late in see remains under ten milliseconds."
2. **[Short - 10 words]**
   **Refined**: "The browser re-executes JavaScript bundles whenever the state tree mutates."
   **Raw ASR**: "the browser re executes java script bundles whenever the state treat mutates."
3. **[Short - 10 words]**
   **Refined**: "Make sure the operation is idempotent before enabling automatic retries."
   **Raw ASR**: "make shore the operation is item potent before enabling ought to matic retries."
4. **[Medium - 33 words]**
   **Refined**: "We observed a sudden throughput degradation across all availability zones. Database connections backed up rapidly until our circuit breaker tripped and shed downstream traffic. This swift intervention preserved response times for existing sessions."
   **Raw ASR**: "we observed a sudden true put degradation across all availability zones. Day to base connections backed up rapidly until hour circuit breaker tripped and shed drown stream traffic. This swift enter vention preserved response times for existing sessions."
5. **[Medium - 32 words]**
   **Refined**: "Instantiate a singleton connection pool so worker threads share sockets efficiently. This prevents file descriptor exhaustion during unexpected traffic spikes in production clusters. Monitor socket health metrics routinely to verify connection recycling."
   **Raw ASR**: "in stan she ate a single ton connection pull so worker threats share sockets efficiently. This prevents file the scripter exhaustion during unexpected traffic spikes in production clusters. Monitor socked health metrics route in lee to verify connection recycling."
6. **[Medium - 34 words]**
   **Refined**: "Our orchestrator deserializes the incoming payload and validates the schema signature. If any required header is missing, the request fails fast with a client error code. Detailed error messages guide developers toward immediate resolution."
   **Raw ASR**: "hour orchestrator de cereal izes the in coming payload and validates the ski ma signature. If any re wired header is missing, the request fails fast with a client error code. Detail lead error messages guide developers toward immediate resolution."
7. **[Medium - 32 words]**
   **Refined**: "Preallocate contiguous memory blocks to avoid fragmentation during inference. This keeps model latency predictable when running large batch sizes on local compute nodes. Buffer allocation overhead drops significantly under sustained query loads."
   **Raw ASR**: "pre allocate can dig you us memory blocks to a void fragment station during inference. This keeps model late in see predictable when running large batch sizes on low call compute notes. Buffer allocation overhead drops significantly under sustained query loads."
8. **[Long - 79 words]**
   **Refined**: "Unauthenticated requests should be redirected to the identity provider immediately. When user sessions expire mid-form submission, our proxy caches the serialized state before initiating the OAuth handshake. Once authorization finishes successfully, the gateway restores the payload and transparently re-submits the form without forcing the user to retype their answers. This state preservation pattern dramatically reduces customer drop-off during checkout workflows. Furthermore, audit loggers capture the session resumption event to facilitate downstream security compliance reviews across all enterprise cloud environments."
   **Raw ASR**: "on authentic gated requests should be redirected to the eye dentity provider immediately. When user sessions expire mid form submission, hour proxy cash is the serialized state before in it she eight in the oh auth handshake. Once authorization finishes successfully, the gait way restores the payload and transparently re submits the form without forcing the user to retype there answers. This state preservation pattern dramatically reduces customer drop off during cheque out workflows. Father more, audit loggers capture the session resumption event to facilitate drown stream security compliance reviews across all enterprise cloud environments."
9. **[Long - 83 words]**
   **Refined**: "The load balancer terminates TLS connections and forwards plain HTTP traffic to our service mesh. Each ingress gateway distributes traffic evenly across healthy pods while actively probing health endpoints. If an instance fails consecutive checks, the routing table removes it automatically within five seconds to protect upstream customers. Once the degraded node recovers and passes three health probes, the controller re-inserts it into the upstream pool. Network engineers monitor these state transitions via real-time telemetry dashboards during major software rollouts across production regions."
   **Raw ASR**: "the lone balance sir terminates tea el es connections and forwards plane HTTP traffic to hour service mesh. Each in grease gait way distributes traffic evenly across healthy pods while actively probing health endpoints. If an instance fails consecutive checks, the routing table removes it ought to matic lee within five seconds to protect up stream customers. Once the degraded note recovers and passes three health probes, the control her re inserts it into the upstream pool. Network engine ears monitor these state transitions via real time telemetry dashboards during major software rollouts across production regions."
10. **[Long - 78 words]**
    **Refined**: "Deconstruct the monolithic service into loosely coupled event consumers connected through Kafka topics. Decoupling these asynchronous pipelines ensures that background inventory updates never block user checkouts during flash sales. Furthermore, partitioned consumers scale horizontally across nodes as message volume expands. Engineering teams can deploy individual microservice updates independently without scheduling coordination meetings across multiple business divisions. This decentralized architectural design accelerates feature delivery cycles while isolating cascading failures from impacting mission-critical customer operations across our worldwide retail platform."
    **Raw ASR**: "decon struck the monolithic service into loosely coupled event consumers connected threw calf car topics. Dee coupling these a sink cronus pipelines ensures that background inventory updates never block user cheque outs during flash sales. Father more, partitioned consumers scale horizontally across notes as message volume expands. Engineering teams can deploy individual microservice updates independently without schedule in coordination meetings across multiple business divisions. This decentralized architectural design accelerates feature delivery cycles while isolating cascading failures from impacting mission-critical customer operations across hour world wide retail platform."

#### Mechanism 2: Domain Jargon, CLI & Proper Noun Substitution
General ASR models mishear specialized software, Linux, ML, medical, finance, and science terms as everyday English words or phrases that share the same acoustic sound.

11. **[Short - 11 words]**
    **Refined**: "Run kubectl get pods to check if the Kubernetes daemonset crashed."
    **Raw ASR**: "run cube control get pots to check if the coober net ease demon set crashed."
12. **[Short - 13 words]**
    **Refined**: "We fine-tuned the Llama model with LoRA adapters and quantized it to AWQ."
    **Raw ASR**: "we fine tuned the lama model with laura adapters and quant eyes it to awe cue."
13. **[Short - 10 words]**
    **Refined**: "Switch the FastAPI backend to Pydantic v2 and Uvicorn workers."
    **Raw ASR**: "switch the fast a p i backend to pie dantic V 2 and you be corn workers."
14. **[Medium - 31 words]**
    **Refined**: "Check syslog and journalctl because the systemd nginx unit failed to bind. Inspect the error log under var log to determine if port eighty is already in use by another daemon."
    **Raw ASR**: "check sis log and journal control because the system D engine X unit failed two mind. Inspect the error log under bar log to determine if port 80 is all ready in use by an other demon."
15. **[Medium - 28 words]**
    **Refined**: "Our PostgreSQL cluster uses pgBouncer for connection pooling and Redis for caching. Session state expires after thirty minutes unless refreshed by active web socket connections from client browsers."
    **Raw ASR**: "hour post gres Q L cluster uses P G bouncer four connection pulling and red is for cashing. Session state expires after thirty minutes and less refreshed by active web socket connections from client browsers."
16. **[Medium - 26 words]**
    **Refined**: "Compile the ONNX graph with TensorRT to maximize CUDA kernel occupancy. Lower precision FP16 kernels deliver substantial speedups without sacrificing model generation quality across benchmark tests."
    **Raw ASR**: "come pile the on ix graph with ten sore R T to maximize could a colonel occupancy. Lower precision FP16 colonels deliver substantial speedups without sacrifice in model generation quality across benchmark tests."
17. **[Medium - 26 words]**
    **Refined**: "The patient exhibited mild tachycardia and orthostatic hypotension after the dose. Administer intravenous fluids immediately and monitor cardiac telemetry every fifteen minutes until vital signs stabilize."
    **Raw ASR**: "the patience exhibited mild tacky cardia and ortho static high po tension after the those. Administer intra venous fluids immediately and monitor cardiac tell emetry every fifteen minutes and till vital signs stabilize."
18. **[Long - 77 words]**
    **Refined**: "Calculate EBITDA margins and amortize the capital expenditure over five quarters. The finance committee requested detailed depreciation schedules for all newly acquired datacenter hardware assets. If projected operating cash flow remains positive through December, leadership will approve the expansion into additional regional colocation facilities. Ensure all audit trail workbooks conform strictly to international accounting guidelines before final executive review. Independent external auditors will inspect our balance sheet valuations prior to submitting statutory filings to the securities commission."
    **Raw ASR**: "calculate he bit da margins and a more ties the capital ex spend a sure over five quarters. The fine ants committee requested detailed depreciation schedules for all newly acquired day to center hard ware assets. If projected operating cash flow remains positive threw December, leader ship will a prove the expansion into additional regional coal location facilities. Ensure all audit trail workbooks conform strictly to inter national accounting guidelines before final executive review. Independent external odd eaters will inspect hour balance sheet valuations prior to submitting statutory filings to the securities commission."
19. **[Long - 77 words]**
    **Refined**: "Deglaze the stainless pan with balsamic vinegar and fold in the mascarpone cheese. Simmer the reduction over medium-low heat until the sauce coats the back of a wooden spoon. Garnish with chopped fresh tarragon and toasted pine nuts right before serving the pasta course to guests. This delicate emulsion separates if exposed to direct boiling temperatures, so remove the skillet from heat promptly. Pair the completed dish with a chilled dry white wine from the northern hills."
    **Raw ASR**: "the glaze the stain less pan with ball samic vinegar and fold in the mass car pony cheese. Simmer the re duction over medium low heat until the sauce coats the back of a wooden spoon. Garnish with chopped fresh tear a gone and toasted pine nuts write before serving the pasta coarse to guests. This delicate a mull shun separates if exposed to direct boiling temperatures, sew remove the skillet from heat promptly. Pear the completed dish with a chilled dry white whine from the northern heels."
20. **[Long - 80 words]**
    **Refined**: "Use tmux or Neovim over SSH when debugging headless Debian containers across remote clusters. Detachable terminal sessions preserve your active shell environment even if transient network disconnects drop your secure connection. Installing persistent terminal multiplexers on bastion hosts allows team members to pair-program on production incidents in real time without sharing credential keys directly. Furthermore, session logs can be piped into persistent storage volumes to preserve diagnostic traces for post-incident root cause analysis meetings with infrastructure stakeholders across regional offices."
    **Raw ASR**: "use tea mux or knee oh vim over S S age when debugging headless debbie in containers across remote clusters. Detachable terminal sessions pro serve hour active shell environment even if transient network disconnects drop hour secure connection. Installing persistent terminal multiple lexers on bastion hosts allows team members to pear program on production incidents in real time without sharing credential peace directly. Father more, session logs can be piped into persistent storage volumes to preserve diagnostic traces for post incident root cause analysis meetings with infrastructure stakeholders across regional offices."

#### Mechanism 3: Unstressed Function-Word & Inflection Shifts
Soft function words (`in`, `on`, `to`, `for`, `with`, `our`, `are`, `a`, `the`) merge into neighbors, and swallowed tense/plural endings produce **valid English root words** (never chopped non-words).

21. **[Short - 10 words]**
    **Refined**: "The permissions were configured by our security team on Tuesday."
    **Raw ASR**: "the permissions were configured buy hour security team in choose day."
22. **[Short - 11 words]**
    **Refined**: "Wait until all background processes have finished before unmounting the volume."
    **Raw ASR**: "weight and till all background processes have finished before unmounting the volume."
23. **[Short - 15 words]**
    **Refined**: "We are going to need a larger buffer if the packets arrive out of order."
    **Raw ASR**: "we're gonna need a larger tough her if the packet arrive out a border."
24. **[Medium - 27 words]**
    **Refined**: "Could you have deployed the hotfix to staging without triggering an alert? The continuous integration pipeline failed on the unit test stage due to missing environment secrets."
    **Raw ASR**: "could of deployed the hot fix to staging without triggering an alert? The continuous integration pipe lane failed on the unit test stage do to missing environment secrets."
25. **[Medium - 26 words]**
    **Refined**: "Several environment variables were overridden by the local configuration file. This caused the database connector to select the default staging host instead of the production replica."
    **Raw ASR**: "several in vironment variables were over ridden buy the local configure ration file. This caused the day to base connector to select the default staging host instead of the production replica."
26. **[Medium - 28 words]**
    **Refined**: "They should have verified whether the SSL certificates had expired before the migration. Renewing credentials during peak business hours introduced unexpected handshake latency for active mobile app users."
    **Raw ASR**: "they should of verified weather the S S L certificates had expired before the my gration. Renewing credentials during peek business hours introduced unexpected handshake late in see for active mobile app users."
27. **[Medium - 27 words]**
    **Refined**: "Bind the socket to all interfaces so internal containers can reach it. Leaving the listener bound to localhost blocks incoming health checks from the external gateway router."
    **Raw ASR**: "find the socked too all inner faces so internal containers can reach it. Leaving the listened bound to vocal host blocks incoming health checks from the external gait way router."
28. **[Long - 76 words]**
    **Refined**: "Most of the latency comes from serializing large nested JSON arrays inside client responses. Our benchmarking suite revealed that converting raw database tuples into structured domain models takes twelve milliseconds per request. Migrating the transport layer to Protocol Buffers with compiled schemas eliminates serialization bottlenecks and shrinks network payload size by sixty percent across distributed RPC services. Adopting binary serialization formats also lowers garbage collector CPU utilization on memory-constrained compute instances throughout heavy sustained load periods."
    **Raw ASR**: "most a the late in see comes from cereal izing large nest it jason a raise inside client responses. Hour bench mark in sweet revealed that converting raw day to base two pulls into structured domain models takes twelve milliseconds per request. Migrating the transport layer to Protocol Buffers with come piled schemas eliminates cereal ization bottle necks and shrinks network payload size buy sixty percent across distributed R P C services. Adopting binary serialization formats also lowers garbage collector C P U utilization on memory constrained compute instances threw out heavy sustained load periods."
29. **[Long - 77 words]**
    **Refined**: "Check whether the upstream branch has diverged from our release tag before pushing changes. Rebasing feature branches against main prevents merge conflicts and ensures linear commit history across git trees. If other developers have merged breaking schema modifications, resolve conflicting migration files locally and execute the entire integration test suite before requesting formal pull request approval. Maintaining strict branch hygiene ensures clean bisect runs when investigating production regressions across multiple release tags during fast-paced agile development sprints."
    **Raw ASR**: "check weather an up stream branch has die verged from hour re release tag before pushing changes. Re basing feature branches against main prevents merge conflicts and in sures linear commit history across get trees. If other developers have merit break in ski ma modifications, resolve conflicting my gration files locally and execute the entire in tegration test sweet before requesting formal pull request a pro val. Maintaining strict branch hygiene in sures clean bisect runs when in vestigating production regressions across multiple release tags during fast paced agile development sprints."
30. **[Long - 77 words]**
    **Refined**: "All deprecated endpoints will be removed in the next major version scheduled for release. Client engineering teams have sixty days to upgrade their mobile client SDKs to use modern GraphQL queries. Backward-compatible fallback endpoints will remain operational during the migration window, but logging monitors will flag remaining legacy API traffic to assist with customer outreach campaigns. Maintaining outdated interface contracts inflates operational maintenance overhead and slows down feature velocity across all backend services in our core platform."
    **Raw ASR**: "all debt per cated end points will be taken down in the neck major version sked jewel for release. Client engineering teams have sixty days to upgrade their mobile client s d cases to use modern graph cue el queries. Backward compatible fallback end points will remain operational during the my gration window, but logging monitors will flag remaining legacy A P I traffic to assist with customer out reach campaigns. Maintaining outdated interface contracts inflates operational maintenance overhead and slows drown feature velocity across all backend services in hour core platform."

#### Mechanism 4: Spoken Punctuation, Code, Paths, CLI Flags, and Numbers
Humans dictate symbols out loud (`slash`, `dash`, `dot`, `colon`, `equals`), and ASR transcribes them as spoken words or splits paths/flags while keeping factual numeric quantities intact.

31. **[Short - 11 words]**
    **Refined**: "Edit the nginx configuration file and set worker processes to auto."
    **Raw ASR**: "edit the engine X configuration file and set worker pro sesses to ought to."
32. **[Short - 12 words]**
    **Refined**: "Run python three dash m venv dot venv to create an environment."
    **Raw ASR**: "run python 3 dash M venv dot venv two create an in vironment."
33. **[Short - 12 words]**
    **Refined**: "The service listens on port eighty eighty and writes logs to disk."
    **Raw ASR**: "the surface listens on port 8080 and rights logs too disk."
34. **[Medium - 26 words]**
    **Refined**: "Pass `--max-seq-len 4096` and `--learning-rate 2e-5` to the training script. Training without explicit sequence limits leads to out-of-memory errors on GPU worker nodes during backward passes."
    **Raw ASR**: "pass dash dash max seq len 4096 and dash dash tray ning rate 2 E minus 5 to the training script. Tray ning without explicit sequence limits leads to out of memory errors on GPU worker notes during backward passes."
35. **[Medium - 31 words]**
    **Refined**: "Set CUDA visible devices to zero and one before running the training script. Restricting the visible device list prevents child processes from competing for primary GPU memory on shared training hosts."
    **Raw ASR**: "set cuda visible devices two 0 and 1 before running the tray ning script. Restricting the visible device list prevents child processes from competing for primary GPU memory on shared training hosts."
36. **[Medium - 30 words]**
    **Refined**: "Commit a seven f three fixed the memory leak inside the tokenizer source file. Rust compiler warnings identified an unreleased buffer slice inside the tokenization loop during streaming batch decoding."
    **Raw ASR**: "come it A 7 F 3 fixed the memory leek inside the token izer sauce file. Rust come piler warnings identified an unreleased buffer slice inside the token eye zation loop during streaming batch decoding."
37. **[Medium - 29 words]**
    **Refined**: "The invoice total is $1,450.75, due by 17:30 UTC on Friday. Remit payment to our corporate checking account to avoid late assessment penalties on next month's billing cycle statement."
    **Raw ASR**: "the in voice total is 1,450 dollars and 75 cents do buy 17 30 U T C on friday. Pay meant to hour corporate cheque in a count to a void late assess meant penalties on neck month billing cycle statement."
38. **[Long - 82 words]**
    **Refined**: "Use chmod plus x on scripts deploy dot sh and run grep dash r n to inspect traces. The container entrypoint script expects executable permissions before initializing daemon workers across our infrastructure. If logging demonstrates failed database migrations, check environment flags inside helm values dot yaml before executing a cluster rollback command to restore previous container revisions. Always archive diagnostic stack traces before restarting containers so that engineers can correlate application error codes with underlying infrastructure events across all active deployment zones."
    **Raw ASR**: "use chmod plus X on scripts the ploy dot S H and run grip dash R N to in spect traces. The container entry point script expects executable permissions before initializing demon workers across hour infrastructure. If logging demonstrates failed day to base migrations, check environment flags inside helm values dot yaml before executing a clutter roll back command to restore previous container revisions. Always archive die egg nostic stack traces before restarting containers sew that engineers can correlate application error codes with underlying infrastructure events across all active deployment zones."
39. **[Long - 79 words]**
    **Refined**: "Set temperature to zero point seven and top p to zero point ninety-five to improve output diversity. High temperature settings produce creative responses but increase hallucination risks on factual domain queries. We recommend evaluating candidate generation checkpoints against our standardized gold test benchmark before deploying modified inference configurations to production endpoints. Furthermore, logging token log-probabilities helps detect degraded decoding trajectories before end users observe corrupted or nonsensical model completions during interactive user dialogue sessions in live customer support environments."
    **Raw ASR**: "set temperature to 0 point 7 and top P to 0 point 95 to improve output diversity. High temperature settings produce creative responses but increase hallucination risks on factual domain queries. We recommend evaluating candidate generation checkpoints against hour standardized gold test benchmark before deploying modified in fur rents configurations to production endpoints. Father more, logging token log probabilities helps detect degraded decoding trajectories before end users observe corrupted or none sensical model completions during interactive user dialogue sessions in live customer support in vironments."
40. **[Long - 79 words]**
    **Refined**: "Send a POST request to our embeddings endpoint with your bearer token attached in headers. The API endpoint accepts batched text inputs and returns dense vector representations for semantic search indexation. Requests exceeding eight thousand input tokens return HTTP 413 payload too large errors, so chunk incoming documents locally before triggering remote batch inference calls. Inspect the response payload to verify that returned vector dimensions match downstream similarity search expectations across your production retrieval pipeline in live deployment environments."
    **Raw ASR**: "send a post request to hour in beddings endpoint with your bare her token attached in headers. The API endpoint accepts badge text inputs and returns dense vector representations for semantic search indexation. Requests exceeding 8,000 in put tokens return HTTP 413 payload too large errors, sew chunk incoming documents locally before triggering remote batch in fur rents calls. Inspect the response payload to verify that returned vector dimensions match down stream similarity search expectations across your production retrieval pipeline in live deployment in vironments."

#### Mechanism 5: Clause & Sentence Boundary Drift (Run-Ons & False Sentence Breaks)
Speakers rush through periods or pause mid-clause, causing ASR to merge sentences into run-ons or drop false periods in the middle of a thought, alongside phonetic slips.

41. **[Short - 14 words]**
    **Refined**: "Stop the container first. If it hangs for ten seconds, send a SIGKILL signal."
    **Raw ASR**: "stop the container first if it hangs four 10 seconds. Send the sick kill single."
42. **[Short - 11 words]**
    **Refined**: "The migration failed halfway through. Roll back the schema changes immediately."
    **Raw ASR**: "the my gration failed half way threw roll back the ski ma changes. Immediately."
43. **[Short - 14 words]**
    **Refined**: "First, verify the checksum of the tarball. Then extract it into the opt directory."
    **Raw ASR**: "first verify the check some of the tar bawl then ex tract it. Into the opt directory."
44. **[Medium - 26 words]**
    **Refined**: "Latency spiked on node three. However, CPU utilization stayed below forty percent. Further investigation showed that network socket saturation throttled incoming packet processing across the interface."
    **Raw ASR**: "late in see spiked on known three how ever. C P U you till ization stayed be low 40 per cent. Father in vestigation showed that net work socket saturation throttled incoming packet tray ning across the inner face."
45. **[Medium - 28 words]**
    **Refined**: "Do not merge this pull request yet. The integration tests are still failing on CI. Several unit tests expect updated mock fixtures matching the new database schema migrations."
    **Raw ASR**: "due not merch this pull request yet the in tegration test are still. Failing on see eye. Several unit tests expect updated mock fixtures matching the knew day to base ski ma my grations."
46. **[Medium - 28 words]**
    **Refined**: "Cache invalidation is tricky. Stale entries can persist for several minutes after updates. Ensure your cache keys include a version prefix so deployments immediately invalidate outdated serialized models."
    **Raw ASR**: "cash in validation is tricky. Stale in trees can persist four several minutes after updates. Ensure your cash keys include a version prefix sew deploy meants immediately invalidate outdated cereal ized models."
47. **[Medium - 28 words]**
    **Refined**: "Check the power supply voltage. A loose ground wire causes intermittent hardware reboots. Verify that all terminal screws are torqued down securely before reconnecting the primary circuit breaker."
    **Raw ASR**: "check the power supply volt age a loss ground wire. Causes inner mittent hard ware re boots. Very fie that all terminal screws are talked down securely before reconnecting the prime mary circuit breaker."
48. **[Long - 80 words]**
    **Refined**: "Close the file descriptor inside the finally block. Otherwise, the process leaks handles under heavy load. Operating system limits restrict each worker process to one thousand open descriptors. When connections accumulate without being garbage collected, subsequent socket open calls fail with resource unavailable exceptions and crash the container instance. Routine audit scripts should inspect proc net tcp periodically to detect lingering file descriptors before connection limits trigger cascading service outages across the distributed computing cluster under heavy production query traffic."
    **Raw ASR**: "clothes the file the scripter inside the final lee block other wise. The process leeks handles under heavy load. Operating system limits restrict each worker process to 1,000 open the scripters. When connections accumulate without being garbage collected, subsequent socked open calls fail with re source unavailable exceptions and crash the container instance. Route in audit scripts should inspect proc net tcp periodically to detect lingering file descriptors before connection limits trigger cascading surface outages across the distributed compute in cluster under heavy pro duction query traffic."
49. **[Long - 80 words]**
    **Refined**: "Our dataset contains ten thousand audio clips. Each clip is sampled at sixteen kilohertz and transcribed manually. Data curators audit individual audio tracks to remove background ambient noise and truncate leading silence periods. These curated training pairs provide clean phonetic supervision for fine-tuning our downstream speech recognition acoustic models. High audio quality in the initial dataset drastically reduces transcription error rates across diverse speaker accents during real-world inference evaluation on live edge hardware platforms deployed across diverse customer edge locations."
    **Raw ASR**: "hour data set can tains 10,000 audio clips each clip is. Sampled at 16 killer hurts and trance cribbed manually. Day to curators audit individual audio tracks to remove ambient noise and truncate leading silence periods. These cure eight ed train in pears provide clean phonetic souper vision for fine tuning hour drown stream speech recognition acoustic models. High audio quality in the initial dataset drastically reduces transcription error rates across diverse speaker accents during real world in fur rents evaluation on live edge hard ware flat forms deployed across diverse customer edge low cay shuns."
50. **[Long - 79 words]**
    **Refined**: "Enable strict mode in the compiler. It catches uninitialized pointers at build time before deployment. Static analysis checks identify potential null pointer dereferences and concurrent race hazards across shared variables. Fixing these compiler warnings early prevents catastrophic memory corruption bugs during high-concurrency production execution. Furthermore, strict compiler enforcement eliminates entire classes of security vulnerabilities before code merges into the mainline release branch across our global repository infrastructure, ensuring resilient software deployments across mission-critical enterprise systems in live cloud environments."
    **Raw ASR**: "in able strict mowed in the compiler it catches. On initialized pointers at billed time before deploy meant. Static analysis checks eye dentify potential null pointer dereferences and concurrent race hazards across shared variables. Fixing these come piler warnings early prevents catastrophic memory corruption bugs during high concurrency production execution. Father more, strict compiler enforcement eliminates entire classes of security vulnerabilities before code merges into the mainline re release branch across hour global re pository infrastructure, in shore in resilient software deployments across mission critical enter prize systems in live cloud in vironments."

#### Mechanism 6: Subtle Homophone & Near-Homophone Swaps in Everyday & Technical Speech
Whisper frequently outputs real English homophones ("same sound, different word") where the spelling changes completely while the pronunciation stays identical.

51. **[Short - 13 words]**
    **Refined**: "Clear the local cache and check whether the serial port is sending bytes."
    **Raw ASR**: "clear the vocal cash and check weather the cereal port is send in bites."
52. **[Short - 11 words]**
    **Refined**: "The principal engineer approved the new routing tier for phase two."
    **Raw ASR**: "the principle engine ear a proved the knew route in tear four faze two."
53. **[Short - 13 words]**
    **Refined**: "Parse the source file carefully so you do not miss any syntax errors."
    **Raw ASR**: "parts the sauce file care fully sew you due not miss any sin tax heirs."
54. **[Medium - 29 words]**
    **Refined**: "Sarah said to call her assistant before we hire a contractor for the site. The electrical inspection report revealed outdated wiring inside the breaker panel that must be upgraded."
    **Raw ASR**: "sarah that nicole her assistant before we hire a contractor four the sight. The electrical inspection report revealed out dated wire in in side the break her panel that must be upgraded."
55. **[Medium - 28 words]**
    **Refined**: "Do three sets of eight squats and pause for two minutes between sets. Proper form prevents lower back strain while building strength through the full range of motion."
    **Raw ASR**: "due 3 sets with recently squats and paws four two minutes between sets. Proper form prevents lower back strain while tray ning strength threw the full range of motion."
56. **[Medium - 26 words]**
    **Refined**: "We ordered grilled lamb skewers, whole wheat pita, and a side of tahini. The Mediterranean restaurant marinates the meat with garlic, lemon, and fresh rosemary overnight."
    **Raw ASR**: "we oar third guild lamb skewers, haul wheat peter and a sighed of to he knee. The Mediterranean restaurant marry nates the meat with garlic, lemon, and fresh rose marry over night."
57. **[Medium - 28 words]**
    **Refined**: "Wait for the brake pads to cool down before you check the wheel alignment. Worn brake rotors cause vibrations through the steering wheel when stopping from highway speeds."
    **Raw ASR**: "weight four the break pads two coal down before you check the we'll a line mint. Worn break row tors cause vibrations threw the steer in wheel when stop in from high way speeds."
58. **[Long - 79 words]**
    **Refined**: "Write a wrapper around the queue so stale messages do not block the main thread. When asynchronous consumer tasks encounter transient database connection timeouts, they should push failed items into a dead-letter exchange. A separate retry worker can re-examine unacknowledged messages after five minutes without halting continuous event ingestion from upstream publishers. Isolating poison-pill messages prevents intermittent message payload errors from cascading across the entire event stream architecture in our cloud datacenter deployment during high-volume promotional consumer sales events."
    **Raw ASR**: "right a rapper a round the cue sew tail messages due not flock the mane threat. When asynchronous consumer tasks in counter transient day to base connection timeouts, they should push failed items into a dead letter exchange. A separate retry worker can re examine un acknowledged messages after five minutes without halting continuous he vent in gestion from up stream publishers. Isolating poison pill messages prevents intermittent message pay load errors from cascading across the entire event stream architecture in hour cloud day to center deployment during high volume promo shun all consumer sales he vents."
59. **[Long - 79 words]**
    **Refined**: "Their flight arrived an hour late because of heavy rain near the coast. Severe thunderstorms delayed departures across the entire regional airport hub throughout Friday afternoon. The airline accommodated stranded passengers on Saturday morning connection flights and issued meal vouchers for airport terminal restaurants during the extended delay. Ground crews worked through difficult weather conditions to de-ice wings and inspect aircraft navigation equipment before nightfall settled across the airfield, allowing resumed flight operations to proceed safely by early morning."
    **Raw ASR**: "there flight a rived in our late because of heavy reign near the cost. Severe thunderstorms delayed departures across the entire regional airport hub threw out friday afternoon. The airline accommodated stranded passengers on saturday morning connection flights and issued meal vouchers four airport terminal restaurants during the extended delay. Ground crews worked through difficult weather conditions to Dee ice wings and inspect aircraft navigation equipment before night fall settled across the air field, allow in resumed flight operations to pro seed safely buy early morning."
60. **[Long - 78 words]**
    **Refined**: "Verify the root cause of the memory leak before rolling out the kernel patch. Profiling production servers under synthetic traffic load revealed uncollected socket buffer allocations inside the network stack driver. Applying the vendor kernel update resolves memory retention and ensures system stability through upcoming peak holiday shopping traffic. Operations teams will monitor memory telemetry graphs around the clock to detect any recurrent memory leaks promptly across all cluster nodes, safeguarding critical infrastructure against sudden memory starvation outages."
    **Raw ASR**: "very fie the route cause of the memory leek before rolling out the colonel patch. Profile in production servers under synthetic traffic load revealed uncollected socked buffer allocations inside the network stack driver. Applying the vendor colonel update resolves memory retention and in sures system stability threw upcoming peek holiday shopping traffic. Operations teams will monitor memory tell emetry graphs around the clock to the tect any recurrent memory leaks promptly across all cluster nodes, safe guard in critical infrastructure against sudden memory star vation out ages."

---

### HARD GUARDRAILS (WHAT YOU MUST NEVER DO)
1. **NO TRUNCATED NON-WORDS**: Never output chopped word fragments (`minut`, `automat`, `releas`, `thinkin`, `configur`). Every word in `"raw_asr"` must be a valid dictionary word or a valid token from `"refined_text"`.
2. **NO LAZY SPACE-ONLY SPLITS OR "-ING" LOOPS**: Do not try to pass by simply splitting compound words (`data base`, `dead lock`) or replacing `-ing` with ` in`. At least half of your edits must change the actual spelling via homophones or phonetic respellings.
3. **KEEP EXISTING GOOD ERRORS**: If a sentence in `"raw_asr"` already has creative, realistic Whisper errors, **keep them!** Only upgrade sentences or samples that are too clean or repetitive.
4. **NEVER ALTER FACTUAL NUMBERS TO DIFFERENT VALUES**: Never change `16` to `32` or `500` to `300`. Only alter how a number is formatted, spaced, or phonetically heard next to neighboring words.
5. **NEVER MODIFY `"refined_text"`**: `"refined_text"` is the sacred ground truth. Do not touch a single character in `"refined_text"`.
6. **NEVER DROP WHOLE SENTENCES**: `"raw_asr"` must cover the complete content of `"refined_text"`.

---

### WORKFLOW FOR EXECUTION
1. Read ONLY the assigned input JSON batch file. Do not inspect or run any external validation scripts.
2. Process the batch sample by sample using the **Mumble & Think Protocol**.
3. For each sample:
   - Identify the sample length tier (Short, Medium, Long).
   - Read `"refined_text"` sentence by sentence.
   - Inject fresh, context-specific acoustic errors combining **Mechanism #1 (multi-word phonetic re-segmentation)**, **Mechanism #6 (same-sound homophones)**, and your batch's seeded mechanisms so every sentence has authentic spoken errors.
   - Verify that every word you wrote is a real word (zero suffix chopping, zero lazy space-only splits) and does not copy phrases from the 60 calibration examples into unrelated sentences.
4. Output and save the updated batch in the exact required JSON format.
