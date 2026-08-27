#!/usr/bin/env node
/**
 * SessionStart hook: report how far the current branch has drifted from the
 * default branch on the remote. It fetches, then it reports. It never merges,
 * never rebases, never touches the working tree.
 *
 * Exit code is 0 on every path, including failure. A session-start hook that
 * fails hard is worse than no hook at all: it blocks work to tell you about
 * something you did not ask about. No network, no remote, no git repo,
 * detached HEAD, and missing credentials are all "stay quiet, get out of the
 * way" cases.
 *
 * Anything printed on stdout is injected into the session context, so keep it
 * short and keep it actionable.
 *
 * Configuration, all optional:
 *   AGENT_DRIFT_REMOTE        remote name              default "origin"
 *   AGENT_DRIFT_DEFAULT_BRANCH  branch to compare to   default: detected, else "main"
 *   AGENT_DRIFT_TIMEOUT_MS    per-git-command timeout  default 20000
 *   AGENT_DRIFT_MAX_COMMITS   commits to list          default 5
 *   AGENT_DRIFT_SYNC_HINT     the command to suggest   default "/sync-main"
 *   CLAUDE_PROJECT_DIR        repo root                default process.cwd()
 *
 * Dependencies: none. Node standard library only.
 */

import { execFileSync } from 'node:child_process';

const CWD = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const REMOTE = process.env.AGENT_DRIFT_REMOTE || 'origin';
const TIMEOUT = Number(process.env.AGENT_DRIFT_TIMEOUT_MS) || 20_000;
const MAX_COMMITS = Number(process.env.AGENT_DRIFT_MAX_COMMITS) || 5;
const SYNC_HINT = process.env.AGENT_DRIFT_SYNC_HINT || '/sync-main';

/**
 * Run git and return trimmed stdout. Return null when the command fails for
 * any reason: non-zero exit, timeout, or git not being installed. Callers
 * treat null as "no answer available" and bail quietly.
 */
function git(args, { timeout = TIMEOUT } = {}) {
  try {
    return execFileSync('git', args, {
      cwd: CWD,
      timeout,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      env: {
        ...process.env,
        // A hook has no one to answer a credential prompt. Without this a
        // private remote hangs session startup until the timeout fires.
        GIT_TERMINAL_PROMPT: '0',
        GIT_ASKPASS: 'echo',
        GIT_OPTIONAL_LOCKS: '0',
      },
    }).trim();
  } catch {
    return null;
  }
}

/**
 * Work out which branch to compare against, in order of confidence:
 *   1. the explicit environment variable,
 *   2. the remote HEAD symref that `git remote set-head` records,
 *   3. whichever of main or master actually exists on the remote,
 *   4. "main".
 */
function resolveDefaultBranch() {
  const configured = process.env.AGENT_DRIFT_DEFAULT_BRANCH;
  if (configured) return configured;

  const symref = git(['symbolic-ref', '--quiet', '--short', `refs/remotes/${REMOTE}/HEAD`]);
  if (symref && symref.startsWith(`${REMOTE}/`)) {
    return symref.slice(REMOTE.length + 1);
  }

  for (const candidate of ['main', 'master']) {
    if (git(['rev-parse', '--verify', '--quiet', `refs/remotes/${REMOTE}/${candidate}`])) {
      return candidate;
    }
  }
  return 'main';
}

function plural(n, word) {
  return `${n} ${word}${n === 1 ? '' : 's'}`;
}

function main() {
  // Not a git repo, or git is missing. Nothing to report.
  if (git(['rev-parse', '--is-inside-work-tree']) !== 'true') return;

  const branch = git(['rev-parse', '--abbrev-ref', 'HEAD']);
  if (!branch || branch === 'HEAD') return; // detached HEAD has nothing to sync

  // No remote configured. A local-only repo cannot drift from anything.
  if (!git(['remote', 'get-url', REMOTE])) return;

  const defaultBranch = resolveDefaultBranch();
  if (branch === defaultBranch) return; // already on the target

  // The fetch is the whole point. Without it the tracking ref is stale and
  // the behind-count reads 0 even when the default branch has moved on.
  // A failure here means offline or no credentials, so report nothing.
  if (git(['fetch', REMOTE, '--prune', '--quiet']) === null) return;

  const target = `${REMOTE}/${defaultBranch}`;
  if (!git(['rev-parse', '--verify', '--quiet', target])) return;

  const counts = git(['rev-list', '--left-right', '--count', `${target}...HEAD`]);
  if (!counts) return;

  const [behind, ahead] = counts.split(/\s+/).map(Number);
  if (!Number.isFinite(behind) || behind === 0) return; // up to date, say nothing

  const commits = (git(['log', '--oneline', '--no-merges', `-${MAX_COMMITS}`, `HEAD..${target}`]) || '')
    .split('\n')
    .filter(Boolean);

  const files = (git(['diff', '--name-only', `HEAD...${target}`]) || '')
    .split('\n')
    .filter(Boolean);

  // Group by the first two path segments so a 40-file diff reads as a few
  // areas instead of a wall of filenames.
  const areas = [...new Set(files.map((f) => f.split('/').slice(0, 2).join('/')))];

  const lines = [
    `[drift] ${branch} is ${plural(behind, 'commit')} behind ${target} (${ahead} ahead).`,
  ];

  if (commits.length) {
    lines.push('', 'Incoming commits:', ...commits.map((c) => `  ${c}`));
  }

  if (areas.length) {
    const shown = areas.slice(0, 8).join(', ');
    const more = areas.length > 8 ? `, and ${areas.length - 8} more` : '';
    lines.push('', `Touched areas (${plural(files.length, 'file')}): ${shown}${more}`);
  }

  lines.push('', `This is a report, not a merge. Run ${SYNC_HINT} when you want to catch up.`);

  console.log(lines.join('\n'));
}

try {
  main();
} catch (err) {
  // Belt and braces. Any unexpected throw stays silent on stdout so it can
  // never corrupt the injected context, and the exit code stays 0.
  process.stderr.write(`[drift] skipped: ${err && err.message ? err.message : err}\n`);
}

process.exit(0);
