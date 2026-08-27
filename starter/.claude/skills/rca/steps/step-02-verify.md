# Step 02: Verify: is the claim true, and was it ever a requirement?

## Step goal

Answer **two independent questions from STATIC evidence**, then assign a **provisional
classification with citable evidence.**

- **QA mode:** (1) Is the reported behaviour **real**: does the code actually do this? (2) Is it
  **wrong**: does it contradict a stated requirement, or is it the intended design?
- **EXTERNAL-DOC mode:** (1) Is the claimed baseline **true**, or does the asked-for thing already
  exist? (2) Is the ask **correct**?

Steps 03 and 03b may change these. **Unprobeable claims survive on code evidence alone.**

## Mandatory rules

- 🛑 **Do NOT fix anything. Not even a one-liner. PROPOSE in the report; never apply.**
- 📌 **Every classification needs a CITATION. No citation means NEEDS-INFO.**
- 🧭 Read the PRD **by section**, never whole.
- 🔎 Orient with a search, then read **only what it points at.**
- ⚖️ **ABSENCE OF A THING IS NOT PROOF IT IS ABSENT.** **Before writing "this does not exist",
  search by at least THREE names: the surface path, the likely service function, and the domain
  noun. A capability can exist under a name the author never guessed**, and it can exist **in a
  legacy or reference tree WITHOUT existing in the live system, which is NOT "exists".**
- 🧱 **Verify on BOTH sides before classifying anything that crosses the wire.** A client symptom
  with a server cause, or the reverse, **is the common case, and the other side is one search
  away.**

## Sequence

### 0. Get the contract: it is generated from the code

Three ways, **cheapest first**, and **they are not equivalent**:

| Source | Staleness |
|---|---|
| **A. Derived in-process from the code** | **Can NEVER be stale relative to the code.** Prefer it. |
| **B. Served by the running system** | Reflects **whatever code that process is running.** |
| **C. The committed snapshot** | ⚠ **CAN BE STALE.** |

⚠ **Never dump the whole contract into context. Filter to the surface you are investigating.**

⚠ **In document mode, a mismatch between the document's quoted shape and the IN-PROCESS contract is
therefore NEVER "our spec is out of date". It is either the author reading an older deployment or
the stale snapshot, or a real difference. FIND OUT WHICH.**

### 1. Locate the implementing code: on both sides

### 2A. QA mode: check the behaviour against the code

Does the code path plausibly produce the reported behaviour?

⚠ **A forbidden result is a property of the CALLER until proven otherwise.**
⚠ **A blank page is a GATE until proven otherwise**: a route guard, a feature flag, an
authorization check.

⚠ **The silent-failure trap: a client sending one parameter name to a schema that declares another
fails SILENTLY into the server default. CHECK THE SCHEMA, NOT THE HANDLER.** The handler looks
perfectly correct while receiving nothing.

### 2B. EXTERNAL-DOC mode: check by claim type

**A BASELINE claim is verified in FOUR parts. All four must hold.**

1. **The surface exists.**
2. **The shape matches**: the fields and types the document describes.
3. **The behaviour matches.** ⚠ **"Returns a conflict if referenced" is a BEHAVIOURAL claim, not a
   route claim. Find the code that raises it, or the claim is wrong.**
4. **The stated semantics match.** ⚠ **The document may correctly name a surface and describe what
   it does INCORRECTLY.**

- **All four hold → BASELINE-CONFIRMED.**
- **Any one fails → BASELINE-WRONG**, and **say precisely WHICH of the four, and what the truth is.
  FLAG IT AS URGENT in your interim report.**

**For an ASK, judge it, not just its absence:**

| Check | If violated |
|---|---|
| Contradicts a locked decision | **ASK-CONFLICTS**. Escalate, do not silently build |
| Would force the client into a multi-call flow | **ASK-CONFLICTS**, one user action equals one call |
| Trusts client-supplied state, unbounded input, client-side secrets, or a client gate instead of server authorization | **ASK-CONFLICTS**, the security floor |
| Non-idempotent mutation, unpaginated list, a query in a loop, an outbound call with no timeout | **ASK-CONFLICTS**, **usually RESHAPEABLE, not a rejection** |
| Needs a schema change | Still **GAP-CONFIRMED**, but **never free**: it raises the effort floor |
| Needs a new interface surface | Still **GAP-CONFIRMED**, with the interface constraints noted |

**For a QUESTION: do the homework so the user decides INFORMED, then STOP.** What each option costs
**in this codebase**, and **your recommendation with a reason.** Classify **NEEDS-DECISION. Do NOT
answer it yourself.**

### 3. Check whether it was ever a requirement

⚠ **The PRD covers whatever feature area it was written for, not the whole product, and there may
be no PRD at all. SILENCE ON A DIFFERENT SUBSYSTEM IS NOT EVIDENCE THE ASK IS UNSPECIFIED. It means
the PRD is not the right authority. Say so rather than mass-classifying a batch as
MISSING-REQUIREMENT.**

### 4. Assign the provisional classification

```
- **Provisional class:** <CLASS>
- **Evidence:** <citation>, <what it proves>
- **Confidence:** high (proven from code/contract) | medium (strongly implied) | low (needs probe/repro)
- **Probe candidate:** yes|no  → step 03
- **Repro candidate:** yes|no  → step 03b
```

### 5. Mark the suspected ownership: do not conclude it yet

⚠ **Resist concluding ownership from ONE side alone.** If both sides are in this repository, **there
is no excuse for a guess.**

### 6. Batch efficiency

**Findings often share a root.** If three trace to one service function, one schema field, or one
component, **note the shared cause ONCE and cross-reference. This collapsing is ITSELF a finding,
and it changes how `/epics` sizes the work.**

## Step completion

Give the user a **compact interim read**: counts per class, and, **FIRST**: any
**BASELINE-WRONG**, any **ASK-CONFLICTS**, and any finding where you already **disagree with the
document's premise.**

Then load `steps/step-03-probe.md`.
