---
name: dataset-generator
description: >-
  Permanent autonomous data generation skill and sub-agent specification for Speech-to-Text (ASR)
  refinement dataset synthesis across 9 engineering domains. Enforces zero-invention, repair-only,
  Phase 3 Long Catch-Up tier ratios (10 Long / 6 Medium / 4 Short), and deterministic Python validation.
---

# Dataset Generator Skill & Sub-Agent Specification

See full documentation and prompt instructions in `prompt/subagent_dataset_generator.md`.

## Core Guidelines
- Invariant: Conservative post-correction (zero invention, repair only).
- Active Batch Distribution: 4 Short (<25w), 6 Medium (25-90w), 10 Long (90+w) [20 samples total].
- Noise Archetypes: All 6 acoustic noise types required (homophones, self-corrections, extended fillers, cut words, phonetic decompositions, spoken hex/digits).
- Multi-Layer Noise Stacking Invariant: Every sample must activate at least 4 of 6 noise layers simultaneously (at least 3 of 6 for Short tier). Batch average must be >= 4.0 active noise layers. Single-layer (filler-only or homophone-only) samples are strictly prohibited.
- Anti-Example Bias: Examples illustrate acoustic mechanics only. Never copy prompt examples. Enforce high lexical and situational diversity across chips, buses, and tools.
- Validation: Mandatory verification through `code/validator.py` (validate_batch with min_short=4, min_medium=6, min_long=10) and `code/cleaner.py`.
- Final Return Output & Actionable Feedback Mandate:
  * Every sub-agent reports sample metrics, tier counts, and validation retries.
  * Provide feedback ONLY on genuine, high-value technical issues (e.g., validator rule edge cases, domain terminology conflicts, or recurring failure patterns).
  * Avoid frivolous or trivial feedback; master prompt updates occur only when feedback represents a solid, verified systemic improvement.
