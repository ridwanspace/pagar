# Cursor adapter

**What this page answers:** a short mapping from this method's four primitives to Cursor, plus one
worked example rule file.

**Tested?** No. Claude Code is the only tool this starter kit was exercised end to end on. This is
a mapping note. Verify the frontmatter fields and the directory against your installed version,
because Cursor's rules format has changed across releases and the details here may be behind.

## Mapping

| Primitive | Cursor |
| --- | --- |
| Always-loaded project context | a rule with `alwaysApply: true`, or the legacy `.cursorrules` file at the repo root |
| Scoped knowledge, loaded on demand | `.cursor/rules/*.mdc` with a `globs` pattern, which is the closest analogue in any of these tools to this kit's path-scoped rules |
| Repeatable named procedures | no first-class equivalent. Keep procedures as markdown in the repo and point at them |
| Deterministic checkpoints | not in the editor. Use CI and a pre-commit hook |

## The one thing Cursor does better than most

Glob-scoped rules. A rule with `globs: ["**/test_*.py"]` costs nothing until the agent touches a
test file. That is the same idea as this kit's `paths:` frontmatter, and it is the mechanism that
keeps always-loaded context small.

Use it. The temptation is to set `alwaysApply: true` on everything so nothing gets missed. That
recreates the single-large-memory-file problem, and it is the most common way a Cursor rules
directory goes bad.

Rough guide:

- `alwaysApply: true` for the orientation rule only: what the project is, the commands, the locked
  decisions. One file.
- `globs` for everything else. Testing rules on test files. API rules on handler files. Frontend
  rules on component files.

## Install

```bash
mkdir -p .cursor/rules
cp starter/agent-adapters/cursor/.cursor/rules/testing.mdc .cursor/rules/
```

Adjust the `globs` in the frontmatter to match your layout. The shipped example covers both a
Python and a TypeScript layout, so delete the half you do not use.

## Example

See [`.cursor/rules/testing.mdc`](.cursor/rules/testing.mdc). Its frontmatter:

```yaml
---
description: Test discipline. Red first, mutation verification, what to assert, mocking traps.
globs:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/test_*.py"
  - "**/tests/**"
alwaysApply: false
---
```

Three fields, and each earns its place:

- `description` tells the agent what the rule is for, so it can decide whether to pull the rule in.
  Write it as a sentence that answers "when would I need this", not as a title.
- `globs` scopes the rule to matching files. This is the field that keeps context small.
- `alwaysApply: false` means the rule loads on match rather than on every request. Set it to `true`
  only for the orientation rule.

## Porting the rest

Take the Antigravity rules in `../antigravity/.agents/rules/` as the source. They are already split
by subject, which is the hard part, and each is small. Add frontmatter and rename to `.mdc`:

| Antigravity rule | Cursor rule | Suggested scope |
| --- | --- | --- |
| `00-project.md` | `project.mdc` | `alwaysApply: true` |
| `10-structure.md` | `structure.mdc` | `alwaysApply: true`, or glob to your source directories |
| `20-testing.md` | `testing.mdc` | glob to test files, shipped here |
| `30-security.md` | `security.mdc` | glob to handlers, auth, and anything touching requests |
| `40-writing.md` | `writing.mdc` | `alwaysApply: true`, it is short |

Cursor has no documented character cap of the kind Antigravity has, but the files are small anyway
and small is the right size.

## What you have to solve elsewhere

**Procedures.** There is no workflow or skill equivalent. Keep `docs/procedures/implement-story.md`
and similar files in the repo, and start a task by pointing the agent at one. More typing, same
result, and the file survives your next tool change.

**Hooks.** There is no in-editor checkpoint that runs outside the model. Put the gates in CI and in
a pre-commit hook. The two scripts in `starter/.claude/hooks/` are plain Node and plain Python that
read environment variables and write to stdout, so they run fine from a pre-commit hook or a CI
step with no changes.

This is the honest limitation of the tool for this method. Rules are instructions the model can
reason around. Without a checkpoint outside the model, the discipline depends on the model
cooperating every time.
