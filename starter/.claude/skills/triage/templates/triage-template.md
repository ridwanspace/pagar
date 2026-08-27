# TRIAGE-NN: <batch title>

> **Status:** <in progress | complete | awaiting decision>
> **Date:** <YYYY-MM-DD>
> **Source:** <who reported it and where>
> **Environment:** <which>, <version / date if known>
> **Checkout position:** <synced with the default branch | N commits behind (sync declined, a caveat on every verdict below)>
> **Branch:** <current branch>

## Summary

| # | Issue | Disposition | Surface | Next |
|---|---|---|---|---|
| 1 | <short title> | ALREADY-SOLVED |, | reply to reporter |
| 2 | <short title> | NOT-A-BUG |, | reply with citation |
| 3 | <short title> | STRAIGHTFORWARD | <which> | fixed here |
| 4 | <short title> | NEEDS-DECISION | <which> | ask <decider>. Draft below |
| 5 | <short title> | NEEDS-RCA | <which / unclear> | → /rca |
| 6 | <short title> | NEEDS-INFO |, | question drafted |

**<N> issues → <X> closed, <Y> fixed here, <Z> awaiting a decision, <W> to investigation.**

## Already-solved checks (step 02)

- **Default branch:** <0 behind | N behind; commits touching reported surfaces: hash + subject>
- **Teammate branches:** <none | branch → owner → what it covers → pending merge>
- **Prior investigations:** <none | id → what it covered → its classification>
- **Prior triage:** <none | id → disposition → status (fixed at hash / awaiting decision since date / question unanswered)>

---

## Issue 1: <title>

- **Raw report (verbatim):** "<exactly what was written>"
- **Surface:** <route / component AND/OR endpoint / job>
- **Observed:** <as reported>
- **Expected (per reporter):** <or "(not stated)">
- **Evidence:** <image N: what it shows / request id / status code / none>
- **Account / role:** <if known>

**Disposition:** <one of the six> · **Surface:** <which, or ", ">

**Reasoning:** <one short paragraph. What settled it>

**Citation:** <file:line | contract path and field | locked-decision id | commit hash | branch | prior report id>

<!-- STRAIGHTFORWARD only: -->
**Fix brief**
- **Surface:** <which>
- **Root cause (proven):** <file:line or contract quote>
- **Fix:** <the change>
- **Blast radius:** <files touched; what consumes them>
- **Test:** <test extended or added>
- **Verification:** <visual pass / real request / test / combination>
- **Applied:** <yes, files changed | no, deferred, why>

<!-- NEEDS-DECISION only: -->
**Decision brief**
- **The open question:** <one sentence>
- **Why it's open:** <PRD silent / no validator / the reporter's requirement does not resolve here, with citations>
- **Precedents:** <2-3 comparable surfaces, file:line, and the rule each uses, note if they DISAGREE and on what axis>
- **Recommendation:** <the specific rule, and where it lives>
- **Why:** <2-4 sentences, grounded>
- **Runner-up:** <alternative + why not>
- **Deviates from the reporter's ask:** <how | nowhere>
- **Decider:** <who>
- **Cost if approved:** <one-line fix brief>
- **Status:** <awaiting answer | approved as recommended | approved with changes: <what> | deferred>

<!-- NEEDS-RCA only: -->
**Cause certainty:** <proven | inferred> · **Suspected ownership:** <which | unclear>
**Why not inline:** <which of the four certainty checks it failed>

<!-- NEEDS-INFO only: -->
**Question for the reporter:** <the one specific thing needed>

---

## Investigation handoff

<!-- Omit this section entirely if nothing routed to /rca. -->

- **Environment:** <which, version/date>
- **Checkout position:** <synced | N behind (sync declined)> <+ note if triage fixes changed the tree>
- **Issues:** <normalized issue blocks, renumbered contiguously>
- **Already ruled out:** <what step 02 killed, and why. Do NOT re-check these>
- **Findings so far:** <per issue: verdict, citation, cause certainty>
- **Suspected ownership:** <per issue>
- **Prior report to extend:** <id | none>

## Replies to send

<!-- Drafted for the user to send. NEVER sent from here. -->

**To <reporter / channel>:**

> <one grouped message covering every closed issue: what is already fixed and whether it is live on
> the environment they test or waiting on a promotion, what is working as designed and why, and
> what is still needed to proceed>

**To <decider>. Decision ask:**

> <the finding, why it is a decision and not a fix, your recommendation plus grounding, where it
> deviates from the reporter's ask, and the unblock line>

## Outcome

- **Fixed here:** <issues + files touched, or "none">
- **Gates:** <honest, including pre-existing baseline noise>
- **Wire / visual verification:** <both directions checked, or what was not>
- **Awaiting a decision:** <issues + decider + when asked, or "none">
- **Handed to investigation:** <issues, or "none">
- **Awaiting reply:** <issues, or "none">
- **Committed:** <hash + subject | not yet. Commit offered>
