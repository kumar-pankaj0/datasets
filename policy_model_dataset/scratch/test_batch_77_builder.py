import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)
eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
eval_refs = {e["refined_text"].strip() for e in eval_data}

samples = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 6-8. Rationale with "by <action>". No decimals, no dotted filenames.
    # =========================================================================

    # Sample 1: Multi-Agent Consensus Arbiter
    {
        "raw_asr": "instruct claude two arbitrat conflicting agent proposals buy scoring architectural trade offs across consensus rounds",
        "refined_text": "Instruct Claude to arbitrate conflicting agent proposals by scoring architectural trade-offs across consensus rounds."
    },

    # Sample 2: Dynamic Few-Shot Exemplar Selection
    {
        "raw_asr": "direct aid er two configur dynamic few shot exemplar selection buy indexing thirty two semantic query embeddings",
        "refined_text": "Direct Aider to configure dynamic few-shot exemplar selection by indexing 32 semantic query embeddings."
    },

    # Sample 3: ReAct Step Limit Termination
    {
        "raw_asr": "tell wind surf two terminat stalled reasoning loops buy enforcing a maximum boundary of fifteen execution steps",
        "refined_text": "Tell Windsurf to terminate stalled reasoning loops by enforcing a maximum boundary of 15 execution steps."
    },

    # Sample 4: Tool Schema Validation
    {
        "raw_asr": "prompt co pilot two validat tool argument schemas buy checking required parameter keys across sixteen registered tools",
        "refined_text": "Prompt Copilot to validate tool argument schemas by checking required parameter keys across 16 registered tools."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # =========================================================================

    # Sample 5: Semantic Intent Dispatching
    {
        "raw_asr": "basically prompt cur sor two refact our semantic intent classifier inside intent underscore router dot py buy mapping incoming user prompts two target agent workflows wait assign queries two twelve specialized skill handlers instead um right four pie test assertions validating embedding cosine distance thresholds",
        "refined_text": "Prompt Cursor to refactor our semantic intent classifier inside intent_router.py by mapping incoming user prompts to target agent workflows, assigning queries to 12 specialized skill handlers instead.\n\nWrite 4 pytest assertions validating embedding cosine distance thresholds."
    },

    # Sample 6: Grammar-Constrained JSON Sampling
    {
        "raw_asr": "ask aid er two configur grammar constrained decoding inside structured underscore sampler dot py buy restricting token generation logits two match our target json schema wait enforce valid enum values buy masking disallowed tokens instead um generat five pie test unit tests asserting zero decoding exceptions across sample model outputs",
        "refined_text": "Ask Aider to configure grammar-constrained decoding inside structured_sampler.py by restricting token generation logits to match our target JSON schema, enforcing valid enum values by masking disallowed tokens instead.\n\nGenerate 5 pytest unit tests asserting zero decoding exceptions across sample model outputs."
    },

    # Sample 7: Agent Workspace Snapshot Checkpointing
    {
        "raw_asr": "direct wind surf two refact workspace serialization inside checkpoint underscore manager dot py buy capturing active file diffs and tool execution logs wait persist agent memory snapshots into sqlite storage instead um right six unit tests verifying state restoration after unexpected process termination",
        "refined_text": "Direct Windsurf to refactor workspace serialization inside checkpoint_manager.py by capturing active file diffs and tool execution logs, persisting agent memory snapshots into SQLite storage instead.\n\nWrite 6 unit tests verifying state restoration after unexpected process termination."
    },

    # Sample 8: Hallucination Citation Verification
    {
        "raw_asr": "prompt co pilot two build a citation verification filter inside citation underscore verifier dot py buy matching extracted answer claims against retrieved source document spans wait discard ungrounded factual assertions buy computing word overlap scores instead um right three pie test fixtures asserting claim attribution precision across sample responses",
        "refined_text": "Prompt Copilot to build a citation verification filter inside citation_verifier.py by matching extracted answer claims against retrieved source document spans, discarding ungrounded factual assertions by computing word overlap scores instead.\n\nWrite 3 pytest fixtures asserting claim attribution precision across sample responses."
    },

    # Sample 9: LLM Provider Fallback Circuit Breaker
    {
        "raw_asr": "basically instruct cur sor two configur an upstream provider fallback inside gateway underscore failover dot py buy intercepting rate limit status four two nine errors from primary models wait redirect request payloads towards secondary v l l m endpoints instead um right five pie test unit tests verifying failover recovery within two hundred milliseconds",
        "refined_text": "Instruct Cursor to configure an upstream provider fallback inside gateway_failover.py by intercepting rate limit status 429 errors from primary models, redirecting request payloads towards secondary vLLM endpoints instead.\n\nWrite 5 pytest unit tests verifying failover recovery within 200 milliseconds."
    },

    # Sample 10: Multi-Modal Vision Payload Optimization
    {
        "raw_asr": "ask aid er two optimiz multimodal image payload preparation inside image underscore preprocessor dot py buy downscaling high resolution screenshots two maximum dimensions of one zero two four pixels wait compress image tiles buy applying jpeg encoding instead um generat four pie test test cases verifying token calculation across sixteen sample screenshots",
        "refined_text": "Ask Aider to optimize multimodal image payload preparation inside image_preprocessor.py by downscaling high-resolution screenshots to maximum dimensions of 1024 pixels, compressing image tiles by applying JPEG encoding instead.\n\nGenerate 4 pytest test cases verifying token calculation across 16 sample screenshots."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # =========================================================================

    # Sample 11: Multi-Agent Consensus Arbiter & Reflection Loop
    {
        "raw_asr": "basically ask cur sor two refact our multi agent consensus engine inside debate underscore arbitrator dot py buy arbitrating conflicting proposals between planner and coder agents our multi agent code synthesis pipeline experiences deadlock when planner and generator models disagree on interface contracts which leads two twenty redundant reasoning iterations and context exhaustion um instruct cur sor two implement a tournament style reflection loop buy evaluating proposed code diffs against architectural rules and calculating compliance scores across three arbitration rounds wait select the proposal with the highest aggregate score buy breaking ties with execution token efficiency instead okay so tell cur sor two benchmark arbitration stability buy simulating twelve synthetic agent debates and right six pie test unit tests asserting that deadlock conditions resolve within four arbitration rounds",
        "refined_text": "Ask Cursor to refactor our multi-agent consensus engine inside debate_arbitrator.py by arbitrating conflicting proposals between planner and coder agents. Our multi-agent code synthesis pipeline experiences deadlock when planner and generator models disagree on interface contracts, which leads to 20 redundant reasoning iterations and context exhaustion.\n\nInstruct Cursor to implement a tournament-style reflection loop by evaluating proposed code diffs against architectural rules and calculating compliance scores across 3 arbitration rounds, selecting the proposal with the highest aggregate score by breaking ties with execution token efficiency instead.\n\nTell Cursor to benchmark arbitration stability by simulating 12 synthetic agent debates, and write 6 pytest unit tests asserting that deadlock conditions resolve within 4 arbitration rounds."
    },

    # Sample 12: Dynamic Vector-Based Exemplar Selection for In-Context Learning
    {
        "raw_asr": "instruct aid er two refact our dynamic prompt assembler inside exemplar underscore selector dot py buy replacing static few shot demonstrations with vector similarity retrieval our agent system prompt currently embeds twelve fixed coding examples which consumes four zero nine six tokens on every inference call regardless of whether the incoming user task relates two web scraping or database migrations um ask aid er two implement an embedding indexed exemplar store buy selecting the top three most relevant demonstrations based on cosine similarity against the user query vector wait limit candidate demonstrations buy restricting total exemplar token consumption two one zero two four tokens instead okay so tell aid er two evaluate retrieval precision buy processing forty test queries across eight distinct programming domains and right five pie test unit tests verifying that selected examples match expected domain labels",
        "refined_text": "Instruct Aider to refactor our dynamic prompt assembler inside exemplar_selector.py by replacing static few-shot demonstrations with vector similarity retrieval. Our agent system prompt currently embeds 12 fixed coding examples, which consumes 4096 tokens on every inference call regardless of whether the incoming user task relates to web scraping or database migrations.\n\nAsk Aider to implement an embedding-indexed exemplar store by selecting the top 3 most relevant demonstrations based on cosine similarity against the user query vector, limiting candidate demonstrations by restricting total exemplar token consumption to 1024 tokens instead.\n\nTell Aider to evaluate retrieval precision by processing 40 test queries across 8 distinct programming domains, and write 5 pytest unit tests verifying that selected examples match expected domain labels."
    },

    # Sample 13: Secure Tool Sandbox Runner with Docker Process Isolation
    {
        "raw_asr": "tell wind surf two refact our tool execution environment inside sandbox underscore runner dot py buy isolating autonomous bash and python script execution within ephemeral docker containers our coding agent currently spawns subprocess commands directly on the host development machine which exposes environment secrets and risks runaway processes during recursive file search operations um instruct wind surf two implement containerized command execution buy mounting temporary workspaces with read only volume permissions and restricting network egress towards localhost ports wait terminate long running commands buy enforcing a hard timeout of thirty seconds on container processes instead okay so ask wind surf two test sandbox security buy simulating sixteen privilege escalation attempts and right four pie test assertions verifying that restricted environment variables remain inaccessible from inside container sandboxes",
        "refined_text": "Tell Windsurf to refactor our tool execution environment inside sandbox_runner.py by isolating autonomous Bash and Python script execution within ephemeral Docker containers. Our coding agent currently spawns subprocess commands directly on the host development machine, which exposes environment secrets and risks runaway processes during recursive file search operations.\n\nInstruct Windsurf to implement containerized command execution by mounting temporary workspaces with read-only volume permissions and restricting network egress towards localhost ports, terminating long-running commands by enforcing a hard timeout of 30 seconds on container processes instead.\n\nAsk Windsurf to test sandbox security by simulating 16 privilege escalation attempts, and write 4 pytest assertions verifying that restricted environment variables remain inaccessible from inside container sandboxes."
    },

    # Sample 14: Prompt Token Budgeting and KV Cache Retention Policy
    {
        "raw_asr": "basically prompt co pilot two refact our inference request compiler inside kv underscore cache underscore budgeter dot py buy aligning static system prompts four prefix cache retention on v l l m clusters our agent gateway dynamically prepends randomized session identifiers and variable tool definitions ahead of the system instructions which invalidates the k v cache and increases first token latency two sixteen hundred milliseconds um tell co pilot two structure prompt messages buy freezing the system prompt and static tool declarations at the prefix while appending dynamic conversational context two the payload tail wait optimize cache hit rates buy setting explicit cache checkpoint markers after static instructions instead okay so instruct co pilot two benchmark inference latency buy measuring first token dispatch across thirty concurrent agent sessions and right five pie test unit tests asserting that cached prompt prefixes hit eighty five percent reuse rates",
        "refined_text": "Prompt Copilot to refactor our inference request compiler inside kv_cache_budgeter.py by aligning static system prompts for prefix cache retention on vLLM clusters. Our agent gateway dynamically prepends randomized session identifiers and variable tool definitions ahead of the system instructions, which invalidates the KV cache and increases first token latency to 1600 milliseconds.\n\nTell Copilot to structure prompt messages by freezing the system prompt and static tool declarations at the prefix while appending dynamic conversational context to the payload tail, optimizing cache hit rates by setting explicit cache checkpoint markers after static instructions instead.\n\nInstruct Copilot to benchmark inference latency by measuring first token dispatch across 30 concurrent agent sessions, and write 5 pytest unit tests asserting that cached prompt prefixes hit 85% reuse rates."
    },

    # Sample 15: Agent Reflection and Backtracking on Failed Test Executions
    {
        "raw_asr": "ask cur sor two refact our autonomous code modification loop inside reflection underscore engine dot py buy implementing a backtrack state stack four failed unit test runs our coding agent currently overwrites working code files without maintaining checkpoints which corrupts git working trees when generated patches fail continuous integration tests um instruct cur sor two implement snapshot rollbacks buy recording file diffs in a stack before applying model edits and restoring previous file states whenever unit tests fail three consecutive attempts wait trigger human intervention buy raising an unrecoverable failure signal if the agent exhausts four backtrack cycles instead okay so tell cur sor two test recovery resilience buy simulating twenty four broken test fixtures and right six pie test unit tests checking that file systems revert cleanly two uncorrupted states",
        "refined_text": "Ask Cursor to refactor our autonomous code modification loop inside reflection_engine.py by implementing a backtrack state stack for failed unit test runs. Our coding agent currently overwrites working code files without maintaining checkpoints, which corrupts git working trees when generated patches fail continuous integration tests.\n\nInstruct Cursor to implement snapshot rollbacks by recording file diffs in a stack before applying model edits and restoring previous file states whenever unit tests fail 3 consecutive attempts, triggering human intervention by raising an unrecoverable failure signal if the agent exhausts 4 backtrack cycles instead.\n\nTell Cursor to test recovery resilience by simulating 24 broken test fixtures, and write 6 pytest unit tests checking that file systems revert cleanly to uncorrupted states."
    },

    # Sample 16: Semantic Routing and Dynamic Tool Pruning
    {
        "raw_asr": "instruct aid er two refact our tool calling preparation pipeline inside tool underscore pruner dot py buy dynamically selecting relevant tools based on user prompt semantics our platform registers eighty distinct m c p tools which exceeds context token budgets and confuses language model function routers when all tool schemas load into every request um ask aid er two implement an embedding based tool filter buy calculating cosine similarity between user queries and tool description vectors wait select only the top eight candidate tool schemas four each turn buy pruning irrelevant schemas from the request payload instead okay so tell aid er two benchmark routing accuracy buy testing sixty natural language user commands and right four pie test unit test cases verifying that required tools appear in selected schema arrays",
        "refined_text": "Instruct Aider to refactor our tool calling preparation pipeline inside tool_pruner.py by dynamically selecting relevant tools based on user prompt semantics. Our platform registers 80 distinct MCP tools, which exceeds context token budgets and confuses language model function routers when all tool schemas load into every request.\n\nAsk Aider to implement an embedding-based tool filter by calculating cosine similarity between user queries and tool description vectors, selecting only the top 8 candidate tool schemas for each turn by pruning irrelevant schemas from the request payload instead.\n\nTell Aider to benchmark routing accuracy by testing 60 natural language user commands, and write 4 pytest unit test cases verifying that required tools appear in selected schema arrays."
    },

    # Sample 17: Agent Web Interaction and DOM Tree Distillation Pipeline
    {
        "raw_asr": "tell wind surf two refact our web browsing extractor inside dom underscore distiller dot py buy distilling raw h t m l trees into compact semantic accessibility trees our autonomous browsing agent feeds raw page source code directly into language model context windows which consumes thirty two thousand tokens and exhausts context limits on single page navigations um instruct wind surf two implement an accessibility tree filter buy removing hidden elements script tags and decorative stylesheets while preserving clickable buttons input fields and heading nodes wait limit distilled tree size buy restricting element hierarchy depth two six levels instead okay so ask wind surf two benchmark context reduction buy processing twenty five complex web pages and right five pie test assertions verifying that navigation links retain functional xpath selectors",
        "refined_text": "Tell Windsurf to refactor our web browsing extractor inside dom_distiller.py by distilling raw HTML trees into compact semantic accessibility trees. Our autonomous browsing agent feeds raw page source code directly into language model context windows, which consumes 32000 tokens and exhausts context limits on single-page navigations.\n\nInstruct Windsurf to implement an accessibility tree filter by removing hidden elements, script tags, and decorative stylesheets while preserving clickable buttons, input fields, and heading nodes, limiting distilled tree size by restricting element hierarchy depth to 6 levels instead.\n\nAsk Windsurf to benchmark context reduction by processing 25 complex web pages, and write 5 pytest assertions verifying that navigation links retain functional XPath selectors."
    },

    # Sample 18: Function Calling Schema Repair and JSON Patch State Machine
    {
        "raw_asr": "prompt co pilot two refact our function call argument decoder inside patch underscore applicator dot py buy handling partial json payloads and malformed parameter keys our autonomous execution agent generates malformed json dictionaries when emitting complex configuration updates which produces syntax errors and halts multi turn agent workflows um tell co pilot two implement a resilient json parser buy repairing unclosed braces and converting emitted parameter changes into r f c six nine zero two json patch operations wait validate target state transitions buy checking patch paths against registered pydantic models before applying modifications instead okay so instruct co pilot two test patch reliability buy processing thirty two corrupted model response snippets and right six pie test unit tests verifying that valid state mutations apply cleanly without data loss",
        "refined_text": "Prompt Copilot to refactor our function call argument decoder inside patch_applicator.py by handling partial JSON payloads and malformed parameter keys. Our autonomous execution agent generates malformed JSON dictionaries when emitting complex configuration updates, which produces syntax errors and halts multi-turn agent workflows.\n\nTell Copilot to implement a resilient JSON parser by repairing unclosed braces and converting emitted parameter changes into RFC 6902 JSON patch operations, validating target state transitions by checking patch paths against registered Pydantic models before applying modifications instead.\n\nInstruct Copilot to test patch reliability by processing 32 corrupted model response snippets, and write 6 pytest unit tests verifying that valid state mutations apply cleanly without data loss."
    },

    # Sample 19: LLM Gateway Circuit Breaker and Provider Fallback Orchestrator
    {
        "raw_asr": "basically ask cur sor two refact our inference routing gateway inside gateway underscore circuit underscore breaker dot py buy handling upstream rate limits and provider outages our agent backend sends all language model requests two a single commercial a p i endpoint which causes total workflow stall when the provider returns status five zero three service unavailable errors um instruct cur sor two implement a sliding window circuit breaker buy tracking failure rates across one hundred requests and tripping open when errors exceed twenty percent threshold wait route overflow traffic towards local v l l m fallback clusters buy transforming prompt payloads two match open source model formats instead okay so tell cur sor two test gateway resilience buy simulating forty intermittent network drops and right five pie test unit tests verifying seamless failover transitions within three hundred milliseconds",
        "refined_text": "Ask Cursor to refactor our inference routing gateway inside gateway_circuit_breaker.py by handling upstream rate limits and provider outages. Our agent backend sends all language model requests to a single commercial API endpoint, which causes total workflow stall when the provider returns status 503 service unavailable errors.\n\nInstruct Cursor to implement a sliding window circuit breaker by tracking failure rates across 100 requests and tripping open when errors exceed 20% threshold, routing overflow traffic towards local vLLM fallback clusters by transforming prompt payloads to match open-source model formats instead.\n\nTell Cursor to test gateway resilience by simulating 40 intermittent network drops, and write 5 pytest unit tests verifying seamless failover transitions within 300 milliseconds."
    },

    # Sample 20: Long-Term Knowledge Graph Episodic Memory Extractor
    {
        "raw_asr": "instruct aid er two refact our long term agent memory store inside graph underscore memory underscore extractor dot py buy extracting entity relationships from completed conversation sessions our autonomous agent currently retains unindexed chat transcripts in flat storage which makes historical architectural decisions inaccessible after fourteen days um ask aid er two implement a knowledge graph extraction pipeline buy identifying code entities library dependencies and design choices from conversation logs wait persist extracted relationships into a graph database buy linking agent decisions two specific source files instead okay so tell aid er two validate knowledge graph extraction buy analyzing eighteen archived development sessions and right four pie test unit tests asserting that graph queries return accurate dependency paths",
        "refined_text": "Instruct Aider to refactor our long-term agent memory store inside graph_memory_extractor.py by extracting entity relationships from completed conversation sessions. Our autonomous agent currently retains unindexed chat transcripts in flat storage, which makes historical architectural decisions inaccessible after 14 days.\n\nAsk Aider to implement a knowledge graph extraction pipeline by identifying code entities, library dependencies, and design choices from conversation logs, persisting extracted relationships into a graph database by linking agent decisions to specific source files instead.\n\nTell Aider to validate knowledge graph extraction by analyzing 18 archived development sessions, and write 4 pytest unit tests asserting that graph queries return accurate dependency paths."
    }
]

print(f"Total candidate samples: {len(samples)}")

# Run checks
all_passed = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, s in enumerate(samples, 1):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    if words < 25:
        tier_counts["short"] += 1
        tier_label = "Short"
    elif words < 90:
        tier_counts["medium"] += 1
        tier_label = "Medium"
    else:
        tier_counts["long"] += 1
        tier_label = "Long"

    # Leakage check against sft_eval.json
    if raw.lower() in eval_raws:
        print(f"Sample {i} ERROR: raw_asr leaked into eval set!")
        all_passed = False
    if ref in eval_refs:
        print(f"Sample {i} ERROR: refined_text leaked into eval set!")
        all_passed = False

    # validate_pair
    ok, reason = validate_pair(s)
    if not ok:
        print(f"Sample {i} ({tier_label}, {words} words) FAILED validate_pair: {reason}")
        all_passed = False
    else:
        # cleaner clean_sample
        cleaned, status = clean_sample(raw, ref)
        if status != "kept":
            print(f"Sample {i} ({tier_label}, {words} words) FAILED clean_sample: {status}")
            all_passed = False
        else:
            print(f"Sample {i:02d} [{tier_label:6s} | {words:3d} words]: PASS")

# validate_batch
batch_ok, batch_reason, batch_counts = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: ok={batch_ok}, reason='{batch_reason}', counts={batch_counts}")

if all_passed and batch_ok:
    print("\nALL 20 SAMPLES PASSED 100% VALIDATION!")
    out_file = Path("scratch/subagent_batch_77.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"Saved verified batch to {out_file} (size: {out_file.stat().st_size} bytes)")
else:
    print("\nFAILURES DETECTED! PLEASE REVIEW AND FIX.")
    sys.exit(1)
