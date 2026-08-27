# RCA-NN: <title>

> **Mode:** <QA | EXTERNAL-DOC>
> **Source:** <who wrote it, and where>
> **Environment:** <which>, <version / date>
> **Checkout:** <synced with the default branch | N behind (sync declined, a caveat on every classification)>
> **Triage:** <TRIAGE-NN handoff | none. Direct entry>
> **Investigated:** <YYYY-MM-DD>
> **Input document:** <path or link | n/a>
> **Scope (EXTERNAL-DOC):** sections <ids>. N of M
> **Not processed this run:** <which sections, and why: not requested / already processed by RCA-NN / deferred>

## 1. Decisions needed from a human

*Ordered by urgency, not by finding number. If this section is empty, write "none".*

### ⚠ Urgent: someone is acting on this now

<!-- Wrong baselines go here. FIRST, ALWAYS. -->

### Decisions blocking work

<!-- Per item:
     - **Options:** A … / B …
     - **Cost in this codebase:** …
     - **Recommendation:** … because … -->

### Escalations: contradicts a locked decision

### Back to the reporter

### A teammate is already on it

## 2. Summary

<!-- QA mode -->

| # | Finding | Class | Owner | Effort | Root cause (one line) |
|---|---|---|---|---|---|

<!-- EXTERNAL-DOC mode -->

| # | Item | Type | Class | Owner | Effort | Verdict (one line) |
|---|---|---|---|---|---|---|

**Counts:** <per class>
**By owner:** <per surface>
**Grouped:** <findings sharing one root cause>
**Audit (04b):** <the reported-versus-actual count line, if the audit found siblings>

## 3. Findings

### Finding N: <title>

- **Claim type** *(EXTERNAL-DOC)*: <BASELINE | ASK | QUESTION>
- **Raw text (verbatim):** "<exactly what was written>"
- **Stated priority / phase:** <or "(not stated)">
- **Surface:** <where>

**Class:** <…> · **Owner:** <…> · **Confidence:** <high | medium | low>

**Evidence (proved):**
<!-- file:line · contract path → field, with a provenance tag: in-process | live | snapshot@<hash>
     · PRD section or locked-decision id -->

**Inferred (not proved):**
<!-- What you believe but could not demonstrate, AND THE CHECK THAT WOULD SETTLE IT. -->

**Probe** *(step 03, if run)*
- Harness: … · Account: … · Called: … · Result: <CONFIRMED | CONTRADICTED | BLOCKED>

**Reproduction** *(step 03b, if run)*
- Client → which system: … · Account: … · Attempted: … · Result: <REPRODUCED | NOT-REPRODUCED | BLOCKED>
- Artifacts: <screenshot · console · network>

**Root cause** *(QA)* / **Build surface** *(EXTERNAL-DOC)*
- <ONE sentence naming the MECHANISM>
- Layers touched: … · Migration required: <yes | no>

**Shape that works** *(ASK-CONFLICTS only)*
- Asked for: … · Conflicts with: … · **Why it matters here:** <the concrete failure the rule
  prevents, NOT "policy"> · Proposed instead: … · Requester-side impact: …

**Fix-site audit** *(step 04b. Required for code-modifying findings; else state why skipped)*
- **Fix site:** `<file>::<function>`
- **Paths enumerated:** <N>
- **Root-cause shape:** <the testable predicate>

| # | Sibling defect | On the default branch | Fixed in flight? | Severity | Fix now / defer |
|---|---|---|---|---|---|

- **⚠ Regressions the naive fix would introduce:** <each one is a MANDATORY GUARDRAIL in the story>
- **Verified empirically:** <what you ran, and the observed output>
- **Not audited:** <what you deliberately left out of scope>

**Sizing:**
- Files: … · Effort: <trivial | small | medium | large> · Blast radius: … · Blocked by: …
- **Test hook (→ a story acceptance criterion):** <one per sibling defect>

## 3b. Shared root cause *(when the audit found siblings)*

- **Cause:** <one sentence>
- **The shape that fixes all of them:** <THE STRUCTURAL CHANGE, not a per-defect patch list>

## 4. /epics handoff block

```markdown
<!-- Copy-paste ready. Only findings with REAL WORK enter. -->

### Handoff: RCA-NN

- **<title>** · Owner: <…> · Touches: <files> · Migration: <yes|no>
  Constraint: <…> · AC hint: <…> · Effort: <…> · Blocked by: <… | none>

**Grouped:** <items sharing one root cause, one story>

**Excluded (do NOT create stories):**
- <item>, <reason: already exists / works as designed / blocked on a decision / baseline was wrong>
```

## 5. Answer-back / reply block

```markdown
<!-- EXTERNAL-DOC mode: always. Paste-ready. Collaboration, not correction. -->

**Already built, available today:** …
**Corrections to the "current state" section:** …
**Your open questions:** …
**Reshaped asks:** …
**Accepted as-is, queued:** …
```

**Delivery:** <kept in this report only | handed to the user to send>

## 6. Method & limits

- **Contract source:** <in-process | live | snapshot> + date, + whether the snapshot matched
- **Which system the client talked to during reproduction:** …
- **Not verified:** <the honest list>
- **Stale-tree caveat:** <if the checkout was behind>
- **Teammate work in flight:** <branches touching these surfaces>

## Revision history

| Date | Change |
| ---- | ------ |
