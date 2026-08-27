package com.example.notes;

import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

/** Web layer. Thin on purpose: parse, call the service, map errors to status codes. */
@RestController
public class NoteController {

  private final NoteService service;

  public NoteController(NoteService service) {
    this.service = service;
  }

  /** Request body for creating a note. */
  public record CreateNoteRequest(String title, String body) {}

  @GetMapping("/health")
  public Map<String, Object> health() {
    // Honest health check. The only dependency is the store, so we say so.
    return Map.of("status", "ok", "notes", service.count());
  }

  @PostMapping("/notes")
  public ResponseEntity<Note> create(@RequestBody CreateNoteRequest request) {
    Note note = service.create(request.title(), request.body());
    return ResponseEntity.status(HttpStatus.CREATED).body(note);
  }

  @GetMapping("/notes/{id}")
  public Note get(@PathVariable String id) {
    return service.get(id);
  }

  /**
   * Publishes a note.
   *
   * <p>One user action, one call. The client does not read, then decide, then
   * write. Idempotency lives in the service so a retry is safe, which is why this
   * returns 200 rather than 409 on a second publish.
   */
  @PostMapping("/notes/{id}/publish")
  public Note publish(@PathVariable String id) {
    return service.publish(id);
  }

  @ExceptionHandler(ValidationException.class)
  public ResponseEntity<Map<String, String>> onValidation(ValidationException ex) {
    return ResponseEntity.unprocessableEntity()
        .body(
            Map.of(
                "error", "validation_error",
                "field", ex.getField(),
                "message", ex.getMessage()));
  }

  @ExceptionHandler(NoteNotFoundException.class)
  public ResponseEntity<Map<String, String>> onNotFound(NoteNotFoundException ex) {
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
        .body(Map.of("error", "not_found", "message", "note not found"));
  }
}
