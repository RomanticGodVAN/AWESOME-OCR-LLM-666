#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER_DAILY_ROOT="${PAPER_DAILY_ROOT:-/Users/vlrlab/projects/paper-daily-666}"
PAYLOAD="$ROOT/data/awesome_updates.json"
README_MD="$ROOT/README.md"

if [[ -d "$PAPER_DAILY_ROOT/.git" ]]; then
  git -C "$PAPER_DAILY_ROOT" pull --ff-only origin main
else
  echo "paper-daily repo not found: $PAPER_DAILY_ROOT" >&2
  exit 2
fi

python3 "$ROOT/scripts/sync_from_paper_daily.py" \
  --paper-daily-root "$PAPER_DAILY_ROOT" \
  --out "$PAYLOAD"

bash "$ROOT/scripts/run_auto_update.sh" "$PAYLOAD" "$README_MD"
