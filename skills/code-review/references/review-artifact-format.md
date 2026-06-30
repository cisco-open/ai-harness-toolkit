# Review Artifact Format

The review artifact is written to `tmp/review/<branch>-review.md`. This file serves as both working state for the fix loop and a human-readable summary.

## File Path

```
tmp/review/<branch>-review.md
```

Where `<branch>` is the current git branch name (e.g., `feat/add-auth` becomes `tmp/review/feat-add-auth-review.md`). Replace `/` with `-` in branch names.

## Structure

```markdown
# Code Review: <branch>

**Date:** <ISO date>
**Base:** <base-branch>
**Stacks detected:** <comma-separated list>
**Companion skills:** <installed count>/<required count>

## Summary

<1-3 sentence summary of the review scope and key findings>

## Findings by Severity

### Errors (<count>)

| # | File:Line | Lane | Description | Status |
|---|-----------|------|-------------|--------|
| 1 | `src/foo.ts:42` | Quick Checks | ... | auto-fixable / needs-human |

### Warnings (<count>)

| # | File:Line | Lane | Description | Status |
|---|-----------|------|-------------|--------|

### Info (<count>)

| # | File:Line | Lane | Description | Status |
|---|-----------|------|-------------|--------|

## Per-Lane Results

### <Lane Name> (<Stack>)

**Status:** pass | fail | skipped
**Companion skill:** <name> | native fallback
**Deterministic checks:**
- <command>: pass | fail (<detail>)

**Findings:**
- <file:line> -- <description>

### <Next Lane>
...

## Fix Loop Log

### Iteration 1
- **Action:** <what was applied>
- **Commands rerun:** <which checks>
- **Result:** <pass/fail, findings remaining>

### Iteration N
...

**Fix loop outcome:** clean | stalled | limit-reached
**Remaining auto-fixable:** <count>

## Final Status

**Total findings:** <count>
**Auto-fixed:** <count>
**Needs human review:** <count>
**Review result:** clean | has-warnings | has-errors
```

## Section Rules

1. **Summary** -- Written after Phase 4 (synthesis). Updated after Phase 5 (fix loop) if fixes changed the picture.
2. **Findings by Severity** -- Populated during Phase 4. Rows removed or updated during Phase 5 as fixes are applied.
3. **Per-Lane Results** -- One subsection per dispatched lane. Written by each subagent, merged during Phase 4.
4. **Fix Loop Log** -- Appended during Phase 5. Each iteration gets its own subsection.
5. **Final Status** -- Written after Phase 5 completes. This is the definitive review outcome.

## Status Values

- **auto-fixable**: A deterministic tool can fix this (lint `--fix`, format). The fix loop will attempt it.
- **needs-human**: Requires manual review or a code change that cannot be automated safely.
- **fixed**: Was auto-fixable and has been fixed by the fix loop.
