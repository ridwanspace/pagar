---
description: Layering and dependency direction, where wiring lives, where background work lives, change-minimally discipline in a repo you share with other people
paths:
  - "{{SOURCE_ROOT}}/**"
---

# Architecture rules

> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/architecture.md` (committed).
> This file may carry personal-workflow detail the committed page must not. When a change
> makes the repo fact here wrong, fix BOTH. `/code-review` step 03b is the checkpoint that
> catches it.

**Fill this file in from your codebase as it exists, not as you wish it were.** The value of
this rule is that it describes the real structure, so a new change fits in instead of starting
a second structure beside it. A rule that describes an aspiration teaches the agent to write
code that does not match its neighbours.

## Layers and where things go

Name your layers, one line each, with the real directory. The common shape:

- **`{{API_LAYER_DIR}}`**: the transport edge. One module per domain. Handlers stay thin:
  validate the request, call one service function, shape the response. No business logic, no
  direct data access, no background-job orchestration beyond "enqueue and record the job id".
- **`{{SERVICE_LAYER_DIR}}`**: business logic. This is where a story's real work lives.
  One module per domain. Naming is often inconsistent in a repo with history. **Copy the
  closest sibling's naming style, do not rename existing ones.**
- **`{{DATA_LAYER_DIR}}`**: persistence models and queries.
- **`{{SCHEMA_LAYER_DIR}}`**: the request and response types at the boundary. Handlers never
  accept or return an untyped bag. See `api-design.md`.
- **`{{SHARED_DIR}}`**: small cross-cutting helpers. Watch this directory. It becomes the
  dumping ground for domain logic that nobody wanted to place, and once it does, the layering
  above is decorative.

## Dependency direction (hard rule)

`api` → `services` → `data`. Services never import the transport layer. Data models never
import services. Cross-domain needs go through the other domain's **service**, never its
models or its private functions.

This is the one rule that keeps a codebase from becoming a graph. When it is broken once,
every later change has a precedent for breaking it again.

## Wiring lives in one place

- **`{{COMPOSITION_ROOT}}` is the single wiring point.** Routes, middleware, dependency
  registration, startup checks. **A module that nothing registers does not exist.** It can be
  fully green under every gate you own and still be unreachable, because no gate asserts
  reachability.
- After adding a route or a module, verify it is reachable, not just that it compiles. A test
  that imports a handler proves the handler exists. It does not prove a client can reach it.
- Background work: `{{BACKGROUND_JOB_DIR}}`. Note the queue or worker each job runs on, and
  **where routing configuration is declared**. ⚠ If your stack declares queue routing in more
  than one file, they must stay identical. A job routed in one file and not the other is
  published to one queue and consumed from another, and no test sees it. Write that trap down
  here with the real file paths.

## Change-minimally discipline

- Prefer the smallest diff that solves the task. Match the neighbouring code's idioms even
  where a rule here would suggest otherwise, then raise the mismatch instead of silently
  refactoring.
- New domain? Copy the shape of the closest existing one, all the way through: transport
  module, schema module, service module, data model, tests, and a migration if a table
  changes.
- **Do not reorganize another engineer's large module as a side effect of your story.** Flag
  it. A refactor bundled into a feature diff makes the feature unreviewable and collides with
  whatever branch that engineer has open.
- Legacy or pre-refactor code kept for reference is **read only**. Useful for seeing what a
  behaviour was. Never import from it, never fix bugs in it, and never cite it as current
  behaviour.
