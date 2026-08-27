"""Flask layer. Thin on purpose: parse, call the domain, map errors to status codes.

The store is an in-memory dict held on the app object. A real project puts a
database here. Keeping it in memory keeps the example about the workflow rather
than about persistence setup.
"""

from __future__ import annotations

import uuid

from flask import Flask, jsonify, request

from app.notes import (
    Note,
    NotFoundError,
    ValidationError,
    create_note,
    publish_note,
)


def _serialize(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "body": note.body,
        "status": note.status,
        "published_at": note.published_at.isoformat() if note.published_at else None,
    }


def create_app() -> Flask:
    app = Flask(__name__)
    # One store per app instance, so every test gets a clean one for free.
    store: dict[str, Note] = {}
    app.config["NOTE_STORE"] = store

    @app.errorhandler(ValidationError)
    def _on_validation_error(err: ValidationError):
        return jsonify(
            {"error": "validation_error", "field": err.field, "message": err.message}
        ), 422

    @app.errorhandler(NotFoundError)
    def _on_not_found(err: NotFoundError):
        return jsonify({"error": "not_found", "message": "note not found"}), 404

    @app.get("/health")
    def health():
        # Honest health check. The only dependency is the store, so we say so.
        return jsonify({"status": "ok", "notes": len(store)}), 200

    @app.post("/notes")
    def post_note():
        payload = request.get_json(silent=True) or {}
        note = create_note(
            store,
            note_id=str(uuid.uuid4()),
            title=payload.get("title", ""),
            body=payload.get("body", ""),
        )
        return jsonify(_serialize(note)), 201

    @app.get("/notes/<note_id>")
    def get_note(note_id: str):
        note = store.get(note_id)
        if note is None:
            raise NotFoundError(note_id)
        return jsonify(_serialize(note)), 200

    @app.post("/notes/<note_id>/publish")
    def post_publish(note_id: str):
        # One user action, one call. The client does not read, then decide, then
        # write. Idempotency lives in the domain so a retry is safe.
        note = publish_note(store, note_id)
        return jsonify(_serialize(note)), 200

    return app


app = create_app()
