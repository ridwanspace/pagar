package com.example.notes;

/** Thrown when a note id does not exist. The web layer maps it to 404. */
public class NoteNotFoundException extends RuntimeException {

  public NoteNotFoundException(String id) {
    super("note not found: " + id);
  }
}
