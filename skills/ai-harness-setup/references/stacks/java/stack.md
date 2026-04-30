# Java

Read this file for Java services, CLIs, Spring applications, or mixed JVM repositories.

## Repo Markers

- `pom.xml`
- `build.gradle` or `build.gradle.kts`
- `settings.gradle` or `settings.gradle.kts`
- `src/main/java` or `src/test/java`

## Fresh Project Setup

For a fresh project in this workflow, use Maven unless the repo already uses Gradle.

Required plugins and tools for Maven-based repos:

- `maven-compiler-plugin`
- `maven-surefire-plugin`
- `spotbugs-maven-plugin`
- `maven-checkstyle-plugin` or `maven-pmd-plugin`
- `dependency-check-maven`

Required setup:

- pin the Java version in the compiler plugin
- fail the build on static-analysis violations
- expose commands for lint, test, build, and dependency scanning
- document local setup for Java and Maven or Gradle versions

## Skill Search Terms

Search for:

- `spring boot`
- `java backend`
- `spotbugs`
- `checkstyle`
- `security review`

## Skills to Install

Install these companion skills for Java code-review support:

```bash
apm install github/awesome-copilot/skills/security-review
apm install github/awesome-copilot/skills/java-refactoring-extract-method
apm install github/awesome-copilot/skills/refactor-method-complexity-reduce
```

These cover security review, method extraction refactoring, and complexity reduction.

## Recommended Deterministic Baseline

- `mvn test` or `./gradlew test`
- `mvn verify` or `./gradlew build`
- `mvn spotbugs:check` or `./gradlew spotbugsMain`
- `mvn checkstyle:check` or `./gradlew checkstyleMain`
- `mvn org.owasp:dependency-check-maven:check` or `./gradlew dependencyCheckAnalyze`

## Precommit Setup

For Java repos, prefer the build tool as the source of truth and wire hooks to that command surface.

Typical split:

- pre-commit: formatting or lightweight style checks if fast enough
- pre-push or explicit validation: full test, build, static-analysis, and dependency-check runs

## Extra Stack Discovery

Search for more stack signals such as:

- `spring-boot`, `quarkus`, `micronaut`, `junit`, `testcontainers`
- `.github/workflows/*.yml`, `Dockerfile`, `Jenkinsfile`
- multi-module build files and shared parent poms

## Framework-Specific References

- Use `references/stacks/java/framework-spring-boot.md` for Spring Boot repos.
