# Spring Boot + JUnit 5 + Maven

A thin vertical slice: one domain object, one operation with a real rule, one edge case.

**Read "What was actually run" before trusting this example.** At authoring time
Maven was not installed, so the JUnit suite had never executed and the other three
examples in this directory were green while this one was not — a difference stated
plainly rather than papered over, because a worked example that lies about its
evidence is worse than no example. Since then the gap was closed: the suite was
executed by hand (Maven 3.9.9, OpenJDK 21, Linux) and both gates pass — `javac`
via Maven, and JUnit 5 through surefire. CI runs the same two gates on every push.

## What this demonstrates

A meeting note has a title, a body, and a status. It can be created as a draft and
published. Publishing has three rules worth testing:

- **Happy path.** A draft with content becomes published and gets a timestamp.
- **Validation failure.** A blank or whitespace-only body cannot be published.
- **Idempotency edge case.** Publishing an already published note is not an error and
  does not move `publishedAt`.

`NoteService` holds the rules and is a plain class with a constructor-injected `Clock`.
Its tests build it with `new` and load no Spring context. `NoteController` is the web
layer and holds no rule.

## Setup

Java 21 and Maven 3.9 or newer.

```bash
cd examples/java-spring
mvn -B -q test-compile
```

Maven downloads the Spring Boot dependency tree on the first run, so it needs network
access once.

## Run

```bash
mvn -B test                 # tests, writes target/surefire-reports/*.xml
mvn -B spring-boot:run      # the API on :8080
```

Through the gate runner, which lives at `../../gates/`:

```bash
node ../../gates/run-gates.mjs
```

The `test` gate runs with `-Dmaven.test.failure.ignore=true` on purpose. The gate's
`junit-xml` parser reads `target/surefire-reports`, and it can only do that if Maven
finishes and writes complete reports. The BASELINE decides what counts as a real failure,
not Maven's exit code.

## What was actually run

**Maven is not installed on this machine and `~/.m2` does not exist.**

```
$ mvn -v
bash: mvn: command not found

$ ls ~/.m2/repository
ls: cannot access '~/.m2/repository': No such file or directory
```

So the following were **UNVERIFIED at authoring time**:

- The JUnit suite had never executed. Zero of the eight acceptance criteria had been
  observed passing through JUnit.
- `gates.config.json` had never been run. The surefire report path came from Maven's
  documented default, not from an observed `target/surefire-reports` directory.
- The Spring wiring was unexecuted: `@SpringBootTest`, the `@TestConfiguration` clock
  bean, `@Primary`, the `@ExceptionHandler` status mapping, and the Jackson `Instant`
  serialization setting. A missing annotation or a context-loading failure would not have
  been caught here.
- The mutation verification of the idempotency rule was NOT done through JUnit.

**Update, since the repo went public: the gap is closed.** With Maven 3.9.9 on
OpenJDK 21 (Linux), `node ../../gates/run-gates.mjs` from this directory reports
**2 PASS**: the `javac` gate, and the surefire gate reading
`target/surefire-reports` — 21 tests (7 `NoteControllerTest` through the Spring
context, 14 `NoteServiceTest`), 0 failures, 0 errors, 0 skipped. The surefire
report path matched the documented default on the first try. CI runs the same
two gates on every push.

What **WAS** verified, on OpenJDK 21.0.12.1:

The five classes that depend only on the JDK were extracted and compiled. That is `Note`,
`NoteStatus`, `ValidationException`, `NoteNotFoundException`, and `NoteService` with its
one `@Service` annotation stripped, since that annotation is the only Spring reference in
the file.

```
$ javac -d out -proc:none com/example/notes/*.java
exit 0
```

Then the domain rules were executed by a scratch harness outside this repo, covering the
same logic as `NoteServiceTest`:

```
PASS create starts as draft
PASS create trims title
PASS blank title rejected
PASS oversized body rejected
PASS publish sets status + timestamp
PASS whitespace body rejected
PASS rejected note stays draft
PASS publish is idempotent (no error)
PASS publish does not move timestamp
PASS published note survives blanked body
PASS unknown id is not-found
PASS concurrent publish stamps once

12 passed, 0 failed
```

And the mutation check, making the already-published branch re-stamp `publishedAt`:

```
FAIL publish does not move timestamp
FAIL published note survives blanked body
FAIL concurrent publish stamps once

9 passed, 3 failed
```

Reverted, 12 passed.

**What that evidence covers:** the publish rules, the check order, and the `compute`
lock behave as specified on a real JVM. **What it does not cover:** anything Spring does.
Treat this example as reviewed-and-reasoned rather than proven, and run `mvn -B test`
before trusting it.

## How the method shows up here

| Concept | Where it lives | What to look at |
| --- | --- | --- |
| **Spec-driven development** | `specs/` | `prd.md` has a locked-decisions table. D4 locks the ORDER of the two publish checks. D7 is Java-specific: `Note` is a record, so publishing returns a new value rather than mutating one two callers may share. |
| **TDD** | `src/test/java/com/example/notes/NoteServiceTest.java` | Plain JUnit, no `@SpringBootTest`, so the rule tests stay fast. `publishIsIdempotent` uses a clock that returns a DIFFERENT instant on its second read, so it can observe a re-stamp. `NoteControllerTest` is the slower MockMvc layer and checks wiring, not rules. |
| **Compound engineering** | `specs/epic-01-notes/story-01-publish-note.md`, section "Dev agent record" | The `@Transactional`-on-a-test trap, plus an honest record of what could not be verified and why. A trap record that admits a gap is more useful than one that hides it. |
| **Local CI enforcement** | `gates.config.json` | Two gates. `junit-xml` is the only parser that reads FILES rather than stdout, so it requires `reportFile`. The config carries a comment saying it is unverified, so the next person does not assume it has been exercised. |

### The Spring-specific trap, in one line

Do not annotate a test `@Transactional` to get isolation. This service stores notes in a
`ConcurrentHashMap`, which is not a transactional resource, so there is nothing to roll
back: every write leaks into the next test while the annotation tells the reader that
isolation is handled. Get isolation from a fresh fixture instead. The full version,
including what changes once a real database is involved, is in the story's Dev agent
record.

## Files

```
src/main/java/com/example/notes/Note.java              record, immutable
src/main/java/com/example/notes/NoteService.java       domain rules, injected Clock
src/main/java/com/example/notes/NoteController.java    routes and error mapping
src/main/java/com/example/notes/NotesApplication.java  entry point, Clock bean
src/test/java/com/example/notes/NoteServiceTest.java   plain JUnit, no Spring context
src/test/java/com/example/notes/NoteControllerTest.java MockMvc, fixed clock
specs/                                                 prd.md, epic, one story with the trap record
gates.config.json                                      mvn test-compile, mvn test + junit-xml
```
