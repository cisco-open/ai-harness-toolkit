# Agentic Legibility Framework

## Purpose

This framework assesses how easily a software repository can be understood, navigated, modified, and verified by an autonomous or semi-autonomous coding agent.

Agentic legibility is not the same as code quality. A codebase can be high quality but still hard for an agent to operate in if intent, structure, workflows, or safety boundaries are implicit.

## How To Use This Framework

Score each metric on a 0-4 scale:

- `0`: Missing or actively hostile to agent execution
- `1`: Present in fragments, but unreliable or inconsistent
- `2`: Usable with manual inference and extra exploration
- `3`: Clear and mostly complete for routine agent work
- `4`: Explicit, current, machine-friendly, and easy to act on

Each metric includes:

- what the agent needs
- what good evidence looks like
- common failure modes

Use the scorecard in `templates/agentic-legibility-scorecard.md` to record results.

## Dimension 1: Repository Orientation

### 1.1 Agent Repo Map

Assesses whether the repo exposes a high-level map of major systems, directories, ownership boundaries, and data flows.

Evidence:

- a top-level architecture map
- directory purpose summaries
- service boundaries and responsibilities
- links between runtime components and source locations

Strong signals:

- "start here" docs for agents or contributors
- module index by function, not just by path
- a concise explanation of how the application is stitched together

Failure modes:

- agents must infer architecture from folder names
- important systems live in "misc", "utils", or overloaded packages
- no explanation of which code is entrypoint vs support code

### 1.2 Entry Point Clarity

Assesses how clearly the repo identifies executable entry points, background jobs, tests, scripts, migrations, and local development commands.

Evidence (check `AGENTS.md`, `docs/`, and `README.md` -- entrypoint mapping can live in any of these):

- documented app startup commands
- known entrypoint files
- CI and automation entrypoints identified (e.g., `Jenkinsfile`, `.github/workflows/`)
- environment-specific startup notes

Strong signals:

- `AGENTS.md` repo map that annotates which files are entrypoints vs support code
- `docs/architecture/overview.md` or `docs/dev-environment/running-the-app.md` that identifies entrypoints

Failure modes:

- multiple plausible entrypoints with no explanation in any file (`AGENTS.md`, `docs/`, or `README.md`)
- scripts with side effects but no documentation
- setup depends on tribal knowledge

## Dimension 2: Information Findability

### 2.1 Context Proximity

Assesses whether an agent can locate the relevant context for a specific code change without reading the whole repo. This is not about whether docs exist — it is about whether the information an agent needs during a change is reachable within a short path from the code being modified.

Evidence:

- in-file or in-directory READMEs that explain module purpose and boundaries
- module-level docstrings or header comments that state responsibility and key dependencies
- cross-references between related modules (e.g., `@see`, links, or explicit "related:" annotations)
- colocated docs close to the code they describe, not only in a top-level `docs/` tree

Failure modes:

- the only explanation of a module lives in a top-level doc the agent would not know to read
- key behavioral context is in commit messages — not in the repo
- an agent must open 5+ unrelated files to understand one component

### 2.2 Change-Relevant Discoverability

Assesses whether the repo makes it easy for an agent to find the specific information it needs to make a safe change — migration patterns, downstream dependencies, and coupling between components.

Evidence:

- docs or comments that explain downstream dependencies and follow-on changes
- migration or rollout guidance near the code that requires it
- explicit notes on coupling between modules (e.g., "changing this schema requires updating X and Y")

Failure modes:

- no guidance on downstream impact; the agent must guess which related systems need to change
- hidden release or deployment coupling that is only known through experience
- an agent can find the file to change but cannot find the downstream impact without reading every import

## Dimension 3: Codebase Navigability

### 3.1 Naming and Path Semantics

Assesses whether names and directories help an agent predict what code does before opening it.

Evidence:

- descriptive module names
- limited overloading of generic directories like `common`, `shared`, or `helpers`
- strong correspondence between file path and behavior

Failure modes:

- logic spread across poorly named utility buckets
- misleading file names
- major behaviors hidden in decorators, config, or metaprogramming without explanation

### 3.2 Locality of Concern

Assesses whether related logic, tests, fixtures, and docs are colocated enough for efficient task execution.

Evidence:

- tests live near the code they verify or are clearly indexed
- feature-level folders
- minimal need to search across unrelated packages for one change

Failure modes:

- implementing one feature requires touching many distant areas with no guidance
- tests are hard to discover from source files

## Dimension 4: Task Executability

### 4.1 Setup Reproducibility

Assesses whether an agent can get from a fresh clone to a working local environment without human intervention. The question is not whether setup docs exist — it is whether the setup path is fully scriptable and self-contained.

Evidence:

- a single command or script bootstraps the entire environment (e.g., `make setup`, `./scripts/bootstrap.sh`)
- no interactive prompts, manual downloads, or GUI steps required
- secrets and environment variables have documented dummy or dev defaults so the agent can proceed without real credentials
- the bootstrap path is idempotent — running it twice does not break the environment

Failure modes:

- setup requires a human to copy-paste env vars from a wiki or vault
- bootstrap depends on globally installed tools not declared in the repo
- the agent can find setup docs but must interpret prose instructions into commands

### 4.2 Task Runbooks

Assesses whether common tasks are documented as repeatable procedures.

Examples:

- add a new endpoint
- change a UI component
- update a schema
- run a targeted test
- debug a failed job

Strong signals:

- repo-specific runbooks for high-frequency changes
- command examples with expected outputs
- skills for common tasks

Failure modes:

- agents must rediscover workflows every time
- no distinction between safe and risky procedures

## Dimension 5: Verification Legibility

### 5.1 Test Discoverability

Assesses whether an agent can determine exactly which tests cover a specific file or module it just changed — not whether a test runner exists, but whether the mapping from source to tests is navigable.

Evidence:

- test files mirror source structure (e.g., `src/auth/handler.ts` → `src/auth/handler.test.ts` or `tests/auth/test_handler.py`)
- test index files or docs that map test files to the source modules they cover
- tests are colocated with source or follow a naming convention an agent can pattern-match without reading every test file
- focused test run commands that accept a file or module path (e.g., `pytest tests/auth/`, `vitest src/auth/`)

Failure modes:

- test files have unrelated names (e.g., `test_suite_3.py`) with no mapping to source modules
- the agent must read every test file to find which ones exercise the changed code
- integration and e2e tests are mixed with unit tests with no categorization

### 5.2 Verification Path Clarity

Assesses whether the repo makes it obvious how to prove a change is safe.

Evidence:

- pre-merge checks
- lint, typecheck, unit, integration, and e2e commands
- definition of done for common changes
- examples of expected verification scope

Failure modes:

- agents can run tests, but cannot tell what is sufficient
- CI exists, but local verification is undocumented

## Dimension 6: Intent and Invariants

### 6.1 Business Logic Explainability

Assesses whether the repo explains why core rules exist, not just how they are implemented.

Evidence:

- comments or docs for domain invariants
- ADRs or decision records
- rationale near complex workflows

Failure modes:

- business rules are encoded only in conditionals
- agents can modify behavior without understanding product intent

### 6.2 Invariant Visibility

Assesses how clearly the repository surfaces constraints an agent must preserve.

Examples:

- authorization rules
- data integrity rules
- compatibility constraints
- performance or latency budgets
- backwards-compatibility expectations

Failure modes:

- invariants are implicit
- violations are only caught in production or review

## Dimension 7: Safety Boundaries

### 7.1 Generated vs Editable Boundaries

Assesses whether the repo clearly marks generated code, vendor code, build artifacts, and hand-edited source.

Evidence:

- generated file banners
- source-of-truth documentation
- codegen instructions

Failure modes:

- agents edit generated files by accident
- ownership of artifacts is unclear

### 7.2 Risk Surface Annotation

Assesses whether the repo highlights sensitive areas where changes carry elevated risk.

Examples:

- auth
- billing
- migrations
- infra
- security controls
- shared schemas

Strong signals:

- explicit warnings
- review requirements
- extra validation steps for sensitive code paths

Failure modes:

- risky areas are discoverable only through experience

## Dimension 8: Machine-Friendliness

### 8.1 Explicit Conventions

Assesses whether conventions are written down in a way an agent can follow consistently.

Evidence:

- coding standards tied to this repo
- architectural conventions
- file placement rules
- patterns to copy and anti-patterns to avoid

Failure modes:

- repo relies on unwritten style norms
- "follow existing patterns" is the only guidance

### 8.2 Structured Metadata

Assesses whether the repo contains machine-friendly artifacts that reduce ambiguity.

Examples:

- architecture indexes
- module manifests
- ownership files
- schema docs
- interface contracts
- task metadata

Failure modes:

- useful information exists only as prose
- no metadata linking systems, owners, or boundaries

## Dimension 9: Freshness and Trustworthiness

### 9.1 Documentation Freshness

Assesses whether the documented repo state matches reality.

Evidence:

- recently updated docs (Check path-filtered history such as `git log -- docs/` or `git log -- <docs path>`)
- commands that still work
- version-specific instructions
- changelog or ADR hygiene

Failure modes:

- docs are comprehensive but outdated
- commands that don't work or refer to files that don't exist

### 9.2 Drift Detection

Assesses whether the repo has mechanisms that catch drift between documentation, configuration, and behavior.

Examples:

- docs linting
- CI validation of examples
- generated architecture docs
- checks for stale schemas or snapshots
- Look in `.github/workflows/` and similar CI config files for jobs that validate, lint, or regenerate documentation (e.g., a markdown linter, generated API docs step, or an agentic workflow that maintains docs). The presence of such a workflow is a strong signal, but only recommend a score of `4` when it clearly runs in CI for relevant changes (such as PRs or mainline updates), covers the docs/examples/generated artifacts in question, and is enforced or otherwise relied on as a meaningful check.

Failure modes:

- docs and workflows silently rot

## Suggested Weighting

For a single composite score, use these weights:

- Repository Orientation: 10%
- Information Findability: 10%
- Codebase Navigability: 20%
- Task Executability: 10%
- Verification Legibility: 10%
- Intent and Invariants: 15%
- Safety Boundaries: 10%
- Machine-Friendliness: 10%
- Freshness and Trustworthiness: 5%

This weighting biases toward whether an agent can safely complete and verify work, not just whether documentation exists.

## Output Levels

Interpret the composite score as:

- `0.0-0.9`: Unaware
- `1.0-1.9`: Nascent
- `2.0-2.9`: Structured
- `3.0-3.5`: Established
- `3.6-4.0`: Exemplary

## Quick Assessment Heuristics

A repository is usually agentically legible if an agent can answer these questions in under 10 minutes:

1. What are the main systems and where do they live?
2. Which files are safe to edit for this task?
3. How do I run the app and the relevant tests?
4. What invariants must not be broken?
5. What evidence would prove the change is correct?

If the answer to most of these requires guesswork, the repo has low agentic legibility even if the code is otherwise well engineered.

## Improvement Backlog Template

When a repo scores poorly, prioritize fixes in this order:

1. Make setup and verification runnable from docs.
2. Add an agent repo map with system boundaries and entrypoints.
3. Document invariants and risky areas.
4. Add task runbooks for common changes.
5. Introduce structured metadata that reduces repeated exploration.
