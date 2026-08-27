# This phase: dev-story for story {{REF}} — {{TITLE}}

Implement dev story {{REF}} by running the `/dev-story` workflow exactly as the skill
defines it (target → implement → validate → finalize).

- Success for THIS phase = every task in the story is done with green tests, the story's
  `## Dev agent record` and File list filled in, and the status ledger set to `done` for
  {{REF}}. The loop independently verifies `status == done` and re-runs the verification
  gates (typecheck, tests — whatever the project has configured) afterward — a story
  marked done with red tests or type errors fails the gate.
- **⚠ Run the verification gates yourself before marking the story done.** A test run
  does NOT type-check TypeScript (test runners transpile without checking), so a suite
  can be fully green and the commit still fail its pre-commit typecheck — and the commit
  phase cannot hand work back to you. When pagar gates exist, run
  `node gates/run-gates.mjs`; otherwise run the project's typecheck and test commands.
- Do NOT commit. The loop has a dedicated commit phase after code-review.
- If you must deviate from the story file, follow the skill's drift-writeback rules and
  log the deviation in the Dev agent record.
