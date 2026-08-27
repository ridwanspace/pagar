# Contributing

This repo is a method plus a small tool, not a product roadmap. The bar for a
change is "would this help another engineer", not "is this how I do it".

## What belongs here

- A method that survives a change of stack, agent tool, or project.
- A trap someone actually hit, with what it cost and how to catch it next time.
- Working code that a reader can copy and run.

## What does not belong here

- Client names, employer names, internal hostnames, credentials, or private
  planning IDs. This is a public repo; nothing company-specific, ever.
- A pattern nobody has run yet. Mark speculation as speculation.
- A rule with no cost attached. "Prefer X" without "because Y bit us" is an
  opinion, and opinions do not compound.

## The honesty rule

Every claim in this repo should be checkable. If you write that a command
works, run it first. If you could not run it, say so in the same paragraph.
A doc that is 80 percent verified and honest about the other 20 percent is
more useful than one that reads as fully verified and is not.

## Changing the gate runner

The runner lives in `gates/`. Two rules are load-bearing:

1. **Zero runtime dependencies, forever.** It must start with a plain `node`,
   with no `npm install`, in any repo, including one that has no
   `package.json` at all. PRs that add a dependency to `gates/` will be
   declined. Build-and-dev tooling outside the runner (CI, shellcheck) is a
   different matter.
2. **Failure keys must be stable.** Same broken code, same keys, on any
   machine, on any day. Before a parser change ships, ask: would this key
   change if somebody added a line at the top of the file? If yes, the parser
   will invent NEW failures out of unrelated edits, and the gate will be
   turned off within a week.

To add a parser or a gate, follow the recipes in
[`gates/README.md`](gates/README.md) ("Adding a stack", and "Adding a parser"
under Design notes). Then run the suite:

```bash
node gates/test/run-tests.mjs
```

Built-ins only, `node:test` and `node:assert`. Nothing to install. CI runs it
on Node 20, 22, and 24, plus the Python, Node, and Go examples.

## Adding a lesson

The most valuable contribution is a real trap. The shape:

- What you expected.
- What happened.
- Why the usual check missed it.
- The guard that would have caught it.

The fourth line is the one that matters. A lesson without a guard decays.

## Style

- Short sentences. Plain words. Name the actor.
- State a hard rule as a hard rule. Hedging a real constraint helps nobody.
- Diagrams where a diagram beats prose. Mermaid renders on GitHub.

## Practicalities

- Small PRs, one purpose each. A doc change and a runner change travel
  separately.
- If your change touches anything a doc claims, fix the doc in the same PR.
- By contributing, you agree your contributions are licensed under the MIT
  License, the same as the rest of this repository.
