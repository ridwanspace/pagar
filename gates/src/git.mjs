/**
 * The small amount of git the runner needs.
 *
 * Two jobs:
 *   1. Is the working tree clean? --update-baseline refuses on a dirty tree,
 *      because a baseline snapshotted over uncommitted work records failures
 *      that no commit explains.
 *   2. Which paths changed? --only-changed uses this to skip whole projects.
 *
 * Every function degrades to a safe answer when git is absent or the directory
 * is not a repo. The gate must still run outside a checkout.
 */
import { spawnSync } from "node:child_process";

function git(args, cwd) {
  return spawnSync("git", args, { cwd, encoding: "utf8", maxBuffer: 16 * 1024 * 1024 });
}

/** Repo root, or null when this is not a git checkout. */
export function repoRoot(cwd) {
  const r = git(["rev-parse", "--show-toplevel"], cwd);
  if (r.status !== 0) return null;
  return r.stdout.trim() || null;
}

/**
 * Is the tree clean? Returns { clean, dirtyFiles, available }.
 * `available: false` means git could not answer, and the caller should say so
 * rather than pretending the tree is clean.
 */
export function workingTreeStatus(cwd) {
  const r = git(["status", "--porcelain"], cwd);
  if (r.status !== 0) return { available: false, clean: false, dirtyFiles: [] };
  const dirtyFiles = r.stdout
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => l.slice(2).trim());
  return { available: true, clean: dirtyFiles.length === 0, dirtyFiles };
}

/**
 * Repo-relative paths changed against `base`, plus uncommitted work.
 *
 * We ask for the merge base first so a long-lived branch does not report every
 * file that moved on main since it forked. When there is no merge base (a fresh
 * repo, a shallow clone, `base` does not exist) we return null, and the caller
 * treats that as "cannot tell, run everything". Running too much is a slow
 * gate. Running too little is a gate that misses a regression.
 */
export function changedPaths(cwd, base = "origin/main") {
  const paths = new Set();

  const mergeBase = git(["merge-base", "HEAD", base], cwd);
  let diffTarget = null;
  if (mergeBase.status === 0 && mergeBase.stdout.trim()) {
    diffTarget = mergeBase.stdout.trim();
  } else {
    // No merge base. Fall back to the previous commit, which at least catches
    // "what am I about to commit" on a repo with no remote.
    const head = git(["rev-parse", "HEAD~1"], cwd);
    if (head.status === 0 && head.stdout.trim()) diffTarget = head.stdout.trim();
  }

  if (diffTarget) {
    const r = git(["diff", "--name-only", diffTarget, "HEAD"], cwd);
    if (r.status !== 0) return null;
    for (const p of r.stdout.split("\n").map((l) => l.trim()).filter(Boolean)) paths.add(p);
  } else {
    // Not even one prior commit. Cannot compute a diff at all.
    const anyCommit = git(["rev-parse", "HEAD"], cwd);
    if (anyCommit.status !== 0) return null;
  }

  // Uncommitted work counts as changed. This is the case that matters most:
  // the gate usually runs right before a commit.
  for (const args of [["diff", "--name-only"], ["diff", "--name-only", "--cached"], ["ls-files", "--others", "--exclude-standard"]]) {
    const r = git(args, cwd);
    if (r.status !== 0) continue;
    for (const p of r.stdout.split("\n").map((l) => l.trim()).filter(Boolean)) paths.add(p);
  }

  return [...paths];
}

/**
 * Does any changed path fall inside one of this project's path prefixes?
 * `"."` matches everything, which is the right default for a single-project repo.
 */
export function projectTouched(project, changed) {
  if (changed === null) return true; // cannot tell, so do not skip
  for (const prefix of project.paths) {
    const clean = prefix === "." || prefix === "" ? "" : prefix.replace(/^\.\//, "").replace(/\/+$/, "");
    if (clean === "") return true;
    if (changed.some((p) => p === clean || p.startsWith(`${clean}/`))) return true;
  }
  return false;
}
