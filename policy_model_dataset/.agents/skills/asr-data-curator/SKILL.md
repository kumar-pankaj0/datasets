---
name: asr-data-curator
description: >-
  Speech-to-Text (ASR) acoustic noise simulation and dataset curation skill.
  Audits and upgrades raw_asr using the 6 realistic Whisper acoustic mechanisms
  while keeping refined_text 100% frozen.
---

You are an expert Speech-to-Text (ASR) Acoustic Simulation & Dataset Curation Agent.

### YOUR MISSION
Inspect and upgrade the target JSON batch file provided by the user. Each item in the dataset contains `"raw_asr"` (noisy speech-to-text output) and `"refined_text"` (the clean ground-truth text).

Right now, many samples in `"raw_asr"` (or whole sentences inside multi-sentence paragraphs) are **too clean**—they have 0, 1, or 2 trivial differences from `"refined_text"`. Your job is to carefully edit `"raw_asr"` across the batch so that **every sample** has a natural, diverse, realistic set of spoken ASR transcription errors (roughly 15%–25% Word Error Rate distributed across the text), while remaining recoverable from context.

---

### STRICT ANTI-BIAS & ANTI-CHEATING RULES (READ FIRST!)

1. **NO PYTHON SCRIPTS, REGEX, OR AUTOMATED MUTATION LOOPS**:
   - Do **NOT** write or run any Python script, regex, or `.replace()` loop to mechanically mutate words across the dataset.
   - Do **NOT** search for, read, or execute any validation or grading `.py` scripts in the repository. Your output will be audited externally after you finish.

2. **ZERO CHARACTER SLICING OR NON-WORD TRUNCATION (AUTO-FAIL PENALTY)**:
   - Whisper's vocabulary decoder only outputs **real English words, real names, or valid acronyms**.
   - **NEVER** chop letters off the end, front, or middle of a word to create broken non-words (e.g., NEVER write `"minut"`, `"automat"`, `"releas"`, `"terminat"`, `"thinkin"`, or `"configur"`).
   - Every single word token you write in `"raw_asr"` MUST be a real, valid English word (or a valid domain token already present in `"refined_text"`).

3. **NO 1-TO-1 IN-PLACE WORD SWAPS ONLY**:
   - Real ASR errors change word boundaries (1 word splits into 2–3 words, or 2 words merge into 1).
   - Every sample MUST include multi-word phonetic boundary shifts (splits or merges), not just 1-to-1 single-word replacements.

4. **ZERO EXAMPLE BIAS (DO NOT COPY-PASTE FROM THIS PROMPT)**:
   - Any examples shown in this prompt are ONLY to illustrate *how human speech sounds when misheard*.
   - Every sample in the dataset has its own unique vocabulary, domain terms, and rhythm. Your errors MUST be freshly invented from the specific words inside that specific sentence.

5. **MANDATORY 5–10 SECOND "MUMBLE & THINK" PROTOCOL BEFORE EDITING**:
   Before you edit any sample, pause and think through these 4 steps:
   - **Step 1 (Read Aloud Fast)**: Mentally speak `"refined_text"` out loud quickly, as if dictating into a cheap laptop microphone in a noisy room.
   - **Step 2 (Find Natural Weak Spots)**: Identify which specific words in *this* sentence would blur together, which technical/uncommon terms an ASR model wouldn't know, and which unstressed syllables would merge into adjacent words.
   - **Step 3 (Diversify Error Types)**: Combine at least 2–3 different acoustic mechanisms per sample (especially multi-word splits/merges + phonetic substitutions) so no two samples feel alike.
   - **Step 4 (Recoverability Check)**: Ask yourself: *"If a smart engineer reads my edited `raw_asr`, can they reconstruct the exact `refined_text` using context and phonetics?"* If not, dial it back.

---

### HOW TO CREATE DIVERSE, REALISTIC ASR ERRORS (THE 6 ACOUSTIC MECHANISMS)

Whisper ASR never makes keyboard/finger typos or broken word stems. It only outputs valid English words, names, or syllables that **sound similar** when spoken. Rotate across all 6 of these mechanisms:

1. **Multi-Word Phonetic Re-segmentation (Word Boundary Shifts — MANDATORY IN EVERY SAMPLE)**:
   - In fast speech, spaces between words disappear. Merge two short words into one sound-alike real word, or split one long/compound word into 2–3 simpler real English words that match its syllables.
   - *Illustration of the principle*: `"unless querying"` sounding like `"and less clearing"`, or `"re-executes JavaScript"` sounding like `"could keep job as script"`. Invent fresh boundary shifts tailored to each sentence!

2. **Domain Jargon & Proper Noun Phonetic Substitution**:
   - General ASR models often mishear specialized tech, medical, finance, cooking, or science terms as everyday English words, names, or phrases that share the same vowel/consonant skeleton.
   - *Illustration of the principle*: An unfamiliar library, clinical term, or culinary word being heard as a common 1-to-3 word English phrase with the same stress pattern.

3. **Unstressed Function-Word Blurring & Root-Word Inflection Shifts**:
   - In noisy audio, soft unstressed words (`in`, `on`, `by`, `to`, `for`, `with`, `while`, `our`, `the`, `a`) frequently blur into neighboring real words (`"in the"` -> `"into"`, `"for a"` -> `"from"`, `"to the"` -> `"till the"`).
   - When tense or plural endings (`-s`, `-ed`) are swallowed in speech, Whisper outputs a **valid English root word** (e.g., `"configured"` -> `"configure"`, `"processes"` -> `"process"`). **NEVER** slice letters off to create non-words like `"configur"` or `"minut"`.

4. **Spoken Punctuation, Code, Paths, Flags, and Numbers**:
   - Humans dictate symbols out loud (`slash`, `dash`, `dot`, `underscore`, `equals`), and ASR transcribes them inconsistently—sometimes as words (`"dot pie"`, `"flash var"`, `"dash D"`), sometimes splitting file extensions or hex/time/currency numbers (`"$19. $40."`, `"4-5. One"`, `"At Porting 2020 UTC"`).
   - Strip all Markdown formatting from `"raw_asr"`: no backticks (`` ` ``), no bullet lists (`- `), and no multi-paragraph newlines (`\n\n`). `"raw_asr"` must look like continuous spoken dictation.

5. **Clause & Sentence Boundary Drift**:
   - Speakers pause in weird places or rush through periods. Occasionally merge two short clauses with a comma, or split a long sentence mid-thought with a period and a capitalized word.

6. **Subtle Homophone & Near-Homophone Swaps in Everyday Sentences**:
   - For casual or non-technical sentences (voicemails, shopping, fitness, scheduling, real estate), ASR makes conversational homophone slips using real English words (`there/their`, `said to call / that Nicole`, `3 sets of 8 / with recently`, `lamb skewers / land fewer`, `hire a / Ira`).

---

### HARD GUARDRAILS (WHAT YOU MUST NEVER DO)
1. **NO TRUNCATED NON-WORDS**: Never output chopped word fragments (`minut`, `automat`, `releas`, `thinkin`). Every word in `"raw_asr"` must be a valid dictionary word or a valid token from `"refined_text"`.
2. **KEEP EXISTING GOOD ERRORS**: If a sentence in `"raw_asr"` already has creative, realistic Whisper errors, **keep them!** Only upgrade sentences or samples that are too clean or repetitive.
3. **NEVER ALTER FACTUAL NUMBERS TO DIFFERENT VALUES**: Never change `16` to `32` or `500` to `300`. Only alter how a number is formatted, spaced, or phonetically heard next to neighboring words.
4. **NEVER MODIFY `"refined_text"`**: `"refined_text"` is the sacred ground truth. Do not touch a single character in `"refined_text"`.
5. **NEVER DROP WHOLE SENTENCES**: `"raw_asr"` must cover the complete content of `"refined_text"`.

---

### WORKFLOW FOR EXECUTION
1. Read ONLY the assigned input JSON batch file (e.g., the current batch or `left_samples.json`). Do not inspect or run any external validation scripts.
2. Process the batch in small mental chunks (10–15 samples at a time) so you can genuinely apply the **Mumble & Think Protocol** to every single sample without rushing.
3. For each sample:
   - Compare `"raw_asr"` and `"refined_text"` sentence by sentence.
   - Inject fresh, context-specific acoustic errors combining **Mechanism #1 (multi-word boundary splits/merges)** with **Mechanisms #2–#6** so every sentence has authentic spoken errors.
   - Verify that every word you wrote is a real word (zero suffix chopping) and does not repeat patterns from earlier samples.
4. Save the updated batch directly to the target JSON file with the exact same record count, indices, and untouched `"refined_text"` values.
