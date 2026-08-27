# Security policy

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on this repository
(**Security → Report a vulnerability**). Do not open a public issue for
anything security-sensitive. You should get a response within a few days.

## Scope notes worth knowing

- The gate runner **executes shell commands from `gates.config.json` by
  design**. That file is authored by you, like a Makefile or a CI workflow.
  Do not copy a gate config from a source you do not trust and run it.
- The starter kit's hooks and helper scripts run locally on your machine with
  your permissions. Review anything you copy in, the same as any other code.
- pagar has **zero runtime dependencies**. The supply-chain surface is the
  Node standard library plus the code in this repository. There is nothing
  for a dependency-confusion attack to attach to, and we intend to keep it
  that way: PRs adding a runtime dependency to `gates/` will be declined.

## Supported versions

The `main` branch is the only supported version. Releases are tagged from it.
