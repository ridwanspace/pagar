---
description: API conventions. Single-call endpoint design (NON-NEGOTIABLE) with a closed exemption list, static routes before parameterized, schema validation at every boundary, registration in the composition root, honest health checks, error handling that leaks nothing, idempotency keys
paths:
  - "{{API_LAYER_DIR}}/**"
  - "{{SCHEMA_LAYER_DIR}}/**"
  - "{{COMPOSITION_ROOT}}"
---

# API design rules

> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/api.md` (committed).
> When a change makes the repo fact here wrong, fix BOTH. `/code-review` step 03b catches it.

## Single-call endpoints (NON-NEGOTIABLE: design this FIRST)

**One user-facing action equals one API call.** The server absorbs the orchestration. The
client sends one request and gets one composite response.

Shipping a flow that forces the client to chain calls, hold intermediate ids, and hand-roll
rollback when step 3 of 4 fails is a **defect**, not a style choice. Fix the endpoint, do not
document the chain. "It was cleaner on the server", "the resources are separate", and "REST
says one resource per endpoint" are not exemptions.

- **One composite request type.** Accept everything the whole flow needs, including inline
  nested payloads, so the client never has to create a parent resource first. Where the client
  may either reference an existing thing or create it inline, enforce exactly-one in the
  schema and return a validation error, never a surprise.
- **One composite response type.** Return every id and derived value the client needs next, so
  there is no mandatory follow-up GET to render the result screen. State and bootstrap
  endpoints follow the same rule: one screen's worth of data in one response, assembled in
  **one service call** with batched queries, not N calls the client fans out.
- **Accept an idempotency key** on any single-call endpoint that writes or triggers background
  or external work. A retry after a client timeout must return the original result, never a
  duplicate.
- **Non-critical side effects never fail the call.** Mail, analytics, cache warms, and usage
  bookkeeping go in a caught block with a logged warning. The core outcome still returns
  success.

**Where the orchestration lives:** the handler is a thin facade. Validate, call one service
method that composes the existing per-step services, shape the response. Multi-step writes that
must not half-apply are the service's job, one transaction or explicit compensation, never the
client's. Granular routes may still exist for clients that genuinely want one step. What is
banned is **the happy-path flow the client actually builds** needing more than one call.

### The only exemptions (closed list: name the one that applies, in the handler)

1. **Long-running work** that cannot finish inside a request budget. Return an accepted status
   with a task or status resource to poll. Enqueue the job, persist the job row, answer with
   the job id. Still **one** call to start it.
2. **Genuinely different auth scopes.** Two principals, for example one role submits and
   another approves. Two actors equals two calls.
3. **Unbounded payload.** A file upload must not be buffered into a JSON body. Upload first,
   then reference the resulting id in the one composite call.
4. **Client-driven branching.** A human must see intermediate output and *decide*, for example
   preview a template then choose. Not "the client finds it convenient to split".

Anything else: combine it. A flow that fits no exemption and cannot be made one call is a
design escalation to the user, not a decision to quietly ship the chain.

**Verifying it:** the API test drives the whole flow in a **single** request and asserts the
response carries every field the client needs next. If the test must make a second call to get
an id the client obviously needs, the endpoint is not done.

## Route shape

- **Declare static paths before parameterized ones**, and keep them grouped: `/task` before
  `/task/{id}`, `/` before `/{id}`. Some routers rank static segments above parameters
  regardless of declaration order and some do not. **Never rely on knowing which yours is.**
  When you add a static route beside a parameterized one, add the reachability assertion: a
  request without the required input must answer a validation, auth, or method error, **not a
  404 from the wrong handler**.
- ⚠ A parameterized route that swallows a static path is the worst kind of routing bug,
  because it **answers**. A 200 from the wrong handler looks like success. Check the status
  code AND the body.
- **Trailing slashes are part of the contract.** Match the neighbouring routes, do not
  "normalise" them. Clients hardcode the exact string.
- **Prefix style is a house convention, not a preference.** A new module copies the prefix
  style of its closest sibling. Do not retro-fit a version prefix onto existing routes, and do
  not double a prefix in both the module and the route.

## Schema validation at every boundary: never raw bags

Every request body, every query string, and every response goes through a declared schema
type. A handler that returns a hand-built untyped object next to a declared response type is a
**contract lie**: the generated spec documents one shape and the wire carries another.

- **Bound every client-controlled field** in the schema. String lengths, list sizes, numeric
  ranges, page sizes, enumerated values. Page size is server-enforced, never trusted.
- Validation failure returns your stack's validation error status with field-level detail.
  Do not catch it in the handler to downgrade it into a generic error.
- **Adding a field to a response schema:** set it on **every** return path with its TRUE value
  there, not a blanket default that is only right on the happy path. Ask "was this computed
  yet?", not "did this fail?".
- Custom field types live in one shared module. Reuse, do not re-implement per schema.

## Registration lives in the composition root

- **`{{COMPOSITION_ROOT}}` is the only place modules are registered.** A module registered
  nowhere is a shipped bug that the scoped test suite cannot see, because tests usually
  assemble their own minimal app.
- After adding a route: regenerate whatever committed API contract file you keep
  (`{{API_CONTRACT_FILE}}`, via `{{API_CONTRACT_REGEN_COMMAND}}`) and confirm the path renders
  in the generated docs. The contract file is part of the deliverable.
- Non-contract routes such as health probes are declared outside the spec by design. Do not
  add business routes there.

## Keep the health check honest

A health check that returns a hardcoded success proves the process answers requests, nothing
else. Your data store can be down and the orchestrator still sees healthy.

- Probe the real dependencies. Return an **unavailable** status when a probe fails, and keep
  the body machine-readable, because the client and the ops probes both key on it.
- Any new downstream dependency joins the probe **in the same change**.
- A startup connectivity check is not a liveness check. They answer different questions.

## Error handling: precise codes, no leaked internals

- Use a precise status with a **constant, client-safe message**. Not-found for an entity miss.
  Forbidden for a foreign tenant's row **only when existence is already public**, otherwise
  not-found. Conflict for a state conflict. A validation status for a well-formed request the
  business rules reject.
- ⚠ **Returning the raw exception text to the client leaks driver and vendor internals.** Log
  the exception with its traceback, answer a constant message.
- Re-raise your framework's own HTTP exceptions inside broad catch blocks, or a deliberate
  not-found becomes a server error.
- Errors leak nothing: no stack, no "that user exists", no driver text, no internal ids the
  caller does not own.

## Authorization decorators

List the real ones from `{{AUTH_MODULE}}` in a table here: name, what it allows, where it
lives. Then the two rules that matter:

- The auth check is the **innermost** wrapper, so it fires before any schema work. A mismatch
  between the two auth failure codes in a test is usually decorator ordering, not a broken
  fixture.
- The decorators typically check **role only**. **Tenant and ownership scoping is the handler
  or service's job.** See `security.md`.

## Idempotency keys

If your stack has an idempotency helper, name it here with its real semantics: what key, what
storage, what happens on a repeat while the first is still running, and what happens when the
backing store is unavailable.

Two things to write down honestly, because they bite:

- **A cache-backed idempotency helper is a cache, not a constraint.** Two concurrent first
  requests can both miss. A genuinely race-free guarantee needs a unique constraint in the
  data store. See `backend-practices.md`.
- **Whether it is opt-in per route.** If it is, then every route that does not opt in
  **silently ignores the key**, and a client retry duplicates the write. Say which routes have
  it today. That count is the real risk surface.
