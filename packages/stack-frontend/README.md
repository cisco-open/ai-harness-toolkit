# stack-frontend

Framework-agnostic frontend package that adds design guidance and the Chrome DevTools MCP.

Composition:

```text
stack-frontend
  -> core
  -> stack-javascript-typescript
```

Included dependencies:

- `git: cisco-open/ai-harness-toolkit`, `path: packages/core`, `ref: core-v1.0.4`
- `vercel-labs/agent-skills/skills/web-design-guidelines`
- `io.github.ChromeDevTools/chrome-devtools-mcp`

Install with:

```bash
apm install --trust-transitive-mcp --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/stack-frontend#stack-frontend-v1.0.4
```
