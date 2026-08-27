package com.example.notes;

import java.time.Clock;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

/** Entry point. Serves the notes API on :8080. */
@SpringBootApplication
public class NotesApplication {

  public static void main(String[] args) {
    SpringApplication.run(NotesApplication.class, args);
  }

  /**
   * The real clock, as a bean.
   *
   * <p>A test overrides this with Clock.fixed(...) and gets a deterministic
   * publishedAt without mocking a static method.
   */
  @Bean
  public Clock clock() {
    return Clock.systemUTC();
  }
}
