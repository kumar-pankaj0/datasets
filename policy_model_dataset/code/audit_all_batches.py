"""
Full Dataset Invariant Auditor across all 1,330 batch files (13,295 samples).
Milestone 1 Quality & Contract Verification.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, 'code')
from generate_whisper_noise_batches import compute_wer, extract_candidates

def run_full_audit():
    print("=" * 60)
    print("Running Full Dataset Invariant Audit across 1,330 Batches")
    print("=" * 60)

    dataset_path = "data/sft_train.json"
    with open(dataset_path) as f:
        orig_dataset = json.load(f)

    total_samples = len(orig_dataset)
    assert total_samples == 13295, f"Expected 13,295 samples, got {total_samples}"

    total_batches = 1330
    banned_words = [
        "minut", "automat", "releas", "terminat", "thinkin", "configur", "approv", "replacin"
    ]

    all_wers = []
    has_refined_count = 0
    banned_violations = []
    markdown_violations = []
    no_m1_violations = []
    long_pristine_violations = []
    missing_indices = set(range(13295))
    duplicate_indices = set()
    seen_indices = set()

    start_time = time.time()

    for b in range(total_batches):
        p = f"scratch/batch_{b}_output.json"
        if not os.path.exists(p):
            print(f"ERROR: Batch file missing: {p}")
            return False

        with open(p, "r", encoding="utf-8") as f:
            batch_data = json.load(f)

        expected_count = 5 if b == 1329 else 10
        if len(batch_data) != expected_count:
            print(f"ERROR: Batch {b} has {len(batch_data)} samples, expected {expected_count}")

        for item in batch_data:
            idx = item["index"]
            raw = item["raw_asr"]

            if idx in seen_indices:
                duplicate_indices.add(idx)
            seen_indices.add(idx)
            missing_indices.discard(idx)

            # Contract: NEVER output refined_text
            if "refined_text" in item:
                has_refined_count += 1

            ref = orig_dataset[idx]["refined_text"]
            wer = compute_wer(ref, raw)
            all_wers.append(wer)

            # Zero banned non-words
            for bad in banned_words:
                if re.search(r"\b" + bad + r"\b", raw, flags=re.IGNORECASE):
                    banned_violations.append((idx, bad))

            # Zero markdown
            if "`" in raw or "#" in raw or "\n\n" in raw:
                markdown_violations.append((idx, "markdown symbol"))
            if re.search(r"^\s*[-*]\s+", raw, flags=re.MULTILINE):
                markdown_violations.append((idx, "bullet marker"))

            # Multi-sentence: no long pristine sentences >= 15 words
            ref_sents = [s.strip() for s in re.split(r"[.!?]+", ref) if s.strip()]
            if len(ref_sents) >= 2:
                for rs in ref_sents:
                    words = rs.split()
                    if len(words) >= 15 and rs in raw:
                        long_pristine_violations.append((idx, rs))

    elapsed = time.time() - start_time
    print(f"Audit completed in {elapsed:.1f}s ({total_samples/max(0.1, elapsed):.1f} samples/s)\n")

    # Invariant checks
    print("--- INVARIANT VERIFICATION SUMMARY ---")
    print(f"1. Total samples covered: {len(seen_indices)}/13295 (missing: {len(missing_indices)}, duplicates: {len(duplicate_indices)})")
    assert len(seen_indices) == 13295, f"Missing {len(missing_indices)} indices!"
    assert len(duplicate_indices) == 0, f"Duplicate indices found: {duplicate_indices}"

    print(f"2. Output contract adherence: {has_refined_count} occurrences of refined_text in output")
    assert has_refined_count == 0, "Violated output contract: refined_text present!"

    print(f"3. Banned non-word violations: {len(banned_violations)}")
    assert len(banned_violations) == 0, f"Banned words detected: {banned_violations[:5]}"

    print(f"4. Markdown violations: {len(markdown_violations)}")
    assert len(markdown_violations) == 0, f"Markdown violations: {markdown_violations[:5]}"

    print(f"5. Long pristine sentence violations: {len(long_pristine_violations)}")
    assert len(long_pristine_violations) == 0, f"Long pristine sentences: {long_pristine_violations[:5]}"

    out_of_range = [w for w in all_wers if w < 0.080 or w > 0.450]
    print(f"6. WER acceptable window [8.0%, 45.0%]: {len(all_wers) - len(out_of_range)}/13295 ({((len(all_wers)-len(out_of_range))*100/len(all_wers)):.2f}%)")
    print(f"   Samples out of acceptable range: {len(out_of_range)}")
    assert len(out_of_range) == 0, f"Found {len(out_of_range)} samples out of range!"

    avg_wer = sum(all_wers) / len(all_wers)
    min_wer = min(all_wers)
    max_wer = max(all_wers)
    sweet_spot = sum(1 for w in all_wers if 0.150 <= w <= 0.280)
    print(f"7. Average WER: {avg_wer*100:.2f}% (Target Sweet Spot 15%-25%)")
    print(f"   Min WER: {min_wer*100:.2f}%, Max WER: {max_wer*100:.2f}%")
    print(f"   Sweet spot samples [15%-28%]: {sweet_spot}/13295 ({sweet_spot*100/len(all_wers):.2f}%)")

    print("\nALL INVARIANTS SATISFIED 100%! Ready for Coordinator Black-Box Validation Gate.")
    return True

if __name__ == "__main__":
    run_full_audit()
