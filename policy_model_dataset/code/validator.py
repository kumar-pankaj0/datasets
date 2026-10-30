import re

PAUSE_WORDS = {"um", "uh", "erm"}

PURPOSE_PATTERNS = [
    r"\s+to safely\b[^.]*",
    r"\s+to safely\b[^:]*",
    r"\s+to prevent\b[^.]*",
    r"\s+to avoid\b[^.]*",
    r"\s+to access the pod\b[^.]*",
    r"\s+to safely evict active workloads and block incoming scheduling requests\b[^.]*",
]

COMPOUND_NUMBERS = [
    (r"\btwenty\s+one\b", "21"), (r"\btwenty\s+two\b", "22"), (r"\btwenty\s+three\b", "23"),
    (r"\btwenty\s+four\b", "24"), (r"\btwenty\s+five\b", "25"), (r"\btwenty\s+six\b", "26"),
    (r"\btwenty\s+seven\b", "27"), (r"\btwenty\s+eight\b", "28"), (r"\btwenty\s+nine\b", "29"),
    (r"\bthirty\s+two\b", "32"), (r"\bthirty\s+one\b", "31"),
    (r"\bfifty\s+two\b", "52"), (r"\beighty\s+four\b", "84"),
    (r"\bten\b", "10"), (r"\beleven\b", "11"), (r"\btwelve\b", "12"),
    (r"\bthirteen\b", "13"), (r"\bfourteen\b", "14"), (r"\bfifteen\b", "15"),
    (r"\bsixteen\b", "16"), (r"\bseventeen\b", "17"), (r"\beighteen\b", "18"), (r"\bnineteen\b", "19"),
    (r"\btwenty\b", "20"), (r"\bthirty\b", "30"), (r"\bforty\b", "40"), (r"\bfifty\b", "50"),
    (r"\bsixty\b", "60"), (r"\bseventy\b", "70"), (r"\beighty\b", "80"), (r"\bninety\b", "90"),
    (r"\bzero\b", "0"), (r"\bone\b", "1"), (r"\btwo\b", "2"), (r"\bthree\b", "3"), (r"\bfour\b", "4"),
    (r"\bfive\b", "5"), (r"\bsix\b", "6"), (r"\bseven\b", "7"), (r"\beight\b", "8"), (r"\bnine\b", "9"),
]

PHONETIC_TERMS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", "/"), ("dot", "."),
    ("a sink i o", "asyncio"), ("a sink", "async"),
    ("dash", "-"), ("minus", "-"), ("negative", "-"), ("colon", ":"), ("equals", "="),
    ("underscore", "_"),
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

CLI_FLAG_PATTERN = re.compile(r'(?:^|\s)(--[a-zA-Z0-9_-]+|-[a-zA-Z])')

HOMOPHONES = [
    (r"\bright\b", "write"),
    (r"\bbuy\b", "by"),
    (r"\bknowed\b", "node"),
]

# Multi-Layer Noise Density Regex Definitions
HOMOPHONE_REGEX = re.compile(r"\b(buy|right|knowed|root|two|four)\b", re.IGNORECASE)
PHONETIC_TOOLS_REGEX = re.compile(
    r"\b(esp tool|cube ctl|cube see tee ell|cube cuddle|coober netties|cube let|cube adm|"
    r"post gres|free are toss|open see vee|open o c d|wi re shark|a sink i o|a sink|"
    r"i two c|s p i|u art|r p c|d m a|c p u|n v i c|r i s c v|"
    r"dock er|engine x|in grass engine x|et see dee|jason|yam el|promethium|graf ana|"
    r"eye pee tables|tensor radio tower|tensor flow|pai torch|"
    r"can figure|config year|al o kate|allo cate|in it shall eyes|cal i brate|"
    r"synk ro nize|dee du pli cate|ter min ate|mi grate|com mu ni cate|ar bi trate|re cal cu late)\b",
    re.IGNORECASE,
)
SPOKEN_SYNTAX_REGEX = re.compile(
    r"\b(zero x|dash dash|dash [a-z0-9]+|slash [a-z0-9]+|dot [a-z0-9]+|underscore)\b",
    re.IGNORECASE,
)
CORRECTION_REGEX = re.compile(
    r"\b(wait|instead|no wait|scratch that|change that|switch to)\b",
    re.IGNORECASE,
)
DISFLUENCY_REGEX = re.compile(
    r"\b(um|uh|basically|like|you know|so um|i mean|so basically)\b",
    re.IGNORECASE,
)
CUT_WORD_REGEX = re.compile(
    r"\b(configur|terminat|allocat|migrat|communicat|arbitrat|transmiss|operat|calibrat|initializ|synchronizat|deduplicat|recalculat)\b",
    re.IGNORECASE,
)


def count_active_noise_layers(raw_asr: str) -> dict[str, bool]:
    """
    Evaluates presence of 6 acoustic noise layers in raw_asr:
    1. homophones
    2. phonetic_tools_acronyms
    3. spoken_syntax_flags_hex
    4. self_corrections
    5. disfluencies
    6. cut_words
    """
    raw = str(raw_asr).lower()
    return {
        "homophones": bool(HOMOPHONE_REGEX.search(raw)),
        "phonetic_tools_acronyms": bool(PHONETIC_TOOLS_REGEX.search(raw)),
        "spoken_syntax_flags_hex": bool(SPOKEN_SYNTAX_REGEX.search(raw)),
        "self_corrections": bool(CORRECTION_REGEX.search(raw)),
        "disfluencies": bool(DISFLUENCY_REGEX.search(raw)),
        "cut_words": bool(CUT_WORD_REGEX.search(raw)),
    }


def get_noise_layer_count(raw_asr: str) -> int:
    """Return total number of distinct active noise layers (0 to 6)."""
    return sum(count_active_noise_layers(raw_asr).values())

def get_noise_layer_token_counts(raw_asr: str) -> dict[str, int]:
    """Return total occurrence counts for each of the 6 acoustic noise layers in raw_asr."""
    raw = str(raw_asr).lower()
    return {
        "homophones": len(HOMOPHONE_REGEX.findall(raw)),
        "phonetic_tools_acronyms": len(PHONETIC_TOOLS_REGEX.findall(raw)),
        "spoken_syntax_flags_hex": len(SPOKEN_SYNTAX_REGEX.findall(raw)),
        "self_corrections": len(CORRECTION_REGEX.findall(raw)),
        "disfluencies": len(DISFLUENCY_REGEX.findall(raw)),
        "cut_words": len(CUT_WORD_REGEX.findall(raw)),
    }

def get_noise_density_profile(raw_asr: str) -> dict:
    """Return both binary presence and occurrence count density profiles for raw_asr."""
    counts = get_noise_layer_token_counts(raw_asr)
    return {
        "active_layers": {k: v > 0 for k, v in counts.items()},
        "active_layer_count": sum(1 for v in counts.values() if v > 0),
        "token_counts": counts,
        "total_noise_tokens": sum(counts.values()),
    }

def normalize_raw(text: str) -> str:
    t = text.lower()
    for pat, rep in HOMOPHONES:
        t = re.sub(pat, rep, t)
    for phrase, rep in PHONETIC_TERMS:
        t = re.sub(rf"\b{re.escape(phrase)}\b", rep, t)
    for pat, rep in COMPOUND_NUMBERS:
        t = re.sub(pat, rep, t)
    return re.sub(r"[^a-z0-9]", "", t)

def is_flag_grounded(flag: str, raw_norm: str, raw_orig: str) -> bool:
    clean = flag.lstrip("-").lower().replace("-", "")
    if not clean:
        return True
    if clean in raw_norm:
        return True
    if f"dash {clean}" in raw_orig.lower() or f"dash dash {clean}" in raw_orig.lower():
        return True
    return False

def validate_pair(
    pair: dict, is_practical_domain: bool = False, min_noise_layers: int = 4
) -> tuple[bool, str]:
    """
    Validate a single (raw_asr, refined_text) pair against deterministic criteria.
    Returns (is_valid, reason).
    """
    raw = str(pair.get("raw_asr") or pair.get("input", "")).strip()
    out = str(pair.get("refined_text") or pair.get("output", "")).strip()

    if not raw or not out:
        return False, "Empty raw or refined text"

    # Check ASCII
    try:
        raw.encode("ascii")
        out.encode("ascii")
    except UnicodeEncodeError as e:
        return False, f"Non-ASCII character found: {e}"

    if "\\u" in raw or "\\u" in out:
        return False, "Found escaped unicode sequence"

    # Raw ASR checks: must be a continuous speech stream without newlines
    if "\n" in raw:
        return False, "Newline in raw_asr"
    if re.search(r"(^|\s)-\s", raw):
        return False, "Bullet dash in raw_asr"
    if re.search(r"(^|\s)\d+\.\s", raw):
        return False, "Numbered list marker in raw_asr"

    raw_words = raw.lower().split()
    out_words = out.lower().split()

    # Check spoken filler words in refined_text
    for w in out_words:
        cleaned_w = w.strip(".,!?\"':;")
        if cleaned_w in PAUSE_WORDS:
            return False, f"Spoken pause word '{cleaned_w}' in refined text"

    if "---" in out:
        return False, "Divider dashes '---' in refined text"

    # Delimiter balance
    if out.count("`") % 2 != 0:
        return False, f"Unbalanced backticks: {out.count('`')}"
    if out.count('"') % 2 != 0:
        return False, f"Unbalanced double quotes: {out.count('\"')}"
    if out.count("**") % 2 != 0:
        return False, f"Unbalanced bold tags: {out.count('**')}"

    # Artifacts
    if "\n\n\n" in out:
        return False, "Triple newline in refined text"
    if "...." in out:
        return False, "Repetitive dots '....' in refined text"
    if out.count("**") > 6:
        return False, f"Excessive bold tags: {out.count('**')}"

    # Newline rules
    if len(out_words) < 25 and "\n" in out:
        return False, "Newline in short text (< 25 words)"

    if len(out_words) >= 90 and "\n" not in out:
        return False, "Long text (>= 90 words) must contain natural paragraph breaks (\\n\\n)"

    # Each markdown paragraph break (\n\n) consists of 2 newline characters
    max_breaks = max(1, len(out_words) // 25)
    if out.count("\n\n") > max_breaks:
        return False, f"Paragraph break count {out.count(chr(10)*2)} exceeds max budget {max_breaks}"

    # Length ratio heuristic
    ratio = len(out_words) / max(1, len(raw_words))
    if ratio < 0.35 or ratio > 1.25:
        return False, f"Word length ratio {ratio:.2f} outside [0.35, 1.25] (raw: {len(raw_words)}, out: {len(out_words)})"

    # Check ungrounded flags
    raw_norm = normalize_raw(raw)
    flags = CLI_FLAG_PATTERN.findall(out)
    for flag in flags:
        if not is_flag_grounded(flag, raw_norm, raw):
            return False, f"Ungrounded flag: {flag}"

    # Check ungrounded backtick code tokens
    code_tokens = re.findall(r'`([^`]+)`', out)
    raw_tokens = raw.lower().split()
    raw_soundexes = {soundex(t) for t in raw_tokens if len(t) >= 3}
    for ct in code_tokens:
        sub_tokens = re.split(r'[\s/=:\.\-_]', ct)
        for token in sub_tokens:
            token_clean = re.sub(r'[^a-z0-9]', '', token.lower())
            if len(token_clean) >= 4 and token_clean not in raw_norm:
                if soundex(token_clean) not in raw_soundexes:
                    return False, f"Ungrounded code token '{token}' in '{ct}'"

    # Practical domains backtick check
    if is_practical_domain and "`" in out:
        return False, "Backticks found in practical non-code domain"

    # Multi-layer acoustic noise density check if requested
    if min_noise_layers > 0:
        active_count = get_noise_layer_count(raw)
        # For short utterances (< 25 words), allow 1 less layer to preserve concise syntax
        target_min = max(1, min_noise_layers - 1) if len(out_words) < 25 else min_noise_layers
        if active_count < target_min:
            return (
                False,
                f"Active noise layers ({active_count}) below threshold ({target_min}) for {raw[:40]}...",
            )

    return True, "OK"


def validate_batch(
    batch: list[dict],
    min_short: int = 4,
    min_medium: int = 6,
    min_long: int = 10,
    min_noise_layers: int = 4,
) -> tuple[bool, str, dict]:
    """
    Validate a batch of pairs:
    1. Ensures every individual pair passes validate_pair().
    2. Enforces diversity across Short (<25), Medium (25-90), and Long (90+) tiers.
    3. Evaluates noise layer density distribution across the batch.
    """
    tier_counts = {"short": 0, "medium": 0, "long": 0}
    layer_counts = []
    token_counts = []
    for idx, pair in enumerate(batch):
        is_valid, reason = validate_pair(pair, min_noise_layers=min_noise_layers)
        if not is_valid:
            return False, f"Sample {idx+1} failed validation: {reason}", tier_counts

        raw_text = str(pair.get("raw_asr") or pair.get("input", ""))
        layer_counts.append(get_noise_layer_count(raw_text))
        token_counts.append(sum(get_noise_layer_token_counts(raw_text).values()))

        words = len(str(pair.get("refined_text", "")).split())
        if words < 25:
            tier_counts["short"] += 1
        elif words < 90:
            tier_counts["medium"] += 1
        else:
            tier_counts["long"] += 1

    tier_counts["avg_noise_layers"] = round(sum(layer_counts) / max(1, len(layer_counts)), 2)
    tier_counts["avg_noise_tokens"] = round(sum(token_counts) / max(1, len(token_counts)), 2)
    tier_counts["noise_layer_distribution"] = {
        f"{i}_layers": layer_counts.count(i) for i in range(7)
    }

    if tier_counts["short"] < min_short:
        return False, f"Batch missing short samples (<25 words): {tier_counts['short']} < {min_short}", tier_counts
    if tier_counts["medium"] < min_medium:
        return False, f"Batch missing medium samples (25-90 words): {tier_counts['medium']} < {min_medium}", tier_counts
    if tier_counts["long"] < min_long:
        return False, f"Batch missing long samples (90+ words): {tier_counts['long']} < {min_long}", tier_counts

    return True, "Batch diversity and quality verified", tier_counts
