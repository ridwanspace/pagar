package com.example.notes;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

/**
 * Web layer tests through MockMvc.
 *
 * <p>Note what is NOT here: no {@code @Transactional}. See the Dev agent record in
 * specs/epic-01-notes/story-01-publish-note.md. Adding it to a MockMvc test makes
 * every write roll back at the end of the method, and because this service stores
 * notes in a plain map the rollback does nothing at all, which is the worst of
 * both worlds: the annotation implies isolation the test does not have.
 * Isolation comes from a fresh context per class instead.
 */
@SpringBootTest
class NoteControllerTest {

  private static final Instant FIXED_NOW = Instant.parse("2026-01-02T03:04:05Z");

  /**
   * Replaces the real clock with a fixed one for this test class.
   *
   * <p>A moving clock would make the idempotency assertion below pass for the
   * wrong reason: two calls a millisecond apart can produce the same instant on a
   * coarse clock, and the test would go green even with a re-stamp bug.
   */
  @TestConfiguration
  static class FixedClockConfig {
    @Bean
    @Primary
    Clock testClock() {
      return new Clock() {
        private boolean used = false;

        @Override
        public ZoneId getZone() {
          return ZoneOffset.UTC;
        }

        @Override
        public Clock withZone(ZoneId zone) {
          return this;
        }

        @Override
        public synchronized Instant instant() {
          if (used) {
            return Instant.parse("2026-06-07T08:09:10Z");
          }
          used = true;
          return FIXED_NOW;
        }
      };
    }
  }

  @Autowired private WebApplicationContext context;
  private final ObjectMapper mapper = new ObjectMapper();

  private MockMvc mockMvc() {
    return MockMvcBuilders.webAppContextSetup(context).build();
  }

  private String createNote(MockMvc mvc, String body) throws Exception {
    MvcResult result =
        mvc.perform(
                post("/notes")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(mapper.writeValueAsString(new NoteController.CreateNoteRequest("Standup", body))))
            .andExpect(status().isCreated())
            .andReturn();
    JsonNode json = mapper.readTree(result.getResponse().getContentAsString());
    return json.get("id").asText();
  }

  @Test
  @DisplayName("health reports ok")
  void healthIsHonest() throws Exception {
    mockMvc()
        .perform(get("/health"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.status", equalTo("ok")));
  }

  @Test
  @DisplayName("creating a note returns 201 and a draft")
  void createReturns201() throws Exception {
    mockMvc()
        .perform(
            post("/notes")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"title\":\"Standup\",\"body\":\"content\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.status", equalTo("DRAFT")))
        .andExpect(jsonPath("$.publishedAt").doesNotExist());
  }

  @Test
  @DisplayName("an empty title returns 422")
  void createEmptyTitleReturns422() throws Exception {
    mockMvc()
        .perform(
            post("/notes")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"title\":\"\",\"body\":\"content\"}"))
        .andExpect(status().isUnprocessableEntity())
        .andExpect(jsonPath("$.field", equalTo("title")));
  }

  @Test
  @DisplayName("publishing returns 200 with a timestamp")
  void publishReturns200() throws Exception {
    MockMvc mvc = mockMvc();
    String id = createNote(mvc, "content");

    mvc.perform(post("/notes/{id}/publish", id))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.status", equalTo("PUBLISHED")))
        .andExpect(jsonPath("$.publishedAt", notNullValue()));
  }

  @Test
  @DisplayName("publishing a note with an empty body returns 422")
  void publishEmptyBodyReturns422() throws Exception {
    MockMvc mvc = mockMvc();
    String id = createNote(mvc, "");

    mvc.perform(post("/notes/{id}/publish", id))
        .andExpect(status().isUnprocessableEntity())
        .andExpect(jsonPath("$.field", equalTo("body")));
  }

  @Test
  @DisplayName("publishing twice returns 200 both times with the same timestamp")
  void publishTwiceKeepsFirstTimestamp() throws Exception {
    // The idempotency edge case at the HTTP boundary. A retried POST is a 200,
    // not a 409, and the timestamp does not move.
    MockMvc mvc = mockMvc();
    String id = createNote(mvc, "content");

    MvcResult first = mvc.perform(post("/notes/{id}/publish", id)).andExpect(status().isOk()).andReturn();
    MvcResult second = mvc.perform(post("/notes/{id}/publish", id)).andExpect(status().isOk()).andReturn();

    String firstAt = mapper.readTree(first.getResponse().getContentAsString()).get("publishedAt").asText();
    String secondAt = mapper.readTree(second.getResponse().getContentAsString()).get("publishedAt").asText();
    org.assertj.core.api.Assertions.assertThat(secondAt).isEqualTo(firstAt);
  }

  @Test
  @DisplayName("publishing an unknown id returns 404")
  void publishUnknownIdReturns404() throws Exception {
    mockMvc().perform(post("/notes/{id}/publish", "does-not-exist")).andExpect(status().isNotFound());
  }
}
