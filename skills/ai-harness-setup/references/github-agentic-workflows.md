# GitHub Agentic Workflows

Use this file when the team wants GitHub Agentic Workflows enabled in the target repository.

Ask this question near the beginning of the setup flow, after initial repo inspection but before installing workflow tooling:

- Do you want to enable GitHub Agentic Workflows in this repository?

If the answer is no, skip this reference entirely.

## Goal

Provide a repeatable path for adding selected upstream `gh aw` workflows into the repository without requiring token values during the install step.

The first supported upstream workflow is:

- `https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-doc-updater.md`

## Install the `gh aw` Extension

First verify whether `gh aw` is already available:

```bash
gh aw version
```

If that fails because the extension is missing, install it:

```bash
curl -sL https://raw.githubusercontent.com/github/gh-aw/main/install-gh-aw.sh | bash
```

Verify again:

```bash
gh aw version
```

If `gh aw` is already installed, prefer upgrading it before importing workflows:

```bash
gh extension upgrade aw
gh aw version
```

## Add a Supported Upstream Workflow

Use the upstream `add` path rather than copying workflow markdown manually.

For `daily-doc-updater`:

```bash
gh aw add https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-doc-updater.md
```

After the import finishes:

1. inspect `git status`
2. review all files created or modified by `gh aw`
3. keep generated workflow assets that belong to the imported workflow
4. confirm whether `.gitattributes` was added or updated with the generated lockfile rule

Do not hand-copy upstream workflow source files when `gh aw add` can generate them.

## Secrets and Token Setup

Complete the workflow import first, then document any required manual secret setup. This bootstrap flow should stop after adding the workflow files and documenting any manual follow-up.

### `COPILOT_GITHUB_TOKEN`

If using Copilot as your AI engine, set the GitHub Actions secret `COPILOT_GITHUB_TOKEN` to a GitHub Personal Access Token (PAT) so Copilot CLI can authenticate.

Reference:

- https://github.github.com/gh-aw/reference/auth/#copilot_github_token

Recommended setup:

1. Create a fine-grained PAT.
2. Verify the resource owner is your user account, not an organization.
3. Under `Permissions -> Account permissions`, set `Copilot Requests` to `Read`.
4. Generate the token and copy the value.
5. Add the PAT to the target repository's GitHub Actions secrets as `COPILOT_GITHUB_TOKEN`.

CLI example:

```bash
gh aw secrets set COPILOT_GITHUB_TOKEN --value "<your-github-pat>"
```

The GitHub UI can also be used if the operator prefers to add the secret manually.

Troubleshooting:

- If the workflow fails at the Copilot inference step even with the token set, verify that the token owner's account has an active Copilot license.
- Use the upstream auth reference above for additional diagnostics and setup details.

Do not ask the user to paste token values into tracked files, do not create pull requests as part of this bootstrap step, and do not configure credentials or repository secrets automatically.

## Scope Control

Keep the first change narrow.

- Start with the specifically requested upstream workflow
- Do not initialize the full `gh aw` repo surface unless the workflow requires it
- Do not add unrelated upstream workflows in the same change unless the user explicitly asks for them

## Files to Expect

The exact output can vary by `gh aw` version and workflow type, but verify the real generated files after import instead of assuming a fixed file set.

Common outcomes include:

- `.github/workflows/<workflow-name>.md`
- `.github/workflows/<workflow-name>.lock.yml`
- `.gitattributes`

Unless the user asks for broader initialization, avoid unrelated repo-wide `gh aw init` changes.

## Verification

- `gh aw version` succeeds
- the selected upstream workflow import command succeeds
- generated workflow files appear in `git status`
- any required secrets or token setup are documented as post-install follow-up
- no secret values were collected or written during bootstrap
