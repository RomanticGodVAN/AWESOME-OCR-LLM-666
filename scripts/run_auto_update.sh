#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAYLOAD="${1:-$ROOT/data/awesome_updates.json}"
TARGET_MD="${2:-$ROOT/README.md}"
PAPER_DAILY_ROOT="${PAPER_DAILY_ROOT:-/Users/vlrlab/projects/paper-daily-666}"

if [[ -d "$PAPER_DAILY_ROOT" ]]; then
  python3 "$ROOT/scripts/sync_from_paper_daily.py" \
    --paper-daily-root "$PAPER_DAILY_ROOT" \
    --out "$PAYLOAD"
fi

if [[ ! -f "$PAYLOAD" ]]; then
  echo "Payload not found: $PAYLOAD"
  exit 2
fi

python3 "$ROOT/scripts/update_awesome_md.py" --md "$TARGET_MD" --json "$PAYLOAD"

git -C "$ROOT" add "$TARGET_MD" "$PAYLOAD" scripts/run_auto_update.sh scripts/sync_from_paper_daily.py
if ! git -C "$ROOT" diff --cached --quiet; then
  git -C "$ROOT" commit -m "Auto-update awesome OCR LLM README"
  git -C "$ROOT" push origin HEAD
else
  echo "No changes to commit."
fi
