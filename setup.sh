#!/usr/bin/env bash
set -Eeuo pipefail
REPO="Augusto-Dantas/My-Dev-Environment"
REF="${DEVBOX_REF:-feat/devbox-project-scaffolding}"
ROOT="${DEVBOX_HOME:-$HOME/.local/share/my-dev-environment}"
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$ROOT" "$BIN_DIR"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
URL="https://raw.githubusercontent.com/$REPO/$REF/setup.py?cachebust=$(date +%s)"
command -v python3 >/dev/null || { echo "Python 3 is required to run the setup TUI." >&2; exit 1; }
curl -fsSL "$URL" -o "$TMP"
python3 "$TMP" --root "$ROOT" --repo "https://github.com/$REPO.git" --ref "$REF" --bin-dir "$BIN_DIR"
