# Architecture Decision Records — Index

This directory contains Architecture Decision Records (ADRs) for the Energy Market Intelligence platform.

## ADR Format

Each ADR follows the format:
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** Why this decision was needed
- **Decision:** What was decided
- **Consequences:** Trade-offs, risks, and impacts

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-sovereign-tiered-llm-architecture.md) | Sovereign-Primary Tiered LLM Architecture | Accepted | 2026-04-01 |
| [ADR-002](ADR-002-orchestration-framework-llamaindex.md) | LlamaIndex as Primary Orchestration Framework | Accepted | 2026-04-01 |
| [ADR-003](ADR-003-pgvector-primary-vector-store.md) | pgvector as Primary Vector Store | Accepted | 2026-04-01 |
| [ADR-004](ADR-004-bge-m3-fine-tuned-embeddings.md) | BGE-M3 Fine-tuned Embeddings as Primary Embedding Model | Accepted | 2026-04-01 |

## Stack Summary

| Layer | Primary | Fallback | Hard Rejects |
|-------|---------|----------|--------------|
| LLM | Llama 3.1 70B (self-hosted, fine-tuned) | Mistral Large 2 EU → GPT-4o Azure | Claude 3.5 Sonnet, AWS Bedrock |
| Orchestration | LlamaIndex | Haystack | **LangChain (CVE-9.3)** |
| Vector DB | pgvector | Qdrant self-hosted | **Pinecone (US-only)** |
| Embeddings | BGE-M3 (fine-tuned, self-hosted) | E5-large | OpenAI embeddings, Cohere |
| Infrastructure | OVHcloud / CUDO UK (sovereign) | Azure UK South (Tier-3) | **AWS Bedrock** |
