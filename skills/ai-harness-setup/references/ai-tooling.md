# AI Tooling Bootstrap

Use this file when installing package-backed AI tooling with APM.

## Prerequisites

- Install APM with `curl -sSL https://aka.ms/apm-unix | sh` on macOS or Linux, or the matching Windows installer when needed.
- Run `apm --version` before modifying the repository.
- Use `npx skills find` only for broader discovery when repo-local and public curated sources do not already cover the need.

## Initialize APM

1. Inspect the repo for `apm.yml`, `apm.lock.yaml`, `apm_modules/`, and APM-managed skill directories.
2. If `apm.yml` is missing, run `apm init --yes` at the repo root.
3. Verify `apm_modules/` is in `.gitignore`.
4. If `apm.yml` already exists, read it before adding dependencies.

## Package Install Flow

1. Audit repo-local skills and existing APM deps before installing anything new.
2. Choose the matching package from the stack detection results in the main workflow.
3. Resolve the latest published tag for that package with `git ls-remote --tags https://github.com/cisco-open/ai-harness-toolkit "<name>-v*"` and install the newest matching tag.
4. Include protocol fallback in the install command:

```bash
apm install --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/<name>#<name>-v<latest>
```

5. Do not install `core` separately when a `stack-*` package already pulls it transitively.
6. If no package matches the detected stack, install `core` explicitly and layer dynamic stack-specific skills on top.

Use the matching package as the default baseline when one exists. After that, keep the dynamic path available for repo-specific gaps instead of treating the package as the complete install plan.

## Dynamic Fallback

- Even when a matching `stack-*` package exists, dynamic installs are still valid for repo-specific gaps that the package does not cover.
- Browse repo-local and public curated sources first for skills that match the detected stack.
- Use `npx skills find <query>` only as a search mechanism when a needed skill is not already available through repo-local or public curated sources.
- Install only the dynamic skills that match the detected stack or framework gap.

Typical order:
1. install the matching package for the detected stack when one exists
2. inspect what that package already deployed
3. add only the extra dynamic skills needed for uncovered framework, testing, review, or AI-runtime gaps
4. add extra MCP servers based on the detected stack
5. run `apm install` so the manifest, lockfile, deployed files, and MCP wiring stay in sync

## What To Commit

- Commit `apm.yml`, `apm.lock.yaml`, and all deployed files in `.github/`, `.claude/`, and `.opencode/` that APM materializes.
- Keep `apm_modules/` in `.gitignore`.
- After any install, run `apm install` if needed so deployed files and the lockfile stay in sync before committing.

## CI Drift Check

To catch cases where `apm.yml` changes without re-running `apm install`, add a CI step that verifies deployed files are in sync:

```bash
apm install
PATHS=".github/"
if [ -d ".claude/" ]; then
  PATHS="$PATHS .claude/"
fi
if [ -d ".opencode/" ]; then
  PATHS="$PATHS .opencode/"
fi
if [ -n "$(git status --porcelain -- $PATHS)" ]; then
  echo "APM deployed files are out of date. Run 'apm install' and commit the changes."
  git status --porcelain -- $PATHS
  exit 1
fi
```

## Verify

- `apm.yml` includes the expected package and any extra dynamic installs.
- `apm.lock.yaml` is present when installs succeeded.
- Deployed files in `.github/`, `.claude/`, and `.opencode/` are committed alongside `apm.yml` and `apm.lock.yaml`.
- `apm_modules/` is in `.gitignore`.
