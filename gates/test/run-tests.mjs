#!/usr/bin/env node
/**
 * Self-test for the gate runner. Built-ins only: node:test and node:assert.
 *
 *   node gates/test/run-tests.mjs
 *
 * What matters most here is not coverage, it is the two properties the whole
 * tool rests on:
 *   1. Parsers produce STABLE keys. Same broken code, same keys, on any machine.
 *   2. Compare fails on NEW failures and stays quiet about baseline ones.
 * Everything else is a detail. These two are the product.
 */
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  extractJson,
  junitKeysFromXml,
  normalizePath,
  parseEslint,
  parseGoTest,
  parsePytest,
  parseTsc,
  parseVitest,
} from "../src/parsers.mjs";
import { compareToBaseline, readBaseline, writeBaseline } from "../src/baseline.mjs";
import { commandName, isExecutableAvailable, runGate } from "../src/runner.mjs";
import { ConfigError, loadConfig } from "../src/config.mjs";
import { projectTouched } from "../src/git.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const FIX = join(HERE, "fixtures");
const fixture = (name) => readFileSync(join(FIX, name), "utf8");

// The fixtures were captured in a repo rooted at /home/dev/app, so the parser
// context has to match for the path stripping to be exercised.
const CTX = { repoRoot: "/home/dev/app", cwd: "/home/dev/app/frontend" };
const PY_CTX = { repoRoot: "/home/dev/app", cwd: "/home/dev/app/backend" };

const sorted = (set) => [...set].sort();

// ---------------------------------------------------------------- pytest ----

test("pytest: keys are path::test, message tail dropped", () => {
  const { keys } = parsePytest(fixture("pytest-failures.txt"), PY_CTX);
  assert.deepEqual(sorted(keys), [
    "backend/tests/test_auth.py::test_login_rejects_expired_token",
    "backend/tests/test_export.py::test_docx_builder_writes_header",
    "backend/tests/test_meeting.py::TestMeetingList::test_pagination_caps_page_size",
  ]);
});

test("pytest: an ERROR keys the same as a FAILED, so a collection error is not invisible", () => {
  const { keys } = parsePytest("ERROR tests/test_x.py::test_y - fixture missing", PY_CTX);
  assert.deepEqual(sorted(keys), ["backend/tests/test_x.py::test_y"]);
});

test("pytest: a green run yields no keys", () => {
  const { keys } = parsePytest(fixture("pytest-clean.txt"), PY_CTX);
  assert.equal(keys.size, 0);
});

test("pytest: keys do not carry the assertion message, which drifts run to run", () => {
  const a = parsePytest("FAILED tests/t.py::test_x - assert 200 == 401", PY_CTX);
  const b = parsePytest("FAILED tests/t.py::test_x - assert 500 == 401", PY_CTX);
  assert.deepEqual(sorted(a.keys), sorted(b.keys));
});

// ---------------------------------------------------------------- vitest ----

test("vitest: keys are file > full test name, absolute paths stripped", () => {
  const { keys } = parseVitest(fixture("vitest-report.json"), CTX);
  assert.deepEqual(sorted(keys), [
    "frontend/src/__tests__/MeetingPage.test.tsx > MeetingPage > paginates at 100 rows",
    "frontend/src/__tests__/MeetingPage.test.tsx > MeetingPage > renders the summary",
    "frontend/src/hooks/useMeeting.test.ts > [suite failed to run]",
  ]);
});

test("vitest: a suite that fails to load is keyed, not silently dropped", () => {
  const { keys } = parseVitest(fixture("vitest-report.json"), CTX);
  assert.ok([...keys].some((k) => k.endsWith("> [suite failed to run]")));
});

test("vitest: a JSON report buried in warning output still parses", () => {
  const { keys, error } = parseVitest(fixture("vitest-noisy.txt"), CTX);
  assert.equal(error, undefined);
  assert.equal(keys.size, 0);
});

test("vitest: unparsable output is an error, not an empty pass", () => {
  const { error } = parseVitest("Segmentation fault", CTX);
  assert.match(error, /no parsable JSON/);
});

// ------------------------------------------------------------------- tsc ----

test("tsc: keys drop (line,col) so an edit above does not fake a NEW failure", () => {
  const { keys } = parseTsc(fixture("tsc-errors.txt"), CTX);
  assert.deepEqual(sorted(keys), [
    "frontend/src/__tests__/meeting.test.tsx: error TS2554: Expected 2 arguments, but got 1.",
    "frontend/src/pages/MeetingPage.tsx: error TS2339: Property 'summaryText' does not exist on type 'Meeting'.",
    "frontend/src/services/api/apiClient.ts: error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'.",
  ]);
});

test("tsc: the same error moved down 30 lines keeps the same key", () => {
  const a = parseTsc("src/a.ts(10,5): error TS2345: Type mismatch.", CTX);
  const b = parseTsc("src/a.ts(40,9): error TS2345: Type mismatch.", CTX);
  assert.deepEqual(sorted(a.keys), sorted(b.keys));
});

test("tsc: two different errors in one file stay two keys", () => {
  const { keys } = parseTsc(
    "src/a.ts(10,5): error TS2345: Type mismatch.\nsrc/a.ts(11,5): error TS2339: No such property.",
    CTX,
  );
  assert.equal(keys.size, 2);
});

test("tsc: a config-level error is a broken gate, not baseline debt", () => {
  const { error } = parseTsc(fixture("tsc-config-error.txt"), CTX);
  assert.match(error, /TS5083/);
  assert.match(error, /did not run/);
});

test("tsc: a clean run yields no keys and no error", () => {
  const { keys, error } = parseTsc(fixture("tsc-clean.txt"), CTX);
  assert.equal(keys.size, 0);
  assert.equal(error, undefined);
});

// ---------------------------------------------------------------- eslint ----

test("eslint: keys are file + rule, line and column dropped", () => {
  const { keys } = parseEslint(fixture("eslint-report.json"), CTX);
  assert.deepEqual(sorted(keys), [
    "frontend/src/hooks/useMeeting.ts: react-hooks/exhaustive-deps",
    "frontend/src/pages/MeetingPage.tsx: @typescript-eslint/no-explicit-any",
    "frontend/src/pages/MeetingPage.tsx: no-console",
  ]);
});

test("eslint: two violations of one rule in one file collapse to one key", () => {
  // MeetingPage.tsx has two no-console hits in the fixture.
  const { keys } = parseEslint(fixture("eslint-report.json"), CTX);
  assert.equal([...keys].filter((k) => k.endsWith("no-console")).length, 1);
});

test("eslint: warnings count too, since teams run with --max-warnings 0", () => {
  const { keys } = parseEslint(fixture("eslint-report.json"), CTX);
  assert.ok(keys.has("frontend/src/hooks/useMeeting.ts: react-hooks/exhaustive-deps"));
});

// --------------------------------------------------------------- go test ----

test("go-test: keys are Package.TestName, subtests included", () => {
  const { keys } = parseGoTest(fixture("go-test.jsonl"));
  assert.ok(keys.has("example.com/app/auth.TestLoginRejectsExpiredToken"));
  assert.ok(keys.has("example.com/app/meeting.TestPagination/caps_page_size"));
});

test("go-test: a package that failed to build is keyed once", () => {
  const { keys } = parseGoTest(fixture("go-test.jsonl"));
  assert.ok(keys.has("example.com/app/broken.[package failed to build or run]"));
});

test("go-test: a package failing only because its tests failed adds no package key", () => {
  const { keys } = parseGoTest(fixture("go-test.jsonl"));
  assert.ok(!keys.has("example.com/app/auth.[package failed to build or run]"));
});

test("go-test: output with no -json events is an error, not a pass", () => {
  const { error } = parseGoTest("ok  \texample.com/app/auth\t0.01s\n");
  assert.match(error, /-json/);
});

// ------------------------------------------------------------- junit xml ----

test("junit-xml: failures and errors are keyed, skipped is not", () => {
  const keys = junitKeysFromXml(fixture("surefire.xml"));
  assert.deepEqual(keys.sort(), [
    "com.example.billing.InvoiceServiceTest.loadsCurrencyTable",
    "com.example.billing.InvoiceServiceTest.rejectsNegativeAmount",
  ]);
});

test("junit-xml: a self-closing passing testcase is not keyed", () => {
  const keys = junitKeysFromXml(fixture("surefire.xml"));
  assert.ok(!keys.includes("com.example.billing.InvoiceServiceTest.totalsIncludeTax"));
});

// ------------------------------------------------------------- utilities ----

test("normalizePath: absolute paths become repo-relative and posix shaped", () => {
  assert.equal(normalizePath("/home/dev/app/frontend/src/a.ts", CTX), "frontend/src/a.ts");
  assert.equal(normalizePath("src/a.ts", CTX), "frontend/src/a.ts");
});

test("normalizePath: a path outside the repo is left alone rather than becoming ../..", () => {
  assert.equal(normalizePath("/opt/linked-pkg/index.ts", CTX), "/opt/linked-pkg/index.ts");
});

test("extractJson: finds a document embedded in noise", () => {
  const doc = extractJson('warning: something\n{"a":1,"b":[2,3]}\ndone\n');
  assert.deepEqual(doc, { a: 1, b: [2, 3] });
});

test("extractJson: a brace inside a string does not confuse the scanner", () => {
  const doc = extractJson('noise {"msg":"unexpected } here","n":1} tail');
  assert.deepEqual(doc, { msg: "unexpected } here", n: 1 });
});

test("commandName: skips VAR=value prefixes", () => {
  assert.equal(commandName("PYTHONPATH=. python -m pytest"), "python");
  assert.equal(commandName("  go test -json ./...  "), "go");
});

test("isExecutableAvailable: node is present, a made-up binary is not", () => {
  assert.equal(isExecutableAvailable("node", process.cwd()), true);
  assert.equal(isExecutableAvailable("definitely-not-a-real-binary-xyz", process.cwd()), false);
});

// -------------------------------------------------------- baseline logic ----

test("compare: a failure not in the baseline is NEW and fails the run", () => {
  const cmp = compareToBaseline(new Set(["a", "b"]), new Set(["a"]));
  assert.deepEqual(cmp.newFailures, ["b"]);
  assert.deepEqual(cmp.knownFailures, ["a"]);
  assert.deepEqual(cmp.fixedFailures, []);
});

test("compare: a failure that IS in the baseline is known and does not fail the run", () => {
  const cmp = compareToBaseline(new Set(["a", "b"]), new Set(["a", "b"]));
  assert.deepEqual(cmp.newFailures, []);
  assert.deepEqual(cmp.knownFailures, ["a", "b"]);
});

test("compare: a baseline failure that now passes is reported as fixed", () => {
  const cmp = compareToBaseline(new Set(["a"]), new Set(["a", "b"]));
  assert.deepEqual(cmp.fixedFailures, ["b"]);
  assert.deepEqual(cmp.newFailures, []);
});

test("compare: everything green against a non-empty baseline reports every key fixed", () => {
  const cmp = compareToBaseline(new Set(), new Set(["a", "b"]));
  assert.deepEqual(cmp.fixedFailures, ["a", "b"]);
  assert.deepEqual(cmp.newFailures, []);
});

test("compare: no baseline at all means every current failure counts as new", () => {
  const cmp = compareToBaseline(new Set(["a"]), null);
  assert.equal(cmp.hasBaseline, false);
  assert.deepEqual(cmp.newFailures, ["a"]);
});

test("compare: no baseline and nothing failing is fine", () => {
  const cmp = compareToBaseline(new Set(), null);
  assert.equal(cmp.hasBaseline, false);
  assert.deepEqual(cmp.newFailures, []);
});

test("compare: the results are order independent, so key ordering cannot flip a verdict", () => {
  const a = compareToBaseline(new Set(["b", "a", "c"]), new Set(["c", "a"]));
  const b = compareToBaseline(new Set(["c", "b", "a"]), new Set(["a", "c"]));
  assert.deepEqual(a, b);
});

// -------------------------------------------------------- baseline store ----

test("baseline store: round trips, sorted, one key per line", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "p", "g.txt");
    writeBaseline(file, new Set(["zebra", "alpha", "mango"]));
    assert.equal(readFileSync(file, "utf8"), "alpha\nmango\nzebra\n");
    assert.deepEqual([...readBaseline(file)].sort(), ["alpha", "mango", "zebra"]);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("baseline store: an empty baseline is a real file, distinct from a missing one", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "p", "g.txt");
    assert.equal(readBaseline(file), null);
    writeBaseline(file, new Set());
    assert.notEqual(readBaseline(file), null);
    assert.equal(readBaseline(file).size, 0);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("baseline store: blank lines and # comments are ignored on read", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "g.txt");
    writeFileSync(file, "# known debt, see MR !412\n\nalpha\nbeta\n");
    assert.deepEqual([...readBaseline(file)].sort(), ["alpha", "beta"]);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

// ------------------------------------------------------------ config load ---

test("config: the shipped example config is valid and fills in defaults", () => {
  const cfg = loadConfig(resolve(HERE, "..", "gates.config.example.json"));
  assert.equal(cfg.projects.length, 4);
  const backend = cfg.projects.find((p) => p.name === "backend");
  const pytest = backend.gates.find((g) => g.id === "pytest");
  assert.equal(pytest.baseline, true);
  assert.equal(pytest.env.PYTHONPATH, ".");
  // exit-code gates default to baseline off, since they produce no keys.
  assert.equal(backend.gates.find((g) => g.id === "format").baseline, false);
});

test("config: an unknown key is a config error, because it is almost always a typo", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "gates.config.json");
    writeFileSync(
      file,
      JSON.stringify({ projects: [{ name: "p", gates: [{ id: "g", run: "true", parser: "pytest", basline: true }] }] }),
    );
    assert.throws(() => loadConfig(file), (err) => err instanceof ConfigError && /basline/.test(err.message));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("config: exit-code plus baseline true is rejected, since there is nothing to baseline", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "gates.config.json");
    writeFileSync(
      file,
      JSON.stringify({ projects: [{ name: "p", gates: [{ id: "g", run: "true", parser: "exit-code", baseline: true }] }] }),
    );
    assert.throws(() => loadConfig(file), (err) => /no failure keys/.test(err.message));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("config: a gate id that would be an unsafe file name is rejected", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const file = join(dir, "gates.config.json");
    writeFileSync(
      file,
      JSON.stringify({ projects: [{ name: "p", gates: [{ id: "../escape", run: "true", parser: "pytest" }] }] }),
    );
    assert.throws(() => loadConfig(file), (err) => /becomes a baseline file name/.test(err.message));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

// ------------------------------------------------------- cwd resolution ----

test("runGate: a project cwd resolves from the config directory, not the repo root", () => {
  // Regression. These two bases are different whenever the config lives in a
  // subdirectory. Resolving cwd from the repo root ran every gate at the top of
  // the checkout, where node_modules/.bin does not exist, so every JS gate
  // reported "not installed" and SKIPPED. A silent false green.
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const sub = join(dir, "packages", "app");
    mkdirSync(sub, { recursive: true });
    const marker = join(sub, "marker.txt");
    const gate = { run: `node -e "require('fs').writeFileSync('marker.txt','here')"`, env: {}, timeoutMs: 30000, cwd: null };
    // baseDir is the config directory. cwd "." must land in packages/app.
    const r = runGate(gate, { baseDir: join(dir, "packages", "app"), projectCwd: "." });
    assert.equal(r.outcome, "ran", `expected the gate to run, got ${r.outcome}: ${r.reason ?? ""}`);
    assert.equal(readFileSync(marker, "utf8"), "here");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("runGate: a relative project cwd is joined onto the config directory", () => {
  const dir = mkdtempSync(join(tmpdir(), "gates-test-"));
  try {
    const sub = join(dir, "backend");
    mkdirSync(sub, { recursive: true });
    const gate = { run: `node -e "process.stdout.write(process.cwd())"`, env: {}, timeoutMs: 30000, cwd: null };
    const r = runGate(gate, { baseDir: dir, projectCwd: "backend" });
    assert.equal(r.outcome, "ran");
    // realpath, because macOS reports /var as /private/var.
    assert.equal(realpathSync(r.stdout.trim()), realpathSync(sub));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

// -------------------------------------------------------- --only-changed ----

test("projectTouched: a change inside the project's paths selects it", () => {
  const project = { paths: ["backend"] };
  assert.equal(projectTouched(project, ["backend/api/meeting.py"]), true);
  assert.equal(projectTouched(project, ["frontend/src/a.ts"]), false);
});

test("projectTouched: a sibling directory with a shared prefix does not select it", () => {
  // "backend-tools/x" must not match the prefix "backend".
  assert.equal(projectTouched({ paths: ["backend"] }, ["backend-tools/x.py"]), false);
});

test("projectTouched: a project rooted at . always runs", () => {
  assert.equal(projectTouched({ paths: ["."] }, ["anything.md"]), true);
});

test("projectTouched: when git cannot answer, run the project rather than skip it", () => {
  assert.equal(projectTouched({ paths: ["backend"] }, null), true);
});
