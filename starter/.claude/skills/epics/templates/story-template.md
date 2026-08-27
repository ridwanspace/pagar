# Story {{N}}.{{M}}: {{story_title}}

**Status:** planned
**Epic:** epic-{{NN}}-{{epic_slug}}
**Covers:** {{feature_codes}} <!-- F-* codes this story implements -->
**Related:** {{related_refs}} <!-- flow / decision / module cross-references from the PRD -->

## User story

As a **{{user_role}}**, <!-- a role the PRD defines in its roles section -->
I want **{{capability}}**,
so that **{{value}}**.

## Context & source of truth

{{context}}

<!-- Where this lives in the PRD (link the section). If the PRD names a domain source of truth,
     its business rules, formulas, and user-facing copy carry over VERBATIM. Quote, do not
     invent. Name the real code surfaces this touches on every half: the transport module and
     route, the service function, the data model change PLUS its migration file, the boundary
     schema, a background job if async; the client page or component, the client service call,
     and any feature flag. -->

## Acceptance criteria

<!-- Given/When/Then. Each criterion independently testable. Include edge cases, error paths,
     idempotency, and authorization. Reference the feature or flow it satisfies.

     EDGE-CASE BUDGET (see rules/edge-cases.md): max 3 edge-case criteria, or 5 if this story
     touches money, authorization, or file upload. Each traces to one of five sources:
     boundaries / equivalence classes / stack-forced error paths / state and concurrency /
     domain. Over 5 means the story is too big. Split it. Happy-path and locked-decision
     criteria are exempt from the cap. -->

**AC1**
**Given** {{precondition}}
**When** {{action}}
**Then** {{expected_outcome}}
**And** {{additional}}

**AC2**
**Given** {{precondition}}
**When** {{action}}
**Then** {{expected_outcome}}

## Invariants & guards (must hold)

<!-- ONLY the locked decisions from the PRD that apply, made specific to this story.
     Illustrative examples of the KIND of guard:
     - Idempotent: a double-submit or re-upload never double-counts (a content hash or client
       nonce plus a unique constraint).
     - Authorization checked SERVER-SIDE on the route; a client-side permission or flag gate is
       UX only, never the sole gate.
     - Money uses an exact decimal type; corrections are reversing entries, not destructive
       edits.
     - An audit trail is written where the PRD requires one: actor, action, before and after. -->

{{invariants}}

## Data & schema touched

{{schema}}

<!-- Tables created or altered, only what THIS story needs, never all tables upfront. EVERY
     model change ships with its migration file. Quote API shapes from the generated contract. -->

## Out of scope

{{out_of_scope}} <!-- Explicitly what this story does NOT do, often handled by a sibling story. -->

## Definition of done

- [ ] Acceptance criteria pass, with tests added.
- [ ] Invariants and guards verified (idempotency, authorization, and the locked decisions that
      apply).
- [ ] Gates green: `{{TEST_COMMAND_SCOPED}}`, `{{BUILD_OR_IMPORT_CHECK}}`,
      `{{LINT_COMMAND}}`, `{{TYPECHECK_COMMAND}}`.
- [ ] Status updated in the status mirror.
