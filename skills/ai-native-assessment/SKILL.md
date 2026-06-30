---
name: ai-native-assessment
description: Evaluate and score how AI-native a repository is. Checks for the existence and maturity of AI primitives -- spec-driven development, deterministic checks, AI skills, documentation, IDE configuration, and agentic legibility -- and produces a scored markdown report with prioritized recommended actions.
compatibility: Works on any repository with local filesystem access.
metadata:
  version: "1.0"
---

# AI-Native Assessment

Use this skill to evaluate any repository's AI-native maturity. The workflow starts with deterministic candidate and evidence discovery, then uses the LLM to score the repository. The bundled scanner can also emit deterministic scores when explicitly requested.

## When To Use It

- When asked whether a repo is AI-native or AI-ready
- When measuring the impact of an `ai-harness-setup` bootstrap
- When comparing repositories for AI-native maturity
- When creating a baseline score before workflow improvements
- When you need a prioritized backlog of AI-native improvements

## Inputs

- The target repository

## Reference Files

- `references/scoring-framework.md` -- graduated rubric for all six categories and their sub-metrics
- `references/detection-signals.md` -- filesystem and tooling signals for detecting AI primitives
- `references/agentic-legibility-framework.md` -- full 9-dimension rubric for Category 6 (Agentic Legibility)

## Output Template

- `templates/ai-native-scorecard.md` -- structure for the final scorecard written to `docs/ai-native-scorecard.md`
- `templates/agentic-legibility-scorecard.md` -- template for the legibility sub-assessment section

## Workflow

### Phase 1: Deterministic Detection (Zero Cost)

Run the bundled detection script to gather all signals, candidates, and evidence deterministically:

```bash
python3 scripts/detect.py <repo_root>
```

If you want the script to also emit its deterministic score payload, use:

```bash
python3 scripts/detect.py <repo_root> --with-scoring
```

This produces a JSON object with:
- Language and package manager detection
- All tool candidates (lint/test/build/format/typecheck) with priority ranking and source provenance
- Additional scan candidates (security, boundary, duplication, dead code, API contracts, infra, container, coverage)
- Selected commands (best picks per kind)
- Evidence-rich category signals for all six categories
- AI validation staging (ambiguous commands, review suggestions)

When `--with-scoring` is used, the JSON additionally includes:
- Category 1-5 deterministic scores and Category 6 partial deterministic scores (8/18 sub-metrics)
- Composite score and tier assignment
- Recommended actions

Parse the JSON output and use it as the foundation for Phase 2. Default mode is preferred when the model should own the final scoring decisions.

**If the script fails**, fall back to the full LLM-based detection workflow below (steps 1-2).

### Phase 2: LLM Repo Scan and Deep Scoring

Phase 1 provides the structural foundation (what tools exist, what's configured, what's in CI). Phase 2 is where the LLM **reads actual code and content** to assess quality, consistency, and legibility - things a filesystem scan cannot determine.

Using the Phase 1 JSON as starting context, the LLM must:

1. **Scan representative source files** — read 5-10 source files across the codebase to assess:
   - Naming consistency and semantic clarity
   - Code comment quality and coverage
   - Error handling patterns
   - Type annotation depth beyond just "typecheck exists"
   - Architecture clarity (can an agent understand the boundaries?)

2. **Assess documentation quality** — read the actual content of AGENTS.md, CONTRIBUTING.md, README.md, and docs/ files to evaluate:
   - Is the documentation actionable for an AI agent, or just boilerplate?
   - Are onboarding paths clear?
   - Are invariants and constraints documented?
   - Is the dependency graph explained?

3. **Score Category 6 deep sub-metrics** — the 10 sub-metrics requiring content reasoning:
   - Semantic naming quality, API documentation clarity, error handling legibility, code comment informativeness, type coverage depth, dependency documentation, architecture explainability, onboarding path clarity, debug affordances, change impact clarity
   - Score each using `references/agentic-legibility-framework.md`

4. **Score the categories, or validate deterministic scores if present** - use Phase 1 evidence plus direct file reads:
    - A linter may exist but be misconfigured or have all rules disabled
    - A docs/ directory may exist but contain only stubs
    - Skills may be installed but poorly written
    - When `--with-scoring` was used, adjust scores with evidence when the deterministic signal overstates or understates reality
    - **Review `ai_validation.evidence_gaps` when present** - these are sub-metrics where capability is present but strictness was not mechanically proven. For each gap:
      - Read the relevant CI config (Jenkins, GitHub Actions, etc.) to verify enforcement
      - Check if the validate/precommit scripts wire the check correctly
      - Confirm or adjust the score with evidence

5. **Validate CI pipeline alignment** — the deterministic scan detects CI keywords but cannot parse pipeline structure. The LLM should:
   - Read CI config files (Jenkinsfile, GitHub Actions, etc.) to confirm checks actually run and fail the build
   - Compare the CI capabilities to the local validate command — are they aligned?
   - Verify parallelized stages are still enforcing (not `continue-on-error: true`)
   - Check if coverage gates, lint strictness, or SAST are wired into CI with proper fail conditions

6. **Resolve ambiguous command selections** — review `ai_validation.ambiguous_commands` and select the correct command if the priority-based selection was wrong

The LLM receives structured evidence from Phase 1 (not starting from scratch), reducing token cost by ~80% while still performing a thorough qualitative assessment.

### Fallback: Full LLM Detection

If Phase 1 is unavailable, use the following parallelized detection workflow:

### Parallelization

Use subagents whenever possible to parallelize independent detection and scoring work. The detection phase (step 1) is highly parallelizable -- launch separate subagents for spec-driven development detection, deterministic checks detection, AI skills + documentation detection, and AI IDE + tech stack detection. These four detection streams have no dependencies on each other and should run concurrently. The scoring phase (step 2) depends on detection results, so it runs after detection completes, but the agentic legibility assessment (Category 6) can run in parallel with the other category scoring since it uses its own independent framework (`references/agentic-legibility-framework.md`).

### 1. Detect the Repo's Stack and AI Primitives

Before scoring, scan the repository to identify what exists. Read `references/detection-signals.md` for the full list of signals.

**Detect in this order (parallelize where possible -- items 1-5 are independent and should run concurrently via subagents):**

1. **Spec-Driven Development system** (priority chain):
   - Check for `openspec/` directory -> score as OpenSpec
   - Check for `specify/` directory -> score as SpecKit
   - Check for `specs/` directory (fallback, only when neither above exists) -> score as SpecKit
   - If none found -> Spec-Driven Development scores 0 across all sub-metrics

2. **Deterministic checks**: Scan manifests, config files, CI pipelines, scripts, and lockfiles for linters, type checkers, test runners, SAST tools, audit tools, build commands, and local validation entry points.

3. **AI skills**: Check for `skills/` directory, `.opencode/skills/` directory, and run `npx skills list` if available.

4. **Documentation primitives**: Check for `AGENTS.md`, `CONTRIBUTING.md`, and `docs/` directory structure.

5. **AI IDE configuration** (required -- at least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be present):
   - Check for Cursor: `.cursor/`, `.cursorrules`, `.cursor/rules/`
   - Check for VS Code / Copilot: `.vscode/settings.json` with Copilot keys, `.github/copilot-*`, copilot config files
   - Check for Windsurf: `.windsurf/`, `.windsurfrules`, `.windsurf/rules/`
   - Check for Claude Code: `.claude/`, `CLAUDE.md`, `.claude/settings.json`
   - Check for OpenCode: `opencode.jsonc`, `.opencode/` directory
   - If none of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode are found -> score Category 5 as 0 (do not mark as N/A)

6. **Tech stack**: Identify languages, frameworks, package managers from manifests and lockfiles (used for contextualizing detection and evidence).

7. **GitHub org**: Run `git remote get-url origin`. Parse the segment immediately before the repo name — this is the org or owner. Record it now so it can be written into `docs/ai-native-scorecard.md` in step 6. If no `origin` remote exists, leave the org blank for now; step 7.1 has a fallback.

Record all findings. These drive scoring in step 2.

### 2. Score Each Category

Read `references/scoring-framework.md` for the full graduated rubric.

For each of the six categories, score every sub-metric on a 0-4 scale using concrete evidence from the repository. Record the score, a brief evidence note, and specific file/config references for each sub-metric.

**Categories (38 sub-metrics total):**

| # | Category | Weight | Count | Sub-metrics |
|---|----------|--------|-------|-------------|
| 1 | Spec-Driven Development | 20% | 3 | System and artifacts, Workflow commands, Documentation |
| 2 | Deterministic Checks | 25% | 7 | Linting, Type checking, Testing, SAST, Dep audit, Build verification, Local validation path |
| 3 | AI Tooling & Skills | 15% | 3 | Workflow skills, Security review skills, Skill relevance |
| 4 | Documentation Tree | 15% | 4 | AGENTS.md, CONTRIBUTING.md, docs/ structure, Content quality |
| 5 | AI IDE Configuration | 10% | 3 | Config exists, Commands/skills, MCP servers |
| 6 | Agentic Legibility | 15% | 18 | 9 dimensions x 2 sub-metrics each (see `references/agentic-legibility-framework.md`) |

Compute each category score (Categories 1-5) as the arithmetic mean of its sub-metric scores. If a sub-metric is marked N/A, exclude it from both the numerator and the denominator -- do not compensate or redistribute its weight. Category 6 uses the weighted composite defined in `references/agentic-legibility-framework.md`, not a simple arithmetic mean.

**Category 5 (AI IDE Configuration):** At least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be configured. If none of these are detected, score as 0 (do not mark as N/A). Score the strongest detected IDE configuration across all detected IDEs.

**Category 6 (Agentic Legibility):** Score using the framework in `references/agentic-legibility-framework.md`. This evaluates 9 dimensions (18 sub-metrics) covering repository orientation, information findability, codebase navigability, task executability, verification legibility, intent and invariants, safety boundaries, machine-friendliness, and freshness. Compute the weighted composite as defined in the framework and use it directly as the Category 6 score. This can run as a parallel subagent alongside other category scoring.

### 3. Verify Arithmetic

Before computing the composite, re-derive every category score from its sub-metric scores:

1. For Categories 1-5, sum the sub-metric scores and divide by the count of scored sub-metrics (excluding any N/A). This is the category score.
2. For Category 6, independently recompute the weighted composite exactly as defined in `references/agentic-legibility-framework.md` using the underlying sub-metric scores and their specified weights. Use this recomputed value as the Category 6 score.
3. If any reported category score (including Category 6) differs from its re-derived value, replace it with the re-derived value.
4. Do not apply qualitative adjustments, rounding bumps, or "weighting" overrides to any category or composite score. The only valid category scores are arithmetic means (Categories 1-5) and the Category 6 weighted composite, and the only valid overall score is the weighted sum (composite).

### 4. Compute Composite Score and Assign Tier

**When all six categories are scored and verified:**

```
Composite = (Cat1 x 0.20) + (Cat2 x 0.25) + (Cat3 x 0.15) + (Cat4 x 0.15) + (Cat5 x 0.10) + (Cat6 x 0.15)
```

**Tier assignment:**

| Composite Score | Tier |
|-----------------|------|
| 0.0 - 0.9 | Unaware |
| 1.0 - 1.9 | Nascent |
| 2.0 - 2.9 | Structured |
| 3.0 - 3.5 | Established |
| 3.6 - 4.0 | Exemplary |

### 5. Generate Recommended Actions

For each sub-metric scoring below 3, generate a recommended action:

- **What to do**: Concrete instruction (command, file to create, tool to install)
- **Which sub-metric it improves**: Category and sub-metric name
- **Expected score improvement**: Current score -> target score (3)
- **Composite impact**: `(target_score - current_score) / 4 x category_weight`

Order actions by descending composite impact so the highest-leverage actions appear first.

### 6. Write the Scorecard

Use `templates/ai-native-scorecard.md` as the structure. Fill in all sections with the assessment results and write the completed scorecard to `docs/ai-native-scorecard.md` in the target repository, creating `docs/` if it does not exist.

The completed file must follow the template exactly: preserve the template's heading hierarchy, section order, field labels, table columns, and required rows. Replace placeholders with assessment content, but do not omit, rename, reorder, or invent sections. If a field cannot be populated from the repository, keep the template entry and mark it `N/A` or add a brief evidence-based explanation instead of removing it.

Write only the final report content to `docs/ai-native-scorecard.md`. Final arithmetic is allowed when it directly explains the reported scores, but do not include scratch work, self-corrections, conversational fillers, calculation retries, or commentary such as "wait", "let me recalculate", or similar process narration anywhere in the file.

If a previous scorecard exists at that path, overwrite it.

**Write the Summary section last.** Complete all detailed per-sub-metric scoring tables, category averages, the agentic legibility composite, the overall composite calculation, and recommended actions before populating the Summary block at the top of the scorecard. Do not pre-populate summary scores before the detailed arithmetic is finished.

### 7. Finish

After writing `docs/ai-native-scorecard.md`, report the scorecard path, composite score, maturity tier, and the highest-impact recommended actions to the user. The local scorecard is the primary and only required output of this skill.

## Scoring Rules

- `0` -- missing or actively hostile to agent workflows
- `1` -- present in fragments, but unreliable or inconsistent
- `2` -- usable with manual inference and extra exploration
- `3` -- clear and mostly complete for routine use
- `4` -- explicit, current, machine-friendly, and easy to act on

## Guardrails

- **Never include actual secret values in the scorecard.** When the assessment discovers hardcoded credentials, API keys, tokens, passwords, connection strings, or any other secret material in the target repository, the scorecard must note the **existence, type, and file location** of the secret (e.g., "Hardcoded MongoDB connection string with plaintext credentials found in `config/database.js:25`") but must **never quote, embed, or reproduce the actual secret values**. Use placeholder descriptions like `<redacted>` or describe the secret generically (e.g., "plaintext password", "auth token") instead of copying the literal value. This applies to all scorecard sections: evidence fields, notes, key strengths, key gaps, recommended actions, and any other prose.
- **Template fidelity is mandatory.** Regardless of which model, IDE, or client invokes this skill, the final `docs/ai-native-scorecard.md` output structure must conform to `templates/ai-native-scorecard.md` rather than a model-invented format.
- **No reasoning transcript in artifacts.** The scorecard is a final report, not a transcript. Final score calculations may be shown as part of the report, but never write chain-of-thought, internal reasoning, retries, arithmetic scratch work, or self-talk into `docs/ai-native-scorecard.md`.
- **Assessment output.** This skill evaluates the repo and writes the scorecard output file. No other modifications are made to the target repository.
- **Evidence-based scoring.** Every sub-metric score must reference concrete files, configs, commands, or their absence. Do not score based on inferred intent.
- **No ad-hoc score adjustments.** Category scores for Categories 1-5 must equal the arithmetic mean of their sub-metric scores. Category 6 must equal the weighted composite defined in `references/agentic-legibility-framework.md`. The composite score must equal the weighted sum of category scores. Do not manually adjust, round up, or apply qualitative overrides to any score. If the rubric produces a result that feels unintuitive, note the concern in commentary but report the mathematically derived score.
- **Artifact classification.** IDE-specific artifacts (VS Code chatmodes, Cursor commands, Copilot agents/prompts) count under Category 5 (AI IDE Configuration), not Category 3 (AI Tooling & Skills). Category 3 covers only standalone skills in a `skills/` or `.opencode/skills/` directory. Do not count the same artifact in multiple categories.
- **AI IDE Configuration is required.** At least one of Cursor, VS Code/Copilot, Windsurf, Claude Code, or OpenCode must be present. If none are detected, score Category 5 as 0. Do not mark Category 5 as N/A or redistribute its weight.
- **Tool-agnostic spec-driven development.** Score OpenSpec and SpecKit on the same unified rubric. Do not favor one over the other.
- **Inline legibility assessment.** Score Category 6 using `references/agentic-legibility-framework.md` directly. Do not invoke a separate skill.
- **Actionable recommendations.** Every recommended action must include a concrete instruction, not generic guidance.

## Reference Map

- `references/scoring-framework.md` -- full graduated rubric for all categories and sub-metrics
- `references/detection-signals.md` -- detection logic for spec-driven development, AI IDE, checks, skills, and docs
- `references/agentic-legibility-framework.md` -- 9-dimension rubric for Category 6 (Agentic Legibility)
- `templates/agentic-legibility-scorecard.md` -- template for the legibility sub-assessment section
- `templates/ai-native-scorecard.md` -- output template for the scorecard report
