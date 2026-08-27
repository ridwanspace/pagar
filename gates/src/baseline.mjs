/**
 * The baseline store, and the compare that makes the whole tool work.
 *
 * A baseline is the set of failures the repo already had when you started. The
 * gate fails only on keys that are NOT in it. That is what makes a gate
 * adoptable in a repo with existing debt. A gate that fails on day one for
 * reasons you did not cause gets disabled by day three.
 *
 * Storage: one plain text file per gate, sorted, one key per line. Sorted text
 * so `git diff` on a baseline is readable by a human reviewer. A JSON blob or a
 * hash would hide exactly the change that most needs a second pair of eyes:
 * somebody adding a line to get past a red gate.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

/** Where one gate's baseline lives. Layout: <baselineDir>/<project>/<gate>.txt */
export function baselinePath(config, projectName, gateId) {
  return resolve(dirname(config.configPath), config.baselineDir, projectName, `${gateId}.txt`);
}

/** Read a baseline. `null` means no baseline exists yet, which is not the same as an empty one. */
export function readBaseline(file) {
  if (!existsSync(file)) return null;
  const text = readFileSync(file, "utf8");
  return new Set(
    text
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l !== "" && !l.startsWith("#")),
  );
}

/** Write a baseline. Always sorted, always newline terminated, so diffs stay minimal. */
export function writeBaseline(file, keys) {
  mkdirSync(dirname(file), { recursive: true });
  const sorted = [...keys].sort();
  const body = sorted.length === 0 ? "" : sorted.join("\n") + "\n";
  writeFileSync(file, body, "utf8");
  return sorted.length;
}

/**
 * Compare the current failures against the baseline.
 *
 * Returns three groups, and the names matter for how the report reads:
 *   newFailures  - present now, absent from the baseline. These fail the run.
 *   knownFailures - present now and in the baseline. Shown, never fatal.
 *   fixedFailures - in the baseline, gone now. You paid down debt. Re-snapshot.
 *
 * Baseline policy, enforced in the CLI, stated here because this is where
 * somebody will read it: the baseline may SHRINK freely. It must NEVER GROW
 * without an explicit human decision. Growing it silently turns the gate into
 * a green light that means nothing.
 */
export function compareToBaseline(currentKeys, baselineKeys) {
  const current = currentKeys instanceof Set ? currentKeys : new Set(currentKeys);
  if (baselineKeys === null) {
    return {
      hasBaseline: false,
      newFailures: [...current].sort(),
      knownFailures: [],
      fixedFailures: [],
      grows: current.size > 0,
    };
  }
  const baseline = baselineKeys instanceof Set ? baselineKeys : new Set(baselineKeys);
  const newFailures = [...current].filter((k) => !baseline.has(k)).sort();
  const knownFailures = [...current].filter((k) => baseline.has(k)).sort();
  const fixedFailures = [...baseline].filter((k) => !current.has(k)).sort();
  return {
    hasBaseline: true,
    newFailures,
    knownFailures,
    fixedFailures,
    // Would re-snapshotting right now make the baseline bigger? The CLI uses
    // this to warn loudly on --update-baseline.
    grows: newFailures.length > 0,
  };
}
