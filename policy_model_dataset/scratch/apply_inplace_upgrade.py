import json
import os
import sys
sys.path.insert(0, 'code')
sys.path.insert(0, 'scratch')
import validator
import cleaner
from refined_retrofit import refined_retrofit

# 1. Load dataset
input_path = 'combined_dataset.jsonl'
with open(input_path, 'r', encoding='utf-8') as f:
    rows = [json.loads(line) for line in f]

total_rows = len(rows)
print(f'Initial total rows: {total_rows}')
assert total_rows == 7500, f'Expected 7500, got {total_rows}'

# 2. In-place upgrade of weak rows
upgraded_count = 0
for idx, r in enumerate(rows):
    ref = r['refined_text']
    raw = r['raw_asr']
    w = len(ref.split())
    min_l = 3 if w < 25 else 4
    if validator.get_noise_layer_count(raw) < min_l:
        new_raw = refined_retrofit(raw, ref)
        v_ok, v_err = validator.validate_pair({'raw_asr': new_raw, 'refined_text': ref}, min_noise_layers=4)
        c_res, c_err = cleaner.clean_sample(new_raw, ref)
        assert v_ok, f'Row {idx} validator failed: {v_err}'
        assert c_err == 'kept', f'Row {idx} cleaner failed: {c_err}'
        r['raw_asr'] = new_raw
        upgraded_count += 1

print(f'Successfully upgraded {upgraded_count} rows in-place.')

# 3. Write back to combined_dataset.jsonl
with open(input_path, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f'Successfully written 7,500 rows back to {input_path}.')

# 4. Full Dataset Deterministic Audit
val_failures = 0
cleaner_failures = 0
noise_distribution = {}
tier_distribution = {'short': 0, 'medium': 0, 'long': 0}
total_noise_layers = 0

for idx, r in enumerate(rows):
    raw = r['raw_asr']
    ref = r['refined_text']
    w = len(ref.split())
    if w < 25:
        tier_distribution['short'] += 1
    elif w < 90:
        tier_distribution['medium'] += 1
    else:
        tier_distribution['long'] += 1
        
    cnt = validator.get_noise_layer_count(raw)
    noise_distribution[cnt] = noise_distribution.get(cnt, 0) + 1
    total_noise_layers += cnt
    
    v_ok, v_err = validator.validate_pair(r, min_noise_layers=4)
    if not v_ok:
        val_failures += 1
        if val_failures <= 3:
            print(f'Audit val fail at {idx}: {v_err}')
            
    c_res, c_err = cleaner.clean_sample(raw, ref)
    if c_err != 'kept':
        cleaner_failures += 1
        if cleaner_failures <= 3:
            print(f'Audit cleaner fail at {idx}: {c_err}')

print('\n=== FULL 7,500 DATASET AUDIT RESULTS ===')
print(f'Total rows: {len(rows)}')
print(f'Validator failures (min_noise_layers=4): {val_failures}')
print(f'Cleaner failures: {cleaner_failures}')
print(f'Tier distribution: {tier_distribution}')
print(f'Noise layer distribution: {noise_distribution}')
avg_layers = total_noise_layers / len(rows)
print(f'Global Average Active Noise Layers: {avg_layers:.2f}')

# 5. Check SFT Eval Leakage
with open('sft_eval.json', 'r', encoding='utf-8') as f:
    eval_set = json.load(f)

eval_targets = {item['refined_text'].strip().lower() for item in eval_set}
leak_count = sum(1 for r in rows if r['refined_text'].strip().lower() in eval_targets)
print(f'Benchmark Leakage against sft_eval.json (358 targets): {leak_count} collisions')
assert leak_count == 0, f'Detected {leak_count} collisions against eval set!'
