# Step 2: Requirements: roles, features, flows, locked decisions

## Step goal

Turn the approved vision into a concrete, ID-structured requirement set. Users and roles,
`F-*` features, `FLOW n` flows, and the `D-number` **locked-decision table**: and get the
user's approval **before drafting**.

## Mandatory rules (read first)

- 🛑 NEVER write the PRD in this step. Structuring and proposing only.
- 📖 Read this entire step file before acting.
- 🎯 **The ID conventions are load-bearing.** The helper parses them out of the finished PRD.
  Features `F-[A-Z][A-Z0-9-]*[A-Z0-9]` (digits allowed after the first letter, must start and
  end on a letter or digit). Flows `FLOW 1`, `FLOW 2`. Decisions `D1`, `D2`. Modules `M1`, `M2`,
  optional suffix.
- 📋 You **propose** a requirement set from the discovery summary. The **user** decides what is
  in, out, and locked. **Every locked decision must be theirs or explicitly ratified by them.**
- 📄 **Document mode:** propose the set **from the document's outline**. Tag every item
  `[doc §x]` (derived from the document) or `[proposed]` (your addition). If the document uses
  its own ids, keep them in the entry's text as a cross-reference: the `F-*` code is the
  pipeline's key, the team's id is the team's key, **both appear**.
- 🚫 No invented domain logic. Ground feature behaviour in the declared sources of truth or the
  user's answers.

## Sequence

### 1. Users and roles

Propose the user and role list implied by discovery. **If the codebase already has roles, start
from those** unless the document redefines them. For each role: one line on what it can do, and
note the authorization question you will lock as a decision, who can see and do what, and
whether ownership is per-tenant, per-resource, or per-role.

### 2. Feature list (`F-*` codes)

Propose the feature catalog. Each entry:

- **`F-CODE`**: short name, one line on what it is and why it earns a place in this version.
- Codes are short, mnemonic, and stable. One code per feature. **Never reuse a code.**

Aim for the **smallest honest set** that covers the approved scope. Mark anything you are
unsure belongs with `(proposed. Confirm)`.

**⚠ The two features every catalog forgets. Propose them explicitly, then let the user decide.**

Feature catalogs get written by asking "what can the user *do*?", which reliably produces domain
verbs and reliably **omits the application's own surface and its accessibility**. Both then
vanish from the coverage check, not because they were declined, but because **nobody ever gave
them a code**. A run can report 100% coverage with an incoherent, keyboard-unusable product.

- **`F-UI` (or your name for it), the application's own interface craft.** The shell every
  authenticated page renders inside, navigation, user menu, theme, plus the reusable
  component vocabulary: page headers, empty states, status badges, alerts, loading skeletons,
  form patterns, **that feature stories compose instead of re-inventing per screen.**
  - **Do not confuse this with output theming.** Exported document templates are a *different*
    feature on a *different* surface. Both can exist. Conflating them is exactly how the
    application's own interface ends up owned by nobody.
  - Skipping it is legitimate for work that touches no screens, but it must be **a stated
    decision, not an oversight**.
- **`F-A11Y` (or folded into `F-UI`). Accessibility as a verified state.** A non-functional
  line saying "WCAG 2.1 AA" is **a standard, not a deliverable**: it says what must be true,
  and never who makes it true or when it gets checked. If the user wants conformance rather
  than aspiration, **it needs an owning feature.**

Propose both with a one-line rationale. **Record a decline as an explicit deferral** so the
coverage map stays honest.

### 3. Core flows (`FLOW n`)

Propose the handful of end-to-end flows that exercise the features. Each flow gets a name, the
actor, a 3-to-7-step happy-path sketch, and the `F-*` codes it exercises.

**Every feature should be reachable from at least one flow. Flag any orphan.** In document
mode, a flow the document already narrates is **quoted step for step, not rewritten**.

### 4. Key decisions to LOCK (the D-table)

Propose the numbered decision table. These are **the invariants every downstream story will
protect**. Walk the user through each. **They lock it, you record it.**

Cover at least:

- **Stack.** If this is an existing codebase, the stack is **locked by reality**, not by choice.
  Capture it as a decision, and capture any deviation as its own row.
- **Data invariants.** The ones this product needs. Offer examples and lock only what applies:
  idempotent mutations, an exact decimal type for money and never a float, soft delete, an
  append-only log, an identity or total that must always hold.
- **Copy language**, if the user-facing copy is in a language other than the PRD's.
- **Authorization model**: roles, tenancy, and who can do what, from section 1.
- **Interface standard.** If a design system exists, lock **how binding it is**: composition
  first, tokens only with no hardcoded values, the accessibility floor, and the part that decays
  without it, that **the application's own interface craft is a deliverable owned by a story,
  not a by-product of feature work.** A guideline nothing schedules is a document, not a
  standard.
- **Anything discovery surfaced as "this must not change"**: a formula from a source of truth,
  a compliance rule, a deadline-driven scope cut, a decision the input document states as
  settled.

Number them `D1`, `D2`, in the order agreed. Each row: id, decision in one dense line, rationale
in fewer words.

### 5. Module map (`M-*` codes): optional

If the product naturally splits into modules, propose a short map assigning each `F-*` to one.
Modules tend to map onto service or domain boundaries. **Skip it if it adds nothing**, say so,
and let the user confirm skipping.

### 6. Present the requirement set for approval

Display the full set compactly. Roles, feature list, flows, decision table, module map or
"skipped", with `[doc §]` / `[proposed]` tags in document mode. Then:

> **Menu:**
>
> - **[A] Approved**: draft the PRD from this set.
> - **[R] Revise**: tell me what to add, drop, merge, or re-lock.
> - **[D] Discuss**: talk through a specific feature or decision before locking.

**Halt and wait for the user's choice.**

#### Menu handling

- IF A: proceed to section 7.
- IF R: apply the changes. **Renumber cleanly, nothing is published yet, so renumbering is
  still safe HERE, and only here.** Re-present, re-show the menu.
- IF D: discuss, update the set, re-show the menu.
- IF anything else: clarify, then re-show the menu.

### 7. Route

Once approved, note "Requirement set approved" and carry it forward **verbatim**. The draft may
reword prose but **must not add, drop, or renumber IDs.**

Then read fully and follow `step-03-draft.md`.

## Success / failure

✅ **Success:** roles defined. Every feature has a valid, unique code. The interface-craft and
accessibility features proposed and decided, accepted or explicitly deferred. Flows reference
features with no orphans. The decision table locked **by the user**, covering stack, invariants,
copy language, authorization, and the interface standard. In document mode every item traceable
to the document or marked proposed. The user explicitly approved the whole set.

❌ **Failure:** drafting the PRD here. Malformed ids the helper cannot parse. **Decisions locked
by you instead of the user.** Features with no flow. **Silently omitting the application's own
interface and accessibility from the catalog.** Proceeding without approval.

**Master rule:** The requirement set is the contract for the draft. IDs are frozen at approval,
the draft renders them, it does not renegotiate them.
