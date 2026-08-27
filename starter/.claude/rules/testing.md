---
description: Testing conventions and discipline. Layout, scoped runs, the baseline gate, red-green-refactor, must-cover lists per story, mock traps, and the structural-guard mechanism with mandatory mutation verification
paths:
  - "{{TEST_DIR}}/**"
  - "**/*.test.*"
  - "**/__tests__/**"
---

# Testing rules

> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/testing.md` (committed).

## Where tests live and how to run them

Fill in the real facts, verified, dated. The three things an agent gets wrong without them:

- **Layout.** Flat directory, mirrored tree, colocated beside the source, or two conventions
  that coexist. If two coexist, say which one a new test joins: **match the neighbour**.
- **The exact run command**, including any working directory or path setup the imports need.
  `{{TEST_COMMAND}}` for everything, `{{TEST_COMMAND_SCOPED}}` for one file or pattern. If
  running from the wrong directory breaks every import, write that down, because the failure
  message will not say so.
- **What CI actually runs**, verbatim, and **when**. ⚠ If CI only runs on pull or merge
  requests, then a plain push runs nothing, your local gate is the first signal anyone gets,
  and "it passed CI" has not happened yet.

Also record: what a test needs to run. If the suite runs with in-memory storage and fakes,
with no live database, cache, or model weights, say so. That fact is the difference between an
agent running the tests and an agent deciding they cannot be run.

## Run scoped, judge by scoped-green

Run the tests for what you touched. Judge the story by **scoped-green plus new tests passing**,
not by a full-suite run you waited ten minutes for.

That only works with a **baseline**. Record the full-suite result once, on a clean checkout, in
`{{BASELINE_DIR}}`. After that, the gate flags only **NEW** failures.

Baseline discipline, all of which is load-bearing:

- The baseline may **shrink** freely. Debt got fixed, re-snapshot it.
- It **never grows** without an explicit human decision.
- **You never re-snapshot to get past a red gate.** If a failure is new and yours, fix it. If
  upstream moved the baseline, prove it from the history first, tell the user, then re-snapshot.

## Red-green-refactor, honestly

- Write the failing test first. Run it. **Confirm it fails.** A test you never watched fail is
  a test you have no evidence works.
- Never mark a task done unless its tests exist and pass.
- ⚠ **A new test that passes during the RED phase proves nothing until you mutation-verify
  it.** When a story fixes a defect that *masks* others, the masked defects' tests go green
  while their code path is still unreachable, and then become load-bearing once the mask lifts.
  For every new test that is green in the red phase, decide which it is. For the masked ones,
  delete the fix block and confirm exactly those go RED.

## Must-cover for a feature story

Every story covers, at minimum:

- The happy path, and each acceptance criterion.
- **A validation failure for every bounded field** the story adds or moves.
- **Both auth failure modes for every auth check on the route**, exercised with an in-scope
  caller and an out-of-scope one. If your roles have aliases, test through the alias, because
  the alias is the path that silently breaks.
- **Tenant or ownership isolation**: another tenant's row is not reachable.
- **Idempotency** wherever the story mutates: the same key twice produces one write.
- Error paths, using the **real** error shape the code throws, not a hand-built generic one.
- Any regression assertion the PRD's locked decisions call for.

For UI stories, add: loading and empty states, flag-gated rendering with the flag on **and**
off, and the not-yet-ready render, plus auth-gated rendering.

## Test style

- **Hand-written fakes over heavy mock frameworks**, where you have the choice. A fake that
  *records* what it received makes the assertion read like the behaviour. A mock call-args
  chain reads like the mock library.
- **Test behaviour, not implementation.** Assert on status codes, response bodies, rendered
  output, and persisted rows. Not on private call counts. Counts that drift use a lower bound,
  never "exactly N".
- **Query by accessible role and label first** in UI tests, over test ids. If your codebase has
  no test ids, do not start sprinkling them onto shared components to make one test pass.
- A test blocked on missing infrastructure gets an explicit skip **naming what is missing and
  what substitutes for it**, never fragile inline scaffolding.
- Open each test file with the case matrix it covers, one line per case. In a codebase with no
  formal spec, that matrix is the closest thing you have to one.

## Mock traps: each of these costs a real debugging detour

These generalize across languages. Write your stack's version of each.

- ⚠ **An attribute you did NOT set on an auto-mocking mock is not absent, it is a truthy
  auto-created mock**, which silently defeats fail-closed code. A default-lookup that should
  return "missing" returns a mock instead. **When a story adds a field, add it explicitly to
  every stand-in fixture, including the legacy case, in the same change.**
- ⚠ **A mock accepts ANY signature**, so widening a parameter is invisible to every call site
  that mocks it. Grep for assertions on that parameter's **value**, not just for call sites.
  Those live in files the story never listed.
- ⚠ **Patch where the name is LOOKED UP, not where it is defined**: if the importing module
  copied the reference at import time, patching the definition site is inert. The inverse
  holds for a lazy import inside a function body. **If a patched mock "never runs" with no
  error, assert it was called before trusting anything downstream.**
- ⚠ **A spy on a module's own export is silently inert when the module calls that export
  internally.** Assert the spy was called first.
- ⚠ **A mock that rejects with the WRONG SHAPE tests a situation that never happens.** If
  production throws a library-specific error object with a status and a body, a test rejecting
  with a generic error exercises a branch production never reaches.
- ⚠ **A module mock can shield the very collaborator your assertion is about.** If you mock the
  service layer in a page test, the real service, its interceptors, and its header injection
  never run, so a claim like "no token reaches the logs" passes against unfixed code. **If the
  claim is about the real thing, it belongs in a test that exercises the real thing.**
- ⚠ **A capture-variable test needs a "did we get here at all" assertion FIRST.** A dictionary
  filled by a side effect proves nothing when the code raised earlier. Assert the key is
  present before asserting its contents.
- ⚠ **A cross-type comparison is silently false**, so a negative assertion over the wrong type
  passes regardless. Prefer positive assertions with exact types.
- ⚠ **Module-scope state persists across tests in one file.** The symptom is order-dependent
  green and red that vanishes when the case runs alone. Reset modules between cases.
- ⚠ **Fake the clock, do not mutate the timezone environment variable.** Most runtimes cache
  the timezone at startup. Pick an instant where a correct and a buggy implementation actually
  diverge.
- ⚠ **Widening a string-literal union is an UNENFORCED refactor.** Adding a value produces zero
  errors when every consumer is an equality check or a ternary. Enumerate call sites by bare
  identifier and review each one, including the ones that must stay on the old value.
- ⚠ **A regression test for "new feature X must not break Y" is VACUOUS unless X is active in
  that scenario.** Ask of every regression test: if I delete the feature, does this still pass?
  If yes, it guards nothing.
- ⚠ **When one case in a batch stays red, suspect the QUERY before the code.** "Found multiple
  elements" is usually a shared prefix. Anchor on a distinctive tail.
- ⚠ **A uniformly red baseline is a smell, not a success.** The honest signal is that the
  red/green split matches the story's diagnosis. Seven of eight failing is usually one dead
  locator.
- ⚠ **When the SAME rule is implemented twice in two languages**: a client formatter mirroring
  a server one, the untested value is the one where they disagree. Write the agreement test
  across the **whole** input space, with the foreign implementation mirrored in a local helper
  that names the file it mirrors.

## Structural guard tests: the "prefer rule to guard" mechanism

A rule in a document decays as the code moves. A test that fails cannot. When a learning is
mechanically checkable, **write the guard, not the paragraph.**

The bar a guard must clear:

- **It WALKS the tree**, using a directory walk plus a file read. Never a hardcoded file list,
  because a new file must be caught automatically. Note that a version-control-based file
  listing cannot see an untracked file. Stage it before trusting a verification.
- **It is UNCONDITIONAL** for an "every file in this family must do X" rule. The conditional
  form is defeated by the likeliest regression: a new file that simply omits the thing.
- **It is import-shaped or call-shaped, never prose-shaped.** A bare substring match hits the
  prose in its own docstring and false-positives on comments. Strip comments and docstrings
  before scanning source.
- **It names what it protects.** The test name is the documentation: `test_no_orphan_route`,
  never `test_misc_guard_3`.
- **It is MUTATION-VERIFIED.** Break the code on purpose, watch the guard go RED, restore.
  **A guard that has never been seen to go red is not evidence of anything.** State the
  mutation you ran, in the notes or the commit body.

Two ways a guard silently excuses the bug it was written for:

1. **The scan unit is coarser than the rule's unit.** A whole-file check is satisfied by one
   correct sibling function. Split the scan on function boundaries.
2. **The accept-pattern matches a NAME, not a CALL.** A pattern for `goodHelper` also matches
   the line that *defines* `goodHelper`. Require a call shape.

And two more failure modes worth writing on the wall:

- ⚠ **An accept-pattern whose match may BEGIN AFTER the operator being audited cannot audit
  that operator.** Anchor every alternative so it ends at the identifier.
- ⚠ **A guard can fail the other way, by matching an identifier inside a string literal.** Run
  every guard against known-good code before trusting it, not only against the mutation.
- ⚠ **A mutation that stays GREEN means the TEST is the bug**, usually because a normalization
  step between your input and your assertion erases the difference. Ask what normalizes your
  input before the assert, and construct the case that bypasses it.
- ⚠ **A mutation probe that comes back green must be proven to have LANDED.** Grep the mutated
  identifier before believing the probe. **Revert with a targeted edit, never by discarding
  the file**, or you lose the rest of your work.
- An allowlist of known offenders must be enforced to only **shrink**, with its own test:
  every listed file must still violate the rule.

**Good guard candidates**, in rough order of value: every route module is registered in the
composition root; no forbidden import crosses a layer boundary; a registry and the document
listing it agree; teardown order respects foreign keys; exactly one instance of a shared
singleton exists in the tree.

## When a script parses freeform text, it must fail LOUD

Any helper that scans prose, a lessons miner, a dependency scanner, a docs checker, **must
print its denominator**: how many files it scanned and how many had the section. So a thin
result reads as "they wrote little" and never as "there is nothing here". Silent
under-collection is the classic bug in this family of scripts.

🚨 And a denominator does not save you: **a denominator cannot see what the matcher never
matched.** It guards against scanning too few *files*, not against collecting too few *items
per file*. **Mutation-verify the matcher against a planted case in the syntax the real corpus
uses**, not only the tidy form in the docstring.
