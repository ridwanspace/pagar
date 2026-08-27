# Smart Commit

Follow these steps exactly, **pausing for user confirmation at decision points.**

The gates depend on **which part of the system was touched**, so read the staged diff before
deciding which to run.

## 1. Check the working tree

Run `git status --short`.

**If it is clean:** report "Nothing to commit. Working tree clean." and **STOP.**

## 2. Show what changed

Run `git diff --stat` and list the untracked files, formatted as a modified-versus-untracked block
so the user can see both at a glance.

## 3. Ask what to stage

Three options:

- **"all"** → `git add -A`
- **specific files** → stage exactly those
- **"modified"** → `git add -u`

**Wait for the user's response before proceeding.**

## 4. Confirm the staged set

Run `git diff --cached --stat` and **list what will be committed.**

## 5. Generate the message

From the staged diff and the recent history, following `{{COMMIT_CONVENTION}}`.

- **The summary is lowercase, imperative, and under 72 characters.**
- **The body explains WHY, not what**, wrapped at 72 columns.
- ⚠ **NO TRAILERS. NON-NEGOTIABLE.** **Never append co-authorship lines, generation notices,
  session links, or any similar trailer. The commit should look like any other team commit.**

Then ask: **"Commit with this message? (yes / edit / cancel)"**

**Cancel** → `git reset HEAD` and **STOP.**

## 6. Run the gates, then commit

**Only the gates for the areas actually touched:**

- **Server-side changes:** `{{TEST_COMMAND_SCOPED}}` for the touched tests, plus
  `{{BUILD_OR_IMPORT_CHECK}}`. ⚠ **If a data model changed, CONFIRM ITS MIGRATION FILE IS STAGED
  TOO. The model change and the migration SHIP TOGETHER.**
- **Client-side changes:** the baseline-aware gate, plus `{{LINT_COMMAND}}` and
  `{{TYPECHECK_COMMAND}}`.
- **Both:** ⚠ **THE PRIVATE-SPEC-ID SWEEP.**

  ```bash
  git diff --cached -U0 | grep -nE '^\+.*([Ss]tory [0-9]+\.[0-9]|\bAC[0-9]{1,2}\b|[Ee]pic [0-9]|RCA-[0-9]|TRIAGE-[0-9]|\.claude/)'
  ```

  **The staged diff must not carry private pipeline ids into the shared repository.** The personal
  tree is git-excluded, **so an id in a docstring points at a file NO TEAMMATE CAN OPEN.**
  **This applies to the COMMIT MESSAGE TOO.**

  ⚠ **The pattern deliberately does NOT match the team's own hyphenated requirement ids. Never
  strip those. Do NOT loosen the word boundary: it is tuned to miss them.**

**If a gate fails:** ask **"Quality gate failed. Would you like me to fix it?"**

- **Yes** → diagnose from the output, fix, stage, and **retry from this step.**
- **No** → **no commit. STOP.**

## Safety

- ⚠ **NEVER skip the gates to "commit fast".**
- ⚠ **NEVER stage or commit personal-workflow paths**: the agent's own directory, the project
  memory file, or any generated index the team does not track.
- ⚠ **If your repository ignores this file type by default, a new document needs a force-add**, and
  it will otherwise be silently missing from the commit.
- ⚠ **If on `{{DEFAULT_BRANCH}}`, WARN the user**: "You're committing directly to the default
  branch. Consider a feature branch first." **Ask for confirmation before proceeding.**
