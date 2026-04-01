# ADR-003: pgvector as Primary Vector Store

**Status:** Accepted  
**Date:** 2026-04-01  
**Deciders:** AI & LLM Solutions Architect  
**Story:** EMI-32  
**Tags:** vector-database, uk-gdpr, data-residency, pgvector

---

## Context

The platform requires a vector store for embedding-based similarity search across energy market documents, competitor data, and regulatory filings. UK GDPR Article 17 (right to erasure) is a critical constraint: embedding vectors derived from documents containing personal data are pseudonymised personal data and must be deletable atomically when the source document is deleted.

**Key GDPR constraint:** Most managed vector databases (notably Pinecone) store data in US infrastructure only and have no self-hosted option — they cannot lawfully store UK GDPR-regulated embedding vectors.

---

## Decision

**Primary vector store: pgvector (PostgreSQL extension)**  
**Overflow store (>10M vectors): Qdrant (self-hosted)**  
**Migration trigger: 8M vectors** (20% headroom before 10M threshold)  
**Pinecone: HARD REJECT**

Rationale for pgvector:
- Only evaluated store satisfying UK GDPR Article 17 atomically: `DELETE CASCADE` removes source document and ALL derived embedding vectors in a single ACID transaction — no orphaned vectors possible
- Runs within existing PostgreSQL infrastructure — no new operational dependency
- Self-hosted = full data residency control
- Sufficient performance for <10M vectors (HNSW index, ~5–10ms p99 at this scale)
- LlamaIndex native integration (ADR-002 alignment)

Rationale for Qdrant as overflow:
- Purpose-built for high-volume vector search
- Self-hosted option available — maintains data residency
- Rust implementation: excellent performance and memory efficiency
- Migration path from pgvector is straightforward

---

## Consequences

### Positive
- UK GDPR Art. 17 compliant — atomic deletion with ACID guarantees
- Zero additional infrastructure at launch (uses existing PostgreSQL)
- Self-hosted maintains sovereignty (ADR-001 alignment)
- Cost: ~$50–100/mo additional PostgreSQL resource vs $700+/mo for Pinecone

### Negative / Trade-offs
- pgvector performance degrades at >10M vectors — requires migration planning
- HNSW index rebuild required after bulk inserts (minor operational overhead)
- DBA ownership required for schema management and index tuning

---

## Alternatives Considered

| Store | Score /30 | Decision |
|-------|:---:|---------|
| pgvector | 22 | ✅ **Selected (primary)** |
| Qdrant (self-hosted) | 21 | ✅ **Selected (overflow >10M)** |
| Weaviate | 18 | Available if Qdrant insufficient |
| ChromaDB | 18 | Dev/test only |
| Pinecone | 12 | 🔴 **HARD REJECT** — US-only infrastructure, no self-hosted, cannot lawfully store UK GDPR-regulated embedding vectors |

---

## Production-Blocking Pre-conditions

- [ ] OI-2: DPIA completed for vector store and embedding pipeline
- [ ] OI-8: DPO review of deletion cascade schema and audit logging
