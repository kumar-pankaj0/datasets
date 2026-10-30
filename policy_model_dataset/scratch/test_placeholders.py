import json
import re

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    samples = [json.loads(line) for line in f]

# Count how many samples have placeholder syntax like <...>, JSON snippets, or heavy paraphrase
placeholders = []
json_snippets = []
for idx, s in enumerate(samples):
    raw = s["raw_asr"].lower()
    ref = s["refined_text"]
    
    # Check angle bracket placeholders e.g. <attachment-id>
    brackets = re.findall(r'<[a-zA-Z0-9_-]+>', ref)
    if brackets and "<" not in raw:
        placeholders.append((idx, brackets, raw, ref))
        
    # Check JSON snippets e.g. {"spec": ...}
    if '{"' in ref and '{"' not in raw:
        json_snippets.append((idx, raw, ref))

print(f"Total samples: {len(samples)}")
print(f"Samples with invented angle-bracket placeholders (<...>): {len(placeholders)}")
print(f"Samples with invented JSON payloads: {len(json_snippets)}")

if placeholders:
    print("\nExample Placeholder:")
    print("  RAW:", placeholders[0][2][:120])
    print("  REF:", placeholders[0][3][:140])

if json_snippets:
    print("\nExample JSON Snippet:")
    print("  RAW:", json_snippets[0][1][:120])
    print("  REF:", json_snippets[0][2][:140])
