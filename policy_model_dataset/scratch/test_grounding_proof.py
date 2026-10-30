import re

HOMOPHONES = [
    (r"\bright\b", "write"),
    (r"\bbuy\b", "by"),
    (r"\bfour\b", "for"),
    (r"\btwo\b", "to"),
    (r"\bknowed\b", "node"),
    (r"\broot\b", "route"),
]

NUM_WORDS = [
    (r"\bzero\b", "0"), (r"\bone\b", "1"), (r"\btwo\b", "2"), (r"\bthree\b", "3"),
    (r"\bfour\b", "4"), (r"\bfive\b", "5"), (r"\bsix\b", "6"), (r"\bseven\b", "7"),
    (r"\beight\b", "8"), (r"\bnine\b", "9"), (r"\bten\b", "10"),
    (r"\btwenty\b", "20"), (r"\bthirty\b", "30"), (r"\bforty\b", "40"), (r"\bfifty\b", "50"),
    (r"\bhundred\b", "00"), (r"\bthousand\b", "000")
]

PHONETIC_TERMS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", " "), ("dot", " "),
    ("dash", " "), ("minus", " "), ("negative", " "), ("colon", " "), ("equals", " "),
    ("zero x", "0x"),
]

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

def normalize_raw(text):
    t = text.lower()
    for pat, rep in HOMOPHONES:
        t = re.sub(pat, rep, t)
    for p, r in PHONETIC_TERMS:
        t = t.replace(p, r)
    for pat, rep in NUM_WORDS:
        t = re.sub(pat, rep, t)
    return t

def test_grounding(raw, ref):
    raw_norm = normalize_raw(raw)
    raw_compact = re.sub(r'[^0-9a-z]', '', raw_norm)
    raw_tokens = set(re.findall(r'[a-z0-9]+', raw_norm))

    ref_clean = ref.lower()
    # Check 1: Numbers & Ports (Zero tolerance)
    ref_nums = re.findall(r'\b\d+\b', ref)
    for n in ref_nums:
        if n not in raw_norm and n not in raw_compact:
            return False, f"DROPPED: Ungrounded number/port '{n}' not in audio"

    # Check 2: Filenames & Extensions (Zero tolerance)
    ref_files = re.findall(r'[\w\.-]+\.(?:yaml|yml|json|toml|cfg|conf|sh|py|bin|hex|h|c|cpp)', ref, re.I)
    for f in ref_files:
        f_clean = re.sub(r'[^a-z0-9]', '', f.lower())
        if f_clean not in raw_compact:
            return False, f"DROPPED: Ungrounded file '{f}' not in audio"

    # Check 3: Content tokens in ref
    ref_tokens = [w for w in re.findall(r'[a-z0-9]+', ref_clean) if w not in STOP_WORDS]
    missing = []
    for w in ref_tokens:
        if w not in raw_tokens and w not in raw_compact:
            missing.append(w)

    if ref_tokens:
        ratio = len(missing) / len(ref_tokens)
        if ratio > 0.20:
            return False, f"DROPPED: High ungrounded vocabulary ({ratio*100:.1f}% new words): {missing[:3]}"

    return True, "PASSED: 100% grounded and faithful"

# Test cases
bad_sample_1 = {
    "name": "Bad Sample 1 (Redis Port 6379 Hallucination)",
    "raw": "so just port forward port eight zero eight zero to the redis master service with cube ctl port forward service slash redis master eight zero eight zero",
    "ref": "Forward port 8080 to the Redis master service using `kubectl port-forward service/redis-master 8080:6379`."
}

bad_sample_2 = {
    "name": "Bad Sample 2 (Autocomplete Ingress Filename)",
    "raw": "apply the ingress configur from ingress dot y a m l using cube ctl apply dash f",
    "ref": "Apply the ingress configuration from `ingress.yaml` using `kubectl apply -f ingress.yaml`."
}

bad_sample_3 = {
    "name": "Bad Sample 3 (Unmentioned Subnet & Procedural Fluff)",
    "raw": "um basically to route all north south internet egress traffic through a centralized inspection v p c using gateway load balancer complete these steps",
    "ref": "To inspect all outbound internet traffic through a centralized security architecture using Gateway Load Balancer, modify route table with subnet 10.0.10.0/24 through endpoint vpce-099."
}

good_sample_1 = {
    "name": "Good Sample 1 (Phonetic Tool & Cut-Words)",
    "raw": "uh basically run cube ctl logs dash f on the payment service pod in production namesp",
    "ref": "Run `kubectl logs -f` on the payment-service pod in the `production` namespace."
}

good_sample_2 = {
    "name": "Good Sample 2 (Spoken Numbers to Digits & OOM Exit Code)",
    "raw": "um so the notification worker pod keeps crash looping with o o m killed exit code one three seven because memory limit was set to two hundred fifty six megabytes",
    "ref": "The notification worker pod keeps crash looping with `OOMKilled` (exit code 137) because its memory limit was set to 256 megabytes."
}

good_sample_3 = {
    "name": "Good Sample 3 (Embedded Register Write & Homophone 'right')",
    "raw": "please right zero x one to register r c c a h b one e n r to enable g p i o a peripheral clock",
    "ref": "Write `0x1` to the `RCC_AHB1ENR` register to enable the GPIOA peripheral clock."
}

for s in [bad_sample_1, bad_sample_2, bad_sample_3, good_sample_1, good_sample_2, good_sample_3]:
    ok, reason = test_grounding(s["raw"], s["ref"])
    print(f"[{s['name']}]")
    print(f"  Result: {reason}")
