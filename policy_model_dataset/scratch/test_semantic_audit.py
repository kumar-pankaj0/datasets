import json
import re

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    samples = [json.loads(line) for line in f]

# Stopwords
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

PHONETIC_REPLACEMENTS = [
    ("cube ctl", "kubectl"), ("cube see tee ell", "kubectl"), ("cube sea tea ell", "kubectl"),
    ("cube cuddle", "kubectl"), ("coober netties", "kubernetes"), ("cube let", "kubelet"),
    ("cube adm", "kubeadm"), ("post gres", "postgres"), ("free are toss", "freertos"),
    ("open see vee", "opencv"), ("wi re shark", "wireshark"), ("c group v two", "cgroupv2"),
    ("c group", "cgroup"), ("c n i", "cni"), ("slash", " "), ("dot", " "),
    ("dash", " "), ("minus", " "), ("negative", " "), ("colon", " "), ("equals", " "),
    ("zero", "0"), ("one", "1"), ("two", "2"), ("three", "3"), ("four", "4"),
    ("five", "5"), ("six", "6"), ("seven", "7"), ("eight", "8"), ("nine", "9"),
    ("twenty", "20"), ("thirty", "30"), ("forty", "40"), ("fifty", "50"),
    ("sixty", "60"), ("seventy", "70"), ("eighty", "80"), ("ninety", "90"),
]

def get_normalized_tokens(text):
    t = text.lower()
    for p, r in PHONETIC_REPLACEMENTS:
        t = t.replace(p, r)
    tokens = set(re.findall(r'[a-z0-9]+', t))
    return {tok for tok in tokens if tok not in STOP_WORDS and len(tok) > 2}

def audit_sample(raw, ref):
    raw_tokens = get_normalized_tokens(raw)
    ref_tokens = get_normalized_tokens(ref)

    if not ref_tokens:
        return True, 0, []

    # Check ungrounded content tokens
    raw_str = "".join(raw_tokens)
    ungrounded = []
    for t in ref_tokens:
        # Check if token exists in raw tokens or raw string substring
        if t not in raw_tokens and t not in raw_str:
            ungrounded.append(t)

    ungrounded_ratio = len(ungrounded) / len(ref_tokens)
    
    # Check numbers/subnets: extract all digits from ref
    ref_numbers = re.findall(r'\b\d+\b', ref)
    for n in ref_numbers:
        # Number must exist in raw (digits or words)
        if n not in raw and not all(d in raw_str for d in n):
            return False, ungrounded_ratio, [f"Ungrounded number/IP: {n}"]

    if ungrounded_ratio > 0.25: # More than 25% content tokens completely absent
        return False, ungrounded_ratio, ungrounded

    return True, ungrounded_ratio, []

failed_samples = []
for idx, s in enumerate(samples):
    ok, ratio, ungrounded = audit_sample(s["raw_asr"], s["refined_text"])
    if not ok:
        failed_samples.append((idx, ratio, ungrounded, s))

print(f"Total surviving: {len(samples)}")
print(f"Samples with severe content hallucination / ungrounded IPs/numbers: {len(failed_samples)} ({len(failed_samples)/len(samples)*100:.1f}%)")
print(f"Clean faithful samples remaining: {len(samples) - len(failed_samples)} ({(len(samples) - len(failed_samples))/len(samples)*100:.1f}%)")

print("\n--- Top 5 Embellished Samples Caught ---")
for i in range(min(5, len(failed_samples))):
    idx, ratio, ungrounded, s = failed_samples[i]
    print(f"\n[Embellished Sample {i+1}] (idx {idx}, ungrounded ratio: {ratio:.2f})")
    print(f"  Offending tokens: {ungrounded[:6]}")
    print(f"  RAW: {s['raw_asr'][:120]}...")
    print(f"  REF: {s['refined_text'][:130]}...")
