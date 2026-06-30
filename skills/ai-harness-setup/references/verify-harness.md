# Verify the Harness

Use this file to run the mandatory verification audit after steps 1-9 are complete and all changes have been staged or committed.

Its purpose is to audit every file the harness added or modified against the harness instructions themselves, catch anything the earlier steps missed or got wrong, and fix every gap before finishing.

## 1. Collect the changeset

Run `git status`, identify the branch point or initial commit from before the harness started as `<base>`, then collect the full changeset with `git diff --name-only <base>..HEAD` for committed changes and `git diff --name-only --cached` for staged but uncommitted changes. Combine and deduplicate those file lists so the changeset fully and reproducibly covers every file the harness created or modified. This changeset is the input for every check below.

## 2. Walk the harness steps against the changeset

Re-read steps 1-9 and the reference files they point to. For each step, verify the changeset satisfies the step's requirements. The checks below are organized by step.

**Step 1 — Repo inspection:**
- Verify the detection results were actually used by later steps (e.g., the detected package manager appears in scripts; the detected CI system received new stages; the detected test runner is referenced, not a different one).

**Step 1b — Preflight .gitignore:**
- Verify none of the harness-created paths (`docs/`, spec-driven development directories, `.opencode/`, `.github/skills/`, `.claude/`, `.cursor/`, `.windsurf/`, etc.) are gitignored. Run `git check-ignore` on every harness-created directory.

**Step 2 — APM:**
- `apm.yml` and `apm.lock.yaml` exist in the changeset.
- `apm_modules/` is in `.gitignore`.
- Deployed files in `.github/` and `.claude/` (if applicable) are in the changeset (not gitignored).

**Step 3 — Spec-driven development:**
- If an existing system was detected (SpecKit, BMAD, etc.), verify it was preserved and not overwritten by OpenSpec. Verify the existing system is documented in `CONTRIBUTING.md` and `AGENTS.md`.
- If OpenSpec was installed, verify `openspec/changes/` and `openspec/specs/` directories exist (with `.gitkeep` if empty), and that OpenCode commands or skill wrappers exist if the repo uses OpenCode.
- `CONTRIBUTING.md` and `AGENTS.md` reference whichever spec-driven development system the repo uses.

**Step 4 — Deterministic checks:**
- Identify the configured enforcement mode first (`enforced` or `advisory`) by inspecting the generated scripts, tool configs, CI steps, and hook commands.
- For every check category in the baseline (lint, type-check, test, build, security/SAST, dependency audit), verify:
  - A script, task, or command entry point exists in the repo (e.g., `package.json` script, Makefile target, Gradle task).
  - If the matching stack reference says a tool is REQUIRED (e.g., `eslint-plugin-unused-imports`, `eslint-plugin-sonarjs`, Husky, Semgrep), verify it is actually installed — present in `package.json` dependencies or the equivalent manifest, not just documented.
  - Config files for each tool exist (e.g., `eslint.config.*`, `tsconfig.json`, `ruff.toml`, `semgrep.yml`, or equivalent).
  - The config does not contradict other harness-generated files. For example, if a linter rule is mentioned as mandatory in `copilot-instructions.md` or `AGENTS.md`, the actual linter config must enable it.
- Apply the right pass criteria for the detected enforcement mode:
  - `enforced`: verify checks are configured to fail on findings or command failures.
  - `advisory`: verify checks are configured to run and surface output without blocking, using the documented no-fail flags or CI wrappers.
- **Dependency audit verification:** Verify that a dependency audit command exists as an executable script or task in the repo (e.g., `npm audit --audit-level=high`, `pnpm audit`, `pip-audit`, `mvn org.owasp:dependency-check-maven:check`), that it is included in the unified local validation command, and that it has a corresponding CI stage or step. A missing dependency audit command is a verification failure that must be fixed before the harness is considered complete.
- A unified local validation command exists (e.g., `npm run validate`, `make check`, `uv run validate`) and it covers lint, type-check, test, build, security scan, and audit.
- CI wiring: every local deterministic check has a corresponding stage or step in the CI config file. Open the CI config from the changeset and confirm 1:1 coverage.
- Git hooks: if the stack reference recommends hooks (e.g., Husky + lint-staged for JS/TS), verify the hook tooling is installed and configured, not just documented.
- Enforcement mode consistency: verify the same mode is expressed across local scripts, CI steps, and git hooks. For example, advisory-mode local scripts should not be paired with enforced CI stages or blocking hook commands.

**Step 5 — Dependabot configuration:**
- If `.github/dependabot.yml` or `.github/dependabot.yaml` already existed before the harness ran, verify no duplicate was created and the existing file was left untouched.
- If neither file existed, verify `.github/dependabot.yml` is now present in the changeset.
- Verify every `package-ecosystem` entry maps to a package manager or manifest actually detected in Step 1. No ecosystem entries should exist for stacks not present in the repo.
- Verify each entry uses `schedule.interval: "weekly"` and `open-pull-requests-limit: 5` unless the repository context explicitly required different values.
- Verify no unnecessary keys (`day`, `time`, `timezone`, `registries`, `target-branch`, `groups`, `ignore`, `allow`) are present unless the repository context explicitly required them.
- For monorepos, verify each workspace subdirectory with its own manifest has a separate `updates` entry with the correct `directory` path.

**Step 6 — AI tooling and skills:**
- `apm deps list` output matches the skills that should have been installed for the detected stack.
- No skills were installed that do not match the detected stack.
- Deployed skill files in `.github/`, `.claude/`, `.opencode/skills/` are present in the changeset.

**Step 7 — Documentation:**
- Cross-reference the seed structure from `references/docs-bootstrap.md` against the changeset. For every file the seed structure says should exist (given the repo's characteristics), verify it was created.
- Open each generated doc and verify:
  - It contains repo-specific content (real commands, real paths, real service names), not generic placeholders.
  - Commands and tool names are consistent with the detection results from step 1 (e.g., if the repo uses Vitest, no doc should reference Jest or Karma).
  - The unified validation command documented in `docs/validation/local-validation-workflow.md` matches the actual script in the manifest.
- `AGENTS.md` routes to `docs/`, includes a repo map/directory structure section near the top that is derived from the Step 1 detection results and rendered to depth 2, and does not inline content that belongs in focused docs.
- `CONTRIBUTING.md` references the docs tree, the spec-driven development workflow, and the validation command.

**Step 8 — AI IDE Configuration:**
- Verify at least GitHub Copilot (`.github/copilot-instructions.md`) is configured. Verify every other IDE the team uses also has config present in the changeset.
- For each configured IDE, verify the config covers all four required areas: (a) validation and build commands, (b) coding conventions and constraints, (c) routing to docs/specs/skills, (d) safety boundaries. If any area is missing, flag it.
- Verify all IDE configs are consistent with each other and with the docs from Step 7 — same tool names, same framework references, same test runner, same validation command, same safety boundaries.
- Verify workflow commands (spec-driven development commands, validation triggers, review commands) are registered in every configured IDE's command surface, not just one.
- If MCP servers were added (via APM), verify they match the detected stack. If no MCP servers are applicable, confirm none were added.
- If OpenCode is configured, verify `opencode.jsonc` contains the required plugin packages, permission rules, and that `.opencode/package.json` exists with resolvable dependencies. Verify JSONC files are syntactically valid.

**Step 9 — APM finalization:**
- `apm install` was the last APM command run (lockfile is up to date).
- All deployed files are staged/committed alongside `apm.yml` and `apm.lock.yaml`.
- CI drift check for APM is wired into the CI config.

## 3. Cross-file consistency check

Scan all generated and modified files for internal contradictions:
- The unified validation command must appear identically in: the manifest script, `docs/validation/local-validation-workflow.md`, `AGENTS.md`, `CONTRIBUTING.md`, and every AI IDE config file (`.github/copilot-instructions.md`, `.cursor/rules/`, `.windsurf/rules/`, `CLAUDE.md`, `opencode.jsonc` — whichever were created).
- Safety boundaries stated in one IDE config must not contradict those in another.
- Any tool listed as mandatory in one generated file must actually be installed and configured, not just mentioned.
- The enforcement mode must be internally consistent across tool configs, local validation scripts, CI steps, and git hooks. Advisory signals such as `--exit-zero`, `|| true`, `continue-on-error: true`, `catchError(...)`, or non-failing Maven plugin flags should either appear together or not at all, based on the chosen mode.

## 4. Fix gaps

For every gap or contradiction found in steps 2-3:
1. Fix it immediately — install the missing package, add the missing CI stage, correct the inconsistent reference, create the missing doc.
2. Log what was fixed.

## 5. Produce the verify report

After all fixes are applied, output a summary with these sections:

1. **Changeset stats** — number of files created, modified, and deleted.
2. **Per-step verification results** — for each step (1-9), state PASS or list what was fixed.
3. **Consistency check results** — any cross-file contradictions found and fixed.
4. **Unresolvable items** — anything that requires human action (secrets, permissions, access grants, large refactors) with the specific action needed.
5. **Final state** — the list of deterministic check commands available, the unified validation command, and the CI stages that mirror them.
6. **Enforcement mode** — whether the harness is configured as enforced or advisory, plus the specific signals that proved it during verification.
