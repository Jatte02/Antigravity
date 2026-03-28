# =============================================================================
# MarketSense — Development Automation
# =============================================================================

.DEFAULT_GOAL := help
VENV         := .venv
PIP          := $(VENV)/bin/pip
PYTHON       := $(VENV)/bin/python
UVICORN      := $(VENV)/bin/uvicorn
RUFF         := $(VENV)/bin/ruff
PYTEST       := $(VENV)/bin/pytest
JUPYTER      := $(VENV)/bin/jupyter

# ── Setup ────────────────────────────────────────────────────────────────────

.PHONY: venv
venv: ## Create virtual environment
	python3 -m venv $(VENV)

.PHONY: install
install: venv ## Install all Python dependencies (core + dev)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PYTHON) -m ipykernel install --user --name marketsense --display-name "MarketSense (Python 3.12)"

.PHONY: install-frontend
install-frontend: ## Install Next.js frontend dependencies
	cd frontend && npm install

# ── Development ──────────────────────────────────────────────────────────────

.PHONY: dev-backend
dev-backend: ## Start FastAPI development server
	$(UVICORN) backend.api.main:app --reload --port 8000

.PHONY: dev-frontend
dev-frontend: ## Start Next.js development server
	cd frontend && npm run dev

.PHONY: dev
dev: ## Start both backend and frontend (requires GNU parallel or run in separate terminals)
	@echo "Starting backend and frontend..."
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals."

# ── Quality ──────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Run linter (ruff check + format)
	$(RUFF) check backend/ tests/ --fix
	$(RUFF) format backend/ tests/

.PHONY: test
test: ## Run tests with pytest
	$(PYTEST) -v

# ── Data ─────────────────────────────────────────────────────────────────────

.PHONY: notebook
notebook: ## Start Jupyter Lab
	$(JUPYTER) lab --notebook-dir=notebooks

# ── Utilities ────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build .pytest_cache .ruff_cache htmlcov .coverage

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
