---
description: How many edge-case acceptance criteria a story gets (3, or 5 for money/authorization/upload) and where each one must come from, the five-source derivation checklist, so edge cases stop coming from vibes and a count over 5 reads as a split signal
paths:
  - ".claude/skills/epics/**"
  - ".claude/skills/create-story/**"
  - "{{SPEC_DIR}}/**"
---

# Edge cases in stories

"Include edge cases" without a budget produces two lazy ones or fifteen bloated ones, depending
on the run. This rule gives the count a **cap** and every case a **source**.

Applies when writing acceptance criteria in `/epics` (planning stories) and `/create-story`
(dev stories).

## The budget

- **3 edge-case acceptance criteria per story.** Default.
- **5** when the story touches **money, authorization, or file upload**: the three places
  where a missed branch costs real damage.
- **Over 5 means the story is too big.** The count is a **size smell, not a coverage target.**
  Split it and let each half carry its own 3.

The cap counts *edge-case* criteria only. Happy-path criteria, and the criteria a locked PRD
decision forces such as idempotency and authorization, are **not** in the budget. They are
mandatory either way. See the must-cover list in `testing.md`.

## The five sources

Every edge-case criterion must trace to one of these. Walk the list **in order**, pick what
applies, and **write one line saying why you skipped each source you skipped.**

That line is the bloat control. It forces a deliberate "not applicable" instead of an unbounded
hunt for cleverness.

### 1. Boundaries: every bounded field gets min-1 / min / max / max+1

Only for fields **the code actually bounds**. List your real bounds here with their file and
line, dated: upload size limits, request body limits, allowed file types, every schema length
and range validator, the pagination page size.

Pick the **one** boundary the story actually moves. A story that does not change a bound does
not re-test that bound. The existing suite already owns it.

### 2. Equivalence classes: one valid representative, one invalid

Group the input space into classes that behave the same, then test one value per class. Not
every value.

This is the technique that keeps the count finite: **"all bad file types" is one class and one
criterion, not eleven criteria.**

### 3. Error paths the stack forces

Derivable from the code shape, so they need no imagination:

- **A validation failure** where the schema rejects a bounded field at the boundary.
- **Unauthenticated and forbidden**, for every auth check on the route, tested with an in-scope
  role and an out-of-scope one, through any role aliases.
- **Service unavailable**, where the health check or a dependency probe fails.
- **Not found**, for another tenant's row.

Only include the ones **this story's route actually has**. A route with no admin check does not
get a forbidden criterion.

### 4. State and concurrency

- A double submit with the same idempotency key produces exactly one write.
- A background job retried after a worker crash produces no duplicate side effect.
- The empty result set, and the first page versus the last page.
- A row deleted between the read and the write.

### 5. Domain-specific: the ones only your product has

Reach here when sources 1 to 4 come back thin. These are the cases that need real knowledge of
what your system processes: degenerate inputs, unusually large ones, inputs in an unexpected
form, and **a value just under a threshold your own processing applies**. A threshold is a
branch, and the value just below it is a real case that no generic checklist would find.

## Writing them

- One source, one criterion. Do not bundle three branches into one Given/When/Then.
- Same Given/When/Then shape as every other criterion, independently testable.
- Say the **behaviour**, not the mechanism: "**Then** the upload is rejected with a message
  naming the size limit", not "Then the validator raises".
- ⚠ Criterion numbers and story references stay in the spec file. Never let them reach committed
  code, test names, or a commit message. See `no-local-spec-refs.md`.

## What this rule does NOT try to do

**Do not script the unpredictable.** Multi-step state bugs and integration surprises are found
by exploratory testing, not by a longer criteria list. Writing more scripted edge cases past
the cap buys bloat and no coverage. Those belong in a testing charter after the story ships,
not in the story.
