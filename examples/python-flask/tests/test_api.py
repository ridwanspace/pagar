"""API tests. These use the Flask test client, which supplies the app context.

The trap recorded in specs/epic-01-notes/story-01-publish-note.md is here: calling
`create_app()` and then touching anything that needs a request or app context
without going through the client raises
"RuntimeError: Working outside of application context". The fixture below is the
fix, and every test in this file goes through `client`.
"""

import pytest

from app.api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    # The test client pushes a request context per request, so handlers can use
    # `request` and `jsonify` normally.
    with app.test_client() as c:
        yield c


def _create(client, title="Standup", body="we shipped the gate runner"):
    resp = client.post("/notes", json={"title": title, "body": body})
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()


def test_health_is_honest(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "notes": 0}


def test_create_returns_draft(client):
    body = _create(client)
    assert body["status"] == "draft"
    assert body["published_at"] is None


def test_create_with_empty_title_returns_422(client):
    resp = client.post("/notes", json={"title": "", "body": "x"})
    assert resp.status_code == 422
    assert resp.get_json()["field"] == "title"


def test_publish_returns_published_note(client):
    note = _create(client)
    resp = client.post(f"/notes/{note['id']}/publish")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["status"] == "published"
    assert payload["published_at"] is not None


def test_publish_empty_body_returns_422(client):
    note = _create(client, body="")
    resp = client.post(f"/notes/{note['id']}/publish")
    assert resp.status_code == 422
    assert resp.get_json()["field"] == "body"


def test_publish_twice_returns_200_both_times(client):
    """The idempotency edge case at the HTTP boundary. A retried POST is a 200,
    not a 409, and the timestamp does not move."""
    note = _create(client)
    first = client.post(f"/notes/{note['id']}/publish")
    second = client.post(f"/notes/{note['id']}/publish")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.get_json()["published_at"] == first.get_json()["published_at"]


def test_publish_unknown_id_returns_404(client):
    resp = client.post("/notes/nope/publish")
    assert resp.status_code == 404


def test_two_apps_do_not_share_a_store(client):
    """Each create_app() gets its own dict. If this ever fails, the store leaked
    to module scope and tests started depending on execution order."""
    other = create_app().test_client()
    _create(client)
    assert other.get("/health").get_json()["notes"] == 0
