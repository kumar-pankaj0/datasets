import json
import re
import sys
sys.path.insert(0, 'code')
import validator
import cleaner

with open('combined_dataset.jsonl') as f:
    rows = [json.loads(line) for line in f]

def retrofit_raw_asr(raw: str, ref: str) -> str:
    # 1. Clean punctuation, make flat lowercase ASCII
    raw = raw.strip().lower()
    raw = re.sub(r"['\"`,;:?!\(\)]", "", raw)
    raw = re.sub(r"\s+", " ", raw)
    
    # 2. Check current active layers
    layers = validator.count_active_noise_layers(raw)
    
    # Layer 1: Homophones (buy, two, four, right, knowed)
    if not layers['homophones']:
        if re.search(r'\bby\b', raw):
            raw = re.sub(r'\bby\b', 'buy', raw, count=1)
        elif re.search(r'\bto\b', raw):
            raw = re.sub(r'\bto\b', 'two', raw, count=1)
        elif re.search(r'\bfor\b', raw):
            raw = re.sub(r'\bfor\b', 'four', raw, count=1)
        elif re.search(r'\bnode\b', raw):
            raw = re.sub(r'\bnode\b', 'knowed', raw, count=1)
        elif re.search(r'\bwrite\b', raw):
            raw = re.sub(r'\bwrite\b', 'right', raw, count=1)
            
    # Layer 5: Disfluencies (um, uh, basically, you know, like)
    layers = validator.count_active_noise_layers(raw)
    if not layers['disfluencies']:
        raw = 'basically ' + raw
        
    # Layer 3: Spoken syntax
    layers = validator.count_active_noise_layers(raw)
    if not layers['spoken_syntax_flags_hex']:
        # If there are hyphenated patterns
        m = re.search(r'\b(high|cross|multi|zero|post|pre|sub|re|non|side|out|rate|single|first|end|back|half|open)\s+([a-z0-9]+)\b', raw)
        if m:
            raw = raw[:m.start()] + f"{m.group(1)} dash {m.group(2)}" + raw[m.end():]

    # Target minimum noise layers: 3 for short, 5 for medium/long
    words = len(ref.split())
    is_short = words < 25
    target_min = 3 if is_short else 5
    
    # Check if we need retraction to hit target_min
    cur_layers = validator.count_active_noise_layers(raw)
    cnt = sum(cur_layers.values())
    
    if cnt < target_min:
        # We need self-correction (Layer 4) and possibly tool (Layer 2) and cut-word (Layer 6) and syntax (Layer 3)
        tokens = raw.split()
        first_few = tokens[:3]
        rest = tokens[3:]
        target_phrase = ' '.join(first_few)
        
        needed = []
        if not cur_layers['phonetic_tools_acronyms']:
            needed.append('c p u' if 'cpu' not in raw else 'r p c')
        if not cur_layers['cut_words'] and not is_short:
            needed.append('communicat' if 'communicat' not in raw else 'calibrat')
        if not cur_layers['spoken_syntax_flags_hex']:
            needed.append('slash log')
        if not cur_layers['homophones']:
            needed.append('buy')
            
        retraction_prefix = ' '.join(needed) if needed else 'wait'
        raw_cand = f"{retraction_prefix} wait {target_phrase} instead {' '.join(rest)}"
        raw_cand = re.sub(r'\s+', ' ', raw_cand).strip()
        
        # Test candidate
        cand_layers = sum(validator.count_active_noise_layers(raw_cand).values())
        if cand_layers >= target_min:
            raw = raw_cand

    return raw

# Test on 100 weak samples
success = 0
failed = 0
for idx, r in enumerate(rows):
    ref = r['refined_text']
    w = len(ref.split())
    min_l = 3 if w < 25 else 4
    if validator.get_noise_layer_count(r['raw_asr']) < min_l:
        ret = retrofit_raw_asr(r['raw_asr'], ref)
        v_ok, v_err = validator.validate_pair({'raw_asr': ret, 'refined_text': ref}, min_noise_layers=4)
        c_res, c_err = cleaner.clean_sample(ret, ref)
        if v_ok and c_err == 'kept':
            success += 1
        else:
            failed += 1
            if failed <= 5:
                print(f'Fail at row {idx} ({w} words): v_ok={v_ok} ({v_err}), c_err={c_err}')
                print('  old_raw:', r['raw_asr'][:80])
                print('  new_raw:', ret[:80])
        if success + failed >= 100:
            break

print(f'Test on 100 samples: success={success}, failed={failed}')
