# Step 01: Diagnose a failed / surprising run

## Step goal

Turn "the loop stopped" into a named failure class with evidence, using the logs and
cheap reproductions — before touching any code.

## Mandatory rules

- 📖 Read this whole step before acting.
- 🔎 Logs first, code second. The loop writes one log per phase session — the answer
  is almost always in the last one.
- 🧪 Reproduce with `--dry-run` or a single `--story <ref> --max 1` before proposing
  a fix. Never "fix" from the error message alone.
- 🛑 Don't rerun the full backlog to debug — that burns real model sessions.

## Sequence

### 1. Collect the evidence

```bash
ls -t scripts/loop/logs/ | head -5          # newest phase logs
tail -30 scripts/loop/logs/<newest>.log     # the session's ending + any LOOP_STATUS line
python .claude/scripts/specs/specs.py story-info <ref> --json   # what the spec state actually says
git log --oneline -5 && git status --short  # what actually got committed / left dirty
```

The loop's own terminal output (if the user still has it) names the failing phase and
the exact gate message — ask for it if missing.

### 2. Classify against the failure taxonomy

| Symptom (loop output)                                        | Class               | Where to look                                                                                                                                                          |
| ------------------------------------------------------------ | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `phase 'X' exited with code N` (N≠0, ≠124)                   | CLI failure         | Log **head**: auth expired, network, unknown flag (often after an agent CLI upgrade — verify flags against `<cli> --help`)                                              |
| `phase 'X' timed out after Ns` (code 124)                    | Timeout             | Was the story too big, or is the per-phase timeout too small? Check how far the log got                                                                                 |
| `phase reported: BLOCKED — <reason>`                         | Honest blocker      | The session obeyed the contract. Read the blocker in the dev story file + the status ledger. Usually NOT a loop bug — fix the blocker, rerun; the loop resumes          |
| `gate failed: dev story file ... does not exist`             | Gate (create)       | Did the session write to a different path? Compare the log's file writes vs what the spec state expects                                                                 |
| `gate failed: status says 'X' (expected 'done')`             | Gate (dev)          | Session ran out of turns/scope or forgot to set status. Log tail + the story's unchecked Tasks                                                                          |
| `gate failed: tests are red after dev-story`                 | Gate (test)         | `scripts/loop/logs/last_test.log` — the session claimed done with a red suite (the gate exists for exactly this)                                                         |
| `gate failed: working tree still dirty after commit phase`   | Gate (commit)       | Pre-commit hook output inside the phase log — usually a cross-file type error the hook cannot auto-fix                                                                   |
| `git commit failed for <ref>: ...`                           | Scripted commit     | Same: the hook rejected it. This is real signal — never suggest `--no-verify`                                                                                             |
| `next candidate <ref> already failed this run — stopping`    | Resolution stop     | By design: auto-mode refuses to retry a failed ref forever. Fix the story's blocker, rerun                                                                               |
| `range ... matched no runnable stories`                      | Range/plan shape    | List the plan: epic dirs must match their naming convention, stories their file convention; done stories are filtered                                                     |
| `'jq' is required` / agent CLI `not found`                   | Environment         | Prereqs in the loop's README                                                                                                                                             |
| Loop "hangs"                                                 | Interactive leak    | The phase session started something interactive despite the contract. Log tail shows the prompt; strengthen the relevant `prompts/*.md` line                              |
| `reflect changed nothing` / `reflect phase did not complete` | Reflect (non-fatal) | By design best-effort — the run continues. Recurring? Check the reflect log and whether `LEARNINGS.md` is growing stale or past its compaction threshold                   |

### 3. Reproduce cheaply

- **Wiring/flag issues** → `scripts/loop/loop.sh --dry-run [same flags]` (executes
  nothing; prints exact commands).
- **One story's phase** → rerun just it: `scripts/loop/loop.sh --story <ref> --max 1`.
  Skip-logic gives resume for free (existing dev story file skips create; `done`
  skips dev).
- **A single phase by hand** → copy the exact headless invocation from dry-run
  output and run it in a terminal; then run the gate manually (spec state, tests).
- **Harness logic without any model** → the fixture trick from the guard suite:
  build a throwaway spec tree, sync status into it, then point the loop at it with
  an env override and `--dry-run`.

### 4. Verdict

State, in one short paragraph: the failure class, the evidence line(s), and whether
the fix belongs to

- **the harness** (loop.sh / common.sh / config / prompts) → continue to
  `steps/step-02-modify.md`;
- **the story/spec** (blocker, red tests, bad plan) → hand off to the owning
  pipeline skill and stop here;
- **the environment** (auth, prereqs, CLI version) → give the user the exact command
  to fix it and stop here.

## Success / failure

- ✅ Named failure class + evidence + reproduction command that the user can run.
- ❌ "Something in the loop is flaky" with no log line attached — that's not a
  diagnosis; go back to 1.
