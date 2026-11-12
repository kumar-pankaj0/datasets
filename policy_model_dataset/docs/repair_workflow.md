**ASR Full Dataset Repair Workflow**

Rewrite `raw_asr` for every sample in `data/sft_train.json` using realistic Whisper acoustic noise.
`refined_text` stays 100% frozen. No agent ever outputs or modifies it.

---

**Strategy: Worker Pool Pattern**

```
samples = load("data/sft_train.json")       # all 13,295
batches = chunk(samples, 10)                 # ~1,330 batches

while batches OR active_agents:
    while active_agents < 10 and batches:
        batch = batches.pop()
        seed = pick_mechanism_bias(batch_id)  # forces variety
        spawn_agent(prompt, batch, seed)
    finished = wait_for_any()
    collect(finished.output)

patch_by_index("data/sft_train.json", all_results)
audit()
```

- **Batch size**: 10 samples per agent.
- **Max concurrent agents**: 10.
- **Rounds to finish**: ~133 rounds.

---

**Input / Output Contract**

Agent receives:
```json
[
  {"index": 4821, "refined_text": "Configure the circuit breaker..."},
  {"index": 4822, "refined_text": "Mount the local development..."}
]
```

Agent outputs **only index + raw_asr**:
```json
[
  {"index": 4821, "raw_asr": "configure the circuit breaker..."},
  {"index": 4822, "raw_asr": "mount the local develop mint..."}
]
```

- Agent reads `refined_text` to understand what to noisify.
- Agent never outputs `refined_text`. It is not the agent's field.
- Coordinator patches `sft_train.json` by matching index. `refined_text` never gets touched.

---

**Anti-Bias: Mechanism Rotation Seed**

All agents share the same skill prompt. Without variety, they develop the same noise "style" and the dataset feels uniform.

Each batch gets a rotation seed that tells the agent which 3 of the 6 mechanisms to favor:

- Batch 1: favor mechanisms 1, 3, 5
- Batch 2: favor mechanisms 2, 4, 6
- Batch 3: favor mechanisms 1, 2, 6
- ... rotate through all 20 possible 3-of-6 combinations

The agent still uses all 6 mechanisms. The seed just says "lean heavier on these 3 for this batch."

---

**What Each Agent Does**

1. Read the skill instructions from `.agents/skills/asr-data-curator/SKILL.md`.
2. Read the batch of 10 samples (index + refined_text).
3. Note the mechanism rotation seed for this batch.
4. For each sample:
   - Apply the Mumble & Think protocol.
   - Generate a new `raw_asr` using the 6 acoustic mechanisms, favoring the seeded 3.
   - Validate with `code/gold_dataset_validator.py`.
   - If validation fails, fix and re-validate.
5. Output JSON array: `[{"index": N, "raw_asr": "..."}]`
6. Write output to `scratch/batch_{batch_id}_output.json`

---

**Hard Rules (Never Break These)**

- **Never output `refined_text`**. Only output `index` and `raw_asr`.
- **Never change factual numbers**. Do not swap `16` to `32`.
- **Never drop whole sentences**. `raw_asr` must cover all content.
- **Distribute noise across every sentence**. Errors in every sentence, not just the first.
- **No Markdown in `raw_asr`**. Zero backticks, zero bullet markers, zero `\n\n`.
- **No keyboard typos**. Whisper outputs real words that sound similar, never `teh` or `configre`.
- **WER target**: 15%-25% per sample (acceptable: 8%-45%).

Do not copy examples from SKILL.md into your output. Use the Mumble & Think protocol to generate unique noise every time.

---

**Validation Gate**

Every sample must pass before saving:

```python
from gold_dataset_validator import validate_sample
ok, msg, metrics = validate_sample(raw_asr, refined_text)
```

Checks: WER 8%-45%, char similarity 55%-98%, no Markdown, no 15+ word verbatim sentences.
If a sample fails, fix it and re-validate. Do not skip.

---

**After All Batches Complete**

1. Collect all `scratch/batch_*_output.json` files.
2. Patch `data/sft_train.json` by index — replace only `raw_asr`.
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

- Skill prompt (with examples and mechanisms): `.agents/skills/asr-data-curator/SKILL.md`
- Validation gate: `code/gold_dataset_validator.py`
- Audit scanner: `code/audit_weak_samples.py`
- Training dataset: `data/sft_train.json`
- Evaluation benchmark: `data/sft_eval.json`
