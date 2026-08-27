# Step E-2: Deep review & change plan

## Step goal

Review the affected parts of the PRD thoroughly, then produce a concrete, section-by-section
**change plan** and get the user's approval, **before any edit is made**.

## Mandatory rules (read first)

- 🛑 NEVER modify the PRD in this step. Planning only.
- 📖 Read this entire step file before acting.
- 🎯 Carry the persistent facts from `SKILL.md` and the standards from `data/prd-purpose.md`.
- 💬 You bring analysis and a plan. **The user holds approval authority.** Do not proceed to
  editing without explicit approval.

## Context

You have: the full PRD, its extracted decision table and sources of truth, the user's edit goals
from step E-1, and any invariant flags raised there. **Focus: analyze and plan. No edits.**

## Sequence

### 1. Deep review of the affected scope

Review the sections the edit touches **and their dependencies**, using the traceability chain in
`data/prd-purpose.md`:

- A change to a **locked decision** → check roles and authorization, features, the data model
  sketch, the non-functional requirements, and **any section that cites that decision number**.
- A new or changed **feature** → check flow references, the data model, the module map, and that
  the code stays **unique and in exactly one entry**.
- A **flow change** → check the feature codes it exercises still exist, and that **no feature is
  orphaned**.
- A **rule or formula change** grounded in a source of truth → re-check the source: **does it
  still say what the PRD will now say?**
- Any **structural change** → check section numbering and **every cross-reference**, including
  anchor links and any table of contents, that points at a section you will rename or renumber.

**Optional: delegate a broad cross-reference sweep.** If the edit is large, a read-only search
agent can sweep the PRD and **report locations**, not edit. For small, targeted edits, search
directly. Do not over-orchestrate.

### 2. Verify against the sources of truth

When the edit adds or changes domain or stack content:

- **Domain:** confirm the proposed content matches the declared sources. **Quote, do not
  paraphrase into something new.** If the user is introducing something genuinely new, note
  whether it is grounded there or is **a new decision**, which belongs in the decision table as
  a fresh numbered row.
- **Platform:** confirm stack and infrastructure content against the project memory file and the
  locked stack decisions.
- **If you find a conflict, surface it in the plan with a recommendation. Do not silently pick a
  side.**

### 3. Build the change plan

Organize **by section, in the order you will apply changes**. For each affected section:

- **Section:** `§N. Title`
- **Current state:** one line on what is there now.
- **Change:** the specific edit, add, update, remove, reword, restructure, **described
  precisely enough to review. Quote the exact new text for anything non-trivial.**
- **Why:** ties back to the user's goal.
- **Ripple:** other sections, anchors, ids, or table-of-contents entries this forces you to also
  update.
- **Risk flag:** locked-decision or source-of-truth impact, or "none".

Then summarize: counts of additions, updates, removals, and restructures. Cross-reference
updates required. **Invariant and decision impact, as an explicit list or "none".** Estimated
effort: quick, moderate, or substantial.

### 4. Present the plan and ask for approval

> **Change Plan, `{{SPEC_DIR}}/plan_artifacts/prd.md`**
>
> **Your goal:** {restate}
>
> **Proposed changes (in apply order):**
> {section-by-section breakdown, with the exact new wording for non-trivial edits}
>
> **Cross-references I'll keep in sync:** {table of contents / anchors / ids, or "none"}
>
> **Invariant & locked-decision impact:** {list, or "none"}
>
> **Effort:** {Quick / Moderate / Substantial}
>
> **Before I edit:**
>
> 1. Does this match what you want?
> 2. Anything to add, drop, or reprioritize?
> 3. For any flagged invariant change. Confirm you want it?

**Wait for the user.**

### 5. Handle feedback

- Wants changes: revise the plan and re-present. **Loop until they approve.**
- Approves: note "Change plan approved" and continue.

### 6. Route to edit

Display a one-line confirmation of the approved plan, then read fully and follow
`step-e-03-edit.md`.

## Success / failure

✅ **Success:** affected sections **and their dependencies** reviewed. Source-of-truth conflicts
surfaced. A precise, ordered, section-by-section plan presented **with exact wording for
non-trivial edits**. Cross-reference and invariant impacts called out. **User explicitly
approved.**

❌ **Failure:** editing in this step. A vague plan with no concrete wording. Missing dependency or
anchor analysis. Proceeding without approval. Not verifying domain or stack content against the
declared sources.

**Master rule:** Plan precisely, then get a yes. The approved plan is the contract for step E-3,
nothing gets edited that was not approved.
