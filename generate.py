import json
import random
import math
import copy
import re

random.seed(42)

def pearson_corr(x, y):
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mean_x)**2 for a in x) * sum((b - mean_y)**2 for b in y))
    if den == 0:
        return 0
    return num / den

def generate_scores():
    scores = [1]*20 + [3]*20 + [5]*20 + [7]*20 + [9]*20
    while True:
        s1 = random.sample(scores, 100)
        s2 = random.sample(scores, 100)
        s3 = random.sample(scores, 100)
        s4 = random.sample(scores, 100)
        
        arr = [s1, s2, s3, s4]
        max_corr = 0
        for i in range(4):
            for j in range(i+1, 4):
                corr = pearson_corr(arr[i], arr[j])
                max_corr = max(max_corr, abs(corr))
        
        if max_corr < 0.70:
            return s1, s2, s3, s4

f_scores, n_scores, e_scores, fmt_scores = generate_scores()

templates = [
    {
        "base_tokens": ["we", "need", "to", "configure", "the", "oauth2", "authentication", "middleware", "for", "the", "new", "api"],
        "asr_noise_tokens": ["so", "uh", "we", "need", "to", "like", "config", "the", "oh", "auth", "two", "authenticat", "mid", "middleware", "for", "the", "new", "a", "p", "i", "you", "know"],
        "error_map": {"oauth2": ["oh auth two", "oh auth", "oauth"], "authentication": ["authenticat", "auth"], "middleware": ["mid middleware", "middle"], "api": ["a p i", "app i", "ap i"]},
        "fillers": ["so", "uh", "like", "you know", "i mean", "um"],
        "stutters": {"configure": "config", "authentication": "authenticat", "middleware": "mid middleware"},
        "meaning_drops": {
            9: ["we", "need", "to", "configure", "the", "oauth2", "authentication", "middleware", "for", "the", "new", "api"],
            7: ["we", "need", "to", "configure", "oauth2", "middleware", "for", "the", "api"],
            5: ["we", "need", "to", "configure", "the", "authentication", "for", "the", "api"],
            3: ["we", "need", "to", "set", "up", "the", "api"],
            1: ["we", "need", "to", "delete", "the", "middleware"]
        },
        "markdown": ["`OAuth2`", "`API`"]
    },
    {
        "base_tokens": ["the", "kubernetes", "cluster", "is", "experiencing", "oom", "kills", "in", "the", "ingress", "controller"],
        "asr_noise_tokens": ["the", "uh", "coober", "netties", "clus", "cluster", "is", "like", "experiencing", "oh", "oh", "em", "kills", "in", "the", "in", "ingress", "k-", "controller"],
        "error_map": {"kubernetes": ["coober netties", "kuber netties"], "cluster": ["clus cluster"], "oom": ["oh oh em", "oh em"], "ingress": ["in ingress"], "controller": ["k- controller"]},
        "fillers": ["uh", "like", "actually", "um"],
        "stutters": {"cluster": "clus cluster", "ingress": "in ingress", "controller": "k- controller"},
        "meaning_drops": {
            9: ["the", "kubernetes", "cluster", "is", "experiencing", "oom", "kills", "in", "the", "ingress", "controller"],
            7: ["the", "kubernetes", "cluster", "has", "oom", "kills", "in", "the", "ingress", "controller"],
            5: ["the", "cluster", "is", "experiencing", "oom", "kills"],
            3: ["the", "cluster", "is", "dying"],
            1: ["the", "kubernetes", "cluster", "is", "working", "perfectly"]
        },
        "markdown": ["`Kubernetes`", "`OOM`", "`ingress controller`"]
    },
    {
        "base_tokens": ["the", "postgres", "database", "requires", "a", "vacuum", "full", "to", "reclaim", "disk", "space"],
        "asr_noise_tokens": ["the", "you", "know", "posgres", "data", "database", "requires", "a", "like", "vac", "vacuum", "full", "to", "re", "reclaim", "mem", "disk", "space"],
        "error_map": {"postgres": ["posgres", "post gres"], "database": ["data database"], "vacuum": ["vac vacuum"], "reclaim": ["re reclaim", "mem disk"]},
        "fillers": ["you know", "like", "basically", "um"],
        "stutters": {"database": "data database", "vacuum": "vac vacuum", "reclaim": "re reclaim"},
        "meaning_drops": {
            9: ["the", "postgres", "database", "requires", "a", "vacuum", "full", "to", "reclaim", "disk", "space"],
            7: ["the", "postgres", "database", "needs", "a", "vacuum", "full", "for", "disk", "space"],
            5: ["the", "database", "requires", "a", "vacuum", "to", "reclaim", "space"],
            3: ["the", "database", "needs", "more", "space"],
            1: ["we", "should", "delete", "the", "postgres", "database"]
        },
        "markdown": ["`Postgres`", "`VACUUM FULL`"]
    },
    {
        "base_tokens": ["tensorflow", "is", "throwing", "an", "out", "of", "memory", "exception", "during", "the", "backpropagation", "step"],
        "asr_noise_tokens": ["ten", "tensor", "flow", "is", "like", "throwing", "an", "uh", "out", "of", "mem", "memory", "exception", "during", "the", "back", "backprop", "step"],
        "error_map": {"tensorflow": ["ten tensor flow", "tensor flow"], "memory": ["mem memory"], "backpropagation": ["back backprop", "back prop"]},
        "fillers": ["like", "uh", "literally", "um"],
        "stutters": {"tensorflow": "ten tensor flow", "memory": "mem memory", "backpropagation": "back backprop"},
        "meaning_drops": {
            9: ["tensorflow", "is", "throwing", "an", "out", "of", "memory", "exception", "during", "the", "backpropagation", "step"],
            7: ["tensorflow", "is", "throwing", "an", "out", "of", "memory", "exception", "during", "backprop"],
            5: ["tensorflow", "is", "throwing", "a", "memory", "exception"],
            3: ["tensorflow", "is", "crashing"],
            1: ["tensorflow", "finished", "training", "successfully"]
        },
        "markdown": ["`TensorFlow`", "`Out Of Memory`", "`backpropagation`"]
    },
    {
        "base_tokens": ["the", "memory", "allocator", "is", "failing", "because", "of", "a", "memory", "leak", "in", "the", "redis", "cache"],
        "asr_noise_tokens": ["the", "mem", "memory", "allocat", "allocator", "is", "um", "failing", "because", "of", "a", "mem", "memory", "leak", "in", "the", "red", "redis", "cache"],
        "error_map": {"memory": ["mem memory", "mem"], "allocator": ["allocat allocator", "allocat"], "redis": ["red redis", "red is"]},
        "fillers": ["um", "so", "like"],
        "stutters": {"memory": "mem memory", "allocator": "allocat allocator", "redis": "red redis"},
        "meaning_drops": {
            9: ["the", "memory", "allocator", "is", "failing", "because", "of", "a", "memory", "leak", "in", "the", "redis", "cache"],
            7: ["the", "memory", "allocator", "is", "failing", "due", "to", "a", "leak", "in", "redis"],
            5: ["the", "allocator", "is", "failing", "because", "of", "a", "memory", "leak"],
            3: ["the", "cache", "is", "failing"],
            1: ["redis", "cache", "is", "working", "fine"]
        },
        "markdown": ["`memory allocator`", "`Redis`"]
    }
]

dataset = []
for i in range(100):
    f, n, e, fmt = f_scores[i], n_scores[i], e_scores[i], fmt_scores[i]
    t = templates[i % 5]
    
    raw_asr = " ".join(t["asr_noise_tokens"])
    words = copy.deepcopy(t["meaning_drops"][f])
    
    if e < 9:
        num_errors_to_inject = max(1, int(len(t["error_map"]) * (9 - e) / 8))
        error_keys = list(t["error_map"].keys())
        random.shuffle(error_keys)
        injected = 0
        for w_idx, w in enumerate(words):
            if w in error_keys and injected < num_errors_to_inject:
                words[w_idx] = random.choice(t["error_map"][w])
                injected += 1
                
    if n < 9:
        num_noise_to_inject = max(1, int(4 * (9 - n) / 8))
        for _ in range(num_noise_to_inject):
            insert_idx = random.randint(0, len(words))
            noise_word = random.choice(t["fillers"])
            words.insert(insert_idx, noise_word)
            
    refined_text = " ".join(words)
    
    if fmt == 9:
        refined_text = refined_text.capitalize() + "."
        for md in t["markdown"]:
            clean_md = md.replace("`", "").lower()
            if clean_md in refined_text.lower():
                refined_text = re.sub(re.escape(clean_md), md, refined_text, flags=re.IGNORECASE)
        refined_text = refined_text + "\n\n---"
    elif fmt >= 7:
        refined_text = refined_text.capitalize() + "."
    elif fmt >= 5:
        refined_text = refined_text.capitalize()
    elif fmt >= 3:
        refined_text = refined_text.lower()
    else:
        refined_text = refined_text.lower().replace(" ", "  ")

    sample = {
        "input": {
            "raw_asr": raw_asr,
            "refined_text": refined_text
        },
        "output": {
            "faithfulness": int(f),
            "noise_removed": int(n),
            "errors_fixed": int(e),
            "formatting": int(fmt)
        }
    }
    dataset.append(sample)

with open("/data/data/com.termux/files/home/project/dataset_generation_for_juage/dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("Dataset generated successfully.")
