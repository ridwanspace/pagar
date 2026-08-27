# Further Reading

**What this page answers:** where the ideas in these pages come from, and what to read next
depending on which part you want to go deeper on. Every item here is real and well known. Where
a URL is not certain, the resource is named by title and author instead of guessed at.

## Specifications and requirements

**"Writing Effective Use Cases", Alistair Cockburn.** The clearest treatment of how much detail
a requirement needs and when more detail stops helping. The scope discipline behind
[self-sufficient story files](02-spec-driven-development.md).

**"Specification by Example", Gojko Adzic.** Requirements expressed as concrete examples that
double as tests. Directly relevant when the reader of your spec is an agent, because an example
is unambiguous in a way a description is not.

**"User Story Mapping", Jeff Patton.** How to slice work so each slice is independently
valuable. Useful when an epic keeps growing and you need a principled place to cut it.

**AGENTS.md convention, <https://agents.md>.** An emerging open convention for a repo-level
instructions file that coding agents read. Worth knowing about whichever agent you use, since it
is the vendor-neutral version of the idea.

## TDD and testing discipline

**"Test-Driven Development: By Example", Kent Beck.** The original. Read it for the rhythm of
the loop, not the Java. The reason [mutation verification](03-tdd-with-agents.md) matters is
that an agent can skip the one step Beck assumed nobody could skip: watching the test fail.

**"Growing Object-Oriented Software, Guided by Tests", Freeman and Pryce.** The best book on
test doubles and on listening to what a hard-to-test design is telling you. Read it if your
mocks keep getting complicated.

**"Working Effectively with Legacy Code", Michael Feathers.** Defines legacy code as code
without tests, then gives you the techniques to get a seam into code that has none. The most
practically useful book on this list for anyone joining an existing project.

**"Unit Testing Principles, Practices, and Patterns", Vladimir Khorikov.** A precise treatment
of what makes a test valuable, and the case against testing implementation details. Sharpens the
"test the behavior, not the mechanism" instinct.

**Mutation testing tools.** `mutmut` and `cosmic-ray` for Python, Stryker Mutator for JavaScript
and TypeScript at <https://stryker-mutator.io>. These automate at scale the manual technique on
the TDD page. Worth knowing the automated version exists, though the manual version on one
specific guard is where the insight comes from.

## Continuous integration and trunk-based development

**"Continuous Delivery", Jez Humble and David Farley.** The deployment pipeline as a design
object, and why every commit should be a release candidate. The source for treating gates as
part of the system rather than as bureaucracy.

**"Accelerate", Nicole Forsgren, Jez Humble, Gene Kim.** The research behind the four delivery
metrics. Read it for the finding that speed and stability rise together rather than trading off,
which is the empirical case for gating.

**"Trunk Based Development", Paul Hammant, <https://trunkbaseddevelopment.com>.** A focused site
on short-lived branches and why long-lived ones cost more than they appear to. Directly relevant
to a `feat/* -> main -> stag -> prod` promotion chain, where each hop is a place work can get
stranded.

**Martin Fowler on Continuous Integration, <https://martinfowler.com/articles/continuousIntegration.html>.**
The canonical article. Short, and it defines the terms most teams use loosely.

## Software design and maintenance

**"A Philosophy of Software Design", John Ousterhout.** Deep modules with narrow interfaces, and
complexity as the accumulation of small obligations. The clearest available argument for why
"one user action equals one API call" is a design rule and not a preference.

**"The Pragmatic Programmer", Andy Hunt and Dave Thomas.** Broad, practical, and the origin of
several habits this method depends on: don't repeat yourself, fix broken windows, and own your
tooling.

**"Refactoring", Martin Fowler.** The catalog of safe transformations. Its precondition, that you
need tests before you refactor, is the reason the guard tests come first.

**"Domain-Driven Design", Eric Evans.** Read it for ubiquitous language: the argument that the
words in the spec and the identifiers in the code must be the same words. That is what makes a
spec checkable against an implementation instead of merely adjacent to it.

## AI-assisted engineering

**Claude Code documentation, <https://docs.claude.com>.** Covers the CLI, project instruction
files, custom slash commands, hooks, subagents, and MCP. The hooks and custom-command sections
are what make a personal pipeline like the one described here mechanically possible.

**Kiro documentation, <https://kiro.dev/docs>.** An IDE built around a spec-driven flow:
requirements, then design, then tasks, as explicit artifacts. Useful as a comparison point,
because it makes similar structural bets in a different shape.

**Antigravity documentation, <https://antigravity.google/docs>.** Google's agent-first
development environment. Worth reading for how it handles multi-agent work and artifact-based
verification.

**GitHub Copilot documentation, <https://docs.github.com/copilot>.** Covers repository custom
instructions and prompt files. Read the custom-instructions part specifically, since it is the
same idea as a project instruction file under a different name.

**"Attention Is All You Need", Vaswani et al., 2017.** The transformer paper. Not a workflow
resource, but understanding that these models predict tokens over a bounded context window is
what makes the [context-economy argument](02-spec-driven-development.md) concrete rather than
superstitious.

**"Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023.** Empirical
finding that models attend less reliably to information in the middle of a long context. This is
the evidence behind "an agent given everything attends to nothing", and the reason a short
self-sufficient story file beats a complete PRD.

## Tools with adjacent ideas

pagar did not invent baselines, gates, or the compound loop. These are the
tools and methods that shaped the thinking, and what pagar takes from each.

**RuboCop's `--auto-gen-config` / `.rubocop_todo.yml`.** The canonical lint
ratchet: existing violations are parked in a TODO file and only new ones fail.
This is where the baseline semantics come from — pagar applies the idea to
every gate at once, across languages, not to one linter's findings.

**FlakeHell's `baseline` command.** The same idea for the flake8 ecosystem;
worth knowing because flake8 itself still lacks it. Evidence that the pattern
is wanted everywhere and shipped almost nowhere.

**cargo-insta, <https://insta.rs>.** Snapshot tests for Rust that fail on
unexpected change and wait for a reviewed accept. The closest prior art to a
baseline you commit and shrink on purpose.

**Betterer, <https://github.com/phenomnomnominal/betterer>.** ESLint-ecosystem
tool that tracks issue counts over time and fails on regression. The
"ratchet" framing is its best contribution.

**pre-commit, lefthook, lint-staged.** Git-hook frameworks; fast, polyglot,
well maintained. pagar is not one of them: they scope checks to staged files
and install through a package manager, while agents work on whole repos in
fresh checkouts and need full-repo gates with machine-readable verdicts and
no install step. Hooks are one way to invoke pagar, not its replacement.

**GitHub spec-kit, <https://github.com/github/spec-kit>.** A spec-authoring
workflow (`/speckit.specify`, `plan`, `tasks`, `implement`) as an installed
CLI. pagar's spec pipeline is plain markdown you copy in, and pagar adds the
half spec-kit leaves out: enforcement. A gate that blocks the merge is worth
more than a prompt that asks nicely.

**BMAD method, <https://github.com/bmad-code-org/bmad-method>.** "Breakthrough
Method for Agile AI-Driven Development." Analyst, architect, PM, dev, and QA
run as agent personas through a structured plan-to-story workflow. The closest
cousin of pagar's spec pipeline, with the opposite center of gravity: BMAD
orchestrates the people-shapes around the work; pagar guards the artifacts the
work produces.

**Every's compound engineering, <https://every.to/guides/compound-engineering>.**
Where the term and the loop come from. Kieran Klaassen's method — brainstorm,
plan, build, review, capture — so each task starts ahead of the last, developed
building Every's AI product Cora. Open-sourced as a plugin:
<https://github.com/everyinc/compound-engineering-plugin>. pagar's
[two loops](04-compound-engineering.md) are the same principle as plain files
an agent of any brand can read.

## If you only read three

1. **Kent Beck, "Test-Driven Development: By Example"**, for the loop.
2. **John Ousterhout, "A Philosophy of Software Design"**, for why constraints are worth
   defending.
3. **"Accelerate"**, for the evidence that gates make you faster rather than slower.
