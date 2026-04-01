# Contributing to Energy Market Intel

Thank you for contributing. Please read this guide before submitting any work.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branch Strategy](#branch-strategy)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Security Guidelines](#security-guidelines)

## Code of Conduct

Be professional, respectful, and constructive. Harassment of any kind will not be tolerated.

## Getting Started

```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/energy-market-intel.git
cd energy-market-intel

# Bootstrap the project (installs deps + pre-commit hooks)
make bootstrap

# Configure your environment
cp .env.example .env
# Fill in .env — never commit this file
```

## Branch Strategy

We follow a **GitFlow-inspired** strategy with Conventional Commits.

| Branch Pattern | Purpose | Base Branch | Merge Into |
|---------------|---------|-------------|------------|
| `main` | Production code only | — | — |
| `develop` | Integration branch | `main` | `main` (via release) |
| `feature/TICKET-short-description` | New features | `develop` | `develop` |
| `release/x.y.z` | Release prep + version bumps | `develop` | `main` + `develop` |
| `hotfix/TICKET-short-description` | Production bug fixes | `main` | `main` + `develop` |

### Rules

- **Never** commit directly to `main` or `develop`
- `feature/*` branches are squash-merged into `develop`
- `release/*` and `hotfix/*` branches use merge commits
- Delete your branch immediately after merge
- Branch names must be lowercase, hyphenated: `feature/EMI-42-elexon-ingest`

## Commit Messages

We use **Conventional Commits** (enforced by commitlint via pre-commit hook).

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change, not feat/fix |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Build process, tooling |
| `ci` | CI/CD changes |
| `security` | Security fix |

### Examples

```
feat(agents): add Elexon BMRS market data ingestion tool
fix(llm-core): handle circuit breaker race condition on provider failover
docs(adr): add ADR-002 vector database selection
security(api): rotate JWT signing key rotation endpoint
```

## Pull Request Process

1. **Create a PR** targeting `develop` (or `main` for hotfixes)
2. **Fill in the PR template** completely — incomplete PRs will not be reviewed
3. **Ensure CI passes** — all checks must be green
4. **Request review** — minimum 1 approval required (2 for `packages/` changes)
5. **Address feedback** within 48 hours
6. **Squash merge** when approved (maintainer responsibility)

### PR Title Format

Must follow Conventional Commits: `feat(scope): description`

### What Makes a Good PR

- Focused: one logical change per PR
- Small: < 400 lines changed where possible
- Tested: new code has tests, existing tests pass
- Documented: public APIs have docstrings
- Secure: no credentials, no new `os.environ` calls

## Code Standards

See [CODE_STANDARDS.md](CODE_STANDARDS.md) for the full style guide.

Quick checklist:
- [ ] PEP 8 compliant (enforced by Ruff)
- [ ] Black formatted (line length 100)
- [ ] Google-style docstrings on all public functions/classes
- [ ] Type annotations on all function signatures
- [ ] No `print()` — use `structlog` logging
- [ ] No `os.environ` — use `pydantic Settings`
- [ ] No hardcoded credentials or API keys

## Testing Requirements

- **Minimum coverage:** 80% overall; 90% for `packages/`; 95% for `packages/energy-schemas`
- Write tests in `tests/unit/` for isolated logic
- Write tests in `tests/integration/` for service interactions (use VCR cassettes for HTTP)
- **Never** make live LLM API calls in tests — use `LLM_MOCK_MODE=true`
- Test file names: `test_<module_name>.py`
- Test function names: `test_<what>_<when>_<expected_result>()`

```bash
# Run tests before pushing
make test

# Check coverage
make test-cov
```

## Security Guidelines

- **NEVER** commit secrets, API keys, passwords, or tokens
- **NEVER** call `os.environ["SECRET"]` directly — use `pydantic Settings`
- `.env` is gitignored — use `.env.example` as the template
- Run `gitleaks` before pushing: `make security`
- If you accidentally commit a secret: rotate it immediately, then clean git history
- All LLM calls must respect `FEATURE_STRICT_DATA_RESIDENCY=true` in production
- PII must never be logged — use structlog `redact` filters

## Questions?

Open a GitHub Discussion or ping the team in the project channel.
