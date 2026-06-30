# Python

Read this file for Python service, CLI, agent, or notebook-heavy repos.

## Repo Markers

- `pyproject.toml`
- `requirements.txt`
- `poetry.lock` or `uv.lock`
- `pytest.ini`, `ruff.toml`, `mypy.ini`, `pyrightconfig.json`, or `[tool.basedpyright]` in `pyproject.toml`

## Detection First

Before recommending or installing any tooling, detect what the repo already uses:
- **Package manager**: check for `uv.lock`, `poetry.lock`, `[tool.poetry]`, `requirements.txt`. Use the detected manager for all commands.
- **Type checker**: check for `mypy.ini`, `.mypy.ini`, `[tool.mypy]`, `pyrightconfig.json`, `[tool.basedpyright]`, `[tool.pyright]`, or type checker packages in dependencies. Use the detected type checker. Do not recommend switching.
- **Linter**: check for `ruff.toml`, `[tool.ruff]`, `[tool.pylint]`, or linter packages in dependencies.
- **Test runner**: check for `pytest.ini`, `[tool.pytest.ini_options]`, `tox.ini`, `noxfile.py`.
- **Monorepo layout**: check for `uv.lock` with `[workspace]`, multiple `pyproject.toml` files, or workspace-level scripts.

See `references/stacks/python/deterministic-scans.md` for detailed detection resolution orders.

## Skill Search Terms

- `fastapi`
- `pydantic`
- `langchain python`
- `pytest`
- `security review`

## Skills to Install

Install the `stack-python-uv` package when the repo is managed with `uv`:

```bash
apm install --target <ide-1> --target <ide-2> --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/stack-python-uv#stack-python-uv-v<latest>
```

This package covers `security-review`, `python-best-practices`, and the transitive `core` workflow bundle. Repo-native tooling still handles linting, type checking, testing, and packaging.

After installing the matching package, keep the dynamic path available for repo-specific gaps such as framework, testing, or AI-runtime skills that are not already included.

For Poetry-, pip-, or other non-`uv`-managed repos, do not force `stack-python-uv`. Keep using the detected package manager for repo commands and install `core` plus only the extra Python-specific skills the repo still needs.

For extra Python-specific needs, browse repo-local and public curated skills first, then use `npx skills find` only when broader discovery is still needed. Install only the additional skills that fill real gaps in the repo's current workflow.

## Recommended Deterministic Baseline

Use the detected package manager's run command (`uv run`, `poetry run`, or direct invocation) for all of these:
- environment bootstrap command (detected: `uv sync`, `poetry install`, or `pip install -r requirements.txt`)
- lint with the detected linter (`ruff check .`, `pylint`, or the repo's existing lint command)
- type check with the detected type checker (`mypy .`, `basedpyright`, or `pyright`)
- tests with the detected runner (`pytest`, `tox`, `nox`, or the repo's existing test entrypoint)
- `bandit -r .`
- vulnerability audit with the detected package manager path (`pip-audit` or the repo's existing audit command)
- `python -m build` for package validation when applicable

## Fresh Project Setup

For a fresh project with no existing tooling, use `uv` as the package manager and `mypy` as the type checker.

Install the baseline packages:

```bash
uv add --dev ruff mypy pytest bandit pip-audit build pre-commit
```

Required setup:
- define tool settings in `pyproject.toml`
- expose checks through `uv run ...`
- configure `mypy` with stricter settings such as `disallow_untyped_defs = true`
- configure `ruff`, `pytest`, and optional coverage settings in `pyproject.toml`
- add `.pre-commit-config.yaml` if using git hook automation

For existing projects, adapt the above to the detected package manager and type checker.

## Documentation Placement

- environment bootstrap belongs in `docs/dev-environment/`
- durable coding and agent conventions belong in `docs/conventions/`

## Precommit Setup

For Python repos, prefer a documented validation command path plus optional git hooks.

Recommended flow:
1. install the repo's validation tools in its environment manager
2. add hook tooling only if the repo benefits from it, and keep the hook configuration minimal
3. keep slower checks like full `pytest`, type checking, or packaging validation available through the repo's main validation command and optionally push-time hooks
4. document the canonical validation command agents and contributors should run

Typical split:
- commit-time hooks: `ruff check .`, formatting, simple file hygiene
- push-time hooks or explicit validation: type checking, `pytest`, `bandit -r .`, `pip-audit`, `python -m build`

## Extra Stack Discovery

Search for more stack signals such as:
- `fastapi`, `django`, `flask`, `langchain`, `langgraph`, `pydantic`
- `Dockerfile`, `docker-compose.yml`, `.github/workflows/*.yml`
- task runners such as `tox.ini`, `noxfile.py`, `Makefile`
- monorepo markers such as uv workspace configuration, multiple `pyproject.toml` files

## Framework-Specific References

- Use `references/stacks/python/framework-fastapi.md` for FastAPI repos.
- Use `references/stacks/python/framework-django.md` for Django repos.
