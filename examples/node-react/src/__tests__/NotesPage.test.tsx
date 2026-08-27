/**
 * Component tests. These render, so they are slower than the domain tests and
 * there are fewer of them on purpose. They check wiring, not rules.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { NotesPage } from "../NotesPage";
import { type Note } from "../notes";

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

/** A clock that hands out each time once, so the second publish is visible. */
function clockOf(...times: string[]) {
  let i = 0;
  return () => times[Math.min(i++, times.length - 1)];
}

describe("NotesPage", () => {
  it("adds a note and shows it as a draft", async () => {
    const user = userEvent.setup();
    render(<NotesPage />);

    await user.type(screen.getByLabelText("Title"), "Retro");
    await user.type(screen.getByLabelText("Body"), "we talked about the gate");
    await user.click(screen.getByRole("button", { name: "Add note" }));

    expect(screen.getByText("Retro")).toBeDefined();
    expect(screen.getByTestId("counts").textContent).toBe("1 total, 0 published");
  });

  it("shows an inline error when the title is empty", async () => {
    const user = userEvent.setup();
    render(<NotesPage />);

    await user.click(screen.getByRole("button", { name: "Add note" }));

    expect(screen.getByRole("alert").textContent).toContain("title must not be empty");
  });

  it("publishes a note and shows the timestamp", async () => {
    const user = userEvent.setup();
    render(<NotesPage initialNotes={[draft()]} now={clockOf(FIXED_NOW)} />);

    await user.click(screen.getByRole("button", { name: "Publish Standup" }));

    expect(screen.getByTestId("status-n1").textContent).toBe("published");
    expect(screen.getByTestId("published-at-n1").textContent).toBe(FIXED_NOW);
  });

  it("shows an error when publishing a note with an empty body", async () => {
    const user = userEvent.setup();
    render(<NotesPage initialNotes={[draft({ body: "" })]} now={clockOf(FIXED_NOW)} />);

    await user.click(screen.getByRole("button", { name: "Publish Standup" }));

    expect(screen.getByTestId("error").textContent).toContain("empty body");
    expect(screen.getByTestId("status-n1").textContent).toBe("draft");
  });

  it("keeps the first timestamp when publish is clicked twice", async () => {
    // The idempotency edge case through the UI. The clock returns LATER on the
    // second call, so a re-stamp bug is visible in the rendered text.
    const user = userEvent.setup();
    render(<NotesPage initialNotes={[draft()]} now={clockOf(FIXED_NOW, LATER)} />);

    const button = screen.getByRole("button", { name: "Publish Standup" });
    await user.click(button);
    await user.click(button);

    expect(screen.getByTestId("published-at-n1").textContent).toBe(FIXED_NOW);
    expect(screen.getByTestId("counts").textContent).toBe("1 total, 1 published");
    // No error banner. A retry is a normal outcome, not a failure.
    expect(screen.queryByTestId("error")).toBeNull();
  });
});
