# Antigravity adapter

**What this page answers:** how to carry this method to Google Antigravity, and the one hard limit
that shapes every decision you make while porting.

**Tested?** No. Claude Code is the only tool this starter kit was exercised end to end on. This
adapter is a documented mapping written against Antigravity's published behavior. Verify it
against your installed version.

## Read this first: rules are capped at 12,000 characters each

**Each rules file is capped at 12,000 characters.** This is a hard limit, and it is the single
fact that decides how you port anything to Antigravity.

If your existing setup has one always-loaded memory file, check its size before you plan anything:

```bash
wc -c .claude/CLAUDE.md
```

A memory file over 12,000 characters cannot become one rules file. It has to become several. That
is not a workaround, it is the intended shape, and it is a better shape than what you had, but you
have to do the split deliberately rather than discovering it when content silently goes missing.

The five rules shipped here, measured with `wc -c`:

| File | Characters | Percent of cap | Headroom |
| --- | --- | --- | --- |
| `00-project.md` | 3,864 | 32% | 8,136 |
| `10-structure.md` | 4,621 | 38% | 7,379 |
| `20-testing.md` | 5,290 | 44% | 6,710 |
| `30-security.md` | 4,640 | 38% | 7,360 |
| `40-writing.md` | 2,913 | 24% | 9,087 |

Every one is under half the cap on purpose. You are going to add project-specific content when you
fill in the placeholders, and a file that starts at 90 percent of the cap is a file you cannot
edit safely.

Check yours after every edit:

```bash
wc -c .agents/rules/*.md
```

## How to split a rule that is too big

Split along the axis a reader would use, not by character count. A file cut in half at the 12,000
character mark produces two files that each make no sense.

**Split by subject.** Testing, security, structure, and writing style are four subjects. Each is
coherent alone. That is the split used here.

**When one subject is still too big, split by scope inside it.** Backend testing and frontend
testing. Or authentication and input validation. The test for a good split: can you name each half
in three words, and would a reader know which half to look in?

**Keep the shared framing in the file it belongs to, not duplicated across both.** If both halves
need the same principle, state it once in the orientation rule, `00-project.md` here, and let both
halves assume it.

**Number the files.** `00-`, `10-`, `20-` gives you a reading order and room to insert without
renaming everything. Renaming a rule file breaks anything that pointed at it.

**Cross-reference explicitly.** Each file here names the others in a table, so the agent knows the
other rules exist and knows what is in them.

## Install

```bash
mkdir -p .agents/rules .agents/workflows
cp starter/agent-adapters/antigravity/.agents/rules/*.md .agents/rules/
cp starter/agent-adapters/antigravity/.agents/workflows/*.md .agents/workflows/
wc -c .agents/rules/*.md   # confirm every file is under 12000
```

Then replace every `{{PLACEHOLDER}}`, and check the counts again.

## Rules versus workflows

The distinction matters and it maps cleanly onto this method's primitives.

**Rules are always active, like system instructions.** They cost context on every task. That is
what makes them the right home for things that must hold regardless of what you are doing: the
security floor, the testing discipline, the layering rule. It is also why the cap exists and why
you should treat headroom as scarce.

**Workflows are saved prompts you invoke on demand.** They guide a sequence of steps. They cost
nothing until you invoke one. That makes them the right home for procedures: implement a story,
review a story, triage an issue.

Three workflows ship here:

| Workflow | What it does |
| --- | --- |
| `implement-story.md` | Load one story, implement it task by task with red-first tests, validate, finish. |
| `review-story.md` | Verify the work and the tests, check what tests cannot see, sync docs, record the lesson, absorb one manual step. |
| `triage-issue.md` | Decide what is real before anyone writes code. Already-solved check first, then route by certainty. |

The split to keep in mind while porting: if a piece of guidance answers "how should this code
always look", it is a rule. If it answers "what steps do I take to do this job", it is a workflow.
Guidance in the wrong home either costs context it did not need to, or is unavailable at the
moment you needed it.

## Global configuration

Global configuration lives in `~/.gemini/`:

- `GEMINI.md` for rules that follow you across every project.
- `config/global_workflows/` for workflows you want everywhere.
- `config/skills/` for skills.

Put personal preferences there, for example how you like commit messages written, and keep the
project's `.agents/` describing the project. Mixing the two means every teammate who clones the
repo inherits your habits.

## Antigravity also reads `AGENTS.md`

Which means the Codex adapter in this kit is not wasted here. If your repo already has a root
`AGENTS.md`, Antigravity will read it.

Two ways to use that:

- **One file, two tools.** Keep everything in `AGENTS.md` and skip `.agents/rules/` entirely. Simpler
  to maintain, but you give up the rules-versus-workflows split and you get no on-demand loading.
- **`AGENTS.md` for the shared core, `.agents/rules/` for the Antigravity-specific split.** More
  files, better use of what Antigravity actually offers.

Whichever you pick, avoid holding the same rule in both places. Two copies of a rule become two
different rules within a month, and neither the agent nor a teammate can tell which one is current.

## What does not carry over cleanly

**Hooks.** This adapter does not document Antigravity hook support, because a confident wrong
example is worse than an omission. Verify against your installed version. If there is no equivalent
to a session-start or stop hook, fall back to CI and a pre-commit hook. Both run outside the model,
which is the property that matters. The two scripts in `starter/.claude/hooks/` are plain Node and
plain Python with nothing tool-specific in them, so if a hook point exists, the scripts should run
unchanged.

**Sub-agents.** Not covered here. Verify against your installed version.

**Path-scoped rules.** This kit's Claude Code rules declare a `paths:` glob so they load only when
the agent touches matching files. Rules here are always active. That is why the character cap
matters so much, and why moving a procedure into a workflow is the main tool you have for keeping
always-active context small.
