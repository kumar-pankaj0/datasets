# Evaluation Dataset Generation Prompt: Real-World Acoustic Noise and Refinement

## System Role
You are an expert synthetic data generator creating a realistic, production-grade evaluation dataset for an ASR (Speech-to-Text) Refinement Policy Model.
The policy model converts broken, noisy acoustic speech transcripts (`raw_asr`) into clean, production-grade technical text (`refined_text`).

---

## 1. Refined Text Structure & Complexity Invariants
The refined text represents what the user intended to prompt or document. It must adhere strictly to length-dependent formatting rules:

### Simple Utterances (< 25 words)
- Exactly one direct, imperative sentence.
- Zero newlines (`\n`) and zero bullet or numbered lists.
- Inline backticks for exact CLI commands, flags, tools, registers, or parameters (e.g., `kubectl logs -f`).
- No divider lines (`---`) or conversational fillers.

### Medium Utterances (25 to 90 words)
- 1 to 3 grammatically complete sentences.
- Natural paragraph breaks (`\n\n`) connecting the problem statement, diagnostic action, or solution.
- Inline backticks for technical identifiers, config keys, error codes, and memory limits.
- No divider lines (`---`).

### Complex Utterances (90+ words)
- Begins with a high-level operational overview sentence.
- Structured into sequential numbered steps (`1.`, `2.`, `3.`) or thematic paragraphs (`\n\n`).
- Commands are fully specified with chained flags, pipes, or compound operations (e.g., `make clean && make -j$(nproc)`).
- Strict delimiter parity: even count of backticks, double quotes, and bold tags.

---

## 2. The 10 Real-World Acoustic Noise Patterns (for `raw_asr`)
Every `raw_asr` sample must sound like genuine, unedited spoken audio captured by an imperfect speech-to-text system. Every sample must exhibit combinations of the following 10 noise patterns:

1. **Spoken Symbols and Flags**:
   - The speaker utters code punctuation phonetically:
   - "dash dash", "dash", "equals", "slash", "backslash", "dot y a m l", "pipe grep", "ampersand ampersand", "semicolon".

2. **Phonetic Tool Mishearings**:
   - Technical tool names are broken into phonetic word pieces by general-purpose speech engines:
   - "cube cuddle" / "cube see tee ell" for `kubectl`
   - "dock er com pose" for `docker-compose`
   - "post gres" for `PostgreSQL`
   - "free are toss" for `FreeRTOS`
   - "open see vee" for `OpenCV`
   - "wi re shark" for `Wireshark`
   - "met a sploit" for `Metasploit`

3. **Cut-Off Words & Buffer Truncations**:
   - Low-power edge devices or mic cut-offs truncate word endings:
   - "terminat", "configur", "namesp", "produc", "allocat", "connecti", "delet", "serializ".

4. **Sound-Alike Words (Homophones)**:
   - Acoustic recognizer picks common phonetically identical words:
   - "knowed" for `node`, "buy" for `by`, "four" for `for`, "two" for `to`, "root" for `route`, "write" for `right`.

5. **Mid-Sentence Self-Corrections & Restarts**:
   - The user changes their mind or corrects themselves mid-sentence:
   - "run flash verify no wait erase flash first then flash sector zero"
   - "check packet drop rate um wait check socket buffer size instead".

6. **Spoken Numbers, Hex, and Versions**:
   - Numbers and versions are spoken out in full words:
   - "zero x seven f" for `0x7F`
   - "version two point four point one" for `2.4.1`
   - "exit code one three seven" for `137`
   - "sixteen gigabytes" for `16GB`.

7. **Heavy Spoken Fillers & Disfluencies**:
   - Thinking pauses and conversational disfluencies:
   - "um", "uh", "you know", "basically", "I mean", "like", "so um".

8. **Accents and Dropped Word Endings**:
   - Non-native speaker grammar slips and dropped plurals/tenses:
   - "deploy three container", "packet drop frequently", "we connect to serial bus yesterday".

9. **Acoustic Dropouts**:
   - Background fan noise or distance swallows short function words:
   - Missing prepositions ("in", "at", "to", "of") or dropped unstressed syllables.

10. **Flat Run-On Speech Streams**:
    - Spoken input is a continuous stream without periods, commas, capitalization, or formatting.
    - Flat lowercase text across 15 to 150 words.

---

## 3. Hard Non-Negotiable Invariants
- **Flat Raw ASR**: `raw_asr` must NEVER contain newline characters (`\n`) or markdown formatting markers (`- `, `1.`, ```).
- **Faithfulness**: Never invent parameters, commands, or values not implied by `raw_asr`. Never swap entities.
- **Clean Refined Text**: `refined_text` must contain ZERO pause fillers (`um`, `uh`, `basically`), zero divider dashes (`---`), and balanced delimiters.
- **Length Ratio**: The word count ratio of `refined_text` to `raw_asr` must stay within `[0.4, 1.3]`.

---

## 4. Output Schema
Each generated batch must be valid JSON:
```json
[
  {
    "raw_asr": "flat lowercase spoken text with acoustic errors and fillers",
    "refined_text": "Clean production-grade technical text following length-based formatting."
  }
]
```
