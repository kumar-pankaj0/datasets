import json

batches = [99, 100, 101, 102, 103]
count = 0

with open("combined_dataset.jsonl", "a", encoding="utf-8") as out_f:
    for b_id in batches:
        fname = f"scratch/subagent_batch_{b_id}.json"
        with open(fname, "r", encoding="utf-8") as in_f:
            data = json.load(in_f)
            for item in data:
                out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
                count += 1

print(f"Successfully appended {count} samples from Wave 21 to combined_dataset.jsonl.")
