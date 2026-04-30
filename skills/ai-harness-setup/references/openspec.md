# OpenSpec Setup

Use this file first when the repo needs OpenSpec installed and wired into the engineering workflow.

## Goal

Make OpenSpec executable in the repo, not just described in prose. After setup, the repo should support:

1. `openspec init`
2. `openspec status`
3. change creation
4. artifact creation in dependency order
5. apply, verify, and archive flow
6. OpenCode commands or skills that expose the workflow ergonomically

## 1. Install the OpenSpec CLI

First verify whether `openspec` is already available:

```bash
openspec --version
```

If that fails, install the CLI globally before doing anything else:

```bash
npm install -g openspec
```

OpenSpec is installed globally because it is a cross-repo workflow tool that should work regardless of the repo's language or package manager. A Python-only repo with no `package.json` still needs access to `openspec`.

After install, verify again:

```bash
openspec --version
```

## 2. Initialize the Repo

Once the CLI exists, initialize OpenSpec in the target repository. The `--tools` flag is required and specifies which AI tools the repo will use:

```bash
openspec init --tools opencode,claude,cursor,github-copilot,codex
```

The `--tools` flag accepts a comma-separated list. Choose the tools that match the team's actual usage. Common valid tool names include:

- `opencode`
- `claude`
- `cursor`
- `github-copilot`
- `codex`

Omit tools the team does not use. At minimum, include the tools the team is actively working with.

Then verify initialization:

```bash
openspec status --json
```

**Note:** On a freshly initialized repo with no change containers yet, `openspec status --json` may return `Error: No changes found` with a non-zero exit code. This is expected behavior, not a failure. To verify initialization succeeded, check that the following directories were created:

```bash
ls openspec/changes/ openspec/specs/
```

If both directories exist, initialization succeeded regardless of the `openspec status` output.

**Empty directory tracking:** Git does not track empty directories. If no initial change or spec exists yet, add `.gitkeep` files so the directory structure is committed:

```bash
touch openspec/changes/.gitkeep openspec/specs/.gitkeep
```

## 3. Add the OpenSpec Workflow Surface

OpenSpec is more useful when the repo exposes the workflow through local commands or skills.

For repos that expose OpenSpec through local commands or skills, add or verify these entry points:

- `/opsx-explore`
- `/opsx-new`
- `/opsx-continue`
- `/opsx-ff`
- `/opsx-apply`
- `/opsx-verify`
- `/opsx-archive`

In an OpenCode repo, these usually live in:

- `.opencode/command/opsx-*.md`
- `.opencode/skills/openspec-*/`

If the repo already vendors these, preserve and extend them rather than replacing them.

## 4. Verify the Expected Change Shape

Create or inspect one change container and confirm the workflow shape matches the repo's intended artifact chain.

Default artifact order:

```text
proposal -> specs/<capability>/spec.md -> design -> tasks
```

The repo should support change containers like:

```text
openspec/changes/<name>/
```

## 5. Document How the Repo Uses OpenSpec

Add durable pointers so contributors know when and how to use it:

- `CONTRIBUTING.md` should explain when OpenSpec is required and list the top-level commands
- `AGENTS.md` should point agents at the relevant workflow docs
- the repo's workflow doc should explain where OpenSpec fits in planning, implementation, and verification

## 6. Verification Checklist

- `openspec --version` succeeds
- `openspec init` has been run for the repo (check that `openspec/changes/` and `openspec/specs/` exist)
- OpenCode command or skill wrappers exist if the repo uses OpenCode
- non-trivial changes have a documented OpenSpec entry path
