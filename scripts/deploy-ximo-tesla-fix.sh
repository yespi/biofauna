#!/usr/bin/env bash
# Ejecutar EN HanSolo (LAN o localhost), no desde cloud Cursor.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_SRC="${PATCH_SRC:-$SCRIPT_DIR/ximo-tesla-patches}"
NEW_BUILD="ximo-tesla-$(date +%Y%m%d%H%M)"

find_composables() {
  find /mnt/docker -type f \( -name '15e-ximo-mediasession.js' -o -name '15p-ximo-player-ui.js' \) 2>/dev/null
}

find_index_html() {
  find /mnt/docker -type f -name 'index.html' 2>/dev/null | rg -i 'lugares|music|ximo|yespi' || find /mnt/docker -maxdepth 4 -type f -name 'index.html' 2>/dev/null
}

echo "=== Host ==="
hostname
echo "PATCH_SRC=$PATCH_SRC"

echo "=== Docs ==="
ls -la /mnt/docs/ 2>/dev/null | head -20 || true
rg -il 'ximo|karaoke|tesla' /mnt/docs/ 2>/dev/null | head -20 || true

echo "=== Locate composables ==="
mapfile -t FILES < <(find_composables)
if ((${#FILES[@]} == 0)); then
  echo "No se encontraron composables bajo /mnt/docker"
  exit 1
fi
printf '%s\n' "${FILES[@]}"

MS=""
PU=""
for f in "${FILES[@]}"; do
  case "$f" in
    *15e-ximo-mediasession.js) MS="$f" ;;
    *15p-ximo-player-ui.js) PU="$f" ;;
  esac
done

if [[ -z "$MS" || -z "$PU" ]]; then
  echo "Faltan 15e o 15p en /mnt/docker"
  exit 1
fi

for f in "$MS" "$PU"; do
  cp -a "$f" "${f}.bak-$(date +%Y%m%d%H%M%S)"
done

deploy_file() {
  local target="$1" name="$2" marker="$3"
  if [[ -f "$PATCH_SRC/$name" ]] && grep -q "$marker" "$PATCH_SRC/$name" 2>/dev/null; then
    echo "Copiando $PATCH_SRC/$name -> $target"
    cp -a "$PATCH_SRC/$name" "$target"
    return 0
  fi
  return 1
}

# --- 15e: stale artwork (path-scoped _lastGoodArtwork) ---
if grep -q '_lastGoodArtworkPath' "$MS"; then
  echo "15e ya tiene _lastGoodArtworkPath"
elif deploy_file "$MS" '15e-ximo-mediasession.js' '_lastGoodArtworkPath'; then
  echo "15e desplegado desde $PATCH_SRC"
else
  sed -i "s/var _lastGoodArtwork = \[\];  \/\/ último artwork válido/var _lastGoodArtwork = [];\nvar _lastGoodArtworkPath = '';/" "$MS"
  python3 <<'PY' "$MS"
import sys
p = sys.argv[1]
text = open(p).read()
old = """    // 404 (Allez) o sin art: _carArtwork sigue teniendo URL rota. No la publiques;
    // reusa el último artwork bueno. Nunca metadata vacío tras uno con art.
    if (artFailed || !(_art && _art.length)) {
      if (_lastGoodArtwork && _lastGoodArtwork.length) {
        _art = _lastGoodArtwork;
        artUrl = (_art[0] && _art[0].src) || '';
        try { host().sessionLog('info', {event: 'mediasession-art-reused', motivo: artFailed ? 'cover-404' : 'no-pisar-vacio', path: song.path || '', via: via}); } catch (_eRe) {}
      } else if (artFailed) {
        _art = [];
        artUrl = '';
      }
    }"""
new = """    if (artFailed || !(_art && _art.length)) {
      var _samePathArt = _lastGoodArtwork && _lastGoodArtwork.length &&
        _lastGoodArtworkPath && _lastGoodArtworkPath === (song.path || '');
      if (_samePathArt) {
        _art = _lastGoodArtwork;
        artUrl = (_art[0] && _art[0].src) || '';
      } else {
        _art = [];
        artUrl = '';
      }
    }"""
if old not in text:
    print('WARN: 15e artwork block pattern not found — apply patch manually', file=sys.stderr)
    sys.exit(1)
text = text.replace(old, new, 1)
text = text.replace(
    'if (_art && _art.length && artUrl) _lastGoodArtwork = _art;',
    'if (_art && _art.length && artUrl) { _lastGoodArtwork = _art; _lastGoodArtworkPath = song.path || ""; }'
)
text = text.replace(
    '// Nunca retry SIN artwork si ya hubo uno bueno.\n      if (_lastGoodArtwork && _lastGoodArtwork.length) {',
    'if (_lastGoodArtwork && _lastGoodArtwork.length && _lastGoodArtworkPath === (song.path || "")) {'
)
text = text.replace(
    '_pubInFlightPath = path;\n  var _mEarly',
    '_pubInFlightPath = path;\n  if (path && path !== _lastGoodArtworkPath) { _lastGoodArtwork = []; _lastGoodArtworkPath = ""; }\n  var _mEarly'
)
text = text.replace(
    "_pubInFlightPath = '';\n  if (_pendingPubTimer)",
    "_pubInFlightPath = '';\n  _lastGoodArtwork = [];\n  _lastGoodArtworkPath = '';\n  if (_pendingPubTimer)"
)
open(p, 'w').write(text)
print('Patched', p)
PY
fi

# --- 15p: auto-advance on ended ---
if grep -q 'native-ended-switch-stuck-reset' "$PU"; then
  echo "15p ya tiene stuck-reset"
elif deploy_file "$PU" '15p-ximo-player-ui.js' 'native-ended-switch-stuck-reset'; then
  echo "15p desplegado desde $PATCH_SRC"
else
  python3 <<'PY' "$PU"
import sys
p = sys.argv[1]
text = open(p).read()
old = """        if (H._fastSwitchIdx >= 0) {
          // Ping-pong ya en vuelo: dejarlo terminar (su watchdog lo desatasca).
          H.sessionLog('warn', {action: 'native-ended-switch-inflight', idx: H._fastSwitchIdx});
          return;
        }"""
new = """        if (H._fastSwitchIdx >= 0) {
          var _preLive = H.preloadEl && !H.preloadEl.paused && H.preloadEl.currentTime > 0.05;
          if (_preLive) {
            H.sessionLog('warn', {action: 'native-ended-switch-inflight', idx: H._fastSwitchIdx});
            return;
          }
          H.sessionLog('warn', {action: 'native-ended-switch-stuck-reset', idx: H._fastSwitchIdx});
          H._fastSwitchIdx = -1;
          try { H._restoreMediaSessionActual(); } catch(_eRst) {}
        }"""
if old not in text:
    print('WARN: 15p ended block pattern not found', file=sys.stderr)
    sys.exit(1)
open(p, 'w').write(text.replace(old, new, 1))
print('Patched', p)
PY
fi

echo "=== Bump ce-build -> $NEW_BUILD ==="
while IFS= read -r idx; do
  [[ -z "$idx" ]] && continue
  if grep -q 'ce-build' "$idx"; then
    cp -a "$idx" "${idx}.bak-$(date +%Y%m%d%H%M%S)"
    sed -i "s/<meta name=\"ce-build\" content=\"[^\"]*\"/<meta name=\"ce-build\" content=\"$NEW_BUILD\"/" "$idx"
    echo "  $idx"
  fi
done < <(find_index_html)

echo "=== Restart ximo containers ==="
mapfile -t CONTAINERS < <(docker ps --format '{{.Names}}' | rg -i 'ximo|music|lugares' || true)
printf '%s\n' "${CONTAINERS[@]:-"(ninguno)"}"
for c in "${CONTAINERS[@]}"; do
  docker restart "$c"
done

echo "=== Verify production ==="
curl -fsS 'https://music.yespi.es/composables/15e-ximo-mediasession.js' | rg '_lastGoodArtworkPath' | head -1 || echo "WARN: 15e sin _lastGoodArtworkPath en prod"
curl -fsS 'https://music.yespi.es/composables/15p-ximo-player-ui.js' | rg 'native-ended-switch-stuck-reset' | head -1 || echo "WARN: 15p sin stuck-reset en prod"
curl -fsS 'https://music.yespi.es/index.html' | rg 'ce-build' | head -1 || true

echo "Done. Modified: $MS $PU"
