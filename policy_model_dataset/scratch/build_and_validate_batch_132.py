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

    # Sample 1: Asynchronous tool call execution in agent dispatcher
    {
        "raw_asr": "um allocat agent underscore dispatch worker pools buy spawning four concurrent a sink i o coroutines",
        "refined_text": "Allocate agent_dispatch worker pools by spawning 4 concurrent asyncio coroutines."
    },

    # Sample 2: Host CPU offloading for agent embedding cache buffers
    {
        "raw_asr": "uh migrat embedding underscore cache buffers buy transferring sixteen memory pages two host c p u ram",
        "refined_text": "Migrate embedding_cache buffers by transferring 16 memory pages to host CPU RAM."
    },

    # Sample 3: Model Context Protocol JSON-RPC tool router session timeouts
    {
        "raw_asr": "basically terminat hanging tool underscore router sessions buy setting four second timeout thresholds four r p c handlers",
        "refined_text": "Terminate hanging tool_router sessions by setting 4 second timeout thresholds for RPC handlers."
    },

    # Sample 4: Persistent vector memory store table partitioning in Postgres
    {
        "raw_asr": "um initializ persistent vector underscore store tables buy creating eight indexed partitions inside post gres",
        "refined_text": "Initialize persistent vector_store tables by creating 8 indexed partitions inside Postgres."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Active noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 5: DSPy prompt teleprompter compiler & few-shot bootstrap optimizer
    {
        "raw_asr": "uh configur prompt optimization passes inside prompt underscore optimizer dot py buy evaluating candidate demonstration traces across sixteen training examples wait twenty four bootstrap demonstrations instead basically prune low scoring exemplars buy tracking validation accuracy across a sink i o test fixtures right three unit tests verifying teleprompter parameter convergence",
        "refined_text": "Configure prompt optimization passes inside prompt_optimizer.py by evaluating candidate demonstration traces across 16 training examples, using 24 bootstrap demonstrations instead.\n\nPrune low-scoring exemplars by tracking validation accuracy across asyncio test fixtures. Write 3 unit tests verifying teleprompter parameter convergence."
    },

    # Sample 6: Structured decoding engine with context-free grammar & token masks
    {
        "raw_asr": "um initializ constrained token generation inside schema underscore sampler dot py buy compiling j son schema rules across sixteen regex state transitions wait thirty two regex state transitions instead buy enforcing deterministic grammar constraints you know prune illegal vocabulary logits buy evaluating candidate token masks across host c p u threads right four unit tests verifying structured payload validation",
        "refined_text": "Initialize constrained token generation inside schema_sampler.py by compiling JSON schema rules across 32 regex state transitions, enforcing deterministic grammar constraints instead.\n\nPrune illegal vocabulary logits by evaluating candidate token masks across host CPU threads. Write 4 unit tests verifying structured payload validation."
    },

    # Sample 7: Agent memory sliding window summary compaction and episodic indexing
    {
        "raw_asr": "basically allocat conversational memory buffers inside memory underscore compactor dot py buy trimming message history across eight dialogue rounds wait twelve recent conversational turns instead buy preserving context continuity uh condens older exchanges buy writing semantic memory summaries across post gres vector tables right three unit tests validating message retention limits",
        "refined_text": "Allocate conversational memory buffers inside memory_compactor.py by trimming message history across 8 dialogue rounds, preserving 12 recent conversational turns instead.\n\nCondense older exchanges by writing semantic memory summaries across Postgres vector tables. Write 3 unit tests validating message retention limits."
    },

    # Sample 8: Asynchronous multi-agent RPC router with fallback retry loop
    {
        "raw_asr": "um operat agent tool dispatch pipelines inside router underscore service dot py buy forwarding parameter payloads across six worker processes wait ten remote r p c endpoints instead buy delegating requests smoothly you know recov failed invocations buy executing a sink i o retry loops across exponential backoff intervals right four unit tests confirming r p c error recovery",
        "refined_text": "Operate agent tool dispatch pipelines inside router_service.py by forwarding parameter payloads across 6 worker processes, delegating requests to 10 remote RPC endpoints instead.\n\nRecover failed invocations by executing asyncio retry loops across exponential backoff intervals. Write 4 unit tests confirming RPC error recovery."
    },

    # Sample 9: KV cache compression and prompt prefix caching for LLM inference serving
    {
        "raw_asr": "uh recalculat dynamic attention key value caches inside cache underscore manager dot py buy compressing token positions across twelve attention heads wait sixteen attention layers instead buy evicting middle layer representations basically maintain prompt prefix embeddings buy locking static system prompt tokens across host c p u memory pages right five unit tests validating cache retrieval stability",
        "refined_text": "Recalculate dynamic attention key-value caches inside cache_manager.py by compressing token positions across 12 attention heads, evicting middle layer representations across 16 attention layers instead.\n\nMaintain prompt prefix embeddings by locking static system prompt tokens across host CPU memory pages. Write 5 unit tests validating cache retrieval stability."
    },

    # Sample 10: Agent plan dependency deduplication & validation in ReAct execution loop
    {
        "raw_asr": "basically deduplicat autonomous planning steps inside plan underscore parser dot py buy evaluating subtask prerequisites across five planned tool calls wait nine candidate steps instead buy enforcing strict acyclic graph sequencing um discard redundant verification actions buy streaming intermediate execution traces across a sink i o message channels right four unit tests confirming plan dependency ordering",
        "refined_text": "Deduplicate autonomous planning steps inside plan_parser.py by evaluating subtask prerequisites across 5 planned tool calls, enforcing strict acyclic graph sequencing across 9 candidate steps instead.\n\nDiscard redundant verification actions by streaming intermediate execution traces across asyncio message channels. Write 4 unit tests confirming plan dependency ordering."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Active noise layers >= 4. Rationale with "by <action>".
    # =========================================================================

    # Sample 11: Dynamic System Prompt Template Versioning & Context Injection Engine
    {
        "raw_asr": "basically our agent runtime platform group refactored dynamic system prompt compilation inside prompt underscore assembler dot py buy introducing template version hashes across autonomous reasoning workflows previously unversioned system instructions suffered from silent prompt regressions exhausting eight one nine two tokens across ten conversational turns wait twelve conversational turns instead buy isolating persona directives um the platform engineers deployed a jinja template compiler which serializes prompt partials across sixteen registered persona definitions buy validating required context schema variables before model invocation so basically when an incoming agent query reaches the runtime gateway the prompt assembler merges dynamic role directives wait allocat episodic memory injections buy capping reserved context across two zero four eight tokens instead okay so instruct cursor two benchmark prompt compilation throughput across fifty concurrent a sink i o tasks right four unit tests verifying that malformed context variables raise structured validation errors without halting execution",
        "refined_text": "Our agent runtime platform group refactored dynamic system prompt compilation inside prompt_assembler.py by introducing template version hashes across autonomous reasoning workflows. Previously unversioned system instructions suffered from silent prompt regressions, exhausting 8192 tokens across 12 conversational turns instead, by isolating persona directives.\n\nThe platform engineers deployed a Jinja template compiler which serializes prompt partials across 16 registered persona definitions by validating required context schema variables before model invocation. When an incoming agent query reaches the runtime gateway, the prompt assembler merges dynamic role directives, allocating episodic memory injections by capping reserved context across 2048 tokens instead.\n\nInstruct Cursor to benchmark prompt compilation throughput across 50 concurrent asyncio tasks, and write 4 unit tests verifying that malformed context variables raise structured validation errors without halting execution."
    },

    # Sample 12: Model Context Protocol (MCP) Server Implementation & JSON-RPC Tool Discovery
    {
        "raw_asr": "um our developer tooling infrastructure group modernized external tool orchestration inside mcp underscore gateway dot py buy implementing a model context protocol server across autonomous agent clients previously direct subprocess invocations suffered from unhandled timeouts and permission leaks failing across sixteen tool execution runs wait twenty four tool execution runs instead buy exposing unvalidated shell commands uh the tooling engineers configured a j son r p c transport layer which exposes standardized tool manifests across thirty two registered agent functions buy enforcing strict input argument schemas before execution so basically when an autonomous client discovers available environment tools the protocol gateway negotiates capability handshakes wait terminat hanging worker processes buy enforcing execution timeouts across forty five seconds instead okay so instruct claude two benchmark tool dispatch latency across sixty simulated agent requests right five unit tests validating that unauthorized tool invocations return standard r p c protocol error envelopes",
        "refined_text": "Our developer tooling infrastructure group modernized external tool orchestration inside mcp_gateway.py by implementing a Model Context Protocol server across autonomous agent clients. Previously direct subprocess invocations suffered from unhandled timeouts and permission leaks, failing across 24 tool execution runs instead, by exposing unvalidated shell commands.\n\nThe tooling engineers configured a JSON-RPC transport layer which exposes standardized tool manifests across 32 registered agent functions by enforcing strict input argument schemas before execution. When an autonomous client discovers available environment tools, the protocol gateway negotiates capability handshakes, terminating hanging worker processes by enforcing execution timeouts across 45 seconds instead.\n\nInstruct Claude to benchmark tool dispatch latency across 60 simulated agent requests, and write 5 unit tests validating that unauthorized tool invocations return standard RPC protocol error envelopes."
    },

    # Sample 13: RAG Hierarchical Context Chunking & ColBERT Late Interaction Token Scoring
    {
        "raw_asr": "basically our enterprise retrieval group upgraded document chunking pipelines inside chunk underscore reranker dot py buy deploying hierarchical parent child chunk trees across technical knowledge bases previously flat chunking strategies missed critical section headings across complex manuals degrading passage retrieval recall across twelve benchmark document searches wait eighteen benchmark document searches instead buy fragmenting contiguous conceptual sections uh the retrieval engineers built a multi level token indexer which links one two eight token child passages two one zero two four token parent contexts across sixteen document collections buy preserving semantic context headers before embedding generation so basically when a user submits an ambiguous technical query the retrieval engine scores candidate token interactions across host c p u threads wait recalculat late interaction token similarity across thirty two retrieved child passages instead okay so instruct windsurf two evaluate passage recall across eighty domain documentation queries right four unit tests verifying that parent document references resolve correctly during context expansion",
        "refined_text": "Our enterprise retrieval group upgraded document chunking pipelines inside chunk_reranker.py by deploying hierarchical parent-child chunk trees across technical knowledge bases. Previously flat chunking strategies missed critical section headings across complex manuals, degrading passage retrieval recall across 18 benchmark document searches instead, by fragmenting contiguous conceptual sections.\n\nThe retrieval engineers built a multi-level token indexer which links 128 token child passages to 1024 token parent contexts across 16 document collections by preserving semantic context headers before embedding generation. When a user submits an ambiguous technical query, the retrieval engine scores candidate token interactions across host CPU threads, recalculating late-interaction token similarity across 32 retrieved child passages instead.\n\nInstruct Windsurf to evaluate passage recall across 80 domain documentation queries, and write 4 unit tests verifying that parent document references resolve correctly during context expansion."
    },

    # Sample 14: LLM Guardrail Pipeline with Prompt Injection & Secret Redaction Filters
    {
        "raw_asr": "um our agent security platform group refactored runtime input sanitization inside guardrail underscore sanitizer dot py buy deploying multi layer prompt injection filters across autonomous coding pipelines previously unvetted repository files triggered unauthorized tool executions compromising agent isolation across ten automated red team tests wait fifteen automated red team tests instead buy leaking internal system prompt tokens uh the security researchers built a token classification harness which scores incoming text anomalies across eight hazard categories buy evaluating role impersonation patterns before prompt expansion so basically when an autonomous agent ingests untrusted pull request comments the safety filter inspects token embeddings across a sink i o background tasks wait terminat suspicious execution cycles buy rejecting prompts exceeding eighty five percent risk scores across twenty threat vectors instead okay so instruct cursor two test guardrail resistance across seventy adversarial attack payloads right five unit tests validating that blocked inputs return structured security audit logs without revealing prompt contents",
        "refined_text": "Our agent security platform group refactored runtime input sanitization inside guardrail_sanitizer.py by deploying multi-layer prompt injection filters across autonomous coding pipelines. Previously unvetted repository files triggered unauthorized tool executions, compromising agent isolation across 15 automated red-team tests instead, by leaking internal system prompt tokens.\n\nThe security researchers built a token classification harness which scores incoming text anomalies across 8 hazard categories by evaluating role impersonation patterns before prompt expansion. When an autonomous agent ingests untrusted pull request comments, the safety filter inspects token embeddings across asyncio background tasks, terminating suspicious execution cycles by rejecting prompts exceeding 85 percent risk scores across 20 threat vectors instead.\n\nInstruct Cursor to test guardrail resistance across 70 adversarial attack payloads, and write 5 unit tests validating that blocked inputs return structured security audit logs without revealing prompt contents."
    },

    # Sample 15: LLM-as-a-Judge Evaluation Pipeline with G-Eval & Cohen Kappa Reliability
    {
        "raw_asr": "basically our model evaluation engineering team modernized offline assessment pipelines inside judge underscore evaluator dot py buy introducing multi judge consensus scoring across complex reasoning prompts previously single judge automated evaluations exhibited severe subjective bias fluctuating across sixteen benchmark evaluation runs wait twenty two benchmark evaluation runs instead buy over weighting response verbosity uh the quality developers built a structured grading engine which scores candidate model outputs across four distinct rubric dimensions buy evaluating chain of thought validity before final aggregation so basically when a prompt candidate generates new evaluation datasets the evaluation harness parses structured scoring judgments across host c p u threads wait recalculat inter rater agreement buy measuring cohen kappa metrics across fifty benchmark cases instead okay so instruct aid er two benchmark judge scoring reproducibility across eighty evaluation dialogues right four unit tests verifying that divergent judge ratings trigger automated consensus arbitration",
        "refined_text": "Our model evaluation engineering team modernized offline assessment pipelines inside judge_evaluator.py by introducing multi-judge consensus scoring across complex reasoning prompts. Previously single-judge automated evaluations exhibited severe subjective bias, fluctuating across 22 benchmark evaluation runs instead, by over-weighting response verbosity.\n\nThe quality developers built a structured grading engine which scores candidate model outputs across 4 distinct rubric dimensions by evaluating chain-of-thought validity before final aggregation. When a prompt candidate generates new evaluation datasets, the evaluation harness parses structured scoring judgments across host CPU threads, recalculating inter-rater agreement by measuring Cohen kappa metrics across 50 benchmark cases instead.\n\nInstruct Aider to benchmark judge scoring reproducibility across 80 evaluation dialogues, and write 4 unit tests verifying that divergent judge ratings trigger automated consensus arbitration."
    },

    # Sample 16: Semantic Caching for Agent Queries with Locality-Sensitive Hashing & Vector Search
    {
        "raw_asr": "um our a i platform infrastructure group implemented semantic response caching inside semantic underscore cache dot py buy deploying approximate nearest neighbor vector indexing across repetitive agent queries previously identical user prompts triggered redundant model inference calls increasing operational latency across thirty daily pipeline runs wait forty daily pipeline runs instead buy repeating expensive token generation uh the platform engineers built an embedding indexer which maps incoming prompt vectors across one five three six embedding dimensions buy evaluating cosine similarity against indexed response clusters inside post gres so basically when an autonomous workflow issues repeated tool inquiries the cache controller matches query representations across a sink i o worker pools wait deduplicat repetitive execution requests buy returning cached responses four similarity matches above ninety five percent across thirty semantic partitions instead okay so instruct co pilot two benchmark cache lookup latency across ninety simulated agent inquiries right five unit tests validating that cache invalidation triggers whenever system prompt definitions update",
        "refined_text": "Our AI platform infrastructure group implemented semantic response caching inside semantic_cache.py by deploying approximate nearest neighbor vector indexing across repetitive agent queries. Previously identical user prompts triggered redundant model inference calls, increasing operational latency across 40 daily pipeline runs instead, by repeating expensive token generation.\n\nThe platform engineers built an embedding indexer which maps incoming prompt vectors across 1536 embedding dimensions by evaluating cosine similarity against indexed response clusters inside Postgres. When an autonomous workflow issues repeated tool inquiries, the cache controller matches query representations across asyncio worker pools, deduplicating repetitive execution requests by returning cached responses for similarity matches above 95 percent across 30 semantic partitions instead.\n\nInstruct Copilot to benchmark cache lookup latency across 90 simulated agent inquiries, and write 5 unit tests validating that cache invalidation triggers whenever system prompt definitions update."
    },

    # Sample 17: Agent State Persistence & SQLite WAL Graph Checkpointing
    {
        "raw_asr": "basically our cognitive agent systems group upgraded session state persistence inside state underscore checkpoint dot py buy deploying transactional graph checkpointing across multi step execution workflows previously in memory execution graphs were lost during unexpected worker restarts dropping agent scratchpad states across one six three eight four context tokens over ten conversational turns wait fourteen conversational turns instead buy relying on volatile process heap storage uh the platform developers built a persistent state manager which serializes agent memory deltas across thirty two execution nodes buy writing structured snapshots into sqlite tables using write ahead logging so basically when a planning agent delegates subtasks two autonomous tools the state manager commits session checkpoints across a sink i o worker queues wait synchronizat historical execution frames buy persisting intermediate reasoning states across six decision branches instead okay so instruct cursor two benchmark state recovery latency across forty five simulated node restarts right four unit tests verifying that resumed agent sessions reconstruct valid scratchpad environments without corrupted states",
        "refined_text": "Our cognitive agent systems group upgraded session state persistence inside state_checkpoint.py by deploying transactional graph checkpointing across multi-step execution workflows. Previously in-memory execution graphs were lost during unexpected worker restarts, dropping agent scratchpad states across 16384 context tokens over 14 conversational turns instead, by relying on volatile process heap storage.\n\nThe platform developers built a persistent state manager which serializes agent memory deltas across 32 execution nodes by writing structured snapshots into SQLite tables using write-ahead logging. When a planning agent delegates subtasks to autonomous tools, the state manager commits session checkpoints across asyncio worker queues, synchronizing historical execution frames by persisting intermediate reasoning states across 6 decision branches instead.\n\nInstruct Cursor to benchmark state recovery latency across 45 simulated node restarts, and write 4 unit tests verifying that resumed agent sessions reconstruct valid scratchpad environments without corrupted states."
    },

    # Sample 18: Speculative Decoding & Verification Loop in LLM Pipeline Serving
    {
        "raw_asr": "um our model serving inference group optimized generation latency inside speculative underscore runner dot py buy integrating speculative decoding loops between a compact draft model and our primary foundation model previously unbatched auto regressive generation limited token serving throughput generating bottlenecks across three two seven six eight context tokens over ten reasoning passes wait sixteen reasoning passes instead buy executing sequential single token predictions uh the systems engineers built an speculative verification engine which emits five speculative draft tokens per step buy scoring candidate token logits across host c p u threads before target verification so basically when the primary model evaluates speculative proposals the verification runner validates draft token streams in parallel wait recalculat speculative acceptance rates buy retaining valid candidate tokens across eight speculation cycles instead okay so instruct windsurf two benchmark generation speedups across sixty benchmark reasoning prompts right five unit tests validating that speculative sampling produces mathematically identical probability distributions two greedy decoding",
        "refined_text": "Our model serving inference group optimized generation latency inside speculative_runner.py by integrating speculative decoding loops between a compact draft model and our primary foundation model. Previously unbatched auto-regressive generation limited token serving throughput, generating bottlenecks across 32768 context tokens over 16 reasoning passes instead, by executing sequential single-token predictions.\n\nThe systems engineers built an speculative verification engine which emits 5 speculative draft tokens per step by scoring candidate token logits across host CPU threads before target verification. When the primary model evaluates speculative proposals, the verification runner validates draft token streams in parallel, recalculating speculative acceptance rates by retaining valid candidate tokens across 8 speculation cycles instead.\n\nInstruct Windsurf to benchmark generation speedups across 60 benchmark reasoning prompts, and write 5 unit tests validating that speculative sampling produces mathematically identical probability distributions to greedy decoding."
    },

    # Sample 19: Multi-Agent Debate & Consensus Arbitration with Conflict Resolution Protocol
    {
        "raw_asr": "basically our autonomous coordination architecture group refactored multi agent debate protocols inside debate underscore arbiter dot py buy establishing structured peer critique across specialized agent personas previously unmoderated multi agent dialogues entered circular reasoning loops consuming six five five three six tokens across fourteen conversational turns wait twenty conversational turns instead buy repeating contradictory assertions uh the platform developers deployed a consensus arbiter which coordinates round robin evaluations among three specialized reviewer agents buy scoring patch confidence across standardized rubric metrics so basically when peer agents propose conflicting code judgments the arbiter aggregates reasoning outputs across a sink i o message streams wait arbitrat divergent verdicts buy running structured rebuttal exchanges across five debate iterations instead okay so instruct claude two evaluate debate convergence across fifty five simulated pull request scenarios right four unit tests verifying that conflicting reviewer judgments resolve into deterministic consensus decisions without hanging",
        "refined_text": "Our autonomous coordination architecture group refactored multi-agent debate protocols inside debate_arbiter.py by establishing structured peer critique across specialized agent personas. Previously unmoderated multi-agent dialogues entered circular reasoning loops, consuming 65536 tokens across 20 conversational turns instead, by repeating contradictory assertions.\n\nThe platform developers deployed a consensus arbiter which coordinates round-robin evaluations among 3 specialized reviewer agents by scoring patch confidence across standardized rubric metrics. When peer agents propose conflicting code judgments, the arbiter aggregates reasoning outputs across asyncio message streams, arbitrating divergent verdicts by running structured rebuttal exchanges across 5 debate iterations instead.\n\nInstruct Claude to evaluate debate convergence across 55 simulated pull request scenarios, and write 4 unit tests verifying that conflicting reviewer judgments resolve into deterministic consensus decisions without hanging."
    },

    # Sample 20: Asynchronous Tool Invocation & Pydantic Validation Fallback Engine
    {
        "raw_asr": "um our agent platform infrastructure group redesigned tool execution pipelines inside tool underscore executor dot py buy deploying strict schema validation alongside partial j son recovery parsers previously malformed argument strings generated buy language models crashed execution loops failing across sixteen autonomous task runs wait twenty six autonomous task runs instead buy rejecting unescaped string literals uh the platform engineers built a resilient dispatcher which validates function call arguments against pydantic schemas across twenty four registered tool definitions buy checking type constraints before tool invocation so basically when an autonomous agent issues asynchronous tool calls across host c p u threads the dispatch manager inspects execution results wait recalculat parameter mappings buy parsing partial j son syntax trees across eight parameter fields instead okay so instruct cursor two benchmark tool deserialization resilience across sixty five synthetic corrupted tool payloads right five unit tests validating that schema errors return actionable correction guidance two the planner",
        "refined_text": "Our agent platform infrastructure group redesigned tool execution pipelines inside tool_executor.py by deploying strict schema validation alongside partial JSON recovery parsers. Previously malformed argument strings generated by language models crashed execution loops, failing across 26 autonomous task runs instead, by rejecting unescaped string literals.\n\nThe platform engineers built a resilient dispatcher which validates function call arguments against Pydantic schemas across 24 registered tool definitions by checking type constraints before tool invocation. When an autonomous agent issues asynchronous tool calls across host CPU threads, the dispatch manager inspects execution results, recalculating parameter mappings by parsing partial JSON syntax trees across 8 parameter fields instead.\n\nInstruct Cursor to benchmark tool deserialization resilience across 65 synthetic corrupted tool payloads, and write 5 unit tests validating that schema errors return actionable correction guidance to the planner."
    }
]

def main():
    print("=" * 60)
    print("VALIDATING BATCH 132 (DOMAIN 7: AI AGENT PROMPTING & LLM PIPELINES)")
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
    output_path = Path("scratch/subagent_batch_132.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(batch)} verified pairs to {output_path}")

if __name__ == "__main__":
    main()
