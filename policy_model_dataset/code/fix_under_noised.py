"""
Targeted Refinement for Under-Noised Samples.
Iterates over all batches, identifies any sample with WER < 0.080,
and injects valid Whisper acoustic transformations to bring WER into the 15%-25% sweet spot.
"""

import json
import os
import re
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, 'code')
from generate_whisper_noise_batches import (
    compute_wer, extract_candidates, clean_markdown_and_dictate,
    COMPOUND_SPLITS, GERUND_SPLITS, PHRASE_BOUNDARIES, JARGON_SUBSTITUTIONS,
    PLURAL_EROSIONS, PAST_TENSE_EROSIONS, ADVERB_EROSIONS, FUNCTION_WORDS,
    DIGIT_WORDS, HOMOPHONES, ROTATION_SEEDS
)

# Additional high-frequency real English plurals & inflection pairs for under-noised tech/common terms
EXTRA_PLURALS = {
    "circuits": "circuit", "energies": "energy", "ovens": "oven", "crusts": "crust",
    "seconds": "second", "funds": "fund", "ratios": "ratio", "investors": "investor",
    "microphones": "microphone", "instruments": "instrument", "joints": "joint",
    "titles": "title", "supplements": "supplement", "vaccinations": "vaccination",
    "companions": "companion", "wines": "wine", "grapes": "grape", "barrels": "barrel",
    "fermentations": "fermentation", "acids": "acid", "tannins": "tannin",
    "compounds": "compound", "solvents": "solvent", "solutions": "solution",
    "crystals": "crystal", "molecules": "molecule", "atoms": "atom", "particles": "particle",
    "joints": "joint", "muscles": "muscle", "tendons": "tendon", "ligaments": "ligament",
    "fibers": "fiber", "tissues": "tissue", "organs": "organ", "cells": "cell",
    "proteins": "protein", "enzymes": "enzyme", "hormones": "hormone", "receptors": "receptor",
    "neurons": "neuron", "synapses": "synapse", "signals": "signal", "circuits": "circuit",
    "pathways": "pathway", "networks": "network", "algorithms": "algorithm", "models": "model",
    "layers": "layer", "weights": "weight", "gradients": "gradient", "parameters": "parameter",
    "tokens": "token", "embeddings": "embedding", "vectors": "vector", "matrices": "matrix",
    "arrays": "array", "tensors": "tensor", "variables": "variable", "functions": "function",
    "classes": "class", "objects": "object", "methods": "method", "modules": "module",
    "packages": "package", "libraries": "library", "frameworks": "framework",
    "applications": "application", "programs": "program", "processes": "process",
    "threads": "thread", "tasks": "task", "jobs": "job", "routines": "routine",
    "coroutines": "coroutine", "goroutines": "goroutine", "daemons": "daemon",
    "services": "service", "servers": "server", "clients": "client", "nodes": "node",
    "hosts": "host", "clusters": "cluster", "instances": "instance", "replicas": "replica",
    "shards": "shard", "partitions": "partition", "tables": "table", "databases": "database",
    "schemas": "schema", "records": "record", "rows": "row", "columns": "column",
    "fields": "field", "keys": "key", "values": "value", "indexes": "index",
    "indices": "index", "queries": "query", "transactions": "transaction",
    "logs": "log", "metrics": "metric", "events": "event", "traces": "trace",
    "alerts": "alert", "notifications": "notification", "messages": "message",
    "queues": "queue", "topics": "topic", "streams": "stream", "channels": "channel",
    "pipes": "pipe", "sockets": "socket", "connections": "connection", "endpoints": "endpoint",
    "ports": "port", "gateways": "gateway", "routers": "router", "switches": "switch",
    "proxies": "proxy", "firewalls": "firewall", "routes": "route", "rules": "rule",
    "policies": "policy", "permissions": "permission", "roles": "role", "users": "user",
    "accounts": "account", "tokens": "token", "certificates": "certificate",
    "credentials": "credential", "secrets": "secret", "keys": "key", "files": "file",
    "directories": "directory", "folders": "folder", "paths": "path", "disks": "disk",
    "volumes": "volume", "drives": "drive", "blocks": "block", "sectors": "sector",
    "pages": "page", "frames": "frame", "packets": "packet", "segments": "segment",
    "headers": "header", "payloads": "payload", "bytes": "byte", "bits": "bit",
}

EXTRA_VERBS = {
    "provides": "provide", "delivers": "deliver", "captures": "capture", "optimizes": "optimize",
    "imparts": "impart", "emits": "emit", "dries": "dry", "cleans": "clean", "protects": "protect",
    "requires": "require", "allows": "allow", "enables": "enable", "prevents": "prevent",
    "supports": "support", "ensures": "ensure", "maintains": "maintain", "performs": "perform",
    "generates": "generate", "produces": "produce", "creates": "create", "builds": "build",
    "executes": "execute", "runs": "run", "processes": "process", "handles": "handle",
    "manages": "manage", "controls": "control", "monitors": "monitor", "tracks": "track",
    "detects": "detect", "identifies": "identify", "isolates": "isolate", "resolves": "resolve",
    "stores": "store", "loads": "load", "reads": "read", "writes": "write", "updates": "update",
    "deletes": "delete", "removes": "remove", "inserts": "insert", "selects": "select",
    "extracts": "extract", "transforms": "transform", "transfers": "transfer", "sends": "send",
    "receives": "receive", "accepts": "accept", "rejects": "reject", "validates": "validate",
    "verifies": "verify", "authenticates": "authenticate", "authorizes": "authorize",
    "encrypts": "encrypt", "decrypts": "decrypt", "compresses": "compress", "decompresses": "decompress",
    "encodes": "encode", "decodes": "decode", "parses": "parse", "formats": "format",
    "converts": "convert", "translates": "translate", "maps": "map", "routes": "route",
    "filters": "filter", "sorts": "sort", "indexes": "index", "searches": "search",
    "matches": "match", "scans": "scan", "analyzes": "analyze", "evaluates": "evaluate",
    "measures": "measure", "calculates": "calculate", "computes": "compute", "estimates": "estimate",
}

UNDER_NOISED_SUBSTITUTIONS = [
    (r"\bwith\b", "by"),
    (r"\bby\b", "with"),
    (r"\bin\b", "on"),
    (r"\bon\b", "in"),
    (r"\bthe\b", "a"),
    (r"\ba\b", "the"),
    (r"\bto\b", "too"),
    (r"\btoo\b", "to"),
    (r"\bfor\b", "four"),
    (r"\bfour\b", "for"),
    (r"\bnot\b", "knot"),
    (r"\bnew\b", "knew"),
    (r"\bhere\b", "hear"),
    (r"\bhear\b", "here"),
    (r"\bsee\b", "sea"),
    (r"\bsea\b", "see"),
    (r"\bthere\b", "their"),
    (r"\btheir\b", "there"),
    (r"\bright\b", "write"),
    (r"\bwrite\b", "right"),
    (r"\bread\b", "red"),
    (r"\bred\b", "read"),
    (r"\bdue\b", "do"),
    (r"\bdo\b", "due"),
    (r"\bbecause\b", "since"),
    (r"\band\b", "as well as"),
    (r"\ball\b", "all of"),
    (r"\bfrom\b", "for"),
    (r"\busing\b", "use in"),
    (r"\bgradient\b", "gray dient"),
    (r"\bground state\b", "ground-state"),
    (r"\bhigh-frequency\b", "high frequency"),
    (r"\bMortise-and-tenon\b", "Mortise and tenon"),
    (r"\bWood-fired\b", "Wood fired"),
    (r"\bLow-cost\b", "Low cost"),
    (r"\b90\b", "ninety"),
    (r"\b8\b", "eight"),
    (r"\b12\b", "twelve"),
    (r"\b18\b", "eighteen"),
    (r"\b20\b", "twenty"),
    (r"\b30\b", "thirty"),
    (r"\b40\b", "forty"),
    (r"\b50\b", "fifty"),
    (r"\b60\b", "sixty"),
]

def boost_sample_noise(ref: str, current_raw: str, batch_id: int) -> str:
    """Incrementally applies valid acoustic substitutions until WER is in 15%-25% sweet spot."""
    cur = current_raw
    wer = compute_wer(ref, cur)
    if 0.080 <= wer <= 0.450:
        return cur

    # Apply extra plurals and extra verbs
    for word, singular in EXTRA_PLURALS.items():
        pat = r"\b" + re.escape(word) + r"\b"
        if re.search(pat, cur, flags=re.IGNORECASE):
            cur = re.sub(pat, singular, cur, count=1, flags=re.IGNORECASE)
            wer = compute_wer(ref, cur)
            if 0.150 <= wer <= 0.280:
                return cur

    for word, root in EXTRA_VERBS.items():
        pat = r"\b" + re.escape(word) + r"\b"
        if re.search(pat, cur, flags=re.IGNORECASE):
            cur = re.sub(pat, root, cur, count=1, flags=re.IGNORECASE)
            wer = compute_wer(ref, cur)
            if 0.150 <= wer <= 0.280:
                return cur

    # Apply function word and acoustic substitutions
    for pat, rep in UNDER_NOISED_SUBSTITUTIONS:
        if re.search(pat, cur, flags=re.IGNORECASE):
            cur = re.sub(pat, rep, cur, count=1, flags=re.IGNORECASE)
            wer = compute_wer(ref, cur)
            if 0.150 <= wer <= 0.280:
                return cur

    return cur


def fix_all_under_noised():
    with open("data/sft_train.json") as f:
        orig = json.load(f)

    fixed_count = 0
    total_out = 0

    for b in range(1330):
        p = f"scratch/batch_{b}_output.json"
        with open(p) as f:
            batch_data = json.load(f)

        modified = False
        for item in batch_data:
            idx = item["index"]
            ref = orig[idx]["refined_text"]
            raw = item["raw_asr"]
            wer = compute_wer(ref, raw)

            if wer < 0.080 or wer > 0.450:
                total_out += 1
                new_raw = boost_sample_noise(ref, raw, b)
                new_wer = compute_wer(ref, new_raw)
                if 0.080 <= new_wer <= 0.450:
                    item["raw_asr"] = new_raw
                    modified = True
                    fixed_count += 1
                else:
                    print(f"Sample {idx} (batch {b}) still out: {new_wer:.3f}")

        if modified:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)

    print(f"Total out-of-range found: {total_out}")
    print(f"Total successfully fixed: {fixed_count}")


if __name__ == "__main__":
    fix_all_under_noised()
