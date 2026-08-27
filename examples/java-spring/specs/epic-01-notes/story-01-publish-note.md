# Story 01: Publish a note

**Epic:** [epic.md](epic.md)
**Status:** done (code written and reviewed, test suite NOT executed, see below)
**Feature IDs:** FR-01-01, FR-01-02, FR-01-03, FR-01-04

## Context an implementer needs

`NoteService` holds the rules and is a plain class with a constructor-injected `Clock`
(PRD D6). Its tests build it directly with `new NoteService(Clock.fixed(...))` and load
no application context (PRD D5).

`Note` is a record (PRD D7), so `published(Instant)` returns a new value rather than
mutating. Nothing hands out a mutable note.

The store is a `ConcurrentHashMap`, and `publish` does its read-check-write inside
`map.compute(...)`, which holds a per-key lock. Two concurrent publishes of the same id
cannot both stamp a timestamp.

`NoteController` maps `ValidationException` to 422 and `NoteNotFoundException` to 404
through `@ExceptionHandler`.

## Acceptance criteria

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | no note exists | POST `/notes` with a title and a body | 201, status `DRAFT`, no `publishedAt` |
| AC2 | no note exists | POST `/notes` with a blank or whitespace title | 422, `field` is `title` |
| AC3 | a draft note with a non-empty body | POST `/notes/{id}/publish` | 200, status `PUBLISHED`, `publishedAt` set |
| AC4 | a draft note with an empty or whitespace-only body | POST `/notes/{id}/publish` | 422, `field` is `body`, note still a draft |
| AC5 | a note already published at T1 | POST `/notes/{id}/publish` again | 200, `publishedAt` is still T1 |
| AC6 | a note published at T1 whose body was later blanked | publish again | 200, still published at T1, no 422 |
| AC7 | an id that does not exist | POST `/notes/{id}/publish` | 404 |
| AC8 | a draft note with content | 8 threads publish it at once | exactly one timestamp |

AC6 pins the ORDER of the two checks (PRD D4). AC8 covers the `compute` lock.

## Tasks

- [x] Write `Note` as a record, plus `NoteStatus`, `ValidationException`, `NoteNotFoundException`.
- [x] Write `NoteService` with a constructor-injected `Clock`.
- [x] Write `publish` with the published check BEFORE the body check, inside `compute`.
- [x] Write `NoteServiceTest` with plain JUnit, no Spring context.
- [x] Write `NoteController` and its `@ExceptionHandler` methods.
- [x] Write `NoteControllerTest` with MockMvc and a fixed-clock `@TestConfiguration`.
- [x] Add `gates.config.json` pointing `junit-xml` at `target/surefire-reports`.
- [ ] **Run the suite.** BLOCKED: Maven is not installed and no local `~/.m2` exists.
- [ ] **Mutation-verify AC5 through JUnit.** BLOCKED by the same thing.

## Dev agent record

### Trap: `@Transactional` on a test does nothing here, and says the opposite

The reflex when writing a Spring integration test is to annotate the class
`@Transactional`. Spring then rolls the transaction back at the end of each test
method, so tests do not see each other's writes. It is the standard recipe and it is
in every tutorial.

It is wrong in this codebase, in a way that is easy to miss because it fails SILENTLY.

`NoteService` stores notes in a `ConcurrentHashMap`. A map is not a transactional
resource. There is nothing for Spring to roll back. Every write survives the "rollback"
and leaks into the next test in the class. The annotation is a comment that lies: it
tells the next reader isolation is handled when nothing is handling it. A test written
later that assumes a clean store passes or fails depending on method order, which
JUnit does not guarantee.

The related surprise, for when this example grows a real database: `@Transactional` on
a test method does NOT wrap the code a MockMvc request runs. The request is handled on
the same thread here, but the service's own `@Transactional` boundary joins the test's
outer transaction, so a rollback the production code expects at the service boundary is
silently absorbed instead. A test asserting "the failed publish rolled the row back"
then passes for the wrong reason, because the outer test transaction rolled EVERYTHING
back at the end regardless.

**Rule taken from this:** do not annotate a test `@Transactional` to get isolation.
Get isolation from a fresh fixture. `NoteControllerTest` relies on a fresh application
context per test class and constructs no shared state. When this grows a database, the
isolation should come from truncating between tests or from a per-test schema, never
from an annotation whose effect depends on which resources happen to be transactional.

### Trap: a coarse clock makes the idempotency assertion pass for the wrong reason

`NoteControllerTest` installs a `@TestConfiguration` whose `Clock` returns one instant
on its first read and a DIFFERENT instant afterwards. `Clock.fixed(...)` would have
been simpler and would have made AC5 worthless: with a fixed clock, a re-stamping bug
writes the same value it overwrote, and the assertion `secondAt.equals(firstAt)` holds
even though the rule is broken.

Same failure mode as `Instant.now()` on a coarse system clock, where two calls
microseconds apart can return equal values.

**Rule taken from this:** a test asserting a value did NOT change must make the change
observable. If the second write would produce the same bytes as the first, the test
proves nothing.

### What was NOT verified, and why

**Maven is not installed on the authoring machine, and `~/.m2` does not exist.** No
Maven command has been run. `mvn -v` reports `command not found`. Downloading the
Spring Boot dependency tree is not possible here.

So the following are UNVERIFIED:

- The JUnit suite has never executed. Zero of the eight acceptance criteria have been
  observed passing through JUnit.
- The mutation verification of AC5 was NOT done through JUnit.
- `gates.config.json` has never been run. The surefire report path is written from the
  documented default, not from an observed `target/surefire-reports` directory.
- The Spring wiring (`@SpringBootTest`, `@TestConfiguration`, `@Primary` on the clock
  bean, the `@ExceptionHandler` status mapping) is unexecuted, so a missing annotation
  or a context-loading failure would not have been caught.

What WAS verified, on JDK 21.0.12.1:

- The five pure-JDK classes (`Note`, `NoteStatus`, `ValidationException`,
  `NoteNotFoundException`, and `NoteService` with its `@Service` annotation stripped)
  compile with `javac`, exit 0.
- The domain rules were executed by a scratch JDK harness outside this repo, covering
  the same logic as `NoteServiceTest`: 12 checks, 12 passed.
- Mutation check through that harness: making the already-published branch re-stamp
  `publishedAt` turned 3 of the 12 red, including the idempotency check and the
  concurrent-publish check. Reverted, 12 passed again.

That is real evidence for the RULES and no evidence at all for the SPRING WIRING.
Treat the Java example as reviewed-and-reasoned rather than proven, and run
`mvn -B test` before trusting it.
