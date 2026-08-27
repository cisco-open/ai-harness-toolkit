# Spring Boot

Use this file when the repo contains Spring Boot dependencies, starters, or common Spring app structure.

## What to Install

Baseline packages and plugins usually include:

- Spring Boot starter dependencies needed by the app
- `maven-compiler-plugin` or Gradle Java plugin configuration
- `maven-surefire-plugin` or Gradle test task configuration
- `spotbugs-maven-plugin` or Gradle SpotBugs plugin
- `maven-checkstyle-plugin` or equivalent style plugin
- `dependency-check-maven` or Gradle OWASP dependency-check plugin

## Required Configuration

- pin Java version
- fail builds on static-analysis violations
- expose deterministic commands for test, build, dependency scanning, and static analysis
- document local runtime dependencies such as Java version and Maven or Gradle version

## Skills to Install

Focus this file on Spring Boot-specific additions instead of shared workflow tooling.

Install the `stack-spring-boot` package:

```bash
apm install --target <ide-1> --target <ide-2> --allow-protocol-fallback cisco-open/ai-harness-toolkit/packages/stack-spring-boot#stack-spring-boot-v<latest>
```

This package covers `java-springboot`, `spring-boot-testing`, `java-junit`, and the transitive `core` workflow bundle.

If the repo includes frontend or AI integrations, add those framework skills separately.

## Search Terms

Use curated sources first, then `npx skills find` for broader discovery when needed. Install the chosen package with `apm install`.

Useful queries include:

- `spring boot`
- `java backend`
- `security review`
- `performance`

## Framework Markers

- `org.springframework.boot`
- `spring-boot-starter-*`
- `src/main/java/.../Application.java`
- `application.yml` or `application.properties`
