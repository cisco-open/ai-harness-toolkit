# Detection Signals

This reference defines the filesystem signals, config files, CLI tools, and artifacts to look for when identifying AI-native primitives in a repository. Use it during step 1 of the assessment workflow.

---

## Spec-Driven Development Detection

Detect the spec-driven development system using this priority chain. Stop at the first match.

```
openspec/ exists?
 ├── yes → Score as OpenSpec
 └── no
      specify/ exists?
       ├── yes → Score as SpecKit
       └── no
            specs/ exists? (fallback)
             ├── yes → Score as SpecKit (fallback)
             └── no  → Score 0 (no system detected)
```

### OpenSpec Signals

**Primary signals (any confirms OpenSpec):**

| Signal | What to check |
|--------|--------------|
| `openspec/` directory | Exists at repo root |
| `openspec/changes/` | Subdirectory with change containers |
| `openspec/specs/` | Subdirectory with spec files |

**Secondary signals (strengthen the score):**

| Signal | What to check |
|--------|--------------|
| OpenSpec CLI | `openspec --version` succeeds |
| OpenSpec CLI in deps | `openspec` in `package.json` dependencies or global install |
| Workflow skills | `.opencode/skills/openspec-*/` directories exist |
| Workflow commands | `.opencode/command/opsx-*.md` or `.opencode/commands/opsx-*.md` files exist |
| GitHub prompts | `.github/prompts/opsx-*.prompt.md` files exist |
| CONTRIBUTING.md reference | CONTRIBUTING.md mentions OpenSpec, `openspec`, or `/opsx-` commands |
| AGENTS.md reference | AGENTS.md mentions OpenSpec or points to `openspec/` |

**Maturity signals (differentiate score 2 vs 3 vs 4):**

| Signal | What it indicates |
|--------|------------------|
| Non-empty `openspec/changes/` | Changes have been created (score 2+) |
| Changes with complete artifact chains | Proposals, specs, design, tasks files with real content (score 3+) |
| Archived changes | Evidence of completed workflow cycles (score 4) |
| Recent change timestamps | Active use, not abandoned setup (score 4) |

### SpecKit Signals

**Primary signal:**

| Signal | What to check |
|--------|--------------|
| `specify/` directory | Exists at repo root. This is the unambiguous SpecKit indicator. |

**Fallback signal (only when neither `openspec/` nor `specify/` exists):**

| Signal | What to check |
|--------|--------------|
| `specs/` directory | Exists at repo root. Inspect contents for SpecKit-specific patterns before scoring. Be cautious: `specs/` may contain OpenAPI specs, test specs, or other non-SpecKit content. |

**Maturity signals:**

| Signal | What it indicates |
|--------|------------------|
| Non-empty `specify/` or `specs/` | Specifications have been created (score 2+) |
| Structured spec files with requirements | Active specification work (score 3+) |
| Workflow integration in docs | Referenced in contributor or workflow documentation (score 4) |

---

## AI IDE Configuration Detection

Detect the AI IDE configuration. At least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be configured. If none of these are detected, score Category 5 as 0 (do not mark as N/A).

### Cursor Signals

**Primary signals (any confirms Cursor):**

| Signal | What to check |
|--------|--------------|
| `.cursor/` directory | Exists at repo root |
| `.cursorrules` | Cursor rules file at repo root |
| `.cursor/rules/` | Directory containing Cursor rule files (`.mdc` or `.md`) |

**Secondary signals (strengthen the score):**

| Signal | What to check |
|--------|--------------|
| `.cursor/mcp.json` | MCP server configuration for Cursor |
| `.cursor/rules/*.mdc` | Individual rule files with frontmatter (`description`, `globs`, `alwaysApply`) |
| Cursor references in docs | CONTRIBUTING.md or AGENTS.md mentions Cursor setup |
| `.cursorignore` | Cursor ignore file |

**Config quality signals:**

| Signal | What it indicates |
|--------|------------------|
| `.cursorrules` or `.cursor/rules/` exist with repo-specific content | Beyond defaults (score 2+) |
| Rules reference repo architecture, conventions, and workflows | Tuned to the repo (score 3+) |
| MCP servers configured, multiple rule files for different contexts, rules use `globs` for scoping | Comprehensive setup (score 4) |

### VS Code / Copilot Signals

**Primary signals (any confirms VS Code/Copilot):**

| Signal | What to check |
|--------|--------------|
| `.github/copilot-instructions.md` | Copilot custom instructions file |
| `.github/copilot-*.md` | Any copilot instruction files |
| `.copilotignore` | Copilot ignore file |

**Secondary signals:**

| Signal | What to check |
|--------|--------------|
| Copilot extensions config | Extension definitions in `.github/` |
| Copilot references in docs | CONTRIBUTING.md or AGENTS.md mentions Copilot setup |
| VS Code settings for Copilot | `.vscode/settings.json` with Copilot-related keys |

**Config quality signals:**

| Signal | What it indicates |
|--------|------------------|
| Custom instructions exist with repo-specific content | Beyond defaults (score 2+) |
| Instructions reference repo architecture and conventions | Tuned to the repo (score 3+) |
| Multiple instruction files for different contexts | Comprehensive setup (score 4) |

### Windsurf Signals

**Primary signals (any confirms Windsurf):**

| Signal | What to check |
|--------|--------------|
| `.windsurf/` directory | Exists at repo root |
| `.windsurfrules` | Windsurf rules file at repo root |
| `.windsurf/rules/` | Directory containing Windsurf rule files |

**Secondary signals (strengthen the score):**

| Signal | What to check |
|--------|--------------|
| `.windsurf/mcp.json` | MCP server configuration for Windsurf |
| `.windsurf/rules/*.md` | Individual rule files |
| Windsurf references in docs | CONTRIBUTING.md or AGENTS.md mentions Windsurf setup |
| `.windsurfignore` | Windsurf ignore file |

**Config quality signals:**

| Signal | What it indicates |
|--------|------------------|
| `.windsurfrules` or `.windsurf/rules/` exist with repo-specific content | Beyond defaults (score 2+) |
| Rules reference repo architecture, conventions, and workflows | Tuned to the repo (score 3+) |
| MCP servers configured, multiple rule files for different contexts | Comprehensive setup (score 4) |

### Claude Code Signals

**Primary signals (any confirms Claude Code):**

| Signal | What to check |
|--------|--------------|
| `.claude/` directory | Exists at repo root |
| `CLAUDE.md` | Claude Code instructions file at repo root |
| `.claude/settings.json` | Claude Code settings file |

**Secondary signals (strengthen the score):**

| Signal | What to check |
|--------|--------------|
| `.claude/commands/` | Custom slash command definitions |
| `.claude/mcp.json` | MCP server configuration for Claude Code |
| Claude Code references in docs | CONTRIBUTING.md or AGENTS.md mentions Claude Code setup |
| `.claudeignore` | Claude Code ignore file |

**Config quality signals:**

| Signal | What it indicates |
|--------|------------------|
| `CLAUDE.md` exists with repo-specific content | Beyond defaults (score 2+) |
| Instructions reference repo architecture, conventions, and workflows | Tuned to the repo (score 3+) |
| MCP servers configured, custom commands defined, multiple context files | Comprehensive setup (score 4) |

### OpenCode Signals

**Primary signals (any confirms OpenCode):**

| Signal | What to check |
|--------|--------------|
| `opencode.jsonc` | Exists at repo root |
| `.opencode/` directory | Exists at repo root |

**Secondary signals (strengthen the score):**

| Signal | What to check |
|--------|--------------|
| `.opencode/package.json` | Plugin dependencies defined |
| `.opencode/plugin/` | Repo-local plugin code |
| `.opencode/command/` | Command definitions (`.md` files) |
| `.opencode/commands/` | Alternative command directory |
| `.opencode/skills/` | Repo-local skill definitions |
| `.opencode/ocx.jsonc` | ocx registry configuration |
| `.opencode/worktree.jsonc` | Worktree plugin sync config |

**Config quality signals (differentiate score 2 vs 3 vs 4):**

| Signal | What it indicates |
|--------|------------------|
| Plugins configured in `opencode.jsonc` | Beyond defaults (score 2+) |
| Core plugins present (DCP, plannotator, subtask2) | Standard workflow plugins (score 3+) |
| MCP server entries | Stack-matched integrations (score 3+) |
| Permission policies defined | Security-conscious config (score 4) |
| Provider restrictions defined | Intentional provider management (score 4) |
| `.opencode/package.json` dependencies resolve | Plugins are installable and maintained (score 4) |

---

## Deterministic Checks Detection

Detect the presence and configuration of each deterministic check type.

### Linter Detection

| Signal | Languages |
|--------|-----------|
| `.eslintrc`, `.eslintrc.*`, `eslint.config.*` | JavaScript/TypeScript |
| `ruff.toml`, `pyproject.toml` with `[tool.ruff]` | Python |
| `.flake8`, `setup.cfg` with `[flake8]` | Python |
| `checkstyle.xml`, `pmd.xml` | Java |
| `.prettierrc`, `.prettierrc.*`, `prettier.config.*` | JavaScript/TypeScript (formatting) |
| `.stylelintrc`, `.stylelintrc.*` | CSS |
| `lint` script in `package.json` | JavaScript/TypeScript |
| `lint` target in `Makefile` | Any |
| CI pipeline step named "lint" or running a lint command | Any |

### Type Checker Detection

| Signal | Languages |
|--------|-----------|
| `tsconfig.json`, `tsconfig.*.json` | TypeScript |
| `mypy.ini`, `pyproject.toml` with `[tool.mypy]`, `.mypy.ini` | Python |
| `pyrightconfig.json`, `pyproject.toml` with `[tool.pyright]` | Python |
| `pyproject.toml` with `[tool.basedpyright]` | Python |
| `pyproject.toml` with `[tool.pytype]` | Python |
| Java compiler (`javac`) with strict flags | Java |
| `typecheck` or `type-check` script in `package.json` | JavaScript/TypeScript |
| CI pipeline step running type check commands | Any |

### Test Runner Detection

| Signal | Languages |
|--------|-----------|
| `vitest.config.*`, `vite.config.*` with test config | JavaScript/TypeScript |
| `jest.config.*`, `package.json` with `jest` key | JavaScript/TypeScript |
| `pytest.ini`, `pyproject.toml` with `[tool.pytest]`, `conftest.py` | Python |
| `pom.xml` with surefire/failsafe plugin | Java |
| `build.gradle` with test config | Java |
| `test/`, `tests/`, `__tests__/`, `spec/` directories | Any |
| `test` script in `package.json` | JavaScript/TypeScript |
| `test` target in `Makefile` | Any |
| CI pipeline step named "test" or running test commands | Any |

### SAST / Security Scanning Detection

| Signal | Languages |
|--------|-----------|
| `.semgrep.yml`, `.semgrep/` | Any |
| `semgrep` in dependencies or CI steps | Any |
| `bandit.yaml`, `.bandit`, `pyproject.toml` with `[tool.bandit]` | Python |
| SpotBugs, FindBugs config | Java |
| `security` or `sast` CI pipeline step | Any |
| `security` script in `package.json` or `Makefile` | Any |

### Dependency / Vulnerability Audit Detection

| Signal | Languages |
|--------|-----------|
| `npm audit` or `yarn audit` in scripts or CI | JavaScript/TypeScript |
| `pip-audit` in dependencies or CI | Python |
| `safety` in dependencies or CI | Python |
| OWASP dependency-check config | Java |
| `audit` script in `package.json` | JavaScript/TypeScript |
| `audit` target in `Makefile` | Any |
| Dependabot config (`.github/dependabot.yml`) | Any |
| Renovate config (`renovate.json`, `.renovaterc`) | Any |
| CI pipeline step running audit commands | Any |

### Build Verification Detection

| Signal | Languages |
|--------|-----------|
| `build` script in `package.json` | JavaScript/TypeScript |
| `build` target in `Makefile` | Any |
| `Dockerfile`, `docker-compose.yml` | Any |
| `pom.xml` with package/install goals | Java |
| `build.gradle` with build tasks | Java |
| `pyproject.toml` with build system config | Python |
| CI pipeline step named "build" or running build commands | Any |

### Local Validation Path Detection

| Signal | What it indicates |
|--------|------------------|
| `make check`, `make validate`, `make ci` target | Unified validation command |
| `validate`, `check`, or `ci` script in `package.json` | Unified validation command |
| `scripts/validate.sh`, `scripts/ci.sh`, `scripts/check.sh` | Validation script |
| Pre-commit hooks (`.pre-commit-config.yaml`, `.husky/`) | Git hook-based validation |
| Pre-push hooks | Git hook-based validation |
| `docs/validation/local-validation-workflow.md` | Documented validation path |
| CI pipeline that mirrors local commands | CI parity |

---

## AI Skills Detection

### Skill Directory Signals

| Signal | What to check |
|--------|--------------|
| `skills/` directory at repo root | Contains skill subdirectories with `SKILL.md` files |
| `.opencode/skills/` directory | OpenCode-specific skills |
| `.github/skills/` directory | GitHub-specific skills |
| Skill subdirectories | Each subdirectory with a `SKILL.md` is one installed skill |

### Skills CLI

| Signal | What to check |
|--------|--------------|
| `npx skills list` | Returns installed skill inventory |
| `npx skills --version` | CLI is available |
| `package.json` with `skills` dependency | Skills CLI is a project dependency |

### Specific Skills to Look For

**Core workflow skills:**
- `create-pull-request-with-reviewers`
- `gh-pr-comment-resolution`
- `reflect-on-changes`

**Security skills:**
- `software-security` (from CodeGuard)
- Any skill with "security" in its name or description

**Stack-specific skills (examples):**
- React/frontend review skills
- LangGraph/LangChain skills
- Testing-focused skills

---

## Documentation Primitive Detection

### AGENTS.md

| Signal | What to check |
|--------|--------------|
| `AGENTS.md` at repo root | File exists |
| Line count | Over 200 lines suggests inline content dump (score reducer). Length alone is not a penalty -- a longer file is fine if the content is routing pointers and a repo map, not inlined documentation. |
| Content pattern | Contains links/pointers to `docs/` (routing file) vs. inline content (dump) |
| Repo map | Includes a directory structure tree showing the repo layout. |
| Freshness | References match actual file paths in the repo |
| Spec-driven development reference | Mentions OpenSpec, SpecKit, or change planning workflow |

### CONTRIBUTING.md

| Signal | What to check |
|--------|--------------|
| `CONTRIBUTING.md` at repo root | File exists |
| References validation workflow | Mentions test, lint, or validation commands |
| References Spec-driven development | Mentions OpenSpec, SpecKit, or structured spec-driven development process |
| References docs tree | Points to `docs/` for detailed guidance |
| Repo-specific content | Contains commands and workflows specific to this repo, not generic boilerplate |

### docs/ Directory Structure

| Signal | What it indicates |
|--------|------------------|
| `docs/` exists | Basic docs directory present |
| `docs/architecture/` | Architecture documentation (overview, services, data model) |
| `docs/dev-environment/` | Developer setup docs (first-time setup, running the app, env vars) |
| `docs/validation/` | Validation docs (local workflow, CI pipeline, testing strategy) |
| `docs/conventions/` | Coding standards and conventions |
| `docs/deployment/` | Deployment documentation |
| `docs/security/` | Security documentation |
| `docs/workflow-overview.md` | Top-level workflow explainer |
| `docs/tech-debt.md` | Known tech debt tracker |
| Cross-links between docs | Docs reference each other (score 4 signal) |
| Real content vs. scaffolds | Files contain repo-specific material, not placeholder text |
