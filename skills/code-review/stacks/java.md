# Java

Stack reference for the code-review orchestrator. Defines detection signals, deterministic checks, framework detection, companion skill mappings, and native review focus areas for Java and Kotlin projects.

## Detection Signals

### File Extensions

- `*.java`
- `*.kt`
- `*.kts`

### Config Files

- `pom.xml`
- `build.gradle`
- `build.gradle.kts`
- `settings.gradle`
- `settings.gradle.kts`

### Directory Patterns

- `src/main/java/`
- `src/test/java/`
- `src/main/kotlin/`
- `src/test/kotlin/`

## Deterministic Check Commands

### Build System Detection

1. Check for `pom.xml` → Maven
2. Check for `build.gradle` or `build.gradle.kts` → Gradle
3. If both exist, prefer the one with recent modifications

### Maven Variant

| Lane | Command |
|---|---|
| Compile | `mvn compile` |
| Test | `mvn test` |
| Static analysis (SpotBugs) | `mvn spotbugs:check` |
| Static analysis (Checkstyle) | `mvn checkstyle:check` |
| Build | `mvn verify` |
| SAST (OWASP) | `mvn org.owasp:dependency-check-maven:check` |

### Gradle Variant

| Lane | Command |
|---|---|
| Compile | `./gradlew compileJava` |
| Test | `./gradlew test` |
| Static analysis (SpotBugs) | `./gradlew spotbugsMain` |
| Static analysis (Checkstyle) | `./gradlew checkstyleMain` |
| Build | `./gradlew build` |
| SAST (OWASP) | `./gradlew dependencyCheckAnalyze` |

### Auto-Fix Commands

Java has limited auto-fix tooling compared to TypeScript and Python. Most fixes require manual intervention.

| Tool | Fix Command | Safe |
|---|---|---|
| Checkstyle (format only) | IDE-assisted or plugin-specific | Partially safe (format only) |
| google-java-format | `google-java-format --replace <files>` | Yes (formatting only) |

## Framework Detection

### Spring Boot

**Signals:**

- `org.springframework.boot` in `pom.xml` or `build.gradle` dependencies
- `spring-boot-starter-*` artifacts in dependencies
- `application.yml` or `application.properties` in `src/main/resources/`
- `@SpringBootApplication` annotation in source files

**Activates:** Framework lane with Spring Boot companion skills.

## Companion Skill Mappings

### Security Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@security-review` | `apm install github/awesome-copilot/skills/security-review` |

### Framework Lane: Spring Boot

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@java-springboot` | `apm install github/awesome-copilot/skills/java-springboot` |
| `github/awesome-copilot@spring-boot-testing` | `apm install github/awesome-copilot/skills/spring-boot-testing` |

### Testing Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@java-junit` | `apm install github/awesome-copilot/skills/java-junit` |

### Refactoring Lane

| Skill | Install Command |
|---|---|
| `github/awesome-copilot@java-refactoring-extract-method` | `apm install github/awesome-copilot/skills/java-refactoring-extract-method` |
| `github/awesome-copilot@refactor-method-complexity-reduce` | `apm install github/awesome-copilot/skills/refactor-method-complexity-reduce` |

## Native Review Focus Areas

Use these when companion skills are not installed. Each area describes patterns to look for in manual review.

### General Java

- **Thread safety in shared state**: Mutable fields accessed from multiple threads without synchronization, missing `volatile`, incorrect use of `synchronized`
- **Resource leaks**: Unclosed streams, connections, or other `AutoCloseable` resources. Missing try-with-resources.
- **Excessive object allocation in loops**: Creating unnecessary objects inside tight loops, boxing/unboxing in performance-sensitive paths
- **N+1 query patterns**: JPA/Hibernate lazy loading triggering individual queries inside loops, missing `JOIN FETCH` or entity graphs
- **Missing transaction boundaries**: Database operations without `@Transactional`, or transactions with too broad a scope
- **Exception swallowing**: Catching exceptions and logging without rethrowing or handling, empty catch blocks

### Spring Boot Specific

- **Missing validation**: Request DTOs without `@Valid` / `@Validated`, missing `@NotNull`, `@Size`, etc.
- **Incorrect scope**: Stateful beans with singleton scope, request-scoped beans injected into singletons
- **Missing error handling**: Controllers without `@ExceptionHandler` or `@ControllerAdvice`
- **Security misconfig**: Endpoints without proper `@PreAuthorize` or security filter chain configuration
- **Blocking in WebFlux**: Synchronous/blocking calls in reactive Spring WebFlux handlers
- **Missing test slices**: Using `@SpringBootTest` (loads full context) when `@WebMvcTest`, `@DataJpaTest`, or `@JsonTest` would suffice
