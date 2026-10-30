import sys
import json

sys.path.append("scratch")
from test_batch import test_samples, validate_pair, validate_batch, clean_sample

with open("scratch/subagent_batch_14.json", "r", encoding="utf-8") as f:
    batch_14 = json.load(f)

ok = test_samples(batch_14)
if not ok:
    print("Validation failed!")
    sys.exit(1)
print("Validation succeeded!")
