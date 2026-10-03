# STT Evaluator Judge Dataset

This repository stores synthetic datasets for fine-tuning a small LLM to act as a judge/evaluator for Speech-to-Text (STT) outputs. The dataset teaches the model to score ASR text based on four orthogonal metrics.

## Files
- `dataset.json`: The master dataset containing all generated samples (2,917 samples).
- `verify_dataset.py`: The main quality gate script that ensures distributions, orthogonality, and formatting rules are strictly met.
- `pipeline_architecture.md`: Detailed documentation on the data generation pipeline, subagent architecture, and the definition of the 4 scoring metrics.
- `varify_rules.md`: The rulebook used by the LLM subagents to enforce quality.
- `scores_blueprint.json` / `target_matrix_50.json`: Pre-computed score matrices designed to guarantee perfect bucket balance and zero metric correlation (Pearson |r| < 0.03).
