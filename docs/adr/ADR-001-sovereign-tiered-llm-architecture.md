# ADR-001: Sovereign-Primary Tiered LLM Architecture

**Status:** Accepted  
**Date:** 2026-04-01  
**Deciders:** AI & LLM Solutions Architect  
**Story:** EMI-32  
**Tags:** llm, architecture, data-residency, uk-gdpr, security

---

## Context

The Energy Market Intelligence platform processes UK energy market data, competitor intelligence, and regulatory documents (Ofgem, BEIS, REMIT). This data is commercially sensitive and potentially subject to UK GDPR as it may include personally identifiable information embedded in business documents.

Three hard regulatory constraints shape this decision:

1. **US CLOUD Act** — All US-headquartered cloud providers (Microsoft, Google, Amazon) are legally compelled to produce data stored anywhere on their infrastructure upon US government order, regardless of the "UK region" label. UK region ≠ data sovereignty.
2. **UK GDPR / DPA 2018 + Ofgem OFG1164 (May 2025)** — Embedding vectors derived from personal or commercially sensitive documents constitute pseudonymised personal data (ICO + EDPB Opinion 28/2024). Board-level AI accountability is now mandated.
3. **REMIT** — AI outputs used in commercial energy decisions carry regulatory liability; the licensee retains full liability for third-party AI outputs.

The naive approach — route all queries to a managed frontier API (OpenAI, Anthropic, Google) — fails all three constraints for the majority of platform traffic.

---

## Decision

Adopt a **three-tier sovereign-primary routing architecture**:

| Tier | Provider | Traffic Share | Use Case |
|------|----------|:---:|----------|
| Tier 1 — Sovereign Primary | Llama 3.1 70B (fine-tuned, self-hosted on OVHcloud UK / CUDO Compute UK) | ~75% | All PII, REMIT-sensitive, commercially sensitive queries |
| Tier 2 — EU Sovereign Fallback | Mistral Large 2 (La Plateforme EU direct — NOT via Azure) | ~15% | Non-sensitive overflow, complex reasoning burst |
| Tier 3 — Non-sensitive only | GPT-4o (Azure OpenAI UK South) | ~10% | Public data summarisation, non-PII only |

**Routing gateway:** LiteLLM + RouteLLM classifier. All routing decisions are logged with audit trail. Sensitivity classification runs as a hard pre-routing gate via Microsoft Presidio + energy-specific PII scanner. Queries classified as PII, REMIT, or commercially sensitive are **force-routed to Tier 1** — the classifier confidence threshold does not apply to this class.

**Sovereign failover:** OVHcloud primary → CUDO UK secondary. If both are unavailable, PII/REMIT processing **halts** — it does NOT fall through to Tier 3.

---

## Consequences

### Positive
- Eliminates CLOUD Act exposure for ~75% of platform traffic
- ~85–90% cost reduction vs all-API baseline ($6,500–9,000/mo vs $45,000–90,000/mo)
- Fine-tuning on proprietary energy corpus creates competitive moat
- Full auditability and explainability of routing decisions
- Satisfies OFG1164 board accountability requirement

### Negative / Trade-offs
- Operational complexity: requires MLOps capability to manage self-hosted GPU infrastructure
- Cold-start latency on Llama 3.1 70B (~200–400ms inference vs ~80ms for managed API)
- GPU infrastructure procurement lead time (2–4 weeks for OVHcloud/CUDO provisioning)
- Fine-tuning pipeline required before Tier 1 reaches production quality
- Board-level CLOUD Act risk acceptance required for Tier 3 (documented)

### Risks
| Risk | Severity | Mitigation |
|------|:---:|---------|
| PII misrouting to non-sovereign tier | 🔴 Critical | Hard pre-routing gate; REMIT queries force-routed; RouteLLM confidence <0.85 falls back to Tier 1 |
| Sovereign infrastructure single point of failure | 🔴 Critical | Dual sovereign providers; platform halts PII processing if both fail |
| LLM hallucination on regulatory content | 🔴 Critical | Automated evals (BERTScore); human review at commercial decision points (OFG1164 req.) |
| CLOUD Act on Tier 2/3 | 🟠 High | Tier 2/3 restricted to non-PII/non-REMIT/non-commercially-sensitive only; board risk acceptance |

---

## Alternatives Considered

| Option | Rejected Reason |
|--------|----------------|
| All-API (OpenAI/Anthropic) | CLOUD Act exposure on 100% of traffic; $45–90K/mo; no fine-tuning for Anthropic |
| Claude 3.5 Sonnet (Anthropic) | No fine-tuning; US-only routing; no UK/EU data centre — **hard reject** |
| AWS Bedrock (eu-west-2) | Fine-tuning routes to us-east-1 regardless of inference region — architecturally incompatible with UK data residency for fine-tuning workloads — **hard reject** |
| Azure OpenAI only | CLOUD Act; insufficient for sensitive data without sovereignty wrapper |

---

## Production-Blocking Pre-conditions

- [ ] OI-1: Board-level AI accountability officer appointed (OFG1164)
- [ ] OI-3: Board-level CLOUD Act risk acceptance for Tier-2/3 documented
- [ ] OI-4: REMIT compliance review of LLM output governance
- [ ] OI-5: NIS supply chain risk assessment: OVHcloud + CUDO
- [ ] OI-6: PII/sensitivity pre-routing classifier built and tested
- [ ] OI-7: Sovereign failover tested (OVHcloud → CUDO)
- [ ] OI-8: Audit logging schema reviewed by DPO; tamper-evident store operational
