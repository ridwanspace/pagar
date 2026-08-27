# This phase: create-story for story {{REF}} — {{TITLE}}

Run the `/create-story` workflow for story {{REF}} exactly as the skill defines it
(target → analyze → write → self-check).

- Success for THIS phase = the dev story file exists at the mirrored
  `specs/implementation_artifacts/` path and passes the skill's self-check. The loop
  verifies with `python3 .claude/scripts/specs/specs.py story-info {{REF}} --json`
  (`devStoryExists` must be `true`).
- Do NOT implement the story. Writing code is the next phase's job, in a fresh session
  that will have ONLY the story file for context — which is exactly why it must be
  complete and self-contained.
