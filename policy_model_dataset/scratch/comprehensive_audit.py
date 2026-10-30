import json
import re
from collections import Counter

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    train_samples = [json.loads(line) for line in f]

with open("sft_eval.json", "r", encoding="utf-8") as f:
    eval_samples = json.load(f)

print(f"Loaded {len(train_samples)} training samples, {len(eval_samples)} eval samples.")

# 1. Number / Port / Value Hallucination Audit
NUM_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
    "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
    "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "00", "thousand": "000"
}

def normalize_digits(text):
    t = text.lower()
    for w, d in NUM_WORDS.items():
        t = re.sub(r'\b' + w + r'\b', d, t)
    # squash separated digits like 8 0 8 0 -> 8080
    t_clean = re.sub(r'[^0-9a-z]', '', t)
    return t_clean

unmatched_number_samples = []
for idx, s in enumerate(train_samples):
    raw_norm = normalize_digits(s["raw_asr"])
    ref_nums = re.findall(r'\b\d+\b', s["refined_text"])
    missing_nums = []
    for n in ref_nums:
        if n not in raw_norm:
            missing_nums.append(n)
    if missing_nums:
        unmatched_number_samples.append((idx, missing_nums, s["raw_asr"], s["refined_text"]))

# 2. Boilerplate Introductory Preambles
# Often generators start with "To resolve...", "Follow these...", "Perform the following..."
BOILERPLATE_PATTERNS = [
    r"^to (?:safely|resolve|ensure|mitigate|troubleshoot|diagnose|harden|clear|maximize|provision|remediate)\b",
    r"follow these (?:steps|remediation steps|procedures|architectural requirements|implementation steps)\b",
    r"apply the following (?:dynamic routing|multi-account|configuration|checklist)\b",
    r"execute the following (?:node upgrade|bus recovery|procedure)\b"
]

boilerplate_samples = []
for idx, s in enumerate(train_samples):
    ref_lower = s["refined_text"].lower()
    raw_lower = s["raw_asr"].lower()
    for pat in BOILERPLATE_PATTERNS:
        if re.search(pat, ref_lower) and not re.search(pat, raw_lower):
            boilerplate_samples.append((idx, pat, s["raw_asr"], s["refined_text"]))
            break

# 3. Fabricated File Extensions / Paths (.yaml, .json, .cfg, .toml, /etc/..., /var/...)
unmatched_files = []
for idx, s in enumerate(train_samples):
    raw_clean = re.sub(r'[^a-z0-9]', '', s["raw_asr"].lower()).replace("dot", ".").replace("slash", "/")
    # find filenames or paths in refined_text
    files_in_ref = re.findall(r'[\w\./-]+\.(?:yaml|yml|json|toml|cfg|conf|sh|py|bin|hex|h|c|cpp)', s["refined_text"], re.IGNORECASE)
    missing_files = []
    for f in files_in_ref:
        f_clean = re.sub(r'[^a-z0-9]', '', f.lower())
        if f_clean not in raw_clean:
            missing_files.append(f)
    if missing_files:
        unmatched_files.append((idx, missing_files, s["raw_asr"], s["refined_text"]))

# 4. Content Word Coverage (Lexical Recall)
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

low_recall_samples = []
for idx, s in enumerate(train_samples):
    raw_tokens = set(re.findall(r'[a-z0-9]+', s["raw_asr"].lower()))
    ref_tokens = [w for w in re.findall(r'[a-z0-9]+', s["refined_text"].lower()) if w not in STOP_WORDS and len(w) > 2]
    if not ref_tokens:
        continue
    missing = [w for w in ref_tokens if w not in raw_tokens and w not in s["raw_asr"].lower().replace(" ", "")]
    recall_gap = len(missing) / len(ref_tokens)
    if recall_gap > 0.30:  # >30% words completely invented
        low_recall_samples.append((idx, recall_gap, missing, s["raw_asr"], s["refined_text"]))

print(f"--- Comprehensive Audit Metrics on {len(train_samples)} Samples ---")
print(f"1. Samples with Unspoken Numbers / Ports / Subnets: {len(unmatched_number_samples)} ({len(unmatched_number_samples)/len(train_samples)*100:.1f}%)")
print(f"2. Samples with AI Boilerplate Preambles: {len(boilerplate_samples)} ({len(boilerplate_samples)/len(train_samples)*100:.1f}%)")
print(f"3. Samples with Fabricated Filenames / Paths: {len(unmatched_files)} ({len(unmatched_files)/len(train_samples)*100:.1f}%)")
print(f"4. Samples with Low Lexical Recall (>30% new words): {len(low_recall_samples)} ({len(low_recall_samples)/len(train_samples)*100:.1f}%)")
