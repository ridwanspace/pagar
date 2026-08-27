# SDD story loop (optional)

Runs stories from the spec pipeline end-to-end, unattended:

```
/create-story <ref>  →  /dev-story <ref>  →  /code-review <ref>  →  commit
     (opus)               (sonnet)              (sonnet)         (script | haiku)
```

…then moves to the next story — one conventional commit per story, and a **fresh
headless session per phase** (`claude -p "/skill <ref>"`). No context bleeds between
phases; the story file, the status ledger, and git are the only shared state. The loop
is entirely **optional**: every phase is the exact same skill an engineer runs by hand,
so you can run one story manually today and let the loop run five tomorrow.

The discipline behind this harness is
[docs/08-loop-engineering.md](https://github.com/ridwanspace/pagar/blob/main/docs/08-loop-engineering.md)
in the pagar repo; the debug/modify/verify manual is the `loop-engineering` skill.

## Prerequisites

- `claude` (Claude Code CLI) installed and authenticated, `jq`, `git`, `python3`.
- A PRD + epics already exist (`/create-prd` → `/epics`), so the status ledger has
  `planned` stories. The loop never invents work — it only pulls from the plan.
- Verification gates are auto-detected: pagar gates (`gates.config.json` +
  `gates/run-gates.mjs`) if present, else `npm test` / `tsc --noEmit` when applicable.
  Override with `LOOP_VERIFY_TEST_CMD` / `LOOP_VERIFY_TYPECHECK_CMD` / `LOOP_VERIFY_BUILD_CMD`.

## Quick start

```bash
# 1. Preview — resolves the next story and prints every command it would run
scripts/loop/loop.sh --dry-run

# 2. First real run: one story, watching the terminal
scripts/loop/loop.sh --max 1

# 3. Then let it run the backlog
scripts/loop/loop.sh
```

## What a story looks like

For each story, in order:

1. **`/create-story`** (fresh session) — writes the self-contained dev story file.
   *Gate:* the file must exist (checked via `specs.py story-info`, never the model's word).
2. **`/dev-story`** (fresh session) — implements, tests, sets status `done`.
   *Gates:* status is `done`, then the script re-runs typecheck and tests itself.
3. **`/code-review`** (fresh session) — the review skill's steps, unattended rules
   applied (decide per the three-tier rule; visual sign-off recorded as
   PENDING HUMAN REVIEW, never claimed).
4. **reflect** (conditional, best-effort) — only when a phase failed this story:
   a cheap session distills the failure into `LEARNINGS.md` **before** commit, so the
   lesson ships with the story. The last 80 lines of that file are injected into every
   future session — the harness compounds.
5. **commit** — one conventional commit per story (`script` mode by default:
   deterministic, hooks run; `claude` mode lets a session write the message).
   *Gate:* the working tree must be clean afterward.

Skip-logic makes every phase resumable: an existing dev story file skips create; a
`done` status skips dev. Ranges (`--from/--to`) follow plan order and skip done stories.

## Configuration

Everything is an env var with a default (`config.sh`), overridable per-run, per-machine
(`config.local.sh`, gitignored), or via flags (`loop.sh --help` for the full list):

| Knob | Default | Meaning |
| --- | --- | --- |
| `LOOP_MODEL_*` | opus / sonnet / sonnet / haiku | Model per phase (create/dev/review/commit) |
| `LOOP_EFFORT_*` | high, high, — | Reasoning effort per phase; empty = CLI default |
| `LOOP_VERIFY_TEST_CMD` | `auto` | pagar gates → `npm test` → skip |
| `LOOP_VERIFY_TYPECHECK_CMD` | `auto` | `npx tsc --noEmit` when a tsconfig exists, else skip |
| `LOOP_VERIFY_BUILD_CMD` | `auto` | `npm run build` when declared, else skip |
| `LOOP_ON_FAILURE` | `stop` | `stop` \| `pause` (TTY) \| `skip` |
| `LOOP_MAX_RETRIES` | `1` | Extra attempts per phase, with the error fed back |
| `LOOP_PHASE_TIMEOUT_*` | 1h / 6h / 2h | Wall-clock per phase; `0` = none |
| `LOOP_LEARN` | `true` | Reflect + LEARNINGS.md injection + compaction |
| `LOOP_COMMIT_MODE` | `script` | `script` (deterministic) \| `claude` (session writes it) |

## Dry-run is a law

`--dry-run` prints the exact commands real mode would run — stories, phases, models,
gates — and executes nothing. Every execution path in this script keeps that promise,
and `loop.test.sh` proves it:

```bash
bash scripts/loop/loop.test.sh
```

Zero dependencies beyond the loop's own prereqs (bash, jq, git, python3). The suite
never invokes the Claude CLI — it drives `--dry-run` against throwaway fixtures.
A guard these tests never saw RED proves nothing: mutation-verify new assertions
(break the code on purpose, watch the test fail, restore).

## Safety notes

- The default `LOOP_CLAUDE_FLAGS` skips Claude Code's permission system entirely —
  the loop is unattended and prompts would wedge it. Run the loop on a branch you
  trust, or tighten with `--permission-mode dontAsk` + a settings allowlist.
- The loop never pushes, never switches branches, never passes `--no-verify`.
  Those are invariants, not defaults — see the loop-engineering skill before
  changing them.
- `logs/` is gitignored; `LEARNINGS.md` is committed on purpose — it is the
  harness's compounding memory.
