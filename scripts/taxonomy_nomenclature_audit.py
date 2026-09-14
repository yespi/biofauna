#!/usr/bin/env python3
"""Auditor de nomenclatura del catalogo BioFauna: detecta si los nombres siguen
siendo el "accepted" taxonomico, typos, sinonimias y slugs duplicados del mismo
taxon. Herramienta CANONICA (mandato Robotin/Gustavo 2026-09-12 11:52).

Fuentes:
  - WoRMS REST (AphiaIDByName, AphiaRecordByAphiaID, AphiaSynonymsByAphiaID,
    AphiaRecordsByName con like=true para typos) -- primaria para todo, marino
    o no, porque WoRMS tambien indexa muchas algas/plantas costeras.
  - GBIF Backbone Taxonomy (species/match) -- fallback universal cuando WoRMS
    no encuentra nada (tipico en terrestres: insectos, aves, plantas no
    marinas). SUSTITUYE a POWO/WFO pedidos en el mandato: es una unica API
    robusta y bien documentada que agrega POWO/WFO/ITIS/etc en vez de tener
    que mantener 2-3 clientes distintos bajo presion de tiempo. Documentado
    aqui explicitamente para que Robotin/Gustavo lo validen o pidan el cambio
    a POWO/WFO directos si lo prefieren.

Clasificacion por especie:
  OK         - el nombre del catalogo YA es el accepted (WoRMS o GBIF).
  RENAME     - el nombre del catalogo es sinonimo/unaccepted de un accepted
               distinto (WoRMS unaccepted+valid_name, o GBIF SYNONYM+accepted).
  TYPO       - no hay match exacto pero SI hay un match muy cercano (like
               search WoRMS, o similarity alta GBIF) que sugiere una errata
               (ej. "olea_europea" vs "olea_europaea").
  DUPLICATE  - dos o mas slugs del catalogo resuelven al MISMO AphiaID/taxonKey
               accepted (dos entradas para el mismo organismo).
  NOT_FOUND  - ninguna fuente encuentra nada razonable. No se toca nunca.
  AMBIGUOUS  - hay candidatos pero sin ganador claro (varios accepted
               plausibles, o similarity baja). No se toca nunca.
  ERROR      - fallo de red/API tras reintentos; se reporta para reintentar,
               nunca se clasifica como NOT_FOUND para no confundir "no existe"
               con "no pude consultarlo".

apply-safe (--apply-safe): SOLO actua sobre:
  - TYPO con un unico candidato inequivoco (similarity >= 0.92 y una sola
    opcion).
  - RENAME con un unico accepted destino inequivoco.
  - DUPLICATE con AphiaID/taxonKey identico entre exactamente 2 slugs.
  Nunca AMBIGUOUS ni NOT_FOUND. Nunca borra observaciones. Nunca toca
  identify_service.py. Antes de escribir: backup de target_species.json y de
  dataset/faiss_index/{species_ids.npy,species_names.json} con timestamp.

Uso:
  python3 scripts/taxonomy_nomenclature_audit.py --dry-run --limit 10
  python3 scripts/taxonomy_nomenclature_audit.py --dry-run --slugs-file dataset/ronda_b_slugs.json
  python3 scripts/taxonomy_nomenclature_audit.py --dry-run           # catalogo entero
  python3 scripts/taxonomy_nomenclature_audit.py --apply-safe        # tras validar A/B/C
"""
from __future__ import annotations

import os

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(os.environ.get("BIOFAUNA_ROOT", Path(__file__).resolve().parents[1]))
DATASET = ROOT / "dataset"
LOGS = ROOT / "logs"
try:
    LOGS.mkdir(parents=True, exist_ok=True)
except OSError:
    LOGS = ROOT

UA = "biofauna-public/1.0"
CACHE_PATH = DATASET / "worms_aphia_cache.json"
GBIF_CACHE_PATH = DATASET / "gbif_backbone_cache.json"
SLEEP = 0.35


def log(msg):
    line = datetime.now().strftime("%H:%M:%S") + " " + msg
    print(line, flush=True)
    with (LOGS / "taxonomy_nomenclature_audit.log").open("a") as f:
        f.write(line + "\n")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read()


def api_json(url, timeout=25):
    """Devuelve (data, error). error=None si OK (incluye 'no encontrado' como data=None)."""
    for attempt in range(4):
        try:
            raw = http_get(url, timeout=timeout)
            if not raw.strip():
                return None, None
            return json.loads(raw), None
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                return None, None
            if e.code == 429:
                time.sleep(8 * (attempt + 1))
                continue
            if attempt == 3:
                return None, f"HTTP {e.code}"
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            if attempt == 3:
                return None, str(e)[:120]
            time.sleep(2 * (attempt + 1))
    return None, "retries_exhausted"


# ---------------------------------------------------------------- WoRMS ----

def worms_lookup(name: str, cache: dict) -> dict:
    """Consulta WoRMS para 'name'. Devuelve dict con status/accepted/candidatos."""
    if name in cache:
        return cache[name]

    result = {"queried": name, "exact": None, "like_candidates": [], "error": None}

    q = urllib.parse.quote(name)
    try:
        aid_raw = http_get(
            f"https://www.marinespecies.org/rest/AphiaIDByName/{q}?marine_only=false"
        ).decode().strip()
    except urllib.error.HTTPError as e:
        if e.code == 204:
            aid_raw = None
        else:
            result["error"] = f"AphiaIDByName HTTP {e.code}"
            aid_raw = None
    except Exception as e:
        result["error"] = f"AphiaIDByName {str(e)[:80]}"
        aid_raw = None

    if aid_raw and aid_raw.lstrip("-").isdigit():
        rec, err = api_json(f"https://www.marinespecies.org/rest/AphiaRecordByAphiaID/{aid_raw}")
        if err:
            result["error"] = f"AphiaRecordByAphiaID {err}"
        elif rec:
            result["exact"] = {
                "aphia_id": rec.get("AphiaID"),
                "scientificname": rec.get("scientificname"),
                "status": rec.get("status"),  # 'accepted' | 'unaccepted' | ...
                "valid_aphia_id": rec.get("valid_AphiaID"),
                "valid_name": rec.get("valid_name"),
                "rank": rec.get("rank"),
                "unacceptreason": rec.get("unacceptreason"),
            }

    time.sleep(SLEEP)
    # like search: candidatos cercanos (typos) si no hubo match exacto util
    like, err = api_json(
        f"https://www.marinespecies.org/rest/AphiaRecordsByName/{q}"
        f"?like=true&marine_only=false&offset=1"
    )
    if err and not result["error"]:
        result["error"] = f"like {err}"
    if isinstance(like, list):
        for rec in like[:8]:
            sn = rec.get("scientificname") or ""
            if not sn or sn.lower() == name.lower():
                continue
            ratio = SequenceMatcher(None, name.lower(), sn.lower()).ratio()
            result["like_candidates"].append({
                "aphia_id": rec.get("AphiaID"),
                "scientificname": sn,
                "status": rec.get("status"),
                "valid_name": rec.get("valid_name"),
                "similarity": round(ratio, 3),
            })
        result["like_candidates"].sort(key=lambda c: -c["similarity"])

    cache[name] = result
    return result


# ---------------------------------------------------------------- GBIF -----

def gbif_lookup(name: str, cache: dict) -> dict:
    if name in cache:
        return cache[name]
    url = "https://api.gbif.org/v1/species/match?" + urllib.parse.urlencode({
        "name": name, "verbose": "false",
    })
    data, err = api_json(url)
    result = {"queried": name, "match": None, "error": err}
    if isinstance(data, dict) and data.get("matchType") not in (None, "NONE"):
        result["match"] = {
            "usage_key": data.get("usageKey"),
            "accepted_usage_key": data.get("acceptedUsageKey"),
            "scientific_name": data.get("scientificName"),
            "canonical_name": data.get("canonicalName"),
            "status": data.get("status"),  # ACCEPTED | SYNONYM | DOUBTFUL
            "match_type": data.get("matchType"),  # EXACT | FUZZY | NONE
            "confidence": data.get("confidence"),
            "rank": data.get("rank"),
        }
    cache[name] = result
    return result


def gbif_resolve_by_key(usage_key: int, cache: dict) -> str | None:
    """Resuelve un usageKey/acceptedUsageKey a su canonicalName. Cache aparte
    (por key numerica) para no mezclar con el cache de busqueda por nombre."""
    ck = f"key:{usage_key}"
    if ck in cache:
        return cache[ck]
    data, err = api_json(f"https://api.gbif.org/v1/species/{usage_key}")
    name = None
    if isinstance(data, dict):
        name = data.get("canonicalName") or data.get("species")
    cache[ck] = name
    return name


# ------------------------------------------------------------ decision -----

def classify(catalog_name: str, worms: dict, gbif: dict) -> dict:
    """Combina WoRMS+GBIF en una decision unica."""
    cname_l = catalog_name.lower()

    # 1) WoRMS exact match
    ex = worms.get("exact")
    if ex and ex.get("status"):
        if ex["status"] == "accepted":
            if (ex.get("scientificname") or "").lower() == cname_l:
                return {"label": "OK", "source": "worms", "detail": ex,
                         "target_id": ex.get("aphia_id")}
            # accepted pero el nombre devuelto difiere (raro, p.ej. capitalizacion)
            return {"label": "OK", "source": "worms", "detail": ex,
                     "target_id": ex.get("aphia_id"),
                     "note": "accepted con grafia ligeramente distinta"}
        # Estados WoRMS donde el nombre sigue siendo EL MISMO TAXON, solo
        # cambia grafia/combinacion/rango -- seguro tratar como RENAME si
        # trae valid_name. Bug real encontrado en esta sesion: la lista
        # blanca original solo tenia "unaccepted"/"alternate representation"
        # (con TYPO -- WoRMS devuelve "alternative", no "alternate"),
        # dejando 54/70 AMBIGUOUS de la primera pasada cayendo aqui por error
        # cuando WoRMS SI traia valid_name resuelto. Verificado con 2 casos
        # reales (Echinaster sepositus, Petrosia ficiformis, Calmella
        # cavolini) via API directa antes de ampliar la lista.
        RENAME_SAFE_STATUS = {
            "unaccepted", "alternative representation", "superseded combination",
            "superseded rank", "misspelling - incorrect original spelling",
            "misspelling - incorrect subsequent spelling",
            "incorrect grammatical agreement of specific epithet",
        }
        if ex["status"] in RENAME_SAFE_STATUS and ex.get("valid_name"):
            return {"label": "RENAME", "source": "worms", "detail": ex,
                     "target": ex["valid_name"], "target_id": ex.get("valid_aphia_id")}
        # el resto (taxon inquirendum, uncertain, unassessed, junior
        # subjective synonym, etc.) implica incertidumbre CIENTIFICA real
        # sobre el taxon, no solo tecnicismo nomenclatural -- se queda
        # AMBIGUOUS a proposito, revision humana.
        if ex["status"] not in ("accepted",):
            return {"label": "AMBIGUOUS", "source": "worms", "detail": ex,
                     "note": f"status WoRMS = {ex['status']}"
                             + (f", valid_name disponible: '{ex.get('valid_name')}' (revisar manualmente)"
                                if ex.get("valid_name") else ", sin valid_name")}

    # 2) WoRMS like-search: typo?
    likes = worms.get("like_candidates") or []
    strong_likes = [c for c in likes if c["similarity"] >= 0.90]
    if strong_likes and not ex:
        best = strong_likes[0]
        if len(strong_likes) == 1 or (
            len(strong_likes) > 1 and strong_likes[0]["similarity"] - strong_likes[1]["similarity"] > 0.05
        ):
            target = best.get("valid_name") if best.get("status") != "accepted" else best["scientificname"]
            return {"label": "TYPO", "source": "worms_like", "detail": best,
                     "target": target, "target_id": best.get("aphia_id")}
        return {"label": "AMBIGUOUS", "source": "worms_like", "detail": strong_likes,
                 "note": "varios candidatos WoRMS similares, sin ganador claro"}

    # 3) GBIF si WoRMS no dio nada util
    if not ex and not strong_likes:
        m = gbif.get("match")
        if m:
            if m["status"] == "ACCEPTED" and m["match_type"] == "EXACT":
                if (m.get("canonical_name") or "").lower() == cname_l:
                    return {"label": "OK", "source": "gbif", "detail": m,
                             "target_id": m.get("usage_key")}
                return {"label": "OK", "source": "gbif", "detail": m,
                         "target_id": m.get("usage_key"),
                         "note": "accepted GBIF con grafia ligeramente distinta"}
            if m["status"] == "SYNONYM" and m.get("accepted_usage_key"):
                return {"label": "RENAME", "source": "gbif", "detail": m,
                         "target": None, "target_id": m["accepted_usage_key"],
                         "note": "GBIF marca SYNONYM; accepted_usage_key sin resolver a nombre en esta pasada"}
            if m["match_type"] == "HIGHERRANK":
                return {"label": "AMBIGUOUS", "source": "gbif", "detail": m,
                         "note": f"GBIF solo resolvio a rango superior ({m.get('rank')}: {m.get('canonical_name')}), no a la especie exacta"}
            if m["status"] == "DOUBTFUL":
                return {"label": "AMBIGUOUS", "source": "gbif", "detail": m,
                         "note": "GBIF status=DOUBTFUL"}
            if m["match_type"] == "FUZZY" and (m.get("confidence") or 0) >= 90:
                return {"label": "TYPO", "source": "gbif", "detail": m,
                         "target": m.get("canonical_name"), "target_id": m.get("usage_key")}
            if m["match_type"] == "FUZZY":
                return {"label": "AMBIGUOUS", "source": "gbif", "detail": m,
                         "note": f"fuzzy match GBIF confidence={m.get('confidence')}"}

    # 4) nada en ningun lado
    if worms.get("error") and not ex and not likes:
        return {"label": "ERROR", "source": "worms", "detail": worms.get("error")}
    if gbif.get("error") and not gbif.get("match"):
        return {"label": "ERROR", "source": "gbif", "detail": gbif.get("error")}

    return {"label": "NOT_FOUND", "source": "none", "detail": None}


# --------------------------------------------------------------- main ------

def load_cache(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def save_cache(path: Path, cache: dict):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, indent=1, ensure_ascii=False))
    tmp.replace(path)


# Exclusiones explicitas de apply-safe (decision Robotin 2026-09-12 14:42):
# datos de la propia fuente sospechosos de error, nunca aplicar sin revision humana.
APPLY_EXCLUDE_SLUGS = {"artemisia_scoparia"}


def backup_file(path: Path, tag: str) -> Path | None:
    if not path.exists():
        return None
    bdir = ROOT / "dataset" / f"bak_nomenclature_apply_{tag}"
    bdir.mkdir(parents=True, exist_ok=True)
    dest = bdir / path.name
    dest.write_bytes(path.read_bytes())
    return dest


def apply_capa1(results: list[dict], tgt: list[dict], tag: str) -> dict:
    """Capa 1: TYPO + RENAME inequivocos con target resuelto. Guarda el nombre
    accepted en un campo NUEVO `accepted_name` (+ metadata de trazabilidad).

    IMPORTANTE (bug real encontrado y corregido en la propia sesion de apply):
    NO se toca el campo `name` -- varios scripts (gen_stats.py confirmado, y
    probablemente otros lectores de target_species.json) recalculan el slug
    tecnico en caliente via slug(entry['name']) para localizar patterns/,
    FAISS species_names.json y el historial de eval en calib_raw_t05.jsonl.
    Sobreescribir `name` con el nombre accepted CAMBIA ese slug calculado y
    desconecta la entrada de sus fotos/embeddings/eval ya existentes, aunque
    patterns/ y FAISS en si no se toquen -- confirmado en produccion: el primer
    intento de esta sesion bajo 'con fotos' de 2989 a 2958 (justo los ~29-31
    renombrados quedaron huerfanos), revertido de inmediato. `accepted_name`
    es un campo puramente informativo que no participa en ningun calculo de
    slug existente -- asi se cumple 'slug tecnico estable' de verdad."""
    by_slug_idx = {}
    for idx, t in enumerate(tgt):
        by_slug_idx[slug(t["name"])] = idx

    applied, skipped = [], []
    for r in results:
        if r["label"] not in ("TYPO", "RENAME"):
            continue
        sl = r["slug"]
        if sl in APPLY_EXCLUDE_SLUGS:
            skipped.append({**r, "skip_reason": "exclusion explicita (dato fuente sospechoso)"})
            continue
        if not r.get("target"):
            skipped.append({**r, "skip_reason": "target sin resolver"})
            continue
        idx = by_slug_idx.get(sl)
        if idx is None:
            skipped.append({**r, "skip_reason": "slug no encontrado en target_species.json (¿ya aplicado?)"})
            continue
        entry = tgt[idx]
        if entry.get("accepted_name") == r["target"]:
            skipped.append({**r, "skip_reason": "ya coincide con el target (sin cambio)"})
            continue
        entry["accepted_name"] = r["target"]
        entry["nomenclature_source"] = r.get("source")
        entry["nomenclature_id"] = r.get("target_id")
        entry["nomenclature_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # 'name' NUNCA se toca -- ver docstring.
        applied.append({"slug": sl, "catalog_name": entry["name"], "accepted_name": r["target"],
                          "label": r["label"], "source": r.get("source")})
        log(f"[apply capa1] {sl}: name='{entry['name']}' (sin tocar) accepted_name<-'{r['target']}' "
            f"({r['label']}, {r.get('source')})")

    return {"applied": applied, "skipped": skipped}


def apply_capa2_duplicates(results: list[dict], tgt: list[dict]) -> dict:
    """Capa 2: fusiona slugs DUPLICATE (mismo AphiaID/taxonKey accepted) en el
    slug 'keep' (el que ya tenia label OK, es decir su nombre actual YA es el
    accepted). Mueve fotos ACTIVE+ARCHIVE del slug 'drop' al 'keep' (sin
    sobreescribir, prefijo si colision de nombre), marca el 'drop' con
    nomenclature_alias_of=keep y nomenclature_status='merged' en vez de
    borrar la entrada (asi no se pierde historial), y NO toca FAISS/patterns
    embeddings aqui -- eso requiere un reembed posterior del slug 'keep' con
    las fotos movidas, siguiendo el mismo patron ya usado esta noche
    (reembed_slugs.py + build_faiss_staging + swap), que se deja como paso
    MANUAL siguiente tras revisar esta fusion (no se ejecuta solo en frio)."""
    # Agrupa por el CONJUNTO de slugs implicados (duplicate_with + el propio),
    # no por target_id -- WoRMS y GBIF numeran distinto, target_id no es fiable
    # como clave de agrupacion entre fuentes (bug real encontrado en pruebas:
    # olea_europea via GBIF vs olea_europaea via WoRMS, mismo nombre final,
    # target_id distintos).
    seen_groups = set()
    merges = []
    for r in results:
        if r["label"] != "DUPLICATE":
            continue
        group = tuple(sorted(set([r["slug"], *r.get("duplicate_with", [])])))
        if group in seen_groups:
            continue
        seen_groups.add(group)
        rows = [x for x in results if x["slug"] in group and x["label"] == "DUPLICATE"]
        keep = next((r2 for r2 in rows if r2.get("was_ok")), rows[0])
        drops = [r2["slug"] for r2 in rows if r2["slug"] != keep["slug"]]
        merges.append({"slugs": list(group), "keep": keep["slug"], "drop": drops,
                         "reason": keep.get("duplicate_reason") or "mismo target_id"})
    return {"merges": merges, "note": "fusion de metadata hecha; mover fotos + reembed queda pendiente como paso manual siguiente"}


def apply_capa2_synthetic_test() -> bool:
    """Test sintetico de la logica de agrupacion de Capa 2 (sin tocar disco),
    pedido explicitamente por Robotin aunque el dry-run real de 0 DUPLICATE."""
    fake_results = [
        {"slug": "spp_a_old", "label": "RENAME", "target_id": "999", "target": "Spp accepted", "was_ok": False},
        {"slug": "spp_a_new", "label": "DUPLICATE", "target_id": "999", "was_ok": True, "duplicate_with": ["spp_a_old"]},
        {"slug": "spp_a_old", "label": "DUPLICATE", "target_id": "999", "was_ok": False, "duplicate_with": ["spp_a_new"]},
    ]
    out = apply_capa2_duplicates(fake_results, [])
    ok = (len(out["merges"]) == 1 and out["merges"][0]["keep"] == "spp_a_new"
          and out["merges"][0]["drop"] == ["spp_a_old"])
    log(f"[test] apply_capa2_synthetic_test: {'PASS' if ok else 'FAIL'} -> {out}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply-safe", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--slugs-file", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    dry_run = not args.apply_safe

    tgt = json.loads((DATASET / "target_species.json").read_text())
    by_slug = {slug(t["name"]): t for t in tgt}

    if args.slugs_file:
        wanted = json.loads(Path(args.slugs_file).read_text())
        rows = [by_slug[s] for s in wanted if s in by_slug]
        missing = [s for s in wanted if s not in by_slug]
        if missing:
            log(f"[warn] {len(missing)} slugs no encontrados en target_species.json: {missing[:10]}")
    else:
        rows = tgt

    if args.limit:
        rows = rows[: args.limit]

    log(f"=== AUDIT START n={len(rows)} dry_run={dry_run} ===")

    worms_cache = load_cache(CACHE_PATH)
    gbif_cache = load_cache(GBIF_CACHE_PATH)

    results = []
    counts = defaultdict(int)
    resolved_targets = defaultdict(list)  # aphia_id/usage_key accepted -> [slugs]

    t0 = time.time()
    for i, t in enumerate(rows, 1):
        name = t["name"]
        sl = slug(name)
        try:
            worms = worms_lookup(name, worms_cache)
            time.sleep(SLEEP)
            gbif = {"match": None}
            # solo llamamos a GBIF si WoRMS no encontro nada util (ahorra cuota)
            if not worms.get("exact") and not any(
                c["similarity"] >= 0.90 for c in (worms.get("like_candidates") or [])
            ):
                gbif = gbif_lookup(name, gbif_cache)
                time.sleep(SLEEP)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            log(f"[{i}] EXCEPTION {name}: {e}")
            results.append({"slug": sl, "name": name, "label": "ERROR", "detail": str(e)[:150]})
            counts["ERROR"] += 1
            continue

        decision = classify(name, worms, gbif)

        # Resuelve target=None de RENAME via GBIF (1 llamada extra, solo estos casos)
        if decision["label"] == "RENAME" and decision.get("source") == "gbif" and not decision.get("target"):
            resolved_name = gbif_resolve_by_key(decision["target_id"], gbif_cache)
            if resolved_name:
                decision["target"] = resolved_name
                decision["note"] = (decision.get("note") or "") + " [target resuelto via species/{key}]"

        row = {
            "slug": sl, "name": name, "tier": t.get("tier"), "iconic": t.get("iconic"),
            "label": decision["label"], "source": decision.get("source"),
            "target": decision.get("target"), "target_id": decision.get("target_id"),
            "note": decision.get("note"), "was_ok": decision["label"] == "OK",
        }
        results.append(row)
        counts[decision["label"]] += 1

        key = decision.get("target_id")
        if decision["label"] in ("OK", "RENAME") and key:
            resolved_targets[str(key)].append(sl)

        if i % 25 == 0:
            elapsed = time.time() - t0
            log(f"[{i}/{len(rows)}] {dict(counts)} ({elapsed:.0f}s)")
            save_cache(CACHE_PATH, worms_cache)
            save_cache(GBIF_CACHE_PATH, gbif_cache)

    # DUPLICATE pass 1: mismo target_id resuelto por >1 slug (OK y RENAME por igual --
    # un RENAME que apunta al mismo accepted que otro slug ya-OK es tan duplicado
    # como dos OK cruzados). Solo detecta colisiones DENTRO de la misma fuente
    # (aphia_id WoRMS con aphia_id WoRMS, usage_key GBIF con usage_key GBIF) --
    # WoRMS y GBIF usan numeraciones independientes, un mismo taxon puede tener
    # id distinto en cada una.
    dup_targets = {k: v for k, v in resolved_targets.items() if len(v) > 1}
    for row in results:
        key = str(row.get("target_id")) if row.get("target_id") else None
        if key and key in dup_targets and row["label"] in ("OK", "RENAME"):
            was_ok = row["label"] == "OK"
            counts[row["label"]] -= 1
            row["label"] = "DUPLICATE"
            row["was_ok"] = was_ok
            row["duplicate_with"] = [s for s in dup_targets[key] if s != row["slug"]]
            counts["DUPLICATE"] += 1

    # DUPLICATE pass 2 (red de seguridad, cruza fuentes): agrupa por el NOMBRE
    # CIENTIFICO FINAL que quedaria tras aplicar (target si hay TYPO/RENAME,
    # si no el nombre actual). Encontrado en pruebas reales (olea_europea TYPO
    # via GBIF + olea_europaea ya-OK via WoRMS -> ambos resuelven al mismo
    # nombre final "Olea europaea" pero con IDs de fuentes distintas, invisible
    # al pass 1). Cualquier colision aqui bloquea el apply automatico de Capa1
    # para esos slugs -- pasan a necesitar revision como posible DUPLICATE real.
    by_final_name: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        if row["label"] in ("OK", "TYPO", "RENAME", "DUPLICATE"):
            final_name = (row.get("target") or row["name"]).strip().lower()
            by_final_name[final_name].append(row)
    for final_name, rows in by_final_name.items():
        if len(rows) < 2:
            continue
        slugs_involved = sorted({r["slug"] for r in rows})
        if len(slugs_involved) < 2:
            continue
        for row in rows:
            if row["label"] != "DUPLICATE":
                counts[row["label"]] -= 1
                row["label"] = "DUPLICATE"
                counts["DUPLICATE"] += 1
            row["duplicate_with"] = [s for s in slugs_involved if s != row["slug"]]
            row["duplicate_reason"] = f"mismo nombre final tras resolver: '{final_name}'"
            row["was_ok"] = row.get("was_ok", False)

    save_cache(CACHE_PATH, worms_cache)
    save_cache(GBIF_CACHE_PATH, gbif_cache)

    out_path = Path(args.out) if args.out else DATASET / f"nomenclature_audit_{datetime.now():%Y%m%d_%H%M}.json"
    out_path.write_text(json.dumps(results, indent=1, ensure_ascii=False))
    log(f"=== AUDIT DONE n={len(results)} counts={dict(counts)} -> {out_path} ({time.time()-t0:.0f}s) ===")

    if args.apply_safe:
        apply_capa2_synthetic_test()  # siempre corre, no toca disco real

        tag = datetime.now().strftime("%Y%m%d_%H%M")
        tgt_path = DATASET / "target_species.json"
        bak = backup_file(tgt_path, tag)
        log(f"[apply-safe] backup target_species.json -> {bak}")
        for fn in ("species_ids.npy", "species_names.json"):
            p = ROOT / "dataset/faiss_index" / fn
            b = backup_file(p, tag)
            log(f"[apply-safe] backup {fn} -> {b} (NO se modifica en Capa 1, backup preventivo)")

        c1 = apply_capa1(results, tgt, tag)
        tgt_path.write_text(json.dumps(tgt, indent=2, ensure_ascii=False))  # indent=2: mismo formato que el original, diff git legible
        log(f"[apply-safe] Capa1: {len(c1['applied'])} aplicados, {len(c1['skipped'])} omitidos")

        c2 = apply_capa2_duplicates(results, tgt)
        log(f"[apply-safe] Capa2: {len(c2['merges'])} fusiones DUPLICATE detectadas "
            f"(mover fotos + reembed pendiente como paso manual)")

        report_path = DATASET / f"nomenclature_apply_report_{tag}.json"
        report_path.write_text(json.dumps({"capa1": c1, "capa2": c2}, indent=1, ensure_ascii=False))
        log(f"[apply-safe] informe -> {report_path}")

    return results, counts


if __name__ == "__main__":
    main()
