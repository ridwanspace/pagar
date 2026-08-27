# Step 03: Validate (tests, gates, criteria, invariants)

## Step goal

**Prove** the implementation is correct and complete. Tests green, quality gates pass, every
criterion satisfied, every applicable invariant verified, **before** finalizing.

## Mandatory rules

- 🧪 **No lying.** This is where you confirm the story is *actually* done. **Fix failures here.
  Do not defer them.**
- 🛡️ **Invariants are part of "done", not optional.**
- 📖 Read this whole step before acting.

## Sequence

### 1. Run the scoped gates for each half the story touched

```bash
{{TEST_COMMAND_SCOPED}}     # every test covering the modules the story's file list touches
{{BUILD_OR_IMPORT_CHECK}}   # catches a broken registration or a circular import
{{LINT_COMMAND}}
{{TYPECHECK_COMMAND}}
```

- **ALL scoped tests must pass. New and pre-existing.** Compare against the recorded baseline.
  **Only NEW failures are yours.**
- **A pre-existing test now failing means you introduced a regression. Fix it before
  continuing**, and confirm you preserved the behaviours the story's "must preserve" column
  listed.
- ⚠ If CI runs only on pull or merge requests, **this local pass is the first signal anyone
  gets.**

### 2. Run the quality self-checks

**If your project has no linter or type checker configured, do not invent one.** Self-check the
rules instead: typed signatures on new code, structured logging instead of print statements, no
silent catch blocks, schema validation on every boundary, static routes before parameterized
ones, an authorization check on every mutating route, and **any deliberately-duplicated
configuration still identical in both of its homes.**

**Schema change?** Confirm the migration file exists, **is idempotent**, and matches the model
edit. Then **apply it to your local data store and re-run the scoped tests.** ⚠ **A green
in-memory test suite proves nothing about the real table.**

**Sweep for leaked private spec ids** over this story's **file list only**:

```bash
grep -nE '[Ss]tory [0-9]+\.[0-9]|\bAC[0-9]{1,2}\b|[Ee]pic [0-9]|RCA-[0-9]|TRIAGE-[0-9]|\.claude/' <file-list>
```

Every hit in a docstring, comment, or test name **is a defect**: rewrite it to state the **reason**
the criterion encoded, or cite a commit hash, a file path, or the API contract. **The team's own
requirement vocabulary is NOT a defect. Leave it.** Pre-existing hits on lines this story did not
touch are out of scope.

**Touched the API surface?** Regenerate the committed contract and **check the diff is exactly
your story**: `{{API_CONTRACT_REGEN_COMMAND}}`. **A field you renamed in a schema shows up here.
Hand-checking field names in prose is how a wrong field name survives review.**

### 3. Verify every acceptance criterion

Go through the criteria **one by one** and confirm each is satisfied by the implementation **and**
covered by a test. **Enforce any quantitative threshold explicitly.** If a criterion is not met,
**it is not done**: return to step 02 for the gap.

### 4. Verify the invariants

For each item in the story's guardrails, confirm it **holds AND is tested**. The guardrails come
from the PRD's locked decisions and **are the authority for this check. Honor each one even if no
criterion restates it.** Typical shapes:

- **Idempotency**: a double-submit, re-upload, or retry does not double-apply, with a test, and
  the key matches what the PRD specifies.
- **Authorization**: enforced **server-side on the route**, not only by a client gate. Sensitive
  actions gated to the roles the PRD names. **Tests cover both in-scope and out-of-scope
  callers.**
- **Data integrity**: the exact decimal type for money, soft delete, or any declared identity
  still holding after the change.
- **Copy**: user-facing strings follow the PRD's copy-language decision, verbatim from the flow
  where quoted.

**If a guardrail cannot hold as written, that is a spec conflict: a HALT trigger, not a thing to
quietly relax.**

### 5. Confirm honest completion

- Every task is checked and **genuinely done**, with tests that exist and pass.
- **The file list includes every new, modified, and deleted file.**
- **The dev agent record has implementation notes, including any trap the green suite would not
  have caught.** These feed the lessons mining later.
- Only permitted dev-story sections were modified.

If any check fails and you can fix it, fix it, looping back to step 02 as needed. If you cannot
fix it, stop and **report precisely.**

### 6. Route

When tests, gates, all criteria, and all invariants pass, read fully and follow
`steps/step-04-finalize.md`.

## Success / failure

✅ **Success:** scoped tests, build check, lint, and type check all green, **with no new failures
against the baseline**. Migration file present for any schema change **and applied locally**.
Every criterion met and tested. Every applicable invariant verified and tested. No regressions.
File list and agent record complete.

❌ **Failure:** skipping the scoped gates. **Ignoring a NEW failing test.** An unmet criterion or
an untested invariant. **A model change with no migration file.** Inventing a gate that does not
exist instead of self-checking. **Declaring done with red gates.**

**Master rule:** "Done" means the suite is green, the gates pass, and every criterion and
invariant is provably satisfied. Verified, not assumed.
