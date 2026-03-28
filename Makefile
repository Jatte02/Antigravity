# =============================================================================
# MarketSense — Automatización de Desarrollo
# =============================================================================

.DEFAULT_GOAL := ayuda
VENV         := .venv
PIP          := $(VENV)/bin/pip
PYTHON       := $(VENV)/bin/python
UVICORN      := $(VENV)/bin/uvicorn
RUFF         := $(VENV)/bin/ruff
PYTEST       := $(VENV)/bin/pytest
JUPYTER      := $(VENV)/bin/jupyter

# ── Configuración ────────────────────────────────────────────────────────────

.PHONY: venv
venv: ## Crear entorno virtual
	python3 -m venv $(VENV)

.PHONY: instalar
instalar: venv ## Instalar todas las dependencias de Python (core + dev)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PYTHON) -m ipykernel install --user --name marketsense --display-name "MarketSense (Python 3.12)"

.PHONY: instalar-frontend
instalar-frontend: ## Instalar dependencias del frontend Next.js
	cd frontend && npm install

# ── Desarrollo ───────────────────────────────────────────────────────────────

.PHONY: dev-backend
dev-backend: ## Iniciar servidor de desarrollo FastAPI
	$(UVICORN) backend.api.main:app --reload --port 8000

.PHONY: dev-frontend
dev-frontend: ## Iniciar servidor de desarrollo Next.js
	cd frontend && npm run dev

.PHONY: dev
dev: ## Iniciar backend y frontend (ejecutar en terminales separadas)
	@echo "Iniciando backend y frontend..."
	@echo "Ejecuta 'make dev-backend' y 'make dev-frontend' en terminales separadas."

# ── Calidad ──────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Ejecutar linter (ruff check + format)
	$(RUFF) check backend/ tests/ --fix
	$(RUFF) format backend/ tests/

.PHONY: test
test: ## Ejecutar tests con pytest
	$(PYTEST) -v

# ── Datos ────────────────────────────────────────────────────────────────────

.PHONY: notebook
notebook: ## Iniciar Jupyter Lab
	$(JUPYTER) lab --notebook-dir=notebooks

# ── Utilidades ───────────────────────────────────────────────────────────────

.PHONY: limpiar
limpiar: ## Eliminar artefactos de build y cachés
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build .pytest_cache .ruff_cache htmlcov .coverage

.PHONY: ayuda
ayuda: ## Mostrar este mensaje de ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
