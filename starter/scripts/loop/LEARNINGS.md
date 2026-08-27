# Loop learnings — the harness's compounding memory

Lessons distilled from real story-loop failures (by the loop's **reflect** phase). The last
`LOOP_LEARN_MAX_LINES` lines of this file are injected into **every** phase session's system
context, so each failure is paid for once and prevented thereafter. This file is committed —
the investment travels with the repo.

Entry format (reflect sessions append at the END, newest last; merge into an existing entry
instead of duplicating it):

```
## YYYY-MM-DD · story <ref> · <phase> · <failure class>

- **What happened:** one line of symptom.
- **Root cause:** one line.
- **Rule for future runs:** one imperative sentence a session can act on.
```

Size is **enforced, not requested**: when this file crosses `LOOP_LEARN_COMPACT_AT` lines
(default 120), the loop automatically runs a compaction session (`prompts/compact.md`)
that merges duplicate root causes and generalizes old entries into class-level rules —
never dropping a rule that still prevents a failure. Sessions are protected either way:
only the last `LOOP_LEARN_MAX_LINES` lines are ever injected into context.

<!-- entries below — reflect sessions append here; humans may edit/compact freely -->

## 1970-01-01 · story 0.1 · example · format demonstration (not a real failure)

- **What happened:** this starter ships with one example entry so a reflect session can see the format in place. Delete it after your first real lesson lands.
- **Root cause:** n/a — this entry exists to be deleted.
- **Rule for future runs:** write entries exactly this shape: one symptom line, one root-cause line, one imperative rule a headless session can act on without asking anyone.
