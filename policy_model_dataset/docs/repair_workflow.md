**ASR Dataset Repair Workflow**

This guide covers the exact steps to repair weak samples in `data/sft_train.json`.
Repair means upgrading `raw_asr` with realistic Whisper acoustic noise while keeping `refined_text` 100% frozen.

---

**When to Use This Workflow**
- You ran `code/audit_weak_samples.py` and got a manifest of flagged samples.
- You want to fix under-noised, pristine, or over-corrupted pairs.
- You want to increase the gold-standard pass rate of the dataset.

---

**Step 1: Identify Weak Samples**

Run the audit script to generate a prioritized repair list:

```bash
cd /data/data/com.termux/files/home/project/fine_tuning/datasets/policy_model_dataset
python3 code/audit_weak_samples.py data/sft_train.json data/weak_samples_manifest.json
```

The manifest file sorts samples by priority:
- **Under-noised**: `raw_asr` is nearly identical to `refined_text` (WER < 8%).
- **Long pristine sentences**: Multi-sentence paragraphs where 1 or more sentences have zero noise.
- **Over-corrupted**: `raw_asr` is so broken that no human can recover the meaning (WER > 60%).

---

**Step 2: Process in Small Batches**

Pick 10 to 15 samples at a time from the manifest.
Small batches prevent the LLM from getting lazy or repetitive.

For each sample:
1. Read the `refined_text` carefully.
2. Read the current `raw_asr` and identify what is wrong (too clean, repetitive errors, or gibberish).

---

**Step 3: Apply the Mumble & Think Protocol**

Before editing any sample, think through these 4 steps:

- **Read Aloud Fast**: Mentally speak `refined_text` quickly, as if dictating into a cheap microphone in a noisy room.
- **Find Natural Weak Spots**: Which words blur together? Which technical terms would Whisper not know? Which unstressed syllables get swallowed?
- **Diversify Error Types**: Pick a different combination of the 6 acoustic mechanisms than the previous sample.
- **Recoverability Check**: Can a smart engineer reconstruct the exact `refined_text` from context and phonetics? If not, dial it back.

---

**Step 4: Apply the 6 Acoustic Mechanisms**

Rotate across these mechanisms so no two samples feel alike:

1. **Word Boundary Shifts**: Split or merge words at phonetic edges.
   - Example: "jacket" → "jack it", "gate open" → "gay token".

2. **Domain Jargon Substitution**: Technical terms misheard as everyday words with the same sound skeleton.
   - Example: "statevector" → "stay vector", "sidechained" → "siech in".

3. **Unstressed Syllable Erosion**: Fast speech clips weak syllables.
   - Example: "apply" → "play", "sedentary" → "seven terry".

4. **Spoken Punctuation & Flags**: Oral dictation of symbols without Markdown formatting.
   - Example: "detailed-exitcode" → "detailed exit coat".

5. **Clause & Sentence Boundary Drift**: Natural pauses merging or splitting clauses.
   - Example: Two short sentences merged with a comma, or one long sentence split mid-thought.

6. **Conversational Homophones**: Everyday phonetic slips.
   - Example: "due" → "do", "bin" → "been", "paid" → "paved".

---

**Step 5: Hard Rules (Never Break These)**

- **Never touch `refined_text`**: It is the frozen ground truth.
- **Never change factual numbers**: Do not swap `16` to `32`. Only alter how numbers sound when spoken.
- **Never drop whole sentences**: `raw_asr` must cover all content from `refined_text`.
- **Distribute noise across every sentence**: Long paragraphs must have errors in every sentence, not just the first one.
- **Keep existing good errors**: If a sentence already has creative Whisper noise, leave it alone.
- **No Markdown in `raw_asr`**: Zero backticks, zero bullet markers, zero `\n\n` paragraph breaks.
- **No keyboard typos**: Whisper never outputs `teh` or `configre`. It outputs real words that sound similar.

---

**Step 6: Validate Each Batch**

Run the gold validator on every repaired sample before saving:

```python
import sys
sys.path.insert(0, "code")
from gold_dataset_validator import validate_sample

raw = "your repaired raw_asr here"
ref = "the frozen refined_text here"

ok, msg, metrics = validate_sample(raw, ref)
print(ok, msg, metrics)
```

**What the validator checks:**
- WER between 8% and 45% (rejects pristine and gibberish samples).
- Character similarity between 55% and 98%.
- No Markdown backticks or bullet lists in `raw_asr`.
- No 15+ word verbatim sentence copied from `refined_text` in multi-sentence samples.

---

**Step 7: Save Repaired Samples**

After validation passes, update the pairs directly in `data/sft_train.json`.
Always verify the total sample count stays at 13,295.
Always verify that zero `refined_text` values changed.

Quick integrity check after patching:

```bash
python3 -c "
import json
with open('data/sft_train.json') as f:
    data = json.load(f)
print('Total samples:', len(data))
"
```

---

**Step 8: Re-Audit and Commit**

After repairing a batch, re-run the audit to update the manifest:

```bash
python3 code/audit_weak_samples.py data/sft_train.json data/weak_samples_manifest.json
```

Then commit and push:

```bash
git add data/sft_train.json data/weak_samples_manifest.json
git commit -m "repair(dataset): upgrade N weak samples with realistic Whisper acoustic noise"
git push origin main
```

---

**Target Quality Metrics**

- **Gold pass rate**: Target 95%+ of all 13,295 samples passing `gold_dataset_validator.py`.
- **WER range**: 10% to 35% per sample (the sweet spot for training signal).
- **Zero benchmark leakage**: 0 collisions against `data/sft_eval.json`.
- **Zero `refined_text` mutations**: Every ground-truth character stays identical.

---

**Reference Files**
- Master skill prompt: `.agents/skills/asr-data-curator/SKILL.md`
- Validation gate: `code/gold_dataset_validator.py`
- Audit scanner: `code/audit_weak_samples.py`
- Weak sample priority list: `data/weak_samples_manifest.json`
- Training dataset: `data/sft_train.json`
- Evaluation benchmark: `data/sft_eval.json`
