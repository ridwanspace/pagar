# This phase: reflect (self-improvement) after story {{REF}} — {{TITLE}}

One or more phases failed while running story {{REF}}. Your ONLY job is to turn those
failures into a durable lesson so future loop runs don't pay for them again.

The failure events (phase, attempt, error) are in the user message. Full session logs are
in `scripts/loop/logs/` if an error line needs context — read narrowly (tail the one log
that matters).

1. Read `scripts/loop/LEARNINGS.md` (it documents its own entry format).
2. Distill the failure(s) into **at most one entry** (merge multiple events with one root
   cause into one entry). If an existing entry already covers this failure class,
   **strengthen that entry** instead of appending a duplicate.
3. The **Rule for future runs** line must be actionable by a session (e.g. "run
   `vitest run`, not `vitest` in watch mode", "restage after the pre-commit hook rewrites
   files"), not a platitude ("be careful with tests").
4. Leave the file tidy: merge rather than append when a root cause repeats. (Size is also
   enforced mechanically — past `LOOP_LEARN_COMPACT_AT` lines the loop runs a dedicated
   compaction pass — but a tidy append beats compaction after the fact.)
5. Generalize: write the rule so it prevents the CLASS of failure, not just this instance.

Hard limits:

- **Touch ONLY `scripts/loop/LEARNINGS.md`.** No code changes, no story-file edits, no
  status changes, no commits — even if you spot the underlying bug, record it in the
  lesson; fixing it belongs to a human or the next story session.
- Do not remove or reword the file's header/format section.
- If the events are pure environment noise with nothing generalizable (e.g. a one-off
  network drop), it is valid to change nothing — say so.
