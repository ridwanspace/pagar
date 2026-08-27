# Scenario 07: the overnight run

**What this page answers:** the backlog is a row of sharp, self-sufficient stories and you
would rather not click through them by hand. What does handing them to the unattended story
loop actually look like — the evening, the night, and the morning after?

The short version: **preflight with a dry-run, one supervised story, then sleep.** The loop
is not a different pipeline. It runs the exact skills you would run — `/create-story` →
`/dev-story` → `/code-review` → commit — one fresh headless session per phase, one
conventional commit per story, with gates between phases that check artifacts instead of
believing markers. Mechanics and configuration:
[`../starter/scripts/loop/README.md`](../starter/scripts/loop/README.md). Laws and failure
taxonomy: [`../docs/08-loop-engineering.md`](../docs/08-loop-engineering.md).

---

## The precondition, checked honestly

The loop is a multiplier on pipeline quality, and multiplying a vague number gives you a
bigger vague number. Before launching, two questions, and the honest answers are checkable:

**Are the stories sharp?** Every story in range is a dev story a developer could build from
alone — acceptance criteria someone could disagree about, guardrails restating the PRD's
locked decisions, a task list that earns its checkboxes. The test is
[`01-new-feature.md`](01-new-feature.md) stage 3: if story 4.1 had to be run by a human with
judgment, 4.2 does too. The loop does not make stories better. It makes finished ones
cheaper.

**Do the gates bite?** `node gates/run-gates.mjs` is green on a clean tree, red within
seconds of a broken one, and the baseline is small enough that a new failure is signal, not
noise. The loop's own verification gates auto-detect pagar gates, or your test command via
`LOOP_VERIFY_TEST_CMD`. A gate that skips is not a pass — if half your gates SKIP, the night
runs half-blind.

If either answer is no, the honest move is to stop here. The loop over vague stories is a
printer of confident wrong code, and you get to read all of it at 8am.

---

## The evening: 17:40

### 1. The dry-run, read as if you were about to pay for it

```bash
scripts/loop/loop.sh --dry-run --from 4.2
```

Executes nothing, mutates nothing, and prints every command real mode would run: the story
resolution, each phase's slash command, model, and reasoning effort, the addendum files, the
commit message shape. Read it line by line — wrong story, wrong model, wrong flags, phases
out of order — because tomorrow morning's first surprise should not be a surprise you
already printed and skimmed.

If the resolution line says something odd ("matched no runnable stories"), fix the plan
shape now. The loop never invents work; it only pulls from the spec tree.

### 2. One supervised story first, not the backlog

```bash
scripts/loop/loop.sh --story 4.2
```

You watch this one. The phases run attended; you see the gates fire (`✓ gate: status ==
done`, `✓ gate: npm test green`, or pagar gates), the scripted commit land, the reflect
phase if something failed. This is the loop's audition. If a gate you expected never fires,
or a prompt contract reads wrong, you want to learn it at 17:50 with your hands on the
keyboard, not from a 3am log.

### 3. Launch, on a branch you trust

```bash
scripts/loop/loop.sh --from 4.3
```

Then close the laptop. Two safety notes that are invariants, not defaults: the loop never
pushes and never switches branches, and its default agent flags skip the permission system
entirely — an unattended session cannot answer prompts. That trade is the same one any
autonomous runner makes; run it on a branch where a bad commit costs a `git reset`, not an
incident.

---

## What happens while you sleep

Per story, in order: a fresh session writes the dev story (gate: the file exists). A fresh
session implements it (gates: status is `done`, typecheck and tests re-run by the script
itself — never the session's word). A fresh session runs the review steps, recording visual
sign-off as `PENDING HUMAN REVIEW` because it cannot obtain yours. If anything failed, a
cheap reflect session distills it into `LEARNINGS.md` — before commit, so the lesson ships
with the story — and the last 80 lines of that file ride into every future session. Then
one conventional commit, and the next story.

State flows through story files, the status ledger, and git. Not through conversation
memory. That is why a phase is resumable, why a timeout retries from the story's task list
instead of from zero, and why you can audit everything in the morning.

---

## The morning: 08:10, in this order

1. **The run summary.** Completed vs failed, then `git log --oneline` — one conventional
   commit per story, or a story that stopped where a gate caught it.
2. **The gates' logs.** `scripts/loop/logs/last_test.log` (and `last_typecheck.log`) for
   the final state of each verification. Green here means the same thing it means at your
   desk.
3. **`git diff main` of the night's work.** You are reading diffs against stated intent —
   each commit message says which story it shipped. This is the review the method promised:
   not "read everything the agent wrote, hope", but "read four focused diffs".
4. **`LEARNINGS.md`.** If the night produced an entry, read it — it is a real trap, paid
   for once, and every future session already inherited it.
5. **Search the story files for `PENDING HUMAN REVIEW`.** The loop records what it cannot
   sign off instead of claiming it. Those lines are your morning's first tasks.

### If a story failed overnight

Classify before you feel anything — the taxonomy is in
[`../docs/08-loop-engineering.md`](../docs/08-loop-engineering.md):

- **A gate failure is the harness succeeding.** The session claimed done, the gate said
  otherwise, the story stopped with the failure named in the log. Read
  `scripts/loop/logs/`, fix the cause, rerun from that story — the skip-logic resumes
  rather than redoes.
- **A BLOCKED marker is honest work.** The session hit something its contract says a human
  must decide. The blocker is written into the story file. That is the loop asking you a
  question, not failing you.
- **A wiring mistake is yours to fix once.** A flag that exists in code but not in
  `--help`, a prompt contract drifting from the skill. That is
  [`loop-engineering`](../starter/.claude/skills/loop-engineering/SKILL.md) territory:
  failing test first, dry-run proven, four doc points synced.

---

## When not to run it

- **The stories are not sharp yet.** Multiply quality, not hope.
- **The gates skip more than they run** on this machine. A half-blind night is worse than
  an attended morning.
- **The change is one story, once.** Supervised `--story <ref>` or plain by-hand skill
  runs cost less than configuring anything.
- **You cannot afford a branch reset.** The loop commits locally with permission checks
  off; make sure the blast radius is a branch.

---

## Honest accounting

The loop's cost is real: the harness exists (it ships with the starter), the preflight
takes ten minutes, and the morning review is not optional — you read the diffs, the gates,
and the pending sign-offs before merging anything. What it returns is the evening: four
stories implemented, tested, reviewed, and committed at machine speed, each one gate-green
before it landed, every lesson banked. The first overnight run usually pays for the whole
harness.

The failure mode is not "the loop broke". It is running it a week after the stories stopped
being sharp, because the machinery was still there. The precondition check is not a formality;
it is the whole game.

---

## See also

- [`../starter/scripts/loop/README.md`](../starter/scripts/loop/README.md) — the runner's
  manual: configuration, gates, safety notes.
- [`../docs/08-loop-engineering.md`](../docs/08-loop-engineering.md) — the laws, the
  failure taxonomy, and what each one costs.
- [`01-new-feature.md`](01-new-feature.md) — the state this scenario starts from: sharp
  stories, believable gates.
- [`06-a-real-week.md`](06-a-real-week.md) — the week that did *not* run the loop, and why
  that was the right call.
