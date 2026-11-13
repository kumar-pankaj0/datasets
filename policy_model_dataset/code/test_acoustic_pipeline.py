"""
Validation & Verification Test for Acoustic Noise Generation Pipeline.
Tests 100 samples across batches 0-9 for all constraints:
1. Mechanism 1 boundary shifts in every sample.
2. Real English words only (zero suffix chopping / banned words).
3. WER between 8% and 45% (average 15%-25%).
4. Zero Markdown (no backticks, bullets, headers, \n\n).
5. All sentences in multi-sentence samples have acoustic noise.
6. Number preservation.
"""

import json
import re
import sys
from typing import Dict, List, Set, Tuple

# Levenshtein WER implementation
def word_error_rate(reference: str, hypothesis: str) -> float:
    # Normalize: lowercase, remove punctuation for standard WER comparison
    ref_norm = re.sub(r"[^\w\s]", " ", reference.lower()).split()
    hyp_norm = re.sub(r"[^\w\s]", " ", hypothesis.lower()).split()
    if not ref_norm:
        return 0.0 if not hyp_norm else 1.0
    d = [[0] * (len(hyp_norm) + 1) for _ in range(len(ref_norm) + 1)]
    for i in range(len(ref_norm) + 1):
        d[i][0] = i
    for j in range(len(hyp_norm) + 1):
        d[0][j] = j
    for i in range(1, len(ref_norm) + 1):
        for j in range(1, len(hyp_norm) + 1):
            if ref_norm[i - 1] == hyp_norm[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 1)
    return d[len(ref_norm)][len(hyp_norm)] / len(ref_norm)

BANNED_WORDS = {
    "minut", "automat", "releas", "terminat", "thinkin", "configur", "approv", "replacin",
    "stallin", "rollin", "addin", "improvin", "durin", "regardin", "processin", "runnin",
    "checkin", "routin", "testin", "streamin", "trackin", "trainin", "monitorin", "blockin"
}

print("Loaded test harness.")
