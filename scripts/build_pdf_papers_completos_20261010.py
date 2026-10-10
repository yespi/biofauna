#!/usr/bin/env python3
"""Regen PDFs correlación (miniaturas en cuadrícula + keep-together) y ARTICULO_COMPLETO_*.

Chrome headless + pdfunite. Sin GPU.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

try:
    import markdown
except ImportError as e:
    raise SystemExit("python-markdown requerido") from e

ROOT = Path("/mnt/docker/biofauna-public")
P = ROOT / "papers/proyecto_correlacion"
Q = ROOT / "papers/biofauna"
N = ROOT / "papers/nudibranquios_calendario"
I = ROOT / "papers/especies_invasoras_cataluna"
DATE = datetime.now().strftime("%Y%m%d")

# CSS correlación: miniaturas 2×2, keep-together figuras/tablas/láminas
CSS_CORR = """
body{font-family:Georgia,'DejaVu Serif',serif;font-size:10.5pt;line-height:1.38;margin:0 1.2cm;color:#111}
h1{font-size:17pt}h2{font-size:14pt;margin-top:16px;break-after:avoid;page-break-after:avoid}
h3{font-size:12pt;break-after:avoid;page-break-after:avoid}
table{border-collapse:collapse;font-size:8.5pt;margin:8px 0;width:100%;
  break-inside:avoid;page-break-inside:avoid}
td,th{border:1px solid #bbb;padding:3px 5px;vertical-align:top}th{background:#eee}
img{max-width:100%;height:auto}
figure{margin:6px 0}
figcaption{font-size:7.5pt;color:#333;line-height:1.25;margin-top:2px}
figure.fig{break-inside:avoid;page-break-inside:avoid;margin:8px 0}
figure.fig img{max-height:8.5cm;max-width:100%;display:block;margin:0 auto;width:auto;height:auto}
.lamina{margin:6px 0 10px;border:1px solid #ddd;padding:5px 7px;background:#fafafa;
  break-inside:avoid;page-break-inside:avoid}
.lamina .lt{font-size:9pt;margin:0 0 3px;break-after:avoid;page-break-after:avoid}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;break-inside:avoid;page-break-inside:avoid}
.grid figure{margin:0;break-inside:avoid;page-break-inside:avoid}
.grid img{width:100%;height:3.55cm;object-fit:contain;background:#f0f0f0;display:block}
.grid figcaption{font-size:6.2pt;line-height:1.15;max-height:1.7cm;overflow:hidden}
.nota{font-size:8.5pt}code{font-size:8.5pt}
a{color:#1a4f8b;text-decoration:none}
@page{size:A4;margin:1.3cm}
"""

CSS_GENERIC = """
body{font-family:Georgia,'DejaVu Serif',serif;font-size:10.5pt;line-height:1.4;margin:0 1.3cm;color:#111}
h1{font-size:18pt}h2{font-size:14pt;margin-top:16px;break-after:avoid}h3{font-size:12pt;break-after:avoid}
table{border-collapse:collapse;font-size:8.5pt;margin:8px 0;width:100%;break-inside:avoid;page-break-inside:avoid}
td,th{border:1px solid #bbb;padding:3px 5px;vertical-align:top}th{background:#eee}
img{max-width:100%;height:auto;max-height:10cm;display:block;margin:6px auto}
figure{break-inside:avoid;page-break-inside:avoid;margin:8px 0}
figcaption{font-size:8pt;color:#333}
code{font-size:8.5pt}a{color:#1a4f8b;text-decoration:none}
@page{size:A4;margin:1.4cm}
"""

CSS_INV = CSS_GENERIC + """
img.lamina-page{max-height:none;width:100%;height:auto;page-break-before:always}
"""


def chrome_pdf(html_path: Path, pdf_path: Path) -> None:
    if not shutil.which("google-chrome"):
        raise SystemExit("google-chrome no encontrado")
    r = subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path}",
        ],
        capture_output=True,
        text=True,
        timeout=360,
    )
    if not pdf_path.exists():
        raise RuntimeError(f"FALLO PDF {pdf_path.name}: {(r.stderr or '')[-500:]}")


def md_to_pdf(base: Path, md_name: str, outs: list[str], css: str) -> Path:
    html_body = markdown.markdown(
        (base / md_name).read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    h = base / f"_tmp_{md_name.replace('.md', '.html')}"
    h.write_text(f"<!doctype html><meta charset='utf-8'><style>{css}</style>{html_body}", encoding="utf-8")
    first = base / outs[0]
    chrome_pdf(h, first)
    h.unlink(missing_ok=True)
    for o in outs[1:]:
        shutil.copy2(first, base / o)
    print("ok", outs[0], first.stat().st_size)
    return first


def pdfunite(parts: list[Path], out: Path) -> None:
    parts = [p for p in parts if p.exists()]
    if not parts:
        raise RuntimeError(f"sin partes para {out}")
    if len(parts) == 1:
        shutil.copy2(parts[0], out)
    else:
        subprocess.run(["pdfunite", *[str(p) for p in parts], str(out)], check=True)
    print("COMPLETO", out, out.stat().st_size)


def pngs_to_pdf(pngs: list[Path], out_pdf: Path) -> Path:
    """Una página A4/A3 por PNG vía Chrome HTML."""
    items = []
    for p in pngs:
        if not p.exists():
            continue
        items.append(
            f'<div style="page-break-after:always;text-align:center">'
            f'<img src="{p.name}" style="max-width:100%;max-height:100vh;height:auto"/></div>'
        )
    if not items:
        raise RuntimeError("sin PNGs")
    # HTML junto a los PNG (rutas relativas)
    parent = pngs[0].parent
    h = parent / "_tmp_lamina_pack.html"
    h.write_text(
        "<!doctype html><meta charset='utf-8'><style>"
        "body{margin:0}@page{size:A3 landscape;margin:0.4cm}"
        "img{max-width:100%;max-height:100vh}</style>" + "".join(items),
        encoding="utf-8",
    )
    chrome_pdf(h, out_pdf)
    h.unlink(missing_ok=True)
    return out_pdf


def build_invasoras_completo() -> Path:
    parts_md = [
        I / "INTRODUCCION.md",
        I / "METODOS.md",
        I / "RESULTADOS_v1.md",
        I / "ORIGEN_Y_VIAS_EXPANSION.md",
        I / "DISCUSION.md",
    ]
    chunks = []
    for p in parts_md:
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8"))
            chunks.append("\n\n")
    # embeber figuras principales si existen
    figs = [
        "figuras/top25_obs_catalunya.png",
        "figuras/esfuerzo_bioquest_catalunya.png",
        "figuras/mapa_cat_1990_1999.png",
        "figuras/mapa_cat_2000_2009.png",
        "figuras/mapa_cat_2010_2019.png",
        "figuras/mapa_cat_2020_2026.png",
    ]
    fig_md = ["\n\n## Figuras\n\n"]
    for rel in figs:
        if (I / rel).exists():
            fig_md.append(f"![{Path(rel).stem}]({rel})\n\n")
    body = "".join(chunks) + "".join(fig_md)
    tmp_md = I / f"_tmp_completo_{DATE}.md"
    tmp_md.write_text(body, encoding="utf-8")
    article_pdf = I / f"_tmp_articulo_{DATE}.pdf"
    md_to_pdf(I, tmp_md.name, [article_pdf.name], CSS_INV)

    # láminas A3 (PNG → PDF pack)
    lam_pngs = sorted((I / "laminas_expansion").glob("lamina_expansion_*_A3.png"))
    lam_pdf = I / f"_tmp_laminas_{DATE}.pdf"
    if lam_pngs:
        pngs_to_pdf(lam_pngs, lam_pdf)

    out = I / f"ARTICULO_COMPLETO_{DATE}.pdf"
    pdfunite([article_pdf] + ([lam_pdf] if lam_pdf.exists() else []), out)
    for p in (tmp_md, article_pdf, lam_pdf, I / f"_tmp_completo_{DATE}.html"):
        p.unlink(missing_ok=True)
    # also clean chrome tmp html name variants
    for p in I.glob("_tmp_*.html"):
        p.unlink(missing_ok=True)
    for p in I.glob("_tmp_*.md"):
        p.unlink(missing_ok=True)
    for p in I.glob("_tmp_*.pdf"):
        if p.name.startswith("_tmp_"):
            p.unlink(missing_ok=True)
    latest = I / "ARTICULO_COMPLETO_latest.pdf"
    shutil.copy2(out, latest)
    return out


def build_nudi_completo() -> Path:
    article = N / "ARTICULO_20261010.pdf"
    # regen article HTML→PDF lightly if script output exists; else use current
    # Prefer merging existing article + laminas + poster
    laminas = [
        N / "LAMINA1_calendario_fenologico_20261010.pdf",
        N / "LAMINA2_rosas_estaciones_20261010.pdf",
        N / "LAMINA3_distribucion_espacial_20261010.pdf",
        N / "LAMINA4_poster_guia_20261010.pdf",
    ]
    out = N / f"ARTICULO_COMPLETO_{DATE}.pdf"
    pdfunite([article] + laminas, out)
    shutil.copy2(out, N / "ARTICULO_COMPLETO_latest.pdf")
    return out


def build_corr_completo(es_pdf: Path) -> Path:
    out = P / f"ARTICULO_COMPLETO_{DATE}.pdf"
    # El artículo ES ya integra figuras + láminas embebidas
    shutil.copy2(es_pdf, out)
    shutil.copy2(out, P / "ARTICULO_COMPLETO_latest.pdf")
    # EN completo
    en = P / f"ARTICLE_v24_EN_{DATE}.pdf"
    if en.exists() or (P / "ARTICLE_EN_latest.pdf").exists():
        en_src = en if en.exists() else P / "ARTICLE_EN_latest.pdf"
        en_out = P / f"ARTICLE_COMPLETO_{DATE}.pdf"
        shutil.copy2(en_src, en_out)
        shutil.copy2(en_out, P / "ARTICLE_COMPLETO_latest.pdf")
    print("COMPLETO", out)
    return out


def build_biofauna_completo() -> Path:
    src = Q / "BIOFAUNA_paper_ES_latest.pdf"
    if not src.exists():
        src = Q / f"BIOFAUNA_paper_ES_{DATE}.pdf"
    out = Q / f"ARTICULO_COMPLETO_{DATE}.pdf"
    shutil.copy2(src, out)
    shutil.copy2(out, Q / "ARTICULO_COMPLETO_latest.pdf")
    # EN
    src_en = Q / "BIOFAUNA_paper_EN_latest.pdf"
    if src_en.exists():
        en_out = Q / f"ARTICLE_COMPLETO_{DATE}.pdf"
        shutil.copy2(src_en, en_out)
        shutil.copy2(en_out, Q / "ARTICLE_COMPLETO_latest.pdf")
    print("COMPLETO", out)
    return out


def main():
    print("=== Correlación ES/EN (CSS grid + keep-together) ===")
    es = md_to_pdf(
        P,
        "ARTICULO.md",
        [f"ARTICULO_v24_ES_{DATE}.pdf", "ARTICULO_ES_latest.pdf"],
        CSS_CORR,
    )
    md_to_pdf(
        P,
        "ARTICLE.md",
        [f"ARTICLE_v24_EN_{DATE}.pdf", "ARTICLE_EN_latest.pdf"],
        CSS_CORR,
    )
    # LAMINAS sueltas también con grid
    if (P / "LAMINAS.md").exists():
        md_to_pdf(
            P,
            "LAMINAS.md",
            [f"LAMINAS_v11_{DATE}.pdf", "LAMINAS_latest.pdf"],
            CSS_CORR + ".lamina{page-break-after:always}",
        )

    print("=== Completos ===")
    build_corr_completo(es)
    build_biofauna_completo()
    if (N / "ARTICULO_20261010.pdf").exists():
        build_nudi_completo()
    build_invasoras_completo()
    print("DONE", DATE)


if __name__ == "__main__":
    main()
