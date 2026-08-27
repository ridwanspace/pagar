package com.example.notes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/**
 * Service tests. Plain JUnit, no Spring context.
 *
 * <p>There is no {@code @SpringBootTest} here on purpose. These construct the
 * service directly, so they run in milliseconds and need no application context,
 * no port, and no database.
 */
class NoteServiceTest {

  private static final Instant FIXED_NOW = Instant.parse("2026-01-02T03:04:05Z");
  private static final Instant LATER = Instant.parse("2026-06-07T08:09:10Z");

  /** A service whose clock is pinned to one instant. */
  private static NoteService serviceAt(Instant instant) {
    return new NoteService(Clock.fixed(instant, ZoneOffset.UTC));
  }

  /** A clock that returns FIXED_NOW on the first read and LATER afterwards. */
  private static NoteService serviceWithMovingClock() {
    return new NoteService(
        new Clock() {
          private boolean used = false;

          @Override
          public ZoneOffset getZone() {
            return ZoneOffset.UTC;
          }

          @Override
          public Clock withZone(java.time.ZoneId zone) {
            return this;
          }

          @Override
          public synchronized Instant instant() {
            if (used) {
              return LATER;
            }
            used = true;
            return FIXED_NOW;
          }
        });
  }

  @Test
  @DisplayName("a new note starts as a draft with no timestamp")
  void createStartsAsDraft() {
    Note note = serviceAt(FIXED_NOW).create("Standup", "we shipped the gate runner");

    assertThat(note.status()).isEqualTo(NoteStatus.DRAFT);
    assertThat(note.publishedAt()).isNull();
  }

  @Test
  @DisplayName("the title is trimmed")
  void createTrimsTitle() {
    assertThat(serviceAt(FIXED_NOW).create("  Standup  ", "body").title()).isEqualTo("Standup");
  }

  @ParameterizedTest(name = "title \"{0}\" is rejected")
  @ValueSource(strings = {"", "   ", "\t\n"})
  void createRejectsBlankTitle(String title) {
    assertThatThrownBy(() -> serviceAt(FIXED_NOW).create(title, "body"))
        .isInstanceOf(ValidationException.class)
        .extracting(ex -> ((ValidationException) ex).getField())
        .isEqualTo("title");
  }

  @Test
  @DisplayName("an oversized body is rejected at create time")
  void createRejectsOversizedBody() {
    String tooLong = "x".repeat(Note.MAX_BODY_LENGTH + 1);

    assertThatThrownBy(() -> serviceAt(FIXED_NOW).create("Standup", tooLong))
        .isInstanceOf(ValidationException.class);
  }

  @Test
  @DisplayName("publishing sets the status and the timestamp")
  void publishHappyPath() {
    NoteService service = serviceAt(FIXED_NOW);
    Note draft = service.create("Standup", "we shipped the gate runner");

    Note published = service.publish(draft.id());

    assertThat(published.status()).isEqualTo(NoteStatus.PUBLISHED);
    assertThat(published.publishedAt()).isEqualTo(FIXED_NOW);
  }

  @ParameterizedTest(name = "body \"{0}\" cannot be published")
  @ValueSource(strings = {"", "   ", "  \n\t "})
  void publishRejectsBlankBody(String body) {
    NoteService service = serviceAt(FIXED_NOW);
    Note draft = service.create("Standup", body);

    assertThatThrownBy(() -> service.publish(draft.id()))
        .isInstanceOf(ValidationException.class)
        .extracting(ex -> ((ValidationException) ex).getField())
        .isEqualTo("body");
    assertThat(service.get(draft.id()).status()).isEqualTo(NoteStatus.DRAFT);
  }

  @Test
  @DisplayName("publishing twice is not an error and does not move the timestamp")
  void publishIsIdempotent() {
    // The edge case. The clock returns LATER on its second read, so a bug that
    // re-stamps publishedAt fails this test loudly.
    NoteService service = serviceWithMovingClock();
    Note draft = service.create("Standup", "we shipped the gate runner");

    Note first = service.publish(draft.id());
    Note second = service.publish(draft.id());

    assertThat(second.status()).isEqualTo(NoteStatus.PUBLISHED);
    assertThat(second.publishedAt()).isEqualTo(FIXED_NOW);
    assertThat(second.publishedAt()).isEqualTo(first.publishedAt());
  }

  @Test
  @DisplayName("an already published note stays published even if the body was blanked")
  void publishSurvivesBlankedBody() {
    // Guards the rule order inside publish(). Swapping the two checks makes this
    // go red, which is what proves the order is deliberate.
    NoteService service = serviceWithMovingClock();
    Note draft = service.create("Standup", "content");
    service.publish(draft.id());
    service.replace(service.get(draft.id()).withBody(""));

    Note result = service.publish(draft.id());

    assertThat(result.status()).isEqualTo(NoteStatus.PUBLISHED);
    assertThat(result.publishedAt()).isEqualTo(FIXED_NOW);
  }

  @Test
  @DisplayName("publishing an unknown id is a not-found error")
  void publishUnknownId() {
    assertThatThrownBy(() -> serviceAt(FIXED_NOW).publish("does-not-exist"))
        .isInstanceOf(NoteNotFoundException.class);
  }

  @Test
  @DisplayName("concurrent publishes stamp exactly one timestamp")
  void concurrentPublishStampsOnce() throws Exception {
    NoteService service = serviceWithMovingClock();
    Note draft = service.create("Standup", "content");

    int threads = 8;
    CountDownLatch start = new CountDownLatch(1);
    CountDownLatch done = new CountDownLatch(threads);
    ExecutorService pool = Executors.newFixedThreadPool(threads);
    try {
      for (int i = 0; i < threads; i++) {
        pool.submit(
            () -> {
              try {
                start.await();
                service.publish(draft.id());
              } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
              } finally {
                done.countDown();
              }
            });
      }
      start.countDown();
      assertThat(done.await(5, TimeUnit.SECONDS)).isTrue();
    } finally {
      pool.shutdownNow();
    }

    assertThat(service.get(draft.id()).publishedAt()).isEqualTo(FIXED_NOW);
  }
}
