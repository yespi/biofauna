/* — XimoPlayerUi: setupPlayer extraído de 15-ia.js (deuda ≤1500, 2026-08-10).
   bindHost no hace falta: setup(H) recibe el host con getters/setters vivos. */
window.XimoPlayerUi = (function(){
  "use strict";

  function setup(H) {
    if (!H) throw new Error('XimoPlayerUi.setup: host required');

    var playBtn = document.getElementById('ia-play-btn');
    var prevBtn = document.getElementById('ia-prev-btn');
    var nextBtn = document.getElementById('ia-next-btn');
    var rewBtn = document.getElementById('ia-rew-btn');
    var fwdBtn = document.getElementById('ia-fwd-btn');
    var shuffleBtn = document.getElementById('ia-shuffle-btn');
    var repeatBtn = document.getElementById('ia-repeat-btn');
    var progressWrap = document.getElementById('ia-progress-wrap');
    var progressBar = document.getElementById('ia-progress-bar');
    var progressThumb = document.getElementById('ia-progress-thumb');

    // ── Toast de carga (petición usuario 2026-08-12) ──
    // Al saltar rápido a una canción que aún no está lista (streaming/MSE sin
    // datos suficientes) el usuario se queda con la barra congelada sin saber
    // si algo va mal. `waiting` es la señal del propio <audio> para eso.
    // Retraso de 400ms: evita el parpadeo en cargas casi instantáneas (caso
    // normal), pero sigue cubriendo el caso real reportado (varios segundos).
    var _loadToast = null, _loadToastTimer = 0;
    function _clearLoadToast() {
      if (_loadToastTimer) { clearTimeout(_loadToastTimer); _loadToastTimer = 0; }
      if (_loadToast) { H.dismissToast(_loadToast); _loadToast = null; }
    }
    function _armLoadToast() {
      if (_loadToast || _loadToastTimer) return;
      _loadToastTimer = setTimeout(function() {
        _loadToastTimer = 0;
        _loadToast = H.showToast('Cargando canción…', 'info', 0);
      }, 400);
    }

    // ── Listeners de deck ──
    // Se enganchan a los DOS elementos <audio>, porque tras un swap gapless el
    // deck activo es el otro objeto. Cada handler ignora los eventos que no
    // vengan del deck activo (`this !== audioEl`), salvo los que necesitan
    // actuar sobre el saliente.
    function _bindDeck(el) {

    el.addEventListener('timeupdate', function() {
      if(this !== H.audioEl) return;
      H._lastTimeupdateTs = Date.now();
      // Stems activos: no pelear con _karaokeTimeUpdate (barra loco adelante/atrás).
      if (H._karaokeHandoffLock || (H._karaokeConnected && H._audioInst)) return;
      if (H._getMse()) {
        H._mseTick();
        // MediaSession position desde el deck activo también en MSE (timeupdate
        // salía antes sin setPositionState; el timer 1s lo cubría, esto lo refuerza).
        var _nowPos = Date.now();
        if (_nowPos - H._lastPosSync > 1000) {
          H._lastPosSync = _nowPos;
          H._updateMediaPositionState();
        }
        return;
      }   // M5: la línea temporal la gestiona el motor MSE
      var _durUi = (H.audioEl.duration && isFinite(H.audioEl.duration) && H.audioEl.duration > 0) ? H.audioEl.duration : 0;
      if(_durUi > 0) {
        var pct = Math.max(0, Math.min(100, (H.audioEl.currentTime / _durUi) * 100));
        if(progressBar) progressBar.style.width = pct + '%';
        if(progressThumb) progressThumb.style.left = pct + '%';
        if(progressWrap) {
          try { progressWrap.setAttribute('aria-valuenow', String(Math.round(pct))); } catch(_eAria) {}
        }
        document.getElementById('ia-time-current').textContent = H.formatTime(H.audioEl.currentTime);
        document.getElementById('ia-time-total').textContent = H.formatTime(_durUi);
        // En modo karaoke usar el tiempo del instrumental (H.audioEl está en pausa)
        var _kt = (H._audioInst && (H._karaokeConnected || document.body.classList.contains('ximo-karaoke')) && H._audioInst.currentTime > 0) ? H._audioInst.currentTime : H.audioEl.currentTime;
        H.updateKaraoke(_kt);
        // #90 — refrescar la posición en el reproductor del coche (~1/s)
        var now = Date.now();
        if(now - H._lastPosSync > 1000) { H._lastPosSync = now; H._updateMediaPositionState(); }
        // GAPLESS: segunda vía de disparo, además del temporizador. En primer
        // plano `timeupdate` es más fino; en 2º plano está estrangulado y manda
        // el timer de H._armGaplessTimer(). Idempotente (H._gaplessArmed).
        if(H.isPlaying && (H.audioEl.duration - H.audioEl.currentTime) <= H._gaplessLead) {
          H._startGapless();
        }
        // FALLBACK nativo (solo si MSE NO está activo; con MSE, timeupdate ya ha
        // salido antes en H._mseTick): adelantar el cambio con la maquinaria
        // mismo-elemento → ping-pong (Tesla-segura, sin recargar el activo).
        if (H._useNativeAudio() && H.isPlaying && !H.isRepeat && !H._gaplessActive && !H._switchingTrack &&
            (H.audioEl.duration - H.audioEl.currentTime) <= H._nativeLead) {
          if (!H._nativeSameElementSwitch('timeupdate')) H._nativeProactiveSwitch();
        }
        // Puente de ruido: red de seguridad para cuando el gapless no cumple
        // (shuffle, repeat, fin de playlist, buffer no listo). Idempotente.
        if(H.isPlaying && !H.isRepeat && !H._gaplessActive && (H.audioEl.duration - H.audioEl.currentTime) <= 0.6) {
          H._startSilenceBridge();
        }
      }
    });

    el.addEventListener('ended', function() {
      // Tras un swap gapless este evento llega del deck SALIENTE, que ya no es
      // el activo: ignorarlo (la siguiente canción lleva ~1s sonando).
      if(this !== H.audioEl) return;
      var _endedUseTransport = false;
      var elapsed = H._songStartTime ? ((Date.now() - H._songStartTime) / 1000).toFixed(1) : '?';
      H.sessionLog('end', {reason: 'natural end', elapsed: elapsed + 's', currentTime: H.audioEl.currentTime, duration: H.audioEl.duration});

      // M5 (MSE): entre pistas NO hay 'ended' (buffer continuo). Si llega, es el
      // fin real de lo bufferizado: si queda algo por anexar, pedirlo y seguir;
      // si no, cerrar el motor y avanzar por la vía clásica (fin de playlist).
      if (H._getMse()) {
        if (_mseNextIdx(H._getMse().lastIdx) >= 0) {
          H.sessionLog('warn', {action: 'mse-ended-refeed', bgLag: H._timeupdateLag()});
          _mseAppendNext();
          H.audioEl.play().catch(function(){});
          return;
        }
        H.sessionLog('info', {action: 'mse-ended-final'});
        H._mseTeardown();
        // cae a la lógica clásica de abajo para cerrar/avanzar playlist
      }

      // Crossfade en curso pero el swap aún no se ha consumado (timer del swap
      // estrangulado en 2º plano): consumarlo ahora y NO seguir por la vía
      // clásica, que recargaría el <audio> y volvería a abrir el hueco.
      if(H._gaplessActive) {
        H._finishGapless(H._expectedNextIndex() >= 0 ? H._expectedNextIndex() : H.currentSongIndex + 1);
        return;
      }

      // Gapless disparado pero AÚN sin consumar: `_gaplessArmed` se pone antes
      // de que resuelva `preloadEl.play()`, así que existe una ventana en la que
      // `ended` llega con armed=true y active=false. Si se sigue por la vía
      // clásica sin cancelar, la promesa resuelve después y cruza los gains
      // sobre decks que ya no son los que cree → dos decks a la vez y corte de
      // audio al cambiar de canción. La ventana se ensancha con la máquina
      // cargada, que es justo cuando se reportó el fallo.
      if(H._gaplessArmed) {
        H.sessionLog('warn', {action: 'gapless-abort-on-ended'});
        H._resetGapless();
      }

      // ── MODO NATIVO (coche): aquí NO se recarga nunca el <audio> activo ──
      // La vía clásica (H.playNext → H.playSong → H.selectSong) reasigna `.src` y
      // hace load()+play() sobre el MISMO elemento, abriendo un hueco de
      // silencio real de cientos de ms (segundos en la red del coche). El
      // Tesla lo lee como "la app del navegador terminó su transmisión" y
      // reanuda la fuente anterior (Spotify). En modo nativo no hay
      // AudioContext, así que el puente de ruido tampoco puede taparlo: la
      // única salida válida es el ping-pong sobre el deck alterno.
      //
      // Además evita el doble avance: sin esta guarda, un ping-pong en vuelo
      // (que ya está cargando la pista N+1 en H.preloadEl) se solapaba con un
      // H.playNext() que cargaba esa MISMA pista en H.audioEl — dos instancias del
      // mismo tema peleando, y el swap posterior pausando el elemento
      // equivocado.
      if (H._useNativeAudio() && !H.isRepeat) {
        if('mediaSession' in navigator) try { navigator.mediaSession.playbackState = 'playing'; } catch(e){}
        if (H._fastSwitchIdx >= 0) {
          // Ping-pong en vuelo: solo esperar si el deck entrante YA suena.
          // Si no (swap clavado), resetear y seguir a playNext — de lo contrario
          // el auto-avance se queda muerto para el resto de la sesión.
          var _preLive = H.preloadEl && !H.preloadEl.paused && H.preloadEl.currentTime > 0.05;
          if (_preLive) {
            H.sessionLog('warn', {action: 'native-ended-switch-inflight', idx: H._fastSwitchIdx});
            return;
          }
          H.sessionLog('warn', {action: 'native-ended-switch-stuck-reset', idx: H._fastSwitchIdx,
            preloadReady: H.preloadEl ? H.preloadEl.readyState : -1});
          H._fastSwitchIdx = -1;
          try { H._restoreMediaSessionActual(); } catch(_eRst) {}
        }
        if (H._expectedNextIndex() >= 0) {
          // timeupdate venía estrangulado y no llegó a disparar el proactivo:
          // lanzarlo ahora. El keep-alive cubre el hueco mientras carga.
          H._startKeepAlive();
          // Fallback: mismo-elemento desde memoria si hay blob; si no, ping-pong
          // SOLO si el deck inactivo YA tiene la siguiente. Tesla 23-24 ago:
          // ended natural -> gapless-not-ready preloadIndex=-1 decks=0 ->
          // native-ended-pingpong -> _nativeProactiveSwitch no-op (MSE eligible
          // o preload vacio) -> return SIN playNext. Skip manual si funciona.
          H.sessionLog('info', {action: 'native-ended-sameel', bgLag: H._timeupdateLag()});
          if (H._nativeSameElementSwitch('ended')) return;
          var _nx = H._expectedNextIndex();
          var _preOk = H._preloadIndex === _nx && H.preloadEl && H.preloadEl.readyState >= 2;
          var _mseOn = false;
          try { _mseOn = !!H._mseEligible(); } catch (_eMseOn) {}
          if (_preOk && !_mseOn) {
            H.sessionLog('info', {action: 'native-ended-pingpong', bgLag: H._timeupdateLag(), preloadIndex: H._preloadIndex});
            H._nativeProactiveSwitch();
            return;
          }
          H.sessionLog('info', {action: 'native-ended-transport',
            preloadIndex: H._preloadIndex, expectedNext: _nx,
            preloadReady: H.preloadEl ? H.preloadEl.readyState : -1,
            mseEligible: _mseOn, decks: (H._deckNodes && H._deckNodes.length) || 0});
          _endedUseTransport = true;
        } else {
          // Fin de playlist, cola pendiente o shuffle sin plan: no hay "siguiente"
          // que cruzar, asi que aqui la via clasica si es la correcta.
          H.sessionLog('info', {action: 'native-ended-classic'});
          H._startKeepAlive();
        }
      }

      // FAST-SWITCH NATIVO: siguiente cancion YA (timeupdate / ended).
      // Idempotente si ya se ejecuto. NO lanzarlo si decidimos transporte
      // (preloadIndex=-1 / MSE eligible): ping-pong frio + playNext = doble avance.
      if (!_endedUseTransport) {
        H._nativeProactiveSwitch();
      }

      // ── PUENTE DE SILENCIO: activar inmediatamente para evitar que el coche detecte el silencio ──
      H._startSilenceBridge();
      // Mantener el estado 'playing' de cara al coche durante el hueco entre canciones
      if('mediaSession' in navigator) try { navigator.mediaSession.playbackState = 'playing'; } catch(e){}

      if(H.isRepeat) {
        H.audioEl.currentTime = 0;
        H._retryPlayCurrent(0);
      } else if(H.partyMode) {
        if(H.currentSongIndex >= H.currentPlaylistSongs.length - 1) {
          H.advanceToNextPlaylist();
        } else {
          H.playNext();
        }
      } else {
        H.playNext();
      }
      
      // Fallback: apagar el puente sólo si la siguiente canción tarda muchísimo
      // (la vía normal es 'playing' → H._stopSilenceBridge). 30s cubre la red lenta
      // del coche sin dejar el ruido colgado indefinidamente si algo falla.
      window.XimoCarBridge.armFallbackTimeout(30000);
    });

    // Detener el puente de silencio cuando empieza a sonar la nueva canción
    el.addEventListener('playing', function() {
      // Durante el crossfade el deck entrante dispara 'playing' antes del swap:
      // sus efectos (registro de escucha, mediaSession) los aplica H._finishGapless.
      if(this !== H.audioEl) return;
      H._switchingTrack = false;   // la nueva canción ya suena: fin de la transición
      H._onDeckPlaying();
      H._armGaplessTimer();        // armar el gapless de ESTA canción
    });
    el.addEventListener('pause', function() {
      if(this !== H.audioEl) return;
      // En KARAOKE / stems VOZ, H.audioEl se pausa A PROPÓSITO (suena H._audioInst).
      // Este listener lo tomaba como pausa EXTERNA → H.isPlaying=false mientras
      // el karaoke sonaba → letra y viz se congelaban.
      if (document.body.classList.contains('ximo-karaoke') || H._karaokeConnected) return;
      // ── FASE 1/2 Fable 5: logging de origen + multi-tap ──
      // Mismo criterio que el handler de Media Session: `_internalOp` a secas
      // se queda corto si el evento llega con unos ms de retraso respecto a
      // nuestro propio pause().
      var _origin = H._isSelfInflictedPause() ? 'internal' : 'external';
      H.sessionLog('info', {event: 'el-event:deck:pause', origin: _origin,
        currentTime: H.audioEl.currentTime, duration: H.audioEl.duration,
        hidden: document.hidden, internalOp: H._internalOp});
      // Si es una pausa externa (Tesla): o la cuenta el multi-tap, o es real.
      if (_origin === 'external' && H._useNativeAudio()) {
        if (H._multiTapEnabled) {
          // Reanudar inmediatamente: el Tesla ya pausó el elemento físicamente,
          // pero no queremos silencio mientras contamos taps.
          H.audioEl.play().catch(function(){});
          H._onExternalPause();
          return;  // no ejecutar la lógica normal de pausa
        }
        // ¿Nos ha pausado el coche al irnos al GPS? Entonces reanudar.
        if (H._pausaPorSegundoPlano()) { H._reanudaTrasFoco('elemento'); return; }
        // Multi-tap apagado y en primer plano: es el usuario, se respeta.
        H._commitExternalPause();
        return;
      }
      // Solo declarar 'paused' al coche si es una pausa REAL del usuario. Durante
      // un cambio de canción (H._switchingTrack), crossfade o auto-avance (H.isPlaying
      // sigue true) mantener 'playing' para que el Tesla NO crea que hemos parado
      // y cambie de fuente.
      var transitando = H.isPlaying || H._crossfadeActive || H._switchingTrack || H._gaplessActive;
      if('mediaSession' in navigator) try {
        navigator.mediaSession.playbackState = transitando ? 'playing' : 'paused';
      } catch(e){}
      H._updateMediaPositionState();
      // Si es una pausa REAL del usuario, apagar el puente (tras un momento para
      // no interferir con un cambio de canción en curso).
      if (!transitando) {
        H._resetGapless();   // pausa real: desarmar el gapless pendiente
        setTimeout(function() {
          if (!H.isPlaying && !H._crossfadeActive && !H._switchingTrack) H._stopSilenceBridge();
        }, 1000);
      }
    });

    el.addEventListener('loadedmetadata', function() {
      if(this !== H.audioEl) return;
      H.sessionLog('loaded', {duration: H.audioEl.duration, title: (H.currentPlaylistSongs[H.currentSongIndex]||{}).title});
      document.getElementById('ia-time-total').textContent = H.formatTime(H.audioEl.duration);
      H._updateMediaPositionState();  // #90 — informar duración al coche en cuanto se conoce
      H._armGaplessTimer();           // ya se conoce la duración: se puede programar el crossfade
    });

    el.addEventListener('seeked', function() {
      if(this !== H.audioEl) return;
      H._armGaplessTimer();           // el punto de disparo cambia tras un seek
    });

    el.addEventListener('error', function(e) {
      if(this !== H.audioEl) return;
      _clearLoadToast();
      H.sessionLog('error', {event: 'audioEl.error', code: H.audioEl.error ? H.audioEl.error.code : '?', msg: H.audioEl.error ? H.audioEl.error.message : 'unknown', net: H.audioEl.networkState, ready: H.audioEl.readyState, src: (H.audioEl.currentSrc||H.audioEl.src||'').split('/').pop()});
    });

    el.addEventListener('waiting', function() {
      if(this !== H.audioEl) return;
      _armLoadToast();
      H.sessionLog('warn', {event: 'waiting', currentTime: H.audioEl.currentTime});
    });

    el.addEventListener('playing', function() {
      if(this !== H.audioEl) return;
      _clearLoadToast();
    });

    // `stalled` viene del pipeline de media, no de los timers: llega aunque el
    // navegador del coche esté estrangulando `setInterval`. Es la vía rápida
    // para detectar el atasco de #100; el intervalo es la red de seguridad.
    el.addEventListener('stalled', function() {
      if(this !== H.audioEl) return;
      // _stallSnapshot/_checkStall son privadas de 15m-ximo-watchdog.js, no
      // globales — llamarlas sueltas aquí lanzaba un ReferenceError sin
      // capturar en CADA 'stalled' real (bug real encontrado 2026-08-10 con
      // telemetría de coche real: 4 crashes en una sesión con una canción
      // que tardó 90-115s en cargar). window.XimoWatchdog.notifyStalled()
      // hace lo mismo por dentro, con acceso correcto a su propio estado.
      window.XimoWatchdog.notifyStalled();
    });

    el.addEventListener('canplay', function() {
      if(this !== H.audioEl) return;
      _clearLoadToast();
      var loadTime = H._songStartTime ? (Date.now() - H._songStartTime) + 'ms' : '?';
      H.sessionLog('info', {event: 'canplay', loadTime: loadTime});
    });

    }  // fin _bindDeck

    _bindDeck(H.audioEl);
    _bindDeck(H.preloadEl);

    if(playBtn) playBtn.addEventListener('click', window.XimoTransport.toggle);
    if(prevBtn) prevBtn.addEventListener('click', window.XimoTransport.previous);
    if(nextBtn) nextBtn.addEventListener('click', window.XimoTransport.next);
    // Stop UI retirado (redundante con Pause). XimoTransport.stop sigue para MediaSession.
    // ±10s: _kSeekRel/_seekRelMain (implementación de seek duplicada y SIN
    // usar — ningún botón ni atajo las llamaba, rew/fwd usan
    // window.XimoTransport.seekBy) se retiraron aquí (auditoría 2026-08-08):
    // dos caminos de seek en paralelo, uno vivo y uno muerto, es exactamente
    // el tipo de trampa que deja "funciona en un sitio pero no en otro" si
    // alguien las conecta más tarde sin saber que a esta le faltaba el
    // resync de letras que sí tiene H._transportSeekTo (15-ia.js más abajo).
    if(rewBtn) rewBtn.addEventListener('click', function() { window.XimoTransport.seekBy(-10); });
    if(fwdBtn) fwdBtn.addEventListener('click', function() { window.XimoTransport.seekBy(10); });
    if(shuffleBtn) shuffleBtn.addEventListener('click', function() {
      H.isShuffle = !H.isShuffle;
      shuffleBtn.classList.toggle('active', H.isShuffle);
      shuffleBtn.setAttribute('aria-pressed', H.isShuffle ? 'true' : 'false');
      H.sessionLog('shuffle', {enabled: H.isShuffle});
      // El plan anterior ya no vale: replanificar y re-precargar el deck para
      // que el gapless apunte a la pista correcta en el nuevo modo.
      H._plannedForIndex = -1;
      H._plannedNextIndex = -1;
      H._resetGapless();
      H._preloadNext();
      H._armGaplessTimer();
      if(H.isShuffle) {
        H.shuffleHistory = [H.currentSongIndex];
        H.shuffleIndex = 0;
      }
    });
    if(repeatBtn) {
      repeatBtn.setAttribute('aria-pressed', H.isRepeat ? 'true' : 'false');
      repeatBtn.addEventListener('click', function() {
        H.isRepeat = !H.isRepeat;
        repeatBtn.classList.toggle('active', H.isRepeat);
        repeatBtn.setAttribute('aria-pressed', H.isRepeat ? 'true' : 'false');
      });
    }
    if (shuffleBtn) shuffleBtn.setAttribute('aria-pressed', H.isShuffle ? 'true' : 'false');
    // Volumen
    var volSlider = document.getElementById('ia-volume');
    if(volSlider) {
      volSlider.value = localStorage.getItem('ximo_volume') || '1';
      H.audioEl.volume = parseFloat(volSlider.value);
      H._savedVolume = H.audioEl.volume;
      volSlider.addEventListener('input', function() {
        var v = parseFloat(this.value);
        H.audioEl.volume = v;
        H._savedVolume = v;
        localStorage.setItem('ximo_volume', this.value);
        // En karaoke el volumen total va por el H._masterGain del AudioContext
        // (H.audioEl está mudo); sin esto el slider no afectaba al karaoke.
        if (document.body.classList.contains('ximo-karaoke') && H._masterGain) {
          try { H._masterGain.gain.value = v; } catch(e) {}
        }
      });
    }

    // #104 — Like de la canción sonando (el botón ya existía en el HTML,
    // #ia-like-btn, pero nunca se había conectado a nada).
    var likeBtn = document.getElementById('ia-like-btn');
    if(likeBtn) {
      likeBtn.addEventListener('click', function() {
        var song = H.currentPlaylistSongs[H.currentSongIndex];
        if(song && song.path) H.toggleFavorite(song.path);
      });
    }
    var sendCurBtn = document.getElementById('ia-send-current-btn');
    if(sendCurBtn) {
      sendCurBtn.addEventListener('click', function() {
        var song = (typeof H._nowPlayingSong === 'function') ? H._nowPlayingSong() : H.currentPlaylistSongs[H.currentSongIndex];
        if(song && song.path) H._sendToAccountQueue(song, false);
      });
    }
    H._updateQueueBadge();
    var queueNavBtn = document.getElementById('ia-queue-nav-btn');
    if(queueNavBtn) queueNavBtn.addEventListener('click', function() { H.iaShowQueue(); });
    var favNavBtn = document.getElementById('ia-fav-nav-btn');
    if(favNavBtn) favNavBtn.addEventListener('click', function() { H.iaShowFavorites(); });
    var recentNavBtn = document.getElementById('ia-recent-nav-btn');
    if(recentNavBtn) recentNavBtn.addEventListener('click', function() { H.iaShowRecent(); });

    // Karaoke mode toggle + SingStar (Web Audio mixer, vocal slider, windowed lyrics)
    var karaokeBtn = document.getElementById('ia-karaoke-btn');
    // Variables del mixer Web Audio (declaradas al inicio del IIFE)
    var _karaokeGen = 0;  // contador de generación: evita callbacks obsoletos

    var _karaokeEotLock = false;
    function _onKaraokeEnded() {
      if (!H._audioInst) return;
      if (!H._karaokeConnected && !document.body.classList.contains('ximo-karaoke')) return;
      if (H._switchingTrack) return;
      if (_karaokeEotLock) return;
      _karaokeEotLock = true;
      var _kPath = '';
      try { _kPath = (H.currentPlaylistSongs[H.currentSongIndex] || {}).path || ''; } catch (_eKp) {}
      H.sessionLog('end', {reason: 'karaoke-eot', path: _kPath, idx: H.currentSongIndex});
      try {
        if (window.XimoTransport && typeof window.XimoTransport.next === 'function') window.XimoTransport.next();
        else H.playNext();
      } catch (_eKn) {
        try { H.playNext(); } catch (_eKn2) {}
      }
      setTimeout(function(){ _karaokeEotLock = false; }, 1600);
    }

    function _karaokeTimeUpdate() {
      // Stems activos: UI karaoke O fader VOZ en modo normal
      if (!H._audioInst || (!H._karaokeConnected && !document.body.classList.contains('ximo-karaoke'))) return;
      var ct = H._audioInst.currentTime;
      // Seguir el audio REAL del stem, no la flag H.isPlaying (que tras restore /
      // handoff puede estar desincronizada → letra congelada mientras suena).
      if (!H._audioInst.paused || H.isPlaying) {
        // Duración = SOLO la del stem de karaoke (H.audioEl.duration es la línea
        // temporal MSE CONCATENADA de todas las canciones → daba un progreso
        // minúsculo y mal). Y el elemento real es #ia-progress-bar; antes se
        // escribía en #ia-progress (que NO existe) → la barra no se movía.
        var karaokeDur = (H._audioInst.duration && isFinite(H._audioInst.duration)) ? H._audioInst.duration : 0;
        var pct = karaokeDur > 0 ? (ct / karaokeDur * 100) : 0;
        var progressBar = document.getElementById('ia-progress-bar');
        var progressThumb = document.getElementById('ia-progress-thumb');
        if(progressBar) progressBar.style.width = Math.min(pct, 100) + '%';
        if(progressThumb) progressThumb.style.left = Math.min(pct, 100) + '%';
        document.getElementById('ia-time-current').textContent = H.formatTime(ct);
        var _tt = document.getElementById('ia-time-total');
        if(_tt && karaokeDur > 0) _tt.textContent = H.formatTime(karaokeDur);
        try { H.updateKaraoke(ct, karaokeDur); } catch(_e) {}
        // Sin esto, la barra de progreso NATIVA del coche (MediaSession
        // setPositionState) quedaba congelada con el valor de justo antes de
        // conectar los stems durante TODA la sesión de karaoke — todas las
        // demás vías que sí actualizan posición están explícitamente
        // excluidas mientras karaoke está activo (auditoría 2026-08-08).
        try { H._updateMediaPositionState(H._audioInst); } catch(_eMps) {}
      }
    }

    function _destroyKaraokeAudioElements() {
      if (H._audioInst) {
        H._audioInst.removeEventListener('timeupdate', _karaokeTimeUpdate);
        H._audioInst.removeEventListener('ended', _onKaraokeEnded);
        if (H._audioInst._syncInterval) { clearInterval(H._audioInst._syncInterval); }
        try { H._audioInst.pause(); } catch(e) {}
        try { H._audioInst.remove(); } catch(e) {}
      }
      if (H._audioVocals) {
        try { H._audioVocals.pause(); } catch(e) {}
        try { H._audioVocals.remove(); } catch(e) {}
      }
      H._audioInst = null;
      H._audioVocals = null;
      H._sourceInst = null;
      H._sourceVocals = null;
      H._vocalDynAnalyser = null;
      H._vocalDynData = null;
      H._getVocalRms = function(){ return 0; };
      H._karaokeConnected = false;
    }

    function _connectKaraokeAudio(karaokeKey, currentTime) {
      // Incrementar generación: las llamadas previas quedan obsoletas
      var myGen = ++_karaokeGen;
      // Destruir elementos anteriores
      _destroyKaraokeAudioElements();
      try {
        if (!H._audioCtx) H._audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        // Master gain: controla el volumen TOTAL del karaoke (instrumental + vocals)
        if (!H._masterGain) { H._masterGain = H._audioCtx.createGain(); H._masterGain.connect(H._audioCtx.destination); H._masterGain.gain.value = 1; }
        // Vocal gain: solo la voz, controlado por el slider
        if (!H._gainNode) { H._gainNode = H._audioCtx.createGain(); H._gainNode.connect(H._masterGain); }
        // Aplicar valor del slider
        if (vocalSlider) {
          var val = parseInt(vocalSlider.value);
          if (!isFinite(val)) val = 100;
          H._gainNode.gain.value = Math.max(0, Math.min(1, val / 100));
        }
        
        // Crear NUEVOS elementos <audio> (imprescindible: createMediaElementSource falla si se reusa)
        H._audioInst = document.createElement('audio');
        window.__audioInst = H._audioInst;
        H._audioInst.preload = 'auto';
        // same-origin + cookie de sesión (no anonymous: bloquearía yespi_access)
        document.body.appendChild(H._audioInst);
        
        H._audioVocals = document.createElement('audio');
        H._audioVocals.preload = 'auto';
        document.body.appendChild(H._audioVocals);
        
        var baseUrl = '/api/ia/karaoke-file/' + karaokeKey + '/';
        H._audioInst.src = baseUrl + 'instrumental.mp3';
        H._audioVocals.src = baseUrl + 'vocals.mp3';
        
        H._audioInst.load();
        H._audioVocals.load();
        
        var ready = function() {
          if (_karaokeGen !== myGen) return;  // llamada obsoleta
          try {
            H._sourceInst = H._audioCtx.createMediaElementSource(H._audioInst);
            H._sourceVocals = H._audioCtx.createMediaElementSource(H._audioVocals);
            H._sourceInst.connect(H._masterGain);
            // Tap vocals BEFORE gain so dynamics guide reflects the reference stem
            // even when the singer lowers VOZ to 0%.
            try {
              H._vocalDynAnalyser = H._audioCtx.createAnalyser();
              H._vocalDynAnalyser.fftSize = 256;
              H._vocalDynAnalyser.smoothingTimeConstant = 0.55;
              H._vocalDynData = new Uint8Array(H._vocalDynAnalyser.fftSize);
              H._sourceVocals.connect(H._vocalDynAnalyser);
              H._getVocalRms = function() {
                if (!H._vocalDynAnalyser || !H._vocalDynData) return 0;
                try {
                  H._vocalDynAnalyser.getByteTimeDomainData(H._vocalDynData);
                  var sum = 0;
                  for (var i = 0; i < H._vocalDynData.length; i++) {
                    var v = (H._vocalDynData[i] - 128) / 128;
                    sum += v * v;
                  }
                  return Math.sqrt(sum / H._vocalDynData.length);
                } catch (_eRms) { return 0; }
              };
            } catch (_eDyn) {
              H._vocalDynAnalyser = null;
              H._vocalDynData = null;
              H._getVocalRms = function(){ return 0; };
            }
            H._sourceVocals.connect(H._gainNode);
            H._karaokeConnected = true;
            // Reaplicar fader VOZ (puede haberse movido antes de que existiera H._gainNode)
            try { if (typeof _applyVocalSliderGain === 'function') _applyVocalSliderGain();
                  else if (vocalSlider && H._gainNode) {
                    var _vg = Math.max(0, Math.min(1, (parseInt(vocalSlider.value)||100)/100));
                    H._gainNode.gain.value = _vg;
                    if (H._audioVocals) H._audioVocals.volume = _vg;
                  }
            } catch(_vgE) {}
            if (currentTime > 0) { H._audioInst.currentTime = currentTime; H._audioVocals.currentTime = currentTime; }
            // Silenciar y pausar el deck base como operación INTERNA. Chromium
            // puede convertir este pause en una acción Media Session; sin la
            // marca interna, el handler karaoke la interpretaba como un toque
            // del usuario y pausaba los stems justo después de conectar.
            try {
              H.audioEl.volume = 0;
              H._audioWantPlay = false;
              H._internalOp++;
              H._lastInternalPauseTs = Date.now();
              H.audioEl.pause();
              setTimeout(function(){ if (H._internalOp > 0) H._internalOp--; }, 100);
            } catch(_e) {}
            // Respetar la INTENCIÓN: solo reproducir si el usuario/estado lo quería
            // (evita autoplay no deseado y el "pulsar play varias veces").
            H.isPlaying = !!H._karaokePlayIntent;
            H._kdbg('ready-set-isPlaying');
            window.__isPlaying = H.isPlaying;
            if (H._karaokePlayIntent) {
              // Alinear la voz al instrumental ANTES de arrancar y de nuevo tras
              // el play: son dos <audio> independientes; si arrancan desfasados
              // la voz se oye "descolocada" (más aún al 100% de volumen).
              try { H._audioVocals.currentTime = H._audioInst.currentTime; } catch(_e){}
              H._audioInst.play().catch(function(){});
              H._audioVocals.play().catch(function(){});
              setTimeout(function(){ try { if (H._audioInst && H._audioVocals && Math.abs(H._audioInst.currentTime - H._audioVocals.currentTime) > 0.04) H._audioVocals.currentTime = H._audioInst.currentTime; } catch(_e){} }, 180);
            }
            try { H._setPlayBtnUi(!!H._karaokePlayIntent); } catch(_e) {}
            H._audioInst.addEventListener('timeupdate', _karaokeTimeUpdate);
            H._audioInst.addEventListener('ended', _onKaraokeEnded);
            // Cargar letras sincronizadas WhisperX (nunca dejar ovh/plana en karaoke)
            try {
              var _songForLrc = (typeof H.currentPlaylistSongs !== 'undefined' && H.currentPlaylistSongs[H.currentSongIndex])
                ? H.currentPlaylistSongs[H.currentSongIndex] : null;
              var _songPathLrc = _songForLrc && _songForLrc.path;
              if (window.XimoKaraoke && typeof XimoKaraoke.loadKaraokeLyrics === 'function') {
                XimoKaraoke.loadKaraokeLyrics(karaokeKey, _songPathLrc).then(function(ok) {
                  if (_karaokeGen !== myGen) return;
                  if (ok) console.log('[Karaoke] Letras WhisperX cargadas');
                });
              } else {
                fetch('/api/ia/karaoke-file/' + karaokeKey + '/lyrics.lrc', { credentials: 'include' })
                  .then(function(r) { return r.ok ? r.text() : null; })
                  .then(function(lrcText) {
                    if (_karaokeGen !== myGen) return;
                    if (lrcText && typeof H.displayLyricsSynced === 'function') H.displayLyricsSynced(lrcText);
                    if (window.XimoKaraoke && typeof XimoKaraoke.loadWordsForKey === 'function') {
                      XimoKaraoke.loadWordsForKey(karaokeKey);
                    }
                  })
                  .catch(function(){});
              }
            } catch (_eLrc2) {}
            if (!H._audioInst._syncInterval) {
              H._audioInst._syncInterval = setInterval(function() {
                if (H._karaokeConnected && H._audioInst && H._audioVocals && !H._audioInst.paused) {
                  var t = H._audioInst.currentTime;
                  var vt = H._audioVocals.currentTime;
                  // Voz esclava del instrumental, umbral apretado (50ms) para que
                  // no se oiga desfase. El skew entre dos <audio> es lento
                  // (~1ms/s) → correcciones esporádicas, sin glitcheo audible.
                  if (Math.abs(t - vt) > 0.05) H._audioVocals.currentTime = t;
                }
              }, 400);
            }
          } catch(e) { console.warn('[Karaoke] Web Audio connect error:', e); }
        };
        
        if (H._audioInst.readyState >= 2 && H._audioVocals.readyState >= 2) { ready(); }
        else {
          var loadedCount = 0;
          var onLoad = function() {
            if (_karaokeGen !== myGen) return;  // llamada obsoleta
            loadedCount++;
            if (loadedCount >= 2) ready();
          };
          H._audioInst.addEventListener('canplay', onLoad, {once: true});
          H._audioVocals.addEventListener('canplay', onLoad, {once: true});
        }
      } catch(e) { console.warn('[Karaoke] init error:', e); }
    }

    function _disconnectKaraokeAudio() {
      _destroyKaraokeAudioElements();
    }

    function _syncKaraokeAudio() {
      if (!H._audioInst || !H._audioVocals || !H._karaokeConnected) return;
      var t = H._audioInst.currentTime;
      var vt = H._audioVocals.currentTime;
      if (Math.abs(t - vt) > 0.2) H._audioVocals.currentTime = t;
    }

    // Vocal fader CUSTOM vertical (div+drag). <input type=range> vertical
    // con writing-mode falla en Chromium/Tesla → se veía un thumb horizontal inútil.
    var vocalSlider = document.getElementById('ia-vocal-slider');
    var vocalPct = document.getElementById('ia-vocal-pct');
    var vocalTrack = document.getElementById('ia-vocal-track');
    var vocalWrap = document.getElementById('ia-vocal-slider-wrap');
    if (!vocalSlider || !vocalTrack) console.warn('[Karaoke] Fader VOZ incompleto en el DOM');

    function _currentKaraokeMeta() {
      var song = H.currentPlaylistSongs[H.currentSongIndex];
      var kp = (song && song.path || '').replace(/^\/api\/ia\/music-file\//, '');
      if (!kp || !H._karaokeMap || !H._karaokeMap[kp] || !H._karaokeMap[kp].has_karaoke) return null;
      return { path: kp, key: H._karaokeMap[kp].karaoke_key, song: song };
    }

    function _syncVoiceFaderVisibility() {
      var wrap = vocalWrap || document.getElementById('ia-vocal-slider-wrap');
      if (!wrap) return;
      var meta = _currentKaraokeMeta();
      // Visible en modo normal Y karaoke si la pista tiene stems.
      wrap.style.display = meta ? 'flex' : 'none';
      if (meta) _paintVocalFader();
    }
    window.__ximoSyncVoiceFader = _syncVoiceFaderVisibility;

    function _paintVocalFader() {
      if (!vocalSlider) return;
      var val = parseInt(vocalSlider.value);
      if (!isFinite(val)) val = 100;
      val = Math.max(0, Math.min(100, val));
      var ratio = val / 100;
      if (vocalWrap) vocalWrap.style.setProperty('--voz', String(ratio));
      if (vocalTrack) {
        vocalTrack.style.setProperty('--voz', String(ratio));
        vocalTrack.setAttribute('aria-valuenow', String(val));
      }
      if (vocalPct) vocalPct.textContent = val === 0 ? 'SIN VOZ' : (val + '%');
    }

    function _setVocalLevel(val, fromUser) {
      if (!vocalSlider) return;
      val = Math.max(0, Math.min(100, Math.round(val)));
      vocalSlider.value = String(val);
      _paintVocalFader();
      if (fromUser) {
        var wasConnected = H._karaokeConnected;
        _ensureVocalMixForSlider();
        if (!wasConnected && !_voiceFaderHintShown && typeof H.showToast === 'function') {
          _voiceFaderHintShown = true;
          H.showToast('VOZ: baja a 0% para cantar (el instrumental sigue)', 'info', 3500);
        }
      }
      _applyVocalSliderGain();
    }

    function _applyVocalSliderGain() {
      if (!vocalSlider) return;
      var val = parseInt(vocalSlider.value);
      if (!isFinite(val)) val = 100;
      val = Math.max(0, Math.min(100, val));
      _paintVocalFader();
      var g = val / 100;
      // Instrumental → H._masterGain (siempre). Voz → H._gainNode.
      if (H._audioCtx && H._audioCtx.state === 'suspended') {
        try { H._audioCtx.resume(); } catch (_e) {}
      }
      if (H._gainNode) {
        try { H._gainNode.gain.value = g; } catch (_e2) {}
      }
      if (H._audioVocals) {
        try { H._audioVocals.volume = g; } catch (_e3) {}
      }
    }

    function _ensureVocalMixForSlider() {
      // En modo normal el audio va por MSE (mezcla completa). Para poder bajar
      // SOLO la voz hay que pasar a stems (instrumental + vocals) sin exigir
      // la UI karaoke a pantalla completa.
      if (H._karaokeConnected && H._gainNode) { _applyVocalSliderGain(); return; }
      var meta = _currentKaraokeMeta();
      if (!meta) return;
      H._karaokePlayIntent = H.isPlaying;
      var _seg = (typeof H._mseCurSeg === 'function') ? H._mseCurSeg() : null;
      var ct = _seg ? _seg.pos : (H.audioEl ? H.audioEl.currentTime : 0);
      _connectKaraokeAudio(meta.key, ct);
    }

    var _voiceFaderHintShown = false;
    var _voiceDrag = false;
    function _vocalValFromClientY(clientY) {
      if (!vocalTrack) return 100;
      var rect = vocalTrack.getBoundingClientRect();
      if (!rect.height) return parseInt(vocalSlider && vocalSlider.value) || 100;
      // Arriba = 100%, abajo = 0%
      var ratio = 1 - ((clientY - rect.top) / rect.height);
      return Math.max(0, Math.min(100, ratio * 100));
    }
    function _onVocalPointerDown(e) {
      e.preventDefault();
      e.stopPropagation();
      _voiceDrag = true;
      try { vocalTrack.setPointerCapture(e.pointerId); } catch (_e) {}
      _setVocalLevel(_vocalValFromClientY(e.clientY), true);
    }
    function _onVocalPointerMove(e) {
      if (!_voiceDrag) return;
      e.preventDefault();
      _setVocalLevel(_vocalValFromClientY(e.clientY), true);
    }
    function _onVocalPointerUp(e) {
      if (!_voiceDrag) return;
      _voiceDrag = false;
      try { vocalTrack.releasePointerCapture(e.pointerId); } catch (_e) {}
    }
    if (vocalTrack) {
      vocalTrack.addEventListener('pointerdown', _onVocalPointerDown);
      vocalTrack.addEventListener('pointermove', _onVocalPointerMove);
      vocalTrack.addEventListener('pointerup', _onVocalPointerUp);
      vocalTrack.addEventListener('pointercancel', _onVocalPointerUp);
      vocalTrack.addEventListener('keydown', function(e) {
        var cur = parseInt(vocalSlider && vocalSlider.value) || 100;
        if (e.key === 'ArrowUp' || e.key === 'ArrowRight') { e.preventDefault(); _setVocalLevel(cur + 5, true); }
        else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') { e.preventDefault(); _setVocalLevel(cur - 5, true); }
        else if (e.key === 'Home') { e.preventDefault(); _setVocalLevel(100, true); }
        else if (e.key === 'End') { e.preventDefault(); _setVocalLevel(0, true); }
      });
    }
    _paintVocalFader();

    function _setKaraoke(on) {
      document.body.classList.toggle('ximo-karaoke', on);
      _syncVoiceFaderVisibility();
      // Al entrar en karaoke: VOZ al 80%. Al salir: vuelve al 100%.
      try {
        if (typeof _setVocalLevel === 'function') _setVocalLevel(on ? 80 : 100, false);
        else if (vocalSlider) {
          vocalSlider.value = on ? '80' : '100';
          if (typeof _applyVocalSliderGain === 'function') _applyVocalSliderGain();
          if (typeof _paintVocalFader === 'function') _paintVocalFader();
        }
      } catch(_vozE) {}
      
      if(karaokeBtn) {
        function _paintKaraokeBtn(active) {
          // Conservar icono Phosphor (no pisar con emoji textContent).
          karaokeBtn.classList.toggle('is-on', !!active);
          karaokeBtn.setAttribute('aria-pressed', active ? 'true' : 'false');
          // Limpiar estilos inline legacy por si quedaron de builds anteriores
          karaokeBtn.style.background = '';
          karaokeBtn.style.color = '';
          karaokeBtn.style.borderColor = '';
          karaokeBtn.style.boxShadow = '';
          if (!karaokeBtn.querySelector('i.ph')) {
            karaokeBtn.innerHTML = '<i class="ph ph-microphone-stage" aria-hidden="true"></i><span class="t-lbl"> KARAOKE</span>';
          }
        }
        if(on) {
          _paintKaraokeBtn(true);
          var currentSong = H.currentPlaylistSongs[H.currentSongIndex];
          var _kp = (currentSong && currentSong.path || '').replace(/^\/api\/ia\/music-file\//, '');
          if (_kp && H._karaokeMap && H._karaokeMap[_kp] && H._karaokeMap[_kp].has_karaoke) {
            var kKey = H._karaokeMap[_kp].karaoke_key;
            // Ya en stems (fader VOZ): no reconectar → evita salto de progreso.
            // PERO sí forzar LRC WhisperX: el fader no carga letra sync y la
            // caché ovh/plana deja la línea activa adelantada (bug 2026-07-31).
            if (H._karaokeConnected && H._audioInst) {
              H._kdbg('setKaraoke-ON-reuse-stems');
              H._karaokePlayIntent = H.isPlaying;
              try {
                if (window.XimoKaraoke && typeof XimoKaraoke.loadKaraokeLyrics === 'function') {
                  XimoKaraoke.loadKaraokeLyrics(kKey, currentSong && currentSong.path).then(function() {
                    try {
                      var _ct2 = H._audioInst ? (H._audioInst.currentTime || 0) : 0;
                      var _kd2 = (H._audioInst && H._audioInst.duration && isFinite(H._audioInst.duration)) ? H._audioInst.duration : 0;
                      if (typeof H.updateKaraoke === 'function') H.updateKaraoke(_ct2, _kd2);
                    } catch (_eKick) {}
                  });
                }
              } catch (_eLrc) {}
            } else {
              H._karaokePlayIntent = H.isPlaying;
              H._kdbg('setKaraoke-ON');
              H._karaokeHandoffLock = true;
              var _seg = (typeof H._mseCurSeg === 'function') ? H._mseCurSeg() : null;
              var ct = _seg ? _seg.pos : (H.audioEl ? H.audioEl.currentTime : 0);
              if (!isFinite(ct) || ct < 0) ct = 0;
              H._karaokeSavedTime = ct;
              _connectKaraokeAudio(kKey, ct);
              setTimeout(function(){ H._karaokeHandoffLock = false; }, 400);
            }
          } else {
            // M049: letras sí, stems no — avisar (guest o pista sin karaoke).
            try { H.showToast('Karaoke: letras OK · stems no disponibles', 'info', 2800); } catch (_eK) {}
          }
        } else {
          _paintKaraokeBtn(false);
          // HAND-OFF sin salto: 1) anclar MSE a la pos del stem 2) luego desconectar.
          var _wasPlaying = H.isPlaying;
          var _kpos = (H._audioInst && isFinite(H._audioInst.currentTime)) ? H._audioInst.currentTime
                    : (H._karaokeSavedTime || 0);
          H._karaokeHandoffLock = true;
          try {
            var _seg2 = (typeof H._mseCurSeg === 'function') ? H._mseCurSeg() : null;
            // Si MSE sigue en la misma canción, usar su start; si no, buscar por índice.
            var _mseStart = null;
            if (_seg2 && isFinite(_seg2.start)) _mseStart = _seg2.start;
            else if (H._getMse() && H._getMse().segs) {
              for (var _si = 0; _si < H._getMse().segs.length; _si++) {
                if (H._getMse().segs[_si].index === H.currentSongIndex) { _mseStart = H._getMse().segs[_si].start; break; }
              }
            }
            if (_mseStart != null && isFinite(_kpos)) {
              try { H.audioEl.currentTime = _mseStart + _kpos; } catch(_eSeek) {}
            }
          } catch(_e2) {}
          // Si el usuario solo quería UI karaoke (stems siguen vía fader), NO desconectar:
          // al salir de karaoke mantenemos stems solo si el fader VOZ < 100.
          var _keepStems = false;
          try {
            var _vv = vocalSlider ? parseInt(vocalSlider.value) : 100;
            _keepStems = isFinite(_vv) && _vv < 100;
          } catch(_eK) {}
          if (!_keepStems) {
            _disconnectKaraokeAudio();
            try { H.audioEl.volume = 1; } catch(_e) {}
            if (_wasPlaying) {
              H.isPlaying = true; window.__isPlaying = true;
              H.audioEl.play().catch(function(){});
              if('mediaSession' in navigator) try { navigator.mediaSession.playbackState = 'playing'; } catch(_e3){}
            }
          } else {
            // Stems siguen: UI normal pero voz atenuada
            H._karaokePlayIntent = _wasPlaying;
          }
          setTimeout(function(){ H._karaokeHandoffLock = false; try { if (typeof H.updateProgressUi === 'function') H.updateProgressUi(); } catch(_eU){} }, 350);
        }
      }
      try { if (window.XimoKaraoke) XimoKaraoke.setAutoScroll(on); } catch(_eAs) {}
      try { if (window.XimoKaraoke && XimoKaraoke.setKaraokeToolsVisible) XimoKaraoke.setKaraokeToolsVisible(on); } catch(_eTools) {}
      // Descubrir música no aplica en karaoke — cerrar panel si estaba abierto.
      try {
        if (window.XimoData && typeof window.XimoData.setExploreOpen === 'function') {
          window.XimoData.setExploreOpen(false);
        } else {
          document.body.classList.remove('explore-open');
          var _ep = document.getElementById('ia-explore-panel');
          if (_ep) _ep.style.display = 'none';
        }
      } catch(_eEx) {}
      // Tras cambiar layout (overlay fijo ↔ columnas), reiniciar viz + tick letra.
      // Sin esto la letra se congela mientras el audio sigue (bug reportado).
      function _kickKaraokeUi() {
        try { if(window.XimoViz) XimoViz.resize(); } catch(_e) {}
        try { if(typeof H.startStaticWaveAnim === 'function') H.startStaticWaveAnim(); } catch(_e2) {}
        try {
          var _ct = 0, _kd = 0;
          if (H._audioInst && (H._karaokeConnected || document.body.classList.contains('ximo-karaoke'))) {
            _ct = H._audioInst.currentTime || 0;
            _kd = (H._audioInst.duration && isFinite(H._audioInst.duration)) ? H._audioInst.duration : 0;
          } else if (H.audioEl) {
            _ct = H.audioEl.currentTime || 0;
            _kd = (H.audioEl.duration && isFinite(H.audioEl.duration)) ? H.audioEl.duration : 0;
          }
          if (typeof H.updateKaraoke === 'function') H.updateKaraoke(_ct, _kd);
          if (typeof H.updateProgressUi === 'function') H.updateProgressUi();
        } catch(_e3) {}
      }
      setTimeout(_kickKaraokeUi, 80);
      setTimeout(_kickKaraokeUi, 320);
      setTimeout(_kickKaraokeUi, 700);
      H.showToast(on ? 'Modo karaoke — letras grandes' : 'Modo normal', 'info', 2000);
    }
    if(karaokeBtn) {
      karaokeBtn.addEventListener('click', function() {
        var turningOn = !document.body.classList.contains('ximo-karaoke');
        // Guest: letras/play OK; stems/karaoke gated — avisar y ofrecer login.
        if (turningOn && typeof H.authUser !== 'undefined' && !H.authUser) {
          try {
            H.showToast('Karaoke completo requiere sesión — puedes oír música como invitado', 'info', 3500);
          } catch (_eT) {}
          try {
            if (typeof window.__ximoNudgeLogin === 'function') window.__ximoNudgeLogin('karaoke');
          } catch (_eN) {}
        }
        _setKaraoke(turningOn);
      });
    }
    // Exponer para que H.playSong/H.togglePlay (top-level) puedan reconectar/salir
    // del karaoke (estas funciones están anidadas aquí, en setupPlayer).
    H._karaokeReconnectFn = _connectKaraokeAudio;
    H._karaokeExitFn = _setKaraoke;
    H._karaokeDisconnectFn = _disconnectKaraokeAudio;
    _syncVoiceFaderVisibility();
    var karaokeExit = document.getElementById('ia-karaoke-exit');
    if(karaokeExit) karaokeExit.addEventListener('click', function(e) { e.stopPropagation(); _setKaraoke(false); });
    document.addEventListener('keydown', function(e) {
      if(e.key !== 'Escape') return;
      var tgt = e.target;
      if (tgt && (tgt.tagName === 'INPUT' || tgt.tagName === 'TEXTAREA' || tgt.tagName === 'SELECT' || tgt.isContentEditable)) return;
      // CantaZamos lobby/partida: no robar Escape
      if (document.body.classList.contains('ximo-game-active')) return;
      // Prompt flotante: lo cierra XimoPrompt
      if (document.body.classList.contains('prompt-open')) return;
      // Descubrir música flotante
      if (document.body.classList.contains('explore-open')) {
        e.preventDefault();
        try {
          if (window.XimoData && typeof window.XimoData.setExploreOpen === 'function') {
            window.XimoData.setExploreOpen(false);
          } else {
            document.body.classList.remove('explore-open');
            var _epEsc = document.getElementById('ia-explore-panel');
            if (_epEsc) _epEsc.style.display = 'none';
          }
        } catch (_eEscEx) {}
        return;
      }
      // Karaoke: Salir (prioridad sobre volver a listas)
      if (document.body.classList.contains('ximo-karaoke')) {
        e.preventDefault();
        _setKaraoke(false);
        return;
      }
      // ESC → vista playlists (home) si estamos en detalle/cola/fav/recientes.
      // Antes solo en desktop (pointer:fine) — el modo coche también puede
      // recibir ESC (teclado bluetooth, teclado físico en pruebas) y el
      // usuario pidió explícitamente que funcione en todos los interfaces
      // (2026-08-10), no solo con ratón.
      if (window.XimoPlaylist && typeof XimoPlaylist.getView === 'function' && typeof XimoPlaylist.showGrid === 'function') {
        var v = XimoPlaylist.getView();
        if (v && v !== 'grid') {
          e.preventDefault();
          XimoPlaylist.showGrid();
        }
      }
    });

    // ── Navegación por teclado en playlists/canciones (2026-08-10) ──
    // Las flechas mueven el FOCO (cursor visual) entre tarjetas de playlist o
    // filas de canción, sin reproducir nada — solo Enter/Espacio o un click
    // reproducen (mismo patrón que un explorador de ficheros). Antes las
    // flechas no hacían más que desplazar la barra de scroll del navegador
    // (comportamiento nativo, sin ningún elemento "seleccionado").
    // Un único listener a nivel de documento en vez de uno por tarjeta/fila:
    // con más de 1000 canciones, delegar así evita miles de listeners.
    document.addEventListener('keydown', function(e) {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp' && e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      var tgt = e.target;
      if (tgt && (tgt.tagName === 'INPUT' || tgt.tagName === 'TEXTAREA' || tgt.tagName === 'SELECT' || tgt.isContentEditable)) return;
      var active = document.activeElement;
      if (!active) return;
      var sel = active.classList && active.classList.contains('ia-pl-card') ? '.ia-pl-card'
        : (active.classList && active.classList.contains('ia-pl-song')) ? '.ia-pl-song' : null;
      if (!sel) return;
      var container = document.getElementById('ia-playlists-list');
      if (!container || !container.contains(active)) return;
      var items = container.querySelectorAll(sel);
      var idx = -1;
      for (var i = 0; i < items.length; i++) { if (items[i] === active) { idx = i; break; } }
      if (idx === -1) return;
      var target = null;
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        // Fila (izq/dcha): siguiente/anterior en orden DOM, tal cual venía leyéndose.
        var nextIdx = (e.key === 'ArrowRight') ? idx + 1 : idx - 1;
        if (nextIdx >= 0 && nextIdx < items.length) target = items[nextIdx];
      } else {
        // Arriba/abajo (2026-08-10): en una rejilla que envuelve (varias
        // tarjetas por fila), "siguiente en el DOM" es la de la DERECHA, no
        // la de ABAJO — el usuario lo pidió explícitamente. Bajar/subir debe
        // saltar de fila de verdad: coger las tarjetas de la fila
        // inmediatamente de arriba/abajo (por su `top`) y, dentro de esa
        // fila, la que quede horizontalmente más cerca de la actual.
        var curRect = active.getBoundingClientRect();
        var down = (e.key === 'ArrowDown');
        var bestRowTop = null;
        for (var r = 0; r < items.length; r++) {
          var rect = items[r].getBoundingClientRect();
          var isBelow = rect.top > curRect.top + 5;
          var isAbove = rect.top < curRect.top - 5;
          if (down ? !isBelow : !isAbove) continue;
          if (bestRowTop === null ||
              (down && rect.top < bestRowTop) ||
              (!down && rect.top > bestRowTop)) {
            bestRowTop = rect.top;
          }
        }
        if (bestRowTop !== null) {
          var bestDist = Infinity;
          for (var s = 0; s < items.length; s++) {
            var rect2 = items[s].getBoundingClientRect();
            if (Math.abs(rect2.top - bestRowTop) > 5) continue;
            var dist = Math.abs((rect2.left + rect2.width / 2) - (curRect.left + curRect.width / 2));
            if (dist < bestDist) { bestDist = dist; target = items[s]; }
          }
        }
      }
      if (!target) return; // en los bordes de la rejilla, no da la vuelta
      e.preventDefault();
      target.focus();
      target.scrollIntoView({ block: 'nearest' });
    });

    // ── Modo coche toggle ──
    // #101 — H._carMode() decide el enrutado de audio (nativo vs Web Audio) la
    // PRIMERA vez que se llama, y esa decisión queda cacheada para toda la
    // sesión (H._useNativeAudio). Restaurar la clase `ximo-car-mode` con un
    // setTimeout(500) dejaba una ventana en la que, si el usuario pulsaba play
    // casi al cargar (autoplay/tap rápido), H._carMode() se evaluaba en false y
    // toda la sesión quedaba enrutada por Web Audio pese a estar en modo coche
    // — el mismo patrón de bug que "primera reproducción" (#83/#84). La clase
    // se aplica ahora de forma SÍNCRONA en el arranque; solo el efecto visual
    // de expandir la playlist (que si necesita el DOM ya pintado) sigue diferido.
    var carBtn = document.getElementById('ia-car-btn');
    if(carBtn) {
      function _applyCarModeUI(isCar, opts) {
        opts = opts || {};
        if(isCar) {
          carBtn.classList.add('is-on');
          carBtn.setAttribute('aria-pressed', 'true');
          carBtn.style.background = '';
          carBtn.style.color = '';
          carBtn.style.borderColor = '';
          carBtn.style.boxShadow = '';
          // Label COCHE visible vía CSS (.is-on .t-lbl); no tocar display inline
          // En modo coche: cerrar prompt bar y explore si están abiertos
          try {
            if (window.XimoData && typeof window.XimoData.setExploreOpen === 'function') {
              window.XimoData.setExploreOpen(false);
            } else {
              document.body.classList.remove('explore-open');
              var explorePanel = document.getElementById('ia-explore-panel');
              if(explorePanel) explorePanel.style.display = 'none';
            }
          } catch(_eExClose) {}
          // Quitar alturas inline del modo normal (rompen el scroll flex en columna)
          if(typeof window._iaClearListHeight === 'function') window._iaClearListHeight();
          // Expandir automáticamente la playlist actual para que se vean las canciones
          setTimeout(function() { H.expandCurrentPlaylist(); }, 400);
        } else {
          carBtn.classList.remove('is-on');
          carBtn.setAttribute('aria-pressed', 'false');
          carBtn.style.background = '';
          carBtn.style.color = '';
          carBtn.style.borderColor = '';
          carBtn.style.boxShadow = '';
          // Restaurar altura calculada de la lista en modo normal
          if(typeof window._iaApplyListHeight === 'function') window._iaApplyListHeight();
        }
        H._purgeObsoletePicker();
        if(!opts.silent) H.showToast(isCar ? 'Modo coche — lista grande' : 'Modo normal', 'info', 2000);
        try {
          var _l = document.getElementById('ia-left');
          if(isCar) { if(window.__ximoRestoreCarFicha) window.__ximoRestoreCarFicha(); }
          else if(_l) { _l.style.flex = ''; _l.style.height = ''; }
        } catch(_e){}
        // Salir/entrar car cambia fixed↔flex: sin kick, canvas y letra se congelan.
        function _kickAfterCar() {
          try { if(window.XimoViz) XimoViz.resize(); } catch(_e) {}
          try { if(typeof H.startStaticWaveAnim === 'function') H.startStaticWaveAnim(); } catch(_e2) {}
          try {
            var _ct = 0, _kd = 0;
            if (H._audioInst && (H._karaokeConnected || document.body.classList.contains('ximo-karaoke'))) {
              _ct = H._audioInst.currentTime || 0;
              _kd = (H._audioInst.duration && isFinite(H._audioInst.duration)) ? H._audioInst.duration : 0;
            } else if (H.audioEl) {
              _ct = H.audioEl.currentTime || 0;
              _kd = (H.audioEl.duration && isFinite(H.audioEl.duration)) ? H.audioEl.duration : 0;
            }
            if (typeof H.updateKaraoke === 'function') H.updateKaraoke(_ct, _kd);
            if (typeof H.updateProgressUi === 'function') H.updateProgressUi();
          } catch(_e3) {}
        }
        setTimeout(_kickAfterCar, 80);
        setTimeout(_kickAfterCar, 350);
        setTimeout(_kickAfterCar, 700);
      }
      carBtn.addEventListener('click', function() {
        document.body.classList.toggle('ximo-car-mode');
        var isCar = document.body.classList.contains('ximo-car-mode');
        localStorage.setItem('ximo_car_mode', isCar ? '1' : '0');
        _applyCarModeUI(isCar);
      });
      // Restaurar modo coche: preferencia explícita, o auto solo en pantallas
      // coche-like (grande + táctil / ?tesla=1). Music-site en desktop con ratón
      // NO auto-activa (M024 — headless/desktop quedaba en car mode).
      var savedMode = localStorage.getItem('ximo_car_mode');
      function _autoCarLike() {
        var qs = location.search || '';
        if (/[?&]tesla=1\b/.test(qs)) return true;
        if (/[?&]tesla=0\b/.test(qs)) return false;
        var ua = navigator.userAgent || '';
        if (/Mobi|Android|iPhone|iPad|iPod/i.test(ua)) return false;
        if (/Tesla|QtCarBrowser/i.test(ua)) return true;
        if (!window.__musicSite) return false;
        var big = Math.max(screen.width || 0, screen.height || 0) >= 1400;
        var noHover = !(window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches);
        return !!(big && noHover);
      }
      if(savedMode === '1' || (savedMode === null && _autoCarLike())) {
        document.body.classList.add('ximo-car-mode');
        _applyCarModeUI(true, {silent: true});
      }
      // Label COCHE: CSS .topbar-mode-btn .t-lbl solo visible con .is-on
    }

    // Prompt flotante + Escape → window.XimoPrompt.setupToggle (Wave 4)

    // Buscar a una fracción [0..1] de la CANCIÓN actual. En M5 H.audioEl.currentTime
    // es la línea temporal continua (suma de pistas), así que hay que mapear al
    // segmento que suena; fuera de M5 es directo sobre la duración del elemento.
    function _seekToPct(pct) {
      pct = Math.max(0, Math.min(1, pct));
      window.XimoTransport.seekToFraction(pct);
      if (progressBar) progressBar.style.width = (pct*100) + '%';
      if (progressThumb) progressThumb.style.left = (pct*100) + '%';
    }
    function _pctFromEvent(e) {
      var rect = progressWrap.getBoundingClientRect();
      var x = (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX;
      return (x - rect.left) / rect.width;
    }
    if (progressWrap) {
      // Seek por PUNTERO: funciona con toque (Tesla) y ratón, tocar y arrastrar.
      var _dragging = false;
      var _onMove = function(e) { if (_dragging) { _seekToPct(_pctFromEvent(e)); if (e.cancelable) e.preventDefault(); } };
      var _onUp = function() { _dragging = false; };
      progressWrap.addEventListener('pointerdown', function(e) {
        _dragging = true;
        if (progressThumb) progressThumb.style.display = 'block';
        _seekToPct(_pctFromEvent(e));
        try { progressWrap.setPointerCapture(e.pointerId); } catch(_e) {}
      });
      progressWrap.addEventListener('pointermove', _onMove);
      progressWrap.addEventListener('pointerup', _onUp);
      progressWrap.addEventListener('pointercancel', _onUp);
      // Respaldo SOLO para navegadores sin Pointer Events. Antes se registraban
      // siempre (click+touchstart+touchmove) "por si el WebView del Tesla no los
      // soportaba bien" — pero el Tesla SÍ los soporta (Chromium reciente), así
      // que un solo arrastre disparaba pointerdown/pointermove Y ADEMÁS
      // touchstart/touchmove/click para el MISMO gesto: 2-3 seeks redundantes y
      // ligeramente distintos por toque, cada uno reposicionando audio/MSE por
      // su cuenta. Encaja con "al avanzar/retroceder dentro de la canción se
      // lía todo" (auditoría 2026-08-08). Registrar el respaldo solo si de
      // verdad hace falta.
      if (!window.PointerEvent) {
        progressWrap.addEventListener('click', function(e) { _seekToPct(_pctFromEvent(e)); });
        progressWrap.addEventListener('touchstart', function(e) { _seekToPct(_pctFromEvent(e)); }, {passive:true});
        progressWrap.addEventListener('touchmove', function(e) { _seekToPct(_pctFromEvent(e)); }, {passive:true});
      }
    }

    progressWrap.addEventListener('mouseenter', function() {
      if(progressThumb) progressThumb.style.display = 'block';
    });
    progressWrap.addEventListener('mouseleave', function() {
      if(progressThumb) progressThumb.style.display = 'none';
    });
  }

  return { setup: setup };
})();
