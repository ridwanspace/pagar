# Step 01: Scope the symptom and the candidate fix

## Step goal

Turn a report, often a screenshot, into **two concrete things: the EXACT failing behaviour, and
THE CODE PATH THAT PRODUCES IT.** Everything downstream compares against these.

## Sequence

### 1. Extract the symptom

- **The literal error text or wrong behaviour. QUOTE IT EXACTLY.** ⚠ **Exact strings are
  searchable. Paraphrases are not.**
- **Which environment**, from the address bar if a screenshot is all you have.
- ⚠ **WHEN they observed it, WITH THE TIMEZONE.** **Convert it and record it. "They tested BEFORE
  the promotion landed" is a complete, cheap explanation** that costs nothing to check and
  frequently ends the run.

⚠ **If the report is a bug LIST rather than one symptom, STOP. That is triage, and it belongs to
`/triage` or `/rca`.**

### 2. Locate the code path: on EVERY side

**Both sides can be involved: one side decides what it SENDS, the other decides whether to ACCEPT.**
Do not assume from the symptom's appearance which one owns it.

### 3. Name the candidate fix

The change or changes the user believes fixed this.

⚠ **Do NOT yet assert that any of them fixes the symptom. That claim requires the DIFF, which is
step 03. At this stage they are ONLY CANDIDATES.**

### 4. Build the file watchlist

The set of files whose content decides whether the symptom happens. This is what step 03 diffs.

⚠ **THE CANDIDATE COMMITS' FILE LIST IS NOT SUFFICIENT ON ITS OWN. The real decision logic often
lives in a helper the change never touched. Searching for the BEHAVIOUR finds it; the commit's file
statistics do not. ALWAYS ADD FILES BY BEHAVIOUR, NOT JUST BY AUTHORSHIP.**

## Output of this step

The quoted symptom, the environment, the observation time in a comparable timezone, the code path
on every side, the candidate changes, and **the watchlist.**

Then load `steps/step-02-gap.md`.
