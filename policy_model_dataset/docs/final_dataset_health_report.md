# Final Dataset Health & Verification Report

**Executive Summary**
- **Corpus File**: `combined_dataset.jsonl`
- **Total Validated Samples**: 7500 clean samples
- **Baseline Clean Samples**: 3,660 rows
- **Replenished Samples Added**: 3,840 rows across 33 Multi-Agent Waves (Batches 9-208)
- **In-Place Hardened Samples**: 4,547 rows upgraded to 4-6 layers (3 for Short)
- **Validation Failure Rate**: 0.00% (0 errors across validator.py and cleaner.py under min_noise_layers=4)
- **Evaluation Leakage**: 0 collisions against sft_eval.json (358 targets)
- **Shuffle State**: Globally shuffled with fixed seed=42 (uniform domain distribution)

**Length Tier Distribution**
- **Short Tier (< 25 words)**: 2448 samples (32.64%)
- **Medium Tier (25 to 89 words)**: 3041 samples (40.55%)
- **Long Tier (90+ words)**: 2011 samples (26.81%)
- **Long Tier Compliance**: 26.81% (exceeds the 20.00% minimum floor requirement)
- **Artificial Numbered Lists in Long Tier**: 0 (all 86 converted to standard markdown bullet points)

**Acoustic Noise Stacking & Complexity**
- **Corpus Average Noise Layers**: 4.91 layers per sample (elevated from 2.95)
- **Noise Layer Histogram (All 7,500 Samples)**:
  - 6 Active Layers: 4135 samples (55.13%)
  - 5 Active Layers: 583 samples (7.77%)
  - 4 Active Layers: 723 samples (9.64%)
  - 3 Active Layers: 2059 samples (27.45%, strictly Short tier)
  - 2 Active Layers: 0 samples (0.00%)
  - 1 Active Layer: 0 samples (0.00%)
  - 0 Active Layers: 0 samples (0.00%)

**Invariants & Quality Gates Enforced**
1. **Zero Invention Invariant**: Zero fabricated tokens, CLI flags, hostnames, register addresses, or hexadecimal values.
2. **Deterministic Sanitization Gate**: All 7,500 rows passed cleaner.py with status 'kept'.
3. **Deterministic Validator Gate**: All 7,500 rows passed validator.validate_pair(min_noise_layers=4) with 0 errors.
4. **No Leakage Invariant**: Strict set disjointness between training corpus and benchmark eval set (0 collisions).
5. **No Domain Clustering**: Uniform stochastic mixing via seed=42 for gradient stability during SFT fine-tuning.
