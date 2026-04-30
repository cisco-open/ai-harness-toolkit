# AI Tooling Bootstrap

Use this file when installing workflow skills and repo-local AI automation.

## Prerequisites

Before installing skills with APM:

- **APM installed**: install it with `curl -sSL https://aka.ms/apm-unix | sh` on macOS or Linux, or the matching Windows installer when needed.
- **Verify APM**: run `apm --version` before modifying the repo.
- **APM auth for private GitHub repos**: use `GITHUB_CLI_PAT` or `GITHUB_TOKEN` when APM needs access to private sources.
- **`npx skills find` is optional and search-only**: use it only for broader ecosystem discovery when `ai-harness-toolkit` or local sources do not already cover the need.
- **`package.json` requirement for discovery only**: if you need `npx skills find` in a non-Node repo, run it from a directory that has a `package.json`, or create a minimal temporary one if needed.

## Initialize APM

1. inspect the repo for `apm.yml`, `apm.lock.yaml`, `apm_modules/`, and APM-managed skill directories
2. if `apm.yml` is missing, run `apm init --yes` at the repo root (always use `--yes` to avoid interactive prompts)
3. verify `apm_modules/` is in `.gitignore` (`apm init` adds it automatically; if not present, add it manually)
4. if `apm.yml` already exists, read it before adding new dependencies
5. use `apm install <package>` for skill installation so the manifest and lockfile are updated together
6. run `apm install` after manual manifest changes when you need to sync the workspace to the declared dependency set

## Install Order

1. audit local skills already vendored in repo-local skill directories
2. verify `apm` is available and initialize `apm.yml` if needed
3. install language-agnostic workflow skills with `apm install`
4. review `ai-harness-toolkit` and other known sources for tech-stack-specific skills based on detection results from step 1 of the main workflow
5. use `npx skills find` only when broader discovery is still needed, then install the selected package with `apm install`
6. install only the stack-specific skills that match the detected tech stack
7. add MCP servers to `apm.yml` using `references/mcp-servers.md` -- baseline defaults first, then `apm mcp search` for stack-driven discovery
8. run `apm install` to sync all APM packages and MCP servers together

## Language-Agnostic Workflow Skills

These apply to any repo regardless of language or framework. Install them first:

- `create-pull-request-with-reviewers`
- `gh-pr-comment-resolution`
- `reflect-on-changes`

For security review coverage, pull the software-security skill from Project CodeGuard:

- `project-codeguard/rules/skills/software-security`

## Install Sources

Install repo-local skills from the current repository when needed.

When pulling from `https://github.com/cisco-open/ai-harness-toolkit`:
- Review the available skills first by browsing the repo's `skills/` tree or a local checkout.
- Install only skills that are applicable to this repo's detected stack and workflow needs.
- Do not bulk-install everything. A Python backend repo does not need React review skills. A frontend-only repo does not need LangGraph skills.
- For OpenCode, Cursor, GitHub Copilot, and Claude Code repos, target those harnesses with `apm install <package> -t opencode -t cursor -t copilot -t claude`.

Use Project CodeGuard as the preferred external source for security review rules and software-security skill content.

Examples:

```bash
apm init --yes
apm install cisco-open/ai-harness-toolkit/skills/create-pull-request-with-reviewers -t opencode -t cursor -t copilot -t claude
apm install cisco-open/ai-harness-toolkit/skills/reflect-on-changes -t opencode -t cursor -t copilot -t claude
apm install project-codeguard/rules/skills/software-security -t opencode -t cursor -t copilot -t claude
npx skills find langgraph
npx skills find copilotkit
npx skills find semgrep
apm install github/awesome-copilot/skills/review-and-refactor -t opencode -t cursor -t copilot
# Discover MCP servers matching the detected stack
apm mcp search playwright
apm mcp search postgres
# Then add selected servers to apm.yml and install
apm install
apm deps list
apm deps tree
```

Use local or repository sources when the exact skill already exists here, then `ai-harness-toolkit` for Cisco-oriented gaps, and broader ecosystem installs when it still does not exist.

**Auth note:** If access to `ai-harness-toolkit` fails, verify GitHub authentication and that `GITHUB_CLI_PAT` or `GITHUB_TOKEN` is available to APM. If the user lacks access, skip these installs and log a warning rather than failing silently.

## Discovery Strategy

Use this order:

1. inspect repo-local skill directories and existing APM dependencies first
2. browse `ai-harness-toolkit` for matching Cisco or repo-standard skills
3. use `npx skills find <query>` only for broader ecosystem discovery
4. install the chosen result with `apm install <package>`

If `npx skills find` returns a skill that is already available through `ai-harness-toolkit` or a local source, prefer the existing curated source.

## Tech-Stack Search Strategy

After the language-agnostic skills are installed, use the detection results from the main workflow's step 1 to search for matching skills. Only install skills that match the detected stack.

Stack signals to match:

- framework markers in manifests and lockfiles
- build tooling configs
- CI workflows
- AI runtime dependencies such as LangChain, LangGraph, CopilotKit, OpenAI SDKs, MCP usage

Useful search themes (use only those relevant to the detected stack):

- `react review` (if React detected)
- `frontend testing` (if frontend framework detected)
- `langgraph` (if LangGraph detected)
- `copilotkit` (if CopilotKit detected)
- `security review` (always applicable)
- `performance` (when relevant to detected framework)
- `nx workspace` (if Nx detected)

## What to Commit

Deployed files should be committed as part of the repo:

- **Commit:** `apm.yml`, `apm.lock.yaml`, and all deployed files in `.github/` (`prompts/`, `skills/`, `instructions/`, `agents/`, `hooks/`) and `.claude/` (`agents/`, `commands/`, `skills/`, `hooks/`).
- **Gitignore:** `apm_modules/` only (APM adds this to `.gitignore` automatically via `apm init`).

Committing deployed files ensures every contributor and Copilot on github.com gets agent context without needing to run `apm install`. After each `apm install`, stage and commit the newly deployed or updated files alongside `apm.yml` and `apm.lock.yaml`.

## CI Drift Check

To catch cases where someone updates `apm.yml` without re-running `apm install`, add a CI step that verifies deployed files are in sync:

```yaml
- name: Verify APM deployed files are in sync
  run: |
    apm install
    PATHS=".github/"
    if [ -d ".claude/" ]; then
      PATHS="$PATHS .claude/"
    fi
    if [ -n "$(git status --porcelain -- $PATHS)" ]; then
      echo "APM deployed files are out of date. Run 'apm install' and commit the changes."
      git status --porcelain -- $PATHS
      exit 1
    fi
```

This replaces gitignore-based management. If a `.claude/` directory does not exist in the repo, omit it from the check.

## Verification

- `apm deps list` and `apm deps tree` show the intended skills
- `apm.yml` includes the expected dependencies
- `apm.lock.yaml` is present when installs succeeded
- installed skills match the actual repo stack and workflow
- no skills were installed that do not match the detected stack
- deployed files in `.github/` and `.claude/` are committed alongside `apm.yml` and `apm.lock.yaml`
- `apm_modules/` is in `.gitignore`
- CI drift check is wired (if CI exists) to verify deployed files stay in sync
