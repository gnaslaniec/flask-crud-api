.PHONY: install venv test test-cov run db-init db-migrate db-upgrade db-downgrade init-admin clean docs docs-clean frontend seed

PYTHON ?= python3
FLASK_APP ?= app:create_app
FLASK ?= flask
SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?=
DOCSSRC ?= docs
DOCSBUILD ?= docs/_build
FRONTEND_PORT ?= 3000
FRONTEND_DIR ?= frontend

install:
	$(PYTHON) -m pip install -r requirements.txt

venv:
	$(PYTHON) -m venv .venv

test:
	pytest

test-cov:
	pytest --cov=app tests/

run:
	$(FLASK) --app $(FLASK_APP) run

db-init:
	$(FLASK) --app $(FLASK_APP) db init

db-migrate:
	$(FLASK) --app $(FLASK_APP) db migrate -m "$(m)"

db-upgrade:
	$(FLASK) --app $(FLASK_APP) db upgrade

db-downgrade:
	$(FLASK) --app $(FLASK_APP) db downgrade

init-admin:
	$(FLASK) --app $(FLASK_APP) init-admin

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \; -o -type f -name "*.pyc" -delete

docs:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) $(DOCSSRC) $(DOCSBUILD)/html

docs-clean:
	rm -rf $(DOCSBUILD)

seed:
	$(PYTHON) scripts/seed_data.py --users $(or $(users),5) --projects $(or $(projects),5)

frontend:
	$(PYTHON) -m http.server $(FRONTEND_PORT) --directory $(FRONTEND_DIR)
