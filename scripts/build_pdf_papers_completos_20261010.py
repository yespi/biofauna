#!/usr/bin/env python3
"""Regen PDFs de papers (Chrome headless + pdfunite) + marca de agua BORRADOR.

Sin GPU. Llama a scripts/papers_watermark.py tras cada PDF generado.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

try:
    import markdown
except ImportError as e:
    raise SystemExit("python-markdown requerido") from e

ROOT = Path("/mnt/docker/biofauna-public")
sys.path.insert(0, str(ROOT / "scripts"))
from papers_watermark import watermark_pdf  # noqa: E402

P = ROOT / "papers/proyecto_correlacion"
P_MAT = P / "material"
P_EN = P_MAT / "en"
Q = ROOT / "papers/biofauna"
Q_MAT = Q / "material"
Q_EN = Q_MAT / "en"
N = ROOT / "papers/nudibranquios_calendario"
N_MAT = N / "material"
I = ROOT / "papers/especies_invasoras_cataluna"
I_MAT = I / "material"
D = ROOT / "papers/especies_peligro_declives"
DATE = datetime.now().strftime("%Y%m%d")
WM_DATE = datetime.now().strftime("%Y-%m-%d")

# CSS: figcaptions ≥7 pt (legibilidad A4)
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
.grid figcaption{font-size:7pt;line-height:1.15;max-height:1.9cm;overflow:hidden}
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


def stamp(pdf: Path) -> Path:
    # force=False: no apilar si ya tiene marca
    watermark_pdf(pdf, date=WM_DATE, force=False)
    print("wm", pdf.name)
    return pdf


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
    stamp(first)
    for o in outs[1:]:
        shutil.copy2(first, base / o)
    print("ok", outs[0], first.stat().st_size)
    return first


def strip_trailing_blank_pages(pdf_path: Path) -> None:
    try:
        import pikepdf
        from PIL import Image
        import numpy as np
    except ImportError:
        return
    tmp_prefix = pdf_path.parent / f"_blankchk_{pdf_path.stem}"
    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True)
    n = None
    for line in info.stdout.splitlines():
        if line.startswith("Pages:"):
            n = int(line.split(":")[1].strip())
    if not n or n < 2:
        return
    subprocess.run(
        ["pdftoppm", "-png", "-r", "60", "-f", str(n), "-l", str(n), str(pdf_path), str(tmp_prefix)],
        check=False,
        capture_output=True,
    )
    imgs = sorted(pdf_path.parent.glob(f"{tmp_prefix.name}*.png"))
    if not imgs:
        return
    a = np.asarray(Image.open(imgs[0]).convert("RGB"))
    white = float((a > 250).all(axis=2).mean())
    for p in imgs:
        p.unlink(missing_ok=True)
    if white < 0.96:
        return
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        del pdf.pages[-1]
        pdf.save(pdf_path)
    print("stripped trailing blank page from", pdf_path.name, f"white={white:.3f}")


def pdfunite(parts: list[Path], out: Path) -> None:
    parts = [p for p in parts if p.exists()]
    if not parts:
        raise RuntimeError(f"sin partes para {out}")
    if len(parts) == 1:
        shutil.copy2(parts[0], out)
    else:
        subprocess.run(["pdfunite", *[str(p) for p in parts], str(out)], check=True)
    stamp(out)
    print("COMPLETO", out, out.stat().st_size)


def pngs_to_pdf(pngs: list[Path], out_pdf: Path) -> Path:
    existing = [p for p in pngs if p.exists()]
    if not existing:
        raise RuntimeError("sin PNGs")
    try:
        import img2pdf

        out_pdf.write_bytes(img2pdf.convert([str(p) for p in existing]))
    except Exception:
        items = []
        for i, p in enumerate(existing):
            br = "page-break-after:always;" if i < len(existing) - 1 else ""
            items.append(
                f'<div style="{br}text-align:center"><img src="{p.name}" '
                f'style="max-width:100%;max-height:98vh"/></div>'
            )
        parent = existing[0].parent
        h = parent / "_tmp_lamina_pack.html"
        h.write_text(
            "<!doctype html><meta charset='utf-8'><style>"
            "body{margin:0}@page{size:A3 landscape;margin:0.3cm}"
            "img{max-width:100%;max-height:98vh}</style>" + "".join(items),
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
        I / "PROSPERAN_O_DESAPARECEN.md",
        I / "NATIVAS_EN_EXPANSION.md",
        I / "DISCUSION.md",
        I / "REVISION_CRITICA_20261011.md",
    ]
    chunks = []
    for p in parts_md:
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8"))
            chunks.append("\n\n")
    figs = [
        "material/figuras/top25_obs_catalunya.png",
        "material/figuras/esfuerzo_bioquest_catalunya.png",
        "material/figuras/mapa_cat_1990_1999.png",
        "material/figuras/mapa_cat_2000_2009.png",
        "material/figuras/mapa_cat_2010_2019.png",
        "material/figuras/mapa_cat_2020_2026.png",
        "material/figuras/prosperan_panel_top8.png",
        "material/figuras/nativa_trend_Thalassoma_pavo.png",
        "material/figuras/nativa_trend_Arbacia_lixula.png",
        "material/figuras/nativa_trend_Pelagia_noctiluca.png",
        "material/figuras/nativa_trend_Sparisoma_cretense.png",
        "material/figuras/expansion/expansion_5y_Pterois_miles.png",
        "material/figuras/expansion/expansion_5y_Caulerpa_cylindracea.png",
        "material/figuras/expansion/expansion_5y_Oculina_patagonica.png",
        "material/figuras/expansion/expansion_5y_Callinectes_sapidus.png",
        "material/figuras/expansion/pterois_miles_longitud_vs_ano.png",
    ]
    fig_md = ["\n\n## Figuras\n\n"]
    for rel in figs:
        if (I / rel).exists():
            fig_md.append(f"![{Path(rel).stem}]({rel})\n\n")
    supl = I_MAT / "figuras" / "prosperan_suplementario.pdf"
    if supl.exists():
        fig_md.append(
            "\n\nMaterial suplementario (resto de series «¿Prosperan o desaparecen?»): "
            f"[`material/figuras/prosperan_suplementario.pdf`](material/figuras/prosperan_suplementario.pdf).\n\n"
        )
    body = "".join(chunks) + "".join(fig_md)
    tmp_md = I / f"_tmp_completo_{DATE}.md"
    tmp_md.write_text(body, encoding="utf-8")
    article_pdf = I / f"_tmp_articulo_{DATE}.pdf"
    md_to_pdf(I, tmp_md.name, [article_pdf.name], CSS_INV)
    strip_trailing_blank_pages(article_pdf)

    lam_pngs = sorted((I_MAT / "laminas_expansion").glob("lamina_expansion_*_A3.png"))
    lam_pdf = I / f"_tmp_laminas_{DATE}.pdf"
    if lam_pngs:
        pngs_to_pdf(lam_pngs, lam_pdf)

    parts = [article_pdf]
    if lam_pdf.exists():
        parts.append(lam_pdf)
    if supl.exists():
        parts.append(supl)

    out = I / f"ARTICULO_COMPLETO_{DATE}.pdf"
    pdfunite(parts, out)
    for p in I.glob("_tmp_*"):
        p.unlink(missing_ok=True)
    latest = I / "ARTICULO_COMPLETO_latest.pdf"
    shutil.copy2(out, latest)
    return out


def build_nudi_completo() -> Path:
    article = N / "ARTICULO_20261010.pdf"
    laminas = [
        N_MAT / "LAMINA1_calendario_fenologico_20261010.pdf",
        N_MAT / "LAMINA2_rosas_estaciones_20261010.pdf",
        N_MAT / "LAMINA3_distribucion_espacial_20261010.pdf",
        N_MAT / "LAMINA4_poster_guia_20261010.pdf",
        N_MAT / "LAMINA5_carta_marina_20261010.pdf",
    ]
    out = N / f"ARTICULO_COMPLETO_{DATE}.pdf"
    pdfunite([article] + [p for p in laminas if p.exists()], out)
    shutil.copy2(out, N / "ARTICULO_COMPLETO_latest.pdf")
    return out


def build_declives_completo() -> Path:
    return md_to_pdf(
        D,
        "ARTICULO.md",
        [f"ARTICULO_COMPLETO_{DATE}.pdf", "ARTICULO_COMPLETO_latest.pdf"],
        CSS_GENERIC,
    )


def build_corr_completo(es_pdf: Path) -> Path:
    out = P / f"ARTICULO_COMPLETO_{DATE}.pdf"
    shutil.copy2(es_pdf, out)
    stamp(out)
    shutil.copy2(out, P / "ARTICULO_COMPLETO_latest.pdf")
    en = P_EN / f"ARTICLE_v27_EN_{DATE}.pdf"
    if not en.exists():
        en = P_EN / "ARTICLE_v27_EN_20261011.pdf"
    if not en.exists():
        en = P_EN / "ARTICLE_EN_latest.pdf"
    if en.exists():
        en_out = P_EN / f"ARTICLE_COMPLETO_{DATE}.pdf"
        shutil.copy2(en, en_out)
        stamp(en_out)
        shutil.copy2(en_out, P_EN / "ARTICLE_COMPLETO_latest.pdf")
        shutil.copy2(en_out, P_EN / "ARTICLE_EN_latest.pdf")
    print("COMPLETO", out)
    return out


def build_biofauna_completo() -> Path:
    es = md_to_pdf(
        Q,
        "01_biofauna_es.md",
        [f"BIOFAUNA_paper_ES_{DATE}.pdf", "BIOFAUNA_paper_ES_latest.pdf"],
        CSS_GENERIC,
    )
    if (Q_EN / "01_biofauna.md").exists():
        md_to_pdf(
            Q_EN,
            "01_biofauna.md",
            [f"BIOFAUNA_paper_EN_{DATE}.pdf", "BIOFAUNA_paper_EN_latest.pdf"],
            CSS_GENERIC,
        )
    out = Q / f"ARTICULO_COMPLETO_{DATE}.pdf"
    shutil.copy2(es, out)
    shutil.copy2(out, Q / "ARTICULO_COMPLETO_latest.pdf")
    en_src = Q_EN / "BIOFAUNA_paper_EN_latest.pdf"
    if en_src.exists():
        en_out = Q_EN / f"ARTICLE_COMPLETO_{DATE}.pdf"
        shutil.copy2(en_src, en_out)
        shutil.copy2(en_out, Q_EN / "ARTICLE_COMPLETO_latest.pdf")
    print("COMPLETO", out)
    return out


def main():
    print("=== Correlación ES/EN ===")
    es = md_to_pdf(
        P,
        "ARTICULO.md",
        [f"ARTICULO_v27_ES_{DATE}.pdf", "ARTICULO_ES_latest.pdf"],
        CSS_CORR,
    )
    if (P_EN / "ARTICLE.md").exists():
        md_to_pdf(
            P_EN,
            "ARTICLE.md",
            [f"ARTICLE_v27_EN_{DATE}.pdf", "ARTICLE_EN_latest.pdf"],
            CSS_CORR,
        )
    if (P_MAT / "LAMINAS.md").exists():
        md_to_pdf(
            P_MAT,
            "LAMINAS.md",
            [f"LAMINAS_v11_{DATE}.pdf"],
            CSS_CORR + ".lamina{page-break-after:always}",
        )
        # copy laminas dated + latest to paper root (public deliverable)
        src = P_MAT / f"LAMINAS_v11_{DATE}.pdf"
        if src.exists():
            shutil.copy2(src, P / f"LAMINAS_v11_{DATE}.pdf")
            shutil.copy2(src, P / "LAMINAS_latest.pdf")

    print("=== Completos ===")
    build_corr_completo(es)
    build_biofauna_completo()
    if (N / "ARTICULO_20261010.pdf").exists():
        # re-stamp article-only + rebuild completo
        stamp(N / "ARTICULO_20261010.pdf")
        for lam in N_MAT.glob("LAMINA*.pdf"):
            stamp(lam)
        build_nudi_completo()
    build_invasoras_completo()
    build_declives_completo()
    print("DONE", DATE)


if __name__ == "__main__":
    main()
