# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
