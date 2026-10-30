import json
from pathlib import Path

batches = [39, 40, 41, 42, 43]
dataset_path = Path("combined_dataset.jsonl")

with open(dataset_path, "r", encoding="utf-8") as f:
    before_count = sum(1 for _ in f)

appended_count = 0
with open(dataset_path, "a", encoding="utf-8") as out_f:
    for b_id in batches:
        b_file = Path(f"scratch/subagent_batch_{b_id}.json")
        with open(b_file, "r", encoding="utf-8") as in_f:
            pairs = json.load(in_f)
            for pair in pairs:
                out_f.write(json.dumps(pair, ensure_ascii=False) + "\n")
                appended_count += 1

with open(dataset_path, "r", encoding="utf-8") as f:
    after_count = sum(1 for _ in f)

print(f"Before: {before_count}")
print(f"Appended: {appended_count}")
print(f"After: {after_count}")
assert after_count == before_count + 100 == 4290
print("Successfully appended Wave 9 batches!")
