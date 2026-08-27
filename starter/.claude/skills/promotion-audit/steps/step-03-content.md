# Step 03: Prove presence or absence by CONTENT

## Step goal

**This is the step that assigns the verdict, and the step where audits go wrong. SLOW DOWN HERE.**

## Sequence

### 1. Diff the watchlist files: the primary evidence

Compare each watchlist file **between the two branches.**

> ⚠ **"IDENTICAL" ACROSS THE WHOLE SYMPTOM PATH IS THE SINGLE STRONGEST SIGNAL IN THIS SKILL. It
> means THE PROMOTION GAP CANNOT EXPLAIN THE BUG, no matter how many commits the branch is
> behind.**

### 2. If a watchlist file DIFFERS: READ THE DIFF, NOT THE MESSAGE

**One question, in writing:**

> **DO THE CHANGED LINES SIT ON THE CODE PATH THAT PRODUCES THE SYMPTOM?**

⚠ **A commit message describes INTENT and COVERAGE. Only the diff describes BEHAVIOUR. A COMMIT
MESSAGE IS NOT EVIDENCE.**

### 3. Cross-check the MECHANISM, not just the file

**Count the load-bearing identifiers on both sides.**

- **Equal counts plus an identical surrounding block** means **the mechanism is unchanged.**
- **Unequal counts point you at the EXACT HUNK to read.**

### 4. Ancestry is a SECONDARY check only

An ancestry check proves a commit is **present** on a branch.

⚠ **IT CANNOT ESTABLISH RELEVANCE. That is section 2's job. NEVER let an ancestry result ALONE name
a cause.**

### 5. Migrations and schema

If the symptom depends on a schema change:

- **Is the migration file present on the target branch?**
- ⚠ **A migration file PRESENT on the target branch while the symptom PERSISTS is a strong pointer
  to VERDICT C: the file shipped, and the database never ran it.**

### 6. Assign the verdict

Per the five-verdict table in `SKILL.md`.

- **Verdict D**: the shipped change does not sit on the failing path. **Say this PLAINLY even if a
  promotion ask was already sent. A correction now is cheaper than a merge that changes nothing.**
- ⚠ **If a previous message named a commit this step now DISPROVES, DRAFT THE CORRECTION in step
  05** rather than quietly moving on.
- **Verdict B → go to step 04.** **The bug still exists somewhere.**

## Output of this step

The per-file verdict, the diff evidence for each differing file, and the assigned verdict **with
the specific reason it was assigned.**

Then load `steps/step-04-environment.md` for verdict B, or `steps/step-05-report.md` otherwise.
