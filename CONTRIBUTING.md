# Contributing to pycountry

Welcome to the pycountry project! We appreciate your interest in contributing. Whether it's improving documentation, adding new features, fixing bugs, or helping with testing, your contributions are valuable to the community.

Before you get started, please take a moment to read through this guide to understand our contribution process and guidelines.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Code of Conduct](#code-of-conduct)
3. [Prerequisites](#prerequisites)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Coding Guidelines](#coding-guidelines)
7. [Pull Requests](#pull-requests)
8. [Review Process](#review-process)
9. [Documentation](#documentation)
10. [Community and Communication](#community-and-communication)
11. [License](#license)

## Getting Started

To start contributing to pycountry, follow these steps:

1. Fork the repository on GitHub.
2. Clone your fork locally.
3. Create a new feature branch (`git checkout -b my-new-feature`).
4. Make your changes and commit them (`git commit -am 'Add some feature'`).
5. Push the branch to GitHub (`git push origin my-new-feature`).
6. Submit a pull request.

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## Code of Conduct

Please note that pycountry has a [Code of Conduct](https://github.com/pycountry/pycountry/blob/main/CODEOFCONDUCT.md) that we expect all contributors and community members to adhere to. By participating in this project, you agree to abide by its terms.

## Prerequisites

Before contributing, make sure you have the following prerequisites:

- Python (3.8 or later)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- [make](https://www.gnu.org/software/make/) (commonly pre-installed on Unix-like systems)

## Making Changes

When making changes to the codebase, keep the following in mind:

- Create a new branch for each feature or bug fix.
- Write clear and concise commit messages.
- Keep your changes focused and avoid unrelated code modifications.
- Update documentation as needed.

## Testing

To maintain the quality of `pycountry`, we encourage contributors to run tests and perform code quality checks before submitting any changes. `pycountry` uses Poetry for dependency management and tools like `mypy`, `pre-commit`, and `make` for testing and linting.

To run the test suite:

1. Install Poetry if you haven't already. Visit the Poetry website for [installation instructions](https://python-poetry.org/docs/#installation).
2. Install the project dependencies by running ``poetry install`` in the project's root directory. This command also installs necessary tools like `mypy` and `pre-commit` as defined in `pyproject.toml`.
3. Activate the Poetry shell with ``poetry shell``. This will spawn a new shell subprocess, which is configured to use your project’s virtual environment.
4. Run the unit tests, linting checks, and type checks using ``make check``. Ensure you have `make` installed on your system (commonly pre-installed on Unix-like systems).
7. Ensure all tests pass successfully.

Note: The project's dependencies and the environment needed to run tests are managed by Poetry, using the `pyproject.toml` and `poetry.lock` files.

If you add new features or fix bugs, please include corresponding tests. Follow the project's coding standards and update [documentation](#documentation) as needed.

## Coding Guidelines

Follow the coding style and guidelines used in the project. We use [black](https://github.com/psf/black) and [isort](https://pycqa.github.io/isort/) for code formatting. Make sure your code aligns with these tools' recommendations.

## Pull Requests

When submitting a pull request:

- Follow the standard Pull Request Template.
- Provide a clear and descriptive title.
- Explain the purpose and context of the changes in the description.
- Reference any related issues or PRs.
- Be responsive to feedback and make necessary revisions.

## Review Process

Expect code reviews from maintainers and contributors. Be open to feedback and be prepared to make revisions to your code.

## Documentation

If your contribution requires changes to documentation, please update the documentation accordingly. This includes code comments, [HISTORY](https://github.com/pycountry/pycountry/blob/main/HISTORY.txt) and [README](https://github.com/pycountry/pycountry/blob/main/README.rst) files.

## Community and Communication

Join our community and feel free to ask questions, seek help, or discuss ideas. You can reach out through [GitHub issues](https://github.com/pycountry/pycountry/issues).

## License

By contributing to pycountry, you agree that your contributions will be licensed under the project's [LGPL 2.1 License](https://github.com/pycountry/pycountry/blob/main/LICENSE.txt).
