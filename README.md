# ⚡ Energy Market Intel

> LLM-powered automated market intelligence and competitor analysis platform for the UK Energy industry.

[![CI](https://github.com/kaushaltrivedi/energy-market-intel/actions/workflows/ci.yml/badge.svg)](https://github.com/kaushaltrivedi/energy-market-intel/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

Energy Market Intel is an AI-first platform that automates intelligence gathering, analysis, and reporting across the UK energy sector. It combines LLM orchestration, real-time data pipelines, and vector search to deliver actionable insights on market dynamics, regulatory changes, and competitor movements.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Energy Market Intel                       │
├──────────────┬──────────────────────┬───────────────────────────┤
│  Data Layer  │  Intelligence Layer  │      Delivery Layer        │
│              │                      │                           │
│  • Elexon    │  • LangGraph Agents  │  • FastAPI REST/WS        │
│  • Ofgem     │  • LLM Core (GPT-4o  │  • Next.js Dashboard      │
│  • News APIs │    → Claude → Gemini)│  • Scheduled Reports      │
│  • Companies │  • Vector Search     │                           │
│    House     │  • RAG Pipelines     │                           │
└──────────────┴──────────────────────┴───────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker + Docker Compose

### Setup

```bash
# Clone the repo
git clone https://github.com/kaushaltrivedi/energy-market-intel.git
cd energy-market-intel

# Bootstrap the project (installs all deps, sets up pre-commit hooks)
make bootstrap

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start local services (Postgres, Weaviate, Redis)
docker-compose up -d

# Run the test suite
make test
```

## Repository Structure

```
energy-market-intel/
├── packages/               # Shared internal libraries (uv workspaces)
│   ├── energy-schemas/     # Pydantic data models for energy domain
│   ├── llm-core/           # LLM client, failover, budget management
│   ├── vector-store/       # Abstract vector DB adapters
│   └── observability/      # Structured logging, tracing, OTEL
├── services/               # Deployable services
│   ├── api/                # FastAPI application
│   ├── agents/             # LangGraph agent graphs
│   ├── pipelines/          # Prefect data ingestion pipelines
│   └── frontend/           # Next.js dashboard
├── config/                 # Non-secret YAML configuration
├── infrastructure/         # Terraform + Docker Compose
├── tests/                  # Test suites (unit / integration / e2e / llm_eval)
└── docs/                   # Architecture docs, ADRs, runbooks
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Code Standards](CODE_STANDARDS.md)
- [ADR Index](docs/architecture/ADRs/)

## Branch Strategy

| Branch | Purpose | Merges Into |
|--------|---------|------------|
| `main` | Production-ready code | — |
| `develop` | Integration branch | `main` (via release) |
| `feature/TICKET-description` | Feature development | `develop` |
| `release/x.y.z` | Release preparation | `main` + `develop` |
| `hotfix/TICKET-description` | Production fixes | `main` + `develop` |

## Licence

MIT — see [LICENSE](LICENSE).
