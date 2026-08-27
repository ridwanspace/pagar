# Step 04: Environment probe: only for verdict B

## Step goal

**The code on the branch is correct, yet the environment still fails.** Find where the **running
environment diverges from the branch**: a stale artifact, an un-applied migration, or wrong
configuration.

## 🚨 The honesty rule for this step

> **PROBE WHAT THE WIRE SHOWS YOU. NEVER STATE AN ARTIFACT VERSION, A DEPLOYED VARIABLE, OR A
> DATABASE COLUMN AS FACT UNLESS YOU OBSERVED IT.**
>
> **"I could not check X" is a FINDING. A GUESS PRESENTED AS A CHECK IS A DEFECT.**

**All probes here are READ-ONLY.** ⚠ **Never send a state-changing request to a shared environment
to prove a point.** The only common exception is authenticating, and **only** to authenticate.

## Sequence

### 0. FIRST: reproduce on the wire: the fastest path to the answer

⚠ **If the deployed host serves a client application, AN UNKNOWN PATH MAY RETURN THE APPLICATION
SHELL WITH A SUCCESS STATUS.** That is **the fallback, not a live surface.**

**JUDGE BY THE BODY AND THE CONTENT TYPE, NOT BY THE STATUS CODE.**

⚠ **A structured not-found on a route the BRANCH HAS is DIRECT EVIDENCE OF A STALE ARTIFACT.** That
single observation often ends the run.

### 1. Compare the environment against the one that tracks the source branch

**Fingerprint the built artifact.** Most build tools emit content-hashed filenames.

- **Different hashes** mean **different builds.**
- ⚠ **IDENTICAL hashes while the BRANCHES DIFFER means a promotion that NEVER REDEPLOYED. Verdict
  C.**

### 2. Check the migration wiring

**Does the pipeline apply migrations, or does a human?**

⚠ **RE-READ THE PIPELINE CONFIGURATION EACH RUN. IT CHANGES.**

**If nothing in the repository guarantees an environment's schema advances when its branch moves,
SAY THAT.** **Offer both readings honestly. ASK RATHER THAN ASSERT, the deployment owner owns that
surface.**

### 3. Compose the schema query for the deployment owner

A read-only query they can run to confirm whether the column, table, or index the branch's model
declares **actually exists in that environment.**

⚠ **Always qualify the query by schema or database name. An unqualified query on a server hosting
several schemas RETURNS ROWS FROM THE WRONG ONE AND INVERTS THE ANSWER.**

### 4. Configuration checks: verdict E

For each candidate variable, record three columns:

| Variable | Symptom when it is wrong | **How to see it from OUTSIDE** |
|---|---|---|

⚠ **Anything in the right-hand column you COULD NOT OBSERVE goes into the message as a QUESTION,
NEVER AS A DIAGNOSIS.**

The highest-value case: **a client base URL baked in at build time.** ⚠ **It leaves NO TRACE in
version control**, so the only way to see it is **to fingerprint the built artifact and read the
target out of it.**

## Output of this step

For each check: **what you observed**, or **explicitly, that you could not observe it and why.**
Plus the refined verdict.

Then load `steps/step-05-report.md`.
