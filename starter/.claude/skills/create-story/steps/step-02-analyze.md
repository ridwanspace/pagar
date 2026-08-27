# Step 02: Exhaustive (but scoped) analysis

## Step goal

Gather everything the developer needs to implement this story correctly, **grounded in the real
codebase and the project's sources of truth**. Be thorough but **scoped**: read only what is
relevant to this story, never the whole PRD or all epics.

> **This is the most important step. Lazy analysis here is the number one cause of failed
> implementations and review cycles. Do not skim.**

## Mandatory rules

- 🔎 Helper plus targeted reads only. Read the PRD **by section**, documents **by topic**, code
  **by file**.
- 🧩 You are building **NEW context**: codebase reality and sources of truth, **not copying the
  epic.**
- 💾 Save questions and uncertainties for the end. Do not block. Note them for the story's open
  questions, which step 04 will resolve.

## Analysis areas (do each that applies)

### 1. Story foundation

Already loaded in step 01. Extract: the user story, the acceptance criteria, the covered
features and flows, and the epic's stated invariants and dependencies. Note where this story sits
in the epic's sequence, **what earlier stories already built, since it may only depend on
those.**

### 2. Previous-story intelligence

If there is a previous story with a dev story, read that file and extract **actionable
carry-over**:

- Files and modules it created or modified, and **the patterns it established**: naming,
  placement, migration-file style, schema shape, component composition, service-call shape, test
  layout.
- Developer notes, gotchas, decisions, and anything in its open questions or completion notes.
- **Testing approaches that worked.**

This prevents re-inventing what the previous story already built, and keeps conventions
consistent.

### 2b. Shipped-story hazards: ALWAYS. This is the compounding step.

**The immediate predecessor is only ONE story.** The developer records of **every** shipped story
are where implementation reality got written down: **the traps a green test suite did NOT
catch**, and the rules that generalize past their own story.

**That corpus grows large and nothing reads it, so the same class of bug gets re-learned at full
price.** Mine it:

```bash
{{SPEC_HELPER_COMMAND}} lessons <ref> --hazards                        # earlier stories in THIS epic
{{SPEC_HELPER_COMMAND}} lessons <ref> --hazards --all-epics --limit=20 # everything shipped before it
```

**Run BOTH.** The same-epic pass gives you the direct carry-over. The all-epics pass catches the
cross-cutting traps: **an idempotency hazard learned in epic 4 will bite an epic 5 writer just as
hard.** The output ranks hazards first and round-robins across stories, so one verbose story
cannot crowd out the rest.

**A hazard is only worth carrying if it can bite THIS story.** For each one, ask: does this story
touch that surface, the same table shape, the same guard style, the same test seam, the same
provider? If yes, fold it into the dev story:

- into **Dev guardrails** if it is an invariant to hold,
- into **Architecture and stack guidance** if it changes the design,
- into **Testing** if it is a test that would have caught it.

**Cite the source story.** If no hazard applies, **say so explicitly** in the story: "Hazard scan:
N shipped stories reviewed, none applicable because …". **A silent skip is indistinguishable from
not looking.**

> ⚠ **The lessons miner is a heuristic over freeform text, not a database.** It always prints its
> denominator. **A thin result means those stories LOGGED LITTLE, not that there is nothing to
> learn.** If the denominator looks wrong, read the dev story directly. See
> `rules/spec-pipeline.md`.

**Also read the planning story's "Inherited from" block(s), if any.** `/code-review`'s
feed-forward step writes these into the *planning* file when an earlier story it depends on was
finished. They carry **ground truth**: final table and column names, a reusable helper's real
signature, a proven pattern, a discovered constraint, **instead of the original guess.**

**Treat an "Inherited from" block as AUTHORITATIVE for those facts.** Use the real schema and
signature it names, reuse the artifact it points at, honor any constraint it flags. **Do not
re-derive or re-invent.** Fold it into this story's carry-over and architecture sections, and
**prefer it over a stale guess elsewhere in the planning body.**

### 3. Version-control intelligence

Scan recent history for patterns relevant to this story. Keep it **brief**: a few commits, not
the whole history. Extract: files recently touched in this area, conventions in use,
dependencies added, and any migration or test patterns.

### 4. PRD sections: scoped, never the whole file

For the features and flows this story covers, read just the relevant sections:

- The **feature catalog** entry: the exact behaviour.
- The matching **flow**: step-by-step behaviour and **any user-facing copy to reuse verbatim**.
- The **locked decisions**: the invariants that constrain this story.
- The **data-model section**: the tables and columns this story creates or alters, plus soft
  delete, audit, and cascade mechanics if the PRD defines them.
- The **roles and permissions** section: who may perform the action, and the **exact server-side
  rule**.
- Any other section the feature cites.

### 5. Domain source of truth

If the PRD names one for this feature, read the relevant part to capture **formulas, business
rules, and user-facing copy VERBATIM. Cite them. Do NOT paraphrase a formula. Quote it.** Use
targeted reads, since such sources are often large. If the PRD names no domain source, the PRD
itself is the source, cited by section.

### 6. Stack and integration documentation, by topic

Read only what is relevant to this story: the project memory file's conventions for this area,
and the path-scoped rules that match the surfaces this story touches. **Capture the exact,
current patterns, environment variable names, mandatory flags, gotchas, so the developer does
not guess.**

### 7. Files to be modified: NON-NEGOTIABLE if any exist

Identify **every** existing source file this story will touch or extend, not create new. For
each, **read it COMPLETELY** and note in the dev story:

- **Current state:** what it does today. Data shapes, existing behaviours, call sites.
- **What this story changes:** the specific functions or sections being modified.
- **What must be preserved:** behaviours and interactions the story must not break.

> **A correct implementation must leave the system working end to end, not just satisfy the
> acceptance criteria. If a behaviour is required for the feature to work in the existing system,
> it is a requirement whether or not the criteria name it.**

If the codebase has no implementation yet for this area, **say so explicitly** and define the NEW
files and their correct locations per the project structure. **Say which half owns each file.**

**Then check nobody else is already building it.** The remote is the team's only task board.
Teammates push work-in-progress branches when they **start**, so **an unmerged branch is the only
warning you get before two people do the same job.** Feed the file list you just derived into the
overlap check.

**Record any overlap in the story's open questions with the branch, the author, and the
overlapping files, and surface it to the user BEFORE writing the story**, since "someone is
already on this" changes whether the story should exist at all. **This is not a blocker to decide
alone.**

⚠ **A migration collision is the expensive kind.** Two branches each adding a migration touching
the same table produce two files that never textually conflict, so version control merges them
without a murmur, **and then they collide at apply time.** Flag any branch adding a migration on
your surface.

### 8. External specifics: the web, only when genuinely needed

The stack is **locked** by the existing codebase, the project memory file, and the PRD. Prefer
those. Use the web **only** for specifics those do not cover and that are genuinely external and
volatile: a third-party file format this story parses, or the current contract of an external
service this story calls.

**If web research is not needed, skip it.** Do not pad the story with generic library
documentation the developer does not need.

## Output of this step

A structured pile of findings, held in your working context, ready to write into the template:
requirements and criteria · developer guardrails from the applicable locked decisions ·
architecture and stack patterns **with cited sources** · files-to-modify analysis ·
previous-story carry-over · **the hazard-scan result** · domain formulas and copy verbatim · any
external specifics · open questions.

Then read fully and follow `steps/step-03-write.md`.

## Success / failure

✅ **Success:** scoped but exhaustive. Relevant PRD sections, stack documentation, and domain
sources read **and cited**. Files-to-modify read **completely**. Previous-story and history
patterns captured. **The shipped-story hazard scan run in BOTH passes, with every applicable
hazard folded in and its source story cited.** Applicable invariants identified. Sources cited
throughout.

❌ **Failure:** loading the whole PRD or all epics. **Skipping the files-to-modify read.**
**Skipping the hazard scan, or running it and silently dropping the result**: if none apply, say
so and why. Paraphrasing formulas instead of quoting. Padding with irrelevant research. Uncited
claims.

**Master rule:** Ground every instruction the developer will follow in a real source, a PRD
section, a document, a domain source, or an existing file, and cite it.
