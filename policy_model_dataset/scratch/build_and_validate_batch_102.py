import json
import sys
import os

sys.path.insert(0, "code")
from validator import validate_pair, validate_batch
from cleaner import clean_sample

batch_102 = [
    # Tier 1: Short (< 25 words) - Exactly 4 samples
    {
        # Short 1: DSPy signature optimization
        "raw_asr": "um prompt engineers configur d s p y assertions buy validating structured intermediate reasoning steps across multi hop agent pipelines",
        "refined_text": "Prompt engineers configure DSPy assertions by validating structured intermediate reasoning steps across multi-hop agent pipelines."
    },
    {
        # Short 2: Token budget truncation / sliding window attention
        "raw_asr": "uh inference engineers allocat fixed token budgets buy constraining sliding window attention caches into four zero nine six tokens",
        "refined_text": "Inference engineers allocate fixed token budgets by constraining sliding window attention caches into 4096 tokens."
    },
    {
        # Short 3: Outlines regex-guided JSON generation
        "raw_asr": "basically compiler runtimes validat structured agent outputs buy constraining next token probability distributions with regular expressions",
        "refined_text": "Compiler runtimes validate structured agent outputs by constraining next-token probability distributions with regular expressions."
    },
    {
        # Short 4: Constitutional AI guardrails / critique revision
        "raw_asr": "um constitutional agent workflows evaluat safety compliance buy applying iterative self critique prompts before emitting final answers",
        "refined_text": "Constitutional agent workflows evaluate safety compliance by applying iterative self-critique prompts before emitting final answers."
    },

    # Tier 2: Medium (25-89 words) - Exactly 6 samples
    {
        # Medium 5: ReAct framework / scratchpad tool calling
        "raw_asr": "our react agent runtime organizes execution steps across thirty two diagnostic workflows wait structure reasoning traces using thought action observation cycles instead um structured scratchpad formatting separates intermediate deductions from tool inputs buy preserving clean reasoning traces across sixteen execution steps",
        "refined_text": "Our ReAct agent runtime organizes execution steps across 32 diagnostic workflows, structuring reasoning traces using thought action observation cycles instead.\n\nStructured scratchpad formatting separates intermediate deductions from tool inputs by preserving clean reasoning traces across 16 execution steps."
    },
    {
        # Medium 6: AutoGen conversational multi-agent debate
        "raw_asr": "basically our multi agent consensus pipeline manages debate turns across three autonomous critic knowed instances buy verifying code safety invariants wait terminate consensus discussions once two consecutive agreement rounds occur instead um agreement detection logic tracks shared proposition tokens across twenty four conversation turns buy preventing redundant argument loops",
        "refined_text": "Our multi-agent consensus pipeline manages debate turns across 3 autonomous critic node instances by verifying code safety invariants, terminating consensus discussions once 2 consecutive agreement rounds occur instead.\n\nAgreement detection logic tracks shared proposition tokens across 24 conversation turns by preventing redundant argument loops."
    },
    {
        # Medium 7: ColBERT late interaction token retrieval
        "raw_asr": "uh our enterprise retrieval engine replaces single vector embeddings across forty eight knowledge bases buy executing token level late interaction matching wait rank candidate document chunks using colbert scoring matrices instead um colbert token representations preserv fine grained lexical nuances across one two eight token query lengths buy computing maximal inner product operations over candidate vectors",
        "refined_text": "Our enterprise retrieval engine replaces single-vector embeddings across 48 knowledge bases by executing token-level late interaction matching, ranking candidate document chunks using ColBERT scoring matrices instead.\n\nColBERT token representations preserve fine-grained lexical nuances across 128 token query lengths by computing maximal inner product operations over candidate vectors."
    },
    {
        # Medium 8: Semantic Router intent dispatch
        "raw_asr": "our routing gateway classifies incoming user intents across sixteen enterprise workflows wait route queries using semantic embedding encoders instead um semantic router layers compare query vectors against thirty two predefined route clusters buy bypassing expensive llm inference calls within five milliseconds",
        "refined_text": "Our routing gateway classifies incoming user intents across 16 enterprise workflows, routing queries using semantic embedding encoders instead.\n\nSemantic router layers compare query vectors against 32 predefined route clusters by bypassing expensive LLM inference calls within 5 milliseconds."
    },
    {
        # Medium 9: Instructor library Pydantic response parsing
        "raw_asr": "basically our data extraction service integrates the instructor framework across twenty four backend pipelines buy enforcing strict pydantic response schemas wait handle missing schema properties buy triggering automated re prompt cycles instead um automated re prompt cycles provide detailed validation errors back to the language model buy resolving malformed fields within two retry attempts",
        "refined_text": "Our data extraction service integrates the Instructor framework across 24 backend pipelines by enforcing strict Pydantic response schemas, handling missing schema properties by triggering automated re-prompt cycles instead.\n\nAutomated re-prompt cycles provide detailed validation errors back to the language model by resolving malformed fields within 2 retry attempts."
    },
    {
        # Medium 10: SGLang RadixAttention KV reuse
        "raw_asr": "uh our serving infrastructure accelerates multi turn conversational throughput across sixty four model instances buy implementing radix tree key value caching wait preserve shared system prompt prefixes inside a radix attention tree instead um radix attention trees retain precomputed attention states across two zero four eight prompt prefix tokens buy eliminating redundant prefill computation",
        "refined_text": "Our serving infrastructure accelerates multi-turn conversational throughput across 64 model instances by implementing radix tree key-value caching, preserving shared system prompt prefixes inside a RadixAttention tree instead.\n\nRadixAttention trees retain precomputed attention states across 2048 prompt prefix tokens by eliminating redundant prefill computation."
    },

    # Tier 3: Long (90+ words) - Exactly 10 samples
    {
        # Long 11: Prompt Injection & Indirect Jailbreak Defense with Canary Tokens
        "raw_asr": "our trust and security platform team overhauled prompt injection defenses across sixteen autonomous customer service pipelines buy deploying canary tokens alongside dual llm validation boundaries our earlier system prompt design allowed indirect prompt injection payloads embedded inside retrieved knowledge base articles to override agent system rules buy commanding the model to exfiltrate private conversation records um the updated security architecture injects random canary tokens into system prompt boundaries while routing all retrieved text through a secondary quarantine classifier model so basically when the when the quarantine worker detects suspicious instruction tokens an automated sanitizer strips untrusted directives before context assembly uh empirical testing across twenty four red team attack suites confirmed that canary token validation achieved one hundred percent injection detection across five hundred simulated adversarial documents while maintaining zero false positive rejections across four thousand normal user inquiries",
        "refined_text": "Our trust and security platform team overhauled prompt injection defenses across 16 autonomous customer service pipelines by deploying canary tokens alongside dual LLM validation boundaries. Our earlier system prompt design allowed indirect prompt injection payloads embedded inside retrieved knowledge base articles to override agent system rules by commanding the model to exfiltrate private conversation records.\n\nThe updated security architecture injects random canary tokens into system prompt boundaries while routing all retrieved text through a secondary quarantine classifier model. When the quarantine worker detects suspicious instruction tokens, an automated sanitizer strips untrusted directives before context assembly. Empirical testing across 24 red team attack suites confirmed that canary token validation achieved 100 percent injection detection across 500 simulated adversarial documents, while maintaining zero false positive rejections across 4000 normal user inquiries."
    },
    {
        # Long 12: DSPy BootstrapFewShot Compilation for Multi-Hop QA Agent
        "raw_asr": "our machine learning platform squad upgraded prompt engineering workflows across thirty two information retrieval agents buy replacing fragile manual few shot prompts with d s p y signature compilation our initial prompt templates suffered from severe accuracy degradation whenever downstream foundation models updated because handcrafted demonstrations failed to generalize across subtle semantic shifts um the compiler pipeline optimizes multi hop signatures buy using bootstrap few shot teleprompters that iteratively search over candidate demonstrations across sixty four seed training exemplars so basically when the when the teleprompter executes validation passes an automated metric evaluator scores reasoning trajectories against gold reference answers buy selecting the top eight most effective demonstrations uh comprehensive evaluation across four hundred validation samples demonstrated that d s p y signature compilation improved answer accuracy from sixty two percent up into eighty eight percent while reducing average token consumption buy fourteen percent",
        "refined_text": "Our machine learning platform squad upgraded prompt engineering workflows across 32 information retrieval agents by replacing fragile manual few-shot prompts with DSPy signature compilation. Our initial prompt templates suffered from severe accuracy degradation whenever downstream foundation models updated, because handcrafted demonstrations failed to generalize across subtle semantic shifts.\n\nThe compiler pipeline optimizes multi-hop signatures by using bootstrap few-shot teleprompters that iteratively search over candidate demonstrations across 64 seed training exemplars. When the teleprompter executes validation passes, an automated metric evaluator scores reasoning trajectories against gold reference answers by selecting the top 8 most effective demonstrations. Comprehensive evaluation across 400 validation samples demonstrated that DSPy signature compilation improved answer accuracy from 62 percent up into 88 percent, while reducing average token consumption by 14 percent."
    },
    {
        # Long 13: vLLM PagedAttention Chunked Prefill & Multi-Turn Latency Tuning
        "raw_asr": "our llm serving operations team reconfigured high concurrency inference parameters across forty eight serving gpus buy enabling paged attention chunked prefill scheduling our legacy serving setup suffered from severe head of line blocking during multi turn agent sessions because long prompt context prefills stalled concurrent token generation steps across active worker streams um the chunked prefill scheduler divides extended prompt inputs into uniform chunks of five one two tokens buy interleaving decode iterations between partial prefill computations so basically when the when the inference engine processes extended agent message chains reaching eight one nine two tokens the scheduler maintains continuous decoding throughput across sixteen concurrent client streams uh production telemetry across twenty four serving clusters confirmed that chunked prefill scheduling reduced p ninety nine time to first token from eight five zero milliseconds down into one one zero milliseconds while improving overall serving concurrency buy thirty five percent",
        "refined_text": "Our LLM serving operations team reconfigured high concurrency inference parameters across 48 serving GPUs by enabling PagedAttention chunked prefill scheduling. Our legacy serving setup suffered from severe head-of-line blocking during multi-turn agent sessions, because long prompt context prefills stalled concurrent token generation steps across active worker streams.\n\nThe chunked prefill scheduler divides extended prompt inputs into uniform chunks of 512 tokens by interleaving decode iterations between partial prefill computations. When the inference engine processes extended agent message chains reaching 8192 tokens, the scheduler maintains continuous decoding throughput across 16 concurrent client streams. Production telemetry across 24 serving clusters confirmed that chunked prefill scheduling reduced P99 time to first token from 850 milliseconds down into 110 milliseconds, while improving overall serving concurrency by 35 percent."
    },
    {
        # Long 14: CrewAI Role-Playing Multi-Agent Hierarchical Delegation
        "raw_asr": "our autonomous solutions group restructured financial audit workflows across sixteen enterprise pipelines buy organizing collaborative agent crews using the crew a i hierarchical process manager our prior single agent prompt implementation frequently lost track of complex corporate compliance guidelines buy attempting to research write and audit documents in a single reasoning pass um the hierarchical crew structure divides responsibilities among four specialized agents covering research financial analysis compliance verification and report synthesis buy enforcing strict role based system prompts so basically when the when the manager agent assigns tasks across twenty four workflow steps a centralized orchestrator knowed tracks task outputs inside shared memory while preventing infinite delegation loops buy capping recursion depth at five iterations uh regression testing across thirty two complex financial disclosures confirmed that hierarchical crew execution increased document factual precision from seventy one percent up into ninety five percent while eliminating circular agent delegation failures",
        "refined_text": "Our autonomous solutions group restructured financial audit workflows across 16 enterprise pipelines by organizing collaborative agent crews using the CrewAI hierarchical process manager. Our prior single-agent prompt implementation frequently lost track of complex corporate compliance guidelines by attempting to research, write, and audit documents in a single reasoning pass.\n\nThe hierarchical crew structure divides responsibilities among 4 specialized agents covering research, financial analysis, compliance verification, and report synthesis by enforcing strict role-based system prompts. When the manager agent assigns tasks across 24 workflow steps, a centralized orchestrator node tracks task outputs inside shared memory while preventing infinite delegation loops by capping recursion depth at 5 iterations. Regression testing across 32 complex financial disclosures confirmed that hierarchical crew execution increased document factual precision from 71 percent up into 95 percent, while eliminating circular agent delegation failures."
    },
    {
        # Long 15: Agentic RAG with Self-RAG Reflective Retrieval & Hallucination Suppression
        "raw_asr": "our knowledge platform engineering group revamped information retrieval pipelines across thirty two technical documentation portals buy deploying self rag reflective tokens into our agent prompt architecture our baseline retrieval system triggered external vector searches on every single query turn which introduced irrelevant context noise and increased token latency on simple factual questions um the self rag architecture trains the reasoning model to generate special critique tokens buy predicting whether retrieval is necessary evaluating passage relevance and auditing answer support so basically when the when the agent decodes an explicit retrieve token the pipeline queries vector indices to fetch candidate passages buy filtering sixty candidate passages down into six verified chunks uh evaluation benchmarking across forty eight technical domains demonstrated that reflective token gating reduced unnecessary vector retrieval calls buy forty percent while reducing hallucination rates from twenty four percent down into two percent across one thousand test queries",
        "refined_text": "Our knowledge platform engineering group revamped information retrieval pipelines across 32 technical documentation portals by deploying Self-RAG reflective tokens into our agent prompt architecture. Our baseline retrieval system triggered external vector searches on every single query turn, which introduced irrelevant context noise and increased token latency on simple factual questions.\n\nThe Self-RAG architecture trains the reasoning model to generate special critique tokens by predicting whether retrieval is necessary, evaluating passage relevance, and auditing answer support. When the agent decodes an explicit retrieve token, the pipeline queries vector indices to fetch candidate passages by filtering 60 candidate passages down into 6 verified chunks. Evaluation benchmarking across 48 technical domains demonstrated that reflective token gating reduced unnecessary vector retrieval calls by 40 percent, while reducing hallucination rates from 24 percent down into 2 percent across 1000 test queries."
    },
    {
        # Long 16: Structured Output Grammar Sampling via Outlines
        "raw_asr": "our platform integrations engineering team overhauled structured data extraction across twenty four api translation services buy implementing context free grammar guided logit masking using the outlines framework our previous system prompt relied on json schema descriptions and few shot exemplars which suffered from intermittent parsing exceptions whenever the generator emitted unescaped quote characters or trailing commas in nested lists um the grammar guided decoding engine compiles json schema definitions into finite state machines buy applying token masks over thirty two thousand vocabulary logits during every sampling step so basically when the when the language model predicts next token probabilities the runtime disables all syntactically invalid tokens directly at the inference layer buy guaranteeing valid payloads without retry prompts uh production benchmarking across thirty two extraction workflows confirmed that grammar guided logit masking achieved one hundred percent json parsing validity across fifty thousand production calls while reducing latency buy eighteen percent",
        "refined_text": "Our platform integrations engineering team overhauled structured data extraction across 24 API translation services by implementing context-free grammar-guided logit masking using the Outlines framework. Our previous system prompt relied on JSON schema descriptions and few-shot exemplars, which suffered from intermittent parsing exceptions whenever the generator emitted unescaped quote characters or trailing commas in nested lists.\n\nThe grammar-guided decoding engine compiles JSON schema definitions into finite state machines by applying token masks over 32000 vocabulary logits during every sampling step. When the language model predicts next-token probabilities, the runtime disables all syntactically invalid tokens directly at the inference layer by guaranteeing valid payloads without retry prompts. Production benchmarking across 32 extraction workflows confirmed that grammar-guided logit masking achieved 100 percent JSON parsing validity across 50000 production calls, while reducing latency by 18 percent."
    },
    {
        # Long 17: Semantic Cache with Fast Embedding Lookups
        "raw_asr": "our llm gateway operations squad deployed an enterprise semantic caching tier across sixty four tenant applications buy intercepting user queries before foundation model inference our baseline architecture dispatched every incoming prompt directly to backend models which resulted in massive inference expenses and high p ninety five latencies on repeated organizational queries um the semantic cache layer vectorizes incoming prompts using one five three six dimensional embeddings buy querying an in memory similarity index with a ninety five percent cosine similarity threshold so basically when the when the cache router finds a semantically equivalent query vector the gateway serves the cached completion payload immediately buy bypassing downstream llm generation uh telemetry analysis across twenty four production services showed that semantic caching intercepted twelve thousand daily requests buy saving forty percent in overall inference compute costs while reducing average response latency from nine zero zero milliseconds down into thirty milliseconds",
        "refined_text": "Our LLM gateway operations squad deployed an enterprise semantic caching tier across 64 tenant applications by intercepting user queries before foundation model inference. Our baseline architecture dispatched every incoming prompt directly to backend models, which resulted in massive inference expenses and high P95 latencies on repeated organizational queries.\n\nThe semantic cache layer vectorizes incoming prompts using 1536 dimensional embeddings by querying an in-memory similarity index with a 95 percent cosine similarity threshold. When the cache router finds a semantically equivalent query vector, the gateway serves the cached completion payload immediately by bypassing downstream LLM generation. Telemetry analysis across 24 production services showed that semantic caching intercepted 12000 daily requests by saving 40 percent in overall inference compute costs, while reducing average response latency from 900 milliseconds down into 30 milliseconds."
    },
    {
        # Long 18: LlamaIndex RouterQueryEngine with Multi-Index Partitioning
        "raw_asr": "our knowledge platform architecture group upgraded document reasoning pipelines across seventy two enterprise knowledge manuals buy replacing flat vector searches with a llama index router query engine our earlier retrieval approach struggled on hybrid questions because vector similarity failed to aggregate numerical data across structured financial tables while tabular text search missed conceptual background context um the router query engine partitions knowledge sources into structured s q l indices and semantic vector indices buy deploying a selector prompt that inspects user queries across sixteen routing channels so basically when the when the router classifies a query asking for numerical statistics the engine executes structured table queries while delegating narrative analysis to vector retrieval buy fusing intermediate summaries into a coherent final answer uh automated evaluation across forty eight complex document suites demonstrated that multi index query routing improved factual answer completeness from fifty eight percent up into ninety two percent across one five zero zero benchmark queries",
        "refined_text": "Our knowledge platform architecture group upgraded document reasoning pipelines across 72 enterprise knowledge manuals by replacing flat vector searches with a LlamaIndex router query engine. Our earlier retrieval approach struggled on hybrid questions, because vector similarity failed to aggregate numerical data across structured financial tables while tabular text search missed conceptual background context.\n\nThe router query engine partitions knowledge sources into structured SQL indices and semantic vector indices by deploying a selector prompt that inspects user queries across 16 routing channels. When the router classifies a query asking for numerical statistics, the engine executes structured table queries while delegating narrative analysis to vector retrieval by fusing intermediate summaries into a coherent final answer. Automated evaluation across 48 complex document suites demonstrated that multi-index query routing improved factual answer completeness from 58 percent up into 92 percent across 1500 benchmark queries."
    },
    {
        # Long 19: Long-Context Needle-In-A-Haystack Memory Retrieval & RoPE Scaling
        "raw_asr": "our ai foundation research squad investigated long context retrieval degradation across sixteen frontier agent deployments buy analyzing attention dispersion in extended context windows our diagnostic tests revealed that context recall decayed significantly beyond sixteen thousand tokens where models failed needle in a haystack retrieval buy ignoring localized facts hidden in massive document prompts um our infrastructure engineers mitigated context rot buy adjusting rotary position embedding base frequencies scaling the theta parameter from ten thousand up into five hundred thousand across six five five three six token windows so basically when the when the context compressor loads lengthy multi session agent transcripts the scaled position encodings preserv attention focus across distant prompt tokens uh benchmark evaluation across thirty two stress test configurations confirmed that scaled rotary embeddings increased needle in a haystack retrieval accuracy from thirty four percent up into ninety six percent across extended six five five three six token contexts while eliminating memory segmentation faults",
        "refined_text": "Our AI foundation research squad investigated long-context retrieval degradation across 16 frontier agent deployments by analyzing attention dispersion in extended context windows. Our diagnostic tests revealed that context recall decayed significantly beyond 16000 tokens, where models failed needle-in-a-haystack retrieval by ignoring localized facts hidden in massive document prompts.\n\nOur infrastructure engineers mitigated context rot by adjusting rotary position embedding base frequencies, scaling the theta parameter from 10000 up into 500000 across 65536 token windows. When the context compressor loads lengthy multi-session agent transcripts, the scaled position encodings preserve attention focus across distant prompt tokens. Benchmark evaluation across 32 stress test configurations confirmed that scaled rotary embeddings increased needle-in-a-haystack retrieval accuracy from 34 percent up into 96 percent across extended 65536 token contexts, while eliminating memory segmentation faults."
    },
    {
        # Long 20: Automated LLM-as-a-Judge Evaluation Pipeline with MT-Bench & Bidirectional Bias Mitigation
        "raw_asr": "our ai quality assurance team established an automated prompt benchmarking harness across forty eight candidate system prompts buy implementing pairwise llm as a judge scoring our prompt development cycle previously suffered from substantial evaluation latency and position bias because human evaluations took days to grade multi turn conversations while naive model judges favored whichever response appeared first in the prompt um the automated evaluation harness runs pairwise comparisons across eighty multi turn benchmark questions buy evaluating answer quality using bidirectional position swapping so basically when the when the evaluator model grades candidate outputs the harness averages scores across both presentation orders buy eliminating position bias while asserting inter annotator agreement using cohen kappa coefficients uh validation metrics across twenty four release cycles confirmed that automated pairwise evaluation caught thirty six prompt regression defects while compressing our prompt iteration lifecycle from five days down into four hours",
        "refined_text": "Our AI quality assurance team established an automated prompt benchmarking harness across 48 candidate system prompts by implementing pairwise LLM-as-a-judge scoring. Our prompt development cycle previously suffered from substantial evaluation latency and position bias, because human evaluations took days to grade multi-turn conversations while naive model judges favored whichever response appeared first in the prompt.\n\nThe automated evaluation harness runs pairwise comparisons across 80 multi-turn benchmark questions by evaluating answer quality using bidirectional position swapping. When the evaluator model grades candidate outputs, the harness averages scores across both presentation orders by eliminating position bias, while asserting inter-annotator agreement using Cohen kappa coefficients. Validation metrics across 24 release cycles confirmed that automated pairwise evaluation caught 36 prompt regression defects, while compressing our prompt iteration lifecycle from 5 days down into 4 hours."
    }
]

def main():
    print(f"Total samples: {len(batch_102)}")
    assert len(batch_102) == 20, f"Expected 20 samples, got {len(batch_102)}"

    all_pairs_valid = True
    tier_counts = {"short": 0, "medium": 0, "long": 0}

    for idx, pair in enumerate(batch_102):
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
    batch_ok, batch_reason, batch_tiers = validate_batch(batch_102, min_short=4, min_medium=6, min_long=10)
    print(f"\nBatch Validation: {batch_ok} ({batch_reason})")
    print(f"Tier counts: {batch_tiers}")

    if all_pairs_valid and batch_ok:
        output_path = "scratch/subagent_batch_102.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(batch_102, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully wrote verified batch to {output_path}")
    else:
        print("\nErrors detected! Aborting write.")
        sys.exit(1)

if __name__ == "__main__":
    main()
