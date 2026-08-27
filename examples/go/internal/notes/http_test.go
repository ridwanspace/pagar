package notes

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// newTestServer returns a handler backed by a store with a pinned clock.
func newTestServer(t *testing.T) http.Handler {
	t.Helper()
	return NewHandler(NewStoreWithClock(clockAt(fixedNow, later)))
}

func do(t *testing.T, h http.Handler, method, path, body string) (*httptest.ResponseRecorder, map[string]any) {
	t.Helper()
	var reader *strings.Reader
	if body == "" {
		reader = strings.NewReader("")
	} else {
		reader = strings.NewReader(body)
	}
	req := httptest.NewRequest(method, path, reader)
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)

	var payload map[string]any
	if rec.Body.Len() > 0 {
		if err := json.Unmarshal(rec.Body.Bytes(), &payload); err != nil {
			t.Fatalf("%s %s returned non-JSON body %q", method, path, rec.Body.String())
		}
	}
	return rec, payload
}

func createNote(t *testing.T, h http.Handler, body string) string {
	t.Helper()
	rec, payload := do(t, h, "POST", "/notes", `{"title":"Standup","body":`+jsonString(body)+`}`)
	if rec.Code != http.StatusCreated {
		t.Fatalf("create returned %d, want 201, body %v", rec.Code, payload)
	}
	return payload["id"].(string)
}

func jsonString(s string) string {
	b, _ := json.Marshal(s)
	return string(b)
}

func TestHealthIsHonest(t *testing.T) {
	t.Parallel()
	rec, payload := do(t, newTestServer(t), "GET", "/health", "")

	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, want 200", rec.Code)
	}
	if payload["status"] != "ok" || payload["notes"].(float64) != 0 {
		t.Errorf("payload = %v, want status ok and 0 notes", payload)
	}
}

func TestCreateReturns201Draft(t *testing.T) {
	t.Parallel()
	rec, payload := do(t, newTestServer(t), "POST", "/notes", `{"title":"Standup","body":"content"}`)

	if rec.Code != http.StatusCreated {
		t.Fatalf("status = %d, want 201", rec.Code)
	}
	if payload["status"] != "draft" || payload["published_at"] != nil {
		t.Errorf("payload = %v, want draft with null published_at", payload)
	}
}

func TestCreateEmptyTitleReturns422(t *testing.T) {
	t.Parallel()
	rec, payload := do(t, newTestServer(t), "POST", "/notes", `{"title":"","body":"x"}`)

	if rec.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d, want 422", rec.Code)
	}
	if payload["field"] != "title" {
		t.Errorf("field = %v, want title", payload["field"])
	}
}

func TestPublishReturns200(t *testing.T) {
	t.Parallel()
	h := newTestServer(t)
	id := createNote(t, h, "content")

	rec, payload := do(t, h, "POST", "/notes/"+id+"/publish", "")
	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, want 200", rec.Code)
	}
	if payload["status"] != "published" || payload["published_at"] == nil {
		t.Errorf("payload = %v, want published with a timestamp", payload)
	}
}

func TestPublishEmptyBodyReturns422(t *testing.T) {
	t.Parallel()
	h := newTestServer(t)
	id := createNote(t, h, "")

	rec, payload := do(t, h, "POST", "/notes/"+id+"/publish", "")
	if rec.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d, want 422", rec.Code)
	}
	if payload["field"] != "body" {
		t.Errorf("field = %v, want body", payload["field"])
	}
}

// The idempotency edge case at the HTTP boundary. A retried POST is a 200, not a
// 409, and the timestamp does not move.
func TestPublishTwiceReturns200Both(t *testing.T) {
	t.Parallel()
	h := newTestServer(t)
	id := createNote(t, h, "content")

	firstRec, firstBody := do(t, h, "POST", "/notes/"+id+"/publish", "")
	secondRec, secondBody := do(t, h, "POST", "/notes/"+id+"/publish", "")

	if firstRec.Code != http.StatusOK || secondRec.Code != http.StatusOK {
		t.Fatalf("statuses = %d and %d, want 200 and 200", firstRec.Code, secondRec.Code)
	}
	if firstBody["published_at"] != secondBody["published_at"] {
		t.Errorf("published_at moved from %v to %v on retry", firstBody["published_at"], secondBody["published_at"])
	}
}

func TestPublishUnknownIDReturns404(t *testing.T) {
	t.Parallel()
	rec, _ := do(t, newTestServer(t), "POST", "/notes/nope/publish", "")

	if rec.Code != http.StatusNotFound {
		t.Fatalf("status = %d, want 404", rec.Code)
	}
}
