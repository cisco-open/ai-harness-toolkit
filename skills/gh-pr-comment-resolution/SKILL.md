---
name: gh-pr-comment-resolution
description: Use for workflows that fetch GitHub pull request review comments with the gh CLI, identify Copilot review threads, and resolve them after code changes. Trigger when asked to review/resolve Copilot PR comments, fetch PR review threads, or document how to close review threads via gh api graphql.
compatibility: Requires gh CLI to be installed and authenticated
---

# GH PR Comment Resolution

## Overview

Use gh CLI + GraphQL to find Copilot review comments, map them to files, and resolve threads once the code is fixed. Provide a deterministic workflow for fetching comments, fixing issues, and closing review threads.

## Workflow

### 1) Identify the PR and review threads

- Get the PR number for the current branch:

```bash
gh pr view --json number,title,url,headRefName
```

- Fetch review threads (includes thread ids for resolving):

```bash
gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner, name:$repo){pullRequest(number:$number){reviewThreads(first:50){nodes{id,isResolved,comments(first:20){nodes{id,body,author{login},path,position}}}}}}}' -f owner='<OWNER>' -f repo='<REPO>' -F number=<PR_NUMBER>
```

- Optionally list classic review comments for easier scanning:

```bash
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments
```

### 2) Triage Copilot comments

- Filter by `author.login` (e.g., `copilot-pull-request-reviewer[bot]`).
- Group comments by `path` and map to files in the workspace.
- For each comment, decide: fix in code or mark as already addressed.

### 3) Apply fixes

- Make code changes in the referenced file(s).
- If the file is vendored or patched, update the patch script instead of the vendored file.

### 4) Resolve review threads

- Resolve each thread via GraphQL:

```bash
gh api graphql -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id,isResolved}}}' -F threadId='<THREAD_ID>'
```

- If a comment was already addressed, reply with context (optional) and resolve the thread.

### 5) Report back

- Summarize the fixes and list any comments resolved as "already handled".
- Suggest tests if relevant.

## Notes

- Prefer GraphQL for review thread resolution because REST review comments do not expose thread ids.
- If reviewThreads exceed 50, paginate with `reviewThreads(first:50, after: <cursor>)`.
