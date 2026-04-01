# EMI-32: LLM Stack Scored Comparison Matrix

**Date:** 2026-04-01  
**Author:** AI & LLM Solutions Architect  
**Story:** EMI-32

---

## Scoring Criteria

| # | Criterion | Weight Notes |
|---|-----------|-------------|
| C1 | UK energy domain capability | Higher = better domain fit |
| C2 | Cost at scale | Higher = lower cost |
| C3 | Latency | Higher = lower latency |
| C4 | Context window | Higher = larger window |
| C5 | Fine-tuning options | Higher = more flexible |
| C6 | Data privacy / UK data residency | Higher = stronger compliance |
| C7 | Vendor lock-in risk | Higher = lower lock-in |

**Scale: 1–5 per criterion. Max score per layer: 35.**

---

## Layer 1: LLM Providers

| Model | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total /35 | Decision |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|---------|
| **Llama 3.1 70B (self-hosted, fine-tuned)** | 5 | 5 | 4 | 5 | 5 | 5 | 4 | **33** | ✅ Primary |
| Mistral Large 2 (La Plateforme EU) | 3 | 4 | 4 | 4 | 3 | 3 | 3 | **24** | ✅ Tier-2 Fallback |
| GPT-4o (Azure UK South) | 4 | 2 | 5 | 4 | 3 | 2 | 2 | **22** | ✅ Tier-3 Non-PII only |
| Gemini 1.5 Pro (Vertex AI) | 3 | 3 | 3 | 5 | 2 | 2 | 2 | **20** | Conditional |
| Claude 3.5 Sonnet (Anthropic) | 4 | 2 | 4 | 4 | 1 | 1 | 3 | **19** | 🔴 Hard Reject |

**Notes:**
- Claude 3.5: No fine-tuning (C5=1), US-only routing (C6=1) — hard reject
- Llama fine-tuning score reflects post-fine-tune quality on energy corpus
- Mistral: Must use La Plateforme EU direct — routing via Azure drops C6 to 2

---

## Layer 2: Orchestration Frameworks

| Framework | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total /35 | Decision |
|-----------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|---------|
| **LlamaIndex** | 4 | 5 | 4 | — | 4 | 4 | — | **21** (/30) | ✅ Primary |
| Haystack (deepset) | 4 | 4 | 4 | — | 4 | 4 | — | **20** (/30) | Fallback |
| CrewAI | 3 | 4 | 3 | — | 3 | 2 | — | **15** (/30) | Supplementary |
| LangChain | 3 | 3 | 3 | — | 3 | 1 | — | **13** (/30) | 🔴 Hard Reject |

**Notes:**
- C4, C7 not applicable to orchestration frameworks
- LangChain C6=1: CVE-2025-68664 (CVSS 9.3) + LangSmith default telemetry to US servers

---

## Layer 3: Vector Databases

| Store | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total /35 | Decision |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|---------|
| **pgvector (self-hosted)** | 4 | 5 | 4 | — | — | 5 | 4 | **22** (/30) | ✅ Primary (<10M) |
| Qdrant (self-hosted) | 4 | 5 | 5 | — | — | 5 | 2 | **21** (/30) | ✅ Overflow (>10M) |
| Weaviate | 3 | 3 | 4 | — | — | 4 | 2 | **16** (/30) | — |
| ChromaDB | 3 | 5 | 3 | — | — | 4 | 3 | **18** (/30) | Dev/test only |
| Pinecone | 3 | 2 | 5 | — | — | 1 | 1 | **12** (/30) | 🔴 Hard Reject |

**Notes:**
- C4, C5 not applicable to vector databases
- pgvector uniquely satisfies UK GDPR Art. 17 via ACID `DELETE CASCADE` (C6=5)
- Pinecone C6=1, C7=1: US-only, no self-hosted, maximum lock-in — hard reject

---

## Layer 4: Embedding Models

| Model | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total /35 | Decision |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|---------|
| **BGE-M3 (fine-tuned, self-hosted)** | 5 | 5 | 4 | 5 | 5 | 5 | 4 | **33** | ✅ Primary |
| E5-large (self-hosted) | 4 | 5 | 4 | 4 | 3 | 5 | 4 | **29** | Fallback |
| Cohere Embed v3 | 3 | 3 | 4 | 4 | 2 | 3 | 2 | **21** | — |
| OpenAI text-embedding-3-large | 4 | 1 | 5 | 4 | 1 | 1 | 1 | **17** | 🔴 Rejected |

**Notes:**
- OpenAI: ~$130K/yr at scale (C2=1); US data egress on every call (C6=1); no fine-tuning (C5=1) — rejected
- BGE-M3 C1=5 reflects post-fine-tuning performance on energy corpus

---

## Layer 5: Infrastructure

| Option | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total /35 | Decision |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---------:|---------|
| **Self-hosted Sovereign (OVHcloud/CUDO UK)** | 5 | 5 | 4 | — | 5 | 5 | 5 | **29** (/35\*) | ✅ Primary |
| GCP Vertex AI (europe-west2) | 3 | 3 | 4 | — | 3 | 3 | 2 | **18** (/35\*) | Conditional |
| Azure OpenAI (UK South) | 3 | 3 | 5 | — | 3 | 2 | 2 | **18** (/35\*) | Tier-3 fallback |
| AWS Bedrock (eu-west-2) | 3 | 3 | 4 | — | 2 | 1 | 2 | **15** (/35\*) | 🔴 Hard Reject |

**Notes:**
- C4 not applicable to infrastructure
- AWS Bedrock C6=1: fine-tuning routes to us-east-1 regardless of inference region — architecturally incompatible with UK data residency

---

## Recommended Full Stack

| Layer | Primary | Fallback | Hard Rejects |
|-------|---------|----------|--------------|
| **LLM** | Llama 3.1 70B (self-hosted, fine-tuned) | Mistral Large 2 EU → GPT-4o Azure UK South | Claude 3.5 Sonnet, AWS Bedrock |
| **Orchestration** | LlamaIndex | Haystack | **LangChain (CVE-2025-68664)** |
| **Vector DB** | pgvector (self-hosted) | Qdrant self-hosted (>10M vectors) | **Pinecone** |
| **Embeddings** | BGE-M3 (fine-tuned, self-hosted) | E5-large (self-hosted) | OpenAI embeddings |
| **Infrastructure** | OVHcloud / CUDO UK (sovereign) | Azure UK South (non-PII only) | **AWS Bedrock** |

---

## Cost Comparison

| Scenario | Monthly Cost |
|----------|:-----------:|
| All-API baseline (OpenAI/Anthropic) | $45,000–90,000 |
| **Recommended sovereign stack** | **$6,500–9,000** |
| Saving | **$38,500–81,000/mo (85–90%)** |

### Recommended Stack Breakdown
| Component | Monthly |
|-----------|:-------:|
| Tier 1 — Llama 3.1 70B self-hosted (~75% traffic) | $4,000–5,000 |
| Tier 2 — Mistral Large 2 EU (~15% traffic) | $800–1,200 |
| Tier 3 — GPT-4o Azure UK South (~10% traffic) | $1,500–2,500 |
| Storage, embedding serving, pgvector/Qdrant | $300–500 |
| **Total** | **$6,500–9,000** |

---

## Regulatory Pre-conditions (All Production-Blocking)

| # | Item | Owner |
|---|------|-------|
| OI-1 | Board-level AI accountability officer appointed (OFG1164) | Board |
| OI-2 | DPIA completed for vector store and embedding pipeline | DPO |
| OI-3 | Board-level CLOUD Act risk acceptance for Tier-2/3 documented | Board + Legal |
| OI-4 | REMIT compliance review of LLM output governance | Compliance |
| OI-5 | NIS supply chain risk assessment: OVHcloud + CUDO | Security |
| OI-6 | PII/sensitivity pre-routing classifier built and tested | Engineering |
| OI-7 | Sovereign failover tested (OVHcloud → CUDO) | Engineering |
| OI-8 | Audit logging schema reviewed by DPO; tamper-evident store operational | DPO + Engineering |
| OI-9 | BGE-M3 fine-tuning corpus ready (5,000+ QA pairs); first run complete | ML Engineering |
| OI-10 | Domain eval benchmark suite established | ML Engineering |
