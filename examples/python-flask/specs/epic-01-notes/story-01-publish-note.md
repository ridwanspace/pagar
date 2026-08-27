# Story 01: Publish a note

**Epic:** [epic.md](epic.md)
**Status:** done
**Feature IDs:** FR-01-01, FR-01-02, FR-01-03, FR-01-04

## Context an implementer needs

The domain rule lives in `app/notes.py`, which imports no Flask (PRD D5). The Flask
layer in `app/api.py` parses the request, calls the domain, and maps exceptions onto
status codes. The store is a plain dict held per app instance.

`publish_note` takes a `now` callable so a test can hand it two different times (PRD D6).
Do not replace it with a direct `datetime.now()` call. The idempotency test needs to
prove a timestamp did NOT move, and it can only do that if the second call would have
produced a different value.

## Acceptance criteria

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | no note exists | POST `/notes` with a title and a body | 201, status `draft`, `published_at` null |
| AC2 | no note exists | POST `/notes` with a blank or whitespace title | 422, `field` is `title` |
| AC3 | a draft note with a non-empty body | POST `/notes/{id}/publish` | 200, status `published`, `published_at` set |
| AC4 | a draft note with an empty or whitespace-only body | POST `/notes/{id}/publish` | 422, `field` is `body`, and the note is still a draft |
| AC5 | a note already published at T1 | POST `/notes/{id}/publish` again | 200, `published_at` is still T1 |
| AC6 | a note published at T1 whose body was later blanked | POST `/notes/{id}/publish` again | 200, still published at T1, no 422 |
| AC7 | an id that does not exist | POST `/notes/{id}/publish` | 404 |

AC5 and AC6 are the edge-case budget for this story. AC6 exists because it is the only
criterion that pins the ORDER of the two checks (PRD D4). Without it, swapping them
leaves every other test green.

## Tasks

- [x] Write `Note`, `ValidationError`, `NotFoundError` in `app/notes.py`.
- [x] Write `create_note` with the title and body-length rules.
- [x] Write `publish_note` with the published check BEFORE the body check.
- [x] Write the domain tests, and watch each one fail before writing the rule.
- [x] Write `create_app` with the three routes and two error handlers.
- [x] Write the API tests through the Flask test client.
- [x] Mutation-verify AC5: make publish re-stamp the timestamp, confirm red.
- [x] Add `gates.config.json` with ruff and pytest.

## Dev agent record

### Trap: the Flask app context, and how it hid behind a passing test

Writing the API tests, the obvious first shape was to build the app once at module
scope and share it:

```python
app = create_app()          # module level

def test_publish():
    with app.test_request_context():
        ...
```

Two things went wrong, and only the second one was obvious.

The first: any test that touched `jsonify` or `request` outside a request context
raised `RuntimeError: Working outside of application context`. That one is loud and
gets fixed in a minute. The fix is the `client` fixture, which pushes a context per
request.

The second cost an hour. Because `app` was built once at module scope, the `store`
dict inside `create_app` was also built once and shared by every test in the file.
Tests passed individually and passed as a file, because pytest happened to run them in
an order where the leftover state did not collide. Adding one test later, in the
middle, broke two unrelated tests that had not changed. The failure pointed at the
wrong tests.

**Rule taken from this:** build the app inside the fixture, never at module scope, and
assert the isolation rather than assume it. `test_two_apps_do_not_share_a_store` in
`tests/test_api.py` exists only to catch this class of regression. It looks like a
pointless test until the day someone moves `create_app()` back to module scope.

### Trap: `datetime.now()` inside the rule made the idempotency test lie

The first version of `publish_note` called `datetime.now(timezone.utc)` directly. The
idempotency test then read:

```python
publish_note(store, "n1")
before = store["n1"].published_at
publish_note(store, "n1")
assert store["n1"].published_at == before
```

That test passes even when publish re-stamps the timestamp on every call, because two
calls a few microseconds apart can land on the same value depending on clock
resolution. It went green against deliberately broken code. Injecting `now` and handing
the second call a visibly different time is what made the test able to fail.

**Rule taken from this:** a test that asserts something did NOT change must be able to
observe the change. If the two states are indistinguishable, the assertion proves
nothing.

### Mutation verification performed

Changed `publish_note` so the already-published branch re-stamps `published_at`:

```
3 failed, 14 passed
FAILED tests/test_notes.py::test_publish_is_idempotent
FAILED tests/test_notes.py::test_publish_of_already_published_note_survives_a_blanked_body
FAILED tests/test_api.py::test_publish_twice_returns_200_both_times
```

Reverted, 17 passed. The tests fail for the right reason, so the green run means something.
