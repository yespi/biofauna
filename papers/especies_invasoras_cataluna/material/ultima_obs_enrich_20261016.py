#!/usr/bin/env python3
"""Última observación en caja CAT: PG local + inat_backfill + Minka (≤1 req/5 s). Sin iNat API."""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

import pandas as pd
import urllib.parse
import urllib.request

M = Path(__file__).parent
BOX = (40.45, 42.95, 0.1, 3.4)
MINKA_BASE = "https://api.minka-sdg.org/v1"
CACHE = M / "ultima_obs_cache_20261016.json"
SLEEP_MINKA = 5.0


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


def fmt_date(y, m=None, d=None) -> str:
    if y is None or y == "" or str(y) in ("None", "nan"):
        return ""
    try:
        y = int(float(y))
    except (ValueError, TypeError):
        return ""
    if m in (None, "", "None") or (isinstance(m, float) and pd.isna(m)):
        return f"{y}"
    try:
        m = int(float(m))
        d = int(float(d)) if d not in (None, "", "None") and not pd.isna(d) else None
        m = min(max(m, 1), 12)
        if d is None:
            return f"{y:04d}-{m:02d}"
        d = min(max(d, 1), 28)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except (ValueError, TypeError):
        return f"{y}"


def max_date(a: str, b: str) -> str:
    if not a:
        return b or ""
    if not b:
        return a
    return a if a >= b else b


def local_max_dates(id_list: str) -> dict[int, str]:
    """Max research-grade date in box from public_observations + inat_backfill (local)."""
    sql = f"""
    WITH obs AS (
      SELECT taxon_id::int AS taxon_id,
             make_date(
               obs_year::int,
               GREATEST(1, LEAST(12, COALESCE(obs_month, 1)::int)),
               GREATEST(1, LEAST(28, COALESCE(obs_day, 1)::int))
             ) AS d
      FROM public_observations
      WHERE quality_grade = 'research'
        AND lat BETWEEN {BOX[0]} AND {BOX[1]}
        AND lng BETWEEN {BOX[2]} AND {BOX[3]}
        AND taxon_id = ANY(ARRAY[{id_list}]::int[])
        AND obs_year IS NOT NULL
      UNION ALL
      SELECT taxon_id::int, observed_on::date AS d
      FROM inat_backfill_20261011
      WHERE quality_grade = 'research'
        AND lat BETWEEN {BOX[0]} AND {BOX[1]}
        AND lng BETWEEN {BOX[2]} AND {BOX[3]}
        AND taxon_id = ANY(ARRAY[{id_list}]::int[])
        AND observed_on IS NOT NULL
    )
    SELECT taxon_id::int, MAX(d)::text AS ultima
    FROM obs
    GROUP BY taxon_id;
    """
    df = psql(sql)
    out: dict[int, str] = {}
    if df.empty:
        return out
    for _, r in df.iterrows():
        tid = int(r["taxon_id"])
        ul = (r.get("ultima") or "").strip()
        out[tid] = ul[:10] if ul else ""
    return out


def load_minka_token() -> str:
    keys = Path("/mnt/utils/.api-keys").read_text()
    m = re.search(r'^MINKA_API_TOKEN=["\']?([^"\'\n]+)', keys, re.M)
    if not m:
        m = re.search(r"MINKA_API_TOKEN=([^\s#]+)", keys)
    if not m:
        raise RuntimeError("MINKA_API_TOKEN no encontrado en .api-keys")
    return m.group(1).strip().strip('"')


def minka_max_date(taxon_name: str, inat_id: int) -> str:
    token = load_minka_token()
    params = {
        "taxon_name": taxon_name,
        "quality_grade": "research,needs_id",
        "per_page": 1,
        "page": 1,
        "order": "desc",
        "order_by": "observed_on",
        "swlat": BOX[0],
        "nelat": BOX[1],
        "swlng": BOX[2],
        "nelng": BOX[3],
    }
    url = MINKA_BASE + "/observations?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode())
    results = data.get("results") or []
    if not results:
        return ""
    obs = results[0]
    on = obs.get("observed_on") or ""
    if len(on) >= 10:
        return on[:10]
    return on


def main():
    pres = pd.read_csv(M / "presencia_cat_es.csv")
    ids = pres["inat_taxon"].dropna().astype(int).tolist()
    id_list = ",".join(str(i) for i in ids)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    local = local_max_dates(id_list)

    need_minka = []
    for _, r in pres.iterrows():
        if int(r.get("obs_catalunya") or 0) <= 0:
            continue
        tid = int(r.inat_taxon)
        ul = max_date(local.get(tid, ""), cache.get(str(tid), ""))
        if not ul:
            need_minka.append((tid, r["especie"]))

    for tid, name in need_minka:
        key = str(tid)
        if key in cache:
            continue
        print("Minka última obs:", name, tid, flush=True)
        try:
            ul = minka_max_date(name, tid)
            cache[key] = ul
            CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        except Exception as e:
            cache[key] = ""
            CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            print("  error", e, flush=True)
        time.sleep(SLEEP_MINKA)

    for _, r in pres.iterrows():
        if pd.isna(r.inat_taxon):
            continue
        tid = int(r.inat_taxon)
        if int(r.get("obs_catalunya") or 0) <= 0:
            pres.at[r.name, "ultima_obs_catalunya"] = ""
            continue
        ul = max_date(local.get(tid, ""), cache.get(str(tid), ""))
        pres.at[r.name, "ultima_obs_catalunya"] = ul if ul else "sin datos"

    pres.to_csv(M / "presencia_cat_es.csv", index=False)
    filled = pres.loc[pres.obs_catalunya > 0, "ultima_obs_catalunya"]
    n_ok = (filled != "sin datos").sum()
    print("OK ultima_obs", n_ok, "/", len(filled), "con fecha")


if __name__ == "__main__":
    main()
