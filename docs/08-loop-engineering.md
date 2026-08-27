# Loop Engineering

**What this page answers:** what it takes to run an agent loop unattended — create
story, implement, review, commit, with no human watching — and the laws that keep
such a loop from quietly going wrong.

## The definition

**Loop engineering: designing the harness around a repeating agent cycle so that the
loop's correctness never depends on the model's good behavior.**

Every agentic workflow that repeats — story after story, fix after fix — is a loop.
Run it with a human watching each step and you have an expensive autopilot. Run it
unattended and you have compound engineering at machine speed, or a disaster,
depending entirely on the harness. The loop itself is boring on purpose: a shell
script, a phase prompt per stage, hard gates between stages, one log per session.

The term sits in the agentic-engineering discourse next to *context engineering* and
*compound engineering* — [Every's compound engineering guide](https://every.to/guides/compound-engineering)
contrasts the mindsets. The practices in this page are not theory: they were
distilled from running an unattended story loop (create-story → dev-story → review
→ commit, one fresh agent session per phase) on a production project, incident by
incident. The working manual ships as a pagar starter skill:
[`loop-engineering`](../starter/.claude/skills/loop-engineering/SKILL.md).

## The failure taxonomy

Every loop incident you will ever see is one of four classes. Diagnosing by class
first is the whole game — it tells you which log to read and which layer owns the
fix.

| Class | Looks like | Owning layer |
| --- | --- | --- |
| **Phase failure** | The agent session exited non-zero, timed out, or hung | The headless CLI: auth, network, flags after an upgrade, a timeout smaller than the story |
| **Gate failure** | `gate failed: ...` — the script-side check caught something | The work, not the loop: a session claimed done with a red suite, a file missing, a dirty tree |
| **Honest blocker** | The session reported `BLOCKED — <reason>` | The story itself. The loop did its job; fix the blocker and rerun |
| **Wiring mistake** | The loop runs, but wrong: wrong prompt, wrong flag, docs drifted from behavior | The harness: flags, prompts, `--help`, README, tests |

The gate failures are the success stories. A gate firing is the harness catching a
confident session being wrong — the sensor half doing its job inside the loop.

## The laws

These are load-bearing. Weakening any of them is a decision a human makes out loud,
never a side effect of a small change.

1. **Fresh session per phase.** State flows through files and git only — never
   through a continued conversation. A phase must be reproducible standalone from
   the story file. `--continue`/`--resume` in a loop is cached context you cannot
   audit.
2. **Gates are the truth; markers are advisory.** A session's `LOOP_STATUS:
   COMPLETE` is a claim. The gate checks the artifact: the file exists, the status
   ledger says `done`, the tests pass, the tree is clean. Never replace a gate with
   trust in the marker.
3. **Dry-run executes nothing, and every path is dry-runnable.** `--dry-run` prints
   the exact commands real mode would run — and every new execution path needs both
   a dry-run branch and a test proving it prints instead of runs. You read dry-run
   output as if you were about to pay for it, because next run you will be.
4. **A gate and a best-effort step are opposites, and wiring one as the other is a
   bug in both directions.** A gate blocks, because its subject is correctness: a
   red suite means the code is wrong. A best-effort step warns and continues,
   because its subject is quality of assistance: a missed lesson or a stale index
   degrades the future without making this story's code wrong. A blocking
   re-index would fail a story over an API hiccup; a non-blocking test gate ships
   red code.
5. **Bounded self-improvement.** Failures feed a reflect session that may touch
   exactly one file — `LEARNINGS.md` — and nothing else. The newest lines are
   injected into every future session, tail-bounded; past a threshold the file is
   compacted by a dedicated session, mechanically triggered, never by a reminder in
   prose. Reflection is best-effort: it must never fail the run it learns from.
6. **Every interface change lands in four places:** the CLI's `--help`, the loop's
   README, the project README, and the guard tests. A flag that exists in code but
   not in all four is a wiring mistake waiting for its taxonomy entry.
7. **Neutral naming.** The machinery is named for what it does — story loop, `LOOP_*`
   — never for a person, project, or meme. Renames are cheap until the logs
   accumulate.
8. **Test-first, even for the harness.** A behavioral change to the loop starts as a
   failing dry-run guard test, watched RED, then implemented GREEN. And a guard you
   never saw RED proves nothing: mutation-verify it — break the code on purpose,
   watch the guard fire, restore.

## The per-phase budget

Not all phases cost the same, and the loop should say so out loud. Model choice,
reasoning effort, and wall-clock timeout are **per phase**: the create and implement
phases earn the deeper model and the longer wall; the mechanical phases (review,
commit, reflect) run cheap and fast. One flat timeout is wrong in both directions —
it starves the phases that need room and wastes it on the ones that don't. And a
timed-out phase left real work on disk: the retry must resume from the story's task
list, not restart from zero and die at the same wall.

## Honest trade-offs

**What unattended loops are genuinely better at.** Backlogs of well-specified,
medium-sized stories. Overnight runs. Anything where the spec is solid and the
gates are sharp, and the cost of a human clicking "approve" exceeds the value of
their judgment at that step.

**What they cost you.** The harness itself — a loop script, phase prompts, gates,
guard tests, and the discipline to maintain all four in sync. On a project with
three stories left, the harness costs more than the clicking.

**The honest failure mode:** a loop that needs watching. If you find yourself
supervising every phase, the loop is not engineered, it is decorated — either the
gates are not catching what matters or the stories are not self-sufficient. Fix the
harness or stop pretending and run the phases attended; the worst outcome is paying
both costs.

---

Next: [09-graphify.md](09-graphify.md) — paying context for what you need, not for
the whole repo.
