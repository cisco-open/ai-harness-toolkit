# Dependabot Configuration

Use this file when adding Dependabot automated dependency update configuration to a repository.

## Guard-rails

- If `.github/dependabot.yml` or `.github/dependabot.yaml` already exists, do **not** create a duplicate. Leave the existing file untouched.
- Do **not** install, build, or execute any dependencies during this step.

## Creating the Configuration

If no Dependabot config exists, create `.github/dependabot.yml` based on the tech-stack ecosystems detected in Step 1. Map each detected package manager or manifest to the corresponding Dependabot `package-ecosystem` value:

| Detected tool / manifest | `package-ecosystem` value |
|---|---|
| npm, pnpm, yarn, bun (`package.json`) | `npm` |
| pip, pip-tools (`requirements.txt`, `setup.py`) | `pip` |
| poetry, uv (`pyproject.toml` with `[tool.poetry]` or `[project]`) | `pip` |
| Maven (`pom.xml`) | `maven` |
| Gradle (`build.gradle`, `build.gradle.kts`) | `gradle` |
| Docker (`Dockerfile`) | `docker` |
| GitHub Actions (`.github/workflows/`) | `github-actions` |
| Go modules (`go.mod`) | `gomod` |
| Cargo (`Cargo.toml`) | `cargo` |
| NuGet (`.csproj`, `packages.config`) | `nuget` |
| Composer (`composer.json`) | `composer` |
| Bundler (`Gemfile`) | `bundler` |
| Terraform (`.tf` files) | `terraform` |
| Hex (`mix.exs`) | `mix` |

Only include ecosystems actually detected in the repo. Do not add entries for stacks that are not present.

## Smallest Correct Configuration

Use the smallest correct configuration. A typical single-stack repo needs only:

```yaml
version: 2
updates:
  - package-ecosystem: "{ecosystem}"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

## Defaults

- `schedule.interval`: `"weekly"`
- `open-pull-requests-limit`: `5`
- Do **not** add `day`, `time`, `timezone`, `registries`, `target-branch`, `groups`, `ignore`, or `allow` unless the repository context explicitly requires them.

## Monorepo Handling

If the repo is a monorepo with workspace subdirectories that have their own manifests, add a separate `updates` entry for each subdirectory with the correct `directory` path. For example:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/packages/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "npm"
    directory: "/packages/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```
