# Step 05: Execute: apply, hand off, reply

## Step goal

Act on the approved routing: **apply the inline fixes, hand the rest to the investigation, and give
the user a ready-to-send reply for everything closed.** This is the only step that writes code.

## Mandatory rules

- ✅ **Only act on what the user approved in step 04.** An unapproved fix is not yours to apply.
- 🛑 **NEEDS-RCA issues stay UNTOUCHED.** Not a "quick look while I am in there". **A partial fix
  corrupts the tree the investigation reads, and its evidence is the whole point.**
- 🛑 **NEEDS-DECISION issues stay unfixed until the decider answers.** **Implementing your own
  recommendation before it is approved is deciding the rule yourself with extra steps.** The
  exception is explicit: the user tells you to proceed anyway, **and then you RECORD in the report
  that it shipped UNAPPROVED**, so the next round knows the rule is provisional.
- 🛑 **One surface per fix.** The brief named a surface. **If the fix starts needing another one,
  STOP: it is NEEDS-RCA after all.**
- 🚫 **Never stage personal-workflow paths.**

## Sequence

### 1. Check for collisions before editing

If step 02 did not already cover the exact files you are about to touch, run the team-overlap check
over those paths. **If it fires, tell the user who else is in these files and confirm before
proceeding. The remote is the team's only board.**

### 2. Apply each approved fix

**One issue at a time, following its fix brief:**

- **Match the surrounding code.** **This is a shared repository: its patterns win over your
  preferences.** Follow the project's conventions for the surface you are in.
- **Fix the CAUSE named in the brief, not the symptom.** ⚠ **If the code does not match what the
  brief claimed. STOP, do not improvise. The brief was the EVIDENCE for routing this inline; if it
  was wrong, the issue is NEEDS-RCA after all. Say so and move it.**
- **Add or extend the test the brief named.** **A fix with no test is a fix that regresses on the
  next release.**
- **Stay in scope.** No drive-by refactors, no unrelated cleanups.

### 3. Verify

**If there are no pre-commit hooks, this is the only thing standing between you and the CI
pipeline.**

Run the scoped tests for what you touched, the build or import check, and the lint and type
checks. **Compare against the recorded baseline: if a gate flags something, confirm it is YOURS
before chasing it.**

Then **verify on the wire, in the real thing:**

- For a **user-visible** fix, drive the real flow **and look at the result**. **A green test suite
  has missed real rendering bugs before. The visual pass is what catches them.**
- For a **server-side** fix, drive the real endpoint with **the payload the client actually
  sends**, against **your own local system**, never a shared one.

**Check BOTH directions: the reported case now behaves, AND whatever the changed code guards STILL
rejects.** ⚠ **A fix that only proves the first half cannot distinguish "fixed it" from "disabled
the check".**

**Report results HONESTLY. If a gate fails or a fix did not hold, say so with the output. Do not
soften it.**

### 4. Draft the ask for NEEDS-DECISION issues

**One message per decider, not one per issue.** Shape it from the decision brief, in this order:

1. **The finding, confirmed**: you reproduced it, it is real.
2. **Why it is a decision and not a fix**: nothing specifies the rule, in one or two lines **with
   the citations.**
3. **Your recommendation with its grounding**: the precedents and the axis you found, and where
   the rule would live.
4. **Where it deviates from what the reporter asked for**, if anywhere.
5. **The unblock line**: what you are doing regardless, and the rough cost of implementing once
   they say yes.

⚠ **The ask is "approve this", NEVER "you decide". An open question hands the research back to the
busiest person in the loop.** If the brief could only produce an open question, **say that plainly
in the message AND in the report. Do not disguise a guess as a recommendation.**

⚠ If the decision genuinely belongs to **the reporter** rather than the lead, they hold the
specification, they are asserting a requirement you cannot see. Draft a second message for them
too, **but keep the asks separate.**

**Draft only. NEVER send.** Then tell the user what happens next.

### 5. Re-entry: a decision that came back

When the user returns with an answer, **do NOT re-run the whole skill. Re-enter at step 04:**

- **Approved as recommended** → the brief's cost line **becomes the fix brief.** **Re-check that
  gates 1 to 3 still hold**, since the tree may have moved, then apply it as STRAIGHTFORWARD.
- **Approved with changes** → **their rule wins, not yours.** Rewrite the fix brief around it, **and
  note the divergence in the report.** The reasoning behind your original recommendation is now on
  the record as **rejected**, which is worth knowing the next time this surface comes up.
- **Deferred** → leave the disposition, mark the report as awaiting a decision, and stop. **It stays
  visible to step 02 of the next triage on this surface, which is exactly what keeps it from being
  re-reported as new.**
- **They point at a document** → read it. **The issue was undetermined, not unspecified.** It
  usually becomes STRAIGHTFORWARD or NOT-A-BUG outright.

**Update the report's outcome section either way.**

### 6. Hand off the investigation-bound issues

Present the handoff block from step 04 and offer to run `/rca` now or leave it for a separate
session. **Note whether a prior report should be EXTENDED rather than a new one opened.**

⚠ **If you applied fixes in this step, the tree has CHANGED since step 02's position. Say so in the
handoff: the investigation needs to know its baseline includes your edits.**

### 7. Draft the replies for closed issues

For every ALREADY-SOLVED, NOT-A-BUG, and NEEDS-INFO issue, draft a reply **grouped into ONE
message**, not one per issue:

- **ALREADY-SOLVED**: what fixed it and **where it stands**: merged and live on their environment,
  merged but not yet promoted, or pending in a teammate's branch. **Say plainly whether the reporter
  should expect it fixed NOW on the environment they test, or AFTER the next promotion. That is the
  part they actually need.**
- **NOT-A-BUG**: the citation, **in plain language.** If they are arguing the requirement rather
  than the implementation, **name that explicitly: it is a product conversation, not a bug.**
- **NEEDS-INFO**: **one specific question per issue.** Ask for **what only they can give**: steps,
  ids, environment, the account used, **never for something you could look up.**

**Draft only. NEVER send. Outward messages are the user's to send.**

### 8. Close out

Update the triage report with **what actually happened**: fixes applied and their files, gate
results, what was handed off, what is awaiting a decision, and what is awaiting a reply. **The
report should stand alone weeks later, when the surface gets re-reported and step 02 searches for
it.**

Then offer the commit. **Let `/commit` do the committing.** It owns the gates, the scope guard, the
private-spec-id sweep, and the message convention.

## Step completion

State in one line: what changed on disk, what is waiting on the user, and what nothing was done
about and why.
