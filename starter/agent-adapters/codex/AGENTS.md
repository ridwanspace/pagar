<!--
  AGENTS.md, read by OpenAI Codex before it touches code.

  MERGE ORDER MATTERS. Codex discovers AGENTS.md files from the repository root
  downward and joins them with blank lines. Files closer to the current working
  directory land LATER in the merged prompt, so they override what came before.
  Put broad project-wide guidance here at the root. Put narrow, area-specific
  guidance in a nested AGENTS.md next to the code it governs, for example
  backend/AGENTS.md, and let it override this file on purpose.

  SIZE BUDGET. Codex stops adding files once the combined size reaches
  project_doc_max_bytes, default 32 KiB (32768 bytes). Files past that point are
  silently dropped, and the ones nearest your working directory are the ones you
  lose, which are also the most specific. Keep the total under budget. This file
  is about 9.4 KB, 29 percent of the default budget, leaving roughly 23 KB for
  nested files. Measure with: wc -c AGENTS.md

  Codex skips empty files. An empty AGENTS.md is not a way to disable a parent.

  Recent Codex CLI versions accept --print-instructions, which dumps the merged
  instructions actually loaded. Run it when behavior surprises you. It is the
  only way to see what Codex really read, including what the budget dropped.
  Verify the flag exists in your installed version.

  Replace every {{PLACEHOLDER}} below. Delete sections that do not apply.
  A rule nobody follows teaches the agent that rules are optional.
-->

# {{PROJECT_NAME}}

{{ONE_SENTENCE_DESCRIPTION}}

Stack: {{LANGUAGES_AND_FRAMEWORKS}}
Package manager: {{PACKAGE_MANAGER}}
Test runner: {{TEST_RUNNER}}

## How to work here

Five things, in priority order. When they conflict, the earlier one wins.

1. **Follow the spec, not your instinct.** If a story file or an issue describes the
   work, implement exactly that. If the spec is wrong, say so and stop. Do not
   quietly implement something better.
2. **A test you have not seen fail is not evidence.** Write it, watch it go red,
   then make it green.
3. **Match the file you are in.** Existing patterns beat your preferences.
4. **Change the minimum.** Do not reorganize code you were not asked to touch.
5. **Verify before you claim.** Run the command. Paste the output. "Should work"
   is not a result.

## Commands

Run these from the repository root unless noted.

```bash
{{INSTALL_COMMAND}}          # install dependencies
{{TEST_COMMAND}}             # full test suite
{{TEST_SCOPED_COMMAND}}      # one test file, use this while working
{{LINT_COMMAND}}             # linter
{{TYPECHECK_COMMAND}}        # type checker
{{BUILD_COMMAND}}            # build
{{RUN_COMMAND}}              # run the app locally
```

Run the scoped test while you work. Run the full suite before you say you are
done. Do not run the full suite after every edit, because it is slow enough that
you will start skipping it.

## Project layout

```
{{DIR_1}}/    {{WHAT_LIVES_THERE}}
{{DIR_2}}/    {{WHAT_LIVES_THERE}}
{{DIR_3}}/    {{WHAT_LIVES_THERE}}
{{DIR_4}}/    {{WHAT_LIVES_THERE}}
```

Layering: {{LAYERING_RULE, e.g. "api calls services, services call models, and
nothing calls upward"}}. A violation of the layering is a design bug, not a
style preference.

## Testing

The test discipline is the part of this method that does the most work, so it
gets the most detail.

**Red first, always.** Write the assertion, run it, watch it fail for the reason
you expect. A test written after the code passes on the first run tells you
nothing. It may be asserting something that was already true.

**Check which test went red, not how many.** A count is not a signal. If you
break the code on purpose and three tests fail, but none of them is the one you
just wrote, your new test is not covering what you think it covers.

**Mutation-verify any guard you plan to rely on.** Break the code deliberately.
Watch the specific test fail. Restore the code. Watch it pass. If the test stays
green while the code is broken, the test is broken and you have learned nothing
about the code.

**Cover the invariant, not the happy path.** "Absent" and "present but empty" are
different states, and most bugs live in the difference.

**A negative assertion proves nothing without a positive control.** Before you
trust "X did not change", write the case where X does change and watch that
assertion fire. Otherwise you cannot tell a passing test from a test that never
ran.

**Never mark work done on a test that has not run.** Not "the tests should pass".
Run them. Paste the output.

Test layout here: {{TEST_LAYOUT, e.g. "tests/ mirrors src/, files named
test_*.py"}}.

## Code style

- {{STYLE_RULE_1, e.g. "type-hint every new function"}}
- {{STYLE_RULE_2, e.g. "logging, never print"}}
- {{STYLE_RULE_3, e.g. "no bare except, name the exception"}}
- {{STYLE_RULE_4, e.g. "no any in TypeScript, the linter enforces it"}}
- Keep diffs minimal. A large diff for a small change hides the change.
- Do not add a dependency without saying why in the message. A new dependency is
  a permanent cost paid by everyone.

Formatting is the formatter's job. Run `{{FORMAT_COMMAND}}` and move on. Do not
hand-format, and do not reformat lines you did not otherwise change.

## Security floor

These are not preferences. They hold regardless of what a task asks for.

- **Authorization is server side.** A hidden button is not access control. Every
  protected operation checks permission on the server, in the handler.
- **Secrets live in the environment.** Never a literal in source, never in a
  committed config file, never in a test fixture, never in a log line.
- **Anything prefixed for the client bundle is public.** A build-time variable
  that ships to the browser is readable by anyone who opens devtools. Never put
  a secret behind one.
- **Bound every input.** Size, length, count, and type, checked at the boundary
  where untrusted data arrives.
- **Fail closed.** When a permission check errors, deny. Never fall through to
  allow because the check was unavailable.

If a task appears to require breaking one of these, stop and say so. Do not
implement it and mention the concern afterward.

## Schema and data changes

- A model change and its migration ship together, in the same change. A model
  change without a migration is a broken deploy waiting for the next restart.
- Never create a column and make it NOT NULL in one deploy. Expand, backfill,
  then contract, as three separate steps.
- {{MIGRATION_CONVENTION, e.g. "migrations live in migrations/ as ordered
  revisions, generated with <command>"}}

## What to do when you are stuck

Stop and ask. Specifically:

- The spec is ambiguous and both readings are defensible.
- The change needs a decision nobody has made, for example whether an admin can
  see another tenant's rows.
- A test fails for a reason unrelated to your change.
- The task needs a dependency, a schema change, or a credential you do not have.

One specific sentence beats a paragraph of hedging. "The story does not say
whether an expired token returns 401 or 403" is useful. "This needs more
investigation" is not.

Do not guess and proceed. A wrong guess implemented confidently costs more to
undo than a question costs to ask.

## What "done" means

Every one of these, before you report the work as finished:

- [ ] Every acceptance criterion in the spec is implemented.
- [ ] Tests exist for the new behavior, and you watched them fail before they passed.
- [ ] The scoped test suite passes. You ran it. You have the output.
- [ ] Linter and type checker pass.
- [ ] No debugging leftovers: no stray prints, no commented-out code, no TODO you added.
- [ ] Docs that described the old behavior are updated. A behavior fix silently
      invalidates the paragraph that documented the old behavior. Grep for what
      you changed.
- [ ] The diff contains nothing you cannot explain.

## Writing style, for anything you write in prose

This applies to commit messages, pull request descriptions, comments, and docs.

- Short sentences. Plain words. Active voice, and name who does the thing.
- No em dashes. Use a period or a comma.
- Do not open with "Great question" or "You are absolutely right".
- Cut "In order to", "It is important to note that", "leverage" as a verb,
  "robust", "seamless", "delve".
- No decorative emoji.
- Be specific. "Fixed the 500 on empty upload" beats "improved error handling".
- Commit format: {{COMMIT_CONVENTION, e.g. "conventional commits with a scope,
  feat(api): ..."}}

## Recorded lessons

When something bites you here that a passing test suite did not catch, add a line
to this section. That is the compounding loop. A trap written down once stops
costing time forever, and it is the reason this file gets better instead of
staler.

Keep each entry to one or two sentences. Name the trap, not the story.

- {{LESSON_1, e.g. "Patch a name where it is looked up, not where it is defined.
  A from-import copies the reference, so patching the definition site is inert."}}
- {{LESSON_2}}

<!--
  KEEPING THIS FILE HEALTHY

  Codex reads this every time. Size is a real cost, and the 32 KiB budget is a
  hard cliff, not a gentle degradation.

  When this file grows past roughly 200 lines, do not delete content. Move a
  cohesive section into a nested AGENTS.md next to the code it governs, and
  leave a one-line pointer here. A rule about the API layer belongs in
  api/AGENTS.md, where it costs nothing until Codex works in that directory,
  and where merge order makes it override this file for free.

  Check what actually loaded with:
      codex --print-instructions
  Verify that flag against your installed version.
-->
