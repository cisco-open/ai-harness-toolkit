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

Search for:

- `fastapi`
- `pydantic`
- `langchain python`
- `pytest`
- `security review`

## Skills to Install

Install these companion skills for Python code-review support:

```bash
apm install astral-sh/claude-code-plugins/skills/ruff
apm install astral-sh/claude-code-plugins/skills/uv
apm install astral-sh/claude-code-plugins/skills/ty
apm install github/awesome-copilot/skills/pytest-coverage
apm install github/awesome-copilot/skills/security-review
apm install cisco-open/ai-harness-toolkit/skills/python-best-practices
```

These cover linting and formatting (ruff), package management (uv), type checking (ty), test coverage (pytest-coverage), security review, and Python-specific best practices.

## Recommended Deterministic Baseline

Use the detected package manager's run command (`uv run`, `poetry run`, or direct invocation) for all of these:

- environment bootstrap command (detected: `uv sync`, `poetry install`, or `pip install -r requirements.txt`)
- `ruff check .`
- type check with detected type checker (`mypy .`, `basedpyright`, or `pyright`)
- `pytest`
- `bandit -r .`
- `pip-audit`
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
2. add hook tooling only if the repo benefits from it, and keep the hook config minimal
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
- monorepo markers such as uv workspace config, multiple `pyproject.toml` files

## Framework-Specific References

- Use `references/stacks/python/framework-fastapi.md` for FastAPI repos.
- Use `references/stacks/python/framework-django.md` for Django repos.
