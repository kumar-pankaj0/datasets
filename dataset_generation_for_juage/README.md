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

## Mathematical Signal Auditing (`verify.py`)
To mathematically guarantee that our datasets contain high-quality signal and no lazy shortcuts, we run strict statistical audits on the labels. The `verify.py` script checks three things:

1. **Variance (Spreadness):** We want a high variance (e.g., > 7.5). If variance is near 0, the dataset is stuck on the "happy path" and lacks hard edge cases. High variance forces the gradient optimizer to do real work.
2. **Shannon Entropy (Distribution):** We want entropy near its mathematical maximum (~2.32 bits for 5 classes). This proves our dataset has a perfectly uniform distribution and is not flooded with biased scores (e.g., too many `9`s).
3. **Pearson Correlation (Independence):** We want all cross-metric correlations to be near zero ($|r| \approx 0$). This proves the metrics are orthogonal, meaning the neural network cannot cheat by using one metric (like formatting) to guess the score of another metric (like grammar).
