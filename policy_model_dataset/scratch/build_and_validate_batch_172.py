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
# Batch 172 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. Zero newlines. Max 1 cut-word. Active layers >= 3.
    # =========================================================================

    # Sample 1: Calibrate vector_index thresholds
    {
        "raw_asr": "um calibrat vector underscore index thresholds buy setting cosine bounds four local c p u workers",
        "refined_text": "Calibrate vector_index thresholds by setting cosine bounds for local CPU workers."
    },

    # Sample 2: Initialize rate_limiter tokens
    {
        "raw_asr": "uh initializ rate underscore limiter tokens buy assigning twenty requests two external r p c clients",
        "refined_text": "Initialize rate_limiter tokens by assigning 20 requests to external RPC clients."
    },

    # Sample 3: Terminate session_queue workers
    {
        "raw_asr": "basically terminat session underscore queue workers buy enforcing five second timeouts four a sink i o tasks",
        "refined_text": "Terminate session_queue workers by enforcing 5 second timeouts for asyncio tasks."
    },

    # Sample 4: Recalculate prompt_cache bounds
    {
        "raw_asr": "you know recalculat prompt underscore cache bounds buy offloading eight shards two post gres tables",
        "refined_text": "Recalculate prompt_cache bounds by offloading 8 shards to Postgres tables."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 5: Exemplar selector in exemplar_selector.py
    {
        "raw_asr": "uh configur few shot demonstration passes inside exemplar underscore selector dot py buy retrieving semantic nearest neighbors across twelve candidate prompts wait twenty four demonstration pairs instead buy enforcing similarity ranking basically prune low scoring candidate prompts buy measuring embedding cosine distances across a sink i o workers right three unit tests verifying prompt selector recall",
        "refined_text": "Configure few-shot demonstration passes inside exemplar_selector.py by retrieving semantic nearest neighbors across 12 candidate prompts, evaluating 24 demonstration pairs instead by enforcing similarity ranking.\n\nPrune low-scoring candidate prompts by measuring embedding cosine distances across asyncio workers. Write 3 unit tests verifying prompt selector recall."
    },

    # Sample 6: JSON schema generator in schema_generator.py
    {
        "raw_asr": "um initializ j son schema extraction routines inside schema underscore generator dot py buy compiling python type annotations across sixteen tool definitions wait twenty eight function parameters instead buy enforcing strict typing boundaries you know filter unsupported recursive data structures buy inspecting nested dictionary schemas across host c p u threads right four unit tests confirming parameter schema generation",
        "refined_text": "Initialize JSON schema extraction routines inside schema_generator.py by compiling Python type annotations across 16 tool definitions, validating 28 function parameters instead by enforcing strict typing boundaries.\n\nFilter unsupported recursive data structures by inspecting nested dictionary schemas across host CPU threads. Write 4 unit tests confirming parameter schema generation."
    },

    # Sample 7: Self-reflection scratchpad in reflection_engine.py
    {
        "raw_asr": "basically allocat self reflection scratchpad buffers inside reflection underscore engine dot py buy capturing execution traceback frames across ten failed tool steps wait eighteen execution attempts instead buy isolating primary exception messages uh mitigat repetitive plan failure cycles buy appending structured critique hints across post gres session records right three unit tests verifying reflection loop convergence",
        "refined_text": "Allocate self-reflection scratchpad buffers inside reflection_engine.py by capturing execution traceback frames across 10 failed tool steps, analyzing 18 execution attempts instead by isolating primary exception messages.\n\nMitigate repetitive plan failure cycles by appending structured critique hints across Postgres session records. Write 3 unit tests verifying reflection loop convergence."
    },

    # Sample 8: Token budget allocator in budget_manager.py
    {
        "raw_asr": "um recalculat token allocation quotas inside budget underscore manager dot py buy distributing context capacity across fourteen active tool schemas wait twenty two schema definitions instead buy bounding parameter documentation length basically throttle long model generation streams buy monitoring output token consumption across a sink i o event channels right four unit tests validating dynamic budget partition bounds",
        "refined_text": "Recalculate token allocation quotas inside budget_manager.py by distributing context capacity across 14 active tool schemas, reserving 22 schema definitions instead by bounding parameter documentation length.\n\nThrottle long model generation streams by monitoring output token consumption across asyncio event channels. Write 4 unit tests validating dynamic budget partition bounds."
    },

    # Sample 9: Multi-agent RPC coordinator in agent_coordinator.py
    {
        "raw_asr": "uh communicat distributed agent coordination parameters inside agent underscore coordinator dot py buy dispatching execution payloads across eight worker processes wait routing two fourteen remote r p c nodes instead buy balancing subtask workload distribution you know synchronizat shared state transitions buy propagating atomic task completion signals across host c p u threads right three unit tests verifying distributed coordination timeouts",
        "refined_text": "Communicate distributed agent coordination parameters inside agent_coordinator.py by dispatching execution payloads across 8 worker processes, routing to 14 remote RPC nodes instead by balancing subtask workload distribution.\n\nSynchronize shared state transitions by propagating atomic task completion signals across host CPU threads. Write 3 unit tests verifying distributed coordination timeouts."
    },

    # Sample 10: Dynamic system prompt compressor in prompt_compressor.py
    {
        "raw_asr": "basically deduplicat system prompt instruction lines inside prompt underscore compressor dot py buy pruning repetitive role formatting across sixteen template sections wait twenty six prompt directives instead buy discarding redundant conversational guidelines um compress system prompt token usage buy caching precomputed token representations across host c p u memory buffers right four unit tests confirming compression ratio accuracy",
        "refined_text": "Deduplicate system prompt instruction lines inside prompt_compressor.py by pruning repetitive role formatting across 16 template sections, evaluating 26 prompt directives instead by discarding redundant conversational guidelines.\n\nCompress system prompt token usage by caching precomputed token representations across host CPU memory buffers. Write 4 unit tests confirming compression ratio accuracy."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 11: Tool call hallucination detection in hallucination_guard.py
    {
        "raw_asr": "um our agent runtime reliability squad refactored tool validation routines inside hallucination underscore guard dot py buy introducing strict schema verification across model function calls previously unvalidated tool arguments produced fatal runtime exceptions failing across sixteen autonomous task iterations wait twenty eight tool executions instead buy passing hallucinated parameter keys uh the platform developers deployed a deterministic argument validator which compares model output keys against registered j son schemas across twenty four agent tools buy verifying parameter types before execution so basically when a language model hallucinates fictitious arguments the guardrail intercepts payload delivery across host c p u threads wait terminat malformed execution requests buy returning corrective feedback prompts across eight recovery iterations instead okay so instruct cursor two benchmark tool validation throughput across sixty simulated agent calls right five unit tests validating that missing required fields trigger immediate validation exceptions",
        "refined_text": "Our agent runtime reliability squad refactored tool validation routines inside hallucination_guard.py by introducing strict schema verification across model function calls. Previously unvalidated tool arguments produced fatal runtime exceptions, failing across 16 autonomous task iterations, evaluating 28 tool executions instead, by passing hallucinated parameter keys.\n\nThe platform developers deployed a deterministic argument validator which compares model output keys against registered JSON schemas across 24 agent tools by verifying parameter types before execution. When a language model hallucinates fictitious arguments, the guardrail intercepts payload delivery across host CPU threads, terminating malformed execution requests by returning corrective feedback prompts across 8 recovery iterations instead.\n\nInstruct Cursor to benchmark tool validation throughput across 60 simulated agent calls, and write 5 unit tests validating that missing required fields trigger immediate validation exceptions."
    },

    # Sample 12: Loop recursion limiter in recursion_guard.py
    {
        "raw_asr": "basically our core agent orchestration squad hardened execution loop safeguards inside recursion underscore guard dot py buy establishing maximum step thresholds across autonomous task graphs previously unconstrained agent reasoning loops encountered runaway recursion exhausting eight one nine two context tokens across fourteen reasoning passes wait twenty six execution steps instead buy repeating identical tool invocations uh the infrastructure engineers implemented a cyclic graph detector which tracks trajectory fingerprints across thirty two sequential tool actions buy hashing parameter signatures before subtask invocation so basically when an autonomous agent enters a circular reasoning pattern the execution supervisor analyzes state transitions across a sink i o streams wait terminat runaway subtask pipelines buy injecting human escalation signals across six decision boundaries instead okay so instruct claude two evaluate loop termination latency across fifty five simulated agent benchmarks right four unit tests confirming that infinite tool recursion triggers safe fallback handlers",
        "refined_text": "Our core agent orchestration squad hardened execution loop safeguards inside recursion_guard.py by establishing maximum step thresholds across autonomous task graphs. Previously unconstrained agent reasoning loops encountered runaway recursion, exhausting 8192 context tokens across 14 reasoning passes, evaluating 26 execution steps instead, by repeating identical tool invocations.\n\nThe infrastructure engineers implemented a cyclic graph detector which tracks trajectory fingerprints across 32 sequential tool actions by hashing parameter signatures before subtask invocation. When an autonomous agent enters a circular reasoning pattern, the execution supervisor analyzes state transitions across asyncio streams, terminating runaway subtask pipelines by injecting human escalation signals across 6 decision boundaries instead.\n\nInstruct Claude to evaluate loop termination latency across 55 simulated agent benchmarks, and write 4 unit tests confirming that infinite tool recursion triggers safe fallback handlers."
    },

    # Sample 13: Hybrid RAG retriever in hybrid_retriever.py
    {
        "raw_asr": "um our retrieval platform engineering group redesigned hybrid context retrieval inside hybrid underscore retriever dot py buy deploying reciprocal rank fusion across enterprise knowledge bases previously pure dense vector search failed on exact identifier queries missing crucial technical passages across eighteen benchmark queries wait thirty retrieval runs instead buy ignoring lexical keyword matches uh the retrieval developers constructed a dual stage ranking harness which blends b m two five lexical scores with dense embedding vectors across forty technical documentation collections buy computing normalized rank weights before document assembly so basically when an agent query requests specific configuration parameters the pipeline queries inverted indices across post gres document tables wait recalculat reciprocal rank scores buy merging top candidate passages across twelve retrieval shards instead okay so instruct windsurf two benchmark hybrid retrieval precision across seventy domain questions right four unit tests validating that exact token matches receive top rank priority",
        "refined_text": "Our retrieval platform engineering group redesigned hybrid context retrieval inside hybrid_retriever.py by deploying reciprocal rank fusion across enterprise knowledge bases. Previously pure dense vector search failed on exact identifier queries, missing crucial technical passages across 18 benchmark queries, evaluating 30 retrieval runs instead, by ignoring lexical keyword matches.\n\nThe retrieval developers constructed a dual-stage ranking harness which blends BM25 lexical scores with dense embedding vectors across 40 technical documentation collections by computing normalized rank weights before document assembly. When an agent query requests specific configuration parameters, the pipeline queries inverted indices across Postgres document tables, recalculating reciprocal rank scores by merging top candidate passages across 12 retrieval shards instead.\n\nInstruct Windsurf to benchmark hybrid retrieval precision across 70 domain questions, and write 4 unit tests validating that exact token matches receive top rank priority."
    },

    # Sample 14: ReAct reasoning trace parser in react_parser.py
    {
        "raw_asr": "basically our autonomous agent core squad revamped stream processing routines inside react underscore parser dot py buy implementing streaming token boundary parsing across multi turn reasoning traces previously monolithic output parsing blocked downstream tool execution delaying response delivery across sixteen conversational turns wait twenty four interaction cycles instead buy waiting four complete model outputs uh the systems developers implemented an incremental state machine which isolates thought blocks from action invocations across twenty streaming tokens buy evaluating regex delimiter patterns on arrival so basically when an l l m generates structured thought tokens the parser routes execution events across host c p u threads wait communicat subtask parameters buy dispatching early tool payloads across eight worker coroutines instead okay so instruct cursor two measure streaming parsing latency across sixty five simulated agent trajectories right five unit tests validating that malformed action delimiters raise explicit parser warnings",
        "refined_text": "Our autonomous agent core squad revamped stream processing routines inside react_parser.py by implementing streaming token boundary parsing across multi-turn reasoning traces. Previously monolithic output parsing blocked downstream tool execution, delaying response delivery across 16 conversational turns, evaluating 24 interaction cycles instead, by waiting for complete model outputs.\n\nThe systems developers implemented an incremental state machine which isolates thought blocks from action invocations across 20 streaming tokens by evaluating regex delimiter patterns on arrival. When an LLM generates structured thought tokens, the parser routes execution events across host CPU threads, communicating subtask parameters by dispatching early tool payloads across 8 worker coroutines instead.\n\nInstruct Cursor to measure streaming parsing latency across 65 simulated agent trajectories, and write 5 unit tests validating that malformed action delimiters raise explicit parser warnings."
    },

    # Sample 15: Dynamic context window partitioner in context_partitioner.py
    {
        "raw_asr": "um our inference platform optimization squad restructured dynamic context allocation inside context underscore partitioner dot py buy introducing proportional token budgets across active conversation components previously static context limits overflowed available capacity truncating system instructions across one six three eight four context tokens over twelve dialogue turns wait twenty two conversational sessions instead buy prioritizing recent chat history uh the platform engineers designed an adaptive partition manager which divides context capacity among system instructions episodic memory and tool results across eighteen task categories buy calculating dynamic token reservations before request submission so basically when a user prompt includes large repository context the partitioner compacts retrieval chunks across a sink i o worker tasks wait allocat context slots buy preserving essential system guidelines across four zero nine six tokens instead okay so instruct claude two benchmark context assembly throughput across fifty simulated agent requests right four unit tests confirming that system prompt boundaries remain strictly protected against memory overflow",
        "refined_text": "Our inference platform optimization squad restructured dynamic context allocation inside context_partitioner.py by introducing proportional token budgets across active conversation components. Previously static context limits overflowed available capacity, truncating system instructions across 16384 context tokens over 12 dialogue turns, evaluating 22 conversational sessions instead, by prioritizing recent chat history.\n\nThe platform engineers designed an adaptive partition manager which divides context capacity among system instructions, episodic memory, and tool results across 18 task categories by calculating dynamic token reservations before request submission. When a user prompt includes large repository context, the partitioner compacts retrieval chunks across asyncio worker tasks, allocating context slots by preserving essential system guidelines across 4096 tokens instead.\n\nInstruct Claude to benchmark context assembly throughput across 50 simulated agent requests, and write 4 unit tests confirming that system prompt boundaries remain strictly protected against memory overflow."
    },

    # Sample 16: Grammar-constrained structured output generation in outlines_sampler.py
    {
        "raw_asr": "basically our agent safety and parsing infrastructure group optimized structured output generation inside outlines underscore sampler dot py buy integrating deterministic finite state automata across token logit processors previously unconstrained model generation produced invalid j son syntax failing across fourteen automated tool executions wait twenty six integration workflows instead buy emitting malformed escape characters uh the runtime developers constructed a grammar guided sampling indexer which translates pydantic model schemas into regular expression transition graphs across thirty target entities buy precomputing valid next token bitmasks before generation so basically when the foundation model samples next token probabilities the sampler masks illegal vocabulary ids across host c p u threads wait initializ transition states buy restricting output tokens across twelve valid j son tokens instead okay so instruct cursor two benchmark grammar constrained decoding latency across sixty simulated agent prompts right five unit tests validating that generated payloads deserialize cleanly without j son decode exceptions",
        "refined_text": "Our agent safety and parsing infrastructure group optimized structured output generation inside outlines_sampler.py by integrating deterministic finite state automata across token logit processors. Previously unconstrained model generation produced invalid JSON syntax, failing across 14 automated tool executions, evaluating 26 integration workflows instead, by emitting malformed escape characters.\n\nThe runtime developers constructed a grammar-guided sampling indexer which translates Pydantic model schemas into regular expression transition graphs across 30 target entities by precomputing valid next-token bitmasks before generation. When the foundation model samples next-token probabilities, the sampler masks illegal vocabulary IDs across host CPU threads, initializing transition states by restricting output tokens across 12 valid JSON tokens instead.\n\nInstruct Cursor to benchmark grammar-constrained decoding latency across 60 simulated agent prompts, and write 5 unit tests validating that generated payloads deserialize cleanly without JSON decode exceptions."
    },

    # Sample 17: Agent memory consolidation in memory_consolidator.py
    {
        "raw_asr": "um our cognitive agent memory squad enhanced long term knowledge retention inside memory underscore consolidator dot py buy establishing automated episodic memory summarization across conversation histories previously unpruned agent scratchpads accumulated redundant observations exhausting three two seven six eight context tokens across ten multi step tasks wait eighteen execution sessions instead buy retaining repetitive tool error dumps uh the memory engineers built an asynchronous consolidation daemon which extracts salient user preferences and code facts across twenty four episodic dialogue transcripts buy running structured summarization passes before persistent indexing so basically when an agent session concludes the daemon commits distilled semantic facts across post gres relational tables wait synchronizat vector embeddings buy indexing condensed memory representations across sixteen memory partitions instead okay so instruct aid er two measure memory retrieval accuracy across seventy simulated user queries right four unit tests verifying that consolidated memory items preserve critical project configuration facts",
        "refined_text": "Our cognitive agent memory squad enhanced long-term knowledge retention inside memory_consolidator.py by establishing automated episodic memory summarization across conversation histories. Previously unpruned agent scratchpads accumulated redundant observations, exhausting 32768 context tokens across 10 multi-step tasks, evaluating 18 execution sessions instead, by retaining repetitive tool error dumps.\n\nThe memory engineers built an asynchronous consolidation daemon which extracts salient user preferences and code facts across 24 episodic dialogue transcripts by running structured summarization passes before persistent indexing. When an agent session concludes, the daemon commits distilled semantic facts across Postgres relational tables, synchronizing vector embeddings by indexing condensed memory representations across 16 memory partitions instead.\n\nInstruct Aider to measure memory retrieval accuracy across 70 simulated user queries, and write 4 unit tests verifying that consolidated memory items preserve critical project configuration facts."
    },

    # Sample 18: Prompt regression test harness in prompt_regression.py
    {
        "raw_asr": "basically our l l m pipeline quality engineering group established automated behavioral regression testing inside prompt underscore regression dot py buy evaluating agent tool accuracy across model checkpoint releases previously unmonitored system prompt adjustments introduced silent capability degradation failing across sixteen benchmark coding tasks wait twenty eight evaluation suites instead buy generating non standard tool parameters uh the test infrastructure engineers constructed an offline evaluation runner which executes standardized prompt scenarios across thirty five autonomous agent test cases buy comparing generated tool calls against golden baseline trajectories so basically when a pull request modifies system prompt templates the test harness computes pass rates across host c p u worker processes wait recalculat regression scores buy evaluating output schema conformance across twenty evaluation rubrics instead okay so instruct cursor two benchmark regression test execution speed across fifty simulated prompt evaluations right five unit tests validating that behavioral regressions above five percent trigger c i pipeline failures",
        "refined_text": "Our LLM pipeline quality engineering group established automated behavioral regression testing inside prompt_regression.py by evaluating agent tool accuracy across model checkpoint releases. Previously unmonitored system prompt adjustments introduced silent capability degradation, failing across 16 benchmark coding tasks, evaluating 28 evaluation suites instead, by generating non-standard tool parameters.\n\nThe test infrastructure engineers constructed an offline evaluation runner which executes standardized prompt scenarios across 35 autonomous agent test cases by comparing generated tool calls against golden baseline trajectories. When a pull request modifies system prompt templates, the test harness computes pass rates across host CPU worker processes, recalculating regression scores by evaluating output schema conformance across 20 evaluation rubrics instead.\n\nInstruct Cursor to benchmark regression test execution speed across 50 simulated prompt evaluations, and write 5 unit tests validating that behavioral regressions above 5 percent trigger CI pipeline failures."
    },

    # Sample 19: Multi-agent supervisor in supervisor_hub.py
    {
        "raw_asr": "um our distributed autonomous systems group upgraded multi agent task orchestration inside supervisor underscore hub dot py buy implementing dynamic role delegation across specialized agent personas previously uncoordinated peer to peer agent communication triggered conflicting file edits corrupting workspace state across twelve collaborative tasks wait twenty multi agent missions instead buy executing unsynchronized tool modifications uh the coordination engineers created a centralized supervisor module which delegates discrete subtasks to planner coder and reviewer agents across sixteen specialized roles buy tracking task dependencies before delegating execution locks so basically when a coding agent completes localized refactoring steps the supervisor dispatches diff payloads across a sink i o message queues wait arbitrat conflicting code proposals buy enforcing peer review sign offs across six verification gates instead okay so instruct claude two benchmark supervisor routing latency across forty five simulated collaborative development runs right four unit tests validating that unapproved agent modifications are automatically reverted",
        "refined_text": "Our distributed autonomous systems group upgraded multi-agent task orchestration inside supervisor_hub.py by implementing dynamic role delegation across specialized agent personas. Previously uncoordinated peer-to-peer agent communication triggered conflicting file edits, corrupting workspace state across 12 collaborative tasks, evaluating 20 multi-agent missions instead, by executing unsynchronized tool modifications.\n\nThe coordination engineers created a centralized supervisor module which delegates discrete subtasks to planner, coder, and reviewer agents across 16 specialized roles by tracking task dependencies before delegating execution locks. When a coding agent completes localized refactoring steps, the supervisor dispatches diff payloads across asyncio message queues, arbitrating conflicting proposals by conducting structured rebuttal exchanges across 6 verification gates instead.\n\nInstruct Claude to benchmark supervisor routing latency across 45 simulated collaborative development runs, and write 4 unit tests validating that unapproved agent modifications are automatically reverted."
    },

    # Sample 20: Cross-encoder context reranker in passage_reranker.py
    {
        "raw_asr": "basically our enterprise r a g platform squad overhauled context filtering pipelines inside passage underscore reranker dot py buy deploying a cross encoder model across retrieved reference documents previously raw vector similarity rankings included noisy irrelevant snippets consuming six five five three six context tokens across fourteen enterprise queries wait twenty four benchmark retrieval tasks instead buy flooding prompt context with tangential text uh the retrieval engineers constructed an asynchronous cross encoder scoring stage which computes deep token interactions across thirty candidate context chunks buy evaluating relevance probabilities before prompt injection so basically when an autonomous agent gathers reference materials from documentation stores the reranker evaluates passage relevance across host c p u threads wait deduplicat overlapping text snippets buy retaining top candidate passages across ten ranked slots instead okay so instruct windsurf two benchmark reranker inference latency across sixty simulated agent retrieval queries right five unit tests validating that low relevance passages below threshold are dropped",
        "refined_text": "Our enterprise RAG platform squad overhauled context filtering pipelines inside passage_reranker.py by deploying a cross-encoder model across retrieved reference documents. Previously raw vector similarity rankings included noisy irrelevant snippets, consuming 65536 context tokens across 14 enterprise queries, evaluating 24 benchmark retrieval tasks instead, by flooding prompt context with tangential text.\n\nThe retrieval engineers constructed an asynchronous cross-encoder scoring stage which computes deep token interactions across 30 candidate context chunks by evaluating relevance probabilities before prompt injection. When an autonomous agent gathers reference materials from documentation stores, the reranker evaluates passage relevance across host CPU threads, deduplicating overlapping text snippets by retaining top candidate passages across 10 ranked slots instead.\n\nInstruct Windsurf to benchmark reranker inference latency across 60 simulated agent retrieval queries, and write 5 unit tests validating that low-relevance passages below threshold are dropped."
    }
]

def main():
    print("=" * 60)
    print("VALIDATING BATCH 172 (DOMAIN 7: AI AGENT PROMPTING & LLM PIPELINES)")
    print("=" * 60)

    # 1. Individual sample validation
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

    # 2. Batch level validation
    is_batch_valid, batch_reason, tier_counts = validate_batch(
        batch, min_short=4, min_medium=6, min_long=10, min_noise_layers=4
    )
    if not is_batch_valid:
        print(f"FAILED validate_batch: {batch_reason}")
        sys.exit(1)

    # 3. Check leakage against sft_eval.json
    if eval_file.exists():
        for idx, sample in enumerate(batch, 1):
            if sample["raw_asr"].strip().lower() in eval_raws:
                print(f"LEAKAGE DETECTED on Sample {idx} (raw_asr matches eval)")
                sys.exit(1)
            if sample["refined_text"].strip().lower() in eval_refs:
                print(f"LEAKAGE DETECTED on Sample {idx} (refined_text matches eval)")
                sys.exit(1)
        print("Passed sft_eval.json zero leakage check.")

    # 4. Save to target file
    out_path = Path("scratch/subagent_batch_172.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(batch)} verified samples to {out_path}")

    # Summary
    print("=" * 60)
    print("BATCH 172 VALIDATION SUMMARY:")
    print(f"  Total samples: {total_samples}")
    print(f"  validate_pair passed: {passed_pair_validation}/{total_samples}")
    print(f"  clean_sample passed: {passed_clean_sample}/{total_samples}")
    print(f"  Tiers: Short={tier_counts['short']}, Medium={tier_counts['medium']}, Long={tier_counts['long']}")
    print(f"  Average noise layers: {tier_counts['avg_noise_layers']} (target >= 4.0)")
    print(f"  Noise layer distribution: {tier_counts['noise_layer_distribution']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
