# Python

Stack reference for the code-review orchestrator. Defines detection signals, deterministic checks, framework detection, companion skill mappings, and native review focus areas for Python projects.

## Detection Signals

### File Extensions

- `*.py`
- `*.pyi` (type stubs)

### Config Files

- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `tox.ini`
- `noxfile.py`

### Lockfiles

- `uv.lock`
- `poetry.lock`
- `requirements.txt`
- `requirements-dev.txt`
- `Pipfile.lock`

## Deterministic Check Commands

### Quick Checks

| Check | Command | Condition |
|---|---|---|
| Lint | `ruff check <files>` | `[tool.ruff]` in `pyproject.toml` or `ruff.toml` exists |
| Format check | `ruff format --check <files>` | Same as above |
| Type check (mypy) | `mypy <files>` | `mypy.ini`, `.mypy.ini`, or `[tool.mypy]` in `pyproject.toml` |
| Type check (pyright) | `pyright <files>` | `pyrightconfig.json` or `[tool.pyright]` in `pyproject.toml` |
| Type check (basedpyright) | `basedpyright <files>` | `[tool.basedpyright]` in `pyproject.toml` |
| Type check (ty) | `ty check <files>` | ty is configured or installed |

Use the detected package manager's run command (`uv run`, `poetry run`, or direct) as prefix.

### Extended Checks

| Check | Command | Condition |
|---|---|---|
| Test | `pytest` | `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml` |
| Coverage | `pytest --cov` | Coverage configured |
| SAST | `bandit -r <files>` | Bandit installed |
| SAST | `semgrep --config auto <files>` | Semgrep installed |
| Audit | `pip-audit` | pip-audit installed |

### Auto-Fix Commands

| Tool | Fix Command | Safe |
|---|---|---|
| Ruff lint | `ruff check --fix <files>` | Yes (excludes unsafe fixes) |
| Ruff format | `ruff format <files>` | Yes |

**Not safe:** `ruff check --unsafe-fixes` -- never use this in the fix loop.

## Framework Detection

### FastAPI

**Signals:**

- `fastapi` in dependencies (check `pyproject.toml` `[project.dependencies]`, `[tool.poetry.dependencies]`, or `requirements.txt`)
- `from fastapi import` in source files
- `uvicorn` or `hypercorn` in dependencies

**Activates:** Framework lane with FastAPI companion skills.

### Django

**Signals:**

- `django` in dependencies
- `manage.py` in project root
- `DJANGO_SETTINGS_MODULE` references
- `from django` in source files

**Activates:** Framework lane with Django companion skills.

## Companion Skill Mappings

### Security Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@security-review` | `apm install github/awesome-copilot/skills/security-review` |

### Best Practices Lane

| Skill | Install Command |
|---|---|
| `cisco-open/ai-harness-toolkit@python-best-practices` | `apm install cisco-open/ai-harness-toolkit/skills/python-best-practices` |

### Framework Lane: FastAPI

| Skill | Install Command |
|---|---|
| `fastapi/fastapi@fastapi` | `apm install fastapi/fastapi/skills/fastapi` |

### Framework Lane: Django

| Skill | Install Command |
|---|---|
| `getsentry/skills@django-perf-review` | `apm install getsentry/skills/skills/django-perf-review` |
| `getsentry/skills@django-access-review` | `apm install getsentry/skills/skills/django-access-review` |

## Native Review Focus Areas

Use these when companion skills are not installed. Each area describes patterns to look for in manual review.

### General Python

- **Blocking code in async functions**: Synchronous I/O, `time.sleep()`, or CPU-heavy work inside `async def` functions without offloading to a thread pool
- **N+1 query patterns**: Database queries inside loops, missing `select_related` / `prefetch_related` in Django, missing eager loading in SQLAlchemy
- **Mutable default arguments**: Using `list`, `dict`, or other mutable objects as default parameter values
- **Bare except clauses**: `except:` or `except Exception:` without specific exception types, swallowing errors silently
- **Resource leaks**: Missing context managers (`with` statements) for files, database connections, HTTP sessions, locks
- **Import-time side effects**: Code that runs at import time (module-level network calls, database queries, heavy computation)
- **Test quality and coverage gaps**: Missing failure-path tests, weak assertions, over-mocking, or coverage blind spots not caught by the repo's native test tooling

### FastAPI Specific

- **Missing response models**: Endpoints without `response_model` parameter, leaking internal data structures
- **Sync endpoints blocking the event loop**: Using synchronous database drivers in async FastAPI endpoints
- **Missing dependency injection**: Hardcoded dependencies instead of using FastAPI's `Depends()`
- **Missing input validation**: Endpoints accepting raw `dict` instead of Pydantic models

### Django Specific

- **Missing permission checks**: Views without `@login_required`, `@permission_required`, or DRF permission classes
- **Queryset evaluation in templates**: Lazy querysets evaluated multiple times in templates
- **Missing database indexes**: Fields used in `filter()`, `order_by()`, or `exclude()` without `db_index=True`
- **Raw SQL injection**: Using `raw()` or `extra()` with user input without parameterization
