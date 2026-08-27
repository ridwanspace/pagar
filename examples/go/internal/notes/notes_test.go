package notes

import (
	"errors"
	"strings"
	"sync"
	"testing"
	"time"
)

var (
	fixedNow = time.Date(2026, 1, 2, 3, 4, 5, 0, time.UTC)
	later    = time.Date(2026, 6, 7, 8, 9, 10, 0, time.UTC)
)

// clockAt returns a clock that hands out times from a fixed list, one per call.
// A test can then tell the first publish apart from the second.
func clockAt(times ...time.Time) func() time.Time {
	var i int
	var mu sync.Mutex
	return func() time.Time {
		mu.Lock()
		defer mu.Unlock()
		t := times[len(times)-1]
		if i < len(times) {
			t = times[i]
			i++
		}
		return t
	}
}

func TestCreateStartsAsDraft(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow))

	note, err := s.Create("Standup", "we shipped the gate runner")
	if err != nil {
		t.Fatalf("Create returned error: %v", err)
	}
	if note.Status != StatusDraft {
		t.Errorf("status = %q, want %q", note.Status, StatusDraft)
	}
	if note.PublishedAt != nil {
		t.Errorf("PublishedAt = %v, want nil", note.PublishedAt)
	}
}

func TestCreateValidation(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name      string
		title     string
		body      string
		wantField string
	}{
		{name: "empty title", title: "", body: "x", wantField: "title"},
		{name: "whitespace title", title: "   ", body: "x", wantField: "title"},
		{name: "oversized body", title: "ok", body: strings.Repeat("x", MaxBodyLength+1), wantField: "body"},
	}

	for _, tc := range cases {
		// Go 1.22 gave every loop iteration its own variable, so the old
		// `tc := tc` line is no longer needed. See the Dev agent record in
		// specs/epic-01-notes/story-01-publish-note.md: on Go 1.21 and earlier,
		// t.Parallel() inside a subtest made every case read the LAST tc, and
		// the table still passed because the last case happened to be valid.
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			s := NewStoreWithClock(clockAt(fixedNow))

			_, err := s.Create(tc.title, tc.body)
			var ve *ValidationError
			if !errors.As(err, &ve) {
				t.Fatalf("Create(%q, len=%d) error = %v, want ValidationError", tc.title, len(tc.body), err)
			}
			if ve.Field != tc.wantField {
				t.Errorf("field = %q, want %q", ve.Field, tc.wantField)
			}
		})
	}
}

func TestPublishHappyPath(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow))
	note, _ := s.Create("Standup", "we shipped the gate runner")

	got, err := s.Publish(note.ID)
	if err != nil {
		t.Fatalf("Publish returned error: %v", err)
	}
	if got.Status != StatusPublished {
		t.Errorf("status = %q, want %q", got.Status, StatusPublished)
	}
	if got.PublishedAt == nil || !got.PublishedAt.Equal(fixedNow) {
		t.Errorf("PublishedAt = %v, want %v", got.PublishedAt, fixedNow)
	}
}

func TestPublishRejectsBlankBody(t *testing.T) {
	t.Parallel()

	cases := []struct{ name, body string }{
		{name: "empty", body: ""},
		{name: "whitespace only", body: "  \n\t "},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			s := NewStoreWithClock(clockAt(fixedNow))
			note, _ := s.Create("Standup", tc.body)

			_, err := s.Publish(note.ID)
			var ve *ValidationError
			if !errors.As(err, &ve) {
				t.Fatalf("Publish error = %v, want ValidationError", err)
			}
			if ve.Field != "body" {
				t.Errorf("field = %q, want body", ve.Field)
			}
			stored, _ := s.Get(note.ID)
			if stored.Status != StatusDraft {
				t.Errorf("status = %q, want it to stay %q", stored.Status, StatusDraft)
			}
		})
	}
}

// TestPublishIsIdempotent is the edge case. A second publish is not an error and
// does not move the timestamp. The clock hands out `later` on the second call,
// so a bug that re-stamps PublishedAt fails this test loudly.
func TestPublishIsIdempotent(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow, later))
	note, _ := s.Create("Standup", "we shipped the gate runner")

	first, err := s.Publish(note.ID)
	if err != nil {
		t.Fatalf("first Publish returned error: %v", err)
	}
	second, err := s.Publish(note.ID)
	if err != nil {
		t.Fatalf("second Publish returned error: %v, want nil", err)
	}

	if second.Status != StatusPublished {
		t.Errorf("status = %q, want %q", second.Status, StatusPublished)
	}
	if !second.PublishedAt.Equal(*first.PublishedAt) {
		t.Errorf("second publish moved PublishedAt from %v to %v", first.PublishedAt, second.PublishedAt)
	}
	if !second.PublishedAt.Equal(fixedNow) {
		t.Errorf("PublishedAt = %v, want the first publish time %v", second.PublishedAt, fixedNow)
	}
}

// Guards the rule order inside Publish. Once published, the note stays published
// even if the body was later emptied. Swapping the two checks makes this go red.
func TestPublishOfPublishedNoteSurvivesBlankedBody(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow, later))
	note, _ := s.Create("Standup", "content")
	if _, err := s.Publish(note.ID); err != nil {
		t.Fatalf("first Publish returned error: %v", err)
	}

	stored, _ := s.Get(note.ID)
	stored.Body = ""

	got, err := s.Publish(note.ID)
	if err != nil {
		t.Fatalf("Publish after blanking body returned error: %v, want nil", err)
	}
	if got.Status != StatusPublished || !got.PublishedAt.Equal(fixedNow) {
		t.Errorf("got status %q at %v, want %q at %v", got.Status, got.PublishedAt, StatusPublished, fixedNow)
	}
}

func TestPublishUnknownIDIsNotFound(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow))

	if _, err := s.Publish("does-not-exist"); !errors.Is(err, ErrNotFound) {
		t.Fatalf("error = %v, want ErrNotFound", err)
	}
}

// Concurrent publishes must produce exactly one timestamp. Run this under
// `go test -race` to make the mutex do real work.
func TestConcurrentPublishStampsOnce(t *testing.T) {
	t.Parallel()
	s := NewStoreWithClock(clockAt(fixedNow, later, later, later, later))
	note, _ := s.Create("Standup", "content")

	var wg sync.WaitGroup
	for range 8 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, _ = s.Publish(note.ID)
		}()
	}
	wg.Wait()

	stored, _ := s.Get(note.ID)
	if !stored.PublishedAt.Equal(fixedNow) {
		t.Errorf("PublishedAt = %v, want the first publish time %v", stored.PublishedAt, fixedNow)
	}
}
