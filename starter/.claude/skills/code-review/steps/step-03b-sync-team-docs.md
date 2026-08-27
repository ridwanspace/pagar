# Step 03b: Mirror the durable learnings out to the committed team docs

## Step goal

Step 03 recorded this story's learnings **inward**, into the personal, git-excluded tree. This step
mirrors the **team-relevant subset OUTWARD** into `{{TEAM_DOCS_DIR}}/`, which is committed and
everyone's, **so the shared documents stay true instead of decaying into a snapshot of the day
they were written.**

The split is deliberate and is the whole point of this step. **See `rules/docs-sync.md`.**

| Lives in `.claude/rules/` | Lives in `{{TEAM_DOCS_DIR}}/` |
|---|---|
| How **I** work: baselines, mutation-verify discipline, my gate scripts, the spec pipeline | What **the repo** is: layering, endpoint rules, traps, how to run things |
| References the personal tree, story references, the status file | **Zero** references to the personal tree, a reader with no access to it must lose nothing |
| May name the exact file and line of a known committed secret | **Never** names a secret's location |
| Loads on demand into my context | Read by a human in the code-hosting UI |

**Everything in the right-hand column is a repo fact. A repo fact that changed in this story and is
now wrong in a committed document is a DEFECT this step exists to catch.**

## Mandatory rules

- 📖 Read this whole step before acting.
- 🚫 **NEVER cite a private spec id or a personal-tree path in these documents.** See
  `rules/no-local-spec-refs.md`. **The team's own requirement vocabulary is exempt.**
- 🔒 **Never copy a secret, or a secret's exact location, into these documents.** The local rule
  file may name file and line **because it is git-excluded.** The committed page states the rule
  and the rotation cost **without the inventory. Keep it that way.**
- ✅ **Confirm the documentation tree actually stages.** ⚠ If the repository ignores this file type
  by default and re-includes the documentation subtree, **know the exact rule.** If a page ever
  refuses to stage, **check that the re-include line survived a merge before reaching for a force
  add.**
- 🎯 **Mirror, do not duplicate.** A fact belongs in exactly one home when it is purely personal or
  purely a repo fact. Facts that are genuinely both appear in **both, stated once each, in the
  register of that home, NEVER as a copy-paste of the other file's wording, which is how the two
  drift apart invisibly.**
- ✅ **Only after the code is green.** This step runs after step 03, so the shipped behaviour is
  settled. **Do not document an intention.**

## Sequence

### 1. Decide whether this step has work

Ask of this story's diff and of step 03's recorded learnings: **did anything change that a page in
the committed documentation currently asserts?**

Resolve it **cheaply. Do NOT read every page.**

```bash
git diff --name-only {{DEFAULT_BRANCH}}...HEAD | sed 's#/[^/]*$##' | sort -u   # which surfaces moved
grep -rn "<the identifier, path, or number that changed>" {{TEAM_DOCS_DIR}}/
```

**The grep is the real check: a committed page that NAMES the thing you changed is the page that
is now wrong.**

Keep a table in your project of which page to re-check for which surface. A page's trigger surface
is the set of directories and files whose change could falsify its claims.

- **If nothing matches:** print,
  > ℹ️ Team docs: no committed page asserts anything this story changed. No update needed.

  and go to `steps/step-04-feed-forward.md`.
- **Otherwise** continue.

### 2. Classify each hit

Each grep hit is one of exactly three things. **Only the first two produce an edit:**

1. **Now false**: the page states behaviour, a path, a line number, or a count that this story
   changed. **Fix it. This is the case this step exists for.**
2. **Now incomplete**: still true, but the story added a case a reader would need: a new queue, a
   new check, a new trap of the same family as ones already listed. **Add ONE tight entry in the
   page's existing shape.**
3. **Still true**: the page names the file, but the claim is unaffected. **Leave it. Do not churn
   a correct page.**

**A step-03 learning with NO page it belongs in is a signal, not a gap:** it was personal
workflow, and the local tree was the right and only home. **Say so in the close-out.**

### 3. Make the edit

- **Surgical.** Change the sentence that is wrong. **Do not restructure a page as a side effect of
  a one-line behaviour change.**
- **Match the page's register:** statements of what the code does, with a path and line or a commit
  hash as evidence. **No hedging, no "we should".**
- **Update the page's verification date ONLY when you actually re-checked its claims**, not merely
  because you edited one line. **A false freshness stamp is worse than a stale one**, because it
  stops the next reader from checking.
- **A genuinely new subsystem** the existing pages do not cover gets a new page **and a row in the
  index. Do not create a page for one fact.** It belongs in the closest existing page.

### 4. Verify the links still resolve

The index table and the cross-links between pages are relative links. **A renamed page breaks them
silently.** Walk every relative link and every anchor, and confirm each target exists. **Empty
output is the pass.**

### 5. Stage them correctly

```bash
git add {{TEAM_DOCS_DIR}}/
git status --short {{TEAM_DOCS_DIR}}/      # confirm every intended file is staged
```

⚠ **The status line is NOT optional.** Confirm the edited pages are actually staged. **A merge
request that reads as "docs updated" and contains no docs is the failure this catches.**

### 6. Close the step

> **Team docs. Story {ref}:** {updated `<page>`: {one line on what was false or incomplete} | no
> page asserted anything this story changed}. Links: {verified | n/a}. Staged: {files | n/a}.
> **Kept personal:** {learnings that correctly stayed local, and why}, or "none, all learnings
> were personal workflow".

Then read fully and follow `steps/step-04-feed-forward.md`.

## Success / failure

✅ **Success:** the committed documents are true after this story. Edits **surgical and
evidence-carrying**. **No personal-tree path, private spec id, or secret location leaked into a
committed page.** Every edited page **confirmed staged.** Links resolve. **The personal-versus-team
split stated honestly, including "nothing to mirror" when that is the truth.**

❌ **Failure:** **leaving a committed page asserting behaviour this story changed.** Copy-pasting a
local rule file into the committed tree wholesale, workflow references and all. **Citing a private
spec id or a secret's line number in a committed document.** Editing a page and **never staging
it.** Restructuring a page that needed one sentence changed. **Stamping a fresh verification date
on claims you did not re-check.**

**Master rule:** The local tree learns how I work; the committed tree learns what the repo is. This
story just changed the repo, so the second one gets updated too, or is confirmed still true.
