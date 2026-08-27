/**
 * Domain rules for a meeting note.
 *
 * This module imports no React. The publish rule is the part worth testing, and
 * keeping it out of the component means its tests need no DOM, no render, and no
 * act() wrapper. See specs/epic-01-notes/story-01-publish-note.md for the trap
 * that made the split worth writing down.
 */

export type NoteStatus = "draft" | "published";

export interface Note {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly status: NoteStatus;
  /** ISO 8601 string, or null while the note is a draft. */
  readonly publishedAt: string | null;
}

/** A body longer than this is almost certainly a paste accident, not a note. */
export const MAX_BODY_LENGTH = 20_000;

/** Thrown when input breaks a domain rule. The UI turns this into an inline message. */
export class ValidationError extends Error {
  constructor(
    readonly field: "title" | "body",
    message: string,
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

export class NotFoundError extends Error {
  constructor(id: string) {
    super(`note not found: ${id}`);
    this.name = "NotFoundError";
  }
}

/** A clock, injected so tests can pin time without faking timers globally. */
export type Clock = () => string;

const systemClock: Clock = () => new Date().toISOString();

/**
 * Create a draft note.
 *
 * Title is required. Body may be empty at create time because a note is often
 * started before there is anything to write in it. The body rule bites at
 * publish time instead.
 */
export function createNote(id: string, title: string, body: string): Note {
  if (title.trim() === "") {
    throw new ValidationError("title", "title must not be empty");
  }
  if (body.length > MAX_BODY_LENGTH) {
    throw new ValidationError("body", `body must be at most ${MAX_BODY_LENGTH} characters`);
  }
  return { id, title: title.trim(), body, status: "draft", publishedAt: null };
}

/**
 * Publish a note. Returns a new Note, never mutates the input.
 *
 * Three rules, and each one has a test:
 *
 * 1. A note with a blank body cannot be published. Whitespace only counts as
 *    blank, so "   " is rejected the same as "".
 * 2. Publishing is idempotent. Publishing an already published note returns the
 *    note unchanged and is not an error. Callers retry on timeouts, and a retry
 *    must not look like a failure or move publishedAt.
 * 3. Rule 2 is checked before rule 1 on purpose. A note that is already
 *    published passed the body check once. Re-running it on a retry would let an
 *    edit that blanked the body turn a successful publish into a late failure.
 */
export function publishNote(note: Note, now: Clock = systemClock): Note {
  if (note.status === "published") {
    return note;
  }
  if (note.body.trim() === "") {
    throw new ValidationError("body", "cannot publish a note with an empty body");
  }
  return { ...note, status: "published", publishedAt: now() };
}

/**
 * Publish one note inside a list, by id.
 *
 * Returns the SAME array reference when nothing changed, so React can skip the
 * re-render. That is the reason publishNote returns the same object for an
 * already published note rather than a fresh copy.
 */
export function publishInList(notes: readonly Note[], id: string, now: Clock = systemClock): readonly Note[] {
  const index = notes.findIndex((n) => n.id === id);
  if (index === -1) {
    throw new NotFoundError(id);
  }
  const updated = publishNote(notes[index], now);
  if (updated === notes[index]) {
    return notes;
  }
  const copy = notes.slice();
  copy[index] = updated;
  return copy;
}
