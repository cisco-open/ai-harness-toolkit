---
name: commit-and-push-changes
description: Commit and push changes with exclusions and a generated commit message
compatibility: Requires git to be installed
metadata:
  version: "1.0"
---

# Commit and Push Changes

Commit all changes except specified files, with an auto-generated or user-provided commit message.

## Instructions

**Step 1:** Show the current state of changes:

```bash
git status --short
```

**Step 2:** Identify files to exclude from the commit.

**Always exclude:**
- All files in `.cursor/` folders
- Files modified by external processes (not by us)

**APM and OpenSpec deployed content:**

Repos using APM or OpenSpec will have deployed content under `.github/` (e.g., `.github/skills/`, `.github/prompts/`, `.github/instructions/`, `.github/agents/`, `.github/hooks/`) and possibly `.claude/`. These files **should be committed** so that every contributor and Copilot on github.com gets agent context without running `apm install`. Only `apm_modules/` should be gitignored.

If `apm install` was run during this session and new deployed files appeared, **include them in the commit**. If deployed files appear in `git status` but were not expected, run `apm install` to verify they are in sync with `apm.yml` before committing.

To detect unintended modifications, compare the changed files against the conversation history. If a file appears in `git status` but was **not edited during this session**, treat it as potentially unintended. For APM/OpenSpec-managed repos, keep `.github/` and `.claude/` changes that come from `apm install` and only exclude `.github/` files that are still unexpected after re-running `apm install`. For non-APM repos, exclude unexpected `.github/` files that are clearly out of scope for this task.

**Step 3:** Stage only the files we intentionally modified:

```bash
git add <file1> <file2> ...
```

Do **NOT** use `git add -A` or `git add .` as this will stage unintended files.

**Step 4:** Generate the commit message.

1. **Extract the Jira key** (try in order until one succeeds):

```bash
git branch --show-current | grep -oE '[A-Z]{2,}-[0-9]+'
git log --oneline -10 | grep -oE '[A-Z]{2,}-[0-9]+' | head -1
```

If no Jira key is found, **ask the user** for the story key. If the user confirms no Jira key is needed, proceed without one.

2. **Generate the descriptive message** based on the work done during this session (from conversation context), not from parsing git diff output.

3. **Compose the final message** in this format:

```bash
# With Jira key:
<JIRA-KEY>: <descriptive message>

# Without Jira key (when user confirms none is needed):
<type>: <descriptive message>
```

Where `<type>` is one of: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `ci`.

**Step 5:** Present the commit details for confirmation:

```bash
📝 Commit Preview

Files to commit:
  - file1.py
  - file2.py

Excluded files (auto):
  - .cursor/* (IDE configuration)
  - package-lock.json (not modified by us)

Commit message:
  EADL-1234: Add retry logic with exponential backoff

Proceed with commit? [Y/n]
```

**Step 6:** After user confirms, create the commit and push:

```bash
git commit -m "<COMMIT_MESSAGE>"
git push
```

**Step 7:** Show the result:

```bash
git log -1 --oneline
```
