# AGENTS.md

Guidance for AI coding agents working **on pagar itself**. If you are an
agent helping someone **adopt** pagar in their project, read the root
`README.md` instead — it has a routing table for that.

## What this repository is

pagar is a baseline-aware gate runner and spec-driven method for agentic
engineering — the sensor half of a coding-agent harness, with zero runtime
dependencies. Nothing here generates or fixes code. The durable artifacts are
plain files: docs, specs, baselines, lessons.

```
gates/        The runner. Node 20+, ESM, zero runtime dependencies.
docs/         The method, stack-neutral. Start at 00-the-sensor-half.md.
workflows/    The method applied to ordinary working days.
starter/      A copy-in template (Claude Code shaped) + other-tool adapters.
examples/     The same notes app on four stacks, each with its own gates.
```

## Hard rules

1. **Never add a runtime dependency to `gates/`.** The runner must start with
   a plain `node`, no `npm install`, in any repo, including one with no
   `package.json`. This is the project's headline property.
2. **Never introduce company-specific or client-specific content** — names,
   hostnames, ticket IDs, planning systems. This is a public repo.
3. **The honesty rule.** Every claim must be checkable. If you write that a
   command works, run it first. If you could not run it, say so in the same
   sentence. Docs that overclaim get reverted.
4. **Failure keys are stable or they are worthless.** Same broken code must
   produce the same key on any machine, any day: no absolute paths, no
   timings, no line numbers.

## Before you finish any change

```bash
node gates/test/run-tests.mjs     # must pass, zero failures
node gates/run-gates.mjs          # the repo's own gates
```

If you touched a doc, re-read it end to end. A doc that is 80 percent right
and honest about the other 20 percent beats one that pretends.

## Where things must stay in sync

- A parser added to `gates/src/parsers.mjs` must also appear in
  `KNOWN_PARSERS` (`gates/src/config.mjs`), the `parser` enum in
  `gates/gates.schema.json`, the table in `gates/README.md`, and the tests in
  `gates/test/run-tests.mjs`. Five places, one PR.
- The repo map in the root `README.md` must match the actual tree.
- `CONTRIBUTING.md` describes contribution rules this file inherits.

## Writing style

Short sentences. Plain words. Name the actor. State a hard rule as a hard
rule. When you describe a trade-off, say what the approach costs, not just
what it buys.
