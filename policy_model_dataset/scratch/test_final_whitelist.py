import json
import re

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
    ("zero x", "0x"), ("a sink i o", "asyncio"), ("a sink", "async"),
]

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
        t = t.replace(p, r)
    tokens = set(re.findall(r'[a-z0-9]+', t))
    compact = re.sub(r'[^a-z0-9]', '', t)
    compact_digits = re.sub(r'[^0-9]', '', t)
    return t, compact, compact_digits, tokens

def clean_sample_final(raw: str, ref: str) -> tuple[dict | None, str]:
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

    # Check 1: Zero tolerance on numbers / ports / subnets
    ref_nums = re.findall(r'\b\d+\b', ref_clean)
    for n in ref_nums:
        if n not in raw_norm and n not in raw_compact and n not in raw_compact_digits:
            return None, f"Ungrounded number/port: {n}"

    # Check 2: Zero tolerance on filenames & path completion
    ref_files = FILE_PATTERN.findall(ref_clean)
    for f in ref_files:
        f_clean = re.sub(r'[^a-z0-9]', '', f.lower())
        if f_clean not in raw_compact:
            return None, f"Ungrounded filename: {f}"
        if ref_clean.lower().count(f.lower()) > 1 and raw_clean.lower().count(f.lower().replace(".", " dot ")) <= 1:
            return None, f"Duplicated autocompleted filename: {f}"

    # Check 3: Zero tolerance on CLI flags
    flags = CLI_FLAG_PATTERN.findall(ref_clean)
    for flag in flags:
        clean_flag = flag.lstrip("-").lower().replace("-", "")
        if clean_flag and clean_flag not in raw_compact and f"dash {clean_flag}" not in raw_clean.lower():
            return None, f"Ungrounded CLI flag: {flag}"

    # Check 4: Zero tolerance on injected purpose clauses
    for pat in PURPOSE_PATTERNS:
        match = re.search(pat, ref_clean, re.IGNORECASE)
        if match:
            matched_phrase = match.group(0).strip()
            sig_words = [w for w in re.findall(r'[a-zA-Z]+', matched_phrase) if len(w) > 3]
            in_raw = sum(1 for w in sig_words if w.lower() in raw_compact)
            if in_raw < len(sig_words) * 0.5:
                return None, f"Injected purpose clause: {matched_phrase}"

    # Check 5: 80% Content Word Recall Floor
    ref_content = [w for w in re.findall(r'[a-z0-9]+', ref_clean.lower()) if w not in STOP_WORDS]
    if ref_content:
        missing = [w for w in ref_content if w not in raw_tokens and w not in raw_compact]
        missing_ratio = len(missing) / len(ref_content)
        if missing_ratio > 0.20:
            return None, f"High ungrounded vocabulary ({missing_ratio*100:.1f}% new words): {missing[:3]}"

    return {"raw_asr": raw_clean, "refined_text": ref_clean}, "kept"

with open("combined_dataset.jsonl") as f:
    samples = [json.loads(line) for line in f]

kept = 0
dropped = 0
reasons = {}

for s in samples[:1000]:
    res, reason = clean_sample_final(s["raw_asr"], s["refined_text"])
    if res:
        kept += 1
    else:
        dropped += 1
        cat = reason.split(":")[0]
        reasons[cat] = reasons.get(cat, 0) + 1

print(f"Tested 1,000 samples: Kept={kept} ({kept/10:.1f}%), Dropped={dropped}")
for k, v in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {k}: {v}")
