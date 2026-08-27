# PRD quality standards

The PRD is the **single source of truth** for the product being built. Everything downstream,
the epic and story breakdown, story creation, implementation, and review. Decomposes from it.

This file defines what "good" looks like. Internalize it before drafting, reviewing, or editing.

---

## What a PRD is for in this pipeline

A dual-audience document serving:

1. **Human stakeholders**: the owner or sponsor, and the engineers doing the build. It carries
   the vision, the locked decisions, and the rules learned the expensive way.
2. **The pipeline**: it feeds the epic breakdown, the data model, and the delivery plan.
   Sections are numbered and ids are machine-parseable for extraction.

The helper parses requirement ids directly out of the PRD. **The ID conventions are therefore
load-bearing:**

- **Features:** `F-[A-Z][A-Z0-9-]*[A-Z0-9]`: digits allowed after the first letter, must start
  and end on a letter or digit. The primary requirement units.
- **Flows:** `FLOW 1`, `FLOW 2`.
- **Locked decisions:** `D1`, `D2`, in the key-decisions table.
- **Module codes:** `M1`, `M2`, optionally suffixed.

**Never reuse or silently renumber an ID.** A retired feature keeps its code, marked as removed.
A new one gets a fresh code.

---

## Core philosophy: information density

**High signal-to-noise. Every sentence carries weight.**

Anti-patterns to eliminate:

- ❌ "The system will allow users to…" → ✅ "Users can…"
- ❌ "It is important to note that…" → ✅ state the fact directly
- ❌ "In order to…" → ✅ "To…"
- ❌ Conversational filler and hedging → ✅ direct, concise statements

**Goal: maximum information per word, zero fluff.**

---

## What makes a great requirement

### Capabilities, not implementation leakage, with one deliberate exception

Naming technologies in requirements is normally leakage. **But when the stack is locked as a
decision, it is correct to name it where a requirement depends on it.** In an existing
codebase, the stack is locked by reality rather than by choice. Capture it as decisions, and
capture any deviation as its own decision row.

- ✅ Name a locked-stack element where a decision depends on it.
- ❌ Invent *new* implementation detail that is not a locked decision and is not grounded in a
  declared source of truth. Do not add libraries, table designs, or flows nobody decided on.

### Measurable and testable

- ✅ "A user can complete checkout on a phone in under 60 seconds."
- ✅ An invariant stated as a checkable fact: "every mutation is idempotent", "ledger totals
  balance to zero".
- ❌ Subjective adjectives: "easy", "intuitive", "fast", "user-friendly". Replace with a metric
  or a concrete capability.
- ❌ Vague quantifiers: "multiple", "several", "various". Use exact counts or enumerations.

### Faithful to the declared sources of truth

If the PRD declares domain sources of truth, an input requirements document, a legacy system, a
spreadsheet, an API contract, existing code, **their business rules, formulas, and copy carry
over verbatim. Quote, do not invent.**

If a proposed edit would contradict a declared source, **stop and flag it. Do not silently
diverge.**

Team ids a source document carries are kept as cross-references inside the feature entry. The
`F-*` code is the pipeline's key. The team's id is the team's key.

---

## Locked decisions are invariants

The key-decisions table is **the PRD's spine**. Each numbered row records a decision the project
committed to: stack choices, data invariants, copy-language conventions, the authorization
model.

**Every downstream story protects these. Never weaken, delete, or contradict one without the
user explicitly deciding to, and when they do, trace the ripple effects.**

---

## Traceability

The chain the PRD must keep intact:

```
Overview & goals → Locked decisions → Users & roles → Features → Flows → Data model → NFRs
```

When one link changes, check the others:

- A new or changed **decision** may ripple into roles, features, the data model, and NFRs.
- A new **feature** usually needs a flow reference, possibly a data-model entry, and a module
  placement.
- A **flow** must reference the features it exercises.
- Every feature code appears in **exactly one** entry, and every entry has at least an
  acceptance sketch.

---

## Checklist for any draft or edit

- ✅ **Density**: no filler, every sentence carries weight.
- ✅ **Measurable**: concrete criteria, no subjective adjectives.
- ✅ **Faithful**: grounded in declared sources of truth, no invented domain logic.
- ✅ **Invariants intact**: no locked decision quietly eroded.
- ✅ **IDs consistent**: unique, machine-parseable, cross-references valid.
- ✅ **Structure preserved**: section numbering stable, no YAML frontmatter.
- ✅ **Traceable**: downstream sections updated when an upstream one changes.
- ✅ **Surgical** (edits). Minimal diff, existing content not accidentally dropped.

---

**Remember:** the PRD is the contract `/epics` decomposes. The default posture is
**conservative**: add what the user decides, state it densely and testably, and never quietly
erode an invariant or the faithful mapping to a declared source of truth.
