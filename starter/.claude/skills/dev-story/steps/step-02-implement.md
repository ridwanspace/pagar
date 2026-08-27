# Step 02: Implement (task by task, red-green-refactor)

## Step goal

Implement the story's tasks **in order**, each via red-green-refactor, updating the dev story's
tracking sections as you go, **running continuously to completion** except on a HALT trigger.

## Mandatory rules

- 📏 **Follow the tasks EXACTLY as written, in order.** NEVER implement anything not mapped to a
  task. NEVER skip ahead.
- 🧪 **Tests first.** NEVER mark a task done until its tests exist and pass.
- 🛡️ **Honor the story's guardrails.** They are requirements even when no criterion restates them.
- 🏃 **Run continuously.** Do not stop for "milestones" or "good progress". Only the HALT triggers
  in `SKILL.md` pause you.
- 🔎 **Scoped reads only:** the files in the story's files table, and a cited source section if you
  must verify something.

## The loop: repeat for each incomplete task, top to bottom

### A. Read the task

Take the current task from the dev story. **It is your authoritative spec.** Note which criteria
it maps to and which guardrails apply.

### B. RED: write failing tests first

- Write the tests for this task's behaviour, in the location the story's testing section names,
  **including the invariant cases the guardrails require**: a double-submit stays idempotent,
  authorization tested **both in and out of scope**, any declared identity still holds after the
  mutation.
- **Run them. Confirm they FAIL.** This is what proves the tests are real.

### C. GREEN: minimal implementation

- Write the **minimal** code to pass the tests, following the story's architecture guidance and
  the project rules: typed signatures, schema validation at the boundary, long work moved to a
  background job, structured logging, no silent catch, and the client-side conventions.
- For files marked **UPDATE**: **read the file first**, change only what is needed, and
  **preserve the behaviours the story's "must preserve" column lists.**
- For files marked **NEW**: place them at the correct project location, and **register them in
  the composition root** if the project requires registration for them to be reachable.
- **Schema change? Write the MIGRATION FILE FIRST**, with idempotent guards, then the model
  change. **A model edit without a migration file is a shipped bug on every existing database**,
  because automatic table creation will not alter an existing table.
- **Use the exact patterns the story cites.** Do not reinvent a pattern the story, or a previous
  story, already established.
- **Run the tests. Confirm they PASS.** Handle the edge and error cases the task specifies.

### D. REFACTOR

Improve structure while keeping tests green. Keep it consistent with the patterns the previous
story established.

### E. Update the dev story tracking: permitted sections only

You may modify **ONLY** these sections of the dev story file:

- **Tasks and subtasks**: check the task done **only after** its tests pass and its criteria are
  satisfied.
- **Dev agent record → completion notes and debug log**: a terse note of what you implemented
  and any decision or gotcha. **Especially record TRAPS: anything that bit you that a green test
  suite did not catch**, a misleading API, an ordering hazard, a configuration surprise.
  **These notes feed the lessons mining later. They are how the pipeline compounds. Do not
  sanitize them into blandness.**
- **File list**: every file created, modified, or deleted, with repository-relative paths.

**Do NOT edit the story's acceptance criteria, guardrails, architecture, or references here.** If
those are wrong, **that is a spec conflict**, which is a HALT trigger handled in step 04.

### F. Next task

Move to the next unchecked task. **Do not proceed until the current task is complete and its tests
pass.**

## HALT triggers: pause and ask, do not freelance

- A new dependency beyond the story → **ask before installing anything.**
- Three consecutive failures on the same task → stop, summarize what you tried, ask for guidance.
- Missing configuration → stop, **name exactly what is missing.**
- The task contradicts the PRD, the epic, or an invariant → stop, note it for the step-04
  writeback, suggest `/edit-prd` or `/epics`. **Do not silently diverge.**

If you HALT, leave the tracking accurate up to that point, keep the status in progress, and tell
the user **precisely where you stopped and why.**

## Route

When **all** tasks are checked, read fully and follow `steps/step-03-validate.md`.

## Success / failure

✅ **Success:** every task implemented in order via red-green-refactor. Tests written first and
passing. Only permitted dev-story sections updated. File list complete. Guardrail cases tested.
**UPDATE files' preserved behaviours intact.** Ran continuously to the end, or HALTed correctly.

❌ **Failure:** implementing unmapped work. Skipping or reordering tasks. **Marking a task done
without passing tests.** Editing forbidden story sections. Stopping for non-HALT reasons.
Reinventing a cited pattern.

**Master rule:** One task at a time, tests first, honestly checked, and the dev story's tracking
always reflects reality.
