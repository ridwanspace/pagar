# Implement a story

Invoke this when you have one dev-ready story to implement. It replaces the "just start coding"
default with a sequence that ends in evidence rather than a claim.

Do not implement anything that is not mapped to a task in the story. If the story is wrong, fix
the story and say so. Do not silently build something better.

## 1. Load the target

- Read the story file end to end. It was written to be self-sufficient, so read all of it before
  writing any code.
- Read only the files the story names. Do not explore the codebase broadly.
- Mark the story in progress in whatever ledger this project uses.
- Find the first task that is not finished.

Stop here and ask if the story is ambiguous in a way that changes what you would build. One
specific sentence naming the ambiguity. Do not guess and proceed.

## 2. Implement, one task at a time

For each task, in the order the story lists them:

**Write the test first.** Write the assertion for the behavior the task describes.

**Run it. Watch it fail.** Read the failure message. It must fail for the reason you expect, not
because of a typo or a missing import. A test that fails for the wrong reason has told you
nothing.

**Write the smallest code that makes it pass.** Not the general version. Not the version that also
handles the next task.

**Run it again. Watch it pass.**

**Mutation-verify anything you will rely on.** Break the code on purpose. Confirm that the test
you just wrote is the one that goes red, not merely that something went red. Restore the code.

**Update the story file** as you go: tick the task, note anything surprising, list the files you
touched. Do this while it is fresh, not at the end.

Then move to the next task. Do not skip ahead, and do not stop at "good progress". Run to
completion or to a real blocker.

## 3. Stop only for these

- The spec is ambiguous and both readings are defensible.
- The work needs a decision nobody has made.
- A test fails for a reason unrelated to your change.
- You need a dependency, a schema change, or a credential you do not have.
- Implementing the task would break a locked decision in `00-project.md`.

Anything else, keep going.

## 4. Validate

Run every gate, and keep the output:

- The scoped test suite for what you touched.
- The linter.
- The type checker.
- The full suite, once, at the end. Its failure count must not have grown.

Then check the story by hand:

- Every acceptance criterion is implemented. Go through them one at a time, naming the code that
  satisfies each.
- Every locked decision still holds. These are requirements even when no acceptance criterion
  restates them.
- A schema change has its migration in the same change.
- Documentation describing behavior you changed is updated.
- No debugging leftovers: no stray prints, no commented-out code, no TODO you added.

## 5. Finish

- Mark the story done, but only if its tests exist and pass. Not because the code looks finished.
- Write back anything implementation revealed that the plan got wrong. Drift discovered and not
  recorded is drift rediscovered by the next person.
- Report: what you built, which commands you ran, what their output was, and anything you could
  not verify.

Do not report "should work". Name the command and show what it printed.
