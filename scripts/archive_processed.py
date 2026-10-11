#!/usr/bin/env python3
"""Move extra photos of already-embedded species to ARCHIVE_DIR, keep SAMPLE_N locally.

Idempotent (`.archived` marker). Set IMAGES_DIR / ARCHIVE_DIR / BIOFAUNA_PATTERNS.
"""
import os
import random
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
ACTIVE = Path(os.environ.get("IMAGES_DIR", str(ROOT / "dataset/images")))
ARCHIVE = Path(os.environ.get("ARCHIVE_DIR", str(ROOT / "dataset/photo_archive")))
_pats = (ROOT / "dataset/patterns", ROOT / "data/patterns")
PAT = Path(os.environ.get("BIOFAUNA_PATTERNS", str(next((p for p in _pats if p.exists()), _pats[-1]))))
SAMPLE_N = 300

if not ACTIVE.exists():
    raise SystemExit(f"IMAGES_DIR does not exist: {ACTIVE}")

moved = freed = 0
for d in sorted(ACTIVE.iterdir()):
    if not d.is_dir():
        continue
    slug = d.name
    if not (PAT / slug / "prototype.npy").exists():
        continue
    if (d / ".archived").exists():
        continue
    jpgs = sorted(d.glob("*.jpg"))
    if len(jpgs) <= SAMPLE_N:
        (d / ".archived").write_text("kept-local (<= muestra)")
        continue
    dest = ARCHIVE / slug
    dest.mkdir(parents=True, exist_ok=True)
    total = len(jpgs)
    names = [p.name for p in jpgs]
    for p in jpgs:
        tgt = dest / p.name
        freed += p.stat().st_size
        if tgt.exists():
            p.unlink()
        else:
            shutil.move(str(p), str(tgt))
    keep = random.sample(names, SAMPLE_N)
    for nm in keep:
        shutil.copy2(dest / nm, d / nm)
    (d / ".archived").write_text(
        f"archived {total} -> {dest}; muestra {SAMPLE_N} local {datetime.now().isoformat()}"
    )
    moved += 1
    print(f"  {slug}: {total} archivadas, {SAMPLE_N} muestra local", flush=True)

print(f"=== {moved} especies archivadas, ~{freed // 1048576} MB movidos ===", flush=True)
