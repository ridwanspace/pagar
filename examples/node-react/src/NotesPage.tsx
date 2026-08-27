/**
 * The UI slice. Thin on purpose: render state, call the domain, show the error.
 *
 * No business rule lives here. A rule in a component can only be tested through
 * a render, which is slower and reads worse than a direct call.
 */
import { useCallback, useMemo, useState } from "react";

import { type Clock, type Note, ValidationError, createNote, publishInList } from "./notes";

let idCounter = 0;
function nextId(): string {
  idCounter += 1;
  return `n${idCounter}`;
}

export interface NotesPageProps {
  /** Seed notes, so a test can start from a known state. */
  initialNotes?: readonly Note[];
  /** Injected clock, so a test can assert on an exact published timestamp. */
  now?: Clock;
}

export function NotesPage({ initialNotes = [], now }: NotesPageProps) {
  const [notes, setNotes] = useState<readonly Note[]>(initialNotes);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Both handlers compute the next value BEFORE calling the setter, and never
  // inside the updater callback. React defers that callback and runs it during
  // render, which is outside this try block, so a throw from there escapes the
  // catch and unmounts the tree instead of showing the message. The component
  // tests caught this. See the Dev agent record in
  // specs/epic-01-notes/story-01-publish-note.md.
  const handleCreate = useCallback(() => {
    let created;
    try {
      created = createNote(nextId(), title, body);
    } catch (err) {
      // Only a domain rule produces a message worth showing. Anything else is a
      // bug and must keep propagating.
      if (err instanceof ValidationError) {
        setError(err.message);
        return;
      }
      throw err;
    }
    setNotes((current) => [...current, created]);
    setTitle("");
    setBody("");
    setError(null);
  }, [title, body]);

  const handlePublish = useCallback(
    (id: string) => {
      let next;
      try {
        next = publishInList(notes, id, now);
      } catch (err) {
        if (err instanceof ValidationError) {
          setError(err.message);
          return;
        }
        throw err;
      }
      setNotes(next);
      setError(null);
    },
    [notes, now],
  );

  const publishedCount = useMemo(() => notes.filter((n) => n.status === "published").length, [notes]);

  return (
    <main>
      <h1>Meeting notes</h1>
      <p data-testid="counts">
        {notes.length} total, {publishedCount} published
      </p>

      <section>
        <label htmlFor="title">Title</label>
        <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <label htmlFor="body">Body</label>
        <textarea id="body" value={body} onChange={(e) => setBody(e.target.value)} />
        <button type="button" onClick={handleCreate}>
          Add note
        </button>
      </section>

      {error !== null && (
        <p role="alert" data-testid="error">
          {error}
        </p>
      )}

      <ul>
        {notes.map((note) => (
          <li key={note.id} data-testid={`note-${note.id}`}>
            <span>{note.title}</span>
            <span data-testid={`status-${note.id}`}>{note.status}</span>
            <span data-testid={`published-at-${note.id}`}>{note.publishedAt ?? ""}</span>
            <button type="button" onClick={() => handlePublish(note.id)}>
              {`Publish ${note.title}`}
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
