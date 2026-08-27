# Story 01: Publish a note

**Epic:** [epic.md](epic.md)
**Status:** done
**Feature IDs:** FR-01-01, FR-01-02, FR-01-03, FR-01-04

## Context an implementer needs

The domain rule lives in `src/notes.ts`, which imports no React (PRD D5). `publishNote`
takes a note and returns a new note. It never mutates.

`src/NotesPage.tsx` renders state and calls the domain. No rule lives in the component.

`publishNote` returns the SAME object when the note was already published (PRD D7), and
`publishInList` returns the SAME array in that case, so React can skip the re-render.
Two tests assert reference identity, and they will look strange until you know why.

## Acceptance criteria

| # | Given | When | Then |
| --- | --- | --- | --- |
| AC1 | an empty list | the user adds a note with a title and a body | it appears with status `draft` |
| AC2 | an empty list | the user adds a note with a blank title | an inline error, and no note is added |
| AC3 | a draft note with a non-empty body | the user clicks Publish | status becomes `published` and the timestamp renders |
| AC4 | a draft note with an empty or whitespace-only body | the user clicks Publish | an inline error, and the note stays a draft |
| AC5 | a note already published at T1 | the user clicks Publish again | still T1, no error banner |
| AC6 | a note published at T1 whose body was later blanked | publish is called again | still published at T1, no throw |
| AC7 | a list that does not contain the id | `publishInList` is called | it throws `NotFoundError` |
| AC8 | a note already published | `publishInList` is called for it | it returns the SAME array reference |

AC6 pins the ORDER of the two checks (PRD D4). AC8 pins the render-skip contract (D7).

## Tasks

- [x] Write `Note`, `ValidationError`, `NotFoundError` in `src/notes.ts`.
- [x] Write `createNote` with the title and body-length rules.
- [x] Write `publishNote` with the published check BEFORE the body check.
- [x] Write `publishInList` returning the same array when nothing changed.
- [x] Write the domain tests, and watch each one fail before writing the rule.
- [x] Write `NotesPage` and the component tests.
- [x] Add `tsconfig.tests.json` and wire it as its own gate.
- [x] Mutation-verify AC5: make publish re-stamp the timestamp, confirm red.
- [x] Add `gates.config.json` with both tsc gates, eslint, and vitest.

## Dev agent record

### Trap: `tsc --noEmit` never type-checked a single test file

This is the named one, and it is worse than it sounds because the gate looked green
the whole time.

Every React + TypeScript template ships a `tsconfig.app.json` that excludes test files.
It has a good reason: the shipped bundle must not depend on vitest globals. The
`type-check` script then runs `tsc --noEmit -p tsconfig.app.json` and reports success.

So the test files are checked by nothing. `tsc` skips them by configuration. vitest
transpiles them with esbuild, which strips types without checking them. A test can pass
the wrong number of arguments, call a method that does not exist, or assert against a
misspelled property, and the only signal is whether the assertion happens to still pass
at runtime.

Proven here rather than asserted. A deliberate type error was added inside
`src/__tests__/notes.test.ts`:

```ts
const holeProof: number = createNote("n1", "t", "b");   // Note is not a number
```

```
tsc -p tsconfig.app.json   ->  exit 0        (the hole)
tsc -p tsconfig.tests.json ->  exit 2        (the fix)
    error TS2322: Type 'Note' is not assignable to type 'number'.
```

The fix is `tsconfig.tests.json`: same `tsconfig.base.json`, but it INCLUDES the tests
and adds the vitest and jest-dom global types. It runs as its own gate,
`type-check-tests`, so deleting it is a visible change to `gates.config.json` rather
than a silent regression.

**Rule taken from this:** any config that excludes files from a checker creates a blind
spot. Find the blind spot and give it its own checker. Then prove the blind spot was
real by putting an error in it and watching the original checker stay green.

The moment it paid for itself: turning `type-check-tests` on immediately failed on
`vite.config.ts`, because `defineConfig` was imported from `vite` rather than
`vitest/config` and therefore had no `test` key in its type. That file had been wrong
since it was written and no gate had ever looked at it.

### Trap: a throw inside a React state updater escapes the try/catch around it

The first version of the publish handler read:

```tsx
try {
  setNotes((current) => publishInList(current, id, now));   // throws in here
  setError(null);
} catch (err) {
  if (err instanceof ValidationError) setError(err.message);
}
```

This looks correct and is not. React does not run the updater callback when
`setNotes` is called. It stores it and runs it later, during render, which is outside
this `try`. The `ValidationError` from a blank body therefore escaped the catch,
propagated out of render, and unmounted the tree. The AC4 test caught it:

```
ValidationError: cannot publish a note with an empty body
 ❯ publishNote src/notes.ts:83:11
 ❯ Module.publishInList src/notes.ts:100:19
 ❯ src/NotesPage.tsx:50:31
 ❯ basicStateReducer node_modules/react-dom/...
```

The stack is the tell: the frames below the throw are React internals, not the click
handler. That means the code ran during render, not during the event.

The fix computes the next value first, then calls the setter with a plain value:

```tsx
let next;
try {
  next = publishInList(notes, id, now);
} catch (err) { ... }
setNotes(next);
```

**Rule taken from this:** never put code that can throw inside a state updater
callback. The updater must be a pure transformation that cannot fail. Validation
belongs before the setter, where the surrounding try/catch actually applies.

### Mutation verification performed

Changed `publishNote` so the already-published branch returns a re-stamped copy:

```
Tests  4 failed | 14 passed (18)
  × publishNote > is idempotent and keeps the first timestamp
  × publishNote > keeps an already published note published even if the body was blanked
  × publishInList > returns the SAME array when the note was already published
  × NotesPage > keeps the first timestamp when publish is clicked twice
```

Reverted, 18 passed. The failures span the domain, the list helper, and the UI, which
is the coverage the three layers were supposed to give.
