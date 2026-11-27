#!/usr/bin/env node
/* 逐帧渲染：Playwright 打开 index.html?render，逐帧调用 render(t) 并截图，经管道送进 ffmpeg。
 *
 *   node render.js stills 1.2,5.5,9 [--scale 0.5]      静帧 -> build/stills/
 *   node render.js video build/silent.mp4 [--fps 60] [--workers 3] [--from 0 --to 92]
 */
'use strict';
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const URL = 'file://' + path.join(__dirname, 'index.html') + '?render';

async function openPage() {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('[page error]', e.message));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[console]', m.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });
  return { browser, page };
}

async function stills() {
  const times = args[1].split(',').map(Number);
  const dir = path.join(__dirname, 'build', 'stills');
  fs.mkdirSync(dir, { recursive: true });
  const { browser, page } = await openPage();
  for (const t of times) {
    // 先渲染前一帧，让依赖“上一帧”的东西（没有）也保持一致；再渲染目标帧
    await page.evaluate(t => render(t), t);
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => r())));
    const f = path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.png`);
    await page.screenshot({ path: f });
    console.log(f);
  }
  await browser.close();
}

async function worker(out, f0, f1, fps) {
  const { browser, page } = await openPage();
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(fps),
    '-x264-params', 'keyint=' + fps * 2 + ':min-keyint=' + fps, out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = f0; i < f1; i++) {
    await page.evaluate(t => render(t), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - f0) % 120 === 0) console.log(`[${path.basename(out)}] frame ${i}/${f1} (${((Date.now() - t0) / Math.max(1, i - f0)).toFixed(0)} ms/f)`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
}

async function video() {
  const out = path.resolve(args[1] || 'build/silent.mp4');
  const fps = +opt('fps', 60), workers = +opt('workers', 3);
  const T = await (async () => { const { browser, page } = await openPage(); const T = await page.evaluate(() => FILM.T); await browser.close(); return T; })();
  const from = +opt('from', 0), to = +opt('to', T);
  const F0 = Math.round(from * fps), F1 = Math.round(to * fps);
  if (process.env.WORKER) {   // 子进程：渲染一段
    const [a, b] = process.env.WORKER.split(':').map(Number);
    await worker(out, a, b, fps);
    return;
  }
  const dir = path.join(path.dirname(out), 'parts'); fs.mkdirSync(dir, { recursive: true });
  const n = Math.max(1, workers), per = Math.ceil((F1 - F0) / n);
  const parts = [];
  const jobs = [];
  for (let k = 0; k < n; k++) {
    const a = F0 + k * per, b = Math.min(F1, a + per);
    if (a >= b) break;
    const p = path.join(dir, `part${k}.mp4`); parts.push(p);
    jobs.push(new Promise((res, rej) => {
      const cp = spawn(process.execPath, [__filename, 'video', p, '--fps', String(fps)], { env: { ...process.env, WORKER: `${a}:${b}` }, stdio: 'inherit' });
      cp.on('close', c => (c === 0 ? res() : rej(new Error('worker ' + k + ' failed'))));
    }));
  }
  const t0 = Date.now();
  await Promise.all(jobs);
  const list = path.join(dir, 'list.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
  await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out], { stdio: 'inherit' })
    .on('close', c => (c === 0 ? res() : rej(new Error('concat failed')))));
  console.log(`done ${out} in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}

/* 音效卡点：在页面里按 60fps 快速“空跑”一遍时间轴，记录每个带 data-sfx 的元素第一次出现的时刻、
 * 打字时每多一个字、年份里程表每次跳字，连同章节/转场等结构时间一起写进 build/cues.json */
async function cues() {
  const { browser, page } = await openPage();
  const res = await page.evaluate(() => {
    const out = [], seen = new Set(), lens = new Map();
    let lastOdo = null;
    const els = [...document.querySelectorAll('[data-sfx]')];
    const N = Math.round(FILM.T * 60);
    for (let i = 0; i <= N; i++) {
      const t = i / 60; render(t);
      for (const el of els) {
        const kind = el.dataset.sfx, sc = el.closest('.scene');
        if (sc && sc.style.display !== 'block') continue;
        if (kind === 'type') { const n = el.textContent.length, q = lens.get(el) || 0; if (n > q) out.push([+t.toFixed(4), 'type']); lens.set(el, n); continue; }
        if (seen.has(el) || el.style.opacity === '') continue;
        if (parseFloat(el.style.opacity) > 0.08) { seen.add(el); out.push([+t.toFixed(4), kind]); }
      }
      const odo = document.getElementById('odo');
      if (odo && odo.style.display !== 'none') {
        const d = [...odo.querySelectorAll('.odo-col')].map(c => c.children[0].textContent).join('');
        if (lastOdo !== null && d !== lastOdo) out.push([+t.toFixed(4), 'tick']);
        lastOdo = d;
      } else lastOdo = null;
    }
    return { events: out, map: cueMap() };
  });
  fs.mkdirSync(path.join(__dirname, 'build'), { recursive: true });
  fs.writeFileSync(path.join(__dirname, 'build', 'cues.json'), JSON.stringify(res, null, 1));
  const kinds = {}; res.events.forEach(e => (kinds[e[1]] = (kinds[e[1]] || 0) + 1));
  console.log('cues:', res.events.length, kinds);
  await browser.close();
}

({ stills, cues, video }[args[0]] || video)().catch(e => { console.error(e); process.exit(1); });
