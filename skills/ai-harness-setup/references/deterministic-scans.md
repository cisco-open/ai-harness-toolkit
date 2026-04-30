# Deterministic Scans

Use repeatable local commands that can run in CI without human judgment.

## Cross-Stack Baseline

Every repo should have deterministic commands for:

- dependency or vulnerability audit
- static analysis or SAST
- linting
- type or compile validation when the language supports it
- tests
- build or packaging verification

Prefer repo-native entrypoints such as `pnpm` scripts, `make` targets, checked-in shell scripts, or the repo's primary build tool.

## Stack Guides

Read the per-stack scan guide that matches the repo:

- JavaScript and TypeScript: `references/stacks/javascript-typescript/deterministic-scans.md`
- Python: `references/stacks/python/deterministic-scans.md`
- Java: `references/stacks/java/deterministic-scans.md`

## Build-Gating Policy

Before wiring any new scan into CI, ask the user whether scans added by this skill should gate builds (fail the pipeline on findings) or run as advisory only (report findings without blocking). Apply the user's choice to all scans this skill adds. Either way, the repo's **pre-existing** checks must retain their current gating behavior -- do not weaken those.

## Wiring Rules

- expose the scans through one documented command path
- reuse existing scripts if the repo already has them
- add CI hooks only after the commands pass locally
- document any required tool bootstrap steps next to the commands that use them
