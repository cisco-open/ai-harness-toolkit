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
- fail the build on static-analysis violations in enforced mode
- expose lint, test, and dependency scan through the repo's chosen build tool
- if SonarQube is used, wire the scanner in CI and keep local static-analysis commands deterministic

For Maven-based repositories, configure OWASP dependency-check to use the cached NVD data feed by default. An NVD API key is optional and must be supplied through the environment rather than committed to the repository:

```xml
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <configuration>
    <nvdDatafeedUrl>https://dependency-check.github.io/DependencyCheck_Builder/nvd_cache/</nvdDatafeedUrl>
    <nvdApiKeyEnvironmentVariable>DEPENDENCY_CHECK_NVD_API_KEY</nvdApiKeyEnvironmentVariable>
  </configuration>
</plugin>
```

Before adding these elements, check the version of `dependency-check-maven` already pinned by the repository. If it does not support `nvdDatafeedUrl` or `nvdApiKeyEnvironmentVariable`, upgrade the plugin to a compatible release. When an upgrade is not possible, use the older plugin's supported `cveUrlBase` and `cveUrlModified` properties with a mirror that publishes the legacy NVD feed format, and verify the update logs show that the configured feed was used.

Treat `DEPENDENCY_CHECK_NVD_API_KEY` as an optional CI or developer environment variable, not a setup prerequisite. Keep the `nvdDatafeedUrl` configuration in both enforced and advisory modes. For Gradle-based repositories, use the OWASP plugin's equivalent data-feed configuration and the same environment-variable policy.

## Commands

- vulnerability audit: `mvn org.owasp:dependency-check-maven:check` or `./gradlew dependencyCheckAnalyze`
- SAST/static analysis: `mvn spotbugs:check` or `./gradlew spotbugsMain`
- lint/style: `mvn checkstyle:check` or `./gradlew checkstyleMain`
- tests: `mvn test` or `./gradlew test`
- build: `mvn verify` or `./gradlew build`

Choose one enforcement mode before wiring these commands:

- `enforced`: static analysis and audit failures should fail the build
- `advisory`: keep the same checks visible, but use tool-native settings so findings do not fail the build

## Advisory Mode Configuration

For Maven-based repos, use these settings in advisory mode:

- checkstyle: `<failOnViolation>false</failOnViolation>`
- SpotBugs: `<failOnError>false</failOnError>`
- OWASP dependency-check: `<failBuildOnCVSS>11</failBuildOnCVSS>`

Example Maven snippet:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-checkstyle-plugin</artifactId>
  <configuration>
    <failOnViolation>false</failOnViolation>
  </configuration>
</plugin>
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <configuration>
    <failOnError>false</failOnError>
  </configuration>
</plugin>
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <configuration>
    <nvdDatafeedUrl>https://dependency-check.github.io/DependencyCheck_Builder/nvd_cache/</nvdDatafeedUrl>
    <nvdApiKeyEnvironmentVariable>DEPENDENCY_CHECK_NVD_API_KEY</nvdApiKeyEnvironmentVariable>
    <failBuildOnCVSS>11</failBuildOnCVSS>
  </configuration>
</plugin>
```

For Gradle-based repos, use the equivalent plugin settings that preserve scan output while keeping the build green.

## Wiring Rules

- keep one documented build-tool entrypoint for local and CI validation
- keep the chosen enforcement mode consistent across build config, hooks, and CI
- document any required plugin bootstrap in setup docs
