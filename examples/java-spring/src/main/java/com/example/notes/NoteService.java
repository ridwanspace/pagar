package com.example.notes;

import java.time.Clock;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.stereotype.Service;

/**
 * Domain rules for a meeting note.
 *
 * <p>The store is a ConcurrentHashMap rather than a JPA repository on purpose.
 * The publish rule is the part worth testing, and a database would make its tests
 * need a container, a schema, and a transaction. See the Dev agent record in
 * specs/epic-01-notes/story-01-publish-note.md for the rollback surprise that
 * made keeping this layer persistence-free worth the trade.
 *
 * <p>The Clock is injected rather than called statically, so a test can pin time
 * without a static mock.
 */
@Service
public class NoteService {

  private final Map<String, Note> notes = new ConcurrentHashMap<>();
  private final AtomicLong nextId = new AtomicLong();
  private final Clock clock;

  public NoteService(Clock clock) {
    this.clock = clock;
  }

  /**
   * Creates a draft note.
   *
   * <p>Title is required. Body may be empty at create time because a note is
   * often started before there is anything to write in it. The body rule bites at
   * publish time instead.
   */
  public Note create(String title, String body) {
    String safeTitle = title == null ? "" : title.trim();
    String safeBody = body == null ? "" : body;

    if (safeTitle.isEmpty()) {
      throw new ValidationException("title", "title must not be empty");
    }
    if (safeBody.length() > Note.MAX_BODY_LENGTH) {
      throw new ValidationException(
          "body", "body must be at most " + Note.MAX_BODY_LENGTH + " characters");
    }

    String id = "n" + nextId.incrementAndGet();
    Note note = new Note(id, safeTitle, safeBody, NoteStatus.DRAFT, null);
    notes.put(id, note);
    return note;
  }

  /** Returns one note, or throws NoteNotFoundException. */
  public Note get(String id) {
    return Optional.ofNullable(notes.get(id)).orElseThrow(() -> new NoteNotFoundException(id));
  }

  /**
   * Publishes a note.
   *
   * <p>Three rules, and each one has a test:
   *
   * <ol>
   *   <li>A note with a blank body cannot be published. Whitespace only counts as
   *       blank, so "   " is rejected the same as "".
   *   <li>Publishing is idempotent. Publishing an already published note returns
   *       the note unchanged and is not an error. Callers retry on timeouts, and a
   *       retry must not look like a failure or move publishedAt.
   *   <li>An unknown id is a NoteNotFoundException.
   * </ol>
   *
   * <p>compute() holds a per-key lock, so two concurrent publishes of the same id
   * cannot both stamp a timestamp.
   */
  public Note publish(String id) {
    if (!notes.containsKey(id)) {
      throw new NoteNotFoundException(id);
    }

    return notes.compute(
        id,
        (key, existing) -> {
          if (existing == null) {
            throw new NoteNotFoundException(key);
          }
          // Rule 2 comes before rule 1 deliberately. A note that is already
          // published passed the body check once. Re-running the check on a retry
          // would let an edit that blanked the body turn a successful publish
          // into a late failure.
          if (existing.status() == NoteStatus.PUBLISHED) {
            return existing;
          }
          if (existing.body().isBlank()) {
            throw new ValidationException("body", "cannot publish a note with an empty body");
          }
          return existing.published(Instant.now(clock));
        });
  }

  /** Replaces a stored note. Used by tests that need to blank a body after publish. */
  public void replace(Note note) {
    notes.put(note.id(), note);
  }

  /** How many notes are stored. Used by the health endpoint. */
  public int count() {
    return notes.size();
  }
}
