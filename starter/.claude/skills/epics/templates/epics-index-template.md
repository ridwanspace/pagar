# {{project_name}}: Epic & Story Index

This is the index for the epic and story breakdown of {{project_name}}. It decomposes the
requirements in [`prd.md`](./prd.md), the feature catalog, the user flows, and the delivery
phases. Into implementable epics and stories.

**Layout:** one epic per subfolder (`epic-NN-<slug>/`), each holding an `epic.md` and one
`story-NN-<slug>.md` per story. Implementation status is mirrored in the status file. Keep it in
sync with `{{SPEC_HELPER_COMMAND}} sync-status`.

**Source of truth:** the PRD for requirements, the domain source(s) the PRD names. Business
rules and copy **verbatim** from there, the generated API contract, and the project stack
documentation. **Do not invent logic.**

## Epic list

<!-- One row per epic, in build order. Keep in sync with the folders. -->

| #   | Epic             | Folder                | Covers         | Phase       | Status  |
| --- | ---------------- | --------------------- | -------------- | ----------- | ------- |
| 1   | {{epic_title_1}} | `epic-01-{{slug_1}}/` | {{features_1}} | {{phase_1}} | planned |
| 2   | {{epic_title_2}} | `epic-02-{{slug_2}}/` | {{features_2}} | {{phase_2}} | planned |

## Requirement → epic coverage map

Generated and checked with `{{SPEC_HELPER_COMMAND}} coverage`. **Every feature in the PRD's
catalog must map to at least one epic.**

| Feature     | Epic(s)  | Notes    |
| ----------- | -------- | -------- |
| {{feature}} | {{epic}} | {{note}} |

**Coverage:** {{covered}}/{{total}} features mapped. **Uncovered:** {{uncovered}}.

⚠ A clean coverage number means **nothing declared is unmapped**. It does not mean the PRD asked
for the right things. See `rules/spec-pipeline.md`.

## Notes on phasing

Epics are sequenced to match the PRD's delivery plan. **Each epic is standalone**: it delivers
complete value for its domain and does not require a later epic to function.
