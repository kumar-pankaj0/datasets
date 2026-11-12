"""
Gold Dataset Validator for Speech-to-Text (ASR) Refinement Datasets.
Replaces legacy validator.py and cleaner.py with deterministic quality checks
grounded in authentic Whisper ASR failure characteristics.
"""

import difflib
import json
import re
from typing import Dict, List, Optional, Tuple


def normalize_for_comparison(text: str) -> str:
    """Strip markdown, normalize whitespace, and lowercase for core comparison."""
    # Remove markdown backticks, bold, italic
    cleaned = re.sub(r"[`*_~]", "", text)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Calculate token-level Word Error Rate (WER) using Levenshtein distance."""
    ref_words = re.findall(r"\b[\w'-]+\b", reference.lower())
    hyp_words = re.findall(r"\b[\w'-]+\b", hypothesis.lower())
    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    r_len, h_len = len(ref_words), len(hyp_words)
    dp = [[0] * (h_len + 1) for _ in range(r_len + 1)]
    for i in range(r_len + 1):
        dp[i][0] = i
    for j in range(h_len + 1):
        dp[0][j] = j

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[r_len][h_len] / r_len


def validate_sample(raw_asr: str, refined_text: str) -> Tuple[bool, str, Dict[str, float]]:
    """
    Validates a single (raw_asr, refined_text) pair.

    Returns:
        (is_valid, failure_reason, metrics_dict)
    """
    metrics: Dict[str, float] = {}

    if not isinstance(raw_asr, str) or not raw_asr.strip():
        return False, "raw_asr is empty or not a string", metrics

    if not isinstance(refined_text, str) or not refined_text.strip():
        return False, "refined_text is empty or not a string", metrics

    # 1. Prohibit Markdown formatting inside raw_asr (must look like spoken transcript)
    if "`" in raw_asr:
        return False, "raw_asr contains Markdown backticks", metrics

    if "\n\n" in raw_asr:
        return False, "raw_asr contains multi-paragraph blank lines", metrics

    lines = [line.strip() for line in raw_asr.splitlines() if line.strip()]
    for line in lines:
        if line.startswith(("- ", "* ", "#")):
            return False, "raw_asr contains Markdown bullet points or headers", metrics

    # 2. Extract words and measure length ratio
    raw_words = re.findall(r"\b[\w'-]+\b", raw_asr)
    ref_words = re.findall(r"\b[\w'-]+\b", refined_text)

    if not raw_words or not ref_words:
        return False, "Zero word tokens extracted from sample", metrics

    len_ratio = len(raw_words) / len(ref_words)
    metrics["length_ratio"] = round(len_ratio, 3)

    if len_ratio < 0.50 or len_ratio > 1.80:
        return False, f"Extreme length divergence (length ratio {len_ratio:.2f})", metrics

    # 3. Compute WER and Character Similarity
    wer = word_error_rate(refined_text, raw_asr)
    metrics["wer"] = round(wer, 3)

    norm_ref = normalize_for_comparison(refined_text)
    norm_raw = normalize_for_comparison(raw_asr)
    char_sim = difflib.SequenceMatcher(None, norm_ref, norm_raw).ratio()
    metrics["char_similarity"] = round(char_sim, 3)

    # 4. Check for under-noised / pristine samples
    # For very short sentences (< 10 words), allow slightly lower WER if at least 1 word changed
    if len(ref_words) < 10:
        if char_sim > 0.985 or wer == 0.0:
            return False, f"Under-noised sample (WER={wer:.1%}, similarity={char_sim:.1%})", metrics
    else:
        if wer < 0.08 or char_sim > 0.980:
            return False, f"Under-noised sample: WER ({wer:.1%}) below 8% or similarity ({char_sim:.1%}) above 98%", metrics

    # 5. Check for over-corrupted / ungrounded gibberish
    if char_sim < 0.55 and wer > 0.60:
        return False, f"Over-corrupted sample: similarity ({char_sim:.1%}) too low, unrecoverable", metrics

    # 6. Multi-sentence noise distribution check
    # Split refined_text into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", refined_text) if len(s.strip().split()) >= 4]
    if len(sentences) >= 3:
        # Check that acoustic noise is distributed (raw_asr shouldn't contain a verbatim 30+ word chunk)
        for sent in sentences:
            if len(sent.split()) >= 15 and sent.lower() in raw_asr.lower():
                return False, f"Long pristine sentence detected inside multi-sentence sample: '{sent[:40]}...'", metrics

    return True, "Valid gold sample", metrics


def validate_dataset(filepath: str) -> Dict:
    """Audits an entire JSON dataset file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {filepath}, got {type(data)}")

    total = len(data)
    valid_count = 0
    weak_count = 0
    invalid_count = 0
    reasons: Dict[str, int] = {}
    metrics_sum = {"wer": 0.0, "char_similarity": 0.0, "length_ratio": 0.0}

    for idx, item in enumerate(data):
        raw = item.get("raw_asr", "")
        ref = item.get("refined_text", "")

        is_valid, reason, m = validate_sample(raw, ref)
        if is_valid:
            valid_count += 1
            for k in metrics_sum:
                metrics_sum[k] += m.get(k, 0.0)
        else:
            category = reason.split(":")[0]
            reasons[category] = reasons.get(category, 0) + 1
            if "Under-noised" in category:
                weak_count += 1
            else:
                invalid_count += 1

    avg_metrics = {
        k: round(v / max(1, valid_count), 3) for k, v in metrics_sum.items()
    }

    return {
        "filepath": filepath,
        "total_samples": total,
        "valid_samples": valid_count,
        "weak_samples": weak_count,
        "invalid_samples": invalid_count,
        "pass_rate": round(valid_count / max(1, total), 3),
        "reasons": reasons,
        "average_metrics": avg_metrics,
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sft_train.json"
    result = validate_dataset(path)
    print(json.dumps(result, indent=2))
