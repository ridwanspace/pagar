/**
 * Reporting.
 *
 * The report has one job: when the gate fails, the reader must know within one
 * screen what to fix. So NEW failures are listed in full and printed first.
 * Known baseline failures are counted, not listed, unless asked for. Mixing the
 * two is how a real regression hides inside forty lines of old debt.
 */

export const STATUS = {
  PASS: "PASS",
  FAIL_NEW: "FAIL(new)",
  FAIL_BASELINE_ONLY: "FAIL(baseline only)",
  SKIP: "SKIP",
  ERROR: "ERROR", // the gate itself is broken, not the code under test
  UPDATED: "UPDATED",
};

/** Do we exit non-zero because of this status? */
export function isFatal(status) {
  return status === STATUS.FAIL_NEW || status === STATUS.ERROR;
}

const COLORS = {
  reset: "[0m",
  red: "[31m",
  green: "[32m",
  yellow: "[33m",
  blue: "[34m",
  dim: "[2m",
  bold: "[1m",
};

/** Colour only when a human is looking. A piped log with escape codes is worse than no colour. */
export function makePainter(enabled) {
  if (!enabled) return new Proxy({}, { get: () => (s) => s });
  return new Proxy({}, { get: (_t, name) => (s) => `${COLORS[name] ?? ""}${s}${COLORS.reset}` });
}

const MARK = {
  [STATUS.PASS]: "PASS",
  [STATUS.FAIL_NEW]: "FAIL",
  [STATUS.FAIL_BASELINE_ONLY]: "KNOWN",
  [STATUS.SKIP]: "SKIP",
  [STATUS.ERROR]: "ERROR",
  [STATUS.UPDATED]: "SAVED",
};

function paintStatus(paint, status) {
  const label = MARK[status].padEnd(5);
  if (status === STATUS.PASS) return paint.green(label);
  if (status === STATUS.FAIL_NEW || status === STATUS.ERROR) return paint.red(label);
  if (status === STATUS.SKIP) return paint.dim(label);
  if (status === STATUS.UPDATED) return paint.blue(label);
  return paint.yellow(label);
}

function seconds(ms) {
  if (ms === undefined || ms === null) return "";
  return ` ${(ms / 1000).toFixed(1)}s`;
}

/** Print one gate's result. */
export function printGateResult(result, { paint, showKnown, out = console.log }) {
  const head = `  ${paintStatus(paint, result.status)} ${result.project}/${result.gateId}`;
  const desc = result.description ? paint.dim(` ${result.description}`) : "";
  out(`${head}${desc}${paint.dim(seconds(result.durationMs))}`);

  if (result.status === STATUS.SKIP) {
    out(`        ${paint.dim(result.message)}`);
    return;
  }
  if (result.status === STATUS.ERROR) {
    for (const line of String(result.message).split("\n")) out(`        ${paint.red(line)}`);
    if (result.outputTail) {
      out(`        ${paint.dim("last lines of output:")}`);
      for (const line of result.outputTail) out(`        ${paint.dim(line)}`);
    }
    return;
  }

  if (result.newFailures?.length) {
    out(`        ${paint.red(`${result.newFailures.length} NEW failure(s), not in the baseline:`)}`);
    for (const key of result.newFailures) out(`          ${paint.red("+")} ${key}`);
  }
  if (result.knownFailures?.length) {
    const line = `${result.knownFailures.length} known failure(s) in the baseline, ignored`;
    out(`        ${paint.yellow(line)}`);
    if (showKnown) for (const key of result.knownFailures) out(`          ${paint.dim("=")} ${key}`);
  }
  if (result.fixedFailures?.length) {
    out(
      `        ${paint.green(
        `${result.fixedFailures.length} baseline failure(s) now pass. Re-snapshot with --update-baseline.`,
      )}`,
    );
    if (showKnown) for (const key of result.fixedFailures) out(`          ${paint.green("-")} ${key}`);
  }
  if (result.status === STATUS.UPDATED) {
    out(`        ${paint.blue(result.message)}`);
  }
}

/** Print the closing summary and the one thing to do next. */
export function printSummary(results, { paint, out = console.log }) {
  const counts = {};
  for (const r of results) counts[r.status] = (counts[r.status] ?? 0) + 1;
  const parts = Object.entries(counts).map(([status, n]) => `${n} ${MARK[status].trim()}`);
  out("");
  out(`  ${parts.join("  ")}`);

  const failed = results.filter((r) => r.status === STATUS.FAIL_NEW);
  const errored = results.filter((r) => r.status === STATUS.ERROR);
  const skipped = results.filter((r) => r.status === STATUS.SKIP);
  const shrunk = results.filter((r) => r.fixedFailures?.length > 0);

  if (errored.length > 0) {
    out("");
    out(paint.red(`  ${errored.length} gate(s) could not run. Fix the gate, then re-run.`));
  }
  if (failed.length > 0) {
    const total = failed.reduce((n, r) => n + r.newFailures.length, 0);
    out("");
    out(paint.red(`  ${total} new failure(s) across ${failed.length} gate(s). Fix them before committing.`));
    out(paint.dim("  Do not add them to the baseline to get past this."));
  }
  if (skipped.length > 0) {
    out("");
    out(paint.dim(`  ${skipped.length} gate(s) skipped. A skip is not a pass.`));
  }
  if (failed.length === 0 && errored.length === 0 && shrunk.length > 0) {
    out("");
    out(paint.green(`  ${shrunk.length} gate(s) have fewer failures than the baseline. Run --update-baseline.`));
  }
  return { counts, failed, errored, skipped };
}

/** Machine-readable form for --json. Stable field names, no colour, no timing noise in keys. */
export function toJson(results, { exitCode }) {
  return {
    ok: exitCode === 0,
    exitCode,
    gates: results.map((r) => ({
      project: r.project,
      gate: r.gateId,
      description: r.description,
      status: r.status,
      durationMs: r.durationMs ?? null,
      message: r.message ?? null,
      newFailures: r.newFailures ?? [],
      knownFailures: r.knownFailures ?? [],
      fixedFailures: r.fixedFailures ?? [],
    })),
  };
}
