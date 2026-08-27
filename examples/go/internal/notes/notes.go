// Package notes holds the domain rules for a meeting note.
//
// The package imports nothing from net/http. The publish rule is the part worth
// testing, and keeping it free of the transport layer means its tests need no
// server, no recorder, and no port.
package notes

import (
	"errors"
	"fmt"
	"strings"
	"sync"
	"time"
)

const (
	StatusDraft     = "draft"
	StatusPublished = "published"

	// A body longer than this is almost certainly a paste accident, not a note.
	MaxBodyLength = 20000
)

// ErrNotFound signals an unknown note id. The HTTP layer maps it to 404.
var ErrNotFound = errors.New("note not found")

// ValidationError signals a broken domain rule. The HTTP layer maps it to 422.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// Note is one meeting note.
type Note struct {
	ID          string     `json:"id"`
	Title       string     `json:"title"`
	Body        string     `json:"body"`
	Status      string     `json:"status"`
	PublishedAt *time.Time `json:"published_at"`
}

// Store keeps notes in memory. A real project puts a database behind this
// interface. The mutex is here because net/http serves each request on its own
// goroutine, so the map is shared state from the first request onward.
type Store struct {
	mu     sync.Mutex
	notes  map[string]*Note
	nextID int
	// now is injected so a test can pin the clock without touching a global.
	now func() time.Time
}

// NewStore returns an empty store using the real clock.
func NewStore() *Store {
	return NewStoreWithClock(func() time.Time { return time.Now().UTC() })
}

// NewStoreWithClock returns an empty store using the supplied clock.
func NewStoreWithClock(now func() time.Time) *Store {
	return &Store{notes: make(map[string]*Note), now: now}
}

// Create adds a draft note.
//
// Title is required. Body may be empty at create time because a note is often
// started before there is anything to write in it. The body rule bites at
// publish time instead.
func (s *Store) Create(title, body string) (*Note, error) {
	if strings.TrimSpace(title) == "" {
		return nil, &ValidationError{Field: "title", Message: "title must not be empty"}
	}
	if len(body) > MaxBodyLength {
		return nil, &ValidationError{
			Field:   "body",
			Message: fmt.Sprintf("body must be at most %d characters", MaxBodyLength),
		}
	}

	s.mu.Lock()
	defer s.mu.Unlock()
	s.nextID++
	note := &Note{
		ID:     fmt.Sprintf("n%d", s.nextID),
		Title:  strings.TrimSpace(title),
		Body:   body,
		Status: StatusDraft,
	}
	s.notes[note.ID] = note
	return note, nil
}

// Get returns one note or ErrNotFound.
func (s *Store) Get(id string) (*Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	note, ok := s.notes[id]
	if !ok {
		return nil, ErrNotFound
	}
	return note, nil
}

// Publish publishes a note.
//
// Three rules, and each one has a test:
//
//  1. A note with a blank body cannot be published. Whitespace only counts as
//     blank, so "   " is rejected the same as "".
//  2. Publishing is idempotent. Publishing an already published note returns the
//     note unchanged and is not an error. Callers retry on timeouts, and a retry
//     must not look like a failure or move PublishedAt.
//  3. An unknown id is ErrNotFound.
func (s *Store) Publish(id string) (*Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	note, ok := s.notes[id]
	if !ok {
		return nil, ErrNotFound
	}

	// Rule 2 comes before rule 1 deliberately. A note that is already published
	// passed the body check once. Re-running the check on a retry would let an
	// edit that blanked the body turn a successful publish into a late failure.
	if note.Status == StatusPublished {
		return note, nil
	}

	if strings.TrimSpace(note.Body) == "" {
		return nil, &ValidationError{Field: "body", Message: "cannot publish a note with an empty body"}
	}

	published := s.now()
	note.Status = StatusPublished
	note.PublishedAt = &published
	return note, nil
}

// Count returns how many notes are stored. Used by the health endpoint.
func (s *Store) Count() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	return len(s.notes)
}
