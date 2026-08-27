# Step 06: Improve the pipeline itself (the chassis, not the cargo)

## Step goal

**Every other step in this workflow makes the CODEBASE compound. This step makes the WORKFLOW
compound.**

Steps 01 to 05 are **paid at full price on every story, forever**: you hand-ran a check, you
hand-noticed a document drift, you hand-decided a rule was worth writing.

**Some of that judgment is genuinely human. Some of it was MECHANICAL WORK YOU DID BY HAND BECAUSE
NO SCRIPT EXISTED YET, and that part is a recurring tax that will be paid roughly one more time
for every story left in the backlog.**

This step finds that tax and kills it. **One question:**

> **What did I just do by hand, this run, that a script or a test should have done for me?**

## Mandatory rules

- 📖 Read this whole step before acting.
- 🎯 **At most ONE improvement per story.** This step must not become its own project. **If nothing
  qualifies, say so and move on. A forced "improvement" is worse than none.**
- 🧱 **Prefer a ratchet over a reminder.** A prose rule is a note to your future self **and it
  DECAYS as the code moves. A test that fails is a law and it CANNOT.** If the thing you learned
  is mechanically checkable, **write the guard, not the paragraph.**
- 🛑 **Do not refactor the pipeline on a hunch.** The trigger is something that **actually happened
  in this run**, not something that might.
- 🔁 The output is **a committed change** to a script, a skill, or a guard test, **or an explicit
  "nothing this run".**

## Sequence

### 1. Scan this run for repeated manual work

Look back at what steps 01 to 05 actually cost you. The qualifying signals, **in descending order
of value**:

| Signal | What it means | The fix |
| --- | --- | --- |
| **I hand-checked something a test could assert** | A rule was written as prose that a guard could enforce | **Write the guard test** (section 2) |
| **I hand-derived something a script could compute** | Hand-searched for dependents, hand-counted a registry, hand-diffed a document | Add a subcommand to the spec helper |
| **I re-learned something a prior story already knew** | The lessons mining did not surface it, or `/create-story` did not read it | **Fix the extractor, or the step that should have fed it forward** |
| **A step's instructions were wrong or stale** | The step file sent you down a wrong path | **Edit the step file. The skill is code too.** |
| **I did the same fiddly thing as last story** | Same migration dance, same seed reset, same probe script | Script it |

**The single highest-value pattern is rule → guard.** Classic candidates that start life as things
someone had to remember: "every route module must be registered in the composition root", "no
forbidden import crosses this layer boundary", "this registry and its documentation appendix must
match", "teardown order must respect foreign keys".

**Ask specifically: did step 03 just write a rule that could have been a guard test instead?**

### 2. If the fix is a guard test: the bar it must clear

**A guard is only worth its line count if it would actually FAIL on the mistake it guards.** So:

- **It must be STRUCTURAL, not textual.** Match an import or a call shape, **not a substring.** A
  bare substring match **hits the prose in its own docstring** and false-positives on comments.
  Walk the syntax tree, inspect the registered routes, introspect the module graph.
- **It must be MUTATION-VERIFIED.** Before you commit it: **break the code on purpose, watch the
  guard go RED, then restore.** **A guard that has never been seen to fail is a guard you have no
  evidence works. State the mutation you ran.**
- **It must NAME what it protects.** The test name is the documentation: `test_no_orphan_route`,
  **not `test_misc_guard_3`.**

⚠ Two ways a guard silently excuses the bug it was written for: **the scan unit is coarser than the
rule's unit**, so a whole-file check is satisfied by one correct sibling function. Split on
function boundaries; and **the accept-pattern matches a NAME, not a CALL**, so it also matches the
line that defines the thing. Require a call shape. **Run every guard against known-good code
before trusting it, not only against the mutation.** See `rules/testing.md`.

### 3. If the fix is a script: where it goes

- **Spec and story-pipeline mechanics** → a new subcommand in the spec helper, **mirroring the
  existing shape**: a command function, a registration, a help line, and a machine-readable output
  option.
- **Infrastructure probes** → the project's script directory, so they run with the project's own
  environment. **Not a system temp directory.**
- **Anything the skills call** → **make sure the calling step file is updated to actually call it.
  A script no step invokes is DEAD ON ARRIVAL.**

> ⚠ **A heuristic over freeform text must fail LOUD.** If your script parses prose, **it must print
> its denominator**, how many files it scanned, how many had the section, **so a thin result reads
> as "they logged little" and never as "there is nothing here". Silent under-collection is the
> classic bug in this family of scripts.** And remember: **a denominator cannot see what the matcher
> never matched.** Mutation-verify the matcher too.

### 4. Apply it, verify it, and record it

- Make the change. **Run the project's gates and the affected tests.**
- **If you wrote a guard: SHOW the mutation-verified RED, then restore green.**
- Add one line to the story's agent record under a **pipeline improvement** heading, **so the next
  lessons run can see it:**

  > **Pipeline improvement (code-review step 06):** {what was manual} → {what now does it}. {Guard
  > name plus the mutation that proves it, if applicable.}

### 5. If nothing qualifies

**Say so plainly and move on:**

> **Pipeline improvement: none this run.** Steps 01 to 05 produced no repeated manual work that a
> script or guard could absorb. {One sentence on what you considered and why it did not clear the
> bar.}

**This is a legitimate and common outcome. Do NOT manufacture an improvement to fill the step. The
failure mode of this step is busywork, and busywork is the opposite of compounding.**

Then read fully and follow `steps/step-07-commit-next.md`.

## Success / failure

✅ **Success:** the run was scanned for mechanical work done by hand. **At most ONE** improvement
made, and it is real: a script a step now calls, or a **structural, mutation-verified** guard, or
an honest "nothing this run" with a stated reason. The change passes the project's gates. **A
pipeline-improvement line is in the agent record.**

❌ **Failure:** **manufacturing an improvement to look productive.** Writing a prose rule when a
guard was possible. **Shipping a guard that was never seen to go RED.** A textual guard that will
false-positive on its own comments. **Adding a script no step calls.** Turning this step into a
refactor.

**Master rule:** The other five steps make the code compound. This one makes the PIPELINE compound
,  convert judgment you had to repeat into a law that runs itself, once per story at most, or
honestly declare there was none.
