# Step E-4: Complete & self-check

## Step goal

Summarize the edits, optionally run a quality self-check, and close out cleanly or loop back for
more.

## Mandatory rules (read first)

- 📖 Read this entire step file before acting.
- 🎯 **No new content changes here** unless the user asks to loop back to editing.

## Sequence

### 1. Compile the edit summary

Gather from this session:

- **Sections changed**, with one-line descriptions.
- **Counts:** additions, updates, removals, restructures.
- **Cross-references touched:** table of contents, anchors, ids.
- **Invariant impact:** what, if anything, was intentionally changed, and the user's confirmation
  of it.

### 2. Run the self-check, if requested

**There is no separate validation skill. The self-check lives here.** Verify the edited PRD
against `data/prd-purpose.md`:

- **Density:** no filler introduced, new prose is tight.
- **Measurability:** new requirements have concrete, testable criteria. No subjective adjectives.
- **Source-of-truth fidelity:** new domain content matches the declared sources. New stack
  content matches the locked stack decisions and the project memory file. **No invented logic.**
- **Invariants intact:** every locked decision still holds and is uncontradicted elsewhere,
  unless the user explicitly changed it this session.
- **Structure and anchors:** any table of contents matches the actual headers, in-page anchors
  resolve, ids are unique and parseable (`{{SPEC_HELPER_COMMAND}} reqs` still lists every
  feature), no YAML frontmatter, title line intact.
- **Language:** copy matches the document's locked language conventions.

You may delegate the **read-only verification sweep** to a search agent, then judge the results
yourself.

Report findings as:

- ✅ **Pass**: list what was checked.
- ⚠️ **Issues found**: list each with its location and a proposed fix, then offer to fix them by
  looping back to E-3.

> Note: this self-check is a **content and consistency** review of a document. It does not run
> the project's test suite. The PRD is documentation, and it lives in the personal, git-excluded
> tree, so **there is nothing to commit for the team.**

### 3. Present the completion summary

> **✓ PRD edit session complete, `{{SPEC_DIR}}/plan_artifacts/prd.md`**
>
> **Changes:**
> {bulleted summary by section}
>
> **Cross-references updated:** {…, or "none"}
> **Invariant impact:** {what changed and was confirmed, or "none. Invariants intact"}
> {If run: **Self-check:** ✅ Pass / ⚠️ {N} issue(s)}
>
> **Revision history:** row added for today.

### 4. Suggest reconciling the epics and stories

**PRD changes usually ripple into the epic and story breakdown.** If this session changed
anything that affects requirements. Added, removed, or renamed a feature, changed a flow, a
decision, the data model, or the scope, **proactively offer `/epics`**:

> Heads up: you changed {what}. That likely affects the epics and stories breakdown.
>
> Want me to run **`/epics`** now to reconcile them? It re-checks requirement coverage, lets you
> revise the affected epics and stories, and re-syncs the status mirror.

- **Yes:** hand off directly. Invoke the `epics` skill. It opens in edit mode, detects the
  existing breakdown, and starts with its coverage check against the just-edited PRD. **Tell it
  which sections and features changed** so it focuses there.
- **No, or not applicable:** skip it. If the edit was purely cosmetic with no requirement impact,
  omit the offer entirely.

**Make this offer once, here, before the menu.**

### 5. Menu

- **[C] Self-check**: run section 2, if not already run.
- **[U] Update epics**: reconcile the breakdown now by invoking the `epics` skill in edit mode.
- **[E] Edit more**: return to editing. Small changes route to `step-e-03-edit.md`, substantial
  ones to `step-e-02-review.md` for a fresh plan.
- **[X] Done**: exit with a final one-line confirmation.

**Halt and wait.**

## Success / failure

✅ **Success:** accurate, specific edit summary. Self-check run when requested, with any issues
offered for fix. Clear options to iterate or finish. **The user knows exactly what changed and
where.**

❌ **Failure:** a vague or incomplete summary. Skipping a requested self-check. Making silent
edits in this step. Not surfacing self-check issues. **Committing without being asked.**

**Master rule:** Close the loop honestly. Say exactly what changed, verify it holds together,
and let the user iterate or stop.
