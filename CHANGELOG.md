# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **README rewritten around the six disciplines.** A thirty-second
  three-door orientation (gates / graphify / story loop), a
  disciplines-at-a-glance table that doubles as the reading map, two new
  mermaid diagrams (the six-station composite loop, and a working day
  from the 09:00 graph query to the 17:40 overnight launch), concrete
  install steps for graphify (pip `graphifyy` + the starter skill +
  first build) and the story loop (copy, guard suite, dry-run,
  supervised first story), a pick-your-scenario table routing to all
  seven workflow walkthroughs, a graphify row in the positioning table,
  and an expanded "what is actually tested" section covering the loop's
  dry-run guards and the graphify-on-pagar verification.

### Added

- **The six disciplines woven into the workflow scenarios.** Graphify
  enters where orientation costs context: story file discovery in
  `01-new-feature`, mechanism location in `02-bug-from-qa` and
  `03-fix-not-on-stag`, Monday re-entry in `04-monday-morning`, and a
  full "build the map on day one" section (free local AST build, god
  nodes, surprising connections) in `05-joining-a-repo`. The story loop
  enters as the new `workflows/07-overnight-run.md`: preconditions
  checked honestly, the 17:40 evening sequence (dry-run preflight, one
  supervised story, launch on a branch), the morning review in order,
  and the failure taxonomy applied to an overnight failure.
  `06-a-real-week.md` gained the honest counterpoint: the week that did
  NOT run the loop, and why that was right. Router updated — decision
  tree, routing table, chaining diagram, and the helpers section.
- **The story loop ships**: `starter/scripts/loop/` — the unattended
  create-story → dev-story → code-review → commit runner (one fresh headless
  session per phase, one conventional commit per story), ported from
  production use and generalized: `specs.py` bridge replaces the TypeScript
  CLI, verification gates auto-detect pagar gates / npm / tsc, the review
  phase maps to pagar's `code-review` skill, and the commit trailer is
  opt-in. Includes per-phase prompts (unattended contract, reflect, compact),
  a starter LEARNINGS.md, and `loop.test.sh` — a zero-dependency dry-run
  guard suite (29 guards, mutation-verified) that never invokes the agent
  CLI. CI runs the suite and shellchecks every loop script.

- **Loop engineering** as the fifth principle: `docs/08-loop-engineering.md`
  (the failure taxonomy — phase, gate, honest blocker, wiring — and the eight
  laws of unattended loops), plus a generalized `loop-engineering` starter
  skill (diagnose / modify / verify step files).
- **Graphify** as the sixth principle: `docs/09-graphify.md` — token
  optimization via navigation; index the repo once (free local AST extraction,
  cached semantic extraction), then query with a budget instead of re-reading
  the corpus. Ships an operating-manual starter skill for the open-source
  graphify tool (PyPI `graphifyy`, Graphify-Labs).
- `docs/10-six-principles-one-workflow.md`: how the six compose into one loop,
  what each catches that the others cannot, and the adoption ladder.
- README expanded to the six principles with credits for both new ones;
  `graphify-out/` gitignored as a derived artifact.
- "Credit where due" section in the README under the four ideas, attributing
  each to its origin: spec-driven development to spec-kit and the BMAD method,
  TDD to Kent Beck plus the mutation-testing tools, compound engineering to
  Kieran Klaassen at Every, baseline semantics to RuboCop, FlakeHell,
  Betterer, and cargo-insta. Matching credit notes added to
  `docs/02-spec-driven-development.md`, `docs/04-compound-engineering.md`, and
  `docs/06-further-reading.md`.

## [0.1.0] - 2026-08-27

Initial public release.

### Added

- **Gate runner** (`gates/`): a baseline-aware, config-driven local CI runner.
  Node 20+, ESM, zero runtime dependencies. Parsers for pytest, vitest, tsc,
  eslint, go-test, junit-xml, plus an exit-code fallback. Baseline snapshot
  and compare, `--only-changed` against a merge base, `--json` output,
  per-gate timeouts, missing-toolchain skip semantics, and a self-test suite
  built on `node:test`.
- **The method** (`docs/`): eight pages covering the sensor/actuator model,
  why harnesses beat better models, spec-driven development, TDD with agents,
  compound engineering, local CI enforcement, and mappings for five agent
  tools.
- **Workflows** (`workflows/`): six scenario playbooks — new feature, bug from
  QA, missing fix downstream, Monday morning, joining a repo, and one honest
  week.
- **Starter kit** (`starter/`): a copy-in template with a spec pipeline CLI,
  11 rules, 11 skills, hooks, and adapters for Codex, Cursor, Kiro, and
  Antigravity.
- **Examples** (`examples/`): the same small notes app implemented on four
  stacks — Python/Flask, Node/React, Go, Java/Spring — each with its own gate
  config and specs.
- One-line installer (`install.sh`), an `AGENTS.md` for agents contributing to
  pagar itself, and CI that runs the self-tests and the Python, Node, and Go
  examples.

[Unreleased]: https://github.com/ridwanspace/pagar/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ridwanspace/pagar/releases/tag/v0.1.0
