# Worked examples

Four minimal projects, one per stack, all building the **same** thin slice. Read one and
you can read the others by diffing against it.

The docs in `../docs/` describe the method in stack-neutral terms. These are the concrete
proof that it instantiates in more than one language.

## The shared slice

A **meeting note** has a title, a body, and a status. Two operations: create and publish.
Publishing carries three things worth testing, chosen because they map onto what the
method emphasises:

| | Rule | Why it is here |
| --- | --- | --- |
| Happy path | A draft with content becomes published and gets a timestamp. | Something has to work. |
| Validation failure | A blank or whitespace-only body cannot be published. | A rule with a real edge, whitespace, that a naive check gets wrong. |
| Idempotency edge case | Publishing an already published note is not an error and does not move the timestamp. | The interesting one. It cannot be tested without an injected clock, which is the whole TDD lesson in miniature. |

Every example also locks one decision that no test would recover on its own: **the
already-published check runs BEFORE the body check**. Swap them and a note published
yesterday starts failing today because someone edited its body. Exactly one test in each
stack pins that order.

## Which to start with

| If you want | Start with |
| --- | --- |
| The shortest read | [`go/`](go/). No dependencies, no build config, no framework. |
| The named type-check trap | [`node-react/`](node-react/). It is the one with `tsconfig.tests.json`. |
| The most familiar shape | [`python-flask/`](python-flask/). |
| An honest account of a partial verification | [`java-spring/`](java-spring/). |

## Concept to artifact, per stack

| Method concept | python-flask | node-react | go | java-spring |
| --- | --- | --- | --- | --- |
| **PRD with locked decisions** | `specs/prd.md` | `specs/prd.md` | `specs/prd.md` | `specs/prd.md` |
| **Epic with feature IDs** | `specs/epic-01-notes/epic.md` | same path | same path | same path |
| **Dev-ready story** | `specs/epic-01-notes/story-01-publish-note.md` | same path | same path | same path |
| **Rules isolated from the framework** | `app/notes.py`, imports no Flask | `src/notes.ts`, imports no React | `internal/notes/notes.go`, imports no `net/http` | `NoteService`, no `@SpringBootTest` in its tests |
| **Framework layer with no rules** | `app/api.py` | `src/NotesPage.tsx` | `internal/notes/http.go` | `NoteController` |
| **Fast rule tests** | `tests/test_notes.py`, 9 | `src/__tests__/notes.test.ts`, 13 | `notes_test.go`, 8 | `NoteServiceTest`, 10 |
| **Slower boundary tests** | `tests/test_api.py`, 8 | `src/__tests__/NotesPage.test.tsx`, 5 | `http_test.go`, 7 | `NoteControllerTest`, 8 |
| **The idempotency test** | `test_publish_is_idempotent` | `is idempotent and keeps the first timestamp` | `TestPublishIsIdempotent` | `publishIsIdempotent` |
| **Injected clock** | `now=` parameter on `publish_note` | `now: Clock` parameter | `Store.now func() time.Time` | constructor-injected `java.time.Clock` |
| **Recorded trap** | app context plus a module-scope store shared across tests | `tsc` never checks test files | `t.Parallel()` loop-variable capture | `@Transactional` on a test that rolls back nothing |
| **Gate config** | `gates.config.json` | `gates.config.json` | `gates.config.json` | `gates.config.json` |
| **Test parser** | `pytest` | `vitest` | `go-test` | `junit-xml` |
| **Lint gate** | `ruff check`, `ruff format --check` | `eslint --format json` | `go vet`, `gofmt -l` | `mvn test-compile` |
| **Type gate** | none, Python | `tsc` x2, app and tests | the compiler | the compiler |

## The flag each parser needs

The single most common way to get a green gate that means nothing is to run the tool in
its human-readable mode. Each parser reads a machine format:

| Stack | The command must carry | If you leave it out |
| --- | --- | --- |
| pytest | `-rfE` | No `FAILED path::test` summary lines, so nothing parses and every run looks green. |
| vitest | `--reporter=json` | No JSON report. The parser reports a broken gate. |
| eslint | `--format json` | Stylish output parses to nothing. |
| go test | `-json` | The parser sees no events and says so. |
| junit-xml | `reportFile` pointing at the XML | It reads files, not stdout, so it has nothing to read. |
| gofmt | `test -z "$(gofmt -l .)"` | `gofmt -l` prints offending files and still **exits 0**, so a naive gate never fails. |

## Verification status

Honesty about evidence is part of the method, so here is exactly what was executed.

| Stack | Lint / vet | Type check | Tests | On the wire | Mutation-verified |
| --- | --- | --- | --- | --- | --- |
| python-flask | ruff, clean | n/a | **17 passed** | yes, port 5099 | yes, 3 went red |
| node-react | eslint, clean | tsc x2, clean | **18 passed** | not run | yes, 4 went red |
| go | vet + gofmt, clean | compiler | **15 tests, 20 with subtests, `-race` clean** | yes, port 8099 | yes, 4 went red |
| java-spring | not run at authoring | javac on the JDK-only classes, clean | **NOT RUN at authoring, run since — green** | not run | via a scratch JDK harness only, 3 went red |

**The gate runner has since been run against all four**, after it was
finished. From each example's own directory, `node ../../gates/run-gates.mjs`:

| Stack | Gate runner result |
| --- | --- |
| python-flask | 3 PASS, lint, format, test |
| node-react | 4 PASS, including the test-file type check |
| go | 3 PASS, vet, fmt, test |
| java-spring | 2 PASS, javac via Maven + JUnit 5 through surefire |

The Node config first called its tools through `npx`, which ignores the copies already
installed under `node_modules/` and pulls different versions from the network. The gate
runner puts `node_modules/.bin` on PATH itself, so the `npx` prefix was removed and all
four gates then passed.

**Java was the honest gap at authoring time.** `mvn` was not installed and `~/.m2`
did not exist, so the JUnit suite had never executed and none of the Spring wiring
had been exercised; the domain rules were verified with `javac` and a scratch harness.
The gap was closed when the repo went public: the suite was executed by hand
(Maven 3.9.9, OpenJDK 21, Linux) and both gates pass, and CI runs it on every push.
See [`java-spring/README.md`](java-spring/README.md).

## The gate runner

Each example carries a `gates.config.json` targeting the polyglot runner at `../../gates/`:

```bash
cd examples/<name>
node ../../gates/run-gates.mjs
```

The runner puts `node_modules/.bin` first on PATH, so the Node config uses bare `tsc`,
`eslint`, and `vitest` rather than `npx`.

## What the examples deliberately leave out

No database, no auth, no persistence across a restart, no editing or unpublishing. Each of
those needs a rule nobody has written, and inventing one would be guessing. Both of the
open questions in every `prd.md` are real: whether an editor can unpublish, and whether
editing a published note republishes it or forks a version. They are left open on purpose,
because that is what an open question looks like in a real PRD.
