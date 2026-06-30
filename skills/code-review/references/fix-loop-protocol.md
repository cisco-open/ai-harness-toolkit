# Fix Loop Protocol

Rules for the automated fix loop in Phase 5 of the code review orchestrator.

## Purpose

Apply safe deterministic fixes automatically and rerun impacted checks. This reduces manual effort for mechanical issues (lint violations, format drift) while keeping human judgment for non-trivial changes.

## What Is Safe to Auto-Fix

### Safe (deterministic tool fixes)

These tools produce deterministic, reproducible output. The same input always produces the same fix.

| Tool | Command | Scope |
|---|---|---|
| ESLint | `eslint --fix <files>` | Lint rule auto-fixes |
| Ruff | `ruff check --fix <files>` | Python lint auto-fixes |
| Ruff format | `ruff format <files>` | Python formatting |
| Prettier | `prettier --write <files>` | JS/TS formatting |
| Checkstyle (with format) | IDE-assisted or plugin | Java style fixes |
| gofmt | `gofmt -w <files>` | Go formatting |

### Not Safe (do not auto-apply)

These require human judgment. Report them but never apply automatically.

| Category | Example | Why Not Safe |
|---|---|---|
| AI-suggested code changes | "Consider using a map instead of a loop" | Non-deterministic, may change behavior |
| Complex refactoring | "Extract this into a separate function" | Changes architecture, needs design judgment |
| Security fixes | "Add input validation here" | Requires understanding of trust boundaries |
| Test additions | "Add a test for this edge case" | Requires understanding of expected behavior |
| Dependency updates | "Upgrade lodash to fix CVE" | May introduce breaking changes |

## Loop Mechanics

```
iteration = 0
max_iterations = 6

while iteration < max_iterations:
    iteration += 1

    1. Collect auto-fixable findings from the review artifact
    2. If none remain: EXIT (clean)

    3. Apply deterministic tool fixes:
       - Run each tool's --fix command on affected files
       - Stage the changes (do not commit)

    4. Rerun ONLY the impacted deterministic checks:
       - If ESLint fixed files → rerun ESLint on those files
       - If ruff fixed files → rerun ruff check on those files
       - Do NOT rerun unrelated checks

    5. Count remaining findings after rerun
    6. If findings == 0: EXIT (clean)
    7. If findings >= previous iteration's count: EXIT (stalled)
    8. Update the review artifact with new state
    9. Log this iteration in the Fix Loop Log section

EXIT (limit-reached) if loop ends without clean or stall
```

## Termination Conditions

| Condition | When | Action |
|---|---|---|
| **Clean** | All impacted checks pass after a fix iteration | Report success, update artifact |
| **Stalled** | A fix iteration does not reduce finding count | Stop, report remaining as needs-human |
| **Limit reached** | 6 iterations completed | Stop, report remaining as needs-human |

## Iteration Limit

**Maximum iterations: 6**

This cap prevents infinite loops when fixes cause cascading issues (e.g., fixing one lint rule triggers another). Six iterations is enough for most convergent fix chains.

## What to Log

Each iteration records in the review artifact:

- **Iteration number**
- **Fixes applied**: Which tools ran, on which files
- **Commands rerun**: Which checks were re-executed
- **Result**: Pass/fail, remaining finding count
- **Delta**: How many findings were resolved vs. previous iteration

## Guardrails

1. **Never modify files outside the diff scope.** Only fix files that were already changed in the branch.
2. **Never apply unsafe fixes.** If a tool's `--fix` flag includes unsafe transformations (e.g., `ruff check --unsafe-fixes`), exclude those.
3. **Never commit automatically.** Stage fixes but let the user review and commit.
4. **Track all changes.** Every file modified by the fix loop must be recorded in the log.
5. **Preserve user changes.** If the user made intentional formatting or style choices, respect them. Only fix clear violations.
