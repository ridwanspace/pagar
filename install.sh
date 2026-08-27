#!/usr/bin/env bash
# pagar installer. Copies the gate runner into a project, with no dependencies.
#
# Usage:
#   ./install.sh [target-dir] [--starter]
#
#   target-dir   Where to install. Default: the current directory.
#   --starter    Also copy the starter kit (specs pipeline, rules, skills).
#                Without it you get gates/ only, which is the right start.
#
# Environment:
#   PAGAR_SRC    Directory containing a pagar checkout (skips the download).
#   PAGAR_URL    Tarball URL to fetch from. Default: the ridwanspace/pagar
#                GitHub main branch tarball.
#
# Exit codes: 0 ok, 1 usage/environment error, 2 download error.
set -euo pipefail

REPO_URL_DEFAULT="https://github.com/ridwanspace/pagar/archive/refs/heads/main.tar.gz"
TARGET="."
WANT_STARTER=0

for arg in "$@"; do
  case "$arg" in
    --starter) WANT_STARTER=1 ;;
    -h|--help)
      sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    -*) printf 'install.sh: unknown option %s\n' "$arg" >&2; exit 1 ;;
    *) TARGET="$arg" ;;
  esac
done

say()  { printf '%s\n' "$*"; }
die()  { printf 'install.sh: %s\n' "$*" >&2; exit "${2:-1}"; }

mkdir -p -- "$TARGET" || die "cannot create target directory '$TARGET'" 1

# Locate a pagar source: an explicit checkout, this checkout, or a download.
SRC="${PAGAR_SRC:-}"
if [ -z "$SRC" ]; then
  script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  [ -f "$script_dir/gates/run-gates.mjs" ] && SRC="$script_dir"
fi
TMPDIR_INSTALL=""
cleanup() { [ -n "$TMPDIR_INSTALL" ] && rm -rf "$TMPDIR_INSTALL"; return 0; }
trap cleanup EXIT

if [ -z "$SRC" ]; then
  command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 \
    || die "need curl or wget to download pagar (or set PAGAR_SRC to a local checkout)" 1
  TMPDIR_INSTALL=$(mktemp -d)
  say ">> downloading pagar"
  URL="${PAGAR_URL:-$REPO_URL_DEFAULT}"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" | tar -xz -C "$TMPDIR_INSTALL" \
      || die "download failed: $URL" 2
  else
    wget -qO- "$URL" | tar -xz -C "$TMPDIR_INSTALL" \
      || die "download failed: $URL" 2
  fi
  SRC=$(find "$TMPDIR_INSTALL" -mindepth 1 -maxdepth 1 -type d | head -n 1)
  [ -n "$SRC" ] && [ -f "$SRC/gates/run-gates.mjs" ] \
    || die "downloaded archive did not contain gates/run-gates.mjs" 2
fi

[ -f "$SRC/gates/run-gates.mjs" ] || die "no gates/ under PAGAR_SRC='$SRC'" 1

say ">> installing gates/ into $TARGET"
mkdir -p "$TARGET/gates"
cp -R "$SRC/gates/." "$TARGET/gates/"

if [ "$WANT_STARTER" -eq 1 ]; then
  say ">> installing starter/ into $TARGET"
  cp -R "$SRC/starter/." "$TARGET/"
fi

# Never clobber an existing config; the user owns it.
if [ ! -f "$TARGET/gates.config.json" ] \
   && [ ! -f "$TARGET/gates/gates.config.json" ] \
   && [ ! -f "$TARGET/.gates.json" ]; then
  cp "$SRC/gates/gates.config.example.json" "$TARGET/gates.config.json"
  CONFIG_COPIED=1
else
  CONFIG_COPIED=0
fi

# pagar runs on Node 20+. A missing node is not fatal to the copy, but say so.
if command -v node >/dev/null 2>&1; then
  node_major=$(node -p 'process.versions.node.split(".")[0]')
  [ "$node_major" -ge 20 ] 2>/dev/null \
    || say "!! node $node_major found; gates need Node 20 or newer"
else
  say "!! node not found; gates need Node 20 or newer"
fi

say ""
say ">> done. Next:"
if [ "$CONFIG_COPIED" -eq 1 ]; then
  say "     1. edit gates.config.json: name your lint, type-check, and test commands"
else
  say "     1. review your existing gates config"
fi
say "     2. node gates/run-gates.mjs --update-baseline   # from a clean tree"
say "     3. commit the baseline, then:  node gates/run-gates.mjs"
if [ "$WANT_STARTER" -eq 1 ]; then
  say ""
  say "     starter kit: read starter/README.md for the adoption order."
  say "     it is a menu, not a bundle. take only what you need."
fi
