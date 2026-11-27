/* 小爱同学 · 九年 —— 分镜与渲染
 * render(t) 是唯一入口：给定时间 t（秒），把整幅画面设置到该时刻的状态。
 */
'use strict';

const FILM = { T: 88.6 };
const bg = ctx2d('bg'), fx = ctx2d('fx'), topc = ctx2d('top');
const SC = $('scenes'), HUD = $('hud');

/* ============================================================
 * 时间表
 * ============================================================ */
const TL = {
  wakeA: 0, wakeB: 4.3,
  logoA: 3.4, logoB: 10.4,
  flood: [5.45, 6.55],        // 开场：光从 logo 中心铺满画面（暗 → 亮）
};
// 章节（年份）——文案在 CH_TEXT 里，视觉在 VIS 里
// 音乐：112.5 BPM，一小节 = 2.1333 秒；从第一章开始，每章 3 小节（2023 为 4 小节），章节切换都落在强拍上
const BAR = 60 / 112.5 * 4, T0 = 9.6;
const bars = n => +(T0 + n * BAR).toFixed(4);
const CHAPTERS = [
  { key: 'speaker', y: 2017, a: bars(0), b: bars(3) },
  { key: 'phone', y: 2018, a: bars(3), b: bars(6) },
  { key: 'chat', y: 2019, a: bars(6), b: bars(9) },
  { key: 'home', y: 2020, a: bars(9), b: bars(12) },
  { key: 'mau', y: 2021, a: bars(12), b: bars(15) },
  { key: 'llm', y: 2023, a: bars(15), b: bars(19), dark: true },
  { key: 'car', y: 2024, a: bars(19), b: bars(22), dark: true },
  { key: 'super', y: 2024, a: bars(22), b: bars(25), dark: true },
  { key: 'glasses', y: 2025, a: bars(25), b: bars(28), dark: true },
  { key: 'agent', y: 2026, a: bars(28), b: bars(31) },
];
CHAPTERS.forEach(c => (c.id = 'c-' + c.key));
const YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];
const FIN = { a: bars(31), b: bars(31) + 12.8 };

/* ============================================================
 * 文案（事实以调研结果为准，见 README 的资料来源）
 * ============================================================ */
const CH_TEXT = {
  speaker: { kicker: '07 · 26　小米AI音箱发布', hl: ['一台音箱，', '一个名字。'], sub: '小米AI音箱发布，内置人工智能语音助手<b>「小爱同学」</b>。',
    chips: ['<span class="dot" style="background:#FF6CA3"></span>首发价 ¥299', '<span class="dot" style="background:#FCCD01"></span>1 元公测「领养」', '<span class="dot" style="background:#0A8EF8"></span>开售 23 秒售罄'] },
  phone: { kicker: '03 · 27　小米 MIX 2S', hl: ['从客厅，', '到口袋。'], sub: '小米 MIX 2S 内置小爱同学，它走进了手机。',
    chips: ['<span class="dot" style="background:#0A8EF8"></span>年底激活设备破 1 亿', '<span class="dot" style="background:#11E6AD"></span>月活 3880 万'] },
  chat: { kicker: '11 · 19　小爱同学 3.0', hl: ['不用每句，', '都叫它名字。'], sub: '全双工自然连续对话，还第一次有了<b>男声</b>。',
    chips: ['<span class="dot" style="background:#FF6CA3"></span>全双工连续对话', '<span class="dot" style="background:#11E6AD"></span>月活 6040 万'] },
  home: { kicker: '11 · 05　小爱同学 5.0', hl: ['一句话，', '整个家都听懂。'], sub: '从语音助手，升级为<b>智能生活助手</b>。',
    chips: ['<span class="dot" style="background:#0A8EF8"></span>激活设备 2.28 亿', '<span class="dot" style="background:#FF957B"></span>累计唤醒 617 亿次'] },
  mau: { kicker: '06　月活破亿', hl: ['每个月，', '一亿人和它说话。'], sub: '2021 年 6 月，月活跃用户<b>首次突破 1 亿</b>。', chips: [] },
  llm: { kicker: '08 · 14　雷军年度演讲', hl: ['然后，', '它开始思考。'], sub: '小米自研大模型 MiLM 亮相，<b>大模型版小爱</b>开启邀测。',
    chips: ['<span class="dot" style="background:#FF6CA3"></span>MiLM-6B · 64 亿参数', '<span class="dot" style="background:#11E6AD"></span>10 · 26 澎湃OS 发布'] },
  car: { kicker: '03 · 28　小米 SU7 上市', hl: ['从家里，', '到路上。'], sub: '车载小爱首发即接入<b>端侧大模型</b>。',
    chips: ['<span class="dot" style="background:#0A8EF8"></span>MiLM-1.3B 端侧大模型', '<span class="dot" style="background:#FF957B"></span>五音区语音'] },
  super: { kicker: '10 · 29　更名「超级小爱」', hl: ['从能听能说，', '到能想能干。'], sub: '随小米 15 与澎湃OS 2 发布，换上新名字。',
    chips: ['<span class="dot" style="background:#11E6AD"></span>07 · 21 大模型全量升级', '<span class="dot" style="background:#FF6CA3"></span>12 · 27 正式版开放'] },
  glasses: { kicker: '06 · 26　小米 AI 眼镜', hl: ['看你所看，', '想你所想。'], sub: '小米首款 AI 眼镜，由<b>超级小爱</b>驱动。',
    chips: ['<span class="dot" style="background:#0A8EF8"></span>04 · 30 MiMo 推理模型开源', '<span class="dot" style="background:#11E6AD"></span>08 · 28 圈屏 · 一步直达'] },
  agent: { kicker: '08 · 13　超级小爱 2.0', hl: ['说一句，', '它就办好了。'], sub: '接入 MiMo 大模型，能<b>跨应用、跨设备</b>执行任务。',
    chips: ['<span class="dot" style="background:#0A8EF8"></span>可调用 260+ 系统工具', '<span class="dot" style="background:#FF6CA3"></span>月活 1.759 亿'] },
};

/* ============================================================
 * 背景：底色 + 漂浮色斑 + 明暗转场（圆形扩散）+ 颗粒
 * ============================================================ */
const BG_TRANS = [   // 明暗转场：在 [a,b] 内，一个 to 色的圆从 (x,y) 扩散到铺满
  { a: TL.flood[0], b: TL.flood[1], to: 'light', x: 960, y: 430 },
  { a: bars(15) - 0.15, b: bars(15) + 1.0, to: 'dark', x: 1350, y: 500 },
  { a: bars(28) - 0.15, b: bars(28) + 0.95, to: 'light', x: 1410, y: 510 },
];
function darkness(t) { // 连续的明暗值，给 HUD 等跟随
  let d = darkAt(t);
  for (const tr of BG_TRANS) if (t >= tr.a && t < tr.b) { const k = E.ioC(seg(t, tr.a, tr.b)); d = tr.to === 'light' ? 1 - k : k; }
  return d;
}
function darkAt(t) { // 0 亮 / 1 暗（转场完成后的基础状态）
  let d = 1;
  for (const tr of BG_TRANS) if (t >= tr.b) d = tr.to === 'light' ? 0 : 1;
  return d;
}
const grainCv = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d'), im = x.createImageData(256, 256);
  for (let i = 0; i < 256 * 256; i++) { const v = (rnd(i * 0.7317 + 0.11) * 255) | 0; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
  x.putImageData(im, 0, 0); return c;
})();
const PAPER = '#F6F6F3', NIGHT = '#05060B';
function fillMode(ctx, mode) { ctx.fillStyle = mode === 'light' ? PAPER : NIGHT; ctx.fillRect(0, 0, W, H); }
function blobs(ctx, t, mode, focus, amt = 1) {
  const cols = [C.pink, C.blue, C.mint, C.coral];
  const dark = mode === 'dark';
  ctx.save();
  if (dark) ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 4; i++) {
    const a = t * 0.16 + i * 1.62;
    const x = focus[0] + Math.cos(a) * (230 + 60 * i) + noise1(t * 0.2, i) * 60;
    const y = focus[1] + Math.sin(a * 1.3) * (150 + 30 * i);
    const r = (dark ? 420 : 560) + 90 * Math.sin(t * 0.37 + i);
    const al = (dark ? 0.13 : 0.11) * amt * (i === 3 ? 0.7 : 1);
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(cols[i], al)); g.addColorStop(1, rgba(cols[i], 0));
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
  }
  ctx.restore();
}
let BG_FOCUS = [1340, 520], BG_AMT = 1;
function drawBG(t) {
  const ctx = bg;
  let mode = darkAt(t) ? 'dark' : 'light';
  fillMode(ctx, mode);
  blobs(ctx, t, mode, BG_FOCUS, BG_AMT);
  for (const tr of BG_TRANS) {
    if (t < tr.a || t >= tr.b) continue;
    const k = E.ioC(seg(t, tr.a, tr.b));
    const R = k * 2400;
    ctx.save();
    const col = tr.to === 'light' ? PAPER : NIGHT;
    const g = ctx.createRadialGradient(tr.x, tr.y, Math.max(0, R - Math.min(260, R * 0.45)), tr.x, tr.y, R + 1);
    g.addColorStop(0, col); g.addColorStop(1, tr.to === 'light' ? 'rgba(246,246,243,0)' : 'rgba(5,6,11,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // 光圈前沿的一道亮边
    if (tr.to === 'light') {
      ctx.globalCompositeOperation = 'lighter';
      const g2 = ctx.createRadialGradient(tr.x, tr.y, Math.max(0, R - 60), tr.x, tr.y, R + 160);
      const a = 0.5 * (1 - k);
      g2.addColorStop(0, 'rgba(255,108,163,0)'); g2.addColorStop(0.25, `rgba(255,108,163,${a * 0.6})`); g2.addColorStop(0.5, `rgba(10,142,248,${a * 0.7})`);
      g2.addColorStop(0.75, `rgba(17,230,173,${a * 0.5})`); g2.addColorStop(1, 'rgba(17,230,173,0)');
      ctx.fillStyle = g2; ctx.fillRect(0, 0, W, H);
    }
    ctx.restore();
  }
  // 暗场：暗角 + 颗粒（也用来抑制暗部渐变的色带）
  const dk = darkAt(t);
  const vig = darkness(t);
  if (vig > 0.001) {
    const v = ctx.createRadialGradient(960, 540, 300, 960, 540, 1150);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${0.55 * vig})`);
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  }
  ctx.save();
  ctx.globalAlpha = vig > 0.5 ? 0.06 : 0.035;
  ctx.globalCompositeOperation = vig > 0.5 ? 'screen' : 'multiply';
  const fr = Math.floor(t * 30);
  const ox = Math.floor(rnd(fr) * 256), oy = Math.floor(rnd(fr + 7.7) * 256);
  for (let x = -ox; x < W; x += 256) for (let y = -oy; y < H; y += 256) ctx.drawImage(grainCv, x, y);
  ctx.restore();
}

/* ============================================================
 * HUD：左上角 logo + 品牌、年份里程表、底部时间轴
 * ============================================================ */
let HUDLOGO, ODO;
function buildHUD() {
  HUD.innerHTML = `
    <div id="hud-brand"><span style="width:44px;height:40px;display:inline-block"></span><span>小爱同学</span><span class="sep"></span><span class="light">2017 — 2026</span></div>
    <div id="odo" class="abs odo" style="left:128px;top:178px"></div>
    <div id="tl"><div class="base"></div><div class="fill"></div>${YEARS.map((y, i) => `<div class="tick" style="left:${i * 180}px"></div><div class="lab" style="left:${i * 180}px">${y}</div>`).join('')}<div class="head"></div></div>`;
  ODO = new Odometer($('odo'), 4);
  HUDLOGO = makeLogo(HUD, { height: 380, glow: true });
}
function yearValue(t) {
  // 每章开头 0.95 秒内滚到新年份
  let v = CHAPTERS[0].y;
  for (let i = 1; i < CHAPTERS.length; i++) {
    const c = CHAPTERS[i];
    const k = E.ioC(seg(t, c.a - 0.25, c.a + 0.7));
    if (k > 0) v = CHAPTERS[i - 1].y + k * (c.y - CHAPTERS[i - 1].y);
  }
  return v;
}
function renderHUD(t) {
  const dkc = darkness(t), dk = dkc > 0.5 ? 1 : 0;
  const ink = mixHex('#0D0E12', '#F2F3F5', dkc);
  // --- 品牌行：logo 从画面中央“停靠”到左上角
  const brand = $('hud-brand');
  brand.style.color = ink;
  const dockA = 8.7, dockB = 9.75;
  const kd = E.ioQ4(seg(t, dockA, dockB));
  const txtK = E.outQ4(seg(t, dockB - 0.2, dockB + 0.4));
  brand.style.opacity = txtK;
  brand.style.transform = `translateX(${(1 - txtK) * -14}px)`;
  const finK = E.ioC(seg(t, FIN.a + 0.2, FIN.a + 1.0)); // 结尾时品牌行退场
  if (finK > 0) brand.style.opacity = txtK * (1 - finK);
  // --- 年份里程表
  const odoEl = $('odo');
  const c0 = CHAPTERS[0];
  const inK = seg(t, c0.a - 0.1, c0.a + 1.1);
  const outK = E.inC(seg(t, FIN.a - 0.2, FIN.a + 0.4));
  if (t < c0.a - 0.1 || outK >= 1) { odoEl.style.display = 'none'; }
  else {
    odoEl.style.display = '';
    const v = yearValue(t);
    const sp = Math.abs(yearValue(t + 1 / 60) - v) * 60;
    if (inK < 1) {
      // 第一次出现：四位数字依次从下方转上来
      const cols = ODO.cols.length;
      for (let i = 0; i < cols; i++) {
        const ki = E.outQ4(seg(t, c0.a - 0.1 + i * 0.09, c0.a + 0.75 + i * 0.09));
        const d = String(c0.y)[i] * 1;
        const vv = d - (1 - ki) * (6 + i * 2);
        const col = ODO.cols[i], A = col.children[0], B = col.children[1];
        const base = Math.floor(vv), f = vv - base;
        A.textContent = ((base % 10) + 10) % 10; B.textContent = ((base + 1) % 10 + 10) % 10;
        A.style.transform = `translateY(${-f * 100}%)`; B.style.transform = `translateY(${100 - f * 100}%)`;
        const bl = ki < 0.98 ? Math.min(5, (1 - ki) * 9) : 0;
        A.style.filter = B.style.filter = bl > 0.05 ? `blur(${bl.toFixed(2)}px)` : 'none';
      }
      odoEl.style.opacity = clamp(inK * 3);
    } else {
      ODO.set(v, sp);
      odoEl.style.opacity = 1 - outK;
    }
    odoEl.style.filter = outK > 0 ? `blur(${outK * 14}px)` : 'none';
    odoEl.style.color = ink;
  }
  // --- 时间轴
  const tl = $('tl');
  const tlIn = E.outQ4(seg(t, c0.a + 0.3, c0.a + 1.1));
  const tlOut = E.inC(seg(t, FIN.a + 0.3, FIN.a + 0.9));
  tl.style.opacity = tlIn * (1 - tlOut);
  tl.style.transform = `translateY(${(1 - tlIn) * 16}px)`;
  const pos = (yearValue(t) - 2017) * 180;
  const fill = tl.querySelector('.fill'), head = tl.querySelector('.head');
  const grow = E.outQ4(seg(t, c0.a + 0.3, c0.a + 1.4));
  fill.style.width = (pos * grow + 0.0001) + 'px';
  head.style.left = (pos * grow) + 'px';
  tl.querySelector('.base').style.background = dk ? 'rgba(255,255,255,.14)' : 'rgba(13,14,18,.10)';
  const labs = $$('.lab', tl), ticks = $$('.tick', tl);
  const yv = yearValue(t);
  labs.forEach((l, i) => {
    const near = clamp(1 - Math.abs(yv - (2017 + i)));
    l.style.color = dk ? `rgba(242,243,245,${0.35 + 0.65 * near})` : `rgba(13,14,18,${0.3 + 0.7 * near})`;
    l.style.fontWeight = near > 0.5 ? 700 : 500;
  });
  ticks.forEach((k, i) => {
    const passed = yv >= 2017 + i - 0.01;
    k.style.background = passed ? (dk ? '#fff' : '#0D0E12') : (dk ? 'rgba(255,255,255,.25)' : 'rgba(13,14,18,.18)');
  });
}

/* ============================================================
 * 开场：一声“小爱同学”——“我在。”——四色丝带画出 logo——光铺满画面
 * ============================================================ */
let INTRO = {};
function buildIntro() {
  const el = document.createElement('div');
  el.className = 'scene'; el.id = 'intro';
  el.innerHTML = `
    <div id="capMe" class="abs" style="left:0;width:1920px;top:640px;text-align:center;font-size:44px;font-weight:500;letter-spacing:.12em;color:#F2F3F5">“小爱同学”</div>
    <div id="capAi" class="abs" style="left:0;width:1920px;top:640px;text-align:center;font-size:44px;font-weight:600;letter-spacing:.12em"><span class="grad">我在。</span></div>
    <div id="title" class="abs" style="left:0;width:1920px;top:690px;text-align:center">
      <div id="tMain" style="font-weight:900;font-size:132px;letter-spacing:.04em;line-height:1.1;color:#0D0E12">小爱同学</div>
      <div id="tSub" style="margin-top:22px;font-weight:400;font-size:34px;letter-spacing:.32em;color:#6E727B">2017 → 2026　·　一个声音的九年</div>
    </div>`;
  SC.appendChild(el);
  INTRO.el = el;
}
// 语音波形：几条叠加的正弦，钟形包络，amp 为整体振幅（px）
function voiceWave(ctx, t, cx, cy, halfW, amp, colors, lw = 3, glow = true) {
  const N = 140;
  colors.forEach((col, j) => {
    ctx.beginPath();
    for (let i = 0; i <= N; i++) {
      const u = i / N * 2 - 1, x = cx + u * halfW;
      const env = Math.pow(1 - u * u, 2.2);
      const y = cy + amp * env * (
        Math.sin(u * (7 + j * 1.3) + t * (9 + j * 1.7) + j * 1.9) * 0.6 +
        Math.sin(u * (13 - j) - t * (6.5 + j) + j) * 0.3 +
        Math.sin(u * 3.1 + t * 3 + j * 2.4) * 0.35) * (j % 2 ? -1 : 1);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    if (glow) { ctx.strokeStyle = rgba(col, 0.16); ctx.lineWidth = lw * 5; ctx.stroke(); }
    ctx.strokeStyle = rgba(col, 0.95); ctx.lineWidth = lw; ctx.stroke();
  });
}
function speechEnv(t, syl) { // 音节包络：syl = [[中心时间, 强度],...]
  let v = 0;
  for (const [c, a] of syl) v += a * Math.exp(-Math.pow((t - c) / 0.085, 2));
  return v;
}
function renderIntro(t) {
  const el = INTRO.el;
  const on = t < TL.logoB + 0.1;
  show(el, on);
  if (!on) return;
  const cx = 960, cy = 540;
  fx.save();
  fx.globalCompositeOperation = 'lighter';
  // --- 中心光点：呼吸
  const dotIn = E.outC(seg(t, 0.15, 0.9)), dotOut = 1 - E.inC(seg(t, 3.1, 3.7));
  const breathe = 1 + 0.18 * Math.sin(t * 3.2);
  const userV = speechEnv(t, [[1.22, 1], [1.44, 0.8], [1.68, 0.9], [1.9, 0.75]]);
  const aiV = speechEnv(t, [[2.62, 1], [2.88, 0.85]]);
  if (dotIn * dotOut > 0.001) {
    const r0 = (5 + 3 * userV + 10 * aiV) * breathe;
    const g = fx.createRadialGradient(cx, cy, 0, cx, cy, 70 + 140 * aiV);
    g.addColorStop(0, `rgba(255,255,255,${0.9 * dotIn * dotOut})`);
    g.addColorStop(0.08, `rgba(220,235,255,${0.35 * dotIn * dotOut})`);
    g.addColorStop(1, 'rgba(120,160,255,0)');
    fx.fillStyle = g; fx.fillRect(cx - 300, cy - 300, 600, 600);
    fx.fillStyle = `rgba(255,255,255,${dotIn * dotOut})`;
    fx.beginPath(); fx.arc(cx, cy, r0, 0, TAU); fx.fill();
  }
  // --- 你说：白色波形
  const uw = E.outQ4(seg(t, 0.95, 1.35)) * (1 - E.inQ(seg(t, 2.0, 2.35)));
  if (uw > 0.001) voiceWave(fx, t, cx, cy, 380 * uw, 10 + 46 * userV, ['#FFFFFF', '#C9D6FF'], 2.2);
  // --- 小爱回应：四色光团 + 四色波形
  const orb = E.outQ4(seg(t, 2.35, 2.75)) * (1 - E.inC(seg(t, 3.45, 3.95)));
  if (orb > 0.001) {
    const cols = [C.pink, C.blue, C.mint, C.yellow];
    for (let i = 0; i < 4; i++) {
      const a = t * 2.2 + i * TAU / 4;
      const rr = (26 + 30 * aiV) * orb;
      const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr * 0.8;
      const R = (90 + 70 * aiV) * orb;
      const g = fx.createRadialGradient(x, y, 0, x, y, R);
      g.addColorStop(0, rgba(cols[i], 0.55)); g.addColorStop(1, rgba(cols[i], 0));
      fx.fillStyle = g; fx.fillRect(x - R, y - R, 2 * R, 2 * R);
    }
    const spread = 1 + 0.6 * E.inC(seg(t, 3.2, 3.9));
    voiceWave(fx, t * 1.2, cx, cy, 430 * orb * spread, (14 + 70 * aiV + 40 * E.inC(seg(t, 3.15, 3.6))) * orb, [C.pink, C.blue, C.mint, C.yellow], 3.2);
  }
  fx.restore();
  // --- 字幕
  const me = $('capMe'), ai = $('capAi');
  const mk = blurIn(me, t, 1.05, 0.5, 14, 12);
  const mo = E.inC(seg(t, 2.1, 2.4));
  me.style.opacity = mk * (1 - mo); if (mo > 0) me.style.filter = `blur(${mo * 12}px)`;
  const ak = blurIn(ai, t, 2.5, 0.5, 14, 12);
  const ao = E.inC(seg(t, 3.35, 3.75));
  ai.style.opacity = ak * (1 - ao); if (ao > 0) ai.style.filter = `blur(${ao * 12}px)`;
  show(me, t < 2.45); show(ai, t > 2.4 && t < 3.8);

  // --- logo：四色丝带依次画出（进度本身在 renderLogoHUD 里每帧设置，这里只画笔刷头的高光）
  const L = HUDLOGO, R = LOGO_STROKES, pr = logoReveal(t);
  // 笔刷头的高光
  if (t > 3.5 && t < 5.4) {
    const s = L.s;
    fx.save(); fx.globalCompositeOperation = 'lighter';
    for (const n in R) {
      const k = pr[n];
      if (k <= 0.01 || k >= 0.995) continue;
      const [hx, hy] = L.head(n, k);
      const pos = logoToScreen(hx, hy);
      const col = { pink: C.pink, blue: C.cyan, yellow: C.yellow, mint: C.mint }[n];
      const g = fx.createRadialGradient(pos[0], pos[1], 0, pos[0], pos[1], 90);
      g.addColorStop(0, 'rgba(255,255,255,.95)'); g.addColorStop(0.12, rgba(col, 0.7)); g.addColorStop(1, rgba(col, 0));
      fx.fillStyle = g; fx.fillRect(pos[0] - 90, pos[1] - 90, 180, 180);
    }
    fx.restore();
  }
}
const LOGO_STROKES = { yellow: [3.55, 4.25], pink: [3.7, 4.75], mint: [4.2, 4.95], blue: [4.5, 5.25] };
function logoReveal(t) { const pr = {}; for (const n in LOGO_STROKES) pr[n] = E.ioC(seg(t, LOGO_STROKES[n][0], LOGO_STROKES[n][1])); return pr; }
// logo 位置（开场居中 → 停靠左上角）
function logoState(t) {
  const dockA = 8.7, dockB = 9.75;
  const k = E.ioQ4(seg(t, dockA, dockB));
  const pop = spring(t - 3.55, 1.3, 0.62);
  const sc0 = lerp(0.86, 1, pop) * (1 + 0.025 * E.ioS(seg(t, 5.3, 8.7)));
  const x = lerp(960, 98, k), y = lerp(430, 78, k);
  const sc = lerp(sc0, 40 / 380, k);
  const rot = lerp(-5, 0, pop) * (1 - k);
  return { x, y, sc, rot };
}
function logoToScreen(lx, ly) {
  const st = logoState(window.__t || 0);
  const s = HUDLOGO.s * st.sc;
  return [st.x + (lx - LOGO.cx) * s, st.y + (ly - LOGO.cy) * s];
}
function renderLogoHUD(t) {
  const st = logoState(t);
  const vis = t > 3.4 && t < FIN.a + 1.2;
  HUDLOGO.root.style.display = vis ? '' : 'none';
  if (!vis) return;
  const out = E.inC(seg(t, FIN.a + 0.2, FIN.a + 1.0));
  // 每帧都由 t 决定画出进度和扫光：从任意时刻起播（或分段并行渲染）都一致
  HUDLOGO.reveal(logoReveal(t));
  HUDLOGO.shine(seg(t, 5.3, 6.1));
  HUDLOGO.place(st.x, st.y, st.sc, st.rot, 1 - out);
  // 暗场里有光晕，铺满亮光后收起
  const gl = t < TL.flood[0] ? 0.55 : lerp(0.55, 0.0, E.outC(seg(t, TL.flood[0], TL.flood[1] + 0.6)));
  HUDLOGO.glowAmt(gl, 36);
}
function renderTitle(t) {
  const tm = $('tMain'), ts = $('tSub');
  if (t < 6.0 || t > 9.6) { tm.style.opacity = 0; ts.style.opacity = 0; return; }
  charsIn(tm, t, 6.05, { stagger: 0.07, dur: 0.7, dy: 0.35, blur: 14 });
  tm.style.opacity = 1;
  blurIn(ts, t, 6.6, 0.8, 16, 12);
  const o = outro($('title'), t, 8.55, 0.45, { scale: 0.04, blur: 18 });
  if (o <= 0) css('title', { opacity: 1, filter: 'none', transform: 'none' });
}

/* ============================================================
 * 章节通用：年份 + 小标题 + 两行大标题 + 副标题 + 标签
 * ============================================================ */
function buildChapters() {
  for (const c of CHAPTERS) {
    const tx = CH_TEXT[c.key];
    const el = document.createElement('div');
    el.className = 'scene' + (c.dark ? ' dark' : '');
    el.id = c.id;
    el.innerHTML = `
      <div class="vis abs" style="left:0;top:0;width:1920px;height:1080px"></div>
      <div class="txt abs" style="left:0;top:0;width:1000px;height:1080px">
        <div class="abs kicker" style="left:146px;top:380px">${tx.kicker}</div>
        <div class="abs hl" style="left:138px;top:428px"><span class="l l1">${tx.hl[0]}</span><span class="l l2 grad">${tx.hl[1]}</span></div>
        <div class="abs sub" style="left:142px;top:672px">${tx.sub}</div>
        <div class="abs chips" style="left:138px;top:752px;display:flex;gap:14px">${(tx.chips || []).map(s => `<span data-sfx="chip" class="chip">${s}</span>`).join('')}</div>
      </div>`;
    SC.appendChild(el);
    c.el = el; c.vis = el.querySelector('.vis'); c.txt = el.querySelector('.txt');
    if (VIS[c.key] && VIS[c.key].build) VIS[c.key].build(c);
  }
}
function renderChapterText(c, t) {
  const l = t - c.a;
  const el = c.el;
  blurIn(el.querySelector('.kicker'), l, 0.2, 0.6, 18, 10);
  charsIn(el.querySelector('.l1'), l, 0.32, { stagger: 0.045 });
  charsIn(el.querySelector('.l2'), l, 0.58, { stagger: 0.05 });
  blurIn(el.querySelector('.sub'), l, 1.05, 0.7, 18, 12);
  $$('.chip', el).forEach((ch, i) => popIn(ch, l, 1.35 + i * 0.14, { from: 0.7, dy: 16 }));
  // 出场
  const o = outro(c.txt, t, c.b - 0.5, 0.42, { scale: 0.03, dy: 10, blur: 16 });
  if (o <= 0) css(c.txt, { opacity: 1, filter: 'none', transform: 'none' });
}

/* ============================================================
 * 各年份的视觉
 * ============================================================ */
const VIS = {};

/* ---------- 2017 · 小米AI音箱 ---------- */
function noteSVG(col) {
  return `<svg viewBox="-14 -46 40 54" width="40" height="54" style="overflow:visible"><ellipse cx="0" cy="0" rx="10" ry="7.4" transform="rotate(-22)" fill="${col}"/><rect x="7.6" y="-40" width="3.4" height="40" rx="1.7" fill="${col}"/><path d="M9.3 -40 C16 -36 24 -31 20 -18 C19 -26 15 -29 9.3 -30 Z" fill="${col}"/></svg>`;
}
VIS.speaker = {
  build(c) {
    const ringStops = `<stop offset="0" stop-color="#FF6CA3"/><stop offset=".3" stop-color="#FF957B"/><stop offset=".5" stop-color="#FCCD01"/><stop offset=".7" stop-color="#11E6AD"/><stop offset="1" stop-color="#0A8EF8"/>`;
    c.vis.innerHTML = `
      <div id="spk" class="abs" style="left:1120px;top:250px;width:420px;height:600px;transform-origin:50% 100%">
      <svg viewBox="0 0 420 600" width="420" height="600" style="overflow:visible">
        <defs>
          <linearGradient id="spBody" x1="0" x2="1"><stop offset="0" stop-color="#D6D9DE"/><stop offset=".15" stop-color="#F1F2F4"/><stop offset=".44" stop-color="#FFFFFF"/><stop offset=".72" stop-color="#F5F6F8"/><stop offset="1" stop-color="#CBCED4"/></linearGradient>
          <linearGradient id="spTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E9EAED"/></linearGradient>
          <pattern id="spDots" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.3" fill="#7E838C"/></pattern>
          <linearGradient id="spShade" x1="0" x2="1"><stop offset="0" stop-color="#1A1F2B" stop-opacity=".16"/><stop offset=".33" stop-color="#1A1F2B" stop-opacity="0"/><stop offset=".72" stop-color="#1A1F2B" stop-opacity="0"/><stop offset="1" stop-color="#1A1F2B" stop-opacity=".24"/></linearGradient>
          <radialGradient id="spShadow"><stop offset="0" stop-color="#1B2130" stop-opacity=".30"/><stop offset="1" stop-color="#1B2130" stop-opacity="0"/></radialGradient>
          <linearGradient id="spRing" gradientUnits="userSpaceOnUse" x1="118" y1="80" x2="302" y2="80">${ringStops}</linearGradient>
          <clipPath id="spClip"><path d="M60 82 L60 520 A150 26 0 0 0 360 520 L360 82 Z"/></clipPath>
        </defs>
        <ellipse cx="210" cy="550" rx="200" ry="34" fill="url(#spShadow)"/>
        <path d="M60 82 L60 520 A150 26 0 0 0 360 520 L360 82 Z" fill="url(#spBody)"/>
        <g clip-path="url(#spClip)"><rect x="60" y="150" width="300" height="420" fill="url(#spDots)" opacity=".2"/><rect x="60" y="60" width="300" height="520" fill="url(#spShade)"/></g>
        <ellipse cx="210" cy="82" rx="150" ry="26" fill="url(#spTop)" stroke="#D3D5DA" stroke-width="1.5"/>
        <ellipse cx="210" cy="82" rx="114" ry="19.5" fill="#F2F3F5"/>
        <g id="spRingG">
          <ellipse id="spRingGlow" cx="210" cy="82" rx="90" ry="15.5" fill="none" stroke="url(#spRing)" stroke-width="22" opacity=".0"/>
          <ellipse cx="210" cy="82" rx="90" ry="15.5" fill="none" stroke="#E3E5E9" stroke-width="6"/>
          <ellipse id="spRingOn" cx="210" cy="82" rx="90" ry="15.5" fill="none" stroke="url(#spRing)" stroke-width="6" opacity="0"/>
        </g>
        <g id="spWaves"></g>
      </svg></div>
      <div id="spNotes" class="abs" style="left:0;top:0"></div>
      <div id="b17me" data-sfx="bubble" class="bub me" style="left:1420px;top:196px;transform-origin:100% 100%">小爱同学，放首歌吧</div>
      <div id="b17ai" data-sfx="bubble2" class="bub ai" style="left:1480px;top:312px;transform-origin:0 100%"><span class="who">小爱同学</span>好的，为你播放今日推荐</div>`;
    const waves = $('spWaves');
    for (let i = 0; i < 3; i++) waves.insertAdjacentHTML('beforeend', `<ellipse class="spw" cx="210" cy="82" rx="150" ry="26" fill="none" stroke="url(#spRing)" stroke-width="3" opacity="0"/>`);
    const notes = $('spNotes');
    const nc = [C.pink, C.blue, C.mint, C.coral, C.cyan];
    for (let i = 0; i < 5; i++) notes.insertAdjacentHTML('beforeend', `<div data-sfx="note" class="abs note" style="left:0;top:0;opacity:0">${noteSVG(nc[i])}</div>`);
  },
  render(c, t) {
    const l = t - c.a;
    const spk = $('spk');
    // 音箱从下方弹起；章节结束时向左缩小让位给手机
    const k = spring(l - 0.15, 1.5, 0.62);
    const ex = E.ioQ4(seg(t, c.b - 0.55, c.b + 0.25));
    spk.style.opacity = clamp(l / 0.25) * (1 - ex);
    spk.style.transform = `translateY(${(1 - k) * 380}px) scale(${lerp(0.92, 1, k) * (1 - 0.25 * ex)}) translateX(${-ex * 260}px)`;
    // 灯环：被唤醒时亮起并旋转
    const wake = E.outC(seg(l, 1.6, 2.1));
    $('spRingOn').setAttribute('opacity', wake);
    $('spRingGlow').setAttribute('opacity', wake * (0.28 + 0.12 * Math.sin(l * 5)));
    $('spRing').setAttribute('gradientTransform', `rotate(${(l * 90) % 360} 210 82)`);
    // 声波一圈圈扩散
    $$('.spw').forEach((w, i) => {
      const ph = ((l - 2.3 - i * 0.6) % 1.8 + 1.8) % 1.8 / 1.8;
      const act = l > 2.3 + i * 0.6 ? 1 : 0;
      w.setAttribute('rx', lerp(150, 330, E.outC(ph)));
      w.setAttribute('ry', lerp(26, 84, E.outC(ph)));
      w.setAttribute('opacity', act * (1 - ph) * 0.8 * wake);
    });
    // 音符飘起
    $$('.note', $('spNotes')).forEach((n, i) => {
      const st = 2.5 + i * 0.55, ph = (l - st) / 2.6;
      if (ph < 0 || ph > 1) { n.style.opacity = 0; return; }
      const x = 1330 + (i % 2 ? 1 : -1) * (40 + 60 * ph) + Math.sin(ph * 6 + i) * 30, y = 300 - ph * 260;
      n.style.opacity = Math.sin(PI * ph) * (1 - ex);
      n.style.transform = `translate(${x}px,${y}px) rotate(${Math.sin(ph * 5 + i) * 14}deg) scale(${0.9 + 0.4 * Math.sin(PI * ph)})`;
    });
    // 对话气泡
    popIn('b17me', l, 1.15, { from: 0.4, freq: 2.4, damp: 0.55 });
    popIn('b17ai', l, 2.05, { from: 0.4, freq: 2.4, damp: 0.55 });
    const bo = E.inC(seg(t, c.b - 0.55, c.b - 0.15));
    if (bo > 0) { $('b17me').style.opacity *= 1 - bo; $('b17ai').style.opacity *= 1 - bo; }
  },
};

/* ---------- 2018 · 手机 ---------- */
const APP_COLS = ['#FFB4A8', '#FFD27A', '#A9E8D0', '#9CCBFF', '#C9B8FF', '#FFC2DD', '#8FE3F0', '#FFE3A3'];
VIS.phone = {
  build(c) {
    const icons = Array.from({ length: 20 }, (_, i) => `<div style="position:absolute;left:${34 + (i % 4) * 76}px;top:${118 + Math.floor(i / 4) * 92}px;width:56px;height:56px;border-radius:17px;background:${APP_COLS[(i * 3) % 8]};opacity:.9"></div>`).join('');
    c.vis.innerHTML = `
    <div id="ph" class="abs" style="left:1158px;top:136px;width:380px;height:790px;transform-origin:50% 70%">
      <div style="position:absolute;left:30px;right:30px;bottom:-26px;height:40px;border-radius:50%;background:radial-gradient(closest-side,rgba(20,28,45,.28),rgba(20,28,45,0))"></div>
      <div style="position:absolute;inset:0;border-radius:62px;background:linear-gradient(150deg,#3A3E48,#0B0C10 46%,#1D2027);box-shadow:0 46px 90px rgba(16,24,40,.25),inset 0 0 0 1.5px rgba(255,255,255,.18)"></div>
      <div id="phScr" style="position:absolute;left:11px;top:11px;width:358px;height:768px;border-radius:52px;overflow:hidden;background:linear-gradient(165deg,#E7EDFB 0%,#F6E8F0 52%,#E3F6EF 100%)">
        <div style="position:absolute;left:34px;top:26px;font-size:19px;font-weight:600;color:#1B1D22">07:00</div>
        <div style="position:absolute;right:30px;top:30px;width:30px;height:14px;border-radius:4px;border:2px solid #1B1D22;opacity:.8"></div>
        <div id="phHome" style="position:absolute;inset:0">${icons}</div>
        <div id="phPanel" data-sfx="swipe" style="position:absolute;left:12px;right:12px;bottom:12px;height:432px;border-radius:40px;background:rgba(255,255,255,.96);box-shadow:0 -10px 40px rgba(16,24,40,.12)">
          <div id="phAsk" data-sfx="type" style="position:absolute;left:30px;top:34px;width:290px;font-size:25px;line-height:1.4;color:#6E727B;font-weight:500"></div>
          <div id="phAns" data-sfx="type" style="position:absolute;left:30px;top:84px;width:300px;font-size:27px;line-height:1.42;color:#0D0E12;font-weight:600"></div>
          <div id="phAlarm" data-sfx="pop" style="position:absolute;left:24px;right:24px;top:196px;height:112px;border-radius:26px;background:#F3F4F7">
            <div style="position:absolute;left:24px;top:14px;font-size:58px;font-weight:300;letter-spacing:-.01em;color:#0D0E12">07:00</div>
            <div style="position:absolute;left:28px;top:80px;font-size:18px;color:#6E727B">闹钟 · 明天</div>
            <div id="phTog" style="position:absolute;right:22px;top:38px;width:68px;height:38px;border-radius:19px;background:#D5D8DE"><div id="phKnob" style="position:absolute;left:3px;top:3px;width:32px;height:32px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.2)"></div></div>
          </div>
          <canvas id="phWave" width="668" height="150" style="position:absolute;left:0;bottom:16px;width:334px;height:75px"></canvas>
        </div>
      </div>
    </div>`;
  },
  render(c, t) {
    const l = t - c.a;
    const ph = $('ph');
    const k = spring(l - 0.25, 1.25, 0.6);
    const ex = E.inC(seg(t, c.b - 0.5, c.b + 0.2));
    const ry = lerp(-38, -8, k) + 4 * Math.sin(l * 0.8), rx = lerp(14, 3, k);
    ph.style.opacity = clamp((l - 0.2) / 0.3) * (1 - ex);
    ph.style.transform = `perspective(1800px) translateY(${(1 - k) * 520}px) rotateY(${ry}deg) rotateX(${rx}deg) scale(${1 - 0.06 * ex})`;
    ph.style.filter = ex > 0 ? `blur(${ex * 12}px)` : 'none';
    // 小爱面板升起
    const pk = spring(l - 1.15, 1.6, 0.68);
    $('phPanel').style.transform = `translateY(${(1 - pk) * 460}px)`;
    $('phHome').style.filter = `blur(${pk * 6}px)`;
    $('phHome').style.opacity = 1 - 0.35 * pk;
    // 语音转文字 → 回答 → 闹钟卡片
    const ask = '明早 7 点叫我起床';
    const n = Math.floor(clamp((l - 1.5) / 0.9) * ask.length);
    $('phAsk').textContent = ask.slice(0, n);
    const ans = '好的，明早 7:00 的闹钟已设好。';
    const n2 = Math.floor(clamp((l - 2.55) / 0.8) * ans.length);
    $('phAns').textContent = ans.slice(0, n2);
    popIn('phAlarm', l, 3.25, { from: 0.85, dy: 24 });
    const tg = E.ioC(seg(l, 3.9, 4.2));
    $('phKnob').style.transform = `translateX(${tg * 30}px)`;
    $('phTog').style.background = mixHex('#D5D8DE', '#11C79A', tg);
    // 面板底部的四色声波（画在面板自己的小画布上）
    const wc = $('phWave').getContext('2d');
    wc.setTransform(2, 0, 0, 2, 0, 0);
    wc.clearRect(0, 0, 334, 75);
    const talk = 0.25 + 0.9 * speechEnv(l, [[1.7, 1], [1.95, .8], [2.2, .9], [2.75, .7], [3.0, .8], [3.25, .6]]);
    voiceWave(wc, l, 167, 37, 150, 16 * talk * pk, [C.pink, C.blue, C.mint, C.yellow], 2.2, false);
  },
};

/* ---------- 2019 · AIoT：一句话控制全屋 ---------- */
const ICON = {
  bulb: 'M24 6a12 12 0 0 1 7 21.8V33H17v-5.2A12 12 0 0 1 24 6zM18 38h12M20.5 43h7',
  tv: 'M6 9h36a3 3 0 0 1 3 3v19a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3zM17 42h14M24 34v8',
  ac: 'M7 9h34a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V13a4 4 0 0 1 4-4zM10 21h28M15 33q3 4 0 8M24 33q3 4 0 8M33 33q3 4 0 8',
  curtain: 'M4 7h40M9 7v35c5 0 9-9 7-35M39 7v35c-5 0-9-9-7-35',
  vacuum: 'M24 6a18 18 0 1 1 0 36a18 18 0 1 1 0-36zM24 18a6 6 0 1 1 0 12a6 6 0 1 1 0-12zM24 6v6',
  purifier: 'M19 4h10a6 6 0 0 1 6 6v28a6 6 0 0 1-6 6H19a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6zM24 11a6 6 0 1 1 0 12a6 6 0 1 1 0-12zM18 31h12M18 37h12',
  cooker: 'M8 21h32v13a8 8 0 0 1-8 8H16a8 8 0 0 1-8-8zM10 21a14 9 0 0 1 28 0M24 8v4',
  camera: 'M24 7a12 12 0 1 1 0 24a12 12 0 1 1 0-24zM24 15a4 4 0 1 1 0 8a4 4 0 1 1 0-8zM24 31v7M15 42h18',
  plug: 'M17 9h14a7 7 0 0 1 7 7v14a7 7 0 0 1-7 7H17a7 7 0 0 1-7-7V16a7 7 0 0 1 7-7zM19 19v6M29 19v6M22 31h4',
  lock: 'M18 4h12a6 6 0 0 1 6 6v28a6 6 0 0 1-6 6H18a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6zM24 15a4.5 4.5 0 1 1 0 9a4.5 4.5 0 1 1 0-9zM24 24v6',
  washer: 'M13 4h22a5 5 0 0 1 5 5v30a5 5 0 0 1-5 5H13a5 5 0 0 1-5-5V9a5 5 0 0 1 5-5zM24 18a9 9 0 1 1 0 18a9 9 0 1 1 0-18zM13 11h6',
  fan: 'M24 21a3 3 0 1 1 0 6a3 3 0 1 1 0-6zM24 21c-1-8 3-14 8-13 4 1 3 7-6 13M27 25c7-3 13 0 13 5-1 4-7 4-13-5M21 25c-5 6-12 7-14 3-1-4 4-7 14-3',
  speaker: 'M19 4h10a7 7 0 0 1 7 7v26a7 7 0 0 1-7 7H19a7 7 0 0 1-7-7V11a7 7 0 0 1 7-7zM24 24a6 6 0 1 1 0 12a6 6 0 1 1 0-12zM21 12h6',
  kettle: 'M14 16h18l3 26H11zM14 16l2-6h14l2 6M35 20c6 0 8 4 8 8s-3 7-7 7M18 10V7h10v3',
};
const ICON_ORDER = ['bulb', 'tv', 'ac', 'curtain', 'vacuum', 'purifier', 'cooker', 'camera', 'plug', 'lock', 'washer', 'fan', 'speaker', 'kettle'];
const ICON_COL = [C.pink, C.blue, C.mint, '#E6A700', C.cyan, C.coral];
function iconSVG(name, col, size = 52, sw = 3.2) {
  return `<svg viewBox="0 0 48 48" width="${size}" height="${size}"><path d="${ICON[name]}" fill="none" stroke="${col}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}
const IOT = { cx: 1352, cy: 520, rings: [{ n: 6, r: 232, sp: 0.16 }, { n: 8, r: 392, sp: -0.10 }] };
VIS.home = {
  build(c) {
    let html = `<div id="iotHub" data-sfx="hub" class="abs" style="left:${IOT.cx - 86}px;top:${IOT.cy - 86}px;width:172px;height:172px;border-radius:50%;background:#fff;box-shadow:0 26px 60px rgba(16,24,40,.14),0 0 0 14px rgba(255,255,255,.55)"></div>`;
    let k = 0;
    IOT.rings.forEach((rg, ri) => {
      for (let i = 0; i < rg.n; i++, k++) {
        const nm = ICON_ORDER[k % ICON_ORDER.length];
        html += `<div data-sfx="tile" class="card iot-tile" data-ring="${ri}" data-i="${i}" style="left:0;top:0;width:98px;height:98px;border-radius:28px;display:flex;align-items:center;justify-content:center">${iconSVG(nm, ICON_COL[k % ICON_COL.length])}</div>`;
      }
    });
    html += `<div id="iotNum" class="abs" style="left:${IOT.cx - 300}px;top:${IOT.cy + 300}px;width:600px;text-align:center"></div>`;
    c.vis.innerHTML = html;
    c.hubLogo = makeLogo($('iotHub'), { height: 86 });
    c.hubLogo.place(86, 86, 1, 0, 1);
  },
  tilePos(c, ri, i, l) {
    const rg = IOT.rings[ri];
    const a = (i / rg.n) * TAU + l * rg.sp + (ri ? 0.2 : 0);
    return [IOT.cx + Math.cos(a) * rg.r, IOT.cy + Math.sin(a) * rg.r * 0.8, a];
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.55, c.b + 0.15));
    const hk = spring(l - 0.2, 1.8, 0.55);
    const hub = $('iotHub');
    hub.style.opacity = clamp(l / 0.2) * (1 - ex);
    hub.style.transform = `scale(${lerp(0.3, 1, hk) * (1 - 0.3 * ex)})`;
    const tiles = $$('.iot-tile', c.vis);
    const pts = [];
    tiles.forEach((tile, j) => {
      const ri = +tile.dataset.ring, i = +tile.dataset.i;
      const [x, y, a] = this.tilePos(c, ri, i, l);
      const st = 0.55 + j * 0.09;
      const kk = spring(l - st, 1.5, 0.62);
      const far = 1100;
      const fx0 = IOT.cx + Math.cos(a) * far, fy0 = IOT.cy + Math.sin(a) * far * 0.8;
      // 出场：所有设备被吸回中心
      const px = lerp(lerp(fx0, x, kk), IOT.cx, ex), py = lerp(lerp(fy0, y, kk), IOT.cy, ex);
      const depth = (Math.sin(a) + 1) / 2;  // 下方离镜头更近
      const sc = lerp(0.86, 1.06, depth) * (1 - 0.6 * ex);
      tile.style.opacity = clamp((l - st) / 0.2) * (1 - ex);
      tile.style.transform = `translate(${px - 49}px,${py - 49}px) scale(${sc})`;
      tile.style.zIndex = Math.round(depth * 10);
      pts.push([px, py, clamp((l - st - 0.25) / 0.3) * (1 - ex), j]);
    });
    // 连线 + 沿线跑的光点（指令从中心发出）
    fx.save();
    for (const [x, y, a, j] of pts) {
      if (a <= 0) continue;
      fx.strokeStyle = `rgba(61,139,255,${0.16 * a})`; fx.lineWidth = 2;
      fx.beginPath(); fx.moveTo(IOT.cx, IOT.cy); fx.lineTo(x, y); fx.stroke();
      const ph = ((l * 0.9 + j * 0.37) % 1);
      const px = lerp(IOT.cx, x, ph), py = lerp(IOT.cy, y, ph);
      const col = [C.pink, C.blue, C.mint][j % 3];
      const g = fx.createRadialGradient(px, py, 0, px, py, 14);
      g.addColorStop(0, rgba(col, 0.9 * a)); g.addColorStop(1, rgba(col, 0));
      fx.fillStyle = g; fx.fillRect(px - 14, py - 14, 28, 28);
    }
    // 中心向外的波纹
    for (let i = 0; i < 3; i++) {
      const ph = ((l - 1 - i * 0.7) % 2.1 + 2.1) % 2.1 / 2.1;
      if (l < 1 + i * 0.7) continue;
      fx.strokeStyle = `rgba(61,139,255,${0.22 * (1 - ph) * (1 - ex)})`; fx.lineWidth = 2;
      fx.beginPath(); fx.ellipse(IOT.cx, IOT.cy, 90 + ph * 360, (90 + ph * 360) * 0.8, 0, 0, TAU); fx.stroke();
    }
    fx.restore();
  },
};

/* ---------- 2020 · 连续对话 ---------- */
const CHAT20 = [
  ['me', '明天会下雨吗？', 0.55],
  ['ai', '明天有小雨，出门记得带伞。', 1.35],
  ['me', '那后天呢？', 2.25],
  ['ai', '后天转晴，最高 18℃。', 3.0],
  ['me', '把客厅空调调到 26 度', 3.75],
  ['ai', '好的，已调到 26℃。', 4.45],
];
VIS.chat = {
  build(c) {
    let html = `<div id="chat20" class="abs" style="left:1080px;top:0;width:720px;height:1080px">`;
    CHAT20.forEach(([who, txt], i) => {
      html += `<div data-sfx="${who === 'me' ? 'bubble' : 'bubble2'}" class="bub ${who} c20b" style="${who === 'me' ? 'right:0' : 'left:0'};top:0;transform-origin:${who === 'me' ? '100%' : '0'} 100%">${who === 'ai' ? '<span class="who">小爱同学</span>' : ''}${txt}</div>`;
    });
    html += `<div id="c20chip" data-sfx="chip" class="chip" style="position:absolute;right:250px;top:0;background:#0D0E12;color:#fff"><span class="dot" style="background:${C.mint}"></span>无需再喊「小爱同学」</div>`;
    html += `</div><canvas id="c20wave" class="abs" width="720" height="120" style="left:1080px;top:820px;width:720px;height:120px"></canvas>`;
    c.vis.innerHTML = html;
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.5, c.b + 0.15));
    const bubs = $$('.c20b', c.vis);
    // 先量出每个气泡高度，按“聊天滚动”排布：新气泡出现时整列上推
    if (!c.hs) c.hs = bubs.map(b => b.offsetHeight);
    const gap = 22, bottom = 790, N = CHAT20.length;
    const ap = CHAT20.map(([, , st]) => spring(l - st, 2.0, 0.78));
    bubs.forEach((b, i) => {
      const st = CHAT20[i][2];
      let y = bottom;
      for (let j = i; j < N; j++) y -= ap[j] * (c.hs[j] + gap);
      const k = spring(l - st, 2.4, 0.55);
      b.style.top = y.toFixed(1) + 'px';
      b.style.opacity = clamp((l - st) / 0.15) * (1 - ex) * clamp(1 - (200 - y) / 150);
      b.style.transform = `scale(${lerp(0.5, 1, k)})`;
    });
    // “无需再喊”标签，跟着第三个气泡
    const chip = $('c20chip');
    const b2 = bubs[2];
    const ck = spring(l - 2.55, 2.2, 0.55);
    chip.style.top = (parseFloat(b2.style.top) + 6) + 'px';
    chip.style.right = (b2.offsetWidth + 22) + 'px';
    chip.style.opacity = clamp((l - 2.55) / 0.15) * (1 - ex) * (1 - E.inC(seg(l, 4.2, 4.6)));
    chip.style.transform = `scale(${lerp(0.6, 1, ck)})`;
    // 底部一直在听的声波
    const wcv = $('c20wave'), wc = wcv.getContext('2d');
    wcv.style.opacity = clamp((l - 0.5) / 0.4) * (1 - ex);
    wc.clearRect(0, 0, 720, 120);
    const talk = 0.35 + 0.8 * speechEnv(l, CHAT20.filter(r => r[0] === 'ai').map(r => [r[2] + 0.15, 1]));
    voiceWave(wc, l, 360, 60, 300, 18 * talk * (1 - ex) * clamp(l / 0.6), [C.pink, C.blue, C.mint, C.yellow], 2.6, false);
  },
};

/* ---------- 2021 · 月活破亿（数据：小米集团业绩公告） ---------- */
const MAU = [ // [距 2018-07 的月数, 月活（万）, 标签]
  [0, 3000, '2018.7'], [2, 3400, '2018.9'], [5, 3880, '2018.12'], [11, 4990, '2019.6'],
  [17, 6040, '2019.12'], [23, 7840, '2020.6'], [29, 8670, '2020.12'], [35, 10200, '2021.6'],
];
const MC = { x0: 1010, x1: 1760, yb: 800, yt: 430, vmax: 12000, col: '#0A7FE6' };
const mx = m => MC.x0 + m / 35 * (MC.x1 - MC.x0);
const my = v => MC.yb - v / MC.vmax * (MC.yb - MC.yt);
function fmtMAU(v) { return v >= 10000 ? (v / 10000).toFixed(2) + ' 亿' : fmtInt(Math.round(v / 10) * 10) + ' 万'; }
VIS.mau = {
  build(c) {
    const grid = [0, 5000, 10000].map(v => `<line class="mgrid" x1="${MC.x0}" x2="${MC.x1}" y1="${my(v)}" y2="${my(v)}" stroke="${v === 10000 ? '#9AA0AA' : '#D9DBE0'}" stroke-width="${v === 10000 ? 1.5 : 1}"/>`).join('');
    const ylab = [[5000, '5000 万'], [10000, '1 亿']].map(([v, s]) => `<text class="mlab" x="${MC.x0}" y="${my(v) - 12}" font-size="20" fill="#6E727B" font-weight="${v === 10000 ? 650 : 400}">${s}</text>`).join('');
    const xlab = [[6, '2019'], [18, '2020'], [30, '2021']].map(([m, s]) => `<line class="mgrid" x1="${mx(m)}" x2="${mx(m)}" y1="${MC.yb}" y2="${MC.yb + 8}" stroke="#C9CCD2" stroke-width="1"/><text class="mlab" x="${mx(m)}" y="${MC.yb + 36}" font-size="20" fill="#6E727B" text-anchor="middle">${s}</text>`).join('');
    const dots = MAU.map((d, i) => `<circle class="mdot" cx="${mx(d[0])}" cy="${my(d[1])}" r="6" fill="${MC.col}" stroke="${PAPER}" stroke-width="2.5" opacity="0"/>`).join('');
    c.vis.innerHTML = `
      <div class="abs" id="mauLab" style="left:${MC.x0}px;top:196px;font-size:24px;color:#6E727B;letter-spacing:.06em">小爱同学 · 月活跃用户</div>
      <div class="abs" id="mauVal" style="left:${MC.x0 - 6}px;top:232px;font-size:118px;font-weight:650;letter-spacing:-.02em;line-height:1">0</div>
      <svg class="abs" width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0;overflow:visible">
        <defs><linearGradient id="mArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${MC.col}" stop-opacity=".16"/><stop offset="1" stop-color="${MC.col}" stop-opacity="0"/></linearGradient></defs>
        ${grid}${ylab}${xlab}
        <path id="mAreaP" fill="url(#mArea)" d=""/>
        <path id="mLine" fill="none" stroke="${MC.col}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" d=""/>
        ${dots}
        <circle id="mRing" cx="0" cy="0" r="10" fill="none" stroke="${MC.col}" stroke-width="2" opacity="0"/>
        <circle id="mHead" cx="0" cy="0" r="8" fill="${MC.col}" stroke="${PAPER}" stroke-width="3" opacity="0"/>
      </svg>
      <div class="abs" id="mSrc" style="left:${MC.x0}px;top:${MC.yb + 66}px;font-size:18px;color:#A4A8B0;letter-spacing:.06em">数据：小米集团业绩公告（2018–2021）</div>`;
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.5, c.b + 0.1));
    const vis = c.vis;
    const ax = E.outC(seg(l, 0.25, 0.8));
    $$('.mgrid,.mlab', vis).forEach(e => e.setAttribute('opacity', ax));
    blurIn('mauLab', l, 0.35, 0.6, 12, 8);
    blurIn('mSrc', l, 0.6, 0.6, 0, 6);
    // 折线从左到右画出；用真实数据点之间的直线段（不做平滑，避免“编”出中间值）
    const p = E.ioS(seg(l, 0.7, 3.4));
    const mEnd = p * 35;
    let pts = [], head = null;
    for (let i = 0; i < MAU.length; i++) {
      const [m, v] = MAU[i];
      if (m <= mEnd) pts.push([mx(m), my(v)]);
      if (i > 0 && MAU[i - 1][0] < mEnd && m > mEnd) {
        const k = (mEnd - MAU[i - 1][0]) / (m - MAU[i - 1][0]);
        head = [mEnd, lerp(MAU[i - 1][1], v, k)];
        pts.push([mx(mEnd), my(head[1])]);
      }
    }
    if (!head) head = mEnd >= 35 ? [35, MAU[MAU.length - 1][1]] : [0, MAU[0][1]];
    const d = pts.map((q, i) => (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1)).join('');
    $('mLine').setAttribute('d', pts.length > 1 ? d : '');
    $('mAreaP').setAttribute('d', pts.length > 1 ? d + `L${pts[pts.length - 1][0].toFixed(1)} ${MC.yb}L${pts[0][0].toFixed(1)} ${MC.yb}Z` : '');
    $$('.mdot', vis).forEach((e, i) => e.setAttribute('opacity', MAU[i][0] <= mEnd + 0.01 && l > 0.7 ? 1 : 0));
    const hx = mx(head[0]), hy = my(head[1]);
    const hv = l > 0.7 ? 1 : 0;
    $('mHead').setAttribute('cx', hx); $('mHead').setAttribute('cy', hy); $('mHead').setAttribute('opacity', hv);
    // 主数字跟着线头计数
    const val = $('mauVal');
    val.textContent = fmtMAU(l < 0.7 ? MAU[0][1] : head[1]);
    val.style.opacity = E.outC(seg(l, 0.5, 0.9));
    // 冲过 1 亿：阈值线闪一下 + 一圈波纹
    const cross = 0.7 + (3.4 - 0.7) * 0.9;     // 约在最后一段
    const rk = seg(l, 3.25, 4.1);
    const ring = $('mRing');
    ring.setAttribute('cx', mx(35)); ring.setAttribute('cy', my(10200));
    ring.setAttribute('r', 8 + 46 * E.outC(rk)); ring.setAttribute('opacity', rk > 0 && rk < 1 ? (1 - rk) * 0.9 : 0);
    const pop = spring(l - 3.35, 2.2, 0.45);
    val.style.transform = `scale(${l > 3.35 ? lerp(1.12, 1, pop) : 1})`;
    val.style.transformOrigin = '0 70%';
    val.style.color = l > 3.35 ? '#0D0E12' : '#2A2D33';
    // 出场
    vis.style.opacity = 1 - ex;
    vis.style.filter = ex > 0 ? `blur(${ex * 14}px)` : 'none';
  },
};

/* ---------- 2024 · 超级小爱：从能听能说，到能想能干 ---------- */
const SUPER = [
  ['能听', '听清你说的每句话', 'M10 24h4M18 16v16M26 10v28M34 16v16M42 21v6'],
  ['能说', '自然地回答你', 'M8 10h32a4 4 0 0 1 4 4v17a4 4 0 0 1-4 4H22l-8 7v-7H8a4 4 0 0 1-4-4V14a4 4 0 0 1 4-4zM16 22.5h.5M24 22.5h.5M32 22.5h.5'],
  ['能想', '理解 · 推理 · 规划', 'M24 4l4.6 13.4L42 22l-13.4 4.6L24 40l-4.6-13.4L6 22l13.4-4.6z'],
  ['能干', '跨应用，替你办事', 'M24 4a20 20 0 1 1 0 40a20 20 0 1 1 0-40zM15 24.5l6.5 6.5L34 18'],
];
VIS.super = {
  build(c) {
    c.vis.innerHTML = `<div id="supT" class="abs" style="left:1040px;top:150px;font-size:56px;font-weight:900;letter-spacing:.08em"><span class="grad">超级小爱</span></div>` +
      SUPER.map((s, i) => {
        const x = 1040 + (i % 2) * 370, y = 260 + Math.floor(i / 2) * 270;
        const hot = i >= 2;
        return `<div data-sfx="${hot ? 'superhot' : 'pop'}" class="abs sup" style="left:${x}px;top:${y}px;width:340px;height:240px;border-radius:34px;${hot ? 'background:linear-gradient(135deg,#FF6CA3,#3D8BFF 55%,#12E2AE);padding:2px' : 'background:rgba(255,255,255,.10);padding:1.5px'}">
          <div style="position:absolute;inset:${hot ? 2 : 1.5}px;border-radius:32px;background:#0E1017"></div>
          <svg class="abs" viewBox="0 0 48 48" width="56" height="56" style="left:34px;top:34px;overflow:visible"><path d="${s[2]}" fill="none" stroke="${hot ? 'url(#supG)' : '#8A90A0'}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <div class="abs" style="left:34px;top:112px;font-size:58px;font-weight:900;color:${hot ? '#FFFFFF' : '#C9CDD6'};letter-spacing:.04em">${s[0]}</div>
          <div class="abs" style="left:36px;top:186px;font-size:22px;color:#9DA2AC">${s[1]}</div>
        </div>`;
      }).join('') +
      `<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="supG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF6CA3"/><stop offset=".5" stop-color="#3D8BFF"/><stop offset="1" stop-color="#12E2AE"/></linearGradient></defs></svg>`;
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.5, c.b + 0.1));
    blurIn('supT', l, 0.25, 0.7, 20, 14);
    $('supT').style.opacity *= 1 - ex;
    $$('.sup', c.vis).forEach((el, i) => {
      const st = i < 2 ? 0.55 + i * 0.16 : 1.75 + (i - 2) * 0.2;
      popIn(el, l, st, { from: 0.7, dy: 30, freq: 2.0, damp: 0.55 });
      const dim = i < 2 ? lerp(1, 0.62, E.ioC(seg(l, 1.6, 2.1))) : 1;
      el.style.opacity = clamp((l - st) / 0.2) * dim * (1 - ex);
      if (i >= 2) {
        const g = 0.5 + 0.5 * Math.sin(l * 3 + i);
        el.style.boxShadow = `0 0 ${40 + 20 * g}px rgba(61,139,255,${0.28 * clamp((l - st) / 0.4)})`;
      }
    });
    // 新能力点亮时的火花
    const ctx = fx;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let q = 0; q < 2; q++) {
      const st = 1.75 + q * 0.2, k = seg(l, st, st + 1.1);
      if (k <= 0 || k >= 1) continue;
      const cx = 1040 + (q % 2) * 370 + 170, cy = 260 + 270 + 120;
      for (let i = 0; i < 26; i++) {
        const a = rnd(i * 3.3 + q) * TAU, sp = 140 + rnd(i * 7.1 + q) * 260;
        const x = cx + Math.cos(a) * sp * E.outC(k), y = cy + Math.sin(a) * sp * E.outC(k) * 0.8;
        const col = [C.pink, C.cyan, C.mint, C.yellow][i % 4];
        const r = 3 * (1 - k) + 1;
        ctx.fillStyle = rgba(col, 0.9 * (1 - k)); ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
      }
    }
    ctx.restore();
  },
};

/* ---------- 2023 · 大模型：会思考的神经球 ---------- */
const SPH = (() => {
  const N = 900, P = [], ga = PI * (3 - Math.sqrt(5));
  for (let i = 0; i < N; i++) {
    const y = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - y * y), th = i * ga;
    P.push([Math.cos(th) * r, y, Math.sin(th) * r]);
  }
  const E2 = [];
  for (let i = 0; i < N; i++) {
    const d = [];
    for (let j = 0; j < N; j++) if (j !== i) { const dx = P[i][0] - P[j][0], dy = P[i][1] - P[j][1], dz = P[i][2] - P[j][2]; d.push([dx * dx + dy * dy + dz * dz, j]); }
    d.sort((a, b) => a[0] - b[0]);
    for (let k = 0; k < 3; k++) if (d[k][1] > i) E2.push([i, d[k][1]]);
  }
  return { N, P, E: E2 };
})();
const TOKENS = ['写诗', '推理', '翻译', '总结', '规划', '写代码', '识图', '问答', '创作', '计算', '搜索', '日程'];
function sphereColor(p) { // 按经纬度在四个品牌色之间过渡
  const u = (Math.atan2(p[2], p[0]) / TAU + 1) % 1, v = (p[1] + 1) / 2;
  const cs = [[255, 108, 163], [10, 142, 248], [17, 230, 173], [252, 205, 1], [255, 108, 163]];
  const f = u * 4, i = Math.floor(f), k = f - i;
  const a = cs[i], b = cs[i + 1];
  const m = [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
  return m.map(x => Math.round(lerp(x, 255, 0.18 * v)));
}
VIS.llm = {
  cx: 1350, cy: 500, R: 300,
  build(c) {
    c.vis.innerHTML = TOKENS.map((w, i) => `<div data-sfx="token" class="abs tok" style="left:0;top:0;font-size:30px;font-weight:500;color:#EEF0F4;white-space:nowrap;letter-spacing:.04em">${w}</div>`).join('');
    c.cols = SPH.P.map(sphereColor);
  },
  proj(p, l, morph) {
    const { cx, cy, R } = this;
    const ay = l * 0.32, ax = 0.32 + 0.08 * Math.sin(l * 0.4);
    // 有机形变：像在“想”
    const wob = 1 + 0.07 * Math.sin(3 * p[0] + l * 1.6) * Math.sin(2.5 * p[1] - l * 1.1) + 0.04 * Math.sin(5 * p[2] + l * 2.3);
    let x = p[0] * wob, y = p[1] * wob, z = p[2] * wob;
    let x1 = x * Math.cos(ay) + z * Math.sin(ay), z1 = -x * Math.sin(ay) + z * Math.cos(ay);
    let y1 = y * Math.cos(ax) - z1 * Math.sin(ax), z2 = y * Math.sin(ax) + z1 * Math.cos(ax);
    const f = 2.6 / (2.6 + z2);
    return [cx + x1 * R * f, cy + y1 * R * f, z2, f];
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.6, c.b + 0.1));
    const ctx = fx;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    const S = SPH, pts = new Array(S.N);
    for (let i = 0; i < S.N; i++) {
      const p = this.proj(S.P[i], l, 1);
      // 入场：从四面八方飞来聚成球
      const st = 0.1 + rnd(i * 1.7) * 1.1, k = E.outQ4(seg(l, st, st + 1.3));
      const a0 = rnd(i * 3.1) * TAU, d0 = 900 + rnd(i * 5.3) * 700;
      const sx = this.cx + Math.cos(a0) * d0, sy = this.cy + Math.sin(a0) * d0 * 0.7;
      // 出场：向内塌缩成一点
      const x = lerp(lerp(sx, p[0], k), this.cx, ex), y = lerp(lerp(sy, p[1], k), this.cy, ex);
      pts[i] = [x, y, p[2], p[3], k * (1 - ex)];
    }
    // 连线
    ctx.lineWidth = 1;
    for (const [i, j] of S.E) {
      const a = pts[i], b = pts[j];
      const al = Math.min(a[4], b[4]) * (0.05 + 0.13 * (1 - (a[2] + b[2]) / 2) / 2);
      if (al < 0.01) continue;
      const col = c.cols[i];
      ctx.strokeStyle = `rgba(${col[0]},${col[1]},${col[2]},${al})`;
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    }
    // 沿边跑的“思维脉冲”
    for (let q = 0; q < 70; q++) {
      const e = S.E[Math.floor(rnd(q * 13.7 + Math.floor(l * 1.5 + rnd(q) * 3) * 0.37) * S.E.length)];
      const ph = (l * 1.5 + rnd(q)) % 1;
      const a = pts[e[0]], b = pts[e[1]];
      const x = lerp(a[0], b[0], ph), y = lerp(a[1], b[1], ph);
      const al = Math.sin(PI * ph) * Math.min(a[4], b[4]) * clamp((l - 1.4) / 0.6);
      if (al < 0.02) continue;
      const g = ctx.createRadialGradient(x, y, 0, x, y, 16);
      g.addColorStop(0, `rgba(255,255,255,${0.9 * al})`); g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.fillRect(x - 16, y - 16, 32, 32);
    }
    // 点
    for (let i = 0; i < S.N; i++) {
      const [x, y, z, f, a] = pts[i];
      if (a < 0.01) continue;
      const near = (1 - z) / 2;
      const col = c.cols[i];
      const r = (1.2 + 2.4 * near) * f;
      ctx.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${(0.35 + 0.65 * near) * a})`;
      ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    }
    // 球心的光
    const core = clamp((l - 1.2) / 0.8) * (1 - ex);
    const pulse = 0.75 + 0.25 * Math.sin(l * 2.4);
    const g = ctx.createRadialGradient(this.cx, this.cy, 0, this.cx, this.cy, 360);
    g.addColorStop(0, `rgba(140,170,255,${0.22 * core * pulse})`); g.addColorStop(1, 'rgba(140,170,255,0)');
    ctx.fillStyle = g; ctx.fillRect(this.cx - 360, this.cy - 360, 720, 720);
    ctx.restore();
    // 环绕的能力词（景深：远的糊、近的清楚）
    $$('.tok', c.vis).forEach((el, i) => {
      const a = (i / TOKENS.length) * TAU + l * 0.22;
      const tilt = 0.2;
      const x3 = Math.cos(a) * 1.5, z3 = Math.sin(a) * 1.1, y3 = Math.sin(a * 2 + i) * 0.22 + (i % 3 - 1) * 0.32;
      const y4 = y3 * Math.cos(tilt) - z3 * Math.sin(tilt), z4 = y3 * Math.sin(tilt) + z3 * Math.cos(tilt);
      const f = 3.4 / (3.4 + z4);
      const x = this.cx + x3 * this.R * f, y = this.cy + y4 * this.R * f;
      const near = clamp((1 - z4 / 1.1) / 2);
      const k = E.outQ4(seg(l, 1.5 + i * 0.08, 2.3 + i * 0.08)) * (1 - ex);
      el.style.opacity = k * (0.25 + 0.75 * near);
      el.style.transform = `translate(${x}px,${y}px) translate(-50%,-50%) scale(${0.6 + 0.6 * near})`;
      el.style.filter = `blur(${((1 - near) * 5 + (1 - k) * 10).toFixed(1)}px)`;
      el.style.zIndex = Math.round(near * 10);
    });
  },
};

/* ---------- 2024 · 上车：夜色里的速度 ---------- */
VIS.car = {
  build(c) {
    c.vis.innerHTML = `
    <div id="car" class="abs" style="left:960px;top:520px;width:800px;height:260px">
      <svg viewBox="-20 -20 800 260" width="800" height="260" style="overflow:visible">
        <defs>
          <linearGradient id="carBody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B4150"/><stop offset=".45" stop-color="#171A22"/><stop offset="1" stop-color="#07080B"/></linearGradient>
          <linearGradient id="carRim" x1="0" x2="1"><stop offset="0" stop-color="#FF6CA3"/><stop offset=".45" stop-color="#3D8BFF"/><stop offset="1" stop-color="#12E2AE"/></linearGradient>
          <linearGradient id="carGlass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2B3345"/><stop offset=".5" stop-color="#0C0F16"/><stop offset="1" stop-color="#1A2233"/></linearGradient>
          <radialGradient id="carBeam" cx="0" cy=".5" r="1"><stop offset="0" stop-color="#EAF3FF" stop-opacity=".55"/><stop offset="1" stop-color="#EAF3FF" stop-opacity="0"/></radialGradient>
          <filter id="beamBlur" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="16"/></filter><radialGradient id="carShadow"><stop offset="0" stop-color="#000" stop-opacity=".7"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
        </defs>
        <ellipse cx="380" cy="214" rx="420" ry="26" fill="url(#carShadow)"/>
        <path id="beam" d="M746 106 L1190 26 L1190 222 Z" fill="url(#carBeam)" opacity=".8" filter="url(#beamBlur)"/>
        <path d="M18 168 C10 140 14 118 40 110 C120 92 210 84 270 78 C320 46 390 22 470 20 C560 18 620 34 680 70 C720 86 748 98 760 118 C768 134 766 156 758 170 L700 172 A64 64 0 0 0 572 172 L238 172 A64 64 0 0 0 110 172 Z" fill="url(#carBody)"/>
        <path d="M40 110 C120 92 210 84 270 78 C320 46 390 22 470 20 C560 18 620 34 680 70 C720 86 748 98 760 118" fill="none" stroke="url(#carRim)" stroke-width="2.5" opacity=".95"/>
        <path d="M292 80 C335 52 395 34 466 32 C540 31 600 44 650 76 Z" fill="url(#carGlass)"/>
        <path d="M478 32 L470 80" stroke="#07080B" stroke-width="7"/>
        <path d="M300 80 L648 76" stroke="rgba(255,255,255,.08)" stroke-width="2"/>
        <rect x="728" y="104" width="30" height="7" rx="3.5" fill="#F4F8FF"/>
        <rect x="16" y="118" width="34" height="6" rx="3" fill="#FF3B5C"/>
        <ellipse cx="33" cy="121" rx="46" ry="16" fill="#FF3B5C" opacity=".22"/>
        <g class="wheel" data-cx="174" data-cy="172"><circle cx="174" cy="172" r="54" fill="#0B0C10"/><circle cx="174" cy="172" r="40" fill="#1E222B"/><g class="spk"></g><circle cx="174" cy="172" r="8" fill="#3A404C"/></g>
        <g class="wheel" data-cx="636" data-cy="172"><circle cx="636" cy="172" r="54" fill="#0B0C10"/><circle cx="636" cy="172" r="40" fill="#1E222B"/><g class="spk"></g><circle cx="636" cy="172" r="8" fill="#3A404C"/></g>
      </svg>
    </div>
    <div id="carCard" data-sfx="pop" class="card" style="left:1180px;top:250px;width:520px;height:150px;border-radius:30px;padding:0">
      <div style="position:absolute;left:28px;top:26px;font-size:22px;color:#9DA2AC;font-weight:500">后排左 · “小爱同学，有点冷”</div>
      <div id="carAns" data-sfx="type" style="position:absolute;left:28px;top:66px;font-size:30px;font-weight:600;color:#F2F3F5"></div>
    </div>`;
    $$('.wheel', c.vis).forEach(w => {
      const cx = +w.dataset.cx, cy = +w.dataset.cy;
      w.querySelector('.spk').innerHTML = Array.from({ length: 5 }, (_, i) => `<rect x="${cx - 4}" y="${cy - 38}" width="8" height="34" rx="4" fill="#5A6170" transform="rotate(${i * 72} ${cx} ${cy})"/>`).join('');
    });
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.55, c.b + 0.15));
    const inK = E.outQ4(seg(l, 0.1, 1.2));
    const speed = 1;
    // 背景光轨：城市灯光（上）+ 路面反光（下），视差向左飞掠
    const ctx = fx;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 70; i++) {
      const depth = rnd(i * 2.3);              // 0 远 1 近
      const y = i < 46 ? lerp(230, 640, rnd(i * 4.1)) : lerp(820, 960, rnd(i * 4.1));
      const v = lerp(500, 2600, depth) * speed;
      const len = lerp(60, 520, depth);
      const x = ((rnd(i * 7.7) * 2600 - l * v) % 2600 + 2600) % 2600 - 300;
      const col = [[255, 214, 160], [255, 120, 140], [120, 170, 255], [255, 255, 255], [17, 230, 173]][i % 5];
      const al = (0.12 + 0.5 * depth) * inK * (1 - ex) * (i < 46 ? 0.7 : 0.45);
      const g = ctx.createLinearGradient(x, 0, x + len, 0);
      g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(1, `rgba(${col},${al})`);
      ctx.strokeStyle = g; ctx.lineWidth = lerp(1.2, 4, depth); ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + len, y); ctx.stroke();
    }
    // 远处的光斑（散景）
    for (let i = 0; i < 26; i++) {
      const x = ((rnd(i * 9.1) * 2400 - l * 160) % 2400 + 2400) % 2400 - 200, y = lerp(300, 600, rnd(i * 3.3));
      const r = lerp(10, 34, rnd(i * 5.5));
      const col = [[255, 190, 120], [120, 170, 255], [255, 108, 163]][i % 3];
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, `rgba(${col},${0.16 * inK * (1 - ex)})`); g.addColorStop(1, `rgba(${col},0)`);
      ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
    }
    // 路面
    ctx.globalCompositeOperation = 'source-over';
    const rg = ctx.createLinearGradient(0, 760, 0, 1080);
    rg.addColorStop(0, `rgba(30,36,50,${0.6 * inK})`); rg.addColorStop(1, 'rgba(5,6,11,0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 735, W, 345);
    for (let i = 0; i < 8; i++) {
      const x = ((i * 300 - l * 1500) % 2400 + 2400) % 2400 - 300;
      ctx.fillStyle = `rgba(255,255,255,${0.35 * inK * (1 - ex)})`;
      ctx.fillRect(x, 812, 130, 5);
    }
    ctx.restore();
    // 车：从右侧滑入，轻微颠簸，轮子转动
    const car = $('car');
    const ck = spring(l - 0.15, 0.9, 0.75);
    const bob = Math.sin(l * 13) * 1.2 + Math.sin(l * 7.3) * 0.8;
    car.style.opacity = clamp(l / 0.3) * (1 - ex);
    car.style.transform = `translate(${(1 - ck) * 900 + ex * 700}px,${bob}px)`;
    $$('.spk', c.vis).forEach((s, i) => {
      const w = s.parentNode; s.setAttribute('transform', `rotate(${(l * 900) % 360} ${w.dataset.cx} ${w.dataset.cy})`);
    });
    $('beam').setAttribute('opacity', (0.65 + 0.1 * Math.sin(l * 3)) * clamp((l - 0.6) / 0.5));
    // 语音卡片
    const card = $('carCard');
    popIn(card, l, 1.55, { from: 0.8, dy: 20 });
    card.style.opacity = clamp((l - 1.55) / 0.2) * (1 - ex);
    const ans = '已为后排左侧打开座椅加热。';
    $('carAns').textContent = ans.slice(0, Math.floor(clamp((l - 2.2) / 1.0) * ans.length));
  },
};

/* ---------- 2025 · 看见：AI 眼镜 ---------- */
VIS.glasses = {
  build(c) {
    const lens = (x) => `<rect x="${x}" y="40" width="250" height="176" rx="70" fill="url(#gLens)" stroke="#0B0C10" stroke-width="22"/>`;
    c.vis.innerHTML = `
    <div id="gls" class="abs" style="left:1020px;top:330px;width:640px;height:260px;transform-origin:50% 50%">
      <svg viewBox="0 0 640 260" width="640" height="260" style="overflow:visible">
        <defs>
          <linearGradient id="gLens" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3A4762" stop-opacity=".85"/><stop offset=".55" stop-color="#121826" stop-opacity=".92"/><stop offset="1" stop-color="#26324A" stop-opacity=".85"/></linearGradient>
          <linearGradient id="gRim" x1="0" x2="1"><stop offset="0" stop-color="#FF6CA3"/><stop offset=".5" stop-color="#3D8BFF"/><stop offset="1" stop-color="#12E2AE"/></linearGradient>
        </defs>
        <path d="M30 70 L-30 64" stroke="#0B0C10" stroke-width="18" stroke-linecap="round"/>
        <path d="M610 70 L670 64" stroke="#0B0C10" stroke-width="18" stroke-linecap="round"/>
        ${lens(40)}${lens(350)}
        <path d="M290 92 C305 74 335 74 350 92" fill="none" stroke="#0B0C10" stroke-width="20"/>
        <rect x="40" y="40" width="250" height="176" rx="70" fill="none" stroke="url(#gRim)" stroke-width="2" opacity=".55"/>
        <rect x="350" y="40" width="250" height="176" rx="70" fill="none" stroke="url(#gRim)" stroke-width="2" opacity=".55"/>
        <path id="gGlint" d="M90 70 L150 70 L100 190 L40 190 Z" fill="#fff" opacity=".10"/>
        <circle cx="570" cy="58" r="7" fill="#1E2530"/><circle cx="570" cy="58" r="3.5" fill="#6FA8FF" id="gCam"/>
      </svg>
    </div>
    <div data-sfx="pop" class="card g25" style="left:1120px;top:150px;width:470px;height:118px"><div class="abs" style="left:26px;top:22px;font-size:20px;color:#9DA2AC">识别 · 你正在看的花</div><div class="abs" style="left:26px;top:56px;font-size:30px;font-weight:600">这是蓝花楹，花期 4–6 月</div></div>
    <div data-sfx="pop" class="card g25" style="left:1290px;top:650px;width:440px;height:118px"><div class="abs" style="left:26px;top:22px;font-size:20px;color:#9DA2AC">翻译 · 路牌</div><div class="abs" style="left:26px;top:56px;font-size:30px;font-weight:600">Exit → 出口在右前方</div></div>
    <div data-sfx="pop" class="card g25" style="left:930px;top:690px;width:330px;height:118px"><div class="abs" style="left:26px;top:22px;font-size:20px;color:#9DA2AC">小米 AI 眼镜</div><div class="abs" style="left:26px;top:56px;font-size:30px;font-weight:600">约 40 克 · ¥1999 起</div></div>`;
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.55, c.b + 0.1));
    const g = $('gls');
    const k = spring(l - 0.2, 1.1, 0.7);
    const ry = Math.sin(l * 0.7) * 10, rx = Math.sin(l * 0.5) * 4;
    g.style.opacity = clamp(l / 0.35) * (1 - ex);
    g.style.transform = `perspective(1600px) translateY(${(1 - k) * 160}px) rotateY(${ry}deg) rotateX(${rx}deg) scale(${lerp(0.8, 1, k) * (1 + 0.15 * ex)})`;
    $('gGlint').setAttribute('transform', `translate(${lerp(-60, 560, (l * 0.35) % 1)} 0)`);
    $('gCam').setAttribute('opacity', 0.5 + 0.5 * Math.sin(l * 6));
    // 取景框 + 识别卡片
    $$('.g25', c.vis).forEach((el, i) => {
      popIn(el, l, 1.3 + i * 0.55, { from: 0.75, dy: 24 });
      el.style.opacity = clamp((l - 1.3 - i * 0.55) / 0.2) * (1 - ex);
    });
    // 镜片前方的扫描线
    const ctx = fx;
    const sc = clamp((l - 0.9) / 0.4) * (1 - ex);
    if (sc > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const y = 360 + ((l * 160) % 200);
      const gr = ctx.createLinearGradient(0, y - 30, 0, y + 2);
      gr.addColorStop(0, 'rgba(61,139,255,0)'); gr.addColorStop(1, `rgba(120,190,255,${0.35 * sc})`);
      ctx.fillStyle = gr; ctx.fillRect(1060, y - 30, 560, 32);
      ctx.restore();
    }
  },
};

/* ---------- 2026 · 智能体：说一句，办成事 ---------- */
const STEPS26 = [
  ['搜索附近的火锅店', '已按评分和距离筛选'],
  ['预订周六 18:30 · 2 位', '已确认订座'],
  ['17:50 叫车到楼下', '已预约'],
  ['写进日程，提前提醒', '已添加'],
];
VIS.agent = {
  build(c) {
    c.vis.innerHTML = `
    <div id="ag" data-sfx="swipe" class="card" style="left:1060px;top:150px;width:700px;height:720px;border-radius:40px">
      <div data-sfx="bubble" class="bub me" style="right:34px;top:34px;font-size:27px">周六晚上订个火锅，两个人，再帮我叫车</div>
      <div class="abs" style="left:40px;top:150px;font-size:20px;color:#6E727B;letter-spacing:.08em" id="agPlan">小爱同学 · 正在规划</div>
      ${STEPS26.map((s, i) => `
      <div data-sfx="step" class="abs ag-step" style="left:34px;top:${200 + i * 118}px;width:632px;height:100px;border-radius:24px;background:#F5F6F8">
        <div class="abs ag-ic" style="left:22px;top:26px;width:48px;height:48px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 2px #E1E3E8"></div>
        <svg data-sfx="check" class="abs ag-ck" viewBox="0 0 48 48" width="48" height="48" style="left:22px;top:26px"><circle cx="24" cy="24" r="24" fill="${[C.pink, C.blue, C.mint, '#FF9E3D'][i]}"/><path d="M14 25 L21 32 L34 17" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="32" stroke-dashoffset="32"/></svg>
        <div class="abs" style="left:92px;top:20px;font-size:28px;font-weight:600;color:#0D0E12">${s[0]}</div>
        <div class="abs ag-st" style="left:92px;top:60px;font-size:20px;color:#6E727B">${s[1]}</div>
      </div>`).join('')}
      <div id="agDone" data-sfx="done" class="chip" style="position:absolute;left:34px;bottom:34px;background:#0D0E12;color:#fff;font-size:24px"><span class="dot" style="background:${C.mint}"></span>都办好了</div>
    </div>`;
  },
  render(c, t) {
    const l = t - c.a;
    const ex = E.inC(seg(t, c.b - 0.5, c.b + 0.15));
    const ag = $('ag');
    const k = spring(l - 0.25, 1.4, 0.66);
    ag.style.opacity = clamp((l - 0.2) / 0.3) * (1 - ex);
    ag.style.transform = `translateY(${(1 - k) * 140}px) scale(${lerp(0.92, 1, k) * (1 - 0.04 * ex)})`;
    ag.style.filter = ex > 0 ? `blur(${ex * 12}px)` : 'none';
    popIn(ag.querySelector('.bub'), l, 0.75, { from: 0.5 });
    blurIn('agPlan', l, 1.3, 0.4, 8, 6);
    $$('.ag-step', ag).forEach((s, i) => {
      const st = 1.5 + i * 0.62;
      s.style.opacity = E.outC(seg(l, st, st + 0.3));
      s.style.transform = `translateY(${(1 - E.outQ4(seg(l, st, st + 0.45))) * 26}px)`;
      const done = st + 0.45;
      const ck = s.querySelector('.ag-ck'), kk = spring(l - done, 2.6, 0.5);
      ck.style.opacity = clamp((l - done) / 0.1);
      ck.style.transform = `scale(${lerp(0.3, 1, kk)})`; ck.style.transformOrigin = '24px 24px';
      ck.querySelector('path').setAttribute('stroke-dashoffset', 32 * (1 - E.outC(seg(l, done + 0.05, done + 0.35))));
      s.querySelector('.ag-st').style.opacity = clamp((l - done) / 0.25);
    });
    popIn('agDone', l, 1.5 + 4 * 0.62 + 0.3, { from: 0.6, dy: 10 });
  },
};

/* ============================================================
 * 结尾
 * ============================================================ */
let FINLOGO, FINPTS;
function buildFinale() {
  const el = document.createElement('div');
  el.className = 'scene'; el.id = 'fin';
  el.innerHTML = `
    <div id="f9" class="abs" style="left:0;top:690px;width:1920px;text-align:center">
      <div id="f9a" style="font-weight:900;font-size:112px;line-height:1.1;letter-spacing:.02em">九年，</div>
      <div id="f9b" style="margin-top:18px;font-weight:400;font-size:40px;letter-spacing:.12em;color:#6E727B">从一句「小爱同学」开始。</div>
    </div>
    <div id="fMe" class="abs" style="left:0;top:716px;width:1920px;text-align:center;font-size:46px;font-weight:500;letter-spacing:.12em;color:#3A3D44">“小爱同学？”</div>
    <div id="fAi" class="abs" style="left:0;top:700px;width:1920px;text-align:center;font-weight:900;font-size:124px;letter-spacing:.06em"><span class="grad">一直在。</span></div>
    <div id="fEnd" class="abs" style="left:0;top:650px;width:1920px;text-align:center">
      <div style="font-weight:900;font-size:84px;letter-spacing:.1em">小爱同学</div>
      <div style="margin-top:14px;font-weight:300;font-size:30px;letter-spacing:.5em;color:#6E727B">2017 — 2026</div>
    </div>
    <div id="fNote" class="abs" style="left:0;top:1010px;width:1920px;text-align:center;font-size:18px;letter-spacing:.14em;color:#A4A8B0">非官方致敬短片 · 资料来自公开报道</div>`;
  SC.appendChild(el);
  FINLOGO = makeLogo(el, { height: 360, glow: true });
  FINPTS = logoPoints(2600, 3);
}
const FL = { x: 960, y: 420, h: 360 };
function finLogoState(t) {
  const l = t - FIN.a;
  const up = E.ioQ4(seg(l, 9.0, 10.2));          // 结尾卡：logo 上移变小
  return { x: 960, y: lerp(FL.y, 372, up), sc: lerp(1, 0.74, up) };
}
function renderFinale(t) {
  const el = $('fin');
  const on = t >= FIN.a - 0.1;
  show(el, on);
  if (!on) return;
  const l = t - FIN.a;
  const st = finLogoState(t);
  // --- 粒子从四周盘旋汇聚成 logo
  const form = 3.0;                                  // 汇聚完成时刻（相对 FIN.a）
  const pOut = E.inC(seg(l, form - 0.1, form + 0.5));
  if (l > 0.2 && pOut < 1) {
    const ctx = fx;
    ctx.save();
    const s = FL.h * st.sc;
    for (let i = 0; i < FINPTS.length; i++) {
      const p = FINPTS[i];
      const s0 = 0.25 + rnd(i * 1.37) * 0.9, d0 = 1.5 + rnd(i * 2.71) * 0.6;
      const k = E.ioC(seg(l, s0, s0 + d0)), k2 = E.ioC(seg(l - 0.04, s0, s0 + d0));
      if (k <= 0) continue;
      const a0 = rnd(i * 4.13) * TAU, r0 = 700 + rnd(i * 6.1) * 900, spin = 2.4 + rnd(i) * 1.2;
      const pos = kk => {
        const R = r0 * Math.pow(1 - kk, 1.6), a = a0 + spin * (1 - kk);
        return [st.x + p.x * s + Math.cos(a) * R, st.y + p.y * s + Math.sin(a) * R * 0.75];
      };
      const [x, y] = pos(k), [x2, y2] = pos(k2);
      const al = clamp(k * 3) * (1 - pOut);
      ctx.strokeStyle = `rgba(${p.r},${p.g},${p.b},${al})`;
      ctx.lineWidth = 3.2; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x + 0.01, y); ctx.stroke();
    }
    ctx.restore();
  }
  // --- 矢量 logo 接管
  const lk = E.outC(seg(l, form - 0.25, form + 0.35));
  FINLOGO.root.style.display = lk > 0 ? '' : 'none';
  const breathe = 1 + 0.012 * Math.sin(l * 2.2) * clamp(l - form);
  const listen = speechEnv(l, [[6.95, 1], [7.2, 0.8]]);  // “一直在”时 logo 轻轻一跳
  FINLOGO.place(st.x, st.y, st.sc * breathe * (1 + 0.035 * listen), 0, lk);
  FINLOGO.glowAmt(0.18 * lk + 0.25 * listen, 40);
  FINLOGO.shine(seg(l, form + 0.1, form + 0.9));
  // --- 文案节拍
  const f9 = $('f9');
  if (l < 6.0) {
    show(f9, true);
    charsIn($('f9a'), l, form + 0.25, { stagger: 0.08, dur: 0.7 });
    blurIn('f9b', l, form + 0.9, 0.8, 16, 12);
    const o = outro(f9, l, 5.2, 0.45, { scale: 0.03 });
    if (o <= 0) css(f9, { opacity: 1, filter: 'none', transform: 'none' });
  } else show(f9, false);
  const me = $('fMe');
  show(me, l > 5.5 && l < 7.3);
  if (l > 5.5 && l < 7.3) {
    blurIn(me, l, 5.65, 0.5, 12, 10);
    const o = E.inC(seg(l, 6.55, 6.85)); if (o > 0) { me.style.opacity = 1 - o; me.style.filter = `blur(${o * 12}px)`; }
  }
  const ai = $('fAi');
  show(ai, l > 6.7 && l < 9.4);
  if (l > 6.7 && l < 9.4) {
    charsIn(ai.querySelector('.grad'), l, 6.85, { stagger: 0.09, dur: 0.7, dy: 0.25, blur: 16 });
    ai.style.opacity = 1;
    const o = outro(ai, l, 8.75, 0.5, { scale: 0.03 });
    if (o <= 0) css(ai, { opacity: 1, filter: 'none', transform: 'none' });
  }
  const end = $('fEnd');
  show(end, l > 9.4);
  if (l > 9.4) {
    blurIn(end, l, 9.6, 0.9, 20, 14);
    blurIn('fNote', l, 10.4, 0.9, 0, 8);
  } else $('fNote').style.opacity = 0;
  // 波形：用户问、小爱答（亮底上用深色/四色）
  const ctx = fx;
  const uw = E.outQ4(seg(l, 5.5, 5.8)) * (1 - E.inQ(seg(l, 6.5, 6.8)));
  if (uw > 0.001) voiceWave(ctx, l, 960, 672, 300 * uw, 6 + 26 * speechEnv(l, [[5.75, 1], [5.95, .8], [6.15, .9], [6.35, .8]]), ['#3A3D44', '#8C919B'], 2, false);
  const aw = E.outQ4(seg(l, 6.75, 7.05)) * (1 - E.inQ(seg(l, 8.4, 8.9)));
  if (aw > 0.001) voiceWave(ctx, l * 1.1, 960, 672, 340 * aw, 6 + 34 * listen, [C.pink, C.blue, C.mint, C.yellow], 2.6, false);
  // 最后 0.6 秒淡到纸白
  const fade = E.inC(seg(t, FIN.b - 0.7, FIN.b));
  el.style.opacity = 1 - fade * 0.0;
}

/* ============================================================
 * 主渲染
 * ============================================================ */
function render(t) {
  window.__t = t;
  fx.clearRect(0, 0, W, H);
  topc.clearRect(0, 0, W, H);
  // 背景焦点随章节移动
  BG_FOCUS = t < CHAPTERS[0].a ? [960, 500] : [1300, 520];
  drawBG(t);
  renderIntro(t);
  renderLogoHUD(t);
  renderTitle(t);
  for (const c of CHAPTERS) {
    const on = t >= c.a - 0.05 && t < c.b + 0.35;
    show(c.el, on);
    if (!on) continue;
    renderChapterText(c, t);
    if (VIS[c.key] && VIS[c.key].render) VIS[c.key].render(c, t);
  }
  renderFinale(t);
  renderHUD(t);
}

/* ============================================================
 * 初始化：等字体（含所有要用到的字形子集）全部加载完再开始
 * ============================================================ */
function cueMap() {
  return {
    T: FILM.T, BAR, T0, TL, FIN,
    chapters: CHAPTERS.map(c => ({ key: c.key, y: c.y, a: c.a, b: c.b, dark: !!c.dark })),
    trans: BG_TRANS.map(({ a, b, to }) => ({ a, b, to })),
    intro: { me: [1.22, 1.44, 1.68, 1.9], ai: [2.62, 2.88], strokes: { yellow: [3.55, 4.25], pink: [3.7, 4.75], mint: [4.2, 4.95], blue: [4.5, 5.25] }, shine: 5.3, title: 6.05, dock: [8.7, 9.75] },
    fin: { form: FIN.a + 3.0, nine: FIN.a + 3.25, me: [5.75, 5.95, 6.15, 6.35].map(x => FIN.a + x), ai: [6.95, 7.2].map(x => FIN.a + x), end: FIN.a + 9.6 },
    mauCross: CHAPTERS.find(c => c.key === 'mau').a + 3.35,
    phoneToggle: CHAPTERS.find(c => c.key === 'phone').a + 3.9,
  };
}
async function init() {
  buildIntro();
  buildChapters();
  buildFinale();
  buildHUD();
  const text = (SC.textContent + HUD.textContent + '0123456789—→·，。、「」“”？！%+亿万年月日').replace(/\s+/g, '');
  const weights = [200, 300, 400, 500, 650, 700, 900];
  await Promise.all(weights.map(w => document.fonts.load(`${w} 40px MiSans`, text)));
  await document.fonts.ready;
  // 渐变字逐字拆开后修正渐变位置（需要可见才能量尺寸）
  $$('.scene').forEach(s => { s.style.display = 'block'; s.style.visibility = 'hidden'; });
  $$('.grad').forEach(el => { if (el.textContent.trim()) { splitChars(el); fixGradientChars(el); } });
  $$('.scene').forEach(s => { s.style.display = 'none'; s.style.visibility = ''; });
  render(0);
  window.__ready = true;
}
init();
