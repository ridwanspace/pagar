/**
 * Domain tests. No render, no DOM, no act().
 *
 * These run in milliseconds because they touch nothing but plain objects. That
 * speed is why the publish rule lives outside the component.
 */
import { describe, expect, it } from "vitest";

import {
  MAX_BODY_LENGTH,
  type Note,
  NotFoundError,
  ValidationError,
  createNote,
  publishInList,
  publishNote,
} from "../notes";

const FIXED_NOW = "2026-01-02T03:04:05.000Z";
const LATER = "2026-06-07T08:09:10.000Z";

function draft(overrides: Partial<Note> = {}): Note {
  return {
    id: "n1",
    title: "Standup",
    body: "we shipped the gate runner",
    status: "draft",
    publishedAt: null,
    ...overrides,
  };
}

describe("createNote", () => {
  it("starts a note as a draft", () => {
    const note = createNote("n1", "Standup", "content");
    expect(note.status).toBe("draft");
    expect(note.publishedAt).toBeNull();
  });

  it("trims the title", () => {
    expect(createNote("n1", "  Standup  ", "content").title).toBe("Standup");
  });

  it("rejects an empty title", () => {
    expect(() => createNote("n1", "   ", "content")).toThrow(ValidationError);
  });

  it("rejects an oversized body", () => {
    const tooLong = "x".repeat(MAX_BODY_LENGTH + 1);
    expect(() => createNote("n1", "Standup", tooLong)).toThrowError(/at most/);
  });
});

describe("publishNote", () => {
  it("sets status and timestamp on the happy path", () => {
    const note = publishNote(draft(), () => FIXED_NOW);
    expect(note.status).toBe("published");
    expect(note.publishedAt).toBe(FIXED_NOW);
  });

  it("does not mutate the input note", () => {
    const original = draft();
    publishNote(original, () => FIXED_NOW);
    expect(original.status).toBe("draft");
    expect(original.publishedAt).toBeNull();
  });

  it("rejects an empty body", () => {
    expect(() => publishNote(draft({ body: "" }), () => FIXED_NOW)).toThrow(ValidationError);
  });

  it("rejects a whitespace only body", () => {
    // The edge case a naive `if (!body)` check gets right and a naive
    // `if (body === undefined)` check gets wrong.
    expect(() => publishNote(draft({ body: "  \n\t " }), () => FIXED_NOW)).toThrow(ValidationError);
  });

  it("is idempotent and keeps the first timestamp", () => {
    // The edge case. The clock returns a DIFFERENT time on the second call, so a
    // bug that re-stamps publishedAt fails this test loudly.
    const first = publishNote(draft(), () => FIXED_NOW);
    const second = publishNote(first, () => LATER);

    expect(second.status).toBe("published");
    expect(second.publishedAt).toBe(FIXED_NOW);
    // Same reference, so React skips the re-render.
    expect(second).toBe(first);
  });

  it("keeps an already published note published even if the body was blanked", () => {
    // Guards the rule order inside publishNote. Swapping the two checks makes
    // this go red, which is what proves the order is deliberate.
    const published = publishNote(draft(), () => FIXED_NOW);
    const blanked: Note = { ...published, body: "" };

    const result = publishNote(blanked, () => LATER);
    expect(result.status).toBe("published");
    expect(result.publishedAt).toBe(FIXED_NOW);
  });
});

describe("publishInList", () => {
  it("publishes the matching note and leaves the others alone", () => {
    const notes = [draft({ id: "n1" }), draft({ id: "n2" })];
    const result = publishInList(notes, "n2", () => FIXED_NOW);

    expect(result[0]).toBe(notes[0]);
    expect(result[1].status).toBe("published");
  });

  it("returns the SAME array when the note was already published", () => {
    // This is the render-skip contract. A new array every call would re-render
    // the whole list on every retry.
    const notes = [publishNote(draft(), () => FIXED_NOW)];
    expect(publishInList(notes, "n1", () => LATER)).toBe(notes);
  });

  it("throws NotFoundError for an unknown id", () => {
    expect(() => publishInList([], "nope", () => FIXED_NOW)).toThrow(NotFoundError);
  });
});
