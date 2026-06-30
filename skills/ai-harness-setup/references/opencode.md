# OpenCode and ocx

Read this file when the repo contains `opencode.jsonc`, `.opencode/`, or the user explicitly wants OpenCode support.

When the repo also supports Cursor, GitHub Copilot, or Claude Code, install reusable skills with `apm install <package>` and keep `.opencode/` focused on OpenCode-specific runtime config, plugins, commands, and `ocx` wiring.

## Files to Manage

- `.agents/skills/` - shared repo-local installed skills when the CLI materializes OpenCode, Cursor, and GitHub Copilot targets there
- `opencode.jsonc` - root OpenCode runtime config
- `.opencode/package.json` - dependencies for repo-local OpenCode plugins
- `.opencode/ocx.jsonc` - registry configuration for `ocx`
- `.opencode/worktree.jsonc` - worktree plugin sync and hook behavior
- `.opencode/plugin/` - repo-local plugin code
- `.opencode/command/` and `.opencode/commands/` - reusable command definitions

When APM is present, it also deploys installed skills to `.opencode/skills/` when the `.opencode/` directory exists. Treat that directory as APM-managed output and keep it aligned through `apm install`.

## Root Config Baseline

When establishing an OpenCode baseline, preserve existing config and merge in:

- plugin packages for DCP, plannotator, and subtask2
- provider or permission policies already established by the team

A baseline root `opencode.jsonc` should include:

- plugins:
  - `@tarquinen/opencode-dcp@latest`
  - `@plannotator/opencode@latest`
  - `@spoons-and-mirrors/subtask2@latest`
- `permission.task = deny`
- `disabled_providers = ["azure"]`

Never replace the entire file if the repo already has custom MCP entries, auth configuration, or provider restrictions.

## MCP Servers

MCP servers are declared centrally in `apm.yml` under `dependencies.mcp` and installed through `apm install`. See `references/mcp-servers.md` for the baseline defaults, stack-driven discovery workflow using `apm mcp search`, and APM dependency format.

Do not declare MCP servers directly in `opencode.jsonc`. Use `apm.yml` as the single source of truth so that APM handles wiring across all targets (OpenCode, Cursor, Copilot) and keeps configuration portable.

If the repo already has MCP entries in `opencode.jsonc` or `.opencode/` config files, migrate them into `apm.yml` `dependencies.mcp` during setup. See the "Detect Existing MCP Configurations" section in `references/mcp-servers.md` for the migration workflow.

## Local Plugin Baseline

When `.opencode/plugin/` exists:

- keep `.opencode/package.json` in sync with plugin imports
- run `bun install` in `.opencode/`
- do not assume root `package.json` dependencies satisfy `.opencode` plugins

Repo-local OpenCode plugins often depend on packages such as:

- `@opencode-ai/plugin`
- `jsonc-parser`
- `zod`
- `node-notifier`
- `detect-terminal`
- `unique-names-generator`

An `.opencode/` setup may also include:

- `.opencode/ocx.jsonc` with the `kdco` registry
- repo-local plugins in `.opencode/plugin/`
- command definitions in `.opencode/command/` and `.opencode/commands/`
- `.opencode/package.json` with `@opencode-ai/plugin` and helper deps

## ocx Baseline

If the repo uses `ocx`, ensure:

- `.opencode/ocx.jsonc` has the correct registry definitions
- `.opencode/worktree.jsonc` exists and matches the repo's worktree sync expectations
- contributors can run `ocx --version` and `bun install` inside `.opencode/`

## Verification

- `bun install` succeeds in `.opencode/`
- install commands avoid hard-coded target flags unless the user explicitly requests a non-default target
- `.agents/skills/` contains the shared installed skills when the CLI materializes those selected targets there
- required plugin packages are present
- local plugin imports resolve
- JSONC files remain valid after editing
- OpenCode startup sees the intended plugin and MCP inventory
- MCP servers are declared in `apm.yml`, not in `opencode.jsonc`
- any pre-existing MCP entries from `opencode.jsonc` have been migrated to `apm.yml`
