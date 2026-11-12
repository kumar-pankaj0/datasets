**Antigravity Native Data Generation & Curation Workflow**

This guide documents the workflow used to curate and validate dataset samples, maintaining high diversity across an engineer's real day-to-day life.

---

**1. Workflow Philosophy in Natural Flow**

We do not use external cloud APIs or brittle regex scripts. Antigravity acts as the native curation agent inside this repository.

Engineers do not spend all day shouting CLI commands into a microphone. In real life, an engineer uses speech-to-text to collaborate with teammates: dictating a Slack message, updating a Jira ticket, giving a standup update, explaining a bug to a coworker, or discussing trade-offs in an architecture meeting.

When curating or repairing samples:
1. The agent follows the master rules in `.agents/skills/asr-data-curator/SKILL.md`.
2. It balances across Short, Medium, and Long utterance lengths.
3. It selects from diverse everyday engineering and technical topics.
4. It passes all pairs immediately through Python validation in `code/gold_dataset_validator.py`.
5. Only 100% verified pairs are stored in `data/sft_train.json`.

---

**2. Utterance Length Distribution (Short, Medium, Long)**

To match real spoken communication, the dataset balances across three length tiers:

**Tier 1: Short Utterances (< 25 words) — Target: 30% to 40% of dataset**
* **Context**: Quick status pings, single terminal commands, short questions, or immediate approvals.
* **Formatting Invariant**: Exactly 1 grammatically complete sentence. Zero newline characters (`\n`). Zero bullet points or dividers.

**Tier 2: Medium Utterances (25 to 90 words) — Target: 35% to 45% of dataset**
* **Context**: Daily standup summaries, PR review comments, error log explanations, or bug reproduction steps.
* **Formatting Invariant**: 1 to 3 grammatically complete sentences. Natural paragraph breaks (`\n\n`) between distinct thoughts.

**Tier 3: Long Utterances (90+ words) — Target: 20% to 30% of dataset**
* **Context**: Outage root cause analysis (RCA), complex voice prompting to AI coding assistants, architecture RFC trade-off proposals, or detailed multi-step postmortems.
* **Formatting Invariant**: Multi-paragraph structure separated by `\n\n`. Numbered or bulleted lists only when describing an explicit sequential checklist.

---

**3. The 6 Realistic Whisper Acoustic Mechanisms (for `raw_asr`)**

Every candidate must exhibit authentic acoustic noise patterns derived from the sentence's own words:
* **Word Boundary Shifts**: Fast speech merges or splits word edges (`jack it` for `jacket`, `gay token` for `gate open`).
* **Domain Jargon Substitution**: Technical terms heard as everyday phrases with the same sound skeleton (`stay vector` for `statevector`, `rock DB` for `RocksDB`).
* **Unstressed Syllable Erosion**: Fast speech clips weak syllables (`play` for `apply`, `seven terry` for `sedentary`).
* **Spoken Punctuation, Code & Flags**: Oral dictation of symbols and flags without Markdown formatting (`dash detailed exitcode`, `dot pie`).
* **Clause & Sentence Boundary Drift**: Natural pauses merging or splitting clauses with commas and periods.
* **Conversational Homophones**: Everyday slips (`do` for `due`, `been` for `bin`, `paved` for `paid`).
* **Spoken Audio Format**: Natural casing and punctuation (commas, periods, questions). Strictly zero Markdown backticks or bullet markers.

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
* Dictating complex refactoring prompts to coding agents
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

**5. Step-by-Step Workflow**

* **Step 1: Check Target & Invariant Rules**
  * Target candidate pairs from `data/weak_samples_manifest.json` or generate new domain pairs.
  * `refined_text` is frozen ground truth. Never alter factual content.

* **Step 2: Apply the Mumble & Think Protocol**
  * Read `refined_text` fast mentally.
  * Identify natural phonetic weak spots.
  * Rotate across the 6 acoustic noise mechanisms.
  * Ensure 100% semantic recoverability from context.

* **Step 3: Execute Deterministic Validation**
  * Run `code/gold_dataset_validator.py`.
  * Verifies Word Error Rate (10% to 35% target).
  * Verifies character similarity bounds (55% to 98%).
  * Rejects Markdown backticks or bullet lists in `raw_asr`.
  * Rejects multi-sentence samples where any 15+ word sentence remains 100% pristine.

* **Step 4: Save Verified Pairs**
  * Append or patch verified samples in `data/sft_train.json`.
  * Zero benchmark leakage against `data/sft_eval.json`.

---

**6. Core Rules**
* Commands are only 15% to 20% of an engineer's voice input; 80% is natural technical collaboration.
* Never trust raw LLM output without deterministic Python validation.
* Only clean, 100% grounded samples touch the training dataset.
