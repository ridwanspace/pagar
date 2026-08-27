# Triage an incoming issue

Invoke this for a bug report, a QA batch, a stakeholder complaint, or a screenshot. The job is to
decide what is real before anyone writes code.

The default failure here is treating a report as a specification. A report describes a symptom.
It is a hypothesis about a cause, and it is frequently wrong about the cause even when it is right
about the symptom.

Take one issue at a time. A batch of six is six separate decisions.

## 1. Check whether it is already solved

Do this first, before any investigation. It is the cheapest step and it closes issues outright.

- Is it fixed on the default branch and not yet deployed to the environment the reporter used?
- Is someone already working on it on an unmerged branch?
- Did a previous investigation already cover it?

If any of these is yes, stop. Say which one, and where the fix is.

## 2. Reality check

- Reproduce it, or establish that you cannot. "Cannot reproduce" is a real outcome and it is
  useful, as long as you say exactly what you tried.
- Check the reported behavior against the specification. The report may be describing the system
  working as designed.
- Separate the symptom from the claimed cause. A report can be right that the page is broken and
  wrong about which field causes it. Verify the diagnosis and the proposed remedy separately.

## 3. Route it

Certainty decides the route, not size. A one-line fix with an unproven cause is not a small job.

**Already solved.** Point at the fix. Say which environment needs it and stop.

**Not a bug.** The system works as specified. Say which rule specifies it. If the specification is
what people actually dislike, that is a product decision, not a defect.

**Straightforward.** Real, and you have *proven* the cause by reading the code and reproducing the
behavior. Fix it now. Write a test that fails before the fix and passes after it. Mutation-verify
that test. Record it.

Proven means you can point at the line. "It is probably the validator" is not proven.

**Needs a decision.** Real, cause proven, but the correct behavior is a question nobody has
answered. Do not pick an answer and build it. Write down the question, the options, and which you
would choose, then stop.

**Needs investigation.** Real, but you cannot prove the cause from what you have. Escalate to a
full investigation rather than guessing. A confident wrong fix costs more than an honest delay.

**Needs information.** You cannot tell what is being reported. Ask one specific question. "Which
account, and what was the exact time" beats "please provide more details".

## 4. Write it down

For each issue, record: what was reported, what you found, the route you chose, and why. Even for
"not a bug", especially for "not a bug", because the same report will arrive again in three
months.

## 5. Draft, do not send

Any reply to the reporter, QA, or a stakeholder is a draft for a human to review before it goes
out. Never send it yourself.
