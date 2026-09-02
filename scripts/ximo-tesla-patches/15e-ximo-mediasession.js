/* — XimoMediaSession: Media Session / Tesla miniplayer (Wave 3). API window.XimoMediaSession. */
window.XimoMediaSession = (function(){
  "use strict";

  var C = null; // host bag from 15-ia.js
  function bindHost(h) { if (h) C = h; }
  function host() {
    if (!C) throw new Error("XimoMediaSession: bindHost pending");
    return C;
  }

  // --- state owned by the module ---
// Registrar los handlers es condición NECESARIA para que el coche muestre el
// botón correspondiente: los controles no se pintan si no hay handler puesto.
// Pero persisten entre reproducciones, así que basta una vez. Se permite
// forzar el refresco al volver a primer plano por si el Tesla los perdiera.
var _msHandlersReady = false;
function setupMediaSessionHandlers(force) {
  if (!('mediaSession' in navigator)) return;
  if (_msHandlersReady && !force) return;
  _msHandlersReady = true;
  function set(action, fn) {
    try { navigator.mediaSession.setActionHandler(action, fn); }
    catch(e) {}
  }
  // ── FASE 1 Fable 5: logging exhaustivo de cada acción ──
  var _msLog = function(action, details) {
    var d = { src: 'mediasession', hidden: document.hidden, internalOp: host().internalOp,
              currentTime: host().audioEl.currentTime || 0, duration: host().audioEl.duration || 0,
              deckA: host().audioEl.paused, deckAvol: host().audioEl.volume,
              deckB: host().preloadEl.paused, deckBvol: host().preloadEl.volume };
    if (details && typeof details === 'object') d.details = details;
    host().sessionLog('info', {event: 'ms-action:'+action, data: d});
  };
  // Controles físicos / miniplayer → SIEMPRE el transporte global (XimoTransport),
  // no un <audio> concreto. Tras ping-pong A↔B el deck activo cambia; el
  // MediaSession de la pestaña debe mapear roller/seek al motor unificado.
  function _msPlay() {
    if (window.XimoTransport && typeof window.XimoTransport.play === 'function') {
      window.XimoTransport.play();
    } else {
      host().playCurrent(false);
    }
  }
  function _msPause() {
    if (window.XimoTransport && typeof window.XimoTransport.pause === 'function') {
      window.XimoTransport.pause();
    } else {
      host().pauseCurrent(false);
    }
  }
  function _msStop() {
    if (window.XimoTransport && typeof window.XimoTransport.stop === 'function') {
      window.XimoTransport.stop();
    } else {
      host().stopCurrent(false);
    }
  }
  function _msNext() {
    if (window.XimoTransport && typeof window.XimoTransport.next === 'function') {
      window.XimoTransport.next();
    } else {
      host().playNext();
    }
  }
  function _msPrev() {
    if (window.XimoTransport && typeof window.XimoTransport.previous === 'function') {
      window.XimoTransport.previous();
    } else {
      host().playPrev();
    }
  }
  function _msSeekTo(t) {
    if (window.XimoTransport && typeof window.XimoTransport.seekTo === 'function') {
      window.XimoTransport.seekTo(t);
    } else if (typeof host().seekTo === 'function') {
      host().seekTo(t);
    }
  }
  function _msSeekBy(s) {
    if (window.XimoTransport && typeof window.XimoTransport.seekBy === 'function') {
      window.XimoTransport.seekBy(s);
    } else if (typeof host().seekBy === 'function') {
      host().seekBy(s);
    }
  }
  set('play',      function(d)   { _msLog('play', d); _msPlay(); });
  // pause/stop: filtrar las pausas que provocamos nosotros al pausar el deck
  // saliente en el swap. El listener del elemento ya distinguía
  // internal/external; este camino no, y era por donde se colaba.
  set('pause',     function(d)   {
    _msLog('pause', d);
    if (host().isSelfInflictedPause()) {
      host().sessionLog('info', {event: 'ms-action:pause-ignorada', motivo: 'transicion propia',
                          internalOp: host().internalOp, fastSwitchIdx: host().fastSwitchIdx,
                          deckActivoPausado: host().audioEl.paused});
      return;
    }
    // Spurious MS pause while our play() is in-flight would AbortError the start.
    if (typeof host().isPlayPending === 'function' && host().isPlayPending()) {
      host().sessionLog('info', {event: 'ms-action:pause-ignorada', motivo: 'play-pending'});
      return;
    }
    // KARAOKE: host().audioEl está SIEMPRE pausado (suena _audioInst por Web Audio).
    // Tesla un botón Stop/Play: pausa si suena (suelta sink). Play deliberado
    // del mismo botón (tras eco 2.5s) SÍ reanuda. Eco inmediato NO.
    if (document.body.classList.contains('ximo-karaoke')) {
      var _kPlaying = !!(host().isPlaying || host().audioWantPlay);
      var _kCar = false;
      try { _kCar = !!(window.XimoCarBridge && window.XimoCarBridge.isTeslaHoldSink && window.XimoCarBridge.isTeslaHoldSink()); } catch (_eKCar) {}
      if (_kPlaying) {
        host().sessionLog('info', {event: 'ms-toggle:karaoke-pause'});
        host().pauseCurrent(true);
      } else if (_kCar && (Date.now() - host().ultimaPausaExterna >= 2500)) {
        host().sessionLog('info', {event: 'ms-toggle:karaoke-play', motivo: 'tesla-un-boton'});
        _msPlay();
      } else {
        host().sessionLog('info', {event: 'ms-toggle:karaoke-ignorada', motivo: 'ya-pausado no reanudar echo'});
      }
      return;
    }
    // Igual que en el listener del elemento: si venimos de irnos al GPS, esto
    // es el coche reclamando el foco, no un toque del usuario.
    if (host().pausaPorSegundoPlano()) { host().reanudaTrasFoco('mediasession'); return; }
    if (host().multiTapEnabled) { host().onExternalPause(); return; }
    // Tesla un botón Stop/Play: el coche casi nunca manda `play`, solo `pause`.
    // Pause REAL (15q) suelta keep-alive. El segundo pause <2.5s es eco (NO
    // reanudar — bug «el coche solo manda pause»). Tras esa ventana, el mismo
    // botón es PLAY deliberado (ms-toggle). Escritorio ?tesla=0: committed, no
    // toggle (hay acción play nativa).
    var _carHold = false;
    try { _carHold = !!(window.XimoCarBridge && window.XimoCarBridge.isTeslaHoldSink && window.XimoCarBridge.isTeslaHoldSink()); } catch (_eCar) {}
    if (host().audioEl.paused || !host().isPlaying) {
      if (Date.now() - host().ultimaPausaExterna < 2500) {
        host().sessionLog('info', {event: 'ms-toggle:ignorada', motivo: 'pausa reciente (no reanudar echo Tesla)'});
        return;
      }
      if (_carHold) {
        host().sessionLog('info', {event: 'ms-toggle:play', motivo: 'tesla-un-boton pause=play'});
        _msPlay();
        return;
      }
      if (!host().isPlaying && !host().audioWantPlay) {
        host().sessionLog('info', {event: 'ms-toggle:ignorada', motivo: 'ya-pausado committed, no ms-toggle:play'});
        return;
      }
      host().sessionLog('info', {event: 'ms-toggle:play', motivo: 'el coche solo manda pause'});
      _msPlay();
    } else {
      host().sessionLog('info', {event: 'ms-toggle:pause'});
      _msPause();
    }
  });
  set('stop',      function(d)   {
    _msLog('stop', d);
    if (host().isSelfInflictedPause()) {
      host().sessionLog('info', {event: 'ms-action:stop-ignorada', motivo: 'transicion propia'});
      return;
    }
    if (host().multiTapEnabled) { host().onExternalPause(); return; }
    _msStop();
  });
  // Mismo transporte que los botones UI. Si el firmware Tesla no dispara
  // nexttrack/previoustrack, esto no basta (TESLA_MUSIC.md §1.2 / #94).
  set('previoustrack', function(d){ _msLog('previoustrack', d); _msPrev(); });
  set('nexttrack',     function(d){ _msLog('nexttrack', d); _msNext(); });
  // `seekto` alimenta la barra de progreso del miniplayer: siempre puesto.
  set('seekto',        function(d){ _msLog('seekto', d);
    if (d && typeof d.seekTime === 'number') _msSeekTo(d.seekTime);
  });
  // seekbackward/seekforward (±10 s) compiten POR HUECO con nexttrack/
  // previoustrack: la UI de medios de Chromium tiene un número limitado de
  // botones y elige un subconjunto de las acciones registradas, así que
  // declarar los de salto puede desplazar a los de canción — candidato a que
  // "los botones de avanzar/retroceder canción no funcionen" (en realidad
  // serían ±10 s). DESACTIVADOS por defecto desde 2026-08-06: issue #94
  // (TESLA_MUSIC.md §6.2) ya documentó con telemetría real que del volante
  // solo llega `pause` — nunca `play`/`nexttrack`/`previoustrack` —, así que
  // esos botones físicos no son recuperables desde aquí; lo único que queda
  // por probar es si el widget TÁCTIL del miniplayer sí respeta el hueco
  // liberado. Conmutable EN VIVO desde la consola del Tesla, sin desplegar:
  //   __ximoSeekButtons(true)   → vuelve a añadir ±10 s (quita hueco a canción)
  //   __ximoSeekButtons(false)  → solo siguiente/anterior canción (por defecto)
  if (_seekButtonsEnabled) {
    set('seekbackward',  function(d){ _msLog('seekbackward', d);
      _msSeekBy(-((d && d.seekOffset) || 10));
    });
    set('seekforward',   function(d){ _msLog('seekforward', d);
      _msSeekBy((d && d.seekOffset) || 10);
    });
  } else {
    set('seekbackward', null);
    set('seekforward', null);
  }
}
var _seekButtonsEnabled = false;
window.__ximoSeekButtons = function(v) {
  if (typeof v === 'boolean' && v !== _seekButtonsEnabled) {
    _seekButtonsEnabled = v;
    try { setupMediaSessionHandlers(true); } catch(_e) {}
  }
  return {seekButtons: _seekButtonsEnabled,
          nota: 'false = libera hueco para siguiente/anterior cancion en el miniplayer'};
};

// #90 — sincronizar la posición/duración con el reproductor del coche para
// que su barra de progreso se mueva (setPositionState). Requiere duración
// válida; si no, no se llama (lanzaría excepción).
var _lastPosSync = 0;
// ÚNICO punto que llama a setPositionState. Sus precondiciones son estrictas
// —duración presente y > 0, posición dentro de [0, duración], velocidad > 0—
// y violarlas lanza excepción. Justo durante un swap es cuando `duration`
// puede ser NaN (metadatos aún sin cargar) o `currentTime` puede pasarse de
// la duración al final de la pista. Antes había tres puntos de llamada con
// guardas distintas: el de `_syncMediaSession` ni siquiera acotaba la
// posición, que es el caso que se da al terminar la canción.
// Segmento MSE actual: {song, pos, dur} según host().audioEl.currentTime, o null si
// no hay motor MSE. En MSE, host().audioEl.currentTime/duration son de la línea
// temporal CONCATENADA (varias canciones), no de la pista actual.
function _mseCurSeg() {
  if (!host().mse || !host().mse.segs || !host().mse.segs.length) return null;
  var t = host().audioEl.currentTime;
  for (var i = host().mse.segs.length - 1; i >= 0; i--) {
    var s = host().mse.segs[i];
    if (t >= s.start - 0.15) {
      // Duración ESTABLE: la real del fichero (song.duration) si la hay; si no,
      // end-start del buffer, que CRECE mientras se alimenta la pista por trozos
      // → el total cambiaría durante la reproducción (bug "Keep the Faith").
      var dur = (s.song && s.song.duration) ? s.song.duration
                : ((s.end && s.end > s.start) ? (s.end - s.start) : 0);
      return { song: s.song, pos: Math.max(0, t - s.start), dur: dur, start: s.start, index: s.index };
    }
  }
  return null;
}
// Canción que SUENA ahora mismo. En MSE la manda el segmento actual, no
// host().currentSongIndex (que va por detrás → el refresco periódico repintaba el
// título/carátula de la canción anterior).
function _nowPlayingSong() {
  var seg = _mseCurSeg();
  if (seg && seg.song) return seg.song;
  return host().currentPlaylistSongs[host().currentSongIndex];
}
function _updateMediaPositionState(deck) {
  if (!('mediaSession' in navigator) || !('setPositionState' in navigator.mediaSession)) return;
  // Por defecto SOLO el deck activo (audioEl tras swap A↔B). Pasar `deck`
  // explícito solo en handoff (preloadEl entrante) desde _syncMediaSession.
  var el = deck || host().audioEl;
  if (!el) return;
  var r = el.playbackRate;
  // En MSE, usar la posición/duración del SEGMENTO actual; si no, la barra del
  // coche sale a media canción al empezar la siguiente (posición absoluta en la
  // línea concatenada). Solo aplica al elemento principal (el deck de precarga
  // no lleva MSE).
  var d, pos;
  var seg = (el === host().audioEl) ? _mseCurSeg() : null;
  if (seg && seg.dur > 0) { d = seg.dur; pos = seg.pos; }
  else { d = el.duration; pos = el.currentTime; }
  // Guard NaN/Infinity (Gemini + web.dev): nunca llamar setPositionState inválido.
  if (!isFinite(d) || d <= 0) return;
  if (!isFinite(pos) || pos < 0) pos = 0;
  if (pos > d) pos = d;
  if (!isFinite(r) || r <= 0) r = 1;
  try {
    navigator.mediaSession.setPositionState({duration: d, playbackRate: r, position: pos});
  } catch(e) {
    host().sessionLog('warn', {event: 'ms-position-fail', msg: (e && e.name) || String(e),
                        d: d, p: pos, r: r});
  }
}

// Al parar del todo: resetear el estado de posición para que el coche no se
// quede con una barra de progreso congelada de la canción anterior.
function _clearMediaPositionState() {
  if (!('mediaSession' in navigator) || !('setPositionState' in navigator.mediaSession)) return;
  try { navigator.mediaSession.setPositionState(null); } catch(e) {}
}

// Carátula en varios tamaños. Extraído para que TODAS las vías que fijan
// metadatos (selectSong, swap del ping-pong, refresco periódico) usen la
// misma lógica; antes el ping-pong usaba una versión pobre, de un solo
// tamaño y sin escapar la URL, así que tras cada transición automática el
// coche perdía calidad de carátula.
// URL de carátula normalizada y ABSOLUTA (el navegador embotado del coche a
// veces no resuelve bien las relativas en la Media Session). Misma cadena que
// usa el prewarm → mismo cache-key.
function _coverSrc(song) {
  if (!song) return '';
  var u = song.cover_url ? String(song.cover_url) : '';
  if (!u && song.path) {
    var rel = String(song.path).replace(/^\/api\/ia\/music-file\//, '');
    var enc = rel.split('/').map(function(seg) {
      if (!seg) return '';
      if (seg.indexOf('%') >= 0) return seg.replace(/ /g, '%20');
      return encodeURIComponent(seg);
    }).join('/');
    if (enc) u = '/api/ia/cover/' + enc;
  }
  if (!u && song.artist) {
    u = '/api/ia/artist-cover/' + encodeURIComponent(String(song.artist));
  }
  if (!u) return '';
  // API ya trae %xx — no tocar ( y ) literales inexistentes ni doble-encodear.
  if (u.indexOf('%') < 0) {
    u = u.replace(/ /g, '%20').replace(/\(/g, '%28').replace(/\)/g, '%29');
  } else {
    u = u.replace(/ /g, '%20');
  }
  // Absolute HTTPS: Tesla/Chromium Media Session often fails on relative or http.
  if (u.charAt(0) === '/') { try { u = location.origin + u; } catch(_e) {} }
  else if (u && !/^https?:\/\//i.test(u) && u.indexOf('blob:') !== 0 && u.indexOf('data:') !== 0) {
    try { u = new URL(u, location.href).href; } catch(_eRel) {}
  }
  if (/^http:\/\//i.test(u) && typeof location !== 'undefined' && location.protocol === 'https:') {
    u = 'https://' + u.slice(7);
  }
  return u;
}
// Precargar la carátula (HTTP cache) en cuanto se prepara la SIGUIENTE pista,
// ~45 s antes de la frontera: así cuando el miniplayer del Tesla la pide, ya
// está en caché y no se pierde en la carrera con la descarga del audio (era la
// causa de "al cambiar de pista pone la portada anterior").
function _prewarmCover(song) {
  // Misma URL que irá a MediaSession (con ?ms=) para compartir caché HTTP.
  try {
    var art = _carArtwork(song);
    var u = (art[0] && art[0].src) || _coverSrc(song);
    if (u) { var im = new Image(); im.src = u; }
  } catch(_e) {}
}
function _prewarmNextCover() {
  try {
    var songs = host().currentPlaylistSongs || [];
    var idx = host().currentSongIndex | 0;
    var next = songs[idx + 1];
    if (next) _prewarmCover(next);
  } catch (_eN) {}
}
function _carArtwork(song) {
  var coverUrl = _coverSrc(song);
  if (!coverUrl) return [];
  // Cache-bust ESTABLE por canción: el Chromium del Tesla a menudo conserva
  // el bitmap decodificado de la pista ANTERIOR si la URL "parece" la misma
  // familia (mismo host/path prefix). Un token por path fuerza recarga del
  // artwork en Media Session sin provocar parpadeo en el refresco periódico
  // (el token no cambia mientras suene la misma pista).
  var token = '';
  try {
    token = encodeURIComponent(String(song.path || song.cover_url || '').replace(/^.*\//, '').slice(0, 64));
  } catch(_eTok) { token = String(Date.now()); }
  if (token) {
    coverUrl += (coverUrl.indexOf('?') >= 0 ? '&' : '?') + 'ms=' + token;
  }
  // #94 — el `type` debe corresponder al fichero real: anunciar
  // 'image/jpeg' para un .png/.webp hace que algunos navegadores
  // empotrados descarten la carátula y el minireproductor del coche se
  // quede sin portada. Se deriva de la extensión; si no se reconoce, se
  // omite (el campo es opcional y el navegador la sniffa).
  var ext = (coverUrl.split('?')[0].match(/\.([a-z0-9]+)$/i) || [])[1];
  var mime = {jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
              webp: 'image/webp', gif: 'image/gif'}[(ext || '').toLowerCase()];
  // 512x512 primero (recomendación Media Session / Tesla); misma URL HTTPS
  // absoluta — no redimensionamos en servidor; el type sigue al fichero real.
  return ['512x512', '256x256', '96x96'].map(function(sz) {
    var a = { src: coverUrl, sizes: sz };
    if (mime) a.type = mime;
    return a;
  });
}

// Nombre de álbum con degradación: álbum real → playlist → 'Ximo'.
function _carAlbum(song) {
  var alb = _cleanName((song && song.album) || '');
  if (alb) return alb;
  return _cleanName(host().currentPlaylistName ||
         (host().playlistsData && host().playlistsData.length > 0 ? host().playlistsData[0].name : '')) || 'Ximo';
}

// ── LÍNEA SECUNDARIA DEL REPRODUCTOR DEL COCHE ──
// El Tesla usa la UI de Media Session de Chromium, que pinta `title`,
// `artist` y, como tercera línea, el ORIGEN de la página ("music.yespi.es").
// Ese origen lo pone el navegador como indicador de seguridad: NO es
// configurable desde la web, no hay API para sustituirlo. El campo `album`
// de MediaMetadata a menudo ni se muestra. Por eso todo lo que se quiera ver
// con garantías hay que empaquetarlo en `title` / `artist`:
//
//   title  → «Canción»
//   artist → «Artista · Álbum — Playlist · 1:23 / 4:05»
//
// La posición se manda además por setPositionState(), que es la vía estándar
// para la barra de progreso: si el coche la pinta, se mueve sola y el texto
// es sólo un refuerzo.
// Los nombres de playlist llevan decoración de la interfaz: las 31 empiezan
// por emoji (📁, 🆕, 📻, 🔥, ⭐, 🎸…) y algunas usan guiones bajos. Eso vale en
// la web, pero metido en la Media Session ensucia la única línea de texto que
// el coche nos deja usar. Aquí se limpia para el reproductor, sin tocar el
// nombre real de la playlist.
function _cleanName(s) {
  if (!s) return '';
  return String(s)
    .replace(/^[^\p{L}\p{N}]+/u, '')   // emoji/símbolos iniciales
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
// Comparación laxa para decidir si álbum y playlist son "lo mismo": sin
// acentos, sin mayúsculas y sin decoración. Sin esto, «Rock FM 500» y
// «📻 Rock FM 500» se consideraban distintos y la línea los repetía.
function _sameName(a, b) {
  var norm = function(x) {
    return _cleanName(x).toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '');
  };
  return !!a && !!b && norm(a) === norm(b);
}

// ── TÍTULO PARA EL COCHE ──
// Comprobado en el Tesla real (23-jul, prueba guiada): el Miniplayer pinta
// SOLO el `title` de MediaMetadata. Ni `artist` ni `album` aparecen, así que
// toda la información útil tiene que caber ahí. De ahí «Canción — Álbum».
// Si algún día se ve también el artista, basta con __ximoTituloAlbum(false).
var _tituloConAlbum = true;
window.__ximoTituloAlbum = function(v) {
  if (typeof v === 'boolean') {
    _tituloConAlbum = v; _carInfoLast = '';
    // Aplicar ya: _refreshCarInfo (el único consumidor de _carInfoLast) solo
    // corre en el tick de 1s de _startPosUpdates, que se corta en pausa y en
    // karaoke — la píldora de pruebas parecía no hacer nada hasta el
    // siguiente cambio real de canción.
    try {
      var _songTA = host().currentPlaylistSongs[host().currentSongIndex];
      if (_songTA) _publishMediaSession(_songTA, null, 'test-toggle', true);
    } catch (_eTA) {}
  }
  return _tituloConAlbum;
};
// Experimento (2026-08-06, picker de pruebas): álbum en la 2ª línea (artist)
// además de/en vez de en el título. false = artist queda solo «Cantante —
// Duración», dejando el álbum únicamente en el campo `album` de MediaMetadata
// (que el Tesla suele ignorar, según lo ya documentado) y en application-name.
var _albumEnArtist = true;
window.__ximoAlbumEnArtist = function(v) {
  if (typeof v === 'boolean') {
    _albumEnArtist = v; _carInfoLast = '';
    try {
      var _songAA = host().currentPlaylistSongs[host().currentSongIndex];
      if (_songAA) _publishMediaSession(_songAA, null, 'test-toggle', true);
    } catch (_eAA) {}
  }
  return _albumEnArtist;
};
var _DEFAULT_DOC_TITLE = 'Ximo — música';
var _DEFAULT_APP_NAME = 'Ximo Player';
function _setAppName(v) {
  try {
    var m = document.querySelector('meta[name="application-name"]'); if (m) m.content = v;
    var a = document.querySelector('meta[name="apple-mobile-web-app-title"]'); if (a) a.content = v;
  } catch (e) {}
}
// Experimento badge/origen (2026-08-03): Chromium desktop fija source_title al
// origen URL (no a document.title). En Tesla embebido no está confirmado.
// Actualizamos title + application-name en cada pista por si el firmware
// usa alguno de esos campos en la 3ª línea — hay que verificar en el coche.
function _setPageChrome(song, meta) {
  try {
    if (!song) {
      document.title = _DEFAULT_DOC_TITLE;
      _setAppName(_DEFAULT_APP_NAME);
      return;
    }
    var m = meta || _carMeta(song, host().audioEl);
    // Preferir «Canción — Álbum»; si no hay álbum útil, «Canción — Artista».
    var t = (m && m.title) || (song.title || 'Ximo');
    document.title = t;
    var app = (m && m.album && m.album !== 'Ximo') ? m.album : _DEFAULT_APP_NAME;
    _setAppName(app);
  } catch (e) {}
}
function _clearPageChrome() {
  _setPageChrome(null);
}

// MediaMetadata para el Miniplayer.
// Tesla real (2026-07): pinta sobre todo `title`; `artist` a veces; `album` a menudo no.
// El hostname `music.yespi.es` lo pone Chromium como source_title (origen). Empaquetamos
// el álbum en title (+ artist) y en album / application-name / document.title.
// Wave 0: retirados selector Cx / _albumCase / __ximoAlbumCase (UI y switch ya muertos).
function _carMeta(song, deck) {
  var cancion = (song && song.title) || 'Ximo';
  var artista = (song && song.artist) || '';
  // Álbum REAL de la pista (no playlist) para la ranura album / app-name.
  var albumReal = _cleanName((song && song.album) || '');
  var album = albumReal || _carAlbum(song);
  var puro = album && album !== 'Ximo' && !_sameName(album, cancion) && !_sameName(album, artista);
  var dur = (song && song.duration) ? host().formatTime(song.duration) : '';
  var bits = [];
  if (artista) bits.push(artista);
  if (puro && _albumEnArtist) bits.push(album);
  if (dur) bits.push(dur);
  // title: «Artista - Canción» (única línea garantizada en Tesla; petición
  // usuario 2026-08-12 — antes era «Canción — Álbum/Artista» y solo quedaba
  // mal ahí; el resto de reproductores pintan artist/title por separado y no
  // usan este campo compuesto).
  var title = artista ? (artista + ' - ' + cancion) : cancion;
  return { title: title, artist: bits.join(' — '), album: album, puro: !!puro };
}

function _carTitle(song) {
  var t = (song && song.title) || 'Ximo';
  if (!_tituloConAlbum) return t;
  var alb = _carAlbum(song);
  // Sin repetir: muchos títulos ya llevan dentro el nombre del álbum.
  if (alb && alb !== 'Ximo' && !_sameName(alb, t)) t += ' — ' + alb;
  return t;
}

function _carArtistLine(song, deck) {
  var bits = [];
  if (song && song.artist) bits.push(song.artist);
  var alb = _cleanName((song && song.album) || '');
  var pl = _cleanName(host().currentPlaylistName || '');
  if (alb && pl && !_sameName(alb, pl)) bits.push(alb + ' — ' + pl);
  else if (alb || pl) bits.push(alb || pl);
  var d = deck && deck.duration;
  if (d && isFinite(d) && d > 0) {
    bits.push(host().formatTime(deck.currentTime || 0) + ' / ' + host().formatTime(d));
  }
  return bits.join(' · ');
}

// Deduplicado + cola. Camino probado (cea63f1263 / Pause→Play 2026-08-02):
// UN solo null-then-set DESPUÉS de que la carátula esté en caché HTTP.
// El cancel-storm (ed03d8f9) publicaba texto+art a los 90 ms y luego otro
// null al cover-ready / mse-deferred → cancelaba el fetch image (spec W3C).
// Aquí: coalescemos callers; chrome (title) inmediato; artwork = un nudge.
var _mediaSetKey = '';
var _mediaSetTs = 0;
var _msArtGen = 0;   // invalida publicaciones diferidas de carátula
var _lastPublishedArtUrl = '';
var _lastGoodArtwork = [];  // último artwork válido; no pisar con vacío (Allez 404)
var _lastGoodArtworkPath = '';  // pista a la que pertenece _lastGoodArtwork (evita AC/DC+Bad Bunny)
var _lastHandlerSong = '';   // última pista para la que se re-registraron handlers
var _livePubPath = '';       // pista cuya metadata está publicada y viva ahora mismo
var _pubInFlightPath = '';   // pista con un pipeline de portada YA en marcha (prefetch sin resolver)
var _pendingPub = null;   // {song, deck, via, force, artReady, artFailed, forceArtClear}
var _pendingPubTimer = 0;
var _coverPipelineGen = 0;
function _mediaSongKey(song, _m) {
  return ((_m && _m.title) || '') + '|' + ((_m && _m.artist) || '') +
         '|' + ((song && song.cover_url) || '') + '|' + ((song && song.path) || '');
}
function _mediaDedup(key) {
  var now = Date.now();
  if (key === _mediaSetKey && (now - _mediaSetTs) < 700) return true;
  _mediaSetKey = key; _mediaSetTs = now; return false;
}
function _artworkUrlOf(song) {
  var art = _carArtwork(song);
  return (art[0] && art[0].src) || '';
}
// Durante handoff ping-pong (fastSwitchIdx>=0) NUNCA dejar playbackState=paused:
// Gemini / experiencia propia — paused + buffer vacío → Tesla destruye miniplayer.
// No toca la lógica A↔B; solo el flag de MediaSession.
function _msPlaybackState() {
  try {
    if (host().fastSwitchIdx >= 0) return 'playing';
    return host().isPlaying ? 'playing' : 'paused';
  } catch (_e) {
    return host().isPlaying ? 'playing' : 'paused';
  }
}
// Aplica MediaMetadata. clearArt=true → null previo (Tesla necesita el nudge
// para sustituir el bitmap; más de un null por pista cancela el fetch).
function _applyMediaMetadata(song, deck, via, clearArt, artFailed) {
  if (!('mediaSession' in navigator) || !song) return;
  try {
    var _m = _carMeta(song, deck || host().audioEl);
    _setPageChrome(song, _m);
    var _art = _carArtwork(song);
    var artUrl = (_art[0] && _art[0].src) || '';
    // NUNCA metadata=null: W3C cancela el fetch de artwork y Tesla interpreta
    // sesión nueva/anterior (portada de la pista previa o vacío). Un set con
    // artwork de ESTA pista basta. clearArt se ignora a propósito.
    void clearArt;
    // 404 (Allez) o sin art: no reutilizar portada de OTRA pista (síntoma Tesla:
    // título Bad Bunny + carátula AC/DC al saltar manualmente). Solo reutilizar
    // si es la misma path; si falla en pista nueva, publicar sin artwork.
    if (artFailed || !(_art && _art.length)) {
      var _samePathArt = _lastGoodArtwork && _lastGoodArtwork.length &&
        _lastGoodArtworkPath && _lastGoodArtworkPath === (song.path || '');
      if (_samePathArt) {
        _art = _lastGoodArtwork;
        artUrl = (_art[0] && _art[0].src) || '';
        try { host().sessionLog('info', {event: 'mediasession-art-reused', motivo: artFailed ? 'cover-404-same-path' : 'no-pisar-vacio', path: song.path || '', via: via}); } catch (_eRe) {}
      } else {
        _art = [];
        artUrl = '';
        if (artFailed) {
          try { host().sessionLog('info', {event: 'mediasession-art-omit', motivo: 'cover-404-new-path', path: song.path || '', via: via}); } catch (_eOm) {}
        }
      }
    }
    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: _m.title, artist: _m.artist, album: _m.album, artwork: _art
      });
      if (_art && _art.length && artUrl) {
        _lastGoodArtwork = _art;
        _lastGoodArtworkPath = song.path || '';
      }
    } catch (eArt) {
      host().sessionLog('warn', {event: 'mediasession-error', msg: (eArt && eArt.message) || String(eArt), fase: 'con-artwork'});
      // Nunca retry con artwork de OTRA pista si ya hubo uno bueno para ESTA.
      if (_lastGoodArtwork && _lastGoodArtwork.length && _lastGoodArtworkPath === (song.path || '')) {
        try {
          navigator.mediaSession.metadata = new MediaMetadata({
            title: _m.title, artist: _m.artist, album: _m.album, artwork: _lastGoodArtwork
          });
          artUrl = (_lastGoodArtwork[0] && _lastGoodArtwork[0].src) || artUrl;
        } catch (_eReuse) {
          host().sessionLog('warn', {event: 'mediasession-error', fase: 'reuse-art-fail', msg: (_eReuse && _eReuse.message) || String(_eReuse)});
        }
      } else {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: _m.title, artist: _m.artist, album: _m.album
        });
        artUrl = '';
      }
    }
    _lastPublishedArtUrl = artUrl;
    _livePubPath = song.path || '';
    _carInfoLast = _mediaSongKey(song, _m);
    _mediaSetKey = _carInfoLast;
    _mediaSetTs = Date.now();
    var _pbState = _msPlaybackState();
    navigator.mediaSession.playbackState = _pbState;
    // Re-registrar los action handlers al CAMBIAR de canción. Sin esto solo se
    // registraban en `_playCurrent` (play del usuario), así que sobrevivían a la
    // 1ª canción pero no a los avances automáticos de la frontera MSE — que es
    // exactamente cuando el usuario reporta que dejan de funcionar los botones
    // de siguiente/anterior del coche. Registrar handlers NO toca `metadata`,
    // así que no cancela el fetch de artwork (a diferencia de republicar).
    var _handlersReregistered = false;
    if (_lastHandlerSong !== (song.path || '')) {
      _lastHandlerSong = song.path || '';
      _handlersReregistered = true;
      try { setupMediaSessionHandlers(true); } catch(_eH) {}
    }
    host().sessionLog('info', {event: 'mediasession-set', via: via || 'select',
                        title: _m.title, artist: _m.artist,
                        album: _m.album, docTitle: document.title,
                        artN: _art.length, artUrl: artUrl,
                        clearArt: !!clearArt, playbackState: _pbState,
                        handlersReregistered: _handlersReregistered,
                        soportado: (typeof MediaMetadata !== 'undefined')});
  } catch(e) {
    host().sessionLog('warn', {event: 'mediasession-error', msg: (e && e.message) || String(e)});
  }
}
function _flushPendingPublish() {
  _pendingPubTimer = 0;
  var job = _pendingPub;
  _pendingPub = null;
  if (!job || !job.song) return;
  var song = job.song;
  var deck = job.deck || host().audioEl;
  var _m = _carMeta(song, deck);
  var key = _mediaSongKey(song, _m);
  if (!job.force && _mediaDedup(key) && !job.artReady && !job.forceArtClear) {
    try { navigator.mediaSession.playbackState = _msPlaybackState(); } catch(_ePs) {}
    _setPageChrome(song, _m);
    return;
  }
  var artUrl = _artworkUrlOf(song);
  var clearArt = false;
  void artUrl;
  _applyMediaMetadata(song, deck, job.via, clearArt, !!job.artFailed);
}
// Encola publicación (refresco de texto / nudge explícito). Coalescida ~90 ms.
function _publishMediaSession(song, deck, via, force, forceArtClear) {
  if (!('mediaSession' in navigator) || !song) return;
  var prev = _pendingPub;
  _pendingPub = {
    song: song,
    deck: deck || host().audioEl,
    via: via || 'select',
    force: !!(force || (prev && prev.force)),
    artReady: !!(prev && prev.artReady),
    artFailed: !!(prev && prev.artFailed),
    forceArtClear: !!(forceArtClear || (prev && prev.forceArtClear))
  };
  if (_pendingPubTimer) return;
  _pendingPubTimer = setTimeout(_flushPendingPublish, 90);
}
// Camino restaurado (cea63f1263 + coalescing):
// 1) chrome (document.title / application-name) YA
// 2) prefetch URL exacta (?ms=)
// 3) UN null-then-set cuando cover lista (o timeout 1.2 s) — patrón Pause→Play
function _publishMediaSessionWhenCoverReady(song, deck, via) {
  if (!song) return;
  var path = song.path || '';
  var artUrl = _artworkUrlOf(song);
  // Ya publicada esta MISMA pista con esta MISMA carátula y sigue viva → no
  // tocar `metadata`. Por spec W3C cada reasignación cancela el fetch de
  // artwork en curso y el `null` previo vacía la imagen ya pintada: republicar
  // "por si acaso" es justo lo que dejaba el miniplayer del Tesla en blanco.
  // El chrome (title/app-name) sí se refresca, que no cuesta nada.
  if (path && artUrl && path === _livePubPath && artUrl === _lastPublishedArtUrl) {
    host().sessionLog('info', {event: 'mediasession-skip', motivo: 'ya-viva-misma-carátula', path: path, via: via});
    try { _setPageChrome(song, _carMeta(song, deck || host().audioEl)); } catch(_eC) {}
    return;
  }
  // Ya hay un pipeline EN CURSO (prefetch de imagen aún sin resolver) para
  // esta MISMA pista: el ping-pong nativo llama aquí DOS veces por canción —
  // «PASO 5-bis» antes del play() y «PASO 5» al consumar el swap en _doSwap
  // (15g-ximo-engine.js) — sin esperar a que la primera termine de precargar
  // la carátula. Si dejamos que la segunda arranque OTRO fetch, se cancelan
  // mutuamente por spec W3C justo en el momento en que el coche negocia el
  // foco de audio con la pista nueva — reproducido con la telemetría real de
  // hoy (2026-08-06). Dejar que termine el pipeline que ya está en marcha.
  if (path && path === _pubInFlightPath) {
    host().sessionLog('info', {event: 'mediasession-skip', motivo: 'pipeline-en-curso-misma-pista', path: path, via: via});
    try { _setPageChrome(song, _carMeta(song, deck || host().audioEl)); } catch(_eC) {}
    return;
  }
  var gen = ++_msArtGen;
  _coverPipelineGen = gen;
  _pubInFlightPath = path;
  if (path && path !== _lastGoodArtworkPath) {
    _lastGoodArtwork = [];
    _lastGoodArtworkPath = '';
  }
  var _mEarly = _carMeta(song, deck || host().audioEl);
  _setPageChrome(song, _mEarly);
  var _t0 = Date.now();
  host().sessionLog('info', {event: 'mediasession-pipeline-start', path: path, artUrl: artUrl, via: via, gen: gen});
  // No publicamos MediaMetadata todavía: un set con artwork vacío / prematuro
  // + null posterior es exactamente el cancel-storm. Solo chrome (tab title)
  // ya; el nudge null-then-set va cuando la cover esté en caché.
  //
  // BUG (2026-08-06, reproducido con Playwright): el `setTimeout` de 1.2 s de
  // abajo era anónimo y nunca se cancelaba cuando `im.onload`/`im.onerror`
  // resolvían antes. Resultado: `go(true)` se llamaba DOS veces por canción —
  // una al cargar la imagen (~200-700 ms) y otra ~1.2 s después por el
  // timeout, que ya no hacía falta. La segunda reasigna metadata (null→set)
  // sobre una URL que el propio Chromium del Tesla puede no servir instantánea
  // desde caché, así que la portada aparecía un instante y volvía a
  // desaparecer ~1 s después — justo el síntoma reportado. Fix: guardar el
  // id del timeout y cancelarlo en cuanto `go()` publica una vez.
  var _published = false;   // go() solo publica UNA vez por generación
  var _fallbackTimer = 0;
  // `reason` (2026-08-12, depuración alta a petición del usuario): onload |
  // onerror | timeout | no-art | exception — para saber por CUÁL de las
  // cuatro vías se resolvió (o no) cada portada, sin tener que adivinarlo.
  function go(artReady, reason) {
    if (gen !== _msArtGen || _published) {
      host().sessionLog('info', {event: 'mediasession-pipeline-discard',
                          motivo: (gen !== _msArtGen ? 'gen-obsoleta' : 'ya-publicado'),
                          path: path, reason: reason, elapsedMs: Date.now() - _t0});
      if (_pubInFlightPath === path) _pubInFlightPath = '';
      return;
    }
    var intended = null;
    try {
      intended = _nowPlayingSong() || host().currentPlaylistSongs[host().currentSongIndex];
    } catch (_eInt) { intended = null; }
    if (path && intended && intended.path && intended.path !== path) {
      if (_pubInFlightPath === path) _pubInFlightPath = '';
      // Instrumentación (2026-08-12): esta pista quedó obsoleta (el usuario ya
      // saltó a otra) y su publish se descarta sin más — candidato a portada
      // "perdida" en saltos rápidos: si el siguiente publish también se
      // descarta por el mismo motivo, el widget se queda con metadata/arte
      // de una pista aún MÁS antigua. Antes esto pasaba en silencio.
      // (Descartada como causa principal 2026-08-13: desactivar este guard en
      // vivo no arregló la portada perdida — se deja el log, se quita el
      // bypass que ya se demostró que no ayudaba.)
      host().sessionLog('warn', {event: 'mediasession-publish-discarded', motivo: 'pista-obsoleta',
                          descartada: path, actual: intended.path, via: via, artReady: !!artReady,
                          reason: reason, elapsedMs: Date.now() - _t0});
      return;
    }
    _published = true;
    if (_pubInFlightPath === path) _pubInFlightPath = '';
    if (_fallbackTimer) { clearTimeout(_fallbackTimer); _fallbackTimer = 0; }
    if (_pendingPubTimer) { clearTimeout(_pendingPubTimer); _pendingPubTimer = 0; }
    host().sessionLog('info', {event: 'mediasession-pipeline-resolved', path: path, reason: reason,
                        artReady: !!artReady, elapsedMs: Date.now() - _t0});
    // Set YA con artwork de ESTA pista. Sin null, sin blob, sin timeout 1.2s.
    _pendingPub = {
      song: song,
      deck: deck || host().audioEl,
      via: (via || 'select') + (artReady ? '-cover' : '-noart'),
      force: true,
      artReady: !!artReady,
      artFailed: !artReady,
      forceArtClear: false
    };
    _flushPendingPublish();
  }
  try { _prewarmNextCover(); } catch (_ePw) {}
  if (!artUrl) { go(false, 'no-art'); return; }
  try {
    var im = new Image();
    im.onload = function() { go(true, 'onload'); };
    // 404 (Allez artist-cover): NO publicar esa URL ni vaciar artwork.
    im.onerror = function() { go(false, 'onerror'); };
    im.src = artUrl;
    // Hung image only. go() cancela el timer; _published evita 2º metadata=.
    _fallbackTimer = setTimeout(function() { go(!!artUrl, 'timeout'); }, 1200);
  } catch(_eImg) { go(false, 'exception'); }
}
function _updateMediaSession(song, deck) {
  // Una vía: chrome inmediato + un nudge null tras cover (camino Pause→Play).
  _publishMediaSessionWhenCoverReady(song, deck || host().audioEl, 'select');
}
// Invalida dedup/arte (MSE boundary, restore).
function _invalidateMediaDedup() {
  // Instrumentación (2026-08-12): si había un pipeline de portada EN CURSO
  // (_pubInFlightPath no vacío) al invalidar, ese `go()` va a caer en la rama
  // "gen-obsoleta" en cuanto resuelva — esta traza es la única forma de saber
  // que la invalidación fue la CAUSA, no una coincidencia.
  if (_pubInFlightPath) {
    try { host().sessionLog('info', {event: 'mediasession-dedup-invalidated', pipelineEnCurso: _pubInFlightPath}); } catch(_e) {}
  }
  _mediaSetKey = '';
  _mediaSetTs = 0;
  _carInfoLast = '';
  _msArtGen++;
  _lastPublishedArtUrl = '';
  _livePubPath = '';
  _pubInFlightPath = '';
  _lastGoodArtwork = [];
  _lastGoodArtworkPath = '';
  if (_pendingPubTimer) { clearTimeout(_pendingPubTimer); _pendingPubTimer = 0; }
  _pendingPub = null;
}

// ── REFRESCO PERIÓDICO DE RESPALDO (catch-all, NO es un reloj) ──
// `_carMeta` usa la duración ESTÁTICA de la canción (song.duration), no la
// posición en vivo — la barra que se mueve en el coche la manda por completo
// `_updateMediaPositionState` (setPositionState), que NUNCA toca `metadata` y
// por eso no cancela el artwork. Este tick de 1 s solo sirve de red de
// seguridad por si algo cambia el título/artista/álbum sin pasar por
// `_updateMediaSession` (p.ej. cambio de nombre de playlist). Republica como
// mucho una vez por segundo, y SOLO si `_livePubPath` ya coincide con la
// pista actual (ver guarda de arriba) para no competir con el pipeline de
// portada durante una transición de canción.
// Apagar en vivo si hiciera falta:
//   __ximoCarInfo(false)   → solo texto estático (sin este respaldo)
//   __ximoCarInfo(5000)    → respaldo cada 5 s en vez de 1 s
var _carInfoEnabled = true;
var _carInfoEveryMs = 1000;
var _carInfoNextTs = 0;
var _carInfoLast = '';

function _refreshCarInfo() {
  if (!_carInfoEnabled || !('mediaSession' in navigator)) return;
  // Durante una transición mandan los metadatos que publicó el ping-pong
  // ANTES del play(). Este refresco lee `host().currentSongIndex`, que hasta el swap
  // sigue apuntando a la canción SALIENTE: sin esta guarda, el tick de 1 s
  // pisaba la info nueva y devolvía la anterior al reproductor del coche.
  if (host().fastSwitchIdx >= 0) return;
  var now = Date.now();
  if (now < _carInfoNextTs) return;
  _carInfoNextTs = now + _carInfoEveryMs;
  // La canción que SUENA la manda el SEGMENTO MSE (posición real del audio),
  // no host().currentSongIndex, que va por detrás en la frontera → por eso el
  // miniplayer del Tesla ponía la portada de la canción ANTERIOR. En karaoke,
  // sin segmento vivo, _nowPlayingSong cae a host().currentSongIndex.
  var song = _nowPlayingSong();
  if (!song) return;
  var _m = _carMeta(song, host().audioEl);
  var key = _mediaSongKey(song, _m);
  if (key === _carInfoLast) return;      // nada que repintar
  // CAMBIO DE CANCIÓN en marcha (_livePubPath aún no es la pista actual):
  // el pipeline _publishMediaSessionWhenCoverReady ya está prefetcheando su
  // carátula y hará el ÚNICO `metadata =` de la transición en cuanto la
  // imagen esté lista. Publicar TAMBIÉN desde aquí —que no espera al
  // prefetch— es el cancel-storm reproducido con datos reales de coche
  // (2026-08-06): dos `mediasession-set` distintos («refresh» y luego
  // «select-cover») a 70-700 ms uno de otro para la MISMA canción, cada uno
  // cancelando por spec W3C el fetch de artwork del anterior. Cuando el
  // pipeline termine, `_applyMediaMetadata` deja `_carInfoLast` al día y este
  // tick vuelve a su no-op normal (`key === _carInfoLast`) el segundo siguiente.
  if ((song.path || '') !== _livePubPath) return;
  // Segundo metadata= (refresh) cancela el fetch W3C / pisa con vacío.
  // Con artwork vivo de ESTA pista: solo chrome + playbackState.
  if (_lastPublishedArtUrl) {
    try {
      navigator.mediaSession.playbackState = _msPlaybackState();
      _setPageChrome(song, _m);
    } catch (_eR) {}
    _carInfoLast = key;
    return;
  }
  // Refresco de texto (reloj): sin forzar clear de artwork si la URL no cambia.
  _pendingPub = {
    song: song,
    deck: host().audioEl,
    via: 'refresh',
    force: false,
    artReady: false,
    forceArtClear: false
  };
  if (_pendingPubTimer) { clearTimeout(_pendingPubTimer); _pendingPubTimer = 0; }
  _flushPendingPublish();
}

// Deshacer los metadatos adelantados: el ping-pong los publica ANTES del
// play(), así que si la transición no llega a consumarse hay que devolver al
// reproductor del coche la canción que sigue sonando de verdad.
function _restoreMediaSessionActual() {
  var song = host().currentPlaylistSongs[host().currentSongIndex];
  if (!song) return;
  _carInfoLast = '';        // forzar repintado
  _updateMediaSession(song, host().audioEl);
}

// Ajuste en vivo desde la consola del coche.
window.__ximoCarInfo = function(v) {
  if (v === false) _carInfoEnabled = false;
  else if (v === true) _carInfoEnabled = true;
  else if (typeof v === 'number' && v >= 250) { _carInfoEnabled = true; _carInfoEveryMs = v; }
  return {activo: _carInfoEnabled, cadaMs: _carInfoEveryMs, linea: _carInfoLast};
};

  return {
    bindHost: bindHost,
    setupHandlers: setupMediaSessionHandlers,
    updatePositionState: _updateMediaPositionState,
    clearPositionState: _clearMediaPositionState,
    mseCurSeg: _mseCurSeg,
    nowPlayingSong: _nowPlayingSong,
    coverSrc: _coverSrc,
    prewarmCover: _prewarmCover,
    carArtwork: _carArtwork,
    carAlbum: _carAlbum,
    carMeta: _carMeta,
    publish: _publishMediaSession,
    publishWhenCoverReady: _publishMediaSessionWhenCoverReady,
    update: _updateMediaSession,
    refreshCarInfo: _refreshCarInfo,
    restoreActual: _restoreMediaSessionActual,
    invalidateDedup: _invalidateMediaDedup,
    clearPageChrome: _clearPageChrome,
    setPageChrome: _setPageChrome,
    bumpCarInfo: function(){ _carInfoNextTs = 0; }
  };
})();
