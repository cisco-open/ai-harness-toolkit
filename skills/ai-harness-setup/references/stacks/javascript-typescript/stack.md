# JavaScript and TypeScript

Read this file for Node.js, browser, React, Next.js, Vite, or Nx repositories.

## Repo Markers

Common markers:

- `package.json`
- `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`
- `tsconfig.json`
- `nx.json`, `turbo.json`, `vite.config.*`, `next.config.*`

## Detection First

Before recommending or installing any tooling, detect what the repo already uses:

- **Package manager**: check for `packageManager` field in `package.json`, lockfiles (`pnpm-lock.yaml`, `bun.lockb`, `yarn.lock`, `package-lock.json`), or workspace config files. Use the detected manager for all commands.
- **Workspace tooling**: check for `nx.json`, `turbo.json`, `pnpm-workspace.yaml`, or Lerna config. Use workspace-aware commands when present.
- **Test runner**: check for `vitest.config.*`, `jest.config.*`, `playwright.config.*`, or test script definitions in `package.json`.
- **Monorepo layout**: check for workspace files, multiple `package.json` files, or project-level configs.

See `references/stacks/javascript-typescript/deterministic-scans.md` for detailed package manager detection order.

Fresh project default when no existing manager is detected: `pnpm`

## Skill Search Terms

Review repo-local skills and the `ai-harness-toolkit` skill inventory first, then use `npx skills find` (or `bunx skills find` for bun repos) only when broader discovery is still needed. Install selected skills with `apm install`.

Useful discovery queries include:

- `react review`
- `nextjs performance`
- `langgraph`
- `copilotkit`
- `nx workspace`
- `frontend testing`
- `security review`

Install only the skills that fill real gaps in the repo's current inventory.

## Skills to Install

Install these companion skills for TypeScript/JavaScript code-review support:

```bash
apm install github/awesome-copilot/skills/security-review
```

Security review is cross-cutting and applies to all TypeScript/JavaScript projects regardless of framework.

## Recommended Deterministic Baseline

- package install and lockfile check
- ESLint
- TypeScript type checking
- Vitest, Jest, Playwright, or the repo's chosen test runner
- Semgrep
- dependency audit
- build verification through the workspace task runner

## Fresh Project Setup

For a fresh project with no existing tooling, use `pnpm`.

Install the baseline packages:

```bash
pnpm add -D typescript eslint @eslint/js typescript-eslint eslint-plugin-sonarjs eslint-plugin-unused-imports prettier husky lint-staged semgrep
```

Add a test runner that matches the app type, such as `vitest`, `jest`, or `playwright`.

Required setup:

- add `"packageManager": "pnpm@<version>"` to `package.json`
- enable `"strict": true` in `tsconfig.json` or `tsconfig.base.json`
- create `eslint.config.*` with TypeScript, SonarJS, and unused-imports rules
- add scripts or Nx targets for `lint`, `type-check`, `test`, `build`, `audit`, and `semgrep`
- if the repo uses Nx, include `@nx/enforce-module-boundaries`

Use the SonarJS defaults documented in `references/stacks/javascript-typescript/deterministic-scans.md` when you want that lint posture.

For existing projects using `npm`, `bun`, or `yarn`, adapt the install command and script wiring to use that package manager instead. Do not switch the repo's package manager.

## Repo Patterns to Prefer

- wire scans through `package.json` scripts or workspace targets
- prefer `nx run`, `nx affected`, or equivalent workspace orchestration when present
- use the detected package manager consistently across all commands
- keep AI framework setup documented in `docs/dev-environment/` or `docs/conventions/`

## Local Validation and Hooks

For JavaScript and TypeScript repos, set up local validation through the workspace task runner and package scripts.

Recommended flow:

1. define canonical scripts or Nx targets for lint, type-check, test, build, audit, and Semgrep
2. document one canonical validation command or task entry point
3. wire git hooks with the package manager's normal tooling such as Husky or lefthook
4. keep staged-file autofix tasks small, but run affected-project validation for typecheck, tests, and build where possible

Typical hook split:

- commit-time hooks: ESLint, Prettier, lightweight staged-file validation
- push-time hooks: affected type-check, test, build, coverage, Semgrep, audit as appropriate

## Extra Stack Discovery

Search for more stack signals beyond top-level manifests:

- `next.config.*`, `vite.config.*`, `vitest.config.*`, `playwright.config.*`
- `electron*`, `tauri.conf.json`, `turbo.json`, `jest.config.*`
- dependencies such as `react`, `next`, `vite`, `electron`, `@langchain/*`, `@copilotkit/*`

## Framework-Specific References

- Use `references/stacks/javascript-typescript/framework-react.md` for React and Next.js repos.
- Use `references/stacks/javascript-typescript/framework-angular.md` for Angular repos.
