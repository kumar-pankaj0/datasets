import json
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, get_noise_layer_count, count_active_noise_layers
from cleaner import clean_sample

print("Validator and cleaner loaded successfully.")
