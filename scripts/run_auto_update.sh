#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAYLOAD="${1:-$ROOT/data/awesome_updates.json}"
TARGET_MD="${2:-$ROOT/README.md}"

if [[ ! -f "$PAYLOAD" ]]; then
  echo "Payload not found: $PAYLOAD"
  exit 2
fi

python3 "$ROOT/scripts/update_awesome_md.py" --md "$TARGET_MD" --json "$PAYLOAD"

git -C "$ROOT" add "$TARGET_MD"
if ! git -C "$ROOT" diff --cached --quiet -- "$TARGET_MD"; then
  git -C "$ROOT" commit -m "Auto-update awesome OCR LLM README"
  git -C "$ROOT" push origin HEAD
else
  echo "No changes to commit."
fi
