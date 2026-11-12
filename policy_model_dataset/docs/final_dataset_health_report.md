# Final Dataset Health & Verification Report

**Executive Summary**
- **Corpus File**: `data/sft_train.json`
- **Total Validated Samples**: 13,295 unique pairs
- **Distinct Ground-Truth Scenarios**: 5,515 scenarios
- **Passing Gold Samples**: 10,820 samples (81.4%) passing gold acoustic validation
- **Samples Flagged for Repair**: 2,475 samples prioritized in `data/weak_samples_manifest.json`
- **Evaluation Leakage**: Exactly 0 collisions against `data/sft_eval.json` (358 targets)
- **Active Skill**: `.agents/skills/asr-data-curator/SKILL.md`
- **Active Validation Gate**: `code/gold_dataset_validator.py`

---

**Core Invariants Enforced**
1. **Frozen Ground Truth**: `refined_text` is 100% immutable across all scripts and repairs.
2. **Deterministic Quality Gate**: Validated with `code/gold_dataset_validator.py`.
3. **No Markdown in Raw Audio**: Strictly zero backticks, zero bullet lists, and zero multi-paragraph breaks in `raw_asr`.
4. **Noise Calibration**: Word Error Rate target between 10% and 35%, with character similarity between 55% and 98%.
5. **No Long Pristine Sentences**: Reject multi-sentence inputs where any 15+ word sentence remains 100% clean.
6. **Zero Benchmark Leakage**: Complete set disjointness between training set and evaluation set.
