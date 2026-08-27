# PRD: Meeting Notes (React reference slice)

**Status:** active
**Owner:** platform team
**Last updated:** 2026-08-26

## Problem

People take meeting notes in a dozen places and nobody can tell which ones are final.
A note that is still being edited looks exactly like a note the team has agreed on.

## Scope

One domain object, a note, with two operations: create and publish. Publishing is the
act that turns a working draft into something other people can rely on.

Out of scope for this slice: editing a published note, unpublishing, sharing,
permissions, search, and storage that survives a restart. Each of those needs a rule
nobody has written yet, and inventing one here would be guessing.

## Key decisions (locked)

Locked means a change needs a new decision recorded here, not a code review comment.

| ID | Decision | Why | Consequence if broken |
| --- | --- | --- | --- |
| D1 | Publish is idempotent. A second publish returns 200 and does not move `published_at`. | Clients retry on timeouts. A retry that 409s makes callers write compensating logic they will get wrong. | Duplicate publish notifications, and an audit trail whose timestamps drift on every retry. |
| D2 | An empty or whitespace-only body cannot be published. | A published note is a claim that content exists. An empty one is worse than no note. | Readers open a published note and find nothing, and stop trusting the published flag. |
| D3 | The body rule is checked at publish, not at create. | Notes get started before there is anything to write in them. Blocking create makes people keep notes outside the tool. | Users work around the tool and it stops reflecting reality. |
| D4 | The already-published check runs BEFORE the body check. | A note that was published once passed the body rule once. Re-checking on a retry lets a later edit turn a past success into a new failure. | A retried publish fails for a reason that did not exist when the publish first succeeded. |
| D5 | Domain rules live in `src/notes.ts` and import no React. | Rules tested through a render need a DOM, an `act()` wrapper, and a user-event round trip. | Rule tests get slow, then get skipped, then the rules drift. |
| D6 | The clock is injected, never called inside the rule. | An idempotency test has to prove the timestamp did NOT move. That needs two different times on demand. | The test passes for the wrong reason on a coarse clock and hides a re-stamp bug. |
| D7 | `publishNote` returns the SAME object reference when nothing changed. | React re-renders on a new reference. A retry that produces a fresh object re-renders the whole list for no reason. | The list flashes on every retried publish, and memoization downstream stops working. |

## Data model

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Server generated, opaque to the client. |
| `title` | string | Required, trimmed. |
| `body` | string | May be empty in draft. Max 20000 characters. |
| `status` | `draft` \| `published` | No third state without a new decision. |
| `published_at` | ISO 8601 or null | Set once, by D1. Null while a draft. `publishedAt` is an ISO 8601 string rather than a `Date`, so it compares by value in a test. |

## API

| Method | Path | Success | Failure |
| --- | --- | --- | --- |
| POST | `/notes` | 201 with the note | 422 on a blank title or an oversized body |
| GET | `/notes/{id}` | 200 with the note | 404 |
| POST | `/notes/{id}/publish` | 200 with the note | 422 on a blank body, 404 on unknown id |

One user action is one call. The client does not read the note, decide locally, then write.

## Open questions

| ID | Question | Blocks | Owner |
| --- | --- | --- | --- |
| OQ-1 | Should an editor be able to unpublish? | A `PUBLISHED -> DRAFT` transition, which D-nothing covers today. | product |
| OQ-2 | Does editing a published note republish it, or fork a new version? | The edit endpoint, which is out of scope for this slice. | product |
