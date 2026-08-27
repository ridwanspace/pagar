// Command api serves the notes API on :8080.
//
// Standard library only. No router dependency, because Go 1.22 method patterns
// in net/http already cover what this example needs.
package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"example.com/notes/internal/notes"
)

func main() {
	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":8080"
	}

	srv := &http.Server{
		Addr:    addr,
		Handler: notes.NewHandler(notes.NewStore()),
		// A server with no timeouts leaks a goroutine per stuck client.
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      15 * time.Second,
	}

	log.Printf("notes api listening on %s", addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server stopped: %v", err)
	}
}
