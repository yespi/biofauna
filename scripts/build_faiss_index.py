#!/usr/bin/env python3
"""Construye índice FAISS desde patterns/ para k-NN acelerado.

Salida por defecto: dataset/faiss_index/ (producción).
Para checkpoints intermedios: --out dataset/faiss_index_staging
"""
from __future__ import annotations

import os

import argparse
import json
import time
from pathlib import Path

import faiss
import numpy as np


def build_faiss(pat: Path, out: Path) -> dict:
    """Replica EXACTAMENTE el orden y el índice gi de load_protos() en identify_service.py.

    Indexa especie a especie (index.add incremental) en vez de acumular todos los
    embeddings en una lista + np.concatenate: esa versión duplicaba el pico de
    memoria (lista completa + array concatenado + copia interna de FAISS
    coexistiendo) y provocaba OOM-kill con el catálogo ya en ~778k vectores."""
    print("Cargando embeddings...", flush=True)
    t0 = time.time()
    names: list[str] = []
    sids: list[int] = []
    index: "faiss.IndexFlatIP | None" = None
    first_vec: np.ndarray | None = None
    n_total = 0
    gi = 0
    for d in sorted(pat.iterdir()):
        if not (d / "prototype.npy").exists():
            continue
        ef = d / "embeddings.npy"
        if ef.exists():
            e = np.load(ef).astype("float32")
            if index is None:
                index = faiss.IndexFlatIP(e.shape[1])
                first_vec = e[0:1].copy()
            index.add(e)
            names.append(d.name)
            sids.extend([gi] * len(e))
            n_total += len(e)
        gi += 1
    if index is None:
        raise SystemExit(f"ERROR: sin embeddings en {pat}")

    y = np.array(sids, dtype="int64")
    print(
        f"  {len(names)} spp, {n_total} embs, dim={index.d} in {time.time() - t0:.0f}s",
        flush=True,
    )

    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "knn.index"))
    np.save(out / "species_ids.npy", y)
    json.dump(names, open(out / "species_names.json", "w"))

    d, i = index.search(first_vec, 5)
    top_slug = names[i[0][0]] if i[0][0] < len(names) else "?"
    print(f"✅ FAISS listo en {out}. Top-1 test: {top_slug}", flush=True)
    return {
        "species_with_embeddings": len(names),
        "vectors": int(n_total),
        "dim": int(index.d),
        "top1_test": top_slug,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Construye índice FAISS desde patterns/")
    ap.add_argument(
        "--root",
        default=os.environ.get("BIOFAUNA_ROOT", str(Path(__file__).resolve().parents[1])),
        help="Repo root (BIOFAUNA_ROOT or this repository)",
    )
    ap.add_argument(
        "--out",
        default="",
        help="Directorio salida (default: <root>/dataset/faiss_index)",
    )
    args = ap.parse_args()

    root = Path(args.root)
    pat = root / "dataset/patterns"
    if not pat.exists():
        pat = root / "data/patterns"
    out = Path(args.out) if args.out else root / "dataset/faiss_index"
    build_faiss(pat, out)


if __name__ == "__main__":
    main()
