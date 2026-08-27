package notes

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"
)

type errorBody struct {
	Error   string `json:"error"`
	Field   string `json:"field,omitempty"`
	Message string `json:"message"`
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	// An encode failure here means the response is already half written, so
	// there is nothing useful left to say to the client.
	_ = json.NewEncoder(w).Encode(payload)
}

// writeErr maps a domain error onto a status code. This is the only place that
// mapping exists, so a new handler cannot invent its own convention.
func writeErr(w http.ResponseWriter, err error) {
	var ve *ValidationError
	switch {
	case errors.As(err, &ve):
		writeJSON(w, http.StatusUnprocessableEntity, errorBody{
			Error: "validation_error", Field: ve.Field, Message: ve.Message,
		})
	case errors.Is(err, ErrNotFound):
		writeJSON(w, http.StatusNotFound, errorBody{Error: "not_found", Message: "note not found"})
	default:
		writeJSON(w, http.StatusInternalServerError, errorBody{Error: "internal", Message: "unexpected error"})
	}
}

// NewHandler wires the routes onto a store.
func NewHandler(store *Store) http.Handler {
	mux := http.NewServeMux()

	// Go 1.22+ method patterns. Static routes are registered before the
	// parameterized ones so "/notes" cannot be swallowed by "/notes/{id}".
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		// Honest health check. The only dependency is the store, so we say so.
		writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "notes": store.Count()})
	})

	mux.HandleFunc("POST /notes", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Title string `json:"title"`
			Body  string `json:"body"`
		}
		// A body we cannot decode is a client mistake, not a server one.
		if err := json.NewDecoder(r.Body).Decode(&in); err != nil && !strings.Contains(err.Error(), "EOF") {
			writeJSON(w, http.StatusBadRequest, errorBody{Error: "bad_request", Message: "body must be JSON"})
			return
		}
		note, err := store.Create(in.Title, in.Body)
		if err != nil {
			writeErr(w, err)
			return
		}
		writeJSON(w, http.StatusCreated, note)
	})

	mux.HandleFunc("GET /notes/{id}", func(w http.ResponseWriter, r *http.Request) {
		note, err := store.Get(r.PathValue("id"))
		if err != nil {
			writeErr(w, err)
			return
		}
		writeJSON(w, http.StatusOK, note)
	})

	mux.HandleFunc("POST /notes/{id}/publish", func(w http.ResponseWriter, r *http.Request) {
		// One user action, one call. The client does not read, then decide, then
		// write. Idempotency lives in the store so a retry is safe.
		note, err := store.Publish(r.PathValue("id"))
		if err != nil {
			writeErr(w, err)
			return
		}
		writeJSON(w, http.StatusOK, note)
	})

	return mux
}
