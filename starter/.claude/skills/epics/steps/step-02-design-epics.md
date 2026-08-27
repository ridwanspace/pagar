# Step 02: Design the epic structure

## Step goal

Design (create mode) or extend (edit mode) the **epic list**, organized by user value, map every
feature to an epic, and get the user's **explicit approval before writing any story**.

## Mandatory rules

- 🛑 Do NOT write individual stories in this step. Epic-level only.
- 🔗 **Each epic must be standalone**: it delivers complete value for its domain and **does not
  require a LATER epic to function.**
- 🎯 Organize by **user value, not technical layers.** Carry the persistent facts and invariants
  from `SKILL.md`.
- ⏸️ Get **explicit approval** before proceeding.

## Sequence

### 1. Review inventory

From step 01 you have the requirement inventory and, in edit mode, the existing tree and
coverage. Re-run `{{SPEC_HELPER_COMMAND}} coverage` if needed.

### 2. Apply the epic-design principles

- **User-value first.** Each epic enables a user or role to accomplish something meaningful:
  "sign up and manage my account", "run the full ordering workflow", "see the dashboard and
  export reports".
- **Group cohesive features.** Features that form one workflow, or touch the same core tables and
  modules, belong in one epic with ordered stories. Avoid epics that each re-touch the same
  modules, which is just file churn. **In a full-stack repository a story usually spans both
  halves. Keep a vertical slice in ONE story rather than splitting "server story" and "client
  story".**
- **Standalone and ordered.** Later epics may build on earlier ones, but each must stand alone.
  **No forward dependencies.**
- **Sequence to the PRD's delivery phases.**
- **Respect invariants at the boundary.** If two features share a locked invariant, two write
  paths into the same ledger, one workflow's idempotency key, **keep those features coherent in
  one epic.**

**✅ Good** (user value, standalone): *Auth and access control* covering sign-in, roles, and
permissions, as the foundation other epics build on. *Core data entry*, the primary day-to-day
record-keeping for the main role. *Reporting and export*, built on the data the earlier epics
capture.

**❌ Bad:** "Database setup", "All API endpoints", "All domain models", "All UI components".
These are technical layers with no user value. Also bad: creating all tables in epic 1.

**⚠ The one exception to "no technical-layer epics", the application's own shell and component
vocabulary.**

"All UI components" is a bad epic. But the rule above, applied without this caveat, produces a
predictable failure: **nobody ever owns the application's own interface.** Every epic is a domain
workflow, each ships its screens on defaults, and forty stories later the product is functionally
complete and visually incoherent, **with coverage reporting 100% the whole way**, because
coverage only checks the feature codes the PRD happened to define.

So if the PRD has an interface-craft feature:

- **Place the shell and vocabulary stories in the FOUNDATION epic**: the one with identity,
  authentication, and navigation that everything else renders into. **Not a standalone "UI
  epic".** They belong with the substrate for the same reason the auth helpers do. They are the
  frame and the visual language every later epic writes into, and **vastly cheaper before the
  screens exist than retrofitted after.**
- **Place any whole-product polish or accessibility-audit story LATE**, in the pre-launch epic,
  **after the surfaces it inspects actually exist.** A sweep run early inspects nothing and has
  to be redone.
- **Prefer guard tests over prose.** A story that ships reusable components **and** tests that
  fail on drift protects every later epic. **A rule in a document decays. A failing test cannot.**

If no such feature exists in the PRD and no design system is in play, **say so explicitly** when
presenting the epic list, so the user can decide, rather than letting it pass unmentioned.

### 3. Propose the epic list

For each epic, draft: a **user-centric title**, a **goal** stating what users can do after it
ships, the **features covered**, the **phase**, the **dependencies** on earlier epics or "none",
and a **cohesion rationale** for why these features are one epic.

Use `{{SPEC_HELPER_COMMAND}} next-id` to get the next epic number(s), **so folder names do not
collide**, especially in edit mode.

### 4. Build the coverage map and check for gaps

Map **every** feature to an epic. Cross-check against the coverage output.

- **Create mode:** ensure all in-scope features are assigned.
- **Edit mode:** focus on the features coverage reports as **uncovered**.

**Call out any feature you are intentionally deferring, so "uncovered" is a choice, not an
oversight.**

**⚠ A 100% coverage number is not the same as complete coverage.** Coverage answers "is every
declared feature mapped to an epic?" **It cannot see a requirement the PRD never gave a code
to.** Before trusting the number, check the two things catalogs systematically omit:

- **The application's own interface craft.** Is there a feature covering the shell and its
  component vocabulary? If one exists in the codebase, do new epics **reuse** it, or would a
  story quietly fork it?
- **Accessibility.** If a non-functional requirement names a standard, **does any story actually
  VERIFY it?** A standard in a non-functional section names no owner and no checkpoint.

If either is missing, **flag it as a GAP IN THE PRD, not a deferral.** The fix is usually a small
`/edit-prd` run to add the feature, then map it here. **Do not silently paper over it by folding
the work into an unrelated epic's story.**

### 5. Present for approval

> **Proposed epic structure** ({N} epics):
>
> {per epic: number, title, one-line goal, features covered, phase, depends-on}
>
> **Coverage:** every in-scope feature maps to an epic. {Deferred: …, or "none."}
>
> **Interface / accessibility check:** {shell + vocabulary story in epic {N}, polish and audit in
> epic {M}} · {or "no interface-craft feature in the PRD. Flagging as a possible gap"} · {or
> "not applicable, no screens in scope, confirmed"}
>
> **Questions:**
>
> 1. Does this organize the work the way you want, by user value and sequenced to the phases?
> 2. Any epics to split, merge, reorder, or rename?
> 3. Confirm the deferred features are intentional?
> 4. Confirm the interface line above. Is the application's own interface owned by a story, or
>    deliberately out of scope?
>
> Approve to proceed to story writing?

**Wait for approval.** Revise and re-present until the user approves.

### 6. Write the epic scaffolding, after approval

For each approved epic:

1. Get the number and slug from the helper.
2. Create the folder.
3. Create `epic.md` from `templates/epic-template.md`, filled in: goal, features covered, related
   flows, phase, cohesion rationale, **the applicable invariants** pulled from the PRD's locked
   decisions, dependencies, and a story table with titles only for now.
4. Create or update the index from `templates/epics-index-template.md`: the epic-list table and
   the feature-to-epic coverage map.

Then run:

```bash
{{SPEC_HELPER_COMMAND}} sync-status   # create/update the status mirror
{{SPEC_HELPER_COMMAND}} coverage      # confirm the map matches the files
```

### 7. Route

Display a one-line confirmation, then read fully and follow `steps/step-03-write-stories.md`.

## Success / failure

✅ **Success:** epics organized by user value, standalone, sequenced to phases. Every in-scope
feature mapped, with deferrals explicit. **The interface and accessibility check made and
answered.** User approved. Epic folders, epic files, and the index created. Status synced.
Coverage verified.

❌ **Failure:** technical-layer epics. Unmapped features with no deferral note. **Reporting full
coverage while nothing owns the application's own interface or verifies its accessibility
floor.** Writing stories here. Creating files before approval. Forgetting to sync status or
update the index.

**Master rule:** Get the shape right and approved, with full coverage, before any story is
written.
