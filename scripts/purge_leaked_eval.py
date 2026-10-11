#!/usr/bin/env python3
"""Saca del eval las filas cuya foto ya está en la galería de su especie (fuga), 23-sep-2026.
Entrada: dataset/leak_audit_20260923.jsonl (scripts/leak_audit_calib.py, embedding global vs galería).
Umbral por defecto 0.98 (copias exactas 0.995-0.999; reescalados/recortes de la misma foto >=0.98).
Aplica a calib_raw.jsonl (entrada de rescore) y calib_raw_t05.jsonl (entrada de fit_calib/gen_stats).
Las filas quitadas se guardan en dataset/calib_raw_leaked_20260923.jsonl (no se borra nada).
Backup en dataset/bak_purge_leak_<ts>/. Uso: python3 scripts/purge_leaked_eval.py [--thr 0.98] [--dry-run]"""
import argparse, json, shutil, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import contextlib, os
try:
    from calib_lock import calib_write_lock
except ImportError:  # public repo: no multi-session lock
    calib_write_lock = lambda name: contextlib.nullcontext()

D = Path(os.environ.get("BIOFAUNA_ROOT", ".")) / "dataset"
ap = argparse.ArgumentParser(); ap.add_argument("--thr", type=float, default=0.98); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
leak = {(int(x["obs"]), x["true"]) for x in map(json.loads, open(D / "leak_audit_20260923.jsonl")) if x["max_sim"] >= a.thr}
print(f"filas con fuga (>= {a.thr}): {len(leak)}")
with calib_write_lock("purge_leaked_eval.py"):
    bak = D / f"bak_purge_leak_{time.strftime('%Y%m%d_%H%M%S')}"
    if not a.dry_run: bak.mkdir()
    for name in ("calib_raw.jsonl", "calib_raw_t05.jsonl"):
        p = D / name
        rows = [l for l in p.read_text().splitlines() if l.strip()]
        keep, out = [], []
        for l in rows:
            r = json.loads(l)
            (out if (int(r["obs"]), r["true"]) in leak else keep).append(l)
        sp_before = {json.loads(l)["true"] for l in rows}; sp_after = {json.loads(l)["true"] for l in keep}
        print(f"{name}: {len(rows)} -> {len(keep)} (quitadas {len(out)}); especies con eval {len(sp_before)} -> {len(sp_after)}")
        if a.dry_run: continue
        shutil.copy2(p, bak / name)
        if name == "calib_raw_t05.jsonl":
            (D / "calib_raw_leaked_20260923.jsonl").write_text("\n".join(out) + "\n")
        tmp = p.with_suffix(".tmp"); tmp.write_text("\n".join(keep) + "\n"); tmp.replace(p)
    if not a.dry_run: print("backup:", bak)
