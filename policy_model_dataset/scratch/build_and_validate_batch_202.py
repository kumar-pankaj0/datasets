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
# Batch 202 Composition: 4 Short (<25 words), 6 Medium (25-89 words), 10 Long (90+ words)

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 sentence. Zero newlines. Max 1 cut-word. Active layers >= 3.
    # =========================================================================

    # Sample 1: Configure canary_router traffic splits
    {
        "raw_asr": "um configur canary underscore router traffic splits buy shifting ten canary requests four remote r p c handlers",
        "refined_text": "Configure canary_router traffic splits by shifting 10 canary requests for remote RPC handlers."
    },

    # Sample 2: Initialize template_buffer limits
    {
        "raw_asr": "uh initializ template underscore buffer limits buy allocating sixteen prompt slots two local c p u workers",
        "refined_text": "Initialize template_buffer limits by allocating 16 prompt slots to local CPU workers."
    },

    # Sample 3: Allocate schema_validator memory
    {
        "raw_asr": "basically allocat schema underscore validator memory buy assigning twenty schema rules two background a sink i o routines",
        "refined_text": "Allocate schema_validator memory by assigning 20 schema rules to background asyncio routines."
    },

    # Sample 4: Terminate backpressure_limiter workers
    {
        "raw_asr": "you know terminat backpressure underscore limiter workers buy committing eight throttle events two persistent post gres tables",
        "refined_text": "Terminate backpressure_limiter workers by committing 8 throttle events to persistent Postgres tables."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 5: ReAct scratchpad compaction in scratchpad_compactor
    {
        "raw_asr": "uh configur scratchpad compaction passes inside scratchpad underscore compactor buy evaluating repetitive thought loops across twelve execution traces wait evaluating twenty two candidate traces instead buy enforcing step significance thresholds basically prune redundant intermediate observations buy compressing thought tokens across a sink i o worker streams and right three unit tests verifying scratchpad compaction fidelity",
        "refined_text": "Configure scratchpad compaction passes inside scratchpad_compactor by evaluating repetitive thought loops across 12 execution traces, evaluating 22 candidate traces instead by enforcing step significance thresholds.\n\nPrune redundant intermediate observations by compressing thought tokens across asyncio worker streams, and write 3 unit tests verifying scratchpad compaction fidelity."
    },

    # Sample 6: Dynamic temperature scaling in temperature_controller
    {
        "raw_asr": "um initializ dynamic temperature scaling limits inside temperature underscore controller buy sampling model entropy values across sixteen generation windows wait sampling twenty four token batches instead buy tracking prediction perplexity boundaries you know damp output randomness buy adjusting logit sampling temperatures across host c p u threads and right four unit tests confirming temperature modulation stability",
        "refined_text": "Initialize dynamic temperature scaling limits inside temperature_controller by sampling model entropy values across 16 generation windows, sampling 24 token batches instead by tracking prediction perplexity boundaries.\n\nDamp output randomness by adjusting logit sampling temperatures across host CPU threads, and write 4 unit tests confirming temperature modulation stability."
    },

    # Sample 7: Sliding KV cache window in kv_window_manager
    {
        "raw_asr": "basically allocat sliding attention key value windows inside k v underscore window underscore manager buy indexing conversation history tokens across ten dialogue sessions wait indexing eighteen session contexts instead buy calculating attention head occupancy uh purge expired attention blocks buy evicting inactive tokens across post gres document tables and right three unit tests verifying key value window retention bounds",
        "refined_text": "Allocate sliding attention key-value windows inside kv_window_manager by indexing conversation history tokens across 10 dialogue sessions, indexing 18 session contexts instead by calculating attention head occupancy.\n\nPurge expired attention blocks by evicting inactive tokens across Postgres document tables, and write 3 unit tests verifying key-value window retention bounds."
    },

    # Sample 8: Agent loop detection in loop_detector
    {
        "raw_asr": "um recalculat agent execution loop thresholds inside loop underscore detector buy tracking repetitive tool call cycles across twelve autonomous trajectories wait tracking twenty agent sessions instead buy measuring tool hash collisions basically abort runaway execution spirals buy terminating stuck tasks across a sink i o event loops and right four unit tests validating loop detector interruption guarantees",
        "refined_text": "Recalculate agent execution loop thresholds inside loop_detector by tracking repetitive tool call cycles across 12 autonomous trajectories, tracking 20 agent sessions instead by measuring tool hash collisions.\n\nAbort runaway execution spirals by terminating stuck tasks across asyncio event loops, and write 4 unit tests validating loop detector interruption guarantees."
    },

    # Sample 9: Fallback orchestrator in fallback_orchestrator
    {
        "raw_asr": "uh communicat tool dispatch fallback routes inside fallback underscore orchestrator buy transmitting schema repair payloads across eight worker processes wait transmitting two sixteen remote r p c endpoints instead buy optimizing network bandwidth you know recover failed tool executions buy retrying degraded calls across host c p u threads and right three unit tests verifying fallback retry reliability",
        "refined_text": "Communicate tool dispatch fallback routes inside fallback_orchestrator by transmitting schema repair payloads across 8 worker processes, transmitting to 16 remote RPC endpoints instead by optimizing network bandwidth.\n\nRecover failed tool executions by retrying degraded calls across host CPU threads, and write 3 unit tests verifying fallback retry reliability."
    },

    # Sample 10: Human-in-the-loop approval broker in approval_broker
    {
        "raw_asr": "basically arbitrat privileged action approval requests inside approval underscore broker buy evaluating operator risk levels across six tool categories wait evaluating fourteen sensitive operation types instead buy inspecting system permission flags um quarantine unauthorized agent requests buy holding sensitive commands across host c p u queues and right four unit tests confirming operator approval escalation timeouts",
        "refined_text": "Arbitrate privileged action approval requests inside approval_broker by evaluating operator risk levels across 6 tool categories, evaluating 14 sensitive operation types instead by inspecting system permission flags.\n\nQuarantine unauthorized agent requests by holding sensitive commands across host CPU queues, and write 4 unit tests confirming operator approval escalation timeouts."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # Active noise layers >= 4 (target 5-6). Rationale with "by <action>".
    # =========================================================================

    # Sample 11: Multi-agent debate consensus in debate_coordinator.py
    {
        "raw_asr": "um our multi agent consensus engineering group redesigned collaborative debate arbitration inside debate underscore coordinator dot py buy deploying structured rebuttal rounds across divergent model outputs previously uncoordinated agent debate cycles produced circular reasoning deadlocks failing across fourteen complex benchmark tasks wait evaluating twenty six debate transcripts instead buy permitting unconstrained argumentation drift uh the coordination developers implemented an argument verification matrix which tracks claim validity across thirty two candidate debate turns buy evaluating premise consistency before final consensus synthesis so basically when specialist agents generate conflicting software design proposals the coordinator routes rebuttal payloads across remote r p c channels wait arbitrat contradictory claims buy enforcing structured voting rounds across eight consensus stages instead okay so instruct cursor two benchmark debate resolution latency across sixty simulated multi agent sessions right five unit tests validating that unverified claims trigger explicit debate rejection",
        "refined_text": "Our multi-agent consensus engineering group redesigned collaborative debate arbitration inside debate_coordinator.py by deploying structured rebuttal rounds across divergent model outputs. Previously uncoordinated agent debate cycles produced circular reasoning deadlocks, failing across 14 complex benchmark tasks, evaluating 26 debate transcripts instead, by permitting unconstrained argumentation drift.\n\nThe coordination developers implemented an argument verification matrix which tracks claim validity across 32 candidate debate turns by evaluating premise consistency before final consensus synthesis. When specialist agents generate conflicting software design proposals, the coordinator routes rebuttal payloads across remote RPC channels, arbitrating contradictory claims by enforcing structured voting rounds across 8 consensus stages instead.\n\nInstruct Cursor to benchmark debate resolution latency across 60 simulated multi-agent sessions, and write 5 unit tests validating that unverified claims trigger explicit debate rejection."
    },

    # Sample 12: Speculative decoding verification in speculative_verifier.py
    {
        "raw_asr": "basically our inference acceleration systems team overhauled speculative decoding verification inside speculative underscore verifier dot py buy implementing tree attention validation across small draft model candidate tokens previously serial draft token verification created execution bottlenecks failing across one six three eight four tokens across twelve generation benchmarks wait twenty four inference streams instead buy validating single draft branches uh the runtime engineers created an asynchronous token verification kernel which assesses draft token probabilities across thirty two speculative frames buy executing parallel forward passes before acceptance commitment so basically when a draft model generates candidate token sequences the verifier evaluates target logits across host c p u threads wait calibrat acceptance threshold weights buy pruning rejected draft tokens across sixteen parallel verification paths instead okay so instruct claude two measure speculative decoding throughput gains across fifty five simulated generation runs right four unit tests validating that rejected tokens trigger immediate draft rollback",
        "refined_text": "Our inference acceleration systems team overhauled speculative decoding verification inside speculative_verifier.py by implementing tree-attention validation across small draft model candidate tokens. Previously serial draft token verification created execution bottlenecks, failing across 16384 tokens across 12 generation benchmarks, evaluating 24 inference streams instead, by validating single draft branches.\n\nThe runtime engineers created an asynchronous token verification kernel which assesses draft token probabilities across 32 speculative frames by executing parallel forward passes before acceptance commitment. When a draft model generates candidate token sequences, the verifier evaluates target logits across host CPU threads, calibrating acceptance threshold weights by pruning rejected draft tokens across 16 parallel verification paths instead.\n\nInstruct Claude to measure speculative decoding throughput gains across 55 simulated generation runs, and write 4 unit tests validating that rejected tokens trigger immediate draft rollback."
    },

    # Sample 13: Prompt injection vector guard in prompt_vector_guard.py
    {
        "raw_asr": "um our platform safety engineering squad reconstructed prompt injection defense layers inside prompt underscore vector underscore guard dot py buy deploying semantic vector classification across external document passages previously naive regex string matchers allowed adversarial evasion attacks failing across fourteen red team benchmark suites wait twenty eight jailbreak datasets instead buy missing obfuscated instruction overrides uh the safety platform developers built an untrusted content quarantine proxy which scans embedding representations across thirty five ingested documents buy calculating cosine distance to known attack centroids before prompt hydration so basically when an autonomous agent consumes untrusted web search results the guard screens instruction vectors across post gres embedding tables wait initializ sandbox quarantine rules buy isolating malicious instruction payloads across eight inspection corridors instead okay so instruct windsurf two evaluate prompt injection classification latency across sixty simulated attack scenarios right five unit tests validating that detected jailbreak payloads trigger immediate input rejection",
        "refined_text": "Our platform safety engineering squad reconstructed prompt injection defense layers inside prompt_vector_guard.py by deploying semantic vector classification across external document passages. Previously naive regex string matchers allowed adversarial evasion attacks, failing across 14 red-team benchmark suites, evaluating 28 jailbreak datasets instead, by missing obfuscated instruction overrides.\n\nThe safety platform developers built an untrusted content quarantine proxy which scans embedding representations across 35 ingested documents by calculating cosine distance to known attack centroids before prompt hydration. When an autonomous agent consumes untrusted web search results, the guard screens instruction vectors across Postgres embedding tables, initializing sandbox quarantine rules by isolating malicious instruction payloads across 8 inspection corridors instead.\n\nInstruct Windsurf to evaluate prompt injection classification latency across 60 simulated attack scenarios, and write 5 unit tests validating that detected jailbreak payloads trigger immediate input rejection."
    },

    # Sample 14: Structured BNF grammar logit masking in grammar_mask_sampler.py
    {
        "raw_asr": "basically our agent tool runtime squad improved schema constrained generation inside grammar underscore mask underscore sampler dot py buy deploying b n f context free grammar masks across vocabulary logits previously unguided token sampling emitted syntax violations failing across twelve automated tool dispatch calls wait twenty two structured output validations instead buy producing unterminated json key arrays uh the inference engineers constructed an accelerated state automaton index which pre computes permitted token sequences across thirty registered schema types buy calculating token mask bitsets before model sampling so basically when a generation model predicts next token probabilities the sampler filters invalid syntax across host c p u threads wait recalculat token mask weights buy enforcing strict grammar transitions across sixteen valid schema tokens instead okay so instruct cursor two measure grammar constrained generation speed across seventy simulated structured tool calls right four unit tests validating that emitted responses adhere strictly two target schema models",
        "refined_text": "Our agent tool runtime squad improved schema-constrained generation inside grammar_mask_sampler.py by deploying BNF context-free grammar masks across vocabulary logits. Previously unguided token sampling emitted syntax violations, failing across 12 automated tool dispatch calls, evaluating 22 structured output validations instead, by producing unterminated JSON key arrays.\n\nThe inference engineers constructed an accelerated state automaton index which pre-computes permitted token sequences across 30 registered schema types by calculating token mask bitsets before model sampling. When a generation model predicts next-token probabilities, the sampler filters invalid syntax across host CPU threads, recalculating token mask weights by enforcing strict grammar transitions across 16 valid schema tokens instead.\n\nInstruct Cursor to measure grammar-constrained generation speed across 70 simulated structured tool calls, and write 4 unit tests validating that emitted responses adhere strictly to target schema models."
    },

    # Sample 15: Cross-model routing & cost arbitrator in model_routing_broker.py
    {
        "raw_asr": "um our model infrastructure efficiency group rebuilt dynamic request dispatching inside model underscore routing underscore broker dot py buy establishing cost and latency aware routing thresholds across inference providers previously static model dispatch logic routed all user queries to large models failing across ten cost budget evaluations wait twenty two benchmark workloads instead buy wasting compute on simple categorization requests uh the routing platform developers built a prompt complexity classifier which assesses input token reasoning depth across twenty eight incoming prompts buy analyzing semantic task features before model assignment so basically when an autonomous agent pipeline dispatches user queries the broker assigns execution paths across a sink i o network queues wait allocat fallback routing slots buy directing complex prompts across six frontier model endpoints instead okay so instruct claude two benchmark cross model routing efficiency across fifty simulated query distributions right five unit tests confirming that low complexity queries route exclusively two lightweight models",
        "refined_text": "Our model infrastructure efficiency group rebuilt dynamic request dispatching inside model_routing_broker.py by establishing cost and latency aware routing thresholds across inference providers. Previously static model dispatch logic routed all user queries to large models, failing across 10 cost budget evaluations, evaluating 22 benchmark workloads instead, by wasting compute on simple categorization requests.\n\nThe routing platform developers built a prompt complexity classifier which assesses input token reasoning depth across 28 incoming prompts by analyzing semantic task features before model assignment. When an autonomous agent pipeline dispatches user queries, the broker assigns execution paths across asyncio network queues, allocating fallback routing slots by directing complex prompts across 6 frontier model endpoints instead.\n\nInstruct Claude to benchmark cross-model routing efficiency across 50 simulated query distributions, and write 5 unit tests confirming that low-complexity queries route exclusively to lightweight models."
    },

    # Sample 16: Episodic memory graph extraction in episodic_extractor.py
    {
        "raw_asr": "basically our cognitive agent memory platform team overhauled long term interaction persistence inside episodic underscore extractor dot py buy establishing entity relationship graph extraction across multi turn dialogues previously raw chat history accumulation saturated three two seven six eight context tokens across twelve multi step agent sessions wait twenty four developer sessions instead buy retaining uncompressed tool debug output uh the memory platform developers created an asynchronous memory extraction daemon which synthesizes persistent user preferences and project facts across thirty conversation transcripts buy executing semantic entity resolution before database commit so basically when an autonomous software agent completes a coding session the extractor writes knowledge triplets across post gres graph tables wait synchronizat memory partitions buy refreshing vector search indices across twelve persistent storage clusters instead okay so instruct windsurf two evaluate episodic memory retrieval accuracy across sixty five simulated developer queries right four unit tests validating that stored memory triplets preserve essential system dependencies",
        "refined_text": "Our cognitive agent memory platform team overhauled long-term interaction persistence inside episodic_extractor.py by establishing entity relationship graph extraction across multi-turn dialogues. Previously raw chat history accumulation saturated 32768 context tokens across 12 multi-step agent sessions, evaluating 24 developer sessions instead, by retaining uncompressed tool debug output.\n\nThe memory platform developers created an asynchronous memory extraction daemon which synthesizes persistent user preferences and project facts across 30 conversation transcripts by executing semantic entity resolution before database commit. When an autonomous software agent completes a coding session, the extractor writes knowledge triplets across Postgres graph tables, synchronizing memory partitions by refreshing vector search indices across 12 persistent storage clusters instead.\n\nInstruct Windsurf to evaluate episodic memory retrieval accuracy across 65 simulated developer queries, and write 4 unit tests validating that stored memory triplets preserve essential system dependencies."
    },

    # Sample 17: Dynamic few-shot teleprompter in teleprompter_optimizer.py
    {
        "raw_asr": "um our prompt engineering systems squad modernized automated demonstration optimization inside teleprompter underscore optimizer dot py buy introducing metric guided few shot teleprompter compilation across specialized agent tasks previously handcrafted few shot prompt exemplars produced inconsistent model reasoning failing across fourteen domain benchmark suites wait twenty six evaluation runs instead buy selecting unrepresentative task demonstrations uh the optimization engineers designed an evolutionary exemplar search harness which scores prompt demonstration candidates across thirty two task examples buy computing validation metric score deltas before prompt publication so basically when an agent pipeline compiles domain instructions the optimizer evaluates trajectory success rates across host c p u threads wait terminat underperforming prompt variants buy eliminating low scoring exemplar candidates across eight optimization iterations instead okay so instruct aider two benchmark teleprompter convergence time across forty five simulated prompt tuning runs right five unit tests confirming that compiled system prompts maintain strict parameter accuracy",
        "refined_text": "Our prompt engineering systems squad modernized automated demonstration optimization inside teleprompter_optimizer.py by introducing metric-guided few-shot teleprompter compilation across specialized agent tasks. Previously handcrafted few-shot prompt exemplars produced inconsistent model reasoning, failing across 14 domain benchmark suites, evaluating 26 evaluation runs instead, by selecting unrepresentative task demonstrations.\n\nThe optimization engineers designed an evolutionary exemplar search harness which scores prompt demonstration candidates across 32 task examples by computing validation metric score deltas before prompt publication. When an agent pipeline compiles domain instructions, the optimizer evaluates trajectory success rates across host CPU threads, terminating underperforming prompt variants by eliminating low-scoring exemplar candidates across 8 optimization iterations instead.\n\nInstruct Aider to benchmark teleprompter convergence time across 45 simulated prompt tuning runs, and write 5 unit tests confirming that compiled system prompts maintain strict parameter accuracy."
    },

    # Sample 18: Sandboxed execution supervisor in sandbox_supervisor.py
    {
        "raw_asr": "basically our agent execution security platform team reconstructed container boundary isolation inside sandbox underscore supervisor dot py buy deploying microVM kernel isolation across dynamic tool execution commands previously unrestricted command execution routines created security vulnerabilities failing across sixteen penetration testing scenarios wait twenty eight sandbox runs instead buy permitting unmonitored child process spawns uh the security infrastructure engineers constructed a system call interception daemon which monitors environment variables and filesystem access across thirty isolated worker containers buy enforcing read only root mounts before process start so basically when an autonomous coding agent runs shell commands the supervisor intercepts privileged calls across host c p u threads wait communicat execution status buy transmitting isolated command output across eight background coroutines instead okay so instruct cursor two evaluate container spawn latency across fifty simulated agent execution jobs right four unit tests validating that file access outside slash tmp triggers immediate process termination",
        "refined_text": "Our agent execution security platform team reconstructed container boundary isolation inside sandbox_supervisor.py by deploying microVM kernel isolation across dynamic tool execution commands. Previously unrestricted command execution routines created security vulnerabilities, failing across 16 penetration testing scenarios, evaluating 28 sandbox runs instead, by permitting unmonitored child process spawns.\n\nThe security infrastructure engineers constructed a system call interception daemon which monitors environment variables and filesystem access across 30 isolated worker containers by enforcing read-only root mounts before process start. When an autonomous coding agent runs shell commands, the supervisor intercepts privileged calls across host CPU threads, communicating execution status by transmitting isolated command output across 8 background coroutines instead.\n\nInstruct Cursor to evaluate container spawn latency across 50 simulated agent execution jobs, and write 4 unit tests validating that file access outside /tmp triggers immediate process termination."
    },

    # Sample 19: Trajectory reward verifier in trajectory_reward_verifier.py
    {
        "raw_asr": "um our automated evaluation platform team overhauled multi step trajectory grading inside trajectory underscore reward underscore verifier dot py buy deploying step level process reward models across complex software refactoring tasks previously final outcome reward scoring missed intermediate reasoning errors failing across eighteen benchmark coding problems wait thirty candidate trajectories instead buy rewarding flawed intermediate code patches uh the evaluation platform developers designed a fine grained step verifier which computes state transition rewards across twenty four intermediate execution steps buy validating unit test assertion passes before terminal score assignment so basically when an autonomous agent refactors software repositories the verifier calculates process reward scores across host c p u threads wait deduplicat redundant trajectory branches buy pruning identical code diffs across ten exploration paths instead okay so instruct claude two benchmark trajectory verification throughput across sixty simulated agent refactoring tasks right five unit tests validating that intermediate syntax regressions trigger immediate trajectory penalization",
        "refined_text": "Our automated evaluation platform team overhauled multi-step trajectory grading inside trajectory_reward_verifier.py by deploying step-level process reward models across complex software refactoring tasks. Previously final outcome reward scoring missed intermediate reasoning errors, failing across 18 benchmark coding problems, evaluating 30 candidate trajectories instead, by rewarding flawed intermediate code patches.\n\nThe evaluation platform developers designed a fine-grained step verifier which computes state transition rewards across 24 intermediate execution steps by validating unit test assertion passes before terminal score assignment. When an autonomous agent refactors software repositories, the verifier calculates process reward scores across host CPU threads, deduplicating redundant trajectory branches by pruning identical code diffs across 10 exploration paths instead.\n\nInstruct Claude to benchmark trajectory verification throughput across 60 simulated agent refactoring tasks, and write 5 unit tests validating that intermediate syntax regressions trigger immediate trajectory penalization."
    },

    # Sample 20: Streaming backpressure demuxer in streaming_backpressure_demuxer.py
    {
        "raw_asr": "basically our real time streaming engineering squad upgraded token demuxing pipelines inside streaming underscore backpressure underscore demuxer dot py buy implementing non blocking token ring buffers across concurrent model output streams previously synchronous stream handling caused network buffer bloat exhausting four zero nine six streaming chunks across fourteen client sessions wait twenty six connection pipelines instead buy dropping late arriving tool call chunks uh the streaming infrastructure developers created an event driven demuxing loop which demuxes reasoning tokens and tool arguments across thirty five active client streams buy enforcing backpressure flow windows before dispatch so basically when an l l m streams partial json tool invocations the demuxer routes execution payloads across a sink i o event loops wait configur stream buffer capacity buy tuning high watermark limits across eight socket channels instead okay so instruct windsurf two measure streaming demuxing latency under load across seventy simulated client streams right four unit tests validating that buffer saturation triggers proactive client throttle signals",
        "refined_text": "Our real-time streaming engineering squad upgraded token demuxing pipelines inside streaming_backpressure_demuxer.py by implementing non-blocking token ring buffers across concurrent model output streams. Previously synchronous stream handling caused network buffer bloat, exhausting 4096 streaming chunks across 14 client sessions, evaluating 26 connection pipelines instead, by dropping late-arriving tool call chunks.\n\nThe streaming infrastructure developers created an event-driven demuxing loop which demuxes reasoning tokens and tool arguments across 35 active client streams by enforcing backpressure flow windows before dispatch. When an LLM streams partial JSON tool invocations, the demuxer routes execution payloads across asyncio event loops, configuring stream buffer capacity by tuning high watermark limits across 8 socket channels instead.\n\nInstruct Windsurf to measure streaming demuxing latency under load across 70 simulated client streams, and write 4 unit tests validating that buffer saturation triggers proactive client throttle signals."
    }
]

def main():
    print("=" * 60)
    print("VALIDATING BATCH 202 (DOMAIN 7: AI AGENT PROMPTING & LLM PIPELINES)")
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
    out_path = Path("scratch/subagent_batch_202.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(batch)} verified samples to {out_path}")

    # Summary
    print("=" * 60)
    print("BATCH 202 VALIDATION SUMMARY:")
    print(f"  Total samples: {total_samples}")
    print(f"  validate_pair passed: {passed_pair_validation}/{total_samples}")
    print(f"  clean_sample passed: {passed_clean_sample}/{total_samples}")
    print(f"  Tiers: Short={tier_counts['short']}, Medium={tier_counts['medium']}, Long={tier_counts['long']}")
    print(f"  Average noise layers: {tier_counts['avg_noise_layers']} (target >= 4.0)")
    print(f"  Noise layer distribution: {tier_counts['noise_layer_distribution']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
