# Python + Flask + pytest

A thin vertical slice: one domain object, one operation with a real rule, one edge case.
Small on purpose. The point is the shape of the workflow, not the application.

## What this demonstrates

A meeting note has a title, a body, and a status. It can be created as a draft and
published. Publishing has three rules worth testing:

- **Happy path.** A draft with content becomes published and gets a timestamp.
- **Validation failure.** A blank or whitespace-only body cannot be published.
- **Idempotency edge case.** Publishing an already published note is not an error and
  does not move `published_at`.

The rules live in `app/notes.py`, which imports no Flask. `app/api.py` is the web layer
and holds no rule.

## Setup

Python 3.13 or newer.

```bash
cd examples/python-flask
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `python3 -m venv` reports that `ensurepip` is unavailable, either install the
`python3-venv` package or use [uv](https://github.com/astral-sh/uv):

```bash
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Run

```bash
python -m pytest -q -rfE          # tests
ruff check . --output-format=concise
ruff format --check .
flask --app app.api run --port 5001   # the API, if you want to poke it
```

Through the gate runner, which lives at `../../gates/`:

```bash
node ../../gates/run-gates.mjs
```

## What was actually run

Everything below was executed on this machine, Python 3.13.5, Flask 3.1.0, pytest 8.3.4.

```
$ python -m pytest -q -rfE
.................                                                        [100%]
17 passed in 0.23s

$ ruff check . --output-format=concise
All checks passed!

$ ruff format --check .
6 files already formatted
```

Ruff was not clean on the first run. It reported five real findings: one line over 100
characters, one `Optional[X]` that should be `X | None`, and three `timezone.utc` uses
that should be `datetime.UTC` on this Python version. All five were fixed rather than
suppressed.

**Mutation verification of the idempotency rule.** The green run above only means
something if the tests can fail. Changing `publish_note` so the already-published branch
re-stamps `published_at`:

```
3 failed, 14 passed
FAILED tests/test_api.py::test_publish_twice_returns_200_both_times
FAILED tests/test_notes.py::test_publish_is_idempotent
FAILED tests/test_notes.py::test_publish_of_already_published_note_survives_a_blanked_body
```

Reverted, 17 passed again.

**Verified on the wire too**, against a real server on port 5099, because a green test
suite and a working HTTP endpoint are two different claims:

```
GET  /health                    {"notes":0,"status":"ok"}
POST /notes                     201, id 734df732-...
POST /notes/{id}/publish        200, published_at 2026-08-26T10:39:37.715504+00:00
POST /notes/{id}/publish  again 200, published_at 2026-08-26T10:39:37.715504+00:00
POST /notes/{blank}/publish     422
POST /notes/nope/publish        404
```

The two `published_at` values are byte-identical, which is the idempotency rule holding
across two separate HTTP requests rather than two function calls.

**Since run:** the gate runner, after it was finished. `node ../../gates/run-gates.mjs`
from this directory reports **3 PASS** (lint, format, test). Verified locally with
Python 3.13.5, Flask 3.1.0, pytest 9.0.2, ruff 0.15.6 — newer than the pins above,
which is what CI uses. At authoring time the runner was still being built and only
the commands inside the config had been run by hand.

## How the method shows up here

| Concept | Where it lives | What to look at |
| --- | --- | --- |
| **Spec-driven development** | `specs/` | `prd.md` has a locked-decisions table. D4 locks the ORDER of the two publish checks, which is the kind of constraint that no amount of reading the code recovers once it is lost. `epic-01-notes/epic.md` maps four feature IDs onto one story. |
| **TDD** | `tests/test_notes.py` | `test_publish_is_idempotent` hands the second call a DIFFERENT clock value, so it can observe a re-stamp. A test that asserts something did not change is worthless unless it could have seen the change. |
| **Compound engineering** | `specs/epic-01-notes/story-01-publish-note.md`, section "Dev agent record" | Two real traps: a module-scope `create_app()` that leaked one dict across every test and broke unrelated tests when a new one was added, and a `datetime.now()` inside the rule that made the idempotency test pass against broken code. Each ends in a rule, and one produced a permanent guard, `test_two_apps_do_not_share_a_store`. |
| **Local CI enforcement** | `gates.config.json` | Three gates. The `pytest` gate carries `-rfE` because that flag is what produces the `FAILED path::test` summary lines the parser reads. Without it every run parses as green. |

### The Flask-specific trap, in one line

Build the app inside the test fixture, never at module scope. A module-scope
`create_app()` shares one store across the whole file, and the resulting failures point
at the wrong tests. `tests/test_api.py::test_two_apps_do_not_share_a_store` exists only
to catch that regression, and looks pointless until the day it fires.

## Files

```
app/notes.py      domain rules, no Flask import
app/api.py        routes and error mapping, no rules
tests/            9 domain tests, 8 API tests
specs/            prd.md, epic, one dev-ready story with the trap record
gates.config.json ruff, ruff format, pytest
```
