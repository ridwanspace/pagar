#!/usr/bin/env python3
"""specs.py - the single interface to a project's spec artifacts.

Planning skills and dev agents call this instead of loading every PRD, epic and
story file into their context. It reads and writes the on-disk spec layout and
keeps the implementation status mirror in sync.

Stack neutral. It knows about markdown files in a directory tree and nothing
about your language, framework, or database.

LAYOUT, relative to the project root. The specs root is configurable with
`--specs-dir`, default `.claude/specs`.

    .claude/specs/
      plan_artifacts/               source of record, written by planning
        prd.md
        epics.md
        epic-NN-<slug>/
          epic.md
          story-NN-<slug>.md
      implementation_artifacts/     what was actually built
        status.yaml                 ref -> planned|in_progress|blocked|done
        epic-NN-<slug>/
          story-NN-<slug>.md        holds a "## Dev agent record" section

HEURISTICS, READ THIS
---------------------
`deps`, `feed-forward`, `suggest-next` and `lessons` are regular expressions run
over freeform markdown prose. They are not a real dependency graph and they are
not a parser. Every verdict they give is a HINT TO VERIFY, never ground truth. A
phrasing outside the recognized keywords defeats them silently. When one says a
story is ready, check the story's own prose before you believe it.

`sync-status` and `set-status` are the only commands that write. Everything else
is read only.

Python 3.9 or newer. Standard library only, no third-party imports.
"""

from __future__ import annotations

import argparse
import json as jsonlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _core import (  # noqa: E402
    DEFAULT_SPECS_DIR,
    STATUS_MARK,
    STATUS_VALUES,
    FlatEntry,
    Paths,
    compute_coverage,
    compute_dependents,
    dev_story_path,
    discover_epics,
    dump_status,
    explicit_deps_of,
    extract_record,
    extract_reqs,
    find_planning_story,
    flat_status,
    forward_looking_lines,
    harvest_identifiers,
    load_status,
    make_paths,
    natural_key,
    pad2,
    previous_story,
    rank_lessons,
    read_text,
    slugify,
    status_of,
    story_codes,
    story_surfaces,
    sync_status,
    HAZARD_RE,
    IDENT_RE,
    IDENT_STOPWORDS,
)

HEURISTIC_CAVEAT = (
    "  note: this is a regex scan over freeform markdown, not a dependency graph. "
    "Verify before you act on it."
)


# ---------------------------------------------------------------------------
# Output helpers. Command output goes to stdout, diagnostics go to stderr.
# ---------------------------------------------------------------------------


def emit(s: str = "") -> None:
    print(s)


def emit_json(data: Any) -> None:
    print(jsonlib.dumps(data, indent=2, ensure_ascii=False))


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------------------
# Planning layer
# ---------------------------------------------------------------------------


def cmd_list(p: Paths, as_json: bool) -> None:
    epics = discover_epics(p)
    status = load_status(p)
    if as_json:
        emit_json(
            [
                {
                    "id": e.id,
                    "title": e.title,
                    "status": status_of(status, e.id),
                    "epicFileExists": e.epic_file.exists(),
                    "stories": [
                        {
                            "id": s.id,
                            "title": s.title,
                            "status": status_of(status, e.id, s.id),
                        }
                        for s in e.stories
                    ],
                }
                for e in epics
            ]
        )
        return
    if not epics:
        emit(f"(no epics yet, nothing matches {p.plan}/epic-*/)")
        return
    for e in epics:
        st = status_of(status, e.id)
        missing = "" if e.epic_file.exists() else "   [!] no epic.md"
        emit(f"{STATUS_MARK[st]} {e.id}  -  {e.title or '(untitled)'}  [{st}]{missing}")
        for s in e.stories:
            ss = status_of(status, e.id, s.id)
            emit(f"    {STATUS_MARK[ss]} {s.id}  -  {s.title or '(untitled)'}  [{ss}]")
        if not e.stories:
            emit("    (no stories yet)")


def cmd_show(p: Paths, epic_arg: str, story_arg: Optional[str]) -> None:
    d = p.plan / epic_arg
    if not d.is_dir():
        die(f"epic not found: {epic_arg} (looked in {d})")
    if story_arg:
        file = d / (story_arg if story_arg.endswith(".md") else f"{story_arg}.md")
    else:
        file = d / "epic.md"
    if not file.exists():
        die(f"file not found: {file}")
    sys.stdout.write(read_text(file))


def cmd_reqs(p: Paths, as_json: bool) -> None:
    if not p.prd.exists():
        die(f"PRD not found at {p.prd}")
    reqs = extract_reqs(read_text(p.prd))
    if as_json:
        emit_json(reqs)
        return
    emit(f"Features (F-*, the primary requirement unit): {len(reqs['features'])}")
    emit("  " + (", ".join(reqs["features"]) or "(none)"))
    emit(f"\nFlows: {len(reqs['flows'])}")
    emit("  " + (", ".join(reqs["flows"]) or "(none)"))
    emit(f"\nDecisions: {len(reqs['decisions'])}")
    emit("  " + (", ".join(reqs["decisions"]) or "(none)"))
    emit(f"\nModules: {len(reqs['modules'])}")
    emit("  " + (", ".join(reqs["modules"]) or "(none)"))


def cmd_coverage(p: Paths, as_json: bool) -> None:
    if not p.prd.exists():
        die(f"PRD not found at {p.prd}. Write the PRD first.")
    rows, uncovered = compute_coverage(p)
    if as_json:
        emit_json({"rows": rows, "uncovered": uncovered})
        return
    emit("Requirement coverage (F-* -> epic):\n")
    for r in rows:
        where = ", ".join(r["epics"]) if r["epics"] else "-- UNCOVERED --"
        emit(f"  {r['feature']:<18} {where}")
    emit(f"\n{len(rows) - len(uncovered)}/{len(rows)} features covered.")
    if uncovered:
        emit(f"UNCOVERED ({len(uncovered)}): {', '.join(uncovered)}")
    emit(
        "\n  note: this checks that every declared feature maps to an epic. "
        "It cannot tell you whether the PRD declared the right features."
    )


def cmd_sync_status(p: Paths) -> None:
    doc, added, removed = sync_status(p)
    n_epics = len(doc["epics"])
    n_stories = sum(len(e.get("stories") or {}) for e in doc["epics"].values())
    emit(f"status.yaml synced -> {p.status_file}")
    emit(f"  {n_epics} epic(s), {n_stories} story(ies).")
    carried = [k for k, v in doc["epics"].items() if isinstance(v, dict) and v.get("source")]
    if carried:
        emit(f"  ~ carried through (externally sourced, no plan parent): {', '.join(carried)}")
    if added:
        emit(f"  + added (status=planned): {', '.join(added)}")
    if removed:
        emit(f"  - removed (no longer on disk): {', '.join(removed)}")
    if not added and not removed:
        emit("  structure unchanged, existing status values preserved.")


def cmd_next_id(p: Paths, epic_arg: Optional[str], as_json: bool) -> None:
    epics = discover_epics(p)
    if not epic_arg:
        nxt = (epics[-1].num if epics else 0) + 1
        out = {"kind": "epic", "num": nxt, "padded": pad2(nxt), "prefix": f"epic-{pad2(nxt)}-"}
        emit_json(out) if as_json else emit(f"{out['prefix']}<slug>  (epic #{nxt})")
        return
    epic = next((e for e in epics if e.id == epic_arg), None)
    if not epic:
        die(f"epic not found: {epic_arg}")
    nxt = (epic.stories[-1].num if epic.stories else 0) + 1
    out = {
        "kind": "story",
        "epic": epic.id,
        "num": nxt,
        "padded": pad2(nxt),
        "prefix": f"story-{pad2(nxt)}-",
    }
    emit_json(out) if as_json else emit(f"{out['prefix']}<slug>  (story #{nxt} in {epic.id})")


# ---------------------------------------------------------------------------
# Dev-story layer
# ---------------------------------------------------------------------------


def _entry_payload(p: Paths, x: FlatEntry) -> Dict[str, Any]:
    dev = dev_story_path(p, x.epic, x.story)
    return {
        "ref": f"{x.epic.num}.{x.story.num}",
        "epic": x.epic.id,
        "story": x.story.id,
        "title": x.story.title,
        "status": x.status,
        "planFile": str(x.story.file),
        "devStoryFile": str(dev),
        "devStoryExists": dev.exists(),
    }


def cmd_next_story(p: Paths, as_json: bool) -> None:
    planned = next((x for x in flat_status(p) if x.status == "planned"), None)
    if not planned:
        emit_json({"found": False}) if as_json else emit(
            "No `planned` story left. Every story is in_progress, blocked, or done."
        )
        return
    out = {"found": True, **_entry_payload(p, planned)}
    if as_json:
        emit_json(out)
        return
    emit(f"Next planned story: {out['ref']} - {out['title'] or '(untitled)'}")
    emit(f"  plan source:      {out['planFile']}")
    exists = "  (already exists)" if out["devStoryExists"] else ""
    emit(f"  dev story output: {out['devStoryFile']}{exists}")


def cmd_next_dev(p: Paths, as_json: bool) -> None:
    """Next story to implement: it has a dev story file and is not done."""
    with_dev = [
        x
        for x in flat_status(p)
        if x.status != "done" and dev_story_path(p, x.epic, x.story).exists()
    ]
    pick = (
        next((x for x in with_dev if x.status == "in_progress"), None)
        or next((x for x in with_dev if x.status == "blocked"), None)
        or (with_dev[0] if with_dev else None)
    )
    if not pick:
        emit_json({"found": False}) if as_json else emit(
            "No dev story to implement. Every dev story is done, or none exist yet."
        )
        return
    out = {"found": True, **_entry_payload(p, pick)}
    if as_json:
        emit_json(out)
        return
    emit(f"Next dev story: {out['ref']} - {out['title'] or '(untitled)'}  [{out['status']}]")
    emit(f"  dev story: {out['devStoryFile']}")
    emit(f"  plan:      {out['planFile']}")


def cmd_story_info(p: Paths, ref: str, as_json: bool) -> None:
    hit = find_planning_story(p, ref)
    if not hit or hit[1] is None:
        extra = f" (matched epic {hit[0].id}, but no such story)" if hit else ""
        die(f'no plan story matched "{ref}"{extra}. Run `list` to see what exists.')
    epic, story = hit[0], hit[1]
    status = load_status(p)
    prev = previous_story(epic, story)
    dev = dev_story_path(p, epic, story)
    prev_dev = dev_story_path(p, epic, prev) if prev else None
    out: Dict[str, Any] = {
        "ref": f"{epic.num}.{story.num}",
        "epic": {
            "id": epic.id,
            "num": epic.num,
            "title": epic.title,
            "file": str(epic.epic_file),
        },
        "story": {
            "id": story.id,
            "num": story.num,
            "title": story.title,
            "status": status_of(status, epic.id, story.id),
        },
        "planFile": str(story.file),
        "devStoryFile": str(dev),
        "devStoryExists": dev.exists(),
        "previousStory": (
            {
                "id": prev.id,
                "ref": f"{epic.num}.{prev.num}",
                "planFile": str(prev.file),
                "devStoryFile": str(prev_dev) if prev_dev else None,
                "devStoryExists": prev_dev.exists() if prev_dev else False,
                "status": status_of(status, epic.id, prev.id),
            }
            if prev
            else None
        ),
    }
    if as_json:
        emit_json(out)
        return
    emit(f"Story {out['ref']}: {story.title or '(untitled)'}  [{out['story']['status']}]")
    emit(f"  epic:        {epic.id} - {epic.title or ''}")
    emit(f"  plan source: {out['planFile']}")
    exists = "  (EXISTS)" if out["devStoryExists"] else "  (not yet created)"
    emit(f"  dev story:   {out['devStoryFile']}{exists}")
    ps = out["previousStory"]
    if ps:
        dev_note = ps["devStoryFile"] if ps["devStoryExists"] else "(none)"
        emit(f"  previous:    {ps['ref']} [{ps['status']}] dev={dev_note}")
    else:
        emit("  previous:    (this is the first story in the epic)")


def cmd_dev_list(p: Paths, as_json: bool) -> None:
    rows = [_entry_payload(p, x) for x in flat_status(p)]
    if as_json:
        emit_json(rows)
        return
    made = [r for r in rows if r["devStoryExists"]]
    if not made:
        emit(f"(no dev stories yet under {p.impl}/epic-*/)")
        return
    for r in made:
        emit(f"  {r['ref']}  [{r['status']}]  {r['devStoryFile']}")
    emit(f"\n{len(made)}/{len(rows)} plan stories have a dev story.")


def cmd_set_status(p: Paths, ref: str, value: str) -> None:
    if value not in STATUS_VALUES:
        die(f'invalid status "{value}". Use one of: {", ".join(STATUS_VALUES)}', 2)
    if not p.status_file.exists():
        sync_status(p)
    doc = load_status(p)
    if not doc:
        die("could not load status.yaml even after a sync")
    hit = find_planning_story(p, ref)
    if not hit:
        die(f'no epic or story matched "{ref}"')
    epic, story = hit[0], hit[1]
    epic_entry = doc["epics"].get(epic.id)
    if not isinstance(epic_entry, dict):
        die(f"epic {epic.id} is not in status.yaml. Run `sync-status` first.")
    if story is None:
        epic_entry["status"] = value
        emit(f"{epic.id} -> {value}")
    else:
        se = (epic_entry.get("stories") or {}).get(story.id)
        if not isinstance(se, dict):
            die(f"story {story.id} is not in status.yaml. Run `sync-status` first.")
        se["status"] = value
        emit(f"{epic.id}/{story.id} -> {value}")
        if value != "planned" and epic_entry.get("status") == "planned":
            epic_entry["status"] = "in_progress"
            emit(f"{epic.id} -> in_progress (auto, the first story moved off planned)")
    dump_status(p, doc)


# ---------------------------------------------------------------------------
# Feed-forward layer
# ---------------------------------------------------------------------------


def cmd_deps(p: Paths, ref: str, as_json: bool) -> None:
    """List later stories that name this one, or share its codes or surfaces.

    HEURISTIC. It is a regex scan over freeform markdown, not a dependency
    graph. Treat every row as a hint to verify.
    """
    hit = find_planning_story(p, ref)
    if not hit or hit[1] is None:
        die(f'no plan story matched "{ref}". Run `list` to see what exists.')
    epic, story = hit[0], hit[1]
    deps = compute_dependents(p, epic, story)
    if as_json:
        emit_json({"of": f"{epic.num}.{story.num}", "count": len(deps), "dependents": deps})
        return
    emit(f"Downstream dependents of {epic.num}.{story.num} - {story.title or ''}")
    emit(HEURISTIC_CAVEAT)
    if not deps:
        emit("  (none. No later story shares its codes or surfaces, or names it.)")
        return
    emit("")
    for d in deps:
        emit(f"  {d['ref']}  [{d['status']}]  {d['title'] or '(untitled)'}")
        emit(f"      why: {d['reason']}")
        dev_note = "   dev: EXISTS" if d["devStoryExists"] else "   dev: (not yet created)"
        emit(f"      plan: {d['planFile']}{dev_note}")
    emit(f"\n{len(deps)} downstream dependent(s).")


def cmd_feed_forward(p: Paths, ref: str, as_json: bool) -> None:
    """Resolve the ground-truth writeback targets for a finished story.

    HEURISTIC, same scan as `deps`. It tells you which later story files to
    open, not what to write in them.
    """
    hit = find_planning_story(p, ref)
    if not hit or hit[1] is None:
        die(f'no plan story matched "{ref}". Run `list` to see what exists.')
    epic, story = hit[0], hit[1]
    deps = compute_dependents(p, epic, story)
    out: Dict[str, Any] = {
        "source": {
            "ref": f"{epic.num}.{story.num}",
            "epic": epic.id,
            "story": story.id,
            "title": story.title,
            "planFile": str(story.file),
            "devStoryFile": str(dev_story_path(p, epic, story)),
            "codes": sorted(story_codes(story.file), key=natural_key),
            "surfaces": sorted(story_surfaces(story.file), key=natural_key),
        },
        "dependents": deps,
    }
    if as_json:
        emit_json(out)
        return
    src = out["source"]
    emit(f"Feed-forward from {src['ref']} - {src['title'] or ''}")
    emit(HEURISTIC_CAVEAT)
    emit(f"  surface codes:    {', '.join(src['codes']) or '(none found)'}")
    emit(f"  surface names:    {', '.join(src['surfaces']) or '(none found)'}")
    emit(f"  dependent stories to update ({len(deps)}):")
    for d in deps:
        emit(f"    -> {d['ref']} [{d['status']}]  {d['title'] or ''}  ({d['reason']})")
        emit(f"        write the inherited ground truth into: {d['planFile']}")
    if not deps:
        emit("    (none, nothing to feed forward)")


def cmd_suggest_next(p: Paths, ref: Optional[str], as_json: bool) -> None:
    """Recommend the next story, dependency aware rather than strictly numeric."""
    status = load_status(p)
    epics = discover_epics(p)
    candidates = [x for x in flat_status(p) if x.status in ("planned", "blocked")]

    def is_done(epic_num: int, story_num: int) -> bool:
        e = next((x for x in epics if x.num == epic_num), None)
        if not e:
            return False
        s = next((x for x in e.stories if x.num == story_num), None)
        if not s:
            return False
        return status_of(status, e.id, s.id) == "done"

    scored: List[Dict[str, Any]] = []
    for c in candidates:
        deps = explicit_deps_of(c.story.file)
        unmet = [d for d in deps if not is_done(*d)]
        scored.append({"entry": c, "deps": deps, "unmet": unmet, "ready": not unmet})

    pick = next((x for x in scored if x["ready"]), scored[0] if scored else None)
    if ref:
        hit = find_planning_story(p, ref)
        if hit and hit[1] is not None:
            src_epic, src_story = hit[0], hit[1]
            successor = next(
                (
                    x
                    for x in scored
                    if x["ready"] and (src_epic.num, src_story.num) in x["deps"]
                ),
                None,
            )
            same_epic_ready = next(
                (x for x in scored if x["ready"] and x["entry"].epic.num == src_epic.num),
                None,
            )
            pick = (
                successor
                or same_epic_ready
                or next((x for x in scored if x["ready"]), scored[0] if scored else None)
            )

    if not pick:
        emit_json({"found": False}) if as_json else emit(
            "No planned or blocked story left to suggest."
        )
        return

    entry: FlatEntry = pick["entry"]
    result: Dict[str, Any] = {
        "found": True,
        **_entry_payload(p, entry),
        "ready": pick["ready"],
        "blockedBy": [f"{e}.{s}" for e, s in pick["unmet"]],
        "note": f"suggested after {ref}" if ref else "suggested from the backlog",
    }
    if as_json:
        emit_json(result)
        return
    emit(
        f"Suggested next story: {result['ref']} - {result['title'] or '(untitled)'}"
        f" [{entry.status}]"
    )
    emit(HEURISTIC_CAVEAT)
    if result["ready"]:
        emit("  ready: every explicit prerequisite it names is done.")
        emit("  Check the story prose for an ordering rule this scan cannot see.")
    else:
        emit(f"  BLOCKED by: {', '.join(result['blockedBy'])}")
    emit(f"  plan: {result['planFile']}")
    if result["devStoryExists"]:
        emit(f"  dev story: {result['devStoryFile']} (exists)")
    else:
        emit("  dev story: (not yet created)")
    if not result["ready"]:
        alt = next((x for x in scored if x["ready"]), None)
        if alt:
            ae: FlatEntry = alt["entry"]
            emit(
                f"  (alt: a ready story exists, {ae.epic.num}.{ae.story.num} - "
                f"{ae.story.title or ''})"
            )


# ---------------------------------------------------------------------------
# lessons
# ---------------------------------------------------------------------------


def cmd_lessons(
    p: Paths,
    ref: Optional[str],
    all_epics: bool,
    hazards_only: bool,
    limit: Optional[int],
    as_json: bool,
) -> None:
    """Mine the `## Dev agent record` of DONE stories for carry-forward lessons.

    THIS COMMAND FAILS LOUD ON PURPOSE. It always prints its denominator:
    how many stories it scanned, how many had a record at all, and how many
    lessons came out. A thin result must read as "those stories logged little",
    never as "there is nothing to learn". Do not remove that line.

    A denominator cannot see what the matcher never matched. It guards against
    scanning too few files, not against extracting too few items per file.
    """
    if limit is None:
        limit = 40 if all_epics else 12

    pool = [x for x in flat_status(p) if x.status == "done"]
    scope_label = "all done stories (every epic)"

    if ref:
        hit = find_planning_story(p, ref)
        if not hit or hit[1] is None:
            die(f'no plan story matched "{ref}". Run `list` to see what exists.')
        epic, story = hit[0], hit[1]
        pool = [
            x
            for x in pool
            if (x.epic.num == epic.num and x.story.num < story.num)
            or (all_epics and x.epic.num < epic.num)
        ]
        scope_label = (
            f"everything shipped before {epic.num}.{story.num}"
            if all_epics
            else f"epic {epic.num}, stories before {story.num}"
        )
    elif not all_epics:
        pool = pool[-limit:]

    pool = list(reversed(pool))  # newest first

    lessons: List[Dict[str, Any]] = []
    with_record = 0
    for x in pool:
        items = extract_record(dev_story_path(p, x.epic, x.story))
        if items:
            with_record += 1
        for text in items:
            hazard = bool(HAZARD_RE.search(text))
            if hazards_only and not hazard:
                continue
            lessons.append(
                {
                    "ref": f"{x.epic.num}.{x.story.num}",
                    "storyId": x.story.id,
                    "title": x.story.title,
                    "text": text,
                    "hazard": hazard,
                }
            )

    shown = rank_lessons(lessons, limit)
    n_hazards = sum(1 for x in lessons if x["hazard"])

    if as_json:
        emit_json(
            {
                "scope": scope_label,
                "storiesScanned": len(pool),
                "storiesWithRecord": with_record,
                "lessonsFound": len(lessons),
                "hazards": n_hazards,
                "shown": len(shown),
                "truncated": len(lessons) > len(shown),
                "lessons": shown,
            }
        )
        return

    emit(f"Lessons from {scope_label}")
    plural = "y" if len(pool) == 1 else "ies"
    emit(
        f"  scanned {len(pool)} done stor{plural}, {with_record} had a record, "
        f"{len(lessons)} lessons, {n_hazards} flagged as hazards"
    )
    if not shown:
        emit("\n  (nothing to carry forward. Those stories logged no dev record entries.)")
        return
    emit("")
    for lesson in shown:
        mark = "[!] " if lesson["hazard"] else "  . "
        body = lesson["text"]
        if len(body) > 400:
            body = body[:400] + "..."
        emit(f"{mark}[{lesson['ref']}] {body}\n")
    if len(lessons) > len(shown):
        emit(
            f"  ... {len(lessons) - len(shown)} more. Raise --limit=N, or use --hazards "
            "to see only the traps."
        )


# ---------------------------------------------------------------------------
# stale-refs
# ---------------------------------------------------------------------------


def cmd_stale_refs(p: Paths, code_dirs: List[str], as_json: bool) -> None:
    """Report code names that forward-looking spec prose promises but the code lacks.

    The drift this catches: a story is planned against a GUESSED helper name,
    the implementation ships a different one, and the plan keeps sending the
    next dev at a symbol that does not exist. Nothing else notices, because the
    specs are markdown.
    """
    defined = harvest_identifiers(p.root, code_dirs)
    if not defined:
        die(
            "no source files found. Pass --code-dir <dir> one or more times, "
            f"or run from the project root. Looked under: {', '.join(code_dirs) or p.root}",
            2,
        )

    files_scanned = 0
    files_with_refs = 0
    findings: List[Dict[str, Any]] = []

    for md in sorted(p.plan.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        files_scanned += 1
        seen_here = False
        for lineno, line in forward_looking_lines(text):
            for raw in IDENT_RE.findall(line):
                ident = raw.split(".")[-1]
                if ident in IDENT_STOPWORDS or len(ident) < 4:
                    continue
                looks_like_code = (
                    ident.startswith("_")
                    or "_" in ident
                    or (ident[:1].isupper() and any(c.islower() for c in ident))
                )
                if not looks_like_code:
                    continue
                seen_here = True
                if ident not in defined:
                    findings.append(
                        {
                            "file": str(md),
                            "line": lineno,
                            "identifier": raw,
                            "context": line.strip()[:160],
                        }
                    )
        if seen_here:
            files_with_refs += 1

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for f in findings:
        key = (f["file"], f["identifier"])
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    if as_json:
        emit_json(
            {
                "scannedFiles": files_scanned,
                "filesWithCodeRefs": files_with_refs,
                "definedIdentifiers": len(defined),
                "stale": deduped,
            }
        )
        return

    # Always print the denominator. A thin result must read as "they named few
    # identifiers", never as "there is nothing here".
    emit(
        f"scanned {files_scanned} plan file(s), {files_with_refs} named code identifiers, "
        f"{len(defined)} identifiers defined in the code, {len(deduped)} stale"
    )
    if not deduped:
        emit("\nNo stale code references in forward-looking spec prose.")
        return
    emit("")
    for f in deduped:
        emit(f"  [!] {f['file']}:{f['line']}  `{f['identifier']}` is not defined in the code")
        emit(f"      {f['context']}")
    emit(
        "\nEach one is a name a future dev story will be sent to look for. Fix the spec "
        "line to the shipped name, or confirm the symbol is still unbuilt."
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_EPILOG = """\
heuristic commands, verify their verdicts:
  deps, feed-forward, suggest-next, lessons and stale-refs are regex scans over
  freeform markdown prose. They are hints, not ground truth. A phrasing outside
  the recognized keywords defeats them without any error.

writes:
  sync-status and set-status write status.yaml. Every other command is read only.

examples:
  python specs.py list
  python specs.py show epic-01-auth story-02-login
  python specs.py story-info 1.2 --json
  python specs.py set-status 1.2 done
  python specs.py lessons 2.3 --hazards --limit=5
  python specs.py --root /path/to/project --specs-dir specs coverage
"""


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="specs.py",
        description=(
            "The single interface to a project's spec artifacts, so an agent never "
            "has to load the whole PRD, epics and stories into its context."
        ),
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="project root (default: the current directory)",
    )
    ap.add_argument(
        "--specs-dir",
        default=DEFAULT_SPECS_DIR,
        help=f"specs root, relative to --root or absolute (default: {DEFAULT_SPECS_DIR})",
    )
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")

    sub = ap.add_subparsers(dest="command")

    sub.add_parser("help", help="print this help")
    sub.add_parser("list", help="list epics and stories with status")

    sp = sub.add_parser("show", help="print one epic.md or story file")
    sp.add_argument("epic", help="epic id, for example epic-01-auth")
    sp.add_argument("story", nargs="?", help="story id, for example story-02-login")

    sub.add_parser("reqs", help="list requirement ids declared in the PRD")
    sub.add_parser("coverage", help="map each requirement to its covering epics")
    sub.add_parser("sync-status", help="rebuild status.yaml structure, preserving values")

    sp = sub.add_parser("next-id", help="next free epic number, or story number in an epic")
    sp.add_argument("epic", nargs="?")

    sp = sub.add_parser("slug", help="print a kebab-case slug for a title")
    sp.add_argument("title", nargs="+")

    sub.add_parser("next-story", help="next planned story to expand")
    sub.add_parser("next-dev", help="next dev story to implement")
    sub.add_parser("dev-list", help="list dev stories that exist, with status")

    sp = sub.add_parser("story-info", help="resolve a story: files, previous story, status")
    sp.add_argument("ref", help='"1.2" | "1-2" | epic-01-x/story-02-y | a story id')

    sp = sub.add_parser("set-status", help="set an epic or story status")
    sp.add_argument("ref")
    sp.add_argument("status", choices=list(STATUS_VALUES))

    sp = sub.add_parser("deps", help="downstream stories that depend on a story (heuristic)")
    sp.add_argument("ref")

    sp = sub.add_parser(
        "feed-forward", help="ground-truth writeback targets for a finished story (heuristic)"
    )
    sp.add_argument("ref")

    sp = sub.add_parser("suggest-next", help="dependency-aware next story (heuristic)")
    sp.add_argument("ref", nargs="?")

    sp = sub.add_parser("lessons", help="mine dev records of done stories (heuristic)")
    sp.add_argument("ref", nargs="?")
    sp.add_argument("--all-epics", action="store_true", help="widen to every done story")
    sp.add_argument("--hazards", action="store_true", help="show only items flagged as traps")
    sp.add_argument("--limit", type=int, default=None, help="max lessons to print")

    sp = sub.add_parser(
        "stale-refs", help="code names the plan promises but the code lacks (heuristic)"
    )
    sp.add_argument(
        "--code-dir",
        action="append",
        default=[],
        dest="code_dirs",
        help="source directory to harvest identifiers from, repeatable (default: --root)",
    )
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    if args.command in (None, "help"):
        ap.print_help()
        return 0

    p = make_paths(Path(args.root), args.specs_dir)
    j: bool = args.json

    if args.command == "list":
        cmd_list(p, j)
    elif args.command == "show":
        cmd_show(p, args.epic, args.story)
    elif args.command == "reqs":
        cmd_reqs(p, j)
    elif args.command == "coverage":
        cmd_coverage(p, j)
    elif args.command == "sync-status":
        cmd_sync_status(p)
    elif args.command == "next-id":
        cmd_next_id(p, args.epic, j)
    elif args.command == "slug":
        emit(slugify(" ".join(args.title)))
    elif args.command == "next-story":
        cmd_next_story(p, j)
    elif args.command == "next-dev":
        cmd_next_dev(p, j)
    elif args.command == "story-info":
        cmd_story_info(p, args.ref, j)
    elif args.command == "dev-list":
        cmd_dev_list(p, j)
    elif args.command == "set-status":
        cmd_set_status(p, args.ref, args.status)
    elif args.command == "deps":
        cmd_deps(p, args.ref, j)
    elif args.command == "feed-forward":
        cmd_feed_forward(p, args.ref, j)
    elif args.command == "suggest-next":
        cmd_suggest_next(p, args.ref, j)
    elif args.command == "lessons":
        cmd_lessons(p, args.ref, args.all_epics, args.hazards, args.limit, j)
    elif args.command == "stale-refs":
        cmd_stale_refs(p, args.code_dirs, j)
    else:  # pragma: no cover - argparse rejects unknown commands first
        die(f"unknown command: {args.command}", 2)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Do not crash when the output is piped into a reader that closes early.
        sys.exit(0)
