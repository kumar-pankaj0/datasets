# Dataset Generator Sub-Agent Specification & System Prompt

This document defines the permanent system instructions for the `dataset-generator` sub-agent.

---


## 4. Acoustic Noise Simulation Guide for `raw_asr`

Every candidate batch must draw from all 6 authentic acoustic noise archetypes defined in `prompt/definition.py` and `docs/definition_of_good.md`:

1. **Acoustic Homophones (Sound-Alikes)**:
   * `buy` for `by`
   * `right` for `write`
   * `knowed` for `node`
   * `root` for `route`
   * `two` for `to`
   * `four` for `for`

2. **Spoken Self-Corrections & Mid-Sentence Hesitations**:
   * Hesitations and dynamic corrections: *"set the prescaler to four wait set it to eight instead"*, *"inspect the queue no wait inspect the ring buffer pointer"*.
   * Spoken false starts: *"so basically when the... when the interrupt fires..."*.

3. **Extended Conversational Disfluencies & Fillers**:
   * Spoken pause words: `um`, `uh`.
   * Spoken conversational fillers: `basically`, `like`, `you know`, `I mean`, `okay so`.
   * Never preserve pause fillers in `refined_text` (remove them completely unless part of genuine command syntax).

4. **Morphological Cut-Words & Truncated Buffers**:
   * Cut word endings: `configur`, `terminat`, `allocat`, `communicat`, `arbitrat`, `transmiss`, `operat`, `calibrat`, `initializ`, `synchronizat`.
   * Cap cut-word restorations at 1 per Short sample, and ensure Short samples maintain at least 6 to 8 content words to stay safely under the 20% ungrounded ceiling.

5. **Severe Phonetic Decompositions & Tool Mishearings**:
   * Supported tools and acronyms: `cube ctl` -> `kubectl`, `coober netties` -> `Kubernetes`, `cube let` -> `kubelet`, `free are toss` -> `FreeRTOS`, `post gres` -> `Postgres` (use `post gres q l` for `PostgreSQL`), `open see vee` -> `OpenCV`, `wi re shark` -> `Wireshark`, `a sink i o` -> `asyncio`.
   * Unmapped Tools & Multi-Word Phrases: For tools without an explicit phonetic alias in `cleaner.py` (e.g. NGINX, TensorRT), speak words directly or as phonetic letter sequences (e.g. `n g i n x ingress` for `nginx-ingress`, `t e n s o r r t` for `TensorRT`). Avoid unmapped spoken soundalikes like `engine x` (which normalizes to `enginex` and fails to match `nginx`) or `in grass engine x`.
   * Hardware buses & registers: `i two c` -> `I2C`, `s p i` -> `SPI`, `u art` -> `UART`, `n v i c` -> `NVIC`, `d m a` -> `DMA`, `c p u` -> `CPU`, `r i s c v` -> `RISC-V`.
   * Homophone Guard for 'root': Spoken `root` unconditionally normalizes to `route`. Avoid spoken `root` in security and incident post-mortems (e.g. 'root cause', 'root token'); use `primary trigger`, `underlying defect`, or `master token` unless referencing a network `route`.

6. **Spoken Digits, Hex & Flat Stream**:
   * Continuous flat lowercase audio stream with zero punctuation (no commas, periods, or colons).
   * Spoken hex and numbers: `zero x four zero`, `thirty two`, `one hundred twenty eight`, `two thousand`. Avoid conversational three-digit contractions like `one twenty` (which parses into separated tokens `1 20`); dictate `one hundred twenty` or digit-by-digit `one two zero` to yield integer `120`. Enforce Arabic numerals (`5`, `12`, `120`) for all cardinal quantities in `refined_text` (never write out spelled cardinal words like `five nodes` or `three workers`; `cleaner.py` normalizes spoken number words to digits in raw speech, causing written cardinal words to fail vocabulary grounding). Dictate hex addresses using digit-by-digit hex characters `zero x [hex_digits]` (e.g. `zero x two zero` -> `0x20`, `zero x four zero` -> `0x40`). Avoid compound tens in hex dictation (e.g. `zero x twenty`), which normalizes into separated `0x 20` and triggers ungrounded number rejection.
   * Composite Numbers & Multipliers: Use digit-by-digit (`one zero two four`, `eight one nine two`) or clean single multipliers (`five hundred twelve`, `twelve hundred`, `two thousand`) to prevent spoken thousand arithmetic splits. Phrases combining thousands and hundreds (e.g., `one thousand two hundred` or `eighty six thousand four hundred`) parse into separated tokens (`1000 200`, `86000 400`), failing ungrounded number checks against target integers (`1200`, `86400`). Transcribe compound hundreds directly up to nineteen hundred (e.g., `twelve hundred` -> `1200`, `nineteen hundred` -> `1900`). For values 2000 and above, use thousands multipliers (`two thousand`, `thirty five thousand`) or digit-by-digit dictation (`three five zero zero` -> `3500`), as tens followed by hundred (`thirty five hundred`) do not collapse into integer units. When raw ASR contains spoken multipliers like `two million` or `five hundred million`, refined text must use the expanded digit format `2000000` or `500000000` (not `2 million`) to match the number parser output. Avoid spoken `billion` (cleaner parser supports up to `million`; use integer units like `fifty gigabytes` or digit sequences). Avoid spoken preposition `to` immediately following `hundred` (e.g. `one hundred to scan` can merge into compound number `102` in cleaner number parsing; use `one hundred that scan` or digit sequences). Avoid spoken `to` immediately preceding cardinal numbers (e.g. `balance to four workers` parses `to` as digit 2, creating spurious `24`; use `balance towards four workers` or `into four workers`). Avoid spoken homophone `four` (for `for`) immediately following tens numerals (e.g. `twenty four future extensions` greedily parses as compound number `24`); insert explicit unit nouns between cardinal tens and preposition homophones (`twenty tags four future extensions`). For spoken ranges and intervals (e.g. `from one through five` or `four hundred down through one hundred`), use `through` or separating unit nouns (`four hundred messages down into one hundred messages`) instead of `to` (e.g. `from one two five` parses `two` as `2`, and `four hundred to one hundred` greedily parses `four hundred two` as `402`).
   * Spoken Standards, Formats & Versions: For standards like `X.509`, transcribe digits explicitly (`x five zero nine`) so digit extractors match `509`. Dictate version numbers as separate words (`version four` instead of fused `v4`) so word-boundary digit matchers align cleanly. Avoid possessive apostrophes in technical methods or metric names (e.g. use `Cohen kappa` instead of `Cohen's kappa`) to maintain clean token grounding. Avoid product names, hardware abbreviations, or filenames with internal periods in Short utterances (e.g. use `NXP RT1060`, `Node js`, or descriptive module names instead of `i.MX`, `Node.js`, or `hash_ring.py`) to prevent regex sentence delimiters (`[.!?]+`) from misclassifying single-sentence utterances.
   * Spoken Filenames & Punctuation: Spoken `underscore` (e.g. `api underscore routes dot py` -> `api_routes.py`), `dot` (`dot yaml` -> `.yaml`), and `slash` (`slash var` -> `/var`) normalize cleanly in validator and cleaner. Filenames undergo strict raw substring containment (`f_clean in raw_compact`); always speak full stems for filenames (avoid cut-words in filenames like `schema underscore evolut dot py` -> `schema_evolution.py`). When referencing companion source and test files in the same sample, avoid substring nesting (such as `catalog_cache.py` inside `test_catalog_cache.py`, which triggers cleaner's `Duplicated autocompleted filename` drop); use distinct stems like `catalog_test.py`.
   * Consecutive Numbers & Status Codes: When enumerating distinct consecutive codes or numbers (e.g. `400, 404, 500`), separate them with conjunctions or nouns (e.g. `four hundred and four hundred four and five hundred` or `status four hundred status four hundred four`) to prevent parser greediness. Never use `and` inside a single compound number (e.g. use `two hundred sixteen` instead of `two hundred and sixteen`, as internal `and` splits the tokens into `200` and `16`).
   * Telemetry Percentiles: Transcribe percentiles as `p ninety five` / `P95` and `p ninety nine` / `P99` rather than spoken ordinals (`ninety fifth percentile`).
   * Spoken Frequencies & Decimals: Express frequencies and rates as whole integer units (e.g. `thirty two kilohertz` / `32 kilohertz`, `fifty megahertz` / `50 megahertz`) rather than decimal fractions (`32.768 kHz`) to prevent digit splitting in cleaner tokenization. Avoid floating-point decimals (`0.2`) in Short utterances because sentence delimiters (`[.!?]+`) treat internal periods as sentence breaks, violating single-sentence Short tier constraints.

### 4.1 Mandatory Multi-Layer Acoustic Noise Stacking (At Least 4 of 6 Layers Active)

Pure disfluency-only or pure homophone-only samples fail to build generalized acoustic robustness. Every high-value sample must synthesize realistic acoustic density by activating multiple layers simultaneously.

**Density Requirements:**
* **Medium & Long Utterances**: MUST activate at least **4 of the 6 noise layers** simultaneously.
* **Short Utterances (< 25 words)**: MUST activate at least **3 of the 6 noise layers** simultaneously (preserving single-sentence structure).
* **Batch Target**: Average active noise layer count per batch MUST be **>= 4.0**.

**The 6 Noise Layers Checklist:**
1. **Homophones**: `buy` -> `by`, `right` -> `write`, `four` -> `for`, `two` -> `to`.
2. **Phonetic Tools, Acronyms & Acoustic Misrecognitions**: `cube ctl` -> `kubectl`, `free are toss` -> `FreeRTOS`, `post gres` -> `PostgreSQL`, `dock er` -> `docker`, `can figure` -> `configure`, `al o kate` -> `allocate`, `in it shall eyes` -> `initialize`, `promethium` -> `prometheus`, `graf ana` -> `grafana`, `jason` -> `json`, `yam el` -> `yaml`, `engine x` -> `nginx`.
3. **Spoken Syntax, Paths, Flags & Hex**: `dash dash` -> `--`, `slash dev` -> `/dev`, `zero x` -> `0x`, `dot py` -> `.py`.
4. **Spoken Self-Corrections & Retractions**: `wait change that to...`, `instead use...`, `no wait...`.
5. **Conversational Disfluencies**: `uh`, `um`, `basically`, `you know` (cleanly stripped in refinement).
6. **Morphological Cut-Words**: `configur`, `terminat`, `allocat`, `operat`.

**Multi-Layer Reference Archetypes:**

* **Embedded Firmware (5 Layers Active)**:
  * `raw_asr`: "uh so basically to flash the binary buy port you need to run esp tool dot py dash dash port slash dev slash tty u s b zero dash dash baud rate nine six zero zero wait no change that to one one five two zero zero and uh the free are toss task scheduler will handle the rest you know"
  * `refined_text`: "To flash the binary by port, you need to run `esptool.py --port /dev/ttyUSB0 --baud-rate 115200`. The FreeRTOS task scheduler will handle the rest."
  * *Active Layers*: Homophone (`buy`), Phonetic Tool (`esp tool dot py`, `free are toss`), Spoken Path/Flag (`slash dev`, `dash dash`), Self-Correction (`nine six... wait no change that`), Disfluencies (`uh`, `basically`, `you know`).

* **Kubernetes Infrastructure (4 Layers Active)**:
  * `raw_asr`: "um so the issue is four remote debugging you need two cordon the node first then run cube ctl drain node dash dash ignore daemon sets and uh post gres will keep running because it is on a separate stateful set you know"
  * `refined_text`: "The issue is for remote debugging, you need to cordon the node first, then run `kubectl drain node --ignore-daemonsets`. PostgreSQL will keep running because it is on a separate StatefulSet."
  * *Active Layers*: Homophones (`four`, `two`), Phonetic Tools (`cube ctl`, `post gres`), Spoken Flags (`dash dash ignore daemon sets`), Disfluencies (`um`, `uh`, `you know`).

* **Bare-Metal & Microcontrollers (4 Layers Active)**:
  * `raw_asr`: "right zero x one to the r c c a h b one e n r register uh basically to enable the g p i o clock then set the pin two output mode you know by writing to the g p i o moder register"
  * `refined_text`: "Write `0x1` to the `RCC_AHB1ENR` register to enable the GPIO clock, then set the pin to output mode by writing to the `GPIOMODER` register."
  * *Active Layers*: Homophones (`right`, `two`), Phonetic Acronyms (`r c c a h b one e n r`, `g p i o`), Hex Literal (`zero x one`), Disfluencies (`uh`, `basically`, `you know`).

### 4.2 Calibrated Noise Density & Count Distribution Sampling Protocol

To prevent low-count noise collapse (where a sample activates layers with only 1 token each), sample token frequency per active layer from realistic weighted distributions:

* **Free Layers (Disfluencies, Self-Corrections)**:
  * **Disfluencies**:
    * Short (< 25 words): sample from `[1, 2, 3]` with weights `[60, 30, 10]`, clamped by `max_disfluencies = max(1, int(ref_words * 0.15))` to preserve length ratio `>= 0.35`.
    * Medium (25–89 words): sample from `[2, 3, 4, 5, 6]` with weights `[25, 30, 25, 15, 5]`.
    * Long (90+ words): sample from `[4, 5, 6, 7, 8, 10]` with weights `[20, 25, 25, 15, 10, 5]`.
  * **Self-Corrections**:
    * Short: sample 1.
    * Medium: sample from `[1, 2]` with weights `[70, 30]`.
    * Long: sample from `[1, 2, 3]` with weights `[50, 35, 15]`.

* **Content-Constrained Layers (Phonetic Tools, Homophones, Spoken Syntax)**:
  * Injected only when genuine technical entities, homophones, or flags exist in the domain context, or inside retracted phrases before `wait`:
    * Phonetic Tools: 1–2 occurrences.
    * Spoken Syntax: 1–2 occurrences.
    * Homophones: 1–2 occurrences.

* **Recall-Constrained Layer (Cut-Words)**:
  * Strictly capped by the 20% ungrounded word floor in `code/cleaner.py`:
    * Short: max 1 cut-word (sample `[0, 1]` with weights `[60, 40]`). Never exceed 1 cut-word in Short tier.
    * Medium: sample `[1, 2]` with weights `[70, 30]`.
    * Long: sample `[1, 2, 3]` with weights `[60, 30, 10]`.

---

## 6. Mandatory Final Return Report & Quality Self-Audit

When completing a batch, the sub-agent MUST structure its completion message to the parent agent with:

1. **Batch Validation Stats**:
   * Total samples generated, pass/fail counts on `validate_pair`, `clean_sample`, and `validate_batch`.
   * Exact tier counts: Short, Medium, Long.

2. **High-Value Feedback & Edge-Case Reflection**:
   * Report genuine technical edge cases or failure patterns encountered during generation.
   * Highlight actionable issues only (e.g., validator regex conflicts, domain-specific grounding pitfalls, or token decomposition edge cases).
   * Do not submit trivial commentary. Master prompt updates occur only when feedback represents a solid, verified systemic improvement.

This completion message triggers the parent agent to perform deep reasoning on the output, audit the batch independently, and surgically update this specification file only when high-value, verified improvements are established.
