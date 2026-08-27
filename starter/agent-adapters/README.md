# Agent adapters

**What this page answers:** what is in this directory, which parts are tested, and how to pick the
adapter you need.

The method in this repo is not the tool it was built on. These adapters carry the same rules to
four other agent tools. The full reasoning, the capability matrix, and the per-tool gotchas are in
[`docs/07-agent-tools.md`](../../docs/07-agent-tools.md). This page is the directory guide.

## Tested versus mapped

**Claude Code is the reference implementation and the only tool this kit was exercised end to end
on.** The hooks in `../.claude/hooks/` were written and run here. The rest of `../.claude/` is the
working setup.

**Everything in this directory is a documented mapping, not a tested integration.** The adapters
were written against each tool's published behavior. Nobody ran a project through them end to end.

That distinction is worth keeping in front of you, because a confident wrong instruction file
produces confidently wrong code. When an adapter says a flag or a directory exists, check it
against your installed version before you rely on it. Where a detail was not verifiable, the
adapter omits it or marks it, rather than guessing.

| Directory | Tool | Status |
| --- | --- | --- |
| `codex/` | OpenAI Codex | Mapped, not tested |
| `kiro/` | AWS Kiro | Mapped, not tested |
| `antigravity/` | Google Antigravity | Mapped, not tested |
| `cursor/` | Cursor | Mapped, not tested, shortest of the four |

## What is in each

```
codex/
  AGENTS.md              root instruction file, about 9.4 KB of a 32 KiB budget
  README.md              merge order and the size cliff
kiro/
  steering/product.md    purpose, users, features, locked decisions
  steering/tech.md       stack, commands, constraints, migrations
  steering/structure.md  layout, layering, naming, change discipline
  steering/testing.md    custom: red first, mutation verification, guards
  steering/security.md   custom: the floor
  README.md              how this method relates to Kiro's native specs
antigravity/
  .agents/rules/         five rules, each well under the 12,000 character cap
  .agents/workflows/     implement-story, review-story, triage-issue
  README.md              the character cap and how to split a large rule
cursor/
  .cursor/rules/testing.mdc   one worked example with correct frontmatter
  README.md              a shorter mapping note
```

## Using one

Each adapter's README has an install block. The shape is always the same:

1. Copy the files into the location the tool reads.
2. Replace every `{{PLACEHOLDER}}` with your project's real values.
3. Verify the size, where the tool has a limit.
4. Check what the tool actually loaded, where the tool can tell you.

Step 2 is not optional. A file full of placeholders is worse than no file, because it teaches the
agent that this directory contains noise, and then it starts skimming the parts that matter.

## Picking an adapter to start from, if you are porting to a fifth tool

The Antigravity rules are the best starting point. They are already split by subject, which is the
work you would otherwise have to do yourself, and each file is small enough to fit almost any
budget. The Cursor README shows the mapping from those files to a different format.

The Codex `AGENTS.md` is the best starting point if your target tool wants a single file, since
several tools read `AGENTS.md` directly, Antigravity included.

## What no adapter can give you

**Deterministic checkpoints, where the tool has no hook support.** A rule is an instruction the
model can reason around. A hook is a program that runs whether the model agrees or not. Where a
tool has no hooks, the fallback is CI and a pre-commit hook. Both run outside the model, which is
the property that actually matters. The two scripts in `../.claude/hooks/` are plain Node and plain
Python with nothing tool-specific in them, so they run from a CI step unchanged.

**The specs, the gates, and the recorded lessons need no adapter at all.** They are markdown files
and scripts in the repository. They do not live in any agent's configuration directory, and they
survive switching agents entirely. That is deliberate, and it is the actual insurance against tool
churn. See the closing section of [`docs/07-agent-tools.md`](../../docs/07-agent-tools.md).
