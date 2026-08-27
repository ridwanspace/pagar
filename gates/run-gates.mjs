#!/usr/bin/env node
/**
 * gates: a baseline-aware, config-driven gate runner.
 *
 * Run the checks CI would run, locally, in seconds, and fail only on breakage
 * you are about to introduce. Pre-existing failures are recorded in a baseline
 * and reported without failing the run.
 *
 * Zero dependencies on purpose. It must start with a plain `node`, with no
 * `npm install`, in any repo, including one that has no package.json at all.
 *
 * Exit codes:
 *   0  all clear
 *   1  new failures, not in the baseline
 *   2  config or usage error
 *   3  a gate command could not be executed and no baseline decision was possible
 */
import { dirname } from "node:path";
import { ConfigError, findConfigFile, loadConfig } from "./src/config.mjs";
import { OUTCOME, runGate } from "./src/runner.mjs";
import { parseOutput } from "./src/parsers.mjs";
import { baselinePath, compareToBaseline, readBaseline, writeBaseline } from "./src/baseline.mjs";
import { changedPaths, projectTouched, repoRoot, workingTreeStatus } from "./src/git.mjs";
import { STATUS, makePainter, printGateResult, printSummary, toJson } from "./src/report.mjs";

const EXIT = { OK: 0, NEW_FAILURES: 1, USAGE: 2, GATE_UNRUNNABLE: 3 };

const HELP = `gates - baseline-aware local CI gates

Usage
  node gates/run-gates.mjs [options]

Options
  --config <path>       Path to the gates config. Default: search upward for
                        gates.config.json, gates/gates.config.json, .gates.json
  --project <name>      Run only this project. Repeatable.
  --gate <id>           Run only gates with this id. Repeatable.
  --only-changed        Skip projects whose paths were not touched, compared to
                        the merge base with --base (plus uncommitted work).
  --base <ref>          Merge base for --only-changed. Default: origin/main
  --update-baseline     Re-snapshot the baselines instead of comparing.
                        Refuses on a dirty working tree unless --force.
  --force               Allow --update-baseline on a dirty tree.
  --show-known          List the known baseline failures, not just the count.
  --json                Print one JSON object instead of the human report.
  --no-color            Disable colour.
  -h, --help            This text.

Exit codes
  0  all clear
  1  new failures, not in the baseline
  2  config or usage error
  3  a gate command could not be executed

Baseline policy
  The baseline may shrink freely. That means you fixed pre-existing debt, so
  re-snapshot it. NEVER grow the baseline to get past a red gate without an
  explicit human decision. Growing it silently is how the gate dies.
`;

function parseArgs(argv) {
  const opts = {
    config: null,
    projects: [],
    gates: [],
    onlyChanged: false,
    base: "origin/main",
    update: false,
    force: false,
    showKnown: false,
    json: false,
    color: process.stdout.isTTY === true && !process.env.NO_COLOR,
    help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const needsValue = () => {
      const v = argv[++i];
      if (v === undefined || v.startsWith("--")) throw new ConfigError(`${arg} needs a value`);
      return v;
    };
    switch (arg) {
      case "-h":
      case "--help": opts.help = true; break;
      case "--config": opts.config = needsValue(); break;
      case "--project": opts.projects.push(needsValue()); break;
      case "--gate": opts.gates.push(needsValue()); break;
      case "--only-changed": opts.onlyChanged = true; break;
      case "--base": opts.base = needsValue(); break;
      case "--update-baseline": opts.update = true; break;
      case "--force": opts.force = true; break;
      case "--show-known": opts.showKnown = true; break;
      case "--json": opts.json = true; opts.color = false; break;
      case "--no-color": opts.color = false; break;
      default:
        throw new ConfigError(`Unknown option "${arg}". Run with --help.`);
    }
  }
  return opts;
}

/** Last N lines of a gate's output, for an ERROR report. */
function tail(text, n = 12) {
  return text.split("\n").filter((l) => l.trim() !== "").slice(-n);
}

/** Run one gate and turn it into a result object the reporter understands. */
function executeGate(config, project, gate, opts, ctxRoot, configDir) {
  const base = {
    project: project.name,
    gateId: gate.id,
    description: gate.description,
  };

  // Two different bases, and mixing them up silently runs gates in the wrong
  // directory: a project cwd resolves from the CONFIG file's directory, while
  // failure keys are made relative to the REPO root.
  const run = runGate(gate, { baseDir: configDir, projectCwd: project.cwd });

  if (run.outcome === OUTCOME.MISSING_TOOL) {
    // A missing toolchain is not breakage. Say so clearly and move on, so the
    // gate config stays usable on a machine that only has half the stacks.
    return { ...base, status: STATUS.SKIP, message: `skipped: ${run.reason}`, durationMs: run.durationMs };
  }
  if (run.outcome === OUTCOME.TIMEOUT) {
    return {
      ...base,
      status: STATUS.ERROR,
      message: `gate ${run.reason}. Raise "timeoutMs" for this gate, or move it to CI.`,
      durationMs: run.durationMs,
      outputTail: tail(run.stdout + run.stderr),
    };
  }
  if (run.outcome === OUTCOME.CRASHED) {
    return {
      ...base,
      status: STATUS.ERROR,
      message: `gate command failed to run: ${run.reason}`,
      durationMs: run.durationMs,
      outputTail: tail(run.stdout + run.stderr),
    };
  }

  // exit-code gates have no keys. Pass or fail on the status, nothing else.
  if (gate.parser === "exit-code") {
    const allowed = gate.allowedExitCodes ?? [0];
    const ok = allowed.includes(run.status);
    if (ok) return { ...base, status: STATUS.PASS, durationMs: run.durationMs, newFailures: [], knownFailures: [] };
    return {
      ...base,
      status: STATUS.FAIL_NEW,
      durationMs: run.durationMs,
      newFailures: [`exited ${run.status} (allowed: ${allowed.join(", ")})`],
      knownFailures: [],
      fixedFailures: [],
    };
  }

  const parsed = parseOutput(gate, run.stdout + run.stderr, { repoRoot: ctxRoot, cwd: run.cwd });
  if (parsed.error) {
    return {
      ...base,
      status: STATUS.ERROR,
      message: parsed.error,
      durationMs: run.durationMs,
      outputTail: tail(run.stdout + run.stderr),
    };
  }

  // A tool that exits non-zero while reporting no failures did not fail a test.
  // It crashed, or it was misconfigured. Snapshotting an empty set here would
  // record a permanently blind gate as healthy.
  const allowed = gate.allowedExitCodes ?? null;
  const statusLooksBroken = allowed ? !allowed.includes(run.status) && parsed.keys.size === 0 : run.status !== 0 && parsed.keys.size === 0;
  if (statusLooksBroken) {
    return {
      ...base,
      status: STATUS.ERROR,
      message:
        `command exited ${run.status} but the "${gate.parser}" parser found no failures. ` +
        `The run itself is broken, not a test.`,
      durationMs: run.durationMs,
      outputTail: tail(run.stdout + run.stderr),
    };
  }

  const file = baselinePath(config, project.name, gate.id);

  if (opts.update) {
    const previous = readBaseline(file);
    const n = writeBaseline(file, parsed.keys);
    const delta = previous === null ? null : n - previous.size;
    const note =
      delta === null
        ? `baseline created with ${n} known failure(s)`
        : delta === 0
          ? `baseline unchanged, ${n} known failure(s)`
          : delta < 0
            ? `baseline shrank by ${-delta}, now ${n} known failure(s)`
            : `baseline GREW by ${delta}, now ${n} known failure(s). Only keep this if a human decided to.`;
    return { ...base, status: STATUS.UPDATED, message: note, durationMs: run.durationMs, grew: delta !== null && delta > 0 };
  }

  if (!gate.baseline) {
    // Baseline turned off for this gate: any failure fails the run.
    const keys = [...parsed.keys].sort();
    return {
      ...base,
      status: keys.length === 0 ? STATUS.PASS : STATUS.FAIL_NEW,
      durationMs: run.durationMs,
      newFailures: keys,
      knownFailures: [],
      fixedFailures: [],
    };
  }

  const baseline = readBaseline(file);
  const cmp = compareToBaseline(parsed.keys, baseline);
  if (!cmp.hasBaseline && cmp.newFailures.length > 0) {
    return {
      ...base,
      status: STATUS.ERROR,
      message:
        `no baseline at ${config.baselineDir}/${project.name}/${gate.id}.txt and ${cmp.newFailures.length} failure(s) present.\n` +
        `Run with --update-baseline from a clean tree to record the current debt, then commit the baseline.`,
      durationMs: run.durationMs,
    };
  }

  let status = STATUS.PASS;
  if (cmp.newFailures.length > 0) status = STATUS.FAIL_NEW;
  else if (cmp.knownFailures.length > 0) status = STATUS.FAIL_BASELINE_ONLY;

  return {
    ...base,
    status,
    durationMs: run.durationMs,
    newFailures: cmp.newFailures,
    knownFailures: cmp.knownFailures,
    fixedFailures: cmp.fixedFailures,
  };
}

function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(err.message);
    return EXIT.USAGE;
  }
  if (opts.help) {
    console.log(HELP);
    return EXIT.OK;
  }

  const paint = makePainter(opts.color);

  let config;
  try {
    const configFile = findConfigFile(process.cwd(), opts.config);
    config = loadConfig(configFile);
  } catch (err) {
    if (err instanceof ConfigError) {
      console.error(paint.red(err.message));
      return EXIT.USAGE;
    }
    throw err;
  }

  // Everything resolves from the config file's directory. That makes the runner
  // behave the same whether it is called from the repo root or a subdirectory.
  const configDir = dirname(config.configPath);
  const ctxRoot = repoRoot(configDir) ?? configDir;

  if (opts.update) {
    const tree = workingTreeStatus(ctxRoot);
    if (!tree.available && !opts.force) {
      console.error(
        paint.red("Refusing to update the baseline: this is not a git checkout, so the tree state cannot be verified."),
      );
      console.error(paint.dim("Pass --force if you are sure the code is in the state you want recorded."));
      return EXIT.USAGE;
    }
    if (tree.available && !tree.clean && !opts.force) {
      console.error(paint.red("Refusing to update the baseline: the working tree is dirty."));
      console.error(
        paint.dim(
          "A baseline snapshotted over uncommitted work records failures that no commit explains.\n" +
            "The next person cannot tell debt from your work in progress. Commit or stash first.\n" +
            "Pass --force only if you deliberately want the current tree recorded.",
        ),
      );
      for (const f of tree.dirtyFiles.slice(0, 10)) console.error(paint.dim(`  ${f}`));
      if (tree.dirtyFiles.length > 10) console.error(paint.dim(`  ... and ${tree.dirtyFiles.length - 10} more`));
      return EXIT.USAGE;
    }
  }

  // Selection.
  let projects = config.projects;
  if (opts.projects.length > 0) {
    const wanted = new Set(opts.projects);
    const known = new Set(projects.map((p) => p.name));
    for (const name of wanted) {
      if (!known.has(name)) {
        console.error(paint.red(`Unknown project "${name}". Known: ${[...known].join(", ")}`));
        return EXIT.USAGE;
      }
    }
    projects = projects.filter((p) => wanted.has(p.name));
  }

  let changed = null;
  if (opts.onlyChanged) {
    changed = changedPaths(ctxRoot, opts.base);
    if (changed === null && !opts.json) {
      console.log(paint.dim(`  --only-changed: cannot compute a diff against ${opts.base}, running everything.`));
    }
  }

  const results = [];
  if (!opts.json) {
    console.log("");
    console.log(paint.bold(opts.update ? "  Snapshotting baselines" : "  Running gates"));
    console.log(paint.dim(`  config ${config.configPath}`));
    console.log("");
  }

  for (const project of projects) {
    if (opts.onlyChanged && !projectTouched(project, changed)) {
      if (!opts.json) console.log(`  ${paint.dim("SKIP ")} ${project.name}/* ${paint.dim("no changes under " + project.paths.join(", "))}`);
      continue;
    }
    for (const gate of project.gates) {
      if (opts.gates.length > 0 && !opts.gates.includes(gate.id)) continue;
      const result = executeGate(config, project, gate, opts, ctxRoot, configDir);
      results.push(result);
      if (!opts.json) printGateResult(result, { paint, showKnown: opts.showKnown });
    }
  }

  if (opts.gates.length > 0 && results.length === 0) {
    console.error(paint.red(`No gate matched --gate ${opts.gates.join(", ")}.`));
    return EXIT.USAGE;
  }

  let exitCode = EXIT.OK;
  if (results.some((r) => r.status === STATUS.FAIL_NEW)) exitCode = EXIT.NEW_FAILURES;
  else if (results.some((r) => r.status === STATUS.ERROR)) exitCode = EXIT.GATE_UNRUNNABLE;

  if (opts.json) {
    console.log(JSON.stringify(toJson(results, { exitCode }), null, 2));
    return exitCode;
  }

  printSummary(results, { paint });
  if (opts.update && results.some((r) => r.grew)) {
    console.log("");
    console.log(paint.yellow("  A baseline grew. Growing a baseline hides a real failure."));
    console.log(paint.dim("  Keep it only if a human decided this failure is acceptable debt. Say why in the commit message."));
  }
  console.log("");
  return exitCode;
}

process.exit(main());
