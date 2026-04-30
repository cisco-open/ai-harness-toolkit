# Java Deterministic Scans

Use repeatable commands that can run locally and in CI without human judgment.

## Build Tool Resolution

Prefer the repo's existing build tool.

- use `pom.xml` when the repo is Maven-based
- use `build.gradle` or `build.gradle.kts` when the repo is Gradle-based
- for a fresh project in this workflow, default to Maven

## Required Plugins and Tools

For Maven-based repos, add or verify:

- `maven-compiler-plugin`
- `maven-surefire-plugin`
- `spotbugs-maven-plugin`
- `maven-checkstyle-plugin` or `maven-pmd-plugin`
- `dependency-check-maven`

For Gradle-based repos, wire equivalent plugins for compile, test, static analysis, and dependency scanning.

## Required Configuration

- pin the Java version in compiler config
- fail the build on static-analysis violations
- expose lint, test, and dependency scan through the repo's chosen build tool
- if SonarQube is used, wire the scanner in CI and keep local static-analysis commands deterministic

## Commands

- vulnerability audit: `mvn org.owasp:dependency-check-maven:check` or `./gradlew dependencyCheckAnalyze`
- SAST/static analysis: `mvn spotbugs:check` or `./gradlew spotbugsMain`
- lint/style: `mvn checkstyle:check` or `./gradlew checkstyleMain`
- tests: `mvn test` or `./gradlew test`
- build: `mvn verify` or `./gradlew build`

## Wiring Rules

- keep one documented build-tool entrypoint for local and CI validation
- fail the build on static-analysis violations
- document any required plugin bootstrap in setup docs
