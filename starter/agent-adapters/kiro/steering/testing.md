# Testing

A custom steering file. Kiro's conventional three are `product.md`, `tech.md`, and
`structure.md`, and custom files are supported alongside them. Testing gets its own file here
because it is the part of this method that does the most work, and burying it inside `tech.md`
buries the part that matters.

Replace every `{{PLACEHOLDER}}`. Delete what does not apply.

## The one rule everything else follows from

**A test that has never been seen to fail is not evidence.**

It is a green check mark, which is not the same thing. A test written after the code, that passes
on its first run, tells you nothing about the code. It may be asserting something that was
already true before the code existed. It may be asserting nothing at all.

So: write the assertion, run it, watch it fail for the reason you expect, then make it pass.

## Mutation verification

Before you rely on a test, break the code on purpose and watch that test go red.

```
1. The test passes.
2. Break the code the test is supposed to protect.
3. Run the test. It MUST fail.
4. Read WHICH test failed. It must be the one you just wrote.
5. Restore the code. The test passes again.
```

Step 4 is the one people skip, and it is where the information is. If you break the code and three
tests fail but none of them is yours, your test does not cover what you think it covers. A count
of failures is not a signal. The identity of the failure is.

If the test stays green while the code is broken, the test is broken. You have learned nothing
about the code, and you now have a test that will never catch this bug again.

Mutation-verify anything you plan to trust: a new guard, a regression test for a bug you just
fixed, any test that is the only thing standing between a mistake and production.

## What to assert

- **Cover the invariant, not the happy path.** The happy path is the case you already thought
  about. Bugs live in the cases you did not.
- **Absent and empty are different states.** A missing field, a field present and null, and a
  field present and empty are three cases. Most code handles one of them and is surprised by the
  other two.
- **Assert on values, not just on calls.** "The function was called" passes when the function was
  called with completely wrong arguments.
- **A negative assertion needs a positive control.** Before you trust "X did not change", write
  the case where X does change and watch that assertion fire. Otherwise you cannot distinguish a
  passing test from a test that never reached the assertion.
- **A capture-based test needs a "did we get here" check first.** A dictionary filled by a side
  effect proves nothing if the code raised before reaching the side effect. Assert the key exists,
  then assert what is in it.

## Mocking traps

- **Patch a name where it is looked up, not where it is defined.** A from-import copies the
  reference, so you patch the importing module's attribute. The inverse trap: an import inside a
  function body means the lookup happens at call time, so patching the importing module is inert
  and you must patch the definition site.
- **A mock accepts any signature.** Changing a function's parameters is invisible to every call
  site that mocks it. When you widen or rename a parameter, grep for assertions on its value, not
  just for call sites.
- **Prefer a small hand-written fake over a permissive mock** for anything that stands in for a
  real entity. A permissive mock auto-creates every attribute you ask for, so a typo in an
  attribute name passes silently.
- **If a patched mock appears never to have run and no error appeared, assert it was called**
  before you trust anything downstream of it.

## Layout and commands

- Test layout: {{TEST_LAYOUT, e.g. "tests/ mirrors src/, files named test_*.py"}}
- Run one file while working: `{{TEST_SCOPED_COMMAND}}`
- Run everything at the gate: `{{TEST_COMMAND}}`
- Coverage: `{{COVERAGE_COMMAND}}`

Scoped while you work, full suite before you claim done. Running everything after every edit is
slow enough that people start skipping it, and a gate people skip is not a gate.

## Baselines

A project with existing test debt needs a recorded baseline of what was already failing before
you arrived. Otherwise every run drowns the one new failure that is yours in a hundred old ones,
and you learn to ignore red.

Record the baseline once. Judge your work by two things: your scoped tests pass, and the failure
count did not grow.

{{BASELINE_LOCATION_AND_HOW_TO_REFRESH_IT}}

## Guards

A guard is a test that checks a rule about the codebase rather than a behavior of the code. "No
handler is missing an authorization check." "Every migration has a down step."

Two rules for writing one:

- **Parse structure, do not match substrings.** A guard that greps for a string fires on the same
  string inside a comment, inside a docstring, and inside a test fixture. Parse the code, or at
  minimum strip comments first.
- **Mutation-verify it before you trust it.** Introduce the exact violation the guard exists to
  catch. Watch it fail. A guard that has never fired is a guard nobody knows is broken.

## What "done" means

- [ ] Tests exist for the new behavior.
- [ ] You watched them fail before they passed.
- [ ] The scoped suite passes, and you have the output.
- [ ] The failure count of the full suite did not grow.
- [ ] Linter and type checker pass.

Never mark work done on a test you have not run. Not "the tests should pass". Run them.
