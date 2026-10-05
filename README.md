# Dataset Generation for Judge Model

This repository contains datasets and scripts used to train and evaluate a metric-based STT (Speech-to-Text) Judge model. The repository structure reflects an iterative AI engineering lifecycle designed to fix blind spots and prevent catastrophic forgetting (information loss).

## Dataset Timeline & Usage Guide

1. **`data_baseline.json` (Iteration 1 Training)**
   The original 2,917 baseline samples. This was used for the initial training run from scratch.

2. **`data_edge_cases.json` (The Fix)**
   450 extreme edge cases (prompt injections, formatting abuse, filler blindness) that were generated when we noticed bad performance on specific tasks after the first iteration of training.

3. **`data_phase2_train.json` (Iteration 2 Incremental Training)**
   The dataset you use for incremental fine-tuning (LoRA). It carefully mixes the new edge cases with the old baseline dataset. This is crucial so that **no information loss happens** (the model learns the new edge cases without forgetting the baseline).

4. **`data_full.json` (Train From Scratch)**
   The combined 3,367 sample dataset (baseline + edge cases). Use this if you want to completely restart and train the model from scratch again, ensuring the edge-case problems do not happen from the start.

5. **`data_eval.json` (Evaluation)**
   A 265-sample, mathematically balanced evaluation dataset. It is strictly filtered so that zero samples overlap with `data_phase2_train.json`, preventing data leakage during your evaluations.

## Scripts
* **`build_train.py`**: Generates `data_phase2_train.json` by calculating score deficits and pulling needed baseline samples.
* **`build_eval.py`**: Generates the leakage-free `data_eval.json` test set.
* **`verify.py`**: Asserts schema integrity and perfectly orthogonal metric correlation (Pearson |r|).
