#!/usr/bin/env python3
"""Limpieza papers/ (11-oct-2026): material/, EN, borrado de obsoletos.

Idempotente a medias: mueve si existe en origen; no recrea lo ya borrado.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/mnt/docker/biofauna-public/papers")


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def mv(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    ensure(dst.parent)
    if dst.exists():
        if dst.is_dir() and src.is_dir():
            # merge
            for child in src.iterdir():
                mv(child, dst / child.name)
            try:
                src.rmdir()
            except OSError:
                pass
            return
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    shutil.move(str(src), str(dst))
    print(f"  mv {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")


def rm(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    print(f"  rm {path.relative_to(ROOT)}")


def rewrite_paths(md: Path, replacements: list[tuple[str, str]]) -> None:
    if not md.exists():
        return
    text = md.read_text(encoding="utf-8")
    orig = text
    for a, b in replacements:
        text = text.replace(a, b)
    if text != orig:
        md.write_text(text, encoding="utf-8")
        print(f"  rewrite {md.relative_to(ROOT)}")


def biofauna() -> None:
    print("=== biofauna ===")
    base = ROOT / "biofauna"
    mat = ensure(base / "material")
    en = ensure(mat / "en")

    # material: figures + svgs + appendix
    mv(base / "figures", mat / "figures")
    for name in ("figure_pipeline.svg", "figure_mejoras.svg", "figure_datos.svg", "appendix_species.md"):
        mv(base / name, mat / name)

    # EN latest only
    mv(base / "01_biofauna.md", en / "01_biofauna.md")
    for name in (
        "BIOFAUNA_paper_EN_20261011.pdf",
        "BIOFAUNA_paper_EN_latest.pdf",
        "ARTICLE_COMPLETO_20261011.pdf",
        "ARTICLE_COMPLETO_latest.pdf",
    ):
        mv(base / name, en / name)

    # Delete older ES/EN and duplicates
    for name in (
        "BIOFAUNA_paper_ES_20261002.pdf",
        "BIOFAUNA_paper_ES_20261006.pdf",
        "BIOFAUNA_paper_ES_20261009.pdf",
        "BIOFAUNA_paper_EN_20261002.pdf",
        "BIOFAUNA_paper_EN_20261006.pdf",
        "BIOFAUNA_paper_EN_20261009.pdf",
        "BIOFAUNA_paper_EN_20261010.pdf",
        "ARTICLE_COMPLETO_20261010.pdf",
    ):
        rm(base / name)

    # Keep: ES 20261010 + 20261011 + latest + ARTICULO_COMPLETO same
    # Paths in ES md
    rewrite_paths(
        base / "01_biofauna_es.md",
        [
            ("(figure_pipeline.svg)", "(material/figure_pipeline.svg)"),
            ("(figure_mejoras.svg)", "(material/figure_mejoras.svg)"),
            ("(figure_datos.svg)", "(material/figure_datos.svg)"),
            ("figures/", "material/figures/"),
        ],
    )
    rewrite_paths(
        en / "01_biofauna.md",
        [
            ("(figure_pipeline.svg)", "(../figure_pipeline.svg)"),
            ("(figure_mejoras.svg)", "(../figure_mejoras.svg)"),
            ("(figure_datos.svg)", "(../figure_datos.svg)"),
            ("figures/", "../figures/"),
        ],
    )


def invasoras() -> None:
    print("=== especies_invasoras_cataluna ===")
    base = ROOT / "especies_invasoras_cataluna"
    mat = ensure(base / "material")

    for name in (
        "figuras",
        "laminas_expansion",
        "upgrade_addendum_456_20261011.py",
        "gen_mapas_proyeccion_y_prosperan_20261011.py",
        "fix_figuras_vacias_20261011.py",
        "prosperan_desaparecen_20261011.csv",
        "primeras_fechas_20261011.csv",
        "tabla_origen_vias_resumen.csv",
        "primera_obs_regiones_bq.csv",
        "nativas_expansion_tendencias_20261011.csv",
        "meta_nativas_20261011.json",
        "meta_fuentes.json",
        "estacionalidad_mensual_cat.csv",
        "esfuerzo_bioquest_anual.csv",
        "serie_anual_normalizada.csv",
        "presencia_cat_es.csv",
        "resumen_medio.csv",
        "resumen_categorias.csv",
        "resumen_grupo.csv",
        "marinas_weitzmann_comparativa_20261010.csv",
        "target_species.json",
        "ORDEN_ROBOTIN_20261011.md",
        "REVISION_CRITICA_20261010.md",
    ):
        mv(base / name, mat / name)

    rm(base / "__pycache__")
    rm(mat / "laminas_expansion" / "__pycache__")

    # Path rewrites in remaining root MDs
    reps = [
        ("figuras/", "material/figuras/"),
        ("laminas_expansion/", "material/laminas_expansion/"),
        ("(`prosperan_desaparecen_20261011.csv`)", "(`material/prosperan_desaparecen_20261011.csv`)"),
        ("[`prosperan_desaparecen_20261011.csv`](prosperan_desaparecen_20261011.csv)",
         "[`prosperan_desaparecen_20261011.csv`](material/prosperan_desaparecen_20261011.csv)"),
        ("[`primeras_fechas_20261011.csv`](primeras_fechas_20261011.csv)",
         "[`primeras_fechas_20261011.csv`](material/primeras_fechas_20261011.csv)"),
        ("[`tabla_origen_vias_resumen.csv`](tabla_origen_vias_resumen.csv)",
         "[`tabla_origen_vias_resumen.csv`](material/tabla_origen_vias_resumen.csv)"),
        ("[`primera_obs_regiones_bq.csv`](primera_obs_regiones_bq.csv)",
         "[`primera_obs_regiones_bq.csv`](material/primera_obs_regiones_bq.csv)"),
        ("[`nativas_expansion_tendencias_20261011.csv`](nativas_expansion_tendencias_20261011.csv)",
         "[`nativas_expansion_tendencias_20261011.csv`](material/nativas_expansion_tendencias_20261011.csv)"),
        ("upgrade_addendum_456_20261011.py", "material/upgrade_addendum_456_20261011.py"),
        ("gen_mapas_proyeccion_y_prosperan_20261011.py", "material/gen_mapas_proyeccion_y_prosperan_20261011.py"),
        ("fix_figuras_vacias_20261011.py", "material/fix_figuras_vacias_20261011.py"),
        ("`prosperan_desaparecen_20261011.csv`", "`material/prosperan_desaparecen_20261011.csv`"),
        ("`primeras_fechas_20261011.csv`", "`material/primeras_fechas_20261011.csv`"),
        ("`tabla_origen_vias_resumen.csv`", "`material/tabla_origen_vias_resumen.csv`"),
        ("`primera_obs_regiones_bq.csv`", "`material/primera_obs_regiones_bq.csv`"),
        ("`serie_anual_normalizada.csv`", "`material/serie_anual_normalizada.csv`"),
        ("`esfuerzo_bioquest_anual.csv`", "`material/esfuerzo_bioquest_anual.csv`"),
        ("`estacionalidad_mensual_cat.csv`", "`material/estacionalidad_mensual_cat.csv`"),
        ("`presencia_cat_es.csv`", "`material/presencia_cat_es.csv`"),
    ]
    for md in base.glob("*.md"):
        rewrite_paths(md, reps)

    # Fix scripts: data/figuras now under material/
    script_reps = [
        ('FIG = ROOT / "figuras"', 'FIG = ROOT / "material" / "figuras"'),
        ('OUT = ROOT / "laminas_expansion"', 'OUT = ROOT / "material" / "laminas_expansion"'),
        ('TABLA = ROOT / "tabla_origen_vias_resumen.csv"',
         'TABLA = ROOT / "material" / "tabla_origen_vias_resumen.csv"'),
        ('FECHAS = ROOT / "primeras_fechas_20261011.csv"',
         'FECHAS = ROOT / "material" / "primeras_fechas_20261011.csv"'),
        ('ROOT / "prosperan_desaparecen_20261011.csv"',
         'ROOT / "material" / "prosperan_desaparecen_20261011.csv"'),
        ('ROOT / "primeras_fechas_20261011.csv"',
         'ROOT / "material" / "primeras_fechas_20261011.csv"'),
        ("[`figuras/prosperan_panel_small_multiples.png`](figuras/prosperan_panel_small_multiples.png)",
         "[`figuras/prosperan_panel_small_multiples.png`](material/figuras/prosperan_panel_small_multiples.png)"),
        ("[`figuras/prosperan/`](figuras/prosperan/)",
         "[`figuras/prosperan/`](material/figuras/prosperan/)"),
        ("[`prosperan_desaparecen_20261011.csv`](prosperan_desaparecen_20261011.csv)",
         "[`prosperan_desaparecen_20261011.csv`](material/prosperan_desaparecen_20261011.csv)"),
        # markdown strings written by scripts (relative to paper root when opened from there)
        ('f"Panel: [`figuras/prosperan_panel_small_multiples.png`](figuras/prosperan_panel_small_multiples.png). "',
         'f"Panel: [`figuras/prosperan_panel_small_multiples.png`](material/figuras/prosperan_panel_small_multiples.png). "'),
        ('f"Series: [`figuras/prosperan/`](figuras/prosperan/).",',
         'f"Series: [`figuras/prosperan/`](material/figuras/prosperan/).",'),
        ('"Panel: [`figuras/prosperan_panel_small_multiples.png`](figuras/prosperan_panel_small_multiples.png).",',
         '"Panel: [`figuras/prosperan_panel_small_multiples.png`](material/figuras/prosperan_panel_small_multiples.png).",'),
    ]
    for py in list(mat.glob("*.py")) + list((mat / "laminas_expansion").glob("*.py")):
        if not py.exists():
            continue
        t = py.read_text(encoding="utf-8")
        newt = t
        for a, b in script_reps:
            newt = newt.replace(a, b)
        # PROSPERAN md is written to paper root — keep that; CSV paths inside it use material/
        if 'out_md = ROOT / "PROSPERAN_O_DESAPARECEN.md"' not in newt and 'PROSPERAN_O_DESAPARECEN.md' in newt:
            pass
        if newt != t:
            py.write_text(newt, encoding="utf-8")
            print(f"  rewrite script {py.relative_to(ROOT)}")


def declives() -> None:
    print("=== especies_peligro_declives ===")
    base = ROOT / "especies_peligro_declives"
    mat = ensure(base / "material")
    for name in (
        "figuras",
        "declives_tendencias_20261011.csv",
        "controles_tendencias_20261011.csv",
        "meta_tendencias_20261011.json",
    ):
        mv(base / name, mat / name)
    rewrite_paths(
        base / "ARTICULO.md",
        [
            ("figuras/", "material/figuras/"),
            ("[`figuras/`](figuras/)", "[`figuras/`](material/figuras/)"),
            ("`figuras/", "`material/figuras/"),
        ],
    )
    rewrite_paths(
        base / "README.md",
        [
            ("[`declives_tendencias_20261011.csv`](declives_tendencias_20261011.csv)",
             "[`declives_tendencias_20261011.csv`](material/declives_tendencias_20261011.csv)"),
            ("[`controles_tendencias_20261011.csv`](controles_tendencias_20261011.csv)",
             "[`controles_tendencias_20261011.csv`](material/controles_tendencias_20261011.csv)"),
            ("[`figuras/`](figuras/)", "[`figuras/`](material/figuras/)"),
            ("[`meta_tendencias_20261011.json`](meta_tendencias_20261011.json)",
             "[`meta_tendencias_20261011.json`](material/meta_tendencias_20261011.json)"),
        ],
    )


def correlacion() -> None:
    print("=== proyecto_correlacion ===")
    base = ROOT / "proyecto_correlacion"
    mat = ensure(base / "material")
    en = ensure(mat / "en")

    for name in (
        "figuras",
        "lamina_fotos",
        "experimentos",
        "METODOS.md",
        "RESULTADOS.md",
        "LAMINAS.md",
        "SUPLEMENTARIO_figuras_v27.md",
        "BENCHMARK_PAPERS_20261011.md",
        "NULO_EXACTO_TODOS_PARES_20261005.md",
    ):
        mv(base / name, mat / name)

    rm(base / "archivo_2026-09")

    # EN latest
    mv(base / "ARTICLE.md", en / "ARTICLE.md")
    for name in (
        "ARTICLE_v27_EN_20261011.pdf",
        "ARTICLE_EN_latest.pdf",
        "ARTICLE_COMPLETO_20261011.pdf",
        "ARTICLE_COMPLETO_latest.pdf",
    ):
        mv(base / name, en / name)

    # Delete older ES/EN PDFs (keep v26 + v27 ES + COMPLETO 10/11 + LAMINAS latest + v11)
    keep_es = {
        "ARTICULO_v27_ES_20261011.pdf",
        "ARTICULO_v26_ES_20261011.pdf",
        "ARTICULO_ES_latest.pdf",
        "ARTICULO_COMPLETO_20261011.pdf",
        "ARTICULO_COMPLETO_20261010.pdf",
        "ARTICULO_COMPLETO_latest.pdf",
        "LAMINAS_v11_20261011.pdf",
        "LAMINAS_v11_20261010.pdf",
        "LAMINAS_latest.pdf",
        "ARTICULO.md",
        "README.md",
    }
    for p in base.glob("*.pdf"):
        if p.name not in keep_es:
            rm(p)

    # Path rewrites in ARTICULO.md
    rewrite_paths(
        base / "ARTICULO.md",
        [
            ('src="figuras/', 'src="material/figuras/'),
            ('src="lamina_fotos/', 'src="material/lamina_fotos/'),
            ("`figuras/", "`material/figuras/"),
            ("(`figuras/", "(material/figuras/"),
            ("experimentos/", "material/experimentos/"),
            ("[`AVANCE_cruzadas_20261011.md`](experimentos/",
             "[`AVANCE_cruzadas_20261011.md`](material/experimentos/"),
        ],
    )
    # EN article paths relative to material/en/
    rewrite_paths(
        en / "ARTICLE.md",
        [
            ('src="figuras/', 'src="../figuras/'),
            ('src="lamina_fotos/', 'src="../lamina_fotos/'),
            ("`figuras/", "`../figuras/"),
            ("experimentos/", "../experimentos/"),
        ],
    )
    # LAMINAS.md
    rewrite_paths(
        mat / "LAMINAS.md",
        [
            ('src="lamina_fotos/', 'src="lamina_fotos/'),  # same dir parent material/
        ],
    )
    # LAMINAS is in material/; lamina_fotos also in material/ — relative ok as lamina_fotos/
    # SUPLEMENTARIO
    rewrite_paths(
        mat / "SUPLEMENTARIO_figuras_v27.md",
        [
            ("../figuras/", "figuras/"),
            ("experimentos/", "experimentos/"),
        ],
    )


def nudibranquios_calendario() -> None:
    print("=== nudibranquios_calendario ===")
    base = ROOT / "nudibranquios_calendario"
    mat = ensure(base / "material")

    for name in (
        "datos",
        "figuras",
        "fotos",
        "fotos_poster",
        "recortes",
        "LICENCIAS_FOTOS.md",
        "LICENCIAS_POSTER_LAMINA4.md",
        "LICENCIAS_POSTER_LAMINA5.md",
        "LEEME_ADDENDUM_LAMINA5.txt",
        "NOTA_HERRAMIENTAS_ROBOTIN.md",
        "REVISION_ALCANCE_20261010.md",
        "CALENDARIO_BORRADOR_20261008.md",
        "calendario_nudibranquios_20261008.csv",
        "meta_generacion_20261010.json",
        "meta_lamina3_20261010.json",
        "LAMINA1_calendario_fenologico_20261010.pdf",
        "LAMINA1_calendario_fenologico_20261010.png",
        "LAMINA2_rosas_estaciones_20261010.pdf",
        "LAMINA2_rosas_estaciones_20261010.png",
        "LAMINA3_distribucion_espacial_20261010.pdf",
        "LAMINA3_distribucion_espacial_20261010.png",
        "LAMINA4_poster_guia_20261010.pdf",
        "LAMINA4_poster_guia_20261010.png",
        "LAMINA5_carta_marina_20261010.pdf",
        "LAMINA5_carta_marina_20261010.png",
        "LAMINA5_carta_marina_20261010.svg",
        "LAMINA5_carta_marina_hibrida_20261011.pdf",
        "LAMINA5_carta_marina_hibrida_20261011.png",
        "ref_carta_marina_gustavo.jpg",
    ):
        mv(base / name, mat / name)

    # obsolete engraving / drafts / caches
    for name in (
        "LAMINA5_carta_marina_grabado_20261011.pdf",
        "LAMINA5_carta_marina_grabado_20261011.png",
        "_articulo_print.html",
        ".venv",
    ):
        rm(base / name)

    # Keep in root: README, ARTICULO_20261010.md, ARTICULO_20261010.pdf,
    # ARTICULO_COMPLETO_20261010/11 + latest


def fanero_nudi() -> None:
    print("=== fanerogamas / nudibranquios (esqueleto) ===")
    # Already minimal; nothing to move
    pass


def main() -> None:
    du_before = subprocess.check_output(["du", "-sh"] + [str(p) for p in sorted(ROOT.iterdir())], text=True)
    (Path("/tmp/papers_du_antes.txt")).write_text(du_before, encoding="utf-8")
    print("BEFORE:\n", du_before)
    biofauna()
    invasoras()
    declives()
    correlacion()
    nudibranquios_calendario()
    fanero_nudi()
    print("REORG DONE")


if __name__ == "__main__":
    main()
