# Deterministic Checks Core

Use this file for the language-agnostic validation layer that should exist before stack-specific checks.

## Core Principle

Prefer repeatable commands that can run locally and in CI without human judgment.

## Progressive Enforcement

Before configuring deterministic checks, ask one binary question: do you want deterministic checks `enforced` or `advisory`?

- `enforced` keeps the current behavior: checks exit non-zero on failures and block commits or CI
- `advisory` keeps the same checks wired in, but they surface findings without blocking local workflows, hooks, or CI
- apply the chosen mode uniformly across all deterministic checks; do not mix enforced lint with advisory audit inside the harness defaults

This mode selection applies to local scripts, CI wiring, and git hooks together. The harness should install the full tooling surface either way. The only change is whether findings fail the workflow.

## Minimum Cross-Repo Baseline

Every repo should define a documented path for:

- dependency or vulnerability audit
- SAST or semantic security scanning
- tests
- build, package, or release verification
- one unified local validation command
- one CI path that mirrors the same checks

If the language supports linting or type checking, add those too, but keep this file focused on the baseline that applies across stacks.

## Wiring Rules

- prefer checked-in scripts, workspace tasks, or `make` targets over tribal-knowledge commands
- run the same checks locally before enforcing them in CI
- document tool installation when the check requires extra binaries
- keep the check names stable so future docs and skills can reference them reliably
- match every local check with a corresponding CI stage or step (see `references/ci-wiring.md` for patterns)

## Typical Shared Tools

- Semgrep or equivalent SAST
- dependency audit tooling
- CI workflow for pull-request validation
- git hooks when the repo uses them

## Local Validation Entry Path

Every repo should have a documented local validation entry path before deeper AI workflow automation is considered complete.

Set up the validation path in this order:

1. define the deterministic checks the repo must run before commit and push
2. expose them through one canonical command or task entry point
3. wire local hooks only after the commands pass reliably
4. make CI enforce the same core checks (see `references/ci-wiring.md`)

At minimum, the validation path should cover:

- linting when the stack supports it
- tests
- build or packaging verification
- security scanning or SAST
- dependency or vulnerability audit when practical

If the repo also uses git hooks, document which checks run at commit time versus push time.

## Monorepo Considerations

When the repo is a monorepo (detected in step 1 of the main workflow):

- determine whether checks should run at the workspace root, per-package, or both
- use workspace-aware commands when available (e.g., `pnpm nx affected`, `uv run` with workspace targeting, Gradle multi-project tasks)
- document the selective testing strategy if the repo has one (e.g., change detection scripts, `nx affected`, Gradle's changed-module detection)
- ensure coverage configuration accounts for multiple packages and their path mappings
- verify that build checks cover all packages, not just the root

## CI Wiring

Every deterministic check added locally should have a corresponding entry in the repo's CI system. See `references/ci-wiring.md` for concrete patterns for Jenkins and GitHub Actions.

Key principles:

- detect the CI system during the repo inspection phase (step 1)
- match local checks 1:1 with CI stages or steps
- reuse existing CI scripts and shared libraries when present
- keep the enforcement mode consistent between local commands, hooks, and CI steps
- document any checks that cannot be wired into CI immediately as explicit follow-up work

## Upgrade Path: Advisory to Enforced

Advisory mode is meant to help existing repos adopt the full check surface without blocking on day one. Upgrading to enforced mode should be a config-only change, not a rewiring project.

- JS/TS ESLint: change harness-added rules from `warn` back to `error`
- JS/TS hooks, audit, and Semgrep: remove the `|| true` suffixes from the generated commands
- Python ruff: remove `--exit-zero`
- Python bandit: remove `--exit-zero`
- Python audit and newly introduced type-checkers: remove `|| true`
- Java checkstyle: set `<failOnViolation>true</failOnViolation>`
- Java SpotBugs: set `<failOnError>true</failOnError>`
- Java OWASP dependency-check: lower `<failBuildOnCVSS>` from `11` to the repo's intended threshold
- GitHub Actions: remove `continue-on-error: true` from deterministic check steps
- Jenkins: remove `catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE')` wrappers around deterministic check stages

After flipping these settings, the same local entry point, CI stages, and hooks should remain in place; only their pass/fail behavior changes.

## Verification

- the repo has a documented deterministic validation path
- CI runs the same core checks as local development
- security scanning is not only advisory prose; it has an executable command
- local validation setup is documented and points to executable local checks
- the repo MUST have a single unified validation command that runs all deterministic checks in one invocation
- for monorepos: checks cover all packages appropriately (workspace-wide or per-package as needed)
