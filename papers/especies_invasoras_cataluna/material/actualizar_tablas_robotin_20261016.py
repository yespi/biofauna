#!/usr/bin/env python3
"""Ultima observación, «sin datos», tablas S1–S6 y acierto BioFauna p19 (sin iNat API)."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pandas as pd

M = Path(__file__).parent
P = M.parent
BOX = (40.45, 42.95, 0.1, 3.4)


def psql(sql: str) -> pd.DataFrame:
    cmd = [
        "docker",
        "exec",
        "postgres-global",
        "psql",
        "-U",
        "admin_yespi",
        "-d",
        "fauna",
        "-A",
        "-F",
        ",",
        "-c",
        sql,
    ]
    out = subprocess.check_output(cmd, text=True)
    lines = [ln for ln in out.strip().splitlines() if ln and not ln.startswith("(")]
    if len(lines) < 2:
        return pd.DataFrame()
    header = lines[0].split(",")
    rows = [ln.split(",") for ln in lines[1:]]
    return pd.DataFrame(rows, columns=header)


def slugify(binomial: str) -> str:
    s = binomial.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def fmt_date(y, m, d) -> str:
    if pd.isna(y) or y == "" or str(y) == "None":
        return "sin datos"
    try:
        y = int(float(y))
        if m in (None, "", "None") or pd.isna(m):
            return f"{y}"
        m = int(float(m))
        if d in (None, "", "None") or pd.isna(d):
            return f"{y:04d}-{min(max(m, 1), 12):02d}"
        d = int(float(d))
        m = min(max(m, 1), 12)
        d = min(max(d, 1), 28)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except (ValueError, TypeError):
        return "sin datos"


def sd_cell(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "sin datos"
    if isinstance(v, str) and v.strip().lower() in ("", "nan", "none", "nat", "s. d.", "s.d."):
        return "sin datos"
    return str(v)


def enrich_presencia():
    import ultima_obs_enrich_20261016 as uo

    uo.main()
    return pd.read_csv(M / "presencia_cat_es.csv")


def eval_p19_ue():
    eval_path = Path("/mnt/docker/biofauna/dataset/calib_raw_t05.jsonl")
    if not eval_path.exists():
        return pd.DataFrame()
    ts = json.loads((M / "target_species.json").read_text())
    slugs = {t["name"]: slugify(t["name"]) for t in ts if t.get("name")}
    agg: dict[str, list[int]] = {s: [] for s in slugs.values()}
    with eval_path.open() as f:
        for line in f:
            d = json.loads(line)
            sp = d.get("true")
            if sp in agg:
                agg[sp].append(int(d.get("ok_species", 0)))
    rows = []
    for name, slug in sorted(slugs.items()):
        ok = agg.get(slug, [])
        n = len(ok)
        acc = (sum(ok) / n * 100) if n else None
        rows.append(
            {
                "especie": name,
                "slug_bf": slug,
                "n_eval_p19": n,
                "acierto_especie_pct": round(acc, 1) if acc is not None else None,
                "en_indice_p19": "sí" if n else "no",
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(M / "cobertura_bf_ue_p19_20261016.csv", index=False)
    return df


def write_all_tables(pres: pd.DataFrame, bf: pd.DataFrame):
    glm = pd.read_csv(M / "glm_tendencias_20261015.csv")
    glm = glm[glm.ventana == "2013-2025"][
        ["especie", "RR_anual", "IC95_lo", "IC95_hi", "q_BH", "clase"]
    ]
    easin = pd.read_csv(M / "concordancia_easin_20261015.csv")
    eff = pd.read_csv(M / "esfuerzo_bioquest_anual.csv")
    cat_h = {
        "ocasional_o_puntual": "ocasional",
        "llegada_reciente_serie_insuficiente": "llegada reciente",
        "en_expansion": "en expansión",
    }

    def cat_label(row):
        c = row["categoria"]
        if c == "recurrente" and row.get("clase") == "creciente":
            return "en expansión"
        return cat_h.get(c, c)

    pres_cat = pres[pres.presencia_catalunya == "sí"].copy()
    pres_cat = pres_cat.merge(glm, on="especie", how="left")

    lines3 = [
        "# Tabla 3. Presencia en Cataluña, tendencias y registros ciudadanos\n\n",
        "Primer y último registro: fechas de observación *research grade* en la caja de estudio (§2.2). "
        "«sin datos» = sin fecha utilizable en las fuentes locales consultadas.\n\n",
        "| Especie | Obs | Celdas UTM 10 km | Primer registro | Última observación | Categoría | RR anual (IC 95 %) | q (FDR) |\n",
        "|---|---:|---:|---|---|---|---:|---:|\n",
    ]
    for _, r in pres_cat.sort_values("obs_catalunya", ascending=False).iterrows():
        pr = sd_cell(r.get("primera_obs_catalunya") or "")
        ul = sd_cell(r.get("ultima_obs_catalunya") or "")
        if pr == "sin datos" and int(r["obs_catalunya"]) > 0:
            pr = "sin datos"
        if ul == "sin datos" and int(r["obs_catalunya"]) == 0:
            ul = "—"
        loc = r.get("localidades_catalunya")
        loc_s = int(loc) if pd.notna(loc) and str(loc) not in ("nan", "") else "sin datos"
        if pd.notna(r.get("RR_anual")) and pd.notna(r.get("IC95_lo")):
            rr = f"{r['RR_anual']:.2f} ({r['IC95_lo']:.2f}–{r['IC95_hi']:.2f})"
            q = f"{r['q_BH']:.3f}" if pd.notna(r["q_BH"]) else "—"
        else:
            rr, q = "—", "—"
        cat = cat_label(r)
        lines3.append(
            f"| *{r['especie']}* | {int(r['obs_catalunya'])} | {loc_s} | {pr} | {ul} | {cat} | {rr} | {q} |\n"
        )
    (P / "TABLA_3_PRESENCIA_TENDENCIAS.md").write_text("".join(lines3), encoding="utf-8")

    pres_cat2 = pres_cat.merge(easin[["especie", "EASIN_vias_CBD"]], on="especie", how="left")
    t2 = [
        "# Tabla 2. Origen, hábitat, vía y registros (taxones presentes en Cataluña)\n\n",
        "| Especie | Hábitat | Origen | Vía principal | Primer registro | Última observación | Categoría |\n",
        "|---|---|---|---|---|---|---|\n",
    ]
    for _, r in pres_cat2.sort_values("obs_catalunya", ascending=False).iterrows():
        hab = sd_cell((r.get("habitat_tags") or r.get("medio") or "s. d.").replace(",", "+"))
        orig = sd_cell(r.get("origen_nativo_probable") or "s. d.")
        via = r.get("via_entrada") or r.get("EASIN_vias_CBD") or "s. d."
        via = sd_cell(via)
        if isinstance(via, str) and len(via) > 70:
            via = via[:67] + "…"
        pr = sd_cell(r.get("primera_obs_catalunya") or "")
        ul = sd_cell(r.get("ultima_obs_catalunya") or "")
        cat = cat_label(r)
        t2.append(
            f"| *{r['especie']}* | {hab} | {orig} | {via} | {pr} | {ul} | {cat} |\n"
        )
    (P / "TABLA_2_ORIGEN_VIAS_CAT.md").write_text("".join(t2), encoding="utf-8")

    # S1 — read reg column from existing if present
    s1_path = P / "SUPLEMENTO_TABLA_S1.md"
    reg_map = {}
    if s1_path.exists():
        for ln in s1_path.read_text(encoding="utf-8").splitlines():
            if ln.startswith("| *"):
                parts = [p.strip() for p in ln.split("|")]
                if len(parts) > 3:
                    reg_map[parts[1].strip("*")] = parts[2]
    s1 = [
        "# Material suplementario — Tabla S1\n\n",
        "114 taxones de la lista UE (Reglamento (UE) 1143/2014; Reglamentos de Ejecución 2016/1141–2025/1422; EUR-Lex, 15-oct-2026).\n\n",
        "| Especie | Reglamento UE | CEEA | Presencia CAT | Obs CAT | Primer registro | Última observación | Hábitat | Categoría |\n",
        "|---|---|---|---|---:|---|---|---|---|\n",
    ]
    cat_h2 = {**cat_h, "ausente": "ausente", "recurrente": "recurrente"}
    for _, r in pres.sort_values("especie").iterrows():
        reg = reg_map.get(r["especie"], "—")
        ceea = "sí" if str(r.get("kingdom", "")) else "—"
        pr = sd_cell(r.get("primera_obs_catalunya") or "") if r.presencia_catalunya == "sí" else "—"
        ul = sd_cell(r.get("ultima_obs_catalunya") or "") if int(r.obs_catalunya or 0) > 0 else "—"
        hab = sd_cell(r.get("habitat_tags") or "T")
        cat = cat_h2.get(r.categoria, r.categoria)
        s1.append(
            f"| *{r['especie']}* | {reg} | {ceea} | {r.presencia_catalunya} | {int(r.obs_catalunya or 0)} | {pr} | {ul} | {hab} | {cat} |\n"
        )
    s1_path.write_text("".join(s1), encoding="utf-8")

    if not bf.empty:
        s6 = [
            "# Tabla S6. Identificador BioFauna (índice producción p19, eval 16-oct-2026)\n\n",
            "Acierto de especie en el panel de evaluación vigente (`calib_raw_t05.jsonl`; "
            "**3.061** especies en índice p19, **84,38 %** acierto global oficial según `stats.json`). "
            "«no» = sin filas de eval para ese slug en el panel (no implica ausencia del catálogo).\n\n",
            "| Especie lista UE | Slug BioFauna | n eval | Acierto especie (%) | En panel eval |\n",
            "|---|---|---:|---:|---|\n",
        ]
        for _, r in bf.sort_values("especie").iterrows():
            acc = f"{r['acierto_especie_pct']:.1f}" if pd.notna(r["acierto_especie_pct"]) else "sin datos"
            s6.append(
                f"| *{r['especie']}* | `{r['slug_bf']}` | {int(r['n_eval_p19'])} | {acc} | {r['en_indice_p19']} |\n"
            )
        (P / "SUPLEMENTO_TABLA_S6_BIOFAUNA.md").write_text("".join(s6), encoding="utf-8")

    n_con_eval = (bf["n_eval_p19"] > 0).sum() if not bf.empty else 0
    mean_acc = bf.loc[bf["n_eval_p19"] > 0, "acierto_especie_pct"].mean() if n_con_eval else None
    summary = {
        "ue_taxones": 114,
        "ue_con_eval_p19": int(n_con_eval),
        "acierto_medio_ue_con_eval": round(mean_acc, 2) if mean_acc is not None else None,
        "indice_global_p19_pct": 84.38,
        "indice_especies_p19": 3061,
    }
    (M / "cobertura_bf_ue_p19_20261016.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


def patch_resultados_top15(pres: pd.DataFrame):
    top = pres[pres.presencia_catalunya == "sí"].nlargest(15, "obs_catalunya")
    cat_h = {"ocasional_o_puntual": "ocasional", "llegada_reciente_serie_insuficiente": "reciente"}
    lines = []
    for _, r in top.iterrows():
        ul = sd_cell(r.get("ultima_obs_catalunya") or "—")
        pr = sd_cell(r.get("primera_obs_catalunya") or "sin datos")
        cat = cat_h.get(r.categoria, r.categoria.replace("_", " "))
        hab = (r.get("habitat_tags") or "T").replace(",", "+")
        loc = int(r.localidades_catalunya) if pd.notna(r.localidades_catalunya) else "sin datos"
        lines.append(
            f"| *{r['especie']}* | {int(r.obs_catalunya)} | {int(r.observadores_catalunya or 0)} | {loc} | {pr} | {ul} | {cat} | {hab} |"
        )
    path = P / "RESULTADOS.md"
    text = path.read_text(encoding="utf-8")
    old = "| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Categoría | Hábitat |\n|---|---:|---:|---:|---|---|\n"
    new = (
        "| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Primer registro | Última observación | Categoría | Hábitat |\n"
        "|---|---:|---:|---:|---|---|---|---|\n"
    )
    if old not in text:
        text = text.replace(
            "| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Categoría | Hábitat |",
            "| Especie | Obs CAT | Observadores | Celdas UTM 10 km | Primer registro | Última observación | Categoría | Hábitat |",
        )
        text = text.replace("|---|---:|---:|---:|---|---|", "|---|---:|---:|---:|---|---|---|---|")
    else:
        text = text.replace(old, new)
    # replace table body between header and Etiquetas
    import re as _re

    block = _re.search(
        r"(\| Especie \| Obs CAT.*?\n)(\|.*\n)+?(?=Etiquetas de hábitat)",
        text,
        _re.DOTALL,
    )
    if block:
        body = "\n".join(lines) + "\n\n"
        text = text[: block.start(2)] + body + text[block.end(2) :]
    path.write_text(text, encoding="utf-8")


def main():
    pres = enrich_presencia()
    bf = eval_p19_ue()
    write_all_tables(pres, bf)
    patch_resultados_top15(pres)
    print("OK tablas 20261016", "eval rows", len(bf), "con eval", (bf.n_eval_p19 > 0).sum())


if __name__ == "__main__":
    main()
