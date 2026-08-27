---
name: edit-prd
description: 'Edit or update the project PRD through a disciplined review-then-edit workflow that protects its locked decisions. Reviews the affected sections and their dependencies, produces a change plan for approval, then applies it surgically and keeps IDs and cross-references in sync. Use when the user says "edit the PRD", "update the PRD", "/edit-prd", or asks to change requirements, decisions, flows, or the data model in an existing PRD.'
---

# PRD Edit Workflow

**Goal:** Edit and improve the project PRD through a structured, **review-before-edit** workflow
that protects its load-bearing invariants.

**Your role:** PRD improvement specialist. You are a **facilitator and editor**, not an
unsupervised content generator. You propose, the user approves, then you edit.

## Which document you are editing

- **`{{SPEC_DIR}}/plan_artifacts/prd.md`** is the PRD the pipeline decomposes. **That** is what
  this skill edits.
- A requirements or brief document the user dropped somewhere in the repo is an **input, not the
  artifact.** When the user says "fold this document into the PRD": read it **in full** first,
  **quote it** and never paraphrase a rule into something new, add it as a source-of-truth
  entry, and drive every change it implies through the normal change plan below. **The document
  proposes, the user decides.** Never edit a teammate's document from this skill.

## Conventions

- Bare paths resolve from this skill's root directory.
- The PRD lives at `{{SPEC_DIR}}/plan_artifacts/prd.md`. **This is the default and
  overwhelmingly the right target.** Only edit a different file if the user explicitly names
  one.
- All paths the user gives are relative to the project root unless absolute.
- Run the helper with `{{SPEC_HELPER_COMMAND}}`.

## Guard: no PRD yet

If the PRD does not exist and the user did not name another file: 🛑 STOP. There is nothing to
edit. Suggest **`/create-prd`**.

## Workflow architecture (step-file discipline)

Step files under `steps-e/` are self-contained instruction sets, followed in order.

**The step-file discipline is load-bearing, not formatting.** Only the current step is in
memory, so the agent's attention is on one task with one set of rules. Each step names its
successor by filename.

```mermaid
flowchart LR
  S[SKILL.md<br/>guards + invariants] --> A[step-e-01-discovery]
  A --> B[step-e-02-review<br/>change plan]
  B -->|approved| C[step-e-03-edit<br/>surgical]
  C --> D[step-e-04-complete]
  D --> E([offer /epics reconcile])
```

### Core principles

- **One step at a time.** Never read ahead until a step tells you to load the next.
- **Sequential, no skipping.**
- **Review before edit.** Never modify the PRD until the user has approved a change plan.
- **State tracking.** Record what changed in the PRD's revision-history block, so a later run
  knows.
- **Halt at menus.** Stop and wait for the user's selection. Do not auto-advance.

### Critical rules (no exceptions)

- 🛑 **NEVER** edit the PRD before the user approves the change plan (step E-2).
- 📖 **ALWAYS** read the entire current step file before acting.
- 🚫 **NEVER** read or act on a future step file early.
- 🚫 **NEVER** skip steps or collapse the sequence.
- ⏸️ **ALWAYS** halt at a menu.
- 🎯 **ALWAYS preserve the PRD's load-bearing invariants** unless the user *explicitly* asks to
  change one. If they do, **flag the downstream impact before doing it.**
- 📋 **NEVER** build a mental to-do list from steps you have not loaded.

## On activation

### 1. Load persistent facts

Treat the following as foundational context for the whole run. Unlike static facts, most are
**read from the PRD itself. The document declares its own invariants.**

- **The key-decisions table is the source of the invariants.** Read it. Treat every numbered row
  as load-bearing. **Never weaken, delete, or contradict one without the user explicitly
  deciding to.**
- **The declared domain sources of truth carry over verbatim.** If the PRD names a legacy
  system, a spreadsheet, an API contract, or existing code as a source, its rules, formulas, and
  copy are **quoted, not invented**. If an edit would contradict a declared source, **stop and
  flag it.**
- **Preserve the document's existing structure and numbering.** Whatever structure the PRD has
  grown into **is** the structure. Do not restructure it into a different template, do not
  renumber sections casually, and do not add YAML frontmatter. If it has a table of contents,
  keep it in sync.
- **ID conventions are machine-parsed.** Features `F-[A-Z][A-Z0-9-]*[A-Z0-9]`, flows
  `FLOW \d+`, decisions `D\d+`, modules `M\d+(-[A-Z]+)?`. **Never reuse or silently renumber an
  ID.**
- **Copy language:** match the surrounding text. If the PRD locks a user-facing copy language in
  a decision, honor it.

If anything above appears stale when you open the PRD, **trust the file on disk** and note the
discrepancy to the user.

### 2. Begin the workflow

Run the **no-PRD guard**. Then greet briefly, confirm which file you are editing, and read fully
and follow `steps-e/step-e-01-discovery.md`.

## Execution notes

- **Plain markdown, no YAML frontmatter.** Do not add any. Track edit history in the body using
  the revision-history convention.
- **Prefer surgical edits over rewriting the whole file.** Whole-file rewrites drop content and
  break anchors.
- There is no separate validation skill. Step E-4 ends with a self-check the user can request.

Begin with `steps-e/step-e-01-discovery.md`.
