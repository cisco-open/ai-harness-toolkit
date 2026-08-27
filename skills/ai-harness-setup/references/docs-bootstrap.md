# Docs Bootstrap

Use this file when creating the docs section that will explain the repo's actual engineering workflow.

## Goal

Create a docs tree that captures how this specific repository really works -- its architecture, services, data flow, deployment, validation, and agent workflow -- not a placeholder structure that promises details later. Every doc should contain real content derived from inspecting the repo.

## Research Before Writing

Before creating any doc, deeply research the repo to extract concrete material. Do not write docs from assumptions.

**What to investigate:**

- **Architecture**: Read source code structure, module boundaries, import graphs, package dependencies, and config files. Identify services, libraries, apps, workers, and their relationships. Map the data flow between components.
- **APIs and interfaces**: Find route definitions, API schemas (OpenAPI, GraphQL), RPC definitions, event handlers, message queues, and webhook endpoints. Document the actual endpoints, not just "the app has an API."
- **Configuration and environment**: Find environment variables, config files, feature flags, secrets references, and external service connections. Document what each service needs to run.
- **Data layer**: Find database configs, migration files, ORM models, schema definitions, cache configs, and storage integrations. Document the actual data model and storage strategy.
- **Deployment**: Find Dockerfiles, Helm charts, Kubernetes manifests, serverless configs, CI/CD deploy stages, and infrastructure-as-code. Document how the app gets from code to running in production.
- **Dependencies and integrations**: Find external service calls, SDK usage, third-party API clients, and MCP server connections. Document what the app depends on at runtime.
- **Testing strategy**: Find test directories, test configs, fixture patterns, mock strategies, and coverage configurations. Document how to run tests and what the testing philosophy is.
- **Scripts and automation**: Find helper scripts, Makefiles, task runner configs, and CLI tools. Document the available automation surface.
- **Tech debt**: While researching the repo, note patterns that indicate tech debt -- deprecated dependencies, TODO/FIXME/HACK comments, dead code, inconsistent patterns, missing tests for critical paths, outdated configs, and workarounds. Record these findings in `docs/tech-debt.md`.

## Seed Structure

```text
docs/
|- architecture/
|  |- overview.md                    - system architecture, component map, dependency flow
|  |- services.md                    - service descriptions, responsibilities, boundaries (if multi-service)
|  |- data-model.md                  - data layer, schemas, storage, migrations
|  `- integrations.md               - external services, APIs consumed, third-party dependencies
|- conventions/
|  |- coding-standards.md            - language conventions, style, patterns used in this repo
|  |- naming-and-structure.md        - directory layout, file naming, module organization
|  |- apm-management.md              - APM usage, installed skills, gitignore rules for managed paths
|  `- {task-runner}-usage.md         - task runner docs (e.g., nx-usage.md, makefile-usage.md, uv-usage.md)
|- dev-environment/
|  |- first-time-setup.md            - dependency bootstrap, toolchain install, env config
|  |- running-the-app.md             - local run commands for all services/apps
|  |- environment-variables.md       - required env vars, secrets, config files
|  `- common-issues.md              - known setup gotchas, platform-specific notes
|- deployment/
|  |- overview.md                    - how code gets to production
|  |- environments.md                - environment descriptions (dev, staging, prod)
|  `- infrastructure.md             - container, cloud, and infra config (if applicable)
|- validation/
|  |- local-validation-workflow.md   - deterministic review and validation path
|  |- ci-pipeline.md                 - CI parity with local checks
|  `- testing-strategy.md           - test organization, coverage, fixture patterns
|- security/
|  `- security.md                   - security expectations, scanning, audit procedures
|- tech-debt.md                      - known tech debt, deprecated patterns, improvement opportunities
`- workflow-overview.md              - top-level engineering workflow explainer
```

Adapt this structure to the repo. Not every repo needs every file:
- Single-service repos may not need `services.md`.
- Repos without a database may not need `data-model.md`.
- Repos that do not deploy (libraries, CLIs) may not need `deployment/`.

Add files when the repo has material that warrants them. Remove files when they would be empty filler.

Keep change proposals, specs, designs, and task breakdowns in OpenSpec artifacts under `openspec/changes/`, not under `docs/`.

## Authoring Order

Create or update these docs in roughly this order:

1. `docs/architecture/overview.md` - the system map: what this repo is, what it contains, how the parts relate
2. `docs/dev-environment/first-time-setup.md` - dependency bootstrap with real commands
3. `docs/dev-environment/running-the-app.md` - local run commands for every service/app/worker
4. `docs/dev-environment/environment-variables.md` - every env var, config file, and secret reference
5. `docs/architecture/services.md` - service descriptions with actual responsibilities (if multi-service)
6. `docs/architecture/data-model.md` - data layer, schemas, migrations (if applicable)
7. `docs/architecture/integrations.md` - external service dependencies and API clients
8. `docs/conventions/coding-standards.md` - observed patterns, not aspirational guidelines
9. `docs/conventions/apm-management.md` - APM usage, installed skills and their targets, and `.gitignore` rules for all APM-managed and OpenSpec-generated paths
10. `docs/conventions/{task-runner}-usage.md` - task runner docs with real commands
11. `docs/validation/local-validation-workflow.md` - deterministic review and validation path
12. `docs/validation/ci-pipeline.md` - CI parity with local checks
13. `docs/validation/testing-strategy.md` - test organization, how to run, coverage expectations
14. `docs/security/security.md` - security scanning, audit procedures, expectations
15. `docs/tech-debt.md` - known tech debt discovered during research (see below)
16. `docs/deployment/overview.md` - how the app ships (if applicable)
17. `docs/workflow-overview.md` - top-level explainer that links to all focused docs
18. `CONTRIBUTING.md` - contributor workflow entry points, referencing the docs above
19. `AGENTS.md` - lean routing file pointing agents to docs (see `references/templates/AGENTS.md`)

Write architecture and environment docs first because they require the deepest research and inform everything else. Write the workflow overview last because it synthesizes all other docs.

## What the Generated Docs Should Actually Contain

The goal is not just to scaffold folders. The generated documentation should describe the actual thing the repo does and the actual workflow contributors follow.

For each doc, prefer concrete material such as:

- the real bootstrap commands from lockfiles, package managers, toolchains, and helper scripts
- the real run commands for apps, workers, notebooks, CLIs, or services
- the real validation commands used locally and in CI
- the actual architecture boundaries, important directories, and dependency flow
- the actual API endpoints, data models, and integration points
- the actual deployment pipeline and environment configurations
- the actual agent touchpoints such as OpenSpec, OpenCode, vendored skills, slash commands, or automation entry points

If the repo uses OpenSpec, document that planning artifacts live in `openspec/changes/` and keep `docs/` focused on durable workflow and reference material.

Avoid vague filler like "run the app" or "follow team conventions" when the repo already exposes the exact commands and files. Every doc should contain information that could only come from actually reading this specific repo's code and config.

## `docs/conventions/apm-management.md` Content Guide

When the repo uses APM, create this doc to serve as the durable reference for how APM-managed dependencies interact with the repository. It should contain:

1. **Installed skills and their targets** -- list every skill installed via `apm install`, including which targets were used (e.g., `-t opencode -t cursor -t copilot -t claude`). Show the actual `apm install` commands used.
2. **Where APM materializes content** -- document the directories APM writes to for each target (e.g., `.github/skills/`, `.github/prompts/`, `.github/instructions/`, `.claude/skills/`).
3. **What to commit** -- explain that all deployed files in `.github/` and `.claude/` should be committed so every contributor gets agent context without running `apm install`. Only `apm_modules/` is gitignored.
4. **How to add a new skill** -- the `apm install` command pattern with targets, then stage and commit the deployed files alongside `apm.yml` and `apm.lock.yaml`.
5. **How to sync after pulling** -- `apm install` to regenerate managed content from `apm.yml` and `apm.lock.yaml`, then verify no drift with a conditional status check that only includes `.claude/` when present, for example:

   ```bash
   if [ -d .claude ]; then
     git status --porcelain .github/ .claude/
   else
     git status --porcelain .github/
   fi
   ```
6. **CI drift check** -- document the CI step that runs `apm install` and uses the same conditional `git status` pattern to fail if deployed files are out of sync (see `references/ai-tooling.md` for the pattern).
7. **Verification** -- `apm deps list`, `apm deps tree`, and confirming deployed files are committed.

This doc is the single source of truth for what APM manages in the repo. When a new skill is installed, this doc should be updated alongside the committed deployed files.

## `AGENTS.md` Purpose and Template

`AGENTS.md` is a **routing file**, not a documentation dump. It should be short and point agents to the right place in `docs/` for details.

Use `references/templates/AGENTS.md` as the starting point, then adapt the pointers to the target repo's actual docs structure. All substantive content belongs in `docs/`.

When creating `AGENTS.md`:
- **always include a repo map/directory structure** near the top of the file, showing the repo's actual layout as a tree (depth 2). This is the single most important section for agent navigation -- without it, agents cannot reliably locate files or understand the project's organization. Use the detection results from Step 1 to produce an accurate tree that covers source directories, config files, docs, scripts, and key entry points.
- explicitly state that non-trivial change planning belongs in OpenSpec
- point to the workflow overview and focused docs, not inline the content
- list the validation commands directly (these are short and agents need them immediately)
- do not duplicate content that lives in `docs/`

If `AGENTS.md` already exists, do not replace or discard its current content. Instead, merge in the `docs/` directory map alongside the existing material. Preserve any project-specific context, routing rules, or conventions the file already captures -- only add the pointers to the new docs tree.

Do not create parallel `docs/exec-plans/` or `docs/product-specs/` trees for work that should live in `openspec/changes/`.

## Synthesis Pass

After the focused docs are drafted:

1. create the top-level workflow overview (`docs/workflow-overview.md`) that links to all focused docs
2. verify every major statement is backed by a file, command, config, or directory in the repo
3. remove duplicate explanations that belong in a more focused page
4. add cross-links so a human or agent can move from setup to architecture to validation to deployment without guesswork
5. verify `AGENTS.md` points to the right docs and does not contain stale references
6. call out any genuinely missing documentation as follow-up work rather than hand-waving around it

## Content Rules

- keep durable rules in docs, not only in OpenSpec artifacts or chat transcripts
- use `AGENTS.md` as a routing file that points to `docs/`, not as a dump of every detail
- use `AGENTS.md` to point non-trivial change planning to OpenSpec
- keep stack-specific how-to material in focused docs under `docs/`
- make sure docs explain both the human entry point and the agent entry point
- prefer repo-specific filenames and titles over copying names from another workspace
- document real commands and observed repo behavior, not aspirational future state
- architecture docs should describe what the code actually does today, not what it might do someday
- log tech debt as you discover it during research -- do not fix it inline, document it in `docs/tech-debt.md` for follow-up

## Verification

- a new contributor can find setup, run, review, and OpenSpec planning entry points without tribal knowledge
- architecture docs accurately describe the repo's real structure, services, and data flow
- dev environment docs contain real commands that actually work
- validation and CI docs reference executable commands, not only policies
- the workflow overview links to all focused docs and reads as a coherent entry point
- `AGENTS.md` is a lean routing file that includes a repo map/directory structure and routes to `docs/`
- focused docs read like one coherent system after synthesis
- no doc is empty filler -- every file contains material derived from the actual repo
