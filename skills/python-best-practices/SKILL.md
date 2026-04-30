---
name: python-best-practices
description: Review and improve Python code using focused guidance on common anti-patterns, performance bottlenecks, test quality, and error handling. Use this skill when writing or reviewing Python code that needs judgment beyond linters and type checkers.
compatibility: Python 3.10+
metadata:
  version: "1.0.0"
---

# Python Best Practices

Use this skill when reviewing or writing Python code that needs human-style engineering judgment: code smells, hot-path performance issues, test quality, and robust failure handling.

## How To Use This Skill

Start by identifying the kind of Python work in front of you, then read only the matching reference files.

- Read `references/anti-patterns.md` when reviewing general code quality, maintainability, architecture smells, configuration handling, resource usage, or type-safety issues.
- Read `references/performance.md` when the code is latency-sensitive, CPU-heavy, memory-heavy, uses async execution, or appears to sit on a hot path.
- Read `references/testing.md` when reviewing test code, coverage quality, fixtures, mocking strategy, parameterization, or the structure of a pytest suite.
- Read `references/error-handling.md` when reviewing validation, exceptions, failure modes, batch processing, recovery behavior, or API/service robustness.

Load more than one reference when the change crosses concerns. Examples:

- API handlers often need both `references/error-handling.md` and `references/testing.md`.
- Async services often need both `references/performance.md` and `references/anti-patterns.md`.
- Refactors of business logic and persistence boundaries often need both `references/anti-patterns.md` and `references/error-handling.md`.

## Review Focus

Use the references to look for issues that mechanical tools often miss:

- brittle boundaries between I/O and business logic
- retries, timeouts, and configuration scattered through the code
- blocking work inside async flows
- tests that only cover happy paths or overuse mocks
- exceptions that lose context or hide partial failures

Do not inline the full guidance from the references into your response unless the user asks for it. Read the relevant file, apply it to the code at hand, and return concrete findings or edits.

## Reference Map

- `references/anti-patterns.md`
- `references/performance.md`
- `references/testing.md`
- `references/error-handling.md`

## Attribution

The reference material in this skill is adapted from [wshobson/agents](https://github.com/wshobson/agents) and used under the MIT license. See [NOTICE](../../NOTICE) for the full license text and copyright notice.
