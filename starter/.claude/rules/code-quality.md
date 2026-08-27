---
description: Code style and quality conventions. What tooling is actually configured (be honest), follow-the-file discipline, error handling, logging, the traps that no linter catches
paths:
  - "{{SOURCE_ROOT}}/**"
  - "{{CLIENT_SOURCE_DIR}}/**"
---

# Code quality rules

## First: state honestly what is configured

Before any style rule, write down **what tooling actually exists**, verified and dated. The
three cases and what each means for the agent:

- **A formatter and linter are configured and enforced.** Name them and their exact commands.
  `{{LINT_COMMAND}}`, `{{FORMAT_COMMAND}}`, `{{TYPECHECK_COMMAND}}`. The agent runs them and
  trusts them.
- **Some are configured but not enforced in CI.** Say which. "It passed CI" then means
  "coverage was collected", not "the code is clean".
- **None are configured.** Say that plainly. **Then do not invent one.** Running a formatter
  over files you are editing rewrites hundreds of lines you do not own, buries the real diff,
  and collides with every open branch. The gates become: build or import check, plus scoped
  tests, plus the self-checks below.

The failure mode this section prevents is an agent inventing a gate that does not exist, then
reporting a green run of a command nobody configured.

## Follow the file you are in

Quote style, import grouping, indentation, line length, string formatting. **Match the
surrounding code, even where a generic guide would differ.**

- Keep diffs minimal. **Never reformat a whole file you did not otherwise change.**
- A rule in this document never outranks the neighbouring idiom in a file you are only touching
  lightly. Raise the mismatch, do not silently refactor.

## Rules that hold in any language

- **Type annotations on every new or changed signature**, in the project's modern syntax. Do
  not churn existing older-style annotations in code you are not otherwise touching. Even with
  no type checker configured, the annotations are for the reader and for whoever configures one
  later.
- **Structured logging, never a print statement** in committed library code. A module-level
  logger at the top of the file.
- **Never a silent catch.** Every handler logs with context and a traceback. An empty catch
  block converts a failure into a wrong answer, which is strictly worse.
- **Re-raise your framework's own HTTP or control-flow exceptions inside broad catch blocks**,
  or a deliberate not-found becomes a server error.
- **Null-check before attribute access**, at the point of access. Not three lines earlier with
  a different condition.
- **Beware types that subclass other types.** In several languages a boolean is a subclass of
  an integer. Any numeric type dispatch decides the boolean case **explicitly and first**, or
  `true` silently serializes as `1`.
- **A coercion or normalization helper must never raise.** On failure it returns the input
  unchanged. Null in, null out. Anything that post-processes data lives on this rule: a
  malformed item degrades to "passed through", never to a failed run.
- No unused imports or variables. Remove the computation, or use it.
- **Log identifiers and counts, never content.** User text, model output, and message bodies in
  logs are a data-leak surface that survives every later access-control fix.

## Schema and boundary idioms

Fill in your stack's version. The generalizable rules:

- Bound **every** client-controlled field with an explicit validator.
- **Separate request and response types per operation.** Never reuse a response type as a
  loader. They diverge the first time one side gains a computed field.
- Cross-field rules go in the schema's own validation hook, not in the handler.
- Field descriptions at API boundaries **feed the generated contract**, which makes them
  committed prose about behaviour. When behaviour changes, they change with it.
- Keep the schema layer free of data-model imports, so tests can pass simple stand-ins.

## Client-side rules

Fill in your stack's version. The generalizable ones:

- **No escape hatch from the type system** in committed code. If existing escape hatches exist,
  they are inherited debt, not a licence. Type the real shape, or use an unknown type with a
  narrowing guard.
- **No debug console output** in committed code. Warnings and errors for genuine diagnostics
  only, and never with a token or payload in the message.
- Match the file for import style and export style. In a codebase where both a path alias and
  relative imports exist, match the neighbour.
- Effects clean up. Memoization only where a dependency actually earns it.

## Both halves

- Comments explain **why**. The what is already in the code.
- Commit messages follow `{{COMMIT_CONVENTION}}`.
- **Committed prose carries its own reason, never a private spec id.** See
  `no-local-spec-refs.md`.
