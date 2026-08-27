# Step 01: Intake: detect the mode, split into checkable claims

## Step goal

Turn whatever the user gave you into a **numbered set of discrete, individually-checkable
findings**, each normalized to a claim you can prove or disprove. **Nothing is verified in this
step.**

## Mandatory rules

- 🛑 Do NOT verify, probe, reproduce, or root-cause yet.
- 🛑 Do NOT write the report file yet.
- 📖 Read this whole step before acting.
- ✂️ **One finding equals one checkable claim.** **Reporters routinely bundle three claims in one
  sentence and split one claim across three bullets. Fix that HERE, or every later step inherits
  the mess.**
- 🖼️ **Open every image before you write a single finding line.** A screenshot settles the
  environment, the literal rendered string, and the route, **often the only environment signal in
  the report.**

## Sequence

### 1. Take the input

- **A `/triage` handoff** → the fast path, below.
- **Pasted directly** → use it.
- **Invoked bare** → ask for the report and **STOP.**
- **A file path** → read it, **completely.**
- **A file path plus section ids** → the slice discipline, below.

#### 1b. Arriving from `/triage`: the fast path

Its intake is done. **Do not redo it.** Take its normalized issues, its already-ruled-out list, and
its findings so far.

⚠ **But treat triage's findings as LEADS, not conclusions. Its cause certainty was assessed under a
deliberate timebox, and a NEEDS-RCA route means it was explicitly NOT settled.**

### 2. Detect the mode, before anything else

**State which mode you are running and why.** If genuinely ambiguous, **ask.**

#### 2b. EXTERNAL-DOC mode: scope to a SLICE, never the whole document ⚠

**Long external documents grow and get edited in place. Re-ingesting the whole document every run
burns context on settled sections, re-asks questions you already answered, and risks promoting a
section into a SECOND story under a new report id.**

**THE UNIT OF WORK IS A SECTION, NOT A DOCUMENT.**

⚠ **A section edited AFTER it was processed outranks a new one.** If the document's text for an
already-processed section differs from what a prior report quoted verbatim, **a story may already
be building the OLDER text. Surface that FIRST.**

### 3. Establish the batch identity

Source · environment · **checkout position** (⚠ **a stale checkout is a caveat on every
classification**) · a batch slug · the next report number.

### 4. Split into discrete findings

**QA mode shape:**

```
### Finding N: <short title>
- **Raw report (verbatim):** "<exactly what was written. Do not paraphrase>"
- **Surface:** <route / page / component AND/OR endpoint / service / job>
- **Observed:** <what happened, as reported>
- **Expected (per reporter):** <or "(not stated)">
- **Repro steps:** <as given, or "(not given)">
- **Evidence given:** <screenshot N / request id / payload / log / none>
- **Account / role (if known):** <username or role>
- **Probe candidate?** <yes|no>. Drives step 03
- **User-visible?** <yes|no>. Drives step 03b
```

**EXTERNAL-DOC mode shape. CLAIM-TYPE FIRST. This is what makes the mode work:**

```
### Finding N: <short title>   [claim type: BASELINE | ASK | QUESTION]
- **Source section:** <where in the document>
- **Raw text (verbatim):** "<exactly what was written>"
- **Claim type:**
    BASELINE: "this already exists / works today"
    ASK     : "please build or change this"
    QUESTION: "please decide or advise"
- **Surface:** <where this would live>
- **Stated priority / phase:** <or "(not stated)">
- **What they assert:** <the checkable proposition, in your words, ONE sentence>
- **Proposed shape:** <the request, response, or screen behaviour they specified, or "(none given)">
- **Probe candidate?** <yes|no>
```

**Splitting rules:**

- ⚠ **EVERY ROW of a "what already exists" table is its OWN baseline finding. Do NOT collapse the
  table into one finding.**
- **Keep the verbatim quote. Your paraphrase can smuggle in an assumption.**
- **Do NOT judge yet.** Even if an ask obviously violates a locked decision, or a baseline is
  obviously wrong, **record it neutrally and let step 02 prove it.**
- ⚠ **A FOOTNOTE IS A FINDING.** External documents bury real defects inside asks: **a "noticed
  while testing" note under a feature request is its own finding.**
- **Trust the pixels over the prose.** When a caption and its screenshot disagree, **the screenshot
  is the observation. Quote what you see.**

### 5. Flag the blocking gaps only

- **A few** findings have gaps → note them, proceed.
- **Most or all** are uncheckable → **stop and ask the user ONCE.**

**Ask the user only what THEY can answer**: scope, priority, environment. **Anything answerable
from the code or the contract is YOUR job in step 02.**

### 6. Confirm the split before investigating

Present the numbered list compactly and **wait for confirmation.** **They may know that finding 4 is
already shipped on a teammate's branch, or that only one phase matters this sprint.**

## Step completion

Carry forward: **the mode**, the batch identity, and the confirmed numbered finding list **with
claim types and probe flags.**

Then load `steps/step-02-verify.md`.
