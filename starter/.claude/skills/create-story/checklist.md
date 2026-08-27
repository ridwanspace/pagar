# Dev story quality checklist (adversarial)

Review the dev story as an **independent validator who did not write it**. Your job is to find
what is missing or wrong **before** a developer implements it. **The developer may have ONLY
this file. Assume something is missing; prove the story complete, do not assume it.**

## Mistakes to hunt for

- **Reinventing wheels.** Does the story point the developer at **existing code, patterns, and
  previous-story work to extend**, instead of rebuilding? Check the carry-over and
  files-to-modify sections.
- **Wrong library or pattern.** Does it use the project's **locked stack** and the exact
  documented patterns? A story that reaches for a library the project does not use is a defect
  even if the library is better.
- **Wrong half or wrong file location.** Does the story say **which half owns each change**, and
  do NEW files sit in the right place per the project structure?
- **Schema change without a migration file.** If a data-model change is in scope, does the story
  **require a matching migration**? **A model-only change is a 🚨 defect**, because automatic
  table creation only covers a fresh database and will not alter an existing table.
- **Someone else already on it.** Was the overlap check run over the files-to-modify list, and is
  any overlap recorded with the branch and the author?
- **Breaking regressions.** For every UPDATE file, is "must preserve" filled **from the real
  file's behaviour**? **Will the system still work end to end, not just pass the criteria?**
- **Missing invariant.** Is every *applicable* locked decision present **AND correct**? Check
  each against what the PRD actually specifies for **this story's** mutation: the idempotency key
  matches the one the PRD specifies · server-side authorization with the right role rule · the
  data-integrity decisions · the audit write · any declared regression invariant not endangered ·
  the copy-language decision honored.
- **Missing abuse guard.** If the story adds or touches an upload endpoint, a model-calling
  surface, a credential or authentication endpoint, an email-triggering flow, or **any
  unauthenticated mutation**: do the criteria and the testing section enforce the security floor
, server-side authorization, bounded inputs, secrets from the environment only, nothing secret
  in a client-public variable? **⚠ If the project has no rate limiter, that is a decision to
  raise, not a helper to assume. A story that lets the client drive an expensive surface unbounded
  is a 🚨 defect, not an enhancement.**
- **A list without list affordances.** If the story exposes a LIST of rows, a catalog, a
  history, a picker, then: **server side**, pagination plus filtering and sorting through
  validated query parameters, **never an unbounded "return everything"**; **client side**, the
  project's shared pagination component, **never a bare loop over everything.**
- **Vague tasks.** Is each task concrete, tied to a criterion, sized for one session, with **no
  forward dependency**?
- **Uncited or wrong claims.** Does every technical instruction trace to a real source?
  **Spot-check a formula and a copy string VERBATIM.**
- **Edge-case budget blown.** Are there more than 3 edge-case criteria (5 for money,
  authorization, or upload)? **Over the cap is a SIZE SIGNAL: the story should be split.** Is
  each one traced to one of the five sources, with the skipped sources named?
- **Fake-done risk.** Are the criteria testable, and does the testing section require coverage for
  **every applicable invariant**?
- **Unresolved open forks.** Does the open-questions section list any **genuine fork** the
  implementing developer would otherwise have to decide? **A story is not ready while a real
  choice is still posed as a question.**
- **Readability for the implementing agent.** Is it scannable and unambiguous, free of
  token-wasting filler, with the critical signals not buried?

## Output

Group findings by severity and present for selection (`all / critical / select / none`):

- **🚨 Critical (must fix):** anything that would cause wrong, broken, incomplete, or
  non-building implementation, or a violated invariant.
- **⚡ Enhancements (should add):** guidance that materially improves correctness or speed.
- **✨ Optional:** minor clarity or efficiency.

Apply accepted fixes **directly and naturally**, with no "added during review" annotations. When
running autonomously, apply all Critical automatically and list the rest as suggestions.

## Pass bar

The story passes when **a developer with only this file could implement correctly without
re-deriving anything**: clear criteria, correct cited patterns, every applicable invariant present
and accurate, a complete files-to-modify list with preserved behaviours, concrete tasks, and
tests that prevent fake-done, **with no leftover placeholders and no open forks.**
