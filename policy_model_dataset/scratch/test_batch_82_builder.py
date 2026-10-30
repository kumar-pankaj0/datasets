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

    # Sample 1: Tool call schema validation
    {
        "raw_asr": "um prompt claude two validat tool parameter types buy enforcing strict json schema schemas four agent actions",
        "refined_text": "Prompt Claude to validate tool parameter types by enforcing strict JSON schema schemas for agent actions."
    },

    # Sample 2: Sliding window context truncation
    {
        "raw_asr": "uh instruct cursor two terminat stale conversation turns buy retaining thirty two previous interaction messages",
        "refined_text": "Instruct Cursor to terminate stale conversation turns by retaining 32 previous interaction messages."
    },

    # Sample 3: Hybrid retrieval filtering
    {
        "raw_asr": "tell windsurf two configur hybrid retrieval filtering buy applying twenty percent score cutoffs four reranked documents",
        "refined_text": "Tell Windsurf to configure hybrid retrieval filtering by applying 20 percent score cutoffs for reranked documents."
    },

    # Sample 4: Structured grammar tokens
    {
        "raw_asr": "um direct aider two synchroniz structured grammar tokens buy masking illegal logits across twelve generation steps",
        "refined_text": "Direct Aider to synchronize structured grammar tokens by masking illegal logits across 12 generation steps."
    },

    # =========================================================================
    # Tier 2: Medium Utterances (25 to 89 words) - Exactly 6 samples (Samples 5-10)
    # 1 to 3 grammatically complete sentences. Natural \n\n breaks. Max \n\n: words // 25.
    # =========================================================================

    # Sample 5: Dynamic prompt template assembly
    {
        "raw_asr": "basically prompt claude two refact our system prompt compiler inside prompt underscore compiler dot py buy wrapping dynamic task instructions inside x m l delimiter tags wait isolate external input context buy escaping triple backtick code blocks instead um right four pie test assertions validating that prompt injections fail two escape delineated blocks",
        "refined_text": "Prompt Claude to refactor our system prompt compiler inside prompt_compiler.py by wrapping dynamic task instructions inside XML delimiter tags, isolating external input context by escaping triple backtick code blocks instead.\n\nWrite 4 pytest assertions validating that prompt injections fail to escape delineated blocks."
    },

    # Sample 6: MCP server stdio connection & tool dispatch
    {
        "raw_asr": "tell windsurf two configur our m c p server dispatcher inside m c p underscore dispatcher dot py buy executing tool calls across local stdio subprocess pipes wait terminat stalled process streams buy enforcing a hard timeout of five seconds instead um right six unit tests verifying graceful worker restarts after subprocess exceptions",
        "refined_text": "Tell Windsurf to configure our MCP server dispatcher inside mcp_dispatcher.py by executing tool calls across local stdio subprocess pipes, terminating stalled process streams by enforcing a hard timeout of 5 seconds instead.\n\nWrite 6 unit tests verifying graceful worker restarts after subprocess exceptions."
    },

    # Sample 7: Multi-agent supervisor-worker task delegation
    {
        "raw_asr": "instruct cursor two refact our supervisor routing graph inside state underscore graph dot py buy assigning incoming developer requests towards four specialized worker nodes wait pass shared scratchpad state buy synchroniz thread memory across sixteen message turns instead um right five pie test test cases validating state transitions between planner and coder agents",
        "refined_text": "Instruct Cursor to refactor our supervisor routing graph inside state_graph.py by assigning incoming developer requests towards 4 specialized worker nodes, passing shared scratchpad state by synchronizing thread memory across 16 message turns instead.\n\nWrite 5 pytest test cases validating state transitions between planner and coder agents."
    },

    # Sample 8: RAG hybrid sparse-dense chunking and reciprocal rank fusion
    {
        "raw_asr": "ask aider two build a reciprocal rank fusion pipeline inside rank underscore fusion dot py buy combining sparse b m twenty five scores with dense vector similarities wait penaliz low rank documents buy applying a smoothing constant of sixty instead um generat four pie test fixtures verifying that top ranked chunks contain relevant source metadata",
        "refined_text": "Ask Aider to build a reciprocal rank fusion pipeline inside rank_fusion.py by combining sparse BM25 scores with dense vector similarities, penalizing low rank documents by applying a smoothing constant of 60 instead.\n\nGenerate 4 pytest fixtures verifying that top ranked chunks contain relevant source metadata."
    },

    # Sample 9: Agentic critic and self-correction verification loop
    {
        "raw_asr": "basically direct copilot two refact our automated code critic inside critic underscore loop dot py buy parsing test runner failure logs and feeding stack traces back into the prompt context wait terminat recursive repair attempts buy capping revision loops at three cycles instead um right six pie test assertions asserting that syntax errors trigger automatic patch regeneration",
        "refined_text": "Direct Copilot to refactor our automated code critic inside critic_loop.py by parsing test runner failure logs and feeding stack traces back into the prompt context, terminating recursive repair attempts by capping revision loops at 3 cycles instead.\n\nWrite 6 pytest assertions asserting that syntax errors trigger automatic patch regeneration."
    },

    # Sample 10: Token rate limiter and sliding window token bucket
    {
        "raw_asr": "tell cursor two configur our rate limit tracker inside token underscore limiter dot py buy tracking sliding window token counts across thirty client tenants wait throttle excessive completions buy delaying request dispatch four two hundred milliseconds instead um right four pie test test cases confirming that burst requests respect token bucket limits",
        "refined_text": "Tell Cursor to configure our rate limit tracker inside token_limiter.py by tracking sliding window token counts across 30 client tenants, throttling excessive completions by delaying request dispatch for 200 milliseconds instead.\n\nWrite 4 pytest test cases confirming that burst requests respect token bucket limits."
    },

    # =========================================================================
    # Tier 3: Long Utterances (90+ words) - Exactly 10 samples (Samples 11-20)
    # Multi-paragraph structure separated by \n\n. Zero numbered checklists.
    # Natural spoken engineer narration. Ratio 0.35 - 1.25. Max \n\n: words // 25.
    # =========================================================================

    # Sample 11: Hierarchical Multi-Agent Task Routing & Speculative Execution
    {
        "raw_asr": "basically our agent platform engineering team designed a hierarchical multi agent routing pipeline buy delegating user coding intents between an architectural planner and four specialized code generator agents our initial single agent loop suffered from reasoning degradation where maintaining monolithic system prompts across forty message turns consumed thirty two seven six eight tokens and triggered repetitive tool hallucinations um the architecture council approved a supervisor router inside agent underscore orchestrator dot py which evaluates incoming user prompts and compiles isolated subtask prompts four worker agents so basically when the when the planner emits an execution plan the supervisor dispatches subtasks concurrently towards worker instances buy provisioning ephemeral scratchpads with dedicated tool schemas wait terminat runaway agent executions buy enforcing a recursion boundary of twelve steps instead okay so tell cursor two benchmark routing latency buy measuring multi agent execution across twenty four synthetic tasks and right five pie test unit tests confirming that subtask outputs assemble cleanly into the primary workspace",
        "refined_text": "Our agent platform engineering team designed a hierarchical multi-agent routing pipeline by delegating user coding intents between an architectural planner and 4 specialized code generator agents. Our initial single-agent loop suffered from reasoning degradation, where maintaining monolithic system prompts across 40 message turns consumed 32768 tokens and triggered repetitive tool hallucinations.\n\nThe architecture council approved a supervisor router inside agent_orchestrator.py, which evaluates incoming user prompts and compiles isolated subtask prompts for worker agents. When the planner emits an execution plan, the supervisor dispatches subtasks concurrently towards worker instances by provisioning ephemeral scratchpads with dedicated tool schemas, terminating runaway agent executions by enforcing a recursion boundary of 12 steps instead.\n\nTell Cursor to benchmark routing latency by measuring multi-agent execution across 24 synthetic tasks, and write 5 pytest unit tests confirming that subtask outputs assemble cleanly into the primary workspace."
    },

    # Sample 12: Context Window KV Cache Prefix Sharing & Prompt Virtual Memory
    {
        "raw_asr": "our inference infrastructure team refactored the prompt compilation pipeline buy optimizing prompt prefix alignments four shared k v cache retention across v l l m worker clusters previously our gateway prepended dynamic session timestamps and randomized customer identifiers two the start of every prompt which invalidated prefix cache blocks and drove first token latency two eighteen hundred milliseconds across twenty four model instances um the engineering team resolved cache thrashing buy freezing static system instructions and thirty two common m c p tool definitions at the prompt prefix inside cache underscore manager dot py while appending variable user queries two the payload tail so basically when the when the inference gateway schedules incoming agent requests it routes requests with matching prefix hashes towards the same worker knowed buy leveraging cache aware scheduling wait evict stale cache blocks buy setting an idle timeout threshold of fifteen minutes instead okay so ask aider two evaluate prefix hit rates buy replaying sixty recorded agent sessions and right four pie test test cases verifying that prefix cache hit rates exceed seventy five percent",
        "refined_text": "Our inference infrastructure team refactored the prompt compilation pipeline by optimizing prompt prefix alignments for shared KV cache retention across vLLM worker clusters. Previously our gateway prepended dynamic session timestamps and randomized customer identifiers to the start of every prompt, which invalidated prefix cache blocks and drove first token latency to 1800 milliseconds across 24 model instances.\n\nThe engineering team resolved cache thrashing by freezing static system instructions and 32 common MCP tool definitions at the prompt prefix inside cache_manager.py, while appending variable user queries to the payload tail. When the inference gateway schedules incoming agent requests, it routes requests with matching prefix hashes towards the same worker node by leveraging cache-aware scheduling, evicting stale cache blocks by setting an idle timeout threshold of 15 minutes instead.\n\nAsk Aider to evaluate prefix hit rates by replaying 60 recorded agent sessions, and write 4 pytest test cases verifying that prefix cache hit rates exceed 75 percent."
    },

    # Sample 13: Autonomous Agent Tool Execution Sandboxing & Privilege Boundary
    {
        "raw_asr": "our platform security working group restructured the autonomous tool execution environment buy isolating agent generated shell scripts inside ephemeral firecracker micro v m sandboxes previously our coding agent executed shell commands directly on shared development hosts which caused resource starvation when recursive search processes consumed thirty two gigabytes of memory and risked accidental secret leakage um our security engineers implemented a sandbox manager inside sandbox underscore isolation dot py which spins up lightweight virtual machine boundaries four each agent session buy restricting filesystem access two a temporary scratch workspace so basically when the when the agent calls bash or python tools the sandbox controller intercepts system calls and limits execution memory two four zero nine six megabytes buy enforcing c group v two memory limits wait terminat runaway subprocesses buy applying an execution timeout of thirty seconds instead okay so tell windsurf two test sandbox resilience buy simulating sixteen hostile command executions and right six pie test unit tests verifying that sensitive environment variables remain isolated",
        "refined_text": "Our platform security working group restructured the autonomous tool execution environment by isolating agent-generated shell scripts inside ephemeral Firecracker microVM sandboxes. Previously our coding agent executed shell commands directly on shared development hosts, which caused resource starvation when recursive search processes consumed 32 gigabytes of memory and risked accidental secret leakage.\n\nOur security engineers implemented a sandbox manager inside sandbox_isolation.py, which spins up lightweight virtual machine boundaries for each agent session by restricting filesystem access to a temporary scratch workspace. When the agent calls Bash or Python tools, the sandbox controller intercepts system calls and limits execution memory to 4096 megabytes by enforcing cgroupv2 memory limits, terminating runaway subprocesses by applying an execution timeout of 30 seconds instead.\n\nTell Windsurf to test sandbox resilience by simulating 16 hostile command executions, and write 6 pytest unit tests verifying that sensitive environment variables remain isolated."
    },

    # Sample 14: Model Context Protocol (MCP) Dynamic Tool Schema Pruning & Routing
    {
        "raw_asr": "basically our agent gateway team redesigned the tool registration and discovery pipeline buy replacing static tool injection with dynamic semantic schema filtering our agent deployment integrates twelve separate m c p servers offering ninety six distinct function schemas which consumed sixteen three eight four tokens on every request and confused the model reasoning loop during tool selection um the gateway team introduced an embedding based tool index inside schema underscore router dot py which indexes tool documentation vectors in a local vector database so basically when the when the user submits an engineering query the router calculates cosine similarity against registered tool descriptions and selects the top six candidate tool schemas buy pruning irrelevant function definitions from the model context wait rank candidate tools buy scoring tool usage frequency across previous agent sessions instead okay so direct copilot two validate schema pruning buy testing fifty synthetic user prompts across eight tool categories and right five pie test assertions confirming that required tool schemas appear in candidate payloads",
        "refined_text": "Our agent gateway team redesigned the tool registration and discovery pipeline by replacing static tool injection with dynamic semantic schema filtering. Our agent deployment integrates 12 separate MCP servers offering 96 distinct function schemas, which consumed 16384 tokens on every request and confused the model reasoning loop during tool selection.\n\nThe gateway team introduced an embedding-based tool index inside schema_router.py, which indexes tool documentation vectors in a local vector database. When the user submits an engineering query, the router calculates cosine similarity against registered tool descriptions and selects the top 6 candidate tool schemas by pruning irrelevant function definitions from the model context, ranking candidate tools by scoring tool usage frequency across previous agent sessions instead.\n\nDirect Copilot to validate schema pruning by testing 50 synthetic user prompts across 8 tool categories, and write 5 pytest assertions confirming that required tool schemas appear in candidate payloads."
    },

    # Sample 15: Agent Reflection, State Backtracking & Git Tree Checkpointing
    {
        "raw_asr": "our autonomous coding platform team overhauled the agent execution loop buy implementing a state checkpointing and rollback engine four failed code refactors previously our coding agent applied generated code patches directly two the working tree without taking snapshots which left corrupted files and uncompilable code when unit tests failed during multi file refactors um our infrastructure developers built a checkpoint engine inside rollback underscore engine dot py which captures git tree diffs and workspace states before executing model proposed modifications so basically when the when the test suite returns non zero exit codes the rollback engine reverts modified files two the last passing snapshot buy restoring cached git trees wait trigger an alternative reasoning branch buy feeding compiler diagnostic messages into the prompt context instead okay so instruct cursor two benchmark rollback recovery buy simulating thirty failing test runs across ten python repositories and right four pie test test cases verifying that file systems revert cleanly two uncorrupted states",
        "refined_text": "Our autonomous coding platform team overhauled the agent execution loop by implementing a state checkpointing and rollback engine for failed code refactors. Previously our coding agent applied generated code patches directly to the working tree without taking snapshots, which left corrupted files and uncompilable code when unit tests failed during multi-file refactors.\n\nOur infrastructure developers built a checkpoint engine inside rollback_engine.py, which captures git tree diffs and workspace states before executing model-proposed modifications. When the test suite returns non-zero exit codes, the rollback engine reverts modified files to the last passing snapshot by restoring cached git trees, triggering an alternative reasoning branch by feeding compiler diagnostic messages into the prompt context instead.\n\nInstruct Cursor to benchmark rollback recovery by simulating 30 failing test runs across 10 Python repositories, and write 4 pytest test cases verifying that file systems revert cleanly to uncorrupted states."
    },

    # Sample 16: RAG Semantic Chunking & Cross-Encoder Reranking Pipeline
    {
        "raw_asr": "basically our search platform engineering team upgraded the document retrieval architecture buy replacing fixed token chunking with semantic boundary splitting and cross encoder reranking our previous retrieval pipeline split engineering manuals into rigid five hundred token blocks which fractured code snippets across chunk boundaries and degraded downstream answer accuracy two forty percent um the retrieval team implemented a semantic chunker inside chunk underscore parser dot py which detects embedding distance shifts across consecutive sentences buy placing chunk splits at topical transitions so basically when the when the vector retriever fetches fifty candidate document chunks a localized cross encoder model scores query passage relevance buy computing joint token cross attention across candidate chunks wait discard low relevance chunks buy enforcing a threshold cutoff score of seventy percent instead okay so tell aider two evaluate chunk coherence buy testing forty technical manual documents and right six pie test unit tests verifying that code blocks remain intact across chunk boundaries",
        "refined_text": "Our search platform engineering team upgraded the document retrieval architecture by replacing fixed token chunking with semantic boundary splitting and cross-encoder reranking. Our previous retrieval pipeline split engineering manuals into rigid 500 token blocks, which fractured code snippets across chunk boundaries and degraded downstream answer accuracy to 40 percent.\n\nThe retrieval team implemented a semantic chunker inside chunk_parser.py, which detects embedding distance shifts across consecutive sentences by placing chunk splits at topical transitions. When the vector retriever fetches 50 candidate document chunks, a localized cross-encoder model scores query passage relevance by computing joint token cross-attention across candidate chunks, discarding low relevance chunks by enforcing a threshold cutoff score of 70 percent instead.\n\nTell Aider to evaluate chunk coherence by testing 40 technical manual documents, and write 6 pytest unit tests verifying that code blocks remain intact across chunk boundaries."
    },

    # Sample 17: Structured JSON Output Enforcement via Context-Free Grammar Masks
    {
        "raw_asr": "our platform developer experience team reconstructed the structured output generation module buy enforcing context free grammar masks directly on token logits during model inference previously our agent pipeline relied on natural language prompting two request j s o n payloads which failed validation fifteen percent of the time due two missing keys and trailing commas across three two zero zero production requests um the engineering team integrated a grammar constrained sampler inside grammar underscore decoder dot py which converts json schema definitions into deterministic finite state automata so basically when the when the language model predicts the next token the sampler evaluates valid schema transitions and masks disallowed token logits buy setting invalid token probabilities two minus infinity wait validate enum literals buy restricting allowed string values two predefined schema options instead okay so prompt windsurf two test decoding reliability buy generating one hundred structured database migration schemas and right five pie test assertions verifying zero json parsing exceptions",
        "refined_text": "Our platform developer experience team reconstructed the structured output generation module by enforcing context-free grammar masks directly on token logits during model inference. Previously our agent pipeline relied on natural language prompting to request JSON payloads, which failed validation 15 percent of the time due to missing keys and trailing commas across 3200 production requests.\n\nThe engineering team integrated a grammar-constrained sampler inside grammar_decoder.py, which converts JSON schema definitions into deterministic finite-state automata. When the language model predicts the next token, the sampler evaluates valid schema transitions and masks disallowed token logits by setting invalid token probabilities to minus infinity, validating enum literals by restricting allowed string values to predefined schema options instead.\n\nPrompt Windsurf to test decoding reliability by generating 100 structured database migration schemas, and write 5 pytest assertions verifying zero JSON parsing exceptions."
    },

    # Sample 18: Autonomous Agent Web Scraping & DOM Accessibility Tree Distillation
    {
        "raw_asr": "our autonomous web agent team overhauled the browser automation pipeline buy distilling raw web page source trees into semantic accessibility trees four language model consumption our browsing agent previously fed raw h t m l documents into the prompt context which consumed sixty four thousand tokens per page and exhausted context limits across twenty five browser interactions um the automation developers constructed an accessibility tree extractor inside accessibility underscore filter dot py which strips non functional styling scripts and hidden svg graphics buy preserving only actionable form inputs buttons and navigational links so basically when the when the browser navigates two a target web application the extractor builds a compacted tree hierarchy and annotates interactive elements with unique integer identifiers buy mapping numeric labels two backend css selectors wait prune deep layout branches buy limiting tree depth two eight levels instead okay so direct copilot two benchmark tree distillation buy navigating thirty complex enterprise portals and right four pie test test cases verifying that interactive form fields retain correct accessibility attributes",
        "refined_text": "Our autonomous web agent team overhauled the browser automation pipeline by distilling raw web page source trees into semantic accessibility trees for language model consumption. Our browsing agent previously fed raw HTML documents into the prompt context, which consumed 64000 tokens per page and exhausted context limits across 25 browser interactions.\n\nThe automation developers constructed an accessibility tree extractor inside accessibility_filter.py, which strips non-functional styling scripts and hidden SVG graphics by preserving only actionable form inputs, buttons, and navigational links. When the browser navigates to a target web application, the extractor builds a compacted tree hierarchy and annotates interactive elements with unique integer identifiers by mapping numeric labels to backend CSS selectors, pruning deep layout branches by limiting tree depth to 8 levels instead.\n\nDirect Copilot to benchmark tree distillation by navigating 30 complex enterprise portals, and write 4 pytest test cases verifying that interactive form fields retain correct accessibility attributes."
    },

    # Sample 19: Agent Memory Compression & Sliding Window Summarization
    {
        "raw_asr": "basically our conversational agent platform group rearchitected the session memory management system buy combining sliding window message buffering with recursive memory summarization previously our customer support agent maintained full message histories within the context window which exceeded eight one nine two tokens and caused forty percent latency increases across sixty minute dialogue sessions um the platform team implemented a memory compaction daemon inside memory underscore compactor dot py which tracks active token counts and triggers summarization whenever context exceeds four zero nine six tokens so basically when the when the memory threshold is reached the compactor condenses older conversation turns into structured factual bullet points buy extracting key entities and resolution state wait archive raw message histories buy writing full session transcripts into cold postgres storage instead okay so instruct cursor two evaluate memory fidelity buy simulating fifty extended dialogue sessions and right six pie test unit tests confirming that agent responses preserve user preferences without factual degradation",
        "refined_text": "Our conversational agent platform group rearchitected the session memory management system by combining sliding window message buffering with recursive memory summarization. Previously our customer support agent maintained full message histories within the context window, which exceeded 8192 tokens and caused 40 percent latency increases across 60 minute dialogue sessions.\n\nThe platform team implemented a memory compaction daemon inside memory_compactor.py, which tracks active token counts and triggers summarization whenever context exceeds 4096 tokens. When the memory threshold is reached, the compactor condenses older conversation turns into structured factual bullet points by extracting key entities and resolution state, archiving raw message histories by writing full session transcripts into cold Postgres storage instead.\n\nInstruct Cursor to evaluate memory fidelity by simulating 50 extended dialogue sessions, and write 6 pytest unit tests confirming that agent responses preserve user preferences without factual degradation."
    },

    # Sample 20: LLM Guardrail Pipeline & Input/Output Policy Enforcement
    {
        "raw_asr": "our enterprise ai security team developed a multi tier guardrail inspection gateway buy enforcing deterministic policy checks ahead of upstream model inference previously our application forwarded external customer inputs directly two downstream language models which exposed internal system instructions during three adversarial red team penetration tests um our security architects built a pipeline filter inside guardrail underscore gateway dot py which screens incoming prompts against known prompt injection vectors buy evaluating semantic embedding distances against an adversarial jailbreak taxonomy so basically when the when the guardrail gateway detects a suspicious prompt token pattern it blocks request dispatch and returns a standardized policy violation status code buy preventing untrusted execution wait audit model outputs buy verifying that generated answers contain zero masked api credentials instead okay so tell aider two benchmark guardrail throughput buy processing eighty adversarial prompt samples across ten attack categories and right five pie test unit tests verifying zero bypass vulnerabilities",
        "refined_text": "Our enterprise AI security team developed a multi-tier guardrail inspection gateway by enforcing deterministic policy checks ahead of upstream model inference. Previously our application forwarded external customer inputs directly to downstream language models, which exposed internal system instructions during 3 adversarial red team penetration tests.\n\nOur security architects built a pipeline filter inside guardrail_gateway.py, which screens incoming prompts against known prompt injection vectors by evaluating semantic embedding distances against an adversarial jailbreak taxonomy. When the guardrail gateway detects a suspicious prompt token pattern, it blocks request dispatch and returns a standardized policy violation status code by preventing untrusted execution, auditing model outputs by verifying that generated answers contain 0 masked API credentials instead.\n\nTell Aider to benchmark guardrail throughput by processing 80 adversarial prompt samples across 10 attack categories, and write 5 pytest unit tests verifying zero bypass vulnerabilities."
    }
]

print(f"Total samples: {len(samples)}")

# Check leakage
for i, s in enumerate(samples):
    r_raw = s["raw_asr"].strip().lower()
    r_ref = s["refined_text"].strip()
    if r_raw in eval_raws:
        print(f"WARNING: Sample {i+1} raw_asr leaks into eval set!")
    if r_ref in eval_refs:
        print(f"WARNING: Sample {i+1} refined_text leaks into eval set!")

# Validate individual pairs
all_valid = True
tier_counts = {"short": 0, "medium": 0, "long": 0}

for i, s in enumerate(samples):
    raw = s["raw_asr"]
    ref = s["refined_text"]
    words = len(ref.split())
    
    # Check validator
    is_valid, reason = validate_pair(s)
    if not is_valid:
        print(f"Sample {i+1} failed validate_pair: {reason}")
        all_valid = False
    
    # Check cleaner
    res, status = clean_sample(raw, ref)
    if status != "kept":
        print(f"Sample {i+1} failed clean_sample: {status}")
        all_valid = False
        
    if words < 25:
        tier_counts["short"] += 1
    elif words < 90:
        tier_counts["medium"] += 1
    else:
        tier_counts["long"] += 1
        
    print(f"Sample {i+1}: words={words}, valid={is_valid}, clean_status={status}")

# Validate batch
batch_valid, batch_reason, counts = validate_batch(samples, min_short=4, min_medium=6, min_long=10)
print(f"\nBatch validation: valid={batch_valid}, reason={batch_reason}, counts={counts}")

if all_valid and batch_valid:
    out_path = Path("scratch/subagent_batch_82.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"\nSUCCESS! Saved to {out_path}")
else:
    print("\nFAILED validation!")
    sys.exit(1)
