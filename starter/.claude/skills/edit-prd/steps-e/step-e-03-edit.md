# Step E-3: Edit & update

## Step goal

Apply the approved change plan **surgically, section by section**, keeping ids,
cross-references, and any table of contents in sync.

## Mandatory rules (read first)

- 📖 Read this entire step file before acting.
- 🎯 **Apply ONLY what the approved plan covers.** If you discover a needed change that was not
  in the plan, **pause and get approval** before doing it.
- ✂️ **Edit surgically.** Use targeted edits on specific passages. **Do NOT rewrite the whole
  file.** Whole-file rewrites drop content and break anchors.
- 🗣️ Match the document's copy-language conventions. Match the language of the text you are
  editing.
- 🛑 **Protect the locked decisions and declared sources of truth.** If an approved edit changes
  one, that is allowed *because the user approved it in E-2*, but **still execute it carefully
  and update everything it ripples into.**

## Sequence

### 1. Restate the approved plan

> **Applying approved changes to `{{SPEC_DIR}}/plan_artifacts/prd.md`:**
> {one line per change, in apply order}

### 2. Apply changes section by section, in plan order

For each change:

**a) Locate the exact text.** For larger sections, delegating the *finding* to a read-only search
agent is fine, but **you** perform the writes.

**b) Make the edit** with enough surrounding context to be unambiguous. Honor the document's
existing formatting:

- Follow the heading style the PRD already uses.
- Markdown tables for decisions, requirements, matrices, the data model, and appendices. Keep
  column alignment consistent with the existing table.
- Diagram blocks only if the document already uses them.
- **IDs stay consistent and machine-parseable.** Features `F-[A-Z][A-Z0-9-]*[A-Z0-9]`, flows
  `FLOW \d+`, decisions `D\d+`, modules `M\d+(-[A-Z]+)?`. **Never reuse or silently renumber.** A
  new decision gets the next free number, a new feature a fresh code, a new flow the next number.
- **No YAML frontmatter.** This document has none. Do not add any.

**c) Keep density and measurability.** New prose is tight, with no filler. Any new requirement is
measurable.

**d) Report progress** after each section:

> **Updated §N, {Title}:** {one-line summary}

### 3. Keep cross-references in sync, as part of the edit, not after

Whenever a change adds, removes, renames, or renumbers a section:

- **Table of contents**, if the document has one: add, remove, or rename the entry and fix its
  anchor link.
- **In-page anchors.** Anchors are typically the lowercased title with spaces turned to hyphens
  and most punctuation dropped. **If you rename a heading, update every link that points to it.**
- **Cross-section references** the change invalidates.

**If a renumber would cascade across many references, prefer APPENDING**: a sub-lettered
section, a new row, the next free id, **over renumbering everything.** It is lower risk and it
is how living PRDs actually grow.

### 4. Record the edit in the revision history

The PRD tracks changes **in its body**, not in frontmatter. Maintain a `## Revision history`
section near the **end** of the document, creating it if absent. Append one row per session:

```markdown
## Revision history

| Date   | Author       | Change summary                                           |
| ------ | ------------ | -------------------------------------------------------- |
| {date} | {user/owner} | {concise summary of this session's changes, with §refs}   |
```

- Use the **real** current date from the session context. **Do not invent one.**
- If the section exists, just append a row.
- Keep the entry concise but specific: which sections, what changed.

### 5. Self-verify the result

After all edits:

- Re-read each changed section to confirm the edit applied and **nothing adjacent was
  clobbered**.
- Confirm any table of contents matches the actual headers.
- Confirm ids are still unique, consistent, and parseable. **Spot-check mechanically**:
  `{{SPEC_HELPER_COMMAND}} reqs` if features changed.
- Confirm **no locked decision was weakened beyond what the user approved.**
- Confirm no YAML frontmatter was introduced and the title line is unchanged.

**If you find a problem, fix it now and note the correction.**

### 6. Confirm completion and present options

> **PRD edits complete, `{{SPEC_DIR}}/plan_artifacts/prd.md`**
>
> **Applied:** {count} change(s) across {sections}
> **Cross-references updated:** {table of contents / anchors / ids, or "none"}
> **Revision history:** row added for today.
>
> **What next?**

Then present the menu. **Halt and wait.**

### 7. Menu

- **[S] Self-check**: run a final quality pass against `data/prd-purpose.md`. Go to
  `step-e-04-complete.md` with the self-check requested.
- **[A] Adjust**: more edits. Small ones loop back to section 2, substantial ones back to
  `step-e-02-review.md` for a fresh plan.
- **[D] Done**: finish with a summary. Go to `step-e-04-complete.md`.

## Success / failure

✅ **Success:** every approved change applied surgically and correctly. Formatting, ids, and
language conventions preserved. Cross-references kept in sync. Revision-history row added.
Self-verification passed. **Invariants intact unless explicitly changed.**

❌ **Failure:** changes beyond the approved plan. **A whole-file rewrite that drops content.**
Broken anchors or a stale table of contents. Duplicated or renumbered ids without updating
references. YAML frontmatter added. Missing revision-history entry. **A locked decision silently
weakened.**

**Master rule:** Execute exactly the approved plan, surgically, and leave the document internally
consistent. Anchors, IDs, numbering, and invariants all coherent.
