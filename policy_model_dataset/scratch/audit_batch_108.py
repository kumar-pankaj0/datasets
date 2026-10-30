import json
import re

with open('scratch/subagent_batch_108.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

print(f'Batch length: {len(batch)}')

tiers = {'short': 0, 'medium': 0, 'long': 0}

for i, s in enumerate(batch):
    raw = s['raw_asr']
    ref = s['refined_text']
    w_count = len(ref.split())
    
    # ASCII check
    raw.encode('ascii')
    ref.encode('ascii')
    
    # No backticks
    assert '`' not in ref, f'Sample {i+1} has backticks!'
    
    # Tier classification
    if w_count < 25:
        tiers['short'] += 1
        assert '\n' not in ref, f'Sample {i+1} short has newline'
        # Sentence count
        sentences = [sent.strip() for sent in re.split(r'[.!?]+', ref) if sent.strip()]
        assert len(sentences) == 1, f'Sample {i+1} short has {len(sentences)} sentences'
        # Content words >= 6
        content_words = [w for w in re.findall(r'[a-zA-Z0-9]+', ref.lower()) if len(w) > 2]
        assert len(content_words) >= 6, f'Sample {i+1} short has too few content words: {len(content_words)}'
    elif w_count < 90:
        tiers['medium'] += 1
        sentences = [sent.strip() for sent in re.split(r'[.!?]+', ref) if sent.strip()]
        assert 1 <= len(sentences) <= 3, f'Sample {i+1} medium has {len(sentences)} sentences'
        assert '\n\n' in ref, f'Sample {i+1} medium missing paragraph break'
    else:
        tiers['long'] += 1
        assert '\n\n' in ref, f'Sample {i+1} long missing paragraph break'
        paragraphs = ref.split('\n\n')
        assert len(paragraphs) >= 2, f'Sample {i+1} long has fewer than 2 paragraphs'

print(f'Tier distribution: {tiers}')
assert tiers == {'short': 4, 'medium': 6, 'long': 10}, f'Unexpected tiers: {tiers}'
print('All detailed structural assertions passed!')
