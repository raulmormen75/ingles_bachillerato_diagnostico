/* Static Heart recordings. No browser speech engine or paid API is used. */
(() => {
  'use strict';
  const base = new URL('../', document.currentScript.src);
  const normalize = text => String(text).replace(/[\u200D\uFE0E\uFE0F]/g, '').replace(/(?:\p{Extended_Pictographic}|\p{Regional_Indicator}|\u20E3)/gu, ' ').replace(/\s+/g, ' ').trim();
  const clips = new Map((window.IFR_HEART_MANIFEST?.clips || []).map(c => [normalize(c.text), c]));
  const audio = document.createElement('audio');
  audio.id = 'heartAudio'; audio.preload = 'none';
  document.body.append(audio);
  const panel = document.createElement('div');
  panel.id = 'heartStatusPanel'; panel.hidden = true;
  panel.innerHTML = '<span id="heartStatus" role="status" aria-live="polite"></span><button type="button" id="heartStop">Detener</button>';
  document.body.append(panel);
  const status = panel.querySelector('span'), stopButton = panel.querySelector('button');
  let active = null, request = 0;
  function resetButton() {
    if (!active) return;
    active.classList.remove('speaking', 'error');
    active.removeAttribute('aria-busy'); active.setAttribute('aria-pressed', 'false');
    active = null;
  }
  function stop() {
    request++; audio.pause();
    try { audio.currentTime = 0; } catch (_) { /* No source loaded yet. */ }
    resetButton(); panel.hidden = true;
    audio.removeAttribute('src'); audio.load();
  }
  function fail(message = 'No se pudo reproducir. Toca el botón de audio para intentar de nuevo.') {
    if (!active) return;
    active.classList.remove('speaking'); active.classList.add('error');
    active.removeAttribute('aria-busy'); active.setAttribute('aria-pressed', 'false');
    status.textContent = message;
    stopButton.textContent = 'Cerrar'; panel.hidden = false;
  }
  function play(text, rate, button) {
    if (active === button && !audio.paused) { stop(); return; }
    stop(); const token = request;
    active = button; panel.hidden = false; stopButton.textContent = 'Detener';
    status.textContent = 'Cargando audio de Heart…';
    button.setAttribute('aria-busy', 'true');
    const clip = clips.get(normalize(text));
    if (!clip) { fail('No se encontró este audio. Recarga la página e intenta de nuevo.'); return; }
    audio.src = new URL(clip.file + '?v=' + clip.sha256.slice(0, 16), base).href;
    audio.playbackRate = [1, .8, .75, .5].includes(Number(rate)) ? Number(rate) : 1;
    audio.preservesPitch = true; audio.webkitPreservesPitch = true;
    window.IFR_SELECTED_VOICE = 'Heart | af_heart | en-US';
    const promise = audio.play();
    if (promise) promise.catch(() => { if (token === request) fail(); });
  }
  audio.addEventListener('playing', () => {
    if (!active || audio.paused) return;
    active.classList.add('speaking'); active.classList.remove('error');
    active.removeAttribute('aria-busy'); active.setAttribute('aria-pressed', 'true');
    status.textContent = 'Heart · Voz sintética en inglés';
  });
  audio.addEventListener('waiting', () => {
    if (!active || audio.paused) return;
    active.classList.remove('speaking'); active.setAttribute('aria-busy', 'true');
    status.textContent = 'Cargando audio de Heart…';
  });
  audio.addEventListener('pause', () => { if (active && audio.paused) { active.classList.remove('speaking'); active.setAttribute('aria-pressed', 'false'); } });
  audio.addEventListener('ended', () => { if (audio.ended) stop(); });
  audio.addEventListener('error', () => { if (audio.getAttribute('src') && audio.error) fail(); });
  stopButton.addEventListener('click', stop);
  window.addEventListener('pagehide', stop);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  window.IFRHeart = { play, stop, normalize };

  // Exclusions are explicit: spelling exercises, letter sequences and isolated letter contrasts.
  const excluded = [
    '#topic-2-2-4',
    '#ejercicio-6','#ejercicio-9','#ejercicio-16','#ejercicio-17','#ejercicio-18','#ejercicio-19','#ejercicio-20'
  ];
  // Exercise indices use their own list, since separator elements may share the parent.
  document.querySelectorAll('#topic-2-2-8 .exercise-item').forEach((e,i) => { if ([0,1,2,3,4,6].includes(i)) e.dataset.noAudio = 'spelling'; });
  document.querySelectorAll('#topic-3-3-8 .exercise-item')[3]?.setAttribute('data-no-audio', 'letters');
  excluded.forEach(selector => document.querySelectorAll(selector).forEach(e => e.dataset.noAudio = 'spelling'));

  const jobs = new Set();
  document.querySelectorAll('.audio-btn').forEach(button => {
    let text = button.dataset.speechText;
    let rate = button.dataset.audioRate || button.dataset.rate;
    const inline = button.getAttribute('onclick');
    if (!text && inline) {
      const match = inline.match(/^speakText\(("(?:\\.|[^"\\])*"),\s*([\d.]+)/);
      if (match) { text = JSON.parse(match[1]); rate = match[2]; }
    }
    if (!text) text = button.closest('.en-line')?.querySelector('.en-text')?.textContent;
    const clean = normalize(text || '');
    const letterSequence = /\b[A-Za-z](?:\s*[-,]\s*[A-Za-z]){1,}\b/.test(clean);
    const letterContrast = /\b[B-Z] and [A-Z]\b|\bA and E\b/.test(clean);
    if (button.closest('[data-no-audio]') || letterSequence || letterContrast || !clean) {
      button.remove(); return;
    }
    button.removeAttribute('onclick'); button.dataset.heartText = clean;
    button.dataset.heartRate = String(Number(rate) || 1);
    button.title = 'Escuchar con Heart, voz sintética en inglés';
    button.setAttribute('aria-pressed', 'false');
    jobs.add(clean);
  });
  document.querySelectorAll('.audio-controls').forEach(group => { if (!group.querySelector('button')) group.remove(); });
  document.addEventListener('click', event => {
    const button = event.target.closest('.audio-btn[data-heart-text]');
    if (!button) return;
    event.preventDefault(); event.stopImmediatePropagation();
    play(button.dataset.heartText, button.dataset.heartRate, button);
  }, true);
  window.IFR_HEART_TEXTS = [...jobs];
})();
