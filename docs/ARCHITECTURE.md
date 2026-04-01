# Architecture Overview

> **Status:** Living document — updated as the system evolves.
> **Last updated:** Phase 1 (Foundation)
> **Owner:** AI & LLM Solutions Architect

## System Purpose

Energy Market Intel is an LLM-powered platform that automates intelligence gathering, analysis, and reporting for the UK energy sector. It ingests real-time and historical data from Elexon, Ofgem, Companies House, and news sources, then applies AI agents to produce structured intelligence reports on market dynamics, regulatory changes, and competitor movements.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Energy Market Intel                              │
│                                                                         │
│  ┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐  │
│  │   Data Layer     │    │ Intelligence Layer│    │  Delivery Layer   │  │
│  │                 │    │                  │    │                   │  │
│  │ Prefect Pipelines│───►│ LangGraph Agents │───►│ FastAPI REST/WS   │  │
│  │                 │    │                  │    │                   │  │
│  │ • Elexon BMRS   │    │ • MarketAnalyst  │    │ • Next.js UI      │  │
│  │ • Ofgem Portal  │    │ • RegWatch       │    │ • Scheduled Jobs  │  │
│  │ • Companies     │    │ • ReportWriter   │    │ • Webhooks        │  │
│  │   House         │    │ • DataFetcher    │    │                   │  │
│  │ • News APIs     │    │                  │    │                   │  │
│  └────────┬────────┘    └────────┬─────────┘    └───────────────────┘  │
│           │                      │                                      │
│           ▼                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Infrastructure Layer                         │   │
│  │                                                                  │   │
│  │  PostgreSQL (checkpoints)  │  Weaviate/Pinecone (vectors)        │   │
│  │  Redis (cache/pub-sub)     │  AWS S3 (report storage)           │   │
│  │  Langfuse (LLM tracing)    │  OTEL (distributed tracing)        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Inventory

| Component | Technology | Purpose |
|-----------|-----------|---------|
| `packages/energy-schemas` | Python + Pydantic | Shared domain models |
| `packages/llm-core` | litellm + LangGraph | LLM routing, failover, budget |
| `packages/vector-store` | Pinecone / Weaviate | Vector DB abstraction |
| `packages/observability` | structlog + OTEL + Langfuse | Logging, tracing, cost |
| `services/api` | FastAPI | REST + WebSocket API |
| `services/agents` | LangGraph | AI agent orchestration |
| `services/pipelines` | Prefect | Data ingestion pipelines |
| `services/frontend` | Next.js 14 | Dashboard UI |

## LLM Stack

### Provider Hierarchy (UK GDPR compliant)

```
1. Azure OpenAI (uksouth) — PRIMARY
   └── GPT-4o, text-embedding-3-large
       └── Data Zone Standard (UK data residency)

2. Anthropic Claude — FALLBACK
   └── claude-3-5-sonnet-20241022
       └── inference_geo: eu header required

3. Vertex AI (europe-west2) — SECONDARY FALLBACK
   └── gemini-1.5-pro
       └── London region
```

⚠️ **Gemini direct API and OpenAI direct API are NOT permitted** for data containing personal or commercially sensitive information — US infrastructure only.

### Orchestration

**LangGraph** (not CrewAI or LangChain LCEL) for agent orchestration. Rationale in [ADR-003](architecture/ADRs/ADR-003-agent-orchestration.md).

Key reasons:
- Postgres checkpointer — agent state survives restarts
- Conditional edges — market branching logic expressed as graph structure
- Per-node retry — granular failure recovery

## Data Flow

```
External APIs
    │
    ▼
Prefect Pipelines (ingest + normalise)
    │
    ├──► PostgreSQL (structured facts + agent checkpoints)
    │
    └──► Vector Store (embedded documents for RAG)
              │
              ▼
         LangGraph Agents
              │
              ├── Tools: Elexon, Ofgem, Companies House, Vector Search
              │
              └──► Intelligence Reports ──► FastAPI ──► Frontend / Webhooks
```

## Security Architecture

- **Authentication:** JWT (FastAPI) + API keys for service-to-service
- **Secrets:** `.env` locally; AWS Secrets Manager in staging/production
- **Data residency:** All LLM calls gated by `FEATURE_STRICT_DATA_RESIDENCY`
- **PII:** Presidio scrubbing on all LLM inputs when `FEATURE_PII_SCRUBBING=true`
- **Audit:** All agent runs logged with `correlation_id` (W3C trace ID)

## Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](architecture/ADRs/ADR-001-monorepo.md) | Monorepo with uv Workspaces | Accepted |
| [ADR-002](architecture/ADRs/ADR-002-vector-database.md) | Vector Database Selection | Draft |
| [ADR-003](architecture/ADRs/ADR-003-agent-orchestration.md) | Agent Orchestration Framework | Draft |
| [ADR-004](architecture/ADRs/ADR-004-llm-providers.md) | LLM Provider Selection & Failover | Draft |

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation: repo setup, engineering standards, tech evaluation | 🟡 In Progress |
| 2 | Architecture design: detailed system design, ADRs | ⏳ Pending |
| 3 | LLM pipeline: core agent graphs, data ingestion | ⏳ Pending |
| 4 | Intelligence features: market analysis, competitor tracking | ⏳ Pending |
| 5 | Production: hardening, monitoring, deployment | ⏳ Pending |
