---
description: The spec helper script's internals and gotchas. Heuristic-scan failure modes, the three requirements entry points, and the two compounding loops every skill depends on
paths:
  - ".claude/scripts/specs/specs.py"
  - ".claude/skills/**"
---

# Spec pipeline helper rules (`.claude/scripts/specs/specs.py`)

One helper for the whole repository, over one status file. **Run it. Never load full spec
context into a session.** `python .claude/scripts/specs/specs.py help` lists the subcommands.

The skills depend on it for: listing the tree, showing one file, extracting requirement ids
from the PRD, checking coverage, allocating the next id, resolving a story reference,
regenerating the status mirror, flipping a status, finding dependents, mining lessons, finding
stale identifiers, and suggesting the dependency-aware next story.

## Heuristics over freeform markdown: the whole family's failure mode

⚠ **The dependency, feed-forward, lessons, and suggest-next subcommands are HEURISTICS over
freeform markdown.** They are regex scans of story prose, not a real dependency graph. **Treat
every verdict as a hint to verify, never as ground truth.**

Concretely, the traps that have actually bitten:

- **⚠ Multi-reference dependency lines need a COLLECTING scan, not a first-match scan.** A
  naive keyword-then-reference scan yields only the FIRST reference after the keyword, so a
  line like `depends on stories 2.1 (registry), 2.2 (surface), 2.3 (defense)` silently drops
  everything after the first. The correct shape: find each keyword match, then scan the **rest
  of that clause** for every reference with a separate global pattern, filtering out
  look-alikes such as dates and version numbers.
- **The clause boundary must be a SENTENCE boundary**, not a semicolon or newline alone, and
  never to the end of the line. A dependency keyword and a later "Independent of X, Y, Z"
  mention can share one physical line, and a scan to the newline collects references the line's
  own tail explicitly excludes. A reference's own decimal point must never trip the boundary.
- **A negation check that rejects references inside a trailing "independent of" clause must
  allow the decimal point in its tail class**, or it stops at the first reference's own decimal
  and the whole check becomes dead code.
- **History lesson: "this sibling function is fine" about a heuristic-over-freeform-markdown
  parser is only as good as the test case that provoked it.** When a new corpus shape breaks
  one, re-verify the sibling. Mutation-verify any change against a real corpus case **in both
  directions**.
- When a next-story suggestion reports a story as ready, **sanity-check it against the story's
  own prose** whenever the epic states an explicit ordering. A phrasing outside the recognized
  keywords defeats the regex, and the tool reports ready for something that is gated.

## Status reconciliation and externally-sourced epics

- The status-sync subcommand **rebuilds structure from a scan of the planning tree but preserves
  status values**. Epics carrying a source marker, written by `/rca` or `/triage`, have no
  planning parent, so they must be **carried through verbatim and merged, never substituted**,
  or implementation-only work is silently reported as removed. Guard this with a test.
- **Generalizable lesson behind that guard: a guard written against the shape that bit you
  tests one POINT, not the invariant.** "Absent" and "partially present" are different states
  that fail differently. When you fix a reconcile or merge bug, **cover the partial state too.**
- Subcommands that scan only the planning tree return empty for externally-sourced references.
  **Edit those statuses by hand**, and know that this is the reason.

## Requirements entry points: what may become an epic

Exactly three upstreams. Nothing else has been verified.

1. **`/create-prd` → `/edit-prd` → the PRD.** Greenfield, or from an existing brief that
   `/create-prd` accepts as its primary source. The requirement-extraction and coverage
   subcommands read only this.
2. **`/rca` in QA mode**: a bug report verified against the code, the live system, and the PRD.
3. **`/rca` in external-document mode**: a requirements or handoff document, verified the same
   way.

⚠ **An externally-authored document is a set of hypotheses, not requirements. Never paste one
straight into `/epics`.** Its "this already exists" table is a claim by someone without commit
access, and its asks may already ship. That is the entire reason `/rca`, and `/triage`'s
already-solved check, sit in front of `/epics`.

- Findings from `/rca` and `/triage` are not PRD features, so **coverage cannot see them, by
  design**. Traceability comes from the source ids recorded in the epic. If a finding deserves
  coverage visibility, write it into the PRD instead.
- A finding that is blocked on a human decision blocks **its own story, not the batch.**

## Coverage is a tautology check

Coverage answers "is every declared feature mapped to an epic?" It **never** answers "did the
PRD ask for the right things?"

A clean number means nothing declared is unmapped. No more.

Feature catalogs written by asking "what can the user do?" systematically skip **the
application's own surface**, its shared interface vocabulary, and accessibility as a verified
state rather than a stated standard. A run can report 100% coverage the whole way to an
incoherent product.

Sequencing is where the real value is: foundation early, sweep late.

⚠ If your feature id pattern allows digits, **every scanner must use the same pattern and all
scanners must agree.** Fix the tool, never rename a feature to dodge a scanner.

## The two compounding loops

Both are cheap to break, and neither is covered by an application test. **Treat them as
load-bearing.**

### 1. `lessons`: the exhaust-to-fuel loop

Dev stories are, by default, **never read again**, so the same class of bug gets re-learned at
full price. The lessons subcommand mines every done story's dev-agent record and ranks traps
first. `/create-story` runs it **every time**.

- ⚠ **It inherits the heuristic failure mode: silent under-collection reading as "nothing to
  learn".** It is built to fail LOUD, always printing its denominator. How many stories it
  scanned, how many had a record, how many lessons it found. **Never optimize that line away.**
  A thin result means those stories logged little, not that the corpus is empty.
- 🚨 **A denominator cannot see what the matcher never matched.** It guards against scanning
  too few *files*, not too few *items per file*. A matcher can silently skip every entry
  written in one syntax while the denominator stays truthful. **Mutation-verify the MATCHER
  against a planted case in the syntax the corpus actually uses**, not only the tidy form from
  the docstring.
- **A hazard pattern that matches everything is worth nothing.** Every clause must name a
  **cost**: "the green suite missed this", "this bit us", or a generalization. Never merely
  a topic. Match the shape of the failure, not a keyword.
- **Ranking without diversity means one story eats the whole budget.** Round-robin across
  stories first, then sort hazards within the diverse set. Any future ranker over per-story
  items needs the same guard.

### 2. `/code-review`'s pipeline-improvement step: the self-improvement loop

One thing done **by hand** becomes a script or a guard. **At most one per story.** "None this
run" is explicitly valid, because manufacturing busywork is the anti-goal.

- **Prefer rule to guard.** A prose rule decays as the code moves. A failing test cannot.
- **A guard must be import-shaped or call-shaped, and mutation-verified.** A bare substring
  match hits the prose in its own docstring, so strip comments before scanning source. **A
  guard that has never been seen to go RED is not evidence of anything.** Break the code on
  purpose, watch it fail, restore.
- **A script no step invokes is dead on arrival.** If you add a subcommand, update the step
  file that should call it, in the same change.
