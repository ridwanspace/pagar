# Step 02: Modify the loop safely

## Step goal

Land the requested change in the **smallest correct layer**, test-first, without
weakening any invariant from SKILL.md.

## Mandatory rules

- 📖 Read this whole step before acting.
- 🧱 Pick the layer from the recipe table — don't spread one change across three
  files when one suffices.
- 🧪 **Failing test first** when behavior changes: extend the loop's guard suite
  (`loop.test.ts` or equivalent — dry-run guards; they never invoke the agent CLI),
  watch it go RED, then implement.
- 📚 A flag/behavior change is not done until all four doc points are synced
  (SKILL.md invariant 7).
- 🛑 If the request would weaken an invariant (drop a gate, trust markers,
  `--no-verify`, shared sessions), STOP and surface the trade-off — the user decides
  explicitly.

## Recipe table — where each kind of change goes

| Request                                         | Layer & recipe                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Different default models                        | `config.sh` `LOOP_MODEL_*` defaults. Per-machine preference → tell the user about `config.local.sh` (gitignored) instead of editing tracked defaults                                                                                                                                                                                                                                                                                                                                   |
| New CLI flag                                    | `loop.sh`: header comment block (drives `--help`) + `case` arm + variable. Then README (both) + a test asserting the flag's dry-run effect                                                                                                                                                                                                                                                                                                                                             |
| Tune verification (tests/build gates, timeouts) | `config.sh`: verification toggles, phase timeouts, max turns, max retries — no code change needed; just document the chosen values                                                                                                                                                                                                                                                                                                                                                      |
| Change/strengthen a gate                        | `lib/common.sh` (`gate_*`). A gate must check an **artifact** (file, status, exit code), never model output. Keep the `DRY_RUN` early-return guard first                                                                                                                                                                                                                                                                                                                               |
| New phase in the cycle                          | 1) `prompts/<phase>.md` contract ({{REF}}/{{TITLE}} placeholders) 2) model var in `config.sh` (+ optional `--<phase>-model` flag) 3) sequence entry via the retry wrapper with a real gate 4) dry-run output + test 5) README pipeline diagrams                                                                                                                                                                                                                                          |
| Change what sessions are told                   | `prompts/unattended.md` (all phases) or `prompts/<phase>.md` (one). The `LOOP_STATUS:` contract lines must stay verbatim-parseable — the runner greps `^LOOP_STATUS:` in the log tail                                                                                                                                                                                                                                                                                                  |
| Failure policy / retries                        | `loop.sh` failure handling + retry wrapper; defaults in `config.sh` (`LOOP_ON_FAILURE`, `LOOP_MAX_RETRIES`)                                                                                                                                                                                                                                                                                                                                                                            |
| Story selection changes                         | `loop.sh`: next-ref resolution (auto mode) or range resolution (`--from/--to`). All spec queries via the spec-state CLI bridge — never parse the status ledger directly                                                                                                                                                                                                                                                                                                                |
| Permissions tightening                          | Agent CLI flags in `config.sh`/`config.local.sh`. Verify a real single-story run still gets through its git/test calls                                                                                                                                                                                                                                                                                                                                                                 |
| Commit behavior                                 | Scripted path: the scripted commit in `lib/common.sh` (keep the restage-on-hook-rewrite retry). Model path: `prompts/commit.md`. Mode default: `LOOP_COMMIT_MODE`                                                                                                                                                                                                                                                                                                                      |
| Self-improvement tuning                         | Knobs only: `LOOP_LEARN`, `LOOP_MODEL_REFLECT`, `LOOP_LEARN_MAX_LINES`, `LOOP_LEARN_COMPACT_AT` (`config.sh`). Contracts: `prompts/reflect.md` / `prompts/compact.md`. Machinery: failure-event ledger / reflect phase / compaction trigger / the injection block in `build_addendum` (`lib/common.sh`). Both extra sessions stay best-effort (never fail the run), only touch `LEARNINGS.md`; injection stays tail-bounded and compaction stays mechanically triggered                                          |

## Sequence

### 1. Confirm the layer

Name the file(s) you'll touch and why the smaller layers don't suffice (one line). If
the change is pure configuration, prefer telling the user the env var /
`config.local.sh` line over editing tracked code at all.

### 2. Write the failing test

For any behavioral change, extend the guard suite first:

- New flag/phase/gate visible in dry-run output → assert on the dry-run text (the
  existing tests show the pattern: fixture, run with `--dry-run`, assert on stdout).
- Error paths → assert exit code `1` and don't forget the happy path stays `0`.
- Run it — confirm RED for the right reason.

Pure-prompt changes (`prompts/*.md`) have no test surface — compensate in step 03
with a manual single-phase run.

### 3. Implement

Match the existing style: `set -euo pipefail` is active — guard arithmetic
(`((x++)) || true`) and remember command substitution swallows failures you don't
check. Keep dry-run branches printing the _exact_ shape of what real mode would
execute.

### 4. Sync the four doc points (for any interface change)

1. `loop.sh` header comment (→ `--help`)
2. `scripts/loop/README.md`
3. Project README's loop section
4. Project context file (`.claude/CLAUDE.md` or `AGENTS.md`) one-liners — only if
   the pipeline shape itself changed

Then load `steps/step-03-verify.md`.

## Success / failure

- ✅ Change in one layer, test written RED→GREEN, docs synced, invariants intact.
- ❌ Gate deleted "because the sessions are reliable now", prompt-only fix for a
  wiring bug, or a flag that exists in code but not in `--help`/README/tests.
