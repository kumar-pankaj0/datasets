import json
import re

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    samples = [json.loads(line) for line in f]

print(f"Total surviving samples: {len(samples)}")

# Stop words to ignore during token overlap check
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "in", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "s", "t", "can", "will", "just", "don", "should", "now", "d", "ll",
    "m", "o", "re", "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn",
    "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn",
    "wasn", "weren", "won", "wouldn", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "should", "could", "ought", "i", "you", "he", "she", "it", "we", "they", "them",
    "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "our", "ours", "ourselves", "your", "yours", "yourself",
    "yourselves", "him", "his", "himself", "her", "hers", "herself", "its", "itself"
}

def clean_words(text):
    return [w for w in re.findall(r'[a-zA-Z0-9]+', text.lower()) if w not in STOP_WORDS and len(w) > 2]

low_overlap_samples = []
hallucinated_numbers = []
suspicious_preambles = []

# Number mapping
WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "twenty": "20", "thirty": "30", "forty": "40",
    "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
    "hundred": "00", "thousand": "000"
}

for idx, s in enumerate(samples):
    raw = s["raw_asr"].lower()
    ref = s["refined_text"]

    # 1. Check content word recall (how many content words in ref are absent in raw)
    ref_words = clean_words(ref)
    raw_clean_str = re.sub(r'[^a-z0-9]', '', raw)
    
    missing_words = []
    for w in ref_words:
        # check if word is in raw string
        if w not in raw_clean_str:
            missing_words.append(w)
            
    missing_ratio = len(missing_words) / max(1, len(ref_words))
    if missing_ratio > 0.35: # More than 35% of content words never appeared in raw
        low_overlap_samples.append((idx, missing_ratio, missing_words, raw, ref))

    # 2. Check numbers in ref that have no representation in raw
    ref_nums = re.findall(r'\b\d+\b', ref)
    for num in ref_nums:
        # Check if digits exist in raw
        has_digit = False
        if num in raw:
            has_digit = True
        else:
            # Check individual digits
            all_digits_found = all(d in raw for d in num)
            if all_digits_found:
                has_digit = True
            # Check spoken words
            spoken_found = any(word in raw for word, digit in WORD_TO_DIGIT.items() if digit in num)
            if spoken_found:
                has_digit = True
        if not has_digit:
            hallucinated_numbers.append((idx, num, raw, ref))
            break

    # 3. Check suspicious preambles or instructional artifacts
    for phrase in ["please make sure", "it is recommended", "note that", "ensure you", "follow these steps to"]:
        if phrase in ref.lower() and phrase not in raw:
            suspicious_preambles.append((idx, phrase, raw, ref))
            break

print(f"\n1. Samples with high missing content word ratio (>35%): {len(low_overlap_samples)} ({len(low_overlap_samples)/len(samples)*100:.1f}%)")
print(f"2. Samples with ungrounded numbers: {len(hallucinated_numbers)} ({len(hallucinated_numbers)/len(samples)*100:.1f}%)")
print(f"3. Samples with conversational / instructional artifacts: {len(suspicious_preambles)} ({len(suspicious_preambles)/len(samples)*100:.1f}%)")

print("\n--- Examples of High Missing Content Words ---")
for i in range(min(5, len(low_overlap_samples))):
    idx, ratio, missing, raw, ref = low_overlap_samples[i]
    print(f"\n[Low Overlap {i+1}] (idx {idx}, missing ratio: {ratio:.2f})")
    print(f"  Missing: {missing[:8]}")
    print(f"  RAW: {raw[:120]}...")
    print(f"  REF: {ref[:140]}...")

print("\n--- Examples of Suspicious Preambles ---")
for i in range(min(3, len(suspicious_preambles))):
    idx, phrase, raw, ref = suspicious_preambles[i]
    print(f"\n[Preamble {i+1}] (idx {idx}, phrase: '{phrase}')")
    print(f"  RAW: {raw[:120]}...")
    print(f"  REF: {ref[:140]}...")
