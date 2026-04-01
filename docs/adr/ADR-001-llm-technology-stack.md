# ADR-001: LLM Technology Stack Selection

| Field        | Value                                   |
|--------------|-----------------------------------------|
| **ID**       | ADR-001                                 |
| **Title**    | LLM Technology Stack Selection          |
| **Status**   | Accepted                                |
| **Date**     | 2025-04-01                              |
| **Author**   | AI & LLM Solutions Architect            |
| **Ticket**   | EMI-32                                  |
| **Reviewers**| Engineering Lead, Data Privacy Officer  |

---

## 1. Context

We are building an LLM-powered, AI-first automated market intelligence and competitor analysis platform for the UK Energy industry. The platform will ingest, analyse, and surface intelligence from Ofgem publications, energy company reports, regulatory filings, pricing data, news feeds, and competitor activity signals.

### Key Constraints

- **UK Data Residency**: UK GDPR compliance is mandatory. Prompts, completions, and embedded document vectors may constitute personal or commercially sensitive data — all inference and storage must be contractually bound to UK/EU data centres.
- **Scale**: 50,000–500,000 documents at launch, growing to millions. Embedding and re-indexing costs matter.
- **Latency**: Interactive analyst queries must return in <3 seconds. Batch analysis pipelines must complete within 10 minutes.
- **Accuracy over cost**: This is a B2B commercial product. Hallucination and incorrect intelligence have business/reputational consequences. Accuracy is prioritised over cost reduction.
- **No lock-in**: Each layer must be swappable without a full rewrite. Abstraction layers are mandatory.
- **Responsible AI**: Source citation, confidence grounding, and hallucination mitigation are product requirements, not optional.
- **Fine-tuning path**: Energy domain-specific fine-tuning is a Phase 2 requirement. Selected components must support it.

---

## 2. Decision

We adopt the following technology stack:

| Layer               | Primary Choice                           | Secondary / Fallback                      |
|---------------------|------------------------------------------|-------------------------------------------|
| LLM Provider        | GPT-4o via Azure OpenAI (UK South)       | Claude 3.5 Sonnet via AWS Bedrock (eu-west-2) — long-context only |
| Orchestration       | Haystack 2.x                             | LlamaIndex (if agent model proves insufficient) |
| Vector Database     | Qdrant Cloud (managed) → self-hosted AKS | Weaviate (if Qdrant UK residency unconfirmed) |
| Embedding Model     | OpenAI text-embedding-3-large (Phase 1)  | BGE-M3 self-hosted (Phase 2)              |
| Infrastructure      | Azure OpenAI Service (UK South)          | AWS Bedrock eu-west-2 (secondary LLM only)|
| LLM Gateway         | LiteLLM (self-hosted)                    | —                                         |
| Observability       | Langfuse (self-hosted on AKS)            | Azure Monitor + OpenTelemetry             |

---

## 3. Evaluation

### 3.1 LLM Providers

**Scoring weights:** Domain reasoning 20% · Context window 15% · Cost at scale 10% · Latency 10% · Data privacy/residency 20% · Fine-tuning 10% · Vendor lock-in 5% · Responsible AI 10%

| Criterion (Weight)                  | GPT-4o Azure | Claude 3.5 Sonnet Bedrock | Gemini 1.5 Pro Vertex | Mistral Large Azure | Llama 3 70B self-hosted |
|-------------------------------------|:---:|:---:|:---:|:---:|:---:|
| UK Energy domain reasoning (20%)    |  5  |  5  |  4  |  3  |  3  |
| Context window 100K+ ideal (15%)    |  3  |  4  |  5  |  3  |  3  |
| Cost at scale (10%)                 |  2  |  3  |  3  |  4  |  5  |
| Latency <3s interactive (10%)       |  4  |  4  |  3  |  5  |  3  |
| Data privacy / UK residency (20%)   |  5  |  4  |  3  |  4  |  5  |
| Fine-tuning availability (10%)      |  3  |  3  |  2  |  4  |  5  |
| Vendor lock-in risk (5%) ↑=low      |  2  |  2  |  2  |  3  |  5  |
| Responsible AI features (10%)       |  4  |  5  |  4  |  3  |  2  |
| **Weighted Total**                  | **3.85** | **4.00** | **3.45** | **3.60** | **3.80** |

**Winner: GPT-4o (Azure OpenAI, UK South)**

Claude 3.5 Sonnet scores 4.00 on raw totals, however routing primary inference to AWS Bedrock while running primary infrastructure on Azure creates a cross-cloud data path that complicates UK GDPR residency audit trails and adds latency/egress on every query. GPT-4o leads on the two most operationally critical criteria: UK residency (5/5) and domain reasoning (5/5), with the strongest contractual posture for commercially sensitive data processing.

Claude 3.5 Sonnet is retained as a **secondary model** routed exclusively for documents exceeding 100K tokens, where its 200K context window provides a capability GPT-4o (128K) cannot match.

**Pricing reference (Q1 2025):**
- GPT-4o: $5 / $15 per 1M in/out tokens
- Claude 3.5 Sonnet: $3 / $15 per 1M in/out tokens
- Gemini 1.5 Pro: $3.50 / $10.50 per 1M in/out tokens
- Mistral Large: ~$2 / $6 per 1M in/out tokens
- Llama 3 70B self-hosted: ~$0.10–$0.80 / 1M token equivalent

---

### 3.2 Orchestration Frameworks

**Scoring weights:** RAG pipeline maturity 25% · Multi-agent support 15% · UK energy adaptability 10% · Community & ecosystem 10% · Observability & debugging 15% · Production readiness 15% · Vendor lock-in 5% · Learning curve 5%

| Criterion (Weight)                        | LangChain | LlamaIndex | CrewAI | Haystack 2.x |
|-------------------------------------------|:---:|:---:|:---:|:---:|
| RAG pipeline maturity (25%)               |  4  |  5  |  2  |  4  |
| Multi-agent support (15%)                 |  4  |  3  |  5  |  3  |
| UK energy adaptability (10%)              |  4  |  4  |  2  |  4  |
| Community & ecosystem (10%)               |  5  |  4  |  3  |  3  |
| Observability & debugging (15%)           |  4  |  3  |  2  |  4  |
| Production readiness (15%)                |  3  |  4  |  2  |  4  |
| Vendor lock-in risk (5%) ↑=low            |  4  |  4  |  3  |  5  |
| Learning curve (5%) ↑=easiest             |  2  |  3  |  4  |  3  |
| **Weighted Total**                        | **3.85** | **3.90** | **2.70** | **3.75** |

**Winner: Haystack 2.x**

LlamaIndex scored highest raw (3.90), and the initial proposal was LlamaIndex + LangGraph for agents. However, a dual-framework approach creates an integration surface that becomes the primary maintenance burden over time. Haystack 2.x ≥v2.10 with `AsyncPipeline`, `Agent`, and `ToolInvoker` handles both RAG pipelines and agentic workflows within a single YAML-configurable framework. The 0.15 weighted point cost is justified by reduced architectural complexity.

Haystack ships with first-class OpenTelemetry tracing, is licensed Apache 2.0, and has established enterprise deployments. LlamaIndex remains the designated fallback if Haystack's agent model proves insufficient for Phase 2 multi-agent requirements.

---

### 3.3 Vector Databases

**Scoring weights:** UK data residency 20% · Scalability 20% · Hybrid search 15% · Managed service quality 10% · Cost at scale 10% · Metadata filtering 10% · Production reliability 10% · Operational complexity 5%

| Criterion (Weight)                        | Pinecone | Weaviate | Qdrant | pgvector | ChromaDB |
|-------------------------------------------|:---:|:---:|:---:|:---:|:---:|
| UK data residency (20%)                   |  3  |  4  |  5  |  5  |  2  |
| Scalability — millions of vectors (20%)   |  5  |  4  |  4  |  3  |  2  |
| Hybrid search BM25+semantic (15%)         |  2  |  5  |  4  |  3  |  1  |
| Managed service quality (10%)             |  5  |  4  |  3  |  3  |  1  |
| Cost at scale (10%)                       |  2  |  3  |  4  |  5  |  4  |
| Metadata filtering richness (10%)         |  4  |  5  |  5  |  4  |  3  |
| Production reliability (10%)              |  5  |  4  |  4  |  4  |  2  |
| Operational complexity (5%) ↑=easiest     |  5  |  3  |  3  |  2  |  4  |
| **Weighted Total**                        | **3.75** | **4.10** | **4.15** | **3.75** | **2.15** |

> **ChromaDB is disqualified for production use**: no native hybrid search, single-node architecture, no enterprise managed service.

**Winner: Qdrant**

Qdrant edges Weaviate (4.15 vs 4.10) on the decisive criteria of data residency and cost. Its Rust engine delivers materially lower memory overhead than Weaviate's JVM at millions of vectors. Native sparse+dense hybrid search in a single engine requires no separate BM25 index. Apache 2.0 licence.

**Deployment strategy**: Qdrant Cloud (managed) at launch to reduce operational burden during initial development, migrating to self-hosted on AKS in Phase 2 once Kubernetes operational maturity is confirmed.

> ⚠️ **Pre-launch action required**: Confirm Qdrant Cloud region is locked to UK South (via Azure Marketplace) or West Europe minimum. Document the Data Processing Agreement before any data ingestion.

---

### 3.4 Embedding Models

**Scoring weights:** Semantic quality 30% · Cost per embedding 15% · UK data residency 20% · Multilingual support 10% · Fine-tuning capability 15% · Dimensionality/performance balance 10%

| Criterion (Weight)                             | OpenAI text-embedding-3-large | Cohere embed-v3 | BGE-M3 self-hosted | E5-large-v2 self-hosted | Jina AI |
|------------------------------------------------|:---:|:---:|:---:|:---:|:---:|
| Semantic quality — technical/regulatory (30%)  |  5  |  4  |  4  |  3  |  3  |
| Cost per embedding (15%)                       |  3  |  3  |  5  |  5  |  4  |
| UK data residency (20%)                        |  3  |  3  |  5  |  5  |  3  |
| Multilingual support (10%)                     |  3  |  5  |  5  |  3  |  4  |
| Fine-tuning capability (15%)                   |  2  |  3  |  5  |  5  |  2  |
| Dimensionality / performance balance (10%)     |  4  |  4  |  5  |  3  |  3  |
| **Weighted Total**                             | **3.55** | **3.60** | **4.70** | **4.00** | **3.10** |

**Winner: BGE-M3 (long term) — phased approach**

BGE-M3 is the clear long-term winner (4.70): full data sovereignty, domain fine-tuning capability, dense+sparse+multi-vector support, near-zero per-token cost at scale. However, Day 1 self-hosted GPU inference requires dedicated MLOps resource and operational runbooks not yet in place.

**Phase 1**: `text-embedding-3-large` via Azure OpenAI UK South — zero-ops, 5/5 semantic quality, aligned with Azure primary infrastructure spine. Cost at launch: ~$16 for 500K documents at 500 tokens/chunk average.

**Phase 2 gate**: BGE-M3 self-hosted, conditional on: (a) MLOps resource confirmed, (b) GPU node pool operational, (c) blue-green migration runbook tested end-to-end.

> ⚠️ **Critical**: Phase 1→2 migration requires full re-indexing (incompatible vector spaces: 1536D → 1024D). Raw document text **must** be stored in Azure Blob Storage as canonical source for re-embedding at any time.

---

### 3.5 Infrastructure

**Scoring weights:** UK data residency guarantee 25% · Model selection breadth 15% · Enterprise compliance 20% · Cost management 10% · Enterprise integration 10% · Operational overhead 10% · SLA/reliability 10%

| Criterion (Weight)                        | Azure OpenAI UK South | AWS Bedrock eu-west-2 | GCP Vertex AI europe-west2 | Self-hosted K8s |
|-------------------------------------------|:---:|:---:|:---:|:---:|
| UK data residency guarantee (25%)         |  5  |  4  |  3  |  5  |
| Model selection breadth (15%)             |  4  |  4  |  4  |  5  |
| Enterprise compliance (20%)               |  5  |  4  |  4  |  3  |
| Cost management tooling (10%)             |  4  |  4  |  3  |  3  |
| Enterprise integration (10%)              |  5  |  3  |  3  |  4  |
| Operational overhead (10%) ↑=lowest       |  5  |  5  |  5  |  1  |
| SLA / reliability (10%)                   |  4  |  4  |  4  |  2  |
| **Weighted Total**                        | **4.65** | **4.00** | **3.65** | **3.60** |

**Winner: Azure OpenAI Service (UK South)**

Azure UK South is the decisive winner (4.65), scoring 5/5 on both highest-weighted criteria. Microsoft's contractual UK GDPR Data Boundary covers inference processing (prompts and completions), not just data-at-rest — a critical distinction for generative AI workloads. Compliance pack: ISO 27001/17/18, SOC 2 Type II, Cyber Essentials Plus, G-Cloud listed, NCSC Cloud Security Principles aligned.

> **GCP note**: Google holds Cyber Essentials Plus scoped to UK personnel/office only — not cloud infrastructure. This is a material gap for regulated sector clients.

> **Self-hosted K8s**: Disqualified as primary infrastructure (1/5 operational overhead). Reserved for Phase 2 fine-tuned model serving only.

---

## 4. Recommended Full Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Energy Market Intel Platform              │
├─────────────────────────────────────────────────────────────┤
│  UI Layer          │  Next.js dashboard (services/frontend)  │
├────────────────────┼────────────────────────────────────────┤
│  API Layer         │  FastAPI (services/api)                 │
├────────────────────┼────────────────────────────────────────┤
│  LLM Gateway       │  LiteLLM (self-hosted, AKS)            │
│                    │  Primary: GPT-4o → Azure UK South       │
│                    │  Secondary: Claude 3.5 → Bedrock        │
│                    │  (auto-routed for >100K token docs)     │
├────────────────────┼────────────────────────────────────────┤
│  Orchestration     │  Haystack 2.x                          │
│                    │  RAG pipelines + Agent workflows        │
├────────────────────┼────────────────────────────────────────┤
│  Vector Store      │  Qdrant Cloud → AKS self-hosted (P2)   │
│                    │  Hybrid search: dense + sparse vectors  │
├────────────────────┼────────────────────────────────────────┤
│  Embeddings        │  P1: OpenAI text-embedding-3-large      │
│                    │  P2: BGE-M3 self-hosted (GPU node pool) │
├────────────────────┼────────────────────────────────────────┤
│  Document Store    │  Azure Blob Storage (UK South)         │
│                    │  Canonical source for re-indexing       │
├────────────────────┼────────────────────────────────────────┤
│  Data Pipelines    │  Prefect (services/pipelines)          │
├────────────────────┼────────────────────────────────────────┤
│  Observability     │  Langfuse (LLM tracing, self-hosted)   │
│                    │  OpenTelemetry → Azure Monitor          │
├────────────────────┼────────────────────────────────────────┤
│  Infrastructure    │  Azure (primary) + AWS (secondary)     │
│                    │  AKS for orchestration workloads        │
└─────────────────────────────────────────────────────────────┘
```

### Why these components work together

1. **Azure spine coherence**: Azure OpenAI (LLM) + Azure Blob (document store) + AKS (orchestration) + Azure Monitor (observability) form a single audit perimeter for UK GDPR. Single DPA covers the entire primary data path.
2. **LiteLLM as abstraction layer**: By routing all LLM calls through LiteLLM, the application code is completely decoupled from model providers. Swapping GPT-4o for Mistral or adding Claude is a config change, not a code change.
3. **Haystack's YAML pipeline definition**: Pipelines are serialisable and versionable as config files. This enables A/B testing of retrieval strategies and prompt templates without code deployments.
4. **Qdrant native hybrid search**: Eliminates the need for a separate BM25/Elasticsearch index for keyword search. Energy regulatory documents have many precise term matches (e.g. "RIIO-ED2", "Distribution Use of System", "Supplier of Last Resort") that pure semantic search misses.
5. **Langfuse for LLM observability**: Every prompt, completion, token count, latency, and retrieved chunk is traced. Essential for debugging RAG quality and demonstrating responsible AI practices to enterprise clients.

---

## 5. Anti-Lock-In Architecture Principles

The following principles are **mandatory** for all engineering work on this platform:

### P1: Abstract all LLM calls behind LiteLLM
No service or package may call `openai.ChatCompletion` or `anthropic.messages.create` directly. All LLM calls go through LiteLLM's OpenAI-compatible interface. Model configuration lives in `config/litellm.yaml`.

### P2: Abstract vector store behind a typed interface
All vector store operations go through `packages/vector-store/` adapters that implement a common `VectorStoreProtocol`. Qdrant is one implementation. pgvector is another. Swap without touching business logic.

### P3: Store raw documents as canonical source of truth
Raw ingested documents (PDFs, HTML, JSON) are always stored in Azure Blob Storage before any processing. The vector index is a derived artefact and can always be rebuilt from the document store.

### P4: Version embedding model in collection metadata
Every Qdrant collection name includes the embedding model slug: e.g. `energy_docs_oai3l_v1`, `energy_docs_bgem3_v1`. This enables blue-green migration without data loss.

### P5: Externalise all pipeline configuration
Haystack pipeline YAML files live in `config/pipelines/`. Prompt templates live in `config/prompts/`. No hardcoded prompts or retrieval parameters in application code.

### P6: LLM calls are logged and attributed
Every LLM call carries: `user_id`, `session_id`, `pipeline_id`, `model_used`, `token_counts`. This is required for cost allocation, debugging, and responsible AI audit trails.

---

## 6. Key Risks and Mitigations

| # | Layer | Risk | Mitigation | Owner |
|---|-------|------|------------|-------|
| 1 | LLM | GPT-4o 128K insufficient for very long regulatory docs (RIIO-ED2 full determination ~300K tokens) | Route all >100K token tasks to Claude 3.5 Sonnet via LiteLLM token-count router | Eng Lead |
| 2 | LLM | Azure UK South model availability lag (2–8 weeks behind US East) | Pin model versions; maintain 200+ energy domain Q&A regression test suite | MLOps |
| 3 | LLM | Single LLM provider failure | LiteLLM failover: GPT-4o 429/5xx → Claude retry; both down → graceful degradation with queued response | Eng Lead |
| 4 | Orchestration | Haystack streaming callbacks unvalidated for <3s UX | Validate ≥v2.26 before UI commitment; FastAPI SSE as fallback | Frontend Eng |
| 5 | Vector DB | Qdrant Cloud UK residency unconfirmed | Lock to Azure Marketplace UK South or West Europe; document DPA before ingestion | Infra |
| 6 | Vector DB | Sparse vector drift (hybrid search degrades silently) | Ingestion validation: assert dense+sparse both populated; alert on `sparse_coverage_ratio` drop | MLOps |
| 7 | Embeddings | Phase 1→2 re-indexing requires full re-embed (incompatible vector spaces) | Blue-green with versioned collection names; always store raw docs in Blob | MLOps |
| 8 | Infrastructure | Cross-cloud egress cost (Azure→Bedrock for long-context) | Monitor egress; size the Claude routing threshold carefully (>100K, not >50K) | FinOps |
| 9 | All | Hallucination in energy market intelligence outputs | Mandatory source citation in all RAG responses; confidence scoring; human review workflow for high-stakes outputs | Product |

---

## 7. Phase Roadmap

| Phase | Milestone | Stack State |
|-------|-----------|-------------|
| **Phase 1** | MVP: RAG-powered document Q&A | GPT-4o + text-embedding-3-large + Qdrant Cloud + Haystack 2.x |
| **Phase 1.5** | Multi-model routing | + Claude 3.5 for long-context via LiteLLM router |
| **Phase 2** | Agent workflows | Haystack Agent pipelines; competitor monitoring agents |
| **Phase 2** | Embedding migration | BGE-M3 self-hosted; blue-green re-index |
| **Phase 3** | Domain fine-tuning | Mistral or Llama 3 fine-tuned on UK energy corpus; self-hosted on AKS GPU nodes |
| **Phase 3** | Vector DB self-host | Qdrant on AKS; Qdrant Cloud decommissioned |

---

## 8. Consequences

### Positive
- Single-cloud primary data path simplifies UK GDPR audit and DPA scope
- LiteLLM abstraction eliminates vendor lock-in at the most critical layer
- Haystack's YAML pipelines enable non-engineer configuration of retrieval strategies
- Qdrant's native hybrid search avoids a dual-index architecture (vector + keyword)
- Clear Phase 2 migration paths prevent technical debt accumulation

### Negative
- Haystack has a smaller community than LangChain; fewer energy-domain examples exist
- BGE-M3 Phase 2 migration requires a full re-embedding run (mitigated by Blob document store)
- Two cloud providers (Azure primary + AWS secondary) increases operational surface area slightly
- Self-hosted LiteLLM + Langfuse adds AKS deployment complexity in Phase 1

### Neutral
- This ADR supersedes any informal technology choices made before EMI-32
- Revisit at Phase 2 kickoff; BGE-M3 and Haystack agent maturity should be re-evaluated at that point

---

## 9. References

- [Azure OpenAI Service UK South availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)
- [Microsoft UK GDPR Data Boundary](https://www.microsoft.com/en-us/trust-center/privacy/european-data-boundary-eudb)
- [Haystack 2.x documentation](https://docs.haystack.deepset.ai/)
- [Qdrant hybrid search documentation](https://qdrant.tech/documentation/concepts/hybrid-queries/)
- [LiteLLM proxy documentation](https://docs.litellm.ai/docs/proxy/quick_start)
- [BGE-M3 technical report](https://arxiv.org/abs/2309.07597)
- [Langfuse self-hosted deployment](https://langfuse.com/docs/deployment/self-host)
- EMI-32 synthesis evaluation (internal)
