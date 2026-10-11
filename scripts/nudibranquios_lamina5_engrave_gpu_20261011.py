#!/usr/bin/env python3
"""Generate Carta-Marina woodcut engravings via SD1.5 img2img + Canny ControlNet.

Uses the real cutout as init + structure guide. Unloads models at the end.
Cache: /mnt/docker/biofauna-public/.hf_cache
"""
from __future__ import annotations

import gc
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HOME", "/mnt/docker/biofauna-public/.hf_cache")
os.environ.setdefault("TRANSFORMERS_CACHE", os.environ["HF_HOME"])
os.environ.setdefault("DIFFUSERS_CACHE", os.environ["HF_HOME"])

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path("/mnt/docker/biofauna-public")
PAPER = ROOT / "papers/nudibranquios_calendario"
MAT = PAPER / "material"
RECORTES = MAT / "recortes"
OUT_DIR = MAT / "datos/engravings_lamina5"
COMPARE_DIR = MAT / "datos/engravings_lamina5_compare"

SPECIES = [
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

PROMPT = (
    "hand-colored copperplate engraving of a nudibranch, thick clean black ink outline, "
    "simple flat pastel gouache fills, sparse hand hatching only for shade, "
    "zoological woodcut on cream parchment, Olaus Magnus Carta Marina beast style, "
    "clear shapes, no texture, no photo"
)
NEGATIVE = (
    "photograph, photo, photorealistic, realistic skin, underwater, sand, algae, "
    "noise, grain, speckles, mottling, blurry, 3d, plastic, watermark, text, "
    "busy background, gradient shading, airbrush, soft focus"
)

SIZE = 512
STRENGTH = 0.72
GUIDANCE = 8.5
STEPS = 32
CONTROL_SCALE = 0.70


def slug(sp: str) -> str:
    return sp.replace(" ", "_").lower()


def load_cutout(sp: str) -> Image.Image:
    s = slug(sp)
    for name in (f"{s}_cutout.png", f"{s}_cutout_raw.png"):
        p = RECORTES / name
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(sp)


def prepare_init(rgba: Image.Image, size: int = SIZE) -> tuple[Image.Image, Image.Image, Image.Image]:
    """RGB on parchment + alpha mask + canny-like edge map for ControlNet."""
    alpha = rgba.split()[-1]
    alpha = alpha.point(lambda p: 255 if p > 40 else 0)
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))

    # Fit subject
    bbox = alpha.getbbox() or (0, 0, rgba.width, rgba.height)
    subj = rgba.crop(bbox)
    sub_a = alpha.crop(bbox)
    pad = int(max(subj.size) * 0.08) + 8
    canvas = Image.new("RGBA", (subj.width + 2 * pad, subj.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(subj, (pad, pad), subj)
    a_full = Image.new("L", canvas.size, 0)
    a_full.paste(sub_a, (pad, pad))

    # Square parchment RGB
    side = max(canvas.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox, oy = (side - canvas.width) // 2, (side - canvas.height) // 2
    square.paste(canvas, (ox, oy), canvas)
    a_sq = Image.new("L", (side, side), 0)
    a_sq.paste(a_full, (ox, oy))

    parch = Image.new("RGB", (side, side), (232, 217, 184))
    rgb = Image.composite(square.convert("RGB"), parch, a_sq)
    rgb = ImageEnhance.Color(rgb).enhance(0.85)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.15)
    rgb = rgb.resize((size, size), Image.Resampling.LANCZOS)
    a_sq = a_sq.resize((size, size), Image.Resampling.NEAREST)

    # Canny via PIL edges (avoid cv2 dependency issues)
    gray = ImageOps.grayscale(rgb)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    sil = a_sq.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 0 else 0)
    sil = sil.filter(ImageFilter.MaxFilter(3))
    canny = ImageChops_lighter(edges.point(lambda p: 255 if p > 40 else 0), sil)
    canny_rgb = Image.merge("RGB", (canny, canny, canny))
    return rgb, a_sq, canny_rgb


def ImageChops_lighter(a: Image.Image, b: Image.Image) -> Image.Image:
    aa = np.asarray(a, dtype=np.uint8)
    bb = np.asarray(b, dtype=np.uint8)
    return Image.fromarray(np.maximum(aa, bb), "L")


def _kmeans_flat(rgb: np.ndarray, mask: np.ndarray, k: int = 5, iters: int = 8) -> np.ndarray:
    """Simple k-means flat colors on masked pixels → pastel palette."""
    pts = rgb[mask]
    if len(pts) < k * 4:
        out = rgb.copy()
        out[mask] = pts.mean(axis=0) if len(pts) else out[mask]
        return out
    rng = np.random.default_rng(1539)
    centers = pts[rng.choice(len(pts), size=k, replace=False)].astype(np.float32)
    for _ in range(iters):
        d = ((pts[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for i in range(k):
            sel = pts[lab == i]
            if len(sel):
                centers[i] = sel.mean(axis=0)
    # Push centers toward pastel
    wash = np.array([235, 220, 185], dtype=np.float32)
    centers = centers * 0.72 + wash * 0.28
    # Keep very dark centers dark (spots)
    lum = centers.mean(axis=1)
    centers[lum < 55] = centers[lum < 55] * 0.35 + np.array([40, 28, 22], dtype=np.float32) * 0.65
    d = ((pts[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    lab = d.argmin(axis=1)
    out = np.zeros_like(rgb)
    flat_pts = centers[lab]
    out[mask] = flat_pts
    return out


def _redraw_dark_spots(arr: np.ndarray, mask: np.ndarray, draw, min_area=40):
    """Replace grainy dark blobs with clean outlined ellipses."""
    from scipy import ndimage

    gray = arr.mean(axis=2)
    dark = (gray < 75) & mask
    labeled, nlab = ndimage.label(dark)
    body = arr.copy()
    body_lum = body.mean(axis=2)
    light = mask & (body_lum >= 75)
    body_col = (
        np.median(body[light], axis=0)
        if light.any()
        else np.array([210, 200, 175], dtype=np.float32)
    )
    for lab in range(1, nlab + 1):
        ys, xs = np.where(labeled == lab)
        if len(ys) < min_area:
            continue
        body[ys, xs] = body_col
        y0, y1 = int(ys.min()), int(ys.max())
        x0, x1 = int(xs.min()), int(xs.max())
        pad = 1
        draw.ellipse(
            (x0 - pad, y0 - pad, x1 + pad, y1 + pad),
            fill=(48, 34, 26, 255),
            outline=(18, 12, 8, 255),
            width=2,
        )
    return body


def post_ink(rgb: Image.Image, alpha: Image.Image, src_rgb: Image.Image | None = None) -> Image.Image:
    """Flat pastel + clean contour + hand-wobbled hatch; stylize dark spots."""
    sil = alpha.point(lambda p: 255 if p > 80 else 0)
    am = np.asarray(sil) > 0
    # Prefer colors from original cutout (truer species hues), structure from SD
    base_rgb = np.asarray((src_rgb or rgb).convert("RGB")).astype(np.float32)
    # Smooth then flatten
    smooth = Image.fromarray(base_rgb.astype(np.uint8)).filter(ImageFilter.MedianFilter(9))
    base_rgb = np.asarray(smooth).astype(np.float32)
    flat = _kmeans_flat(base_rgb, am, k=5)
    # Build RGBA canvas
    rgba = np.zeros((flat.shape[0], flat.shape[1], 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(flat, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.asarray(sil)
    out = Image.fromarray(rgba, "RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    body = _redraw_dark_spots(flat, am, ld, min_area=35)
    out = Image.fromarray(
        np.dstack([np.clip(body, 0, 255).astype(np.uint8), np.asarray(sil)]),
        "RGBA",
    )
    out = Image.alpha_composite(out, layer)

    # Clean outer contour
    outline = sil.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 0 else 0)
    outline = outline.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3))
    eroded = sil.filter(ImageFilter.MinFilter(9))
    ring = (
        (np.asarray(sil) > 0).astype(np.int16) - (np.asarray(eroded) > 0).astype(np.int16)
    ).clip(0, 1).astype(np.uint8) * 255
    ink = ImageChops_lighter(outline, Image.fromarray(ring, "L"))
    ink_rgba = Image.merge(
        "RGBA",
        (
            Image.new("L", ink.size, 18),
            Image.new("L", ink.size, 12),
            Image.new("L", ink.size, 8),
            ink,
        ),
    )

    # Hand-wobbled hatch only in mid/dark (skip flat light fills & solid spots)
    g = np.asarray(ImageOps.grayscale(out.convert("RGB")))
    hatch = Image.new("L", out.size, 0)
    hd = ImageDraw.Draw(hatch)
    rng = np.random.default_rng(42)
    step = 9
    for y0 in range(0, out.height, step):
        x_start = int(rng.integers(-2, 3))
        for x0 in range(x_start, out.width + out.height, step):
            pts = []
            for t in range(0, step + 8):
                wobble = int(rng.integers(-1, 2))
                xx, yy = x0 + t + wobble, y0 + t
                if 0 <= xx < out.width and 0 <= yy < out.height and am[yy, xx]:
                    if 55 < g[yy, xx] < 155:
                        pts.append((xx, yy))
                    else:
                        if len(pts) >= 3:
                            hd.line(pts, fill=150, width=1)
                        pts = []
                else:
                    if len(pts) >= 3:
                        hd.line(pts, fill=150, width=1)
                    pts = []
            if len(pts) >= 3:
                hd.line(pts, fill=150, width=1)
    # Sparse cross-hatch in deeper shade only
    for y0 in range(0, out.height, step + 3):
        for x0 in range(out.width + out.height, -out.height, -(step + 3)):
            pts = []
            for t in range(0, step + 10):
                xx, yy = x0 - t, y0 + t + int(rng.integers(-1, 2))
                if 0 <= xx < out.width and 0 <= yy < out.height and am[yy, xx] and g[yy, xx] < 100:
                    pts.append((xx, yy))
                else:
                    if len(pts) >= 3:
                        hd.line(pts, fill=190, width=1)
                    pts = []
            if len(pts) >= 3:
                hd.line(pts, fill=190, width=1)

    hatch_rgba = Image.merge(
        "RGBA",
        (
            Image.new("L", hatch.size, 24),
            Image.new("L", hatch.size, 16),
            Image.new("L", hatch.size, 10),
            hatch.point(lambda p: int(p * 0.85)),
        ),
    )
    out = Image.alpha_composite(out, hatch_rgba)
    out = Image.alpha_composite(out, ink_rgba)
    r, g2, b, _ = out.split()
    return Image.merge("RGBA", (r, g2, b, sil))


def engraving_cpu_fallback(rgba: Image.Image, size: int = SIZE) -> Image.Image:
    """True flat-pastel + hatch engraving (no photo edges)."""
    rgb, alpha, _ = prepare_init(rgba, size=size)
    # Heavy median + quantize → flat washes
    flat = rgb.filter(ImageFilter.MedianFilter(9))
    flat = ImageOps.posterize(ImageEnhance.Color(flat).enhance(0.7), bits=2)
    # Soft parchment cast
    arr = np.asarray(flat).astype(np.float32)
    a = np.asarray(alpha).astype(np.float32) / 255.0
    wash = np.array([230, 210, 170], dtype=np.float32)
    arr = arr * 0.78 + wash * 0.22
    flat = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    base = Image.merge("RGBA", (*flat.split(), alpha))
    return post_ink(base.convert("RGB"), alpha)


def build_pipe():
    from diffusers import (
        ControlNetModel,
        DPMSolverMultistepScheduler,
        StableDiffusionControlNetImg2ImgPipeline,
    )

    dtype = torch.float16
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny", torch_dtype=dtype
    )
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=dtype,
        safety_checker=None,
        requires_safety_checker=False,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    try:
        pipe.enable_vae_slicing()
    except Exception:
        pass
    pipe = pipe.to("cuda")
    return pipe


def unload_pipe(pipe):
    # fp16 pipelines cannot move to CPU — just drop refs and free VRAM
    try:
        del pipe.unet
        del pipe.vae
        del pipe.text_encoder
        del pipe.controlnet
    except Exception:
        pass
    del pipe
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def compare_side(sp: str, eng: Image.Image, cut: Image.Image):
    COMPARE_DIR.mkdir(parents=True, exist_ok=True)
    cut_rgb, _, _ = prepare_init(cut, size=SIZE)
    eng_rgb = Image.new("RGB", (SIZE, SIZE), (232, 217, 184))
    eng_rgb.paste(eng.convert("RGBA"), mask=eng.split()[-1] if eng.mode == "RGBA" else None)
    both = Image.new("RGB", (SIZE * 2 + 20, SIZE + 40), (245, 240, 230))
    both.paste(cut_rgb, (0, 30))
    both.paste(eng_rgb, (SIZE + 20, 30))
    d = ImageDraw.Draw(both)
    d.text((10, 8), f"{sp} · foto", fill=(30, 20, 10))
    d.text((SIZE + 30, 8), f"{sp} · grabado", fill=(30, 20, 10))
    both.save(COMPARE_DIR / f"{slug(sp)}_compare.jpg", quality=88)


def main(only: list[str] | None = None):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spp = only or SPECIES
    print("Loading SD1.5 + ControlNet Canny…", flush=True)
    pipe = None
    use_gpu = True
    try:
        pipe = build_pipe()
        print("GPU pipeline ready", flush=True)
    except Exception as e:
        print(f"GPU pipeline failed ({e}); CPU fallback", flush=True)
        use_gpu = False

    gen = torch.Generator(device="cuda").manual_seed(1539) if use_gpu else None

    for sp in spp:
        print(f"→ {sp}", flush=True)
        cut = load_cutout(sp)
        init, alpha, canny = prepare_init(cut, SIZE)
        if use_gpu and pipe is not None:
            try:
                with torch.inference_mode():
                    result = pipe(
                        prompt=PROMPT,
                        negative_prompt=NEGATIVE,
                        image=init,
                        control_image=canny,
                        strength=STRENGTH,
                        guidance_scale=GUIDANCE,
                        num_inference_steps=STEPS,
                        controlnet_conditioning_scale=CONTROL_SCALE,
                        generator=gen,
                    ).images[0]
                eng = post_ink(result, alpha, src_rgb=init)
            except Exception as e:
                print(f"  GPU fail {e}; CPU", flush=True)
                eng = engraving_cpu_fallback(cut, SIZE)
        else:
            eng = engraving_cpu_fallback(cut, SIZE)

        # Final square with transparency
        out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        out.paste(eng, (0, 0), eng.split()[-1])
        out_path = OUT_DIR / f"{slug(sp)}_woodcut.png"
        out.save(out_path)
        compare_side(sp, out, cut)
        print(f"  saved {out_path.name}", flush=True)

    if pipe is not None:
        print("Unloading models…", flush=True)
        unload_pipe(pipe)
    print("DONE", flush=True)


if __name__ == "__main__":
    only = sys.argv[1:] or None
    main(only)
