# Project

Always active. This is the orientation rule: what the project is, how to work in it, and which
other rule file covers what.

Replace every `{{PLACEHOLDER}}`. Delete what does not apply.

## What this is

{{ONE_PARAGRAPH: what the product does, in plain words a new engineer would understand on first
read. No marketing, no feature list.}}

Stack: {{LANGUAGES_AND_FRAMEWORKS}}
Package manager: {{PACKAGE_MANAGER}}
Test runner: {{TEST_RUNNER}}

## Who uses it

| User | What they want | What ruins their day |
| --- | --- | --- |
| {{USER_TYPE_1}} | {{THEIR_GOAL}} | {{THEIR_PAIN}} |
| {{USER_TYPE_2}} | {{THEIR_GOAL}} | {{THEIR_PAIN}} |

The last column tells you which bugs are expensive.

## How to work here

Five things, in priority order. When they conflict, the earlier one wins.

1. **Follow the spec, not your instinct.** If a story or an issue describes the work, implement
   exactly that. If the spec is wrong, say so and stop. Do not quietly implement something better.
2. **A test you have not seen fail is not evidence.** Write it, watch it go red, then make it
   green. Details in `20-testing.md`.
3. **Match the file you are in.** Existing patterns beat your preferences.
4. **Change the minimum.** Do not reorganize code you were not asked to touch.
5. **Verify before you claim.** Run the command. Show the output. "Should work" is not a result.

## Commands

```bash
{{INSTALL_COMMAND}}          # install dependencies
{{RUN_COMMAND}}              # run the app locally
{{TEST_COMMAND}}             # full test suite
{{TEST_SCOPED_COMMAND}}      # one test file, use this while working
{{LINT_COMMAND}}             # linter
{{TYPECHECK_COMMAND}}        # type checker
{{BUILD_COMMAND}}            # build
```

Scoped test while working. Full suite at the gate, before claiming done. A full suite on every
edit is slow enough that you will start skipping it.

## Locked decisions

Invariants, not defaults and not preferences. Later work is not allowed to weaken one. If a task
appears to require breaking one, stop and raise it. Do not implement it and mention the concern
afterward.

| ID | Decision | Why |
| --- | --- | --- |
| D1 | {{DECISION, e.g. "every list endpoint is paginated, no exceptions"}} | {{REASON}} |
| D2 | {{DECISION, e.g. "authorization is checked server side in the handler"}} | {{REASON}} |
| D3 | {{DECISION}} | {{REASON}} |

Keep this short. A table of thirty invariants is a table nobody reads.

## Vocabulary

Use these words in code, tests, and commit messages. When the spec says one word and the code
says another, every future reader pays a tax.

| Term | Means | Is not |
| --- | --- | --- |
| {{TERM_1}} | {{MEANING}} | {{COMMON_CONFUSION}} |
| {{TERM_2}} | {{MEANING}} | {{COMMON_CONFUSION}} |

## When to stop and ask

- The spec is ambiguous and both readings are defensible.
- The work needs a decision nobody has made, for example whether an admin sees another tenant's
  rows.
- A test fails for a reason unrelated to your change.
- You need a dependency, a schema change, or a credential you do not have.

One specific sentence beats a paragraph of hedging. "The story does not say whether an expired
token returns 401 or 403" is useful. "This needs more investigation" is not.

Do not guess and proceed. A wrong guess implemented confidently costs more to undo than a
question costs to ask.

## The other rules

| File | Covers |
| --- | --- |
| `10-structure.md` | Layout, layering, naming, imports, where a new thing goes. |
| `20-testing.md` | Red first, mutation verification, mocking traps, guards. |
| `30-security.md` | Server-side authorization, secrets, bounded input, fail closed. |
| `40-writing.md` | Prose style for commits, pull requests, comments, docs. |

Rules are always active, like system instructions. Workflows in `../workflows/` are saved prompts
you invoke on demand.
