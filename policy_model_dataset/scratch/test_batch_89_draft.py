import json
import re
import sys
import os

# Add code directory to path
sys.path.append("code")
import validator
import cleaner

# Load eval set for leakage check
eval_file = "sft_eval.json"
eval_data = []
if os.path.exists(eval_file):
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

print(f"Loaded {len(eval_data)} eval samples for leakage checks.")
