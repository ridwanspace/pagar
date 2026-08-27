/**
 * Process running.
 *
 * One job: run a gate command and say what happened, in terms the reporter can
 * act on. The important distinction is "the tool is missing" versus "the tool
 * ran and found failures". A missing tool must SKIP, never FAIL. A gate that
 * fails red on a machine without Go installed gets deleted from the config by
 * the next person who hits it.
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { delimiter, isAbsolute, join, resolve } from "node:path";

/** 64 MB. A full test suite in JSON can be large, and a truncated report is a lie. */
const MAX_BUFFER = 64 * 1024 * 1024;

/** Outcome kinds a gate command can have. */
export const OUTCOME = {
  RAN: "ran", // the tool ran to completion, output is trustworthy
  MISSING_TOOL: "missing-tool", // the command does not exist on this machine
  TIMEOUT: "timeout",
  CRASHED: "crashed", // ran, but exited in a way that says the run itself broke
};

/**
 * Pull the executable name out of a shell command string.
 * We only need the first token to answer "is this tool installed". Env-var
 * prefixes such as `FOO=1 pytest` are skipped so we look at the real binary.
 */
export function commandName(run) {
  for (const token of run.trim().split(/\s+/)) {
    if (/^[A-Za-z_][A-Za-z0-9_]*=/.test(token)) continue; // VAR=value prefix
    return token;
  }
  return run.trim();
}

/**
 * Is `name` runnable from `cwd`? Checks a path-shaped name directly, otherwise
 * walks PATH plus the node_modules/.bin directories a JS project would use.
 */
export function isExecutableAvailable(name, cwd, env = process.env) {
  if (name.includes("/")) {
    const p = isAbsolute(name) ? name : resolve(cwd, name);
    return existsSync(p);
  }
  const dirs = [
    join(cwd, "node_modules", ".bin"),
    ...String(env.PATH ?? "").split(delimiter).filter(Boolean),
  ];
  for (const dir of dirs) {
    if (existsSync(join(dir, name))) return true;
    // Windows-ish shims. Cheap to check, saves a confusing SKIP.
    if (existsSync(join(dir, `${name}.cmd`)) || existsSync(join(dir, `${name}.exe`))) return true;
  }
  return false;
}

/**
 * Run one gate command.
 *
 * We run through a shell on purpose. Gate commands are copied from a README or
 * a package.json script, and those use pipes, quotes and env prefixes freely.
 * The config is local and hand written, so there is no untrusted input here.
 */
export function runGate(gate, { baseDir, projectCwd, env = process.env }) {
  // baseDir is the CONFIG file's directory, not the repo root. A config in a
  // subdirectory with cwd "." must run there, not at the top of the checkout.
  const cwd = resolve(baseDir, gate.cwd ?? projectCwd);
  if (!existsSync(cwd)) {
    return {
      outcome: OUTCOME.MISSING_TOOL,
      reason: `working directory does not exist: ${cwd}`,
      stdout: "",
      stderr: "",
      status: null,
      cwd,
    };
  }

  const bin = commandName(gate.run);
  if (!isExecutableAvailable(bin, cwd, env)) {
    return {
      outcome: OUTCOME.MISSING_TOOL,
      reason: `"${bin}" is not installed or not on PATH`,
      stdout: "",
      stderr: "",
      status: null,
      cwd,
    };
  }

  // node_modules/.bin first so `vitest` and `tsc` resolve to the project copy
  // rather than a global one that may be a different major version.
  const localBin = join(cwd, "node_modules", ".bin");
  const childEnv = {
    ...env,
    ...gate.env,
    PATH: `${localBin}${delimiter}${env.PATH ?? ""}`,
  };

  const started = Date.now();
  const result = spawnSync(gate.run, {
    cwd,
    shell: true,
    encoding: "utf8",
    maxBuffer: MAX_BUFFER,
    timeout: gate.timeoutMs,
    env: childEnv,
  });
  const durationMs = Date.now() - started;

  const stdout = result.stdout ?? "";
  const stderr = result.stderr ?? "";

  if (result.error && result.error.code === "ETIMEDOUT") {
    return {
      outcome: OUTCOME.TIMEOUT,
      reason: `timed out after ${gate.timeoutMs} ms`,
      stdout,
      stderr,
      status: null,
      durationMs,
      cwd,
    };
  }
  if (result.error && result.error.code === "ENOBUFS") {
    return {
      outcome: OUTCOME.CRASHED,
      reason: `produced more than ${MAX_BUFFER} bytes of output`,
      stdout,
      stderr,
      status: null,
      durationMs,
      cwd,
    };
  }
  if (result.error) {
    return {
      outcome: OUTCOME.CRASHED,
      reason: result.error.message,
      stdout,
      stderr,
      status: null,
      durationMs,
      cwd,
    };
  }
  // 127 is the shell's "command not found". The availability check above misses
  // it when the command is a pipeline and the missing binary is not the first.
  if (result.status === 127) {
    return {
      outcome: OUTCOME.MISSING_TOOL,
      reason: `shell reported command not found (exit 127)`,
      stdout,
      stderr,
      status: 127,
      durationMs,
      cwd,
    };
  }

  return { outcome: OUTCOME.RAN, stdout, stderr, status: result.status, durationMs, cwd };
}
