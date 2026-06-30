# Angular

Use this file when the repo contains `@angular/*`, `angular.json`, `nx g @nx/angular:*`, or other Angular workspace markers.

## What to Install

Baseline packages usually include:
- `typescript`
- `@angular/core`
- `@angular/cli`
- `typescript-eslint`
- Angular ESLint packages for lint integration
- test tooling used by the repo such as `jest`, `karma`, or `playwright`

## Required Configuration

- enable strict TypeScript mode
- enable Angular compiler strictness where applicable
- add deterministic lint, test, build, audit, and Semgrep commands
- keep workspace configuration checked in via `angular.json` or Nx project configuration

## Skills to Install

Focus this file on Angular-specific additions instead of shared workflow tooling.

Install the `stack-angular` package as the primary Angular companion:

```bash
apm install --target <ide-1> --target <ide-2> --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/stack-angular#stack-angular-v<latest>
```

This package covers `angular-developer`, `web-design-guidelines`, the transitive `stack-javascript-typescript`, and `core`, plus the Chrome DevTools MCP server.

Search for additional Angular-specific review or frontend testing skills in repo-local, public curated, and broader skills sources only when the package does not cover the repo's needs, then install the selected package with `apm install`.

Treat the package as the default baseline, then add only the dynamic Angular or frontend skills that close real repo-specific gaps.

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
