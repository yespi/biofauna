#!/bin/bash
# Weekly dry-run of taxonomy_nomenclature_audit.py
# Crontab:  15 3 * * 0  BIOFAUNA_ROOT=/path/to/biofauna  scripts/taxonomy_nomenclature_cron.sh
set -euo pipefail
ROOT="${BIOFAUNA_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
LOCK="${TMPDIR:-/tmp}/taxonomy_nomenclature_cron.lock"
LOG="$ROOT/logs/nomenclature_audit_cron.log"
mkdir -p "$ROOT/logs"

exec 200>"$LOCK"
flock -n 200 || { echo "$(date '+%F %T') [skip] already running" >> "$LOG"; exit 0; }

cd "$ROOT"
echo "=== $(date '+%F %T') nomenclature_audit_cron START ===" >> "$LOG"
OUT="dataset/nomenclature_audit_$(date +%Y%m%d).json"
python3 -u scripts/taxonomy_nomenclature_audit.py --dry-run --out "$OUT" >> "$LOG" 2>&1
# Recurrent --apply-safe: leave commented until you accept automatic renames.
# python3 -u scripts/taxonomy_nomenclature_audit.py --apply-safe --out "$OUT" >> "$LOG" 2>&1
echo "=== $(date '+%F %T') nomenclature_audit_cron DONE -> $OUT ===" >> "$LOG"
