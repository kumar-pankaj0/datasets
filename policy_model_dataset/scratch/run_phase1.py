import json
import re
import sys
sys.path.insert(0, './code')
from cleaner import sanitize_jsonl, sanitize_json, clean_sample
from validator import validate_pair

print("==========================================")
print("PHASE 1: DETERMINISTIC PURGE & AUDIT")
print("==========================================")

# Step 1.2: Sanitize Training Dataset from fresh pre-purge backup
print("\n--- Task 1.2: Sanitizing combined_dataset.jsonl ---")
src_train = "archive/backups/combined_dataset.jsonl.bak"
dst_train = "combined_dataset.jsonl"
t_tot, t_clean, t_mod, t_drop, t_reasons = sanitize_jsonl(src_train, dst_train)
print(f"Training Data: {t_tot} total -> {t_clean} clean samples kept ({t_clean/t_tot*100:.1f}%), {t_mod} clauses stripped, {t_drop} dropped")

# Step 1.3: Sanitize Evaluation Dataset from fresh pre-purge backup
print("\n--- Task 1.3: Sanitizing sft_eval.json ---")
src_eval = "archive/backups/sft_eval.json.bak"
dst_eval = "sft_eval.json"
e_tot, e_clean, e_mod, e_drop, e_reasons = sanitize_json(src_eval, dst_eval)
print(f"Evaluation Data: {e_tot} total -> {e_clean} clean samples kept ({e_clean/e_tot*100:.1f}%), {e_mod} clauses stripped, {e_drop} dropped")

# Step 1.4: Train / Test Leakage & Contamination Check
print("\n--- Task 1.4: Train / Test Contamination & Leakage Audit ---")
with open(dst_eval, "r", encoding="utf-8") as f:
    eval_samples = json.load(f)

eval_raw_set = {s["raw_asr"].strip().lower() for s in eval_samples}
eval_ref_set = {s["refined_text"].strip().lower() for s in eval_samples}

with open(dst_train, "r", encoding="utf-8") as f:
    train_samples = [json.loads(line) for line in f]

non_leaked_train = []
leaked_count = 0

for s in train_samples:
    r = s["raw_asr"].strip().lower()
    o = s["refined_text"].strip().lower()
    if r in eval_raw_set or o in eval_ref_set:
        leaked_count += 1
    else:
        non_leaked_train.append(s)

if leaked_count > 0:
    print(f"WARNING: Found {leaked_count} leaked samples between train and test! Purging from training set...")
    with open(dst_train, "w", encoding="utf-8") as f:
        for s in non_leaked_train:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Purged {leaked_count} leaks. Clean training set size: {len(non_leaked_train)}")
else:
    print("Zero leakage detected between training and evaluation datasets!")

# Step 1.5: Measure Clean Baseline Metrics
print("\n--- Task 1.5: Measure and Record Clean Baseline Metrics ---")
with open(dst_train, "r", encoding="utf-8") as f:
    final_train = [json.loads(l) for l in f]

with open(dst_eval, "r", encoding="utf-8") as f:
    final_eval = json.load(f)

# Length breakdown
def get_tiers(dataset):
    tiers = {"short": 0, "medium": 0, "long": 0}
    for s in dataset:
        w = len(s["refined_text"].split())
        if w < 25:
            tiers["short"] += 1
        elif w <= 90:
            tiers["medium"] += 1
        else:
            tiers["long"] += 1
    return tiers

train_tiers = get_tiers(final_train)
eval_tiers = get_tiers(final_eval)

print(f"Final Clean Training Samples: {len(final_train)}")
print(f"  Short (<25w):  {train_tiers['short']} ({train_tiers['short']/len(final_train)*100:.1f}%)")
print(f"  Medium (25-90w): {train_tiers['medium']} ({train_tiers['medium']/len(final_train)*100:.1f}%)")
print(f"  Long (90+w):    {train_tiers['long']} ({train_tiers['long']/len(final_train)*100:.1f}%)")

print(f"\nFinal Clean Evaluation Samples: {len(final_eval)}")
print(f"  Short (<25w):  {eval_tiers['short']} ({eval_tiers['short']/len(final_eval)*100:.1f}%)")
print(f"  Medium (25-90w): {eval_tiers['medium']} ({eval_tiers['medium']/len(final_eval)*100:.1f}%)")
print(f"  Long (90+w):    {eval_tiers['long']} ({eval_tiers['long']/len(final_eval)*100:.1f}%)")

# Check embedded domain count in train
embedded_keywords = re.compile(r'\b(esptool|esp32|openocd|stm32|freertos|uart|gpio|i2c|spi|baudrate|jtag)\b', re.IGNORECASE)
embedded_count = sum(1 for s in final_train if embedded_keywords.search(s['refined_text']))
print(f"\nEmbedded / Firmware samples in clean train: {embedded_count} ({embedded_count/len(final_train)*100:.1f}%)")
