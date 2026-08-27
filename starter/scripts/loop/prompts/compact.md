# This phase: compact LEARNINGS.md (housekeeping)

`scripts/loop/LEARNINGS.md` has crossed its size threshold (the exact numbers are in the
user message). Your ONLY job is to shrink it below the threshold **without losing
prevention power** — the last lines of this file are injected into every loop session, so
it must stay dense signal, not an archive.

1. Read the whole file.
2. Compact, in this order of preference:
   - **Merge** entries that share a root cause into one entry.
   - **Generalize** several narrow old entries into one class-level rule ("any watch-mode
     tool blocks headless runs", not three entries about vitest/a dev server/a REPL).
   - **Trim** entry bodies to their load-bearing lines — the _Rule for future runs_ line
     is the part that must survive; symptom/cause lines may be shortened.
3. Never remove the file's header/format section. Never drop a rule that still prevents
   a plausible failure — generalize it instead. Keep newest entries most specific (they
   sit in the injected tail).
4. Keep the entry format intact and entries ordered oldest → newest.

Hard limits: touch ONLY `scripts/loop/LEARNINGS.md`; no commits, no other files.
