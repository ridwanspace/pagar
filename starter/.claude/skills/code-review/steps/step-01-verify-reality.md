# Step 01: Verify reality (real requests, then verify and fix)

## Step goal

If the finished story touched a **user-reachable surface**, build a tight, numbered, labeled check
list from the story's acceptance criteria, **run those checks yourself with real requests or a
real browser**, fix what the results reveal, then hand the user the **actual transcripts plus a
short confirm list** for final sign-off.

**If the story has no user-reachable surface, this step is a no-op: say so and advance.**

> **The system running the latest code proves the code RUNS, not that it WORKS.** The automated
> pass fires the requests and catches response-provable defects. **Only the user's sign-off earns
> "verified".**

## Mandatory rules

- 📖 Read this whole step before acting.
- 👤 **You fire the requests. The human still signs off.** A real transcript is far stronger
  evidence than a green test suite, **but it is still you grading your own homework.** Never claim
  the surface works from tests alone, and **never close this step on the automated pass alone.**
- 🎯 **Tie every check to an acceptance criterion**, plus any check the PRD's locked decisions
  demand, an invariant number, a gated action, a formatting rule.
- 🗣️ **Name endpoints, fields, and messages in their ACTUAL on-the-wire form.** Quote what the
  system responds. **Do not paraphrase.**
- 🧪 **Honest boundary.** If part of a criterion **cannot be proven on dummy data**: a
  multi-period trend, a real file upload, real third-party data, **say so and name the real-data
  action that would exercise it.**

## Sequence

### 1. Decide if this step applies

Read the dev story's files table and acceptance criteria. The story is **surface-relevant** if it
created or changed anything a client reaches: a route, a request or response schema, middleware,
an error handler, a status code, an auth gate, or a rendered screen.

- **If NOT surface-relevant**: pure domain logic, an infrastructure adapter, a script, a job, a
  library refactor. Print one line:
  > ℹ️ Story {ref} has no user-reachable surface. Skipping the verification pass. Proceeding to
  > the documentation check.

  then go to `step-02-user-docs.md`. **Do NOT invent a test.**
- **If surface-relevant:** continue.

### 1b. Make any NEW surface reachable, before testing it

**A built endpoint nothing registers is a shipped bug that every gate misses.** A module can be
fully green, types, lint, a green suite, **yet unreachable because nobody wired it into the
composition root.**

- **Verify the story's new route or module is registered in the composition root**, with the
  correct prefix, matching the existing entries' shape. **If it is not, add it now** and note the
  change in the file list.
- **Verify it appears in the generated API contract** and renders in the docs UI. A route that is
  registered but missing from the contract, a leftover hide flag, a duplicate operation id, **is
  a defect.** Fix it unless the story explicitly wants it hidden.
- ⚠ **Watch for silent-fallback traps.** A parameterized route declared before a static one **can
  swallow the new path and make a wrong URL look real**, answering 200 from the wrong handler. A
  catch-all or a permissive validator can turn a bad request into a fake success. **Verify the
  actual path resolves to the actual handler: check the status code AND the body.**

> ℹ️ If you find yourself hand-comparing modules against registrations, **that is a step-06
> candidate**: a "no orphan module" guard test turns this check into a law.

### 2. Make sure the latest code is running, or pick the no-server route

Two equally valid harnesses. Pick per situation:

- **Live instance:** check whether it is already up before starting one. Then exercise it over the
  real transport.
- **In-process test client:** exercises the exact same stack. Routing, validation, middleware,
  error handlers, **with no server at all.** Prefer it when no server is running and the checks
  do not need one.
- If the story added a **new route**, note the exact path **verified against the real registered
  routes, never from memory.** A wrong path produces a 404, or worse, **a parameterized handler
  that answers and looks real.**
- If the story added **persistence or configuration**, remind the user it must be in place first.
  **Name exactly what is needed.**

⚠ **Your fix is not live until the process restarts**, unless auto-reload is on, **and you should
not assume it is.** A background worker caches its task code too. **"The fix does not work" is
this, most of the time.**

### 3. Build the numbered check list

Order the checks **the way the data flows**, derived from the story's criteria:

1. **Any one-time setup**: only if needed. Skip and say so if none.
2. **The requests or interactions**: for each surface the story shipped: the **happy path** with
   **concrete values, not placeholders**, and **at least one failure path**.
3. **The result checks**: expected status **and** expected values, **spelled out**.
4. **The contract checks**: the generated contract lists the new paths with the right models.

**One numbered check equals one assertion, labeled A, B, C**, so the user can reply "A ok, B ok, C
returns X".

**Include these when they apply:**

- **An authorization check**, if the story has role-gated actions: a request from an out-of-scope
  caller **must** be rejected, not a success, and **not a leaky error body.**
- **An invariant check**, if the locked decisions pin a number or identity the response exposes:
  confirm it still holds **on the wire.**

### 4. Run the automated pass: always, without asking

**Do not offer, do not ask permission. Run it.** Announce it in one line and proceed.

1. Pick the harness. **Watch the logs while you test**: stack traces and warnings surface there and
   nowhere else.
2. Map the checks **one to one** onto requests: **one labeled transcript per check**: method,
   path, headers minus secrets, body, status, response. **Use a distinct caller per role**, since
   the authorization check needs the out-of-scope caller's own credentials. **Add a persistence
   assertion where a check writes data**, by reading it back.
3. **Verify every result against its expected value.** `A ✅` / `B ❌ returned X, expected Y`,
   plainly.
4. **Fix any defect at the source**, re-run the narrow gate, **re-fire that one request** to
   confirm, then clean up. Throwaway scripts deleted, seeded rows removed.
5. Sort the checks into **wire-proven** versus **needs a human**: anything a response cannot
   prove: a real file upload, real third-party data, behaviour under load, plus the honest-boundary
   items from section 3.

**Fall back to a fully manual guide only when the automated pass genuinely CANNOT run**: the
service cannot start because of configuration the user must supply, or the flow is dominated by
checks a response cannot prove. A user asking for the manual guide also overrides, **but never
pre-empt that by asking.**

### 5. Hand it off and wait

Present the results table, check, transcript, verdict, fix applied, include the labeled
transcripts **verbatim**, and end with:

> The wire-provable checks are verified above. Please eyeball the transcripts and confirm, and run
> the remaining checks {list the labels} yourself. Reply per label and I'll debug anything off.

**Halt and wait for the user's report.** Do not advance until the pass is resolved. **The automated
pass shrinks the user's list. It never removes the sign-off.**

### 6. When results arrive: verify, then fix

For each check the user reports:

- **Verify** it against the expected value. Call out matches and mismatches plainly.
- **For any mismatch, bug, or contract defect**: a wrong status, a wrong value, a leaky error
  message, missing validation, wrong serialization, anything breaking a locked invariant:
  - Diagnose from the report and **the specific file** the story's file list names. **Read only
    that file.**
  - **Fix or improve it directly**, respecting all project rules. Add or adjust the test.
  - Re-run the narrow gates the change touches, and **tell the user exactly which check to redo.**
- If a result reveals the implementation **contradicts the PRD or the epic**: not just a bug, but
  a wrong rule, **do not quietly patch around it.** Surface it, recommend `/edit-prd` or
  `/epics`, and note it for steps 03 and 04.

**Loop until every labeled check passes or the user is satisfied.** Keep the dev story's file list
and completion notes updated if a fix changed files.

### 7. Close the step

> **Verification. Story {ref}** ({automated pass + human confirm | fully manual}): {N} checks,
> {pass}/{N} ✅ ({K} wire-proven, {M} human-verified). Fixes applied: {list or "none"}. Boundary
> notes: {what could not be proven on dummy data, or "none"}.

**If your team hands scenarios to a QA function, this is the moment to emit those rows**, since
the checks you just ran **are** the test rows: same scenarios, same expected values.

⚠ **Write the expected value from the CODE, not from the story.** That is the whole point. **A
wrong expected value in a QA sheet carries your name and costs a test cycle plus a long written
correction. If the story and the code disagree, the code wins**, and you surface the story defect.

⚠ **Those rows LEAVE the personal tree and go to teammates**, so `rules/no-local-spec-refs.md`
applies: **never a private spec id in a cell.**

Then read fully and follow `steps/step-02-user-docs.md`.

## Success / failure

✅ **Success:** correctly decided applicable versus no-op. **Every new surface is reachable**,
registered and present in the contract. An criteria-tied, labeled check list including happy and
failure paths plus the authorization and invariant checks. **The automated pass run without
asking**, every transcript verified, transcripts plus a short confirm list handed over. Every
human-returned check verified. Bugs fixed at the source with tests. Harness cleaned up. Any spec
contradiction flagged. **Ends in the user's sign-off.**

❌ **Failure:** closing the step on the automated pass alone, with **no human sign-off**. Claiming
it works without verification. **Shipping a module nothing registers.** A generic guide not tied to
this story's criteria. Testing only the happy path. Making the user re-run checks the transcripts
already proved. **Asking whether to run the automated pass instead of just running it.** Skipping
a locked-invariant check the response exposes. Silently coding around a spec conflict.

**Master rule:** You fire the requests; the human's eyes are the final gate. Capture the
transcripts precisely, verify honestly, fix at the source.
