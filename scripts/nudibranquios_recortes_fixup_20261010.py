#!/usr/bin/env python3
"""Reprocesa recortes problemáticos: mejor fuente, alpha-matting, CCA, limpieza color."""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import new_session, remove
from scipy import ndimage

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
FOTOS = PAPER / "fotos"
FOTOS_LG = PAPER / "fotos_poster"
OUT = PAPER / "recortes"
META = OUT / "meta_recortes_20261010.json"
UA = "BioFaunaNudiRecortes/2026-10 (yespi.es; educational)"

# Preferencias de fuente + flags
FIX = {
    "Peltodoris atromaculata": {"prefer": "thumb", "model": "u2net", "alpha": True},
    "Cratena peregrina": {"prefer": "large", "model": "isnet-general-use", "alpha": True, "debrown": True},
    "Paradoris indecora": {"prefer": "redownload", "model": "isnet-general-use", "alpha": True, "taxon": 489147},
    "Antiopella cristata": {"prefer": "large", "model": "u2net", "alpha": True, "cca": True},
    "Calmella cavolini": {"prefer": "large", "model": "isnet-general-use", "alpha": True, "debrown": True},
    "Felimare tricolor": {"prefer": "large", "model": "u2net", "alpha": True, "cca": True},
    "Felimare fontandraui": {"prefer": "large", "model": "u2net", "alpha": True, "degreen": True},
    "Polycera quadrilineata": {"prefer": "large", "model": "isnet-general-use", "alpha": True},
    "Diaphorodoris papillata": {"prefer": "large", "model": "u2net", "alpha": True, "cca": True},
}


def slug(sp: str) -> str:
    return sp.replace(" ", "_").lower()


def soft_outline_and_shadow(rgba: Image.Image, pad: int = 28) -> Image.Image:
    arr = np.asarray(rgba)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        return rgba
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    crop = rgba.crop((x0, y0, x1, y1))
    cw, ch = crop.size
    canvas_w, canvas_h = cw + 2 * pad, ch + 2 * pad
    mask = crop.split()[-1]
    shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    sh = mask.point(lambda a: int(a * 0.38)).filter(ImageFilter.GaussianBlur(radius=7))
    shadow_layer = Image.new("RGBA", (cw, ch), (20, 35, 45, 255))
    shadow_layer.putalpha(sh)
    shadow.paste(shadow_layer, (pad + 4, pad + 6), shadow_layer)
    outline = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    om = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius=1.2))
    cream = Image.new("RGBA", (cw, ch), (248, 250, 252, 255))
    cream.putalpha(om.point(lambda a: min(255, int(a * 0.85))))
    outline.paste(cream, (pad, pad), cream)
    subject = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    subject.paste(crop, (pad, pad), crop)
    return Image.alpha_composite(Image.alpha_composite(shadow, outline), subject)


def keep_largest_component(rgba: Image.Image, thr: int = 20) -> Image.Image:
    a = np.asarray(rgba.split()[-1])
    lab, n = ndimage.label(a > thr)
    if n <= 1:
        return rgba
    counts = np.bincount(lab.ravel())
    counts[0] = 0
    keep = counts.argmax()
    mask = (lab == keep).astype(np.uint8) * 255
    # dilatar un poco para no perder antenas finas conectadas por puentes débiles
    mask = ndimage.binary_dilation(mask > 0, iterations=1).astype(np.uint8) * 255
    out = rgba.copy()
    out.putalpha(Image.fromarray(np.minimum(a, mask)))
    return out


def remove_brown_substrate(rgba: Image.Image) -> Image.Image:
    """Quita píxeles marrón/verde oliva típicos de hidrarios/algas (no animal)."""
    arr = np.asarray(rgba).copy()
    rgb = arr[:, :, :3].astype(np.float32)
    a = arr[:, :, 3]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    sat = (mx - mn) / (mx + 1e-6)
    # marrón: R≈G>B o R>G>B, no muy saturado de magenta/rojo puro
    brown = (r > 55) & (g > 40) & (b < 0.85 * g) & (r > b + 15) & (sat < 0.55) & (mx < 200)
    # verde oliva
    olive = (g > r) & (g > b) & (g > 40) & (sat < 0.45) & (mx < 180)
    # blancos/rosas/naranjas vivos del animal: proteger
    animalish = ((r > 180) & (g > 160) & (b > 150)) | ((r > 160) & (g < 120) & (b < 120)) | (
        (r > 140) & (b > 140) & (g < 160)
    )
    kill = (brown | olive) & (~animalish) & (a > 10)
    # solo si el píxel no es parte del núcleo denso del animal (erosionar kill hacia bordes)
    a2 = a.copy()
    a2[kill] = 0
    arr[:, :, 3] = a2
    return Image.fromarray(arr, "RGBA")


def remove_green_algae(rgba: Image.Image) -> Image.Image:
    arr = np.asarray(rgba).copy()
    rgb = arr[:, :, :3].astype(np.float32)
    a = arr[:, :, 3]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = (g > r + 15) & (g > b + 10) & (g > 50)
    # proteger azul del felimare
    blue = (b > r + 20) & (b > g + 10)
    yellow = (r > 150) & (g > 130) & (b < 100)
    kill = green & (~blue) & (~yellow) & (a > 10)
    a2 = a.copy()
    a2[kill] = 0
    arr[:, :, 3] = a2
    return Image.fromarray(arr, "RGBA")


def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def http_bytes(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=50) as r:
            return r.read()
    except Exception:
        return None


def redownload_inat(taxon_id: int, dest: Path) -> dict | None:
    """Busca foto CC limpia (preferencia Med / votos)."""
    for bbox in [
        {"swlat": 40.45, "swlng": 0.10, "nelat": 42.95, "nelng": 3.40},
        {"swlat": 35.0, "swlng": -6.0, "nelat": 45.5, "nelng": 16.0},
        {},
    ]:
        params = {
            "taxon_id": taxon_id,
            "quality_grade": "research",
            "photos": "true",
            "photo_license": "cc0,cc-by,cc-by-sa",
            "per_page": 40,
            "order_by": "votes",
            **bbox,
        }
        url = "https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)
        data = http_json(url)
        time.sleep(0.5)
        for obs in data.get("results") or []:
            photos = obs.get("photos") or []
            if not photos:
                continue
            purl = (photos[0].get("url") or "").replace("square", "large").replace("medium", "large")
            blob = http_bytes(purl)
            if not blob or len(blob) < 20000:
                continue
            dest.write_bytes(blob)
            user = obs.get("user") or {}
            return {
                "author": user.get("name") or user.get("login") or "?",
                "license": (obs.get("license_code") or "").lower(),
                "uri": obs.get("uri") or "",
                "source": "inat_redownload",
            }
    return None


def source_for(sp: str, cfg: dict) -> Path:
    s = slug(sp)
    large = FOTOS_LG / f"{s}_large.jpg"
    thumb = FOTOS / f"{s}_thumb.jpg"
    pref = cfg.get("prefer", "large")
    if pref == "thumb" and thumb.exists():
        return thumb
    if pref == "redownload":
        meta = redownload_inat(int(cfg["taxon"]), large)
        if meta:
            # actualizar crédito en meta json
            m = json.loads(META.read_text(encoding="utf-8"))
            for it in m["items"]:
                if it["species"] == sp:
                    it.update({k: meta[k] for k in ("author", "license", "uri") if k in meta})
                    it["source_file"] = large.name
                    it["note"] = "foto redescargada (mejor contraste)"
            META.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return large
    if large.exists():
        return large
    return thumb


def process(sp: str, cfg: dict, sessions: dict):
    src = source_for(sp, cfg)
    print(f"FIX {sp} ← {src.name} model={cfg.get('model')} alpha={cfg.get('alpha')}", flush=True)
    model = cfg.get("model", "u2net")
    if model not in sessions:
        sessions[model] = new_session(model, providers=["CPUExecutionProvider"])
    session = sessions[model]
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    max_side = 1000
    w, h = im.size
    if max(w, h) > max_side:
        sc = max_side / max(w, h)
        im = im.resize((int(w * sc), int(h * sc)), Image.Resampling.LANCZOS)
    kwargs = {}
    if cfg.get("alpha"):
        kwargs.update(
            dict(
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=8,
                post_process_mask=True,
            )
        )
    try:
        raw = remove(im, session=session, **kwargs)
    except Exception as e:
        print(f"  alpha falló ({e}); sin alpha", flush=True)
        raw = remove(im, session=session, post_process_mask=True)
    if raw.mode != "RGBA":
        raw = raw.convert("RGBA")
    if cfg.get("cca", True):
        raw = keep_largest_component(raw)
    if cfg.get("debrown"):
        raw = remove_brown_substrate(raw)
        raw = keep_largest_component(raw)
    if cfg.get("degreen"):
        raw = remove_green_algae(raw)
        raw = keep_largest_component(raw)
    dest_raw = OUT / f"{slug(sp)}_cutout_raw.png"
    dest = OUT / f"{slug(sp)}_cutout.png"
    raw.save(dest_raw, "PNG", optimize=True)
    styled = soft_outline_and_shadow(raw)
    styled.save(dest, "PNG", optimize=True)
    a = np.asarray(styled.split()[-1])
    print(f"  → {dest.name} {styled.size} fg={float((a>20).mean()):.3f}", flush=True)


def main():
    # scipy needed
    sessions = {}
    try:
        for sp, cfg in FIX.items():
            process(sp, cfg, sessions)
    finally:
        sessions.clear()
        import gc

        gc.collect()
    print("fixup done", flush=True)


if __name__ == "__main__":
    main()
