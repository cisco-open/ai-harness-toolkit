---
name: code-review
description: Stack-aware code review orchestrator that detects tech stacks from changed files, dispatches parallel review lanes to subagents with prescriptive instructions, synthesizes findings, and runs a fix loop for deterministic fixes. Supports TypeScript/JavaScript, Python, and Java.
compatibility: Works in any coding harness that supports subagent/task dispatch (OpenCode, Cursor, Copilot, Claude Code). Requires git.
metadata:
  version: "1.0.0"
---

# Code Review

Stack-aware code review orchestrator. Detects the tech stack from changed files, validates companion skills, dispatches parallel review lanes, synthesizes findings, runs a fix loop, and optionally reflects.

## How To Use This Skill

Run this skill on a feature branch with uncommitted or committed changes. The orchestrator will:

1. Validate that required companion skills are installed
2. Scope the review from `git diff` and `git status`
3. Detect stacks and route review lanes
4. Dispatch parallel subagents with prescriptive instructions
5. Synthesize findings into a review artifact
6. Run a fix loop for safe deterministic fixes
7. Optionally reflect on changes

The review artifact is written to `tmp/review/<branch>-review.md`.

## Phase 0: Validate Companion Skills

Check that required companion skills are installed before dispatching lanes. Inspect these directories for installed skills:

- `skills/`
- `.agents/skills/`
- `.claude/skills/`
- `.opencode/skills/`
- `.cursor/skills/`
- `.github/skills/`

For each detected stack, load its stack reference file (`stacks/<stack>.md`) and check the companion skill mappings section. For each required skill:

1. Check if it exists in any of the skill directories above
2. If missing, record it with its `apm install` command

**If all skills are installed:** Proceed to Phase 1 without warnings.

**If skills are missing:** Display which skills are missing, provide `apm install` commands for each, and ask the user whether to:
- Install the missing skills now and retry validation
- Continue with native fallback for affected lanes
- Abort the review

## Phase 1: Scope Detection

Determine the review scope from changed files:

```bash
BASE_BRANCH=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
git diff "${BASE_BRANCH:-main}"...HEAD --name-only
git status --porcelain
```

Combine both outputs to get the full list of changed files. Detect the base branch from `origin/HEAD`, falling back to `main` only when that cannot be resolved.

Create the review artifact directory and file:

```bash
mkdir -p tmp/review
```

Write the initial review artifact to `tmp/review/<branch>-review.md` using the format defined in `references/review-artifact-format.md`.

**If no changes are detected:** Report "No changes to review" and exit.

## Phase 2: Detect Stacks and Route Lanes

Match changed file extensions to stack reference files:

| Extensions | Stack Reference |
|---|---|
| `*.ts`, `*.tsx`, `*.js`, `*.jsx` | `stacks/javascript-typescript.md` |
| `*.py` | `stacks/python.md` |
| `*.java`, `*.kt` | `stacks/java.md` |

For each activated stack:
1. Load the stack reference file
2. Filter changed files to only those matching the stack
3. Check framework detection signals from the stack reference
4. Determine which lanes to activate based on the stack and detected frameworks

**Polyglot repos:** If files span multiple stacks, load all matching stack references and activate lanes for each. Each lane receives only files relevant to its stack.

## Phase 3: Dispatch Parallel Subagents

For each activated lane, dispatch a subagent with prescriptive instructions. Each subagent receives:

- **File scope**: Only the changed files relevant to its stack (not the entire diff)
- **Deterministic commands**: Exact commands to run from the stack reference
- **Companion skills**: Which skills to use and how
- **Native focus areas**: What patterns to look for in manual review

### Lane Types

Each stack defines content for these lane types:

1. **Quick Checks** -- Lint, type-check, format verification. Fast deterministic commands.
2. **Extended Validation** -- Tests, coverage, SAST, dependency audit. Slower but still deterministic.
3. **Security** -- Security-focused review using `security-review` companion skill and SAST tools.
4. **Framework** -- Framework-specific review using framework companion skills (React, Angular, FastAPI, Django, Spring Boot).
5. **Performance** -- Performance pattern review using native focus areas and companion skills.
6. **Testing** -- Test quality and coverage review using testing companion skills.

Lanes are independent -- each can execute without depending on results from other lanes. Dispatch them as parallel tasks/subagents where the harness supports it.

### Subagent Instruction Template

For each subagent, provide instructions in this format:

```
## Review Lane: <lane-name> (<stack>)

### Scope
Files to review:
<file list>

### Deterministic Commands
Run these commands and report results:
<commands from stack reference>

### Companion Skills
Use these skills for guided review:
<skill names and what to use them for>

### Native Review Focus
If companion skills are not available, focus on:
<focus areas from stack reference>

### Output Format
Report findings as:
- **file:line** -- severity (error|warning|info) -- description
- Classify each as: auto-fixable | needs-human
```

## Phase 4: Synthesize Findings

After all subagents complete:

1. Collect all findings from all lanes
2. Merge findings that reference the same file and line from different lanes
3. Deduplicate overlapping issues (prefer the more specific finding)
4. Classify each finding:
   - **auto-fixable**: A deterministic tool fix exists (lint auto-fix, format)
   - **needs-human**: Requires manual review or code change
5. Group findings by severity: error, warning, info
6. Update the review artifact at `tmp/review/<branch>-review.md`

## Phase 5: Fix Loop

Apply safe deterministic fixes and rerun impacted checks. Read `references/fix-loop-protocol.md` for the full protocol.

Summary:

1. Collect auto-fixable findings
2. Apply deterministic tool fixes (lint `--fix`, format)
3. Rerun only the impacted deterministic checks
4. Record the iteration in the fix loop log
5. Repeat until:
   - All impacted checks pass (success)
   - No progress made in an iteration (stall -- report remaining as needs-human)
   - Iteration limit reached (6 iterations -- report remaining as needs-human)

**Never auto-apply non-deterministic fixes.** AI-suggested code changes are reported but not applied automatically.

## Phase 6: Reflect

Optionally invoke the `reflect-on-changes` skill if installed:

1. Check if `reflect-on-changes` exists in any skill directory
2. If installed, invoke it with the review findings to update docs, conventions, or skills that may be stale
3. If not installed, skip without error

## Reference Map

| Reference | When to Read |
|---|---|
| `references/review-artifact-format.md` | When creating or updating the review artifact |
| `references/fix-loop-protocol.md` | When running the fix loop in Phase 5 |
| `stacks/javascript-typescript.md` | When TypeScript/JavaScript files are in the diff |
| `stacks/python.md` | When Python files are in the diff |
| `stacks/java.md` | When Java/Kotlin files are in the diff |
