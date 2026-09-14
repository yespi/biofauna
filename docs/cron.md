# BioFauna — scheduled jobs (cron)

HanSolo runs these as `/etc/cron.d/biofauna-semanal` plus a few lines in the `yespi` crontab.
Times are **Europe/Madrid**. GPU jobs (BF-05, BF-07) contend with the identify service: on a 12 GB card, stop or nicen identify while they run.

Templates: [`../deploy/cron/`](../deploy/cron/). Install:

```bash
export BIOFAUNA_ROOT=/opt/biofauna   # clone of this repo
export IMAGES_DIR=/data/fotofauna-images
sudo cp deploy/cron/biofauna-weekly /etc/cron.d/biofauna-weekly
sudo chmod 644 /etc/cron.d/biofauna-weekly
# optional user crontab extras:
crontab -l | cat - deploy/cron/crontab.user.example | crontab -
```

Edit the template and replace `/opt/biofauna` if your clone lives elsewhere. Jobs that need PyTorch must run as the user who has `torch`/`numpy` installed (on HanSolo that bug was real: BF-05/06/07 as `root` failed with `No module named numpy`).

## Weekly plan (BF-01 … BF-10)

| ID | When | Script | What it does |
|----|------|--------|----------------|
| **BF-01** | Mon 10:00 | `scripts/repesca_diaria.py` | iNaturalist photos for species still short of the 1000 cap; curator feedback. |
| **BF-02** | Mon 11:00 | `scripts/autoaprendizaje_minka.py` | Minka research-grade photos + `dataset/minka_manifest.jsonl`. |
| **BF-03** | Tue 10:00 | `scripts/autoaprendizaje_inat.py` | Same for iNaturalist + `dataset/inat_manifest.jsonl`. |
| **BF-04** | Wed 10:00 | `scripts/reverificar_minka.py` | Re-fetch Minka obs from the manifest; move/delete if the taxon changed. |
| **BF-05** | Thu 09:00 | `scripts/reembed_vith.py` | Re-embed `IMAGES_DIR` → `data/patterns/` (ViT-H). HanSolo uses `consolidate_species_reembed.py` (SSD+HDD, not in this repo). |
| **BF-06** | Thu 10:00 | `fit_calib.py` then `fit_calib_hierarchical.py` | Refit logistic + hierarchical AutoID thresholds. Needs a prior harvest jsonl. |
| **BF-07** | Fri 14:00 | `harvest_calib.py 3` | Out-of-sample harvest, 3 photos/species, leak check. GPU. |
| **BF-08** | Sat 10:00 | `archive_processed.py` + `audit_biofauna.sh` | Keep ~300 photos/species on the fast disk; health check. |
| **BF-09** | Sun 09:00 | `renovar_especies.py` | On species at the 1000-photo cap, delete the oldest 200 so Mon/Tue can refill. |
| **BF-10** | Sun 10:00 | `reverificar_minka.py` | Second taxon-drift pass. |

## Extra jobs (HanSolo user crontab)

| When | Script | What |
|------|--------|------|
| Sun 03:15 | `taxonomy_nomenclature_cron.sh` | WoRMS/GBIF **dry-run**. Does **not** `--apply-safe` unless you uncomment it. |
| Daily 09:00 | (optional) `fit`/`stats` | On HanSolo, `gen_stats.py` refreshes the FotoFauna admin panel. **Not shipped** (talks to `fauna_api` / Docker). |

`15 * * * * wave_watchdog.sh` and `claude_session_keepalive.sh` are **HanSolo ops** (remediation waves + Cursor sessions). They are not reconstruction. Do not install them on a replica.

## Environment

| Variable | Meaning |
|----------|---------|
| `BIOFAUNA_ROOT` | Clone of this repo |
| `IMAGES_DIR` | Per-slug photo folders (`minka_*.jpg`, `inat_*.jpg`) |
| `ARCHIVE_DIR` | Cold copy of extra photos (BF-08). Default `$BIOFAUNA_ROOT/dataset/photo_archive` |
| `HF_TOKEN` | Hugging Face (embed jobs) |
| `INAT_API_TOKEN` / `MINKA_API_TOKEN` | Optional; public endpoints work without them, rate limits are tighter |

## Identify service (not a cron)

`deploy/systemd/biofauna-id.service.example` — `uvicorn src.identify_service:app` on `:8090`. Do not commit API tokens in unit files; use `EnvironmentFile=-/etc/biofauna.env`.

## Respect platform ToS

iNaturalist and Minka rate-limit and restrict bulk download. Keep `MAX_TOTAL` / sleeps as in the scripts; do not tighten the cron to “every hour, whole catalog”.
