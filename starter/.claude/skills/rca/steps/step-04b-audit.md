# Step 04b: Audit the fix site: find the siblings of the reported defect

## Step goal

For every finding that will become work, **audit the function or module the fix lands in**, and
report **EVERY defect of the same class living there, not just the one the reporter happened to
notice.**

## Why this step exists

**A reporter sees a SYMPTOM, from outside, through one path they happened to walk.**

The root cause found in step 04 usually **lives in a SHAPE**: a trusted client field, a missing
ownership filter, an additive overlay, a truthy default, **and a shape defect almost never has
exactly one victim.**

**Whoever fixes the reported case will be inside that code with full context EXACTLY ONCE. Every
sibling they do not see now becomes its own bug report, its own investigation, its own change
request, weeks later, at full price.**

### The lesson this step encodes

**On a previous project, ONE reported bug in a header-resolution helper, when audited, turned out
to be FIVE defects sharing one root cause: two already fixed on a teammate's branch, THREE NEVER
REPORTED BY ANYONE, and those three were precisely the cases the obvious fix STRUCTURALLY COULD
NOT REACH.**

**Without the audit, the story would have shipped a fix that closed 2 of 5 and LOOKED COMPLETE.**

## When this step applies

Run it for every finding classed as a **confirmed bug** or a **confirmed gap** that **MODIFIES
EXISTING CODE.**

**Skip it, and SAY you skipped it, with the reason, when** the finding builds something new, is
already-exists or baseline-confirmed or works-as-designed, or is **blocked on a decision**, because
⚠ **auditing the wrong shape is wasted work.**

## Mandatory rules

- 🎯 **Audit the FIX SITE, not the codebase.** The unit is **the function the fix edits, plus the
  schema or type that feeds it, plus the callers that depend on it. Usually ONE file.** A general
  review of the module is `/code-review`, later.
- 🛑 **Still no fixes.**
- 📌 **Every sibling needs the SAME EVIDENCE BAR as the reported one**: a file, a line, a quoted
  mechanism, a class. **An unproven suspicion is a hypothesis with a named next check.**
- 🔬 **PREFER EMPIRICAL OVER TEXTUAL.** If a defect depends on a default, a truthiness, a coercion,
  or how unknown fields are handled, **RUN IT. Reading is how you miss that a fallback expression
  never actually yields the fallback.**
- 🚫 **NEVER WIDEN THE STORY SILENTLY.** Siblings go in the report **with a severity and a
  fix-or-defer recommendation. Whether they enter the story is the USER'S call in step 05.**

## Sequence

### 1. Name the shape of the root cause

**This table is the engine of the step. The GENERALIZATION is the product.**

| Root cause found | The shape | So ask of every other path… |
|---|---|---|
| An overlay applied additively over pre-populated state | *additive-only* | which cases need **removal or renaming**, not overwrite? |
| A guard excludes a case | *guarded path* | **what else does that guard exclude that it should not?** |
| A client-supplied value trusted | *trusted input* | **what other fields on this payload are trusted the same way?** |
| A default defeats a fallback | *truthy default* | which other fallbacks does a non-optional default kill? |
| A missing ownership or tenant filter | *unscoped query* | **which other queries on this model skip ownership scoping?** |
| Missing invalidation on write | *stale derived state* | what else derives from this and is not refreshed? |
| A parameter name mismatch across the wire | *contract drift* | **which other calls from this module use the same stale name?** |

### 2. Enumerate every path through the fix site: exhaustively, not narratively

Work the function's inputs **exhaustively**:

- **Every branch, INCLUDING THE IMPLICIT ONE NOBODY WROTE.**
- **Every enumerated value, INCLUDING THE ONE THAT MEANS NOTHING, NONE, OR OFF.** ⚠ **That case is
  disproportionately buggy, because it requires REMOVING state rather than setting it.**
- **Every optional field at both its absent value AND its default. ⚠ THESE DIFFER.**
- **Every state transition:** set it, change it, **unset it.**
- ⚠ **Both callers AND call shapes. The same helper reached from two different flows may be correct
  in one and broken in the other.**

### 3. Verify the suspicious ones empirically

**Defects that depend on defaults, truthiness, or coercion are INVISIBLE TO READING.**

**Paste the actual output into the report. An OBSERVED VALUE outranks a confident sentence.**

### 4. Check each sibling against work already in flight

**A sibling may be covered by a teammate's open change even when the reported one is not.** For
each sibling record: **is it broken on the default branch? Is it fixed by any open branch or
request?** Use a **content check, which is immune to how a branch was eventually merged.**

**The two-column table this produces is the HIGHEST-VALUE ARTIFACT of the step.**

### 5. ⚠ Check for defects the obvious fix would CREATE

**Do this BEFORE recommending anything.**

**A defect can be UNREACHABLE TODAY because another defect masks it, and become LIVE the moment the
reported bug is fixed.**

**Ask directly: if the reported defect is fixed naively, WHAT BREAKS THAT WORKS TODAY?**

**The archetype:** a masked placeholder value was never sent because the whole block was discarded.
**Fix the discard alone, and every previously-working record starts sending the placeholder.**

**Any such case is a MANDATORY GUARDRAIL in the story**: *"the fix must also handle X, or it
introduces a new bug"*, **not merely another row.**

### 6. Rank and recommend

**Default to FIX-NOW when the sibling shares the root cause.** **Defer when it needs a DIFFERENT
fix, a migration, a contract change, or a product decision, and say which.**

**Then state explicitly what you did NOT audit.**

## Anti-goals

- ❌ A general code review of the file.
- ❌ Scope creep into adjacent modules.
- ❌ Padding the count.

**ZERO SIBLINGS IS A PERFECTLY GOOD OUTCOME.** Write "audited N paths, no sibling defects" and move
on.

Then load `steps/step-05-report.md`.
