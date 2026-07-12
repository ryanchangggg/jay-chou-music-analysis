# =============================================================================
# Jay Chou Music Deep Analysis — Makefile
# =============================================================================

.PHONY: help install setup lint clean data notebooks

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install Python dependencies"
	@echo "  setup            Create virtual environment + install deps"
	@echo "  lint             Run flake8 on src/analysis/"
	@echo "  clean            Remove __pycache__ and .ipynb_checkpoints"
	@echo "  data             Run preprocessing pipeline"
	@echo "  notebooks        Launch Jupyter Lab"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Run: source .venv/bin/activate"

lint:
	flake8 src/analysis/ --max-line-length=100

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ipynb_checkpoints' -exec rm -rf {} + 2>/dev/null || true

data:
	python3 -m src.analysis.preprocess

notebooks:
	jupyter lab notebooks/
