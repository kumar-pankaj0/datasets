**ASR Full Dataset Repair Workflow**

Rewrite `raw_asr` for every sample in `data/sft_train.json` using realistic Whisper acoustic noise.
`refined_text` stays 100% frozen. Every character stays identical.

---

**Strategy: Worker Pool Pattern**

Process all 13,295 samples. Not just weak ones — every single sample gets a fresh `raw_asr`.

```
samples = load("data/sft_train.json")       # all 13,295
batches = chunk(samples, 10)                 # ~1,330 batches

while batches OR active_agents:
    while active_agents < 10 and batches:
        spawn_agent(prompt, batches.pop())
    finished = wait_for_any()
    collect(finished.output)

save("data/sft_train.json", all_results)
audit()
```

- **Batch size**: 10 samples per agent.
- **Max concurrent agents**: 10 (100 samples in flight at once).
- **Rounds to finish**: ~133 rounds.

---

**What Each Agent Does**

Each spawned agent receives:
1. The skill instructions from `.agents/skills/asr-data-curator/SKILL.md`
2. A batch of 10 `{index, raw_asr, refined_text}` samples
3. These instructions:

For each sample in your batch:
- Read `refined_text` carefully. This is the frozen ground truth. Copy it exactly as-is.
- Generate a new `raw_asr` by applying the Mumble & Think protocol and the 6 acoustic mechanisms.
- Validate the result using `code/gold_dataset_validator.py`.
- If validation fails, fix and re-validate until it passes.
- Output a JSON array: `[{"index": N, "raw_asr": "new value", "refined_text": "exact copy"}]`
- Write output to `scratch/batch_{batch_id}_output.json`

---

**The 6 Acoustic Mechanisms (rotate across samples)**

1. **Word Boundary Shifts** — split or merge words at phonetic edges.
   "jacket" → "jack it", "gate open" → "gay token"

2. **Domain Jargon Substitution** — technical terms misheard as everyday words.
   "statevector" → "stay vector", "sidechained" → "siech in"

3. **Unstressed Syllable Erosion** — fast speech clips weak syllables.
   "apply" → "play", "sedentary" → "seven terry"

4. **Spoken Punctuation & Flags** — oral dictation of symbols, no Markdown.
   "detailed-exitcode" → "detailed exit coat"

5. **Clause & Sentence Boundary Drift** — natural pauses merge or split clauses.
   Two short sentences merged with a comma, or one long sentence split mid-thought.

6. **Conversational Homophones** — everyday phonetic slips.
   "due" → "do", "bin" → "been", "paid" → "paved"

---

**Hard Rules (Never Break These)**

- **Never touch `refined_text`**. It is the frozen ground truth.
- **Never change factual numbers**. Do not swap `16` to `32`.
- **Never drop whole sentences**. `raw_asr` must cover all content from `refined_text`.
- **Distribute noise across every sentence**. Long paragraphs must have errors in every sentence.
- **No Markdown in `raw_asr`**. Zero backticks, zero bullet markers, zero `\n\n` paragraph breaks.
- **No keyboard typos**. Whisper never outputs `teh` or `configre`. It outputs real words that sound similar.
- **WER target**: 15%-25% per sample (acceptable range: 8%-45%).

---

**Validation Gate**

Every repaired sample must pass `code/gold_dataset_validator.py` before saving.

```python
from gold_dataset_validator import validate_sample

ok, msg, metrics = validate_sample(raw_asr, refined_text)
```

Checks:
- WER between 8% and 45%.
- Character similarity between 55% and 98%.
- No Markdown in `raw_asr`.
- No 15+ word verbatim sentence in multi-sentence samples.

If a sample fails, fix it and re-validate. Do not skip.

---

**After All Batches Complete**

1. Collect all batch outputs.
2. Patch `data/sft_train.json` with new `raw_asr` values.
3. Verify total count is still 13,295.
4. Verify zero `refined_text` mutations.
5. Run full audit:

```bash
python3 code/audit_weak_samples.py data/sft_train.json data/weak_samples_manifest.json
```

6. Commit and push:

```bash
git add data/sft_train.json
git commit -m "repair(dataset): full rewrite of raw_asr with realistic Whisper acoustic noise"
git push origin main
```

---

**Target Quality**

- **Gold pass rate**: 95%+ of all 13,295 samples.
- **WER sweet spot**: 15%-25% per sample.
- **Zero benchmark leakage**: 0 collisions against `data/sft_eval.json`.
- **Zero `refined_text` mutations**: Every ground-truth character stays identical.

---

**Reference Files**

- Skill prompt: `.agents/skills/asr-data-curator/SKILL.md`
- Validation gate: `code/gold_dataset_validator.py`
- Audit scanner: `code/audit_weak_samples.py`
- Training dataset: `data/sft_train.json`
- Evaluation benchmark: `data/sft_eval.json`
