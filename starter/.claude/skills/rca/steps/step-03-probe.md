# Step 03: Probe: exercise the running system, read-only

## Step goal

**A live observation, or a solid failure to observe, OUTRANKS ANY AMOUNT OF CODE REASONING**, and
it is what lets you hand `/epics` a finding that is **known** true.

**In EXTERNAL-DOC mode this step is unusually cheap and unusually valuable**: most baseline claims
are about read-only surfaces, **and a read costs nothing to check.**

## Mandatory rules

- 🔐 **READ-ONLY against anything shared.** Other people work there. **No "small exception".**
- 🔑 **Credentials from the environment only.** **Never inline a token, password, or key into a
  script, the report, or a message.**
- ⏱️ **Timebox.** Two or three honest attempts per finding.
- 🧹 Throwaway probe scripts go in the scratch directory, **not the repository.**
- 🚫 **No raw personal data or response bodies in the report.** **Reference a call by surface,
  status, and SHAPE, never by dumping a body.**

## The harness ladder: cheapest first

| Harness | Cost | Mutations? |
|---|---|---|
| **In-process test client** against the assembled system | none, no server at all | in-process only |
| **Your own local system** | start it | **allowed here** |
| **A shared deployed environment** | none | ⚠ **READS ONLY** |
| **A scoped test** | writes a test | yes, **and this is also the test hook the story will need** |

## Sequence

### 1. Decide whether this step runs at all

### 2. Probe in-process first

⚠ **An authentication rejection without credentials is ITSELF INFORMATIVE**: it proves the surface
exists and is guarded, **which settles most baseline route claims with no credential at all. Do NOT
treat an auth rejection as "surface missing".** A not-found is "missing". A wrong-method error is
"the path exists, the method does not".

### 3. ⚠ The account trap: for anything authorization-flavoured

**WHICH ACCOUNT YOU USE CHANGES WHAT THE SYSTEM DOES.**

**A forbidden result is a property of the ACCOUNT, not of the surface.**

**The war story:** on a previous project an endpoint guard was classified as a confirmed bug **and a
blocker**, from a **single low-privilege account**. Re-running it as an administrator **returned
success**, and the real issue had been reproducible all along.

**A super-role account CANNOT reach permission-denied states, so "cannot reproduce the forbidden
error" on that account PROVES NOTHING.**

**Record which account and role produced each result. If a result hinges on authorization, re-check
on an account with different rights BEFORE classifying.** And **read how the role is resolved before
trusting a decoded token**. Aliases and normalization change the answer.

### 4. When a claim needs a mutation: never against shared data

**In order:** read the code and cite it → **run against your own local system**, sending **the
payload the client actually sends, including any idempotency header** ⚠ **a probe that omits it, or
a single call where the client retries, can HIDE the defect** → **write a scoped test.**

⚠ **Do NOT run the full suite and read failures as evidence.** Judge by the scoped file, **and if it
fails, re-run it ALONE before believing it.**

### 5. Record the verdict per finding

```
- **Harness:** … · **Account:** … · **Probe:** <one line>
- **Result:** CONFIRMED | CONTRADICTED | BLOCKED (<why>)
- **Observed:** <status + shape note, NEVER a raw body>
- **Class change:** <none | new class>
```

**Update classifications HONESTLY, IN BOTH DIRECTIONS.**

- **Contradicted** → **state the delta**: data, account, already fixed on this branch, or the
  deployed build differing from your checkout. Then check the history for a change after the
  document's date. **"Already shipped" is a COMMON outcome.**
- **True but different from described** → keep it real, **and rewrite the claim line to what you
  OBSERVED.**

### 6. Clean up

Delete throwaway scripts and any probe rows. **Leave the system as you found it.**

Then load `steps/step-03b-reproduce.md`.
