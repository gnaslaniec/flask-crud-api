.PHONY: install test test-cov run init-db clean docs docs-clean

PYTHON ?= python3
FLASK_APP ?= run.py
FLASK ?= flask
SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?=
DOCSSRC ?= docs
DOCSBUILD ?= docs/_build
SOURCE ?= source

install:
	$(PYTHON) -m pip install -r requirements.txt

venv:
	$(PYTHON) -m venv venv

test:
	pytest

test-cov:
	pytest --cov=app tests/

run:
	$(FLASK) --app $(FLASK_APP) run

init-db:
	$(FLASK) --app $(FLASK_APP) init-db

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \; -o -type f -name "*.pyc" -delete

docs:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) $(DOCSSRC) $(DOCSBUILD)/html

docs-clean:
	rm -rf $(DOCSBUILD)
