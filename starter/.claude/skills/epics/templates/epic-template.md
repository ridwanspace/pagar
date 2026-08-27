# Epic {{N}}: {{epic_title}}

**Status:** planned
**Requirements covered:** {{feature_codes}} <!-- F-* codes from the PRD feature catalog -->
**Related flows:** {{flow_refs}} <!-- e.g. FLOW 2, FLOW 3 -->
**Phase:** {{phase}} <!-- which delivery phase from the PRD's delivery plan -->

## Goal

{{epic_goal}}

<!-- One paragraph: what a user can accomplish once this epic ships. USER VALUE, not technical
     layers. -->

## Why this is one epic (cohesion)

{{cohesion_rationale}}

<!-- Why these features belong together: same domain, same core modules, or one user workflow.
     Each epic must be standalone and deliver complete value for its domain. -->

## Load-bearing invariants this epic must respect

<!-- Pull ONLY the locked decisions from the PRD that apply to these features, cited by their
     decision number. Illustrative examples of the KIND of invariant to look for:
     - Every mutation is idempotent: double-submits and re-uploads never double-count.
     - Money uses an exact decimal type, never a float; corrections are reversing entries.
     - Authorization is enforced server-side; sensitive actions require specific roles.
     Replace these with what THIS PRD actually declares. -->

{{invariants}}

## Stories

<!-- One file per story in this folder: story-NN-<slug>.md. List them here IN BUILD ORDER.
     Stories must NOT depend on FUTURE stories in the same epic. -->

| #       | Story             | File                     | Covers               |
| ------- | ----------------- | ------------------------ | -------------------- |
| {{N}}.1 | {{story_title_1}} | `story-01-{{slug_1}}.md` | {{story_features_1}} |
| {{N}}.2 | {{story_title_2}} | `story-02-{{slug_2}}.md` | {{story_features_2}} |

## Dependencies

**Depends on (must ship first):** {{epic_dependencies}} <!-- an earlier epic id, or "none" -->
**Enables:** {{enables}} <!-- which later epics build on this -->
