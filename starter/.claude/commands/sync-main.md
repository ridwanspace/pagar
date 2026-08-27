---
description: Fetch the default branch and merge it into the current branch, safely
allowed-tools: Bash, Read, Edit, Grep, Glob
---

# Sync with the default branch

**This MERGES. It never rebases.** ⚠ **Feature branches here are PUSHED and may be shared.
Rewriting their history BREAKS ANYONE WHO HAS PULLED THEM.**

## 0. Preconditions

Run the checks together and **read them all before proceeding.**

**Stop and report** if:

- You are already **on the default branch.**
- **The worktree is dirty.** ⚠ **Do NOT stash automatically. The user may have in-flight work they
  have not looked at.** **Show the dirty files and ask whether to commit, stash, or abort. WAIT for
  an answer.**
- **A merge or rebase is already in progress.**

⚠ **The status should never list personal-workflow paths. If one appears, the exclude
configuration was lost. SAY SO rather than committing it.**

## 1. Fetch and assess

**Fetch ALL branches, not just the default one.** ⚠ **A narrow fetch leaves every teammate branch
stale, which SILENTLY BREAKS the overlap check.** The merge below still targets the default branch
only: **the wider fetch buys visibility, not scope.**

⚠ **NEVER trust a behind-count from before the fetch.**

- **Zero behind** → **report and STOP. Do not create an empty merge commit.**
- Otherwise, **show what is incoming**: the commit list and the changed file list, **before
  merging.**

## 2. Predict conflicts BEFORE merging

Use a dry-run merge to surface conflicts without starting one.

**This is the step that keeps a bad merge from ever starting.**

## 2b. ⚠ The migration-ordering trap: check this EVEN ON A CLEAN MERGE

> **Two branches each adding a migration touching THE SAME TABLE produce two files that NEVER TOUCH
> EACH OTHER. Version control merges them WITHOUT A MURMUR, and then they COLLIDE AT APPLY TIME on
> the environment.**

**Manual ordering is required. Coordinate: whoever lands second adjusts theirs.**

## 2c. ⚠ Deliberately-duplicated configuration

**If your project keeps a configuration table in two places on purpose, DIFF BOTH AFTER THE MERGE.**
A merge can leave them disagreeing with no conflict marker anywhere.

**Other files that collide across branches BY NATURE:** the composition root, dependency manifests
and their lock files, the container or compose definition, and the generated API contract. ⚠ **If
both sides changed the generated contract, REGENERATE IT rather than merging it by hand.**

## 3. Merge

Merge the default branch with no editor prompt.

⚠ **If it conflicts despite the prediction, DO NOT IMPROVISE A RESOLUTION.** Show the status, list
the conflicted files, and **ask the user how to resolve each. Offer aborting the merge as the clean
escape hatch.**

## 4. Verify the result still WORKS

> ⚠ **A merge that succeeds TEXTUALLY can still break things. TWO BRANCHES CAN EACH BE VALID WHILE
> THEIR UNION IS NOT**, a renamed function called by new code, a field that moved, two migrations
> on one table.

- **Diff any deliberately-duplicated configuration.**
- **Run the build or import check.**
- **Run the scoped tests for the files the merge actually touched.**
- **Run the client-side gate if it touched that side.**

**Judge by SCOPED-GREEN, not a full-suite run.**

## 5. Report

- The commits merged and what they changed, **by area.**
- ⚠ **Whether migrations came in from BOTH SIDES, and the same-table answer. SAY IT EXPLICITLY,
  EVERY RUN THAT INVOLVES A MIGRATION.**
- Whether any duplicated configuration still matches.
- Which scoped tests ran.
- ⚠ **Anything the user should know about their IN-FLIGHT WORK**: for example, "the default branch
  changed the helper your branch also edits".

**Do NOT push. Do NOT commit anything beyond the merge commit itself.**
