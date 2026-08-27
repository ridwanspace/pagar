# Step 01: Context & requirements

## Step goal

Establish the mode, pull the requirement inventory **from the PRD via the helper** rather than by
loading the whole PRD, and confirm the scope of work with the user, **before designing or
editing any epic**.

## Mandatory rules

- 🛑 Do NOT create or edit any epic or story file in this step.
- 🔎 Use the helper for inventory and current state. Read only the **specific PRD sections** you
  need. **Never dump the whole PRD into context.**
- 📖 Read this whole step before acting.
- 🎯 Carry the persistent facts from `SKILL.md`.

## Sequence

### 1. Determine mode and current state

```bash
{{SPEC_HELPER_COMMAND}} list
```

- **Empty → CREATE mode.** There is no breakdown yet.
- **Has epics → EDIT mode.** Show the tree and proceed to understand the requested change.

### 2. Extract the requirement inventory, without reading the whole PRD

```bash
{{SPEC_HELPER_COMMAND}} reqs        # features (primary), flows, decisions, modules
{{SPEC_HELPER_COMMAND}} coverage    # which features are already covered (edit mode)
```

- The **`F-*` feature codes are the primary requirement units.** Flows, decisions, and module
  codes are cross-reference dimensions.
- **To understand what a feature *means*, read just its definition** in the feature catalog and,
  if needed, its flow and its data-model entries. **By section, not the whole file.** Use
  targeted searches and offset reads.
- Note any **non-functional requirements** and **delivery phases** the PRD declares. **Epics
  should sequence to the phases.**

### 3. Confirm scope with the user

**CREATE mode:**

> I'll break the PRD into epics and stories under `{{SPEC_DIR}}/plan_artifacts/`, one epic per
> folder, and mirror status in the status file.
>
> From the PRD I see **{N} features**, **{F} flows**, and **{P} delivery phases**.
>
> - Do you want to cover **all** features now, or scope to a subset?
> - Any features to explicitly defer?

**EDIT mode:**

> Current breakdown:
> {paste the `list` output}
>
> What would you like to do?
>
> - Add a new epic, or a story to an existing epic
> - Revise an epic or story (goal, criteria, scope)
> - Re-sync the status mirror after manual changes
> - Re-check coverage after a PRD change
> - Renumber or re-slug
>
> (If the PRD just changed, I'll run `coverage` to find newly-uncovered features.)

**Arriving from `/rca`**, where the user pastes or points at its handoff block: **the findings
are already verified and root-caused. Do NOT re-investigate.** Each accepted finding becomes an
epic or story with a source marker set to the report id. It **covers no feature code** unless the
PRD already has one, and **coverage will rightly not list it.** Confirm which findings are in
scope, then continue.

**Wait for the user's answer.** Do not proceed until scope is clear.

### 4. Flag invariant and source-of-truth considerations

Based on the scope, read the PRD's **key-decisions table** and note up front **which locked
invariants the affected features touch.** These become guardrails the stories must encode.

If the sources-of-truth section names a domain source, note which features must quote it. **If
anything in the requested scope would contradict the PRD or that source, surface it now.**

### 5. Route

- **CREATE mode**, or EDIT mode adding at least one new epic: read fully and follow
  `steps/step-02-design-epics.md`.
- **EDIT mode editing an existing epic or story only:** skip to `steps/step-03-write-stories.md`,
  telling it which one you are editing.
- **EDIT mode, only a re-sync or coverage check:** do it now, report results, then go to
  `steps/step-04-finalize.md`.

**State which route you are taking and why**, then load that step.

## Success / failure

✅ **Success:** mode detected. Requirement inventory pulled **via the helper**, with the PRD read
only by needed section. Scope explicitly confirmed. Invariants flagged. Correct route chosen.

❌ **Failure:** **loading the whole PRD into context.** Creating or editing files in this step.
Proceeding without confirmed scope. Missing the feature, flow, and phase inventory.

**Master rule:** Understand the requirements and the ask first, cheaply, via the helper, before
touching the breakdown.
