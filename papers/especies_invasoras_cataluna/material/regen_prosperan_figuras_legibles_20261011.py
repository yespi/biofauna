#!/usr/bin/env python3
"""Regen panel «¿Prosperan?» legible: top-8 en cuerpo + suplementario 1–2/página.

Sin DB. Usa CSV + series PNG ya generadas (o re-dibuja desde CSVs de serie si existen).
Fuente ≥7 pt a tamaño A4.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from PIL import Image

ROOT = Path("/mnt/docker/biofauna-public/papers/especies_invasoras_cataluna")
FIG = ROOT / "material" / "figuras"
FIG_P = FIG / "prosperan"
CSV = ROOT / "material" / "prosperan_desaparecen_20261011.csv"
MD = ROOT / "PROSPERAN_O_DESAPARECEN.md"

# Prefer clear signals: expansion / decline / disappearance, then by |z| and n
PRIORITY = {
    "en_expansion": 0,
    "en_declive": 1,
    "desaparecida": 2,
    "desaparecida_proxy": 3,
    "estable": 4,
    "dato_escaso": 5,
    "sin_serie": 6,
}


def load_rows() -> list[dict]:
    with CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try:
            r["_z"] = abs(float(r.get("z") or 0))
        except ValueError:
            r["_z"] = 0.0
        try:
            r["_n"] = int(float(r.get("n_obs") or 0))
        except ValueError:
            r["_n"] = 0
        r["_prio"] = PRIORITY.get(r.get("categoria", ""), 9)
    rows.sort(key=lambda r: (r["_prio"], -r["_z"], -r["_n"]))
    return rows


def slug(sp: str) -> str:
    return sp.replace(" ", "_")


def pick_top8(rows: list[dict]) -> list[dict]:
    # Prefer marine/flagship when available among clear categories
    preferred = [
        "Caulerpa cylindracea",
        "Callinectes sapidus",
        "Rugulopteryx okamurae",
        "Oculina patagonica",
        "Magallana gigas",
        "Asparagopsis armata",
        "Ailanthus altissima",
        "Vespa velutina nigrithorax",
        "Procambarus clarkii",
        "Trachemys scripta elegans",
    ]
    by_name = {r["especie"]: r for r in rows}
    chosen = []
    for name in preferred:
        if name in by_name and by_name[name]["_prio"] <= 4:
            chosen.append(by_name[name])
        if len(chosen) >= 8:
            return chosen[:8]
    for r in rows:
        if r in chosen:
            continue
        if r["_prio"] <= 4 and (FIG_P / f"trend_{slug(r['especie'])}.png").exists():
            chosen.append(r)
        if len(chosen) >= 8:
            break
    return chosen[:8]


def make_top8_panel(top: list[dict]) -> Path:
    n = len(top)
    ncols = 4
    nrows = math.ceil(n / ncols)
    # Large figure so when shrunk to A4 width (~17 cm) text stays ≥7 pt
    # At dpi=150, figsize width 11 in → ~280 mm; in PDF max-height 10cm → scale ~0.35
    # Use fontsize 11–12 so after scale ≥7 pt
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.8 * nrows), dpi=150)
    axes = np.array(axes).reshape(-1)
    colors = {
        "en_expansion": "#c0392b",
        "estable": "#2980b9",
        "en_declive": "#8e44ad",
        "desaparecida": "#1c2833",
        "desaparecida_proxy": "#7f8c8d",
        "dato_escaso": "#95a5a6",
    }
    for i, r in enumerate(top):
        ax = axes[i]
        png = FIG_P / f"trend_{slug(r['especie'])}.png"
        if png.exists():
            ax.imshow(np.asarray(Image.open(png).convert("RGB")))
            ax.axis("off")
            ax.set_title(
                f"{r['especie']}\n({r['categoria']}, |Z|={r['_z']:.2f})",
                fontsize=11,
                pad=4,
            )
        else:
            ax.text(0.5, 0.5, r["especie"], ha="center", va="center", fontsize=11)
            ax.set_title(r["categoria"], fontsize=10)
            ax.axis("off")
        # color bar under title
        for spine in ax.spines.values():
            spine.set_color(colors.get(r["categoria"], "#333"))
            spine.set_linewidth(2)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle(
        "¿Prosperan o desaparecen? — 8 especies con señal más clara (tasa / esfuerzo)",
        fontsize=13,
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = FIG / "prosperan_panel_top8.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    # Keep old name as alias pointing to top8 for any leftover links
    alias = FIG / "prosperan_panel_small_multiples.png"
    Image.open(out).save(alias)
    print("OK", out)
    return out


def make_suplementario(rest: list[dict]) -> Path:
    out = FIG / "prosperan_suplementario.pdf"
    # 2 graphs per A4 page
    with PdfPages(out) as pdf:
        # cover
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(
            0.5,
            0.6,
            "Material suplementario\n¿Prosperan o desaparecen?\nSeries individuales (resto)",
            ha="center",
            va="center",
            fontsize=16,
        )
        fig.text(
            0.5,
            0.4,
            "BioFauna · G. Zafra · borrador — no citar ni difundir",
            ha="center",
            fontsize=10,
            color="#666",
        )
        pdf.savefig(fig)
        plt.close(fig)

        for i in range(0, len(rest), 2):
            batch = rest[i : i + 2]
            fig, axes = plt.subplots(len(batch), 1, figsize=(8.27, 11.69), dpi=120)
            if len(batch) == 1:
                axes = [axes]
            for ax, r in zip(axes, batch):
                png = FIG_P / f"trend_{slug(r['especie'])}.png"
                ax.set_title(
                    f"{r['especie']}  ·  {r['categoria']}  ·  |Z|={r['_z']:.2f}  ·  n={r['_n']}",
                    fontsize=12,
                    pad=6,
                )
                if png.exists():
                    ax.imshow(np.asarray(Image.open(png).convert("RGB")))
                else:
                    ax.text(0.5, 0.5, "(sin serie PNG)", ha="center", fontsize=11)
                ax.axis("off")
            fig.tight_layout(rect=(0.04, 0.04, 0.96, 0.96))
            pdf.savefig(fig)
            plt.close(fig)
    print("OK", out, "pages≈", 1 + math.ceil(len(rest) / 2))
    return out


def patch_md(top: list[dict]) -> None:
    if not MD.exists():
        return
    t = MD.read_text(encoding="utf-8")
    block = (
        "Figura principal (cuerpo): "
        "[`material/figuras/prosperan_panel_top8.png`](material/figuras/prosperan_panel_top8.png) "
        "(8 especies con señal más clara). "
        "Resto de series: "
        "[`material/figuras/prosperan_suplementario.pdf`](material/figuras/prosperan_suplementario.pdf) "
        "(1–2 gráficas por página). "
        f"Top-8: {', '.join('*' + r['especie'] + '*' for r in top)}."
    )
    old = (
        "Panel: [`figuras/prosperan_panel_small_multiples.png`]"
        "(material/figuras/prosperan_panel_small_multiples.png). "
        "Series: [`figuras/prosperan/`](material/figuras/prosperan/)."
    )
    new = (
        f"{block} "
        "Series individuales: [`figuras/prosperan/`](material/figuras/prosperan/)."
    )
    if old in t:
        t = t.replace(old, new)
    elif "prosperan_panel_top8" not in t:
        t = t.replace(
            "Series: [`figuras/prosperan/`](material/figuras/prosperan/).",
            new,
        )
    MD.write_text(t, encoding="utf-8")
    print("OK patched", MD.name)


def main() -> None:
    rows = load_rows()
    top = pick_top8(rows)
    rest = [r for r in rows if r not in top and (FIG_P / f"trend_{slug(r['especie'])}.png").exists()]
    print("top8:", [r["especie"] for r in top])
    print("supl:", len(rest))
    make_top8_panel(top)
    make_suplementario(rest)
    patch_md(top)


if __name__ == "__main__":
    main()
