# Step 04: Land it

## 1. Documentation sweep (fast, automated, about 20 seconds)

> ⚠ **A BEHAVIOUR FIX SILENTLY INVALIDATES THE DOCUMENT THAT DESCRIBED THE OLD BEHAVIOUR**, and the
> committed documentation is what teammates and integrators read.

Search the committed documentation and the contract for what you changed. **Nothing matched → done,
move on.**

If something matched:

- 🚨 **DIFF THE DOCUMENT'S FIELD NAMES AGAINST THE SCHEMA. DO NOT READ THE PROSE.** ⚠ **Reading the
  prose CANNOT FIND THIS CLASS OF ERROR: a document naming a field the response lacks READS AS
  COMPLETELY PLAUSIBLE, because the sentence around it is true.**
- ⚠ **Documents can also be wrong BY OMISSION: if your fix gave an existing mechanism a NEW EFFECT,
  an enumeration of its effects is now INCOMPLETE WITH EVERY WORD STILL TRUE.**
- **Schema description strings are wire contract too.** Regenerate the committed contract **so the
  committed file does not lie.**

## 2. The ledger row: the only spec artifact a hotfix writes

Append one row to `{{SPEC_DIR}}/hotfix-ledger.md`:

| date | surface | symptom | mechanism | fix | commit |
|---|---|---|---|---|---|

- **Leave the commit cell empty and fill it after the commit in section 4.** You cannot know it
  yet.
- **The MECHANISM column is the one worth writing carefully. IT IS WHAT MAKES A REPEAT VISIBLE
  LATER.**

The ledger's own header should say why it exists:

> *One row per hotfix. Deliberately thin, the commit message carries the full reasoning.* **Mine
> this when a surface keeps coming back: THREE ROWS ON ONE FILE IS A DESIGN PROBLEM, NOT THREE BUGS,
> and that is the signal this table exists to make visible.**

## 3. Private-spec-id sweep

**The authoritative check is the whole-file guard**, which walks every tracked file and **catches
violations in files this commit did not touch, WHICH A DIFF SWEEP STRUCTURALLY CANNOT.**

⚠ **If you use a diff sweep as a convenience, compare against the committed state, NOT the unstaged
diff.** A bare unstaged diff **shows nothing once you have staged, so it silently reports CLEAN on
a real violation. This grep is a convenience, not the gate.**

## 4. Commit

**Stage only the code and the tests.**

Follow `{{COMMIT_CONVENTION}}`. **The title states THE BEHAVIOUR RESTORED, not the code moved.**

**The body is the contract.** ⚠ **For a hotfix it REPLACES THE STORY FILE, so write it for a
teammate who never saw the bug report:**

- **What the user could not do**, concretely.
- **The mechanism**, in enough detail to **recognize the class again.**
- ⚠ **Why the narrower or obvious fix was rejected. YOU HAVE MUTATION EVIDENCE, USE IT.**
- **What still correctly triggers the guarded behaviour.**
- **Any caveat that survives**: unbackfilled data, a first-run cost, **a worker that must be
  restarted on deploy.**

Then fill the ledger's commit cell.

## 5. Report honestly: the five-item contract

1. **What was wrong**: the mechanism, one short paragraph.
2. **Why you did not take the recommended or obvious fix, if you did not, WITH THE MUTATION
   EVIDENCE.**
3. **Verification**: both wire directions, the mutation results, the scoped tests, the gates.
4. **What you did NOT verify.** **The honest limit, and BE PRECISE ABOUT WHICH KIND IT IS:**
   - ⚠ **Not driving the interface for a server-side fix is a CAVEAT.** Say so and suggest a visual
     pass. **A reporter's own run is a stronger tier than probes.**
   - 🚨 **Not driving the wire at all, or a test you could not get RED, is a FAILED FLOOR, NOT a
     caveat. LEAD WITH IT, DO NOT CALL THE FIX VERIFIED, and treat the run as an escalation.**
5. **Side effects on their machine**: local rows, migrations applied, services restarted, probe
   data.

⚠ **DO NOT CLAIM "VERIFIED END TO END" FOR ANYTHING YOU DID NOT ACTUALLY RUN.**

## 6. Offer the next move

**Offer, do not assume.**

> ⚠ **If the run surfaced something that is NOT a hotfix, a design smell, a second bug you had to
> route around, a document that needs rewriting, a migration the environment may not have. NAME IT
> NOW as a candidate for `/rca`, `/promotion-audit`, or the full pipeline. THAT HAND-OFF IS HOW THE
> FAST PATH STAYS HONEST INSTEAD OF ACCUMULATING DEBT SILENTLY.**
