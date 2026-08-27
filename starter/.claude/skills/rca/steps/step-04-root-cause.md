# Step 04: Root cause, ask-shaping & ownership

## Step goal

- **QA mode:** **the actual cause**, and **which part of the system owns the fix.**
- **EXTERNAL-DOC mode:** **what building it actually touches**, and, where the ask is mis-shaped,
  **the shape that would work.**

Both end with an **effort size, a blocked-by flag, and a test hook.**

## Mandatory rules

- 📌 **Ownership must be CITED, not smelled.** "Unknown, pending the other side" is a **to-do
  inside this step, never a terminal label.**
- 🛑 **Still no fixes. Propose; never apply.**
- 🎯 **Stop at the deepest cause you can PROVE. Label the rest as INFERRED.**

## Sequence: QA mode: trace to the deepest provable cause

**Write the cause as ONE SENTENCE NAMING THE MECHANISM, not the symptom.**

- ❌ "The list comes back empty."
- ✅ "The client sends one parameter name while the boundary schema declares another, so the value
  is dropped and the server default applies."

⚠ **A cause you SUSPECT but cannot prove is a HYPOTHESIS WITH A NAMED NEXT CHECK.** Write it that
way.

**Recurring root causes worth checking explicitly**: cheap to confirm and commonly missed:

- **Field or parameter drift across the wire**, where one side's name does not match the other's.
- **The model does not match the deployed database**: an unapplied migration.
- **Background-job routing mismatch**, where the routing configuration is duplicated and the two
  copies disagree.
- **Timezone-naive and timezone-aware values mixed.**
- **A non-idempotent mutation under a retrying client.**
- **A query inside a loop** for anything reported as "slow".
- **"Flag or guard, not bug"**: a feature flag or a route guard producing what looks like a
  missing feature.
- **The wrong system behind the client**: a build-time-baked base URL.

## Sequence: EXTERNAL-DOC mode: size the build and shape the ask

### 1. For each GAP-CONFIRMED: what does building it actually touch?

### 2. For each ASK-CONFLICTS: write the shape that would work

**⚠ THIS IS THE HIGHEST-LEVERAGE OUTPUT OF DOCUMENT MODE. NEVER STOP AT "we cannot do it as
asked".**

```
- **Asked for:** <what the document requested>
- **Conflicts with:** <the specific locked decision, platform rule, or security floor>
- **Why it matters here:** <THE CONCRETE FAILURE THE RULE PREVENTS, not "policy">
- **Shape that works:** <the alternative that meets the underlying need>
- **What the requester must change:** <on their side>
```

**Two archetypes cover most of them:**

- **A multi-call flow.** One user action equals one call is non-negotiable: **one surface absorbs
  the orchestration, WHICH USUALLY MAKES THE CLIENT'S LIFE EASIER, not harder.** Say that.
- **Client-supplied trust**: a status, a computed total, or a permission asserted by the client.
  **DERIVE IT SERVER-SIDE.**

⚠ **If the need genuinely cannot be met without weakening a locked decision, that is a
NEEDS-DECISION for the user, NOT a unilateral rejection.**

### 3. Decide ownership: the decision table

| Situation | Ownership |
|---|---|
| The server contradicts its own contract, or the capability is absent server-side | **server** |
| The server matches the contract; the client sends the wrong parameter or misreads the response (**cited**) | **client** |
| Needs both | **BOTH**, **and say which lands FIRST** |
| Each side behaves per its own reading of the contract, and **the readings disagree** | **CONTRACT-MISMATCH**, **reconciling the contract IS the work** |
| One side read, the other not | **UNKNOWN-PENDING-OTHER-SIDE** → **do section 4 NOW** |

### 4. Read the other side before claiming

⚠ **Diffing the committed contract snapshot against the in-process one shows EXACTLY what a stale
contract PROMISED versus what the system SERVES, the single most common source of a contract
mismatch. CITE THE SPECIFIC FIELD.**

### 5. Size the work

- **Files to change.**
- **Effort:** `trivial` (under an hour, one file) · `small` (a few files, no new patterns) ·
  `medium` (a new surface, service, table, or screen, **or a migration**) · `large` (a new
  subsystem, or it needs a PRD).
- **Migration?** ⚠ **A "yes" RAISES THE FLOOR.**
- **Blast radius**: **other callers of the service function, other consumers of the component.
  CHECK BEFORE CHANGING A SHARED ONE.**
- **Blocked by?** ⚠ **An item blocked by a decision CANNOT BECOME A STORY YET.**
- **Test hook**: **the check that would have caught this, and that proves the fix.**

### 6. Collapse shared causes

**One story covers three items when they share a root. Conversely, SPLIT a single document item
that is really two independent changes.**

Then load `steps/step-04b-audit.md`.
