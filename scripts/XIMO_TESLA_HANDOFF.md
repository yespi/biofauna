# Ximo Tesla — sesión cerrada (2026-09-02)

**Origen:** hilo "Comportamiento música Ximo" (`bc-f3626d0c`)  
**Despliegue:** hilo "biofauna tier1 consolidación" vía worker HanSolo  
**Estado:** ✅ **desplegado en producción** — sesión cerrada por ahora

## Problemas resueltos

1. **Portada incorrecta en miniplayer Tesla** — título de pista nueva + carátula de la anterior (p. ej. AC/DC + Bad Bunny al saltar manualmente).
2. **Sin auto-avance** — si `_fastSwitchIdx` quedaba clavado, el handler `ended` hacía `return` y no llamaba a `playNext()`.

## Fixes aplicados

| Archivo | Cambio | Marcador en prod |
|---------|--------|------------------|
| `15e-ximo-mediasession.js` | `_lastGoodArtworkPath` — solo reutilizar artwork si `song.path` coincide | 7 matches |
| `15p-ximo-player-ui.js` | `native-ended-switch-stuck-reset` — reset si ping-pong no está sonando | 1 match |

## Producción (verificado)

- **Build:** `ximo-tesla-202609021522`
- **URL:** https://music.yespi.es
- **Health:** ok
- **Código fuente:** [hansolo-dockers PR #23](https://github.com/yespi/hansolo-dockers/pull/23)

```bash
curl -fsS 'https://music.yespi.es/index.html' | grep ce-build
curl -fsS 'https://music.yespi.es/composables/15e-ximo-mediasession.js' | grep _lastGoodArtworkPath
curl -fsS 'https://music.yespi.es/composables/15p-ximo-player-ui.js' | grep native-ended-switch-stuck-reset
```

**En el Tesla:** recargar la webapp para coger el JS nuevo (`ce-build` distinto).

## Cómo se desplegó (no usar el script tal cual)

El script `scripts/deploy-ximo-tesla-fix.sh` de este repo es **referencia**, no el procedimiento usado en prod:

| Riesgo del script | Qué hizo el agente en HanSolo |
|-------------------|------------------------------|
| `find /mnt/docker` parchea backups y `cargaev` | Copió parches solo en `/mnt/docker/ximo/` (PRO + mismo hunk en PRE) |
| Reinicia contenedores `ximo\|music\|lugares` | Reinició **solo** el contenedor `ximo` (lugares no) |

## Worker HanSolo (mantener activo)

Para futuras iteraciones de Ximo/karaoke/Tesla, mantener el **private worker** conectado:

| Campo | Valor |
|-------|-------|
| Worker ID | `9ede1131-bd45-591b-933c-ab319961c399` |
| Display | `/mnt/docker @ HanSolo` |
| Repo asociado | `yespi/hansolo-dockers` |
| SSH (LAN) | `yespi@192.168.1.135` o `192.168.31.135`, puerto **3322** |

Los agentes cloud **sin** `usePrivateWorker: true` no alcanzan `/mnt/docker` ni la LAN; hay que lanzar el agente en el worker o ejecutar en HanSolo directamente.

## Artefactos en este repo (biofauna)

| Ruta | Uso |
|------|-----|
| `scripts/ximo-tesla-patches/` | Parches JS usados como referencia |
| `scripts/deploy-ximo-tesla-fix.sh` | Script genérico (ver advertencias arriba) |
| Este archivo | Bitácora de la sesión |

## Próximos pasos (si reaparece el bug)

1. Confirmar en Tesla que la webapp cargó `ximo-tesla-202609021522` (no caché vieja).
2. Revisar logs de sesión: `mediasession-art-omit`, `native-ended-switch-stuck-reset`, `native-ended-switch-inflight`.
3. Relanzar agente con worker HanSolo para tocar solo `/mnt/docker/ximo/` y reiniciar solo `ximo`.
