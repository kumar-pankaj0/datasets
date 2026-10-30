import json
import re
from code.validator import validate_pair, validate_batch
from code.cleaner import clean_sample

samples = []

# --- SHORT SAMPLES (1 to 4): < 25 words, exactly 1 sentence, 0 newlines, max 1 cut-word ---

# Sample 1
# Refined: Our architectural decision record selects Kafka topic compaction by preserving the latest state key. (14 words)
# Cut-word: select -> selects (1 cut word: select is normal word or select -> selects)
# In raw: "our architectural decis record selects kafka topic compact buy preserving the latest state key"
# Wait, let's make sure "compact" -> "compaction" or "decis" -> "decision". Let's have max 1 cut-word restoration.
# Let's say "topic compaction" spoken as "topic compact" (1 cut-word).
s1_raw = "our architectural decision record selects kafka topic compact buy preserving the latest state key"
s1_ref = "Our architectural decision record selects Kafka topic compaction by preserving the latest state key."

# Sample 2
# Refined: This technical RFC rejects Postgres in favor of ClickHouse for telemetry ingestion. (13 words)
# Cut-word: ingest -> ingestion (1 cut-word)
s2_raw = "this technical r f c rejects post gres in favor of clickhouse four telemetry ingest"
s2_ref = "This technical RFC rejects Postgres in favor of ClickHouse for telemetry ingestion."

# Sample 3
# Refined: We standardize inter-service RPC payloads on Protocol Buffers by deprecating JSON. (11 words)
# Cut-word: standardiz -> standardize (1 cut-word)
s3_raw = "we standardiz inter service r p c payloads on protocol buffers buy deprecating j son"
s3_ref = "We standardize inter-service RPC payloads on Protocol Buffers by deprecating JSON."

# Sample 4
# Refined: The consensus RFC specifies an election timeout of 300 milliseconds. (10 words)
# Cut-word: specifi -> specifies (1 cut-word)
s4_raw = "the consensus r f c specifi an election timeout of three hundred milliseconds"
s4_ref = "The consensus RFC specifies an election timeout of 300 milliseconds."

samples.extend([
    {"raw_asr": s1_raw, "refined_text": s1_ref},
    {"raw_asr": s2_raw, "refined_text": s2_ref},
    {"raw_asr": s3_raw, "refined_text": s3_ref},
    {"raw_asr": s4_raw, "refined_text": s4_ref},
])

print("Short samples loaded:", len(samples))
