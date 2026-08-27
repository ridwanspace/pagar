---
description: Server-side engineering practices. Idempotency, N+1 queries, mandatory pagination, transactions and partial failure, concurrency, timeouts and retries, observability, typed config and secrets, input bounding, API compatibility
paths:
  - "{{SERVICE_LAYER_DIR}}/**"
  - "{{API_LAYER_DIR}}/**"
  - "{{BACKGROUND_JOB_DIR}}/**"
---

# Server-side engineering practices

> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/practices.md` (committed).

Route and payload shape live in `api-design.md`. Layering lives in `architecture.md`. This file
is about what makes a server correct **under retries, load, and partial failure**: the three
conditions no unit test reproduces by default.

## Idempotency (every non-GET that matters)

Networks retry. If your client retries by design, a client timeout does **not** mean the write
did not happen.

- Put the idempotency guard on any route that creates a resource, enqueues a job, sends mail,
  or bills. Same key returns the original success. A repeat while the first is in flight
  returns a conflict, which the client treats as "retry later".
- **A cache-backed guard is not a constraint.** For anything with money or quota consequences,
  enforce at the **storage layer**: a unique constraint on the natural key, or on
  `(scope, idempotency_key)`, is the only race-free check. `if exists: return` before an insert
  is a time-of-check/time-of-use bug under concurrency.
- **State transitions check current state first.** A background job re-delivered after a worker
  crash, or a webhook arriving twice, must no-op when the row is already terminal.
- **Background jobs must be re-runnable.** If your worker acknowledges late, a hard kill
  mid-job re-queues it. Write the tracking row, then publish. Inside the job, look up state
  before doing work.

## Performance: the two rules that catch most regressions

**1. No query inside a loop.** That is an N+1. Batch-fetch, then look up in memory.

```
# FORBIDDEN: one query per item
for item in items:
    owner = fetch_user(item.user_id)

# REQUIRED: one query, then an in-memory map
owners = {u.id: u for u in fetch_users_by_ids({i.user_id for i in items})}
for item in items:
    owner = owners.get(item.user_id)
```

Or load the relationship eagerly at the query that builds the page. *Exception*: a small fixed
set, under about five, where batching costs more complexity than it saves.

**2. Slow work leaves the request.** Each request holds a worker slot. Anything that runs a
model, calls a slow third party, or renders a large document belongs in a background job with
an accepted status and a pollable task resource. A composite endpoint fans out **inside one
service call**. It never does N things serially in a handler when one batched query would do.

Also: never let a summary endpoint call the full detailed path and throw away most of it. Give
every recursive or retrying helper an explicit termination guard.

## Pagination: every list endpoint, no exceptions

An unbounded list endpoint is a latent outage. Every collection response is paginated with a
**server-enforced max page size** declared in the schema, and returns the total, the page, and
the page size so the client can page.

Prefer keyset pagination for large or live-updating sets. Deep offset degrades, and it **skips
rows** when data shifts under the reader.

A client that paginates in its own memory is not pagination. That is not a licence to return
everything.

## Transactions and partial failure

- A multi-step write that must not half-apply runs in **one transaction**, one commit at the
  end and a rollback in the failure path, **or** has an explicit **compensating action** per
  step. Decide which, and say which in the docstring.
- **Do not hold a transaction open across a network call.** Stage the local work, commit, call
  out, then record the outcome. Or write a job row and let the worker make the call.
- **Non-critical side effects never fail the request.** Mail, cache, metrics, usage logging go
  in a caught block with a logged warning. If it must not be lost, it is a **persisted outbox
  row**, not a fire-and-forget.
- Know the lifetime of your data-store session. In a background job, build your own context.
  Never reuse a session across jobs.

## Concurrency

- Read-modify-write on a shared row, quota counters, usage totals, billing anchors, is a
  lost-update bug. Use an **atomic update** (`SET used = used + :n WHERE used + :n <= quota`)
  or **optimistic locking** with a version column in the WHERE clause. Handle the conflict, do
  not retry blindly forever.
- Check-then-act across two statements is a race. Push the invariant into a constraint or into
  the atomic update.
- Two workers can touch the same row. A job must tolerate the other having moved it.

## Timeouts, retries, resilience

- **Every outbound call gets an explicit timeout.** A client with no timeout turns a slow
  dependency into worker-pool exhaustion, which presents as "the whole service is down".
- Retries: **bounded attempts, exponential backoff with jitter**, and only for idempotent
  operations or ones carrying an idempotency key. Never an unbounded loop.
- Fail fast on a dependency already known to be down. A job's hard time limit is a safety net,
  not a budget.

## Observability

- **Structured logging through your logging library, never a print statement.** A print goes
  nowhere useful in a container. Prefer lazy format arguments over eager string interpolation
  in log calls, so the aggregator can group them.
- **Never log secrets, personal data, or user content.** No tokens, passwords, or API keys, and
  no user-supplied body text. Log ids, durations, and counts. Content in logs is a data-leak
  surface that survives every later access-control fix.
- If you have tracing, a request or job id already rides the span. Put that in your log lines
  rather than inventing a second correlation id.
- Log at the boundary where you have context. Do not log-and-rethrow at every layer.

## Configuration and secrets

- **Config comes from the environment**, read once through one typed config module. Not
  scattered environment reads through the service layer. **Do not build a second source of
  truth** beside the first one.
- **Every new environment variable ships in `{{ENV_EXAMPLE_FILE}}`** with an empty or
  placeholder value, in the same change.
- **Never rely on a committed default in a deployed environment, and never add a new
  secret-bearing default.** See `security.md`.
- Validate config at startup and fail fast where a feature is unusable without it. A missing
  key should be a clear boot-time refusal, never a server error discovered in production.

## Input validation and safety

- Validate at the **boundary** with your schema layer, so services can then trust their inputs.
- **Bound everything a client controls**: string lengths, list sizes, page sizes, upload sizes,
  numeric ranges. An unbounded field is a memory and denial-of-service vector, doubly so when
  it feeds a model prompt or a document renderer.
- **Never interpolate client input into a query.** Bound parameters only, everywhere, including
  in the places that use a raw cursor.
- Authorization is checked **server-side on every request**, against the resource being
  touched. Never inferred from a client-supplied role, never "the client hides it".

## API versioning and compatibility

- Additive changes, a new optional field, a new endpoint, are safe. **Removing or renaming a
  field, tightening validation, or changing a status code is breaking.**
- ⚠ The client in your own repo may move in step with you. **Deployed environments run older
  client builds than your default branch.** A change that is safe in your working tree is a
  break in staging. Deprecate on a timeline, do not ship it silently.
- New response fields are optional with defaults, so older client builds keep parsing. Prefer
  additive enum values over redefining existing ones.
- After any contract change, regenerate `{{API_CONTRACT_FILE}}` in the same commit.

## Wire code immediately

Do not write a service method with a "call this later" comment. If it exists, it is wired at
every call site **in the same change**. Orphaned helpers rot, and the gap is invisible to a
green test suite.
