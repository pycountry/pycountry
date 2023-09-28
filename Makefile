PYTHON ?= python
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
TOX ?= tox

.PHONY: all
all: data poetry.lock lint test
	$(POETRY) build

.PHONY: data
data:
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	$(PYTHON) generate.py

.PHONY: sdist
sdist: data poetry.lock
	$(POETRY) build --format=sdist

.PHONY: wheel
wheel: data poetry.lock
	$(POETRY) build --format=wheel

poetry.lock: pyproject.toml
	$(POETRY) lock

.PHONY: lint
lint:
	$(PRE_COMMIT) run --all-files

.PHONY: test
test:
	$(TOX)
