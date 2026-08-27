# Vite + React + TypeScript + vitest

A thin vertical slice: one domain object, one operation with a real rule, one edge case.
This is the example that carries the **type-check hole**, which is one of the method's
named traps. If you read only one section here, read that one.

## What this demonstrates

A meeting note has a title, a body, and a status. It can be created as a draft and
published. Publishing has three rules worth testing:

- **Happy path.** A draft with content becomes published and gets a timestamp.
- **Validation failure.** A blank or whitespace-only body cannot be published.
- **Idempotency edge case.** Publishing an already published note is not an error and
  does not move `publishedAt`.

The rules live in `src/notes.ts`, which imports no React. `src/NotesPage.tsx` renders and
holds no rule.

## Setup

Node 24 or newer.

```bash
cd examples/node-react
npm install
```

## Run

```bash
npm run type-check          # tsc on application sources
npm run type-check:tests    # tsc on test files, the hole fix
npm run lint                # eslint, warnings are failures
npm test                    # vitest
npm run dev                 # the app on :5173
```

Through the gate runner, which lives at `../../gates/`:

```bash
node ../../gates/run-gates.mjs
```

## The type-check hole

**Most React + TypeScript templates never type-check a single test file, and the gate
stays green the whole time.**

The mechanism has two halves that are each individually reasonable:

1. `tsconfig.app.json` **excludes** test files. It has a good reason: the shipped bundle
   must not depend on vitest globals. So `tsc --noEmit -p tsconfig.app.json` skips them.
2. vitest transpiles tests with esbuild, which **strips types without checking them**.

Nothing checks the tests. A test can pass the wrong number of arguments, call a method
that does not exist, or assert against a misspelled property, and the only signal is
whether the assertion happens to still pass at runtime.

This was proven here rather than asserted. A deliberate type error was placed inside
`src/__tests__/notes.test.ts`:

```ts
const holeProof: number = createNote("n1", "t", "b");   // Note is not a number
```

```
$ tsc --noEmit -p tsconfig.app.json
exit 0                                       <- the hole

$ tsc --noEmit -p tsconfig.tests.json
src/__tests__/notes.test.ts(33,7): error TS2322: Type 'Note' is not assignable to type 'number'.
exit 2                                       <- the fix
```

**The fix** is `tsconfig.tests.json`. It extends the same `tsconfig.base.json` so the two
checks cannot drift apart in strictness, but it INCLUDES the tests and adds the vitest and
jest-dom global types. It runs as its own gate, `type-check-tests`, so removing it is a
visible change to `gates.config.json` rather than a silent regression.

The config layout:

```
tsconfig.base.json    shared compiler options, the single source of strictness
tsconfig.app.json     extends base, includes src, EXCLUDES tests  -> ships
tsconfig.tests.json   extends base, includes tests + config files -> checks the rest
tsconfig.json         solution style, references both
```

**It paid for itself immediately.** Turning the gate on failed on the first run, and not
on a test file: `vite.config.ts` imported `defineConfig` from `vite` rather than
`vitest/config`, so the `test` block had no type and was an error. That file had been
wrong since it was written, and no gate had ever looked at it.

## What was actually run

Everything below was executed on this machine, Node 24.18.0, TypeScript 5.7, vitest 3.2.7,
eslint 9, vite 6.4.3.

```
$ tsc --noEmit -p tsconfig.app.json
exit 0

$ tsc --noEmit -p tsconfig.tests.json
exit 0

$ eslint . --max-warnings 0
exit 0

$ vitest run
 ✓ src/__tests__/notes.test.ts (13 tests) 10ms
 ✓ src/__tests__/NotesPage.test.tsx (5 tests) 451ms

 Test Files  2 passed (2)
      Tests  18 passed (18)
```

Both JSON reporters were checked against what the gate parsers expect:
`eslint --format json` emits the array, and `vitest run --reporter=json` parses to
`numTotalTests 18, numPassedTests 18, testResults 2`. The commands were also run bare
(`tsc`, `eslint`, `vitest`, no `npx`), which is the form in `gates.config.json`, because
the runner puts `node_modules/.bin` first on PATH.

**Two real bugs were found by these gates while writing this example**, which is why they
are worth the setup:

1. `vite.config.ts` imported `defineConfig` from the wrong package. Found by
   `type-check-tests`, invisible to `type-check`.
2. The publish handler wrapped `setNotes(updater)` in a `try/catch`. React defers the
   updater and runs it during render, outside the `try`, so the `ValidationError`
   escaped and unmounted the tree instead of showing a message. Found by the AC4
   component test.

An earlier `vitest` 2.1.x pin also produced a type conflict, because vitest 2 depends on
vite 5 while this project uses vite 6, so two copies of vite's types were installed.
Upgrading to vitest 3 left a single vite copy and resolved it.

**Mutation verification of the idempotency rule.** Changing `publishNote` so the
already-published branch returns a re-stamped copy:

```
Tests  4 failed | 14 passed (18)
  × publishNote > is idempotent and keeps the first timestamp
  × publishNote > keeps an already published note published even if the body was blanked
  × publishInList > returns the SAME array when the note was already published
  × NotesPage > keeps the first timestamp when publish is clicked twice
```

Reverted, 18 passed.

**Since run:** the gate runner, after it was finished. `node ../../gates/run-gates.mjs`
from this directory reports **4 PASS**, including the test-file type check. CI runs
the same thing on every push (Node 22, `npm ci`). At authoring time the runner was
still being built and only the commands inside the config had been run by hand.
`npm run dev` was also not run, since nothing here depends on the dev server.

## How the method shows up here

| Concept | Where it lives | What to look at |
| --- | --- | --- |
| **Spec-driven development** | `specs/` | `prd.md` has a locked-decisions table. D4 locks the ORDER of the two publish checks. D7 is React-specific: `publishNote` returns the SAME object when nothing changed, so React skips the re-render. That is why two tests assert reference identity. |
| **TDD** | `src/__tests__/notes.test.ts` | 13 fast domain tests with no DOM, 5 slower component tests that check wiring rather than rules. `is idempotent and keeps the first timestamp` hands the second call a different clock value so it can observe a re-stamp. |
| **Compound engineering** | `specs/epic-01-notes/story-01-publish-note.md`, section "Dev agent record" | Two real traps with their evidence: the tsconfig hole with the exact exit codes, and the React state-updater throw with the stack trace that identified it. |
| **Local CI enforcement** | `gates.config.json` | Four gates, and `type-check-tests` is a separate one on purpose. Each gate's `run` carries the flag its parser needs: `--format json` for eslint, `--reporter=json` for vitest. |

## Files

```
src/notes.ts                     domain rules, no React import
src/NotesPage.tsx                UI, no rules
src/__tests__/notes.test.ts      13 domain tests
src/__tests__/NotesPage.test.tsx 5 component tests
tsconfig.base.json               shared strictness
tsconfig.app.json                ships, excludes tests
tsconfig.tests.json              THE HOLE FIX
specs/                           prd.md, epic, one dev-ready story with the trap record
gates.config.json                tsc x2, eslint, vitest
```
