---
name: loop-engineering
description: 'Debug, fix, or modify the unattended story loop (the create-story → dev-story → review → commit runner). Use when the user says "/loop-engineering", "the loop failed", "debug the story loop", "why did the loop stop", "change the loop models", "add a phase to the loop", or asks to modify the loop script, its gates, or its prompts.'
---

# Loop Engineering (debug · fix · modify)

**Goal:** Keep an unattended agent loop trustworthy while adapting it to the engineer's
preference. A good loop is deliberately boring — a shell script, a few phase prompts,
and hard gates between phases. Almost every incident is either a _phase_ failure (the
headless agent session), a _gate_ failure (the script-side check), or a _wiring_
mistake (flags, prompts, and docs drifting apart). This skill routes you to the right
one fast and keeps every modification honest: test-first, dry-run-proven, docs-synced.

**Your role:** the engineer who owns the harness, not the stories. You fix the loop's
machinery; you do NOT re-implement stories, edit spec artifacts, or touch the pipeline
skills themselves from here (that is `/create-story` / `/dev-story` / `/code-review`
territory).

The discipline behind this skill is written up in pagar's repo:
https://github.com/ridwanspace/pagar/blob/main/docs/08-loop-engineering.md —
this file is the working manual. The reference implementation ships beside this
starter as `scripts/loop/` (loop.sh, config.sh, lib/common.sh, prompts/,
LEARNINGS.md, loop.test.sh).

## Conventions

- Bare paths (e.g. `steps/step-01-diagnose.md`) resolve from this skill's root.
- All project paths are relative to the project root.
- The reference loop lives in `scripts/loop/`. If yours differs, map your files onto
  these roles before proceeding:

| File                    | Owns                                                                                                                                                                        |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `loop.sh`               | CLI parsing, range resolution (`--from/--to`), target resolution, the per-story phase sequence, retry wrapper, failure handling, summary                                     |
| `config.sh`             | Every tunable as an env var with a default (models per phase, gates, timeouts, failure mode); sources gitignored `config.local.sh` last                                      |
| `lib/common.sh`         | Logging, the bridge to the spec-state helper CLI, prompt assembly, the headless runner, the gates, the scripted commit                                                       |
| `prompts/unattended.md` | The system addendum every phase gets: no-human rules + the `LOOP_STATUS:` marker contract                                                                                   |
| `prompts/<phase>.md`    | Per-phase contract ({{REF}}/{{TITLE}} substituted): what success means, what NOT to do (e.g. dev-story must not commit)                                                     |
| `LEARNINGS.md`          | The loop's compounding memory (committed): reflect sessions distill each failure into a rule; the newest `LOOP_LEARN_MAX_LINES` lines are injected into every phase session |
| `prompts/reflect.md`    | The reflect contract: touch ONLY `LEARNINGS.md`, merge don't duplicate, actionable rules, compact past ~120 lines                                                           |
| `loop.test.ts`          | Dry-run guard tests against a throwaway fixture — the loop's only automated safety net                                                                                      |
| `logs/` (gitignored)    | One log per phase session (`<ts>_<ref>_<phase>.log`) + per-story failure-event ledgers                                                                                      |

## Load-bearing invariants (never weaken without the user explicitly deciding to)

1. **Fresh session per phase.** Each phase is one headless agent invocation with its
   own prompt (for Claude Code: `claude -p "/skill <ref>"`). Never add
   `--continue`/`--resume`; state flows ONLY through story files, the spec-status
   ledger, and git.
2. **The user prompt stays a bare slash command.** Extra instructions travel via the
   system-prompt addendum — text appended to the prompt becomes the skill's
   _arguments_.
3. **Gates are the truth; markers are advisory.** `LOOP_STATUS: COMPLETE` is never
   sufficient — the script verifies artifacts (file exists, status is `done`, the
   project's tests pass, clean tree). Never replace a gate with trust in the model's
   word.
4. **`--dry-run` executes nothing and mutates nothing.** Every new execution path
   needs a dry-run branch AND a test proving it prints instead of runs.
5. **No `--no-verify`, no pushing, no branch switching** — in the scripts and in the
   prompt contracts alike.
6. **The spec-state CLI is the only reader/writer of spec state.** Never hand-parse
   the status ledger in bash; add a subcommand if one is missing.
7. **Every new flag lands in four places:** the `loop.sh` header comment (`--help` is
   extracted from it), the loop's README, the project README's loop section, and
   `loop.test.ts`.
8. **Neutral naming.** Name the machinery for what it does — "story loop", "SDD loop",
   `LOOP_*` variables — never for a person, project, or meme. Renames are cheap now
   and expensive after the logs accumulate.

## Workflow (step-file discipline)

Step files run **one at a time**; load only the one you're on.

1. `steps/step-01-diagnose.md` — a run failed, stopped, or behaved unexpectedly:
   read the right log, classify the failure (phase / gate / resolution / environment),
   reproduce cheaply.
2. `steps/step-02-modify.md` — change the loop (models, flags, gates, phases,
   prompts, failure policy): pick the smallest correct layer, write the failing test
   first.
3. `steps/step-03-verify.md` — prove the loop still holds: syntax, dry-run matrix,
   full suite, mutation-verify, docs sync. **Every path through this skill ends
   here.**

## Begin

Classify the request, state your classification in one line, then load the step:

- **"It broke / stopped / did something weird"** → start at
  `steps/step-01-diagnose.md`. If the diagnosis demands a code change, continue to
  step 02; either way finish with step 03.
- **"Change / add / tune something"** → skim the invariants above, then start at
  `steps/step-02-modify.md`; finish with step 03.
- **"How does it work?"** → answer from this file + the loop's README (read
  narrowly); no steps needed.

If the request is actually about a _story_ misbehaving (bad code, wrong spec) rather
than the harness, say so and hand off to the pipeline skill that owns it.
