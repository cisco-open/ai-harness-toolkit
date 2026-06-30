# Python Deterministic Scans

Use repeatable commands that can run locally and in CI without human judgment.

## Package Manager Resolution

Detect the environment manager from the repo first. Do not assume a package manager -- use what the repo already has.

Detection order:

- `uv.lock` -> use `uv`
- `poetry.lock` -> use `poetry`
- `pyproject.toml` with `[tool.poetry]` -> use `poetry`
- `pyproject.toml` with `[tool.uv]` or `[build-system]` referencing `hatchling` or `setuptools` -> use `uv` or `pip` as appropriate
- checked-in `requirements.txt` or `requirements-dev.txt` -> use `pip`

Fresh project default when no existing manager is detected: `uv`

## Type Checker Resolution

Detect which type checker the repo already uses before recommending one.

Detection order:

- `pyrightconfig.json`, `pyrightconfig.jsonc`, or `[tool.pyright]` in `pyproject.toml` -> use `pyright`
- `[tool.basedpyright]` in `pyproject.toml` or basedpyright in dev dependencies -> use `basedpyright`
- `mypy.ini`, `.mypy.ini`, `setup.cfg` with `[mypy]`, or `[tool.mypy]` in `pyproject.toml` -> use `mypy`
- mypy in dev dependencies -> use `mypy`

If the repo already uses a type checker, use it. Do not recommend switching.

Fresh project default when no existing type checker is detected: `mypy`

Common type checker configurations:

- **mypy**: `disallow_untyped_defs = true` in `[tool.mypy]`
- **basedpyright**: `typeCheckingMode = "strict"` or baseline management in `[tool.basedpyright]`
- **pyright**: `typeCheckingMode = "strict"` in `pyrightconfig.json`

## Required Packages

Detect what is already installed. Only add packages that are missing.

Baseline packages (adjust tool names to match detected type checker and package manager):

- `ruff` (linter and formatter)
- type checker: `mypy`, `basedpyright`, or `pyright` (whichever the repo uses)
- `pytest` (test runner)
- `bandit` (SAST)
- `pip-audit` (vulnerability audit)
- `build` (packaging verification, when the repo produces packages)
- `pre-commit` (git hooks, when the repo uses them)

Example install for a fresh `uv` project using `mypy`:

```bash
uv add --dev ruff mypy pytest bandit pip-audit build pre-commit
```

Adapt the command for the detected package manager:

- **poetry**: `poetry add --group dev ruff mypy pytest bandit pip-audit build pre-commit`
- **pip**: `pip install ruff mypy pytest bandit pip-audit build pre-commit` (and add to `requirements-dev.txt`)

## Required Configuration

- keep tool configuration in `pyproject.toml` where possible
- configure the detected type checker with strict-ish settings appropriate to that tool
- define `tool.ruff` and `tool.pytest.ini_options` in `pyproject.toml`
- expose validation through the detected package manager's run command

## Commands

Substitute `{run}` with the appropriate command prefix for the detected package manager:

- **uv**: `uv run`
- **poetry**: `poetry run`
- **pip/venv**: use the virtualenv-activated command directly, or `python -m`

| Check | Command |
|-------|---------|
| vulnerability audit | `{run} pip-audit` |
| SAST | `{run} bandit -r .` |
| lint and format | `{run} ruff check .` |
| type check | `{run} mypy .` or `{run} basedpyright` or `{run} pyright` |
| tests | `{run} pytest` |
| packaging check | `{run} python -m build` |

Choose one enforcement mode before wiring these commands:

- `enforced`: use the commands above as blocking checks
- `advisory`: keep the same commands, but switch to native no-fail options where available

## Advisory Mode Configuration

In advisory mode, keep every deterministic check installed and wired, but make findings non-blocking:

- use `ruff check --exit-zero`
- use `bandit --exit-zero`
- suffix `pip-audit` with `|| true`
- if the harness is introducing a new type checker, suffix that command with `|| true` until the repo is ready to enforce it

Examples:

```bash
uv run ruff check . --exit-zero
uv run bandit -r . --exit-zero
uv run pip-audit || true
uv run mypy . || true
```

If the repo already had a type checker before the harness setup, keep using it as detected and decide whether to preserve existing enforcement rather than loosening it automatically.

## Wiring Rules

- keep one documented validation path
- use the detected package manager's run wrapper for local and CI consistency
- keep the chosen enforcement mode consistent across local commands, hooks, and CI
- add pre-push or CI hooks only after the commands pass locally
- for monorepos with uv workspaces, determine whether checks should run at the workspace root or per-package and document the approach
