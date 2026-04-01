# ADR-001: Monorepo with uv Workspaces

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-01 |
| **Deciders** | AI & LLM Solutions Architect |
| **Phase** | 1 — Foundation |

## Context

We need to decide whether to use a monorepo (single Git repository for all services and packages) or a multi-repo approach (separate repositories per service/package).

The platform consists of:
- 4 shared packages (`energy-schemas`, `llm-core`, `vector-store`, `observability`)
- 4 services (`api`, `agents`, `pipelines`, `frontend`)

These components share domain models, LLM abstractions, and observability tooling heavily.

## Decision

**Monorepo using uv workspaces.**

## Rationale

### Why monorepo?

1. **Zero schema drift** — `packages/energy-schemas` is the single source of truth for all Pydantic domain models. In a multi-repo setup, schema changes require coordinated releases across multiple repos, leading to version skew and drift.

2. **Single onboarding command** — `make bootstrap` gets any developer running in one step. Multi-repo requires cloning 8 repositories and coordinating local installs.

3. **Atomic cross-cutting changes** — A change to `energy-schemas` that also requires updates to `agents` and `api` can be a single PR with a single review, CI run, and rollback if needed.

4. **Unified observability** — Single Langfuse project, consistent `correlation_id` propagation, and a single `OTEL_SERVICE_NAME` namespace.

5. **Consistent tooling** — One `pyproject.toml`, one `.pre-commit-config.yaml`, one CI pipeline definition. No drift in linting rules or test standards across repos.

### Why uv workspaces?

- **10–100× faster** than Poetry for dependency resolution
- Native workspace support (similar to npm workspaces / Cargo workspaces)
- Single `uv.lock` committed to the repo — reproducible builds
- `uv sync --all-packages` installs everything in one command

### Rejected alternatives

| Option | Rejected Because |
|--------|-----------------|
| **Multi-repo** | Schema drift between packages/services; complex local dev setup; 8 PRs for cross-cutting changes |
| **Poetry** | 10–100× slower than uv; workspace support is immature |
| **Nx** | Immature Python support; adds significant tooling complexity |
| **Pants** | Excellent monorepo tool but steep learning curve; uv workspaces sufficient for our scale |

## Consequences

- **Good:** Single CI pipeline, single `.env.example`, atomic changes
- **Good:** Import linter (`import-linter`) enforces `services → packages` dependency direction
- **Good:** `CODEOWNERS` for `packages/` requires `@ai-lead` review — protects shared foundations
- **Neutral:** Repository will grow large over time — mitigated by `.gitignore` and sparse checkout if needed
- **Risk:** All services share the same `uv.lock` — a dependency conflict blocks all services. Mitigation: each service can override deps in its own `pyproject.toml`
