---
name: acoustic-noise-repairer
description: >-
  Permanent autonomous data repair skill and sub-agent specification for Speech-to-Text (ASR)
  dataset acoustic retrofitting. Takes existing dataset samples with frozen refined_text and
  re-engineers raw_asr to activate 4-5 stacked acoustic noise layers with 100% deterministic grounding.
---

Acoustic Noise Repairer Skill & Sub-Agent Specification

See full documentation and operational prompt instructions in `prompt/subagent_acoustic_repairer.md`.

Core Invariants:
- Invariant 1 (Frozen Refined Text): `refined_text` is strictly read-only and immutable. Never alter, rewrite, or delete any characters in `refined_text`.
- Invariant 2 (Multi-Layer Noise Stacking): Every repaired `raw_asr` must simultaneously activate at least 4 of the 6 acoustic noise layers (at least 3 for Short tier, target 5-6).
- Invariant 3 (100% Acoustic Grounding): Every number, path, register, hex literal, and CLI flag in `refined_text` must be acoustically grounded in `raw_asr`. Zero token invention.
- Invariant 4 (Flat Spoken Speech): `raw_asr` is flat lowercase ASCII with zero punctuation, zero newlines, and zero bullet points.
- Invariant 5 (Deterministic Number Grounding): Use cardinal numbers (one, two) for numbered lists, never ordinals (first, second). Dictate numbers >= 2000 digit-by-digit.
- Invariant 6 (Purpose & Filename Retention): Retain all purpose clause keywords (>3 chars) and repeat filenames as often as they appear in `refined_text`.
- Invariant 7 (Deterministic Python Validation): Mandatory pass on `code/validator.py` (`validate_pair(min_noise_layers=4)`) and `code/cleaner.py` (`clean_sample() == 'kept'`).
- Invariant 8 (Zero Benchmark Leakage): 0 collisions against `sft_eval.json`.
- Invariant 9 (Calibrated Noise Density): Sample noise token frequencies from weighted distributions (1-3 disfluencies for Short, 2-6 for Medium, 4-10 for Long) while clamping cut-words (max 1 in Short) to protect the 20% cleaner recall ceiling.
