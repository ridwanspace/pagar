/**
 * Config loading and validation.
 *
 * Why validate by hand instead of shipping a validator dependency: the runner
 * must start with a plain `node` and no `npm install`. A teammate who clones
 * the repo runs the gate in the next five seconds, not after a package fetch.
 * gates.schema.json still ships so editors give live feedback while typing.
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, isAbsolute, resolve } from "node:path";

/** Config keys we understand. An unknown key is almost always a typo. */
const GATE_KEYS = new Set([
  "id",
  "description",
  "run",
  "parser",
  "baseline",
  "env",
  "timeoutMs",
  "cwd",
  "reportFile",
  "allowedExitCodes",
  "_comment",
]);
const PROJECT_KEYS = new Set(["name", "cwd", "paths", "gates", "_comment"]);
const ROOT_KEYS = new Set(["$schema", "baselineDir", "defaultTimeoutMs", "projects", "_comment"]);

export const KNOWN_PARSERS = new Set([
  "pytest",
  "vitest",
  "tsc",
  "eslint",
  "go-test",
  "junit-xml",
  "exit-code",
]);

const DEFAULT_TIMEOUT_MS = 10 * 60 * 1000;
const DEFAULT_BASELINE_DIR = ".gates/baselines";

/** Thrown for anything the user can fix by editing the config or the command line. */
export class ConfigError extends Error {}

/** Candidate config file names, in the order we look for them. */
export const CONFIG_NAMES = ["gates.config.json", "gates/gates.config.json", ".gates.json"];

/**
 * Find the config file. An explicit path wins. Otherwise walk up from `startDir`
 * so the gate runs the same way from a subdirectory as from the repo root.
 */
export function findConfigFile(startDir, explicitPath) {
  if (explicitPath) {
    const p = isAbsolute(explicitPath) ? explicitPath : resolve(startDir, explicitPath);
    if (!existsSync(p)) throw new ConfigError(`Config file not found: ${p}`);
    return p;
  }
  let dir = resolve(startDir);
  for (;;) {
    for (const name of CONFIG_NAMES) {
      const p = resolve(dir, name);
      if (existsSync(p)) return p;
    }
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new ConfigError(
    `No gates config found. Looked for ${CONFIG_NAMES.join(", ")} from ${startDir} upward.\n` +
      `Copy gates/gates.config.example.json to gates.config.json at your repo root and edit it.`,
  );
}

function fail(where, message) {
  throw new ConfigError(`${where}: ${message}`);
}

function checkUnknownKeys(where, obj, allowed) {
  for (const key of Object.keys(obj)) {
    // Any key starting with _ is a comment slot. JSON has no comments, so the
    // config format buys them back this way.
    if (key.startsWith("_")) continue;
    if (!allowed.has(key)) fail(where, `unknown key "${key}"`);
  }
}

function validateGate(gate, where, seenIds) {
  if (typeof gate !== "object" || gate === null || Array.isArray(gate)) {
    fail(where, "gate must be an object");
  }
  checkUnknownKeys(where, gate, GATE_KEYS);
  if (typeof gate.id !== "string" || gate.id.trim() === "") fail(where, `"id" must be a non-empty string`);
  // The id becomes a baseline file name, so keep it filesystem safe.
  if (!/^[A-Za-z0-9._-]+$/.test(gate.id)) {
    fail(where, `"id" must match [A-Za-z0-9._-]+ (it becomes a baseline file name), got "${gate.id}"`);
  }
  if (seenIds.has(gate.id)) fail(where, `duplicate gate id "${gate.id}" inside the same project`);
  seenIds.add(gate.id);
  if (typeof gate.run !== "string" || gate.run.trim() === "") fail(where, `"run" must be a non-empty command string`);
  if (typeof gate.parser !== "string" || !KNOWN_PARSERS.has(gate.parser)) {
    fail(where, `"parser" must be one of: ${[...KNOWN_PARSERS].join(", ")}`);
  }
  if (gate.baseline !== undefined && typeof gate.baseline !== "boolean") {
    fail(where, `"baseline" must be a boolean`);
  }
  // exit-code produces no keys, so there is nothing for a baseline to hold.
  if (gate.parser === "exit-code" && gate.baseline === true) {
    fail(where, `parser "exit-code" produces no failure keys, so "baseline" cannot be true`);
  }
  if (gate.env !== undefined) {
    if (typeof gate.env !== "object" || gate.env === null || Array.isArray(gate.env)) {
      fail(where, `"env" must be an object of string values`);
    }
    for (const [k, v] of Object.entries(gate.env)) {
      if (typeof v !== "string") fail(where, `env["${k}"] must be a string`);
    }
  }
  if (gate.timeoutMs !== undefined && (!Number.isInteger(gate.timeoutMs) || gate.timeoutMs <= 0)) {
    fail(where, `"timeoutMs" must be a positive integer`);
  }
  if (gate.cwd !== undefined && typeof gate.cwd !== "string") fail(where, `"cwd" must be a string`);
  if (gate.reportFile !== undefined && typeof gate.reportFile !== "string") {
    fail(where, `"reportFile" must be a string`);
  }
  // junit-xml has no stdout to read. It always needs a file or a glob.
  if (gate.parser === "junit-xml" && !gate.reportFile) {
    fail(where, `parser "junit-xml" needs "reportFile" pointing at the XML report directory or file`);
  }
  if (gate.allowedExitCodes !== undefined) {
    if (!Array.isArray(gate.allowedExitCodes) || gate.allowedExitCodes.some((c) => !Number.isInteger(c))) {
      fail(where, `"allowedExitCodes" must be an array of integers`);
    }
  }
}

/**
 * Read, parse and validate the config. Returns a normalised object where every
 * default is filled in, so no other module needs to know what the defaults are.
 */
export function loadConfig(configPath) {
  let raw;
  try {
    raw = readFileSync(configPath, "utf8");
  } catch (err) {
    throw new ConfigError(`Cannot read config ${configPath}: ${err.message}`);
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new ConfigError(`Config ${configPath} is not valid JSON: ${err.message}`);
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new ConfigError(`Config ${configPath} must be a JSON object`);
  }
  checkUnknownKeys(configPath, parsed, ROOT_KEYS);

  if (!Array.isArray(parsed.projects) || parsed.projects.length === 0) {
    throw new ConfigError(`${configPath}: "projects" must be a non-empty array`);
  }
  if (parsed.defaultTimeoutMs !== undefined && (!Number.isInteger(parsed.defaultTimeoutMs) || parsed.defaultTimeoutMs <= 0)) {
    throw new ConfigError(`${configPath}: "defaultTimeoutMs" must be a positive integer`);
  }
  if (parsed.baselineDir !== undefined && typeof parsed.baselineDir !== "string") {
    throw new ConfigError(`${configPath}: "baselineDir" must be a string`);
  }

  const defaultTimeoutMs = parsed.defaultTimeoutMs ?? DEFAULT_TIMEOUT_MS;
  const seenProjects = new Set();
  const projects = parsed.projects.map((project, i) => {
    const where = `${configPath} projects[${i}]`;
    if (typeof project !== "object" || project === null || Array.isArray(project)) {
      fail(where, "project must be an object");
    }
    checkUnknownKeys(where, project, PROJECT_KEYS);
    if (typeof project.name !== "string" || project.name.trim() === "") {
      fail(where, `"name" must be a non-empty string`);
    }
    if (!/^[A-Za-z0-9._-]+$/.test(project.name)) {
      fail(where, `"name" must match [A-Za-z0-9._-]+ (it becomes a baseline directory name), got "${project.name}"`);
    }
    if (seenProjects.has(project.name)) fail(where, `duplicate project name "${project.name}"`);
    seenProjects.add(project.name);
    if (project.cwd !== undefined && typeof project.cwd !== "string") fail(where, `"cwd" must be a string`);
    if (project.paths !== undefined) {
      if (!Array.isArray(project.paths) || project.paths.some((p) => typeof p !== "string")) {
        fail(where, `"paths" must be an array of repo-relative path prefixes`);
      }
    }
    if (!Array.isArray(project.gates) || project.gates.length === 0) {
      fail(where, `"gates" must be a non-empty array`);
    }
    const seenIds = new Set();
    const gates = project.gates.map((gate, gi) => {
      const gwhere = `${configPath} projects[${i}].gates[${gi}]`;
      validateGate(gate, gwhere, seenIds);
      return {
        id: gate.id,
        description: gate.description ?? "",
        run: gate.run,
        parser: gate.parser,
        // Default to baseline-aware for every parser that produces keys. That is
        // the whole point of the tool, so it should not need opting in.
        baseline: gate.baseline ?? gate.parser !== "exit-code",
        env: gate.env ?? {},
        timeoutMs: gate.timeoutMs ?? defaultTimeoutMs,
        cwd: gate.cwd ?? null,
        reportFile: gate.reportFile ?? null,
        allowedExitCodes: gate.allowedExitCodes ?? null,
      };
    });
    return {
      name: project.name,
      cwd: project.cwd ?? ".",
      // paths drives --only-changed. Default to the project cwd, which is right
      // for the common monorepo layout of one directory per project.
      paths: project.paths ?? [project.cwd ?? "."],
      gates,
    };
  });

  return {
    configPath,
    baselineDir: parsed.baselineDir ?? DEFAULT_BASELINE_DIR,
    defaultTimeoutMs,
    projects,
  };
}
