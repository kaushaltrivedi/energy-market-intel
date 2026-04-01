## Summary

> Describe what this PR does and why. Link to the ticket if applicable.
>
> Closes #TICKET

## Type of Change

- [ ] `feat` — New feature
- [ ] `fix` — Bug fix
- [ ] `refactor` — Code change (no feat/fix)
- [ ] `docs` — Documentation only
- [ ] `test` — Tests only
- [ ] `chore` — Build/tooling
- [ ] `security` — Security fix
- [ ] `ci` — CI/CD change

## Changes Made

> Bullet-point list of the key changes. Be specific.

-
-
-

## Testing

> Describe how this was tested. Include test commands run.

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] `make test` passes locally
- [ ] Coverage meets or exceeds threshold (`make test-cov`)

```bash
# Commands run to test this:
make test
```

## Engineering Checklist

### Code Quality
- [ ] Code follows [CODE_STANDARDS.md](../CODE_STANDARDS.md)
- [ ] PEP 8 compliant — `make lint` passes with no errors
- [ ] Black formatted (line length 100)
- [ ] No `print()` statements — using `structlog` logging
- [ ] Type annotations on all new public functions/methods
- [ ] Google-style docstrings on all new public APIs

### Testing
- [ ] Test coverage ≥ 80% overall (≥ 90% for `packages/`, ≥ 95% for `packages/energy-schemas`)
- [ ] No live LLM API calls in tests (`LLM_MOCK_MODE=true` in all test scenarios)
- [ ] VCR cassettes sanitised (no API keys, no PII, no MPAN/MPRN)
- [ ] New test functions follow naming convention `test_<what>_<when>_<expected>()`

### Security
- [ ] No secrets, API keys, tokens, or credentials committed
- [ ] No `os.environ` calls — using `pydantic Settings`
- [ ] No new PII logged
- [ ] `make security` passes (bandit + pip-audit + gitleaks)
- [ ] New API endpoints have authentication/authorisation

### LLM & AI (if applicable)
- [ ] All LLM calls respect `AGENT_TOKEN_BUDGET`
- [ ] New prompts added to `packages/llm-core/llm_core/prompts/` as `.j2` files
- [ ] `FEATURE_STRICT_DATA_RESIDENCY` compliance verified
- [ ] No hardcoded model names — using config YAML values

### Documentation
- [ ] Public APIs documented with docstrings
- [ ] `README.md` updated if relevant
- [ ] `docs/ARCHITECTURE.md` updated if component changes
- [ ] ADR created for significant architectural decisions
- [ ] `.env.example` updated if new env vars introduced

### Dependencies (if applicable)
- [ ] New dependencies justified (build-vs-buy trade-off considered)
- [ ] `uv.lock` updated and committed
- [ ] No known vulnerabilities (`pip-audit` clean)
- [ ] Licence compatible with MIT

## Deployment Notes

> Any special steps needed to deploy this? Database migrations, config changes, feature flags?

_None required / [describe steps]_

## Screenshots (if applicable)

> Add screenshots for UI changes.

---

**Reviewer notes:** Please pay particular attention to [highlight any area needing close review].
