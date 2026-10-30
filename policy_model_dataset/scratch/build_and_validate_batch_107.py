import json
import sys
import os
from pathlib import Path

# Add code directory to path
sys.path.insert(0, os.path.abspath("code"))

from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch = [
    # =========================================================================
    # Tier 1: Short Utterances (< 25 words) - Exactly 4 samples (Samples 1-4)
    # Exactly 1 grammatically complete sentence. Zero newlines. Max 1 cut-word.
    # Content words >= 11-13. Rationale with "by <action>". No decimals, no dotted filenames.
    # =========================================================================

    # Sample 1: Conversation buffer compaction
    {
        "raw_asr": "um instruct the orchestrator two compact conversation history buy discarding tool output payloads older than ten turns",
        "refined_text": "Instruct the orchestrator to compact conversation history by discarding tool output payloads older than 10 turns."
    },

    # Sample 2: Tool argument type validation
    {
        "raw_asr": "uh validat tool parameter arguments buy enforcing strict schema constraints across incoming agent function calls",
        "refined_text": "Validate tool parameter arguments by enforcing strict schema constraints across incoming agent function calls."
    },

    # Sample 3: Prompt injection mitigation
    {
        "raw_asr": "basically isolat untrusted user prompts buy scoring input tokens against a prompt injection classifier",
        "refined_text": "Isolate untrusted user prompts by scoring input tokens against a prompt injection classifier."
    },

    # Sample 4: Speculative draft token verification
    {
        "raw_asr": "um synchroniz candidate draft tokens buy matching speculative predictions against target model logits",
        "refined_text": "Synchronize candidate draft tokens by matching speculative predictions against target model logits."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # =========================================================================

    # Sample 5: MCP Server SSE Transport and Tool Discovery
    {
        "raw_asr": "uh configur our m c p gateway client inside mcp underscore transport dot py buy registering four remote tool endpoints wait eight remote tool endpoints instead across persistent s s e connections basically terminat idle connection streams buy applying a heartbeat interval of thirty seconds um right four unit tests validating automatic stream reconnects",
        "refined_text": "Configure our MCP gateway client inside mcp_transport.py by registering 8 remote tool endpoints instead across persistent SSE connections.\n\nTerminate idle connection streams by applying a heartbeat interval of 30 seconds. Write 4 unit tests validating automatic stream reconnects."
    },

    # Sample 6: RAG Late Chunking and Contextual Retrieval
    {
        "raw_asr": "um optimiz our r a g embedding pipeline inside chunk underscore encoder dot py buy applying late chunking across long document embeddings wait five one two tokens instead buy preserving contextual dependencies across chunk boundaries okay so right five test assertions verifying that the retriever passes top ten candidate passages towards the reranker",
        "refined_text": "Optimize our RAG embedding pipeline inside chunk_encoder.py by applying late chunking across long document embeddings, using 512 tokens instead while preserving contextual dependencies across chunk boundaries.\n\nWrite 5 test assertions verifying that the retriever passes top 10 candidate passages towards the reranker."
    },

    # Sample 7: Agentic Reflection and Lint Feedback Loop
    {
        "raw_asr": "basically prompt claude two refact our agent self reflection loop inside feedback underscore runner dot py buy feeding linter diagnostic errors back into the model prompt wait three iteration loops instead buy capping recursive repair attempts um right six unit tests verifying that syntax errors trigger automated code regeneration",
        "refined_text": "Prompt Claude to refactor our agent self-reflection loop inside feedback_runner.py by feeding linter diagnostic errors back into the model prompt, capping recursive repair attempts at 3 iteration loops instead.\n\nWrite 6 unit tests verifying that syntax errors trigger automated code regeneration."
    },

    # Sample 8: Dynamic Few-Shot Exemplar Selection via Vector Distance
    {
        "raw_asr": "uh direct cursor two implement dynamic few shot exemplar selection inside exemplar underscore selector dot py buy selecting two demonstration examples wait four demonstration examples instead buy computing cosine distance against incoming queries um right five unit tests confirming that selected prompt exemplars match user query domains",
        "refined_text": "Direct Cursor to implement dynamic few-shot exemplar selection inside exemplar_selector.py by selecting 4 demonstration examples instead by computing cosine distance against incoming queries.\n\nWrite 5 unit tests confirming that selected prompt exemplars match user query domains."
    },

    # Sample 9: Token Bucket Rate Limiting for Parallel Agent Dispatch
    {
        "raw_asr": "basically tell windsurf two configur our token bucket limiter inside rate_tracker dot py buy monitoring sliding window consumption across ten worker threads wait twenty worker threads instead buy applying fifty milliseconds delay four burst requests um right four unit tests validating that burst traffic respects token budget ceilings",
        "refined_text": "Tell Windsurf to configure our token bucket limiter inside rate_tracker.py by monitoring sliding window consumption across 20 worker threads instead by applying 50 milliseconds delay for burst requests.\n\nWrite 4 unit tests validating that burst traffic respects token budget ceilings."
    },

    # Sample 10: Context Window KV Cache Prefix Sharing in SGLang
    {
        "raw_asr": "um optimiz prefix cache retention in s g l a n g inside prefix underscore cache dot py buy sharing static system prompt tokens across sixteen concurrent streams wait thirty two concurrent streams instead buy locking prompt prefix blocks inside k v memory okay so right five unit tests confirming that prefix cache hits reduce time two first token latency",
        "refined_text": "Optimize prefix cache retention in SGLang inside prefix_cache.py by sharing static system prompt tokens across 32 concurrent streams instead by locking prompt prefix blocks inside KV memory.\n\nWrite 5 unit tests confirming that prefix cache hits reduce time to first token latency."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # =========================================================================

    # Sample 11: Graph-Based State Machine Routing in LangGraph
    {
        "raw_asr": "basically our agent infrastructure team migrated multi step developer workflows from linear chains into a graph based state machine inside state underscore graph dot py buy orchestrating complex agent transitions across modular nodes our previous sequential execution pipeline suffered from cascading failures where a single bad tool call aborted multi turn tasks after exhausting twenty tokens four context retention um the platform developers built a cyclic state router which tracks execution state across eight specialized agent nodes so basically when the when the primary agent generates a task plan the router evaluates conditional edges and routes subtasks towards dedicated executor nodes buy isolating scratchpad state within thread memory wait break infinite recursion loops buy enforcing a maximum recursion depth of five cycles instead okay so tell aider two evaluate state machine transitions buy running twenty four synthetic benchmark tasks and right six unit tests verifying that failed nodes trigger graceful recovery edges",
        "refined_text": "Our agent infrastructure team migrated multi-step developer workflows from linear chains into a graph-based state machine inside state_graph.py by orchestrating complex agent transitions across modular nodes. Our previous sequential execution pipeline suffered from cascading failures, where a single bad tool call aborted multi-turn tasks after exhausting 20 tokens for context retention.\n\nThe platform developers built a cyclic state router which tracks execution state across 8 specialized agent nodes. When the primary agent generates a task plan, the router evaluates conditional edges and routes subtasks towards dedicated executor nodes by isolating scratchpad state within thread memory, breaking infinite recursion loops by enforcing a maximum recursion depth of 5 cycles instead.\n\nTell Aider to evaluate state machine transitions by running 24 synthetic benchmark tasks, and write 6 unit tests verifying that failed nodes trigger graceful recovery edges."
    },

    # Sample 12: Context Window Compaction with Attention Sinks in Streaming Inference
    {
        "raw_asr": "uh our inference platform developers rebuilt the conversational context manager buy implementing streaming attention sink eviction four long running agent dialogues previously our agent sessions exhausted their six five five three six token limits during deep research loops which caused severe memory fragmentation across sixteen worker instances um the engineering team integrated a streaming context compressor inside context underscore compressor dot py which retains four initial attention sink tokens and a rolling window of four zero nine six recent tokens buy evicting intermediate conversational turns so basically when the when the agent conversation exceeds sliding limits the manager evicts stale key value pairs buy maintaining essential attention sinks wait mitigate token drift buy updating position embeddings across thirty two active streams instead okay so direct copilot two benchmark memory reduction across sixty simulated dialogue sessions and right five unit tests confirming that attention sink tokens remain pinned inside the cache",
        "refined_text": "Our inference platform developers rebuilt the conversational context manager by implementing streaming attention sink eviction for long-running agent dialogues. Previously our agent sessions exhausted their 65536 token limits during deep research loops, which caused severe memory fragmentation across 16 worker instances.\n\nThe engineering team integrated a streaming context compressor inside context_compressor.py, which retains 4 initial attention sink tokens and a rolling window of 4096 recent tokens by evicting intermediate conversational turns. When the agent conversation exceeds sliding limits, the manager evicts stale key-value pairs by maintaining essential attention sinks, mitigating token drift by updating position embeddings across 32 active streams instead.\n\nDirect Copilot to benchmark memory reduction across 60 simulated dialogue sessions, and write 5 unit tests confirming that attention sink tokens remain pinned inside the cache."
    },

    # Sample 13: gVisor Containerized Tool Execution Sandbox with Linux cgroupv2 Throttling
    {
        "raw_asr": "um our platform security engineering team restructured autonomous tool execution isolation buy running untrusted shell tools inside gvisor container sandboxes previously our coding agent executed bash scripts directly on shared runner knowed instances which caused memory exhaustion when runaway loops consumed host memory across eight worker containers um our security architects built a sandbox isolation controller inside sandbox underscore controller dot py which intercepts system calls and limits resource access four each agent session buy enforcing c group v two memory constraints down into two zero four eight megabytes so basically when the when the agent triggers shell commands the controller spawns an ephemeral sandbox and monitors subprocess execution wait terminat hung processes buy enforcing a command timeout of thirty seconds instead okay so tell windsurf two benchmark sandbox security buy executing sixteen adversarial test scripts and right four unit tests validating that file access outside the sandbox workspace is rejected",
        "refined_text": "Our platform security engineering team restructured autonomous tool execution isolation by running untrusted shell tools inside gVisor container sandboxes. Previously our coding agent executed Bash scripts directly on shared runner node instances, which caused memory exhaustion when runaway loops consumed host memory across 8 worker containers.\n\nOur security architects built a sandbox isolation controller inside sandbox_controller.py, which intercepts system calls and limits resource access for each agent session by enforcing cgroupv2 memory constraints down into 2048 megabytes. When the agent triggers shell commands, the controller spawns an ephemeral sandbox and monitors subprocess execution, terminating hung processes by enforcing a command timeout of 30 seconds instead.\n\nTell Windsurf to benchmark sandbox security by executing 16 adversarial test scripts, and write 4 unit tests validating that file access outside the sandbox workspace is rejected."
    },

    # Sample 14: Constrained Structured Decoding with Context-Free Grammars (CFG) for SQL
    {
        "raw_asr": "basically our analytics agent developers redesigned the text two s q l generation pipeline buy implementing grammar constrained logit masking four complex database queries previously our model generated free form s q l text which caused syntax errors across twenty percent of queries when joins omitted foreign key clauses across sixteen relational schemas um our platform engineers built a context free grammar sampler inside grammar underscore sampler dot py which converts database schemas into finite state transition tables buy evaluating legal tokens at every generation step so basically when the when the model generates subsequent tokens the sampler masks invalid vocabulary logits buy setting disallowed token probabilities two minus infinity wait restrict table identifiers buy projecting registered schema catalogs instead okay so tell aider two evaluate query validat buy executing five hundred benchmark queries and right five unit tests confirming zero syntax errors during automated test runs",
        "refined_text": "Our analytics agent developers redesigned the text-to-SQL generation pipeline by implementing grammar-constrained logit masking for complex database queries. Previously our model generated free-form SQL text, which caused syntax errors across 20 percent of queries when joins omitted foreign key clauses across 16 relational schemas.\n\nOur platform engineers built a context-free grammar sampler inside grammar_sampler.py, which converts database schemas into finite-state transition tables by evaluating legal tokens at every generation step. When the model generates subsequent tokens, the sampler masks invalid vocabulary logits by setting disallowed token probabilities to minus infinity, restricting table identifiers by projecting registered schema catalogs instead.\n\nTell Aider to evaluate query validation by executing 500 benchmark queries, and write 5 unit tests confirming zero syntax errors during automated test runs."
    },

    # Sample 15: LLM-as-a-Judge Evaluation Pipeline with G-Eval and Cohen Kappa Scoring
    {
        "raw_asr": "uh our evaluation infrastructure team overhauled model benchmarking buy constructing an automated judge pipeline four multi turn conversation quality previously our quality reviews relied on manual human scoring which created evaluation bottlenecks across thirty projects and showed inconsistent ratings um our assessment engineers deployed a scoring harness inside judge underscore evaluator dot py which grades conversational coherence using detailed rubric criteria from one through five points buy comparing candidate responses against reference trajectories so basically when the when the evaluator model scores an agent response it computes detailed scoring rubrics across four judge models buy measuring annotator agreement using cohen kappa score wait calibrate evaluation thresholds buy requiring cohen kappa agreement above eighty five percent instead okay so tell cursor two run evaluation benchmarks across two hundred multi turn dialogues and right six unit tests verifying that judge ratings correlate with human ground truth",
        "refined_text": "Our evaluation infrastructure team overhauled model benchmarking by constructing an automated judge pipeline for multi-turn conversation quality. Previously our quality reviews relied on manual human scoring, which created evaluation bottlenecks across 30 projects and showed inconsistent ratings.\n\nOur assessment engineers deployed a scoring harness inside judge_evaluator.py, which grades conversational coherence using detailed rubric criteria from 1 through 5 points by comparing candidate responses against reference trajectories. When the evaluator model scores an agent response, it computes detailed scoring rubrics across 4 judge models by measuring annotator agreement using Cohen kappa score, calibrating evaluation thresholds by requiring Cohen kappa agreement above 85 percent instead.\n\nTell Cursor to run evaluation benchmarks across 200 multi-turn dialogues, and write 6 unit tests verifying that judge ratings correlate with human ground truth."
    },

    # Sample 16: RAG Hybrid Retrieval with Reciprocal Rank Fusion and Cross-Encoder
    {
        "raw_asr": "basically our search platform developers upgraded document retrieval buy constructing a hybrid sparse dense index four enterprise knowledge bases our previous pure vector retriever missed exact keyword matches on technical error codes which degraded downstream response accuracy across forty production queries um our retrieval team built a hybrid search engine inside hybrid underscore retriever dot py which combines sparse b m twenty five scoring with dense vector embeddings across one five three six dimensions buy aggregating search results through reciprocal rank fusion so basically when the when the retriever fetches candidate documents it calculates reciprocal rank scores using a smoothing constant of sixty buy merging lexical and semantic ranks wait rerank top passages buy scoring thirty candidate chunks with a localized cross encoder model instead okay so ask aider two evaluate retrieval recall buy testing fifty technical support documents and right five unit tests verifying that exact keywords rank within top results",
        "refined_text": "Our search platform developers upgraded document retrieval by constructing a hybrid sparse-dense index for enterprise knowledge bases. Our previous pure vector retriever missed exact keyword matches on technical error codes, which degraded downstream response accuracy across 40 production queries.\n\nOur retrieval team built a hybrid search engine inside hybrid_retriever.py, which combines sparse BM25 scoring with dense vector embeddings across 1536 dimensions by aggregating search results through reciprocal rank fusion. When the retriever fetches candidate documents, it calculates reciprocal rank scores using a smoothing constant of 60 by merging lexical and semantic ranks, reranking top passages by scoring 30 candidate chunks with a localized cross-encoder model instead.\n\nAsk Aider to evaluate retrieval recall by testing 50 technical support documents, and write 5 unit tests verifying that exact keywords rank within top results."
    },

    # Sample 17: Autonomous Web Browsing Agent with DOM Accessibility Tree Distillation
    {
        "raw_asr": "um our browser automation team redesigned web page processing buy converting bloated html documents into distilled accessibility trees our initial web browsing agent ingested raw d o m structures which overwhelmed the prompt context with four five zero zero zero tokens and degraded action planning across ten agent sessions um our frontend engineers built a tree distiller inside dom underscore distiller dot py which extracts semantic accessibility roles and interactive bounding boxes buy pruning ninety percent of decorative tags and script nodes so basically when the when the agent navigates two a target web page the distiller strips hidden elements and condenses the d o m down into three five zero zero tokens buy assigning unique integer labels two interactive buttons wait filter decorative styling buy discarding unclickable container tags instead okay so instruct windsurf two validate tree distillation across twenty five dynamic web applications and right four unit tests confirming that distilled trees retain clickable input elements",
        "refined_text": "Our browser automation team redesigned web page processing by converting bloated HTML documents into distilled accessibility trees. Our initial web browsing agent ingested raw DOM structures, which overwhelmed the prompt context with 45000 tokens and degraded action planning across 10 agent sessions.\n\nOur frontend engineers built a tree distiller inside dom_distiller.py, which extracts semantic accessibility roles and interactive bounding boxes by pruning 90 percent of decorative tags and script nodes. When the agent navigates to a target web page, the distiller strips hidden elements and condenses the DOM down into 3500 tokens by assigning unique integer labels to interactive buttons, filtering decorative styling by discarding unclickable container tags instead.\n\nInstruct Windsurf to validate tree distillation across 25 dynamic web applications, and write 4 unit tests confirming that distilled trees retain clickable input elements."
    },

    # Sample 18: Dual-LLM Guardrail and Canary Token Injection Defense
    {
        "raw_asr": "basically our application security team hardened agent workflows buy deploying a dual model guardrail and canary token defense against indirect prompt injections previously untrusted external documents injected hidden instructions into model context which compromised agent decision making across twelve test cases um our security developers built a prompt firewall inside prompt underscore firewall dot py which injects randomized eight character canary tokens into internal system prompts buy monitoring tool call arguments four secret token leaks so basically when the when the primary agent prepares an outgoing tool execution payload a secondary auditor model inspects tool parameters buy evaluating injection risk and verifying canary confidentiality wait quarantine suspicious payloads buy blocking tool execution when canary strings appear inside tool arguments instead okay so direct copilot two validate firewall robustness across sixty adversarial attack prompts and right four unit tests confirming that compromised tool calls are dropped",
        "refined_text": "Our application security team hardened agent workflows by deploying a dual-model guardrail and canary token defense against indirect prompt injections. Previously untrusted external documents injected hidden instructions into model context, which compromised agent decision making across 12 test cases.\n\nOur security developers built a prompt firewall inside prompt_firewall.py, which injects randomized 8-character canary tokens into internal system prompts by monitoring tool call arguments for secret token leaks. When the primary agent prepares an outgoing tool execution payload, a secondary auditor model inspects tool parameters by evaluating injection risk and verifying canary confidentiality, quarantining suspicious payloads by blocking tool execution when canary strings appear inside tool arguments instead.\n\nDirect Copilot to validate firewall robustness across 60 adversarial attack prompts, and write 4 unit tests confirming that compromised tool calls are dropped."
    },

    # Sample 19: Agentic Memory Hierarchy Decoupling Working Scratchpad from Episodic Storage
    {
        "raw_asr": "uh our agent architecture team overhauled agent memory systems buy separating short term working scratchpads from long term episodic vector storage previously our coding assistant maintained an unbounded conversational history which cluttered the reasoning scratchpad across twenty interaction turns and diluted key architectural decisions um our software engineers deployed a tiered memory manager inside memory underscore tier dot py which automatically summarizes conversational history every eight interaction turns and persists key episodic entities into a seven six eight dimensional vector store buy maintaining concise state snapshots so basically when the when the agent starts a new subtask the memory controller retrieves relevant historical context buy querying episodic embeddings and refreshing active scratchpad memory wait prune irrelevant historical dialogue buy clearing transient intermediate thoughts instead okay so tell aider two benchmark recall fidelity across fifty multi turn user workflows and right four unit tests confirming that episodic memory accurately restores archived design requirements",
        "refined_text": "Our agent architecture team overhauled agent memory systems by separating short-term working scratchpads from long-term episodic vector storage. Previously our coding assistant maintained an unbounded conversational history, which cluttered the reasoning scratchpad across 20 interaction turns and diluted key architectural decisions.\n\nOur software engineers deployed a tiered memory manager inside memory_tier.py, which automatically summarizes conversational history every 8 interaction turns and persists key episodic entities into a 768-dimensional vector store by maintaining concise state snapshots. When the agent starts a new subtask, the memory controller retrieves relevant historical context by querying episodic embeddings and refreshing active scratchpad memory, pruning irrelevant historical dialogue by clearing transient intermediate thoughts instead.\n\nTell Aider to benchmark recall fidelity across 50 multi-turn user workflows, and write 4 unit tests confirming that episodic memory accurately restores archived design requirements."
    },

    # Sample 20: Speculative Tool Execution and Rollback in Agent Workflows
    {
        "raw_asr": "basically our autonomous agent developers improved tool call responsiveness buy implementing speculative tool execution with transactional rollback support previously our workflow pipeline paused model reasoning at every step which added round trip latency across sixteen sequential tool executions um our workflow developers built a speculative dispatcher inside tool underscore dispatcher dot py which speculatively executes non destructive read operations while buffering destructive file modifications buy requiring human approval gates four irreversible actions so basically when the when the agent predicts upcoming read commands the dispatcher prefetches file contents and search results buy storing temporary execution outputs wait rollback speculative writes buy reverting workspace changes when user approval is rejected instead okay so tell cursor two benchmark tool dispatch latency across thirty complex agent scenarios and right five unit tests verifying that unapproved filesystem writes revert cleanly without data corruption",
        "refined_text": "Our autonomous agent developers improved tool call responsiveness by implementing speculative tool execution with transactional rollback support. Previously our workflow pipeline paused model reasoning at every step, which added round-trip latency across 16 sequential tool executions.\n\nOur workflow developers built a speculative dispatcher inside tool_dispatcher.py, which speculatively executes non-destructive read operations while buffering destructive file modifications by requiring human approval gates for irreversible actions. When the agent predicts upcoming read commands, the dispatcher prefetches file contents and search results by storing temporary execution outputs, rolling back speculative writes by reverting workspace changes when user approval is rejected instead.\n\nTell Cursor to benchmark tool dispatch latency across 30 complex agent scenarios, and write 5 unit tests verifying that unapproved filesystem writes revert cleanly without data corruption."
    }
]

# Validation checks
print(f"Total samples: {len(batch)}")
assert len(batch) == 20, f"Expected 20 samples, got {len(batch)}"

# Check evaluation set leakage
eval_file = Path("sft_eval.json")
if eval_file.exists():
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    eval_raws = {e.get("raw_asr", e.get("input", "")).strip().lower() for e in eval_data}
    eval_refs = {e.get("refined_text", e.get("output", "")).strip() for e in eval_data}
    for idx, s in enumerate(batch, 1):
        raw_test = s["raw_asr"].strip().lower()
        ref_test = s["refined_text"].strip()
        if raw_test in eval_raws:
            raise ValueError(f"Sample {idx} raw_asr leaked into evaluation set!")
        if ref_test in eval_refs:
            raise ValueError(f"Sample {idx} refined_text leaked into evaluation set!")
    print("Eval leakage check passed: 0 leaks.")

# Check individual validation and cleaning
for idx, s in enumerate(batch, 1):
    is_valid, reason = validate_pair(s)
    if not is_valid:
        raise ValueError(f"Sample {idx} failed validate_pair: {reason}")
    res, status = clean_sample(s["raw_asr"], s["refined_text"])
    if status != "kept":
        raise ValueError(f"Sample {idx} failed clean_sample: {status}")

print("Individual validation & cleaner checks passed: 20/20 kept.")

# Batch validation
batch_valid, batch_reason, tier_counts = validate_batch(batch, min_short=4, min_medium=6, min_long=10)
if not batch_valid:
    raise ValueError(f"Batch validation failed: {batch_reason}")

print(f"Batch validation passed: {batch_reason}")
print(f"Tier counts: {tier_counts}")

# Save verified batch to scratch/subagent_batch_107.json
output_path = Path("scratch/subagent_batch_107.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"Saved {len(batch)} verified samples to {output_path}")
