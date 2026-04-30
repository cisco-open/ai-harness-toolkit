# FastAPI

Use this file when the repo contains `fastapi` in dependencies, `uvicorn` or `hypercorn` as the ASGI server, or FastAPI-style route patterns.

## What to Install

Baseline packages usually include:

- `fastapi`
- `uvicorn` or `hypercorn`
- `pydantic` (included with FastAPI)
- `httpx` for async test client
- `pytest` and `pytest-asyncio` for async test support

## Required Configuration

- enable strict Pydantic model validation
- configure async test support in pytest
- expose deterministic commands for lint, type check, test, and build
- document local runtime dependencies such as Python version and ASGI server

## Skills to Install

Focus this file on FastAPI-specific additions instead of shared workflow tooling.

Install the official FastAPI skill:

```bash
apm install fastapi/fastapi/skills/fastapi
```

If the repo includes frontend or AI integrations, add those framework skills separately.

## Search Terms

Use curated sources first, then `npx skills find` for broader discovery when needed. Install the chosen package with `apm install`.

Useful queries include:

- `fastapi`
- `pydantic`
- `async python`
- `api testing`

## Framework Markers

- `fastapi` in dependencies (`pyproject.toml`, `requirements.txt`)
- `from fastapi import` in source files
- `uvicorn` or `hypercorn` in dependencies or scripts
- `@app.get`, `@app.post`, `@router.get` patterns in source files
