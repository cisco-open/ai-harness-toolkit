# React and Next.js

Use this file when the repo contains `react`, `react-dom`, `next`, `@vitejs/plugin-react`, or React-based Nx projects.

## What to Install

Baseline packages usually include:

- `react`
- `react-dom`
- `typescript`
- `eslint`
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
- keep framework-specific runtime config checked in, such as `next.config.*` or `vite.config.*`

## Skills to Install

Prefer these skills when the repo is React-heavy:

- `vercel-react-best-practices`
- `frontend-testing`
- `frontend-code-review`
- `web-design-guidelines`
- `component-refactoring` when large React components need decomposition
- `performance-optimization` for runtime bottlenecks

Install the testing companion skills for code-review support:

```bash
apm install github/awesome-copilot/skills/javascript-typescript-jest
apm install github/awesome-copilot/skills/webapp-testing
```

Keep general workflow and security guidance in the shared setup docs; this file should stay focused on React-specific additions.

## Install Order

1. audit local skills already vendored in the repo
2. install `vercel-react-best-practices` from the local repo if available, or use `apm install` from the preferred remote source if not
3. install frontend review/testing skills with `apm install`
4. stop once the React-specific gaps are covered, then defer shared workflow installs to the common setup guidance

## Search Terms

Browse `ai-harness-toolkit` or other curated sources first, then use `npx skills find` with queries such as:

- `react review`
- `react performance`
- `nextjs performance`
- `frontend testing`
- `accessibility review`

Install any selected package with `apm install <package>`.

## Framework Markers

- `react`
- `react-dom`
- `next`
- `@vitejs/plugin-react`
- `react-router-dom`
- `app/`, `pages/`, or `src/components/` patterns typical of React apps
