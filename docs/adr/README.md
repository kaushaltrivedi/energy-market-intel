# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the Energy Market Intel platform.

ADRs document significant technical decisions, the context in which they were made, the options considered, and the rationale for the chosen approach.

## Format

Each ADR follows the format defined in [Michael Nygard's ADR template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-llm-technology-stack.md) | LLM Technology Stack Selection | Accepted | 2025-04-01 |

## Status values

- **Proposed** — Under discussion, not yet decided
- **Accepted** — Decision made and in effect
- **Deprecated** — Was accepted, no longer applies
- **Superseded** — Replaced by a newer ADR (link to superseding ADR)

## Creating a new ADR

1. Copy `ADR-000-template.md` to `ADR-NNN-short-title.md`
2. Fill in all sections
3. Open a PR with label `adr`
4. Requires approval from Engineering Lead + one domain expert
5. Update this index once merged
