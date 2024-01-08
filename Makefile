PYTHON ?= python
POETRY ?= poetry
PRE_COMMIT ?= pre-commit
TOX ?= tox

# Note: any comment that starts with '## ' is taken to be a help string and
# emitted by the 'help' target, along with the line above it with a leading
# ".PHONY: " or ".HELP: " removed.  Any other commentary must use just one '#'.

.PHONY: help
## Display this help message
help: _ESCAPE := $(shell printf '\033')
help:
	@echo "Usage: make [target]"
	@grep --no-group-separator -EB1 '^## ' Makefile \
	| sed \
	-e 's/^.\(PHONY\|HELP\): \(.\+\)/\n$(_ESCAPE)[36m\2$(_ESCAPE)[0m:/' \
	-e 's/^## /\t/'

.PHONY: all
## Run all commands necessary to ensure that everything is up to date and
## passing existing tests, then build distribution artifacts
all: data poetry.lock lint test
	$(POETRY) build

.PHONY: data
## Regenerate all ISO data from the upstream Debian iso-codes project
data:
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	$(PYTHON) generate.py

.PHONY: sdist
## Create a source distribution of the project
sdist: data poetry.lock
	$(POETRY) build --format=sdist

.PHONY: wheel
## Create a wheel distribution of the project
wheel: data poetry.lock
	$(POETRY) build --format=wheel

.HELP: poetry.lock
## Ensure that the poetry.lock file is up to date and install all dependencies
## in the poetry environment
poetry.lock: pyproject.toml
	$(POETRY) lock

.PHONY: lint
## Run automatic formatting checkers and fixers against all files of all types
lint:
	$(PRE_COMMIT) run --all-files

.PHONY: test
## Run unit tests using every supported version of Python
test:
	$(TOX)

.PHONY: clean
## Clean the project directory, removing all existing .gitignore-ed files
clean:
	git clean -fdX
