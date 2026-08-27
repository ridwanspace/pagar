# Step 02: Already solved?: kill the work that does not exist

## Step goal

For each issue from step 01, answer one question **before any code reading**: *has this already
been handled, by me, by a teammate, on the default branch, or in a prior investigation?*

**Anything answered "yes" is closed here with a citation, and never reaches step 03.**

## Why this step is first

**The reporter tested a DEPLOYED build. Your checkout is a different thing.** Three failure modes
this prevents:

- **The phantom bug.** A bug fixed on the default branch after your last sync **still reproduces in
  your local reading of the code.** Investigating it produces **a confident, fully-evidenced
  classification of a bug that no longer exists.**
- **The duplicate.** A teammate has an unmerged branch fixing exactly this. **The default branch
  only reveals the collision AFTER both people paid for it. The unmerged branch is the only
  pre-emptive signal**, because the remote is the team's only board: teammates push
  work-in-progress branches when they **start**.
- **The re-report.** A reporter retests the same surface each round and **re-files what a prior
  investigation already classified as working-as-designed**, or what a prior triage already closed.
  **Re-investigating it costs the same as the first time.**

## Mandatory rules

- 🛑 **Read-only.** No edits, no merges, no branch switches. **If a sync is warranted, OFFER it.
  Never do it unprompted.**
- 🛑 **Do NOT root-cause anything here.** You are **matching issues against known work**, not
  explaining them.
- ⚖️ **A match must be ARGUED, not assumed.** **A branch named for the area is not proof it fixes
  THIS issue. Read the diff or the commit body and cite it. A wrong ALREADY-SOLVED is worse than a
  wrong NEEDS-RCA, because it silently drops a real bug.**

## Sequence: four sources, in this order

### 1. The default branch, ahead of your checkout

```bash
git fetch origin {{DEFAULT_BRANCH}} --quiet && \
  git rev-list --left-right --count origin/{{DEFAULT_BRANCH}}...HEAD
```

⚠ **ALWAYS fetch first. A stale reference reports zero behind while really being several commits
behind.**

- **Zero behind** → note it and move on.
- **Behind by N** → look at **what is actually incoming, scoped to the surfaces the issues name**:

```bash
git log --oneline HEAD..origin/{{DEFAULT_BRANCH}}
git diff --stat HEAD...origin/{{DEFAULT_BRANCH}} -- <the paths the issues name>
```

For each issue whose surface appears in that diff, **read the relevant commit's DIFF, not just its
subject**, and decide whether it addresses the issue. If yes → **ALREADY-SOLVED**, citing the hash
and subject, **and say whether it has reached the environment the reporter tested.**

**If the incoming diff touches a reported surface, tell the user and offer a sync before
continuing.** A stale tree makes step 03 unreliable **for exactly those issues.** If they decline,
**record the position in the report header as a caveat on every classification.**

### 2. Unmerged teammate branches

Run the team-overlap check, **querying by DOMAIN NOUN**, not by generic words like "api" or "test".

For a plausible branch match, **confirm it before calling it**: read its commits, its diff stat,
and **the content of the specific file**, which is immune to how the branch was eventually merged.

If it genuinely covers the issue → **ALREADY-SOLVED**, citing the branch and who owns it, **and
note that it is PENDING MERGE, not on the default branch, not deployed anywhere, so the reporter
knows the fix is not live yet.**

⚠ **This only sees PUSHED branches. It is NEVER a substitute for asking the person.** If a match is
ambiguous, **say so and let the user check with them.**

### 3. Prior investigation reports

List and search the investigation reports. **Match on SYMPTOM and SURFACE, not filename.** When a
prior report covers the issue, **read its classification and act on it:**

- Prior **confirmed bug, since fixed** → **ALREADY-SOLVED**, citing the report and the fixing
  commit.
- Prior **confirmed bug, still open** → **NEEDS-RCA**, but say the investigation already exists:
  **it should be EXTENDED, not reopened as a new report.**
- Prior **works-as-designed** → **NOT-A-BUG**, citing the report and the requirement it cited.
  **This is a re-report; the reply should point at the original reasoning.**
- Prior **missing requirement** → **NOT-A-BUG** pending the product decision. **Note whether that
  decision has since been made.**

### 4. Prior triage reports

Same matching discipline. **Read the prior report's outcome section:**

- **STRAIGHTFORWARD, fixed and committed** → **ALREADY-SOLVED**, citing the report and the hash.
  **Check whether that hash is on the default branch yet**, so the reply can say "merged" versus
  "on my branch".
- **NOT-A-BUG** → reuse its citation. **A second report of the same thing is a signal the reporter
  DISAGREES WITH THE REQUIREMENT. Say so in the reply rather than re-arguing the implementation.**
- **NEEDS-DECISION, still awaiting an answer** → **ALREADY-SOLVED as triage work**: it is filed and
  waiting on a person, so there is nothing new to raise. **Flag it: a re-report is evidence the
  unanswered decision is costing someone**, which the user may want to use to chase it. **If the
  answer HAS come back, this is the re-entry case.**
- **NEEDS-INFO, never answered** → ask the same question again, **citing the earlier ask.**
- **NEEDS-RCA, handed off** → **check whether the investigation actually happened.** If not, **the
  handoff is stale.** Route it again and say so.

### 5. Report the kills

Present a compact table of what died here, with the issue, what killed it, and the evidence. Then
**state how many issues survive to step 03.**

**If ALL issues died here, skip straight to step 05** to produce the report and the replies. **There
is nothing to investigate or fix.**

## Step completion

Carry forward: the surviving issue list, the killed issues **with their citations**, and the
checkout position, including whether a sync was offered and declined.

Then load `steps/step-03-reality-check.md`.
