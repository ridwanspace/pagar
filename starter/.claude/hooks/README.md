# Hooks

**What this page answers:** what these two hooks do, how to wire them, and why a hook is worth
writing at all when you could put the same instruction in a rule file.

## Why a hook and not a rule

A rule is an instruction. The model reads it, weighs it against everything else in context, and
usually follows it. Usually is the problem. Under a long session, a rule competes for attention
with the task, and the model can reason its way to an exception. That is not a defect. It is
what a language model does with an instruction.

A hook is not an instruction. It is a program the harness runs at a fixed point in the loop. It
runs whether the model agrees with it or not. The model cannot skip it, cannot argue with it,
and cannot decide this one time does not count.

So the split is:

- Put **judgment** in a rule. "Prefer composition over inheritance here."
- Put **facts that must be checked** in a hook. "This file is 340 lines and it loads every turn."

A hook is the deterministic checkpoint. It is the part of the method the model cannot talk its
way past.

## The two rules of a hook

**A hook must be cheap.** It runs on every session start or every turn. A hook that adds two
seconds to a turn gets deleted within a week, and then you have no checkpoint at all. Both hooks
here are under a second in the normal case. `check-drift.mjs` is the slower of the two because
it does one network fetch, and it caps that with a timeout.

**A hook must not fail hard.** Blocking work to report something the developer did not ask about
is worse than staying quiet. Both hooks exit 0 on every failure path: no git, no remote, offline,
detached HEAD, missing files, unreadable files, garbage configuration. The context hook exits 2
when it has something to say, which is the Claude Code convention for surfacing a message to the
model without stopping the turn.

## `check-drift.mjs`

Runs on **SessionStart**. Reports how far the current branch has drifted from the default branch
on the remote.

It fetches, then it reports. It never merges, never rebases, never touches the working tree. The
fetch is the point: without it the tracking ref is stale and the behind-count reads 0 even when
the default branch has moved on.

Sample output:

```
[drift] feat/mine is 3 commits behind origin/main (1 ahead).

Incoming commits:
  54e2b82 docs: update the guide
  e79a729 feat(web): add the filter row
  837d07b fix(api): correct the parser

Touched areas (3 files): docs/x.md, src/api, src/web

This is a report, not a merge. Run /sync-main when you want to catch up.
```

It stays completely silent when there is nothing to say: you are up to date, you are on the
default branch, there is no remote, or the fetch failed.

Configuration, all optional:

| Variable | Default | What it does |
| --- | --- | --- |
| `AGENT_DRIFT_REMOTE` | `origin` | Which remote to compare against. |
| `AGENT_DRIFT_DEFAULT_BRANCH` | detected, else `main` | Which branch is the target. Detection reads the remote HEAD symref, then falls back to whichever of `main` or `master` exists. |
| `AGENT_DRIFT_TIMEOUT_MS` | `20000` | Per-git-command timeout. Caps the cost of a slow or unreachable remote. |
| `AGENT_DRIFT_MAX_COMMITS` | `5` | How many incoming commits to list. |
| `AGENT_DRIFT_SYNC_HINT` | `/sync-main` | The command the message tells you to run. Set it to whatever your project uses. |
| `CLAUDE_PROJECT_DIR` | `process.cwd()` | Repo root. The harness sets this for you. |

Requirements: Node 18 or newer, and `git` on `PATH`. No packages.

## `check-context-size.py`

Runs on **Stop**. Warns when always-loaded context has grown past its budget.

The always-loaded memory file is paid for on every single turn. Past a couple of hundred lines
it starts crowding out the actual task. The fix is never to delete content. The fix is to move a
cohesive section into a scoped rule file that loads only when the agent touches matching paths,
and to leave a one-line pointer behind.

It watches two things:

1. The always-loaded memory file, `.claude/CLAUDE.md` by default.
2. Every `*.md` under `.claude/rules/`. A rule that declares a `paths:` key in its YAML
   frontmatter loads on demand, so it gets the higher soft limit. A rule without `paths:` loads
   at launch just like the memory file, so it gets the strict limit and the warning says so.

Sample output:

```
Context budget: some always-loaded files have grown past their target.
  - .claude/CLAUDE.md is 251 lines, target is under 200. This file is loaded on every turn. Move one cohesive section into a scoped rule file and leave a one-line pointer to it.
  - .claude/rules/scoped-big.md is 305 lines, target is under 250. It is path-scoped, so it only costs context on matching files, but it is now long enough to split. Move a sub-topic into a sibling rule with a narrower paths glob.
  - .claude/rules/unscoped-big.md is 223 lines, target is under 200. It has no paths: frontmatter, so it loads at launch like the memory file. Add a paths glob to scope it, or split it.
This is a reminder, not a block. Split when you next touch the file.
```

Configuration, all optional:

| Variable | Default | What it does |
| --- | --- | --- |
| `AGENT_CONTEXT_ROOT` | two levels up from the hook | Repo root. |
| `AGENT_CONTEXT_MEMORY_FILE` | `.claude/CLAUDE.md` | The always-loaded file, relative to the root. Set it to `AGENTS.md` if that is your file. |
| `AGENT_CONTEXT_RULES_DIR` | `.claude/rules` | The rules directory, relative to the root. |
| `AGENT_CONTEXT_HARD_LIMIT` | `200` | Line limit for always-loaded files. |
| `AGENT_CONTEXT_SOFT_LIMIT` | `250` | Line limit for on-demand, path-scoped rule files. |
| `CLAUDE_PROJECT_DIR` | see above | Repo root, if `AGENT_CONTEXT_ROOT` is not set. |

A non-numeric or negative limit falls back to the default rather than crashing.

Requirements: Python 3.8 or newer. Standard library only, on purpose. It has to run under a bare
`python3` with no virtualenv active, because a hook that needs an environment is a hook that
breaks the first time someone forgets to activate one.

## Wiring

Copy [`settings.example.json`](settings.example.json) to `.claude/settings.json`, or merge the
`hooks` block into the settings file you already have:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/check-drift.mjs\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/check-context-size.py\""
          }
        ]
      }
    ]
  }
}
```

Two details in that JSON:

- The `SessionStart` matcher is `startup|clear`, so the drift report fires when a session opens
  and after `/clear`, not on every resume.
- The `Stop` matcher is the empty string, which matches everything. `Stop` has no meaningful
  matcher values to filter on.

Quote `$CLAUDE_PROJECT_DIR`. A path with a space in it breaks an unquoted command.

## Verifying a hook

Run it by hand before you wire it. A hook you have only ever seen return 0 is not evidence that
it works. It is evidence that it ran.

```bash
node .claude/hooks/check-drift.mjs; echo "exit=$?"
python3 .claude/hooks/check-context-size.py < /dev/null; echo "exit=$?"
```

Then make it fire. Check out a branch that is genuinely behind, or point the context hook at a
fixture with an oversized file:

```bash
AGENT_CONTEXT_HARD_LIMIT=5 AGENT_CONTEXT_SOFT_LIMIT=5 python3 .claude/hooks/check-context-size.py < /dev/null
```

If you cannot make a checkpoint fail on demand, you do not know that it would catch the thing
you wrote it to catch.

## Porting to other agents

Hook support differs a lot between agent tools, and it is the least portable of the four
primitives this method uses. See [`docs/07-agent-tools.md`](../../../docs/07-agent-tools.md) for
the capability matrix. The short version: both of these scripts are plain Node and plain Python
that read the environment and write to stdout or stderr. Any agent tool that can run a command at
a lifecycle point can run them unchanged. What changes per tool is the wiring file, not the hook.

Where a tool has no hook support at all, the fallback is your CI pipeline and your pre-commit
hook. Those run outside the model too.
