# Go + net/http + go test

A thin vertical slice: one domain object, one operation with a real rule, one edge case.
Standard library only. No dependencies, so `go.sum` does not exist.

## What this demonstrates

A meeting note has a title, a body, and a status. It can be created as a draft and
published. Publishing has three rules worth testing:

- **Happy path.** A draft with content becomes published and gets a timestamp.
- **Validation failure.** A blank or whitespace-only body cannot be published.
- **Idempotency edge case.** Publishing an already published note is not an error and
  does not move `published_at`.

The rules live in `internal/notes/notes.go`, which imports no `net/http`.
`internal/notes/http.go` is the transport layer and holds no rule.

Go hands you concurrency whether you asked for it or not, so this example carries one
thing the other three do not need as urgently: the store is mutex-guarded and there is a
test that publishes from eight goroutines at once.

## Setup

Go 1.25 or newer. Nothing to install.

```bash
cd examples/go
```

## Run

```bash
go test ./...              # tests
go test -race ./...        # tests with the race detector
go vet ./...               # the compiler's own lint
gofmt -l .                 # prints unformatted files, prints nothing when clean
go run ./cmd/api           # the API on :8080, or set ADDR
```

Through the gate runner, which lives at `../../gates/`:

```bash
node ../../gates/run-gates.mjs
```

## What was actually run

Everything below was executed on this machine, Go 1.25.0 linux/amd64.

```
$ go vet ./...
(no output, exit 0)

$ gofmt -l .
(no output, exit 0)

$ go test ./...
?   	example.com/notes/cmd/api	[no test files]
ok  	example.com/notes/internal/notes	0.006s

$ go test -race ./...
?   	example.com/notes/cmd/api	[no test files]
ok  	example.com/notes/internal/notes	1.016s
```

Fifteen top-level tests, twenty counting subtests, all passing, race detector clean.

`go test -json ./...` was also run and produces 167 JSON events, which is the format the
gate runner's `go-test` parser reads.

**Mutation verification of the idempotency rule.** Changing `Publish` so the
already-published branch re-stamps `PublishedAt`:

```
--- FAIL: TestPublishOfPublishedNoteSurvivesBlankedBody
--- FAIL: TestPublishIsIdempotent
--- FAIL: TestConcurrentPublishStampsOnce
--- FAIL: TestPublishTwiceReturns200Both
FAIL	example.com/notes/internal/notes
```

Reverted, `ok`. Four tests across the domain, the concurrency case, and the HTTP layer
all point at the same broken rule.

**Verified on the wire**, against a real server on port 8099:

```
GET  /health                    {"notes":0,"status":"ok"}
POST /notes/{id}/publish        200, published_at 2026-08-26T10:39:59.063345556Z
POST /notes/{id}/publish  again 200, published_at 2026-08-26T10:39:59.063345556Z
POST /notes/{blank}/publish     422
POST /notes/nope/publish        404
```

The two timestamps are byte-identical to the nanosecond, so the rule holds across two
separate HTTP requests and not just two function calls.

**Not run:** the gate runner itself. It was still being built while this example was
written, so `gates.config.json` here is written against its documented config shape and
has not been executed. The commands inside it have all been run by hand, as shown above.

## How the method shows up here

| Concept | Where it lives | What to look at |
| --- | --- | --- |
| **Spec-driven development** | `specs/` | `prd.md` has a locked-decisions table. D4 locks the ORDER of the two publish checks. D7 is Go-specific: the store is mutex-guarded because `net/http` serves each request on its own goroutine. |
| **TDD** | `internal/notes/notes_test.go` | `TestPublishIsIdempotent` uses a clock that returns a DIFFERENT time on its second call, so it can observe a re-stamp. `TestConcurrentPublishStampsOnce` runs eight goroutines and is meant to be run under `-race`. |
| **Compound engineering** | `specs/epic-01-notes/story-01-publish-note.md`, section "Dev agent record" | The `t.Parallel()` loop-variable trap, including the part that matters: it does not crash, it silently tests the LAST table case N times and prints `--- PASS` for all of them. |
| **Local CI enforcement** | `gates.config.json` | Three gates. `go test` carries `-json` because the parser reads the event stream. The `gofmt` gate is `test -z "$(gofmt -l .)"` because `gofmt -l` prints offending files and still exits 0, so a naive gate would never fail. |

### The Go-specific trap, in one line

`t.Parallel()` inside a table subtest read the LAST loop variable on Go 1.21 and
earlier, so every subtest tested one case and all of them printed PASS. Go 1.22 fixed
the scoping, but **the fix is gated on the version declared in `go.mod`, not on the
installed toolchain**. A repo still saying `go 1.19` gets the old behaviour from a new
compiler, silently. Check `go.mod` before trusting a parallel table test.

## Files

```
internal/notes/notes.go       domain rules, no net/http import
internal/notes/http.go        routes and error mapping, no rules
internal/notes/notes_test.go  domain tests including the concurrency case
internal/notes/http_test.go   handler tests with httptest
cmd/api/main.go               server with timeouts
specs/                        prd.md, epic, one dev-ready story with the trap record
gates.config.json             go vet, gofmt, go test -json -race
```
