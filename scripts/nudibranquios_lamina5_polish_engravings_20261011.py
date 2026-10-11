#!/usr/bin/env python3
"""Polish L5 engravings from real cutouts → clean woodcut (flat pastel + hatch).

Does not load diffusion models. Overwrites datos/engravings_lamina5/*_woodcut.png.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from scipy import ndimage

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
MAT = PAPER / "material"
RECORTES = MAT / "recortes"
OUT_DIR = MAT / "datos/engravings_lamina5"
COMPARE_DIR = MAT / "datos/engravings_lamina5_compare"
SIZE = 520

# Hand-tuned pastel body / accent (species → (body RGB, accent RGB))
PALETTE = {
    "peltodoris_atromaculata": ((210, 205, 195), (45, 32, 24)),
    "diaphorodoris_papillata": ((235, 215, 140), (200, 95, 45)),
    "diaphorodoris_alba": ((235, 230, 220), (200, 120, 90)),
    "paradoris_indecora": ((200, 195, 185), (90, 70, 60)),
    "felimare_picta": ((90, 130, 170), (230, 200, 70)),
    "felimare_tricolor": ((70, 110, 160), (230, 210, 80)),
    "felimare_fontandraui": ((80, 100, 150), (220, 160, 70)),
    "cratena_peregrina": ((230, 225, 220), (40, 40, 45)),
    "flabellina_affinis": ((180, 120, 170), (230, 180, 200)),
    "edmundsella_pedata": ((190, 100, 150), (230, 160, 180)),
    "calmella_cavolini": ((230, 150, 120), (220, 90, 70)),
    "antiopella_cristata": ((55, 55, 60), (200, 195, 190)),
    "polycera_quadrilineata": ((235, 230, 220), (35, 35, 40)),
    "rudmania_krohni": ((120, 160, 200), (230, 210, 100)),
    "nemesignis_banyulensis": ((230, 140, 160), (220, 80, 100)),
    "facelina_annulicornis": ((230, 220, 200), (60, 50, 45)),
}

SPECIES = list(PALETTE.keys())


def load_cutout(slug: str) -> Image.Image:
    for name in (f"{slug}_cutout.png", f"{slug}_cutout_raw.png"):
        p = RECORTES / name
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(slug)


def fit_square(rgba: Image.Image, size: int) -> tuple[Image.Image, Image.Image]:
    alpha = rgba.split()[-1].point(lambda p: 255 if p > 40 else 0)
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    bbox = alpha.getbbox() or (0, 0, rgba.width, rgba.height)
    sub = rgba.crop(bbox)
    sa = alpha.crop(bbox)
    pad = int(max(sub.size) * 0.10) + 10
    c = Image.new("RGBA", (sub.width + 2 * pad, sub.height + 2 * pad), (0, 0, 0, 0))
    c.paste(sub, (pad, pad), sub)
    a = Image.new("L", c.size, 0)
    a.paste(sa, (pad, pad))
    side = max(c.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox, oy = (side - c.width) // 2, (side - c.height) // 2
    sq.paste(c, (ox, oy), c)
    asq = Image.new("L", (side, side), 0)
    asq.paste(a, (ox, oy))
    sq = sq.resize((size, size), Image.Resampling.LANCZOS)
    asq = asq.resize((size, size), Image.Resampling.NEAREST)
    asq = asq.point(lambda p: 255 if p > 80 else 0)
    return sq, asq


def polish(slug: str) -> Image.Image:
    body_col, accent = PALETTE[slug]
    rgba, sil = fit_square(load_cutout(slug), SIZE)
    rgb = np.asarray(rgba.convert("RGB")).astype(np.float32)
    # Heavy smooth — kill photo grain
    smooth = Image.fromarray(rgb.astype(np.uint8)).filter(ImageFilter.MedianFilter(13))
    smooth = smooth.filter(ImageFilter.GaussianBlur(1.2))
    rgb = np.asarray(smooth).astype(np.float32)
    am = np.asarray(sil) > 0
    gray = rgb.mean(axis=2)

    # Flat body wash
    canvas = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    canvas[am] = np.array(body_col, dtype=np.float32)

    # Relative dark spots / features (not absolute — avoids muddy whole body)
    local = ndimage.uniform_filter(gray, size=21)
    rel_dark = am & ((local - gray) > 28) & (gray < local * 0.92)
    # Also very dark absolute cores inside silhouette
    abs_dark = am & (gray < np.percentile(gray[am], 18) if am.any() else False)
    spots = rel_dark | abs_dark
    # Clean small speckles
    spots = ndimage.binary_opening(spots, iterations=1)
    spots = ndimage.binary_closing(spots, iterations=1)
    labeled, nlab = ndimage.label(spots)

    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    base = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    base[..., :3] = np.clip(canvas, 0, 255).astype(np.uint8)
    base[..., 3] = np.asarray(sil)
    out = Image.fromarray(base, "RGBA")
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Accent midtones (cerata / stripes) — soft flat patches
    mid = am & (~spots) & (gray < np.percentile(gray[am], 45) if am.any() else False)
    mid = ndimage.binary_opening(mid, iterations=1)
    if mid.any() and slug.startswith(("felimare", "flabellina", "edmundsella", "rudmania", "nemesignis", "calmella")):
        arr = np.asarray(out).astype(np.float32)
        acc = np.array(accent, dtype=np.float32)
        arr[mid, :3] = arr[mid, :3] * 0.35 + acc * 0.65
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    do_spots = any(
        k in slug
        for k in ("peltodoris", "paradoris", "diaphorodoris", "polycera", "cratena", "antiopella")
    )
    if do_spots:
        for lab in range(1, nlab + 1):
            ys, xs = np.where(labeled == lab)
            if len(ys) < 25:
                continue
            y0, y1 = int(ys.min()), int(ys.max())
            x0, x1 = int(xs.min()), int(xs.max())
            area = (y1 - y0 + 1) * (x1 - x0 + 1)
            if area > SIZE * SIZE * 0.06 or len(ys) > SIZE * SIZE * 0.04:
                continue
            aspect = (x1 - x0 + 1) / max(1, y1 - y0 + 1)
            if aspect > 3.5 or aspect < 0.28:
                continue
            pad = 1
            if "peltodoris" in slug or "paradoris" in slug or "diaphorodoris" in slug:
                fill = (48, 34, 26, 255)
            else:
                fill = (30, 28, 26, 255)
            ld.ellipse(
                (x0 - pad, y0 - pad, x1 + pad, y1 + pad),
                fill=fill,
                outline=(18, 12, 8, 255),
                width=2,
            )
        out = Image.alpha_composite(out, layer)
    else:
        # Aeolids: accent wash on darker zones only (no blotch ellipses)
        arr = np.asarray(out).astype(np.float32)
        acc = np.array(accent + (255,), dtype=np.float32)
        shade = am & (gray < np.percentile(gray[am], 40) if am.any() else False)
        shade = ndimage.binary_opening(shade, iterations=1)
        if shade.any():
            arr[shade] = arr[shade] * 0.45 + acc * 0.55
            out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    # Light pastel parchment cast
    arr = np.asarray(out).astype(np.float32)
    wash = np.array([236, 222, 190, 255], dtype=np.float32)
    a = arr[..., 3:4] / 255.0
    arr[..., :3] = arr[..., :3] * 0.88 + wash[:3] * 0.12
    arr[..., :3] *= a
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    # Contour
    outline = sil.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 0 else 0)
    outline = outline.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3))
    eroded = sil.filter(ImageFilter.MinFilter(11))
    ring = (
        (np.asarray(sil) > 0).astype(np.int16) - (np.asarray(eroded) > 0).astype(np.int16)
    ).clip(0, 1).astype(np.uint8) * 255
    ink = np.maximum(np.asarray(outline), ring)
    ink_img = Image.merge(
        "RGBA",
        (
            Image.new("L", (SIZE, SIZE), 16),
            Image.new("L", (SIZE, SIZE), 10),
            Image.new("L", (SIZE, SIZE), 6),
            Image.fromarray(ink),
        ),
    )

    # Hand hatch: only in outer shade ring + underside (not full body)
    dist = ndimage.distance_transform_edt(np.asarray(sil) > 0)
    maxd = dist.max() or 1
    shade = (np.asarray(sil) > 0) & ((dist / maxd < 0.35) | (np.indices((SIZE, SIZE))[0] > SIZE * 0.62))
    hatch = Image.new("L", (SIZE, SIZE), 0)
    hd = ImageDraw.Draw(hatch)
    rng = np.random.default_rng(abs(hash(slug)) % 10_000)
    step = 10
    for y0 in range(0, SIZE, step):
        wob0 = int(rng.integers(-2, 3))
        for x0 in range(wob0, SIZE + SIZE, step):
            pts = []
            for t in range(0, step + 9):
                xx = x0 + t + int(rng.integers(-1, 2))
                yy = y0 + t
                if 0 <= xx < SIZE and 0 <= yy < SIZE and shade[yy, xx]:
                    pts.append((xx, yy))
                else:
                    if len(pts) >= 3:
                        hd.line(pts, fill=140, width=1)
                    pts = []
            if len(pts) >= 3:
                hd.line(pts, fill=140, width=1)

    hatch_img = Image.merge(
        "RGBA",
        (
            Image.new("L", (SIZE, SIZE), 22),
            Image.new("L", (SIZE, SIZE), 14),
            Image.new("L", (SIZE, SIZE), 10),
            hatch.point(lambda p: int(p * 0.75)),
        ),
    )
    out = Image.alpha_composite(out, hatch_img)
    out = Image.alpha_composite(out, ink_img)
    r, g, b, _ = out.split()
    out = Image.merge("RGBA", (r, g, b, sil))
    # Slight contrast for print
    rgb2 = ImageEnhance.Contrast(out.convert("RGB")).enhance(1.05)
    out = Image.merge("RGBA", (*rgb2.split(), sil))
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COMPARE_DIR.mkdir(parents=True, exist_ok=True)
    for slug in SPECIES:
        print(slug, flush=True)
        eng = polish(slug)
        eng.save(OUT_DIR / f"{slug}_woodcut.png")
        # compare
        cut, _ = fit_square(load_cutout(slug), 280)
        left = Image.new("RGB", (280, 280), (232, 217, 184))
        left.paste(cut.convert("RGB"), mask=cut.split()[-1])
        right = Image.new("RGB", (280, 280), (232, 217, 184))
        e = eng.copy()
        e.thumbnail((280, 280))
        right.paste(e, ((280 - e.width) // 2, (280 - e.height) // 2), e)
        both = Image.new("RGB", (580, 300), (245, 240, 230))
        both.paste(left, (10, 20))
        both.paste(right, (300, 20))
        d = ImageDraw.Draw(both)
        d.text((20, 4), f"{slug} foto", fill=(20, 15, 10))
        d.text((310, 4), f"{slug} grabado", fill=(20, 15, 10))
        both.save(COMPARE_DIR / f"{slug}_compare.jpg", quality=88)
    print("OK", len(SPECIES))


if __name__ == "__main__":
    main()
