# Step 04: Finalize & sync the documents

## Step goal

Mark the story done, run the definition-of-done checklist, and **keep every relevant spec document
consistent with what was actually built**, on both the implementation side and the planning side.
Then summarize.

## Mandatory rules

- 🔁 **Documents must end this step truthful:** the dev story, the status mirror, the planning
  story's drift notes, and the epics index.
- 📝 **Write back to the planning side only where implementation revealed drift or conflict.** Do
  not rewrite the plan wholesale.
- 📖 Read this whole step before acting.
- ⚠ **Committed team documents are NOT written from this step.** If implementation revealed a
  team document is stale or contradicted, **record that in the completion notes.**
  `/code-review` makes the surgical team-document update, or surfaces the conflict. **Personal
  planning writeback is not team-document editing.**

## Sequence

### 1. Definition-of-done checklist

Validate against `checklist.md`. The story is done **only if ALL hold**. If anything fails, go
back to step 02 or 03. **Do not finalize a partial story.**

### 2. Finalize the dev story file

In permitted sections only:

- Set the status to done.
- **Completion notes:** a concise summary. What was built, key decisions, tests added, and **any
  trap the green suite did not catch**: a surprising behaviour, a configuration gotcha, an
  ordering hazard. **This is the raw material the lessons mining reads and `/code-review`
  distills into rules. A lesson not written here is a lesson lost.**
- **File list:** confirm it lists every file touched.
- Tick the definition-of-done items that are now true.

### 3. Flip status in the mirror

```bash
{{SPEC_HELPER_COMMAND}} set-status <ref> done
{{SPEC_HELPER_COMMAND}} dev-list      # confirm this story now shows done
```

### 4. Write back to the planning side: keep the plan truthful

**This is why this skill touches both trees.** Do each that applies:

**a) Drift notes on the planning story.** If implementation diverged from what the planning story
described, a criterion was refined, a constraint surfaced, the approach changed, scope shifted,
append a short block so **the plan reflects reality**:

```markdown
## Implementation notes (from /dev-story)

- {what changed vs the plan, and why}. See the dev story at {path}.
- {any new constraint future stories should know}
```

Keep it **brief and factual**. **If there was no drift, skip this. Do not add an empty block.**

**b) Flag PRD or epic conflicts. Do not silently diverge.** If implementation revealed that the
**PRD** or the **epic** is wrong or no longer holds, a formula, a locked decision, a flow, the
data model, **do NOT quietly bake a contradiction into the code.** Surface it:

> ⚠️ Implementation conflict: {what the code needed vs what the spec says}.
> This should be reconciled in the spec. Want me to run **/edit-prd** or **/epics**?

**Note the conflict in the completion notes and the planning story's implementation notes, so it
is not lost.**

**c) Refresh the index.** Ensure the planning index is not stale:

```bash
{{SPEC_HELPER_COMMAND}} sync-status   # reconcile structure, preserving manual status
{{SPEC_HELPER_COMMAND}} coverage      # confirm the story's features are still covered
```

If the index's tables visibly drifted from reality, update them, or recommend `/epics` for a
structural change.

### 5. Summarize

> **✓ Story {ref} implemented & done, {title}**
>
> - **Dev story:** {path} (Status: done)
> - **Status mirror:** {ref} → done
> - **Files changed:** {count} ({key paths})
> - **Tests:** {added or updated; suite green}
> - **Invariants verified:** {list}
> - **Plan writeback:** {drift notes added? conflicts flagged? index refreshed?} or "no drift,
>   plan unchanged"
> - **Open questions / conflicts:** {list, or none}
>
> **Next:** run **`/code-review`** to close the loop. Verify the surface with real requests
> and/or a visual pass, sync the end-user documentation, extract learnings, mirror the
> team-relevant subset to the committed docs, feed this story's ground truth forward into
> dependent stories, and absorb one piece of manual work into the pipeline itself.

> Tip: for the review, prefer a **different model** than the one that implemented this.

### 6. Menu

- **[P] Post-review**: run `/code-review {ref}`. **Recommended next.**
- **[N] Next story**: loop to step 01 for the next dev story.
- **[R] Reconcile spec**: invoke `/edit-prd` or `/epics` for a flagged conflict.
- **[X] Done**: exit. **Commit only when the user asks**, via `/commit`, which re-runs the
  gates. **The spec documents are never staged.**

## Success / failure

✅ **Success:** the definition of done passes. The dev story finalized with status, notes, and file
list. Status mirror flipped. **The planning side kept truthful**: drift notes where needed,
conflicts flagged rather than buried, index refreshed. A clear summary and next step.

❌ **Failure:** marking done with a failing definition of done. Updating the implementation side
but **leaving the planning side stale or contradictory. Silently coding around a PRD or epic
conflict.** Forgetting to flip the status.

**Master rule:** Finish by leaving the whole spec, both trees, an honest reflection of what was
built; flag conflicts for reconciliation rather than hiding them.
