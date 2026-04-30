# MCP Server Setup

Use this file when adding MCP servers to `apm.yml` as part of the harness setup. MCP servers give agents runtime access to external tools and services. Only add servers that match the repo's detected tech stack.

## APM MCP Dependency Format

MCP servers are declared under `dependencies.mcp` in `apm.yml`. APM supports three forms:

**String reference** (registry-resolved, preferred when available):

```yaml
mcp:
  - microsoft/playwright-mcp
```

**Object with overlays** (registry-resolved with customizations):

```yaml
mcp:
  - name: microsoft/playwright-mcp
    transport: stdio
    env:
      PLAYWRIGHT_HEADLESS: "1"
```

**Self-defined server** (private or not in the registry):

```yaml
mcp:
  - name: my-private-server
    registry: false
    transport: http
    url: "${MY_SERVER_URL}"
    env:
      MY_SERVER_TOKEN: "${MY_SERVER_TOKEN}"
```

For the full format reference, see https://microsoft.github.io/apm/guides/dependencies/#mcp-dependency-formats

## UI App MCP Servers

Add these when the repo is a frontend or full-stack application with a browser-facing UI:

| MCP Server | Registry Name | Add when... |
|------------|---------------|-------------|
| Chrome DevTools | `io.github.ChromeDevTools/chrome-devtools-mcp` | React, Angular, Next.js, Vue, Svelte, or any browser-rendered UI |

Detection signals for UI apps: `react`, `react-dom`, `@angular/core`, `next`, `vue`, `svelte`, `@vitejs/plugin-react`, `vite` with frontend framework, `app/` or `pages/` or `src/components/` directory patterns, Electron, Tauri.


## Detect Existing MCP Configurations

Before adding new MCP servers, inspect the repo for MCP entries that already exist in tool-specific config files. Treat `apm.yml` as the single source of truth and migrate existing MCP declarations into `dependencies.mcp` instead of leaving them scattered across runtime-specific config files.

Common places to inspect:

- `opencode.jsonc`
- `.opencode/*.jsonc`
- `.cursor/`
- `.claude/settings.json`
- any checked-in agent or IDE config that contains `mcp`, `mcpServers`, or server definitions

Migration workflow:

1. detect any existing MCP server declarations in repo-local config files
2. preserve those server definitions and re-express them in `apm.yml` `dependencies.mcp`
3. prefer registry references when the server exists in the APM registry
4. use `registry: false` when the existing server is private or not available in the registry
5. after migrating, let `apm install` materialize the target-specific runtime wiring

Do not drop existing MCP servers just because they were defined outside `apm.yml`. Carry them forward into APM-managed configuration unless the user asks for cleanup.

## Stack-Driven MCP Discovery

After adding any platform-specific and UI-specific servers justified by detection, use `apm mcp search` to find additional servers that match the detected tech stack from step 1 of the main workflow. Run searches based on the frameworks, tools, and infrastructure detected in the repo.

**Discovery workflow:**

1. Identify the key tech stack terms from detection (frameworks, databases, cloud providers, CI systems, monitoring tools, etc.)
2. Run `apm mcp search <term>` for each relevant term
3. Review the results and select only servers that provide clear value for the repo's actual workflow
4. Add selected servers to `apm.yml` using the appropriate format

**Example search terms based on detection signals:**

| Detected in repo | Search terms to try |
|-------------------|-------------------|
| Playwright | `playwright` |
| PostgreSQL, MySQL, or other databases | `postgres`, `mysql`, `database` |
| Sentry or error monitoring | `sentry` |
| Kubernetes or container orchestration | `kubernetes` |
| Terraform or infrastructure-as-code | `terraform` |
| LangChain, LangGraph, or AI agent frameworks | `langchain`, `langgraph`, `ai` |

This is not an exhaustive list. Use the detection results to drive the searches. If the repo uses a notable tool or service, search for it.

Do not add GitHub MCP as part of this setup. For repository, issue, and pull request automation, prefer the `gh` CLI instead of installing a GitHub MCP server.

## Installation

MCP servers are installed through `apm install` alongside APM package dependencies. After declaring servers in `apm.yml`:

```bash
# Install all dependencies including MCP servers
apm install

# Install only MCP servers (skip APM packages)
apm install --only=mcp

# Preview what would be configured
apm install --dry-run
```

## Guardrails

- **Only add servers that match detected signals.** Do not speculatively add servers for tools the repo does not use.
- **Self-defined servers require env vars.** Document which environment variables are needed for each self-defined server so contributors know what to configure.
- **Do not bulk-add from search results.** Review each search result and only select servers that provide clear value.
- **Prefer `gh` over GitHub MCP.** Do not add the GitHub MCP server as part of this harness setup. Use the `gh` CLI for GitHub repository, issue, and pull request operations.
- **Preserve existing MCP entries.** If `apm.yml` already has MCP servers, do not remove or replace them. Add new ones alongside existing entries.
- **Migrate repo-local MCP config into APM.** If the repo already declares MCP servers in `opencode.jsonc`, `.opencode/`, Cursor, Claude, or other checked-in config, move those definitions into `apm.yml` instead of maintaining multiple sources of truth.
- **Log what was added and why.** When summarizing the setup, list each MCP server that was added and the detection signal that justified it.
