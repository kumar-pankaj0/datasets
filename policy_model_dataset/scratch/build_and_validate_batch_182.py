import json
import re
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch, count_active_noise_layers, get_noise_layer_count
from cleaner import clean_sample

# Load eval set for leakage check
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e["raw_asr"].strip().lower() for e in eval_data}
    eval_refs = {e["refined_text"].strip().lower() for e in eval_data}
else:
    eval_raws = set()
    eval_refs = set()

# Domain 7: AI Agent System Prompting & LLM Pipeline Architecture
# Batch 182 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. Zero newlines. Max 1 cut-word. Active layers >= 3.
    # =========================================================================

    # Sample 1: Configure tool_dispatcher latency limits
    {
        "raw_asr": "um configur tool underscore dispatcher latency limits buy setting ten millisecond timeouts four remote r p c handlers",
        "refined_text": "Configure tool_dispatcher latency limits by setting 10 millisecond timeouts for remote RPC handlers."
    },

    # Sample 2: Allocate chunk_allocator buffers
    {
        "raw_asr": "uh allocat chunk underscore allocator buffers buy assigning thirty two token windows two local c p u threads",
        "refined_text": "Allocate chunk_allocator buffers by assigning 32 token windows to local CPU threads."
    },

    # Sample 3: Terminate agent_queue workers
    {
        "raw_asr": "basically terminat agent underscore queue workers buy enforcing eight second deadlines four background a sink i o routines",
        "refined_text": "Terminate agent_queue workers by enforcing 8 second deadlines for background asyncio routines."
    },

    # Sample 4: Initialize vector_memory partitions
    {
        "raw_asr": "you know initializ vector underscore memory partitions buy allocating sixteen index shards two persistent post gres tables",
        "refined_text": "Initialize vector_memory partitions by allocating 16 index shards to persistent Postgres tables."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 5: Chain-of-thought scratchpad distillation in scratchpad_trimmer
    {
        "raw_asr": "uh configur scratchpad distillation passes inside scratchpad underscore trimmer buy pruning repetitive chain of thought steps across fourteen reasoning traces wait twenty two candidate reasoning traces instead buy enforcing step significance thresholds basically prune redundant intermediate observations buy compressing thought tokens across a sink i o worker streams and right three unit tests verifying scratchpad compression fidelity",
        "refined_text": "Configure scratchpad distillation passes inside scratchpad_trimmer by pruning repetitive chain-of-thought steps across 14 reasoning traces, evaluating 22 candidate reasoning traces instead by enforcing step significance thresholds.\n\nPrune redundant intermediate observations by compressing thought tokens across asyncio worker streams, and write 3 unit tests verifying scratchpad compression fidelity."
    },

    # Sample 6: Agent tool schema parser in tool_parser
    {
        "raw_asr": "um initializ agent tool schema validation routines inside tool underscore parser buy parsing pydantic argument models across sixteen registered functions wait twenty four schema definitions instead buy enforcing strict field type boundaries you know filter unsupported recursive parameter definitions buy checking nested dictionary constraints across host c p u threads and right four unit tests confirming schema validation coverage",
        "refined_text": "Initialize agent tool schema validation routines inside tool_parser by parsing Pydantic argument models across 16 registered functions, validating 24 schema definitions instead by enforcing strict field type boundaries.\n\nFilter unsupported recursive parameter definitions by checking nested dictionary constraints across host CPU threads, and write 4 unit tests confirming schema validation coverage."
    },

    # Sample 7: Multi-query RAG expansion in query_expander
    {
        "raw_asr": "basically allocat sub query generation memory inside query underscore expander buy producing diverse search perspectives across ten user prompts wait eighteen generation passes instead buy enforcing semantic keyword variance uh deduplicate generated retrieval queries buy comparing vector embeddings across post gres document indices and right three unit tests verifying multi query retrieval diversity",
        "refined_text": "Allocate sub-query generation memory inside query_expander by producing diverse search perspectives across 10 user prompts, executing 18 generation passes instead by enforcing semantic keyword variance.\n\nDeduplicate generated retrieval queries by comparing vector embeddings across Postgres document indices, and write 3 unit tests verifying multi-query retrieval diversity."
    },

    # Sample 8: KV-cache eviction manager in kv_cache_evictor
    {
        "raw_asr": "um recalculat attention key value cache quotas inside k v underscore cache underscore evictor buy evicting stale conversation tokens across twelve session contexts wait twenty dialogue turns instead buy enforcing sliding attention windows basically purge inactive context blocks buy tracking timestamp markers across a sink i o background workers and right four unit tests validating attention cache eviction thresholds",
        "refined_text": "Recalculate attention key-value cache quotas inside kv_cache_evictor by evicting stale conversation tokens across 12 session contexts, retaining 20 dialogue turns instead by enforcing sliding attention windows.\n\nPurge inactive context blocks by tracking timestamp markers across asyncio background workers, and write 4 unit tests validating attention cache eviction thresholds."
    },

    # Sample 9: Multi-agent message bus coordinator in blackboard_state
    {
        "raw_asr": "uh communicat shared agent memory states inside blackboard underscore state buy broadcasting structured intermediate artifacts across eight local processes wait routing two sixteen remote r p c nodes instead buy balancing communication overhead you know synchronize multi agent workspace modifications buy asserting atomic revision locks across host c p u threads and right three unit tests verifying state transition consistency",
        "refined_text": "Communicate shared agent memory states inside blackboard_state by broadcasting structured intermediate artifacts across 8 local processes, routing to 16 remote RPC nodes instead by balancing communication overhead.\n\nSynchronize multi-agent workspace modifications by asserting atomic revision locks across host CPU threads, and write 3 unit tests verifying state transition consistency."
    },

    # Sample 10: Privileged tool escalation router in escalation_router
    {
        "raw_asr": "basically arbitrat privileged tool invocation permissions inside escalation underscore router buy dispatching approval requests across six risk tiers wait fourteen critical action categories instead buy intercepting sensitive system operations um suspend unapproved execution requests buy queueing agent tool calls across host c p u threads and right four unit tests confirming human escalation timeouts",
        "refined_text": "Arbitrate privileged tool invocation permissions inside escalation_router by dispatching approval requests across 6 risk tiers, evaluating 14 critical action categories instead by intercepting sensitive system operations.\n\nSuspend unapproved execution requests by queueing agent tool calls across host CPU threads, and write 4 unit tests confirming human escalation timeouts."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 11: Tool execution sandbox isolation in sandbox_executor.py
    {
        "raw_asr": "um our agent runtime security team overhauled container execution boundaries inside sandbox underscore executor dot py buy deploying hardened g visor isolation across dynamic code interpretation tasks previously unconstrained code execution routines exposed host resources failing across sixteen benchmark test workloads wait twenty eight tool executions instead buy leaking environment variable tokens uh the security infrastructure developers constructed an ephemeral microVM runner which mounts read only system directories across thirty isolated agent sandboxes buy enforcing strict namespace boundaries before shell invocation so basically when an autonomous coding agent executes generated bash commands the runtime supervisor traps unprivileged syscalls across host c p u threads wait terminat runaway container instances buy revoking network ingress permissions across eight execution corridors instead okay so instruct cursor two benchmark sandbox instantiation latency across sixty simulated agent coding tasks right five unit tests validating that file modification outside slash tmp triggers immediate execution denial",
        "refined_text": "Our agent runtime security team overhauled container execution boundaries inside sandbox_executor.py by deploying hardened gVisor isolation across dynamic code interpretation tasks. Previously unconstrained code execution routines exposed host resources, failing across 16 benchmark test workloads, evaluating 28 tool executions instead, by leaking environment variable tokens.\n\nThe security infrastructure developers constructed an ephemeral microVM runner which mounts read-only system directories across 30 isolated agent sandboxes by enforcing strict namespace boundaries before shell invocation. When an autonomous coding agent executes generated bash commands, the runtime supervisor traps unprivileged syscalls across host CPU threads, terminating runaway container instances by revoking network ingress permissions across 8 execution corridors instead.\n\nInstruct Cursor to benchmark sandbox instantiation latency across 60 simulated agent coding tasks, and write 5 unit tests validating that file modification outside /tmp triggers immediate execution denial."
    },

    # Sample 12: Automated prompt compiler and few-shot teleprompter in prompt_compiler.py
    {
        "raw_asr": "basically our l l m optimization engineering group reconstructed prompt compilation pipelines inside prompt underscore compiler dot py buy introducing metric driven teleprompter optimization across reasoning tasks previously handcrafted system prompts exhibited variable task performance failing across eight one nine two context tokens over fourteen evaluation epochs wait twenty six prompt variations instead buy generating inconsistent output schemas uh the platform developers designed a multi stage bootstrapping optimizer which synthesizes candidate prompt instructions across thirty two task examples buy evaluating validation metric gradients before prompt deployment so basically when an autonomous agent pipeline compiles task instructions the optimizer evaluates trajectory scores across a sink i o execution queues wait recalculat prompt token weights buy selecting top performing demonstration sets across six optimization rounds instead okay so instruct claude two measure prompt compilation convergence speed across fifty five simulated agent workflows right four unit tests verifying that compiled prompts maintain strict schema compliance",
        "refined_text": "Our LLM optimization engineering group reconstructed prompt compilation pipelines inside prompt_compiler.py by introducing metric-driven teleprompter optimization across reasoning tasks. Previously handcrafted system prompts exhibited variable task performance, failing across 8192 context tokens over 14 evaluation epochs, evaluating 26 prompt variations instead, by generating inconsistent output schemas.\n\nThe platform developers designed a multi-stage bootstrapping optimizer which synthesizes candidate prompt instructions across 32 task examples by evaluating validation metric gradients before prompt deployment. When an autonomous agent pipeline compiles task instructions, the optimizer evaluates trajectory scores across asyncio execution queues, recalculating prompt token weights by selecting top-performing demonstration sets across 6 optimization rounds instead.\n\nInstruct Claude to measure prompt compilation convergence speed across 55 simulated agent workflows, and write 4 unit tests verifying that compiled prompts maintain strict schema compliance."
    },

    # Sample 13: Tree-of-Thoughts exploration planner in tree_search_planner.py
    {
        "raw_asr": "um our autonomous reasoning platform squad revamped multi step decision trees inside tree underscore search underscore planner dot py buy integrating monte carlo tree search across complex software planning tasks previously greedy chain of thought generation entered dead end reasoning paths failing across eighteen benchmark planning problems wait thirty search trajectories instead buy accumulating early reasoning errors uh the planning algorithm engineers built a tree exploration harness which tracks value function scores across forty candidate reasoning branches buy evaluating state transition heuristics before action commitment so basically when an autonomous planning agent encounters ambiguous task requirements the planner expands exploration frontiers across post gres state logs wait arbitrat competing trajectory paths buy pruning unpromising reasoning branches across twelve decision steps instead okay so instruct windsurf two benchmark tree search planning efficiency across seventy simulated agent decision runs right four unit tests confirming that subtrees below score threshold are pruned",
        "refined_text": "Our autonomous reasoning platform squad revamped multi-step decision trees inside tree_search_planner.py by integrating Monte Carlo tree search across complex software planning tasks. Previously greedy chain-of-thought generation entered dead-end reasoning paths, failing across 18 benchmark planning problems, evaluating 30 search trajectories instead, by accumulating early reasoning errors.\n\nThe planning algorithm engineers built a tree exploration harness which tracks value function scores across 40 candidate reasoning branches by evaluating state transition heuristics before action commitment. When an autonomous planning agent encounters ambiguous task requirements, the planner expands exploration frontiers across Postgres state logs, arbitrating competing trajectory paths by pruning unpromising reasoning branches across 12 decision steps instead.\n\nInstruct Windsurf to benchmark tree search planning efficiency across 70 simulated agent decision runs, and write 4 unit tests confirming that subtrees below score threshold are pruned."
    },

    # Sample 14: Streaming token demuxer in stream_demuxer.py
    {
        "raw_asr": "basically our agent streaming infrastructure team redesigned real time event demuxing inside stream underscore demuxer dot py buy introducing incremental tool call parsing across concurrent generation events previously monolithic stream processors delayed downstream tool dispatch failing across sixteen conversational turns wait twenty four chunk sequences instead buy blocking on complete model responses uh the streaming engineers constructed a stateful delimiter tokenizer which isolates thought streams from action payloads across twenty streaming chunk frames buy checking regular expression boundary patterns on arrival so basically when a language model emits structured action tokens the demuxer routes execution payloads across host c p u threads wait communicat partial tool arguments buy dispatching pre parsed parameters across eight background coroutines instead okay so instruct cursor two evaluate streaming demuxing latency across sixty five simulated tool generation streams right five unit tests validating that malformed boundary delimiters trigger graceful fallback parsing",
        "refined_text": "Our agent streaming infrastructure team redesigned real-time event demuxing inside stream_demuxer.py by introducing incremental tool call parsing across concurrent generation events. Previously monolithic stream processors delayed downstream tool dispatch, failing across 16 conversational turns, evaluating 24 chunk sequences instead, by blocking on complete model responses.\n\nThe streaming engineers constructed a stateful delimiter tokenizer which isolates thought streams from action payloads across 20 streaming chunk frames by checking regular expression boundary patterns on arrival. When a language model emits structured action tokens, the demuxer routes execution payloads across host CPU threads, communicating partial tool arguments by dispatching pre-parsed parameters across 8 background coroutines instead.\n\nInstruct Cursor to evaluate streaming demuxing latency across 65 simulated tool generation streams, and write 5 unit tests validating that malformed boundary delimiters trigger graceful fallback parsing."
    },

    # Sample 15: Sliding window context budgeter in context_budgeter.py
    {
        "raw_asr": "um our inference context management group re architected dynamic token budgeting inside context underscore budgeter dot py buy establishing adaptive token reservation partitions across conversation histories previously rigid context allocation caused sudden system prompt truncation exhausting one six three eight four context tokens across twelve multi turn dialogues wait twenty two interaction sessions instead buy over allocating retrieval history buffers uh the infrastructure developers created a dynamic partition scheduler which balances prompt capacity among system instructions retrieval documents and scratchpad logs across eighteen task domains buy calculating token density distributions before model submission so basically when an agent query incorporates extensive repository context the budgeter condenses historical observations across a sink i o worker pipelines wait allocat reserved context windows buy preserving core system rules across four zero nine six tokens instead okay so instruct claude two benchmark context partition assembly speed across fifty simulated multi turn tasks right four unit tests validating that system instruction capacity remains strictly protected against overflow",
        "refined_text": "Our inference context management group re-architected dynamic token budgeting inside context_budgeter.py by establishing adaptive token reservation partitions across conversation histories. Previously rigid context allocation caused sudden system prompt truncation, exhausting 16384 context tokens across 12 multi-turn dialogues, evaluating 22 interaction sessions instead, by over-allocating retrieval history buffers.\n\nThe infrastructure developers created a dynamic partition scheduler which balances prompt capacity among system instructions, retrieval documents, and scratchpad logs across 18 task domains by calculating token density distributions before model submission. When an agent query incorporates extensive repository context, the budgeter condenses historical observations across asyncio worker pipelines, allocating reserved context windows by preserving core system rules across 4096 tokens instead.\n\nInstruct Claude to benchmark context partition assembly speed across 50 simulated multi-turn tasks, and write 4 unit tests validating that system instruction capacity remains strictly protected against overflow."
    },

    # Sample 16: Grammar-constrained decoding engine in grammar_decoder.py
    {
        "raw_asr": "basically our agent safety and structured parsing squad enhanced token logit masking inside grammar underscore decoder dot py buy deploying deterministic transition graphs across tool payload generations previously unconstrained vocabulary sampling emitted malformed syntax failing across fourteen automated tool invocations wait twenty six schema validations instead buy producing unterminated string literals uh the runtime developers implemented a finite state automata sampler which transforms pydantic schemas into token level transition bitmasks across thirty tool types buy filtering illegal vocabulary indices before logit processing so basically when the model predicts next token probabilities the engine masks disallowed vocabulary tokens across host c p u threads wait initializ parser state machines buy bounding output symbols across twelve valid j son tokens instead okay so instruct cursor two measure grammar constrained decoding throughput across sixty simulated agent tool prompts right five unit tests validating that output payloads conform strictly two expected schema structures",
        "refined_text": "Our agent safety and structured parsing squad enhanced token logit masking inside grammar_decoder.py by deploying deterministic transition graphs across tool payload generations. Previously unconstrained vocabulary sampling emitted malformed syntax, failing across 14 automated tool invocations, evaluating 26 schema validations instead, by producing unterminated string literals.\n\nThe runtime developers implemented a finite-state automata sampler which transforms Pydantic schemas into token-level transition bitmasks across 30 tool types by filtering illegal vocabulary indices before logit processing. When the model predicts next-token probabilities, the engine masks disallowed vocabulary tokens across host CPU threads, initializing parser state machines by bounding output symbols across 12 valid JSON tokens instead.\n\nInstruct Cursor to measure grammar-constrained decoding throughput across 60 simulated agent tool prompts, and write 5 unit tests validating that output payloads conform strictly to expected schema structures."
    },

    # Sample 17: Episodic memory indexing and consolidation in memory_indexer.py
    {
        "raw_asr": "um our cognitive agent memory architecture team upgraded long term persistence routines inside memory underscore indexer dot py buy implementing structured episodic memory synthesis across agent task histories previously unmanaged conversation logs accumulated noisy redundant text consuming three two seven six eight context tokens across ten multi step sessions wait eighteen dialogue transcripts instead buy preserving unhelpful tool stack traces uh the memory engineers constructed a background consolidation service which extracts distilled user guidelines and technical facts across twenty four developer interactions buy running automated summarization passes before persistent indexing so basically when an autonomous development session concludes the worker commits semantic embeddings across post gres vector tables wait synchronizat index partitions buy updating nearest neighbor indices across sixteen memory partitions instead okay so instruct aid er two evaluate episodic memory recall accuracy across seventy simulated user queries right four unit tests confirming that consolidated memory entries preserve critical repository paths",
        "refined_text": "Our cognitive agent memory architecture team upgraded long-term persistence routines inside memory_indexer.py by implementing structured episodic memory synthesis across agent task histories. Previously unmanaged conversation logs accumulated noisy redundant text, consuming 32768 context tokens across 10 multi-step sessions, evaluating 18 dialogue transcripts instead, by preserving unhelpful tool stack traces.\n\nThe memory engineers constructed a background consolidation service which extracts distilled user guidelines and technical facts across 24 developer interactions by running automated summarization passes before persistent indexing. When an autonomous development session concludes, the worker commits semantic embeddings across Postgres vector tables, synchronizing index partitions by updating nearest-neighbor indices across 16 memory partitions instead.\n\nInstruct Aider to evaluate episodic memory recall accuracy across 70 simulated user queries, and write 4 unit tests confirming that consolidated memory entries preserve critical repository paths."
    },

    # Sample 18: Agent behavioral regression runner in benchmark_runner.py
    {
        "raw_asr": "basically our pipeline reliability engineering team established continuous capability evaluation inside benchmark underscore runner dot py buy tracking agent tool invocation precision across prompt modifications previously unmonitored system prompt changes caused subtle reasoning degradations failing across sixteen coding benchmark problems wait twenty eight benchmark suites instead buy emitting malformed function arguments uh the test infrastructure developers created an automated evaluation harness which executes standardized prompt tasks across thirty five agent scenarios buy comparing generated tool sequences against ground truth trajectories so basically when an engineer updates system prompt templates the runner computes task success metrics across host c p u worker tasks wait recalculat capability scores buy evaluating tool accuracy across twenty evaluation rubrics instead okay so instruct cursor two benchmark regression suite execution duration across fifty simulated prompt variations right five unit tests validating that capability drops above five percent trigger c i build failures",
        "refined_text": "Our pipeline reliability engineering team established continuous capability evaluation inside benchmark_runner.py by tracking agent tool invocation precision across prompt modifications. Previously unmonitored system prompt changes caused subtle reasoning degradations, failing across 16 coding benchmark problems, evaluating 28 benchmark suites instead, by emitting malformed function arguments.\n\nThe test infrastructure developers created an automated evaluation harness which executes standardized prompt tasks across 35 agent scenarios by comparing generated tool sequences against ground truth trajectories. When an engineer updates system prompt templates, the runner computes task success metrics across host CPU worker tasks, recalculating capability scores by evaluating tool accuracy across 20 evaluation rubrics instead.\n\nInstruct Cursor to benchmark regression suite execution duration across 50 simulated prompt variations, and write 5 unit tests validating that capability drops above 5 percent trigger CI build failures."
    },

    # Sample 19: Multi-agent consensus arbiter in consensus_arbiter.py
    {
        "raw_asr": "um our distributed agent orchestration squad modernized collaborative decision resolution inside consensus underscore arbiter dot py buy establishing structured voting protocols across specialized agent personas previously unmanaged peer to peer agent debates resulted in circular argumentation deadlocks failing across twelve multi agent tasks wait twenty collaboration runs instead buy generating conflicting workspace file modifications uh the coordination engineers built a hierarchical arbitration module which aggregates task proposals from planner coder and reviewer agents across sixteen specialized roles buy verifying consensus thresholds before executing filesystem changes so basically when a coding agent proposes refactoring patches the arbiter routes candidate diffs across a sink i o message channels wait arbitrat merge conflicts buy conducting structured rebuttal exchanges across six verification gates instead okay so instruct claude two measure consensus resolution speed across forty five simulated team development runs right four unit tests validating that unapproved agent diffs are automatically rejected",
        "refined_text": "Our distributed agent orchestration squad modernized collaborative decision resolution inside consensus_arbiter.py by establishing structured voting protocols across specialized agent personas. Previously unmanaged peer-to-peer agent debates resulted in circular argumentation deadlocks, failing across 12 multi-agent tasks, evaluating 20 collaboration runs instead, by generating conflicting workspace file modifications.\n\nThe coordination engineers built a hierarchical arbitration module which aggregates task proposals from planner, coder, and reviewer agents across 16 specialized roles by verifying consensus thresholds before executing filesystem changes. When a coding agent proposes refactoring patches, the arbiter routes candidate diffs across asyncio message channels, arbitrating merge conflicts by conducting structured rebuttal exchanges across 6 verification gates instead.\n\nInstruct Claude to measure consensus resolution speed across 45 simulated team development runs, and write 4 unit tests validating that unapproved agent diffs are automatically rejected."
    },

    # Sample 20: Cross-encoder context reranker in context_reranker.py
    {
        "raw_asr": "basically our enterprise knowledge retrieval squad optimized context relevance filtering inside context underscore reranker dot py buy deploying deep cross attention rerankers across candidate documentation snippets previously standard dense vector similarity returned irrelevant context passages consuming six five five three six context tokens across fourteen complex technical queries wait twenty four search benchmarks instead buy injecting tangential documentation text uh the retrieval engineers built an asynchronous cross encoder scoring pipeline which calculates multi token relevance interactions across thirty candidate context passages buy predicting document utility probabilities before prompt assembly so basically when an autonomous agent searches internal repositories the reranker scores passage relevance across host c p u threads wait deduplicat redundant context chunks buy selecting top ranked passages across ten available prompt slots instead okay so instruct windsurf two measure cross encoder scoring latency across sixty simulated agent search tasks right five unit tests validating that candidate passages below relevance threshold are excluded",
        "refined_text": "Our enterprise knowledge retrieval squad optimized context relevance filtering inside context_reranker.py by deploying deep cross-attention rerankers across candidate documentation snippets. Previously standard dense vector similarity returned irrelevant context passages, consuming 65536 context tokens across 14 complex technical queries, evaluating 24 search benchmarks instead, by injecting tangential documentation text.\n\nThe retrieval engineers built an asynchronous cross-encoder scoring pipeline which calculates multi-token relevance interactions across 30 candidate context passages by predicting document utility probabilities before prompt assembly. When an autonomous agent searches internal repositories, the reranker scores passage relevance across host CPU threads, deduplicating redundant context chunks by selecting top-ranked passages across 10 available prompt slots instead.\n\nInstruct Windsurf to measure cross-encoder scoring latency across 60 simulated agent search tasks, and write 5 unit tests validating that candidate passages below relevance threshold are excluded."
    }
]

def main():
    print("=" * 60)
    print("VALIDATING BATCH 182 (DOMAIN 7: AI AGENT PROMPTING & LLM PIPELINES)")
    print("=" * 60)

    total_samples = len(batch)
    passed_pair_validation = 0
    passed_clean_sample = 0
    total_noise_layers = 0

    for idx, sample in enumerate(batch, 1):
        raw = sample["raw_asr"]
        refined = sample["refined_text"]
        words = len(refined.split())
        raw_words = len(raw.split())
        ratio = words / max(1, raw_words)

        # Check noise layers
        active_layers = count_active_noise_layers(raw)
        layer_count = sum(active_layers.values())
        total_noise_layers += layer_count

        # Target min noise layers: 3 for short, 4 for medium/long
        min_layers = 3 if words < 25 else 4
        is_valid, reason = validate_pair(sample, min_noise_layers=min_layers)
        if not is_valid:
            print(f"FAILED validate_pair on Sample {idx}: {reason}")
            print(f"  Raw: {raw}")
            print(f"  Refined: {refined}")
            sys.exit(1)
        passed_pair_validation += 1

        # Clean sample
        cleaned, status = clean_sample(raw, refined)
        if not cleaned:
            print(f"FAILED clean_sample on Sample {idx}: {status}")
            print(f"  Raw: {raw}")
            print(f"  Refined: {refined}")
            sys.exit(1)
        passed_clean_sample += 1

        print(f"Sample {idx:02d}: {words:3d} words, ratio {ratio:.2f}, {layer_count} noise layers -> OK")

    # Batch level validation
    is_batch_valid, batch_reason, tier_counts = validate_batch(
        batch, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    if not is_batch_valid:
        print(f"FAILED validate_batch: {batch_reason}")
        sys.exit(1)

    # Check leakage against sft_eval.json
    if eval_file.exists():
        for idx, sample in enumerate(batch, 1):
            if sample["raw_asr"].strip().lower() in eval_raws:
                print(f"LEAKAGE DETECTED on Sample {idx} (raw_asr matches eval)")
                sys.exit(1)
            if sample["refined_text"].strip().lower() in eval_refs:
                print(f"LEAKAGE DETECTED on Sample {idx} (refined_text matches eval)")
                sys.exit(1)
        print("Passed sft_eval.json zero leakage check.")

    # Save to target file
    out_path = Path("scratch/subagent_batch_182.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(batch)} verified samples to {out_path}")

    # Summary
    print("=" * 60)
    print("BATCH 182 VALIDATION SUMMARY:")
    print(f"  Total samples: {total_samples}")
    print(f"  validate_pair passed: {passed_pair_validation}/{total_samples}")
    print(f"  clean_sample passed: {passed_clean_sample}/{total_samples}")
    print(f"  Tiers: Short={tier_counts['short']}, Medium={tier_counts['medium']}, Long={tier_counts['long']}")
    print(f"  Average noise layers: {tier_counts['avg_noise_layers']} (target >= 4.0)")
    print(f"  Noise layer distribution: {tier_counts['noise_layer_distribution']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
