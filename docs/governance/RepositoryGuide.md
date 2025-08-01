# Repository Governance Guide

## 1. Branching Strategy
We follow a streamlined Trunk-Based Development approach to minimize merge conflicts and ensure continuous integration.
*   `main`: The primary, deployable branch. Always stable.
*   `feature/<name>`: Short-lived branches for new functionality (e.g., `feature/semantic-compression`).
*   `fix/<name>`: Short-lived branches for bug fixes (e.g., `fix/dynamo-ttl-bug`).
*   **Direct commits to `main` are strictly prohibited.** All changes must go through a Pull Request.

## 2. Pull Request Review Process
To merge a branch into `main`, the following criteria must be met:
1.  **CI Pipeline Pass**: All automated tests, linting, and security scans must pass.
2.  **Code Coverage**: The PR must maintain or increase the overall repository test coverage (minimum threshold: 85%).
3.  **Approvals**: At least one approving review from a code owner (defined in `.github/CODEOWNERS`).
4.  **No Stale Comments**: All review comments must be explicitly resolved.

## 3. CI/CD Pipeline (GitHub Actions)
Our automated pipeline ensures code quality and deployment safety.
*   **On Pull Request**:
    *   `lint`: Runs `flake8`, `black`, and `mypy` for static typing checks.
    *   `test`: Runs `pytest` suite across multiple Python versions.
    *   `security`: Runs `bandit` for Python security flaws and `trivy` for Docker image vulnerabilities.
*   **On Merge to `main`**:
    *   Executes all PR checks.
    *   Builds the Docker image and tags it with the short Git SHA.
    *   Pushes to Amazon ECR.
    *   Triggers ArgoCD to sync the deployment in the `staging` cluster.

## 4. Versioning Strategy
We adhere to Semantic Versioning (SemVer) 2.0.0 (`MAJOR.MINOR.PATCH`).
*   **MAJOR**: Breaking changes to the API contract (e.g., changing the structure of `AssembledContext`).
*   **MINOR**: Backwards-compatible new features (e.g., adding a new compression algorithm option).
*   **PATCH**: Backwards-compatible bug fixes (e.g., fixing a token counting edge case).
Releases are cut manually by tagging a commit on `main` (e.g., `git tag v1.2.0`). This triggers the production deployment pipeline.

## 5. Dependency Management
Dependencies are strictly pinned to ensure reproducible builds.
*   **Tooling**: We use `Poetry` for dependency management.
*   **Adding a dependency**: Use `poetry add <package>`. Do not manually edit `pyproject.toml`.
*   **Updates**: Dependabot is configured to create weekly PRs for minor and patch updates to our dependencies. These must be reviewed and merged promptly to avoid accumulating technical debt.

## 6. Code Quality Standards
*   **Formatting**: Code is auto-formatted using `Black` (line length 100).
*   **Typing**: Strict type hinting is enforced via `mypy`. All function signatures and variables must have explicit types.
*   **Docstrings**: All public classes and methods must include Google-style docstrings explaining parameters, return types, and potential exceptions raised.
