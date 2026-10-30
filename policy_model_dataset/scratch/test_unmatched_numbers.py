import json
import re

with open("combined_dataset.jsonl", "r", encoding="utf-8") as f:
    samples = [json.loads(line) for line in f]

NUM_WORDS = [
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

def map_spoken_numbers(raw):
    t = raw.lower()
    for pat, digit in NUM_WORDS:
        t = re.sub(pat, digit, t)
    # also remove spaces between isolated digits like 1 3 7 -> 137
    t_no_space = re.sub(r'(\d)\s+(\d)', r'\1\2', t)
    t_no_space = re.sub(r'(\d)\s+(\d)', r'\1\2', t_no_space)
    return t, t_no_space

hallucinated_port_and_numbers = []

for idx, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    t_spaced, t_compact = map_spoken_numbers(raw)
    
    # find numbers in ref
    ref_numbers = re.findall(r'\b\d+\b', ref)
    unmatched = []
    for n in ref_numbers:
        if n not in t_spaced and n not in t_compact and n not in raw:
            unmatched.append(n)
            
    if unmatched:
        hallucinated_port_and_numbers.append((idx, unmatched, raw, ref))

print(f"Total surviving: {len(samples)}")
print(f"Samples with genuine ungrounded numbers/ports: {len(hallucinated_port_and_numbers)} ({len(hallucinated_port_and_numbers)/len(samples)*100:.1f}%)")

for i in range(min(5, len(hallucinated_port_and_numbers))):
    idx, unrec, raw, ref = hallucinated_port_and_numbers[i]
    print(f"\n[Ungrounded Number {i+1}] (idx {idx})")
    print(f"  Invented numbers/ports: {unrec}")
    print(f"  RAW: {raw}")
    print(f"  REF: {ref}")
