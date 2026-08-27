/**
 * Parsers: turn a gate's raw output into a set of stable failure keys.
 *
 * "Stable" is the entire contract, and it is stricter than it looks. A key must
 * be identical across two runs of the same broken code on two machines. So a key
 * never contains:
 *   - an absolute path (differs per checkout, per CI runner)
 *   - a duration or a timestamp
 *   - a line or column number (an unrelated edit above shifts it and fakes a
 *     NEW failure, which is the fastest way to make people stop trusting the gate)
 *   - the assertion message (it carries received values, which drift)
 *   - ordering (we return a Set, the caller sorts)
 *
 * Every parser returns { keys: Set<string>, error?: string }. `error` means the
 * output could not be parsed at all, which is a broken gate, not test debt.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, resolve, sep } from "node:path";

/**
 * Make a path repo-relative and posix-shaped.
 * Keys land in a text file that people diff, so `/` everywhere, always.
 */
export function normalizePath(p, { repoRoot, cwd }) {
  if (!p) return p;
  let out = p.trim();
  // Some tools print `file:line:col`. Strip nothing here, callers do that.
  const abs = out.startsWith("/") || /^[A-Za-z]:[\\/]/.test(out) ? out : resolve(cwd, out);
  let rel = relative(repoRoot, abs);
  // A path outside the repo (a linked package, a temp dir) has no stable
  // repo-relative form. Keep the original so at least it is deterministic.
  if (rel.startsWith("..")) rel = out;
  return rel.split(sep).join("/");
}

/**
 * pytest. Key: `path/to/test_file.py::test_name`.
 *
 * We read the `-rfE` short summary lines, not the noisy body. That needs no
 * plugin and no JSON report file, which keeps the gate command something a
 * teammate already recognises.
 */
export function parsePytest(text, ctx) {
  const keys = new Set();
  for (const line of text.split("\n")) {
    // `FAILED tests/test_x.py::test_y - AssertionError: ...`
    // The ` - message` tail is dropped: it carries received values that drift.
    const m = line.match(/^(?:FAILED|ERROR)\s+(\S+)/);
    if (!m) continue;
    const raw = m[1];
    // Split off the ::test part before normalising the file half.
    const sepIdx = raw.indexOf("::");
    const file = sepIdx === -1 ? raw : raw.slice(0, sepIdx);
    const rest = sepIdx === -1 ? "" : raw.slice(sepIdx);
    keys.add(`${normalizePath(file, ctx)}${rest}`);
  }
  return { keys };
}

/**
 * vitest, JSON reporter. Key: `path/to/file.test.ts > full test name`.
 *
 * A suite that fails to load reports zero assertions, so it would silently look
 * green. We key that case explicitly.
 */
export function parseVitest(text, ctx) {
  const report = extractJson(text);
  if (!report) return { keys: new Set(), error: "vitest produced no parsable JSON report" };
  const keys = new Set();
  for (const suite of report.testResults ?? []) {
    const file = normalizePath(suite.name ?? "<unknown file>", ctx);
    const asserts = suite.assertionResults ?? [];
    if (suite.status === "failed" && asserts.length === 0) {
      keys.add(`${file} > [suite failed to run]`);
      continue;
    }
    for (const a of asserts) {
      if (a.status === "failed") keys.add(`${file} > ${a.fullName ?? a.title}`);
    }
  }
  return { keys };
}

/**
 * tsc --noEmit. Key: `path/to/file.ts: error TS2345: message`.
 *
 * The (line,col) is stripped on purpose. The message stays, because for a type
 * error the message IS the identity. Two different errors on the same file
 * would otherwise collapse into one key and one of them could hide.
 */
export function parseTsc(text, ctx) {
  const keys = new Set();
  const configErrors = [];
  for (const line of text.split("\n")) {
    const m = line.match(/^(.*?)\((\d+),(\d+)\):\s*(error TS\d+:.*)$/);
    if (m) {
      const key = `${normalizePath(m[1], ctx)}: ${m[4].trim()}`;
      keys.add(key);
      continue;
    }
    // Config-level errors have no file position: `error TS5083: Cannot read file`.
    const c = line.match(/^\s*(error TS\d+:.*)$/);
    if (c) configErrors.push(c[1].trim());
  }
  // A broken tsconfig is not baseline debt, it means the gate itself does not
  // run. Snapshotting it would bake a permanently blind gate into the repo.
  if (configErrors.length > 0) {
    return {
      keys,
      error: `tsc reported a project-level error, so the type-check did not run:\n    ${configErrors.join("\n    ")}`,
    };
  }
  return { keys };
}

/**
 * eslint --format json. Key: `path/to/file.ts: rule-id`.
 *
 * Line and column are dropped, so moving code around does not invent NEW
 * failures. One key per file+rule pair means five identical violations in one
 * file collapse to one key, which is what you want in a baseline.
 */
export function parseEslint(text, ctx) {
  const report = extractJson(text);
  if (!Array.isArray(report)) return { keys: new Set(), error: "eslint produced no parsable JSON array" };
  const keys = new Set();
  for (const file of report) {
    const path = normalizePath(file.filePath ?? "<unknown file>", ctx);
    for (const msg of file.messages ?? []) {
      // severity 2 = error, 1 = warning. Both count: teams run with
      // --max-warnings 0 and a warning that lands today is an error tomorrow.
      const rule = msg.ruleId ?? `[fatal] ${String(msg.message ?? "").split("\n")[0]}`;
      keys.add(`${path}: ${rule}`);
    }
  }
  return { keys };
}

/**
 * go test -json. Key: `package/path.TestName`.
 *
 * The stream is one JSON object per line. A line that is not JSON is build
 * output and gets skipped. We take Action "fail" events that name a Test.
 */
export function parseGoTest(text) {
  const keys = new Set();
  let sawEvent = false;
  const buildFailures = new Set();
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("{")) continue;
    let ev;
    try {
      ev = JSON.parse(trimmed);
    } catch {
      continue;
    }
    sawEvent = true;
    if (ev.Action === "fail") {
      if (ev.Test) {
        // Subtests arrive as `TestOuter/sub_case`. Keep them, they are the unit
        // a developer fixes.
        keys.add(`${ev.Package}.${ev.Test}`);
      } else if (ev.Package) {
        // A package-level fail with no test means it did not compile.
        buildFailures.add(ev.Package);
      }
    }
  }
  if (!sawEvent) return { keys, error: "go test produced no -json events (is `-json` in the command?)" };
  // Only report a package-level failure when no individual test in that package
  // failed. Otherwise the package line is just the sum of its tests.
  for (const pkg of buildFailures) {
    const hasTestFailure = [...keys].some((k) => k.startsWith(`${pkg}.`));
    if (!hasTestFailure) keys.add(`${pkg}.[package failed to build or run]`);
  }
  return { keys };
}

/**
 * JUnit XML (Maven surefire, Gradle test, and anything else that emits it).
 * Key: `classname.testname`.
 *
 * Read from files, not stdout. `reportFile` may be one file or a directory,
 * which is how surefire and gradle actually write reports.
 */
export function parseJunitXml(_text, ctx, gate) {
  const target = resolve(ctx.cwd, gate.reportFile);
  const files = collectXmlFiles(target);
  if (files.length === 0) {
    return { keys: new Set(), error: `no JUnit XML reports found at ${gate.reportFile}` };
  }
  const keys = new Set();
  for (const file of files) {
    const xml = readFileSync(file, "utf8");
    for (const key of junitKeysFromXml(xml)) keys.add(key);
  }
  return { keys };
}

/** Extract failing `classname.name` pairs from one JUnit XML document. */
export function junitKeysFromXml(xml) {
  const keys = [];
  // Match each <testcase ...> element with whatever it contains, self-closing
  // or not. A regex is enough here: JUnit XML is machine generated and flat,
  // and a real XML parser would be a dependency we refuse to add.
  const re = /<testcase\b([^>]*?)(\/>|>([\s\S]*?)<\/testcase\s*>)/g;
  let m;
  while ((m = re.exec(xml)) !== null) {
    const attrs = m[1];
    const body = m[3] ?? "";
    // A testcase is failing when it holds a <failure> or an <error>. <skipped>
    // is not a failure.
    if (!/<(failure|error)\b/.test(body)) continue;
    const name = attr(attrs, "name");
    const classname = attr(attrs, "classname");
    if (!name) continue;
    keys.push(classname ? `${classname}.${name}` : name);
  }
  return keys;
}

function attr(attrs, key) {
  const m = attrs.match(new RegExp(`\\b${key}\\s*=\\s*"([^"]*)"`)) ?? attrs.match(new RegExp(`\\b${key}\\s*=\\s*'([^']*)'`));
  return m ? decodeXmlEntities(m[1]) : null;
}

function decodeXmlEntities(s) {
  return s
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&");
}

function collectXmlFiles(target) {
  if (!existsSync(target)) return [];
  const st = statSync(target);
  if (st.isFile()) return [target];
  const out = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, entry.name);
      if (entry.isDirectory()) walk(p);
      else if (entry.isFile() && entry.name.endsWith(".xml")) out.push(p);
    }
  };
  walk(target);
  return out.sort();
}

/**
 * exit-code: the fallback for any tool with no machine-readable output.
 * It produces no keys, so it cannot be baselined. The gate simply passes or
 * fails on the process exit status. Use it for a build, a format check, or a
 * shell script.
 */
export function parseExitCode() {
  return { keys: new Set() };
}

/**
 * Pull a JSON document out of mixed output.
 * Tools print warnings and progress on the same stream as the report, so a
 * plain JSON.parse of the whole text fails. Scan for the first balanced object
 * or array and parse that.
 */
export function extractJson(text) {
  const trimmed = text.trim();
  if (!trimmed) return null;
  try {
    return JSON.parse(trimmed);
  } catch {
    // fall through to scanning
  }
  for (let i = 0; i < trimmed.length; i++) {
    const ch = trimmed[i];
    if (ch !== "{" && ch !== "[") continue;
    const end = findBalancedEnd(trimmed, i);
    if (end === -1) continue;
    try {
      return JSON.parse(trimmed.slice(i, end + 1));
    } catch {
      // Not a real document, keep scanning from the next candidate.
    }
  }
  return null;
}

/** Index of the character closing the bracket at `start`, or -1. String aware. */
function findBalancedEnd(s, start) {
  const open = s[start];
  const close = open === "{" ? "}" : "]";
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let i = start; i < s.length; i++) {
    const c = s[i];
    if (inString) {
      if (escaped) escaped = false;
      else if (c === "\\") escaped = true;
      else if (c === '"') inString = false;
      continue;
    }
    if (c === '"') inString = true;
    else if (c === open) depth++;
    else if (c === close) {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

const PARSERS = {
  pytest: parsePytest,
  vitest: parseVitest,
  tsc: parseTsc,
  eslint: parseEslint,
  "go-test": parseGoTest,
  "junit-xml": parseJunitXml,
  "exit-code": parseExitCode,
};

/**
 * Run the parser named on the gate.
 * `ctx` carries { repoRoot, cwd } so paths can be made repo-relative.
 */
export function parseOutput(gate, text, ctx) {
  const fn = PARSERS[gate.parser];
  if (!fn) return { keys: new Set(), error: `unknown parser "${gate.parser}"` };
  // A gate may point the parser at a report file instead of stdout. That is how
  // vitest and eslint behave when someone passes --outputFile.
  let input = text;
  if (gate.reportFile && gate.parser !== "junit-xml") {
    const p = resolve(ctx.cwd, gate.reportFile);
    if (!existsSync(p)) {
      return { keys: new Set(), error: `reportFile not found after the run: ${gate.reportFile}` };
    }
    input = readFileSync(p, "utf8");
  }
  return fn(input, ctx, gate);
}
