#!/usr/bin/env bash
# =============================================================================
# Story-loop dry-run guard tests — the loop's only automated safety net.
#
# Zero dependencies on purpose (bash + jq + git + python3, the loop's own
# prereqs). Every test drives `loop.sh --dry-run` against a throwaway fixture:
# NOTHING here invokes the Claude CLI, pays for a model session, or mutates
# anything outside its temp dir. A guard these tests never saw RED proves
# nothing — mutation-verify new assertions (see the loop-engineering skill).
#
# Usage:  bash starter/scripts/loop/loop.test.sh   (or ./loop.test.sh)
# Exit:   0 all green, 1 any failure
# =============================================================================
set -uo pipefail

LOOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTER_ROOT="$(cd "$LOOP_DIR/../.." && pwd)"
SPECS_CLI="$STARTER_ROOT/.claude/scripts/specs/specs.py"

PASS=0 FAIL=0
ok()   { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
section() { echo ""; echo "== $1"; }

# assert_rc <expected-rc> <actual-rc> <label>
assert_rc() { if [[ "$1" == "$2" ]]; then ok "$3 (rc=$2)"; else fail "$3: expected rc=$1, got rc=$2"; fi; }
# assert_grep <pattern> <file|stdin-string> <label>
assert_grep() { if grep -q -e "$1" <<<"$2"; then ok "$3"; else fail "$3: pattern not found: $1"; fi; }
# assert_not_grep <pattern> <file|stdin-string> <label>
assert_not_grep() { if grep -q -e "$1" <<<"$2"; then fail "$3: pattern FOUND but must be absent: $1"; else ok "$3"; fi; }

# --- fixture: a throwaway project with a 3-story plan --------------------------
# make_fixture [done_refs...]  — marks the given refs done after sync
make_fixture() {
  local FX
  FX="$(mktemp -d)"
  mkdir -p "$FX/.claude/specs/plan_artifacts/epic-01-demo"
  echo "# Demo PRD" >"$FX/.claude/specs/plan_artifacts/prd.md"
  echo "# Demo epic" >"$FX/.claude/specs/plan_artifacts/epic-01-demo/epic.md"
  printf '# First story\n\n- [ ] does the thing\n' >"$FX/.claude/specs/plan_artifacts/epic-01-demo/story-01-first.md"
  printf '# Second story\n\n- [ ] does another thing\n' >"$FX/.claude/specs/plan_artifacts/epic-01-demo/story-02-second.md"
  printf '# Third story\n\n- [ ] does the last thing\n' >"$FX/.claude/specs/plan_artifacts/epic-01-demo/story-03-third.md"
  python3 "$SPECS_CLI" --root "$FX" sync-status >/dev/null 2>&1
  local ref
  for ref in "$@"; do
    python3 "$SPECS_CLI" --root "$FX" set-status "$ref" "done" >/dev/null 2>&1
  done
  echo "$FX"
}

# run_loop <fixture> [args...] — dry-run-safe invocation; echoes combined output
run_loop() {
  local FX="$1"; shift
  (LOOP_PROJECT_ROOT="$FX" LOOP_SPECS_CLI="$SPECS_CLI" \
    LOOP_LOG_DIR="$FX/logs" bash "$LOOP_DIR/loop.sh" "$@") 2>&1
}

# --- 1. help --------------------------------------------------------------------
section "help extracts the usage block"
OUT="$(bash "$LOOP_DIR/loop.sh" --help 2>&1)"; RC=$?
assert_rc 0 "$RC" "--help exits 0"
assert_grep -- "--dry-run" "$OUT" "--help lists --dry-run"

# --- 2. argument validation -------------------------------------------------------
section "argument validation rejects bad values"
OUT="$(run_loop "$(make_fixture)" --effort bogus 2>&1)"; RC=$?
assert_rc 1 "$RC" "--effort bogus exits 1"
assert_grep "expects low|medium|high|xhigh|max" "$OUT" "--effort names the accepted values"

OUT="$(run_loop "$(make_fixture)" --phase-timeout soon 2>&1)"; RC=$?
assert_rc 1 "$RC" "--phase-timeout non-numeric exits 1"

FX="$(make_fixture)"
OUT="$(LOOP_PROJECT_ROOT="$FX" LOOP_SPECS_CLI="$SPECS_CLI" LOOP_LOG_DIR="$FX/logs" \
  bash "$LOOP_DIR/loop.sh" --story 1.1 --from 1.1 --to 1.3 --dry-run 2>&1)"; RC=$?
assert_rc 1 "$RC" "--story + --from/--to conflict exits 1"
rm -rf "$FX"

# --- 3. dry-run prints the full phase sequence, executes nothing ------------------
section "dry-run prints every phase and executes nothing"
FX="$(make_fixture)"
OUT="$(run_loop "$FX" --story 1.1 --dry-run)"; RC=$?
assert_rc 0 "$RC" "dry-run --story 1.1 exits 0"
assert_grep "phase=create-story model=" "$OUT" "prints create-story phase with model"
assert_grep "phase=dev-story model=" "$OUT" "prints dev-story phase with model"
assert_grep "phase=code-review model=" "$OUT" "prints code-review phase with model"
assert_grep "phase=reflect model=" "$OUT" "prints conditional reflect phase"
assert_grep "phase=commit mode=script" "$OUT" "prints scripted commit phase"
assert_grep "/create-story 1.1" "$OUT" "user prompt is the bare slash command"
assert_grep "DRY RUN — nothing will be executed" "$OUT" "announces dry-run mode"
LOGS_COUNT="$(find "$FX/logs" -name '*.log' -type f 2>/dev/null | wc -l)"
if [[ "$LOGS_COUNT" == "0" ]]; then ok "no phase logs written (nothing executed)"
else fail "dry-run wrote $LOGS_COUNT log file(s) — it must execute nothing"; fi
rm -rf "$FX"

# --- 4. resume: existing dev file skips create, done status skips dev --------------
section "resume skip-logic honors on-disk state"
FX="$(make_fixture)"
mkdir -p "$FX/.claude/specs/implementation_artifacts/epic-01-demo"
echo "# Dev: first story" >"$FX/.claude/specs/implementation_artifacts/epic-01-demo/story-01-first.md"
python3 "$SPECS_CLI" --root "$FX" set-status 1.1 "done" >/dev/null 2>&1
OUT="$(run_loop "$FX" --story 1.1 --dry-run)"; RC=$?
assert_rc 0 "$RC" "resume dry-run exits 0"
assert_grep "skipping create-story (resume)" "$OUT" "existing dev story file skips create-story"
assert_grep "skipping dev-story (resume)" "$OUT" "done status skips dev-story"
assert_grep "phase=code-review" "$OUT" "review still runs after resume skips"
rm -rf "$FX"

# --- 5. range resolution: plan order, done stories filtered ------------------------
section "range resolution follows plan order and skips done"
FX="$(make_fixture 1.2)"
OUT="$(run_loop "$FX" --from 1.1 --to 1.3 --dry-run)"; RC=$?
assert_rc 0 "$RC" "range dry-run exits 0"
assert_grep "1.2 already done — skipping" "$OUT" "done story named and skipped"
assert_grep "range 1.1..1.3 → 1.1 1.3" "$OUT" "range resolves to the runnable stories only"
rm -rf "$FX"

FX="$(make_fixture)"
OUT="$(run_loop "$FX" --from 9.9 --to 9.9 --dry-run)"; RC=$?
assert_rc 0 "$RC" "empty range exits 0 with a warning"
assert_grep "matched no runnable stories" "$OUT" "empty range warns clearly"
rm -rf "$FX"

# --- 6. auto-resolution: picks the planned story, stops after one iteration --------
section "auto-resolution dry-run"
FX="$(make_fixture)"
OUT="$(run_loop "$FX" --dry-run)"; RC=$?
assert_rc 0 "$RC" "auto dry-run exits 0"
assert_grep "STORY 1.1 — First story \[planned\]" "$OUT" "resolves the first planned story with title"
assert_grep "stopping after one" "$OUT" "dry-run stops after one iteration (state cannot change)"
rm -rf "$FX"

# --- 7. nothing to do ----------------------------------------------------------------
section "empty backlog says so and exits 0"
FX="$(make_fixture 1.1 1.2 1.3)"
OUT="$(run_loop "$FX" --dry-run)"; RC=$?
assert_rc 0 "$RC" "all-done exits 0"
assert_grep "Nothing to do" "$OUT" "states there is nothing to do"
rm -rf "$FX"

# --- summary -----------------------------------------------------------------------
echo ""
echo "pass=$PASS fail=$FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
