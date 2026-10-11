#!/bin/bash
# Lightweight health check for a self-hosted BioFauna (no FotoFauna admin panel).
set -euo pipefail
ROOT="${BIOFAUNA_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
IMAGES="${IMAGES_DIR:-$ROOT/dataset/images}"
PAT="${BIOFAUNA_PATTERNS:-$ROOT/data/patterns}"
ISSUES=0
echo "=== AUDIT $(date -Is) ROOT=$ROOT ==="

echo -n "1. Photos on disk: "
if [[ -d "$IMAGES" ]]; then
  DISK=$(find "$IMAGES" -type f \( -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' \) | wc -l)
  echo "$DISK"
else
  echo "no IMAGES_DIR ($IMAGES) — skip"
fi

echo -n "2. Prototype dim: "
DIMS=$(python3 -c "import numpy as np; from pathlib import Path
p=Path('$PAT')
dims=set()
if p.exists():
  for d in sorted(p.iterdir()):
    f=d/'prototype.npy'
    if f.exists():
      dims.add(int(np.load(f).shape[-1]))
      if len(dims)>=3: break
print(','.join(str(x) for x in sorted(dims)) or 'none')")
if [[ "$DIMS" == "1024" ]]; then echo "OK 1024"; else echo "WARN $DIMS"; ISSUES=$((ISSUES+1)); fi

echo -n "3. Identify /health: "
if curl -fsS http://127.0.0.1:8090/health 2>/dev/null | grep -q '"ok"'; then echo "OK"; else echo "OFFLINE"; ISSUES=$((ISSUES+1)); fi

echo "issues=$ISSUES"
exit "$ISSUES"
