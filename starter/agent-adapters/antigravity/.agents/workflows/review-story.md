# Review a finished story

Invoke this after a story is implemented and before it merges. The point is not to admire the
diff. It is to catch what a green test suite could not, and to convert what you learn into
something that makes the next story cheaper.

Review the diff, not the commit messages. A commit message is a claim. The diff is the evidence.

## 1. Verify the work is what was asked for

- Read the story's acceptance criteria. For each one, name the code that satisfies it. If you
  cannot name it, it is not done, whatever the ledger says.
- Check the locked decisions in `00-project.md`. Each still holds, including the ones no
  acceptance criterion restated.
- Run the tests yourself. Do not trust a reported result.

## 2. Verify the tests are real

This is the part that catches what the suite missed.

- For the most important new test, break the code it protects and confirm that specific test goes
  red. If it stays green, the test is decorative and the behavior is unprotected.
- Check that negative assertions have a positive control somewhere. "X did not change" with no
  test proving the detector can fire is not a check.
- Check the boundary cases. Absent, present-but-null, and present-but-empty are three states.
  A test covering one of them is not covering the invariant.
- Check that mocks assert on values, not only that a call happened.

## 3. Look for what the tests cannot see

- Is any new list endpoint unpaginated?
- Is there a query inside a loop?
- Does any outbound call lack a timeout?
- Does a new protected operation check authorization on the server, in the handler, including
  object-level ownership and not just the role?
- Did a secret reach the diff, including test fixtures and seed data?
- Does a failure path fall through to allow?
- Does a schema change ship with its migration, and does it avoid creating a column and making it
  NOT NULL in one step?

## 4. Sync the documentation

A behavior change silently invalidates the paragraph that described the old behavior. The tests
will not tell you, because documentation has no tests.

- Grep the docs for what changed. Field names, status codes, defaults, endpoint paths.
- Fix both homes: working notes stay with the workflow, team-facing pages live under `docs/` and
  carry no private workflow references and no internal spec IDs.
- Verify claims against the code rather than reading the prose and nodding. Diff the field names
  the doc uses against the names the schema actually declares. Reading cannot find a field that
  does not exist.

## 5. Record the lesson

This is the step that makes the method compound, and it is the step that gets skipped.

Ask one question: **did anything get through that a passing test suite should have caught?**

If yes, write one or two sentences in the recorded-lessons section of `20-testing.md`. Name the
trap, not the story. "Patching the importing module is inert when the import is inside the
function body" is a lesson. "Story 3.2 had a mocking issue" is a note nobody can use.

If nothing got through, write nothing. "None this run" is a valid answer, and a lessons file
padded with non-lessons is a lessons file nobody reads.

## 6. Absorb one manual step

Ask a second question: **what did I do by hand this round that a script or a guard could do?**

Pick one. Write it. Then mutation-verify it, which means introducing the exact violation it exists
to catch and watching it fail. A guard that has never fired is a guard nobody knows is broken.

Prefer turning a rule into a guard over writing a longer rule. A rule asks the model to remember.
A guard does not care whether the model remembered.

"None this run" is valid here too.

## 7. Report

Say what you checked, what you found, what you fixed, and what you deliberately left. Name
commands and their output. Mark anything you could not verify as unverified rather than leaving a
reader to assume you checked it.
