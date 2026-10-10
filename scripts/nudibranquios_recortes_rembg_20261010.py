#!/usr/bin/env python3
"""Recortes estilo guía: nudibranquio sin fondo + sombra/contorno suave.

CPU only (rembg / onnxruntime). Prefer fotos_poster/*_large.jpg; si faltan, thumbs.
Salida: papers/nudibranquios_calendario/recortes/{slug}_cutout.png + meta JSON.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Forzar CPU antes de importar onnxruntime / rembg
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "4"

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
FOTOS = PAPER / "fotos"
FOTOS_LG = PAPER / "fotos_poster"
OUT = PAPER / "recortes"
META_THUMBS = PAPER / "datos/fotos_meta_20261010.json"
META_POSTER = PAPER / "datos/poster_lamina4_meta_20261010.json"
META_OUT = OUT / "meta_recortes_20261010.json"

# Top 16 del póster (mismo orden que especies_mensual_normalizado)
TOP16 = [
    "Cratena peregrina",
    "Flabellina affinis",
    "Peltodoris atromaculata",
    "Felimare picta",
    "Edmundsella pedata",
    "Felimare tricolor",
    "Calmella cavolini",
    "Diaphorodoris papillata",
    "Paradoris indecora",
    "Antiopella cristata",
    "Polycera quadrilineata",
    "Rudmania krohni",
    "Nemesignis banyulensis",
    "Diaphorodoris alba",
    "Facelina annulicornis",
    "Felimare fontandraui",
]


def slugify(sp: str) -> str:
    return sp.replace(" ", "_").lower()


def load_credit_map() -> dict[str, dict]:
    cred: dict[str, dict] = {}
    if META_THUMBS.exists():
        for p in json.loads(META_THUMBS.read_text(encoding="utf-8")):
            cred[p["species"]] = {
                "author": p.get("author") or "?",
                "license": p.get("license") or "",
                "uri": p.get("uri") or "",
                "source_meta": "fotos_meta",
            }
    if META_POSTER.exists():
        for p in json.loads(META_POSTER.read_text(encoding="utf-8")):
            cred[p["species"]] = {
                "author": p.get("author") or cred.get(p["species"], {}).get("author", "?"),
                "license": p.get("license") or cred.get(p["species"], {}).get("license", ""),
                "uri": p.get("uri") or cred.get(p["species"], {}).get("uri", ""),
                "source_meta": "poster_meta",
            }
    return cred


def source_path(sp: str) -> Path | None:
    slug = slugify(sp)
    large = FOTOS_LG / f"{slug}_large.jpg"
    thumb = FOTOS / f"{slug}_thumb.jpg"
    if large.exists() and large.stat().st_size > 15000:
        return large
    if thumb.exists() and thumb.stat().st_size > 5000:
        return thumb
    return None


def alpha_bbox(alpha: np.ndarray, thr: int = 8) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(alpha > thr)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def soft_outline_and_shadow(rgba: Image.Image, pad: int = 28) -> Image.Image:
    """Contorno crema suave + sombra ligera bajo el sujeto (estilo lámina de guía)."""
    arr = np.asarray(rgba).copy()
    if arr.shape[2] != 4:
        raise ValueError("se espera RGBA")
    alpha = arr[:, :, 3]
    box = alpha_bbox(alpha, thr=10)
    if box is None:
        return rgba
    x0, y0, x1, y1 = box
    crop = rgba.crop((x0, y0, x1, y1))
    cw, ch = crop.size
    canvas_w, canvas_h = cw + 2 * pad, ch + 2 * pad
    # sombra (desplazada)
    mask = crop.split()[-1]
    shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    sh = Image.new("L", (cw, ch), 0)
    sh.paste(mask, (0, 0))
    sh = sh.point(lambda a: int(a * 0.38))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=7))
    shadow_layer = Image.new("RGBA", (cw, ch), (20, 35, 45, 255))
    shadow_layer.putalpha(sh)
    shadow.paste(shadow_layer, (pad + 4, pad + 6), shadow_layer)

    # contorno suave (dilatar máscara)
    outline = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    om = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius=1.2))
    cream = Image.new("RGBA", (cw, ch), (248, 250, 252, 255))
    cream.putalpha(om.point(lambda a: min(255, int(a * 0.85))))
    outline.paste(cream, (pad, pad), cream)

    # sujeto
    subject = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    subject.paste(crop, (pad, pad), crop)

    out = Image.alpha_composite(shadow, outline)
    out = Image.alpha_composite(out, subject)
    return out


def qa_stats(rgba: Image.Image) -> dict:
    a = np.asarray(rgba.split()[-1])
    fg = a > 20
    frac = float(fg.mean()) if a.size else 0.0
    # trozos de fondo: componentes? proxy = alpha parcial en bordes del bbox
    box = alpha_bbox(a, 20)
    edge_leak = 0.0
    if box:
        x0, y0, x1, y1 = box
        border = np.zeros_like(a, dtype=bool)
        border[y0:y1, x0] = True
        border[y0:y1, x1 - 1] = True
        border[y0, x0:x1] = True
        border[y1 - 1, x0:x1] = True
        edge_leak = float(a[border].mean() / 255.0) if border.any() else 0.0
    return {
        "fg_frac": round(frac, 4),
        "edge_alpha_mean": round(edge_leak, 4),
        "size": list(rgba.size),
    }


def remove_bg(session, im: Image.Image) -> Image.Image:
    from rembg import remove

    # limitar tamaño de entrada para CPU (mantener detalle)
    max_side = 900
    w, h = im.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    im = ImageOps.exif_transpose(im).convert("RGB")
    out = remove(im, session=session)
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    return out


def process_one(session, sp: str, cred: dict) -> dict | None:
    src = source_path(sp)
    if src is None:
        return {"species": sp, "ok": False, "error": "sin foto fuente"}
    slug = slugify(sp)
    dest = OUT / f"{slug}_cutout.png"
    dest_raw = OUT / f"{slug}_cutout_raw.png"
    print(f"recorte: {sp} ← {src.name}", flush=True)
    im = Image.open(src)
    raw = remove_bg(session, im)
    raw.save(dest_raw, "PNG", optimize=True)
    styled = soft_outline_and_shadow(raw)
    styled.save(dest, "PNG", optimize=True)
    meta = {
        "species": sp,
        "ok": True,
        "source_file": src.name,
        "cutout": dest.name,
        "cutout_raw": dest_raw.name,
        "author": cred.get("author", "?"),
        "license": cred.get("license", ""),
        "uri": cred.get("uri", ""),
        "qa": qa_stats(styled),
        "engine": "rembg/u2net CPU",
    }
    print(
        f"  → {dest.name} {styled.size} fg={meta['qa']['fg_frac']} "
        f"crédito={meta['author']} · {meta['license']}",
        flush=True,
    )
    return meta


def main(species: list[str] | None = None):
    OUT.mkdir(parents=True, exist_ok=True)
    from rembg import new_session
    import onnxruntime as ort

    providers = ["CPUExecutionProvider"]
    # Azure EP a veces aparece primero; forzar CPU
    print("onnx providers disponibles:", ort.get_available_providers(), flush=True)
    print("usando:", providers, flush=True)
    session = new_session("u2net", providers=providers)

    creds = load_credit_map()
    spp = species or TOP16
    results = []
    try:
        for sp in spp:
            results.append(process_one(session, sp, creds.get(sp) or {}))
    finally:
        # liberar sesión / refs
        del session
        try:
            import gc

            gc.collect()
        except Exception:
            pass

    payload = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M %Z"),
        "engine": "rembg u2net CPU",
        "n": len(results),
        "items": results,
    }
    META_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # README créditos
    lines = [
        "# Recortes estilo guía (sin fondo)",
        f"Generado: {payload['generated']} · rembg u2net CPU",
        "",
        "PNG con transparencia, contorno crema suave y sombra ligera.",
        "Créditos heredados de la foto fuente (CC0 / CC BY / CC BY-SA).",
        "",
    ]
    for r in results:
        if not r or not r.get("ok"):
            lines.append(f"- *{r.get('species','?')}*: FALLO — {r.get('error')}")
            continue
        lines.append(
            f"- *{r['species']}*: `{r['cutout']}` · {r['author']} · {r['license']}"
            + (f" · {r['uri']}" if r.get("uri") else "")
        )
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok = sum(1 for r in results if r and r.get("ok"))
    print(f"OK {ok}/{len(results)} → {OUT}", flush=True)
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    only = sys.argv[1:]
    raise SystemExit(main(only if only else None))
