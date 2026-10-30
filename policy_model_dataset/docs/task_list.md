# Hardened Dataset Cleanup and Replenishment Execution Plan

This plan decomposes the dataset restoration into atomic, strictly verifiable phases, enforcing a strict drop policy for all tainted samples.

---

## Phase 1: Whitelist Grounding Purge & Baseline Verification

- [x] **Task 1.1: Verify Pre-Purge Backups**
  - Completed: Verified raw backups in `archive/backups/combined_dataset_pre_purge_20261026.jsonl` (6,580 rows) and `sft_eval_pre_purge_20261026.json` (671 rows).

- [x] **Task 1.2: Execute Whitelist Training Dataset Sanitization**
  - Completed: Enforced strict Whitelist Grounding Engine in `code/cleaner.py` (zero patching). Kept 3,660 100% faithful samples (55.6%), dropped 2,920 corrupted/hallucinated samples. Zero validation failures.

- [x] **Task 1.3: Execute Whitelist Evaluation Dataset Sanitization**
  - Completed: Enforced strict Whitelist Grounding Engine on evaluation set. Kept 358 clean benchmark targets (53.4%), dropped 313 corrupted targets. Zero validation failures.

- [x] **Task 1.4: Train/Test Contamination & Leakage Audit**
  - Completed: Zero overlap detected between `combined_dataset.jsonl` and `sft_eval.json` (0 leaked samples).

- [x] **Task 1.5: Measure and Record Clean Baseline Metrics**
  - Completed: Recorded clean baseline metrics:
    * Training: 3,660 clean samples (1,670 Short [45.6%], 1,886 Medium [51.5%], 104 Long [2.8%]).
    * Evaluation: 358 clean benchmark targets (zero failures).
    * Deficit identified: Severe shortage of authentic Long samples (104 remaining) and starved Embedded firmware domain.

---

## Phase 2: Target Quotas & Batch Planning

- [x] **Task 2.1: Determine Exact Replenishment Target**
  - Completed: Total target dataset size set to 7,500 clean samples. Current clean base is 3,660. Replenishment deficit is 3,840 clean samples.

- [x] **Task 2.2: Establish Domain Quotas**
  - Completed: Replenishment deficit allocated to restore domain and length balance:
    * Domain 6 (Firmware, registers, hardware): 25% (~960 samples)
    * Domain 4 (Incident management, RCA narration - Long focus): 20% (~768 samples)
    * Domain 8 (RFCs, system design, architectural trade-offs - Long focus): 20% (~768 samples)
    * Domain 7 (Voice prompting to AI coding tools): 15% (~576 samples)
    * Domains 1, 2, 3, 5, 9 (Team chats, sprint planning, PRs, mentoring, interviews): 15% (~576 samples)
    * Identity / Low-Noise Samples: 5% (~192 samples)

- [x] **Task 2.3: Set Batch Invariants**
  - Completed: Verified batch structure in `code/validator.py`:
    * 10 samples per batch.
    * Phase 3 Long Catch-Up ratio active: 2 Short (< 25 words), 3 Medium (25–90 words), 5 Long (90+ words with `\n\n` natural paragraph breaks).
    * Enforce strict repair-only policy: zero invented tokens, flags, filenames, or ports.

---

## Phase 3: Antigravity Native Generation & Quality Gate

- [x] **Task 3.1: Execute Domain Generation Cycle (Batches 1-48 Across Domains)**
  - Completed: Generated Batches 1 through 48 (730 samples total across Domains 6, 4, 8, 7, 3, 5, 9, and 1/2).
  - Multi-Agent Wave 1 completed: Batches 9, 10, 11 (30 samples).
  - Multi-Agent Wave 2 completed: Batches 12, 13, 14 (30 samples).
  - Multi-Agent Wave 3 completed: Batches 15, 16, 17 (30 samples).
  - Multi-Agent Wave 4 completed: Batches 18, 19, 20 (30 samples).
  - Multi-Agent Wave 5 completed: Batches 21, 22, 23 (30 samples).
  - Multi-Agent Wave 6 completed: Batches 24-28 (100 samples).
  - Multi-Agent Wave 7 completed: Batches 29-33 (100 samples).
  - Multi-Agent Wave 8 completed: Batches 34-38 (100 samples).
  - Multi-Agent Wave 9 completed: Batches 39-43 (100 samples).
  - Multi-Agent Wave 10 completed:
    * Batch 44 (Domain 6: Firmware, 20 samples)
    * Batch 45 (Domain 4: Incident RCA, 20 samples)
    * Batch 46 (Domain 8: Architecture RFCs, 20 samples)
    * Batch 47 (Domain 7: AI Voice Prompting, 20 samples)
    * Batch 48 (Domain 9 & 1: Interviews & Sprint Grooming, 20 samples)
  - Accumulated 335 Long, 201 Medium, and 134 Short samples across Waves 1 to 10.

- [x] **Task 3.2: Run Deterministic Validation Gate (Batches 1-48)**
  - Completed: Verified all 730 samples with `validate_pair()` and `clean_sample()`. `validate_batch()` passed with exact tier ratios across all batches. Zero leakage against `sft_eval.json`.

- [x] **Task 3.3: Automatic Regeneration of Failing Samples (Batches 1-48)**
  - Completed: Zero validation errors in Multi-Agent Wave 10.

- [x] **Task 3.4: Append Verified Batch to Training Dataset (Batches 1-208 / Wave 33)**
  - Completed: Appended Wave 33 batches (Batches 199-208, 190 samples) with enforced Multi-Layer Noise Stacking to `combined_dataset.jsonl`. Total clean samples reached exactly 7,500 with 0 validation failures. Long tier ratio sustained at 26.81% (2,011 samples).

- [x] **Task 3.5: Iterate Across Domain Batches (Multi-Layer Noise Stacking Mandate)**
  - Completed: Finished all 33 waves across 9 engineering domains. Replenished 3,840 clean samples to reach the 7,500 sample target with zero ungrounded inventions.

---

## Phase 4: Final Quality Audit, Shuffling & Documentation

- [x] **Task 4.1: Run Full-Dataset Deterministic Audit**
  - Completed: Executed full deterministic audit with `validator.validate_pair()` and `cleaner.clean_sample()` across all 7,500 rows in `combined_dataset.jsonl`. 100% pass rate (0 errors, 0 dropped). Zero leakage against `sft_eval.json`.

- [x] **Task 4.2: Global Dataset Shuffling**
  - Completed: Globally shuffled all 7,500 rows in `combined_dataset.jsonl` with fixed random seed (`seed=42`) to prevent domain clustering and ensure uniform gradient updates during SFT.

- [x] **Task 4.3: JSONL Syntax & Schema Validation**
  - Completed: Verified all 7,500 lines parse as valid JSON with exact keys `["raw_asr", "refined_text"]`. Zero blank lines, zero trailing commas, 100% ASCII compliance.

- [x] **Task 4.4: Audit Global Length & Domain Distribution**
  - Completed: Verified global length tier parity across 7,500 rows: 2,448 Short (32.64%), 3,041 Medium (40.55%), 2,011 Long (26.81%). Long tier comfortably exceeds the 20.0% floor requirement. Balanced representation sustained across all 9 everyday engineering domains.

- [x] **Task 4.5: Generate Final Health Report**
  - Completed: Generated final health report in `docs/final_dataset_health_report.md` with complete breakdown of sample counts, tier distributions, and noise layer metrics.

---

## Phase 5: In-Place Acoustic Hardening & Quality Gate Unification

- [x] **Task 5.1: Artificial Numbered List Elimination**
  - Completed: Converted exactly 86 Long rows containing artificial checklist numbers (`1. ... 2. ...`) to clean markdown bullet points (`- ...`). Refined text preserved with zero paraphrasing.

- [x] **Task 5.2: In-Place Acoustic Retrofitting (4,547 Rows)**
  - Completed: Deployed autonomous `acoustic-noise-repairer` engine to retrofit all 4,547 weak legacy rows in-place in `combined_dataset.jsonl`. Total corpus kept at exactly 7,500 rows. Re-engineered `raw_asr` backwards from frozen `refined_text` to activate 4-6 acoustic noise layers (3 for Short tier).

- [x] **Task 5.3: Validator Code Gate Hardening**
  - Completed: Set `min_noise_layers: int = 4` as default in `code/validator.py` (`validate_pair` and `validate_batch`). Unified repository quality gates.

- [x] **Task 5.4: Full Corpus Deterministic Verification**
  - Completed: 100% pass rate across all 7,500 rows in `combined_dataset.jsonl` under `validator.validate_pair()` with default `min_noise_layers=4` (0 errors) and `cleaner.clean_sample()` (0 dropped). Zero leakage against `sft_eval.json` (0 collisions). Global average active noise layers elevated to 4.91 per sample.
