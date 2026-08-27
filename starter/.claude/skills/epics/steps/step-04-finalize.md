# Step 04: Finalize, validate & sync

## Step goal

Validate full requirement coverage and story quality, ensure the status file mirrors the plan,
summarize what changed, and close out.

## Mandatory rules

- 🔎 Validate **via the helper**, not by re-reading every file.
- 🔁 The status file must end this step as a **faithful mirror of the tree**, with manual status
  values preserved.
- 📖 Read this whole step before acting.

## Sequence

### 1. Coverage validation

```bash
{{SPEC_HELPER_COMMAND}} coverage
```

- Every in-scope feature must map to at least one epic **and be covered by a story within it**.
- **If anything is UNCOVERED, it must be a deliberate deferral.** Otherwise return to step 02 to
  assign it, or step 03 to write the missing story. **Do not close with accidental gaps.**

### 2. Structure & quality spot-check

Run `{{SPEC_HELPER_COMMAND}} list` and verify:

- Every epic folder has an epic file.
- Story numbering is contiguous within each epic, and titles are present.
- **The index's epic-list table and coverage map match the actual folders.** Fix the index if it
  drifted.

Spot-check a couple of stories for: testable Given/When/Then criteria, **idempotency and
authorization guards on any mutation story**, tables created only as needed, no forward
dependencies, and that each story's invariants **trace back to the PRD's locked decisions**.

### 3. Sync the status mirror

```bash
{{SPEC_HELPER_COMMAND}} sync-status
```

Confirm the reported counts match what you built, and that **previously-set status values were
preserved.** The command prints added and removed items; "structure unchanged" means nothing
drifted.

### 4. Summarize

> **✓ Epics & stories, {create|edit} complete**
>
> - **Epics:** {count} ({list})
> - **Stories:** {count}
> - **Coverage:** {covered}/{total} features mapped {(+ deferred: …)}
> - **Status mirror:** synced
> - **What changed this session:** {bullets}
>
> Next: run `/create-story` to turn a planning story into a dev story, then implement it.

### 5. Menu

- **[V] Validate again**: re-run coverage and list after fixes.
- **[E] Edit more**: add or revise an epic or story. Route to step 02 for a new epic, step 03
  for an existing one.
- **[X] Done**: exit with the summary.

#### Handling

- IF V: run sections 1 and 2 again, report, re-show the menu.
- IF E: gather the ask, route to the right step.
- IF X: confirm and exit. **The spec documents live in the personal, git-excluded tree, so there
  is nothing to commit.** If you changed the helper script, run its own tests.
- Anything else: clarify, re-show the menu.

## Success / failure

✅ **Success:** all in-scope features covered, with deferrals explicit. Every epic has an epic
file. The index matches the tree. Status synced with manual values preserved. Accurate change
summary. Clean exit.

❌ **Failure:** **silent coverage gaps.** An index out of sync with the folders. Status not
regenerated. Closing without a summary.

**Master rule:** Close only when the plan is complete, internally consistent, and faithfully
mirrored in the status file.
