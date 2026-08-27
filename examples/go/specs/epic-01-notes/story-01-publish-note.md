# Story 01: Publish a note

**Epic:** [epic.md](epic.md)
**Status:** done
**Feature IDs:** FR-01-01, FR-01-02, FR-01-03, FR-01-04

## Context an implementer needs

The domain rule lives in `internal/notes/notes.go`, which imports no `net/http` (PRD D5).
`internal/notes/http.go` holds the handlers and the single error-to-status mapping.

`Store` carries an injected `now func() time.Time` (PRD D6) and a mutex (PRD D7).
`Publish` reads and writes under that lock, because `net/http` serves each request on
its own goroutine.

Routes use Go 1.22 method patterns (`"POST /notes/{id}/publish"`). Register static
routes before parameterized ones so `/notes` cannot be swallowed by `/notes/{id}`.

## Acceptance criteria

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | no note exists | POST `/notes` with a title and a body | 201, status `draft`, `published_at` null |
| AC2 | no note exists | POST `/notes` with a blank or whitespace title | 422, `field` is `title` |
| AC3 | a draft note with a non-empty body | POST `/notes/{id}/publish` | 200, status `published`, `published_at` set |
| AC4 | a draft note with an empty or whitespace-only body | POST `/notes/{id}/publish` | 422, `field` is `body`, note still a draft |
| AC5 | a note already published at T1 | POST `/notes/{id}/publish` again | 200, `published_at` is still T1 |
| AC6 | a note published at T1 whose body was later blanked | POST `/notes/{id}/publish` again | 200, still published at T1, no 422 |
| AC7 | an id that does not exist | POST `/notes/{id}/publish` | 404 |
| AC8 | a draft note with content | 8 goroutines publish it at once | exactly one timestamp, and `go test -race` is clean |

AC6 pins the ORDER of the two checks (PRD D4). AC8 exists because Go hands you
concurrency by default, so the race is real rather than theoretical.

## Tasks

- [x] Write `Note`, `ValidationError`, `ErrNotFound` in `internal/notes/notes.go`.
- [x] Write `Store` with an injected clock and a mutex.
- [x] Write `Create` with the title and body-length rules.
- [x] Write `Publish` with the published check BEFORE the body check.
- [x] Write the domain tests, and watch each one fail before writing the rule.
- [x] Write `NewHandler` with the four routes and the `writeErr` mapping.
- [x] Write the handler tests with `httptest`.
- [x] Mutation-verify AC5: make Publish re-stamp the timestamp, confirm red.
- [x] Add `gates.config.json` with `go vet`, `gofmt`, and `go test -json -race`.

## Dev agent record

### Trap: `t.Parallel()` in a table test, and the Go version that changed the answer

The table tests below use `t.Parallel()` inside each subtest:

```go
for _, tc := range cases {
    t.Run(tc.name, func(t *testing.T) {
        t.Parallel()
        // ... uses tc
    })
}
```

On Go 1.21 and earlier this is a well-known bug. `tc` was ONE variable reused across
iterations. `t.Parallel()` pauses the subtest and returns immediately, so the loop
finishes before any subtest body runs, and every subtest then reads whatever `tc` held
last. The standard fix was `tc := tc` at the top of the loop.

What made it worth writing down is HOW it fails. It does not blow up. Every subtest
silently tests the LAST case. In the `TestCreateValidation` table the last case was
`oversized body`, which is a valid rejection, so all three subtests passed while
actually testing one case three times. Two of the three rules had zero coverage and the
output said `--- PASS` three times.

Go 1.22 changed loop variable scoping so each iteration gets its own `tc`, and this
code is correct as written on the Go 1.25 this example targets. The `tc := tc` line is
no longer needed and is left out on purpose.

**Rule taken from this:** `go.mod` must declare the language version (`go 1.25` here),
not just whatever toolchain happens to be installed. The scoping fix is gated on the
declared version in `go.mod`, not on the compiler. A repo that still says `go 1.19`
gets the OLD behaviour from a new toolchain, silently. Check `go.mod` before trusting a
parallel table test.

**Second rule:** when a table test passes, change one case's expectation and confirm
that ONE subtest fails. If more than one fails, or the wrong one does, the cases are
not isolated.

### Trap: `-json` is not optional for the gate

`go test ./...` prints a human summary. The gate runner's `go-test` parser reads the
`-json` event stream and reports "produced no -json events" when it is missing. The
first gate config here ran plain `go test ./...`, and the runner correctly refused to
treat it as a green run. That is the parser doing its job: a gate it cannot read is a
broken gate, not a passing one.

### Mutation verification performed

Changed `Publish` so the already-published branch re-stamps `PublishedAt`:

```
--- FAIL: TestPublishOfPublishedNoteSurvivesBlankedBody
--- FAIL: TestPublishIsIdempotent
--- FAIL: TestConcurrentPublishStampsOnce
--- FAIL: TestPublishTwiceReturns200Both
```

Reverted, `ok example.com/notes/internal/notes`. Four tests, three of them at different
layers, all pointed at the same broken rule.
