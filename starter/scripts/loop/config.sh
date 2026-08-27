# shellcheck shell=bash disable=SC2034
# (every var here is consumed by lib/common.sh)
# =============================================================================
# Story-loop configuration — autonomous runner for the SDD pipeline
# =============================================================================
# Every setting is an environment variable with a default, so you can override
# per-run (`LOOP_MODEL_DEV_STORY=opus ./loop.sh`), per-machine
# (scripts/loop/config.local.sh — gitignored), or via CLI flags (see --help).
# =============================================================================

# --- Claude Code invocation ---------------------------------------------------
# Each phase runs `claude -p "<slash command>"` = a FRESH headless session with
# the project's skills, rules, and CLAUDE.md loaded (do not add --bare).
LOOP_CLAUDE_CMD="${LOOP_CLAUDE_CMD:-claude}"

# Extra flags appended to every claude invocation. The loop is unattended, so
# permission prompts must never block it. The default skips the permission
# system entirely (same trade-off as any autonomous agent loop — run it on a
# branch / in a sandbox you trust). A tighter alternative is:
#   LOOP_CLAUDE_FLAGS="--permission-mode dontAsk"
# plus an allowlist in .claude/settings.json covering git/npm/npx.
LOOP_CLAUDE_FLAGS="${LOOP_CLAUDE_FLAGS:---dangerously-skip-permissions}"

# --- Spec-pipeline bridge --------------------------------------------------------
# The loop and the skills must share one definition of "next" and "done", so
# every spec-state question goes through the same helper CLI. Default is the
# starter kit's specs.py, resolved relative to the project root.
LOOP_SPECS_CLI="${LOOP_SPECS_CLI:-$PROJECT_ROOT/.claude/scripts/specs/specs.py}"
LOOP_PYTHON="${LOOP_PYTHON:-python3}"

# --- Model per phase -----------------------------------------------------------
# Aliases (fable | opus | sonnet | haiku) or full model ids both work (`claude --model`).
LOOP_MODEL_CREATE_STORY="${LOOP_MODEL_CREATE_STORY:-opus}"
LOOP_MODEL_DEV_STORY="${LOOP_MODEL_DEV_STORY:-sonnet}"
LOOP_MODEL_CODE_REVIEW="${LOOP_MODEL_CODE_REVIEW:-sonnet}"
LOOP_MODEL_COMMIT="${LOOP_MODEL_COMMIT:-haiku}"

# --- Reasoning effort per phase -------------------------------------------------
# `claude --effort` (low | medium | high | xhigh | max). EMPTY = omit the flag
# entirely and let the CLI pick its per-model default.
# High only where deeper reasoning actually changes the artifact: create-story
# (one bad story file misleads every later phase) and dev-story (the code).
# The mechanical phases (code-review's checklist, the commit message, and the
# deliberately-cheap haiku reflect/compact passes) stay on the default.
LOOP_EFFORT_CREATE_STORY="${LOOP_EFFORT_CREATE_STORY:-high}"
LOOP_EFFORT_DEV_STORY="${LOOP_EFFORT_DEV_STORY:-high}"
LOOP_EFFORT_CODE_REVIEW="${LOOP_EFFORT_CODE_REVIEW:-}"
LOOP_EFFORT_COMMIT="${LOOP_EFFORT_COMMIT:-}"
LOOP_EFFORT_REFLECT="${LOOP_EFFORT_REFLECT:-}"

# --- Commit phase ---------------------------------------------------------------
# script → deterministic `git add -A` + conventional message, pre-commit hooks
#          run normally (free, no model call).
# claude → a fresh claude session (LOOP_MODEL_COMMIT) reviews the diff and
#          writes the commit message itself.
LOOP_COMMIT_MODE="${LOOP_COMMIT_MODE:-script}"
# Optional trailer line appended to every scripted commit (e.g.
# "Co-Authored-By: Claude <noreply@anthropic.com>"). Empty = no trailer.
LOOP_COMMIT_TRAILER="${LOOP_COMMIT_TRAILER:-}"

# --- Verification gates (script-side, between phases) ---------------------------
# The loop never trusts a phase's word alone: after create-story it checks the
# dev story file exists; after dev-story it checks the status ledger == done and
# re-runs verification; after commit it checks the tree is clean.
#
# Each command has three states: "auto" (detect from the repo), a command
# string (run exactly that, from the project root), or empty "" (skip).
# auto-detection:
#   test       pagar gates (gates.config.json + gates/run-gates.mjs) if present,
#              else `npm test` when package.json declares a test script, else skip
#   typecheck  `npx tsc --noEmit` when a tsconfig.json exists, else skip
#              (test runners transpile TS without type-checking — the classic
#              "green suite, uncommittable commit" trap. Keep this on for TS.)
#   build      `npm run build` when package.json declares a build script, else skip
LOOP_VERIFY_TEST="${LOOP_VERIFY_TEST:-true}"
LOOP_VERIFY_TEST_CMD="${LOOP_VERIFY_TEST_CMD:-auto}"
LOOP_VERIFY_TYPECHECK="${LOOP_VERIFY_TYPECHECK:-true}"
LOOP_VERIFY_TYPECHECK_CMD="${LOOP_VERIFY_TYPECHECK_CMD:-auto}"
LOOP_VERIFY_BUILD="${LOOP_VERIFY_BUILD:-false}"
LOOP_VERIFY_BUILD_CMD="${LOOP_VERIFY_BUILD_CMD:-auto}"

# --- Knowledge-graph re-cluster (epic boundary) ----------------------------------
# A post-commit hook may refresh graphify with `--no-cluster`: graph.json
# re-extracts every commit (so `graphify query` stays current — it reads that file
# and nothing else), but the LLM pass that assigns community IDs and draws the
# code↔docs edges is skipped, because it costs an API call per commit.
# Left skipped forever, every new code node lands with an empty community and the
# graph decays into two disjoint layers. The epic boundary is the right cadence
# to pay for it: one full re-cluster before the first story of each epic, when a
# whole epic of new code has landed and cross-layer questions start getting
# asked. Self-disabling: no-ops when the graphify CLI or graph.json is absent.
LOOP_RECLUSTER_GRAPH="${LOOP_RECLUSTER_GRAPH:-true}"
LOOP_RECLUSTER_TIMEOUT="${LOOP_RECLUSTER_TIMEOUT:-900}" # seconds; 0 = no timeout

# --- Self-improvement (compound engineering for the harness) ----------------------
# When a story hits any failure, a cheap "reflect" session distills it into
# scripts/loop/LEARNINGS.md (committed with the story); the last
# LOOP_LEARN_MAX_LINES of that file are injected into every phase session's
# system context — so the loop gets smarter with each error.
LOOP_LEARN="${LOOP_LEARN:-true}"
LOOP_MODEL_REFLECT="${LOOP_MODEL_REFLECT:-haiku}"
LOOP_LEARN_MAX_LINES="${LOOP_LEARN_MAX_LINES:-80}"  # lines injected per session (hard bound)
LOOP_LEARN_COMPACT_AT="${LOOP_LEARN_COMPACT_AT:-120}" # file lines that trigger the compaction pass
LOOP_LEARNINGS_FILE="${LOOP_LEARNINGS_FILE:-}" # default: scripts/loop/LEARNINGS.md (set in loop.sh)

# --- Failure handling ------------------------------------------------------------
# stop  → end the loop on first failure (default; safest unattended)
# pause → ask at the terminal: retry / skip / quit (needs a TTY; falls back to stop)
# skip  → record the failure and move on (only useful with an explicit --story list)
LOOP_ON_FAILURE="${LOOP_ON_FAILURE:-stop}"
LOOP_MAX_RETRIES="${LOOP_MAX_RETRIES:-1}" # extra attempts per phase, with error feedback

# --- Limits ------------------------------------------------------------------------
LOOP_MAX_STORIES="${LOOP_MAX_STORIES:-0}"     # 0 = run until no planned stories remain
# Global fallback for any phase without its own value below. Setting this
# EXPLICITLY (env or --phase-timeout) also overrides the built-in per-phase
# defaults, so the knob never looks inert; an explicitly-set LOOP_PHASE_TIMEOUT_*
# still wins over it. `LOOP_PHASE_TIMEOUT_SET` records which happened.
LOOP_PHASE_TIMEOUT_SET="${LOOP_PHASE_TIMEOUT+set}"
LOOP_PHASE_TIMEOUT="${LOOP_PHASE_TIMEOUT:-3600}" # seconds per phase; 0 = no timeout
LOOP_MAX_TURNS="${LOOP_MAX_TURNS:-0}"         # claude --max-turns per phase; 0 = unlimited

# Per-phase wall-clock, resolved by `timeout_for_phase` (lib/common.sh); empty =>
# fall back to LOOP_PHASE_TIMEOUT above. One flat timeout is wrong in both
# directions: a value generous enough for dev-story lets a wedged create-story
# idle for hours, and a value tight enough to catch that kills dev-story mid-task.
# A timeout is NOT a safety gate (the gates are) — it only bounds a wedged
# session, so the implementing phases get real room. 0 = no timeout for that phase.
# Each records whether it was set explicitly, so `timeout_for_phase` can tell a
# deliberate per-phase choice (always wins) from a built-in default (which an
# explicit global overrides).
LOOP_PHASE_TIMEOUT_CREATE_STORY_SET="${LOOP_PHASE_TIMEOUT_CREATE_STORY+set}"
LOOP_PHASE_TIMEOUT_DEV_STORY_SET="${LOOP_PHASE_TIMEOUT_DEV_STORY+set}"
LOOP_PHASE_TIMEOUT_CODE_REVIEW_SET="${LOOP_PHASE_TIMEOUT_CODE_REVIEW+set}"
LOOP_PHASE_TIMEOUT_CREATE_STORY="${LOOP_PHASE_TIMEOUT_CREATE_STORY:-3600}"
LOOP_PHASE_TIMEOUT_DEV_STORY="${LOOP_PHASE_TIMEOUT_DEV_STORY:-21600}"  # 6h — implement + tests + gates
LOOP_PHASE_TIMEOUT_CODE_REVIEW="${LOOP_PHASE_TIMEOUT_CODE_REVIEW:-7200}" # 2h — review + doc sync

# --- Logging --------------------------------------------------------------------------
LOOP_LOG_DIR="${LOOP_LOG_DIR:-}" # default: scripts/loop/logs (set in loop.sh)

# --- Local overrides (gitignored) --------------------------------------------------------
_loop_config_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${_loop_config_dir}/config.local.sh" ]]; then
  # shellcheck source=/dev/null
  source "${_loop_config_dir}/config.local.sh"
fi
unset _loop_config_dir
