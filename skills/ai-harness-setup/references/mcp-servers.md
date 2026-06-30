# MCP Server Setup

Use this file when adding MCP servers to `apm.yml` as part of the harness setup. MCP servers give agents runtime access to external tools and services. Only add servers that match the repo's detected tech stack.

## Package-Provided Defaults

- `stack-frontend`, `stack-react`, and `stack-angular` already provide Chrome DevTools.
- Do not add those servers again as separate MCP installs when the matching package is already selected.
- Treat these package-provided MCP servers as the starting point. Add more MCP servers when the detected stack, infrastructure, or workflow still needs them.

## Detect Existing MCP Configurations

Before adding anything new, inspect the repo for MCP entries that already exist in tool-specific config files. Treat `apm.yml` as the single source of truth and migrate existing MCP declarations into `dependencies.mcp` instead of leaving them scattered across runtime-specific config files.

Common places to inspect:
- `opencode.jsonc`
- `.opencode/*.jsonc`
- `.cursor/`
- `.claude/settings.json`
- any checked-in agent or IDE config that contains `mcp`, `mcpServers`, or server definitions

When migrating existing entries:
1. Preserve the existing server definition.
2. Re-express it in `apm.yml` under `dependencies.mcp`.
3. Prefer a registry reference when the server exists in the APM registry.
4. Use `registry: false` when the existing server is private or not available in the registry.

## Discover Extra MCP Servers

For servers that are not already provided by a selected package, use `apm mcp search <term>` based on the detected stack.

Common search themes:
- `playwright`
- `postgres`
- `mysql`
- `sentry`
- `kubernetes`
- `terraform`
- `langgraph`
- `langchain`
- `ai`

Only add servers that provide clear value for the repo's actual workflow. Good examples include Cisco Design System for Cisco UI repos, Playwright for browser automation, or Postgres for database-heavy backends.

Typical workflow:
1. account for any MCP servers already bundled by the selected package
2. migrate any repo-local MCP config into `apm.yml`
3. run `apm mcp search <term>` for the detected frameworks, databases, cloud providers, or AI runtimes that still need coverage
4. add only the extra servers that fill real workflow gaps

## Install and Guardrails

- MCP servers are declared under `dependencies.mcp` in `apm.yml` and installed through `apm install`.
- Use `apm install --only=mcp` when you need to sync only MCP servers.
- Use `apm install --dry-run` to preview what would be configured.
- Prefer `gh` over a GitHub MCP server for GitHub repo, issue, and pull request operations.
- Preserve existing MCP entries unless the user explicitly asks for cleanup.
- Do not bulk-add search results. Select only the MCP servers that match the repo's actual workflow.
- Document required environment variables for any self-defined server.
