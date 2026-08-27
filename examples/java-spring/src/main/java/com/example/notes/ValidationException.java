package com.example.notes;

/** Thrown when input breaks a domain rule. The web layer maps it to 422. */
public class ValidationException extends RuntimeException {

  private final String field;

  public ValidationException(String field, String message) {
    super(message);
    this.field = field;
  }

  public String getField() {
    return field;
  }
}
