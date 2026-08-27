# Step 03: Reality check: is it a bug at all?

## Step goal

For each **surviving** issue, answer *"is this actually broken?"*, **cheaply.** You are separating
real defects from intended behaviour and from unspecified wishes.

**You are NOT finding root causes. That is the investigation's job for anything that stays
uncertain.**

## Mandatory rules

- 🛑 **Read-only. No edits.**
- ⏱️ **TIMEBOX each issue.** If you cannot settle it with one orientation search, one or two
  targeted reads, and a contract check, **it is uncertain BY DEFINITION → mark it NEEDS-RCA and
  move on. That is a CORRECT outcome, not a failure.**
- 🛑 **Do not chase root causes.** The instant you catch yourself building a causal chain across
  more than a couple of files, **or across a system boundary, STOP. You have crossed into
  investigation territory and are doing that work twice.**
- 📎 **Every verdict carries a citation:** a file and line, a contract quote, or a locked-decision
  id.

## Sequence

### 1. Orient before reading

Search for the route fragment or the rendered string, then **read only what it points at, and only
the lines you will cite.**

**A rendered error string found in the server code means the SERVER decides it and the client only
displays it. Found only in the client means the CLIENT decides it.** That one check settles
ownership for a large fraction of issues.

### 2. Check the issue against the three sources of truth, in this order

**The first one that settles it, wins.**

**a. The PRD's locked decisions.** If the reported behaviour **MATCHES a locked decision, the issue
is NOT-A-BUG, and it is not yours to "fix". Cite the decision id.** If the reporter is arguing the
requirement itself, **say so: that is a team decision to escalate, not work to schedule.**

Read **by section**, never whole. Use the helper's requirement inventory to avoid loading the PRD.

**b. The generated API contract.** The schema **is** the code. **Filter to the one path or schema in
question. Never dump the whole thing.**

**A mismatch between what the client sends or reads, and what the server's schema declares, is
strong, citable evidence. Quote the field name and type from BOTH sides.**

⚠ **If the client matches the committed contract snapshot but the reported behaviour still
contradicts it, the SNAPSHOT MAY BE STALE relative to the code.** Regenerate it. **Do not assume
the committed file reflects the running system.**

**c. The code of the relevant surface.** Does the code path **plausibly produce** the reported
behaviour? **Check the cheap gates first, ⚠ A BLANK PAGE IS A GATE UNTIL PROVEN OTHERWISE**: route
guards, feature flags, and the server-side authorization checks. **A behaviour no code path can
produce, on a build you have confirmed is current, is cannot-reproduce territory → route it
NEEDS-INFO with the specific question.**

### 3. Reproduce only when it is cheap and decisive

Reproduce a user-visible issue **when a look settles the routing call.** **Skip it when the contract
or a locked decision already settled it. Reproduction adds nothing to a decided issue.**

⚠ **THE ACCOUNT CHANGES WHAT THE SYSTEM DOES.** **A super-role account passes every guard, so
permission-denied states are UNREACHABLE on it: "cannot reproduce the forbidden error" on that
account PROVES NOTHING. And a forbidden result you DO see is a property of the account until
re-tested on a second one with different rights. Record the account beside every result.**

⚠ **Before blaming code when a deployed flow contradicts correct source, PROBE THE ENVIRONMENT.**
**A set-but-wrong environment variable presents exactly like a code bug**: a misconfigured
cross-origin setting reads as "the API is down", a missing credential reads as "the feature is
broken", a build-time-baked client base URL reads as "the client calls the wrong server". **If the
evidence points that way, that ALONE makes the issue NEEDS-RCA. Environment forensics are not a
triage-depth activity.**

**If reproduction is impractical, say why in one line and route on code evidence alone.**

### 4. Assign a provisional verdict

Per issue, one of:

- **NOT-A-BUG**: matches a locked decision, the contract, or intended behaviour. Cite it.
  *Terminal, closed in step 05.*
- **REAL**: the behaviour is wrong against a stated requirement or the contract. **Carry to step
  04.**
- **PROBABLY-REAL**: looks wrong, **but nothing states the expected behaviour.** This is where
  NEEDS-DECISION comes from, so **classify the gap PRECISELY:**
  - **unspecified**: nobody ever wrote the rule. **Someone has to DECIDE it.**
  - **undetermined**: a rule probably exists somewhere you cannot reach: a document outside this
    repository, a design file, a conversation. **Note where you think it lives.** The ask is "send
    me that document", **which is a DIFFERENT question from "please decide".**
  - **contested**: the reporter cites a requirement that does not resolve here. ⚠ **Check whether
    their id means something in this repository before assuming it is foreign.** An id that resolves
    to an unrelated clause is the signal they are working from a specification you do not have.
- **NEEDS-INFO**: cannot be settled from what you were given. **One specific question.**
  *Terminal.*

For every REAL and PROBABLY-REAL issue, record **two things step 04 needs:**

- **Cause certainty:** `proven`: you can point at the line or the contract clause that causes it,
  or `inferred`: you have a plausible story. **BE HONEST. This is the field that ROUTES the issue,
  and optimism here is how a configuration problem becomes a misdiagnosed code fix.**
- **Suspected ownership:** which surface, or `unclear`. **Only a confident, cited single surface can
  go inline. Anything crossing a boundary, or unclear, goes to investigation, and you do NOT argue
  cross-boundary ownership here.**

## Step completion

Carry forward: every surviving issue with its verdict, citation, cause certainty, and suspected
ownership.

Then load `steps/step-04-route.md`.
