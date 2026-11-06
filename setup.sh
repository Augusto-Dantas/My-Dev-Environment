#!/usr/bin/env bash
set -Eeuo pipefail
REPO="Augusto-Dantas/My-Dev-Environment"
REF="${DEVBOX_REF:-main}"
ROOT="${DEVBOX_HOME:-$HOME/.local/share/my-dev-environment}"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$ROOT" "$BIN_DIR"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
URL="https://raw.githubusercontent.com/$REPO/$REF/setup.py?cachebust=$(date +%s)"
command -v python3 >/dev/null || { echo "Python 3 is required to run the setup TUI." >&2; exit 1; }
curl -fsSL "$URL" -o "$TMP"
PYTHON_BIN="python3"
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
    command -v python3 >/dev/null || { echo "Python 3 is required." >&2; exit 1; }
    python3 -m venv "$ROOT/installer-venv" || {
        echo "Python venv support is required. Install python3-venv and retry." >&2
        exit 1
    }
    PYTHON_BIN="$ROOT/installer-venv/bin/python"
    "$PYTHON_BIN" -m pip install --quiet --upgrade pip PyYAML
fi
"$PYTHON_BIN" "$TMP" --root "$ROOT" --repo "https://github.com/$REPO.git" --ref "$REF" --bin-dir "$BIN_DIR" "$@"
