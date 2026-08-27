---
description: The abuse-resistance floor, server-side authorization, UI gates are not authorization, secrets in environment only, bounded inputs, fail closed, rate limiting on expensive surfaces, untrusted content
paths:
  - "{{API_LAYER_DIR}}/**"
  - "{{AUTH_MODULE}}"
  - "{{CLIENT_SOURCE_DIR}}/**"
---

# Security rules: the abuse-resistance floor

> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/security.md` (committed).
> ⚠ **The committed page states the rules without the inventory.** This local file may name
> the exact file and line of a known committed secret, because it is git-excluded. The
> committed page never does. Copying this file wholesale into a shared doc publishes a map of
> your unrotated credentials.

**The client is an untrusted input device.** Every endpoint re-derives anything with role,
tenant, quota, or cost consequences from server-side state. The caller only nominates WHAT it
wants. It never says who it is, what it costs, or how often it may ask.

## Authorization is server-side, per request

- Every non-public route carries an auth check as its **innermost** wrapper, so an
  unauthenticated or unauthorized caller is rejected before any schema work runs.
- **If your roles have aliases or a legacy naming**, compare through the normalizing function,
  never against the raw stored value. A legacy role name that skips normalization silently
  loses access, and the symptom looks like a data bug.
- The role check is not the whole check. **Tenant and ownership scoping is the handler or
  service's job**: filter by the caller's tenant unless the caller is a super-role. Any new
  route on tenant-owned data gets the same check. A foreign row answers **not-found**, not
  forbidden, unless its existence is already public.

## UI gates are UX, not security

Route guards, feature flags, and a hidden menu item **hide** screens. They **deny** nothing.

- Never "fix" an authorization bug purely in the client.
- Never let a client-supplied role field influence a server decision. If the client stores a
  role for display, it is for display.
- A feature-flagged-off screen must still be denied server-side when the data is sensitive.
- If the client holds an opaque token, keep it opaque. It is stored and forwarded, never
  decoded for a decision. The server's own identity endpoint is the source of truth for who
  the user is.

## Secrets live in the environment, never in code

- **No credential, API key, token, password, or private key is ever written into source.** Not
  a constant, not a fallback default, not a test fixture, not an automation script.
- **Every new environment variable ships in `{{ENV_EXAMPLE_FILE}}`** with an empty or
  placeholder value.
- ⚠ **Anything with a client-side build prefix is compiled into the public bundle.** No secret
  ever gets that prefix. If the browser needs a capability, the server proxies it. This is why
  local test credentials should be deliberately un-prefixed.
- **Never log a secret.** Keep authorization header values and payloads out of anything logged
  or sent to an error tracker.
- ⚠ **"It is masked on read" says NOTHING about what you SENT.** A field the server returns
  masked is plaintext in the create or update payload, and a log context built from the
  submitted payload publishes it. Redact from the **submitted** copy, and drop the key entirely
  rather than substituting a marker.
- **A key that touched a log, a commit, or an error report is burned. Rotate it, do not scrub
  it.** Removing it from the working tree does not remove it from history, from the log
  aggregator, or from anyone's local clone.
- **If you build a trust mechanism on a config key**: signed tokens, share links, signed
  download URLs, the code **must refuse to operate while the key is the committed default**.
  Fail closed at both ends: raise on mint, treat as unverified on verify, and test both. A
  warning log is not enough. With a public default, the mechanism does not degrade, it
  **inverts**: anyone can forge what it was built to prove.

### Recording existing committed-secret debt

If your repo already has committed secrets, list them here with file and line, dated, and add:
**do not add a single new one, and do not copy the pattern.** "The others have defaults" is how
the count grows. Keep this inventory out of any committed document.

## Bounded inputs: every public and unauthenticated surface

- **Schema-bound every body.** Max length on strings, max size on lists, ranges on numbers and
  page sizes. An unbounded string is an amplification vector into whatever stores, mails, or
  prompts with it.
- **File uploads validate by probed content, not by the client's filename extension or declared
  content type.** Reject before the file reaches any processing pipeline. Reuse the one
  validator, do not hand-roll a second check in a handler.
- **Capability-shaped URLs**: share links, download URLs, task ids. Are unguessable, scoped
  to a tenant, and expiring where the product allows. Ownership is re-checked on **every hit**,
  not only at mint time.
- **Fail closed.** Missing config or a missing environment variable means **deny**, never
  skip-the-check. ⚠ If any of your tooling leaves a surface **open** when its credentials are
  unset, an unauthenticated docs page is the classic, write that down here, and confirm the
  variable is set in every deployed environment.

## Rate limiting: wire it when you CREATE the surface

If your service has no rate limiter, **say so here, dated**. That is a finding, not a blank.
Then list the surfaces that must be limited the day they are added or next touched:

| Surface | Key | Why |
|---|---|---|
| Model or AI endpoints | `llm:{tenant}` | tokens are money, an unthrottled client loop is an unbounded bill |
| Expensive compute submits | `{job}:{tenant}` | finite worker minutes |
| Credential endpoints. Login, password change | `{flow}:{ip}` | brute force |
| Email-triggering flows | `{flow}:{user\|ip}` | provider bills and sender reputation |
| Any unauthenticated mutation | `{route}:{ip}` | it is the internet |

Semantics: over the limit returns a rate-limit status **with a retry-after hint**, never a
silent drop. Durable allowances such as paid quotas belong in the data store, never in the
limiter. **A quota is not a limiter**: a quota says how much you may use in total, a limiter
says how fast.

⚠ **A missing rate limiter is a decision to raise, not a helper to assume.** A story that lets
the client drive an expensive surface unbounded is a defect, not an enhancement.

## Untrusted content

- Model output and user-supplied text rendered into a UI is **hostile input**. Keep the
  renderer escaping. Never reach for a raw-HTML injection API for convenience.
- The same applies server-side. Text that flows into a generated document must be escaped for
  **that** target format. HTML escaping does not protect a spreadsheet or a document renderer.
- **Prompt injection is a real vector** wherever user text reaches a model prompt. Keep system
  instructions server-side, and never let a client field alter the prompt template.

## When to escalate

A change touching token storage, auth checks, tenant scoping, file upload or validation, share
links, model-calling endpoints, rendering of untrusted content, or any new client-side-public
variable gets a security review before commit.
