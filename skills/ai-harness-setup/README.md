# AI Harness Setup

Use `ai-harness-setup` to bootstrap a repository for agent-driven engineering. The skill inspects the repo first, then helps set up APM, OpenSpec, deterministic checks, AI skills, workflow documentation, and OpenCode or other supported AI tooling surfaces.

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
apm install cisco-open/ai-harness-toolkit/skills/ai-harness-setup -t opencode -t cursor -t copilot
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
npx skills add https://github.com/cisco-open/ai-harness-toolkit --skill ai-harness-setup
```

You can verify the CLI and installed skills with:

```bash
npx skills --version
npx skills list
```

## What The Skill Helps Set Up

- APM as the skill and dependency delivery layer
- OpenSpec for spec-driven change management
- Deterministic checks matched to the detected stack
- AI workflow and security skills
- `docs/` and `AGENTS.md` guidance for humans and agents
- OpenCode or other supported AI IDE surfaces when present

## Typical Outcomes

Depending on what the repository already contains, this skill may help create or update:

- `apm.yml` and `apm.lock.yaml`
- `openspec/`
- deterministic check configs and CI wiring
- `.opencode/`, `.github/`, `.claude/`, or other tool-specific skill surfaces
- `docs/`
- `AGENTS.md`
- `CONTRIBUTING.md`

## Good Times To Use It

- When starting AI workflow adoption in an existing repo
- When bootstrapping a new repo for agent-assisted development
- When standardizing repo setup across OpenCode, Cursor, and Copilot
- Before running an `ai-native-assessment`
