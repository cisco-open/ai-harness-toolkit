# Angular

Use this file when the repo contains `@angular/*`, `angular.json`, `nx g @nx/angular:*`, or other Angular workspace markers.

## What to Install

Baseline packages usually include:

- `typescript`
- `@angular/core`
- `@angular/cli`
- `eslint`
- `typescript-eslint`
- Angular ESLint packages for lint integration
- test tooling used by the repo such as `jest`, `karma`, or `playwright`

## Required Configuration

- enable strict TypeScript mode
- enable Angular compiler strictness where applicable
- add deterministic lint, test, build, audit, and Semgrep commands
- keep workspace config checked in via `angular.json` or Nx project config

## Skills to Install

Focus this file on Angular-specific additions instead of shared workflow tooling.

Install the official Angular developer skill as the primary Angular companion:

```bash
apm install angular/skills/skills/angular-developer
```

Search for additional Angular-specific review or frontend testing skills in local sources, `ai-harness-toolkit`, and the broader skills ecosystem, then install the selected package with `apm install`.

## Search Terms

Browse curated sources first, then use `npx skills find` with queries such as:

- `angular review`
- `angular testing`
- `frontend testing`
- `security review`

## Framework Markers

- `@angular/core`
- `angular.json`
- `@angular/cli`
- `@nx/angular`
