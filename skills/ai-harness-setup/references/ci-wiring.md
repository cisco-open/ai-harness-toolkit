# CI Wiring Patterns

Use this file when wiring deterministic checks into the repo's CI system. Detect the CI system during the repo inspection phase (step 1 of the main workflow) and use the matching pattern below.

## Principle

Every deterministic check that runs locally should have a corresponding CI stage, step, or job. CI should enforce the same checks as local development -- no more, no less.

Choose one enforcement mode before wiring CI:

- `enforced`: deterministic checks fail the pipeline on findings
- `advisory`: deterministic checks still run and surface output, but CI remains green or unstable rather than failed

## Detecting the CI System

Look for:

- `Jenkinsfile` or `Jenkinsfile.*` -> Jenkins
- `.github/workflows/*.yml` -> GitHub Actions
- `.gitlab-ci.yml` -> GitLab CI
- `Dockerfile` or `docker-compose.yml` -> containerized builds (may layer on top of any CI)

If the repo uses a CI system not covered here, follow the same principles: match local checks 1:1 with CI stages, reuse existing scripts, and document any gaps.

## Jenkins Patterns

### Detecting Existing Structure

Before adding stages, understand the existing Jenkinsfile:

- Is it declarative (`pipeline { ... }`) or scripted (`node { ... }`)?
- Does it use shared libraries (`@Library('...')`)? If so, check which functions are already available.
- Does it have an existing validation, quality, or check stage?
- Does it call existing scripts (e.g., `make ci-check`, `./scripts/ci.sh`)?

### Adding Checks to a Declarative Pipeline

Add a new stage for deterministic checks, or append to an existing validation stage:

```groovy
stage('Deterministic Checks') {
    steps {
        // Lint
        sh '{lint_command}'

        // Type check
        sh '{type_check_command}'

        // Tests
        sh '{test_command}'

        // Security scanning
        sh '{sast_command}'

        // Dependency audit
        sh '{audit_command}'

        // Build verification
        sh '{build_command}'
    }
}
```

Replace `{lint_command}`, `{type_check_command}`, etc. with the actual commands from the stack-specific deterministic scans reference, using the detected package manager.

### Advisory Mode in Jenkins

When advisory mode is selected, wrap each deterministic check so the build stays successful while the stage is marked unstable:

```groovy
stage('Deterministic Checks') {
    steps {
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{lint_command}'
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{type_check_command}'
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{test_command}'
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{sast_command}'
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{audit_command}'
        }
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '{build_command}'
        }
    }
}
```

Remove the `catchError(...)` wrappers when the repo upgrades to enforced mode.

### When to Add a New Stage vs. Modify an Existing One

- If the Jenkinsfile already has a `Quality` or `Validation` stage, **add the missing checks to it** rather than creating a parallel stage.
- If the Jenkinsfile uses shared library functions for checks, **call the existing functions** and only add new stages for checks not covered by the shared library.
- If the Jenkinsfile has no validation stage, **add a new `Deterministic Checks` stage** before the deploy or publish stage.

### Monorepo Jenkins Patterns

For monorepos with selective change detection:

```groovy
stage('Detect Changes') {
    steps {
        script {
            def changed = sh(script: './scripts/detect_changes.sh', returnStdout: true).trim()
            env.CHANGED_PACKAGES = changed
        }
    }
}

stage('Validate Changed Packages') {
    when { expression { env.CHANGED_PACKAGES != '' } }
    steps {
        sh "{run_checks_for_changed_packages}"
    }
}
```

## GitHub Actions Patterns

### Adding Checks to an Existing Workflow

Add a job or steps to the existing PR validation workflow (typically `.github/workflows/ci.yml` or `.github/workflows/pull-request.yml`):

```yaml
jobs:
  deterministic-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup environment
        # Use the appropriate setup action for the detected stack
        # e.g., actions/setup-node, actions/setup-python, actions/setup-java

      - name: Install dependencies
        run: {install_command}

      - name: Lint
        run: {lint_command}

      - name: Type check
        run: {type_check_command}

      - name: Tests
        run: {test_command}

      - name: Security scan
        run: {sast_command}

      - name: Dependency audit
        run: {audit_command}

      - name: Build verification
        run: {build_command}
```

### Advisory Mode in GitHub Actions

When advisory mode is selected, add `continue-on-error: true` to each deterministic check step:

```yaml
jobs:
  deterministic-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: {install_command}

      - name: Lint
        continue-on-error: true
        run: {lint_command}

      - name: Type check
        continue-on-error: true
        run: {type_check_command}

      - name: Tests
        continue-on-error: true
        run: {test_command}

      - name: Security scan
        continue-on-error: true
        run: {sast_command}

      - name: Dependency audit
        continue-on-error: true
        run: {audit_command}

      - name: Build verification
        continue-on-error: true
        run: {build_command}
```

Remove `continue-on-error: true` when the repo upgrades to enforced mode.

### When to Add a New Job vs. Add Steps

- If the workflow already has a `test` or `ci` job, **add missing checks as new steps** within that job.
- If the workflow separates concerns (lint job, test job, build job), **add each check to the appropriate existing job**.
- If no validation workflow exists, **create a new workflow file**.

### Monorepo GitHub Actions Patterns

Use path filters or change detection to run checks only for affected packages:

```yaml
on:
  pull_request:
    paths:
      - 'packages/my-package/**'
```

Or use a matrix strategy with a change detection step.

## General Wiring Rules

- **Reuse existing scripts.** If the repo has `make ci-check`, `./scripts/validate.sh`, or equivalent, call those from CI rather than duplicating individual commands.
- **Match local commands exactly.** CI should run the same commands that developers run locally. If local validation uses `make check`, CI should use `make check`.
- **Keep enforcement mode consistent.** If local commands or hooks are advisory, CI should also be advisory until the repo is intentionally tightened.
- **Document gaps explicitly.** If a check cannot be wired into CI immediately (e.g., missing credentials for a scanning tool), document it as a follow-up item rather than silently omitting it.
- **Keep CI config minimal.** Prefer calling a single validation script from CI over listing every check command inline. This ensures local and CI stay in sync.
