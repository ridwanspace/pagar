# Kiro adapter

**What this page answers:** how to carry this method to AWS Kiro, and the honest answer to the
obvious question, which is why you would bother when Kiro already does spec-driven development.

**Tested?** No. Claude Code is the only tool this starter kit was exercised end to end on. This
adapter is a documented mapping written against Kiro's published behavior. Verify it against your
installed version.

## Install

```bash
mkdir -p .kiro/steering
cp starter/agent-adapters/kiro/steering/*.md .kiro/steering/
```

Then replace every `{{PLACEHOLDER}}`. A steering file full of placeholders is worse than no
steering file, because it teaches the agent that this directory contains noise.

Project steering lives in `.kiro/steering/` at the project root. Steering that should follow you
across every project goes in `~/.kiro/steering/`. Put personal preferences there, for example how
you like commit messages written, and leave the project files describing the project.

Kiro also has `.kiro/hooks/`. See the hooks section below.

## The five files

| File | Convention | What it carries here |
| --- | --- | --- |
| `product.md` | conventional | Purpose, users, features, business goals. Plus the locked-decision table, which is this method's invariant list. |
| `tech.md` | conventional | Frameworks, libraries, tools, constraints. Plus commands, the pagination and N+1 and timeout rules, and the migration discipline. |
| `structure.md` | conventional | File organization, naming, imports, architecture. Plus the change-minimally rule and the two-homes documentation rule. |
| `testing.md` | custom | The red-first rule, mutation verification, mocking traps, guards, baselines. |
| `security.md` | custom | The floor: server-side authorization, fail closed, secrets, bounded input. |

Kiro's conventional three are `product.md`, `tech.md`, and `structure.md`. Custom steering files
are supported, and `security.md` is a commonly cited example. Testing and security are split out
here because both are long enough to swamp the file they would otherwise live in, and both are
things you want the agent to read as rules rather than as background.

## Gotcha: steering is several files, not one memory file

If you are coming from a tool with a single always-loaded memory file, the port is not a copy. It
is a split. You have to decide which of your existing rules is a product fact, which is a tech
fact, and which is a structure fact, and some of them will not obviously be any of the three.

Two failure modes to avoid:

- **Dumping everything into one steering file** and leaving the other two as stubs. That recreates
  the single-file problem inside a directory that was designed to solve it, and Kiro's conventions
  stop helping you.
- **Splitting so finely that no file has enough context to be useful.** A rule needs enough
  surrounding material to be interpretable. Fifteen files of four lines each is not organization.

The useful test for where a rule goes: would a new engineer look for this under "what is this
product", "what is it built with", or "where do things go"? If the answer is none of those, it
probably wants its own custom file, the way testing and security do here.

## How this method relates to Kiro's native specs

Kiro is built around spec-driven development natively. Of the four tools this kit maps to, it is
the closest fit to this method, and the honest advice follows from that.

**Use Kiro's own specs.** Do not port this kit's spec pipeline on top of them. Kiro's specs are a
first-class feature of the tool, integrated with how it plans and executes. Running a parallel
markdown pipeline beside them gives you two sources of truth, which is strictly worse than one.

**Take from this method the parts Kiro's specs do not cover.** There are three, and they are the
parts that make the method compound rather than just organize:

**1. The gates.** A spec tells the agent what to build. A gate checks what came back, outside the
model, where it cannot be reasoned around. That is `starter/.claude/hooks/`, plus your CI and your
pre-commit hook. Kiro has `.kiro/hooks/`, so there is a natural home for it. The two scripts in
this kit are plain Node and plain Python that read environment variables and write to stdout, with
nothing Claude Code specific in them, so the wiring is the only thing you need to translate.
Verify the hook configuration format against your installed version.

**2. Lesson mining.** When a bug gets through a green test suite, the fact that it got through is
information about your tests, and it evaporates within a week unless you write it down. Keep a
recorded-lessons section, in `.kiro/steering/testing.md` or a custom `lessons.md`, and add a line
each time something bites you. Steering files are always active, so a lesson recorded there is
paid forward into every future task automatically. This is the highest-value thing to port,
because it is the loop that makes the next task cheaper than this one.

**3. The two-homes documentation rule.** Working notes stay next to the workflow. Team-facing
documentation lives under `docs/`, committed, with no references to private workflow files or
internal spec IDs. When a change makes a fact wrong, fix it in both homes in the same change. See
`structure.md`.

## Hooks

`.kiro/hooks/` exists. The configuration format and the available lifecycle events are not
documented in this adapter, because they change between versions and a confident wrong example is
worse than an omission. **Check your installed version's documentation.**

What to wire, once you know the format:

- A session-start check that reports branch drift. `starter/.claude/hooks/check-drift.mjs` does
  this and exits 0 on every failure path.
- A stop check on context size. `starter/.claude/hooks/check-context-size.py` does this. Point it
  at your steering directory:

  ```bash
  AGENT_CONTEXT_MEMORY_FILE=.kiro/steering/product.md \
  AGENT_CONTEXT_RULES_DIR=.kiro/steering \
  python3 .claude/hooks/check-context-size.py
  ```

  Note that this treats every steering file as always loaded, which is correct for Kiro, since
  steering is not path-scoped the way this kit's rule files are.

If the hook format does not fit, fall back to CI and a pre-commit hook. Both run outside the
model, which is the property that actually matters.

## Sub-agents

Not covered by this adapter. Verify against your installed version.
