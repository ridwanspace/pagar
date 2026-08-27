# Step 03: Extract learnings into the local rules (with compaction)

## Step goal

Capture the **non-obvious, durable** learnings from implementing this story and record them **in
the smallest right place**, so the next session and the next story do not relearn them. Keep the
always-loaded context lean by routing topic-specific rules into path-scoped rule files, and
**compacting any file that crosses the size threshold.**

**This is the step that makes the project smarter over time. Quality over volume.**

## Mandatory rules

- 📖 Read this whole step before acting.
- 🧠 **Record only what is non-obvious AND durable**: it would save real time or prevent a repeat
  mistake. **Version control already has the changelog. Do NOT restate code, routine edits, or
  anything the history captures.**
- 📏 **Keep the always-loaded project memory file under about 200 lines.** A longer file consumes
  more context and **reduces adherence to everything in it.** When it crosses the threshold,
  **compact.**
- 🎯 **The right home for each fact**, per the routing table below.
- 🇬🇧 The rule content is technical. Write it in the project's working language, regardless of the
  product's copy language.

## Sequence

### 1. Gather what actually happened, scoped

- Read the **dev story's completion notes and agent record.** Do not reopen the whole story tree.
- Look at the shape of what changed, **to jog memory, not to copy it.**
- Recall from this session: decisions made, **assumptions overturned**, gotchas hit, a pattern or
  helper proven, a constraint discovered, and **anything VERIFIED LIVE in step 01.**

### 2. Decide what is worth recording

Record a fact only if **non-obvious and durable**. Good candidates:

- **A platform gotcha proven the expensive way**: a framework quirk, a validation-layer edge, a
  concurrency behaviour, a type-checker corner, a third-party API's undocumented trap. Beyond
  what the project's documentation already says.
- **An architecture decision and WHY**: a module boundary, an idempotency-key shape, where a
  layer's line falls, that future stories must match.
- **A reusable helper's real signature, or a proven pattern**, so the next story calls it
  correctly instead of reinventing.
- **A constraint discovered** that changes a future approach: a quota, a performance limit, a
  real-data shape.
- **A fact verified LIVE.** High value: it moves a risk from "assumed" to "proven".

**Do NOT record:** what the code says, routine edits, restated existing documentation, or facts
relevant only to this one conversation.

### 3. Route each fact to the smallest right home

| Fact type | Home | How |
| --- | --- | --- |
| A global rule that applies everywhere, every session | the project memory file | Append to the right existing section. **One tight bullet.** |
| A rule or gotcha specific to a subsystem or file type | `.claude/rules/<topic>.md` | A **path-scoped** rule file. Loads on demand only when matching files are touched. |
| The user's preference or working style | the agent's memory mechanism | One fact per entry. **Project facts do NOT go here.** |
| A repeatable multi-step procedure | a skill | Rare. A rule usually suffices. |

**The rule-file format**: frontmatter is what makes it path-scoped:

```markdown
---
description: <one line. What this rule covers>
paths:
  - "<glob>"
  - "<glob>"
---

# <Topic> rules

- <durable, specific, actionable fact>
- <fact. Cite the source if it is a decision>
```

- **Rules WITHOUT paths load at launch.** Use sparingly: that is always-loaded budget. **Rules
  WITH paths load only when a matching file is touched, which is free context the rest of the
  time. Prefer path-scoped.**
- **One topic per file.** Reuse an existing rule file if the topic already has one. Check first.

### 4. Compaction: the size trigger

**Check sizes before and after editing**, with a line count over the memory file and the rule
files.

Apply the **200-line threshold**:

- **The memory file is at or over the threshold**, or your edit would push it over: **compact
  it.** Pick the **most self-contained, topic-cohesive section**, move it into a path-scoped rule
  file, and leave a **one-line pointer** behind:
  > - <Topic>: see `.claude/rules/<topic>.md` (loads when you touch `<matching paths>`).

  This both records the new learning **and** shrinks the always-loaded budget. **Prefer moving a
  section that is already path-scoped in practice.** That is pure win.
- **A rule file is at or over the threshold:** split it. Either carve a sub-topic into a sibling
  with a narrower path glob, or **tighten** it: collapse verbose prose into dense bullets. **The
  file is for the model, not a tutorial.**
- **Do NOT compact for its own sake.** If everything is comfortably under, append your bullets and
  move on. **Note in the summary that no compaction was needed.**

**When compacting, MOVE content, do not lose it.** Re-read the destination after the move to
confirm the section landed intact and the pointer is correct. **Compaction must be
content-preserving.**

### 5. Update the user-preference memory, if any

If this story surfaced something about the **user's preferences or working style**, not the code,
record it in the agent's memory mechanism. **Check for an existing entry that already covers it
first. Update rather than duplicate. Project facts belong in the rules, NOT in memory.**

### 6. Self-check the edits

- Re-read each file you changed. **Confirm the fact is recorded ONCE, in one right place, with no
  duplication** between the memory file and a rule file.
- Confirm the memory file is under the threshold, or that you compacted it down.
- Confirm any new rule file has **valid frontmatter** and that **its path globs actually match the
  files the rule is about.** A rule scoped to a path nothing matches never loads.

### 7. Close the step

> **Extracted learnings. Story {ref}:**
>
> - {fact} → `.claude/rules/<topic>.md` (path-scoped) | the memory file §<section> | memory
> - …
>
> **Compaction:** {moved §X from the memory file to rules/<topic>.md, now N lines | none needed}.
> **Deliberately NOT recorded:** {what you skipped and why}, so the user can override.

Then read fully and follow `steps/step-03b-sync-team-docs.md`.

## Success / failure

✅ **Success:** only **non-obvious, durable** facts recorded, each in the smallest right home.
Path-scoped rules used for subsystem facts. The memory file kept under the threshold via
**content-preserving** compaction when needed. Memory updated only for user-style facts. No
duplication. **A clear report including what was deliberately skipped.**

❌ **Failure:** **logging a changelog of edits.** Bloating the always-loaded file past the threshold
without compacting. Duplicating a fact in two homes. Putting a path-specific rule in the global
file, or a global rule only in a path-scoped file. **Losing content during a "compaction".**
Recording project facts in the user-preference memory.

**Master rule:** Make the project permanently smarter with the fewest, best facts, and keep the
always-loaded context lean by routing detail to on-demand rules.
