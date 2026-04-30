# AI-Native Assessment

Use `ai-native-assessment` to evaluate and score how AI-native a repository is. The skill scans the repo for AI primitives — spec-driven development, deterministic checks, AI skills, documentation, IDE configuration, and agentic legibility — and produces a scored markdown report with prioritized recommended actions.

## Two Installation Options

You can install this skill with either `apm` or `npx skills`.

## Option 1: Install With APM

Use this option when you want the skill managed as a dependency and deployed to one or more supported targets.

### Prerequisites

- Install APM if needed: `curl -sSL https://aka.ms/apm-unix | sh`
- Verify APM: `apm --version`
- Initialize APM in the repo if needed: `apm init --yes`

### Install The Skill

```bash
apm install cisco-open/ai-harness-toolkit/skills/ai-native-assessment -t opencode -t cursor -t copilot
```

Notes:

- Adjust the `-t` targets to match the tools you use.
- For OpenCode only, `-t opencode` is enough.
- For private repository access, ensure `GITHUB_TOKEN` is exported in your shell before running `apm install`.

### Verify The Install

```bash
apm deps list
apm deps tree
```

## Option 2: Install With `npx skills`

Use this option when you want to add the skill directly from the repository without managing it through APM.

```bash
npx skills add https://github.com/cisco-open/ai-harness-toolkit --skill ai-native-assessment
```

You can verify the CLI and installed skills with:

```bash
npx skills --version
npx skills list
```

## Typical Outputs

Depending on the repository's current state, the skill produces:

- `docs/ai-native-scorecard.md` — the completed scorecard, formatted to match `templates/ai-native-scorecard.md`, with per-sub-metric scores, category averages, composite score, and tier assignment
- A prioritized list of recommended actions ordered by composite impact

## What The Skill Does

The assessment evaluates six weighted categories and computes a composite score on a 0–4 scale:

| # | Category | Weight |
|---|----------|--------|
| 1 | Spec-Driven Development | 20% |
| 2 | Deterministic Checks | 25% |
| 3 | AI Tooling & Skills | 15% |
| 4 | Documentation Tree | 15% |
| 5 | AI IDE Configuration | 10% |
| 6 | Agentic Legibility | 15% |

Based on the composite score, the repository is assigned a maturity tier:

| Composite Score | Tier |
|-----------------|------|
| 0.0 – 0.9 | Unaware |
| 1.0 – 1.9 | Nascent |
| 2.0 – 2.9 | Structured |
| 3.0 – 3.5 | Established |
| 3.6 – 4.0 | Exemplary |

The skill writes a completed scorecard to `docs/ai-native-scorecard.md` using the exact section and table structure from `templates/ai-native-scorecard.md`.

## Good Times To Use It

- After running `ai-harness-setup` to verify and measure what was set up
- Before starting AI workflow improvements to establish a baseline
- Periodically to track maturity progress over time
- When onboarding a repo into an AI-native engineering practice
