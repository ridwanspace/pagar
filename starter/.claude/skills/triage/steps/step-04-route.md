# Step 04: Route: assign the final disposition

## Step goal

Turn each issue's verdict into one of the six dispositions, write the triage report, and present
the routing table for the user's approval. **No code is touched until step 05.**

## Mandatory rules

- 🛑 **Still read-only.** The report file is the only thing you write.
- ⚖️ **Apply the certainty test LITERALLY. It exists to override your instinct about effort, and it
  only works if you do not negotiate with it.**
- 🚦 **Default to NEEDS-RCA when torn.** **The costs are asymmetric: a wrongly-escalated issue
  wastes an investigation; a wrongly-inlined issue ships a fix for a cause you GUESSED, into a
  shared repository, past the review the pipeline exists to provide.**

## The certainty test

An issue is **STRAIGHTFORWARD** only when **ALL FOUR** hold:

1. **The cause is PROVEN.** You can name the file and line, or quote the contract clause that
   produces the behaviour. **Not "it is probably the mapper".**
2. **Ownership is settled and lives in ONE place**, proven by file and line. **A fix that needs a
   change in one place AND an adopting change in another, or whose cross-boundary behaviour is only
   suspected, means NEEDS-RCA.**
3. **The fix is CONTAINED.** One module, one component, or one helper, plus its test.
   - ⚠ **Regardless of line count, these are NEVER contained:** the shared client instance and its
     interceptors, the global state provider, the routing guards, the feature-flag provider, a
     widely-imported shared component, the authorization module, the background-job routing, and the
     composition root.
   - ⚠ **A model change, or anything that needs a migration, is a SCHEMA CHANGE → NEEDS-RCA or the
     full pipeline. Never inline.**
4. **No requirement question is open.** You are **correcting an implementation against a STATED
   expectation**, not deciding what the behaviour should be. **A PROBABLY-REAL issue with nothing
   specifying the expected behaviour is NEVER STRAIGHTFORWARD.**

**Failing gate 4 ALONE**: 1, 2, and 3 all hold, and the only thing missing is a stated rule →
**NEEDS-DECISION.** You know the file, you know the shape of the fix, **you are just not authorized
to invent the requirement.**

**Failing gate 1, 2, or 3** → **NEEDS-RCA.** The cause is unproven, the ownership crosses a
boundary, or the blast radius is wide. **That needs investigation, not a decision.**

⚠ **Do not collapse these two.** **Routing a DECISION-shaped issue to a full investigation produces
an investigation whose conclusion is "someone should decide the rule", a question you could
already state at triage. Routing an INVESTIGATION-shaped issue to NEEDS-DECISION hands your lead a
recommendation built on a cause you guessed.**

**Explicitly NOT part of the test:** how many lines the fix is, how confident you feel, how urgent
the reporter says it is, or whether it "looks like a typo".

## Sequence

### 1. Assign dispositions

| From | → Disposition |
|---|---|
| killed in step 02 | **ALREADY-SOLVED** |
| step 03 not-a-bug | **NOT-A-BUG** |
| step 03 needs-info | **NEEDS-INFO** |
| step 03 real or probably-real, **passing all four** certainty checks | **STRAIGHTFORWARD** |
| step 03 probably-real, passing 1 to 3, **failing only 4** | **NEEDS-DECISION** |
| everything else real | **NEEDS-RCA** |

### 2. For each STRAIGHTFORWARD issue, write the fix brief

This is what step 05 executes, **and what makes the fix reviewable BEFORE it exists:**

```
- **Surface:** <which>
- **Root cause (proven):** <file:line or contract quote>
- **Fix:** <the specific change, in one or two sentences>
- **Blast radius:** <files touched; what else imports or consumes them>
- **Test:** <the existing test to extend, or the new case to add>
- **Verification:** <what proves it works, a visual pass, a real request, a test, or a combination>
```

⚠ **If writing this brief reveals the cause was actually INFERRED, the blast radius is wider than
you thought, or the fix turns out to need another surface too. DOWNGRADE IT TO NEEDS-RCA NOW. That
is the brief doing its job.**

### 3. For each NEEDS-DECISION issue, write the decision brief

**The whole point of this disposition is that the issue leaves triage with a RECOMMENDATION, not an
open question.** **A lead handed "what should the rule be?" has to redo the research you just did.
A lead handed "I propose X, here is why, say no if you disagree" answers in one line.**

**Make the call yourself.** **The blocker is the AUTHORITY to set the rule, not the ABILITY to
reason about it.** Ground the recommendation in this codebase:

- **Find the precedents.** How is this kind of thing already done here? **Two or three comparable
  surfaces, with file and line.** ⚠ **Precedents that DISAGREE with each other are the most valuable
  finding**, because they mean the codebase has **no house rule**, and the split usually tracks
  **PURPOSE**: an identifier the system constrains versus a display label nobody parses. **Name the
  axis. That is what makes your recommendation an ARGUMENT rather than a preference.**
- **Check the contract.** Does the schema constrain it? **A field with NO validator means the server
  accepts anything, so a client-only rule is a REAL LIMITATION of the proposal. Say that out loud**,
  and say whether the right fix is a server-side validator, which is still one surface, just the
  other one.
- **Check the reporter's own expectation.** If they supplied an allowed list or an expected format,
  **does it survive contact with the actual data?** **A reporter's rule can contradict the field's
  own documented example, or values already stored. Following it literally would break something
  that works today. Where you deviate from what the reporter asked for, SAY SO EXPLICITLY. That is
  the part they will re-test.**

```
- **The open question:** <one sentence. Exactly what has to be decided>
- **Why it's open:** <PRD silent / no validator / the reporter's requirement does not resolve here, with citations>
- **Precedents:** <2-3 comparable surfaces, file:line, and the rule each uses>
- **Recommendation:** <the specific rule you would ship, and where it lives>
- **Why:** <2-4 sentences grounded in the precedents and the field's purpose>
- **Runner-up:** <the strongest alternative, and why not>
- **Where it deviates from the reporter's ask:** <or "nowhere">
- **Decider:** <who>
- **Cost if approved:** <the fix brief, in one line. This becomes a real fix brief on re-entry>
```

⚠ **A recommendation you cannot defend from a file and line is NOT READY.** If the precedents do not
exist or do not agree and you cannot name the axis, **you are guessing: say so in the brief and ask
an open question instead. That is a worse outcome, not a forbidden one.**

⚠ **NEEDS-DECISION is not a way to launder a weak cause.** Gates 1 to 3 must genuinely hold. **If
you are unsure WHY the behaviour happens, no decision about the rule unblocks anything: that is
NEEDS-RCA.**

### 4. For NEEDS-RCA issues, write the handoff block

**The investigation's intake work is already done. Do not make it redo it.**

```
### Investigation handoff: <batch slug>
- **Environment:** <which, version/date>
- **Checkout position:** <synced | N behind (sync declined)>
- **Issues:** <the normalized issue blocks, renumbered contiguously>
- **Already ruled out:** <what step 02 killed and why, so the investigation does not re-check>
- **Findings so far:** <per issue: verdict, citation, cause certainty>
- **Suspected ownership:** <per issue>
- **Prior report to extend:** <id, if step 02 found one covering this surface>
```

### 5. Write the report

Create `{{SPEC_DIR}}/triage/TRIAGE-NN-<slug>.md` from `templates/triage-template.md`. **Fill every
section. Leave no placeholder.**

⚠ **NEVER stage this path.** Personal workflow, untracked.

### 6. Present the routing table and stop

A table with: the issue number, its title, its disposition, its surface, why, and what happens
next. Summarize in one line: *"N issues → X closed, Y to fix here, Z awaiting a decision, W to
investigation."*

Then ask for the go-ahead, **naming what will actually change on disk:**

> *"Shall I apply the fixes for #3 and #4? The investigation-bound items stay untouched, I'll draft
> the ask for #5, and the replies for the closed ones."*

**Wait for approval before any edit.** The user may want an investigation-bound item fixed anyway,
or a straightforward one deferred. **Both are their call, and both are fine as long as the routing
reasoning is on the record.**

## Step completion

Carry forward: the report path, the routing table, the fix briefs, the decision briefs, and the
handoff block.

Then load `steps/step-05-execute.md`.
