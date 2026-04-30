---
name: reflect-on-changes
description: Analyze recent code changes, review findings, and touched docs to codify what changed in the repository. Use when work is complete, after a review/fix loop, or whenever the agent should update docs, commands, skills, and conventions based on recent changes while identifying repeatable problems that should become lint rules or other mechanical checks.
---

# Reflect on Changes

Use this skill after meaningful code changes, review passes, workflow updates, or bug-fix loops.

The goal is to turn local knowledge into durable repository knowledge.

## Core Outcomes

1. Update the docs, commands, or skills that became stale because of the change.
2. Identify repeatable problems that should be enforced mechanically instead of re-reviewed manually.
3. Either implement the enforcement immediately when it is low-risk and clearly scoped, or record a concrete follow-up.

## Workflow

1. Gather the learning scope.
   - Inspect the current diff against `main` plus any untracked files that matter.
   - Read any rolling review artifacts if present.
   - Read touched docs, commands, skills, configs, and validation scripts before concluding they are up to date.
2. Determine what repository knowledge changed.
   - conventions
   - command behavior
   - skill behavior
   - validation workflow
   - developer expectations
3. Update the source of truth directly.
   - Prefer updating the most specific doc first, then update summaries.
   - Keep related docs and affected command/skill files in sync.
4. Mine repeated problems from the change and review history.
   - Look for issues that appeared more than once in the same task or across related files.
   - Treat "we had to fix this manually again" as a strong signal for mechanical enforcement.
5. Choose the right enforcement layer.
   - ESLint: AST-shaped TS/JS rules and import/code-organization invariants.
   - Nx/module-boundary config: project graph and tag dependency rules.
   - Semgrep: security patterns and broader code-shape checks.
   - Knip: dead code, unused exports, dependency drift.
   - Custom script/CI check: docs freshness, repo metadata, or non-AST structural validation.
   - Docs only: judgment-heavy guidance that should not be mechanized yet.
6. Act on the best candidates.
   - Implement low-risk, well-understood enforcement immediately when it fits the current task.
   - Otherwise add a concrete follow-up entry with:
     - the repeatable problem
     - recommended enforcement layer
     - why it is worth mechanizing
     - any expected false-positive risk or rollout caveat
7. Summarize what was learned.
   - docs updated
   - commands/skills updated
   - enforcement added
   - follow-up lint-rule or validation candidates deferred

## Heuristics

- If a rule matters and can be checked mechanically, prefer enforcement over prose.
- If the same review comment would likely be written again, propose a lint rule or validation script.
- If the rule is still ambiguous or product-dependent, document it instead of enforcing it.
- Do not add noisy checks just because something is theoretically automatable.

## Output

Return a concise learning summary with these sections:

- `Docs updated`
- `Workflow or skill changes`
- `Mechanical enforcement added`
- `Deferred lint-rule candidates`

If nothing needed updating, say that explicitly and explain why the current docs/checks already cover the change.
