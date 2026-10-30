import json
import os
import sys

sys.path.insert(0, os.path.abspath("code"))
import validator

def index_weak_samples(dataset_path="combined_dataset.jsonl", out_path="scratch/weak_samples_index.json"):
    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f]

    weak_list = []
    for idx, s in enumerate(samples):
        raw = s.get("raw_asr") or s.get("input", "")
        ref = s.get("refined_text") or s.get("output", "")
        layers = validator.get_noise_layer_count(raw)
        words = len(ref.split())
        min_layers = 3 if words < 25 else 4
        
        tier = "short" if words < 25 else ("medium" if words < 90 else "long")
        
        if layers < min_layers:
            weak_list.append({
                "row_index": idx,
                "current_layers": layers,
                "required_layers": min_layers,
                "tier": tier,
                "word_count": words,
                "raw_asr": raw,
                "refined_text": ref
            })

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(weak_list, f, indent=2, ensure_ascii=False)

    print(f"Total dataset rows: {len(samples)}")
    print(f"Indexed weak samples: {len(weak_list)}")
    print(f"Index written to {out_path}")

if __name__ == "__main__":
    index_weak_samples()
