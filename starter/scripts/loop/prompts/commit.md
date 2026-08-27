# This phase: commit for story {{REF}} — {{TITLE}}

Create ONE conventional commit containing all pending changes for story {{REF}}.

1. Review `git status --short` and `git diff --stat` to understand the change set.
2. Stage everything: `git add -A`.
3. Commit with a conventional message — `<type>(<scope>): <summary>` — where the summary
   reflects what the story actually shipped (not just its title), plus a body line
   referencing story {{REF}}.
4. Pre-commit hooks (typecheck, linters, related tests — whatever this project runs)
   MUST pass. If a hook rewrites files, restage and retry (max 3 attempts). Never
   `--no-verify`.
5. Success = `git status --porcelain` is empty. The loop verifies this.

Do not push. Do not touch the remote.
