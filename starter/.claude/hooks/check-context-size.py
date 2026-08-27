#!/usr/bin/env python3
"""Stop hook: warn when always-loaded context has grown too big.

The always-loaded memory file is paid for on every single turn. When it drifts
past a couple of hundred lines it starts crowding out the actual task, and
instruction adherence drops. The fix is not to delete anything. The fix is to
move a cohesive section into a scoped rule file that loads only when the agent
touches the matching paths, and to leave a one-line pointer behind.

This hook watches two things:

  1. The always-loaded memory file, by default ``.claude/CLAUDE.md``.
  2. Every rule file under ``.claude/rules/``. A rule that declares a ``paths:``
     key in its YAML frontmatter loads on demand, so it gets a higher limit. A
     rule without ``paths:`` loads at launch like the memory file, so it gets
     the same strict limit.

It warns. It never blocks. Exit code is 0 when everything is within budget and
2 when there is something to say, which is the Claude Code convention for
surfacing a message to the model without stopping the turn.

Configuration, all optional:

  AGENT_CONTEXT_ROOT          repo root                    default: two levels up
  AGENT_CONTEXT_MEMORY_FILE   always-loaded file, relative  default .claude/CLAUDE.md
  AGENT_CONTEXT_RULES_DIR     rules directory, relative     default .claude/rules
  AGENT_CONTEXT_HARD_LIMIT    lines, always-loaded files    default 200
  AGENT_CONTEXT_SOFT_LIMIT    lines, on-demand rule files   default 250
  CLAUDE_PROJECT_DIR          repo root, overrides the default

Python 3 standard library only. It has to run under a bare ``python3`` with no
virtualenv active, because a hook that needs an environment is a hook that
breaks the first time someone forgets to activate one.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


HARD_LIMIT = _int_env("AGENT_CONTEXT_HARD_LIMIT", 200)
SOFT_LIMIT = _int_env("AGENT_CONTEXT_SOFT_LIMIT", 250)


def repo_root() -> Path:
    """Find the repo root.

    Priority: the explicit override, then CLAUDE_PROJECT_DIR, then two levels
    up from this file, which is where ``.claude/hooks/`` sits.
    """
    for var in ("AGENT_CONTEXT_ROOT", "CLAUDE_PROJECT_DIR"):
        value = os.environ.get(var)
        if value:
            return Path(value).resolve()
    return Path(__file__).resolve().parent.parent.parent


ROOT = repo_root()
MEMORY_FILE = ROOT / os.environ.get("AGENT_CONTEXT_MEMORY_FILE", ".claude/CLAUDE.md")
RULES_DIR = ROOT / os.environ.get("AGENT_CONTEXT_RULES_DIR", ".claude/rules")

FRONTMATTER_PATHS = re.compile(r"^\s*paths\s*:", re.MULTILINE)


def read_text(path: Path) -> str | None:
    """Read a file, returning None on any IO or decoding problem.

    A hook must not crash on a half-written file or a stray binary.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def line_count(text: str) -> int:
    return len(text.splitlines())


def is_path_scoped(text: str) -> bool:
    """True when the file opens with YAML frontmatter that declares ``paths:``.

    Frontmatter is a leading ``---`` line, then keys, then a closing ``---``.
    Only the frontmatter block is searched, so a ``paths:`` mentioned in the
    prose below does not count as scoping.
    """
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end == -1:
        return False
    return FRONTMATTER_PATHS.search(text[3:end]) is not None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_memory_file(warnings: list[str]) -> None:
    text = read_text(MEMORY_FILE) if MEMORY_FILE.is_file() else None
    if text is None:
        return
    n = line_count(text)
    if n < HARD_LIMIT:
        return
    warnings.append(
        f"{rel(MEMORY_FILE)} is {n} lines, target is under {HARD_LIMIT}. "
        "This file is loaded on every turn. Move one cohesive section into a "
        "scoped rule file and leave a one-line pointer to it."
    )


def check_rules(warnings: list[str]) -> None:
    if not RULES_DIR.is_dir():
        return
    for rule in sorted(RULES_DIR.glob("*.md")):
        text = read_text(rule)
        if text is None:
            continue
        n = line_count(text)
        scoped = is_path_scoped(text)
        limit = SOFT_LIMIT if scoped else HARD_LIMIT
        if n < limit:
            continue
        if scoped:
            advice = (
                "It is path-scoped, so it only costs context on matching files, "
                "but it is now long enough to split. Move a sub-topic into a "
                "sibling rule with a narrower paths glob."
            )
        else:
            advice = (
                "It has no paths: frontmatter, so it loads at launch like the "
                "memory file. Add a paths glob to scope it, or split it."
            )
        warnings.append(f"{rel(rule)} is {n} lines, target is under {limit}. {advice}")


def main() -> int:
    # The Stop hook receives JSON on stdin. This hook does not need it, but it
    # drains the pipe so the caller never blocks on a full buffer.
    if not sys.stdin.isatty():
        try:
            sys.stdin.read()
        except (OSError, ValueError):
            pass

    warnings: list[str] = []
    check_memory_file(warnings)
    check_rules(warnings)

    if not warnings:
        return 0

    sys.stderr.write(
        "Context budget: some always-loaded files have grown past their target.\n"
        + "".join(f"  - {w}\n" for w in warnings)
        + "This is a reminder, not a block. Split when you next touch the file.\n"
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - a hook must never crash a session
        sys.stderr.write(f"check-context-size: skipped, {exc}\n")
        sys.exit(0)
