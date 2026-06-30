# ai-harness-toolkit

Agent skills and APM packages for bootstrapping and assessing AI-native engineering workflows in repositories. This toolkit helps teams adopt structured, agent-driven development practices with deterministic checks, spec-driven development, package-managed AI workflows, and comprehensive documentation.

## Skills

### Primary Skills

| Skill | Description |
| --- | --- |
| [ai-harness-setup](skills/ai-harness-setup/) | Bootstrap a repository for agent-driven engineering -- sets up APM, OpenSpec, deterministic checks, AI skills, docs, and IDE configuration |
| [ai-native-assessment](skills/ai-native-assessment/) | Evaluate and score how AI-native a repository is across 6 weighted categories, producing a scored markdown report with prioritized actions |

### Bundled Dependency Skills

These skills are referenced by the primary skills and included for completeness:

| Skill | Description |
| --- | --- |
| [create-pull-request-with-reviewers](skills/create-pull-request-with-reviewers/) | Create a PR with automatically recommended reviewers based on git history |
| [gh-pr-comment-resolution](skills/gh-pr-comment-resolution/) | Fetch and resolve GitHub PR review comment threads via the gh CLI |
| [reflect-on-changes](skills/reflect-on-changes/) | Analyze recent code changes and update docs, commands, skills, and conventions |
| [python-best-practices](skills/python-best-practices/) | Review and improve Python code for anti-patterns, performance, testing, and error handling |

## APM Packages

This repo also publishes composable APM package manifests under `packages/`, with marketplace metadata rooted at `apm.yml`.

`packages/` is the source-of-truth package graph for transitive composition. For dependency-bearing packages, use direct tagged package refs against `packages/<name>` as the supported install path.

Install APM `0.18.0+` first and make sure your shell resolves that binary before any older system copy:

```bash
curl -sSL https://aka.ms/apm-unix | APM_INSTALL_DIR="$HOME/.local/bin" sh -s -- @v0.18.0
export PATH="$HOME/.local/bin:$PATH"
apm --version
```

Use this install shape:

```bash
apm install --target <harness> --allow-protocol-fallback [--trust-transitive-mcp] cisco-open/ai-harness-toolkit/packages/<package>#<package>-v<version>
```

- Always set `--target` so APM writes the right harness config.
- Use `--trust-transitive-mcp` for packages that include MCP servers directly.
- Keep `--allow-protocol-fallback` in the command for GitHub transport compatibility.

Package layout:

```text
core
|\
| +-- stack-javascript-typescript
| |   |
| |   +-- stack-frontend
| |   +-- stack-react
| |   +-- stack-angular
| |
| +-- stack-python-uv
| +-- stack-spring-boot
```

Available packages:

| Package | Description |
| --- | --- |
| `core` | Cisco workflow and software-security foundation |
| `stack-javascript-typescript` | JavaScript and TypeScript base package for web composition on top of `core` |
| `stack-frontend` | Frontend web package with `core`, JS/TS base, design guidance, and Chrome DevTools MCP |
| `stack-react` | React package with frontend guidance, JS/TS base, and Chrome DevTools MCP |
| `stack-angular` | Angular package with frontend guidance, JS/TS base, and Chrome DevTools MCP |
| `stack-python-uv` | Python and uv package with coding and security review skills |
| `stack-spring-boot` | Spring Boot package with Java implementation and testing skills |

## Installation

You can install individual skills with either `apm` or `npx skills`. Use the package install commands above when you want a full stack package instead of a single skill.

### With APM

```bash
apm install cisco-open/ai-harness-toolkit/skills/ai-harness-setup -t opencode -t cursor -t copilot
```

### With npx skills

```bash
npx skills add https://github.com/cisco-open/ai-harness-toolkit --skill ai-harness-setup
```

See each skill's README for detailed installation and invocation instructions.

## Repository Structure

```text
ai-harness-toolkit/
|-- LICENSE                              # Apache 2.0
|-- README.md
|-- CONTRIBUTING.md
|-- CODE_OF_CONDUCT.md
|-- SECURITY.md
|-- NOTICE                               # Third-party attributions
|-- apm.yml                              # Root APM marketplace manifest
|-- .gitignore
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   |   |-- bug_report.md
|   |   `-- feature_request.md
|   `-- PULL_REQUEST_TEMPLATE.md
|-- packages/
|   |-- core/
|   |-- stack-angular/
|   |-- stack-frontend/
|   |-- stack-javascript-typescript/
|   |-- stack-python-uv/
|   |-- stack-react/
|   `-- stack-spring-boot/
`-- skills/
    |-- ai-harness-setup/
    |-- ai-native-assessment/
    |-- create-pull-request-with-reviewers/
    |-- gh-pr-comment-resolution/
    |-- reflect-on-changes/
    `-- python-best-practices/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills and submitting changes.

## License

[Apache 2.0](LICENSE) -- Copyright 2025 Cisco Systems, Inc.
