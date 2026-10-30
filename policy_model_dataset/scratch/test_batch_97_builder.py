import json
import sys
import os

sys.path.insert(0, "code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch_97 = [
    # Tier 1: Short (< 25 words) - Exactly 4 samples
    {
        # Short 1: System prompt XML delimiter isolation
        "raw_asr": "um system prompt engineers configur xml delimiters around tool calling schemas buy isolating user instructions from tool declarations",
        "refined_text": "System prompt engineers configure XML delimiters around tool calling schemas by isolating user instructions from tool declarations."
    },
    {
        # Short 2: Context window memory compaction
        "raw_asr": "uh our conversational agent pipeline compacts historical session memory buy trimming message buffers into eight one nine two tokens",
        "refined_text": "Our conversational agent pipeline compacts historical session memory by trimming message buffers into 8192 tokens."
    },
    {
        # Short 3: Pydantic schema validation for tool arguments
        "raw_asr": "um agent orchestrators enforce pydantic schema validat buy rejecting malformed json function arguments during streaming execution",
        "refined_text": "Agent orchestrators enforce Pydantic schema validation by rejecting malformed JSON function arguments during streaming execution."
    },
    {
        # Short 4: Ragas faithfulness evaluation
        "raw_asr": "uh our evaluation harness calculates ragas faithfulness metrics buy comparing generated answers against retrieved document passages",
        "refined_text": "Our evaluation harness calculates Ragas faithfulness metrics by comparing generated answers against retrieved document passages."
    },

    # Tier 2: Medium (25-89 words) - Exactly 6 samples
    {
        # Medium 5: Hybrid search with reciprocal rank fusion
        "raw_asr": "our retrieval pipeline combines dense vector embeddings with sparse b m twenty five keyword scoring across forty eight document collections wait rank hybrid search results using reciprocal rank fusion instead um reciprocal rank fusion calculates balanced relevance scores across three zero seven two dimensional vector embeddings and inverted indices buy prioritizing document chunks retrieved across both search channels",
        "refined_text": "Our retrieval pipeline combines dense vector embeddings with sparse BM25 keyword scoring across 48 document collections, ranking hybrid search results using reciprocal rank fusion instead.\n\nReciprocal rank fusion calculates balanced relevance scores across 3072 dimensional vector embeddings and inverted indices by prioritizing document chunks retrieved across both search channels."
    },
    {
        # Medium 6: LangGraph supervisor routing
        "raw_asr": "basically our lang graph multi agent pipeline configur state transitions between research workers and synthesizer workers buy routing intermediate messages through a centralized supervisor knowed wait assign routing decisions to a specialized classification prompt instead um specialized classification prompts evaluat worker outputs across sixteen conversation turns buy selecting the next active worker knowed from the state graph",
        "refined_text": "Our LangGraph multi-agent pipeline configures state transitions between research workers and synthesizer workers by routing intermediate messages through a centralized supervisor node, assigning routing decisions to a specialized classification prompt instead.\n\nSpecialized classification prompts evaluate worker outputs across 16 conversation turns by selecting the next active worker node from the state graph."
    },
    {
        # Medium 7: Shared KV prefix caching
        "raw_asr": "uh our inference gateway optimizes prompt caching across twenty four tenant pipelines buy preserving static system prompt prefixes inside the shared key value cache wait isolate tenant parameters inside downstream dynamic prompt blocks instead um static system prompt caching accelerates time to first token across twelve hundred active requests buy reusing precomputed attention matrices",
        "refined_text": "Our inference gateway optimizes prompt caching across 24 tenant pipelines by preserving static system prompt prefixes inside the shared key-value cache, isolating tenant parameters inside downstream dynamic prompt blocks instead.\n\nStatic system prompt caching accelerates time to first token across 1200 active requests by reusing precomputed attention matrices."
    },
    {
        # Medium 8: Tool calling schema repair loop
        "raw_asr": "our agent execution harness detects invalid function calling responses across thirty two database inspection tools wait dispatch schema repair prompts directly to the llm generator instead um schema repair prompts display validation errors and expected field signatures buy guiding the model towards valid arguments within two correction iterations",
        "refined_text": "Our agent execution harness detects invalid function calling responses across 32 database inspection tools, dispatching schema repair prompts directly to the LLM generator instead.\n\nSchema repair prompts display validation errors and expected field signatures by guiding the model towards valid arguments within 2 correction iterations."
    },
    {
        # Medium 9: BGE reranker cross-encoder filtering
        "raw_asr": "uh our rag retrieval pipeline truncates sixty candidate document passages down into eight relevant context chunks buy executing a cross encoder reranking pass wait score passage relevance using a b g e reranker model instead um b g e reranker models filter peripheral background noise buy scoring query document relevance across one zero two four token context limits",
        "refined_text": "Our RAG retrieval pipeline truncates 60 candidate document passages down into 8 relevant context chunks by executing a cross-encoder reranking pass, scoring passage relevance using a BGE reranker model instead.\n\nBGE reranker models filter peripheral background noise by scoring query document relevance across 1024 token context limits."
    },
    {
        # Medium 10: Session token compaction & summary
        "raw_asr": "basically our session management service monitors active conversation histories across seventy two customer support agents buy measuring cumulative token consumption wait generat structured conversation summaries using an a sink worker instead um structured conversation summaries compress historical dialog turns from four hundred messages down into one hundred messages buy preserving key user requests and entity attributes",
        "refined_text": "Our session management service monitors active conversation histories across 72 customer support agents by measuring cumulative token consumption, generating structured conversation summaries using an async worker instead.\n\nStructured conversation summaries compress historical dialog turns from 400 messages down into 100 messages by preserving key user requests and entity attributes."
    },

    # Tier 3: Long (90+ words) - Exactly 10 samples
    {
        # Long 11: Llama Guard jailbreak defense & XML tags
        "raw_asr": "our trust and safety engineering team updated the agent system prompt architecture across sixteen conversational service pipelines buy hardening prompt boundary formatting against adversarial jailbreak attempts our legacy prompt template concatenated user inputs directly into the instruction context where prompt injection attacks bypassed persona instructions buy instructing the agent to ignore previous constraints and expose sensitive system prompts um the updated system prompt embeds system instructions inside explicit x m l tags buy enforcing strict delimiter parsing within the inference runtime so basically when the when the input ingestion worker receives incoming user queries an automated safety filter runs llama guard classification across eight threat categories buy blocking malicious inputs before tokenization uh our production evaluation across twenty four test suites demonstrated that structured x m l tag isolation reduced adversarial prompt bypass rates from eighteen percent down into zero percent while preserving valid customer intent across four thousand validation benchmarks",
        "refined_text": "Our trust and safety engineering team updated the agent system prompt architecture across 16 conversational service pipelines by hardening prompt boundary formatting against adversarial jailbreak attempts. Our legacy prompt template concatenated user inputs directly into the instruction context, where prompt injection attacks bypassed persona instructions by instructing the agent to ignore previous constraints and expose sensitive system prompts.\n\nThe updated system prompt embeds system instructions inside explicit XML tags by enforcing strict delimiter parsing within the inference runtime. When input ingestion workers receive incoming user queries, an automated safety filter runs Llama Guard classification across 8 threat categories by blocking malicious inputs before tokenization. Our production evaluation across 24 test suites demonstrated that structured XML tag isolation reduced adversarial prompt bypass rates from 18 percent down into 0 percent, while preserving valid customer intent across 4000 validation benchmarks."
    },
    {
        # Long 12: Parallel tool calling dispatcher
        "raw_asr": "our agent runtime infrastructure team refactored the tool execution engine across thirty two autonomous analysis agents buy replacing sequential tool calls with a sink parallel tool dispatching our previous agent loop executed tool calls one buy one where chained database queries and network diagnostics incurred cumulative round trip latencies exceeding twelve seconds per workflow step um the modernized agent harness parses parallel tool calls emitted buy the llm buy utilizing strict j son schema declarations registered across twenty four backend services so basically when the when the reasoning engine generates multiple tool calls simultaneously an a sink dispatcher executes each function concurrently buy collecting structured tool responses within an event loop uh benchmark profiling across sixteen integration environments confirmed that a sink parallel tool execution reduced p ninety five agent step completion times from twelve seconds down into three seconds while maintaining complete schema validat across eight hundred synthetic workload runs",
        "refined_text": "Our agent runtime infrastructure team refactored the tool execution engine across 32 autonomous analysis agents by replacing sequential tool calls with async parallel tool dispatching. Our previous agent loop executed tool calls one by one, where chained database queries and network diagnostics incurred cumulative round-trip latencies exceeding 12 seconds per workflow step.\n\nThe modernized agent harness parses parallel tool calls emitted by the LLM by utilizing strict JSON schema declarations registered across 24 backend services. When the reasoning engine generates multiple tool calls simultaneously, an async dispatcher executes each function concurrently by collecting structured tool responses within an event loop. Benchmark profiling across 16 integration environments confirmed that async parallel tool execution reduced P95 agent step completion times from 12 seconds down into 3 seconds, while maintaining complete schema validation across 800 synthetic workload runs."
    },
    {
        # Long 13: Sliding window memory compaction
        "raw_asr": "our context management engineering team overhauled session memory compaction across forty eight autonomous support agents buy replacing naive message eviction with recursive semantic summarizat our earlier context pipeline dropped older dialog turns once token consumption reached three two seven six eight tokens which frequently erased critical user constraints and prior tool execution outcomes um the new memory architecture splits conversation history into a sliding active window of sixteen recent turns and a compressed background summary buy preserving key entity bindings inside the prompt prefix so basically when the when the total token count exceeds four eight zero zero zero tokens a background worker invokes a fast summarizer model buy extracting unresolved action items and state variables uh production telemetry across sixty four agent deployments showed that semantic summarizat reduced context truncation errors from twenty eight percent down into one percent while maintaining steady token budgets across twelve hundred active customer sessions",
        "refined_text": "Our context management engineering team overhauled session memory compaction across 48 autonomous support agents by replacing naive message eviction with recursive semantic summarization. Our earlier context pipeline dropped older dialog turns once token consumption reached 32768 tokens, which frequently erased critical user constraints and prior tool execution outcomes.\n\nThe new memory architecture splits conversation history into a sliding active window of 16 recent turns and a compressed background summary by preserving key entity bindings inside the prompt prefix. When the total token count exceeds 48000 tokens, a background worker invokes a fast summarizer model by extracting unresolved action items and state variables. Production telemetry across 64 agent deployments showed that semantic summarization reduced context truncation errors from 28 percent down into 1 percent, while maintaining steady token budgets across 1200 active customer sessions."
    },
    {
        # Long 14: LangGraph multi-agent DAG orchestrator
        "raw_asr": "our core platform architecture group redesigned our enterprise document analysis pipeline buy replacing monolithic system prompts with a lang graph directed acyclic graph architecture our initial single prompt design struggled with cognitive overload because combining document retrieval table parsing and compliance auditing inside one prompt caused frequent hallucinations and missing analysis sections um the hierarchical multi agent architecture routes tasks through a central orchestrator knowed that assigns execution steps to specialized sub agents buy tracking state across a shared graph memory schema so basically when the when the orchestrator receives a financial disclosure filing specialized worker knowed instances execute extraction tasks across thirty two distinct tables buy validating tabular data against pydantic models uh regression evaluation across seventy two complex filings demonstrated that multi agent graph routing improved document extraction accuracy from seventy four percent up into ninety eight percent while eliminating deadlocks across twelve hundred automated batch evaluations",
        "refined_text": "Our core platform architecture group redesigned our enterprise document analysis pipeline by replacing monolithic system prompts with a LangGraph directed acyclic graph architecture. Our initial single-prompt design struggled with cognitive overload, because combining document retrieval, table parsing, and compliance auditing inside one prompt caused frequent hallucinations and missing analysis sections.\n\nThe hierarchical multi-agent architecture routes tasks through a central orchestrator node that assigns execution steps to specialized sub-agents by tracking state across a shared graph memory schema. When the orchestrator receives a financial disclosure filing, specialized worker node instances execute extraction tasks across 32 distinct tables by validating tabular data against Pydantic models. Regression evaluation across 72 complex filings demonstrated that multi-agent graph routing improved document extraction accuracy from 74 percent up into 98 percent, while eliminating deadlocks across 1200 automated batch evaluations."
    },
    {
        # Long 15: Hybrid dense/sparse RAG with BGE reranking
        "raw_asr": "our search and knowledge retrieval team upgraded our enterprise r a g pipeline across twenty four documentation domains buy combining dense vector embeddings with sparse inverted indexing our baseline vector search failed on exact identifier matches and error codes because dense representations smoothed over specific alphanumeric tokens um the hybrid retrieval engine queries b g e vector indices with one five three six dimensions while simultaneously querying sparse b m twenty five indices across five hundred thousand documents buy fusing candidate lists through reciprocal rank fusion so basically when the when the fusion stage completes candidates a cross encoder reranker model evaluates the top forty retrieved passages buy computing fine grained query passage cross attention scores uh our production evaluation across ninety six technical benchmark datasets demonstrated that hybrid retrieval with cross encoder reranking improved mean reciprocal rank from sixty four percent up into ninety one percent while keeping p ninety nine retrieval latency below three hundred fifty milliseconds",
        "refined_text": "Our search and knowledge retrieval team upgraded our enterprise RAG pipeline across 24 documentation domains by combining dense vector embeddings with sparse inverted indexing. Our baseline vector search failed on exact identifier matches and error codes, because dense representations smoothed over specific alphanumeric tokens.\n\nThe hybrid retrieval engine queries BGE vector indices with 1536 dimensions while simultaneously querying sparse BM25 indices across 500000 documents by fusing candidate lists through reciprocal rank fusion. When the fusion stage completes candidates, a cross-encoder reranker model evaluates the top 40 retrieved passages by computing fine-grained query-passage cross-attention scores. Our production evaluation across 96 technical benchmark datasets demonstrated that hybrid retrieval with cross-encoder reranking improved mean reciprocal rank from 64 percent up into 91 percent, while keeping P99 retrieval latency below 350 milliseconds."
    },
    {
        # Long 16: Grammar-constrained FSM structured output decoding
        "raw_asr": "our inference runtime optimization group overhauled structured data generation across thirty two extraction pipelines buy replacing prompt based json formatting with grammar constrained f s m decoding our legacy pipeline relied on few shot system prompt instructions which frequently suffered from syntax violations and trailing commas when generating deeply nested records um the grammar constrained decoding engine builds a token level finite state machine from pydantic schemas buy masking invalid vocabulary tokens during every auto regressive sampling step so basically when the when the llm produces output tokens the sampling engine enforces valid json syntax transitions directly at the logit level buy preventing malformed payloads before completion uh stress validation across forty eight production extraction tasks confirmed that grammar constrained decoding achieved one hundred percent schema compliance across sixty four thousand generated records while reducing prompt token overhead buy sixteen percent",
        "refined_text": "Our inference runtime optimization group overhauled structured data generation across 32 extraction pipelines by replacing prompt-based JSON formatting with grammar-constrained FSM decoding. Our legacy pipeline relied on few-shot system prompt instructions, which frequently suffered from syntax violations and trailing commas when generating deeply nested records.\n\nThe grammar-constrained decoding engine builds a token-level finite state machine from Pydantic schemas by masking invalid vocabulary tokens during every auto-regressive sampling step. When the LLM produces output tokens, the sampling engine enforces valid JSON syntax transitions directly at the logit level by preventing malformed payloads before completion. Stress validation across 48 production extraction tasks confirmed that grammar-constrained decoding achieved 100 percent schema compliance across 64000 generated records, while reducing prompt token overhead by 16 percent."
    },
    {
        # Long 17: Multi-tenant KV cache prefix sharing
        "raw_asr": "our llm serving infrastructure team implemented automatic prefix caching across twenty four multi tenant inference clusters buy standardizing system prompt layout into static and dynamic token blocks our previous serving deployment recomputed full key value attention caches four identical corporate instructions across eighty thousand daily queries which created massive computational redundancy and elevated prefill latencies um the prefix cache architecture aligns common system guardrails into five one two token chunks buy reusing cached key value blocks across all shared tenant requests so basically when the when the inference server receives a prompt matching existing prefix hashes the scheduler bypasses prefill computation buy loading precomputed attention keys directly from high bandwidth memory uh telemetry across thirty two production model instances showed that automatic prefix caching reduced time to first token from seven hundred milliseconds down into sixty milliseconds while increasing serving throughput across sixteen tenant applications",
        "refined_text": "Our LLM serving infrastructure team implemented automatic prefix caching across 24 multi-tenant inference clusters by standardizing system prompt layout into static and dynamic token blocks. Our previous serving deployment recomputed full key-value attention caches for identical corporate instructions across 80000 daily queries, which created massive computational redundancy and elevated prefill latencies.\n\nThe prefix cache architecture aligns common system guardrails into 512 token chunks by reusing cached key-value blocks across all shared tenant requests. When the inference server receives a prompt matching existing prefix hashes, the scheduler bypasses prefill computation by loading precomputed attention keys directly from high-bandwidth memory. Telemetry across 32 production model instances showed that automatic prefix caching reduced time to first token from 700 milliseconds down into 60 milliseconds, while increasing serving throughput across 16 tenant applications."
    },
    {
        # Long 18: LLM-as-a-judge CI/CD evaluation harness
        "raw_asr": "our ai platform quality team deployed an automated evaluation harness across thirty two model pipelines buy establishing a continuous llm as a judge regression testing suite our prompt development workflow previously relied on manual spot checks across arbitrary test queries which allowed subtle prompt regressions and format drifts to escape into production deployments um the continuous evaluation harness runs synthetic test suites buy scoring candidate model outputs against reference criteria using ragas context precision and faithfulness metrics across sixteen technical task categories so basically when the when the prompt engineer pushes updated system prompt templates the automated harness executes evaluation passes across eight hundred standardized prompt test cases buy flagging responses that drop below target score thresholds uh benchmark reports from forty eight prompt release cycles demonstrated that automated evaluation caught twenty four critical regression failures while cutting prompt evaluation turnaround from two days down into thirty minutes",
        "refined_text": "Our AI platform quality team deployed an automated evaluation harness across 32 model pipelines by establishing a continuous LLM-as-a-judge regression testing suite. Our prompt development workflow previously relied on manual spot checks across arbitrary test queries, which allowed subtle prompt regressions and format drifts to escape into production deployments.\n\nThe continuous evaluation harness runs synthetic test suites by scoring candidate model outputs against reference criteria using Ragas context precision and faithfulness metrics across 16 technical task categories. When prompt engineers push updated system prompt templates, the automated harness executes evaluation passes across 800 standardized prompt test cases by flagging responses that drop below target score thresholds. Benchmark reports from 48 prompt release cycles demonstrated that automated evaluation caught 24 critical regression failures, while cutting prompt evaluation turnaround from 2 days down into 30 minutes."
    },
    {
        # Long 19: Coding agent self-reflection repair loops
        "raw_asr": "our autonomous coding agent platform group upgraded the execution feedback loop across twenty four software repair agents buy adding an automated self reflection prompt stage our legacy agent architecture aborted execution immediately whenever syntax errors or failing unit tests occurred which created frequent workflow interruptions on minor compilation issues um the reflection loop captures execution trace errors and compiler output buy feeding formatted stack traces back into the reasoning prompt within an iterative repair cycle so basically when the when the agent receives failing test outputs the reflection prompt instructs the model to diagnose error triggers and plan patch modifications buy updating code files incrementally uh integration testing across forty eight complex coding benchmarks confirmed that self reflection repair loops improved automated bug fixing success rates from forty two percent up into eighty six percent while resolving failing test cases within three correction attempts",
        "refined_text": "Our autonomous coding agent platform group upgraded the execution feedback loop across 24 software repair agents by adding an automated self-reflection prompt stage. Our legacy agent architecture aborted execution immediately whenever syntax errors or failing unit tests occurred, which created frequent workflow interruptions on minor compilation issues.\n\nThe reflection loop captures execution trace errors and compiler output by feeding formatted stack traces back into the reasoning prompt within an iterative repair cycle. When the agent receives failing test outputs, the reflection prompt instructs the model to diagnose error triggers and plan patch modifications by updating code files incrementally. Integration testing across 48 complex coding benchmarks confirmed that self-reflection repair loops improved automated bug fixing success rates from 42 percent up into 86 percent, while resolving failing test cases within 3 correction attempts."
    },
    {
        # Long 20: Strict JSON schema parameter validation
        "raw_asr": "our conversational commerce architecture group redesigned our tool call validation layer across sixteen customer assistant agents buy implementing strict json schema parameter casting and fallback recovery handlers our baseline agent runtime experienced frequent tool execution crashes when the language model passed string representations of integer identifiers or hallucinated unsupported query parameters um the enhanced validation layer sanitizes incoming tool call arguments buy matching property types against strict pydantic schemas before function execution so basically when the when the argument parser detects an invalid parameter type or missing required field an automated recovery prompt provides the exact schema definition buy guiding the model to correct parameters within two correction turns uh production monitoring across sixty four deployed tools demonstrated that strict parameter validation and automated error feedback reduced tool execution failures from thirty six percent down into zero percent across sixteen thousand daily transactions",
        "refined_text": "Our conversational commerce architecture group redesigned our tool call validation layer across 16 customer assistant agents by implementing strict JSON schema parameter casting and fallback recovery handlers. Our baseline agent runtime experienced frequent tool execution crashes when the language model passed string representations of integer identifiers or hallucinated unsupported query parameters.\n\nThe enhanced validation layer sanitizes incoming tool call arguments by matching property types against strict Pydantic schemas before function execution. When the argument parser detects an invalid parameter type or missing required field, an automated recovery prompt provides the exact schema definition by guiding the model to correct parameters within 2 correction turns. Production monitoring across 64 deployed tools demonstrated that strict parameter validation and automated error feedback reduced tool execution failures from 36 percent down into 0 percent across 16000 daily transactions."
    }
]

def main():
    print(f"Total samples: {len(batch_97)}")
    assert len(batch_97) == 20, f"Expected 20 samples, got {len(batch_97)}"

    # Check each pair with validate_pair and clean_sample
    all_pairs_valid = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for idx, pair in enumerate(batch_97):
        words = len(pair["refined_text"].split())
        if words < 25:
            tier = "short"
        elif words < 90:
            tier = "medium"
        else:
            tier = "long"
        tier_counts[tier] += 1

        val_ok, val_reason = validate_pair(pair)
        clean_res, clean_status = clean_sample(pair["raw_asr"], pair["refined_text"])

        if not val_ok or clean_status != "kept":
            all_pairs_valid = False
            print(f"FAIL sample {idx+1} ({tier}, {words} words):")
            print(f"  validate_pair: {val_ok} ({val_reason})")
            print(f"  clean_sample: {clean_status}")
        else:
            print(f"PASS sample {idx+1} ({tier}, {words} words): validate=OK, clean=kept")

    # Check batch
    batch_ok, batch_reason, batch_tiers = validate_batch(batch_97, min_short=4, min_medium=6, min_long=10)
    print(f"\nBatch Validation: {batch_ok} ({batch_reason})")
    print(f"Tier counts: {batch_tiers}")

    if all_pairs_valid and batch_ok:
        output_path = "scratch/subagent_batch_97.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(batch_97, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully wrote verified batch to {output_path}")
    else:
        print("\nErrors detected! Aborting write.")
        sys.exit(1)

if __name__ == "__main__":
    main()
