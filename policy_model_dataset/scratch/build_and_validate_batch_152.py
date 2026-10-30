import json
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Active noise layers >= 3. Rationale with "by <action>". No dotted filenames.
    # =========================================================================

    # Sample 1: Agent scratchpad memory buffer allocation
    {
        "raw_asr": "um allocat scratchpad underscore buffer slots buy spawning four concurrent a sink worker threads",
        "refined_text": "Allocate scratchpad_buffer slots by spawning 4 concurrent async worker threads."
    },

    # Sample 2: Agent tool gateway session timeout termination
    {
        "raw_asr": "basically terminat hanging tool underscore gateway sessions buy setting two second timeout limits four r p c handlers",
        "refined_text": "Terminate hanging tool_gateway sessions by setting 2 second timeout limits for RPC handlers."
    },

    # Sample 3: Vector reranker partition migration to CPU RAM
    {
        "raw_asr": "uh migrat vector underscore reranker partitions buy transferring eight index segments two host c p u ram",
        "refined_text": "Migrate vector_reranker partitions by transferring 8 index segments to host CPU RAM."
    },

    # Sample 4: Episodic trajectory table initialization in Postgres
    {
        "raw_asr": "um initializ episodic underscore trajectory tables buy creating six indexed partitions inside post gres",
        "refined_text": "Initialize episodic_trajectory tables by creating 6 indexed partitions inside Postgres."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Active noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 5: Metaprompt compiler with Jinja2 system prompt templates
    {
        "raw_asr": "uh configur system prompt compilation passes inside prompt underscore compiler dot py buy validating dynamic variables across sixteen template schemas wait twenty four bootstrap prompts instead buy enforcing strict schema constraints you know prune dangling reference tags buy analyzing template tokens across a sink i o test routines right three unit tests verifying prompt syntax validation",
        "refined_text": "Configure system prompt compilation passes inside prompt_compiler.py by validating dynamic variables across 16 template schemas, using 24 bootstrap prompts instead by enforcing strict schema constraints.\n\nPrune dangling reference tags by analyzing template tokens across asyncio test routines. Write 3 unit tests verifying prompt syntax validation."
    },

    # Sample 6: Constrained JSON grammar decoding with regex state transitions
    {
        "raw_asr": "um initializ constrained tool payload decoding inside schema underscore decoder dot py buy compiling grammar transition tables across eighteen regex states wait thirty six state transitions instead buy enforcing deterministic json syntax rules basically mask invalid token probabilities buy evaluating vocabulary logits across host c p u threads right four unit tests confirming parser error handling",
        "refined_text": "Initialize constrained tool payload decoding inside schema_decoder.py by compiling grammar transition tables across 18 regex states, using 36 state transitions instead by enforcing deterministic JSON syntax rules.\n\nMask invalid token probabilities by evaluating vocabulary logits across host CPU threads. Write 4 unit tests confirming parser error handling."
    },

    # Sample 7: Agent working memory sliding window compaction and summary extraction
    {
        "raw_asr": "basically allocat conversation history buffers inside context underscore compactor dot py buy trimming stale chat messages across eight dialogue turns wait fourteen conversational turns instead buy preserving core reasoning steps uh condens historical message exchanges buy generating semantic summary tokens across post gres vector stores right three unit tests verifying buffer retention bounds",
        "refined_text": "Allocate conversation history buffers inside context_compactor.py by trimming stale chat messages across 8 dialogue turns, using 14 conversational turns instead by preserving core reasoning steps.\n\nCondense historical message exchanges by generating semantic summary tokens across Postgres vector stores. Write 3 unit tests verifying buffer retention bounds."
    },

    # Sample 8: Multi-agent asynchronous RPC tool dispatcher with backoff retry
    {
        "raw_asr": "um operat distributed agent tool invocations inside dispatcher underscore service dot py buy routing parameter payloads across six worker coroutines wait twelve remote r p c endpoints instead buy balancing execution load you know mitigat failed tool executions buy running a sink i o retry loops across exponential backoff intervals right four unit tests validating r p c fault tolerance",
        "refined_text": "Operate distributed agent tool invocations inside dispatcher_service.py by routing parameter payloads across 6 worker coroutines, targeting 12 remote RPC endpoints instead by balancing execution load.\n\nMitigate failed tool executions by running asyncio retry loops across exponential backoff intervals. Write 4 unit tests validating RPC fault tolerance."
    },

    # Sample 9: Prefix caching and attention key-value cache compression
    {
        "raw_asr": "uh recalculat dynamic attention key value caches inside kv underscore cache dot py buy compressing token representations across ten attention layers wait sixteen attention heads instead buy discarding redundant context activations basically pin static system prompt embeddings buy locking shared prefix buffers across host c p u memory pages right five unit tests measuring prefix lookup speedups",
        "refined_text": "Recalculate dynamic attention key-value caches inside kv_cache.py by compressing token representations across 10 attention layers, using 16 attention heads instead by discarding redundant context activations.\n\nPin static system prompt embeddings by locking shared prefix buffers across host CPU memory pages. Write 5 unit tests measuring prefix lookup speedups."
    },

    # Sample 10: Agent plan dependency deduplication & DAG topological ordering
    {
        "raw_asr": "basically deduplicat autonomous execution plan steps inside dag underscore scheduler dot py buy resolving subtask dependencies across six candidate tool actions wait ten planned operations instead buy enforcing strict acyclic sequence constraints um filter redundant intermediate verifications buy streaming status events across a sink i o event queues right four unit tests confirming topological execution ordering",
        "refined_text": "Deduplicate autonomous execution plan steps inside dag_scheduler.py by resolving subtask dependencies across 6 candidate tool actions, evaluating 10 planned operations instead by enforcing strict acyclic sequence constraints.\n\nFilter redundant intermediate verifications by streaming status events across asyncio event queues. Write 4 unit tests confirming topological execution ordering."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Active noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 11: Dynamic System Prompt Template Versioning & Context Injection Engine
    {
        "raw_asr": "basically our agent orchestration infrastructure group refactored dynamic prompt compilation inside template underscore manager dot py buy introducing cryptographic version hashes across autonomous system prompts previously unversioned system directives caused unexpected prompt regressions exhausting eight one nine two context tokens across ten conversational turns wait fourteen conversational turns instead buy isolating variable persona parameters um the platform developers built a modular template compiler which validates prompt fragments across twelve registered persona schemas buy verifying variable types before model invocation so basically when an incoming query reaches our runtime gateway the compiler renders active role instructions wait allocat episodic memory slots buy capping reserved context across two zero four eight tokens instead okay so instruct cursor two benchmark prompt rendering latency across fifty concurrent a sink i o tasks right four unit tests verifying that unescaped template parameters raise structured validation exceptions",
        "refined_text": "Our agent orchestration infrastructure group refactored dynamic prompt compilation inside template_manager.py by introducing cryptographic version hashes across autonomous system prompts. Previously unversioned system directives caused unexpected prompt regressions, exhausting 8192 context tokens across 14 conversational turns instead, by isolating variable persona parameters.\n\nThe platform developers built a modular template compiler which validates prompt fragments across 12 registered persona schemas by verifying variable types before model invocation. When an incoming query reaches our runtime gateway, the compiler renders active role instructions, allocating episodic memory slots by capping reserved context across 2048 tokens instead.\n\nInstruct Cursor to benchmark prompt rendering latency across 50 concurrent asyncio tasks, and write 4 unit tests verifying that unescaped template parameters raise structured validation exceptions."
    },

    # Sample 12: Model Context Protocol (MCP) Server Implementation & JSON-RPC Tool Discovery
    {
        "raw_asr": "um our developer experience infrastructure squad modernized external tool dispatch inside mcp underscore server dot py buy implementing a model context protocol daemon across autonomous coding agents previously direct subprocess executions suffered from silent timeouts and memory exhaustion failing across twenty tool invocations wait twenty eight tool executions instead buy exposing unconstrained shell environments uh the systems engineers configured a j son r p c transport layer which registers standardized tool definitions across thirty two agent functions buy enforcing strict input schemas before execution so basically when a client agent discovers local environment capabilities the protocol server negotiates handshake parameters wait terminat unresponsive worker subtasks buy enforcing execution timeout limits across forty seconds instead okay so instruct claude two benchmark tool dispatch latency across sixty simulated agent queries right five unit tests confirming that unauthorized tool invocations return standard r p c error messages",
        "refined_text": "Our developer experience infrastructure squad modernized external tool dispatch inside mcp_server.py by implementing a Model Context Protocol daemon across autonomous coding agents. Previously direct subprocess executions suffered from silent timeouts and memory exhaustion, failing across 28 tool executions instead, by exposing unconstrained shell environments.\n\nThe systems engineers configured a JSON-RPC transport layer which registers standardized tool definitions across 32 agent functions by enforcing strict input schemas before execution. When a client agent discovers local environment capabilities, the protocol server negotiates handshake parameters, terminating unresponsive worker subtasks by enforcing execution timeout limits across 40 seconds instead.\n\nInstruct Claude to benchmark tool dispatch latency across 60 simulated agent queries, and write 5 unit tests confirming that unauthorized tool invocations return standard RPC error messages."
    },

    # Sample 13: RAG Hierarchical Context Chunking & ColBERT Late Interaction Token Scoring
    {
        "raw_asr": "basically our enterprise search engineering team upgraded document chunking pipelines inside hierarchical underscore chunker dot py buy deploying multi level chunk trees across internal engineering manuals previously single size passage chunking missed structural section headings degrading passage recall across fourteen benchmark retrieval queries wait twenty benchmark retrieval queries instead buy isolating narrow text fragments uh the retrieval engineers built a hierarchical token indexer which links two five six token child chunks two one zero two four token parent passages across sixteen technical repositories buy preserving structural context before dense embedding generation so basically when an engineer submits an ambiguous architecture question the reranker computes token interactions across host c p u threads wait recalculat late interaction similarity scores across thirty two candidate child passages instead okay so instruct windsurf two evaluate retrieval recall across seventy five domain questions right four unit tests validating that parent passage references expand correctly during context assembly",
        "refined_text": "Our enterprise search engineering team upgraded document chunking pipelines inside hierarchical_chunker.py by deploying multi-level chunk trees across internal engineering manuals. Previously single-size passage chunking missed structural section headings, degrading passage recall across 20 benchmark retrieval queries instead, by isolating narrow text fragments.\n\nThe retrieval engineers built a hierarchical token indexer which links 256 token child chunks to 1024 token parent passages across 16 technical repositories by preserving structural context before dense embedding generation. When an engineer submits an ambiguous architecture question, the reranker computes token interactions across host CPU threads, recalculating late-interaction similarity scores across 32 candidate child passages instead.\n\nInstruct Windsurf to evaluate retrieval recall across 75 domain questions, and write 4 unit tests validating that parent passage references expand correctly during context assembly."
    },

    # Sample 14: LLM Guardrail Pipeline with Prompt Injection & Secret Redaction Filters
    {
        "raw_asr": "um our agent security defense squad redesigned runtime prompt sanitization inside guardrail underscore filter dot py buy introducing multi layer injection detection filters across autonomous agent workflows previously unvalidated user inputs triggered unauthorized tool executions compromising safety boundaries across twelve penetration tests wait eighteen red team evaluations instead buy leaking confidential system prompt instructions uh the security developers built a token classification harness which monitors incoming prompt anomalies across six hazard categories buy evaluating adversarial role play patterns before prompt delivery so basically when an untrusted prompt enters the processing gateway the guardrail inspector evaluates semantic embeddings across a sink i o background workers wait terminat suspicious tool request sequences buy dropping prompts exceeding eighty percent threat scores across twenty threat categories instead okay so instruct cursor two test guardrail robustness across sixty five adversarial injection payloads right five unit tests validating that blocked requests generate structured audit records without leaking system prompts",
        "refined_text": "Our agent security defense squad redesigned runtime prompt sanitization inside guardrail_filter.py by introducing multi-layer injection detection filters across autonomous agent workflows. Previously unvalidated user inputs triggered unauthorized tool executions, compromising safety boundaries across 18 red-team evaluations instead, by leaking confidential system prompt instructions.\n\nThe security developers built a token classification harness which monitors incoming prompt anomalies across 6 hazard categories by evaluating adversarial role-play patterns before prompt delivery. When an untrusted prompt enters the processing gateway, the guardrail inspector evaluates semantic embeddings across asyncio background workers, terminating suspicious tool request sequences by dropping prompts exceeding 80 percent threat scores across 20 threat categories instead.\n\nInstruct Cursor to test guardrail robustness across 65 adversarial injection payloads, and write 5 unit tests validating that blocked requests generate structured audit records without leaking system prompts."
    },

    # Sample 15: LLM-as-a-Judge Evaluation Pipeline with Rubric Scoring & Cohen Kappa Reliability
    {
        "raw_asr": "basically our model evaluation quality squad overhauled offline assessment pipelines inside rubric underscore evaluator dot py buy establishing multi judge consensus scoring across complex agent reasoning outputs previously single judge automated evaluations produced inconsistent rating scores fluctuating across fourteen benchmark assessment runs wait twenty four benchmark evaluation rounds instead buy over weighting output length uh the evaluation engineers created a multi criterion grading harness which scores agent trajectories across five evaluation rubric dimensions buy evaluating chain of thought coherence before final score aggregation so basically when an agent benchmark run completes the evaluator parses structured scoring records across host c p u processes wait recalculat inter judge reliability buy measuring cohen kappa statistics across forty benchmark tasks instead okay so instruct aid er two benchmark evaluator agreement across seventy evaluation dialogues right four unit tests confirming that divergent judge scores trigger automatic arbitration workflows",
        "refined_text": "Our model evaluation quality squad overhauled offline assessment pipelines inside rubric_evaluator.py by establishing multi-judge consensus scoring across complex agent reasoning outputs. Previously single-judge automated evaluations produced inconsistent rating scores, fluctuating across 24 benchmark evaluation rounds instead, by over-weighting output length.\n\nThe evaluation engineers created a multi-criterion grading harness which scores agent trajectories across 5 evaluation rubric dimensions by evaluating chain-of-thought coherence before final score aggregation. When an agent benchmark run completes, the evaluator parses structured scoring records across host CPU processes, recalculating inter-judge reliability by measuring Cohen kappa statistics across 40 benchmark tasks instead.\n\nInstruct Aider to benchmark evaluator agreement across 70 evaluation dialogues, and write 4 unit tests confirming that divergent judge scores trigger automatic arbitration workflows."
    },

    # Sample 16: Semantic Caching for Agent Queries with Locality-Sensitive Hashing & Vector Search
    {
        "raw_asr": "um our a i runtime infrastructure squad deployed semantic response caching inside embedding underscore cache dot py buy establishing approximate nearest neighbor vector indexing across repetitive agent queries previously identical agent prompts triggered redundant model inference requests increasing latency across twenty daily pipeline runs wait thirty five daily pipeline executions instead buy repeating expensive foundation model calls uh the platform developers built a vector lookup module which indexes incoming prompt vectors across one five three six embedding dimensions buy checking cosine similarity against cached response clusters inside post gres so basically when an agent executes repetitive status queries the cache manager evaluates vector distances across a sink i o worker tasks wait deduplicat identical execution requests buy returning cached outputs four similarity matches above ninety four percent across twenty five cache partitions instead okay so instruct co pilot two measure cache lookup latency across eighty five simulated agent queries right five unit tests validating that cache entries invalidate whenever system prompt definitions change",
        "refined_text": "Our AI runtime infrastructure squad deployed semantic response caching inside embedding_cache.py by establishing approximate nearest neighbor vector indexing across repetitive agent queries. Previously identical agent prompts triggered redundant model inference requests, increasing latency across 35 daily pipeline executions instead, by repeating expensive foundation model calls.\n\nThe platform developers built a vector lookup module which indexes incoming prompt vectors across 1536 embedding dimensions by checking cosine similarity against cached response clusters inside Postgres. When an agent executes repetitive status queries, the cache manager evaluates vector distances across asyncio worker tasks, deduplicating identical execution requests by returning cached outputs for similarity matches above 94 percent across 25 cache partitions instead.\n\nInstruct Copilot to measure cache lookup latency across 85 simulated agent queries, and write 5 unit tests validating that cache entries invalidate whenever system prompt definitions change."
    },

    # Sample 17: Agent State Persistence & SQLite WAL Graph Checkpointing
    {
        "raw_asr": "basically our agent runtime architecture squad upgraded execution state persistence inside session underscore checkpoint dot py buy introducing transactional graph checkpointing across multi step agent workflows previously in memory scratchpad buffers were lost during worker process restarts dropping execution context across one six three eight four tokens over eight task iterations wait sixteen task iterations instead buy storing volatile heap pointers uh the systems developers built an asynchronous state coordinator which serializes agent memory states across twenty four execution nodes buy writing structured checkpoints into sqlite databases using write ahead logging so basically when a primary planner delegates subtasks two worker tools the state manager commits execution frames across a sink i o task queues wait synchronizat historical execution steps buy persisting scratchpad snapshots across six decision branches instead okay so instruct cursor two benchmark recovery latency across forty simulated worker crashes right four unit tests validating that resumed agent sessions restore valid scratchpad state without data corruption",
        "refined_text": "Our agent runtime architecture squad upgraded execution state persistence inside session_checkpoint.py by introducing transactional graph checkpointing across multi-step agent workflows. Previously in-memory scratchpad buffers were lost during worker process restarts, dropping execution context across 16384 tokens over 16 task iterations instead, by storing volatile heap pointers.\n\nThe systems developers built an asynchronous state coordinator which serializes agent memory states across 24 execution nodes by writing structured checkpoints into SQLite databases using write-ahead logging. When a primary planner delegates subtasks to worker tools, the state manager commits execution frames across asyncio task queues, synchronizing historical execution steps by persisting scratchpad snapshots across 6 decision branches instead.\n\nInstruct Cursor to benchmark recovery latency across 40 simulated worker crashes, and write 4 unit tests validating that resumed agent sessions restore valid scratchpad state without data corruption."
    },

    # Sample 18: Speculative Decoding & Verification Loop in LLM Pipeline Serving
    {
        "raw_asr": "um our model serving optimization squad accelerated agent generation latency inside speculative underscore engine dot py buy implementing speculative decoding loops between a small draft model and a large foundation model previously sequential auto regressive token sampling created severe inference bottlenecks across three two seven six eight context tokens over twelve reasoning passes wait eighteen reasoning passes instead buy issuing single token forward passes uh the serving engineers designed a parallel verification runner which proposes six speculative tokens per step buy scoring candidate token logits across host c p u threads before primary model verification so basically when the primary model evaluates candidate tokens the verification loop validates speculative streams in parallel wait recalculat token acceptance rates buy accepting valid draft tokens across eight speculation cycles instead okay so instruct windsurf two measure token throughput speedups across fifty benchmark agent prompts right five unit tests confirming that speculative sampling produces mathematically identical token sequences two standard decoding",
        "refined_text": "Our model serving optimization squad accelerated agent generation latency inside speculative_engine.py by implementing speculative decoding loops between a small draft model and a large foundation model. Previously sequential auto-regressive token sampling created severe inference bottlenecks across 32768 context tokens over 18 reasoning passes instead, by issuing single-token forward passes.\n\nThe serving engineers designed a parallel verification runner which proposes 6 speculative tokens per step by scoring candidate token logits across host CPU threads before primary model verification. When the primary model evaluates candidate tokens, the verification loop validates speculative streams in parallel, recalculating token acceptance rates by accepting valid draft tokens across 8 speculation cycles instead.\n\nInstruct Windsurf to measure token throughput speedups across 50 benchmark agent prompts, and write 5 unit tests confirming that speculative sampling produces mathematically identical token sequences to standard decoding."
    },

    # Sample 19: Multi-Agent Debate & Consensus Arbitration with Conflict Resolution Protocol
    {
        "raw_asr": "basically our autonomous systems coordination group refactored multi agent debate protocols inside consensus underscore arbiter dot py buy establishing structured peer critique across specialized agent personas previously unmoderated multi agent dialogues suffered from circular argument loops consuming six five five three six tokens across twelve debate rounds wait twenty two debate rounds instead buy repeating ungrounded assertions uh the platform developers deployed a deterministic consensus arbiter which moderates structured discussions among three reviewer agents buy calculating claim agreement across standardized metric rubrics so basically when reviewer agents offer conflicting code modification suggestions the arbiter aggregates reasoning traces across a sink i o streams wait arbitrat conflicting proposals buy conducting structured rebuttal exchanges across five debate iterations instead okay so instruct claude two evaluate debate convergence stability across forty five simulated code review sessions right four unit tests validating that contradictory reviewer outputs resolve into deterministic consensus decisions without hanging",
        "refined_text": "Our autonomous systems coordination group refactored multi-agent debate protocols inside consensus_arbiter.py by establishing structured peer critique across specialized agent personas. Previously unmoderated multi-agent dialogues suffered from circular argument loops, consuming 65536 tokens across 22 debate rounds instead, by repeating ungrounded assertions.\n\nThe platform developers deployed a deterministic consensus arbiter which moderates structured discussions among 3 reviewer agents by calculating claim agreement across standardized metric rubrics. When reviewer agents offer conflicting code modification suggestions, the arbiter aggregates reasoning traces across asyncio streams, arbitrating conflicting proposals by conducting structured rebuttal exchanges across 5 debate iterations instead.\n\nInstruct Claude to evaluate debate convergence stability across 45 simulated code review sessions, and write 4 unit tests validating that contradictory reviewer outputs resolve into deterministic consensus decisions without hanging."
    },

    # Sample 20: Asynchronous Tool Invocation & Pydantic Validation Fallback Engine
    {
        "raw_asr": "um our agent runtime integration squad redesigned tool execution pipelines inside tool underscore validator dot py buy implementing strict schema validation alongside partial j son recovery parsing previously corrupted argument strings generated buy language models crashed execution routines failing across sixteen autonomous task cycles wait twenty four autonomous task cycles instead buy rejecting malformed string literals uh the platform developers constructed a resilient dispatch manager which validates function arguments against pydantic models across twenty registered tool functions buy checking type constraints before execution so basically when an autonomous planner issues asynchronous tool invocations across host c p u threads the dispatcher inspects return payloads wait recalculat parameter structures buy repairing truncated j son trees across eight argument keys instead okay so instruct cursor two benchmark tool parsing resilience across seventy simulated corrupted tool payloads right five unit tests confirming that schema validation failures produce structured remediation prompts two the agent planner",
        "refined_text": "Our agent runtime integration squad redesigned tool execution pipelines inside tool_validator.py by implementing strict schema validation alongside partial JSON recovery parsing. Previously corrupted argument strings generated by language models crashed execution routines, failing across 24 autonomous task cycles instead, by rejecting malformed string literals.\n\nThe platform developers constructed a resilient dispatch manager which validates function arguments against Pydantic models across 20 registered tool functions by checking type constraints before execution. When an autonomous planner issues asynchronous tool invocations across host CPU threads, the dispatcher inspects return payloads, recalculating parameter structures by repairing truncated JSON trees across 8 argument keys instead.\n\nInstruct Cursor to benchmark tool parsing resilience across 70 simulated corrupted tool payloads, and write 5 unit tests confirming that schema validation failures produce structured remediation prompts to the agent planner."
    }
]

def main():
    print("=" * 60)
    print("VALIDATING BATCH 152 (DOMAIN 7: AI AGENT PROMPTING & LLM PIPELINES)")
    print("=" * 60)

    # 1. Individual sample validation
    total_samples = len(batch)
    passed_pair_validation = 0
    passed_clean_sample = 0
    total_noise_layers = 0

    for idx, sample in enumerate(batch, 1):
        raw = sample["raw_asr"]
        ref = sample["refined_text"]
        words = len(ref.split())

        # Determine target min noise layers (3 for short, 4 for medium/long)
        min_layers = 3 if words < 25 else 4
        is_valid, reason = validate_pair(sample, min_noise_layers=min_layers)
        cleaned_res, status = clean_sample(raw, ref)
        active_layers = count_active_noise_layers(raw)
        layer_count = sum(active_layers.values())
        total_noise_layers += layer_count

        if not is_valid:
            print(f"FAILED Sample {idx} (words={words}) in validate_pair: {reason}")
            sys.exit(1)
        passed_pair_validation += 1

        if status != "kept":
            print(f"FAILED Sample {idx} (words={words}) in clean_sample: {status}")
            sys.exit(1)
        passed_clean_sample += 1

        tier = "Short" if words < 25 else ("Medium" if words < 90 else "Long")
        print(f"Sample {idx:02d} [{tier:6s} | {words:3d}w | {layer_count} layers]: PASS (cleaner={status})")

    avg_noise_layers = round(total_noise_layers / total_samples, 2)
    print(f"\nAverage Active Noise Layers: {avg_noise_layers} (Target >= 4.0)")

    # 2. Batch level validation
    is_batch_valid, batch_reason, tier_counts = validate_batch(
        batch, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )

    if not is_batch_valid:
        print(f"\nFAILED validate_batch: {batch_reason}")
        sys.exit(1)

    print(f"\nBatch validation PASSED: {batch_reason}")
    print(f"Tier counts: {tier_counts}")

    # 3. Contamination check against sft_eval.json
    eval_file = Path("sft_eval.json")
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        eval_raws = {s.get("raw_asr", "").strip() for s in eval_data}
        eval_refs = {s.get("refined_text", "").strip() for s in eval_data}

        for idx, sample in enumerate(batch, 1):
            if sample["raw_asr"].strip() in eval_raws:
                print(f"FAILED Sample {idx}: raw_asr overlaps with sft_eval.json!")
                sys.exit(1)
            if sample["refined_text"].strip() in eval_refs:
                print(f"FAILED Sample {idx}: refined_text overlaps with sft_eval.json!")
                sys.exit(1)
        print("Contamination check PASSED: 0 leaked samples against sft_eval.json.")

    # 4. Save output
    output_path = Path("scratch/subagent_batch_152.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(batch)} verified pairs to {output_path}")

if __name__ == "__main__":
    main()
