#!/usr/bin/env python3
"""Auditoría de fuga eval->galería (23-sep-2026).
Para cada fila de calib_raw_t05.jsonl embebe la foto de eval (calib_photos/<obs>.jpg) SIN fusion ROI
(global, igual que las fotos de galería) y mide la similitud máxima con la galería de su propia especie
(patterns/<slug>/embeddings.npy). >=0.995 = la misma imagen está en la galería (fuga: el k-NN se encuentra
a sí mismo). Salida reanudable: dataset/leak_audit_20260923.jsonl  {obs,true,max_sim,argmax}
Uso: python3 -u scripts/leak_audit_calib.py [--workers 2]"""
import argparse, json, sys, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import io, os, time, urllib.request, uuid
EMBED_URL = os.environ.get("BIOFAUNA_EMBED_URL", "http://127.0.0.1:8090/embed")  # a running identify service with /embed
log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)
def embed(im):
    """Global embedding of the whole image (no TTA, no ROI fusion) -- same as the gallery."""
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=92); b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode() + buf.getvalue() + f"\r\n--{b}--\r\n".encode()
    r = urllib.request.urlopen(urllib.request.Request(EMBED_URL, data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"}), timeout=60).read()
    import json as _j; v = np.array(_j.loads(r)["vec"], dtype="float32").reshape(-1); return v / max(np.linalg.norm(v), 1e-9)

D = Path(os.environ.get("BIOFAUNA_ROOT", ".")) / "dataset"; OUT = D / "leak_audit_20260923.jsonl"
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=2); a = ap.parse_args()
rows = [json.loads(l) for l in open(D / "calib_raw_t05.jsonl") if l.strip()]
done = {(json.loads(l)["obs"], json.loads(l)["true"]) for l in open(OUT)} if OUT.exists() else set()
todo = [r for r in rows if (r["obs"], r["true"]) not in done]
todo.sort(key=lambda r: r["true"])  # agrupa por especie para aprovechar la caché de galería
log(f"filas: {len(rows)} hechas: {len(done)} pendientes: {len(todo)}")
G, glock, wlock = {}, threading.Lock(), threading.Lock()
fo = open(OUT, "a")

def gal(sl):
    with glock:
        if sl not in G:
            if len(G) > 64: G.clear()
            try:
                g = np.load(D / "patterns" / sl / "embeddings.npy").astype("float32")
                G[sl] = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
            except Exception:
                G[sl] = None
        return G[sl]

def one(r):
    p = D / "calib_photos" / f"{r['obs']}.jpg"
    if not p.exists(): return None
    try: v = embed(Image.open(p).convert("RGB"))
    except Exception: return None
    g = gal(r["true"])
    if g is None or not len(g): return None
    s = g @ v; i = int(s.argmax())
    rec = {"obs": r["obs"], "true": r["true"], "max_sim": round(float(s[i]), 5), "argmax": i}
    with wlock: fo.write(json.dumps(rec) + "\n")
    return rec

n = 0
with ThreadPoolExecutor(a.workers) as ex:
    for rec in ex.map(one, todo):
        n += 1
        if n % 1000 == 0: fo.flush(); log(f"  {n}/{len(todo)}")
fo.close()
A = [json.loads(l) for l in open(OUT)]
s = np.array([x["max_sim"] for x in A])
log(f"HECHO: {len(A)} filas auditadas; >=0.995 (misma imagen en galería): {(s >= 0.995).sum()} ({(s >= 0.995).mean():.1%})")
