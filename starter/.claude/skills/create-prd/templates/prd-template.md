# PRD: {Product Name}

<!-- Plain markdown, no YAML frontmatter. Keep section numbering stable: downstream tooling and
     skills reference section numbers. Delete all template comments from the final document. -->

## 1. Overview & goals

<!-- 2 to 4 dense paragraphs: what this is, for whom, the problem it solves, and what "done"
     means. State goals measurably where possible, not as aspirations. -->

{Product statement.}

**Goals:**

- {Measurable goal 1}
- {Measurable goal 2}

## 2. Key decisions (locked)

<!-- The spine of the PRD. Every downstream story protects these. IDs are D1, D2, …, never
     reuse or renumber. Cover: stack, data invariants, copy language, authorization model, and
     anything that "must not change". -->

| ID  | Decision | Rationale |
| --- | -------- | --------- |
| D1  | {e.g. the existing stack, locked by reality: name the real frameworks, data store, migration mechanism, and background-job system} | {why} |
| D2  | {e.g. all mutations are idempotent} | {why} |
| D3  | {…} | {…} |

## 3. Users & roles / authorization

<!-- Who uses this, what each role can do, and the authorization model. Reference the decision
     that locks it. A small can-do matrix beats prose. -->

| Role   | Can do         | Cannot do    |
| ------ | -------------- | ------------ |
| {role} | {capabilities} | {exclusions} |

## 4. Scope & non-goals

**In scope (this version):** {summary, the feature list in §6 is the authoritative
enumeration.}

**Non-goals:**

- {Explicitly out of scope, so nobody builds it by accident}

## 5. Domain sources of truth

<!-- If an existing system, spreadsheet, API contract, or codebase defines the domain, name it
     here with its location. Its business rules, formulas, and copy carry over VERBATIM,
     downstream skills quote it, never invent. If this PRD was created from an input document,
     that document is the FIRST entry, cited by path and heading. If greenfield, say so
     explicitly. -->

- {Source}, {location}, {what carries over verbatim}
- *Or:* Greenfield, the decisions in this document are the domain source.

## 6. Features

<!-- The primary requirement units. One entry per feature. Codes match
     F-[A-Z][A-Z0-9-]*[A-Z0-9]; each code appears in EXACTLY ONE entry, the helper parses this
     section. -->

### F-{CODE}: {Feature name}

- **What:** {capability, stated as "Users can…" or "The system …". Dense, concrete}
- **Why:** {tie to a §1 goal or a §5 source}
- **Acceptance sketch:**
  - {Testable statement}
  - {Testable statement}

### F-{CODE}: {…}

…

## 7. Core flows

<!-- End-to-end journeys exercising the features. IDs: FLOW 1, FLOW 2, … Every flow lists the
     feature codes it exercises; every feature should appear in at least one flow. -->

### FLOW 1: {Flow name}

- **Actor:** {role}
- **Features:** F-{CODE}, F-{CODE}
- **Steps:**
  1. {step}
  2. {step}
- **Key edge cases:** {branches worth naming, or "none"}

### FLOW 2: {…}

…

## 8. Data model sketch

<!-- Entities, key fields, relationships. A sketch to plan from, the real data models, boundary
     schemas, and migration files become the code-level source of truth. Honor the §2 data
     invariants here. -->

- **{entity}**: {key fields; relations}
- **{entity}**: {…}

## 9. Non-functional requirements

<!-- Only NFRs actually decided or constrained. Every line measurable, no "fast", no
     "user-friendly". -->

- {e.g. 95th-percentile endpoint latency under N ms on target hardware}
- {e.g. every endpoint appears in the generated API contract with typed request and response
  schemas}
- {e.g. accessibility: keyboard-navigable, labeled controls. Owned by a §6 feature, not only
  stated here}

## 10. Open questions

<!-- Deliberately unresolved items, so /epics and the stories do not silently guess. Remove
     entries as they are decided; promote them to §2 if they become locked decisions. -->

- {Question}, {owner / when it must be answered}

## Appendix A: Module map

<!-- Optional. Codes M1, M2, … (suffix allowed). Assign every feature to a module. Modules map
     naturally onto service or domain boundaries. Delete this appendix if unused. -->

| Module | Name     | Features           |
| ------ | -------- | ------------------ |
| M1     | {module} | F-{CODE}, F-{CODE} |

## Revision history

<!-- One row per editing session. Real dates only. -->

| Date   | Author   | Change summary                       |
| ------ | -------- | ------------------------------------ |
| {date} | {author} | Initial PRD created via /create-prd. |
