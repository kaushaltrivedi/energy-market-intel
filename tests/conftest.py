"""Root test configuration and shared fixtures.

This module configures pytest for the entire test suite, including:
- Blocking live LLM API calls in all non-nightly tests
- Shared fixtures for database, Redis, and HTTP mocking
- VCR cassette configuration with PII scrubbing
"""

from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


# Ensure LLM_MOCK_MODE is set before any imports that might trigger LLM calls
os.environ.setdefault("LLM_MOCK_MODE", "true")
os.environ.setdefault("APP_ENV", "test")


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "llm_eval: marks tests as LLM evaluation tests (nightly only, requires live APIs)",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (requires running services)",
    )
    config.addinivalue_line(
        "markers",
        "e2e: marks tests as end-to-end tests (staging only)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Skip llm_eval tests unless explicitly running the nightly suite."""
    if not config.getoption("--run-llm-eval", default=False):
        skip_llm_eval = pytest.mark.skip(
            reason="LLM eval tests are nightly only. Run with --run-llm-eval to include."
        )
        for item in items:
            if "llm_eval" in item.keywords:
                item.add_marker(skip_llm_eval)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom CLI options."""
    parser.addoption(
        "--run-llm-eval",
        action="store_true",
        default=False,
        help="Run LLM evaluation tests (requires live API keys)",
    )


@pytest.fixture(autouse=True)
def block_live_llm_calls() -> Generator[None, None, None]:
    """Autouse fixture that blocks all live LLM API calls in tests.

    This is a safety net — tests should not rely on this to mock LLMs,
    but it prevents accidental live API calls from burning budget.

    Yields:
        None
    """
    if os.environ.get("LLM_MOCK_MODE", "true").lower() == "true":
        with patch("litellm.completion") as mock_completion, \
             patch("litellm.acompletion") as mock_acompletion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="[MOCKED LLM RESPONSE]"))],
                usage=MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            )
            mock_acompletion.return_value = mock_completion.return_value
            yield
    else:
        yield


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for anyio tests."""
    return "asyncio"
