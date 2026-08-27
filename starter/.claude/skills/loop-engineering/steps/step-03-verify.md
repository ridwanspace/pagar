# Step 03: Verify the loop still holds

## Step goal

Prove — not assume — that the loop works after your change, using only free checks
(syntax, dry-runs, the guard suite); optionally one supervised real story when the
change touched live execution.

## Mandatory rules

- 📖 Read this whole step before acting.
- 🧪 A guard you never saw RED proves nothing — mutation-verify anything you added
  to the guard suite.
- 💸 Real (non-dry) verification runs cost model sessions — only with the user's
  go-ahead, and always `--max 1`.

## Sequence

### 1. Static checks

```bash
bash -n scripts/loop/loop.sh scripts/loop/config.sh scripts/loop/lib/common.sh
scripts/loop/loop.sh --help >/dev/null && echo help-ok
# plus the project's own lint/format checks over the files you touched
```

### 2. Dry-run matrix (no plan in the repo? use a fixture)

If the spec tree has no epics (fresh template), build a throwaway plan exactly like
the guard suite does, then point the loop at it:

```bash
scripts/loop/loop.sh --dry-run                          # auto-resolution
scripts/loop/loop.sh --dry-run --story <ref>            # explicit story
scripts/loop/loop.sh --dry-run --from <a> --to <b>      # range incl. a done story → must be skipped
scripts/loop/loop.sh --dry-run --<your-new-flag> ...    # whatever you changed
```

Read the printed commands _as if you were about to pay for them_: right slash
command, right model, right flags, phases in order, and nothing executed.

### 3. Guard suite + mutation check

Run the full project test suite — the loop's guard tests ride along with everything
else.

If you added/changed an assertion: break the code on purpose (flip the default
model, drop the phase, invert the exit code), watch the test go RED, restore, watch
GREEN. Confirm the mutation was actually in the executed path — a green mutation is
a false proof.

### 4. Real-run smoke test (optional, user-approved)

Only when the change affects live execution (runner, gates, prompts, permissions)
and the user agrees:

```bash
scripts/loop/loop.sh --max 1        # one story, supervised, on a branch
```

Watch for: the phase log appearing under `scripts/loop/logs/`, each gate line
(`✓ gate: ...`), the commit landing with hooks run, and the summary counting 1
completed.

### 5. Close out

- Confirm the four doc points match reality (step 02 §4) — stale `--help` text is a
  bug.
- Report to the user: what changed, what was verified at which tier (static /
  dry-run / suite / real), and anything deliberately NOT verified (e.g. "prompt
  change unexercised until the next real run — watch phase X's log").
- If this session did something _by hand_ that a check could do next time, say so —
  that's `/code-review` step-06 material even for harness work.

## Success / failure

- ✅ All tiers you ran are green, new guards seen RED under mutation, docs truthful.
- ❌ "Tests pass" with an unverified new guard, a dry-run matrix skipped because
  "it's a small change", or a real run launched without the user opting in.
