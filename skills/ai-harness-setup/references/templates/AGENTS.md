# AGENTS

This file is a routing map. Read the linked docs for details.

## Repo Map

<!-- REQUIRED: Generate this tree from the actual repo layout detected in Step 1. -->
<!-- Show depth 2. This section is critical for agent navigation. -->
<!-- Replace the example below with the real directory structure. -->

```text
├── src/                        - source code
│   ├── components/             - UI components
│   └── services/               - business logic
├── docs/                       - engineering docs (see links below)
│   ├── architecture/           - system design and data model
│   └── validation/             - deterministic checks and CI
├── openspec/                   - change proposals and specs
├── .github/                    - CI, skills, prompts, instructions
│   ├── workflows/              - CI/CD pipelines
│   └── skills/                 - agent skills
├── ...                         - (replace with real directories from the repo)
```

## Understand the System

- **Architecture**: `docs/architecture/overview.md`
- **Services and boundaries**: `docs/architecture/services.md`
- **Data model**: `docs/architecture/data-model.md`
- **External integrations**: `docs/architecture/integrations.md`

## Set Up and Run

- **First-time setup**: `docs/dev-environment/first-time-setup.md`
- **Run the app locally**: `docs/dev-environment/running-the-app.md`
- **Environment variables**: `docs/dev-environment/environment-variables.md`

## Validate Before PR

- **Local validation**: `docs/validation/local-validation-workflow.md`
- **CI pipeline**: `docs/validation/ci-pipeline.md`
- **Testing strategy**: `docs/validation/testing-strategy.md`

## Conventions

- **Coding standards**: `docs/conventions/coding-standards.md`
- **Task runner usage**: `docs/conventions/{task-runner}-usage.md`

## Workflow

- **Full workflow overview**: `docs/workflow-overview.md`
- **Contributing**: `CONTRIBUTING.md`
- **Security**: `docs/security/security.md`

## Tech Debt

- **Known tech debt**: `docs/tech-debt.md`
- When you encounter tech debt during any task (deprecated patterns, dead code, missing tests, workarounds, TODOs), log it in `docs/tech-debt.md` rather than fixing it inline. Keep entries actionable with file paths and brief descriptions.

## Change Planning

Use OpenSpec for non-trivial changes. Create proposals, specs, designs, and tasks under `openspec/changes/`. Do not create planning docs under `docs/`.

## Deployment

- **How we ship**: `docs/deployment/overview.md`
