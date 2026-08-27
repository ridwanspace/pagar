# Step 01: Prove the mechanism

**You may NOT write a fix in this step.** The output is **a PROVEN root cause, or an escalation.**

**Everything downstream is cheap. Being wrong HERE is what makes a hotfix worse than no fix.**

## Sequence

### 1. Scope check (30 seconds)

**Restate the symptom in ONE sentence: what the user did, what happened, what should have
happened.**

- **If you cannot name a specific surface**: a route, a field, a component, a function, **this is
  not a hotfix. Say so and recommend `/triage` or `/rca`.**
- **Name the part of the system the fix lands in.** ⚠ **A fix spanning more than one is a SOFT
  ESCALATION TRIGGER.**

### 2. Is someone already on this surface?

Run the team-overlap check, **querying by DOMAIN NOUN.**

⚠ **This has cost a wasted run before: a bug investigated from scratch turned out to be fixed on a
teammate's UNMERGED branch.** The remote is the team's only board, **teammates push
work-in-progress branches when they START.**

**Overlap is not a stop sign**, but if it fires, **look at their branch before writing anything.**

### 3. Reproduce, then prove: never one without the other

⚠ **REPRODUCING IS NOT PROVING.** A reproduction tells you **the symptom is real.** **PROVING means
demonstrating THE MECHANISM: the specific line, comparison, or shape that produces it.**

**The cheapest proof is usually RUNNING THE REAL FUNCTIONS ON THE TWO REAL SHAPES**, rather than
reading the code.

⚠ **PREFER RUNNING OVER READING.** **A comparison that LOOKS symmetric in source can be fed two
different types by two call sites, and ONLY RUNNING IT SHOWS THAT.**

#### If a report came with a diagnosis, VERIFY it: do not adopt it

**An external report, from QA, a stakeholder, a teammate, or a triage fix brief, is A SET OF
HYPOTHESES.** **Verify the claim before building on it, and VERIFY THE REMEDY SEPARATELY FROM THE
DIAGNOSIS. THEY FAIL INDEPENDENTLY.**

> 🚨 **A REPORT CAN BE RIGHT ABOUT THE FIELD AND WRONG ABOUT THE FIX, and adopting its
> recommendation wholesale SHIPS A SECOND DEFECT.**
>
> **On a previous project, a report correctly named the divergent field, then recommended a fix
> keyed on a HARDCODED LIST OF NAMES, which left the bug LIVE for the unnamed sibling AND OPENED
> THE GATE IT PROTECTED. The mechanism was right; the remedy was wrong; adopting it would have been
> A REGRESSION WITH A GREEN TEST.**

**So: reproduce their case, then ask "WHAT IS THE MOST GENERAL STATEMENT OF THIS MECHANISM?" If the
report names N specific instances, CHECK WHETHER INSTANCE N+1 EXISTS.**

#### Prove it is not already fixed

⚠ **If the symptom does not reproduce on the current default branch, STOP. You are about to fix
something twice.**

⚠ **The reporter tested a DEPLOYED build.** **A symptom seen on a downstream environment may
already be fixed on the default branch. That is `/promotion-audit` territory, not a hotfix.**

### 4. State the root cause: three clauses

> **Symptom:** …
> **Mechanism:** …
> **Why it was invisible:** …

**The third clause matters: it usually NAMES THE TEST THAT SHOULD EXIST, which is what step 02
writes.**

### 5. Escalation check, before you continue

Re-read the hard and soft triggers in `SKILL.md`. **If one fires, stop and hand back. That is a
successful run, not a failed one.**

## → Next

Read fully and follow `steps/step-02-fix.md`.
