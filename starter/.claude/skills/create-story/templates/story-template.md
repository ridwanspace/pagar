# Story {{epic_num}}.{{story_num}}: {{story_title}}

Status: in_progress <!-- set when this dev story is created; flip in the status file via the helper -->

> Dev-ready implementation story. **The developer, human or agent, may have ONLY this file.** It
> must be complete, precise, and grounded in cited sources.
> Planning source: `{{SPEC_DIR}}/plan_artifacts/{{epic_id}}/{{story_id}}.md`.

## Story

As a **{{role}}**, <!-- a role from the PRD's roles section -->
I want **{{action}}**,
so that **{{benefit}}**.

**Covers:** {{feature_codes}} · **Flows:** {{flow_refs}} · **Epic:** {{epic_id}}

## Acceptance criteria

<!-- Given/When/Then, each independently testable. Include edge cases, error paths, and any
     idempotency or authorization criteria the locked decisions imply. Tag each with the feature
     or flow it satisfies.

     EDGE-CASE BUDGET (rules/edge-cases.md): max 3 edge-case criteria, or 5 if this story touches
     money, authorization, or file upload. Each must trace to one of the five sources:
     boundaries / equivalence classes / stack-forced error paths / state and concurrency /
     domain. Over 5 means the story is too big. Split it. Happy-path and locked-decision
     criteria do not count against the cap.

     ⚠ Criterion numbers live HERE and stop here. This file is git-excluded, so `AC3` and
     `story 1.2` must NEVER appear in the committed code, docstrings, test names, or commit
     message the developer produces. Write the REASON the criterion encodes instead.
     See rules/no-local-spec-refs.md. -->

1. **AC1**: **Given** … **When** … **Then** … **And** …
2. **AC2**: …

**Edge-case sources used:** {{which of the five}} · **Skipped:** {{which, and why, in one line}}

## Dev guardrails (invariants this story MUST hold)

<!-- Pull ONLY the locked decisions that apply to THIS story; make each concrete and cite the PRD
     section. The lines below are EXAMPLES of what a PRD might lock. Replace them with the
     project's actual decisions and delete what does not apply. -->

- **Idempotency:** {{key}}. Enforced at the storage layer with a unique constraint, not only by
  a cache. A double-submit, retry, or re-upload must not double-count.
  [Source: prd §{{n}} / D{{n}}]
- **Authorization (server-side):** {{the exact check on the route, and who may perform this
  action per the PRD's roles section}}. **The client-side gate is UX, never the only gate.**
  [Source: prd §{{n}}]
- **Money:** an exact decimal type, never a float. Ledgers append-only, corrections are reversing
  entries. [Source: prd §{{n}} / D{{n}}]
- **Audit log:** write an audit row. Actor, action, entity, before and after.
  [Source: prd §{{n}} / D{{n}}]
- **Regression invariant:** {{any domain identity the PRD declares must keep holding}}.
  [Source: prd §{{n}}]
- **Copy:** {{the PRD's copy-language decision. Reuse exact strings from the flow}}.
  [Source: prd §{{n}} / D{{n}}]

## Architecture & stack guidance

<!-- The patterns the developer MUST follow, with cited sources. Be concrete. Fold in any
     applicable hazard from the shipped-story scan, citing its source story. -->

- **Which half owns what:** {{server-only | client-only | vertical slice. List the files per
  half}}.
- **Data model:** the tables or models this story creates or alters, **only what it needs**,
  **plus the migration file** with idempotent guards. [Source: prd §{{n}}; project memory file]
- **Transport and service:** the route location and shape, the boundary schema on the request and
  the response, the logic in the service layer, **static paths declared before parameterized
  ones**, the background job and its queue if the work is long, and **registration in the
  composition root**. [Source: rules/api-design.md]
- **Client:** the page or component placement, the service function on the shared client, the
  design-system components and tokens, the feature flag, and the route registration. **API shapes
  quoted from the generated contract.** [Source: rules/…; the contract file]
- **Integrations used:** {{integration, exact pattern, environment variables, mandatory flags}}.
- **Domain formulas and rules (verbatim):** {{quote, do not paraphrase}}.
  [Source: the domain source the PRD names]
- **Lists:** **if this story exposes a LIST of rows, the endpoint MUST support pagination plus
  filtering and sorting through validated query parameters, never an unbounded "return
  everything", and the client MUST use the shared pagination component, never a bare loop.**
  [Source: rules/backend-practices.md]
- **Hazards carried forward:** {{trap + which shipped story taught it + how this story avoids
  it}}, or "hazard scan: N stories reviewed, none applicable because …".

## Files to create / modify

<!-- Be explicit. For UPDATE files, you MUST have read them completely in step 02. -->

| Path       | NEW / UPDATE | What & why  | Must preserve                      |
| ---------- | ------------ | ----------- | ---------------------------------- |
| `{{path}}` | UPDATE       | {{change}}  | {{existing behavior not to break}} |
| `{{path}}` | NEW          | {{purpose}} |, |

## Tasks / subtasks

<!-- Ordered, each tied to a criterion. Sized for a single session. No forward dependencies. -->

- [ ] Task 1 (AC: 1), {{…}}
  - [ ] {{subtask}}
- [ ] Task 2 (AC: 2), {{…}}
- [ ] Tests: {{cases including the applicable invariants, e.g. idempotency and authorization}}

## Testing

- **How to run:** `{{TEST_COMMAND_SCOPED}}`. [Source: rules/testing.md]
- **Must-cover:** the happy path, each acceptance criterion, error paths, **and every applicable
  locked-decision invariant**, a double-submit for idempotency, in-scope and out-of-scope callers
  for authorization, and any declared regression invariant.

## Previous-story carry-over

<!-- Patterns, files, and gotchas from the previous story's dev file. Or "first story in epic."
     ALSO fold in any "Inherited from" block on the planning story: ground truth fed forward by
     /code-review. Real schema and columns, helper signatures, proven patterns, constraints.
     TREAT INHERITED FACTS AS AUTHORITATIVE. Cite the source dev story. -->

{{carry_over}}

## References

<!-- Every technical claim above must trace to a source. -->

- [Source: the planning story path]. Planning story
- [Source: prd §<section>], …
- [Source: rules/<topic>.md | the API contract], …
- [Source: the domain source the PRD names, with its path], …

## Open questions

<!-- Genuine forks are RESOLVED before the story ships and folded into the body above. A developer
     may have ONLY this file, so no real decision is left posed as a question. This section ends
     with "All resolved, none remain open" plus a one-line recap of each decision. -->

{{open_questions}}

## Definition of done

- [ ] All acceptance criteria pass, with tests.
- [ ] Applicable locked-decision invariants verified.
- [ ] Gates green: `{{TEST_COMMAND_SCOPED}}` · `{{BUILD_OR_IMPORT_CHECK}}` · `{{LINT_COMMAND}}` ·
      `{{TYPECHECK_COMMAND}}`.
- [ ] Schema change ships with its migration file, **or "no schema change"**.
- [ ] **System still works end to end**: the preserved behaviours in the files-to-modify table
      are intact.
- [ ] No private spec ids in any committed line. [rules/no-local-spec-refs.md]
- [ ] Status set to done in the status mirror.

## Dev agent record

<!-- ⚠ THIS SECTION IS THE FUEL FOR THE LESSONS LOOP. What gets written here is what the NEXT
     story's hazard scan reads. Record the traps a green test suite did NOT catch. Do not
     sanitize them into blandness. -->

### Agent model used

### Debug log references

### Completion notes

### File list
