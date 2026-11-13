"""
Gold Dataset Validator for Speech-to-Text (ASR) Refinement Datasets.
Replaces legacy validator.py and cleaner.py with deterministic quality checks
grounded in authentic Whisper ASR failure characteristics and anti-reward-hacking gates.
"""

import argparse
from collections import Counter
import difflib
import json
import os
import re
from typing import Dict, List, Optional, Tuple


def normalize_for_comparison(text: str) -> str:
    """Strip markdown, normalize whitespace, and lowercase for core comparison."""
    cleaned = re.sub(r"[`*_~]", "", text)
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


def _is_mechanical_truncation(ref_w: str, raw_w: str) -> bool:
    """
    Detects if raw_w is a lazy substring/character-slice of ref_w
    (e.g., 'minute' -> 'minut', 'automate' -> 'automat', 'release' -> 'releas', 'thinking' -> 'thinkin').
    """
    if ref_w == raw_w or len(ref_w) < 4 or len(raw_w) < 3:
        return False

    # Allow standard plural/tense inflection shifts on real root words only if >=2 chars changed
    # Pure 1-2 char prefix/suffix slicing on words >=5 chars is the classic script cheat
    if ref_w.startswith(raw_w) or ref_w.endswith(raw_w):
        diff_len = len(ref_w) - len(raw_w)
        if 1 <= diff_len <= 2:
            return True

    # Also catch 1-character internal deletion (e.g. 'testing' -> 'tsting')
    if len(ref_w) - len(raw_w) == 1:
        it = iter(ref_w)
        if all(c in it for c in raw_w):
            return True

    return False


def _is_lazy_orthographic_split(ref_chunk_str: str, raw_chunk_str: str) -> bool:
    """
    Catches lazy compound word space-splitting ('database' -> 'data base')
    and repetitive '-ing' -> ' in' tricks ('switching' -> 'switch in')
    where the underlying letter sequence barely changed.
    """
    ref_clean = ref_chunk_str.replace(" ", "").replace("-", "")
    raw_clean = raw_chunk_str.replace(" ", "").replace("-", "")
    if not ref_clean or not raw_clean:
        return False

    # 1. Pure space insertion/removal ('deadlock' -> 'dead lock', 'microservices' -> 'micro services')
    if ref_clean == raw_clean:
        return True

    # 2. Lazy '-ing' -> 'in' or 'e' + 'in' ('monitoring' -> 'monitor in', 'handling' -> 'handle in')
    if ref_clean.endswith("ing") and raw_clean.endswith("in"):
        ref_stem = ref_clean[:-3]
        raw_stem = raw_clean[:-2].rstrip("e")
        if ref_stem == raw_stem:
            return True

    return False


def analyze_word_edits(
    ref_words: List[str], raw_words: List[str]
) -> Dict[str, object]:
    """
    Aligns word tokens using SequenceMatcher to classify the structural nature of edits.
    Catches 1-to-1 word slicing, lazy space-splitting, and checks for multi-word boundary shifts.
    """
    ref_lower = [w.lower() for w in ref_words]
    raw_lower = [w.lower() for w in raw_words]

    matcher = difflib.SequenceMatcher(None, ref_lower, raw_lower, autojunk=False)
    total_edit_ops = 0
    truncation_count = 0
    lazy_split_count = 0
    boundary_shift_count = 0  # Splits, merges, insertions, deletions
    edit_pairs: List[Tuple[str, str]] = []
    truncated_examples: List[str] = []
    lazy_split_examples: List[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        ref_chunk = ref_lower[i1:i2]
        raw_chunk = raw_lower[j1:j2]
        ref_str = " ".join(ref_chunk)
        raw_str = " ".join(raw_chunk)
        edit_pairs.append((ref_str, raw_str))
        total_edit_ops += 1

        is_trunc = False
        for rw, aw in zip(ref_chunk, raw_chunk):
            if _is_mechanical_truncation(rw, aw):
                truncation_count += 1
                truncated_examples.append(f"{rw}->{aw}")
                is_trunc = True

        if _is_lazy_orthographic_split(ref_str, raw_str):
            lazy_split_count += 1
            lazy_split_examples.append(f"{ref_str}->{raw_str}")

        if len(ref_chunk) != len(raw_chunk):
            boundary_shift_count += 1

    truncation_ratio = truncation_count / max(1, total_edit_ops)
    lazy_split_ratio = lazy_split_count / max(1, total_edit_ops)
    boundary_shift_ratio = boundary_shift_count / max(1, total_edit_ops)

    return {
        "total_edit_ops": total_edit_ops,
        "truncation_count": truncation_count,
        "truncation_ratio": round(truncation_ratio, 3),
        "lazy_split_count": lazy_split_count,
        "lazy_split_ratio": round(lazy_split_ratio, 3),
        "boundary_shift_count": boundary_shift_count,
        "boundary_shift_ratio": round(boundary_shift_ratio, 3),
        "truncated_examples": truncated_examples,
        "lazy_split_examples": lazy_split_examples,
        "edit_pairs": edit_pairs,
    }


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
    char_sim = difflib.SequenceMatcher(None, norm_ref, norm_raw, autojunk=False).ratio()
    metrics["char_similarity"] = round(char_sim, 3)

    # 4. Check for under-noised / pristine samples
    if len(ref_words) < 10:
        if char_sim > 0.985 or wer == 0.0:
            return False, f"Under-noised sample (WER={wer:.1%}, similarity={char_sim:.1%})", metrics
    else:
        if wer < 0.08 or char_sim > 0.980:
            return False, f"Under-noised sample: WER ({wer:.1%}) below 8% or similarity ({char_sim:.1%}) above 98%", metrics

    # 5. Check for over-corrupted / ungrounded gibberish
    if char_sim < 0.55 and wer > 0.60:
        return False, f"Over-corrupted sample: similarity ({char_sim:.1%}) too low, unrecoverable", metrics

    # 6. Anti-Reward-Hacking Gate: Mechanical Word Slicing & Lazy Space Splits
    edit_analysis = analyze_word_edits(ref_words, raw_words)
    metrics["truncation_ratio"] = edit_analysis["truncation_ratio"]
    metrics["lazy_split_ratio"] = edit_analysis["lazy_split_ratio"]
    metrics["boundary_shift_ratio"] = edit_analysis["boundary_shift_ratio"]

    # Reject if mechanical truncations detected
    if edit_analysis["truncation_count"] >= 2 or (
        edit_analysis["total_edit_ops"] >= 3 and edit_analysis["truncation_ratio"] > 0.25
    ):
        examples = ", ".join(edit_analysis["truncated_examples"][:3])
        return (
            False,
            f"Mechanical suffix/character slicing detected ({examples})",
            metrics,
        )

    # Reject if lazy space-splits and -ing loops dominate edits (> 50% of edits in sample)
    if edit_analysis["lazy_split_ratio"] > 0.50 or (
        edit_analysis["lazy_split_count"] >= 2 and edit_analysis["lazy_split_ratio"] >= 0.33
    ):
        examples = ", ".join(edit_analysis["lazy_split_examples"][:3])
        return (
            False,
            f"Lazy orthographic space-splitting or -ing loop detected ({examples}) - requires genuine phonetic spelling changes",
            metrics,
        )

    # 7. Multi-sentence noise distribution check
    sentences = [s.strip() for s in re.split(r"[.!?]+", refined_text) if len(s.strip().split()) >= 4]
    if len(sentences) >= 3:
        for sent in sentences:
            if len(sent.split()) >= 15 and sent.lower() in raw_asr.lower():
                return False, f"Long pristine sentence detected inside multi-sentence sample: '{sent[:40]}...'", metrics

    return True, "Valid gold sample", metrics


def validate_dataset(filepath: str) -> Dict:
    """Audits an entire JSON dataset file, including batch-level reward-hacking gates."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {filepath}, got {type(data)}")

    total = len(data)
    valid_count = 0
    weak_count = 0
    invalid_count = 0
    reasons: Dict[str, int] = {}
    metrics_sum = {
        "wer": 0.0,
        "char_similarity": 0.0,
        "length_ratio": 0.0,
        "truncation_ratio": 0.0,
        "lazy_split_ratio": 0.0,
        "boundary_shift_ratio": 0.0,
    }
    all_edit_pairs: Counter = Counter()

    for item in data:
        raw = item.get("raw_asr", "")
        ref = item.get("refined_text", "")

        raw_words = re.findall(r"\b[\w'-]+\b", raw) if isinstance(raw, str) else []
        ref_words = re.findall(r"\b[\w'-]+\b", ref) if isinstance(ref, str) else []
        if raw_words and ref_words:
            edit_info = analyze_word_edits(ref_words, raw_words)
            for pair in edit_info["edit_pairs"]:
                if pair[0] and pair[1]:
                    all_edit_pairs[f"{pair[0]} -> {pair[1]}"] += 1

        is_valid, reason, m = validate_sample(raw, ref)
        if is_valid:
            valid_count += 1
            for k in metrics_sum:
                metrics_sum[k] += m.get(k, 0.0)
        else:
            category = reason.split(":")[0].split("(")[0].strip()
            reasons[category] = reasons.get(category, 0) + 1
            if "Under-noised" in category:
                weak_count += 1
            else:
                invalid_count += 1

    avg_metrics = {
        k: round(v / max(1, valid_count), 3) for k, v in metrics_sum.items()
    }

    # Batch-Level Anti-Script Audits
    batch_warnings: List[str] = []
    hard_script_failure = False

    if total >= 10:
        # Check 1: Are all errors 1-to-1 in-place word replacements?
        if avg_metrics["boundary_shift_ratio"] < 0.15:
            msg = (
                f"LOW BOUNDARY SHIFT RATIO ({avg_metrics['boundary_shift_ratio']:.1%}): "
                "Errors are almost purely 1-to-1 word swaps. Real ASR requires splits/merges (e.g., 'kubectl' -> 'kube control')."
            )
            batch_warnings.append(msg)
            hard_script_failure = True

        # Check 2: Did a script repeat the exact same edit rule over and over?
        total_pair_edits = sum(all_edit_pairs.values())
        if total_pair_edits >= 20:
            most_common_edit, count = all_edit_pairs.most_common(1)[0]
            repeat_share = count / total_pair_edits
            if repeat_share > 0.12:
                msg = (
                    f"REPETITIVE SCRIPT PATTERN DETECTED: Edit '{most_common_edit}' accounts for "
                    f"{repeat_share:.1%} ({count}/{total_pair_edits}) of all word edits in batch."
                )
                batch_warnings.append(msg)
                hard_script_failure = True

        # Check 3: Is the batch dominated by lazy space-splits instead of true phonetic noise?
        if avg_metrics.get("lazy_split_ratio", 0.0) > 0.40:
            msg = (
                f"HIGH LAZY ORTHOGRAPHIC SPLIT RATIO ({avg_metrics['lazy_split_ratio']:.1%}): "
                "Edits are dominated by space-insertion ('data base') or '-ing' -> 'in' tricks. Real Whisper noise requires true phonetic homophone/spelling substitutions."
            )
            batch_warnings.append(msg)
            hard_script_failure = True

    final_pass_rate = round(valid_count / max(1, total), 3)
    if hard_script_failure:
        final_pass_rate = 0.0

    return {
        "filepath": filepath,
        "total_samples": total,
        "valid_samples": valid_count,
        "weak_samples": weak_count,
        "invalid_samples": invalid_count,
        "pass_rate": final_pass_rate,
        "batch_script_warnings": batch_warnings,
        "reasons": reasons,
        "average_metrics": avg_metrics,
    }


def process_batch_filtering(
    batch_path: str,
    merge_passed_path: Optional[str] = None,
    split_failed_path: Optional[str] = None,
) -> Dict:
    """
    Validates a batch file.
    Merges passing samples into merge_passed_path (by index or id).
    Appends failing samples into split_failed_path for retry.
    """
    with open(batch_path, "r", encoding="utf-8") as f:
        batch_items = json.load(f)

    if not isinstance(batch_items, list):
        raise ValueError(f"Expected JSON list in {batch_path}")

    # If merge_passed_path exists, load master dataset for ground-truth reference
    master_dataset = None
    if merge_passed_path and os.path.exists(merge_passed_path):
        with open(merge_passed_path, "r", encoding="utf-8") as f:
            master_dataset = json.load(f)

    passed_items = []
    failed_items = []

    for item in batch_items:
        raw_asr = item.get("raw_asr", "")
        refined_text = item.get("refined_text", "")
        idx = item.get("index")

        if not refined_text and master_dataset is not None and isinstance(idx, int) and 0 <= idx < len(master_dataset):
            refined_text = master_dataset[idx].get("refined_text", "")

        is_valid, reason, metrics = validate_sample(raw_asr, refined_text)

        if is_valid:
            passed_record = dict(item)
            passed_record["raw_asr"] = raw_asr
            if refined_text:
                passed_record["refined_text"] = refined_text
            passed_items.append(passed_record)
        else:
            failed_record = dict(item)
            failed_record["raw_asr"] = raw_asr
            if refined_text:
                failed_record["refined_text"] = refined_text
            failed_record["failure_reason"] = reason
            failed_items.append(failed_record)

    # 1. Update passing samples into master dataset
    if merge_passed_path and passed_items:
        if master_dataset is not None:
            for p in passed_items:
                idx = p.get("index")
                if isinstance(idx, int) and 0 <= idx < len(master_dataset):
                    master_dataset[idx]["raw_asr"] = p["raw_asr"]
            with open(merge_passed_path, "w", encoding="utf-8") as f:
                json.dump(master_dataset, f, indent=2, ensure_ascii=False)
            print(f"[Merge] Updated {len(passed_items)} passed samples into {merge_passed_path}")

    # 2. Append/Write failing samples into split_failed_path
    if split_failed_path:
        existing_failed = []
        if os.path.exists(split_failed_path):
            try:
                with open(split_failed_path, "r", encoding="utf-8") as f:
                    existing_failed = json.load(f)
            except Exception:
                existing_failed = []

        existing_indices = {x.get("index") for x in existing_failed if "index" in x}
        for item in failed_items:
            if item.get("index") not in existing_indices:
                existing_failed.append(item)

        os.makedirs(os.path.dirname(os.path.abspath(split_failed_path)), exist_ok=True)
        with open(split_failed_path, "w", encoding="utf-8") as f:
            json.dump(existing_failed, f, indent=2, ensure_ascii=False)
        print(f"[Split] Wrote {len(failed_items)} failed samples to {split_failed_path} (Total queue: {len(existing_failed)})")

    return {
        "batch_total": len(batch_items),
        "passed_count": len(passed_items),
        "failed_count": len(failed_items),
        "pass_rate": round(len(passed_items) / max(1, len(batch_items)), 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Gold Dataset Validator with Anti-Reward-Hacking Gates")
    parser.add_argument("filepath", nargs="?", default="data/sft_train.json", help="Path to JSON file to audit")
    parser.add_argument("--merge-passed", dest="merge_passed", default=None, help="Path to sft_train.json to update passing samples into")
    parser.add_argument("--split-failed", dest="split_failed", default=None, help="Path to left_samples.json to append failing samples into")
    args = parser.parse_args()

    if args.merge_passed or args.split_failed:
        summary = process_batch_filtering(args.filepath, args.merge_passed, args.split_failed)
        print(json.dumps(summary, indent=2))
    else:
        result = validate_dataset(args.filepath)
        print(json.dumps(result, indent=2))
        if result["pass_rate"] < 1.0 or result.get("batch_script_warnings"):
            exit(1)


if __name__ == "__main__":
    main()
