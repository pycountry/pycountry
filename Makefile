VENV_DIR ?= .venv

SYSTEM_PYTHON ?= python3

# If poetry already exists, use it.  If not, we'll create a local venv for it
POETRY ?= $(or $(shell command -v poetry 2>/dev/null),$(VENV_DIR)/bin/poetry)
# Calculate it once
POETRY := $(POETRY)
POETRY_READY_MARKER := .cache/poetry_ready
MYPY ?= $(POETRY) run mypy
PYTHON ?= $(POETRY) run python
PRE_COMMIT ?= $(POETRY) run pre-commit
TOX ?= $(POETRY) run tox

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
	@echo
	@echo "If available, a global installation of \`poetry\` will be used \
	       to manage this project.  Otherwise, a local virtual \
	       environment will be created in $(VENV_DIR) using \
	       \`$(SYSTEM_PYTHON)\`.  Other commands such as \`mypy\` or \
	       \`tox\` will be run using \`poetry run\`.  There are several \
	       makefile variables set at the top of Makefile that may be \
	       defined in your environment or on the command line to affect \
	       how various targets are run." \
	       | sed -e 's/\s\s\+/ /g' \
	       | fmt -w 80

.PHONY: all
## Run all commands necessary to ensure that everything is up to date and
## passing existing tests, then build distribution artifacts
all: update data check
	$(POETRY) build

.PHONY: data
## Regenerate all ISO data from the upstream Debian iso-codes project
data: $(POETRY_READY_MARKER)
	rm -rf src/pycountry/databases
	rm -rf src/pycountry/locales
	$(PYTHON) generate.py

.PHONY: sdist
## Create a source distribution of the project
sdist: data
	$(POETRY) build --format=sdist

.PHONY: wheel
## Create a wheel distribution of the project
wheel: data
	$(POETRY) build --format=wheel

.HELP: poetry.lock
## Ensure that the poetry.lock file is up to date
poetry.lock: pyproject.toml | $(POETRY)
	$(POETRY) lock --no-update

.cache:
	@mkdir .cache

$(POETRY_READY_MARKER): poetry.lock | .cache
	$(POETRY) install
	@touch $@

$(VENV_DIR)/bin/poetry:
	$(SYSTEM_PYTHON) -m venv --clear $(VENV_DIR)
	$(VENV_DIR)/bin/python3 -m pip install -U poetry

.PHONY: venv
## Create a local virtual environment with poetry installed
venv: $(VENV_DIR)/bin/poetry

.PHONY: update
## Update all dependencies
update: poetry.lock
	$(POETRY) update
	$(PRE_COMMIT) autoupdate

.PHONY: lint
## Run automatic formatting checkers and fixers against all files of all types
lint: $(POETRY_READY_MARKER)
	$(PRE_COMMIT) run --all-files

.PHONY: test
## Run unit tests using every supported version of Python
test: $(POETRY_READY_MARKER)
	$(TOX)

.PHONY: typecheck
## Run static typing checks on the codebase
typecheck: $(POETRY_READY_MARKER)
	$(MYPY)

.PHONY: check
## Run all checks, including linting, static typing, and unit tests
check: lint typecheck test

.PHONY: clean
## Clean the project directory, removing all existing .gitignore-ed files
clean:
	git clean -fdX
