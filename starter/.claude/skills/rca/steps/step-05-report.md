# Step 05: Report & handoff

## Step goal

Write the report, show the user a **decision-grade** summary, and emit the **`/epics` handoff
block**, so the next command **starts from verified facts instead of re-reading the source
document.**

## Mandatory rules

- 📁 Write to `{{SPEC_DIR}}/rca/RCA-NN-<slug>.md`.
- 🚫 **Never stage this file.** Personal workflow, untracked.
- 🔐 **No credentials, tokens, or raw personal data.**
- ✍️ **Every finding keeps its VERBATIM QUOTE alongside your verdict.**

## Sequence

### 1. Write the report

Use `templates/rca-template.md`. **Fill every section. Write "n/a" rather than deleting a heading,
THE SHAPE IS WHAT MAKES THESE COMPARABLE ACROSS BATCHES.**

**State what you PROVED and what you INFERRED, separately.** ⚠ **A confident-sounding guess is
worse than an honest gap, because `/epics` will BUILD ON IT.**

**If step 04b found siblings, say so on its OWN LINE immediately after the summary table.** ⚠ **The
reported count and the actual count differing is THE SINGLE MOST DECISION-RELEVANT FACT IN THE
RUN:**

> *The document reported **1** defect in `<file>::<function>`; the fix-site audit found **N**,
> sharing one root cause. **K** are already fixed in flight; **M** have never been reported. **1**
> regression the naive fix would introduce is a mandatory guardrail.*

### 2. Present the summary table

### 3. Lead with what the user must DECIDE

**Above the table, ORDERED BY URGENCY, NOT BY FINDING NUMBER:**

1. ⚠ **Wrong baselines. FIRST, ALWAYS. They may be planning against it TODAY.**
2. ⚠ **Already-built asks.** This **unblocks them immediately and prevents duplicate work.**
3. **Decisions needed.** ⚠ **No story can be written for a blocked item.**
4. **Escalations**: anything contradicting a locked decision.
5. **Back to the reporter.**
6. **A teammate is already on it.**

### 4. Emit the `/epics` handoff block

**Only findings with REAL WORK enter:** confirmed bugs, confirmed gaps, accepted missing
requirements, and **ask-conflicts WHOSE RESHAPED FORM THE USER ACCEPTED.**

**EVERYTHING ELSE IS EXPLICITLY EXCLUDED, WITH ITS REASON.**

Each item: title · **owner** · files it touches · **migration: yes or no** · the constraint · **an
acceptance-criterion hint** · effort · **blocked by**. Plus a grouped line, and an explicit **"do
NOT create stories for these"** list with reasons.

**Rules that keep `/epics` honest:** every item carries **its report id** and **its owner**.
**Blocked items are marked with what blocks them and are SEQUENCED, not started in parallel.**
Grouped causes stay grouped. **A both-sides item says which side lands first.**

### 5. Emit the answer-back block

**EXTERNAL-DOC mode: ALWAYS.** The author made claims and asked questions. **They get an answer.**

**Paste-ready, and written as COLLABORATION, NOT CORRECTION.** Sections: already built and available
today · corrections to the current-state section · your open questions · reshaped asks · accepted
as-is and queued.

**Both blocks are DRAFTS. This skill NEVER SENDS ANYTHING and never files anything on the author's
behalf.**

### 6. Close the loop

**Always state WHAT REMAINS UNPROCESSED in an external document.** ⚠ **Leaving the remainder unsaid
makes it look like the whole document was handled.**

**OFFER, do not auto-run.** If any decision is unresolved, **say plainly that `/epics` should wait
on the blocked items.** The unblocked ones can proceed.

**Done. Do not start implementing.**

## Success / failure

✅ **Success:** every finding classified with citable evidence and its verbatim quote. Proven and
inferred stated separately. **The audit result surfaced on its own line where it changes the
count.** The decisions section ordered by urgency, with **wrong baselines first**. The handoff
gated to real work, **with exclusions and their reasons stated.** The answer-back drafted. The
unprocessed remainder named.

❌ **Failure:** **a confident guess presented as proven.** Burying a wrong baseline below the table.
Promoting a decision-blocked item into the handoff. **Sending anything.** Implying the whole
document was processed when it was sliced.

**Master rule:** Hand the next command verified facts and nothing else, and make what you could
not verify impossible to miss.
