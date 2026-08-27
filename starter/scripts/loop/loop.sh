#!/usr/bin/env bash
# =============================================================================
# SDD story loop — run stories end-to-end, autonomously
# =============================================================================
# Runs stories end-to-end, each phase in a FRESH headless Claude Code session
# (`claude -p`), with a per-phase model:
#
#   /create-story <ref>  →  /dev-story <ref>  →  /code-review <ref>  →  commit
#        (opus)                (sonnet)             (sonnet)         (script|haiku)
#
# then moves to the next story. Entirely optional: every phase is the same
# skill an engineer runs by hand — the loop only sequences and verifies them.
#
# Usage:
#   scripts/loop/loop.sh [options]
#
#   --story <ref>         run only this story; repeatable, runs in given order
#   --from <ref>          run a range: first story (inclusive); omit --to = to the end
#   --to <ref>            run a range: last story (inclusive); omit --from = from the start
#                         (ranges follow plan order, skip stories already done,
#                          and cannot be combined with --story)
#   --max <n>             stop after n stories (default: all planned)
#   --dry-run             print what would run (stories, phases, models); no changes
#   --interactive         pause for confirmation between stories
#   --on-failure <mode>   stop | pause | skip   (default: stop)
#   --create-model <m>    model for /create-story   (default: opus)
#   --dev-model <m>       model for /dev-story      (default: sonnet)
#   --review-model <m>    model for /code-review    (default: sonnet)
#   --commit-model <m>    model for the commit phase when --commit-mode claude
#   --commit-mode <m>     script | claude           (default: script)
#   --effort <level>      reasoning effort for the create-story + dev-story phases:
#                         low | medium | high | xhigh | max   (default: high)
#                         per-phase overrides: LOOP_EFFORT_* in config.sh
#   --phase-timeout <s>   wall-clock per phase, in seconds; 0 = no timeout.
#                         Flattens every phase onto one value. By default the
#                         timeout is PER PHASE (dev-story gets far more room than
#                         create-story) — see LOOP_PHASE_TIMEOUT_* in config.sh.
#   --no-recluster        skip the full `graphify update .` that otherwise runs
#                         once per EPIC (before the epic's first story). That
#                         re-cluster costs one API call and is what keeps the
#                         knowledge graph's code↔docs edges alive; the per-commit
#                         hook only does the free AST pass. No-ops automatically
#                         when graphify isn't installed / no graph exists.
#   --help
#
# Configuration: scripts/loop/config.sh (env vars, config.local.sh overrides).
# =============================================================================

# shellcheck disable=SC1091,SC2034,SC2317
# (config.sh/lib/common.sh are sourced and use these globals; gate_none is
#  invoked indirectly by name through run_phase_with_retry)
set -euo pipefail

LOOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${LOOP_PROJECT_ROOT:-$(cd "$LOOP_DIR/../.." && pwd)}"

DRY_RUN=false
INTERACTIVE=false
declare -a STORY_LIST=()
MAX_OVERRIDE=""
RANGE_FROM=""
RANGE_TO=""

# shellcheck source=config.sh
source "$LOOP_DIR/config.sh"

print_usage() { sed -n '/^# Usage:/,/^# Configuration:/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --story)
      STORY_LIST+=("$2")
      shift 2
      ;;
    --from)
      RANGE_FROM="$2"
      shift 2
      ;;
    --to)
      RANGE_TO="$2"
      shift 2
      ;;
    --max)
      MAX_OVERRIDE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --interactive)
      INTERACTIVE=true
      shift
      ;;
    --no-recluster)
      LOOP_RECLUSTER_GRAPH=false
      shift
      ;;
    --on-failure)
      LOOP_ON_FAILURE="$2"
      shift 2
      ;;
    --create-model)
      LOOP_MODEL_CREATE_STORY="$2"
      shift 2
      ;;
    --dev-model)
      LOOP_MODEL_DEV_STORY="$2"
      shift 2
      ;;
    --review-model)
      LOOP_MODEL_CODE_REVIEW="$2"
      shift 2
      ;;
    --commit-model)
      LOOP_MODEL_COMMIT="$2"
      shift 2
      ;;
    --commit-mode)
      LOOP_COMMIT_MODE="$2"
      shift 2
      ;;
    --effort)
      case "$2" in
        low | medium | high | xhigh | max) ;;
        *)
          # NB: common.sh (log_err) is sourced AFTER arg parsing — use plain echo here.
          echo "loop.sh: --effort expects low|medium|high|xhigh|max (got '$2')" >&2
          exit 1
          ;;
      esac
      # Sets the two reasoning phases; per-phase LOOP_EFFORT_* still override via env.
      LOOP_EFFORT_CREATE_STORY="$2"
      LOOP_EFFORT_DEV_STORY="$2"
      shift 2
      ;;
    --phase-timeout)
      case "$2" in
        "" | *[!0-9]*)
          # NB: common.sh (log_err) is sourced AFTER arg parsing — use plain echo here.
          echo "loop.sh: --phase-timeout expects seconds as a whole number, 0 = none (got '$2')" >&2
          exit 1
          ;;
      esac
      # An EXPLICIT global: overrides the built-in per-phase defaults (so the
      # flag is never inert), while an explicitly-set LOOP_PHASE_TIMEOUT_* env
      # var still wins over it. config.sh is sourced BEFORE this parse loop, so
      # the _SET marker it derives is already fixed — set it here by hand.
      LOOP_PHASE_TIMEOUT="$2"
      LOOP_PHASE_TIMEOUT_SET="set"
      shift 2
      ;;
    --help | -h)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage
      exit 1
      ;;
  esac
done

[[ -n "$MAX_OVERRIDE" ]] && LOOP_MAX_STORIES="$MAX_OVERRIDE"
LOOP_LOG_DIR="${LOOP_LOG_DIR:-$LOOP_DIR/logs}"
mkdir -p "$LOOP_LOG_DIR"
LOOP_LEARNINGS_FILE="${LOOP_LEARNINGS_FILE:-$LOOP_DIR/LEARNINGS.md}"
LOOP_LAST_ERROR=""

# shellcheck source=lib/common.sh
source "$LOOP_DIR/lib/common.sh"
check_prereqs

# ---------------------------------------------------------------------------
# Range mode (--from / --to) — expands to the same explicit STORY_LIST that
# --story uses, so everything downstream is identical. Inclusive bounds, plan
# order (epic.story numeric), stories already `done` are filtered out.
# ---------------------------------------------------------------------------
ref_le() { # ref_le A B → true when A <= B in (epic, story) numeric order
  local a_e="${1%%.*}" a_s="${1##*.}" b_e="${2%%.*}" b_s="${2##*.}"
  ((a_e < b_e || (a_e == b_e && a_s <= b_s)))
}

resolve_range() {
  local bound
  for bound in "$RANGE_FROM" "$RANGE_TO"; do
    if [[ -n "$bound" && ! "$bound" =~ ^[0-9]+\.[0-9]+$ ]]; then
      log_err "--from/--to expects an epic.story ref like 1.3 (got '$bound')"
      exit 1
    fi
  done
  # ordered "ref status" pairs straight from the plan
  local rows
  rows="$(specs --json list | jq -r '
    .[]
    | (.id | capture("^epic-(?<e>[0-9]+)").e | tonumber) as $e
    | .stories[]
    | "\($e).\(.id | capture("^story-(?<s>[0-9]+)").s | tonumber) \(.status)"
  ')"
  local ref status
  while read -r ref status; do
    [[ -z "$ref" ]] && continue
    [[ -n "$RANGE_FROM" ]] && ! ref_le "$RANGE_FROM" "$ref" && continue
    [[ -n "$RANGE_TO" ]] && ! ref_le "$ref" "$RANGE_TO" && continue
    if [[ "$status" == "done" ]]; then
      log_info "range: $ref already done — skipping"
      continue
    fi
    STORY_LIST+=("$ref")
  done <<<"$rows"
  if [[ ${#STORY_LIST[@]} -eq 0 ]]; then
    log_warn "range ${RANGE_FROM:-start}..${RANGE_TO:-end} matched no runnable stories (check specs.py list)"
  else
    log_info "range ${RANGE_FROM:-start}..${RANGE_TO:-end} → ${STORY_LIST[*]}"
  fi
}

if [[ -n "$RANGE_FROM" || -n "$RANGE_TO" ]]; then
  if [[ ${#STORY_LIST[@]} -gt 0 ]]; then
    log_err "--from/--to cannot be combined with --story (pick one selection mode)"
    exit 1
  fi
  resolve_range
fi

declare -a FAILED_REFS=() DONE_REFS=()
STORY_CURSOR=0

# ---------------------------------------------------------------------------
# Target resolution — one story ref per iteration.
# Explicit --story list wins; otherwise an unfinished dev story (resume) takes
# priority over the next planned one, all via specs.py so the loop and the
# skills share one definition of "next".
# ---------------------------------------------------------------------------
resolve_next_ref() {
  if [[ ${#STORY_LIST[@]} -gt 0 ]]; then
    [[ $STORY_CURSOR -ge ${#STORY_LIST[@]} ]] && return 1
    NEXT_REF="${STORY_LIST[$STORY_CURSOR]}"
    ((STORY_CURSOR++)) || true
    return 0
  fi
  local json ref
  json="$(specs --json next-dev 2>/dev/null || true)"
  if [[ "$(jq -r '.found // empty' <<<"$json")" == "true" ]]; then
    ref="$(jq -r '.ref' <<<"$json")"
  else
    json="$(specs --json next-story 2>/dev/null || true)"
    [[ "$(jq -r '.found // empty' <<<"$json")" == "true" ]] || return 1
    ref="$(jq -r '.ref' <<<"$json")"
  fi
  # A ref that already failed this run would loop forever in auto mode — stop.
  local f
  for f in "${FAILED_REFS[@]:-}"; do
    if [[ "$f" == "$ref" ]]; then
      log_warn "next candidate $ref already failed this run — stopping auto-resolution"
      return 1
    fi
  done
  NEXT_REF="$ref"
  return 0
}

# run_phase_with_retry <phase> <model> <prompt> <addendum> <ref> <title> <gate-fn>
run_phase_with_retry() {
  local phase="$1" model="$2" prompt="$3" addendum="$4" ref="$5" title="$6" gate="$7"
  local attempt=0 retry_ctx=""
  while true; do
    if run_agent_phase "$phase" "$model" "$prompt" "$addendum" "$ref" "$title" "$retry_ctx" &&
      "$gate" "$ref"; then
      return 0
    fi
    ((attempt++)) || true
    record_failure_event "$ref" "$phase" "$attempt" "$LOOP_LAST_ERROR"
    if [[ $attempt -gt $LOOP_MAX_RETRIES || "$DRY_RUN" == "true" ]]; then
      return 1
    fi
    retry_ctx="$LOOP_LAST_ERROR"
    log_warn "retrying phase '$phase' for $ref with error feedback (attempt $((attempt + 1))/$((LOOP_MAX_RETRIES + 1)))"
  done
}

gate_none() { return 0; }

run_story() {
  local ref="$1"
  local title status dev_exists
  if [[ "$DRY_RUN" == "true" ]]; then
    title="$(story_field "$ref" '.story.title // empty' || true)"
    status="$(story_field "$ref" '.story.status // empty' || true)"
    dev_exists="$(story_field "$ref" '.devStoryExists // empty' || true)"
    : "${title:=(unresolved)}" "${status:=planned}" "${dev_exists:=false}"
  else
    title="$(story_field "$ref" '.story.title')" || {
      LOOP_LAST_ERROR="story $ref not found in the plan (specs.py story-info failed)"
      log_err "$LOOP_LAST_ERROR"
      return 1
    }
    status="$(story_field "$ref" '.story.status')"
    dev_exists="$(story_field "$ref" '.devStoryExists')"
  fi

  log_header "STORY $ref — ${title} [${status}]"

  # fresh failure ledger for this story (feeds the reflect phase)
  [[ "$DRY_RUN" != "true" && "$LOOP_LEARN" == "true" ]] && : >"$(events_file_for "$ref")"

  # Step 0: knowledge-graph re-cluster, only when this story opens a new epic.
  # Runs BEFORE create-story so the analysis phase queries a freshly clustered
  # graph. Best-effort — never fails the story (see maybe_recluster_graph).
  maybe_recluster_graph "$ref"

  # Phase 1: /create-story (skipped when the dev story file already exists)
  if [[ "$dev_exists" == "true" ]]; then
    log_info "dev story file already exists — skipping create-story (resume)"
  else
    run_phase_with_retry "create-story" "$LOOP_MODEL_CREATE_STORY" \
      "/create-story $ref" "create-story.md" "$ref" "$title" gate_create_story || return 1
  fi

  # Phase 2: /dev-story (skipped when the status ledger already says done)
  if [[ "$status" == "done" ]]; then
    log_info "status already 'done' — skipping dev-story (resume)"
  else
    run_phase_with_retry "dev-story" "$LOOP_MODEL_DEV_STORY" \
      "/dev-story $ref" "dev-story.md" "$ref" "$title" gate_dev_story || return 1
  fi

  # Phase 3: /code-review (no hard artifact gate — marker + exit code)
  run_phase_with_retry "code-review" "$LOOP_MODEL_CODE_REVIEW" \
    "/code-review $ref" "code-review.md" "$ref" "$title" gate_none || return 1

  # Phase 3.5: reflect (self-improvement) — only when this story hit failures.
  # Runs BEFORE commit so the distilled lesson ships inside the story's commit
  # and compounds: build_addendum injects LEARNINGS.md into every future session.
  if [[ "$DRY_RUN" == "true" ]]; then
    if [[ "$LOOP_LEARN" == "true" ]]; then
      echo "  ${C_YELLOW}[dry-run]${C_OFF} phase=reflect model=${LOOP_MODEL_REFLECT} (conditional — only if a phase failed this story; distills the failure into LEARNINGS.md before commit)"
    fi
  else
    run_reflect_phase "$ref" "$title"
  fi

  # Phase 4: commit
  if [[ "$LOOP_COMMIT_MODE" == "claude" ]]; then
    run_phase_with_retry "commit" "$LOOP_MODEL_COMMIT" \
      "Commit all pending changes for story $ref as ONE conventional commit. Follow the system addendum." \
      "commit.md" "$ref" "$title" gate_commit || return 1
  else
    if ! commit_story_script "$ref" "$title" || ! gate_commit "$ref"; then
      record_failure_event "$ref" "commit" 1 "$LOOP_LAST_ERROR"
      return 1
    fi
  fi

  log_ok "story $ref complete"
  return 0
}

handle_story_failure() {
  local ref="$1"
  # Learn from the terminal failure too — the lesson lands on disk even when the
  # run stops here (it gets committed with the eventual fix).
  run_reflect_phase "$ref" "(story failed this run)" || true
  FAILED_REFS+=("$ref")
  case "$LOOP_ON_FAILURE" in
    skip)
      log_warn "story $ref failed — skipping (on-failure=skip)"
      return 0
      ;;
    pause)
      if [[ -t 0 ]]; then
        echo "${C_YELLOW}Story $ref failed: ${LOOP_LAST_ERROR}${C_OFF}"
        echo "  [r] retry story   [s] skip to next   [q] quit"
        local choice
        read -r choice
        case "$choice" in
          r)
            FAILED_REFS=("${FAILED_REFS[@]/$ref/}")
            if run_story "$ref"; then
              DONE_REFS+=("$ref")
              return 0
            fi
            FAILED_REFS+=("$ref")
            return 1
            ;;
          s) return 0 ;;
          *) return 1 ;;
        esac
      fi
      log_err "on-failure=pause but no TTY — stopping"
      return 1
      ;;
    *) return 1 ;; # stop
  esac
}

main() {
  log_header "SDD STORY LOOP"
  log_info "project:  $PROJECT_ROOT"
  log_info "models:   create-story=$LOOP_MODEL_CREATE_STORY  dev-story=$LOOP_MODEL_DEV_STORY  code-review=$LOOP_MODEL_CODE_REVIEW  commit=$LOOP_COMMIT_MODE$([[ "$LOOP_COMMIT_MODE" == "claude" ]] && echo "($LOOP_MODEL_COMMIT)")"
  log_info "learning: $([[ "$LOOP_LEARN" == "true" ]] && echo "on — reflect=$LOOP_MODEL_REFLECT, inject last $LOOP_LEARN_MAX_LINES lines, compact at $LOOP_LEARN_COMPACT_AT" || echo "off (LOOP_LEARN=false)")"
  # a LEARNINGS.md that crossed the threshold outside a run (merge, hand edits)
  # gets compacted up front, before any session inherits the bloat
  maybe_compact_learnings
  log_info "verify:   test=$(fmt_verify test)  typecheck=$(fmt_verify typecheck)  build=$(fmt_verify build)"
  log_info "failure:  $LOOP_ON_FAILURE · retries/phase: $LOOP_MAX_RETRIES · max stories: $([[ "$LOOP_MAX_STORIES" == "0" ]] && echo "all" || echo "$LOOP_MAX_STORIES")"
  log_info "timeout:  create-story=$(fmt_timeout create-story)  dev-story=$(fmt_timeout dev-story)  code-review=$(fmt_timeout code-review)"
  [[ "$DRY_RUN" == "true" ]] && log_warn "DRY RUN — nothing will be executed, no state will change"

  local count=0
  while true; do
    if [[ "$LOOP_MAX_STORIES" != "0" && $count -ge $LOOP_MAX_STORIES ]]; then
      log_info "reached --max $LOOP_MAX_STORIES — stopping"
      break
    fi
    if ! resolve_next_ref; then
      if [[ $count -eq 0 && ${#FAILED_REFS[@]} -eq 0 ]]; then
        log_ok "Nothing to do — no planned stories and no unfinished dev stories. (Run /epics to add more.)"
      fi
      break
    fi
    local ref="$NEXT_REF"

    if [[ "$INTERACTIVE" == "true" && "$DRY_RUN" != "true" && -t 0 && $count -gt 0 ]]; then
      echo "${C_CYAN}Next story: $ref — press Enter to run, 'q' to stop here...${C_OFF}"
      local go
      read -r go
      [[ "$go" == "q" ]] && break
    fi

    if run_story "$ref"; then
      DONE_REFS+=("$ref")
    else
      handle_story_failure "$ref" || break
    fi
    ((count++)) || true

    # In dry-run mode state never changes, so auto-resolution would return the
    # same story forever — show one full iteration and stop.
    if [[ "$DRY_RUN" == "true" && ${#STORY_LIST[@]} -eq 0 ]]; then
      log_info "(dry-run) later iterations resolve at runtime as statuses change — stopping after one"
      break
    fi
  done

  log_header "SDD STORY LOOP — run summary"
  log_info "completed: ${#DONE_REFS[@]}  (${DONE_REFS[*]:-—})"
  if [[ ${#FAILED_REFS[@]} -gt 0 ]]; then
    log_err "failed:    ${#FAILED_REFS[@]}  (${FAILED_REFS[*]})"
    exit 1
  fi
  exit 0
}

main
