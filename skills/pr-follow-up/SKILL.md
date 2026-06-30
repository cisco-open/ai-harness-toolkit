---
name: pr-follow-up
description: Monitor a GitHub pull request after creation, wait for new review comments, resolve code review comments after fixes, and report CI success or failure. Use when the user wants the backend of the review flow handled after a PR is opened.
compatibility: Requires gh CLI to be installed and authenticated
---

# PR Follow-up

Use this skill after a PR already exists. It is intentionally narrower than full CI self-healing: it watches for review comments, helps resolve them, and reports CI outcome. It does not require extra MCP servers.

## When To Use

- The user says things like:
  - "watch the PR"
  - "handle PR comments as they come in"
  - "monitor this PR and tell me if CI fails"
  - "wait for comments, fix them, then keep watching"
- A PR has already been created, or can be discovered from the current branch.

## Inputs

Accept any of:

- PR number
- PR URL
- current branch with an existing PR

If the PR is ambiguous, determine it with:

```bash
gh pr view --json number,url,title,headRefName,baseRefName
```

## Scope

This skill should:

1. Identify the PR for the current branch.
2. Poll for new PR review comments.
3. When comments appear, fetch the review threads and comment bodies.
4. Present the new comments and ask the user whether to apply fixes.
5. After fixes are validated, ask the user whether to resolve the addressed review threads.
6. Use the `gh-pr-comment-resolution` workflow to resolve review threads after approval.
7. Poll PR checks and notify on success or failure.

This skill should not:

- invent a full CI self-healing flow from scratch
- use unsupported interactive watch commands
- force-push or skip hooks without user approval

## Default Workflow

### 1. Identify the PR

Prefer the PR for the current branch:

```bash
gh pr view --json number,url,title,headRefName,baseRefName,statusCheckRollup
```

If that fails, ask the user which PR to monitor.

### 2. Establish a baseline snapshot

Capture these once at the start:

```bash
gh pr view <PR_NUMBER> --json reviewThreads,statusCheckRollup,url,title
gh pr checks <PR_NUMBER>
```

Track:

- unresolved review thread ids
- current failing checks

### 3. Poll for updates

Use a short repeated loop with one-time status calls, not `--watch` flags.

Recommended calls:

```bash
gh pr view <PR_NUMBER> --json reviewThreads,statusCheckRollup,url,title
gh pr checks <PR_NUMBER>
```

On each poll:

- detect newly added unresolved review threads
- detect newly failed checks
- detect transition to all-green checks

### 4. Handle review comments

When new unresolved review threads appear, treat that as a trigger to enter this flow rather than a stop condition:

1. Fetch full thread details with GraphQL, following the `gh-pr-comment-resolution` skill.
2. Summarize the new comments to the user.
3. Ask the user whether to apply fixes.
4. If the user confirms, implement them.
5. Re-run the smallest relevant validation.
6. Ask the user whether to resolve the addressed review threads.
7. If the user confirms, resolve them.

If you need owner and repo for GraphQL calls, derive them once with:

```bash
gh repo view --json owner,name
```

Use this GraphQL pattern:

```bash
gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:50){nodes{id,isResolved,comments(first:20){nodes{id,body,author{login},path,position}}}}}}}' -f owner='<OWNER>' -f repo='<REPO>' -F number=<PR_NUMBER>
```

Resolve threads with:

```bash
gh api graphql -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id,isResolved}}}' -F threadId='<THREAD_ID>'
```

### 5. Handle CI status

For CI, use read-only polling via `gh pr checks <PR_NUMBER>`.

Default behavior:

- if checks are still pending, keep polling and report that the PR is still running
- if any check fails, report which check failed and stop
- if all required checks pass, report success and stop

If the user separately asks to investigate a failure, then pivot into a deeper CI workflow.

### 6. Stop conditions

Stop and report when any of these is true:

- new review comments were found and surfaced to the user in watch-only mode
- all checks passed
- any check failed
- polling timeout reached

## Good Defaults

- Poll every 60 to 120 seconds.
- Default timeout: 30 minutes unless the user asks for longer.
- Keep updates short and event-driven.
- Only surface deltas since the last poll.

## Reporting Format

When monitoring starts:

```markdown
Watching PR #<number>: <title>
```

When new comments arrive:

```markdown
New PR review comments detected on:
- <file/path>

Next step: inspect threads and ask whether to apply fixes.
```

When CI fails:

```markdown
CI failed on PR #<number>.

Failed checks:
- <check name>
```

When CI succeeds:

```markdown
PR #<number> checks passed.
```

## Recommended Companion Skills

- `gh-pr-comment-resolution` for thread fetch/resolve mechanics
- `create-pull-request-with-reviewers` before this skill, when opening the PR
- a separate CI investigation workflow only when the user explicitly wants deeper failure analysis or auto-fix behavior

## Implementation Guidance

If you later automate this further, keep the separation clean:

- this skill = PR comment + outcome watcher
- `gh-pr-comment-resolution` = review-thread resolution workflow
- deeper CI failure analysis = separate workflow if the repo later adds one
