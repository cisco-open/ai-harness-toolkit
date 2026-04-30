# JavaScript and TypeScript Deterministic Scans

Use repeatable commands that can run locally and in CI without human judgment.

## Package Manager Resolution

Detect the package manager from the repo first. Do not assume a package manager -- use what the repo already has, then wire all scan commands through that tool.

Detection order:

- `packageManager` field in `package.json` -> use the specified manager
- `pnpm-workspace.yaml` or `pnpm-lock.yaml` -> use `pnpm`
- `bun.lockb` or `bun.lock` -> use `bun`
- `yarn.lock` -> use `yarn`
- `package-lock.json` -> use `npm`

Fresh project default when no existing manager is detected: `pnpm`

## Required Packages

- `typescript`
- `eslint`
- `@eslint/js`
- `typescript-eslint`
- `eslint-plugin-sonarjs`
- `eslint-plugin-unused-imports`
- `prettier`
- `husky`
- `lint-staged`
- test runner packages such as `vitest` or `jest`
- workspace tooling such as `nx` when the repo is an Nx workspace

## Required Configuration

- `tsconfig.json` or `tsconfig.base.json` should enable strict type checking
- `eslint.config.*` should include the repo's TypeScript, SonarJS, and unused-import rules
- for Nx repos, include `@nx/enforce-module-boundaries`
- wire `lint`, `type-check`, `test`, `build`, `audit`, and `semgrep` scripts or Nx targets

For fresh projects using `pnpm`, add `"packageManager": "pnpm@..."` to `package.json`. For other package managers, follow that manager's lockfile conventions.

## SonarJS Baseline From This Repo

Mirror these rule settings when building a repo like this one:

- `sonarjs/cognitive-complexity`: error at `15`
- `sonarjs/max-switch-cases`: error at `30`
- `sonarjs/no-commented-code`: warn
- `no-console`: error, allow `warn` and `error`
- `max-lines`: warn at `400`, skip blanks and comments
- `complexity`: warn at `15`
- `max-depth`: warn at `4`
- disable noisy overlap rules already covered elsewhere, such as duplicate-string and unused-import variants

## Required Commands

Substitute `{pm}` with the detected package manager (`pnpm`, `npm`, `bun`, or `yarn`).

For workspaces using Nx, prefer `{pm} nx affected -t <target>` over direct script calls.

| Check | Nx workspace | Non-Nx |
|-------|-------------|--------|
| vulnerability audit | `{pm} audit --audit-level=high` | `{pm} audit --audit-level=high` |
| SAST | `{pm} semgrep` | `{pm} semgrep` |
| lint | `{pm} nx affected -t lint` | `{pm} lint` or `{pm} run lint` |
| type check | `{pm} nx affected -t type-check` | `{pm} exec tsc --noEmit` |
| tests | `{pm} nx affected -t test` | `{pm} test` or `{pm} run test` |
| build | `{pm} nx affected -t build` | `{pm} build` or `{pm} run build` |

**Note on `bun`:** `bun` uses `bun run <script>` for package.json scripts and `bunx` instead of `npx`. The audit command may differ -- check `bun` docs for the current equivalent.

**Note on `npm`:** `npm` uses `npm run <script>` and `npx` for one-off executions. `npm audit` works the same as `pnpm audit`.

## Wiring Rules

- prefer repo-native entrypoints: package.json scripts, Nx targets, or workspace task runner commands
- use the detected package manager consistently across all commands
- expose one documented command path for contributors and CI
- add CI hooks only after the commands pass locally
