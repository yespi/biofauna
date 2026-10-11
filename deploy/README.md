Templates for installing BioFauna on a replica (not HanSolo’s live `/etc`).

| Path | Use |
|------|-----|
| `cron/biofauna-weekly` | `/etc/cron.d/` weekly plan BF-01…BF-10 |
| `cron/crontab.user.example` | Nomenclature dry-run |
| `systemd/biofauna-id.service.example` | Identify API |
| `biofauna.env.example` | Tokens (do not commit a filled copy) |

Full schedule and meaning of each job: [`../docs/cron.md`](../docs/cron.md).
