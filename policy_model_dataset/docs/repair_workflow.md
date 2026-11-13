**ASR Full Dataset Repair Workflow**

Rewrite `raw_asr` for every sample in `data/sft_train.json` using realistic Whisper acoustic noise.
`refined_text` stays 100% frozen. No worker agent ever outputs or modifies it.

---

**Strategy: Worker-Verifier Isolation Pool**

```python
samples = load("data/sft_train.json")  # all 13,295 (or left_samples.json on retry passes)
batches = chunk(samples, 10)          # ~1,330 batches

while batches or active_agents:
    while active_agents < 10 and batches:
        batch = batches.pop()
        seed = pick_mechanism_bias(batch_id)  # Mechanism 1 + 2 rotated from {2..6}
        spawn_agent(prompt, batch, seed)      # Worker NEVER sees or runs validator
    finished = wait_for_any()
    collect(finished.output)

# Coordinator-Only Black-Box Audit & Split
# Passed samples update sft_train.json; failed samples append to left_samples.json
run_validator(
    "scratch/all_batches.json",
    merge_passed="data/sft_train.json",
    split_failed="data/left_samples.json"
)
```

- **Batch size**: 10 samples per agent.
- **Max concurrent agents**: 10.
- **Rounds to finish**: ~133 rounds (plus targeted retry pass on `data/left_samples.json`).
- **Strict Isolation**: Worker agents never read, import, or execute `code/gold_dataset_validator.py`.

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
- Coordinator patches `sft_train.json` by matching index only for samples that pass validation. `refined_text` never gets touched.

---

**Anti-Bias: Mechanism Rotation Seed**

All agents share the same skill prompt. Without variety, they develop the same noise "style" and the dataset feels uniform.

Every batch **must** include **Mechanism 1 (Multi-Word Boundary Shifts)** so errors are never lazy 1-to-1 word swaps, plus a rotation seed of 2 additional mechanisms from `{2, 3, 4, 5, 6}`:

- Batch 1: Mechanism 1 + favor mechanisms 3, 5
- Batch 2: Mechanism 1 + favor mechanisms 2, 4
- Batch 3: Mechanism 1 + favor mechanisms 2, 6
- ... rotate through all 10 possible combinations of 1 + {two of 2..6}

---

**What Each Worker Agent Does**

1. Read the skill instructions from `.agents/skills/asr-data-curator/SKILL.md`.
2. Read the assigned batch of 10 samples (index + refined_text).
3. Note the mechanism rotation seed for this batch.
4. For each sample:
   - Apply the Mumble & Think protocol.
   - Generate a new `raw_asr` using real spoken English words, combining Mechanism 1 (multi-word splits/merges) with the seeded mechanisms.
   - Self-verify against the Hard Rules (zero suffix chopping, zero Markdown, real English words only, errors distributed across all sentences).
5. Output JSON array: `[{"index": N, "raw_asr": "..."}]`
6. Write output to `scratch/batch_{batch_id}_output.json`.

*(Note: Worker agents are strictly forbidden from reading or executing any `.py` validation scripts or writing Python mutation scripts.)*

---

**Hard Rules (Never Break These)**

- **Never output `refined_text`**. Only output `index` and `raw_asr`.
- **Zero character/suffix slicing (Real Words Only)**. Never chop letters off words to create non-words like `minut`, `automat`, `releas`, `terminat`, or `thinkin`. Every word in `raw_asr` must be a valid English word or a valid token already in `refined_text`.
- **Mandatory multi-word boundary shifts**. Do not only make 1-to-1 in-place word swaps; merge or split word boundaries naturally in every sample.
- **Never write Python scripts or regex loops to mutate text mechanically**.
- **Never change factual numbers**. Do not swap `16` to `32`.
- **Never drop whole sentences**. `raw_asr` must cover all content.
- **Distribute noise across every sentence**. Errors in every sentence, not just the first.
- **No Markdown in `raw_asr`**. Zero backticks, zero bullet markers, zero `\n\n`.
- **No keyboard typos**. Whisper outputs real words that sound similar, never `teh` or `configre`.
- **WER target**: 15%-25% per sample (acceptable: 8%-45%).

Do not copy examples from `SKILL.md` into your output. Use the Mumble & Think protocol to generate unique noise every time.

---

**Coordinator Validation & Retry Loop**

1. Collect all `scratch/batch_*_output.json` files.
2. Coordinator runs the Black-Box Validation Gate ([code/gold_dataset_validator.py](code/gold_dataset_validator.py)) against the ground-truth `refined_text`:

```bash
# Automated split: passing samples update sft_train.json; failed samples append to left_samples.json
python3 code/gold_dataset_validator.py scratch/batch_0_output.json --merge-passed data/sft_train.json --split-failed data/left_samples.json
```

3. **Retry Loop on `data/left_samples.json`**:
   - If `data/left_samples.json` is non-empty, chunk it into batches of 10 and re-run the worker pool on those remaining samples until all samples pass.
4. Verify total count in `data/sft_train.json` is still 13,295 and verify zero `refined_text` mutations.
5. Run full dataset audit:

```bash
python3 code/gold_dataset_validator.py data/sft_train.json
```

6. Commit and push:

```bash
git add data/sft_train.json
git commit -m "repair(dataset): full rewrite of raw_asr with realistic Whisper acoustic noise"
git push origin main
```

---

**Target Quality**

- **Gold pass rate**: 100% of all 13,295 samples.
- **WER sweet spot**: 15%-25% per sample.
- **Zero mechanical slicing**: 0 truncated non-words (`minut`, `automat`, etc.).
- **Zero benchmark leakage**: 0 collisions against `data/sft_eval.json`.
- **Zero `refined_text` mutations**: Every ground-truth character stays identical.

---

**Reference Files**

- **Skill prompt (worker-facing)**: `.agents/skills/asr-data-curator/SKILL.md`
- **Coordinator validation gate (coordinator-only)**: `code/gold_dataset_validator.py`
- **Training dataset**: `data/sft_train.json`
- **Retry queue**: `data/left_samples.json`
- **Evaluation benchmark**: `data/sft_eval.json`
