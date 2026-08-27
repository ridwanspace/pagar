# Commands

Slash commands are short, imperative procedures the agent follows on demand. They differ from
skills in scope: **a skill is a multi-step workflow with its own step files; a command is one
procedure with gates.**

## What ships here

| Command | What it does |
|---|---|
| `commit.md` | Stage, generate a conventional message, **run the gates for the areas actually touched**, sweep for private spec ids, and commit. Warns on the default branch. |
| `sync-main.md` | Fetch and **merge** the default branch in, with conflict prediction, the migration-ordering check, and post-merge verification. **Never rebases.** |
| `whos-working-on-this.md` | Check the remote for a teammate already on your surface, **before** you start. |

## Frontmatter

Two of these carry frontmatter, and one does not. Both forms work:

```yaml
---
description: One line shown in the command list
allowed-tools: Bash, Read, Edit, Grep, Glob
argument-hint: <what the user should type after the command>
---
```

`commit.md` ships without frontmatter, which is fine when the filename and the first heading are
self-explanatory. **Prefer frontmatter for anything taking arguments**, since `argument-hint` is
the only place the caller learns what to pass.

---

## The merge-request driver: worth writing for your own forge

**Deliberately not shipped**, because it is the most forge-specific command in the set. A useful
version depends on your host's CLI, its request vocabulary, and your promotion chain. **Write your
own.** Here is what it should do, and why each part earns its place.

### What it does

1. **Detect the tooling.** Find your forge's CLI and check its authentication. ⚠ **Read the
   per-host result, not the exit code: a stale entry for a host you do not use can make the command
   fail while the host that matters is fine.** With no CLI, fall back to push options or a
   constructed URL, and **mention it once. Do not nag.**
2. **Resolve the promotion hop.** A feature branch targets the default branch. The default branch
   targets the first environment branch, and so on up the chain. **At the top, there is nothing to
   promote: stop.**
   ⚠ **A feature branch must target the DEFAULT BRANCH ONLY, never an environment branch directly,
   even for an urgent fix. SKIPPING THE DEFAULT BRANCH LEAVES IT WITHOUT THE CHANGE, so the next
   promotion SILENTLY DROPS IT.** If asked to skip anyway, **push back ONCE, then confirm**: it
   can be a real request, just not the default.
3. **Run three gates before pushing.**
   - **A scope guard:** no personal-workflow path may appear in the commits being promoted.
   - ⚠ **The migration-collision gate**, which version control cannot warn about. **And remember: if
     migrations are applied by hand, landing on a branch DOES NOT MOVE THE SCHEMA.**
   - **The project's test and lint gates.** ⚠ **If CI runs tests only on requests, LOCAL IS WHERE
     FAILURES GET CAUGHT. DO NOT PUSH RED.**
4. **Push and open the request**, with a body that carries **the reasoning, not a file list**, the
   commit list, and **the test evidence.** ⚠ **No private spec ids in the request either.** Run the
   overlap check first, and **name a teammate's touching branch in the description rather than
   silently superseding their work.**
5. **Wait for CI.** ⚠ **Pushing a branch alone may run NO pipeline: a quiet pipeline list right
   after a push is EXPECTED, not a failure.** On failure, fetch the log, diagnose, and **fix ON THE
   SOURCE BRANCH**, never on the target. ⚠ **Do NOT read a green pipeline as "the tests passed".
   Read it as "the pipeline ran". The real protection is the gates you ran in step 3.**
6. **Hand off.** **Merging is usually a reviewer's call, not yours.** Default to leaving it for
   review. **Never merge without the user's explicit go-ahead.**
7. **After the merge**, confirm the target contains the work, **restate that merged is not
   deployed**, and offer the next hop as **its own separate request.** ⚠ **If the merged work
   included a migration, SAY SO EXPLICITLY and confirm WHO APPLIES IT on that environment before
   calling the deploy done.**

### Why it is worth the effort

**The chain is where changes get lost.** A fix that lands on the default branch and never reaches
an environment produces exactly the report `/promotion-audit` exists to investigate. **A command
that makes each hop explicit, gated, and one-at-a-time is the cheapest prevention available.**
