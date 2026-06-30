# TypeScript / JavaScript

Stack reference for the code-review orchestrator. Defines detection signals, deterministic checks, framework detection, companion skill mappings, and native review focus areas for TypeScript and JavaScript projects.

## Detection Signals

### File Extensions

- `*.ts`
- `*.tsx`
- `*.js`
- `*.jsx`
- `*.mts`
- `*.cts`
- `*.mjs`
- `*.cjs`

### Config Files

- `tsconfig.json`
- `package.json`
- `eslint.config.*`
- `.eslintrc.*`

### Lockfiles

- `pnpm-lock.yaml`
- `yarn.lock`
- `package-lock.json`
- `bun.lockb`

## Deterministic Check Commands

### Package Manager Detection

Detect the package manager before running any commands:

1. Check `packageManager` field in `package.json`
2. Check for lockfiles: `pnpm-lock.yaml` → pnpm, `bun.lockb` → bun, `yarn.lock` → yarn, `package-lock.json` → npm
3. Default: `pnpm`

Use these placeholders below so commands stay valid across package managers:

- `{script}`: package.json script runner (`pnpm`, `npm run`, `yarn`, `bun run`)
- `{exec}`: binary runner (`pnpm exec`, `npx`, `yarn exec`, `bunx`)
- `{audit}`: audit command (`pnpm audit`, `npm audit`, `yarn audit`, `bun audit` when available in the repo's bun setup)

### Nx Workspace Variant

When `nx.json` is present, use affected commands scoped to the diff:

| Lane | Command |
|---|---|
| Lint | `{script} nx affected -t lint` |
| Type-check | `{script} nx affected -t type-check` |
| Build | `{script} nx affected -t build` |
| Test | `{script} nx affected -t test` |
| SAST | `{exec} semgrep --config auto <files>` |
| Audit | `{audit}` |

### Non-Nx Variant

When `nx.json` is not present:

| Lane | Command |
|---|---|
| Lint | `{script} lint` or `{exec} eslint <files>` |
| Type-check | `{exec} tsc --noEmit` |
| Build | `{script} build` |
| Test | `{script} test` |
| SAST | `{exec} semgrep --config auto <files>` |
| Audit | `{audit}` |

### Auto-Fix Commands

| Tool | Fix Command | Safe |
|---|---|---|
| ESLint | `{exec} eslint --fix <files>` | Yes |
| Prettier | `{exec} prettier --write <files>` | Yes |

## Framework Detection

### React / Next.js

**Signals:**

- `next.config.*` (Next.js)
- `react` in `package.json` dependencies
- `@vitejs/plugin-react` in dependencies
- `react-dom` in dependencies

**Activates:** Framework lane with React/Next.js companion skills.

### Angular

**Signals:**

- `angular.json`
- `@angular/core` in `package.json` dependencies
- `@nx/angular` in dependencies

**Activates:** Framework lane with Angular companion skills.

## Companion Skill Mappings

### Security Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@security-review` | `apm install github/awesome-copilot/skills/security-review` |

### Testing Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@javascript-typescript-jest` | `apm install github/awesome-copilot/skills/javascript-typescript-jest` |
| `github/awesome-copilot@webapp-testing` | `apm install github/awesome-copilot/skills/webapp-testing` |

### Framework Lane: React / Next.js

| Skill | Install Command |
|---|---|
| `vercel-labs/agent-skills@vercel-react-best-practices` | `apm install vercel-labs/agent-skills/skills/vercel-react-best-practices` |
| `vercel-labs/agent-skills@web-design-guidelines` | `apm install vercel-labs/agent-skills/skills/web-design-guidelines` |
| `vercel-labs/agent-skills@vercel-composition-patterns` | `apm install vercel-labs/agent-skills/skills/vercel-composition-patterns` |

### Framework Lane: Angular

| Skill | Install Command |
|---|---|
| `angular/skills@angular-developer` | `apm install angular/skills/skills/angular-developer` |

## Native Review Focus Areas

Use these when companion skills are not installed. Each area describes patterns to look for in manual review.

### React / Next.js

- **Hook dependency arrays**: Missing or over-specified dependencies in `useEffect`, `useMemo`, `useCallback`
- **Unnecessary re-renders**: Components re-rendering due to unstable references, missing memoization, or prop drilling
- **Bundle size impact**: Large imports that should be code-split or dynamically loaded
- **Accessibility regressions**: Missing `aria-*` attributes, non-semantic elements used for interaction, missing alt text
- **Server/client boundary**: Incorrect use of `"use client"` / `"use server"` directives in Next.js App Router

### Angular

- **Change detection**: Components using default change detection when OnPush would be more efficient
- **Memory leaks**: Subscriptions not unsubscribed in `ngOnDestroy`
- **Template complexity**: Complex logic in templates that should be in the component class
- **Lazy loading**: Modules that should be lazy-loaded but are eagerly imported

### General TypeScript

- **Type safety**: Use of `any`, missing return types on exported functions, type assertions that hide errors
- **Async patterns**: Unhandled promise rejections, missing `await`, race conditions in concurrent operations
- **Error handling**: Swallowed errors in catch blocks, missing error boundaries
- **Import hygiene**: Circular imports, barrel file re-exports that defeat tree-shaking
