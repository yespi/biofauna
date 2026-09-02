# Ximo Tesla — handoff para agente en HanSolo

**Origen:** hilo "Comportamiento música Ximo" (`bc-f3626d0c`)  
**Destino:** hilo con acceso a HanSolo (p. ej. "biofauna tier1 consolidación")  
**Estado:** parches listos, producción **sin desplegar** (verificado 2026-09-02)

## Problemas

1. **Portada incorrecta en miniplayer Tesla** — título de pista nueva + carátula de la anterior (AC/DC + Bad Bunny).
2. **Sin auto-avance** — si `_fastSwitchIdx` queda clavado, el handler `ended` hace `return` y no llama a `playNext()`.

## Fixes (ya en este branch)

| Archivo | Cambio |
|---------|--------|
| `15e-ximo-mediasession.js` | `_lastGoodArtworkPath` — solo reutilizar artwork si `song.path` coincide |
| `15p-ximo-player-ui.js` | `native-ended-switch-stuck-reset` — reset si ping-pong no está sonando |

Parches completos: `scripts/ximo-tesla-patches/`  
Script de despliegue: `scripts/deploy-ximo-tesla-fix.sh`

## Ejecutar en HanSolo

```bash
hostname   # debe ser HanSolo, no cursor
cd /mnt/docker/biofauna   # o donde tengas el clone de yespi/biofauna
git fetch origin cursor/ximo-tesla-handoff-1c00
git checkout cursor/ximo-tesla-handoff-1c00

export PATCH_SRC="$(pwd)/scripts/ximo-tesla-patches"
sudo bash scripts/deploy-ximo-tesla-fix.sh
```

## Verificación

```bash
curl -fsS 'https://music.yespi.es/composables/15e-ximo-mediasession.js' | grep -c '_lastGoodArtworkPath'   # >0
curl -fsS 'https://music.yespi.es/composables/15p-ximo-player-ui.js' | grep -c 'native-ended-switch-stuck-reset'  # >0
```

Producción actual (sin fix): `ce-build` = `ximo-858e9995`, 0 matches en ambos greps.
