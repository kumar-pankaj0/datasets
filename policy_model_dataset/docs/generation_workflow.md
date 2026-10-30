**Antigravity Native Data Generation Workflow**

This guide documents the exact step-by-step process Antigravity uses to generate and validate dataset samples without external APIs, maintaining high diversity across an engineer's real day-to-day life.

---

**1. Workflow Philosophy in Natural Flow**

"We do not use external cloud APIs or complex multi-stage script chains. Antigravity acts as the native generator inside this environment.

Engineers do not spend all day shouting CLI commands into a microphone. In real life, an engineer uses speech-to-text to talk to teammates: dictating a Slack message, updating a Jira ticket, giving a standup update, explaining a bug to a coworker, or discussing trade-offs in an architecture meeting.

When the user requests a batch of samples, Antigravity pulls the invariant rules from `prompt/definition.py`, balances across Short, Medium, and Long utterance lengths, selects from diverse everyday engineering topics, drafts candidates, and passes them immediately through Python validation in `code/validator.py`.

Any sample that fails validation gets rejected instantly. Only 100% verified, zero-invention pairs get appended to `combined_dataset.jsonl`."

---

**2. Utterance Length Distribution (Short, Medium, Long)**

To match real spoken communication, every generated batch must balance across three length tiers:

**Tier 1: Short Utterances (< 25 words) — Target: 40% of dataset**
* **Context**: Quick status pings, single terminal commands, short questions, or immediate approvals.
* **Formatting Invariant**: Exactly 1 grammatically complete sentence. Zero newline characters (`\n`). Zero bullet points or dividers.

**Tier 2: Medium Utterances (25 to 90 words) — Target: 40% of dataset**
* **Context**: Daily standup summaries, PR review comments, error log explanations, or bug reproduction steps.
* **Formatting Invariant**: 1 to 3 grammatically complete sentences. Natural paragraph breaks (`\n\n`) between distinct thoughts.

**Tier 3: Long Utterances (90+ words) — Target: 20% of dataset**
* **Context**: Outage root cause analysis (RCA), complex voice prompting to AI coding assistants, architecture RFC trade-off proposals, or detailed multi-step postmortems.
* **Formatting Invariant**: Multi-paragraph structure separated by `\n\n`. Numbered or bulleted lists only when describing an explicit sequential checklist.

**Phase 3 Long Catch-Up Mode (Active)**:
To rapidly eliminate the 1,386 sample Long deficit before reaching the 7,500 target ceiling, generation batches switch to the accelerated catch-up ratio:
* 2 Short samples (< 25 words / 20%)
* 3 Medium samples (25–90 words / 30%)
* 5 Long samples (90+ words / 50%)
Strict zero-invention and repair-only invariants remain fully enforced on every sample.

---

**3. Acoustic Noise Simulation Patterns (for `raw_asr`)**

Every candidate must exhibit combinations of authentic acoustic noise patterns:
* **Phonetic Tool Mishearings**: `cube ctl` for `kubectl`, `a sink` for `async`, `free are toss` for `FreeRTOS`, `post gres` for `PostgreSQL`.
* **Sound-Alike Homophones**: `buy` for `by`, `four` for `for`, `two` for `to`, `knowed` for `node`, `root` for `route`.
* **Mid-Sentence Self-Corrections**: *"check the memory usage wait check the socket buffer size instead"*.
* **Spoken Hex & Digits**: *"zero x one zero"* for `0x10`, *"one hundred thousand"* for `100000`.
* **Cut-Off Buffer Truncations**: *"configur"*, *"terminat"*, *"allocat"*, *"namesp"*.
* **Spoken Disfluencies & Fillers**: *"um"*, *"uh"*, *"basically"*, *"you know"*, *"like"*.
* **Flat Speech Stream**: Continuous lowercase spoken audio without periods, commas, or line breaks.

---

**4. Day-to-Day Engineering Diversity Topics**

**Domain 1: Team Chat & Async Updates (Slack / Teams / Discord)**
* Daily async standup update (completed work, planned tasks, active blockers)
* Asking a coworker for debugging help or a second pair of eyes
* Heads-up notification about broken staging or failing test suites
* Shift handoff notes before signing off or going on call

**Domain 2: Live Meetings & Spoken Discussions**
* Sprint planning and task complexity estimation
* Architecture review and technical trade-off debate
* Incident bridge call (real-time live outage triage)
* Sprint retrospective feedback (process pain points and wins)

**Domain 3: Code Review & Pull Request Discussions**
* Explaining the intent and design of a complex pull request
* Leaving review feedback on a teammate's implementation
* Debating architectural patterns vs performance trade-offs
* Describing steps to reproduce a flaky test or edge-case bug

**Domain 4: Incident Management & Postmortems**
* Live root cause analysis (RCA) verbal narration
* Reconstructing an outage timeline for postmortem review
* Explaining why an immediate production rollback is required
* Drafting customer-facing status page incident summaries

**Domain 5: Mentoring & Developer Onboarding**
* Walking a new engineer through local environment setup
* Explaining repository architecture and service boundaries
* Documenting unwritten tribal knowledge and system quirks
* Explaining database indexing, caching strategies, or race conditions

**Domain 6: Hands-on Technical Operations (The Command & Tooling Slice)**
* Git branch management, rebasing, and merge conflict resolution
* Container and orchestration troubleshooting (Docker, Kubernetes)
* Database migrations, slow queries, and connection pools
* Embedded firmware flashing, serial logs, and hardware register tuning

**Domain 7: Voice Prompting to AI Coding Assistants**
* Dictating complex refactoring prompts to coding agents (e.g., Cursor, Claude, Antigravity)
* Providing verbal context, logs, and stack traces to an AI assistant
* Requesting unit test coverage and mock setups for edge cases

**Domain 8: Technical Specs, RFCs & Architecture Decision Records (ADRs)**
* Dictating the executive summary of a system design proposal
* Documenting architectural justifications for selecting specific tools or frameworks
* Outlining system scalability, throughput limits, and latency trade-offs

**Domain 9: Technical Interview & Candidate Debriefs**
* Spoken evaluation of a candidate's problem-solving and coding ability
* Reviewing a candidate's system design trade-offs and architectural depth
* Articulating hiring recommendation and technical seniority alignment

---

**5. The 5 Step-by-Step Actions**

* **Step 1: Ingest Invariant Rules**
  * Review the active definition in `prompt/definition.py`.
  * Enforce the primary constraint: zero parameter invention and zero unprompted purpose clauses.
  * Pick an active domain and target length tier (Short, Medium, or Long).

* **Step 2: Generate Candidate Pairs**
  * Draft the requested batch size (e.g., 10 pairs).
  * `raw_asr`: Flat lowercase spoken text with acoustic errors, spelled numbers, cut words, and pause fillers.
  * `refined_text`: Cleaned technical documentation and communication preserving exact spoken tokens.

* **Step 3: Execute Deterministic Python Validation**
  * Run `validate_pair()` on each generated sample and `validate_batch()` across the whole batch.
  * **Flag Grounding Check**: Every CLI flag (`-f`, `--baud`) must exist phonetically in `raw_asr`.
  * **Code Token Check**: Every backticked register, tool, or identifier must exist phonetically in `raw_asr`.
  * **Word Length Ratio Check**: Ratio `len(refined_words) / len(raw_words)` must stay within `[0.35, 1.25]`.
  * **Formatting Invariants Check**:
    * Short (< 25 words): exactly 0 newlines (`\n`).
    * Long (90+ words): must contain natural paragraph breaks (`\n\n`).
    * Divider protection: zero `---` divider spam and zero ungrounded bullet lists.
  * **Batch Tier Distribution Check**: `validate_batch()` verifies a minimum presence of Short, Medium, and Long samples.

* **Step 4: Discard and Regenerate Failures**
  * Drop any candidate pair that returns `is_valid == False`.
  * Regenerate replacements until 100% of the requested batch passes all deterministic checks.

* **Step 5: Append to Combined Dataset**
  * Append verified samples directly to `combined_dataset.jsonl` (when approved by user).
  * Print verification output and sample diffs for user review.

---

**6. The Simple Rule**

* Balance across lengths: 40% Short, 40% Medium, 20% Long.
* Commands are only 15% to 20% of an engineer's voice input; 80% is natural collaboration.
* Never trust raw LLM output without deterministic code validation.
* Only clean, 100% grounded samples touch the training dataset.
