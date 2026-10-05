# STT Judge Dataset Pipeline Architecture

This document outlines the pipeline used to generate the synthetic dataset for training an STT judge model.

## Goal
The goal is to train a small policy model via GRPO (Generative Reward Policy Optimization) to evaluate the cleanup of noisy Speech-to-Text (ASR) outputs. The judge model must independently evaluate 4 dimensions:

1. **Faithfulness**: Did the cleanup preserve the core technical meaning without hallucinating details or changing numbers?
2. **Noise Removed**: Did the cleanup successfully strip filler words (uh, um, like), stutters, and false starts?
3. **Errors Fixed**: Were acoustic misinterpretations and cut-words (e.g. `authenticat`, `mem`, `configur`) correctly inferred and fixed?
4. **Formatting**: Did the model apply appropriate markdown structure (paragraphs, bullet lists, code backticks) based on utterance length?

## Scoring Scale (1 to 9)
We use a discrete 1, 3, 5, 7, 9 scale.
* **1 (Very Poor)**: Complete failure in this dimension.
* **5 (Moderate)**: Average, partially correct.
* **9 (Very Good / Production-Grade)**: Perfect execution.

### Why not 1-99?
Small LLMs struggle to calibrate continuous 99-class logits effectively due to BPE subword tokenization dynamics. 9^4 combinations provide 6,561 distinct states, which is rich enough for variance without collapsing the gradients.

## Core Pipeline (The Map-Reduce Architecture)
To scale the dataset massively without mode collapse or stylistic repetition, we use a map-reduce subagent architecture.

1. **Score Blueprint Generation**: We pre-compute exact target scores (e.g., `target_matrix_50.json`) that guarantee exactly 20% of samples fall into each of the {1, 3, 5, 7, 9} buckets for every metric, AND that the Pearson correlation between any two metrics is $|r| < 0.70$ (usually $< 0.03$).
2. **Map (Generator Subagents)**: We spawn multiple autonomous generator agents (`domain-dataset-generator`). Each agent focuses on a specific technical domain (e.g., Kubernetes, eBPF, WebRTC) and generates exactly 50 samples matching the blueprint. Each agent writes its own `verify.py` to assert it met the length and orthogonality requirements.
3. **Reduce (Merger Subagent)**: A central merger agent waits for all shards, independently verifies them again, deduplicates by `(raw_asr, refined_text)`, and merges them into the master `dataset.json`.

## Crucial Calibrated Formatting Rules
If we always force heavy markdown (like `---` and `\n\n`), the RL policy will reward-hack and start inserting dividers into 3-word sentences. To prevent this:
- **Short Utterances (<25 words)**: A score of 9 MUST ONLY use clean inline punctuation and backticks. No dividers or paragraphs.
- **Long Utterances (90+ words)**: A score of 9 MUST use structured markdown (paragraphs, horizontal dividers, numbered lists).

## Automated Quality Gating (`verify_dataset.py`)
Before a merge is accepted, the dataset must pass:
1. Schema validation.
2. Perfect balance check (15% to 32% per bucket).
3. Pearson Correlation Matrix (all pairwise $|r| < 0.70$).
4. Reward Signal Diversity check (ensuring high variance in the 4D score profiles to prevent $\sigma(R) \to 0$, which kills the policy gradient update).
