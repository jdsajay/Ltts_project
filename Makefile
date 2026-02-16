.PHONY: help install dev test lint run clean

PYTHON ?= python3
VENV   := .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Environment ───────────────────────────────────────

venv:  ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv  ## Install project + dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "\n✅ Installed. Activate with: source $(VENV)/bin/activate"

dev: install  ## Install with dev dependencies
	$(PIP) install -e ".[dev]"
	@echo "\n✅ Dev environment ready."

# ── Quality ───────────────────────────────────────────

test:  ## Run tests
	$(PY) -m pytest tests/ -v --tb=short

lint:  ## Lint code
	$(PY) -m ruff check src/ tests/
	$(PY) -m mypy src/label_compliance/

format:  ## Auto-format code
	$(PY) -m ruff format src/ tests/

# ── Pipeline ──────────────────────────────────────────

ingest:  ## Ingest ISO standards into knowledge base
	$(PY) -m label_compliance ingest

check:  ## Run compliance check on all labels
	$(PY) -m label_compliance check

run:  ## Run full pipeline (ingest + check)
	$(PY) -m label_compliance run

# ── Utilities ─────────────────────────────────────────

clean:  ## Remove generated outputs
	rm -rf outputs/redlines/* outputs/reports/* outputs/logs/*
	rm -rf data/knowledge_base/chromadb/
	@echo "✅ Cleaned outputs."

distclean: clean  ## Remove venv too
	rm -rf $(VENV)
	rm -rf *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	@echo "✅ Deep clean complete."
