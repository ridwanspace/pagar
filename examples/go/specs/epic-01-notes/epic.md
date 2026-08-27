# Epic 01: Notes

**Status:** in_progress
**PRD:** ../prd.md

## Goal

A note can be created as a draft and published once it has content. Publishing survives
a retry.

## Feature IDs

| ID | Feature | PRD decisions | Story |
| --- | --- | --- | --- |
| FR-01-01 | Create a draft note with a required title | D3 | story-01-publish-note.md |
| FR-01-02 | Reject a publish when the body is blank | D2 | story-01-publish-note.md |
| FR-01-03 | Publish is idempotent and keeps the first timestamp | D1, D4, D6 | story-01-publish-note.md |
| FR-01-04 | Unknown ids return 404 rather than 500 | none | story-01-publish-note.md |

## Stories

| # | Story | Status |
| --- | --- | --- |
| 01 | [Publish a note](story-01-publish-note.md) | done |

## Out of scope

Editing, unpublishing, permissions, and durable storage. See PRD "Out of scope" and OQ-1.

## Definition of done for the epic

- Every feature ID above has at least one test that has been watched fail.
- `go vet ./...`, `gofmt -l .`, and `go test -race ./...` are green through the gate runner.
- The idempotency test has been mutation-verified: break the rule, watch it go red.
