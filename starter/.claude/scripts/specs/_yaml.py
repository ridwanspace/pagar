"""A tiny YAML reader/writer for the flat `status.yaml` shape.

This tool depends on the Python standard library only, so it cannot use PyYAML.
It does not need to. `status.yaml` is written by this tool and read by this tool,
and its shape is small and fixed.

ACCEPTED SUBSET
---------------
Block mappings only, nested by two-space indentation. Every value is one of:

  - a nested block mapping (the key line has no value after the colon)
  - a plain scalar on the same line as the key
  - a quoted scalar, single or double quotes, on the same line as the key
  - a block scalar folded onto one logical value, written as `>` or `|`

Scalars are decoded like this:

  - `true` / `false` (any case) become Python bools
  - `null` / `~` / an empty value become None
  - a bare integer becomes an int
  - anything else stays a str

Comment lines (`#` at the start of the trimmed line) and blank lines are
skipped. A `#` inside a quoted scalar is kept.

NOT ACCEPTED, and rejected with a clear error rather than mangled:

  - block sequences (`- item`) and flow collections (`[a, b]`, `{a: 1}`)
  - anchors, aliases, tags, merge keys (`&x`, `*x`, `!!str`, `<<:`)
  - multiple documents in one file (`---` separators)
  - tab indentation
  - odd indentation that does not line up with a known parent level

The writer emits the same subset. It quotes any string that could be read back
as something else (a number, a bool, a null, an empty string), and it uses a
block scalar for a string with a newline in it.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["YamlSubsetError", "load_yaml", "dump_yaml"]


class YamlSubsetError(ValueError):
    """The input uses YAML this reader does not accept."""


_KEY_RE = re.compile(r"^(?P<key>[A-Za-z0-9_.\-/][^:]*?)\s*:(?P<rest>\s.*|)$")
_INT_RE = re.compile(r"^[+-]?\d+$")


def _decode_scalar(raw: str) -> Any:
    """Turn one scalar token into a Python value."""
    s = raw.strip()
    if s == "" or s in ("~", "null", "Null", "NULL"):
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if _INT_RE.match(s):
        return int(s)
    return s


def _strip_comment(line: str) -> str:
    """Drop a trailing `#` comment, but not one inside quotes."""
    out: List[str] = []
    quote: Optional[str] = None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _reject_unsupported(line: str, lineno: int) -> None:
    stripped = line.strip()
    if stripped.startswith("- "):
        raise YamlSubsetError(
            f"line {lineno}: block sequences are not supported by this YAML subset: {stripped!r}"
        )
    if stripped in ("---", "..."):
        raise YamlSubsetError(
            f"line {lineno}: multi-document YAML is not supported by this subset"
        )
    if stripped.startswith(("&", "*", "!", "<<:")):
        raise YamlSubsetError(
            f"line {lineno}: anchors, aliases, tags and merge keys are not supported: {stripped!r}"
        )
    if "\t" in line[: len(line) - len(line.lstrip())]:
        raise YamlSubsetError(f"line {lineno}: tab indentation is not supported")


def _reject_flow(value: str, lineno: int) -> None:
    """Reject a value the subset cannot represent: a flow collection, an anchor,
    an alias, or a tag. These are rejected rather than mangled into a string."""
    v = value.strip()
    if v.startswith("[") or v.startswith("{"):
        raise YamlSubsetError(
            f"line {lineno}: flow collections are not supported by this YAML subset: {v!r}"
        )
    if v[:1] in ("&", "*", "!"):
        raise YamlSubsetError(
            f"line {lineno}: anchors, aliases and tags are not supported: {v!r}"
        )


def load_yaml(text: str) -> Dict[str, Any]:
    """Parse the accepted subset into nested dicts.

    Raises YamlSubsetError on any shape outside the subset. It never guesses.
    """
    root: Dict[str, Any] = {}
    # stack of (indent, mapping) pairs, outermost first
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        i += 1
        lineno = i
        if not raw_line.strip():
            continue
        if raw_line.lstrip().startswith("#"):
            continue
        _reject_unsupported(raw_line, lineno)

        line = _strip_comment(raw_line)
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()

        m = _KEY_RE.match(body)
        if not m:
            raise YamlSubsetError(
                f"line {lineno}: expected a `key: value` mapping entry, got {body!r}"
            )
        key = m.group("key").strip()
        if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
            key = key[1:-1]
        rest = m.group("rest").strip()
        _reject_flow(rest, lineno)

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise YamlSubsetError(f"line {lineno}: indentation does not match any parent block")
        parent = stack[-1][1]

        if rest in (">", "|", ">-", "|-", ">+", "|+"):
            # Block scalar. Take every following line indented deeper than the key.
            fold = rest[0] == ">"
            chunk: List[str] = []
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    chunk.append("")
                    i += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent <= indent:
                    break
                chunk.append(nxt.strip())
                i += 1
            value: Any = (" ".join(c for c in chunk if c) if fold else "\n".join(chunk)).strip()
            parent[key] = value
            continue

        if rest == "":
            child: Dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
            continue

        parent[key] = _decode_scalar(rest)

    return root


_PLAIN_SAFE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ .,;:/()\[\]'@+&%!?*=#-]*$")


def _encode_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    s = str(value)
    if s == "":
        return '""'
    if "\n" in s:
        # dump_yaml routes multi-line strings to the block-scalar form before it
        # gets here, so this is unreachable through the public API. Raise rather
        # than return a sentinel, so a future direct caller fails loudly instead
        # of writing "None" into the file.
        raise YamlSubsetError("multi-line strings must be written as a block scalar")
    low = s.lower()
    ambiguous = (
        low in ("true", "false", "null", "~", "yes", "no", "on", "off")
        or _INT_RE.match(s) is not None
        or s[0] in "\"'#-[]{}>|*&!%@`"
        or s != s.strip()
        or ": " in s
        or s.endswith(":")
    )
    if ambiguous or not _PLAIN_SAFE_RE.match(s):
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


def dump_yaml(data: Dict[str, Any], indent: int = 0) -> str:
    """Serialize nested dicts back into the accepted subset."""
    if not isinstance(data, dict):
        raise YamlSubsetError(f"dump_yaml only writes mappings, got {type(data).__name__}")
    pad = " " * indent
    out: List[str] = []
    for key, value in data.items():
        key_s = str(key)
        if not _PLAIN_SAFE_RE.match(key_s) or ":" in key_s:
            key_s = '"' + key_s.replace('"', '\\"') + '"'
        if isinstance(value, dict):
            if value:
                out.append(f"{pad}{key_s}:")
                out.append(dump_yaml(value, indent + 2))
            else:
                # An empty mapping has no block form in this subset. Write the key
                # with no children. It reads back as None, which callers coerce.
                out.append(f"{pad}{key_s}:")
            continue
        if isinstance(value, (list, tuple, set)):
            raise YamlSubsetError(
                f"key {key_s!r}: sequences are not supported by this YAML subset"
            )
        if isinstance(value, str) and "\n" in value:
            out.append(f"{pad}{key_s}: |")
            for line in value.split("\n"):
                out.append(f"{pad}  {line}")
            continue
        out.append(f"{pad}{key_s}: {_encode_scalar(value)}")
    return "\n".join(out)
