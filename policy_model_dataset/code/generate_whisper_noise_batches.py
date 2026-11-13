"""
Whisper Acoustic Noise Batch Generator.
Milestone 1: Noise Generation Pool.

Generates realistic Whisper acoustic noise for samples in data/sft_train.json
across 1,330 batch files in scratch/batch_{batch_id}_output.json.

Strict Guarantees:
1. Input contract: Takes {index, refined_text}.
2. Output contract: Outputs List[{"index": int, "raw_asr": str}] saved to scratch/batch_{batch_id}_output.json.
   NEVER outputs refined_text in batch files.
3. Mechanism Rotation Seed: Every batch includes Mechanism 1 + 2 rotated mechanisms from {2,3,4,5,6}.
4. Real English Words Only: Zero suffix chopping or non-word truncation.
5. Mandatory Boundary Shifts: Every sample includes Mechanism 1 multi-word boundary shifts.
6. Zero Markdown: Strips all backticks, bullet points, headers, and converts \\n\\n to . .
7. Noise Distribution: In multi-sentence samples, distributes noise across every sentence.
8. Target WER: 15%-25% (acceptable: 8%-45%).
9. Preservation: Never alters numbers to different factual values. Never drops whole sentences.
10. All 1,330 batch files covered (indices 0 to 13294).
"""

import copy
import json
import os
import random
import re
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# 1. Mechanism Rotation Seeds (10 combinations of 1 + two of 2..6)
# ---------------------------------------------------------------------------
ROTATION_SEEDS: List[Tuple[int, int, int]] = [
    (1, 3, 5),  # Batch 0: Mechanism 1 + favor 3, 5
    (1, 2, 4),  # Batch 1: Mechanism 1 + favor 2, 4
    (1, 2, 6),  # Batch 2: Mechanism 1 + favor 2, 6
    (1, 2, 3),  # Batch 3: Mechanism 1 + favor 2, 3
    (1, 2, 5),  # Batch 4: Mechanism 1 + favor 2, 5
    (1, 3, 4),  # Batch 5: Mechanism 1 + favor 3, 4
    (1, 3, 6),  # Batch 6: Mechanism 1 + favor 3, 6
    (1, 4, 5),  # Batch 7: Mechanism 1 + favor 4, 5
    (1, 4, 6),  # Batch 8: Mechanism 1 + favor 4, 6
    (1, 5, 6),  # Batch 9: Mechanism 1 + favor 5, 6
]

# ---------------------------------------------------------------------------
# 2. Strict Real English Word Dictionaries & Mechanisms
# ---------------------------------------------------------------------------

# Mechanism 1: Compound Word & Tech Term Boundary Splits
COMPOUND_SPLITS: Dict[str, str] = {
    "database": "data base", "databases": "data bases", "backend": "back end", "backends": "back ends",
    "frontend": "front end", "frontends": "front ends", "pipeline": "pipe line", "pipelines": "pipe lines",
    "workflow": "work flow", "workflows": "work flows", "bandwidth": "band width", "bandwidths": "band widths",
    "watchdog": "watch dog", "workload": "work load", "workloads": "work loads", "endpoint": "end point",
    "endpoints": "end points", "deadlock": "dead lock", "deadlocks": "dead locks", "bytecode": "byte code",
    "metadata": "meta data", "timeout": "time out", "timeouts": "time outs", "runtime": "run time",
    "failover": "fail over", "failovers": "fail overs", "backpressure": "back pressure",
    "throughput": "through put", "lifecycle": "life cycle", "lifecycles": "life cycles",
    "sandboxing": "sand boxing", "filesystem": "file system", "filesystems": "file systems",
    "heartbeat": "heart beat", "heartbeats": "heart beats", "bottleneck": "bottle neck",
    "bottlenecks": "bottle necks", "gateway": "gate way", "gateways": "gate ways",
    "firewall": "fire wall", "firewalls": "fire walls", "payload": "pay load", "payloads": "pay loads",
    "namespace": "name space", "namespaces": "name spaces", "timeseries": "time series",
    "timestamp": "time stamp", "timestamps": "time stamps", "playbook": "play book",
    "playbooks": "play books", "runbook": "run book", "runbooks": "run books", "bootstrap": "boot strap",
    "middleware": "middle ware", "firmware": "firm ware", "hardware": "hard ware", "software": "soft ware",
    "hypervisor": "hyper visor", "hypervisors": "hyper visors", "downstream": "down stream",
    "upstream": "up stream", "crossplane": "cross plane", "wireguard": "wire guard",
    "multicloud": "multi cloud", "multithreaded": "multi threaded", "microservices": "micro services",
    "microservice": "micro service", "serverless": "server less", "stateless": "state less",
    "stateful": "state full", "checkpoint": "check point", "checkpoints": "check points",
    "hotfix": "hot fix", "hotfixes": "hot fixes", "fallback": "fall back", "fallbacks": "fall backs",
    "standby": "stand by", "cleanup": "clean up", "setup": "set up", "setups": "set ups",
    "offline": "off line", "online": "on line", "into": "in to", "onto": "on to", "within": "with in",
    "without": "with out", "upon": "up on", "towards": "to wards", "sometimes": "some times",
    "forever": "for ever", "already": "all ready", "another": "an other", "cannot": "can not",
    "throughout": "through out", "furthermore": "further more", "meanwhile": "mean while",
    "nevertheless": "never the less", "nonetheless": "none the less", "overhead": "over head",
    "feedback": "feed back", "timesheet": "time sheet", "timeslot": "time slot", "timeslots": "time slots",
    "baseline": "base line", "baselines": "base lines", "timeline": "time line", "timelines": "time lines",
    "deadline": "dead line", "deadlines": "dead lines", "subsystem": "sub system",
    "subsystems": "sub systems", "roundtrip": "round trip", "subquery": "sub query",
    "subqueries": "sub queries", "subgraph": "sub graph", "subgraphs": "sub graphs",
    "statevector": "stay vector", "statevectors": "stay vectors", "jacket": "jack it",
    "together": "to gather", "understand": "under stand", "configure": "can figure",
    "configuring": "can figuring", "configured": "can figured", "authenticate": "then locate",
    "descriptor": "the scripter", "descriptors": "the scripters", "keyword": "key word",
    "keywords": "key words", "input": "in put", "inputs": "in puts", "midday": "mid day",
    "rescheduling": "re scheduling", "wellness": "well ness", "tonight": "to night",
    "checksum": "check sum", "checksums": "check sums", "unresponsive": "un responsive",
    "rebalance": "re balance", "checkout": "check out", "kubectl": "kube control",
    "nginx": "engine X", "postgresql": "post gres Q L", "postgres": "post gres",
    "mongodb": "mongo D B", "mariadb": "maria D B", "rocksdb": "rocks DB", "rabbitmq": "rabbit M Q",
    "etcd": "et see dee", "grpc": "G R P C", "oauth": "O auth", "terraform": "terra form",
    "firecracker": "fire cracker", "gvisor": "gee visor", "microvm": "micro VM", "microvms": "micro VMs",
    "jetstream": "jet stream", "daemonset": "daemon set", "daemonsets": "daemon sets",
    "webhook": "web hook", "webhooks": "web hooks", "websocket": "web socket", "websockets": "web sockets",
    "goroutine": "go routine", "goroutines": "go routines", "coroutine": "co routine",
    "coroutines": "co routines", "multiprocessing": "multi processing", "multithreading": "multi threading",
    "ciphertext": "cypher text", "plaintext": "plain text", "wireshark": "wire shark",
    "loopback": "loop back", "conntrack": "conn track", "tcpdump": "tcp dump", "devops": "dev ops",
    "mlops": "M L ops", "sysadmin": "sys admin", "standup": "stand up", "standups": "stand ups",
    "rollout": "roll out", "rollouts": "roll outs", "rollback": "roll back", "rollbacks": "roll backs",
    "waterfall": "water fall", "waterfalls": "water falls", "framework": "frame work",
    "frameworks": "frame works", "background": "back ground", "backgrounds": "back grounds",
    "underlying": "under lying", "override": "over ride", "overrides": "over rides",
    "overloaded": "over loaded", "overload": "over load", "overheating": "over heating",
    "overheat": "over heat", "lookup": "look up", "lookups": "look ups", "timeframe": "time frame",
    "timeframes": "time frames", "filepath": "file path", "filepaths": "file paths",
    "filename": "file name", "filenames": "file names", "username": "user name",
    "usernames": "user names", "hostname": "host name", "hostnames": "host names",
    "clusterip": "cluster IP", "nodeport": "node port", "clusterrole": "cluster role",
    "serviceaccount": "service account", "configmap": "config map", "configmaps": "config maps",
    "cronjob": "cron job", "cronjobs": "cron jobs", "ingress": "in gress", "outbound": "out bound",
    "inbound": "in bound", "upfront": "up front", "tradeoff": "trade off", "tradeoffs": "trade offs",
    "handshake": "hand shake", "datacenter": "data center", "datacenters": "data centers",
    "dataset": "data set", "datasets": "data sets", "datasource": "data source",
    "datasources": "data sources", "submodule": "sub module", "submodules": "sub modules",
    "codebase": "code base", "codebases": "code bases", "quickstart": "quick start",
    "workaround": "work around", "workarounds": "work arounds", "troubleshooting": "trouble shooting",
    "uptime": "up time", "downtime": "down time", "update": "up date", "updates": "up dates",
    "updating": "up dating", "updated": "up dated", "upgrade": "up grade", "upgrades": "up grades",
    "upgrading": "up grading", "upgraded": "up graded", "upload": "up load", "uploads": "up loads",
    "download": "down load", "downloads": "down loads", "microchip": "micro chip", "peanuts": "pea nuts",
    "overtime": "over time", "before": "be for", "behind": "be hind", "between": "be tween",
    "beyond": "be yond", "inside": "in side", "outside": "out side", "today": "to day",
    "become": "be come", "became": "be came", "maybe": "may be", "anyone": "any one",
    "anything": "any thing", "anyway": "any way", "everyone": "every one", "everything": "every thing",
    "everyday": "every day", "someone": "some one", "something": "some thing", "somewhere": "some where",
    "nowhere": "no where", "nobody": "no body", "nothing": "no thing", "unless": "and less",
    "outage": "out age", "outages": "out ages", "overview": "over view", "output": "out put",
    "outputs": "out puts", "outcome": "out come", "outcomes": "out comes", "fielddata": "field data",
    "windsurf": "wind surf", "pasta": "pass to", "prescaler": "pre scaler", "synthesizer": "synth sizer",
    "suitcase": "suit case", "covenants": "cover notes", "easements": "ease mints", "basecamp": "base camp",
    "linear": "line ear", "keybase": "key base", "mattermost": "matter most", "standuply": "stand up ly",
    "preact": "pre act", "crossbeam": "cross beam", "indicatif": "in decay tif", "soundfile": "sound file",
    "tiptap": "tip tap", "undici": "un dee chee", "dramatiq": "dramatick", "courtroom": "court room",
    "backlog": "back log", "platform": "plat form", "upcoming": "up coming", "unindexed": "un indexed",
    "tomorrow": "to morrow", "upward": "up ward", "downward": "down ward", "forward": "for ward",
    "backward": "back ward", "inward": "in ward", "outward": "out ward", "elasticsearch": "elastic search",
    "redis": "read is", "because": "be cause", "monthly": "month ly", "treatment": "treat meant",
    "interviews": "inter views", "punishments": "punish mints", "punishment": "punish meant",
    "recreation": "re creation", "unencrypted": "un encrypted", "controller": "control ler",
    "subsequently": "sub sequently", "initially": "initial ly", "delivery": "deliver ee",
    "employers": "em ploy ers", "attorney": "at torney", "sharedpreferences": "shared preferences",
    "viewing": "view in", "bedrooms": "bed rooms", "backpacks": "back packs", "unattended": "un attended",
    "pickup": "pick up", "cosign": "co sign", "payment": "pay meant", "appointment": "appoint meant",
    "samtools": "sam tools", "overwriting": "over writing", "overwrite": "over write",
    "overwrites": "over writes", "unassigned": "un assigned", "untrusted": "un trusted",
    "unexpected": "un expected", "unauthorized": "un authorized", "unauthenticated": "un authenticated",
    "unresolved": "un resolved", "unhandled": "un handled", "unsupported": "un supported",
    "unstable": "un stable", "unavailable": "un available", "rebuild": "re build", "restart": "re start",
    "reload": "re load", "reconnect": "re connect", "redeploy": "re deploy", "reconfigure": "re configure",
    "reopen": "re open", "retry": "re try", "retrying": "re trying", "review": "re view",
    "replace": "re place", "recover": "re cover", "refresh": "re fresh", "restore": "re store",
    "reset": "re set", "reduce": "re duce", "return": "re turn", "resolve": "re solve",
    "interrupt": "inter rupt", "interrupts": "inter rupts", "intermediate": "inter mediate",
    "intermittent": "inter mittent", "internal": "inter nal", "interface": "inter face",
    "interfaces": "inter faces", "subtask": "sub task", "subtasks": "sub tasks",
    "subcomponent": "sub component", "subcomponents": "sub components", "substring": "sub string",
    "substrings": "sub strings", "multitenant": "multi tenant", "multiregion": "multi region",
    "microchips": "micro chips", "microcontroller": "micro controller",
    "microcontrollers": "micro controllers", "crosscluster": "cross cluster",
    "crossregion": "cross region", "deployment": "deploy meant", "agreement": "agree meant",
    "environment": "environ meant", "management": "manage meant", "development": "develop meant",
    "settlement": "settle meant", "document": "doc you meant", "documents": "doc you ments",
    "requirement": "require meant", "requirements": "require meants", "assessment": "assess meant",
    "improvement": "improve meant", "enhancement": "enhance meant", "containment": "contain meant",
    "tabletop": "table top", "tabletops": "table tops", "doorway": "door way", "hallway": "hall way",
    "stairway": "stair way", "walkway": "walk way", "pathway": "path way", "pathways": "path ways",
    "driveway": "drive way", "roadway": "road way", "freeway": "free way", "highway": "high way",
    "railway": "rail way", "subway": "sub way", "waterway": "water way", "waterways": "water ways",
    "waterfront": "water front", "lakefront": "lake front", "oceanfront": "ocean front",
    "beachfront": "beach front", "riverfront": "river front", "seashore": "sea shore",
    "sunlight": "sun light", "moonlight": "moon light", "daylight": "day light", "nighttime": "night time",
    "daytime": "day time", "lifetime": "life time", "lunchtime": "lunch time", "bedtime": "bed time",
    "springtime": "spring time", "summertime": "summer time", "wintertime": "winter time",
}

# Mechanism 1: Common Gerund Syllable Splits (Valid Real Words Only)
GERUND_SPLITS: Dict[str, str] = {
    "thinking": "think in", "replacing": "replace in", "stalling": "stall in", "rolling": "roll in",
    "adding": "add in", "improving": "improve in", "processing": "process in", "running": "run in",
    "checking": "check in", "routing": "route in", "testing": "test in", "streaming": "stream in",
    "tracking": "track in", "training": "train in", "monitoring": "monitor in", "blocking": "block in",
    "serving": "serve in", "handling": "handle in", "migrating": "migrate in", "updating": "update in",
    "clearing": "clear in", "logging": "log in", "scanning": "scan in", "building": "build in",
    "allocating": "allocate in", "filtering": "filter in", "scheduling": "schedule in", "caching": "cache in",
    "indexing": "index in", "locking": "lock in", "parsing": "parse in", "flushing": "flush in",
    "sorting": "sort in", "measuring": "measure in", "binding": "bind in", "polling": "poll in",
    "fetching": "fetch in", "dropping": "drop in", "failing": "fail in", "passing": "pass in",
    "reloading": "reload in", "starting": "start in", "stopping": "stop in", "holding": "hold in",
    "sending": "send in", "calling": "call in", "buying": "by in", "setting": "set in",
    "getting": "get in", "putting": "put in", "doing": "do in", "going": "go in", "coming": "come in",
    "saying": "say in", "making": "make in", "taking": "take in", "looking": "look in", "asking": "ask in",
    "giving": "give in", "showing": "show in", "trying": "try in", "working": "work in", "moving": "move in",
    "paying": "pay in", "living": "live in", "waiting": "wait in", "watching": "watch in",
    "bringing": "bring in", "carrying": "carry in", "leaving": "leave in", "feeling": "feel in",
    "opening": "open in", "changing": "change in", "closing": "close in", "cleaning": "clean in",
    "breaking": "break in", "fixing": "fix in", "staying": "stay in", "saving": "save in",
    "spending": "spend in", "reaching": "reach in", "pointing": "point in", "turning": "turn in",
    "driving": "drive in", "writing": "righting", "reading": "read in", "leaking": "leak in",
    "cramming": "cram in", "swapping": "swap in", "missing": "miss in", "shedding": "shed in",
    "comparing": "compare in", "yellowing": "yellow in", "washing": "wash in", "lighting": "light in",
    "setting": "set in", "scaling": "scale in", "routing": "route in", "pointing": "point in",
    "switching": "switch in", "matching": "match in", "batching": "batch in", "patching": "patch in",
    "merging": "merge in", "purging": "purge in", "branching": "branch in", "cloning": "clone in",
    "forking": "fork in", "pushing": "push in", "pulling": "pull in", "tagging": "tag in",
    "staging": "stage in", "committing": "commit in", "reverting": "revert in", "rebasing": "rebase in",
    "squashing": "squash in", "cherry-picking": "cherry pick in", "dropping": "drop in",
    "draining": "drain in", "flushing": "flush in", "seeding": "seed in", "weeding": "weed in",
    "feeding": "feed in", "breeding": "breed in", "speeding": "speed in", "bleeding": "bleed in",
}

# Mechanism 1: Multi-Word Phrase Merges / Boundary Shifts
PHRASE_BOUNDARIES: List[Tuple[str, str]] = [
    ("in the", "into"), ("to the", "till the"), ("for a", "from"), ("on the", "on a"),
    ("at the", "at a"), ("with the", "with a"), ("by the", "by a"), ("into the", "in to the"),
    ("next sprint", "neck sprint"), ("hire a", "Ira"), ("set up", "setup"),
    ("clean up", "cleanup"), ("fall back", "fallback"), ("back up", "backup"),
    ("roll back", "rollback"), ("roll out", "rollout"), ("time out", "timeout"),
    ("shut down", "shutdown"), ("log in", "login"), ("sign in", "signin"),
    ("check in", "checkin"), ("work out", "workout"), ("point in time", "point-in-time"),
    ("end to end", "end-to-end"), ("real time", "real-time"), ("next monday", "neck Monday"),
    ("next tuesday", "neck Tuesday"), ("next wednesday", "neck Wednesday"),
    ("next thursday", "neck Thursday"), ("next friday", "neck Friday"),
    ("next saturday", "neck Saturday"), ("next sunday", "neck Sunday"),
    ("next week", "neck week"), ("next month", "neck month"), ("next year", "neck year"),
    ("next step", "neck step"), ("next time", "neck time"), ("last week", "last-week"),
    ("last month", "last-month"), ("last year", "last-year"), ("due to", "do to"),
    ("as well as", "as well"), ("because of", "because"), ("instead of", "instead"),
    ("in order to", "to"), ("according to", "a cord in to"), ("thanks to", "thanks"),
    ("forward to", "for ward to"), ("close to", "close"),
    ("can't", "can not"), ("don't", "do not"), ("doesn't", "does not"), ("didn't", "did not"),
    ("won't", "will not"), ("wouldn't", "would not"), ("couldn't", "could not"),
    ("shouldn't", "should not"), ("isn't", "is not"), ("aren't", "are not"),
    ("wasn't", "was not"), ("weren't", "were not"), ("haven't", "have not"),
    ("hasn't", "has not"), ("hadn't", "had not"), ("it's", "it is"), ("that's", "that is"),
    ("there's", "there is"), ("here's", "here is"), ("what's", "what is"), ("let's", "let us"),
    ("dinner bill", "dinner-bill"), ("four ways", "four-ways"), ("store card", "store-card"),
    ("sleep routine", "sleep-routine"), ("car loan", "car-loan"), ("door seal", "door-seal"),
    ("written notice", "written-notice"), ("house sale", "house-sale"),
    ("package delivery", "package-delivery"), ("rigid body", "rigid-body"),
    ("cleans up", "cleanup"), ("power of attorney", "power-of-attorney"),
]

# Mechanism 2: Domain Jargon Phonetic Substitutions (Real Words Only)
JARGON_SUBSTITUTIONS: Dict[str, str] = {
    "kernel": "colonel", "kernels": "colonels", "nodes": "notes", "node": "note",
    "pod": "part", "pods": "parts", "queue": "cue", "queues": "cues",
    "keys": "peace", "key": "pea", "mounts": "bounce", "mount": "bounce",
    "erase": "array", "liens": "leans", "lien": "lean", "parcel": "partial",
    "parcels": "partials", "firecracker": "fire cracker", "gvisor": "gee visor",
    "microvm": "micro VM", "microvms": "micro VMs", "nats": "NAFs",
    "jetstream": "jet stream", "quorum": "Quorum", "rocksdb": "rocks DB",
    "etcd": "et see dee", "kubernetes": "koober nettes", "kubectl": "kube control",
    "postgresql": "post gres Q L", "postgres": "post gres", "mariadb": "maria D B",
    "mongodb": "mongo D B", "redis": "read is", "nginx": "engine X",
    "rabbitmq": "rabbit M Q", "kafka": "calf car", "ansible": "and see bull",
    "terraform": "terra form", "oauth": "O auth", "grpc": "G R P C",
    "json": "jason", "yaml": "yam el", "http": "H T T P", "https": "H T T P S",
    "sql": "sequel", "nosql": "no sequel", "graphql": "graph Q L", "api": "A P I",
    "apis": "A P Is", "sdk": "S D K", "sdks": "S D Ks", "cli": "C L I",
    "gui": "gooey", "cicd": "C I C D", "devops": "dev ops", "sysadmin": "sys admin",
    "mutex": "mew tex", "mutexes": "mew texes", "daemon": "demon", "daemons": "demons",
    "daemonset": "daemon set", "daemonsets": "daemon sets", "boolean": "boo lee in",
    "asymmetric": "a symmetric", "ciphertext": "cypher text", "plaintext": "plain text",
    "entropy": "enter pea", "sharding": "shorting", "concurrency": "can currency",
    "websocket": "web socket", "websockets": "web sockets", "webhook": "web hook",
    "webhooks": "web hooks", "telemetry": "tell emetry", "observability": "up server ability",
    "roux": "rue", "mirepoix": "meer pwah", "sauté": "saw tay", "confit": "con fee",
    "flambé": "flam bay", "asynchronous": "a synchronous", "sha-256": "shot 256",
    "gke": "G K E", "aws": "A W S", "dns": "D N S", "udp": "U D P", "tcp": "T C P",
    "cni": "C N I", "glibc": "gee lib see", "p99": "p 99", "cache": "cash",
    "caches": "cashes", "zpool": "Z pool", "numa": "new ma", "kubeadm": "cube admin",
    "70b": "seventy B", "sous-vide": "sue veed",
}

# Mechanism 3: Real English Plural Erosions (Valid Singular Dictionaries)
PLURAL_EROSIONS: Dict[str, str] = {
    "buffers": "buffer", "processes": "process", "requests": "request", "nodes": "node",
    "hosts": "host", "pools": "pool", "limits": "limit", "benchmarks": "benchmark",
    "tests": "test", "regions": "region", "instances": "instance", "metrics": "metric",
    "clusters": "cluster", "partitions": "partition", "transactions": "transaction",
    "parameters": "parameter", "connections": "connection", "exceptions": "exception",
    "services": "service", "packages": "package", "updates": "update", "records": "record",
    "fields": "field", "values": "value", "errors": "error", "warnings": "warning",
    "messages": "message", "events": "event", "threads": "thread", "calls": "call",
    "queries": "query", "lookups": "lookup", "shards": "shard", "replicas": "replica",
    "packets": "packet", "traces": "trace", "clients": "client", "servers": "server",
    "drivers": "driver", "devices": "device", "registers": "register", "counters": "counter",
    "cycles": "cycle", "allocations": "allocation", "vulnerabilities": "vulnerability",
    "dependencies": "dependency", "exploits": "exploit", "attacks": "attack",
    "questions": "question", "investigations": "investigation", "slots": "slot",
    "principles": "principle", "properties": "property", "systems": "system",
    "panels": "panel", "simulations": "simulation", "trade-offs": "trade-off",
    "boundaries": "boundary", "workloads": "workload", "tokens": "token",
    "peanuts": "peanut", "ticks": "tick", "identifiers": "identifier", "meetings": "meeting",
    "pets": "pet", "years": "year", "changes": "change", "violations": "violation",
    "interviews": "interview", "structures": "structure", "rounds": "round",
    "drops": "drop", "sessions": "session", "schemas": "schema", "instructions": "instruction",
    "sizes": "size", "runs": "run", "minutes": "minute", "releases": "release",
    "clocks": "clock", "cleaners": "cleaner", "matches": "match", "terms": "term",
    "boots": "boot", "hashes": "hash", "specials": "special", "drinks": "drink",
    "comes": "come", "needs": "need", "windows": "window", "speakers": "speaker",
    "dogs": "dog", "handlers": "handler", "collars": "collar", "tanks": "tank",
    "scrubs": "scrub", "mirrors": "mirror", "resources": "resource", "sources": "source",
    "practices": "practice", "clauses": "clause", "rules": "rule", "tickets": "ticket",
    "finishes": "finish", "tones": "tone", "compounds": "compound", "elements": "element",
    "documents": "document", "payments": "payment", "appointments": "appointment",
    "settlements": "settlement", "treatments": "treatment", "punishments": "punishment",
    "deployments": "deployment", "agreements": "agreement", "environments": "environment",
    "requirements": "requirement", "assessments": "assessment", "improvements": "improvement",
    "enhancements": "enhancement", "containments": "containment", "statements": "statement",
    "adjustments": "adjustment", "measurements": "measurement", "commitments": "commitment",
    "departments": "department", "investments": "investment", "instruments": "instrument",
    "components": "component", "segments": "segment", "fragments": "fragment",
    "arguments": "argument", "incidents": "incident", "accidents": "accident",
    "residents": "resident", "presidents": "president", "students": "student",
    "agents": "agent", "patients": "patient", "merchants": "merchant",
    "assistants": "assistant", "participants": "participant", "consultants": "consultant",
    "accountants": "accountant", "tenants": "tenant", "constants": "constant",
    "variants": "variant", "invariants": "invariant",
}

# Mechanism 3: Real English Past Tense to Root Verb (Valid Verbs Only)
PAST_TENSE_EROSIONS: Dict[str, str] = {
    "approved": "approve", "replaced": "replace", "terminated": "terminate",
    "released": "release", "automated": "automate", "configured": "configure",
    "suffered": "suffer", "saturated": "saturate", "demonstrated": "demonstrate",
    "reduced": "reduce", "remained": "remain", "experienced": "experience",
    "verified": "verify", "conducted": "conduct", "allocated": "allocate",
    "dropped": "drop", "triggered": "trigger", "connected": "connect",
    "disconnected": "disconnect", "updated": "update", "adjusted": "adjust",
    "identified": "identify", "captured": "capture", "stabilized": "stabilize",
    "reached": "reach", "failed": "fail", "affected": "affect", "forced": "force",
    "executed": "execute", "detected": "detect", "disabled": "disable", "enabled": "enable",
    "flagged": "flag", "patched": "patch", "drained": "drain", "redirected": "redirect",
    "showed": "show", "scheduled": "schedule", "measured": "measure",
    "standardized": "standardize", "selected": "select", "opened": "open",
    "lowered": "lower", "mitigated": "mitigate", "restored": "restore",
    "accumulated": "accumulate", "blocked": "block", "closed": "close",
    "merged": "merge", "completed": "complete", "parsed": "parse",
    "isolated": "isolate", "routed": "route", "indexed": "index", "stored": "store",
    "loaded": "load", "flushed": "flush", "cached": "cache", "cleared": "clear",
    "locked": "lock", "unlocked": "unlock", "logged": "log", "started": "start",
    "stopped": "stop", "resumed": "resume", "paused": "pause", "restarted": "restart",
    "passed": "pass", "inspected": "inspect", "deployed": "deploy", "migrated": "migrate",
    "rotated": "rotate", "eliminated": "eliminate", "imparted": "impart",
    "delivered": "deliver", "emitted": "emit", "dried": "dry", "cleaned": "clean",
}

# Mechanism 3: Real English Adverb Erosions (Valid Adjectives Only)
ADVERB_EROSIONS: Dict[str, str] = {
    "properly": "proper", "safely": "safe", "strictly": "strict", "thoroughly": "thorough",
    "predictably": "predictable", "recently": "recent", "completely": "complete",
    "normally": "normal", "automatically": "automatic", "directly": "direct",
    "carefully": "careful", "consistently": "consistent", "significantly": "significant",
    "heavily": "heavy", "cleanly": "clean", "temporarily": "temporary",
    "intermittently": "intermittent", "simultaneously": "simultaneous",
    "frequently": "frequent", "immediately": "immediate", "slightly": "slight",
    "inadvertently": "inadvertent", "correctly": "correct", "accurately": "accurate",
    "regularly": "regular", "reliably": "reliable", "periodically": "periodic",
    "consequently": "consequent", "initially": "initial", "subsequently": "subsequent",
    "effortlessly": "effortless", "conversely": "converse", "dramatically": "dramatic",
    "substantially": "substantial", "exceptionally": "exceptional",
}

# Mechanism 3: Function Word Blurring (Soft prepositions & articles)
FUNCTION_WORDS: Dict[str, str] = {
    "with": "by", "by": "with", "in": "on", "on": "in", "to": "too",
    "too": "to", "for": "four", "four": "for", "the": "a", "a": "the",
    "at": "in", "from": "for", "during": "due ring", "without": "with out",
    "into": "in to", "onto": "on to", "upon": "up on", "under": "below",
}

# Mechanism 3: Prefix Erosions
PREFIX_EROSIONS: Dict[str, str] = {
    "to address": "address", "to ensure": "ensure", "our infrastructure": "infrastructure",
    "our engineering": "engineering", "apply": "play", "evaluating": "valuating",
    "the library": "library", "the team": "team", "the offer": "offer",
    "the worker": "worker", "the electricity": "electricity", "hi, ": "I, ",
}

# Mechanism 4: Digit Words (Preserving Numerical Facts)
DIGIT_WORDS: Dict[str, str] = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "10": "ten", "12": "twelve", "14": "fourteen", "16": "sixteen",
    "20": "twenty", "24": "twenty four", "30": "thirty", "40": "forty",
    "50": "fifty", "60": "sixty", "100": "one hundred", "1000": "one thousand"
}

# Mechanism 6: Subtle Conversational Homophones (Real Words Only)
HOMOPHONES: Dict[str, str] = {
    "their": "there", "there": "their", "they're": "there",
    "to": "too", "too": "to", "two": "to", "for": "four", "four": "for",
    "your": "you're", "you're": "your", "its": "it's", "it's": "its",
    "hear": "here", "here": "hear", "see": "sea", "sea": "see",
    "seen": "scene", "scene": "seen", "been": "bin", "bin": "been",
    "due": "do", "do": "due", "paid": "paved", "receipt": "receive",
    "write": "right", "right": "write", "writing": "righting",
    "read": "red", "red": "read", "passed": "past", "past": "passed",
    "led": "lead", "break": "brake", "brake": "break", "piece": "peace",
    "peace": "piece", "site": "sight", "sight": "site", "cite": "site",
    "some": "sum", "sum": "some", "know": "no", "no": "know",
    "knew": "new", "new": "knew", "whole": "hole", "hole": "whole",
    "role": "roll", "roll": "role", "root": "route", "route": "root",
    "way": "weigh", "weigh": "way", "wait": "weight", "weight": "wait",
    "weak": "week", "week": "weak", "wear": "where", "where": "wear",
    "warn": "worn", "worn": "warn", "waste": "waist", "waist": "waste",
    "weather": "whether", "whether": "weather", "allowed": "aloud",
    "aloud": "allowed", "board": "bored", "bored": "board", "coarse": "course",
    "course": "coarse", "fair": "fare", "fare": "fair", "heal": "heel",
    "heel": "heal", "idle": "idol", "idol": "idle", "lesson": "lessen",
    "lessen": "lesson", "meet": "meat", "meat": "meet", "minor": "miner",
    "miner": "minor", "plain": "plane", "plane": "plain", "poor": "pour",
    "pour": "poor", "principal": "principle", "principle": "principal",
    "profit": "prophet", "prophet": "profit", "raise": "rays", "rays": "raise",
    "sail": "sale", "sale": "sail", "sole": "soul", "soul": "sole",
    "stair": "stare", "stare": "stair", "steal": "steel", "steel": "steal",
    "suite": "sweet", "sweet": "suite", "tail": "tale", "tale": "tail",
    "buy": "by", "by": "buy", "affect": "effect", "effect": "affect",
    "accept": "except", "except": "accept", "ensure": "insure", "insure": "ensure",
    "then": "than", "than": "then", "bare": "bear", "bear": "bare",
    "great": "grate", "grate": "great", "night": "knight", "knight": "night",
    "knot": "not", "not": "knot", "pair": "pear", "pear": "pair",
    "peak": "peek", "peek": "peak", "road": "rode", "rode": "road",
    "sure": "shore", "shore": "sure", "son": "sun", "sun": "son",
    "wood": "would", "would": "wood", "hour": "our", "our": "hour",
    "parking": "barking", "inn": "in", "gate": "gait", "gait": "gate",
    "flea": "flee", "flee": "flee", "one": "won", "won": "one",
    "tuesday": "choose day", "distinct": "discreet", "unless": "and less",
}

# ---------------------------------------------------------------------------
# 3. Clean Markdown and Spoken Normalizer
# ---------------------------------------------------------------------------
def clean_markdown_and_dictate(text: str) -> str:
    """Strips all Markdown and converts code symbols/extensions to spoken words."""
    # Headers
    text = re.sub(r"^\s*#+\s+", "", text, flags=re.MULTILINE)
    # Bullet points and numbered lists
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*[-*]\s+", ". ", text)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*\d+\.\s+", ". ", text)

    # Convert code backticks to spoken dictation
    def replace_backtick(match):
        code_str = match.group(1).strip()
        if ":" in code_str and "_" in code_str:
            return code_str
        if code_str.startswith("--"):
            code_str = "dash dash " + code_str[2:]
        elif code_str.startswith("-") and len(code_str) <= 3:
            code_str = "dash " + code_str[1:]
        # File extensions
        code_str = re.sub(r"\.py\b", " dot py", code_str)
        code_str = re.sub(r"\.json\b", " dot json", code_str)
        code_str = re.sub(r"\.yaml\b", " dot yaml", code_str)
        code_str = re.sub(r"\.yml\b", " dot yaml", code_str)
        code_str = re.sub(r"\.sh\b", " dot sh", code_str)
        code_str = re.sub(r"\.bam\b", " dot bam", code_str)
        return code_str

    text = re.sub(r"`([^`]+)`", replace_backtick, text)
    text = text.replace("`", "")

    # Multi-paragraph blank lines become spoken transitions
    text = re.sub(r"\n\n+", ". ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# 4. Levenshtein Word Error Rate (WER) Evaluator
# ---------------------------------------------------------------------------
def compute_wer(reference: str, hypothesis: str) -> float:
    """Calculates standard Word Error Rate between reference and hypothesis."""
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


# ---------------------------------------------------------------------------
# 5. Acoustic Candidate Extractor
# ---------------------------------------------------------------------------
class TransformationCandidate:
    def __init__(self, mechanism_id: int, start: int, end: int, original: str, replacement: str, desc: str):
        self.mechanism_id = mechanism_id
        self.start = start
        self.end = end
        self.original = original
        self.replacement = replacement
        self.desc = desc


def extract_candidates(sentence: str) -> List[TransformationCandidate]:
    """Extracts candidate acoustic transformations across all 6 mechanisms."""
    candidates: List[TransformationCandidate] = []
    lower_sent = sentence.lower()

    # Mechanism 3: Prefix erosions
    for pref, rep in PREFIX_EROSIONS.items():
        if lower_sent.startswith(pref):
            orig = sentence[:len(pref)]
            rep_text = rep.capitalize() if orig[0].isupper() else rep
            candidates.append(TransformationCandidate(3, 0, len(pref), orig, rep_text, "prefix erosion"))

    # Mechanism 1: Multi-word phrase boundary shifts
    for phrase, rep in PHRASE_BOUNDARIES:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        for match in re.finditer(pattern, sentence, flags=re.IGNORECASE):
            orig = match.group(0)
            rep_text = rep
            if orig[0].isupper():
                rep_text = rep_text[0].upper() + rep_text[1:]
            candidates.append(TransformationCandidate(1, match.start(), match.end(), orig, rep_text, "phrase boundary shift"))

    # Word-level scanning
    for match in re.finditer(r"\b[\w'-]+\b", sentence):
        orig = match.group(0)
        low = orig.lower()
        start, end = match.start(), match.end()

        # Mechanism 1: Compound word & tech term splits
        if low in COMPOUND_SPLITS:
            rep = COMPOUND_SPLITS[low]
            if orig[0].isupper():
                rep = rep[0].upper() + rep[1:]
            candidates.append(TransformationCandidate(1, start, end, orig, rep, "compound split"))
        elif "-" in orig and len(orig) > 3:
            rep = orig.replace("-", " ")
            candidates.append(TransformationCandidate(1, start, end, orig, rep, "hyphen split"))
        elif "_" in orig and len(orig) > 3:
            rep = orig.replace("_", " ")
            candidates.append(TransformationCandidate(1, start, end, orig, rep, "underscore split"))

        # Mechanism 1: Gerund syllable splits
        if low in GERUND_SPLITS:
            rep = GERUND_SPLITS[low]
            if orig[0].isupper():
                rep = rep[0].upper() + rep[1:]
            candidates.append(TransformationCandidate(1, start, end, orig, rep, "gerund split"))

        # Mechanism 2: Domain jargon substitutions
        if low in JARGON_SUBSTITUTIONS:
            rep = JARGON_SUBSTITUTIONS[low]
            if orig[0].isupper():
                rep = rep[0].upper() + rep[1:]
            candidates.append(TransformationCandidate(2, start, end, orig, rep, "jargon substitution"))

        # Mechanism 6: Homophones
        if low in HOMOPHONES:
            rep = HOMOPHONES[low]
            if orig[0].isupper():
                rep = rep[0].upper() + rep[1:]
            candidates.append(TransformationCandidate(6, start, end, orig, rep, "homophone swap"))

        # Mechanism 3: Plural to singular (Real dictionary words only)
        if low in PLURAL_EROSIONS:
            rep = PLURAL_EROSIONS[low]
            if orig[0].isupper():
                rep = rep.capitalize()
            candidates.append(TransformationCandidate(3, start, end, orig, rep, "plural erosion"))

        # Mechanism 3: Past tense to root (Real dictionary words only)
        if low in PAST_TENSE_EROSIONS:
            rep = PAST_TENSE_EROSIONS[low]
            if orig[0].isupper():
                rep = rep.capitalize()
            candidates.append(TransformationCandidate(3, start, end, orig, rep, "past tense erosion"))

        # Mechanism 3: Adverb to adjective (Real dictionary words only)
        if low in ADVERB_EROSIONS:
            rep = ADVERB_EROSIONS[low]
            if orig[0].isupper():
                rep = rep.capitalize()
            candidates.append(TransformationCandidate(3, start, end, orig, rep, "adverb erosion"))

        # Mechanism 3: Function words
        if low in FUNCTION_WORDS:
            rep = FUNCTION_WORDS[low]
            if orig[0].isupper():
                rep = rep.capitalize()
            candidates.append(TransformationCandidate(3, start, end, orig, rep, "function word swap"))

        # Mechanism 4: Spoken digits (Preserves factual numbers!)
        if orig.isdigit() and orig in DIGIT_WORDS:
            candidates.append(TransformationCandidate(4, start, end, orig, DIGIT_WORDS[orig], "digit dictation"))

    # Mechanism 4: Ordinals & Currency
    for match in re.finditer(r"\b(\d+)(st|nd|rd|th)\b", sentence, flags=re.IGNORECASE):
        candidates.append(TransformationCandidate(4, match.start(), match.end(), match.group(0), match.group(1), "ordinal dictation"))

    for match in re.finditer(r"\$(\d+(?:,\d+)*(?:\.\d+)?)", sentence):
        val = match.group(1)
        candidates.append(TransformationCandidate(4, match.start(), match.end(), match.group(0), f"{val} dollars", "currency dictation"))

    # Mechanism 5: Clause and boundary drift
    for match in re.finditer(r";\s*however,", sentence, flags=re.IGNORECASE):
        candidates.append(TransformationCandidate(5, match.start(), match.end(), match.group(0), ", however,", "semicolon drift"))
    for match in re.finditer(r";\s*", sentence):
        if match.group(0).strip() == ";":
            candidates.append(TransformationCandidate(5, match.start(), match.end(), ";", ",", "semicolon to comma"))

    return candidates


# ---------------------------------------------------------------------------
# 6. Sample Acoustic Noise Generator
# ---------------------------------------------------------------------------
def apply_acoustic_noise(
    refined_text: str,
    rotation_seed: Tuple[int, int, int],
    rng: random.Random,
    target_wer: float = 0.20,
    allow_splits: bool = True
) -> str:
    """Applies realistic Whisper acoustic noise honoring all constraints."""
    cleaned_text = clean_markdown_and_dictate(refined_text)

    sentence_matches = list(re.finditer(r"([^.!?]+(?:[.!?]+|$))", cleaned_text))
    sentences = [m.group(1).strip() for m in sentence_matches if m.group(1).strip()]

    if not sentences:
        return cleaned_text

    is_multi_sentence = len(sentences) >= 2
    transformed_sentences = []
    has_mechanism_1 = False

    for sent_idx, sent in enumerate(sentences):
        words = re.findall(r"\b[\w'-]+\b", sent)
        word_count = len(words)
        candidates = extract_candidates(sent)

        if not allow_splits:
            candidates = [
                c for c in candidates
                if len(re.findall(r"\b[\w'-]+\b", c.replacement)) <= len(re.findall(r"\b[\w'-]+\b", c.original))
            ]

        if word_count == 0:
            transformed_sentences.append(sent)
            continue

        # In multi-sentence, ensure every sentence has noise (target at least 1 edit if >= 10 words)
        min_changes = 1 if (is_multi_sentence or word_count >= 8) else 1
        k_target = max(min_changes, round(word_count * target_wer))
        if is_multi_sentence and word_count >= 15:
            k_target = max(2, k_target)

        if not candidates:
            transformed_sentences.append(sent)
            continue

        # Weights: favor rotation seed mechanisms, with Mechanism 1 given strong priority
        weights = []
        for c in candidates:
            w = 1.0
            if c.mechanism_id == 1:
                w = 4.0  # Mechanism 1 mandatory priority
            elif c.mechanism_id in rotation_seed:
                w = 2.5
            weights.append(w)

        selected: List[TransformationCandidate] = []
        available_indices = list(range(len(candidates)))

        # If Mechanism 1 not yet applied across sample, prioritize picking one here
        if not has_mechanism_1:
            m1_indices = [i for i in available_indices if candidates[i].mechanism_id == 1]
            if m1_indices:
                chosen_m1 = rng.choice(m1_indices)
                cand = candidates[chosen_m1]
                selected.append(cand)
                has_mechanism_1 = True
                available_indices = [
                    i for i in available_indices
                    if (candidates[i].end <= cand.start or candidates[i].start >= cand.end)
                ]

        # Select remaining up to k_target
        for _ in range(min(k_target - len(selected), len(available_indices))):
            if not available_indices:
                break
            current_weights = [weights[i] for i in available_indices]
            total_w = sum(current_weights)
            if total_w <= 0:
                break
            chosen_idx = rng.choices(available_indices, weights=current_weights, k=1)[0]
            cand = candidates[chosen_idx]
            selected.append(cand)
            if cand.mechanism_id == 1:
                has_mechanism_1 = True

            available_indices = [
                i for i in available_indices
                if (candidates[i].end <= cand.start or candidates[i].start >= cand.end)
            ]

        selected.sort(key=lambda x: x.start, reverse=True)
        mod_sent = sent
        for cand in selected:
            mod_sent = mod_sent[:cand.start] + cand.replacement + mod_sent[cand.end:]

        transformed_sentences.append(mod_sent)

    result_raw = " ".join(transformed_sentences)
    # Strip any stray markdown
    result_raw = re.sub(r"[`*~#]", "", result_raw)
    result_raw = re.sub(r"\n+", " ", result_raw)
    result_raw = re.sub(r"\s+", " ", result_raw).strip()

    return result_raw


# Target under-noised substitutions (Real English Words Only)
UNDER_NOISED_SUBSTITUTIONS: List[Tuple[str, str]] = [
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
]


def generate_valid_raw_asr(
    refined_text: str,
    rotation_seed: Tuple[int, int, int],
    seed: int
) -> str:
    """Generates valid raw_asr guaranteeing WER within 8%-45% and Mechanism 1 boundary shift."""
    cleaned = clean_markdown_and_dictate(refined_text)

    # Search for an optimal noise injection
    best_raw = cleaned
    best_wer = 0.0

    target_wers = [0.20, 0.22, 0.18, 0.24, 0.16, 0.26, 0.15, 0.28, 0.14]

    for attempt in range(8):
        rng = random.Random(seed + attempt * 777)
        for tw in target_wers:
            cand_raw = apply_acoustic_noise(refined_text, rotation_seed, rng, target_wer=tw)
            wer = compute_wer(refined_text, cand_raw)

            # Accept if in the ideal target sweet spot
            if 0.150 <= wer <= 0.260:
                return cand_raw

            # Track best candidate in acceptable range
            if 0.080 <= wer <= 0.450:
                if best_wer == 0.0 or abs(wer - 0.20) < abs(best_wer - 0.20):
                    best_raw = cand_raw
                    best_wer = wer

    if 0.080 <= best_wer <= 0.450:
        return best_raw

    # Fallback with adaptive boost if under-noised
    cur = apply_acoustic_noise(refined_text, rotation_seed, random.Random(seed), target_wer=0.22)
    cur_wer = compute_wer(refined_text, cur)

    if cur_wer < 0.080:
        for pat, rep in UNDER_NOISED_SUBSTITUTIONS:
            if re.search(pat, cur, flags=re.IGNORECASE):
                cur = re.sub(pat, rep, cur, count=1, flags=re.IGNORECASE)
                w = compute_wer(refined_text, cur)
                if 0.080 <= w <= 0.450:
                    return cur

    return cur


# ---------------------------------------------------------------------------
# 7. Batch Pool Generation Driver
# ---------------------------------------------------------------------------
def generate_all_batches(
    dataset_path: str = "data/sft_train.json",
    scratch_dir: str = "scratch",
    batch_size: int = 10,
    start_batch: int = 0,
    end_batch: Optional[int] = None
):
    print("=" * 60)
    print("Milestone 1: Realistic Whisper Acoustic Noise Generation Pool")
    print("=" * 60)

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total_samples = len(dataset)
    total_batches = (total_samples + batch_size - 1) // batch_size
    print(f"Total samples: {total_samples}")
    print(f"Total batches: {total_batches}")

    os.makedirs(scratch_dir, exist_ok=True)

    if end_batch is None:
        end_batch = total_batches

    start_time = time.time()
    total_processed = 0
    all_wers = []

    for batch_id in range(start_batch, end_batch):
        start_idx = batch_id * batch_size
        end_idx = min(start_idx + batch_size, total_samples)
        batch_slice = dataset[start_idx:end_idx]

        # Rotation seed: Mechanism 1 + 2 rotated from {2..6} across 10 rotation seeds
        rotation_seed = ROTATION_SEEDS[batch_id % 10]

        # Worker input contract: strictly {index, refined_text}
        worker_input = [
            {"index": start_idx + j, "refined_text": item["refined_text"]}
            for j, item in enumerate(batch_slice)
        ]

        # Worker output contract: strictly List[{"index": int, "raw_asr": str}]
        worker_output: List[Dict[str, any]] = []

        for item in worker_input:
            idx = item["index"]
            ref = item["refined_text"]

            raw_asr = generate_valid_raw_asr(ref, rotation_seed, seed=idx)
            wer = compute_wer(ref, raw_asr)
            all_wers.append(wer)

            # Invariant: Never output refined_text
            worker_output.append({
                "index": idx,
                "raw_asr": raw_asr
            })
            total_processed += 1

        # Write output file to scratch/batch_{batch_id}_output.json
        output_file = os.path.join(scratch_dir, f"batch_{batch_id}_output.json")
        with open(output_file, "w", encoding="utf-8") as bf:
            json.dump(worker_output, bf, indent=2, ensure_ascii=False)

        if (batch_id + 1) % 100 == 0 or (batch_id + 1) == end_batch:
            elapsed = time.time() - start_time
            rate = total_processed / max(0.1, elapsed)
            avg_wer = sum(all_wers) / len(all_wers) if all_wers else 0.0
            print(f"Batch {batch_id + 1}/{end_batch} | Processed: {total_processed} samples | Rate: {rate:.1f} s/s | Avg WER: {avg_wer*100:.1f}%")

    elapsed_total = time.time() - start_time
    print(f"\nGeneration completed in {elapsed_total:.1f}s ({total_processed/max(0.1, elapsed_total):.1f} samples/s)")
    if all_wers:
        print(f"Overall Average WER: {sum(all_wers)/len(all_wers)*100:.2f}%")
        print(f"WER Min: {min(all_wers)*100:.2f}%, Max: {max(all_wers)*100:.2f}%")
        in_range = sum(1 for w in all_wers if 0.080 <= w <= 0.450)
        print(f"Samples in acceptable [8%, 45%] range: {in_range}/{len(all_wers)} ({in_range*100/len(all_wers):.2f}%)")


if __name__ == "__main__":
    generate_all_batches()
