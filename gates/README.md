# gates

pagar's gate runner: a baseline-aware, config-driven local CI runner. It runs the checks CI would run, locally, in seconds, and fails only on breakage you are about to introduce.

Written in Node.js, ESM, **zero runtime dependencies**. It starts with a plain `node` and no `npm install`, in any repo, including one with no `package.json`.

The method behind it is written up in [`../docs/05-local-ci-enforcement.md`](../docs/05-local-ci-enforcement.md). Read that first if you want the reasoning. This page is the manual.

## What problem it solves

Most repos have some failures already. A gate that goes red on day one for reasons you did not cause gets disabled by day three. So `gates` snapshots the currently-failing set into a **baseline**, then fails only on failures that are **not in it**.

That single idea is what makes a gate survive contact with a real codebase.

## Install

Three ways, same tool. Pick by how much you want in your repo:

**1. The installer** — copies `gates/` in and prints the next steps:

```bash
curl -fsSL https://raw.githubusercontent.com/ridwanspace/pagar/main/install.sh | bash -s -- /path/to/your/repo
```

**2. The npm package** (`pagar-gates`, binary `pagar`, zero dependencies) — nothing
copied at all; you author only a `gates.config.json`:

```bash
npx pagar-gates --update-baseline
```

**3. By hand** — copy the directory, own it forever:

```bash
cp -r path/to/pagar/gates your-repo/gates
cd your-repo
cp gates/gates.config.example.json gates.config.json
$EDITOR gates.config.json          # delete the stacks you do not have
```

Requires Node 20 or newer. Check with `node --version`.

## Quick start

```bash
# 1. See the options.
node gates/run-gates.mjs --help

# 2. Record the debt you already have. Commit first, the tree must be clean.
node gates/run-gates.mjs --update-baseline

# 3. Commit the baseline. It is a reviewed record of known debt.
git add .gates/baselines && git commit -m "chore: record gate baselines"

# 4. From now on, run this before every commit.
node gates/run-gates.mjs
```

Add a shortcut so nobody has to remember the path:

```json
{ "scripts": { "gates": "node gates/run-gates.mjs" } }
```

## Example output

A run where the code under test has one pre-existing failure and one you just introduced:

```
  Running gates
  config /home/dev/app/gates.config.json

  FAIL  backend/pytest unit tests 0.5s
        1 NEW failure(s), not in the baseline:
          + backend/tests/test_math.py::test_new_regression
        1 known failure(s) in the baseline, ignored

  1 FAIL

  1 new failure(s) across 1 gate(s). Fix them before committing.
  Do not add them to the baseline to get past this.
```

Exit code 1. The new failure is named. The old one is counted and left alone, so the thing you broke does not hide inside forty lines of old debt.

After you fix both:

```
  PASS  backend/pytest unit tests 0.5s
        2 baseline failure(s) now pass. Re-snapshot with --update-baseline.

  1 PASS

  1 gate(s) have fewer failures than the baseline. Run --update-baseline.
```

A machine that is missing a toolchain skips instead of failing:

```
  SKIP  billing-java/surefire mvn test
        skipped: "mvn" is not installed or not on PATH

  1 PASS  1 SKIP

  1 gate(s) skipped. A skip is not a pass.
```

## Baseline policy

Say this out loud to the team, once, and hold the line:

- The baseline may **shrink** freely. A smaller baseline means you fixed pre-existing debt. Re-snapshot and commit it.
- The baseline must **never grow** to get past a red gate without an explicit human decision. A grown baseline is a failure somebody decided to keep. That can be legitimate, and it must be a choice a person made and wrote down, not a side effect of running a command.

The runner helps you hold that line. `--update-baseline` prints how the baseline changed, and says so loudly when it grew:

```
  SAVED backend/pytest unit tests 0.5s
        baseline GREW by 1, now 2 known failure(s). Only keep this if a human decided to.

  A baseline grew. Growing a baseline hides a real failure.
  Keep it only if a human decided this failure is acceptable debt. Say why in the commit message.
```

Baselines are sorted plain text, one key per line, one file per gate. That is deliberate. A growing baseline then shows up as added lines in a diff, where a reviewer can see it.

`--update-baseline` refuses to run on a dirty working tree. A baseline snapshotted over uncommitted work records failures that no commit explains, and the next person cannot tell your work in progress from real debt. Commit or stash first. `--force` overrides it when you mean to.

## Config reference

The config lives at `gates.config.json` in your repo root. The runner also accepts `gates/gates.config.json` or `.gates.json`, and searches upward from the current directory, so it behaves the same from a subdirectory.

Point your editor at the schema for completion and validation while you type:

```json
{ "$schema": "./gates/gates.schema.json" }
```

JSON has no comments. Any key starting with `_` is ignored by the runner, so use `_comment` for notes. Every gate also takes a `description`, which appears in the report.

### Top level

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `baselineDir` | string | `.gates/baselines` | Where baselines live, relative to the config. Layout is `<baselineDir>/<project>/<gate>.txt`. Commit it. |
| `defaultTimeoutMs` | integer | `600000` | Default per-gate timeout. A gate that needs more than a few minutes is a CI job, not a local gate. |
| `projects` | array | required | One entry per buildable unit. In a monorepo, usually one per top-level directory. |

### Project

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `name` | string | required | Becomes a directory under `baselineDir` and the value for `--project`. `[A-Za-z0-9._-]+`. |
| `cwd` | string | `.` | Directory the gate commands run in, relative to the config. |
| `paths` | string[] | `[cwd]` | Repo-relative prefixes owned by this project. `--only-changed` skips the project when git reports no change under any of them. |
| `gates` | array | required | Gates run in the order listed. Put them cheapest first. |

### Gate

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `id` | string | required | Unique inside the project. Becomes the baseline file name and the value for `--gate`. |
| `description` | string | `""` | One short line shown next to the gate in the report. |
| `run` | string | required | The shell command. Runs through a shell, so pipes, quotes and `VAR=value` prefixes work. `node_modules/.bin` of the gate cwd is prepended to `PATH`. |
| `parser` | enum | required | How to turn output into failure keys. See below. |
| `baseline` | boolean | `true`, except `exit-code` | Compare against the baseline and fail only on new failures. Set `false` to make any failure fatal. |
| `env` | object | `{}` | Extra environment variables for this gate only. |
| `timeoutMs` | integer | `defaultTimeoutMs` | Per-gate timeout override. |
| `cwd` | string | project `cwd` | Override the working directory for this one gate. |
| `reportFile` | string | none | Read parser input from this file instead of stdout. Required for `junit-xml`, where it may be one XML file or a directory to walk. |
| `allowedExitCodes` | integer[] | `[0]` | Exit codes that mean the tool ran normally. A test runner exiting 1 on failures ran normally, so put `[0, 1]` there. |

### Parsers

Each parser turns raw output into a set of **stable failure keys**. Stable means: same broken code, same keys, on any machine, on any day. Keys never carry an absolute path, a timing, a line number that shifts, or an assertion message.

| Parser | Reads | Key shape | Notes |
| --- | --- | --- | --- |
| `pytest` | stdout | `path/test_x.py::test_name` | Needs `-rfE` in the command. Reads the short summary lines, so no plugin required. The ` - message` tail is dropped. |
| `vitest` | JSON reporter | `path/file.test.ts > full test name` | Write to `--outputFile` and set `reportFile`. A suite that fails to load is keyed as `[suite failed to run]` rather than passing silently. |
| `tsc` | stdout | `path/file.ts: error TS2345: message` | `(line,col)` is dropped. The message stays, because for a type error the message is the identity. A project-level error such as TS5083 is reported as a broken gate, never baselined. |
| `eslint` | `--format json` | `path/file.ts: rule-id` | Line and column dropped. Errors and warnings both count. Five hits of one rule in one file collapse to one key. |
| `go-test` | `-json` stream | `package/path.TestName` | Subtests included. A package that failed to build is keyed once, and only when no individual test in it failed. |
| `junit-xml` | XML files | `classname.testname` | For Maven surefire and Gradle. `reportFile` may be a file or a directory to walk. `<skipped/>` is not a failure. |
| `exit-code` | exit status | none | Fallback for any tool with no machine-readable output. Produces no keys, so it cannot be baselined. Use it for a build, a format check, or a shell script. |

## CLI reference

```
node gates/run-gates.mjs [options]
```

| Flag | Meaning |
| --- | --- |
| `--config <path>` | Path to the config. Default: search upward for `gates.config.json`, `gates/gates.config.json`, `.gates.json`. |
| `--project <name>` | Run only this project. Repeatable. |
| `--gate <id>` | Run only gates with this id. Repeatable. |
| `--only-changed` | Skip projects whose `paths` were not touched, against the merge base with `--base`, plus uncommitted work. |
| `--base <ref>` | Merge base for `--only-changed`. Default `origin/main`. |
| `--update-baseline` | Re-snapshot instead of comparing. Refuses on a dirty tree unless `--force`. |
| `--force` | Allow `--update-baseline` on a dirty tree. |
| `--show-known` | List the known baseline failures, not just the count. |
| `--json` | Print one JSON object instead of the human report. |
| `--no-color` | Disable colour. Colour is off automatically when output is not a TTY. |
| `-h`, `--help` | Usage. |

### Exit codes

| Code | Meaning | What to do |
| --- | --- | --- |
| `0` | All clear. Known baseline failures may still exist and are reported. | Commit. |
| `1` | New failures, not in the baseline. | Fix them. Do not add them to the baseline. |
| `2` | Config or usage error. | Fix the config or the command line. |
| `3` | A gate command could not be executed, or the gate itself is broken. | Fix the gate. This is not test debt. |

A **missing toolchain is not a failure**. It reports `SKIP` and does not change the exit code, so one config works on a machine that only has half the stacks. The summary still says a skip is not a pass, so nobody mistakes it for green.

### `--json`

```json
{
  "ok": false,
  "exitCode": 1,
  "gates": [
    {
      "project": "backend",
      "gate": "pytest",
      "description": "unit tests",
      "status": "FAIL(new)",
      "durationMs": 502,
      "message": null,
      "newFailures": ["backend/tests/test_math.py::test_new_regression"],
      "knownFailures": ["backend/tests/test_math.py::test_known_debt"],
      "fixedFailures": []
    }
  ]
}
```

`status` is one of `PASS`, `FAIL(new)`, `FAIL(baseline only)`, `SKIP`, `ERROR`, `UPDATED`.

## Adding a stack

Most stacks need no code. Pick the parser whose key shape fits and write a gate:

1. Run the tool by hand and look at its failure output.
2. If a parser already matches that shape, use it. If the tool can emit JUnit XML, use `junit-xml`, since most runners can.
3. If nothing fits, use `exit-code`. It gives you pass or fail with no baseline, which is still worth having.

To add a real parser:

1. Capture realistic output into `gates/test/fixtures/<tool>-failures.txt`.
2. Write the parser in `gates/src/parsers.mjs`. It takes `(text, ctx, gate)` and returns `{ keys: Set<string>, error?: string }`. Use `normalizePath` for any path. Return `error` when the output cannot be parsed at all, which means the gate is broken and not that the code is.
3. Register it in the `PARSERS` map and add the name to `KNOWN_PARSERS` in `gates/src/config.mjs` and to the `parser` enum in `gates/gates.schema.json`.
4. Add tests in `gates/test/run-tests.mjs`. Cover at least: keys from the fixture, a clean run producing no keys, and unparsable output producing an `error`.

The key stability rule is the one to get right. Before you commit a parser, ask: would this key change if somebody added a line at the top of the file? If yes, the parser will invent NEW failures out of unrelated edits, and the gate will be turned off within a week.

## Tests

```bash
node gates/test/run-tests.mjs
```

Built-ins only, `node:test` and `node:assert`. No test runner to install.

## Design notes

**Zero dependencies.** A teammate clones the repo and runs the gate in the next five seconds, not after a package fetch. That also means no supply chain to audit for a tool that runs on every commit.

**Baselines as sorted plain text.** A JSON blob or a hash would hide exactly the change that most needs review: somebody adding a line to get past a red gate.

**A missing tool skips, a broken gate errors.** These are different and the exit codes keep them different. A tool that exits non-zero while reporting zero failures is treated as `ERROR`, not as a clean pass, because snapshotting that would record a permanently blind gate as healthy.
