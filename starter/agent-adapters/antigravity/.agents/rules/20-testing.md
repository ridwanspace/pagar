# Testing

Always active. This is the rule that does the most work, so it gets the most space.

Replace every `{{PLACEHOLDER}}`.

## The one rule everything follows from

**A test that has never been seen to fail is not evidence.**

It is a green check mark, which is a different thing. A test written after the code, passing on
its first run, tells you nothing about the code. It may assert something that was already true
before the code existed. It may assert nothing at all.

So: write the assertion, run it, watch it fail for the reason you expect, then make it pass.

## Mutation verification

Before you rely on a test, break the code on purpose and watch that test go red.

```
1. The test passes.
2. Break the code the test is supposed to protect.
3. Run it. The test MUST fail.
4. Read WHICH test failed. It must be the one you just wrote.
5. Restore the code. It passes again.
```

Step 4 is where the information is, and it is the step people skip. If you break the code and
three tests fail but none is yours, your test does not cover what you think it covers. A count of
failures is not a signal. The identity of the failure is.

If the test stays green while the code is broken, the test is broken. You have learned nothing
about the code, and you now hold a test that will never catch this bug again.

Mutation-verify anything you plan to trust: a new guard, a regression test for a bug you just
fixed, any test that is the only thing between a mistake and production.

## What to assert

- **Cover the invariant, not the happy path.** The happy path is the case you already thought
  about. Bugs live in the cases you did not.
- **Absent and empty are different states.** A missing field, a field present and null, and a
  field present and empty are three cases. Most code handles one and is surprised by the others.
- **Assert on values, not just on calls.** "The function was called" passes when it was called
  with completely wrong arguments.
- **A negative assertion needs a positive control.** Before trusting "X did not change", write the
  case where X does change and watch that assertion fire. Otherwise you cannot tell a passing test
  from a test that never reached its assertion.
- **A capture-based test needs a "did we get here" check first.** A dictionary filled by a side
  effect proves nothing if the code raised before reaching the side effect. Assert the key exists,
  then assert its contents.

## Mocking traps

- **Patch a name where it is looked up, not where it is defined.** A from-import copies the
  reference, so you patch the importing module's attribute. The inverse trap: an import inside a
  function body means the lookup happens at call time, so patching the importing module is inert
  and you must patch the definition site.
- **A mock accepts any signature.** Changing a function's parameters is invisible to every call
  site that mocks it. When you widen or rename a parameter, grep for assertions on its value, not
  just for call sites.
- **Prefer a small hand-written fake over a permissive mock** for anything standing in for a real
  entity. A permissive mock auto-creates every attribute you ask for, so a typo passes silently.
- **If a patched mock appears never to have run and no error appeared, assert it was called**
  before trusting anything downstream.

## Guards

A guard is a test that checks a rule about the codebase rather than a behavior of the code. "No
handler is missing an authorization check." "Every migration has a down step."

- **Parse structure, do not match substrings.** A guard that greps for a string fires on that
  string inside a comment, a docstring, and a test fixture. Parse the code, or at minimum strip
  comments first.
- **Mutation-verify it before you trust it.** Introduce the exact violation it exists to catch.
  Watch it fail. A guard that has never fired is a guard nobody knows is broken.

## Baselines

A project with existing test debt needs a recorded baseline of what already failed before you
arrived. Otherwise every run buries your one new failure under a hundred old ones, and you learn
to ignore red.

Record it once. Judge your work by two things: your scoped tests pass, and the failure count did
not grow.

{{BASELINE_LOCATION_AND_HOW_TO_REFRESH_IT}}

## Layout and commands

- Layout: {{TEST_LAYOUT, e.g. "tests/ mirrors src/, files named test_*.py"}}
- One file, while working: `{{TEST_SCOPED_COMMAND}}`
- Everything, at the gate: `{{TEST_COMMAND}}`
- Coverage: `{{COVERAGE_COMMAND}}`

## What "done" means

- [ ] Every acceptance criterion is implemented.
- [ ] Tests exist for the new behavior.
- [ ] You watched them fail before they passed.
- [ ] The scoped suite passes, and you have the output.
- [ ] The full suite's failure count did not grow.
- [ ] Linter and type checker pass.
- [ ] No debugging leftovers: no stray prints, no commented-out code, no TODO you added.
- [ ] Docs describing the old behavior are updated.

Never mark work done on a test you have not run. Not "the tests should pass". Run them.

## Recorded lessons

When something bites you that a passing suite did not catch, add a line here. That is the loop
that makes the next task cheaper than this one. One or two sentences. Name the trap, not the
story.

- {{LESSON_1}}
- {{LESSON_2}}
