  HOW SENIOR ML PRACTITIONERS DEFINE DATASET TIERS

  Synthesized from engineering postmortems and practitioner consensus across ML
  engineering teams:

  BAD DATASET

  • Volume over curation: Thousands of uninspected samples containing template
  repetition, boilerplate prompt leakage ("Here is the refined output:"), and
  hallucinations.
  • Label collapse: Dominant target clustering (e.g., 80% positive labels) causing
  the loss surface to converge on predicting a single constant mode.
  • Spurious correlation: The model learns superficial shortcuts (e.g., associating
  longer length with higher quality scores) rather than evaluating underlying
  semantic features.
  • Zero contrast: Isolated samples without counterfactuals (variations of the same
  input testing specific failure modes), forcing the model to infer boundaries
  without direct comparison points.

  GOOD DATASET

  • Balanced label histogram: Target scores distributed uniformly across evaluation
  buckets {1, 3, 5, 7, 9} rather than skewed toward positive examples.
  • Deterministic rubric execution: Consistent scoring where identical failure types
  receive identical scores across the dataset without annotator drift (gradual shift
  in subjective criteria over time).
  • Domain breadth: Covers diverse systems, CLI tools, protocols, and error codes
  rather than repeating a single environment like Kubernetes.
  • Structural hygiene: Strict schema compliance with zero syntax errors, valid JSON
  encoding, and escaped character verification.

  VERY GOOD (PRODUCTION-GRADE) DATASET

  • Hard negatives over synthetic noise: Uses realistic acoustic degradation (e.g.,
  clipped plosives like "lease ass", DSP noise-gate dropouts, and out-of-vocabulary
  phonetic decompositions like "in grass engine x") rather than artificial typos.
  • Orthogonal dimension independence: Distinct failure modes isolated per axis (e.g.,
  (9, 1, 9, 9) for disfluency retention vs (1, 9, 9, 9) for semantic reversal),
  preventing the neural network from correlating all scoring heads.
  • Contrastive rollout pairs: Identical raw_asr inputs paired with multiple
  alternative completions spanning gold, mediocre, and degenerate tiers, directly
  driving high advantage variance (σ_R > 0) in RL algorithms like GRPO (Group
  Relative Policy Optimization).
  • Manual spot-check pass rate: 100% human-verified calibration on edge boundaries
  (verifying the exact technical fault separating a score 5 from a score 7).

  HOW SENIOR ENGINEERS AUDIT IN PRACTICE

  1. Spot-check worst and best deciles: Inspect 20 samples from bucket 1 and 20 from
  bucket 9 to verify true polarity separation.
  2. Correlation matrix calculation: Run Pearson correlation across target dimensions
  to verify no two scoring keys have r > 0.70 (confirming metric orthogonality).
  3. Loss curve diagnostic: Evaluate early training checkpoints; instant loss
  collapse indicates label predictability shortcuts rather than true task learning.

