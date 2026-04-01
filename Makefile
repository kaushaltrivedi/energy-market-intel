.PHONY: bootstrap lint typecheck test test-unit test-integration security clean help

PYTHON := python3
UV := uv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Install all dependencies and set up pre-commit hooks
	$(UV) sync --all-packages
	$(UV) run pre-commit install
	$(UV) run pre-commit install --hook-type commit-msg
	@echo "✅ Bootstrap complete. Copy .env.example to .env and configure your API keys."

lint: ## Run ruff linter and black formatter check
	$(UV) run ruff check .
	$(UV) run black --check .

lint-fix: ## Auto-fix lint issues
	$(UV) run ruff check --fix .
	$(UV) run black .

typecheck: ## Run mypy type checking
	$(UV) run mypy packages/ services/

test: ## Run all tests (unit + integration)
	$(UV) run pytest tests/unit tests/integration

test-unit: ## Run unit tests only
	$(UV) run pytest tests/unit -v

test-integration: ## Run integration tests only
	$(UV) run pytest tests/integration -v

test-e2e: ## Run end-to-end tests
	$(UV) run pytest tests/e2e -v

test-cov: ## Run tests with coverage report
	$(UV) run pytest tests/unit tests/integration --cov --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

security: ## Run security scans (bandit + pip-audit + gitleaks)
	$(UV) run bandit -r packages/ services/ -c pyproject.toml
	$(UV) run pip-audit
	gitleaks detect --source . --verbose

clean: ## Remove build artifacts, caches, and coverage reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "coverage.xml" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

docker-up: ## Start local services (Postgres, Weaviate, Redis)
	docker-compose up -d

docker-down: ## Stop local services
	docker-compose down
