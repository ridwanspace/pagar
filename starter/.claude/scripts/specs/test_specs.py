"""Guard tests for specs.py.

Every test name maps to one numbered correctness requirement from the port
brief. Each of those requirements is a bug that was found and fixed once
already. These tests exist so it cannot come back.

Run:  python3 -m pytest test_specs.py -v
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import specs  # noqa: E402
from _core import (  # noqa: E402
    FEATURE_RE,
    HAZARD_RE,
    IDENT_RE,
    Paths,
    explicit_deps_of,
    explicitly_depends_on,
    extract_record,
    make_paths,
    rank_lessons,
    sync_status,
)
from _yaml import YamlSubsetError, dump_yaml, load_yaml  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def build_tree(root: Path, *, with_plan_epic: bool = True) -> Paths:
    """Minimal spec tree built through the real path factory."""
    p = make_paths(root)
    p.plan.mkdir(parents=True, exist_ok=True)
    p.impl.mkdir(parents=True, exist_ok=True)
    p.prd.write_text("# PRD\n", encoding="utf-8")
    if with_plan_epic:
        d = p.plan / "epic-01-normal"
        d.mkdir(exist_ok=True)
        (d / "epic.md").write_text("# Epic 1 - Normal\n", encoding="utf-8")
        (d / "story-01-thing.md").write_text("# Story - Thing\n", encoding="utf-8")
    return p


def write_status(p: Paths, doc: dict) -> None:
    p.status_file.parent.mkdir(parents=True, exist_ok=True)
    p.status_file.write_text(dump_yaml(doc) + "\n", encoding="utf-8")


def story_file(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "story.md"
    f.write_text(body, encoding="utf-8")
    return f


def run_cli(*argv: str) -> str:
    """Run the CLI and capture stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        specs.main(list(argv))
    return buf.getvalue()


SOURCED_EPIC = {
    "status": "done",
    "source": "research/RESEARCH-02-headers-audit.md",
    "stories": {
        "story-01-auth-overlay": {
            "status": "done",
            "title": "Exercise on-screen auth, not stored auth",
            "created": "2026-01-11",
            "completed": "2026-01-11",
        }
    },
}


# ---------------------------------------------------------------------------
# Requirement 1. Multi-ref dependency lines need a COLLECTING scan.
# ---------------------------------------------------------------------------


def test_req1_multi_ref_dependency_line_collects_every_ref(tmp_path):
    """`depends on stories 2.1 (a), 2.2 (b), 2.3 (c)` must yield all three.

    A naive keyword-plus-ref finditer yields only 2.1 and silently drops the
    rest. This is the exact line shape that exposed it.
    """
    f = story_file(
        tmp_path,
        "This story depends on stories 2.1 (registry), 2.2 (surface), 2.3 (defense)\n",
    )
    assert explicit_deps_of(f) == [(2, 1), (2, 2), (2, 3)]


def test_req1_non_story_lookalikes_are_filtered(tmp_path):
    """A date and a version must not read as story refs."""
    f = story_file(
        tmp_path,
        "Depends on 2.1, shipped 2026-07-07 against tool 1.49.0 and lib 3.4.5\n",
    )
    deps = explicit_deps_of(f)
    assert (2, 1) in deps
    assert (2026, 7) not in deps
    assert (1, 49) not in deps
    assert (3, 4) not in deps


def test_req1_a_later_semicolon_clause_is_a_different_relationship(tmp_path):
    """`; gates 2.4` names an inverse relationship and must not be swept in."""
    f = story_file(tmp_path, "Depends on 2.1 and 2.2; GATES 2.4 and 2.5\n")
    deps = explicit_deps_of(f)
    assert (2, 1) in deps and (2, 2) in deps
    assert (2, 4) not in deps and (2, 5) not in deps


# ---------------------------------------------------------------------------
# Requirement 2. The clause boundary must be a SENTENCE boundary.
# ---------------------------------------------------------------------------


def test_req2_trailing_independent_of_sentence_on_the_same_line_is_excluded(tmp_path):
    """A dependency keyword and a later "Independent of" sentence share one line.

    A scan that runs to the newline collects refs the same line explicitly
    excludes. The boundary must cut at ". " followed by a capital.

    This test alone cannot isolate the boundary. The negation regex is anchored
    to the end of the clause, so with a newline-only boundary it swallows the
    whole tail and masks every ref after "Independent of" by accident. The
    companion test below, with no negation on the line, is the one that goes RED
    when the boundary stops being a sentence boundary. Keep both.
    """
    line = (
        "**Depends on 2.2** for the registry. **Independent of 2.1, 2.3, 2.4.** "
        "Ships alongside 4.7 and 4.8.\n"
    )
    f = story_file(tmp_path, line)
    deps = explicit_deps_of(f)
    assert (2, 2) in deps, f"the real dependency was lost: {deps}"
    for excluded in ((2, 1), (2, 3), (2, 4)):
        assert excluded not in deps, f"{excluded} came from the Independent-of sentence: {deps}"
    for excluded in ((4, 7), (4, 8)):
        assert excluded not in deps, (
            f"{excluded} came from a later sentence on the same line, so the clause "
            f"boundary is not a sentence boundary: {deps}"
        )


def test_req2_a_plain_later_sentence_on_the_same_line_is_excluded(tmp_path):
    """The boundary must cut at a sentence even with no negation in sight.

    This is the case that isolates the boundary itself. A `[;\\n]`-only boundary
    sweeps 4.7 and 4.8 in, because nothing else here would stop it.
    """
    f = story_file(
        tmp_path, "Depends on 2.2 for the registry. Ships alongside 4.7 and 4.8.\n"
    )
    assert explicit_deps_of(f) == [(2, 2)]


def test_req2_a_refs_own_decimal_point_never_ends_the_clause(tmp_path):
    """`2.3` must not split into `2` and `3` at its own dot."""
    f = story_file(tmp_path, "Depends on 2.3 and 2.4 for the shared surface\n")
    assert explicit_deps_of(f) == [(2, 3), (2, 4)]


def test_req2_explicitly_depends_on_shares_the_same_boundary(tmp_path):
    """The sibling scanner must agree with the collecting one, in both directions."""
    line = (
        "**Depends on 2.2.** **Independent of 2.1, 2.3.** Ships alongside 4.7.\n"
    )
    f = story_file(tmp_path, line)
    assert explicitly_depends_on(f, 2, 2) is True
    assert explicitly_depends_on(f, 2, 1) is False
    assert explicitly_depends_on(f, 2, 3) is False
    assert explicitly_depends_on(f, 4, 7) is False, (
        "a ref from a later sentence on the same line was read as a dependency"
    )


# ---------------------------------------------------------------------------
# Requirement 3. The negation tail must ALLOW a dot.
# ---------------------------------------------------------------------------


def test_req3_negation_tail_allows_a_dot_so_later_refs_are_still_rejected(tmp_path):
    """A `[^.;\\n]*` tail stops at the first ref's own decimal point.

    That turns the negation check into dead code for every ref after the first.
    Here 2.7 sits past 2.5's decimal point inside the same negating tail, so it
    must still be rejected.
    """
    f = story_file(tmp_path, "Depends on stories independent of 2.5, 2.7 and 2.9\n")
    deps = explicit_deps_of(f)
    assert deps == [], f"a ref past the first decimal point escaped the negation: {deps}"
    assert explicitly_depends_on(f, 2, 9) is False


def test_req3_negation_does_not_swallow_a_genuine_earlier_dependency(tmp_path):
    """The negation is a TAIL. A real dependency before it must survive."""
    f = story_file(tmp_path, "Depends on 3.1, independent of 3.2 and 3.4\n")
    deps = explicit_deps_of(f)
    assert (3, 1) in deps
    assert (3, 2) not in deps and (3, 4) not in deps


# ---------------------------------------------------------------------------
# Requirement 4. sync-status preserves values while rebuilding structure.
# Both the fully-absent and the partially-sourced states, they fail differently.
# ---------------------------------------------------------------------------


def test_req4_sync_status_preserves_a_fully_absent_sourced_epic(tmp_path):
    """A sourced epic with NO plan parent must survive a rebuild verbatim."""
    p = build_tree(tmp_path, with_plan_epic=True)
    write_status(p, {"epics": {"epic-00-research-fixes": SOURCED_EPIC}})

    doc, _added, removed = sync_status(p)

    assert "epic-00-research-fixes" in doc["epics"], f"deleted: {list(doc['epics'])}"
    assert "epic-00-research-fixes" not in removed
    carried = doc["epics"]["epic-00-research-fixes"]
    assert carried["status"] == "done"
    assert carried["source"].endswith("RESEARCH-02-headers-audit.md")
    story = carried["stories"]["story-01-auth-overlay"]
    assert story["status"] == "done"
    assert story["completed"] == "2026-01-11", "story metadata must survive verbatim"

    on_disk = load_yaml(p.status_file.read_text(encoding="utf-8"))
    assert "epic-00-research-fixes" in on_disk["epics"], "kept in memory but lost on disk"


def test_req4_sync_status_preserves_a_partially_sourced_epic(tmp_path):
    """A sourced epic that LATER gains plan stories must keep the older ones.

    Conditioning carry-through on "absent from the tree" fails here: the epic
    becomes visible to the scan, drops out of the carry-through set, and every
    implementation-only story is deleted along with the `source` key.
    """
    p = build_tree(tmp_path, with_plan_epic=True)
    d = p.plan / "epic-00-research-fixes"
    d.mkdir(exist_ok=True)
    (d / "epic.md").write_text("# Epic 0 - Research fixes\n", encoding="utf-8")
    (d / "story-03-new-finding.md").write_text("# Story - New finding\n", encoding="utf-8")
    write_status(p, {"epics": {"epic-00-research-fixes": SOURCED_EPIC}})

    doc, _added, removed = sync_status(p)
    carried = doc["epics"]["epic-00-research-fixes"]

    assert "story-01-auth-overlay" in carried["stories"], (
        f"implementation-only story deleted: {list(carried['stories'])}"
    )
    assert carried["stories"]["story-01-auth-overlay"]["completed"] == "2026-01-11"
    assert "epic-00-research-fixes/story-01-auth-overlay" not in removed
    assert carried.get("source", "").endswith("RESEARCH-02-headers-audit.md"), (
        "the epic lost its source key, so the next sync would delete it outright"
    )
    assert "story-03-new-finding" in carried["stories"], "the new plan story was not picked up"


def test_req4_sync_status_still_removes_a_genuinely_deleted_epic(tmp_path):
    """The guard must not degrade into "never remove anything"."""
    p = build_tree(tmp_path, with_plan_epic=True)
    write_status(
        p,
        {
            "epics": {
                "epic-09-deleted": {
                    "status": "planned",
                    "stories": {"story-01-gone": {"status": "planned", "title": "Gone"}},
                }
            }
        },
    )
    doc, _added, removed = sync_status(p)
    assert "epic-09-deleted" not in doc["epics"]
    assert "epic-09-deleted" in removed


def test_req4_sync_status_preserves_a_hand_edited_status(tmp_path):
    """A status a human set must survive the structural rebuild."""
    p = build_tree(tmp_path, with_plan_epic=True)
    sync_status(p)
    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")
    doc, _added, _removed = sync_status(p)
    assert doc["epics"]["epic-01-normal"]["stories"]["story-01-thing"]["status"] == "done"


# ---------------------------------------------------------------------------
# Requirement 5. lessons must fail LOUD, always printing its denominator.
# ---------------------------------------------------------------------------


def _done_story_with_record(p: Paths, epic: str, story: str, record: str) -> None:
    (p.plan / epic).mkdir(parents=True, exist_ok=True)
    (p.plan / epic / f"{story}.md").write_text(f"# {story}\n", encoding="utf-8")
    (p.impl / epic).mkdir(parents=True, exist_ok=True)
    (p.impl / epic / f"{story}.md").write_text(
        f"# {story}\n\n## Dev agent record\n\n{record}\n", encoding="utf-8"
    )


def test_req5_lessons_always_prints_its_denominator(tmp_path):
    """A thin result must read as "they logged little", not "nothing to learn"."""
    p = build_tree(tmp_path, with_plan_epic=False)
    _done_story_with_record(
        p,
        "epic-01-core",
        "story-01-first",
        "- The green suite missed a null column, so the write silently dropped rows.",
    )
    (p.plan / "epic-01-core" / "story-02-second.md").write_text("# second\n", encoding="utf-8")
    sync_status(p)
    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")

    out = run_cli("--root", str(tmp_path), "lessons", "1.2")
    assert "scanned 1 done story," in out, out
    assert "1 had a record" in out, out
    assert "1 lessons" in out, out


def test_req5_lessons_prints_the_denominator_even_when_nothing_was_found(tmp_path):
    """Zero lessons must still show the denominator, never a bare empty result."""
    p = build_tree(tmp_path, with_plan_epic=False)
    (p.plan / "epic-01-core").mkdir(parents=True, exist_ok=True)
    (p.plan / "epic-01-core" / "story-01-first.md").write_text("# first\n", encoding="utf-8")
    (p.plan / "epic-01-core" / "story-02-second.md").write_text("# second\n", encoding="utf-8")
    sync_status(p)
    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")

    out = run_cli("--root", str(tmp_path), "lessons", "1.2")
    assert "scanned 1 done story," in out, out
    assert "0 had a record" in out, out
    assert "0 lessons" in out, out


def test_req5_lessons_json_carries_the_same_denominator(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=False)
    _done_story_with_record(
        p,
        "epic-01-core",
        "story-01-first",
        "- A footgun that bit us twice: the retry loop silently swallowed the error code.",
    )
    (p.plan / "epic-01-core" / "story-02-second.md").write_text("# second\n", encoding="utf-8")
    sync_status(p)
    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")

    data = json.loads(run_cli("--root", str(tmp_path), "--json", "lessons", "1.2"))
    assert data["storiesScanned"] == 1
    assert data["storiesWithRecord"] == 1
    assert data["lessonsFound"] == 1
    assert data["hazards"] == 1


def test_req5_lessons_hazards_and_limit_flags_work(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=False)
    _done_story_with_record(
        p,
        "epic-01-core",
        "story-01-first",
        "- Plain note about the migration ordering that carries no cost signal at all.\n"
        "- The bug that shipped was silently swallowed by the retry wrapper, twice over.",
    )
    (p.plan / "epic-01-core" / "story-02-second.md").write_text("# second\n", encoding="utf-8")
    sync_status(p)
    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")

    everything = json.loads(run_cli("--root", str(tmp_path), "--json", "lessons", "1.2"))
    assert everything["lessonsFound"] == 2

    only_traps = json.loads(
        run_cli("--root", str(tmp_path), "--json", "lessons", "1.2", "--hazards")
    )
    assert only_traps["lessonsFound"] == 1
    assert all(x["hazard"] for x in only_traps["lessons"])

    capped = json.loads(
        run_cli("--root", str(tmp_path), "--json", "lessons", "1.2", "--limit=1")
    )
    assert capped["shown"] == 1
    assert capped["truncated"] is True


# ---------------------------------------------------------------------------
# Requirement 6. The identifier matcher must handle the syntax the corpus uses.
# ---------------------------------------------------------------------------


def test_req6_ident_matcher_handles_a_call_written_with_arguments():
    """A matcher tested only against `f()` skips every `f(x)` in the real corpus.

    `\\(?\\)?` tolerates empty parens only, so every backticked call written
    with real arguments matched nothing and was never checked. The tool then
    reported clean for names it never looked at.
    """
    line = (
        "Call `mint_verification_token(user, ttl)` after "
        "`compute_config_fingerprint(cfg)` and before `flush()`."
    )
    found = IDENT_RE.findall(line)
    assert "mint_verification_token" in found, f"a call with args was skipped: {found}"
    assert "compute_config_fingerprint" in found, f"a call with args was skipped: {found}"
    assert "flush" in found


def test_req6_ident_matcher_does_not_swallow_a_second_call_on_one_line():
    """The argument class must not eat a closing backtick."""
    found = IDENT_RE.findall("`first_call(a, b)` then `second_call(c)`")
    assert found == ["first_call", "second_call"], found


def test_req6_stale_refs_finds_a_promised_name_written_with_arguments(tmp_path):
    """End to end: a promised call with real arguments must be reported stale."""
    p = build_tree(tmp_path, with_plan_epic=False)
    src = tmp_path / "code"
    src.mkdir()
    (src / "real.py").write_text("def coerce_param_value(x):\n    return x\n", encoding="utf-8")
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text(
        "# Epic 1\n\n## Dependencies\n\nStory 1 needs `coerce_param(value, kind)` from the core.\n",
        encoding="utf-8",
    )
    data = json.loads(
        run_cli(
            "--root", str(tmp_path), "--json", "stale-refs", "--code-dir", "code"
        )
    )
    idents = [f["identifier"] for f in data["stale"]]
    assert "coerce_param" in idents, f"a call with args was never checked: {data}"


# ---------------------------------------------------------------------------
# Requirement 7. A hazard filter that matches everything is worth nothing.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hazard",
    [
        "The green suite missed it, the column stayed nullable in production.",
        "That one bit us twice before anyone noticed the retry was silent.",
        "It fails silently when the payload is empty, no log line at all.",
        "This generalizes to any scanner over freeform prose, not just this one.",
        "A classic footgun: the default argument is shared across every call.",
    ],
)
def test_req7_hazard_matcher_fires_on_a_named_cost_or_generalization(hazard):
    assert HAZARD_RE.search(hazard), f"a real hazard was missed: {hazard!r}"


@pytest.mark.parametrize(
    "plain",
    [
        "Added the endpoint and its handler, then wired the route table.",
        "Renamed the config key and updated the two callers.",
        "The bug report came from QA on Tuesday afternoon.",
        "Wrote a warning in the docs about ordering.",
        "Refactored the parser into three smaller functions.",
    ],
)
def test_req7_hazard_matcher_stays_quiet_on_a_plain_note(plain):
    """A signal that fires on everything carries no information.

    An early draft matched a bare warning sign and the word "bug", so every
    scanned item came back flagged.
    """
    assert not HAZARD_RE.search(plain), f"false positive on a plain note: {plain!r}"


def test_req7_hazard_matcher_does_not_flag_every_item_in_a_mixed_record(tmp_path):
    """On a realistic mixed record, well under half the items should be hazards."""
    f = tmp_path / "dev.md"
    f.write_text(
        "# Story\n\n## Dev agent record\n\n"
        "- Added the create endpoint plus its marshalling layer and route entry.\n"
        "- Renamed two config keys and updated every caller in the service layer.\n"
        "- Extended the fixture set so the new path has coverage in both branches.\n"
        "- The green suite missed the null column, so the write silently dropped rows.\n",
        encoding="utf-8",
    )
    items = extract_record(f)
    assert len(items) == 4, items
    hazards = [i for i in items if HAZARD_RE.search(i)]
    assert len(hazards) == 1, f"the filter flagged too much: {hazards}"


# ---------------------------------------------------------------------------
# Requirement 8. Ranking needs diversity, round-robin first.
# ---------------------------------------------------------------------------


def test_req8_ranking_round_robins_across_stories_before_sorting():
    """One verbose story must not eat the whole budget.

    Story 1.1 logs six items, story 1.2 and 1.3 log one each. A flat sort and
    slice at limit 3 would return three items all from 1.1.
    """
    lessons = [{"ref": "1.1", "text": f"verbose {i}", "hazard": False} for i in range(6)]
    lessons.append({"ref": "1.2", "text": "quiet one", "hazard": False})
    lessons.append({"ref": "1.3", "text": "quiet two", "hazard": False})

    shown = rank_lessons(lessons, limit=3)
    refs = {x["ref"] for x in shown}
    assert refs == {"1.1", "1.2", "1.3"}, f"one story ate the budget: {refs}"


def test_req8_ranking_puts_hazards_first_within_the_diverse_set():
    """Diversity comes first, then hazards sort to the top of that set."""
    lessons = [
        {"ref": "1.1", "text": "plain a", "hazard": False},
        {"ref": "1.1", "text": "plain b", "hazard": False},
        {"ref": "1.2", "text": "trap", "hazard": True},
    ]
    shown = rank_lessons(lessons, limit=2)
    assert shown[0]["hazard"] is True, f"hazard was not first: {shown}"
    assert {x["ref"] for x in shown} == {"1.1", "1.2"}


def test_req8_ranking_prefers_a_hazard_within_one_story(tmp_path):
    """Inside a single story's bucket, the hazard must be the item that shows."""
    lessons = [
        {"ref": "1.1", "text": "plain", "hazard": False},
        {"ref": "1.1", "text": "trap", "hazard": True},
    ]
    shown = rank_lessons(lessons, limit=1)
    assert shown == [{"ref": "1.1", "text": "trap", "hazard": True}]


# ---------------------------------------------------------------------------
# Requirement 9. Feature ids may contain digits, and all scanners must agree.
# ---------------------------------------------------------------------------


def test_req9_feature_ids_may_contain_digits():
    """`F-A11Y` is a valid id. A `[A-Z-]+` pattern truncates or drops it."""
    text = "Covers F-A11Y, F-AUTH, F-OAUTH2 and F-I18N-RTL."
    found = FEATURE_RE.findall(text)
    assert set(found) == {"F-A11Y", "F-AUTH", "F-OAUTH2", "F-I18N-RTL"}, found


def test_req9_all_scanners_agree_on_the_digit_bearing_feature_id(tmp_path):
    """reqs, coverage, and the story surface scan must all see F-A11Y."""
    p = build_tree(tmp_path, with_plan_epic=False)
    p.prd.write_text("# PRD\n\nF-A11Y accessibility is a verified state.\n", encoding="utf-8")
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Epic 1\n\nCovers F-A11Y.\n", encoding="utf-8")
    (d / "story-01-audit.md").write_text("# Audit\n\nImplements F-A11Y.\n", encoding="utf-8")

    reqs = json.loads(run_cli("--root", str(tmp_path), "--json", "reqs"))
    assert "F-A11Y" in reqs["features"]

    cov = json.loads(run_cli("--root", str(tmp_path), "--json", "coverage"))
    row = next(r for r in cov["rows"] if r["feature"] == "F-A11Y")
    assert row["epics"] == ["epic-01-core"], f"coverage disagreed with reqs: {cov}"
    assert cov["uncovered"] == []


def test_req9_shared_digit_bearing_code_links_two_stories(tmp_path):
    """The dependents scan must match on F-A11Y too, not only on plain ids."""
    p = build_tree(tmp_path, with_plan_epic=False)
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Epic 1\n", encoding="utf-8")
    (d / "story-01-first.md").write_text("# First\n\nBuilds F-A11Y.\n", encoding="utf-8")
    (d / "story-02-second.md").write_text("# Second\n\nExtends F-A11Y.\n", encoding="utf-8")

    data = json.loads(run_cli("--root", str(tmp_path), "--json", "deps", "1.1"))
    assert data["count"] == 1
    assert data["dependents"][0]["sharedCodes"] == ["F-A11Y"]


# ---------------------------------------------------------------------------
# Requirement 10. Every heuristic is a hint. Say so, in help and in output.
# ---------------------------------------------------------------------------


def test_req10_help_output_names_the_heuristic_commands():
    out = run_cli("help")
    low = out.lower()
    assert "heuristic" in low, out
    for name in ("deps", "feed-forward", "suggest-next", "lessons"):
        assert name in out, f"{name} missing from help"
    assert "verify" in low, "help must tell the reader to verify the verdicts"


def test_req10_deps_prints_a_caveat_line(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=False)
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Epic 1\n", encoding="utf-8")
    (d / "story-01-first.md").write_text("# First\n", encoding="utf-8")
    out = run_cli("--root", str(tmp_path), "deps", "1.1")
    assert "regex scan over freeform markdown" in out, out
    assert "Verify" in out, out


def test_req10_suggest_next_prints_a_caveat_line(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=True)
    sync_status(p)
    out = run_cli("--root", str(tmp_path), "suggest-next")
    assert "regex scan over freeform markdown" in out, out


def test_req10_coverage_says_what_it_cannot_answer(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=True)
    out = run_cli("--root", str(tmp_path), "coverage")
    assert "cannot tell you whether the PRD declared the right features" in out, out


def test_req10_docstrings_carry_the_hint_warning():
    for fn in (
        specs.cmd_deps,
        specs.cmd_feed_forward,
        specs.cmd_suggest_next,
        specs.cmd_lessons,
        specs.cmd_stale_refs,
    ):
        assert fn.__doc__, f"{fn.__name__} has no docstring"
    assert "heuristic" in specs.__doc__.lower()
    assert "HINT TO VERIFY" in specs.__doc__


# ---------------------------------------------------------------------------
# YAML subset reader and writer
# ---------------------------------------------------------------------------


def test_yaml_round_trips_the_status_shape():
    doc = {
        "generated_from": "plan_artifacts",
        "epics": {
            "epic-01-core": {
                "title": "Core",
                "status": "in_progress",
                "stories": {
                    "story-01-first": {"title": "First", "status": "done"},
                    "story-02-second": {"title": None, "status": "planned"},
                },
            }
        },
    }
    assert load_yaml(dump_yaml(doc)) == doc


def test_yaml_keeps_scalar_types_and_quotes_ambiguous_strings():
    doc = {"a": {"n": 12, "t": True, "f": False, "z": None, "s": "true", "num": "42"}}
    back = load_yaml(dump_yaml(doc))
    assert back["a"]["n"] == 12
    assert back["a"]["t"] is True
    assert back["a"]["f"] is False
    assert back["a"]["z"] is None
    assert back["a"]["s"] == "true", "a quoted string must not decode as a bool"
    assert back["a"]["num"] == "42", "a quoted number must not decode as an int"


def test_yaml_skips_comments_and_blank_lines():
    doc = load_yaml("# a header\n\nepics:\n  epic-01: \n    status: done  # trailing\n")
    assert doc["epics"]["epic-01"]["status"] == "done"


def test_yaml_rejects_shapes_outside_the_subset_instead_of_mangling_them():
    for bad in (
        "items:\n  - one\n  - two\n",
        "a: [1, 2]\n",
        "a: {b: 1}\n",
        "base: &anchor\n",
        "---\na: 1\n",
    ):
        with pytest.raises(YamlSubsetError):
            load_yaml(bad)


def test_yaml_writer_rejects_a_sequence_value():
    with pytest.raises(YamlSubsetError):
        dump_yaml({"a": [1, 2]})


def test_status_file_with_unreadable_yaml_fails_loudly(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=True)
    p.status_file.write_text("epics:\n  - not a mapping\n", encoding="utf-8")
    with pytest.raises(SystemExit) as err:
        run_cli("--root", str(tmp_path), "list")
    assert "cannot read it" in str(err.value)


# ---------------------------------------------------------------------------
# The rest of the CLI surface
# ---------------------------------------------------------------------------


def test_list_and_story_info_and_dev_list_and_next_commands(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=True)
    d = p.plan / "epic-01-normal"
    (d / "story-02-next.md").write_text("# Next thing\n", encoding="utf-8")
    sync_status(p)

    listed = json.loads(run_cli("--root", str(tmp_path), "--json", "list"))
    assert listed[0]["id"] == "epic-01-normal"
    assert [s["id"] for s in listed[0]["stories"]] == ["story-01-thing", "story-02-next"]

    info = json.loads(run_cli("--root", str(tmp_path), "--json", "story-info", "1.2"))
    assert info["ref"] == "1.2"
    assert info["previousStory"]["ref"] == "1.1"
    assert info["devStoryExists"] is False

    nxt = json.loads(run_cli("--root", str(tmp_path), "--json", "next-story"))
    assert nxt["ref"] == "1.1"

    (p.impl / "epic-01-normal").mkdir(parents=True, exist_ok=True)
    (p.impl / "epic-01-normal" / "story-01-thing.md").write_text("# dev\n", encoding="utf-8")
    dev = json.loads(run_cli("--root", str(tmp_path), "--json", "next-dev"))
    assert dev["ref"] == "1.1"

    rows = json.loads(run_cli("--root", str(tmp_path), "--json", "dev-list"))
    assert sum(1 for r in rows if r["devStoryExists"]) == 1


def test_set_status_lifts_the_epic_off_planned(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=True)
    sync_status(p)
    out = run_cli("--root", str(tmp_path), "set-status", "1.1", "in_progress")
    assert "epic-01-normal -> in_progress" in out
    doc = load_yaml(p.status_file.read_text(encoding="utf-8"))
    assert doc["epics"]["epic-01-normal"]["status"] == "in_progress"


def test_show_prints_a_file_and_next_id_and_slug(tmp_path):
    build_tree(tmp_path, with_plan_epic=True)
    assert "Epic 1 - Normal" in run_cli("--root", str(tmp_path), "show", "epic-01-normal")
    assert "Thing" in run_cli(
        "--root", str(tmp_path), "show", "epic-01-normal", "story-01-thing"
    )
    assert "epic-02-" in run_cli("--root", str(tmp_path), "next-id")
    assert "story-02-" in run_cli("--root", str(tmp_path), "next-id", "epic-01-normal")
    assert run_cli("slug", "Add  OAuth2 / SSO login!").strip() == "add-oauth2-sso-login"


def test_specs_dir_is_configurable(tmp_path):
    """The specs root must not be hardcoded to .claude/specs."""
    p = make_paths(tmp_path, "specs")
    p.plan.mkdir(parents=True)
    p.impl.mkdir(parents=True)
    p.prd.write_text("# PRD\n\nF-LOGIN.\n", encoding="utf-8")
    d = p.plan / "epic-01-core"
    d.mkdir()
    (d / "epic.md").write_text("# Core\n\nCovers F-LOGIN.\n", encoding="utf-8")

    out = run_cli("--root", str(tmp_path), "--specs-dir", "specs", "list")
    assert "epic-01-core" in out
    assert not (tmp_path / ".claude").exists(), "it wrote to the default path anyway"


def test_suggest_next_reports_blocked_by(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=False)
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Core\n", encoding="utf-8")
    (d / "story-01-base.md").write_text("# Base\n", encoding="utf-8")
    (d / "story-02-uses.md").write_text("# Uses\n\nDepends on 1.1 for the store.\n", encoding="utf-8")
    sync_status(p)

    data = json.loads(run_cli("--root", str(tmp_path), "--json", "suggest-next"))
    assert data["ref"] == "1.1", data
    assert data["ready"] is True

    run_cli("--root", str(tmp_path), "set-status", "1.1", "done")
    data = json.loads(run_cli("--root", str(tmp_path), "--json", "suggest-next", "1.1"))
    assert data["ref"] == "1.2"
    assert data["ready"] is True
    assert data["blockedBy"] == []


def test_feed_forward_lists_the_writeback_targets(tmp_path):
    p = build_tree(tmp_path, with_plan_epic=False)
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Core\n", encoding="utf-8")
    (d / "story-01-base.md").write_text(
        "# Base\n\nBuilds F-LOGIN over `session_token`.\n", encoding="utf-8"
    )
    (d / "story-02-uses.md").write_text(
        "# Uses\n\nReads `session_token` for the refresh path.\n", encoding="utf-8"
    )
    sync_status(p)

    data = json.loads(run_cli("--root", str(tmp_path), "--json", "feed-forward", "1.1"))
    assert data["source"]["surfaces"] == ["session_token"]
    assert data["dependents"][0]["ref"] == "1.2"
    assert data["dependents"][0]["sharedSurfaces"] == ["session_token"]


def test_generic_tokens_do_not_create_a_false_dependency(tmp_path):
    """`user_id` appears everywhere, so a shared match on it means nothing."""
    p = build_tree(tmp_path, with_plan_epic=False)
    d = p.plan / "epic-01-core"
    d.mkdir(parents=True)
    (d / "epic.md").write_text("# Core\n", encoding="utf-8")
    (d / "story-01-base.md").write_text("# Base\n\nWrites `user_id`.\n", encoding="utf-8")
    (d / "story-02-other.md").write_text("# Other\n\nReads `user_id`.\n", encoding="utf-8")
    sync_status(p)

    data = json.loads(run_cli("--root", str(tmp_path), "--json", "deps", "1.1"))
    assert data["count"] == 0, f"a generic token created a false link: {data}"


def test_extract_record_drops_short_noise_lines(tmp_path):
    f = tmp_path / "dev.md"
    f.write_text(
        "# S\n\n## Dev agent record\n\n- short\n"
        "- A long enough entry to count as a real lesson worth carrying forward later.\n"
        "\n## Next section\n\n- Should not be read at all from the following section.\n",
        encoding="utf-8",
    )
    items = extract_record(f)
    assert len(items) == 1
    assert items[0].startswith("A long enough entry")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
