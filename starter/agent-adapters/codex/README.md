# Codex adapter

**What this page answers:** how to carry this method to OpenAI Codex, what maps cleanly, and the
two things that will bite you.

**Tested?** No. Claude Code is the only tool this starter kit was exercised end to end on. This
adapter is a documented mapping written against Codex's published behavior. Verify it against
your installed version before you trust it.

## Install

Copy `AGENTS.md` to your repository root and replace every `{{PLACEHOLDER}}`.

```bash
cp starter/agent-adapters/codex/AGENTS.md ./AGENTS.md
```

Then check what Codex actually loaded:

```bash
codex --print-instructions
```

Recent CLI versions accept that flag. It dumps the merged instructions Codex really read, which
is the only reliable way to see the result of discovery, merge order, and the size budget
together. Verify the flag exists in your version.

## What maps cleanly

| This method | Codex |
| --- | --- |
| Always-loaded project context (`.claude/CLAUDE.md`) | root `AGENTS.md` |
| Scoped rules that load on demand | nested `AGENTS.md` files, see the caveat below |
| Deterministic checkpoints | Codex hooks, plus your CI and pre-commit hooks |
| Specs, gates, recorded lessons | plain files in the repo, unchanged |

The specs and the gates need no adapter at all. They are markdown files and scripts. That is the
point of keeping them out of any agent's configuration directory.

## Gotcha 1: merge order, and it is the reverse of what people assume

Codex discovers `AGENTS.md` files from the repository root downward and joins them with blank
lines. **Files closer to the current working directory appear LATER in the merged prompt, so they
override earlier guidance.**

Read that twice, because the intuition usually runs the other way. People expect the root file to
be authoritative and the nested one to be a detail. It is the opposite. The nested file wins.

Use it deliberately:

```
AGENTS.md              broad project guidance, style, security floor
backend/AGENTS.md      overrides for the backend, Python specifics
frontend/AGENTS.md     overrides for the frontend, TypeScript specifics
```

Write the root file so a nested override reads as a refinement, not a contradiction. If your root
file says "never use `any`" and your backend file is about Python, there is nothing to override
and no confusion. If your root file says "tests go in `tests/`" and one area colocates them,
state the override explicitly in that area's file rather than hoping the model infers it.

## Gotcha 2: the 32 KiB cliff

Codex stops adding files once the combined size reaches `project_doc_max_bytes`, default 32768
bytes. Files past that point are dropped.

This is worse than it sounds, because of the discovery order. Root files are added first. So when
you blow the budget, the files you lose are the ones **nearest your working directory**, which are
also the most specific and usually the most important for the task at hand. The failure is silent
and it looks like the model ignoring a rule.

Two consequences:

- Keep the root file lean. It is paid for on every task in every directory.
- Measure. `wc -c AGENTS.md`, or sum every `AGENTS.md` on the path from the root to where you are
  working.

The shipped `AGENTS.md` here is about 9.4 KB, 29 percent of the default budget, leaving roughly
23 KB for nested files. Check with:

```bash
wc -c AGENTS.md
find . -name AGENTS.md -not -path './node_modules/*' -exec wc -c {} +
```

Codex also skips empty files. An empty `AGENTS.md` is not a way to disable a parent file. To
override a parent, write the override.

## Hooks

Codex has a hooks extensibility framework for injecting scripts into the agentic loop. Published
use cases include logging, scanning prompts for secrets, persistent memory, validation checks,
and customizing prompts by directory.

That last one is the interesting one for this method. It covers roughly the same ground as
`check-context-size.py`, and it maps to the same idea: a checkpoint that runs outside the model.

The exact configuration format and lifecycle event names change between versions, so this adapter
does not ship a hooks config. **Check your installed version's documentation.** The two hook
scripts in `starter/.claude/hooks/` are plain Node and plain Python that read environment
variables and write to stdout or stderr. They have no Claude Code specific code in them, so
whatever wiring your Codex version uses, the scripts themselves should run unchanged.

If your version's hook support does not fit, fall back to CI and a pre-commit hook. Both run
outside the model, which is the property that matters.

## Sub-agents

Not documented as available at the time of writing. Do not design a workflow around parallel
sub-agents on Codex. Verify against your installed version.

## What does not carry over

Named slash commands. The Claude Code skills in this kit, `/dev-story` and `/code-review` and the
rest, have no direct Codex equivalent. Two options:

- Keep each procedure as a markdown file in the repo, for example `docs/procedures/dev-story.md`,
  and start a task by telling Codex to follow it. More typing, same result, and the file stays
  useful when you switch tools again.
- Wrap the common ones in shell aliases or a small script that pastes the procedure text.

The procedure is the asset. The invocation shortcut is convenience.
