# ADR-002: LlamaIndex as Primary Orchestration Framework

**Status:** Accepted  
**Date:** 2026-04-01  
**Deciders:** AI & LLM Solutions Architect  
**Story:** EMI-32  
**Tags:** orchestration, rag, langchain, security

---

## Context

The platform requires an LLM orchestration framework to manage RAG pipelines, multi-hop document retrieval, agentic workflows, and citation chains for REMIT compliance. Four frameworks were evaluated: LangChain, LlamaIndex, CrewAI, and Haystack.

**Critical security finding:** LangChain CVE-2025-68664 (CVSS 9.3) — credential leakage via prompt injection in RAG pipelines. Additionally, LangSmith's default tracing configuration transmits prompt content (including document text) to US servers, directly violating UK GDPR data residency requirements for this platform.

---

## Decision

**Primary orchestration framework: LlamaIndex**  
**Supplementary agentic layer: CrewAI** (for multi-agent workflows only)  
**LangChain: HARD REJECT** — do not use until independently audited post-patch.

Rationale for LlamaIndex:
- Purpose-built for RAG — superior retrieval pipeline primitives vs LangChain's general-purpose abstraction
- Native pgvector integration aligns with ADR-003
- Multi-hop query decomposition and citation chain generation are first-class features — directly enables REMIT audit trail requirements
- No default telemetry to external servers (unlike LangSmith)
- Active development with strong enterprise adoption

---

## Consequences

### Positive
- Best-in-class RAG retrieval quality
- Citation chains satisfy OFG1164 audit trail requirement
- No credential leakage risk from CVE-2025-68664
- Native pgvector support simplifies stack

### Negative / Trade-offs
- Smaller community than LangChain (though growing rapidly)
- Fewer pre-built integrations — some custom connectors required for energy data sources
- Team may need upskilling if familiar only with LangChain

---

## Alternatives Considered

| Framework | Score /30 | Decision |
|-----------|:---:|---------|
| LlamaIndex | 21 | ✅ **Selected** |
| Haystack (deepset) | 20 | Fallback — German HQ, strong EU AI Act compliance posture |
| CrewAI | 15 | Supplementary agentic layer only |
| LangChain | 13 | 🔴 **HARD REJECT** — CVE-2025-68664 (CVSS 9.3), LangSmith UK GDPR violation |

---

## Re-evaluation Trigger

LangChain may be re-evaluated if: independent security audit post-patch confirms CVE remediation AND LangSmith telemetry can be fully disabled/self-hosted with verified no egress.
