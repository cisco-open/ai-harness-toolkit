# Scoring Framework

This reference defines the graduated rubric for all six categories of the AI-Native Scorecard. Use it when scoring each sub-metric during an assessment.

## Scoring Scale

Every sub-metric uses the same 0-4 graduated scale:

| Score | Meaning |
|-------|---------|
| 0 | Missing or actively hostile to agent workflows |
| 1 | Present in fragments, but unreliable or inconsistent |
| 2 | Usable with manual inference and extra exploration |
| 3 | Clear and mostly complete for routine use |
| 4 | Explicit, current, machine-friendly, and easy to act on |

Score based on concrete evidence found in the repository, not inferred intent.

---

## Category 1: Spec-Driven Development (20%)

Evaluates whether the repo has a spec-driven development system (OpenSpec or SpecKit) and how mature its usage is. The rubric applies identically regardless of which tool is detected.

### 1.1 System and Artifacts

| Score | Evidence |
|-------|----------|
| 0 | No spec-driven development directory exists. No trace of structured planning. |
| 1 | A directory exists (`openspec/`, `specify/`, or `specs/`) but is empty, contains only default scaffolding, or has only placeholder artifact files with no real content. |
| 2 | Directory exists with at least one real content file (e.g., a proposal or spec with substantive text), but artifacts are incomplete (e.g., a proposal exists but no specs or tasks). |
| 3 | Multiple changes exist with complete artifact chains (proposal, specs, design, tasks or equivalent). The directory structure shows active use. |
| 4 | System shows lifecycle maturity: both active and archived changes exist with comprehensive artifacts. If a CLI is available, it produces valid output (e.g., `openspec status` exits 0). |

### 1.2 Workflow Commands

| Score | Evidence |
|-------|----------|
| 0 | No workflow commands, skills, or CLI entry points exist for the spec-driven development system. |
| 1 | A CLI exists but no repo-level commands or skills surface it (e.g., `openspec` is installed globally but the repo has no `/opsx-*` commands). |
| 2 | Some commands or skills are registered but the coverage is incomplete (e.g., only `new` and `status` but no `apply` or `archive`). |
| 3 | Core workflow commands are present and functional (create, apply, verify, archive or equivalent). |
| 4 | Full command surface is documented, integrated into the contributor workflow, and referenced in AGENTS.md or CONTRIBUTING.md. |

### 1.3 Documentation

| Score | Evidence |
|-------|----------|
| 0 | No documentation anywhere references the spec-driven development system. |
| 1 | Mentioned in passing (e.g., a comment or TODO referencing OpenSpec/SpecKit). |
| 2 | Partially documented. The system is mentioned in a doc but without usage instructions. |
| 3 | Referenced in CONTRIBUTING.md or AGENTS.md with clear guidance on when and how to use it. |
| 4 | Fully documented with examples. CONTRIBUTING.md, AGENTS.md, and workflow docs all reference it. Team clearly operates through it. |

---

## Category 2: Deterministic Checks (25%)

Evaluates the presence and maturity of repeatable validation commands that can run locally and in CI without human judgment.

### 2.1 Linting

| Score | Evidence |
|-------|----------|
| 0 | No linter configured. No linter config files, no lint scripts in package manifests. |
| 1 | Linter config exists (e.g., `.eslintrc`, `ruff.toml`) but the linter is broken, has unresolved dependency issues, or is clearly unused. |
| 2 | Linter runs locally but is not wired into CI. Or linter runs but with many warnings ignored. |
| 3 | Linter is CI-enforced (lint step exists in CI config and failures block merge). Default or lightly customized rules. |
| 4 | Linter is CI-enforced in strict/zero-warning mode (e.g., `--max-warnings=0`, `select = ["ALL"]`, `strict: true`). Config contains repo-specific rule overrides beyond defaults. |

### 2.2 Type Checking

Note: If the repo's primary language does not support type checking (e.g., shell scripts, plain JavaScript without TypeScript), mark this sub-metric as N/A and exclude it from the category average.

| Score | Evidence |
|-------|----------|
| 0 | No type checker configured for a language that supports it. |
| 1 | Type checker config exists (e.g., `tsconfig.json`, `mypy.ini`) but the checker either fails to run, is effectively disabled (e.g., `strict: false` with pervasive `any`), or has never been executed (stale config). |
| 2 | Type checker runs successfully but relies on suppressions to pass (`# type: ignore`, `@ts-ignore` in >5% of typed files, or loose mode hides real errors). |
| 3 | Type checker runs cleanly. Suppressions exist in ≤5% of typed files. |
| 4 | Type checker runs in strict mode and is CI-enforced. Suppressions are rare and justified. |

### 2.3 Testing

| Score | Evidence |
|-------|----------|
| 0 | No tests exist. No test directories, no test runner config. |
| 1 | Sparse tests exist with no runner configuration. Tests may be stale or not runnable. |
| 2 | Tests exist and are manually runnable but not wired into CI or lack runner config. |
| 3 | Test runner is configured, tests pass, and CI runs them. |
| 4 | Tests have great coverage (>= 90%), support selective/focused runs, and are CI-enforced. Fixtures and mocks are organized. |

### 2.4 SAST / Security Scanning

| Score | Evidence |
|-------|----------|
| 0 | No security scanning tool exists. No Semgrep, Bandit, SpotBugs, or equivalent. |
| 1 | A scanning tool is mentioned in docs or comments but is not installed or configured. |
| 2 | A scanning tool is installed but not wired into CI or local validation. |
| 3 | Scanning runs locally and in CI. |
| 4 | Scanning runs in both CI and local validation, and blocks on findings (non-zero exit code fails the build or merge). |

### 2.5 Dependency / Vulnerability Audit

| Score | Evidence |
|-------|----------|
| 0 | No audit tooling exists. No `npm audit`, `pip-audit`, `safety`, OWASP dependency-check, or equivalent. |
| 1 | No audit tool is declared in the project's dependency manifest. Audits happen only when a developer manually runs a one-off command. |
| 2 | An audit tool is declared in dev dependencies (e.g., `pip-audit` in `requirements-dev.txt`, `audit-ci` in `devDependencies`) but is not wired into CI or any automated workflow. |
| 3 | Audit is automated in CI. Runs on PRs or on a schedule. |
| 4 | Audit is a blocking CI check with a defined severity threshold (e.g., `audit-ci.jsonc`, `safety` policy file, or equivalent). Any accepted vulnerabilities are documented in an allowlist file with justification. |

### 2.6 Build Verification

| Score | Evidence |
|-------|----------|
| 0 | No build step exists. No build script, no Dockerfile, no compilation step. |
| 1 | A build step exists but is broken or has unresolved issues that prevent successful completion. |
| 2 | Build works locally but is not verified in CI. |
| 3 | Build runs in CI and passes reliably. |
| 4 | Build system produces identical results locally and in CI (e.g., same Makefile, Dockerfile, or build script used in both). Build is reproducible and artifacts are well-defined. |

### 2.7 Local Validation Path

| Score | Evidence |
|-------|----------|
| 0 | No validation entry point exists. No script, no make target, no documented command. |
| 1 | Scattered commands exist but there is no unified validation path. Developer must know which commands to run and in what order. |
| 2 | A partial validation script or make target exists but does not cover the full check suite (e.g., runs tests but not linting or SAST). |
| 3 | A single-command validation path exists (e.g., `make check`, `npm run validate`) that covers the core checks. |
| 4 | The validation path is documented, covers all checks, and matches CI exactly. Running it locally gives the same result as the CI pipeline. |

---

## Category 3: AI Tooling & Skills (15%)

Evaluates whether AI workflow skills are installed, relevant to the stack, and include security review coverage.

### 3.1 Workflow Skills

| Score | Evidence |
|-------|----------|
| 0 | No skills are installed. No `skills/` directory, no `.opencode/skills/`, `npx skills list` returns nothing or is not available. |
| 1 | One skill is present but it may be a default or generic skill with no clear workflow purpose. |
| 2 | Core workflow skills are present (e.g., `create-pull-request-with-reviewers`, `reflect-on-changes`, or equivalent). |
| 3 | Core workflow skills plus stack-specific skills are present (e.g., React review skills for a React repo, LangGraph skills for an AI agent repo). |
| 4 | Skills are curated, maintained, and documented. The skill inventory is intentional, not bulk-installed. Skills are referenced in workflow docs. |

### 3.2 Security Review Skills

| Score | Evidence |
|-------|----------|
| 0 | No security review skills exist. No CodeGuard, no software-security skill, no security-focused rules. |
| 1 | Generic security guidance exists in docs but no executable skill or rule set, or a security skill is installed but clearly unused or has no real rule content. |
| 2 | A security review skill (e.g., `software-security` from CodeGuard) is deployed to at least one IDE target but not all configured targets. |
| 3 | Security review skill is deployed to all configured IDE targets with the tool's default/generic rule set. |
| 4 | Security review skill is deployed to all configured IDE targets with custom rules or overrides tailored to the repo's language, frameworks, or threat model (not just defaults). |

### 3.3 Skill Relevance

| Score | Evidence |
|-------|----------|
| 0 | No skills exist (same as 3.1 score of 0). |
| 1 | Skills are bulk-installed with many irrelevant to the detected stack (e.g., React skills in a Python-only repo). |
| 2 | Most installed skills are relevant to the stack but some are unnecessary or unused. |
| 3 | All installed skills are relevant. The selection uses only common/generic workflow skills (e.g., `create-pull-request-with-reviewers`, `reflect-on-changes`). |
| 4 | Skills include framework-specific or domain-specific entries that would not appear in a generic installation (e.g., a LangGraph review skill in a LangGraph repo, a Terraform plan skill in an IaC repo). |

---

## Category 4: Documentation Tree (15%)

Evaluates the presence and quality of documentation primitives that support both human and agent workflows.

### 4.1 AGENTS.md

| Score | Evidence |
|-------|----------|
| 0 | No `AGENTS.md` exists at the repository root. |
| 1 | `AGENTS.md` exists but is bloated (>200 lines of inline content), stale, or contradicts the actual repo structure. |
| 2 | `AGENTS.md` exists and is partially useful but contains a mix of routing pointers and inline content, or has some stale references. |
| 3 | `AGENTS.md` is a lean routing file with accurate pointers to `docs/`, validation commands, and workflow entry points. |
| 4 | `AGENTS.md` is current, structured as a routing file with a repo map, links are verified, points to spec-driven development workflow, and accurately routes agents to all relevant docs. |

### 4.2 CONTRIBUTING.md

| Score | Evidence |
|-------|----------|
| 0 | No `CONTRIBUTING.md` exists at the repository root. |
| 1 | `CONTRIBUTING.md` exists but contains only boilerplate (e.g., a generic "thanks for contributing" template with no repo-specific content). |
| 2 | `CONTRIBUTING.md` references some repo-specific workflow (e.g., mentions the test command or branch strategy). |
| 3 | `CONTRIBUTING.md` references the validation workflow, spec-driven development system, and provides a clear contributor path. |
| 4 | `CONTRIBUTING.md` provides a complete contributor workflow: setup, branching, validation, spec-driven development, review expectations, and references the docs tree. |

### 4.3 docs/ Structure

| Score | Evidence |
|-------|----------|
| 0 | No `docs/` directory exists. Documentation lives only in a single `README.md` or nowhere. |
| 1 | A `docs/` directory exists but contains only one or two files, or files are empty scaffolds. |
| 2 | `docs/` contains several files covering some topics (e.g., setup instructions, some architecture notes) but the structure is ad-hoc. |
| 3 | `docs/` has a structured tree with dedicated sections (e.g., `architecture/`, `dev-environment/`, `validation/`). Most sections have real content. |
| 4 | Full docs tree exists with real, cross-linked content. Architecture, dev environment, validation, conventions, and workflow overview are all populated with content derived from the actual repo. |

### 4.4 Content Quality

| Score | Evidence |
|-------|----------|
| 0 | No documentation content exists beyond a minimal README. |
| 1 | Docs exist but are empty scaffolds, placeholder text, or generic templates not customized to the repo. |
| 2 | A mix of real content and placeholder text. Some docs contain repo-specific material, others are stubs. |
| 3 | Most documentation contains real content derived from the repository: actual commands, real architecture descriptions, specific config references. |
| 4 | All documentation is grounded in the actual repository. Every doc contains material that could only come from reading this specific repo's code and config. No placeholder text remains. |

---

## Category 5: AI IDE Configuration (10%)

Evaluates the configuration of an AI-aware IDE or CLI tool. At least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be configured. If none of these are detected, score this category as 0 (do not mark as N/A).

### 5.1 Config Exists

| Score | Evidence |
|-------|----------|
| 0 | No recognized AI IDE config file found (e.g., no `.github/copilot-instructions.md`, `.cursorrules`, `.cursor/rules/`, `opencode.jsonc`, `.opencode/`, `CLAUDE.md`, or `.windsurfrules`). |
| 1 | A config file exists but contains only boilerplate or generic advice that could apply to any repo (e.g., "write clean code", "follow best practices"). No repo-specific actionable instructions. |
| 2 | Config contains at least one actionable, repo-specific instruction an agent can follow without human clarification (e.g., a validation command to run, a naming convention, a directory to avoid). |
| 3 | Config covers ≥2 of the following: (a) validation or build commands, (b) coding conventions or constraints, (c) routing to docs, specs, or skills. |
| 4 | Config covers all three areas from score 3 and includes explicit boundaries (what the agent must not do, files or patterns to avoid, or permission constraints). |

### 5.2 Commands / Skills

| Score | Evidence |
|-------|----------|
| 0 | No custom commands or skills registered in the IDE config. |
| 1 | Only default commands exist with no repo-specific additions. |
| 2 | Some custom commands are registered (e.g., a few `.opencode/command/*.md` files, copilot slash commands, or Cursor rule files). |
| 3 | Workflow commands are registered covering the core development loop (e.g., OpenSpec commands, validation triggers). |
| 4 | Full command surface is documented, covers the complete workflow, and is referenced in contributor docs. |

### 5.3 MCP Servers

| Score | Evidence |
|-------|----------|
| 0 | No MCP server entries configured despite the repo using frameworks that have MCP servers available. |
| 1 | MCP server entries exist but do not match the repo's actual stack (e.g., LangChain MCP on a repo that does not use LangChain). |
| 2 | Some MCP servers match the stack but coverage is incomplete. |
| 3 | MCP server entries match the detected stack (e.g., CopilotKit MCP for a CopilotKit repo, LangSmith MCP for a LangSmith-integrated repo). |
| 4 | MCP servers exactly match the stack, are conditionally applied, and are documented. No unnecessary servers. |

---

## Category 6: Agentic Legibility (15%)

This category uses the framework in `references/agentic-legibility-framework.md` to evaluate how easily an autonomous coding agent can understand, navigate, modify, and verify the repository.

### How to Score

1. Read `references/agentic-legibility-framework.md` for the full 9-dimension rubric (18 sub-metrics).
2. Score each sub-metric on the same 0-4 scale using concrete evidence from the repository.
3. Compute the weighted composite as defined in the framework (Repository Orientation 10%, Information Findability 10%, Codebase Navigability 20%, Task Executability 10%, Verification Legibility 10%, Intent and Invariants 15%, Safety Boundaries 10%, Machine-Friendliness 10%, Freshness and Trustworthiness 5%).
4. Use the composite score directly as the Category 6 score. Do not re-interpret or modify it.
5. Include the legibility tier (Unaware / Nascent / Structured / Established / Exemplary) in the scorecard output alongside the AI-native tier for context.
6. Use `templates/agentic-legibility-scorecard.md` to structure the detailed legibility findings as internal working notes, to be later used to populate the actual `templates/ai-native-scorecard.md`, which is the final output

The legibility assessment evaluates 9 dimensions (18 sub-metrics) covering repository orientation, information findability, codebase navigability, task executability, verification legibility, intent and invariants, safety boundaries, machine-friendliness, and freshness. See `references/agentic-legibility-framework.md` for the full framework.

---

## Weights and Composite Calculation

### Standard Weights (all 6 categories applicable)

| Category | Weight |
|----------|--------|
| Spec-Driven Development | 20% |
| Deterministic Checks | 25% |
| AI Tooling & Skills | 15% |
| Documentation Tree | 15% |
| AI IDE Configuration | 10% |
| Agentic Legibility | 15% |

### Composite Formula

```
Composite = (Cat1 x 0.20) + (Cat2 x 0.25) + (Cat3 x 0.15) + (Cat4 x 0.15) + (Cat5 x 0.10) + (Cat6 x 0.15)
```

### Note on AI IDE Configuration

Category 5 (AI IDE Configuration) is always scored. At least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be present. If none are detected, score as 0. Weight redistribution does not apply to this category.

### Handling N/A Sub-Metrics Within a Category

If a sub-metric is marked N/A (e.g., type checking for a language without a type system), exclude it from the category average. Compute the category score as the mean of the remaining sub-metrics only.

---

## Tier Definitions

| Composite Score | Tier | Description |
|-----------------|------|-------------|
| 0.0 - 0.9 | **Unaware** | No AI-native infrastructure exists. Agents would be flying blind. |
| 1.0 - 1.9 | **Nascent** | Fragments exist. AI use is opportunistic, not systematic. |
| 2.0 - 2.9 | **Structured** | Core primitives are in place. Agents can operate with some friction. |
| 3.0 - 3.5 | **Established** | AI workflow is reliable and actively used. Agents can operate effectively. |
| 3.6 - 4.0 | **Exemplary** | Model AI-native repo. Full infrastructure, actively maintained, intentionally curated. |
