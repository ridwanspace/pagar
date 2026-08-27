# Step 06: Write the decision record, sync the project memory, commit

## Step goal

**Make the guide MAINTAINABLE BY THE PIPELINE.**

> ⚠ **WITHOUT THE RECORD, THE GUIDE YOU JUST BUILT ROTS.**

## 1. Write the decision record

**This file is the guide's SOURCE OF RECORD.** ⚠ **When a future agent wonders "how do I add a
documentation page here", THE ANSWER MUST BE COMPLETE IN THIS ONE FILE.**

It states: where pages live · the organization and why · the page patterns · **how the reference
table is regenerated, with the exact command** · **what the guards check and where they live** ·
the examples policy · the copy language · **and any repository trap, such as an ignore rule that
requires a force-add.**

**No placeholder survives. Delete optional sections that do not apply.**

## 2. Sync the project memory file

⚠ **Check the line budget FIRST.** It is kept near 200 lines. See `/code-review` step 03.

⚠ **POINT, DO NOT DUPLICATE. The record holds the detail.**

## 3. Sync the README

Add or fix the pointer to the guide.

⚠ **Do NOT fix the README's other staleness in this run. Out of scope.**

## 4. Self-check

- [ ] **`/code-review` step 02 could add a page FROM THE RECORD ALONE**: structure, index wiring,
      table regeneration, guards, examples policy, and any staging trap all stated.
- [ ] Guards pass, **and were seen RED during mutation verification.**
- [ ] Every example was **replayed on the wire.**
- [ ] Field names **diffed mechanically, in both directions.**
- [ ] ⚠ **Confirm the full list of new files is actually staged.** **Listing what changed recently
      is NOT enough. Enumerate every page you created**, especially if an ignore rule required a
      force-add.

## 5. Commit

⏸️ **HALT:**

> **[C] Run /commit · [S] I'll commit myself · [R] Something to revise first**

🛑 **Do not commit without the user's say-so. Never bypass the gates.**

**Done. The guide is live, guarded, and wired into the pipeline.**
