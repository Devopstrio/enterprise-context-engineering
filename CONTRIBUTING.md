# Contributing to enterprise-context-engineering

Thank you for contributing to the **enterprise-context-engineering** platform!

## Development Workflow

1. Fork & clone the repository.
2. Install package in editable mode: `pip install -e .[dev]`
3. Create a feature branch: `git checkout -b feat/my-context-feature`
4. Write tests for new context engineering capabilities in `tests/`.
5. Run the test suite: `pytest -v tests/`
6. Run linting: `ruff check src/ tests/`
7. Run type checking: `mypy src/`
8. Submit a Pull Request against `main`.

## Code Standards

- Python 3.11+ with type hints on all functions
- Pydantic v2 for data models
- structlog for structured logging
- All new modules must include unit tests
- Maintain >90% code coverage

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` adding tests
- `ci:` CI/CD changes
- `refactor:` code refactoring

## Review Process

All PRs require at least one approval from `@Devopstrio/context-engineering-team`.
