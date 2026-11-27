#!/usr/bin/env node
/* 确定性自检：同一时刻 t，“新开页面直接跳到 t” 与 “从 0 顺序播到 t” 必须画出同一帧。
 * 分段并行渲染、浏览器里拖进度条都依赖这一点。  node test_stateless.js [t1,t2,...] */
'use strict';
const { chromium } = require('playwright');
const path = require('path');
const URL = 'file://' + path.join(__dirname, 'index.html') + '?render';
const times = (process.argv[2] || '4.6,13.5,30,45,53,60,66,73,80,86').split(',').map(Number);

async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(URL);
  await p.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });
  return p;
}
function diff(a, b) { // 两张 PNG 的字节级差异比例（同尺寸 PNG 解码后比较更准，这里用截图 raw 比较）
  let n = 0; const L = Math.min(a.length, b.length);
  for (let i = 0; i < L; i++) if (a[i] !== b[i]) n++;
  return n / L;
}
(async () => {
  const browser = await chromium.launch();
  const seq = await page(browser);
  let bad = 0, prev = 0;
  for (const t of times) {
    for (let x = prev; x < t; x += 0.1) await seq.evaluate(x => render(x), x);   // 顺序播到 t 附近
    prev = t;
    await seq.evaluate(t => render(t), t);
    const A = await seq.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    const fresh = await page(browser);
    await fresh.evaluate(t => render(t), t);
    const B = await fresh.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    await fresh.close();
    const d = A.equals(B) ? 0 : diff(A, B);
    console.log(`t=${t.toFixed(2)}  ${d === 0 ? 'identical' : 'DIFF ' + (d * 100).toFixed(2) + '%'}`);
    if (d > 0) { bad++; require('fs').writeFileSync(`build/diff_seq_${t}.png`, A); require('fs').writeFileSync(`build/diff_fresh_${t}.png`, B); }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
