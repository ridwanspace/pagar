# This phase: code-review for story {{REF}} — {{TITLE}}

Run the `/code-review` workflow for story {{REF}} — all steps in order, each either done
or explicitly skipped with a one-line reason (skip the work, never the step).

Unattended adjustments (a human will review this run later):

- **Visual/UI verification:** if the story touched UI and an automated screenshot
  capability exists in this project, run it yourself, fix what the pixels reveal, and
  save the shots. You cannot obtain human sign-off — record
  `Visual sign-off: PENDING HUMAN REVIEW — see <shot paths>` in the dev story's
  Dev agent record instead. Never claim sign-off happened.
- **The remaining steps** (reality check, user docs, learning extraction, feed-forward,
  demo/seed sync, one pipeline improvement — "none this run" stays a valid outcome):
  run normally. Where a step would ask the user, decide and record per the three-tier
  rule above (recommended option by default; senior-engineer reasoning for hard calls;
  BLOCKED for irreversible ones).
- **The commit step:** do NOT commit — the loop's commit phase runs next. Do run
  `suggest-next` and put the suggested next story in your final message just above the
  LOOP_STATUS line.
