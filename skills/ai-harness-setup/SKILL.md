---
name: ai-harness-setup
description: Build a step-by-step path from a plain repository to a full agent-driven engineering workflow. Inspects the repo first to detect the full tech stack, package managers, CI systems, and monorepo layout before making any changes. Then initializes APM, sets up spec-driven development (OpenSpec by default, or respects existing systems like SpecKit and BMAD), adds deterministic checks matched to the detected stack, installs applicable AI skills, creates workflow documentation, configures AI IDEs (Copilot, Cursor, Windsurf, Claude Code, OpenCode), and verifies the entire setup.
compatibility: NodeJS, APM or permission to install it, and access to the target repository
metadata:
  version: "3.1"
---

# AI Harness Setup

Use this skill to bootstrap a repository toward a durable agent-driven workflow: deep inspection first, then APM as the dependency and skill delivery layer, spec-driven development for change management (OpenSpec by default, or the repo's existing system), deterministic checks matched to the detected stack, AI skills for review and delivery, a docs tree that explains the whole system, and AI IDE configuration for every IDE the team uses.

## Quick Start

1. **Inspect first.** Search the repo's manifests, lockfiles, CI configs, framework configs, and existing docs to classify the full stack before changing anything. Record: languages, package managers, type checkers, test runners, linters, CI system, monorepo layout, and existing tooling.
2. Read the matching stack guide based on detection results:
   - `references/stacks/javascript-typescript/stack.md`
   - `references/stacks/python/stack.md`
   - `references/stacks/java/stack.md`
3. If the repo uses a major framework, also read the matching framework guide:
   - `references/stacks/javascript-typescript/framework-react.md`
   - `references/stacks/javascript-typescript/framework-angular.md`
   - `references/stacks/java/framework-spring-boot.md`
4. Ask whether the team wants GitHub Agentic Workflows enabled in this repository.
5. Ask whether deterministic checks should be `enforced` or `advisory` before configuring any checks. Carry that answer through all downstream local scripts, CI wiring, and git hooks.
6. If GitHub Agentic Workflows are enabled, read `references/github-agentic-workflows.md` before installing AI workflow tooling.
7. Read `references/ai-tooling.md` before initializing APM or installing package-backed skills.
8. Read `references/mcp-servers.md` before adding extra MCP servers to `apm.yml`.
9. Read `references/openspec.md` for change management setup.
10. Read `references/deterministic-checks-core.md` and the matching per-stack `deterministic-scans.md` together -- they form one phase.
11. Read `references/dependabot.md` when adding Dependabot configuration.
12. Read `references/docs-bootstrap.md` when creating the docs section that explains the workflow.
13. Read `references/opencode.md` when OpenCode or `ocx` support is requested.
14. **Verify is mandatory.** After all setup steps finish, run the Verify step in Workflow Step 10 to audit the changeset against the harness instructions, fix every gap found, and produce a verify report. Never skip this step.

For non-trivial setup work, use subagents to split independent exploration or authoring tasks across stack, tooling, validation, and documentation domains, then merge the results in one final coordinating pass.

## Workflow

### 1. Inspect the Repo and Detect the Full Stack

Run this step before making any changes. The results drive every decision in later steps.

- Search manifests, lockfiles, CI configs, framework configs, dependency declarations, and existing docs.
- Do not stop at top-level markers. Search deeply for framework configs, nested package files, and CI pipeline definitions.
- Ask early whether the team wants GitHub Agentic Workflows enabled and whether deterministic checks should be enforced or advisory so the setup path can either include or skip that layer intentionally and wire checks correctly.
- **Detect and record:**
  - Languages and their versions
  - Package managers (npm, pnpm, bun, yarn, uv, poetry, pip, Maven, Gradle)
  - Type checkers already in use (TypeScript, mypy, basedpyright, pyright, pytype)
  - Linters already in use (ESLint, ruff, checkstyle, spotbugs)
  - Test runners (vitest, jest, pytest, junit, playwright)
  - Security scanners already present (bandit, Semgrep, npm audit, pip-audit, OWASP dependency-check)
  - CI system (Jenkins, GitHub Actions, GitLab CI) and its config files
  - Monorepo layout (uv workspaces, pnpm workspaces, Nx, Turborepo, Gradle multi-module, Maven multi-module)
  - Frameworks (React, Next.js, Angular, FastAPI, LangGraph, Spring Boot, etc.)
  - Existing docs, AGENTS.md, CONTRIBUTING.md
  - Existing skills, spec-driven development artifacts (OpenSpec `openspec/`, SpecKit `specify/` or `specs/`, BMAD, or other structured planning systems)
  - AI IDE configs already present: Cursor (`.cursor/`, `.cursorrules`), GitHub Copilot (`.github/copilot-instructions.md`, `.github/copilot-*`), Windsurf (`.windsurf/`, `.windsurfrules`), Claude Code (`.claude/`, `CLAUDE.md`), OpenCode (`opencode.jsonc`, `.opencode/`)
  - MCP surfaces and automation entry points
- Record all findings. This detection output drives steps 2-10.

**Monorepo detection:** If the repo is a monorepo (workspace files, multiple packages, shared build tooling), note the workspace layout, which packages have their own tooling configs, and whether checks should run at workspace level vs. per-package level. Adapt all later steps accordingly.

- Look for frameworks and tools such as React, Next.js, Vite, Electron, LangChain, LangGraph, CopilotKit, FastAPI, Hono, Axum, Tauri, Playwright, Docker, Jenkins, and GitHub Actions.
- When a framework is detected, load its framework-specific reference for use during the deterministic checks and skills phases.

### 1b. Preflight: Check `.gitignore` for Path Conflicts

Before creating any directories or files, verify that the paths this workflow will generate are not ignored by `.gitignore`:

```bash
git check-ignore docs/ openspec/ .opencode/ .opencode/skills/ .github/skills/ .github/prompts/ .github/instructions/ .github/agents/ .github/hooks/ .claude/ .claude/skills/
```

If any of these paths are listed in `.gitignore`, warn the user and resolve the conflict before proceeding. Content created under ignored paths will not appear in `git status` and will silently fail to commit.

**APM deployed files should be committed.** Files that APM places in `.github/` (prompts, skills, instructions, agents, hooks) and `.claude/` are intended to be version-controlled so that every contributor and Copilot on github.com gets agent context without running `apm install`. Only `apm_modules/` should be gitignored (APM handles this automatically).

To catch drift between `apm.yml` and deployed files, use a CI drift check rather than gitignore. See `references/ai-tooling.md` for the drift check pattern.

### 2. Initialize APM

- Treat APM as the dependency and delivery foundation for skills, prompts, and related agent packages.
- Detect whether the repo already has `apm.yml`, `apm.lock.yaml`, `apm_modules/`, or APM-managed `.github/skills/`, `.claude/skills/`, `.cursor/skills/`, or `.opencode/skills/` directories.
- If `apm.yml` does not exist, initialize it before installing skills:
  - run `apm --version`
  - run `apm init --yes` from the repo root
- If `apm.yml` already exists, inspect it before adding dependencies, then use `apm install` to sync the current dependency graph when needed.
- Verify `apm_modules/` is in `.gitignore` (`apm init` should add it automatically; if not, add it manually).
- Use imperative `apm install <package>` commands for skill installation so the manifest and lockfile stay aligned with the actual installed set.
- Use `references/ai-tooling.md` for initialization, install order, discovery strategy, and verification.

### 3. Set Up Spec-Driven Development

Ensure the repo has a spec-driven development system for managing non-trivial changes. Use the detection results from Step 1 to determine what already exists.

**If a spec-driven development system already exists** (SpecKit via `specify/` or `specs/`, BMAD, or any structured planning system with real artifacts):
- Respect it. DO NOT replace it with OpenSpec.
- Document the existing system in the docs tree (Step 7), `CONTRIBUTING.md`, and `AGENTS.md`.
- Wire its workflow commands into the AI IDE configs (Step 8) if it has a CLI or command surface.
- If the system has no CLI or command surface, document the manual workflow contributors should follow.

**If no spec-driven development system exists:**
- Install OpenSpec as the default.
- Use `references/openspec.md` for the install sequence, `openspec init`, command surfacing, and verification flow.
- Confirm `openspec/changes/` and `openspec/specs/` exist after initialization (with `.gitkeep` if empty).
- Add OpenSpec workflow commands to the AI IDE command surfaces (Step 8).

### 4. Add Deterministic Checks

Combine the language-agnostic baseline with stack-specific checks in a single pass, informed by the detection results from step 1.

Before configuring any deterministic checks, ask: "Do you want deterministic checks enforced or advisory?" Apply that one answer uniformly to all deterministic checks, CI steps, and git hooks that this workflow wires in.

**Language-agnostic baseline** (use `references/deterministic-checks-core.md`):
- dependency or vulnerability audit
- SAST or Semgrep-style scanning
- tests
- build or packaging verification
- CI parity with local commands

**Stack-specific checks** (use `references/deterministic-scans.md` as the overview, then the matching per-stack file):
- Read the core baseline first, then the stack-specific guide, then act once.
- Use the package manager, type checker, linter, and test runner **detected in step 1**. Do not override existing tooling with defaults.
- If the repo already has a tool fulfilling a check category (e.g., `basedpyright` for type checking), use it instead of recommending the default.
- Keep per-language commands and setup instructions in separate reference files instead of bloating the main workflow.

**Monorepo considerations:**
- Determine whether checks run at the workspace root or per-package.
- Use workspace-aware commands when available (e.g., `pnpm nx affected -t lint`, `uv run` with workspace targeting).
- Document selective testing strategy if the repo has one (e.g., change detection scripts).

**CI wiring:**
- Match every deterministic check added locally with a corresponding CI stage or step.
- Detect the CI system from step 1 and wire checks into the appropriate config format.
- For Jenkins repos, add checks as stages in the Jenkinsfile or as calls to existing shared library functions. See `references/ci-wiring.md` for patterns.
- For GitHub Actions repos, add checks as workflow steps.
- Reuse existing CI scripts if the repo already encodes the right invariant.

### 5. Add Dependabot Configuration

Ensure the repo has a Dependabot configuration for automated dependency updates based on the ecosystems detected in Step 1.

- Use `references/dependabot.md` for the guard-rails, ecosystem mapping, defaults, and monorepo handling.
- If `.github/dependabot.yml` or `.github/dependabot.yaml` already exists, leave it untouched.
- If neither exists, create `.github/dependabot.yml` with entries for each detected ecosystem.

### 6. Install AI Tooling and Skills

- Ask whether GitHub Agentic Workflows should be enabled before changing AI tooling.
- If the answer is yes, use `references/github-agentic-workflows.md` as the source of truth for `gh aw` installation, workflow import, generated files, and post-install token guidance.
- If the answer is no, skip `gh aw` setup entirely.

Use a package-first install flow. The curated APM packages are the default delivery path for skills and any MCP servers they already bundle.

- Start with `apm --version`.
- Audit repo-local skill directories and existing APM dependencies before installing duplicates.
- Initialize APM first if the repo does not already have `apm.yml`.
- Resolve the latest published package tag at install time. Use `git ls-remote --tags https://github.com/cisco-open/ai-harness-toolkit "<name>-v*"`, sort the returned tags by semver, and install the newest matching tag. Do not hardcode package versions in this skill.
- Use the detected IDE targets in every package install command and include protocol fallback:

```bash
apm install --target <ide-1> --target <ide-2> --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/<name>#<name>-v<latest>
```

- Choose the default package from the detection results in step 1:

| Detected stack | Install |
| --- | --- |
| JavaScript/TypeScript, no framework | `stack-javascript-typescript` |
| Vue, Svelte, or other generic web UI | `stack-frontend` |
| React or Next.js | `stack-react` |
| Angular | `stack-angular` |
| Python managed with `uv` | `stack-python-uv` |
| Java with Spring Boot | `stack-spring-boot` |
- Every `stack-*` package already pulls `core` transitively. Do not install `core` separately when a stack package matches.
- If no stack package matches (for example Go, Rust, plain Java, or another unpackaged backend), install `core` explicitly and then add only the extra dynamic skills that the detected stack still needs.
- Use `references/ai-tooling.md` for the install mechanics, what-to-commit rules, and dynamic fallback workflow.

**Dynamic fallback and add-ons:**
- Use the matching package as the default baseline when one exists, then add only the extra dynamic skills that cover real repo-specific gaps.
- Browse repo-local and public curated sources first for Cisco-curated skills that match the detected stack.
- Use `npx skills find <query>` only as a search mechanism when the needed skill is not already available through repo-local or public curated sources.
- If no package matches (for example FastAPI, Django, plain Java, Go, Rust, LangGraph, or CopilotKit), keep that part of the stack dynamic.

### 6b. Add MCP Servers

Add MCP servers to `apm.yml` based on the detected tech stack. MCP servers give agents runtime access to external tools and services.

- Read `references/mcp-servers.md` for the package-backed defaults, discovery workflow, and APM dependency format.
- Inspect the repo for existing MCP declarations in `opencode.jsonc`, `.opencode/`, Cursor, Claude, and similar config files, then migrate those definitions into `apm.yml` so APM becomes the single source of truth.
- Treat package-provided MCP servers as already handled by the corresponding package install:
  - `stack-frontend`, `stack-react`, and `stack-angular` provide Chrome DevTools.
- Treat those package-provided MCP servers as the baseline, not the ceiling. Add extra MCP servers when the detected stack still justifies them.
- Use `apm mcp search <term>` only for extra servers not covered by a package, such as Cisco Design System, Postgres, Playwright, Sentry, Kubernetes, or Terraform. Only add servers that provide clear value for the repo's actual workflow.
- All MCP servers are declared in the `dependencies.mcp` section of `apm.yml` and installed through `apm install`.
- Preserve any existing MCP entries in `apm.yml` and carry forward any repo-local MCP config that should remain supported.

### 7. Create the Docs Section That Explains the Workflow

**Synthesis checkpoint:** Before writing docs, consolidate all findings from steps 1-6. The docs must accurately reflect everything that was detected, installed, and configured.

- **Verify `docs/` is not gitignored.** Run `git check-ignore docs/` before creating any files. If `docs/` is ignored, update `.gitignore` first -- otherwise the entire docs tree will be invisible to git.
- **Research deeply before writing.** Read source code, configs, CI pipelines, deployment configs, data models, API definitions, and integration points. Every doc should contain material that could only come from actually reading this repo.
- Use `references/docs-bootstrap.md` for the full seed structure, research checklist, and authoring order.
- Create architecture docs first (system overview, services, data model, integrations) because they require the deepest research and inform everything else.
- Create dev environment docs with real commands (setup, run, env vars).
- Create validation docs that reference the deterministic checks wired in step 4.
- Create deployment docs if the repo ships to production.
- Write the workflow overview last -- it synthesizes all other docs.
- Create `AGENTS.md` as a **lean routing file** that points agents to `docs/`. Do not dump content into `AGENTS.md` that belongs in focused docs.
- Update `CONTRIBUTING.md` to reference the docs tree.
- Every doc must contain real content derived from the repo. No empty scaffolds or placeholder text.

### 8. Configure OpenCode and ocx When Present

- If the repo uses OpenCode, merge config instead of replacing it.
- Use `references/opencode.md` for the file-level config, plugin, command, and verification details.
- For repos that also use Cursor or GitHub Copilot, install reusable skills with `apm install <package> -t opencode -t cursor -t copilot` and let the CLI materialize the repo-local layout.
- Ensure the repo's OpenCode layer includes the required plugin packages and permission rules.
- Add MCP server entries only when they match the detected stack. See `references/mcp-servers.md` for the baseline and discovery workflow, and `references/opencode.md` for OpenCode-specific MCP config.

### 9. Finalize APM State and Commit Deployed Files

After all skills are installed and configuration is complete:

1. Run `apm install` to ensure `apm_modules/`, the lockfile, and all deployed files are fully in sync with `apm.yml`.
2. Verify `apm_modules/` is in `.gitignore`.
3. Stage and commit together:
   - `apm.yml`
   - `apm.lock.yaml`
   - All deployed files in `.github/` (skills, prompts, instructions, agents, hooks)
   - All deployed files in `.claude/` (if present)
   - All deployed files in `.opencode/skills/` (if present)
4. These files are version-controlled so every contributor and Copilot on github.com gets agent context without running `apm install`.

### 10. Verify the Harness

This step is mandatory. Run it only after steps 1-9 are complete and all changes have been staged or committed.

Use `references/verify-harness.md` for the full verification procedure. It covers:

1. Collecting the changeset (committed + staged files)
2. Walking each harness step (1-9) against the changeset to confirm requirements are satisfied
3. Cross-file consistency checks (validation commands, safety boundaries, tool names across all generated files)
4. Fixing gaps immediately rather than logging them as tech debt
5. Producing a structured verify report

## Guardrails

- **Never run deterministic checks.** This skill adds and configures deterministic commands (linters, type checkers, security audits, test runners, SAST tools, dependency audits, builds, scans, etc.) but must never execute them. Running these checks is the responsibility of the developer or CI pipeline, not this setup skill.
- **Detect before prescribing.** Always check what the repo already uses before recommending or installing tooling. Never override an existing tool with a default.
- Keep `apm.yml` and `apm.lock.yaml` aligned with the actual installed packages.
- Never overwrite existing secrets or credential files.
- Never remove user-defined plugin, skill, or MCP entries unless the user asked for cleanup.
- Prefer idempotent edits so the setup can be re-run safely.
- Prefer repo-local commands over globally assumed tooling.
- Document durable workflow rules in `docs/`, not only in the final chat response.
- When installing skills from external sources, install only those applicable to the repo. Do not bulk-install everything from a source.

## Reference Map

- `references/openspec.md` - step-by-step OpenSpec bootstrap
- `references/github-agentic-workflows.md` - optional `gh aw` bootstrap and workflow import guidance
- `references/deterministic-checks-core.md` - language-agnostic deterministic baseline
- `references/deterministic-scans.md` - cross-language deterministic scan overview
- `references/dependabot.md` - Dependabot configuration guard-rails, ecosystem mapping, and defaults
- `references/ai-tooling.md` - APM initialization, package install mechanics, and dynamic fallback workflow
- `references/mcp-servers.md` - package-provided MCP defaults, extra MCP discovery, and APM dependency format
- `references/opencode.md` - OpenCode and ocx config patterns
- `references/docs-bootstrap.md` - how to create the docs section
- `references/verify-harness.md` - full verification procedure for Step 10 (changeset audit, per-step checks, consistency, gap fixing, report)
- `references/ci-wiring.md` - CI integration patterns for Jenkins and GitHub Actions
- `references/stacks/javascript-typescript/stack.md` - JS/TS-specific setup
- `references/stacks/javascript-typescript/deterministic-scans.md` - JS/TS deterministic commands and wiring
- `references/stacks/javascript-typescript/framework-react.md` - React and Next.js setup plus the `stack-react` package
- `references/stacks/javascript-typescript/framework-angular.md` - Angular setup plus the `stack-angular` package
- `references/stacks/python/stack.md` - Python-specific setup plus the `stack-python-uv` package
- `references/stacks/python/deterministic-scans.md` - Python deterministic commands and wiring
- `references/stacks/java/stack.md` - Java-specific setup
- `references/stacks/java/deterministic-scans.md` - Java deterministic commands and wiring
- `references/stacks/java/framework-spring-boot.md` - Spring Boot setup plus the `stack-spring-boot` package
