"""Domain tests. No Flask, no app context, no client.

These run in milliseconds because they touch nothing but a dict. That speed is
why the publish rule lives outside the Flask layer.
"""

from datetime import UTC, datetime

import pytest

from app.notes import (
    DRAFT,
    MAX_BODY_LENGTH,
    PUBLISHED,
    NotFoundError,
    ValidationError,
    create_note,
    publish_note,
)

FIXED_NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
LATER = datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC)


@pytest.fixture
def store():
    return {}


def test_create_note_starts_as_draft(store):
    note = create_note(store, "n1", "Standup", "we discussed the release")
    assert note.status == DRAFT
    assert note.published_at is None
    assert store["n1"] is note


def test_create_note_rejects_empty_title(store):
    with pytest.raises(ValidationError) as exc:
        create_note(store, "n1", "   ", "body")
    assert exc.value.field == "title"


def test_create_note_rejects_oversized_body(store):
    with pytest.raises(ValidationError) as exc:
        create_note(store, "n1", "Standup", "x" * (MAX_BODY_LENGTH + 1))
    assert exc.value.field == "body"


def test_publish_happy_path_sets_status_and_timestamp(store):
    create_note(store, "n1", "Standup", "we shipped the gate runner")
    note = publish_note(store, "n1", now=lambda: FIXED_NOW)
    assert note.status == PUBLISHED
    assert note.published_at == FIXED_NOW


def test_publish_rejects_empty_body(store):
    create_note(store, "n1", "Standup", "")
    with pytest.raises(ValidationError) as exc:
        publish_note(store, "n1", now=lambda: FIXED_NOW)
    assert exc.value.field == "body"
    assert store["n1"].status == DRAFT


def test_publish_rejects_whitespace_only_body(store):
    """Whitespace is the edge case a naive `if not body` check gets right and a
    naive `if body is None` check gets wrong."""
    create_note(store, "n1", "Standup", "   \n\t  ")
    with pytest.raises(ValidationError):
        publish_note(store, "n1", now=lambda: FIXED_NOW)


def test_publish_is_idempotent(store):
    """The edge case. A second publish is not an error and does not move the
    timestamp. The injected clock returns a different time on the second call,
    so a bug that re-stamps published_at fails this test loudly."""
    create_note(store, "n1", "Standup", "we shipped the gate runner")
    first = publish_note(store, "n1", now=lambda: FIXED_NOW)
    second = publish_note(store, "n1", now=lambda: LATER)

    assert second.status == PUBLISHED
    assert second.published_at == FIXED_NOW, "second publish must not re-stamp published_at"
    assert first is second


def test_publish_of_already_published_note_survives_a_blanked_body(store):
    """Guards the rule order inside publish_note. Once published, the note stays
    published even if the body was later emptied. Swapping the two checks makes
    this test go red, which is what proves the order is deliberate."""
    create_note(store, "n1", "Standup", "content")
    publish_note(store, "n1", now=lambda: FIXED_NOW)
    store["n1"].body = ""

    note = publish_note(store, "n1", now=lambda: LATER)
    assert note.status == PUBLISHED
    assert note.published_at == FIXED_NOW


def test_publish_unknown_id_raises_not_found(store):
    with pytest.raises(NotFoundError):
        publish_note(store, "does-not-exist", now=lambda: FIXED_NOW)
