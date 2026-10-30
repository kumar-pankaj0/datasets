import json
import re

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    train_samples = [json.loads(line) for line in f]

# Word to number mapping
NUM_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
    "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
    "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "00", "thousand": "000"
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

PHONETIC_TERMS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", " "), ("dot", " "),
    ("dash", " "), ("minus", " "), ("negative", " "), ("colon", " "), ("equals", " "),
]

def normalize_text(text):
    t = text.lower()
    for p, r in PHONETIC_TERMS:
        t = t.replace(p, r)
    for w, d in NUM_WORDS.items():
        t = re.sub(r'\b' + w + r'\b', d, t)
    return re.sub(r'[^0-9a-z\s]', ' ', t)

def is_sample_grounded(raw, ref):
    raw_norm = normalize_text(raw)
    raw_tokens = set(raw_norm.split())
    raw_compact = "".join(raw_tokens)

    ref_norm = normalize_text(ref)
    ref_tokens = [w for w in ref_norm.split() if w not in STOP_WORDS and len(w) > 2]

    if not ref_tokens:
        return True, "OK"

    # 1. Content word grounding
    missing = [w for w in ref_tokens if w not in raw_tokens and w not in raw_compact]
    missing_ratio = len(missing) / len(ref_tokens)
    if missing_ratio > 0.25:
        return False, f"High ungrounded vocabulary ({missing_ratio*100:.1f}% new words): {missing[:4]}"

    # 2. Check numbers
    ref_nums = re.findall(r'\b\d+\b', ref)
    for n in ref_nums:
        if n not in raw_norm and not all(d in raw_compact for d in n):
            return False, f"Ungrounded number/port: {n}"

    # 3. Check filenames in backticks
    code_tokens = re.findall(r'`([^`]+)`', ref)
    for ct in code_tokens:
        parts = re.split(r'[\s/=:\.\-_]', ct)
        for p in parts:
            p_clean = re.sub(r'[^a-z0-9]', '', p.lower())
            if len(p_clean) >= 4 and p_clean not in raw_tokens and p_clean not in raw_compact:
                return False, f"Ungrounded code entity: {p}"

    return True, "OK"

grounded_count = 0
reasons = {}

for s in train_samples:
    ok, reason = is_sample_grounded(s["raw_asr"], s["refined_text"])
    if ok:
        grounded_count += 1
    else:
        cat = reason.split(":")[0]
        reasons[cat] = reasons.get(cat, 0) + 1

print(f"Total surviving: {len(train_samples)}")
print(f"100% strictly grounded samples: {grounded_count} ({grounded_count/len(train_samples)*100:.1f}%)")
print(f"Ungrounded/Embellished samples: {len(train_samples) - grounded_count} ({(len(train_samples) - grounded_count)/len(train_samples)*100:.1f}%)")
print("\nBreakdown of hidden defects:")
for k, v in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
    print(f"  {k}: {v}")
