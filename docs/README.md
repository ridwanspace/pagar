# The pagar method

**What this page answers:** what is in this `docs/` directory, and what order to read it in.

This is a write-up of a working method for building software with an AI coding
agent. It comes from real use on a production full-stack project, not from
theory. Nothing here is a mandate. Take the parts that fit your project.
Ignore the rest.

## Pages

| Page | What it answers |
| --- | --- |
| [00-the-sensor-half.md](00-the-sensor-half.md) | What pagar is: the sensor half of a coding-agent harness, and why sensors live outside the model. |
| [01-why.md](01-why.md) | Why AI coding assistants stop getting better after week one, and what the fix costs you. |
| [02-spec-driven-development.md](02-spec-driven-development.md) | How to make the spec the durable artifact: PRD, epics, stories, a status ledger, locked decisions. |
| [03-tdd-with-agents.md](03-tdd-with-agents.md) | How to run red-green-refactor when an agent writes both the code and the test. Mutation verification. |
| [04-compound-engineering.md](04-compound-engineering.md) | The centerpiece. Two loops that make the next task cheaper than this one. |
| [05-local-ci-enforcement.md](05-local-ci-enforcement.md) | The gate runner's method: gates, the ladder, the baseline pattern. |
| [06-further-reading.md](06-further-reading.md) | Books, papers, and official tool docs, grouped by topic. |
| [07-agent-tools.md](07-agent-tools.md) | Claude Code, Codex, Kiro, Antigravity, Cursor: what maps to what. |
| [08-loop-engineering.md](08-loop-engineering.md) | Running agent loops unattended: the failure taxonomy and the laws that keep them honest. |
| [09-graphify.md](09-graphify.md) | Token optimization via navigation: index the repo once, pay context for the question, not the corpus. |
| [10-six-principles-one-workflow.md](10-six-principles-one-workflow.md) | The whole fence, assembled: how the six principles compose into one loop. |

## Read these in order if you are new

Start with [00-the-sensor-half.md](00-the-sensor-half.md) for the idea in one
page, then [01-why.md](01-why.md) to see whether the problem is your problem.
Then read [02-spec-driven-development.md](02-spec-driven-development.md) and
[03-tdd-with-agents.md](03-tdd-with-agents.md), which are the two halves you
need before the loops make sense. Then
[04-compound-engineering.md](04-compound-engineering.md), which is the part
worth your time. [05-local-ci-enforcement.md](05-local-ci-enforcement.md)
pays off the same day you apply it. When the basics hold, [08](08-loop-engineering.md)
and [09](09-graphify.md) extend the method to unattended loops and cheap context,
and [10](10-six-principles-one-workflow.md) assembles the whole fence.

## A note on scope

The examples use Python with pytest and TypeScript with vitest, and they
assume a hosted Git repo with pull requests and a QA handoff step. The method
does not depend on any of that. It depends on three things only: a spec you
can point an agent at, a test you have watched fail, and a place to write
down what bit you.
