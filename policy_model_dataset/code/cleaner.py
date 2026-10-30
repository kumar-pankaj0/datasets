import json
import re
import sys

HOMOPHONES = [
    (r"\bright\b", "write"),
    (r"\bbuy\b", "by"),
    (r"\bknowed\b", "node"),
    (r"\broot\b", "route"),
]

PHONETIC_TERMS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", " "), ("dot", " "),
    ("dash", "-"), ("minus", "-"), ("negative", "-"), ("colon", ":"), ("equals", "="),
    ("underscore", " "),
    ("zero x", "0x"), ("a sink i o", "asyncio"), ("a sink", "async"),
    ("can figure", "configure"), ("config year", "configure"),
    ("al o kate", "allocate"), ("allo cate", "allocate"),
    ("in it shall eyes", "initialize"), ("initial eyes", "initialize"),
    ("cal i brate", "calibrate"), ("callie brate", "calibrate"),
    ("synk ro nize", "synchronize"), ("sink ronize", "synchronize"),
    ("dee du pli cate", "deduplicate"), ("ter min ate", "terminate"),
    ("mi grate", "migrate"), ("com mu ni cate", "communicate"),
    ("ar bi trate", "arbitrate"), ("re cal cu late", "recalculate"),
    ("dock er", "docker"), ("jason", "json"), ("yam el", "yaml"),
    ("engine x", "nginx"), ("in grass engine x", "ingress-nginx"),
    ("et see dee", "etcd"), ("promethium", "prometheus"),
    ("graf ana", "grafana"), ("eye pee tables", "iptables"),
    ("tensor radio tower", "tensorrt"), ("tensor flow", "tensorflow"),
    ("pai torch", "pytorch"), ("see are dee", "crd"), ("h p a", "hpa"),
]

def soundex(name: str) -> str:
    """Return 4-character Soundex code for phonetic representation."""
    cleaned = re.sub(r'[^a-zA-Z]', '', name).upper()
    if not cleaned:
        return ''
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    first = cleaned[0]
    coded = [first]
    prev = mapping.get(first, '0')
    for char in cleaned[1:]:
        code = mapping.get(char, '0')
        if code != '0':
            if code != prev:
                coded.append(code)
            prev = code
        else:
            prev = '0'
    res = ''.join(coded)
    return (res + '000')[:4]

ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}

TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "s", "t", "can", "will", "just", "should", "now", "d", "ll", "m", "o", "re",
    "ve", "y", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "having", "do", "does", "did", "doing", "would", "could", "i", "you",
    "he", "she", "it", "we", "they", "them", "their", "this", "that", "these", "those"
}

PURPOSE_PATTERNS = [
    r"\s+to safely\b[^.]*",
    r"\s+to safely\b[^:]*",
    r"\s+to prevent\b[^.]*",
    r"\s+to avoid\b[^.]*",
    r"\s+to access the pod\b[^.]*",
    r"\s+to safely evict active workloads and block incoming scheduling requests\b[^.]*",
    r"\s+with sector erase\b[^.]*",
    r"\s+via the ST-LINK programmer\b[^.]*",
    r"\s+to ensure\b[^.]*",
    r"\s+in order to\b[^.]*",
]

CLI_FLAG_PATTERN = re.compile(r'(?:^|\s)(--[a-zA-Z0-9_-]+|-[a-zA-Z])')
FILE_PATTERN = re.compile(r'[\w\.-]+\.(?:yaml|yml|json|toml|cfg|conf|sh|py|bin|hex|h|c|cpp)', re.I)

def parse_spoken_numbers(text: str) -> str:
    tokens = text.lower().split()
    out = []
    i = 0
    while i < len(tokens):
        if (i + 3 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" 
            and tokens[i+2] in TENS and tokens[i+3] in ONES):
            val = ONES[tokens[i]] * 100 + TENS[tokens[i+2]] + ONES[tokens[i+3]]
            out.append(str(val))
            i += 4
        elif (i + 2 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" and tokens[i+2] in TENS):
            val = ONES[tokens[i]] * 100 + TENS[tokens[i+2]]
            out.append(str(val))
            i += 3
        elif (i + 2 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred" and tokens[i+2] in ONES):
            val = ONES[tokens[i]] * 100 + ONES[tokens[i+2]]
            out.append(str(val))
            i += 3
        elif (i + 1 < len(tokens) and tokens[i] in ONES and tokens[i+1] == "hundred"):
            val = ONES[tokens[i]] * 100
            out.append(str(val))
            i += 2
        elif (i + 1 < len(tokens) and tokens[i] in TENS and tokens[i+1] in ONES):
            val = TENS[tokens[i]] + ONES[tokens[i+1]]
            out.append(str(val))
            i += 2
        elif tokens[i] in TENS:
            out.append(str(TENS[tokens[i]]))
            i += 1
        elif tokens[i] in ONES:
            out.append(str(ONES[tokens[i]]))
            i += 1
        elif tokens[i] == "thousand":
            if out and out[-1].isdigit():
                out[-1] = str(int(out[-1]) * 1000)
            else:
                out.append("1000")
            i += 1
        elif tokens[i] == "million":
            if out and out[-1].isdigit():
                out[-1] = str(int(out[-1]) * 1000000)
            else:
                out.append("1000000")
            i += 1
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)

def normalize_raw(text: str) -> tuple[str, str, str, set[str]]:
    t = text.lower()
    t = parse_spoken_numbers(t)
    for pat, rep in HOMOPHONES:
        t = re.sub(pat, rep, t)
    for p, r in PHONETIC_TERMS:
        t = re.sub(rf"\b{re.escape(p)}\b", r, t)
    tokens = set(re.findall(r'[a-z0-9]+', t))
    compact = re.sub(r'[^a-z0-9]', '', t)
    compact_digits = re.sub(r'[^0-9]', '', t)
    return t, compact, compact_digits, tokens

def is_flag_grounded(flag: str, raw_clean: str, raw_compact: str) -> bool:
    clean_flag = flag.lstrip("-").lower().replace("-", "")
    if not clean_flag:
        return True
    raw_lower = raw_clean.lower()
    if len(clean_flag) == 1:
        return (
            f"dash {clean_flag}" in raw_lower or
            f"dash capital {clean_flag}" in raw_lower or
            f"minus {clean_flag}" in raw_lower or
            f"flag {clean_flag}" in raw_lower or
            f"-{clean_flag}" in raw_lower
        )
    return (
        clean_flag in raw_compact or
        f"dash {clean_flag}" in raw_lower or
        f"dash dash {clean_flag}" in raw_lower
    )

def clean_sample(raw: str, ref: str) -> tuple[dict | None, str]:
    raw_clean = raw.strip()
    ref_clean = ref.strip()

    if not raw_clean or not ref_clean:
        return None, "Empty text"
    if "\n" in raw_clean:
        return None, "Newline in raw ASR"

    # Invariant: length ratio
    raw_words = len(raw_clean.split())
    ref_words = len(ref_clean.split())
    ratio = ref_words / max(1, raw_words)
    if ratio < 0.35 or ratio > 1.25:
        return None, f"Extreme length ratio: {ratio:.2f}"

    raw_norm, raw_compact, raw_compact_digits, raw_tokens = normalize_raw(raw_clean)

    # 1. Zero tolerance on numbers / ports / subnets
    ref_clean_nums = re.sub(r'(\d),(\d)', r'\1\2', ref_clean)
    ref_nums = re.findall(r'\b\d+\b', ref_clean_nums)
    for n in ref_nums:
        if n not in raw_norm and n not in raw_compact and n not in raw_compact_digits:
            return None, f"Ungrounded number/port: {n}"

    # 2. Zero tolerance on filenames & path completion
    ref_files = FILE_PATTERN.findall(ref_clean)
    for f in ref_files:
        f_clean = re.sub(r'[^a-z0-9]', '', f.lower())
        if f_clean not in raw_compact:
            return None, f"Ungrounded filename: {f}"
        if ref_clean.lower().count(f.lower()) > 1 and raw_clean.lower().count(f.lower().replace(".", " dot ")) <= 1:
            return None, f"Duplicated autocompleted filename: {f}"

    # 3. Zero tolerance on CLI flags
    flags = CLI_FLAG_PATTERN.findall(ref_clean)
    for flag in flags:
        if not is_flag_grounded(flag, raw_clean, raw_compact):
            return None, f"Ungrounded CLI flag: {flag}"

    # 4. Zero tolerance on injected purpose clauses (zero text patching: drop completely)
    for pat in PURPOSE_PATTERNS:
        match = re.search(pat, ref_clean, re.IGNORECASE)
        if match:
            matched_phrase = match.group(0).strip()
            sig_words = [w for w in re.findall(r'[a-zA-Z]+', matched_phrase) if len(w) > 3]
            in_raw = sum(1 for w in sig_words if w.lower() in raw_compact)
            if in_raw < len(sig_words) * 0.5:
                return None, f"Injected purpose clause: {matched_phrase}"

    # 5. 80% Content Word Recall Floor (with phonetic Soundex grounding)
    ref_content = [w for w in re.findall(r'[a-z0-9]+', ref_clean.lower()) if w not in STOP_WORDS]
    if ref_content:
        raw_soundex = {soundex(tok) for tok in raw_tokens if len(tok) >= 3}
        missing = [
            w for w in ref_content
            if w not in raw_tokens and w not in raw_compact and (len(w) >= 3 and soundex(w) not in raw_soundex)
        ]
        missing_ratio = len(missing) / len(ref_content)
        if missing_ratio > 0.20:
            return None, f"High ungrounded vocabulary ({missing_ratio*100:.1f}% new words): {missing[:3]}"

    return {"raw_asr": raw_clean, "refined_text": ref_clean}, "kept"

def sanitize_jsonl(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f]

    cleaned_samples = []
    dropped_count = 0
    drop_reasons = {}

    for s in samples:
        raw = s.get("raw_asr") or s.get("input", "")
        ref = s.get("refined_text") or s.get("output", "")
        res, status = clean_sample(raw, ref)
        if res:
            cleaned_samples.append(res)
        else:
            dropped_count += 1
            cat = status.split(":")[0]
            drop_reasons[cat] = drop_reasons.get(cat, 0) + 1

    with open(output_file, "w", encoding="utf-8") as f:
        for s in cleaned_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    return len(samples), len(cleaned_samples), dropped_count, drop_reasons

def sanitize_json(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    cleaned_samples = []
    dropped_count = 0
    drop_reasons = {}

    for s in samples:
        raw = s.get("raw_asr") or s.get("input", "")
        ref = s.get("refined_text") or s.get("output", "")
        res, status = clean_sample(raw, ref)
        if res:
            cleaned_samples.append(res)
        else:
            dropped_count += 1
            cat = status.split(":")[0]
            drop_reasons[cat] = drop_reasons.get(cat, 0) + 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_samples, f, ensure_ascii=False, indent=2)

    return len(samples), len(cleaned_samples), dropped_count, drop_reasons

if __name__ == "__main__":
    train_in = sys.argv[1] if len(sys.argv) > 1 else "combined_dataset.jsonl"
    train_out = sys.argv[2] if len(sys.argv) > 2 else train_in
    eval_in = sys.argv[3] if len(sys.argv) > 3 else "sft_eval.json"
    eval_out = sys.argv[4] if len(sys.argv) > 4 else eval_in

    print(f"Sanitizing training dataset: {train_in} -> {train_out}...")
    t_tot, t_clean, t_drop, t_reasons = sanitize_jsonl(train_in, train_out)
    print(f"Training Data: {t_tot} total -> {t_clean} kept ({t_clean/t_tot*100:.1f}%), {t_drop} dropped")
    for r, c in sorted(t_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {r}: {c}")

    print(f"\nSanitizing evaluation dataset: {eval_in} -> {eval_out}...")
    e_tot, e_clean, e_drop, e_reasons = sanitize_json(eval_in, eval_out)
    print(f"Evaluation Data: {e_tot} total -> {e_clean} kept ({e_clean/e_tot*100:.1f}%), {e_drop} dropped")
    for r, c in sorted(e_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {r}: {c}")
