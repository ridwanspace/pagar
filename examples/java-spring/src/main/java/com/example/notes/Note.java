package com.example.notes;

import java.time.Instant;

/**
 * One meeting note.
 *
 * <p>A record, so it is immutable and every "change" produces a new value. That
 * removes a whole class of bug where one caller mutates a note another caller is
 * still holding.
 */
public record Note(String id, String title, String body, NoteStatus status, Instant publishedAt) {

  /** A body longer than this is almost certainly a paste accident, not a note. */
  public static final int MAX_BODY_LENGTH = 20_000;

  /** Returns a copy marked published at the given instant. */
  public Note published(Instant at) {
    return new Note(id, title, body, NoteStatus.PUBLISHED, at);
  }

  /** Returns a copy with a different body. Used by tests that blank a body. */
  public Note withBody(String newBody) {
    return new Note(id, title, newBody, status, publishedAt);
  }
}
