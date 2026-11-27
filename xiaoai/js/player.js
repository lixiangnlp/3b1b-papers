/* 浏览器播放器：自适应缩放、播放/暂停、拖动进度、配乐同步。
 * 渲染模式（URL 带 ?render）下什么都不做，由 render.js 逐帧调用 render(t)。 */
'use strict';
(function () {
  const stage = $('stage');
  const isRender = /[?&]render/.test(location.search);
  window.__stageScale = 1;
  if (isRender) { document.body.classList.add('render'); return; }
  const CTL = 46;
  function fit() {
    const s = Math.min(innerWidth / W, (innerHeight - CTL) / H);
    stage.style.transform = `translate(${(innerWidth - W * s) / 2}px,${(innerHeight - CTL - H * s) / 2}px) scale(${s})`;
    window.__stageScale = s;
  }
  fit(); addEventListener('resize', fit);
  const music = $('music'), btn = $('play'), scrub = $('scrub'), tc = $('tc');
  let playing = false, cur = 0, t0 = 0, base = 0;
  const hasMusic = () => music && music.readyState >= 2 && !music.error;
  function play() {
    if (cur >= FILM.T - 0.05) cur = 0;
    playing = true; base = cur; t0 = performance.now();
    if (hasMusic()) { music.currentTime = cur; music.play().catch(() => {}); }
    btn.textContent = '❚❚ 暂停';
  }
  function pause() { playing = false; if (music) music.pause(); btn.textContent = '▶ 播放'; }
  function seek(t) { cur = clamp(t, 0, FILM.T); base = cur; t0 = performance.now(); if (hasMusic()) music.currentTime = cur; }
  btn.onclick = () => (playing ? pause() : play());
  scrub.oninput = () => seek(scrub.value / 1000 * FILM.T);
  addEventListener('keydown', e => {
    if (e.code === 'Space') { e.preventDefault(); playing ? pause() : play(); }
    if (e.code === 'ArrowRight') seek(cur + 1);
    if (e.code === 'ArrowLeft') seek(cur - 1);
  });
  function tick(now) {
    if (playing) {
      cur = base + (now - t0) / 1000;
      // 以音乐时钟为准，避免音画漂移
      if (hasMusic() && !music.paused && Math.abs(music.currentTime - cur) > 0.08) cur = music.currentTime;
      if (cur >= FILM.T) { cur = FILM.T; pause(); }
    }
    if (window.__ready) render(cur);
    tc.textContent = cur.toFixed(2) + ' / ' + FILM.T.toFixed(0) + 's';
    if (document.activeElement !== scrub) scrub.value = Math.round(cur / FILM.T * 1000);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  const q = location.hash.match(/t=([\d.]+)/);
  if (q) cur = +q[1];
})();
