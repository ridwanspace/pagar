# specs.py

The single interface to a project's spec artifacts.

A planning skill or a dev agent calls this instead of loading the whole PRD,
every epic, and every story file into its context. It reads and writes the spec
tree on disk, and it keeps the implementation status mirror in sync.

Stack neutral. It knows about markdown files in a directory tree and nothing
about your language, framework, database, or CI.

Python 3.9 or newer. Standard library only, no third-party imports, not even
PyYAML.

## Read this before you trust a verdict

`deps`, `feed-forward`, `suggest-next`, `lessons` and `stale-refs` are regular
expressions run over freeform markdown prose a human wrote. They are not a
dependency graph and they are not a parser.

**Every verdict they give is a hint to verify, never ground truth.** A phrasing
outside the recognized keywords defeats them without any error. When
`suggest-next` says a story is ready, read the story's own prose before you act
on it. When `deps` returns nothing, that can mean no dependency exists, or it
can mean the prose used words the scan does not know.

Where it matters, the text output prints a caveat line saying exactly that.

`sync-status` and `set-status` are the only commands that write. Every other
command is read only.

## Directory layout

The specs root is configurable with `--specs-dir`. The default is
`.claude/specs`, relative to `--root`.

```
.claude/specs/
  plan_artifacts/               source of record, written by planning
    prd.md                      requirement ids live here: F-*, FLOW n, Dn, Mn
    epics.md                    index of epics and coverage
    epic-NN-<slug>/
      epic.md                   epic goal, requirements covered, story list
      story-NN-<slug>.md        one story per file, the WHAT
  implementation_artifacts/     what was actually built
    status.yaml                 ref -> planned|in_progress|blocked|done
    epic-NN-<slug>/
      story-NN-<slug>.md        the HOW, holds "## Dev agent record"
```

Directory and file names carry the numbering. `epic-01-auth` is epic 1,
`story-02-login` inside it is story 1.2. A dev story mirrors its plan story path
one for one, so both share a single entry in `status.yaml`.

The first markdown `# H1` in a file is read as its title.

## Global flags

| Flag | Meaning |
| --- | --- |
| `--root PATH` | project root, default the current directory |
| `--specs-dir PATH` | specs root, relative to `--root` or absolute, default `.claude/specs` |
| `--json` | emit JSON instead of text, supported by most read commands |

## Subcommands

### `help`

Prints the full help, including the heuristics warning and which commands write.

```
$ python3 specs.py help
```

### `list`

Every epic and story with its status.

```
$ python3 specs.py list
~ epic-01-auth  -  Authentication  [in_progress]
    * story-01-signup  -  Sign up with email  [done]
    ~ story-02-login  -  Log in and hold a session  [in_progress]
    o story-03-reset  -  Reset a forgotten password  [planned]
o epic-02-billing  -  Billing  [planned]   [!] no epic.md
    (no stories yet)
```

Status marks: `o` planned, `~` in_progress, `x` blocked, `*` done.

### `show <epic> [story]`

Prints one file to stdout, unchanged. With no story argument it prints
`epic.md`.

```
$ python3 specs.py show epic-01-auth story-02-login
# Log in and hold a session

Covers F-AUTH. Depends on 1.1 for the user record.
...
```

### `story-info <ref>`

Resolves everything a story-creation step needs. A `ref` may be `1.2`, `1-2`,
`epic-01-auth/story-02-login`, or a bare story id.

```
$ python3 specs.py story-info 1.2
Story 1.2: Log in and hold a session  [in_progress]
  epic:        epic-01-auth - Authentication
  plan source: /proj/.claude/specs/plan_artifacts/epic-01-auth/story-02-login.md
  dev story:   /proj/.claude/specs/implementation_artifacts/epic-01-auth/story-02-login.md  (EXISTS)
  previous:    1.1 [done] dev=/proj/.claude/specs/implementation_artifacts/epic-01-auth/story-01-signup.md
```

### `dev-list`

Every dev story that exists on disk, with its status.

```
$ python3 specs.py dev-list
  1.1  [done]  /proj/.claude/specs/implementation_artifacts/epic-01-auth/story-01-signup.md
  1.2  [in_progress]  /proj/.claude/specs/implementation_artifacts/epic-01-auth/story-02-login.md

2/3 plan stories have a dev story.
```

### `next-dev`

The next story to implement: it has a dev story file and it is not done.
`in_progress` wins, then `blocked`, then plan order.

```
$ python3 specs.py next-dev
Next dev story: 1.2 - Log in and hold a session  [in_progress]
  dev story: /proj/.claude/specs/implementation_artifacts/epic-01-auth/story-02-login.md
  plan:      /proj/.claude/specs/plan_artifacts/epic-01-auth/story-02-login.md
```

There is a sibling, `next-story`, which returns the next `planned` story to
expand into a dev story.

### `set-status <ref> <status>`

Sets one epic or story status. Valid values: `planned`, `in_progress`,
`blocked`, `done`. Everything else in `status.yaml` is left alone. Moving the
first story of an epic off `planned` lifts the epic to `in_progress`.

```
$ python3 specs.py set-status 1.2 done
epic-01-auth/story-02-login -> done
```

### `sync-status`

Rebuilds the structure of `status.yaml` from the plan tree while preserving the
values.

- A new epic or story arrives as `planned`.
- An epic or story whose file is gone is dropped and reported.
- Everything that still exists keeps the status it had. A hand edit is never
  clobbered.

**The exception that matters.** An epic entry carrying a `source:` key was
written by something outside the plan tree, for example a research or triage
step. It has no `plan_artifacts/` parent by design, so the tree scan cannot see
it. Such an epic is carried through verbatim and is never reported as removed.

An externally sourced epic can also be **partially** on disk: research records
its early stories in `implementation_artifacts/` only, then a later planning run
writes plan stories for the same epic. The epic then becomes visible to the
scan. Carry-through is therefore not conditioned on the epic being absent. The
tree is merged **into** the preserved entry, never substituted for it, so
implementation-only stories survive.

```
$ python3 specs.py sync-status
status.yaml synced -> /proj/.claude/specs/implementation_artifacts/status.yaml
  3 epic(s), 9 story(ies).
  ~ carried through (externally sourced, no plan parent): epic-00-research-fixes
  + added (status=planned): epic-02-billing/story-01-plans
  - removed (no longer on disk): epic-03-old/story-04-dropped
```

### `deps <ref>`  (heuristic)

Later stories that name this one in a dependency clause, or that share its
feature codes or its backticked snake_case names.

Forward only. A story never feeds back into one that comes before it.

```
$ python3 specs.py deps 1.1
Downstream dependents of 1.1 - Sign up with email
  note: this is a regex scan over freeform markdown, not a dependency graph. Verify before you act on it.

  1.2  [in_progress]  Log in and hold a session
      why: explicit-depends-on; shared-code(F-AUTH); shared-surface(session_token)
      plan: /proj/.claude/specs/plan_artifacts/epic-01-auth/story-02-login.md   dev: EXISTS

1 downstream dependent(s).
```

### `feed-forward <ref>`  (heuristic)

The same scan, framed as writeback targets. Use it after finishing a story to
find which later story files should learn the ground truth it just established.
It tells you which files to open, not what to write in them.

```
$ python3 specs.py feed-forward 1.1
Feed-forward from 1.1 - Sign up with email
  note: this is a regex scan over freeform markdown, not a dependency graph. Verify before you act on it.
  surface codes:    F-AUTH
  surface names:    session_token, user_record
  dependent stories to update (1):
    -> 1.2 [in_progress]  Log in and hold a session  (explicit-depends-on)
        write the inherited ground truth into: /proj/.claude/specs/plan_artifacts/epic-01-auth/story-02-login.md
```

### `suggest-next [ref]`  (heuristic)

The next story to work on, dependency aware rather than strictly numeric. A
story is "ready" when every story it explicitly names as a prerequisite is
`done`. Given a `ref`, it prefers a ready story that depends on that ref, then a
ready story in the same epic, then any ready story.

```
$ python3 specs.py suggest-next 1.1
Suggested next story: 1.2 - Log in and hold a session [planned]
  note: this is a regex scan over freeform markdown, not a dependency graph. Verify before you act on it.
  ready: every explicit prerequisite it names is done.
  Check the story prose for an ordering rule this scan cannot see.
  plan: /proj/.claude/specs/plan_artifacts/epic-01-auth/story-02-login.md
  dev story: (not yet created)
```

### `lessons [ref]`  (heuristic)

Mines the `## Dev agent record` section of every DONE story for lessons worth
carrying forward, and flags the ones that cost someone something.

Default scope is earlier stories in the same epic. `--all-epics` widens it to
everything shipped before that story. With no `ref`, it takes the most recent
done stories.

Flags: `--hazards` shows only flagged traps, `--all-epics` widens the scope,
`--limit=N` caps the output.

**This command fails loud on purpose.** It always prints its denominator: how
many stories it scanned, how many had a record at all, and how many lessons came
out. A thin result must read as "those stories logged little", never as "there
is nothing to learn". Do not remove that line.

The denominator cannot see what the matcher never matched. It guards against
scanning too few files, not against extracting too few items per file.

```
$ python3 specs.py lessons 2.3 --hazards --limit=3
Lessons from epic 2, stories before 3
  scanned 2 done stories, 2 had a record, 7 lessons, 3 flagged as hazards

[!] [2.2] The green suite stayed green while the write silently dropped every row with a null tenant.

[!] [2.1] This generalizes to any scanner over freeform prose: a first-match loop reads as a collecting one.

  ... 4 more. Raise --limit=N, or use --hazards to see only the traps.
```

Ranking is diverse by construction. It round-robins across stories first, taking
one item per story per pass, then sorts hazards to the top of that set.
Otherwise one verbose story fills every slot and buries all the others.

### `reqs`

Requirement ids declared in `prd.md`. Features `F-*` are the primary unit.
Flows, decisions and modules are surfaced as extra cross-reference dimensions.

A feature id may contain digits after its first letter, for example `F-A11Y` or
`F-OAUTH2`. Every scanner in the tool uses one shared pattern so they cannot
drift apart.

```
$ python3 specs.py reqs
Features (F-*, the primary requirement unit): 4
  F-A11Y, F-AUTH, F-BILLING, F-OAUTH2

Flows: 2
  FLOW 1, FLOW 2

Decisions: 3
  D1, D2, D3

Modules: 0
  (none)
```

### `coverage`

Maps each PRD feature to the epics that name it, and reports what nothing
covers.

This is a tautology check. It answers "is every declared feature mapped to an
epic", never "did the PRD ask for the right things". A clean number means
nothing declared is unmapped, no more.

```
$ python3 specs.py coverage
Requirement coverage (F-* -> epic):

  F-A11Y             -- UNCOVERED --
  F-AUTH             epic-01-auth
  F-BILLING          epic-02-billing

2/3 features covered.
UNCOVERED (1): F-A11Y

  note: this checks that every declared feature maps to an epic. It cannot tell you whether the PRD declared the right features.
```

### `stale-refs`  (heuristic)

Reports code names that forward-looking spec prose promises but the code does
not define.

The drift it catches: a story is planned against a guessed helper name, the
implementation ships a different one, and the plan keeps sending the next dev at
a symbol that does not exist. Nothing else notices, because the specs are
markdown.

Pass `--code-dir` once per source directory. It defaults to `--root`, which is
usually too broad to be useful.

It only reads lines under forward-looking headings. A dev record or an evidence
section quotes the past on purpose, so flagging those would train the reader to
ignore the output.

Identifier harvesting deliberately over-collects. A missed drift costs nothing.
A false positive on a perfectly good name teaches the reader to ignore
everything the command says.

```
$ python3 specs.py stale-refs --code-dir src --code-dir lib
scanned 12 plan file(s), 7 named code identifiers, 4180 identifiers defined in the code, 1 stale

  [!] /proj/.claude/specs/plan_artifacts/epic-01-auth/epic.md:34  `coerce_param` is not defined in the code
      Story 1 needs `coerce_param(value, kind)` from the core.

Each one is a name a future dev story will be sent to look for. Fix the spec line to the shipped name, or confirm the symbol is still unbuilt.
```

### `next-id [epic]` and `slug "<title>"`

Small helpers for naming a new file.

```
$ python3 specs.py next-id
epic-03-<slug>  (epic #3)

$ python3 specs.py next-id epic-01-auth
story-04-<slug>  (story #4 in epic-01-auth)

$ python3 specs.py slug "Add OAuth2 / SSO login!"
add-oauth2-sso-login
```

## The YAML subset

The tool has no third-party dependencies, so it ships its own small reader and
writer for `status.yaml`. That file is written by this tool and read by this
tool, and its shape is small and fixed.

**Accepted.** Block mappings only, nested by two-space indentation. Every value
is one of:

- a nested block mapping, meaning the key line has nothing after its colon
- a plain scalar on the same line as the key
- a quoted scalar, single or double quotes, on the same line as the key
- a block scalar written as `>` or `|`, folded onto one value

Scalars decode like this:

| Written | Read as |
| --- | --- |
| `true` / `false`, any case | Python `bool` |
| `null`, `~`, or nothing | `None` |
| a bare integer | `int` |
| `"true"`, `"42"` | `str`, the quotes are honored |
| anything else | `str` |

Comment lines and blank lines are skipped. A `#` inside a quoted scalar is kept.

**Rejected with a clear error, never silently mangled.**

- block sequences (`- item`) and flow collections (`[a, b]`, `{a: 1}`)
- anchors, aliases, tags, merge keys (`&x`, `*x`, `!!str`, `<<:`)
- more than one document in a file (`---` separators)
- tab indentation
- indentation that does not line up with a known parent level

If `status.yaml` uses something outside this subset, every command that reads it
exits with a message naming the line. It does not guess.

The writer emits the same subset. It quotes any string that could read back as
something else, which covers a number, a bool, a null, and the empty string. A
string containing a newline is written as a block scalar.

Example of the accepted shape:

```yaml
generated_from: plan_artifacts (epic-*/ + story-*.md)
epics:
  epic-01-auth:
    title: Authentication
    status: in_progress
    stories:
      story-01-signup:
        title: Sign up with email
        status: done
      story-02-login:
        title: Log in and hold a session
        status: in_progress
  epic-00-research-fixes:
    status: done
    source: research/RESEARCH-02-headers-audit.md
    stories:
      story-01-auth-overlay:
        status: done
        completed: "2026-01-11"
```

## Files

| File | What it holds |
| --- | --- |
| `specs.py` | the CLI entry point, argparse wiring, and every command body |
| `_core.py` | paths, tree discovery, status handling, and all the scanners |
| `_yaml.py` | the YAML subset reader and writer |
| `test_specs.py` | the guard tests, one group per numbered correctness rule |

## Tests

```
$ cd starter/.claude/scripts/specs
$ python3 -m pytest test_specs.py -v
```

Every test name maps to one numbered correctness rule. Each of those rules is a
bug that was found and fixed once already. The tests exist so it cannot come
back. Each one has been mutation verified: break the fix in `_core.py` or
`specs.py`, and the matching test goes red.

If you change a scanner, break it on purpose first and watch the test fail. A
guard that has never been seen to go red is not evidence of anything.
