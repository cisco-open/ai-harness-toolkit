# Django

Use this file when the repo contains `django` in dependencies, `manage.py`, or Django-style project structure.

## What to Install

Baseline packages usually include:

- `django`
- `djangorestframework` (if building APIs)
- `pytest-django` for test integration
- `django-debug-toolbar` for local development
- `django-stubs` or `djangorestframework-stubs` for type checking

## Required Configuration

- configure `DJANGO_SETTINGS_MODULE` for test and lint environments
- enable strict type checking with Django stubs
- expose deterministic commands for lint, type check, test, migrations check, and build
- document local runtime dependencies such as Python version and database setup

## Skills to Install

Focus this file on Django-specific additions instead of shared workflow tooling.

Install the Django companion skills from Sentry's collection:

```bash
apm install getsentry/skills/skills/django-perf-review
apm install getsentry/skills/skills/django-access-review
```

These cover Django performance review (N+1 queries, queryset optimization) and access control review (permission checks, authentication).

## Search Terms

Use curated sources first, then `npx skills find` for broader discovery when needed. Install the chosen package with `apm install`.

Useful queries include:

- `django`
- `django rest framework`
- `django testing`
- `django security`

## Framework Markers

- `django` in dependencies (`pyproject.toml`, `requirements.txt`)
- `manage.py` in the project root
- `settings.py` or `DJANGO_SETTINGS_MODULE` references
- `from django` or `from rest_framework` in source files
- `urls.py`, `views.py`, `models.py` patterns
