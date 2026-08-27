"""Core model and scanners for the spec helper.

Everything here is stack neutral. It knows about markdown files in a directory
tree and nothing about any language, framework, or database.

A WARNING THAT APPLIES TO HALF THIS FILE
----------------------------------------
The dependency scan, the surface scan, and the lesson miner are HEURISTICS over
freeform markdown. They are regular expressions run against prose a human wrote.
They are hints for an agent or a person to check, never ground truth. Read the
docstring on each function for the exact failure mode it is known to have.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from _yaml import YamlSubsetError, dump_yaml, load_yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DEFAULT_SPECS_DIR = ".claude/specs"


@dataclass(frozen=True)
class Paths:
    """Where every artifact lives. The specs root is configurable."""

    root: Path
    specs: Path
    plan: Path
    impl: Path
    prd: Path
    epics_index: Path
    status_file: Path


def make_paths(root: Path, specs_dir: str = DEFAULT_SPECS_DIR) -> Paths:
    """Build the path set for a project root.

    `root` is the project directory. `specs_dir` is the specs root relative to
    it, or an absolute path. Default is `.claude/specs`.
    """
    specs_path = Path(specs_dir)
    specs = specs_path if specs_path.is_absolute() else root / specs_path
    plan = specs / "plan_artifacts"
    impl = specs / "implementation_artifacts"
    return Paths(
        root=root,
        specs=specs,
        plan=plan,
        impl=impl,
        prd=plan / "prd.md",
        epics_index=plan / "epics.md",
        status_file=impl / "status.yaml",
    )


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

STATUS_VALUES = ("planned", "in_progress", "blocked", "done")
STATUS_MARK = {"planned": "o", "in_progress": "~", "blocked": "x", "done": "*"}


def slugify(title: str) -> str:
    """Kebab-case a title, capped at 50 characters."""
    s = unicodedata.normalize("NFKD", title.lower())
    s = re.sub(r"[^\w\s-]", "", s)
    s = s.strip()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s[:50].rstrip("-")


def pad2(n: int) -> str:
    return str(n).zfill(2)


def natural_key(s: str) -> Tuple[Any, ...]:
    """Sort key where digit runs compare as numbers, so `2.10` follows `2.9`."""
    parts = re.split(r"(\d+)", s.lower())
    return tuple((1, int(p)) if p.isdigit() else (0, p) for p in parts)


def read_text(file: Path) -> str:
    return file.read_text(encoding="utf-8")


def read_title(file: Path) -> Optional[str]:
    """First markdown H1 of a file, or None."""
    if not file.exists():
        return None
    m = re.search(r"^#\s+(.+?)\s*$", read_text(file), re.MULTILINE)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------------------
# Tree discovery
# ---------------------------------------------------------------------------


@dataclass
class StoryNode:
    id: str
    num: int
    title: Optional[str]
    file: Path


@dataclass
class EpicNode:
    id: str
    num: int
    title: Optional[str]
    dir: Path
    epic_file: Path
    stories: List[StoryNode] = field(default_factory=list)


EPIC_RE = re.compile(r"^epic-(\d+)-(.+)$")
STORY_RE = re.compile(r"^story-(\d+)-(.+)\.md$")


def discover_epics(p: Paths) -> List[EpicNode]:
    """Read the plan tree into epic and story nodes, in numeric order."""
    if not p.plan.is_dir():
        return []
    epics: List[EpicNode] = []
    for entry in sorted(x.name for x in p.plan.iterdir()):
        d = p.plan / entry
        m = EPIC_RE.match(entry)
        if not m or not d.is_dir():
            continue
        epic_file = d / "epic.md"
        stories: List[StoryNode] = []
        for f in sorted(x.name for x in d.iterdir()):
            sm = STORY_RE.match(f)
            if not sm:
                continue
            file = d / f
            stories.append(
                StoryNode(
                    id=f[: -len(".md")],
                    num=int(sm.group(1)),
                    title=read_title(file),
                    file=file,
                )
            )
        stories.sort(key=lambda s: s.num)
        epics.append(
            EpicNode(
                id=entry,
                num=int(m.group(1)),
                title=read_title(epic_file),
                dir=d,
                epic_file=epic_file,
                stories=stories,
            )
        )
    epics.sort(key=lambda e: e.num)
    return epics


def dev_story_path(p: Paths, epic: EpicNode, story: StoryNode) -> Path:
    """Mirror a plan story path into implementation_artifacts/."""
    return p.impl / epic.id / f"{story.id}.md"


def previous_story(epic: EpicNode, story: StoryNode) -> Optional[StoryNode]:
    earlier = sorted((s for s in epic.stories if s.num < story.num), key=lambda s: -s.num)
    return earlier[0] if earlier else None


def find_planning_story(
    p: Paths, ref: str
) -> Optional[Tuple[EpicNode, Optional[StoryNode]]]:
    """Resolve a loose reference to an epic and maybe a story.

    Accepts `1.2`, `1-2`, `epic-01-x/story-02-y`, a bare epic id, a bare epic
    number, or a bare story id.
    """
    epics = discover_epics(p)

    parts = ref.split("/") if "/" in ref else ref.split()
    if len(parts) == 2:
        epic = next((e for e in epics if e.id == parts[0]), None)
        if epic:
            wanted = parts[1][:-3] if parts[1].endswith(".md") else parts[1]
            story = next((s for s in epic.stories if s.id in (parts[1], wanted)), None)
            if story:
                return epic, story

    num = re.match(r"^(\d+)[.\-_](\d+)$", ref)
    if num:
        en, sn = int(num.group(1)), int(num.group(2))
        epic = next((e for e in epics if e.num == en), None)
        if not epic:
            return None
        story = next((s for s in epic.stories if s.num == sn), None)
        return (epic, story) if story else (epic, None)

    epic_only = next((e for e in epics if e.id == ref), None)
    if not epic_only and ref.isdigit():
        epic_only = next((e for e in epics if e.num == int(ref)), None)
    if epic_only:
        return epic_only, None

    for epic in epics:
        story = next((s for s in epic.stories if s.id == ref), None)
        if story:
            return epic, story
    return None


# ---------------------------------------------------------------------------
# status.yaml
# ---------------------------------------------------------------------------

STATUS_HEADER = (
    "# status.yaml - implementation status mirror of the plan artifacts.\n"
    "# Regenerate with: python specs.py sync-status\n"
    "# Structure is reconciled from the plan. The `status` values are yours to edit.\n\n"
)


def load_status(p: Paths) -> Optional[Dict[str, Any]]:
    """Read status.yaml, or None when it does not exist or holds no mapping."""
    if not p.status_file.exists():
        return None
    try:
        doc = load_yaml(read_text(p.status_file))
    except YamlSubsetError as err:
        raise SystemExit(f"status.yaml is present but this tool cannot read it: {err}") from err
    if not isinstance(doc, dict):
        return None
    if not isinstance(doc.get("epics"), dict):
        doc["epics"] = {}
    return doc


def dump_status(p: Paths, doc: Dict[str, Any]) -> None:
    p.status_file.parent.mkdir(parents=True, exist_ok=True)
    p.status_file.write_text(STATUS_HEADER + dump_yaml(doc) + "\n", encoding="utf-8")


def status_of(
    prev: Optional[Dict[str, Any]], epic_id: str, story_id: Optional[str] = None
) -> str:
    e = ((prev or {}).get("epics") or {}).get(epic_id)
    if not isinstance(e, dict):
        return "planned"
    if story_id is None:
        own = e.get("status")
        return str(own) if own in STATUS_VALUES else "planned"
    s = (e.get("stories") or {}).get(story_id)
    if isinstance(s, dict) and s.get("status") in STATUS_VALUES:
        return str(s["status"])
    return "planned"


def sync_status(p: Paths) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """Rebuild status.yaml structure from the plan tree, preserving values.

    New items arrive as `planned`. Items whose file or folder is gone are
    dropped. Everything that still exists keeps the status it had, so a hand
    edit is never clobbered.

    THE EXCEPTION THAT MATTERS. An epic entry carrying a `source:` key was
    written by something outside the plan tree, for example a research or
    triage step. It has no plan_artifacts parent by design, so the tree scan
    cannot see it. Such an epic is carried through VERBATIM and is never
    reported as removed.

    An externally sourced epic can also be PARTIALLY on disk. The research step
    records its early stories in implementation_artifacts only, then a later
    planning run writes plan stories for the same epic. The epic then becomes
    visible to the tree scan. Carry-through is therefore NOT conditioned on the
    epic being absent. The tree is merged INTO the preserved entry, never
    substituted for it, so implementation-only stories survive.
    """
    epics = discover_epics(p)
    prev = load_status(p)
    added: List[str] = []
    removed: List[str] = []

    externally_sourced: Dict[str, Any] = {
        epic_id: entry
        for epic_id, entry in ((prev or {}).get("epics") or {}).items()
        if isinstance(entry, dict) and entry.get("source")
    }
    partially_sourced: Set[str] = {
        epic_id for epic_id in externally_sourced if any(x.id == epic_id for x in epics)
    }

    if prev:
        for epic_id, e in (prev.get("epics") or {}).items():
            if epic_id in externally_sourced and epic_id not in partially_sourced:
                continue
            live = next((x for x in epics if x.id == epic_id), None)
            if not live:
                removed.append(epic_id)
                continue
            if not isinstance(e, dict):
                continue
            for story_id in e.get("stories") or {}:
                if not any(s.id == story_id for s in live.stories):
                    # Inside a partially sourced epic, "absent from the tree" is
                    # the normal state of a story that never had a plan parent.
                    if epic_id in partially_sourced:
                        continue
                    removed.append(f"{epic_id}/{story_id}")

    out: Dict[str, Any] = {
        "generated_from": "plan_artifacts (epic-*/ + story-*.md)",
        "note": (
            "Mirror of the plan. Each `status` is preserved across syncs, edit it as you "
            "implement. Values: planned | in_progress | blocked | done. An epic carrying a "
            "`source:` key is externally sourced. It has no plan parent by design, "
            "sync-status carries it through verbatim, and its statuses are edited by hand."
        ),
        "epics": {},
    }

    for epic in epics:
        stories: Dict[str, Any] = {}
        for s in epic.stories:
            prev_epic_entry = ((prev or {}).get("epics") or {}).get(epic.id)
            prev_story = (
                (prev_epic_entry.get("stories") or {}).get(s.id)
                if isinstance(prev_epic_entry, dict)
                else None
            )
            if prev is not None and prev_story is None:
                added.append(f"{epic.id}/{s.id}")
            stories[s.id] = {"title": s.title, "status": status_of(prev, epic.id, s.id)}

        prev_epic = ((prev or {}).get("epics") or {}).get(epic.id)
        if prev is not None and prev_epic is None:
            added.append(epic.id)

        epic_status = status_of(prev, epic.id)
        if prev_epic is None:
            sv = [s["status"] for s in stories.values()]
            if sv and all(v == "done" for v in sv):
                epic_status = "done"
            elif any(v != "planned" for v in sv):
                epic_status = "in_progress"
            else:
                epic_status = "planned"

        if epic.id in partially_sourced:
            preserved = dict(externally_sourced[epic.id])
            merged_stories = dict(preserved.get("stories") or {})
            for story_id, story_entry in stories.items():
                existing = merged_stories.get(story_id)
                merged_stories[story_id] = (
                    {**existing, **story_entry} if isinstance(existing, dict) else story_entry
                )
            preserved["stories"] = merged_stories
            preserved["status"] = status_of(prev, epic.id) or epic_status
            if not preserved.get("title"):
                preserved["title"] = epic.title
            out["epics"][epic.id] = preserved
        else:
            out["epics"][epic.id] = {
                "title": epic.title,
                "status": epic_status,
                "stories": stories,
            }

    for epic_id, entry in externally_sourced.items():
        if epic_id not in partially_sourced:
            out["epics"][epic_id] = entry

    p.impl.mkdir(parents=True, exist_ok=True)
    dump_status(p, out)
    return out, added, removed


@dataclass
class FlatEntry:
    epic: EpicNode
    story: StoryNode
    status: str


def flat_status(p: Paths) -> List[FlatEntry]:
    """Flatten the tree plus status.yaml into one ordered list."""
    epics = discover_epics(p)
    status = load_status(p)
    return [
        FlatEntry(epic=e, story=s, status=status_of(status, e.id, s.id))
        for e in epics
        for s in e.stories
    ]


# ---------------------------------------------------------------------------
# Requirements and coverage
# ---------------------------------------------------------------------------

# A feature id may contain DIGITS after the first letter, for example `F-A11Y`.
# Every scanner in this file uses this one pattern. If you change it, change it
# here only, so the scanners cannot drift apart.
FEATURE_RE = re.compile(r"\bF-[A-Z][A-Z0-9-]*[A-Z0-9]\b")
FLOW_RE = re.compile(r"\bFLOW\s+\d+\b")
DECISION_RE = re.compile(r"\bD\d{1,2}\b")
MODULE_RE = re.compile(r"\bM\d{1,2}(?:-[A-Z]+)?\b")


def extract_reqs(prd_text: str) -> Dict[str, List[str]]:
    """Pull requirement ids out of the PRD text.

    Features `F-*` are the primary unit. Flows, decisions and modules are
    surfaced as extra cross-reference dimensions.
    """

    def uniq_sorted(items: Iterable[str]) -> List[str]:
        return sorted(set(items), key=natural_key)

    return {
        "features": uniq_sorted(FEATURE_RE.findall(prd_text)),
        "flows": uniq_sorted(re.sub(r"\s+", " ", m) for m in FLOW_RE.findall(prd_text)),
        "decisions": uniq_sorted(DECISION_RE.findall(prd_text)),
        "modules": uniq_sorted(MODULE_RE.findall(prd_text)),
    }


def epic_covered_ids(epic: EpicNode) -> Set[str]:
    """Requirement ids an epic claims, read from epic.md plus its story files."""
    ids: Set[str] = set()

    def scan(text: str) -> None:
        ids.update(FEATURE_RE.findall(text))
        ids.update(re.sub(r"\s+", " ", m) for m in FLOW_RE.findall(text))

    if epic.epic_file.exists():
        scan(read_text(epic.epic_file))
    for s in epic.stories:
        if s.file.exists():
            scan(read_text(s.file))
    return ids


def compute_coverage(p: Paths) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Map each PRD feature to the epics that name it.

    This is a tautology check. It answers "is every declared feature mapped to
    an epic", never "did the PRD ask for the right things".
    """
    if not p.prd.exists():
        raise SystemExit(f"PRD not found at {p.prd}")
    features = extract_reqs(read_text(p.prd))["features"]
    epics = discover_epics(p)
    epic_ids = [(e.id, epic_covered_ids(e)) for e in epics]
    rows = [
        {"feature": f, "epics": [eid for eid, ids in epic_ids if f in ids]} for f in features
    ]
    uncovered = [r["feature"] for r in rows if not r["epics"]]
    return rows, uncovered


# ---------------------------------------------------------------------------
# Dependency scanning. HEURISTIC. Read the warnings.
# ---------------------------------------------------------------------------

DEP_KEYWORD_RE = re.compile(
    r"(depends?\s+on|carry[- ]over|inherit(?:ed|s)?\s+from|blocked\s+by"
    r"|prereq(?:uisite)?s?|after\s+story|hardens)",
    re.IGNORECASE,
)

# The clause boundary is a SENTENCE boundary, not just `;` or a newline.
# A "." ends the clause only when whitespace and a capital follow it, or when it
# ends the text. A ref's own decimal point in `2.3` therefore never trips it.
# `;` and a newline always end the clause.
CLAUSE_BOUNDARY_RE = re.compile(r"\.(?=\s+[A-Z]|\s*$)|[;\n]")

# The negation tail MUST allow ".". A ref's own decimal point sits inside the
# negating tail of "independent of 2.1/2.3", and a tail class that excludes "."
# stops at that first decimal point, which turns this whole check into dead code.
NEGATING_RE = re.compile(
    r"(independent\s+of|not\s+depend(?:ent|s)?\s+(?:on|of))[^;\n]*$", re.IGNORECASE
)

# A real story ref is `N.M` with no third segment and no digit, dot or dash
# glued to either end. That excludes a date like `2026-07-07` and a version
# like `1.49.0`.
STORY_REF_RE = re.compile(r"(?<![.\d-])\b(\d{1,3})[.\-_](\d{1,3})\b(?![.\-_]?\d)")

MAX_EPIC_NUM = 100


def _dep_clauses(text: str) -> List[Tuple[str, Optional[re.Match]]]:
    """Every dependency clause in the text, with its negating tail if any.

    A clause starts right after a dependency keyword and runs to the next
    sentence boundary, `;`, or newline. Nothing past that boundary belongs to
    the clause. A later `;`-separated clause names a DIFFERENT relationship, and
    a later "Independent of X, Y." sentence on the same physical line names the
    inverse one.
    """
    out: List[Tuple[str, Optional[re.Match]]] = []
    for kw in DEP_KEYWORD_RE.finditer(text):
        rest = text[kw.end() :]
        boundary = CLAUSE_BOUNDARY_RE.search(rest)
        clause = rest if boundary is None else rest[: boundary.start()]
        out.append((clause, NEGATING_RE.search(clause)))
    return out


def explicitly_depends_on(file: Path, epic_num: int, story_num: int) -> bool:
    """Does this file name story `N.M` inside a dependency clause?

    HEURISTIC. It reads prose. A phrasing outside DEP_KEYWORD_RE defeats it.
    """
    if not file.exists():
        return False
    text = read_text(file)
    ref_re = re.compile(r"\b%d[.\-_]%d\b" % (epic_num, story_num))
    for clause, neg in _dep_clauses(text):
        if not ref_re.search(clause):
            continue
        if neg and ref_re.search(neg.group(0)):
            continue  # the ref sits inside the negating tail
        return True
    return False


def explicit_deps_of(file: Path) -> List[Tuple[int, int]]:
    """Collect EVERY `N.M` ref named after a dependency keyword.

    THIS MUST BE A COLLECTING SCAN, NOT A FIRST-MATCH SCAN. A single keyword
    plus ref `finditer` yields only the first ref, so a line reading
    `depends on stories 2.1 (registry), 2.2 (surface), 2.3 (defense)` silently
    drops two thirds of its own meaning. The correct shape, used here: find each
    keyword, cut the clause at its sentence boundary, then scan that clause with
    a separate global ref regex.

    Refs sitting in a trailing negating tail are rejected. Look-alikes with a
    year-sized first segment are rejected.
    """
    res: List[Tuple[int, int]] = []
    if not file.exists():
        return res
    for clause, neg in _dep_clauses(read_text(file)):
        for m in STORY_REF_RE.finditer(clause):
            e = int(m.group(1))
            if e < 1 or e > MAX_EPIC_NUM:
                continue
            if neg and m.start() >= neg.start():
                continue
            res.append((e, int(m.group(2))))
    return res


# Tokens that appear backticked in nearly every story, so a shared match between
# two stories says nothing about them touching the same real surface. Extend
# this set with your own project's ubiquitous names as they show up.
GENERIC_SURFACE_TOKENS = {
    "user_id",
    "tenant_id",
    "org_id",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
}

NON_SURFACE_TOKENS_RE = re.compile(r"^(uv|uvx|pip|npm|src|app|api|lib|tests?)$")
SURFACE_TOKEN_RE = re.compile(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`")


def story_codes(file: Path) -> Set[str]:
    """Feature and flow codes a story names, meaning its declared surface."""
    ids: Set[str] = set()
    if not file.exists():
        return ids
    text = read_text(file)
    ids.update(FEATURE_RE.findall(text))
    ids.update(re.sub(r"\s+", " ", m) for m in FLOW_RE.findall(text))
    return ids


def story_surfaces(file: Path) -> Set[str]:
    """Backticked snake_case names a story mentions, as a shared-surface hint.

    Stack neutral on purpose. A snake_case token in backticks might be a table,
    a column, a config key, a fixture, or an env var. The command that uses this
    only claims two stories mention the same name, nothing more.
    """
    surfaces: Set[str] = set()
    if not file.exists():
        return surfaces
    for m in SURFACE_TOKEN_RE.finditer(read_text(file)):
        ident = m.group(1)
        if NON_SURFACE_TOKENS_RE.match(ident) or ident in GENERIC_SURFACE_TOKENS:
            continue
        surfaces.add(ident)
    return surfaces


def compute_dependents(
    p: Paths, epic: EpicNode, story: StoryNode
) -> List[Dict[str, Any]]:
    """Later stories that name this one, or that share its codes or surfaces.

    Forward only. A story never feeds back into one that comes before it.
    HEURISTIC, see the module docstring.
    """
    status = load_status(p)
    epics = discover_epics(p)
    my_codes = story_codes(story.file)
    my_surfaces = story_surfaces(story.file)
    out: List[Dict[str, Any]] = []

    for e in epics:
        for s in e.stories:
            is_later = e.num > epic.num or (e.num == epic.num and s.num > story.num)
            if not is_later:
                continue

            reasons: List[str] = []
            if explicitly_depends_on(s.file, epic.num, story.num):
                reasons.append("explicit-depends-on")

            shared_codes = sorted(my_codes & story_codes(s.file), key=natural_key)
            if shared_codes:
                reasons.append("shared-code(%s)" % ",".join(shared_codes))

            shared_surfaces = sorted(my_surfaces & story_surfaces(s.file), key=natural_key)
            if shared_surfaces:
                reasons.append("shared-surface(%s)" % ",".join(shared_surfaces[:4]))

            if not reasons:
                continue

            dev = dev_story_path(p, e, s)
            out.append(
                {
                    "ref": f"{e.num}.{s.num}",
                    "epic": e.id,
                    "story": s.id,
                    "title": s.title,
                    "status": status_of(status, e.id, s.id),
                    "planFile": str(s.file),
                    "devStoryFile": str(dev),
                    "devStoryExists": dev.exists(),
                    "reason": "; ".join(reasons),
                    "sharedCodes": shared_codes,
                    "sharedSurfaces": shared_surfaces,
                }
            )

    def sort_key(d: Dict[str, Any]) -> Tuple[Any, ...]:
        explicit = 0 if "explicit" in d["reason"] else 1
        richness = -(len(d["sharedCodes"]) + len(d["sharedSurfaces"]))
        return (explicit, richness, natural_key(d["ref"]))

    out.sort(key=sort_key)
    return out


# ---------------------------------------------------------------------------
# Lessons. Mine the `## Dev agent record` of shipped stories.
# ---------------------------------------------------------------------------

DEV_RECORD_HEADING = "## Dev agent record"

# A hazard is a lesson that COST someone something, or a rule that generalizes
# past its own story.
#
# KEEP THIS NARROW. An early draft matched a bare warning sign and the word
# "bug", so it flagged every scanned item. A signal that fires on everything
# carries no information. Every clause below names a cost or a generalization,
# never merely a topic.
HAZARD_RE = re.compile(
    "|".join(
        [
            # it shipped past the tests
            r"green suite|still green|passing tests|tests? (?:stayed|were|all) green",
            # it hides
            r"silently|false[- ]positiv|footgun|gotcha|trap\b",
            # it recurs
            r"generali[sz]es|any \w+ (?:over|with)|this class of|the same shape",
            # it already cost someone
            r"the bug (?:a|that)|missed by|caught by the live|bit us|cost (?:us|me)",
        ]
    ),
    re.IGNORECASE,
)

MIN_LESSON_CHARS = 60


def extract_record(dev_file: Path) -> List[str]:
    """Split a `## Dev agent record` section into bullets and bold lead lines.

    Items shorter than MIN_LESSON_CHARS are dropped as noise, for example a bare
    model-name line.
    """
    if not dev_file.exists():
        return []
    text = read_text(dev_file)
    m = re.search(r"^%s\s*$" % re.escape(DEV_RECORD_HEADING), text, re.MULTILINE)
    if not m:
        return []
    rest = text[m.start() :]
    next_h2 = re.search(r"^## ", rest[3:], re.MULTILINE)
    section = rest if next_h2 is None else rest[: next_h2.start() + 3]

    out: List[str] = []
    buf: List[str] = []

    def flush() -> None:
        s = re.sub(r"\s+", " ", " ".join(buf)).strip()
        if len(s) >= MIN_LESSON_CHARS:
            out.append(s)
        buf.clear()

    for line in section.split("\n"):
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+", line):
            flush()
            buf.append(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line))
        elif buf and re.match(r"^\s+\S", line):
            buf.append(line.strip())
        elif re.match(r"^\*\*.+\*\*", line.strip()):
            flush()
            buf.append(line.strip())
        else:
            flush()
    flush()
    return out


def rank_lessons(lessons: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Pick `limit` lessons, diverse across stories, hazards first.

    RANKING WITHOUT DIVERSITY LETS ONE STORY EAT THE BUDGET. Sorting the flat
    list and slicing it means one verbose story fills every slot and buries all
    the others. So round-robin across stories FIRST, taking one item per story
    per pass, then sort hazards to the top of that diverse set.
    """
    by_story: Dict[str, List[Dict[str, Any]]] = {}
    for lesson in lessons:
        by_story.setdefault(lesson["ref"], []).append(lesson)
    for bucket in by_story.values():
        bucket.sort(key=lambda x: not x["hazard"])  # best first within a story

    shown: List[Dict[str, Any]] = []
    round_i = 0
    while len(shown) < limit:
        placed = False
        for bucket in by_story.values():
            if round_i >= len(bucket):
                continue
            shown.append(bucket[round_i])
            placed = True
            if len(shown) >= limit:
                break
        if not placed:
            break
        round_i += 1

    shown.sort(key=lambda x: not x["hazard"])
    return shown


# ---------------------------------------------------------------------------
# stale-refs. Names the plan promises that the code does not define.
# ---------------------------------------------------------------------------

# A backticked identifier, with an OPTIONAL and ARBITRARY argument list.
#
# THE ARGUMENT LIST MUST BE ARBITRARY. A pattern that only tolerates empty
# parens, `\(?\)?`, matches nothing for every backticked call written with real
# arguments, so those names are silently never checked. That is under
# collection: the tool reports clean for identifiers it never even looked at.
# `[^`(]*` stops the args from swallowing a closing backtick or a second call on
# the same line.
IDENT_RE = re.compile(r"`([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)?)(?:\([^`(]*\))?`")

# Only these sections make FORWARD-LOOKING claims about code that must exist.
# A dev record or an evidence section quotes the past on purpose.
#
# These are PREFIX matches, not whole-word matches. "Dependencies" does not
# match a `\bdepend\b` pattern, and that exact miss made an early draft skip the
# one section where the drift actually lived.
FORWARD_HEADING_RE = re.compile(
    r"^#{1,4}\s+.*\b("
    r"depend|gate|inherit|architect|stack|files to|story|stories|"
    r"task|acceptance|guardrail|invariant|data|schema|goal|scope|context|interface|contract"
    r")",
    re.I,
)
HISTORICAL_HEADING_RE = re.compile(
    r"^#{1,4}\s+.*\b(dev agent record|completion notes|debug log|evidence|"
    r"previous-story carry-over|carry-over|references|open questions|changelog)\b",
    re.I,
)

IDENT_STOPWORDS = frozenset(
    {
        "None", "True", "False", "null", "true", "false", "str", "int", "bool",
        "float", "dict", "list", "set", "tuple", "type", "id", "name", "value",
        "self", "cls", "Any", "Optional", "Literal", "json", "yaml", "yes", "no",
        "main", "app", "test", "tests", "TODO", "src", "lib", "build", "dist",
    }
)

# Default source suffixes to harvest identifiers from. Stack neutral: this list
# covers the common ones and is overridable on the command line.
DEFAULT_CODE_SUFFIXES = (
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rb", ".rs",
    ".java", ".kt", ".cs", ".php", ".swift", ".scala", ".sql", ".c", ".h",
    ".cc", ".cpp", ".hpp",
)

SKIP_DIR_PARTS = {
    "node_modules", "__pycache__", ".venv", "venv", ".git", "dist", "build",
    "target", "vendor", "coverage", ".mypy_cache", ".pytest_cache", ".tox",
}

# Over-collect on purpose. This command exists to catch a name that appears
# NOWHERE in the code. A missed drift costs nothing. A false positive on a
# perfectly good name teaches the reader to ignore the whole output.
_HARVEST_PATTERNS = [
    re.compile(r"\b(?:def|class|func|fn|type|interface|enum|struct|trait)\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"\b(?:const|let|var|val)\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*(?::[^=\n]+)?=", re.M),
    re.compile(r"\.([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"['\"`]([A-Za-z_][A-Za-z0-9_-]{2,})['\"`]"),
    re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*[?]?:", re.M),
    re.compile(r"<([A-Z][A-Za-z0-9_]*)[\s/>]"),
    re.compile(r"\b(?:import|from|require)\s+([A-Za-z_$][A-Za-z0-9_$.]*)"),
    re.compile(r"[{,]\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*[},:]"),
]


def harvest_identifiers(
    root: Path, code_dirs: List[str], suffixes: Tuple[str, ...] = DEFAULT_CODE_SUFFIXES
) -> Set[str]:
    """Every name defined, assigned, accessed, or quoted in the code directories."""
    names: Set[str] = set()
    dirs = [root / d for d in code_dirs] if code_dirs else [root]
    for d in dirs:
        if not d.is_dir():
            continue
        for src_file in d.rglob("*"):
            if not src_file.is_file():
                continue
            if SKIP_DIR_PARTS & set(src_file.parts):
                continue
            if src_file.suffix not in suffixes:
                continue
            try:
                src = src_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat in _HARVEST_PATTERNS:
                for hit in pat.findall(src):
                    if "," in hit or " as " in hit:
                        for part in hit.split(","):
                            leaf = part.strip().split(" as ")[-1].split(":")[0].strip()
                            if leaf:
                                names.add(leaf)
                        continue
                    names.add(hit)
                    if "." in hit:
                        names.update(hit.split("."))
    return names


def forward_looking_lines(text: str) -> List[Tuple[int, str]]:
    """Lines under a forward-looking heading, skipping historical sections."""
    out: List[Tuple[int, str]] = []
    forward = True  # prose before the first heading counts as forward looking
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            if HISTORICAL_HEADING_RE.match(stripped):
                forward = False
            elif FORWARD_HEADING_RE.match(stripped):
                forward = True
            elif stripped.startswith("## "):
                forward = False  # an unrecognized top-level section, stay quiet
            continue
        if forward:
            out.append((i, line))
    return out
