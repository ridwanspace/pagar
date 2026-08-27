# Step 04: Feed the story's ground truth forward

## Step goal

The story you just finished was a **dependency** of later stories. **Those later stories were
specced as guesses. Now there is ground truth**. Final table and column names, a reusable helper's
real signature, a proven pattern, a discovered constraint.

**Wire that ground truth into each dependent story's planning file**, so when `/create-story` later
expands them, **the developer starts from FACT instead of a sketch.**

**This is what makes the pipeline compound instead of just logging.**

**Forward-only: never rewrite a story at or before the finished one.**

## Mandatory rules

- 📖 Read this whole step before acting.
- 🔎 **Script-resolved, not full context.** Use the helper to find dependents. **Do NOT open every
  later story to guess relevance.**
- ➡️ **FORWARD-ONLY.** Edit only *later* dependent stories' planning files. Never a predecessor.
- ✍️ **Tight and factual.** One or two precise sentences per dependent. **Replace a guess with
  reality.** Name the reusable artifact. Flag a constraint. **No paragraphs, no manufactured
  feed-forward.**
- 🧭 **The source of record is the PLANNING story.** Feed-forward writes into the planning tree, the
  "what". `/create-story` pulls it into the dev story's carry-over later.

## Sequence

### 1. Resolve the dependents

```bash
{{SPEC_HELPER_COMMAND}} feed-forward <ref> --json
```

This returns the finished story's **surface**: its feature codes and the tables it touches, and
the **dependent stories**: later stories that either explicitly name it or share a requirement code
or a table with it. Each comes with its planning file, its status, and **why** it is downstream.

- **If no dependents:** print,
  > ℹ️ Story {ref} has no downstream dependents. Nothing to feed forward.

  and go to `step-05-sync-demo-seed.md`. **A story with no dependents can still have shipped
  seedable data.**
- Otherwise continue.

⚠ **This resolver is a heuristic over freeform prose**, not a real dependency graph. See
`rules/spec-pipeline.md`. **Treat its verdict as a hint to verify.**

### 2. Identify the ground-truth facts to propagate

From step 03's learnings and the dev story's completion notes, pick the facts a **dependent** must
build against. The useful forms:

- **Reality versus the guess.** The *actual* final table and column names, or model and field
  names, with types. The plan may have said "a log table with these columns"; **reality may differ
  slightly. Quote the real shape.**
- **A reusable artifact by name.** The helper or service the dependent should call **instead of
  re-inventing**, **with its exact signature.**
- **A proven pattern.** A dedup-key scheme, a correction pattern, an audit-row shape, an upload
  flow: "reuse the pattern proven in {ref}".
- **A constraint discovered.** A quota, a performance limit, a real-data shape **that changes the
  dependent's planned approach.** If it changes the dependent's approach or risks, **edit those
  now. Do not wait for it to fail mid-build.**

**Only facts that actually affect that dependent.** If the finished story changed nothing a given
dependent needs, **skip it and say so. Do not manufacture a note.**

### 3. Write the inherited-ground-truth note into each dependent's planning file

For each dependent, read **only that planning file**, then append or update **a single block near
its top context**, so it is the first thing `/create-story` sees:

```markdown
## Inherited from {ref} (verified {date})

- **Now solid ground:** {what is real now, e.g. the final table's columns, with types}.
  [from the dev story at {path}]
- **Reuse, do not reinvent:** call `{helper(signature)}`: proven in {ref}.
- **Constraint:** {discovered limit that changes this story's approach}, so {the adjustment}.
```

- Use the **real** current date from the session context. **Do not invent one.**
- If such a block already exists from a re-run, **update it in place rather than duplicating.**
- **If the new ground truth INVALIDATES something the dependent's body already states**: a
  now-wrong table name, an obsolete approach, **fix that line too** and note it in the block.
  **Keep edits surgical.**
- If a dependent **already has a dev story**, the planning note still goes in, **and flag it**:
  > ⚠️ Dependent {ref} already has a dev story but predates {this ref}'s ground truth. Its
  > carry-over may be stale. Re-run `/create-story {ref}` to refresh, or I can patch its
  > carry-over now.

### 4. Catch the names that drifted: use the script, do NOT hand-grep this

**A story is planned against GUESSED identifiers, the implementation ships different ones, and the
planning documents keep sending the next developer at a symbol that does not exist. Nothing else in
the pipeline notices, because specs are prose.**

```bash
{{SPEC_HELPER_COMMAND}} stale-refs   # backticked identifiers in forward-looking prose the code no longer defines
```

**Every finding is one of exactly two things. Decide which, per finding:**

- **Drift**: the name shipped differently. **Fix the spec line to the shipped name.** This is the
  same class of edit as section 3, and it is forward-only.
- **Not built yet**: a later story's deliverable, which its own criteria will name. **Leave it.**
  **The command cannot tell these apart, and it is not supposed to.**

⚠ It scans only **forward-looking** sections. A dev story's agent record and an investigation's
evidence **quote the past on purpose and are skipped.** If a run reports a suspiciously round
number of findings, **read the denominator line before believing it.**

### 5. Refresh the index and re-confirm coverage

```bash
{{SPEC_HELPER_COMMAND}} sync-status     # structure reconciled, manual status preserved
{{SPEC_HELPER_COMMAND}} coverage        # the finished story's features still covered downstream
```

### 6. Close the step

> **Feed-forward from Story {ref}:**
>
> - {dep-ref} ← {one-line ground truth wired in} (`<planning file>`)
> - {dep-ref} ← {…}
> - {dep-ref}: nothing relevant. Skipped.
>
> {Any "dev story already exists, may be stale" flags.}
> **Stale references:** {N found. K fixed as drift, M left as not-built-yet | none}.

Then read fully and follow `steps/step-05-sync-demo-seed.md`.

## Success / failure

✅ **Success:** dependents resolved **via the helper**, not by reading everything. **Real ground
truth**, final schema, helper signatures, proven patterns, constraints, wired into each *relevant*
dependent's planning file as a **dated** inherited block. Stale dev stories flagged. **The
stale-reference scan run and every finding triaged as drift-to-fix or not-built-yet.** Index and
coverage refreshed. **Forward-only.**

❌ **Failure:** **opening every later story to guess dependence.** Manufacturing feed-forward where
nothing changed. **Rewriting a predecessor.** Vague notes like "remember story X" **instead of the
actual signatures and columns.** Leaving a dependent's now-wrong body unedited.

**Master rule:** Turn this story's hard-won reality into the next story's starting facts,
precisely, forward-only, script-resolved.
