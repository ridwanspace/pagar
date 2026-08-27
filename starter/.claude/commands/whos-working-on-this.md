---
description: Check whether a teammate is already working on a surface before you start
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <area, keywords, or --files path...>
---

# Who is working on this?

**Run this BEFORE picking up a task, not at session start.**

> **Many teams have no shared task board that reflects reality, so THE REMOTE IS THE TRACKER:
> teammates push descriptively-named work-in-progress branches, and A BRANCH APPEARS WHEN SOMEONE
> STARTS, NOT WHEN THEY FINISH.**
>
> **That is the only PRE-EMPTIVE duplicate-work signal available. A merged-only view of the default
> branch reports the collision AFTER IT HAS ALREADY COST TWO PEOPLE THE SAME DAY OF WORK.**

## 1. Run the scan

Two modes:

- **Keyword**: matches branch names and changed paths. **Use when scoping a task described in
  prose.**
- **`--files <path>...`**: **sharper. Use once you know the files. THIS IS THE MODE TO PREFER WHEN
  THE ANSWER ACTUALLY MATTERS.**

**Exit codes:** `2` means overlap found. `0` means clear. `1` means **the scan itself failed,
report that. ⚠ DO NOT READ A BROKEN SCAN AS "CLEAR".**

⚠ **The scan fetches first. Skip the fetch only when you fetched moments ago: A STALE SCAN IS WORSE
THAN NONE, BECAUSE IT READS AS AN ALL-CLEAR.**

## 2. Interpret it: the numbers are a PROMPT, not a VERDICT

**The scan reports mechanical overlap. YOU judge whether it is duplication:**

| Case | What to do |
|---|---|
| **Same surface, same intent** | **Stop and talk to them.** |
| **Same files, different intent** | Not duplication, **but a merge conflict in waiting. Prefer to land after them.** |
| **A stale branch** | ⚠ **Do NOT assume either way. ASK.** An abandoned branch is also **USEFUL: their partial work may save you hours.** |
| **Would conflict today** | **Coordination is mandatory.** |
| **It adds a migration file** | ⚠ **Treat this as overlap EVEN WHEN NO FILE IS SHARED.** Same clean-merge, collide-at-apply reasoning as the sync command. |

### ⚠ Query terms that lie

Words like `test`, `api`, `app`, `service`, `model`, `schema`, and the names of your top-level
directories **name the repository's SHAPE, not a domain surface.**

**QUERY BY DOMAIN NOUN.** ⚠ **If a scan returns a suspiciously large number of branches, YOUR QUERY
WAS PROBABLY TOO GENERIC. Re-run it narrower.**

## 3. Report

**LEAD WITH THE DECISION, NOT THE DATA.**

- **Clear** → one line.
- **Overlap** → **the person, the branch, its age, the overlapping files, and A CONCRETE
  RECOMMENDATION**: talk to them, land after them, or pick a different task.

⚠ **RECOMMEND, DO NOT DECIDE. You cannot see their chat, their standup, or who was assigned what.**

Then check the recent history on the default branch: ⚠ **A BUG SOMEONE REPORTED MAY ALREADY BE
FIXED.** That is the first check `/triage` runs, for the same reason.

## Limits: state these when they matter

- ⚠ **Only sees PUSHED branches. A teammate working locally for three days is INVISIBLE.** This
  lowers duplication risk. **It does not eliminate it.**
- **No assignment data.** Branch existence is the proxy for "someone is on it".
- ⚠ **NEVER a substitute for asking.** **The output is a reason to START A CONVERSATION, not a
  replacement for one.**
