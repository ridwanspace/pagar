# 00 — The sensor half

**What this page answers:** what "the sensor half of a coding-agent harness"
means, why the sensors must live outside the model, and what pagar is and is not.

## A harness has three parts

An AI coding agent on its own is an actuator. It writes code, runs commands,
and asserts that things work. What it does not do is *observe*. When an agent
says "the tests pass", that is a claim, not a measurement. The whole trick of
engineering with agents is building the parts around the agent that turn claims
back into measurements.

Those parts split cleanly into three:

| Part | Job | Where it lives in pagar |
| --- | --- | --- |
| **Actuator** | Writes the code | Whatever agent you use. Claude Code, Codex, Cursor, a script, a human. |
| **Sensors** | Observe reality and report it | The gate runner, the baselines, the acceptance criteria in specs |
| **Memory** | Carry knowledge across sessions | The spec tree, the baselines, the recorded lessons |

pagar is deliberately only the sensor half, plus the method for keeping memory
in plain files. It never generates, refactors, or fixes code. That is not a
missing feature. A sensor that can also reach out and change the thing it is
measuring is not a sensor any more.

## Why sensors must be outside the model

A model under pressure to succeed will find the shortest path to looking
successful. Sometimes that path is correct code. Sometimes it is a weakened
assertion, a deleted test, a `baseline: false` flipped to quiet a red gate, or
a confident summary of a test run that never happened. You cannot fix this by
asking harder. Confidence does not get a vote.

So the checks that decide "done" run as plain processes in your repository,
driven by a config the model can read but the verdict of which it cannot argue
with. An exit code is not an opinion. This is the same reason CI exists, moved
to where it is cheapest: your machine, before the commit, in seconds.

## Baseline-aware: the difference between signal and noise

Any sensor that alarms constantly gets unplugged by Wednesday. Most real repos
already have failures — inherited debt, a flaky suite, a lint rule nobody
agreed to. A gate that goes red on day one for reasons you did not cause is a
gate that gets disabled by day three, and then you have nothing.

So pagar gates are baseline-aware. You snapshot the currently-failing set once,
commit it as a reviewed record of known debt, and from then on the gate fails
**only on failures that are new**. The alarm fires for the only kind of
breakage you can act on before it lands: the one you are about to introduce.

The baseline is plain sorted text, one failure key per line, committed on
purpose. It may shrink freely — that is debt paid back. It must never grow to
get past a red gate without a human deciding out loud, because a quietly
growing baseline is how a gate dies. The runner enforces the ceremony around
that policy; the policy itself is a team agreement.

## Specs are sensors too

A gate catches *the code is broken*. It cannot catch *the wrong thing was
built correctly* — clean code, green tests, wrong feature. The spec is the
sensor for that class of failure: acceptance criteria that turn intent into
statements an agent can be checked against, and a locked-decisions table so a
constraint (an authorization rule, a money limit) cannot be quietly traded
away to make a test pass.

That is why pagar is a gate runner *and* a method, not just a script. The
runner is the sensor for the code; the spec pipeline is the sensor for the
intent; the recorded lessons are the sensor calibration for the next task.

## What pagar is not

- Not an agent, not a wrapper around a model, not a competitor to your tool.
  The actuator half is yours, and it is replaceable. The sensors persist.
- Not a platform. Nothing here has an account, a server, a dashboard, or a
  vendor. Everything durable is a plain file in your repository.
- Not a dependency. The gate runner is Node 20+, ESM, zero runtime
  dependencies, and must stay that way. It starts with a plain `node` and no
  `npm install`, in any repo, including one with no `package.json`.

## Why "pagar"

*Pagar* is Indonesian for **fence**. A fence does not herd the cattle, does
not decide where they should go, and does not move. It stands at the boundary
and stops them at it. That is the whole design: pagar holds the line the agent
works against, and everything the agent does inside the line is its business.

---

Next: [01-why.md](01-why.md) — why a harness beats a better model.
