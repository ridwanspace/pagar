# Definition of done: dev-story

A story is **done** only when EVERY item below holds. **No lying, no partial credit.**

## Implementation completeness

- [ ] Every task and subtask is checked **and genuinely implemented**, not aspirational.
- [ ] EVERY acceptance criterion is satisfied. **Quantitative thresholds enforced explicitly.**
- [ ] Only work mapped to a task was implemented. **No scope creep, no freelancing.**
- [ ] Edge cases and error paths the story specified are handled.
- [ ] **No new dependency added beyond the story without user approval.**

## Invariants: the story's guardrails, those that apply

The guardrails come from the PRD's locked decisions. **The story's list is the authority.** Each
applicable one must **hold AND be tested**. Examples of the shape these take:

- [ ] **Idempotency** holds and is tested. A double-submit, re-upload, or retry cannot
      double-apply. The key matches what the PRD specifies.
- [ ] **Authorization** enforced **server-side on the route**, not only by a client gate. Role
      gating as the PRD names it. **Tested both in and out of scope.**
- [ ] **Data integrity** decisions honored: the exact decimal type for money, soft delete, and any
      declared identity still holding.
- [ ] **Copy** follows the PRD's copy-language decision, with quoted strings carried **verbatim**
      from the source of truth.
- [ ] **Every OTHER guardrail the story lists** is verified the same way. **None skipped, none
      silently weakened.**

## Tests & quality gates

- [ ] Unit tests for all core logic introduced or changed. Integration tests where the story
      requires them.
- [ ] Tests cover the criteria **and the invariant cases above**, written first, red-green-refactor.
- [ ] `{{TEST_COMMAND_SCOPED}}` green, with **no NEW failures against the recorded baseline**.
- [ ] `{{BUILD_OR_IMPORT_CHECK}}` green. **A module nothing registers is a shipped bug every other
      gate misses.**
- [ ] `{{LINT_COMMAND}}` and `{{TYPECHECK_COMMAND}}` green, where they exist. **Where they do not,
      the self-checks in step 03 stand in. Do not invent a gate.**
- [ ] **Schema change → its migration file is present next to the model change, is idempotent, and
      was applied locally with the scoped tests re-run against the real table.**
- [ ] Any deliberately-duplicated configuration is still identical in both of its homes.
- [ ] **System works end to end.** The behaviours listed in "must preserve" are intact.
- [ ] **No private spec ids** in any committed line. [rules/no-local-spec-refs.md]

## Documents in sync: both trees

- [ ] **Dev story:** status done. File list complete, with repository-relative paths. **Dev agent
      record has completion notes INCLUDING any trap the green suite did not catch**, which feeds
      the lessons mining. Only permitted sections modified.
- [ ] **Status mirror:** this story is done, set via the helper.
- [ ] **Planning story:** implementation notes appended **IF** implementation drifted from the
      plan. Otherwise untouched. **Committed team documents are NOT written from here.**
- [ ] **PRD or epic conflicts:** any contradiction is **FLAGGED to the user** with a recommended
      tool, and recorded. **Never silently coded around.**
- [ ] **Index:** status synced, and the index tables updated if they drifted from reality.

## Output

```
Definition of Done: PASS | FAIL
Story: <ref>, <title>
Score: <n>/<total> items
Gates: tests {pass/fail} · build {pass/fail} · lint {pass/fail/n-a} · types {pass/fail/n-a} · migration {present/n-a}
Docs: dev-story · status mirror · plan writeback · index
```

**FAIL** → list each failing item plus the required action, and return to the relevant step. **Do
not mark done.**
**PASS** → the story is implemented, verified, and the spec in both trees reflects reality.
