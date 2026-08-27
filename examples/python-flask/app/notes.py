"""Domain rules for a meeting note.

This module holds no Flask import on purpose. The publish rule is the part worth
testing, and keeping it free of the web framework means its tests need no app
context, no test client, and no request. See specs/epic-01-notes/story-01-publish-note.md
for the trap that made this split non-negotiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

DRAFT = "draft"
PUBLISHED = "published"

# A body longer than this is almost certainly a paste accident, not a note.
MAX_BODY_LENGTH = 20_000


class ValidationError(Exception):
    """Raised when input breaks a domain rule. The API layer turns this into a 422."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.message = message


class NotFoundError(Exception):
    """Raised when a note id does not exist. The API layer turns this into a 404."""


@dataclass
class Note:
    id: str
    title: str
    body: str
    status: str = DRAFT
    published_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(UTC)


def create_note(store: dict[str, Note], note_id: str, title: str, body: str) -> Note:
    """Add a draft note to the store.

    Title is required. Body may be empty at create time because a note is often
    started before there is anything to write in it. The body rule bites at
    publish time instead.
    """
    if not title or not title.strip():
        raise ValidationError("title", "title must not be empty")
    if len(body) > MAX_BODY_LENGTH:
        raise ValidationError("body", f"body must be at most {MAX_BODY_LENGTH} characters")
    note = Note(id=note_id, title=title.strip(), body=body)
    store[note_id] = note
    return note


def publish_note(store: dict[str, Note], note_id: str, now=_utcnow) -> Note:
    """Publish a note.

    Three rules, and each one has a test:

    1. A note with a blank body cannot be published. Whitespace only counts as
       blank, so "   " is rejected the same as "".
    2. Publishing is idempotent. Publishing an already published note returns the
       note unchanged and is not an error. Callers retry on timeouts, and a retry
       must not look like a failure or move published_at.
    3. An unknown id is a NotFoundError.

    `now` is injected so a test can pin the clock without patching the module.
    """
    note = store.get(note_id)
    if note is None:
        raise NotFoundError(note_id)

    # Rule 2 comes before rule 1 deliberately. A note that is already published
    # passed the body check once. Re-running the check on a retry would let an
    # edit that blanked the body turn a successful publish into a late failure.
    if note.status == PUBLISHED:
        return note

    if not note.body or not note.body.strip():
        raise ValidationError("body", "cannot publish a note with an empty body")

    note.status = PUBLISHED
    note.published_at = now()
    return note
