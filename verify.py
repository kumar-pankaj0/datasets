import json
import math

with open('data_full.json', 'r') as f:
    data = json.load(f)

metrics = ['faithfulness', 'noise_removed', 'errors_fixed', 'formatting']
scores = {m: [] for m in metrics}

for item in data:
    for m in metrics:
        scores[m].append(item['output'][m])

n = len(data)
print(f"=== DATASET SIGNAL AUDIT (data_full.json - {n} samples) ===\n")

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

# 1. Variance and Entropy
print(f"{'Metric':<15} | {'Variance (Spread)':<18} | {'Entropy (Bits)':<15}")
print("-" * 55)
for m in metrics:
    var = vars_dict[m]
    ent = calc_entropy(scores[m])
    print(f"{m:<15} | {var:<18.4f} | {ent:<15.4f}")

# 2. Pearson Correlation
print("\n=== PEARSON CORRELATION MATRIX (|r| should be approx 0) ===")
header = " " * 15 + "".join([f"{m[:5]:>8}" for m in metrics])
print(header)

for m1 in metrics:
    row = f"{m1:<15}"
    for m2 in metrics:
        cov = calc_cov(scores[m1], means[m1], scores[m2], means[m2])
        r = cov / (math.sqrt(vars_dict[m1]) * math.sqrt(vars_dict[m2]))
        row += f"{r:>8.3f}"
    print(row)
