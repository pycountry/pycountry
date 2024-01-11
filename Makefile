PYTHON ?= python
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
TOX ?= tox
MYPY ?= mypy

.PHONY: help
help:  ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all
all: data poetry.lock lint test  ## Build the project: generate data, lock dependencies, lint, test, and build
	$(POETRY) build

.PHONY: data
data:  ## Pull most up to date data from Debian iso-codes
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	$(PYTHON) generate.py

.PHONY: sdist
sdist: data poetry.lock  ## Create a source distribution of the project
	$(POETRY) build --format=sdist

.PHONY: wheel
wheel: data poetry.lock  ## Create a wheel distribution of the project
	$(POETRY) build --format=wheel

.PHONY: lock
lock: pyproject.toml  ## Generate a lock file for project dependencies
	$(POETRY) lock

.PHONY: lint
lint:  ## Run linters on the codebase
	$(PRE_COMMIT) run --all-files

.PHONY: test
test:  ## Run pytest tests on the project using Tox
	$(TOX)

.PHONY: clean
clean:  ## Clean the project directory (removes build files and temporary files)
	git clean -fdX

.PHONY: check
check: lint test mypy-check  ## Run checks: linting, testing, and mypy type checking

.PHONY: mypy-check
mypy-check:  ## Run mypy for type checking
	$(MYPY) .
