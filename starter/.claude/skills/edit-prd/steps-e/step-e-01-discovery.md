# Step E-1: Discovery & understanding

## Step goal

Understand exactly what the user wants to change, load the PRD, and confirm scope, **before any
review or editing**.

## Mandatory rules (read first)

- 🛑 NEVER edit the PRD in this step. Discovery only.
- 📖 Read this entire step file before acting.
- 📋 You are a **facilitator**, not a content generator. Ask, then listen.
- 🎯 Carry the persistent facts from `SKILL.md`: the key-decisions table is the invariant list,
  the declared sources of truth carry over verbatim, existing structure and numbering are
  preserved, ids are machine-parsed.

## Sequence

### 1. Load the PRD quality standards

Read `data/prd-purpose.md` in full. It guides every recommendation you make.

### 2. Resolve the PRD file

- **Default target:** `{{SPEC_DIR}}/plan_artifacts/prd.md`. Use it unless the user explicitly
  named a different file.
- Confirm it exists. If it does not:
  - Search for it, excluding dependency and vendored trees. **A hit in the team documentation
    tree is an input document, not the PRD.**
  - If nothing is found, suggest **`/create-prd`** and stop. If candidates exist, report them
    and ask which file to edit. **Do not guess.**
- Load the **complete** PRD. You need the full structure to plan edits and keep numbering, ids,
  and any table of contents in sync.

### 3. Confirm what is actually in the PRD

Extract and note for yourself:

- All top-level section headers and their numbers, so you can keep numbering and any table of
  contents consistent.
- **The key-decisions table.** List each decision number and what it locks. **These are the
  invariants you protect this session.**
- The declared domain sources of truth, their locations, and what carries over verbatim.
- Whether the document matches the persistent facts in `SKILL.md`. **If anything has drifted,
  trust the file and note the difference to the user.**

### 4. Discover the edit requirements

Ask the user:

> **PRD Edit**
>
> I'm working with `{{SPEC_DIR}}/plan_artifacts/prd.md`.
>
> **What would you like to change?** For example:
>
> - Add or revise a feature, a flow, or an acceptance sketch
> - Change or add a locked decision
> - Update users, roles, authorization, or the data model sketch
> - Adjust scope or non-goals, or resolve an open question
> - Tighten density, fix wording, fix anti-patterns
> - Fold in an external requirements document. I will read it in full and quote it
> - Something else
>
> Describe the change, and point me at the section(s) if you already know where it lands.

**Wait for the user's response.** Do not proceed until you understand the intent.

If the request is vague ("improve the PRD", "clean it up"), ask **one or two** narrowing
questions first: which sections, what outcome they want, what is in or out of scope.

**If the request names an input document, read it completely now.** Never guess the contents of
a file you could not open. Build an outline of what it says per PRD section, with a pointer per
item, and list what it **contradicts** in the current PRD or in the codebase. **Those
contradictions are decisions for the user, not edits you make.**

### 5. Flag invariant and decision impact early

Once you understand the request, check it against the PRD's own declarations and tell the user
**now**, not after editing, if the change appears to:

- **Change a locked decision.** Note which one, and that you will trace ripple effects. **Confirm
  they really mean to change something load-bearing.**
- **Diverge from a declared source of truth.** Note the conflict and ask whether they want to
  override the source or align with it.
- **Require renumbering or new sections or ids.** Note that you will keep numbering,
  cross-references, and any table of contents in sync, and that **existing ids are never reused
  or silently renumbered.**

State these plainly and let the user confirm or adjust before you review.

### 6. Summarize and route

> **Understood.**
>
> - **Target:** `{{SPEC_DIR}}/plan_artifacts/prd.md`
> - **Edit goals:** {concise summary}
> - **Sections likely affected:** {list}
> - **Invariant / decision flags:** {any from section 5, or "none"}
>
> Proceeding to a deep review of the affected sections and a change plan for your approval…

Then read fully and follow `step-e-02-review.md`.

## Success / failure

✅ **Success:** PRD loaded in full. Its locked decisions and sources of truth extracted. Edit
intent clearly understood. Affected sections identified. **Invariant and decision impacts flagged
before editing.** Clean handoff to review.

❌ **Failure:** editing in this step. Proceeding without understanding intent. **Ignoring a
locked decision or source of truth the edit would touch.** Guessing the target file.

**Master rule:** Understand before touching anything. Surface load-bearing impacts at discovery
time, not after the edit.
