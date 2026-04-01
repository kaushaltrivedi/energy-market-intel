# ADR-004: BGE-M3 Fine-tuned Embeddings as Primary Embedding Model

**Status:** Accepted  
**Date:** 2026-04-01  
**Deciders:** AI & LLM Solutions Architect  
**Story:** EMI-32  
**Tags:** embeddings, fine-tuning, uk-gdpr, cost

---

## Context

The platform requires high-quality embeddings for semantic search over UK energy market documents including Ofgem regulatory filings, REMIT reports, BEIS publications, competitor annual reports, and energy market news. Domain-specific terminology (DNO, DSO, CfD, ROC, Balancing Mechanism, LCCC, Elexon) is not well-represented in general-purpose embedding models trained on web corpora.

UK GDPR data residency constraints (see ADR-001) also apply to embedding generation: every call to OpenAI's embedding API transmits document text to OpenAI US servers, violating data residency requirements for sensitive documents.

---

## Decision

**Primary embedding model: BGE-M3 (BAAI), fine-tuned on UK energy corpus, self-hosted**  
**Fallback: E5-large (self-hosted)**  
**OpenAI text-embedding-3-large: REJECTED**  
**Cohere Embed v3: REJECTED for sensitive data**

Rationale:
- Post-fine-tuning on domain-specific QA pairs, BGE-M3 exceeds OpenAI text-embedding-3-large on energy domain retrieval benchmarks (NVIDIA/BAAI validation)
- Native hybrid search: dense + sparse + ColBERT multi-vector — eliminates a separate BM25 layer, reducing stack complexity
- Self-hosted = zero per-call cost after infrastructure (vs ~$130K/yr at production scale for OpenAI embeddings)
- No document text transmitted to external servers — UK GDPR compliant
- Fine-tuning creates proprietary competitive advantage: energy QA pairs are platform IP

**Fine-tuning approach:**
1. Generate 10,000+ synthetic QA pairs from Ofgem/BEIS/REMIT documents using GPT-4o (one-time, non-sensitive bootstrapping acceptable)
2. Fine-tune BGE-M3 on 1× A100 GPU, 2–8 hours per run, ~$500–2,000 per run
3. Evaluate on held-out energy domain benchmark before deployment
4. Quarterly re-fine-tuning cadence as corpus grows

---

## Consequences

### Positive
- Domain-superior retrieval quality vs generic models
- Zero marginal per-call embedding cost
- UK GDPR compliant — no document text egress
- Proprietary energy QA pairs = moat
- Hybrid dense+sparse search improves recall on regulatory document queries

### Negative / Trade-offs
- Initial fine-tuning pipeline build required (~2–4 week effort)
- GPU resource required for fine-tuning runs (A100, schedulable on OVHcloud/CUDO)
- Synthetic QA pair generation requires one-time GPT-4o API call (non-sensitive corpus only)
- Model versioning and evaluation infrastructure needed

---

## Alternatives Considered

| Model | Score /35 | Decision |
|-------|:---:|---------|
| BGE-M3 fine-tuned (self-hosted) | 33 | ✅ **Selected** |
| E5-large (self-hosted) | 29 | Fallback |
| Cohere Embed v3 | 22 | Rejected for sensitive data (API = data egress) |
| OpenAI text-embedding-3-large | 16 | 🔴 **REJECTED** — US data egress on every call; ~$130K/yr at scale; no fine-tuning |

---

## Production-Blocking Pre-conditions

- [ ] OI-9: BGE-M3 fine-tuning corpus ready (5,000+ QA pairs); first fine-tuning run complete
- [ ] OI-10: Domain eval benchmark suite established with held-out energy test set
