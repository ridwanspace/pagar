# Step 4: Complete: self-check and handoff

## Step goal

Verify the written PRD holds together, confirm the revision history is in place, and hand the
user off to the next stage of the pipeline.

## Mandatory rules (read first)

- 📖 Read this entire step file before acting.
- 🎯 **No new content decisions here.** Fixes from the self-check are consistency repairs, not
  scope changes. Anything that would change scope goes back to the user.

## Sequence

### 1. Run the quality self-check

**Re-read the PRD from disk.** Verify what was actually written, not what you remember writing.
Then check:

- **Feature coverage:** every `F-*` from the approved set appears in **exactly one** feature
  entry. None missing, none duplicated, no stray codes.
- **Flow linkage:** every flow lists the codes it exercises, and every feature is reachable from
  at least one flow, or its absence is deliberate and noted.
- **Locked decisions consistent:** the decision table matches what the user locked. No section
  contradicts a decision. Sections that depend on a decision reference its number.
- **ID syntax parseable.** Confirm **mechanically**, not by eye:
  `{{SPEC_HELPER_COMMAND}} reqs` should list every feature.
- **Testable statements:** acceptance sketches and non-functional requirements are concrete and
  checkable. **No subjective adjectives** ("easy", "fast"), **no vague quantifiers**
  ("several", "various").
- **No invented domain logic:** everything domain-specific traces to a declared source of truth,
  cited by path and heading in document mode, or to an explicit user decision. Open unknowns
  live in the open-questions section, **not papered over**.
- **Document fidelity (document mode): spot-check three quoted passages against the source
  file. They must match verbatim. A paraphrase that drifted is a defect.**
- **Structure:** template numbering intact, no YAML frontmatter, revision history present at
  the end.

### 2. Fix or escalate

- **Consistency defects**: a typo'd id, a missing cross-reference, a duplicated code: fix them
  now with surgical edits and note each fix.
- **Scope-level findings**: a feature with no flow, a contradiction between sections: **present
  them to the user with a proposed resolution and wait for their call** before editing.

### 3. Confirm the revision history

Ensure the revision-history block exists at the end with the initial row: the **real** current
date from the session context, the author, and the creation note. Add it if the draft step
missed it.

### 4. Present the completion summary

> **✓ PRD created, `{{SPEC_DIR}}/plan_artifacts/prd.md`**
>
> - **Features:** {N} (`F-…` list)
> - **Flows:** {N} · **Locked decisions:** {N} · **Open questions:** {N}
> - **Source document:** {`<path>`, read in full, quoted | none, from scratch}
> - **Self-check:** ✅ Pass {or: ⚠️ {N} issue(s) fixed or escalated. List}
> - **Revision history:** initial row added.
>
> This PRD is now the single source of truth the pipeline decomposes. The natural next step is
> **`/epics`**: it reads the PRD, checks requirement coverage, and breaks the work into epics
> and stories.

### 5. Menu

- **[E] Run /epics**: start decomposing the PRD now.
- **[R] Review a section**: walk through any section together. Small fixes applied surgically,
  scope changes go through a mini plan-and-approve.
- **[D] Done**: finish with a one-line confirmation and stop.

**Halt and wait for the user's choice.**

#### Menu handling

- IF E: invoke the `epics` skill. Tell it this is a fresh PRD with no existing breakdown.
- IF R: review the named section, apply approved fixes, re-show the menu. **Substantial rework
  means recommending `/edit-prd`** as the disciplined path.
- IF D: confirm completion and exit. The PRD lives in the personal, git-excluded tree, so there
  is nothing to commit for the team. **If the user wants a team-facing copy, that is a separate
  committed document, and only when they ask.**
- IF anything else: clarify, then re-show the menu.

## Success / failure

✅ **Success:** self-check run **against the file on disk**. Defects fixed or escalated honestly.
Revision history in place. User handed off with a clear next step and a working menu.

❌ **Failure:** skipping the self-check, or **running it from memory instead of the file**.
Silently "fixing" scope-level problems. A vague summary. Auto-running `/epics` without the user
choosing it.

**Master rule:** Close the loop honestly. Verify the artifact on disk, say exactly what it
contains, and let the user choose the next move.
