# React and Next.js

Use this file when the repo contains `react`, `react-dom`, `next`, `@vitejs/plugin-react`, or React-based Nx projects.

## What to Install

Baseline packages usually include:

- `typescript`
- `typescript-eslint`
- `eslint-plugin-react`
- `eslint-plugin-react-hooks`
- `eslint-plugin-jsx-a11y`
- `eslint-plugin-sonarjs`
- `@testing-library/react`
- `@testing-library/user-event`
- `vitest` or `jest`

For Next.js, also install the normal Next runtime and lint setup for that repo.

## Required Configuration

- enable TypeScript strict mode
- enable React, hooks, and accessibility lint rules
- include SonarJS rules for complexity and maintainability
- add deterministic test, build, and audit commands
- keep framework-specific runtime configuration checked in, such as `next.config.*` or `vite.config.*`

## Skills to Install

Install the `stack-react` package:

```bash
apm install --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/stack-react#stack-react-v<latest>
```

This package covers React best practices, `javascript-typescript-jest`, `webapp-testing`, `web-design-guidelines`, the transitive `stack-javascript-typescript`, and `core`, plus the Chrome DevTools MCP server.

Keep general workflow and security guidance in the shared setup docs; this file should stay focused on React-specific additions.

Treat the package as the default baseline, not the full ceiling. If the repo still has React- or Next-specific gaps after that install, add targeted dynamic skills on top.

## Install Order

1. audit local skills already vendored in the repo
2. install the `stack-react` package
3. add only extra dynamic skills when the repo has React-specific gaps the package does not cover
4. stop once the React-specific gaps are covered, then defer shared workflow installs to the common setup guidance

## Search Terms

Browse repo-local or other public curated sources first, then use `npx skills find` with queries such as:

- `react review`
- `react performance`
- `nextjs performance`
- `frontend testing`
- `accessibility review`

Install any selected extra package with `apm install <pkg>`.

## Framework Markers

- `react`
- `react-dom`
- `next`
- `@vitejs/plugin-react`
- `react-router-dom`
- `app/`, `pages/`, or `src/components/` patterns typical of React apps
