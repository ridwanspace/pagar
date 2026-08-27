# shellcheck shell=bash
# Story-loop shared helpers: logging, specs.py bridge, phase runner, gates, commit.
# Sourced by loop.sh — expects config.sh already sourced and these globals set:
#   PROJECT_ROOT LOOP_DIR DRY_RUN

# --- logging -----------------------------------------------------------------
if [[ -t 1 ]]; then
  C_RED=$'\033[0;31m' C_GREEN=$'\033[0;32m' C_YELLOW=$'\033[0;33m'
  C_CYAN=$'\033[0;36m' C_BOLD=$'\033[1m' C_OFF=$'\033[0m'
else
  C_RED="" C_GREEN="" C_YELLOW="" C_CYAN="" C_BOLD="" C_OFF=""
fi

_ts() { date +"%H:%M:%S"; }
log_info() { echo "${C_CYAN}[$(_ts)]${C_OFF} $*"; }
log_ok() { echo "${C_GREEN}[$(_ts)] ✓${C_OFF} $*"; }
log_warn() { echo "${C_YELLOW}[$(_ts)] ⚠${C_OFF} $*"; }
log_err() { echo "${C_RED}[$(_ts)] ✗${C_OFF} $*" >&2; }
log_header() {
  echo ""
  echo "${C_BOLD}────────────────────────────────────────────────────────────${C_OFF}"
  echo "${C_BOLD}$*${C_OFF}"
  echo "${C_BOLD}────────────────────────────────────────────────────────────${C_OFF}"
}

# --- prerequisites -------------------------------------------------------------
check_prereqs() {
  local missing=0
  for bin in jq git; do
    command -v "$bin" >/dev/null 2>&1 || {
      log_err "'$bin' is required (install it and retry)"
      missing=1
    }
  done
  if [[ "$DRY_RUN" != "true" ]]; then
    command -v "$LOOP_CLAUDE_CMD" >/dev/null 2>&1 || {
      log_err "'$LOOP_CLAUDE_CMD' (Claude Code CLI) not found — npm install -g @anthropic-ai/claude-code"
      missing=1
    }
    [[ -f "$LOOP_SPECS_CLI" ]] || {
      log_err "spec CLI not found at $LOOP_SPECS_CLI (set LOOP_SPECS_CLI or copy the starter's .claude/scripts/specs/)"
      missing=1
    }
  fi
  [[ $missing -eq 0 ]] || exit 1
}

# --- specs.py bridge -------------------------------------------------------------
# All spec-pipeline state questions go through the shared helper CLI so the loop
# and the skills can never disagree about what "next" or "done" means.
# NB: specs.py's --root/--json are GLOBAL flags — they must precede the
# subcommand, so call sites use `specs --json <cmd> ...`.
specs() {
  "$LOOP_PYTHON" "$LOOP_SPECS_CLI" --root "$PROJECT_ROOT" "$@"
}

# story_field <ref> <jq-expr> — one field from `story-info --json`
story_field() {
  specs --json story-info "$1" 2>/dev/null | jq -r "$2"
}

# --- verification command resolution ---------------------------------------------
# resolve_verify_cmd <kind: test|typecheck|build> — honours three states:
#   ""     → configured off, skip silently
#   "auto" → detect from the repo (pagar gates first, then npm scripts, then tsc)
#   else   → the literal command, run from the project root
has_npm_script() { # has_npm_script <name> — true when package.json declares it
  [[ -f "$PROJECT_ROOT/package.json" ]] &&
    jq -e --arg s "$1" '.scripts[$s] != null' "$PROJECT_ROOT/package.json" >/dev/null 2>&1
}

resolve_verify_cmd() {
  local cfg_var="LOOP_VERIFY_${1^^}_CMD" cfg
  cfg="${!cfg_var:-}"
  [[ -z "$cfg" ]] && return 0
  if [[ "$cfg" != "auto" ]]; then
    echo "$cfg"
    return 0
  fi
  case "$1" in
    test)
      if [[ -f "$PROJECT_ROOT/gates.config.json" && -f "$PROJECT_ROOT/gates/run-gates.mjs" ]]; then
        echo "node gates/run-gates.mjs"
      elif has_npm_script test; then
        echo "npm test"
      fi
      ;;
    typecheck)
      if [[ -f "$PROJECT_ROOT/tsconfig.json" ]]; then
        echo "npx tsc --noEmit"
      fi
      ;;
    build)
      if has_npm_script build; then
        echo "npm run build"
      fi
      ;;
  esac
}

# fmt_verify <kind> — for the run summary: the command, or "(off)"/"(skip)".
fmt_verify() {
  local on_var="LOOP_VERIFY_${1^^}" cmd
  [[ "${!on_var:-false}" != "true" ]] && { echo "(off)"; return; }
  cmd="$(resolve_verify_cmd "$1")"
  [[ -z "$cmd" ]] && { echo "(skip — none detected; set LOOP_VERIFY_${1^^}_CMD)"; return; }
  echo "$cmd"
}

# run_verify_cmd <kind> — run the resolved command from the project root with
# output teed to a log; returns 0 on skip, 1 on failure. Sets LOOP_LAST_ERROR.
run_verify_cmd() {
  local kind="$1" cmd log
  cmd="$(resolve_verify_cmd "$kind")"
  [[ -z "$cmd" ]] && return 0
  log="$LOOP_LOG_DIR/last_${kind}.log"
  if (cd "$PROJECT_ROOT" && eval "$cmd" >"$log" 2>&1); then
    log_ok "gate: ${cmd} green"
    return 0
  fi
  LOOP_LAST_ERROR="gate failed: '${cmd}' is red after dev-story — $(tail -n 20 "$log")"
  log_err "'${cmd}' failed (full output: $log)"
  return 1
}

# --- prompt assembly ----------------------------------------------------------------
# The user prompt is ONLY the slash command (so the skill receives clean args);
# unattended-mode rules + the phase contract ride in via --append-system-prompt.
build_addendum() {
  local phase_file="$1" ref="$2" title="$3" retry_context="${4:-}"
  local text
  text="$(cat "$LOOP_DIR/prompts/unattended.md" "$LOOP_DIR/prompts/$phase_file")"
  text="${text//\{\{REF\}\}/$ref}"
  text="${text//\{\{TITLE\}\}/$title}"
  # Compounding memory: lessons paid for by earlier loop failures ride into
  # every session (bounded — newest entries live at the end of the file).
  if [[ "$LOOP_LEARN" == "true" && -s "$LOOP_LEARNINGS_FILE" ]]; then
    text+=$'\n\n'"# Lessons from previous loop runs (scripts/loop/LEARNINGS.md)"
    text+=$'\n'"These rules were paid for with real failures in earlier runs — apply them:"
    text+=$'\n\n'"$(tail -n "$LOOP_LEARN_MAX_LINES" "$LOOP_LEARNINGS_FILE")"
  fi
  if [[ -n "$retry_context" ]]; then
    text+=$'\n\n'"# Retry — previous attempt failed"$'\n'"$retry_context"$'\n'
    if [[ "$retry_context" == *"timed out"* ]]; then
      # A timeout is not a defect — the previous session ran out of wall-clock
      # with real, valid work ALREADY ON DISK. Echoing the error alone makes a
      # fresh session restart from zero against the same wall and time out again
      # at the same place. Point it at the evidence instead so it resumes.
      text+="This is a WALL-CLOCK timeout, not a broken build. The previous session's work is still on disk and is presumed GOOD unless it fails a gate."$'\n'
      text+="Do NOT start over and do NOT revert anything. Resume where it stopped:"$'\n'
      text+="1. Read the story file's task list — tasks already marked [x] are DONE; trust them."$'\n'
      text+="2. Run 'git status' to see what the previous attempt already wrote."$'\n'
      text+="3. Run the verification gates (typecheck, tests) before writing anything new."$'\n'
      text+="4. Continue from the first unchecked task, then finish the remaining ones."$'\n'
      text+="Prioritise reaching a committable, gate-green state over breadth of work."
    else
      text+="Fix the cause before redoing work that already succeeded."
    fi
  fi
  printf '%s' "$text"
}

# --- self-improvement: failure events + the reflect phase --------------------------
# Every phase/gate failure is recorded; when a story finishes (or finally fails)
# with events on the books, a cheap reflect session distills them into
# LEARNINGS.md — which build_addendum feeds back into all future sessions.
events_file_for() { echo "$LOOP_LOG_DIR/events_${1//./-}.log"; }

record_failure_event() {
  local ref="$1" phase="$2" attempt="$3" error="$4"
  [[ "$LOOP_LEARN" != "true" ]] && return 0
  printf '%s | story %s | phase %s | attempt %s | %s\n' \
    "$(date +%Y-%m-%dT%H:%M:%S)" "$ref" "$phase" "$attempt" "$error" \
    >>"$(events_file_for "$ref")"
}

# Best-effort by design: reflection must never fail the run it is learning from.
run_reflect_phase() {
  local ref="$1" title="$2"
  [[ "$LOOP_LEARN" != "true" || "$DRY_RUN" == "true" ]] && return 0
  local ev
  ev="$(events_file_for "$ref")"
  [[ -s "$ev" ]] || return 0
  local before after
  before="$(cksum "$LOOP_LEARNINGS_FILE" 2>/dev/null || true)"
  log_info "phase ${C_BOLD}reflect${C_OFF} — distilling this story's failures into LEARNINGS.md"
  if ! run_agent_phase "reflect" "$LOOP_MODEL_REFLECT" \
    "$(printf 'The story loop hit failures while running story %s (%s). Distill them into scripts/loop/LEARNINGS.md per the reflect contract in your system context.\n\nFailure events:\n%s' \
      "$ref" "$title" "$(cat "$ev")")" \
    "reflect.md" "$ref" "$title"; then
    log_warn "reflect phase did not complete — continuing (self-improvement is best-effort)"
  fi
  after="$(cksum "$LOOP_LEARNINGS_FILE" 2>/dev/null || true)"
  if [[ "$before" == "$after" ]]; then
    log_warn "reflect changed nothing in LEARNINGS.md (valid if the failure was one-off noise)"
  else
    log_ok "LEARNINGS.md updated — future sessions inherit this lesson"
  fi
  : >"$ev" # events consumed — never reflect on the same failure twice
  maybe_compact_learnings
}

learnings_lines() {
  if [[ -f "$LOOP_LEARNINGS_FILE" ]]; then wc -l <"$LOOP_LEARNINGS_FILE"; else echo 0; fi
}

# Enforced compaction — a mechanism, not a reminder. Whenever LEARNINGS.md
# crosses LOOP_LEARN_COMPACT_AT lines, a dedicated session shrinks it (merge
# duplicates, generalize old entries) so the file stays small enough that the
# injected tail is dense signal, not archaeology. Best-effort like reflect:
# even if compaction fails, context stays bounded — build_addendum only ever
# injects the last LOOP_LEARN_MAX_LINES lines.
maybe_compact_learnings() {
  [[ "$LOOP_LEARN" != "true" || "$DRY_RUN" == "true" ]] && return 0
  local lines
  lines="$(learnings_lines)"
  ((lines <= LOOP_LEARN_COMPACT_AT)) && return 0
  log_info "phase ${C_BOLD}compact${C_OFF} — LEARNINGS.md is ${lines} lines (threshold ${LOOP_LEARN_COMPACT_AT})"
  if ! run_agent_phase "compact" "$LOOP_MODEL_REFLECT" \
    "$(printf 'scripts/loop/LEARNINGS.md is %s lines — over its %s-line threshold. Compact it to at most %s lines per the contract in your system context.' \
      "$lines" "$LOOP_LEARN_COMPACT_AT" "$LOOP_LEARN_COMPACT_AT")" \
    "compact.md" "learnings" "compaction"; then
    log_warn "compact phase did not complete — continuing (best-effort)"
  fi
  lines="$(learnings_lines)"
  if ((lines > LOOP_LEARN_COMPACT_AT)); then
    log_warn "LEARNINGS.md still ${lines} lines after compaction — sessions stay bounded (only the last ${LOOP_LEARN_MAX_LINES} lines are injected), but compact it by hand soon"
  else
    log_ok "LEARNINGS.md compacted to ${lines} lines"
  fi
}

# --- reasoning effort ----------------------------------------------------------------------
# effort_for_phase <phase-name> -> the LOOP_EFFORT_* value for that phase ("" = use
# the CLI default and omit the flag). Unknown phases deliberately fall through to
# empty rather than inheriting another phase's level.
effort_for_phase() {
  case "$1" in
    create-story) echo "${LOOP_EFFORT_CREATE_STORY:-}" ;;
    dev-story) echo "${LOOP_EFFORT_DEV_STORY:-}" ;;
    code-review) echo "${LOOP_EFFORT_CODE_REVIEW:-}" ;;
    commit) echo "${LOOP_EFFORT_COMMIT:-}" ;;
    reflect | compact) echo "${LOOP_EFFORT_REFLECT:-}" ;;
    *) echo "" ;;
  esac
}

# timeout_for_phase <phase> — seconds of wall-clock this phase may use.
# Same shape as effort_for_phase (resolved from the phase NAME, not a positional
# arg, so run_agent_phase's call sites stay untouched).
#
# Precedence, highest first:
#   1. an explicitly-set LOOP_PHASE_TIMEOUT_<PHASE>  (deliberate per-phase choice)
#   2. an explicitly-set LOOP_PHASE_TIMEOUT          (--phase-timeout / env global)
#   3. the built-in per-phase default from config.sh (dev-story gets the room)
#   4. the built-in global default
# Rule 2 above 3 is what keeps the global knob from looking inert once phases
# carry their own defaults. A phase with no entry here (commit/reflect/compact)
# always lands on the global. `0` is a real value at every level, never a fallback.
timeout_for_phase() {
  local t set_flag
  case "$1" in
    create-story) t="$LOOP_PHASE_TIMEOUT_CREATE_STORY" set_flag="${LOOP_PHASE_TIMEOUT_CREATE_STORY_SET:-}" ;;
    dev-story) t="$LOOP_PHASE_TIMEOUT_DEV_STORY" set_flag="${LOOP_PHASE_TIMEOUT_DEV_STORY_SET:-}" ;;
    code-review) t="$LOOP_PHASE_TIMEOUT_CODE_REVIEW" set_flag="${LOOP_PHASE_TIMEOUT_CODE_REVIEW_SET:-}" ;;
    *) echo "$LOOP_PHASE_TIMEOUT" && return 0 ;;
  esac
  # explicit per-phase wins outright; otherwise an explicit global beats this
  # phase's built-in default
  if [[ -n "$set_flag" ]]; then
    echo "$t"
  elif [[ -n "${LOOP_PHASE_TIMEOUT_SET:-}" ]]; then
    echo "$LOOP_PHASE_TIMEOUT"
  else
    echo "${t:-$LOOP_PHASE_TIMEOUT}"
  fi
}

# fmt_timeout <phase> — timeout_for_phase rendered for the run summary ("6h", "45m", "none").
fmt_timeout() {
  local s
  s="$(timeout_for_phase "$1")"
  if [[ "$s" == "0" ]]; then
    echo "none"
  elif ((s % 3600 == 0)); then
    echo "$((s / 3600))h"
  else
    echo "$((s / 60))m"
  fi
}

# --- phase runner ------------------------------------------------------------------------
# run_agent_phase <phase-name> <model> <user-prompt> <addendum-file> <ref> <title> [retry-ctx]
# Runs one fresh `claude -p` session, tees output to a log, and fails if the
# session ends with a LOOP_STATUS: BLOCKED marker or a non-zero exit.
run_agent_phase() {
  local phase="$1" model="$2" user_prompt="$3" addendum_file="$4" ref="$5" title="$6" retry_ctx="${7:-}"
  local addendum log_file
  addendum="$(build_addendum "$addendum_file" "$ref" "$title" "$retry_ctx")"
  log_file="$LOOP_LOG_DIR/$(date +%Y%m%d_%H%M%S)_${ref//./-}_${phase}.log"

  # Reasoning effort is resolved from the phase name (not a positional arg) so
  # all call sites stay unchanged. Empty => omit --effort, CLI default wins.
  local effort
  effort="$(effort_for_phase "$phase")"

  local -a cmd=("$LOOP_CLAUDE_CMD" -p "$user_prompt" --model "$model")
  [[ -n "$effort" ]] && cmd+=(--effort "$effort")
  [[ "$LOOP_MAX_TURNS" != "0" ]] && cmd+=(--max-turns "$LOOP_MAX_TURNS")
  # LOOP_CLAUDE_FLAGS is intentionally word-split (a list of flags)
  # shellcheck disable=SC2206
  cmd+=($LOOP_CLAUDE_FLAGS)

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  ${C_YELLOW}[dry-run]${C_OFF} phase=${phase} model=${model}${effort:+ effort=${effort}}"
    echo "            ${cmd[*]} --append-system-prompt '<prompts/unattended.md + prompts/${addendum_file} for ${ref}>'"
    return 0
  fi

  log_info "phase ${C_BOLD}${phase}${C_OFF} → model ${model} (fresh session; log: ${log_file#"$PROJECT_ROOT"/})"

  local phase_timeout
  phase_timeout="$(timeout_for_phase "$phase")"

  local rc=0
  if [[ "$phase_timeout" != "0" ]]; then
    (cd "$PROJECT_ROOT" && timeout --foreground "$phase_timeout" \
      "${cmd[@]}" --append-system-prompt "$addendum") 2>&1 | tee "$log_file" || rc=${PIPESTATUS[0]}
  else
    (cd "$PROJECT_ROOT" && "${cmd[@]}" --append-system-prompt "$addendum") 2>&1 |
      tee "$log_file" || rc=${PIPESTATUS[0]}
  fi

  if [[ $rc -eq 124 ]]; then
    LOOP_LAST_ERROR="phase '$phase' timed out after ${phase_timeout}s"
    log_err "$LOOP_LAST_ERROR"
    return 1
  fi
  if [[ $rc -ne 0 ]]; then
    LOOP_LAST_ERROR="phase '$phase' exited with code $rc (see $log_file)"
    log_err "$LOOP_LAST_ERROR"
    return 1
  fi

  local marker
  marker="$(tail -n 5 "$log_file" | grep -E '^LOOP_STATUS:' | tail -n 1 || true)"
  if [[ "$marker" == *"BLOCKED"* ]]; then
    LOOP_LAST_ERROR="phase '$phase' reported: ${marker#LOOP_STATUS: }"
    log_err "$LOOP_LAST_ERROR"
    return 1
  fi
  [[ -z "$marker" ]] && log_warn "phase '$phase' ended without a LOOP_STATUS marker — relying on the gate check"
  return 0
}

# --- gates (script-side truth, never the model's word) ------------------------------------
gate_create_story() {
  local ref="$1"
  [[ "$DRY_RUN" == "true" ]] && return 0
  if [[ "$(story_field "$ref" '.devStoryExists')" == "true" ]]; then
    log_ok "gate: dev story file exists for $ref"
    return 0
  fi
  LOOP_LAST_ERROR="gate failed: dev story file for $ref does not exist after create-story"
  log_err "$LOOP_LAST_ERROR"
  return 1
}

gate_dev_story() {
  local ref="$1"
  [[ "$DRY_RUN" == "true" ]] && return 0
  local status
  status="$(story_field "$ref" '.story.status')"
  if [[ "$status" != "done" ]]; then
    LOOP_LAST_ERROR="gate failed: status ledger says '$status' (expected 'done') for $ref after dev-story"
    log_err "$LOOP_LAST_ERROR"
    return 1
  fi
  log_ok "gate: status == done for $ref"
  # Typecheck FIRST: it is usually the cheapest gate and the one a test runner
  # cannot cover (vitest/jest transpile TS without type-checking). This is the
  # same check a pre-commit hook typically runs — catching it here means the
  # failure surfaces in dev-story, where a retry gets error context, instead of
  # in the commit phase, which cannot hand work back and just kills the story.
  if [[ "$LOOP_VERIFY_TYPECHECK" == "true" ]]; then
    run_verify_cmd typecheck || return 1
  fi
  if [[ "$LOOP_VERIFY_TEST" == "true" ]]; then
    run_verify_cmd test || return 1
  fi
  if [[ "$LOOP_VERIFY_BUILD" == "true" ]]; then
    run_verify_cmd build || return 1
  fi
  return 0
}

# --- knowledge-graph re-cluster (epic boundary) ---------------------------------
# `previousStory: null` from story-info means "first story of its epic" — the
# cadence at which we pay for a FULL graphify re-cluster (no --no-cluster).
# See LOOP_RECLUSTER_GRAPH in config.sh for why this is not per-commit.
is_epic_boundary() {
  local prev
  prev="$(story_field "$1" '.previousStory // "null"' 2>/dev/null || echo "")"
  [[ "$prev" == "null" ]]
}

# Best-effort by design: a stale graph must never fail a story the way a red
# suite does. It degrades query quality, it does not make the code wrong.
maybe_recluster_graph() {
  local ref="$1"
  [[ "$LOOP_RECLUSTER_GRAPH" != "true" ]] && return 0
  is_epic_boundary "$ref" || return 0
  # Self-disabling when graphify isn't part of this project (same guards as a
  # post-commit hook — the loop must work in a repo without the graph).
  [[ -f "$PROJECT_ROOT/graphify-out/graph.json" ]] || return 0
  PATH="$HOME/.local/bin:$PATH" command -v graphify >/dev/null 2>&1 || return 0

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  ${C_YELLOW}[dry-run]${C_OFF} step=recluster (epic boundary — $ref is first in its epic)"
    echo "            graphify update .   # FULL re-cluster: rebuilds community IDs + code↔docs edges + GRAPH_REPORT.md"
    return 0
  fi

  log_info "epic boundary — full graphify re-cluster before $ref (one API call; keeps code↔docs edges alive)"
  local timeout_prefix=()
  [[ "$LOOP_RECLUSTER_TIMEOUT" -gt 0 ]] && timeout_prefix=(timeout "$LOOP_RECLUSTER_TIMEOUT")
  if (cd "$PROJECT_ROOT" && PATH="$HOME/.local/bin:$PATH" \
    "${timeout_prefix[@]}" graphify update . >"$LOOP_LOG_DIR/last_recluster.log" 2>&1); then
    log_ok "graph re-clustered (log: $LOOP_LOG_DIR/last_recluster.log)"
  else
    # Non-fatal on purpose: warn loudly, keep going.
    log_warn "graphify re-cluster failed — continuing with a stale graph (log: $LOOP_LOG_DIR/last_recluster.log)"
  fi
  return 0
}

gate_commit() {
  [[ "$DRY_RUN" == "true" ]] && return 0
  if [[ -z "$(cd "$PROJECT_ROOT" && git status --porcelain)" ]]; then
    log_ok "gate: working tree clean"
    return 0
  fi
  LOOP_LAST_ERROR="gate failed: working tree still dirty after commit phase"
  log_err "$LOOP_LAST_ERROR"
  return 1
}

# --- scripted commit (LOOP_COMMIT_MODE=script) ----------------------------------------------
commit_story_script() {
  local ref="$1" title="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  ${C_YELLOW}[dry-run]${C_OFF} phase=commit mode=script"
    echo "            git add -A && git commit -m 'feat(story-${ref}): ${title}' (pre-commit hooks run; retries if hooks modify files)"
    return 0
  fi
  cd "$PROJECT_ROOT" || return 1
  if [[ -z "$(git status --porcelain)" ]]; then
    log_warn "nothing to commit for $ref (working tree already clean)"
    return 0
  fi
  log_info "phase ${C_BOLD}commit${C_OFF} (script mode)"
  git add -A
  local attempt=1 out
  local -a msg=(-m "feat(story-${ref}): ${title}"
    -m "SDD loop: /create-story → /dev-story → /code-review (story ${ref}).")
  [[ -n "$LOOP_COMMIT_TRAILER" ]] && msg+=(-m "$LOOP_COMMIT_TRAILER")
  while [[ $attempt -le 3 ]]; do
    if out="$(git commit "${msg[@]}" 2>&1)"; then
      log_ok "committed: $(git log -1 --oneline)"
      return 0
    fi
    # a pre-commit hook may rewrite files during the hook — restage and retry
    if [[ -n "$(git status --porcelain)" ]]; then
      log_warn "pre-commit hook modified files — restaging (attempt $attempt/3)"
      git add -A
      ((attempt++)) || true
    else
      break
    fi
  done
  LOOP_LAST_ERROR="git commit failed for $ref: $(echo "$out" | tail -n 20)"
  log_err "$LOOP_LAST_ERROR"
  return 1
}
