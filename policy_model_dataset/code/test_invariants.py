import json
import re

with open('data/sft_train.json') as f:
    orig = json.load(f)

# Import extract_candidates
import sys
sys.path.insert(0, 'code')
from generate_whisper_noise_batches import extract_candidates

no_m1 = 0
for b in range(10):
    with open(f'scratch/batch_{b}_output.json') as f:
        data = json.load(f)
    for item in data:
        idx = item['index']
        raw = item['raw_asr']
        ref = orig[idx]['refined_text']

        # Check if Mechanism 1 replacement was applied
        # In raw vs ref, check if any Mechanism 1 candidate replacement appears in raw
        cands = extract_candidates(ref)
        m1_cands = [c for c in cands if c.mechanism_id == 1]
        m1_applied = any(c.replacement in raw for c in m1_cands)
        if not m1_applied:
            no_m1 += 1
            print(f'Sample {idx} no m1 applied! Ref: {ref[:60]}... Raw: {raw[:60]}...')

print(f'Samples without Mechanism 1: {no_m1}/100')
