# ai-harness-toolkit

Agent skills for bootstrapping and assessing AI-native engineering workflows in repositories. These skills help teams adopt structured, agent-driven development practices with deterministic checks, spec-driven development, and comprehensive documentation.

## Skills

### Primary Skills

| Skill | Description |
|-------|-------------|
| [ai-harness-setup](skills/ai-harness-setup/) | Bootstrap a repository for agent-driven engineering -- sets up APM, OpenSpec, deterministic checks, AI skills, docs, and IDE configuration |
| [ai-native-assessment](skills/ai-native-assessment/) | Evaluate and score how AI-native a repository is across 6 weighted categories, producing a scored markdown report with prioritized actions |

### Bundled Dependency Skills

These skills are referenced by the primary skills and included for completeness:

| Skill | Description |
|-------|-------------|
| [create-pull-request-with-reviewers](skills/create-pull-request-with-reviewers/) | Create a PR with automatically recommended reviewers based on git history |
| [gh-pr-comment-resolution](skills/gh-pr-comment-resolution/) | Fetch and resolve GitHub PR review comment threads via the gh CLI |
| [reflect-on-changes](skills/reflect-on-changes/) | Analyze recent code changes and update docs, commands, skills, and conventions |
| [python-best-practices](skills/python-best-practices/) | Review and improve Python code for anti-patterns, performance, testing, and error handling |

## Installation

You can install individual skills with either `apm` or `npx skills`.

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

```
ai-harness-toolkit/
├── LICENSE                              # Apache 2.0
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── NOTICE                               # Third-party attributions
├── .gitignore
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
└── skills/
    ├── ai-harness-setup/
    ├── ai-native-assessment/
    ├── create-pull-request-with-reviewers/
    ├── gh-pr-comment-resolution/
    ├── reflect-on-changes/
    └── python-best-practices/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills and submitting changes.

## License

[Apache 2.0](LICENSE) -- Copyright 2025 Cisco Systems, Inc.
