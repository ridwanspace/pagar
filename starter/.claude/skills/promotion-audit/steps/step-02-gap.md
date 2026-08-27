# Step 02: Measure the branch gap, per hop and per area

## Step goal

Establish **how far the target branch trails its source.** **This step produces NUMBERS, NOT
CONCLUSIONS.**

## Sequence

### 1. Fetch first, always

⚠ **NON-NEGOTIABLE: a stale reference makes every later answer CONFIDENTLY WRONG.**

```bash
git fetch origin --prune --quiet
git rev-list --left-right --count origin/<target>...origin/<source>
```

### 2. Read the numbers PER AREA, not per repository

A repository-wide count tells you almost nothing in a monorepo. **Scope the count to the
directories the symptom's code path lives in.**

### 3. Interpret "direct commits on the target" before it alarms you

- **Merge-only ahead counts are NORMAL and BENIGN.** ⚠ **Say so explicitly if you quote an
  ahead-count in your message: an unexplained "29 commits ahead" INVITES A WRONG PANIC.**
- **Direct commits on an environment branch are a REAL FINDING.** Someone committed or cherry-picked
  straight onto it, **so that work is STRANDED, it is not on the source branch, and the
  environment may be running code the source branch NEVER HAD.**

### 4. The timeline check: cheap, often decisive

Compare **when the promotion merge landed** against **when the reporter observed the symptom.**

⚠ **A promotion merge at a given time does NOT mean the artifact was deployed at that time.** The
deployment picks it up separately. **"Promoted after they tested" is an explanation. "Promoted"
alone is NOT proof it is live.**

### 5. Do NOT conclude yet

⚠ **A BEHIND-COUNT IS NOT A VERDICT.**

**A branch can be many commits behind IN THE SYMPTOM'S OWN AREA and STILL CONTAIN EVERY LINE THAT
MATTERS.**

**Resist the pull to message the deployment owner here. The CONTENT CHECK in step 03 is what earns
the verdict.**

## Output of this step

The per-hop, per-area behind counts. The direct-commit finding, if any. The timeline comparison.
**And explicitly: no verdict yet.**

Then load `steps/step-03-content.md`.
