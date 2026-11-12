"""
Audit script to scan datasets for under-noised / weak samples.
Generates weak_samples_manifest.json to prioritize batch retrofitting.
"""

import json
import os
import sys
from typing import Dict, List

from gold_dataset_validator import validate_sample


def audit_dataset(filepath: str, output_manifest: str = "weak_samples_manifest.json") -> Dict:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    manifest: List[Dict] = []
    category_counts: Dict[str, int] = {}

    for idx, item in enumerate(data):
        raw = item.get("raw_asr", "")
        ref = item.get("refined_text", "")

        is_valid, reason, metrics = validate_sample(raw, ref)
        if not is_valid:
            cat = reason.split(":")[0].strip()
            category_counts[cat] = category_counts.get(cat, 0) + 1

            manifest.append({
                "index": idx,
                "reason": reason,
                "wer": metrics.get("wer", 0.0),
                "char_similarity": metrics.get("char_similarity", 0.0),
                "length_ratio": metrics.get("length_ratio", 0.0),
                "raw_asr": raw,
                "refined_text": ref,
            })

    # Sort manifest: pristine / under-noised first (highest similarity / lowest WER)
    manifest.sort(key=lambda x: (-x["char_similarity"], x["wer"]))

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    summary = {
        "dataset_path": filepath,
        "total_samples": len(data),
        "total_flagged": len(manifest),
        "clean_or_under_noised": sum(v for k, v in category_counts.items() if "Under-noised" in k),
        "other_violations": sum(v for k, v in category_counts.items() if "Under-noised" not in k),
        "manifest_path": output_manifest,
        "categories": category_counts,
    }

    return summary


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "sft_train.json"
    manifest_file = sys.argv[2] if len(sys.argv) > 2 else "weak_samples_manifest.json"
    result = audit_dataset(target, output_manifest=manifest_file)
    print(json.dumps(result, indent=2))
