# Step 05: Ledger row and the deployment ask

## Step goal

**Record the audit so the next one is cheaper**, then hand the user **a message they can send
as-is.**

## Sequence

### 1. Report to the user first

⚠ **Keep the distinction between "a promotion is worth doing" and "a promotion FIXES THIS BUG"
VISIBLE. Both can be true, or only the first, and CONFLATING THEM IS WHAT SENDS SOMEONE ON A MERGE
THAT CHANGES NOTHING.**

**Report what you could NOT verify, stated plainly.**

### 2. Write the ledger row

Append to `{{SPEC_DIR}}/promotion-audit-ledger.md`:

| Date | Symptom | Area audited | Behind (per hop) | Verdict | Evidence | Asked of the owner | Outcome |
|---|---|---|---|---|---|---|---|

⚠ **Fill the OUTCOME column later, when they reply. THAT COLUMN IS WHAT MAKES THIS LEDGER
COMPOUND.**

**A verdict-C row confirmed by the deployment owner is proof that hand-applied migrations are a
RECURRING risk, not a one-off. THREE of them is a case for putting a migration step in the
pipeline. TWO verdict-E rows on the same variable is a case for a build-time assertion.**

### 3. Draft the ask

**Register and tone:**

- **QUESTIONING, not instructing.** **Ask them to check and verify. THEY OWN THE DEPLOY SURFACE AND
  CAN CORRECT YOUR READING OF IT.**
- ⚠ **Refer to the work, not to people. CITE COMMIT HASHES, NOT AUTHORS.**
- **Short. Long messages get skimmed**, and the one line that matters gets skipped.
- **Name the exact thing to promote, or the exact thing to verify.** Not "please check staging".

⚠ **IF AN EARLIER MESSAGE NAMED THE WRONG CAUSE, LEAD THE FOLLOW-UP WITH THE CORRECTION**: briefly,
without over-apologising. **State what you re-checked, what it showed, and what the new ask is.**

### 4. The pipeline-improvement question

**Did anything in this run get done by hand that should be a script or a rule?**

**"None this run" is a valid answer.** **Prefer updating the step file over adding prose elsewhere:
this skill is the thing that will be re-read next time.**

### 5. Do not act on the promotion

**This skill NEVER merges, pushes, or promotes.**

**Ending here, with the message drafted, IS THE CORRECT TERMINAL STATE.**

## Success / failure

✅ **Success:** exactly one verdict, **proven from content**, with the evidence stated. What you
could not observe **named as unverified, not guessed.** A ledger row written, with the outcome
column left open. **A short, questioning, specific message drafted, naming the exact commit or the
exact check.**

❌ **Failure:** **naming a commit from its message instead of its diff.** Reading "behind" as
"missing". **Closing on verdict B without probing further.** Stating an unobserved deployment fact
as a check. **Merging or promoting from this skill.**

**Master rule:** Prove it from content, name exactly one verdict, say what you could not see, and
hand over an ask, not an action.
