import json
import math
import sys

with open('data_full.json', 'r') as f:
    data = json.load(f)

metrics = ['faithfulness', 'noise_removed', 'errors_fixed', 'formatting']
scores = {m: [] for m in metrics}

print("=== 1. SCHEMA INTEGRITY CHECK ===")
valid_scores = {1, 3, 5, 7, 9}
for i, item in enumerate(data):
    # Schema assertions
    assert 'input' in item, f"Missing 'input' at index {i}"
    assert 'raw_asr' in item['input'], f"Missing 'raw_asr' at index {i}"
    assert 'refined_text' in item['input'], f"Missing 'refined_text' at index {i}"
    
    # Handle both old and new schema keys
    out_key = 'output' if 'output' in item else 'expected_output'
    assert out_key in item, f"Missing output at index {i}"
    
    for m in metrics:
        val = item[out_key].get(m)
        assert val in valid_scores, f"Invalid score {val} for {m} at index {i}"
        scores[m].append(val)

n = len(data)
print(f"Passed: All {n} samples have perfect JSON schema and valid scores (1,3,5,7,9).\n")

print(f"=== 2. DATASET SIGNAL AUDIT (data_full.json) ===\n")

# Math helpers
def calc_mean(arr):
    return sum(arr) / n

def calc_var(arr, mean):
    return sum((x - mean)**2 for x in arr) / n

def calc_entropy(arr):
    counts = {s: arr.count(s) for s in [1, 3, 5, 7, 9]}
    probs = [count / n for count in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def calc_cov(arr_x, mean_x, arr_y, mean_y):
    return sum((arr_x[i] - mean_x) * (arr_y[i] - mean_y) for i in range(n)) / n

means = {m: calc_mean(scores[m]) for m in metrics}
vars_dict = {m: calc_var(scores[m], means[m]) for m in metrics}

# Variance and Entropy
print(f"{'Metric':<15} | {'Variance (Spread)':<18} | {'Entropy (Bits)':<15}")
print("-" * 55)
for m in metrics:
    var = vars_dict[m]
    ent = calc_entropy(scores[m])
    print(f"{m:<15} | {var:<18.4f} | {ent:<15.4f}")

# Pearson Correlation
print("\n=== 3. PEARSON CORRELATION MATRIX (|r| should be approx 0) ===")
header = " " * 15 + "".join([f"{m[:5]:>8}" for m in metrics])
print(header)

for m1 in metrics:
    row = f"{m1:<15}"
    for m2 in metrics:
        cov = calc_cov(scores[m1], means[m1], scores[m2], means[m2])
        r = cov / (math.sqrt(vars_dict[m1]) * math.sqrt(vars_dict[m2]))
        row += f"{r:>8.3f}"
    print(row)
