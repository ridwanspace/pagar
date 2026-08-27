# Step 03: Verify: the floor. Never skip either half.

**Two checks, both mandatory, in this order. THEY ARE THE REASON A HOTFIX IS ALLOWED TO SKIP
EVERYTHING ELSE.**

## A. Mutation-verify the test

> **A TEST YOU HAVE NEVER SEEN FAIL IS NOT EVIDENCE.**

**Break the fix on purpose, confirm the new test goes RED, restore.**

- **Apply the mutation with an EDIT and invert it with an EDIT.** That is the safest form, and it
  scales to a fix spanning several files.
- ⚠ **NEVER revert a mutation by discarding the file from version control. That wipes the session's
  uncommitted work in that file, not just the mutation.**
- ⚠ If you keep a file copy instead, **give it a PER-FILE name in the scratch directory, never one
  fixed name: mutating a second file OVERWRITES THE FIRST FILE'S BACKUP, and the restore then
  writes the WRONG CONTENT over real work.**

### Pick the mutation that RECREATES THE BUG

**This is the part that goes wrong.** ⚠ **A mutation that merely BREAKS the function proves
nothing. It makes tests fail for a COINCIDENTAL reason.**

- **A value-computation fix** → **mutate the CALL SITE back to the old wiring, not the callee.**
  **Making the helper return a constant breaks everything for the wrong reason.**
- **A condition fix** → **restore the ORIGINAL CONDITION EXACTLY.**
- **A render-branch or prop fix** → **restore the original value, NOT a blanket "render nothing".**
- ⚠ **CHECK WHICH TESTS GO RED, NOT HOW MANY. A mutation that reds tests OTHER than the one it
  targets has proven NOTHING about that one.**

### Also mutation-test the REJECTED alternative

**If you rejected a narrower fix, especially one an external report recommended, APPLY IT AS A
MUTATION AND SHOW IT FAILS.**

**This converts "I judged it insufficient" into EVIDENCE.** A single line reading "the recommended
fix leaves test X and test Y red" is **routinely THE STRONGEST ARTIFACT OF THE WHOLE RUN**, because
it proves **both** that the alternative left the bug live **and** whether it opened the gate.

### If a mutation stays GREEN, the TEST is the bug

⚠ **DO NOT SHRUG.** The usual cause is **a NORMALIZATION STEP between your input and your assertion
that ERASES the difference you meant to detect**: a loader that coerces, a timestamp that
normalizes, a helper collapsing a doubled prefix, a query that matches a sibling element.

**Find what normalizes your inputs, and construct the case that BYPASSES it.**

> 🚨 **A TEST YOU CANNOT GET RED IS NOT A GUARD, AND THE RUN DOES NOT PASS THE FLOOR.**
>
> If you genuinely cannot construct the case, **STOP AND SAY SO. "I tried, it stayed green, moving
> on" IS NOT AN OUTCOME.** Report it as an escalation. **Shipping with a test that CANNOT FAIL is
> worse than shipping with none, because the next engineer will TRUST it.**

## B. Verify on the wire

> **GREEN TESTS ARE WHAT THE BUG REPORT ALREADY GOT PAST.**

**Drive the real surface against the running system.**

**The two most time-costly facts:**

- ⚠ **YOUR FIX IS NOT LIVE UNTIL YOU RESTART THE PROCESS**, unless auto-reload is on, **and you
  should not assume it is. A fix that "does not work" is THIS, most of the time.** A background
  worker caches its task code too: **restart it if the fix is in a job.**
- ⚠ **Point probes at your OWN local system, never at a deployed host.** Shared environments are
  other people's data.

⚠ **If you cannot bring the system up, YOU HAVE NOT COMPLETED THE FLOOR. Do NOT substitute green
scoped tests, and do NOT call the fix verified.** Say so explicitly in the report and **treat the
run as an escalation.**

### Send the payload the CLIENT actually sends

> 🚨 **A HAND-WRITTEN PROBE CAN MASK THE BUG ENTIRELY.**

**Reproduce the CLIENT'S payload shape, not a convenient one.** ⚠ **An extra field the client never
sends, or a missing one it always sends, CHANGES WHICH CODE PATH RUNS.**

**Two archetypes:**

- **The idempotency header.** ⚠ **A probe that REUSES one may get a cached response and LOOK
  "fixed".**
- **The retry.** ⚠ **A handler that is wrong only on the SECOND identical request is INVISIBLE to a
  single call. SEND IT TWICE.**

**The fastest way to get the real shape is to CAPTURE IT FROM THE RUNNING CLIENT and replay it.**

**For a user-facing fix, "the wire" is the SCREEN.** Drive the flow through the real interface
**and look at the result.** ⚠ **A green test suite has missed real rendering bugs before. The
visual pass is what catches them.**

### Verify BOTH directions

| Direction | What it proves |
|---|---|
| The reported failing case → **now succeeds** | the fix works |
| The behaviour the guard protects → **STILL fails / still rejects** | **you did not just disable the check** |

⚠ **A hotfix that only proves the FIRST half CANNOT DISTINGUISH "fixed it" from "disabled the
check".**

### Reproduce the product's gates, do not route around them

If the flow requires a login, a role, a prior upload, or a completed job, **go through them the way
the interface does.** ⚠ **RELAXING A GATE FOR TESTABILITY, an auth-disabled flag, a hand-minted
token, a commented-out check. INVALIDATES THE TEST.**

### Clean up

Delete probe rows, leave the system as you found it, and **note any local state change so you can
report it.**

## C. Scoped gates

Run the scoped tests, the build or import check, the lint, and the type check.

- **If the project has no linter, DO NOT ADD ONE, and do not run one and "fix" unrelated lines.**
- ⚠ **Did you break an EXISTING test? READ IT BEFORE "FIXING" IT.** **If it asserts an
  IMPLEMENTATION DETAIL your fix legitimately changed, RETARGET IT TO THE INVARIANT it was
  protecting. Do not delete it, and do not weaken it to green. If it asserts a REAL BEHAVIOUR, YOUR
  FIX IS WRONG.**
- **A failure you did not cause? ATTRIBUTE IT** by stashing only your own paths and re-running,
  **before blaming yourself.**

## → Next

Read fully and follow `steps/step-04-land.md`.
