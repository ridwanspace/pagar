---
description: Committed code must never cite private spec-pipeline IDs (story N.N, bare AC5, epic N, RCA-NN, .claude/ paths), a teammate cannot resolve them; the team's own established spec vocabulary is exempt and must never be stripped
paths:
  - "{{SOURCE_ROOT}}/**"
  - "{{CLIENT_SOURCE_DIR}}/**"
  - "{{MIGRATIONS_DIR}}/**"
  - "{{TEAM_DOCS_DIR}}/**"
  - "{{API_CONTRACT_FILE}}"
---

# No local spec references in committed code

**The rule:** anything committed, source, tests, comments, docstrings, migrations, team docs,
contract metadata, commit messages. Must be readable by a teammate **who has never seen your
spec tree**.

The pipeline in `.claude/` generates identifiers that exist only on your machine. They must not
cross into committed code.

## Why this matters more than it looks

`.claude/` is git-excluded. A comment saying `# story 1.1 / RCA-03#A2` points at a file **no
one else can open**.

That is worse than no citation at all. It *reads* as authoritative, so the next engineer
assumes a specification constrains the code, and hesitates to change it, **with no way to check
what the constraint was.** The reason has to travel with the code.

The worst shape is a literal `.claude/...` path, because it names a file that does not exist in
the clone.

## Banned in committed artifacts

Artifacts of **your** pipeline:

- `story 1.1`, `Story 1.2`: story numbers
- **Bare** `AC5`, `AC2`, `AC10`
- `epic 1`, `Epic 1.2`
- `RCA-03`, `RCA-03#A1`, `TRIAGE-04`: report ids and sub-issue anchors
- **Any `.claude/` path**, including references to the status file or the spec directories
- `Phase 8`, when it means a phase of *your* plan rather than a release the team names

## NOT banned: the team's own ID vocabulary

⚠ **The distinction is AUTHORSHIP, not format.** Ban what *your* pipeline invented. Keep what
*the team* already speaks.

| ID shape | Verdict |
|---|---|
| The team's established requirement and criterion ids, whatever their shape | **keep**. House vocabulary, never strip or rewrite |
| Your pipeline's story numbers, bare criterion numbers, report ids, `.claude/` paths | **ban**. Yours |

If an unfamiliar ID shape appears, **check authorship before flagging it**:

```bash
git log -S'<id>' --format='%an' -- {{SOURCE_ROOT}} | sort -u
```

If the author is not you, it stays.

This table exists because a first draft of this rule **flagged a teammate's convention as a
defect**. If a team ID is unresolvable, that is a question for the team, not a cleanup task.

## Allowed: cite these instead

- The team's own requirement ids, where the team already uses them
- The generated API contract. Quote the endpoint and the field
- Commit hashes, merge or pull request numbers, issue links
- Committed documentation pages
- File and symbol references
- Absolute dates rather than "this sprint"

## How to rewrite

Do not delete the note. The constraint is usually real. **Replace the ID with the reason it
stood for**, so the comment carries its own justification:

```
# WRONG  The verdict is SERVER-DERIVED (story 1.1 / RCA-03#A2): ...
# RIGHT  The verdict is SERVER-DERIVED: a client-supplied verdict would let a caller
#        mark an unreachable target as tested and bypass the save gate entirely.

# WRONG  How long a verification token stays valid (story 1.1).
# RIGHT  Bounded so a token cannot outlive the config it attests to.
```

## Where the IDs DO belong

Unrestricted inside the git-excluded personal workspace: the spec tree, the rules, the project
memory file, the skills. Story files **should** keep citing their own criterion numbers. That
is their job.

**The boundary is the git index, not the concept.** Committed documentation is committed, so it
follows the committed rule.

## Enforcement

- `/dev-story`, `/create-story`, `/rca`, `/triage`, and `/code-review` each carry a step for
  this. `/commit` runs the sweep.
- A staged-diff sweep, precision-tuned. **Do not loosen it**, and re-test any edit of the
  pattern against both known-clean and known-dirty files:
  ```bash
  git diff --cached -U0 | grep -nE '^\+.*([Ss]tory [0-9]+\.[0-9]|\bAC[0-9]{1,2}\b|[Ee]pic [0-9]|RCA-[0-9]|TRIAGE-[0-9]|\.claude/)'
  ```
  The word boundary after the bare criterion pattern is what excludes the team's hyphenated
  ids. That is deliberate. Adjust the pattern to your team's actual vocabulary, then re-test it.
- **A guard test is stronger than the sweep**, because it walks every tracked file and catches
  whole-file violations a staged diff cannot see. Write it, mutation-verify it, and run it
  before committing.
- **Pre-existing violations are not a cleanup task.** Fix them opportunistically on lines you
  are already editing. Do not open a sweep pull request into other engineers' files.
