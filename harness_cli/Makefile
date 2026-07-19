# Bridle — build & test shortcuts
# Usage: make test / make build / make clean

PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

.PHONY: install test build clean

install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTEST) tests/ -v --tb=short

test-cov:
	$(PYTEST) tests/ -v --tb=short --cov=harness_cli --cov-report=term-missing

build:
	$(PYTHON) -m PyInstaller bridle.spec --clean --noconfirm

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info __pycache__ src/**/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
