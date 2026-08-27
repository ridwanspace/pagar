# Step 3: Draft the PRD

## Step goal

Render the approved requirement set into a full PRD using `templates/prd-template.md`, review it
with the user, and, **only after approval**: write `{{SPEC_DIR}}/plan_artifacts/prd.md`.

## Mandatory rules (read first)

- 🛑 NEVER write the file before the user approves the draft.
- 📖 Read this entire step file before acting.
- 🎯 **The approved requirement set from step 2 is the contract.** Render every `F-*`, `FLOW n`,
  `Dn`, and `Mn` exactly as approved. No additions, drops, or renumbering. **If drafting exposes
  a gap, pause and ask.** Do not silently patch the set.
- ✍️ Apply the standards from `data/prd-purpose.md`: dense prose, measurable statements, no
  filler, no invented domain logic. **Content from declared sources of truth, including an input
  document, is quoted, not paraphrased into something new.**
- 🚫 No YAML frontmatter. Plain markdown, numbered sections per the template.

## Sequence

### 1. Load the template

Read `templates/prd-template.md` in full. It defines the section skeleton. **Keep its numbering
and section titles.** Fill its placeholders. **Delete the template guidance comments** from the
final text.

### 2. Ask the review mode

> **Ready to draft.** How do you want to review?
>
> - **[S] Section by section**: I present each major section for sign-off before the next.
> - **[W] Whole draft**: I present the complete draft in one pass and we iterate on it.

**Halt and wait.**

### 3. Draft, per the chosen mode

Write each section from the approved materials:

- **§1 Overview and goals**: from the discovery summary. Product, problem, goals **stated
  measurably where possible**.
- **§2 Key decisions (locked)**: the decision table **verbatim** from step 2.
- **§3 Users and roles / authorization**: roles and the authorization model, referencing the
  decision that locks it.
- **§4 Scope and non-goals**: the in-scope summary plus the explicit non-goals list.
- **§5 Domain sources of truth**: each source, its location, and **what carries over
  verbatim**. In document mode, the input document is the **first** entry, cited by path and
  heading. Or state "greenfield, the decisions in this document are the domain source".
- **§6 Features**: one entry per `F-*`: what, why, and an acceptance sketch of 2 to 4 testable
  bullets. **Every code from the approved set appears in exactly one entry.** Keep any team ids
  the source document attached, as cross-references inside the entry.
- **§7 Core flows**: each `FLOW n` with actor, numbered steps, the key error and edge branches
  worth naming, and the `F-*` codes it exercises.
- **§8 Data model sketch**: entities, key fields, relationships. **Honor the locked data
  invariants.** This is a sketch to plan from, not a schema. The real models, boundary schemas,
  and migrations become the code-level source of truth later.
- **§9 Non-functional requirements**: **only NFRs actually decided or constrained**. Every line
  measurable or absent.
- **§10 Open questions**: everything deliberately unresolved, including document contradictions
  the user chose to defer, **so `/epics` does not trip on it silently**.
- **Appendix A Module map**: the `M-*` map from step 2. Omit the appendix entirely if the map
  was skipped.
- **Revision history**: one initial row: today's **real** date, taken from the session context
  and **never invented**, the author, and "Initial PRD created via /create-prd", plus the source
  file in document mode.

**Review mode S:** present each major section, halt for approval or edits, then continue.
**Review mode W:** present the whole draft, halt, iterate until approved.

### 4. Final approval gate

When the full draft is approved in review, ask explicitly:

> Draft approved. **Write it to `{{SPEC_DIR}}/plan_artifacts/prd.md` now?**
> [Y] Yes / [N] Not yet: more changes

**Halt and wait.** IF N: gather changes, revise, re-ask.

### 5. Write the file

On Yes: create the directory if needed, write the approved draft **exactly as approved**.
Confirm:

> **Written:** `{{SPEC_DIR}}/plan_artifacts/prd.md`
> ({N} sections, {N} features, {N} flows, {N} locked decisions)

### 6. Route

Read fully and follow `step-04-complete.md`.

## Success / failure

✅ **Success:** the draft rendered faithfully from the approved set in the user's chosen review
mode. Every id placed correctly. Dense, testable prose. Explicit write approval obtained. **File
written once, matching the approved draft.**

❌ **Failure:** writing before approval. IDs added, dropped, or renumbered during drafting.
Padding sections with invented logic or filler. Skipping the review-mode question. Adding YAML
frontmatter.

**Master rule:** The draft is a rendering of decisions already made. The file on disk must equal
the draft the user approved, nothing more, nothing less.
