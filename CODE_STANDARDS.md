# Code Standards

Engineering standards for the Energy Market Intel platform.

## Table of Contents

- [Python Version](#python-version)
- [Code Formatting](#code-formatting)
- [Type Annotations](#type-annotations)
- [Docstrings](#docstrings)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Configuration & Secrets](#configuration--secrets)
- [Testing](#testing)
- [LLM-Specific Standards](#llm-specific-standards)

---

## Python Version

**Target: Python 3.11+**

Use modern Python idioms:
- `match` statements over long `if/elif` chains
- `tomllib` for TOML parsing (stdlib in 3.11)
- `ExceptionGroup` for multi-error handling
- `typing.Self` for fluent builder patterns

---

## Code Formatting

### Black

Line length: **100 characters**. Black is non-negotiable — no manual formatting debates.

```bash
uv run black .
```

### Ruff

Ruff handles linting + import sorting. Key rule sets enabled:

| Rule Set | Purpose |
|----------|---------|
| `E`, `W` | pycodestyle |
| `F` | pyflakes |
| `I` | isort (import sorting) |
| `B` | flake8-bugbear |
| `C4` | flake8-comprehensions |
| `UP` | pyupgrade (modern syntax) |
| `S` | bandit security rules |
| `ANN` | type annotation enforcement |
| `D` | pydocstyle (Google convention) |
| `N` | naming conventions |
| `RUF` | Ruff-specific rules |

```bash
uv run ruff check .        # Check
uv run ruff check --fix .  # Auto-fix safe issues
```

---

## Type Annotations

**All public functions and methods must have full type annotations.** No bare `Any` without justification.

```python
# ✅ Good
def fetch_settlement_periods(
    date: datetime.date,
    settlement_period: int,
    *,
    timeout: float = 30.0,
) -> list[SettlementPeriod]:
    ...

# ❌ Bad
def fetch_data(date, period, timeout=30):
    ...
```

Use `from __future__ import annotations` at the top of every file for forward references.

Pydantic models are preferred over TypedDicts for structured data.

---

## Docstrings

**Google-style docstrings** on all public classes, functions, and methods.

```python
def analyse_competitor_position(
    competitor_id: str,
    analysis_date: datetime.date,
    *,
    include_regulatory: bool = True,
) -> CompetitorAnalysis:
    """Analyse a competitor's current market position.

    Fetches recent market data, regulatory filings, and news to produce
    a structured competitive analysis using the MarketAnalyst LangGraph agent.

    Args:
        competitor_id: Companies House registration number of the competitor.
        analysis_date: Date for which to produce the analysis.
        include_regulatory: Whether to include Ofgem regulatory filings.
            Defaults to True.

    Returns:
        CompetitorAnalysis containing market share estimates, pricing strategy,
        and recent strategic moves.

    Raises:
        CompaniesHouseError: If the competitor cannot be found in Companies House.
        LLMBudgetExceededError: If the analysis exceeds the configured token budget.
        DataResidencyError: If FEATURE_STRICT_DATA_RESIDENCY is set and a
            non-compliant LLM provider would be used.

    Example:
        >>> analysis = analyse_competitor_position(
        ...     competitor_id="12345678",
        ...     analysis_date=date(2025, 1, 15),
        ... )
        >>> print(analysis.market_share_estimate)
        0.08
    """
```

Module-level docstrings required for all `packages/` modules.

---

## Logging

**Use `structlog` exclusively.** No `print()`, no `logging.getLogger()` directly.

```python
import structlog

logger = structlog.get_logger(__name__)

# ✅ Good — structured, queryable
logger.info(
    "llm.completion",
    model="gpt-4o",
    prompt_tokens=1250,
    completion_tokens=380,
    latency_ms=2340,
    correlation_id=ctx.correlation_id,
)

# ❌ Bad — unstructured, unsearchable
print(f"LLM call completed: 1250 tokens")
logging.info("LLM completed")
```

### Log Levels

| Level | When to use |
|-------|------------|
| `DEBUG` | Detailed diagnostic info (disabled in production) |
| `INFO` | Normal operational events (agent started, pipeline completed) |
| `WARNING` | Unexpected but recoverable (fallback provider used, budget >80%) |
| `ERROR` | Failures requiring investigation (agent failed, API unreachable) |
| `CRITICAL` | System-level failures requiring immediate response |

### Mandatory Fields

Every log event must include:
- `correlation_id` — W3C trace ID (32 hex chars), set at API gateway
- `service` — service name (e.g. `agents`, `api`, `pipelines`)

**Never log:**
- API keys or tokens
- Full LLM prompt content (log token counts only)
- Personal data (names, emails, addresses)
- MPAN/MPRN numbers without masking

---

## Error Handling

Define domain-specific exceptions in `packages/energy-schemas`:

```python
class EnergyMarketIntelError(Exception):
    """Base exception for all EMI errors."""

class LLMBudgetExceededError(EnergyMarketIntelError):
    """Raised when an agent run exceeds its token budget."""

class DataResidencyError(EnergyMarketIntelError):
    """Raised when a LLM call would violate UK/EU data residency requirements."""

class ElexonAPIError(EnergyMarketIntelError):
    """Raised when the Elexon BMRS API returns an unexpected response."""
```

Rules:
- Never catch bare `Exception` without re-raising or logging
- Always include context in exception messages
- Use `raise X from Y` to preserve exception chains
- Prefer early returns over deeply nested `try/except`

---

## Configuration & Secrets

**Single source of truth: Pydantic `BaseSettings`.**

```python
# ✅ Good
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    azure_openai_api_key: str
    agent_token_budget: int = 50_000

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# ❌ Bad — direct env access
import os
api_key = os.environ["AZURE_OPENAI_API_KEY"]
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
```

Rules:
- `.env` is gitignored — never commit it
- `.env.example` is the canonical template — keep it up to date
- Never hardcode URLs, model names, or limits — use `config/base.yaml`
- Secrets in staging/production come from AWS Secrets Manager, not env vars

---

## Testing

### Structure

```
tests/
├── conftest.py          # Shared fixtures, autouse mocks (blocks live LLM calls)
├── cassettes/           # VCR cassettes (sanitised — no keys/PII)
├── unit/                # Fast, no I/O, mock all dependencies
├── integration/         # Service interactions, VCR cassettes for HTTP
├── e2e/                 # Full system tests (staging only)
└── llm_eval/            # RAGAS/DeepEval evals (nightly CI only)
```

### Coverage Requirements

| Module | Minimum Coverage |
|--------|----------------|
| `packages/energy-schemas` | 95% |
| `packages/llm-core` | 90% |
| `services/api` | 90% |
| `services/agents` | 80% |
| `services/pipelines` | 80% |
| **Overall** | **80%** |

### Naming Convention

```python
# test_<module>.py
def test_<what>_<when>_<expected>():
    ...

# Examples:
def test_circuit_breaker_opens_after_five_consecutive_failures():
def test_fetch_settlement_periods_returns_empty_list_for_bank_holiday():
def test_competitor_analysis_raises_data_residency_error_when_us_provider_selected():
```

### Golden Rules

- `LLM_MOCK_MODE=true` is **always set in CI** — live API calls in tests are forbidden
- VCR cassettes must be sanitised: no API keys, no PII, no MPAN/MPRN numbers
- `tests/llm_eval/` runs nightly only — tag with `@pytest.mark.llm_eval`
- Test data must not contain real customer or competitor data

---

## LLM-Specific Standards

### Prompt Management

- Prompts live in `packages/llm-core/llm_core/prompts/` as Jinja2 `.j2` files
- Prompts are version-controlled in Git — tagged on release
- No hardcoded prompt strings in application code
- Prompts are tested via `promptfoo` in CI on any `prompts/**` change

### Token Budget Enforcement

Every agent run must respect `AGENT_TOKEN_BUDGET`. The `TokenBudget` class in `llm-core` enforces this.

```python
# ✅ Good
async with TokenBudget(max_tokens=settings.agent_token_budget) as budget:
    result = await agent.run(task, budget=budget)

# ❌ Bad — unbounded LLM call
result = await llm.invoke(messages)
```

### Data Residency

When `FEATURE_STRICT_DATA_RESIDENCY=true`, all LLM calls must use EU/UK endpoints:
- Azure OpenAI (`uksouth`) — primary
- Anthropic with `inference_geo: eu` — fallback
- Vertex AI `europe-west2` — secondary fallback
- **Never** use Gemini direct API or OpenAI direct API with personal/business data

### Structured Outputs

Prefer structured outputs via Pydantic models over free-text parsing:

```python
# ✅ Good
response = await llm.with_structured_output(CompetitorAnalysis).ainvoke(messages)

# ❌ Bad — fragile string parsing
response = await llm.ainvoke(messages)
data = json.loads(response.content)  # Breaks on malformed JSON
```
