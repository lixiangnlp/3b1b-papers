/* 小爱同学 · 九年 —— 动画内核
 * 所有画面只由时间 t（秒）决定：不用 CSS 动画 / transition / setTimeout / Math.random，
 * 这样逐帧截图渲染出来的视频和浏览器里实时播放的一模一样。
 */
'use strict';

const W = 1920, H = 1080;
const PI = Math.PI, TAU = Math.PI * 2;

/* ---------- 数学 & 缓动 ---------- */
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));            // 区间进度 0..1
const smooth = x => x * x * (3 - 2 * x);
const E = {
  lin: x => x,
  inQ: x => x * x,
  outQ: x => 1 - (1 - x) * (1 - x),
  inC: x => x * x * x,
  outC: x => 1 - Math.pow(1 - x, 3),
  ioC: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outQ4: x => 1 - Math.pow(1 - x, 4),
  ioQ4: x => (x < 0.5 ? 8 * x * x * x * x : 1 - Math.pow(-2 * x + 2, 4) / 2),
  outX: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  inX: x => (x <= 0 ? 0 : Math.pow(2, 10 * x - 10)),
  ioX: x => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2),
  ioS: x => -(Math.cos(PI * x) - 1) / 2,
  outB: (x, s = 1.70158) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2),
};
/* 阻尼弹簧的阶跃响应（解析解，确定性）。dt = 开始后经过的秒数 */
function spring(dt, freq = 2.4, damp = 0.5) {
  if (dt <= 0) return 0;
  const w = TAU * freq, z = damp;
  if (z >= 1) return 1 - Math.exp(-w * dt) * (1 + w * dt);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * dt) * (Math.cos(wd * dt) + (z * w / wd) * Math.sin(wd * dt));
}
/* 确定性伪随机 */
function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453123; return x - Math.floor(x); }
function rnd2(i, j) { return rnd(i * 57.13 + j * 13.7 + 0.37); }
/* 平滑值噪声（1D），用于漂浮/呼吸 */
function noise1(x, seed = 0) {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  return lerp(rnd(i + seed * 101.3) * 2 - 1, rnd(i + 1 + seed * 101.3) * 2 - 1, u);
}

/* ---------- 颜色 ---------- */
function hex2rgb(h) { h = h.replace('#', ''); return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16)); }
function mixHex(a, b, k) { const A = hex2rgb(a), B = hex2rgb(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], k))).join(',')})`; }
function rgba(h, a) { const [r, g, b] = hex2rgb(h); return `rgba(${r},${g},${b},${a})`; }

/* 品牌色（取自 logo 渐变的实测值） */
const C = {
  coral: '#FF957B', pink: '#FF6CA3', cyan: '#02CBF8', blue: '#0A8EF8',
  yellow: '#FCCD01', mint: '#11E6AD', teal: '#06D6E2',
  ink: '#0D0E12', ink2: '#3A3D44', gray: '#6E727B', gray2: '#A4A8B0', line: '#E3E4E8',
  paper: '#F6F6F3', night: '#04050A',
};
const GRAD_TEXT = 'linear-gradient(100deg,#FF8A78 0%,#FF5F9E 22%,#3D8BFF 52%,#06C7F0 72%,#12E2AE 100%)';

/* ---------- DOM 小工具 ---------- */
const $ = id => document.getElementById(id);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
function css(el, o) { if (typeof el === 'string') el = $(el); if (!el) return; for (const k in o) el.style[k] = o[k]; return el; }
function show(el, on) { if (typeof el === 'string') el = $(el); const v = on ? (el.classList.contains('scene') ? 'block' : '') : 'none'; if (el.style.display !== v) el.style.display = v; }
function tf(x = 0, y = 0, s = 1, r = 0, extra = '') {
  return `translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) scale(${(+s).toFixed(4)}) rotate(${(+r).toFixed(3)}deg) ${extra}`;
}

/* 把元素里的文字拆成逐字 span，便于逐字入场 */
function splitChars(el) {
  if (el.dataset.split) return $$('.ch', el);
  const walk = node => {
    if (node.nodeType === 3) {
      const frag = document.createDocumentFragment();
      for (const ch of node.textContent) {
        const s = document.createElement('span');
        s.className = 'ch';
        s.textContent = ch;
        if (ch === ' ') s.style.whiteSpace = 'pre';
        frag.appendChild(s);
      }
      node.replaceWith(frag);
    } else if (node.nodeType === 1 && !node.classList.contains('nosplit')) {
      Array.from(node.childNodes).forEach(walk);
    }
  };
  Array.from(el.childNodes).forEach(walk);
  el.dataset.split = '1';
  return $$('.ch', el);
}
/* 渐变文字被拆成逐字 span 后，让每个字取整行渐变中对应的那一段 */
function fixGradientChars(line) {
  const chars = $$('.ch', line), w = line.getBoundingClientRect().width / (window.__stageScale || 1);
  const x0 = line.getBoundingClientRect().left;
  chars.forEach(c => {
    const dx = (c.getBoundingClientRect().left - x0) / (window.__stageScale || 1);
    c.style.backgroundImage = getComputedStyle(line).backgroundImage;
    c.style.backgroundSize = `${w}px 100%`;
    c.style.backgroundPosition = `${-dx}px 0`;
    c.style.webkitBackgroundClip = 'text';
    c.style.backgroundClip = 'text';
    c.style.color = 'transparent';
  });
  line.style.backgroundImage = 'none';
}

/* 逐字入场：上移 + 去模糊 + 淡入；返回最后一个字的进度 */
function charsIn(el, t, a, o = {}) {
  const chars = splitChars(el);
  const st = o.stagger ?? 0.035, dur = o.dur ?? 0.55, dy = o.dy ?? 0.55, blur = o.blur ?? 10, ease = o.ease || E.outQ4;
  let k = 0;
  chars.forEach((c, i) => {
    k = ease(seg(t, a + i * st, a + i * st + dur));
    c.style.opacity = k;
    c.style.transform = `translateY(${((1 - k) * dy).toFixed(3)}em)`;
    c.style.filter = k < 0.999 ? `blur(${((1 - k) * blur).toFixed(2)}px)` : 'none';
  });
  return k;
}
/* 整块模糊入场 */
function blurIn(el, t, a, dur = 0.6, dy = 26, blur = 14) {
  if (typeof el === 'string') el = $(el);
  const k = E.outQ4(seg(t, a, a + dur));
  el.style.opacity = k;
  el.style.filter = k < 0.999 ? `blur(${((1 - k) * blur).toFixed(2)}px)` : 'none';
  el.style.transform = `translateY(${((1 - k) * dy).toFixed(2)}px)`;
  return k;
}
/* 弹性弹出 */
function popIn(el, t, a, o = {}) {
  if (typeof el === 'string') el = $(el);
  const dt = t - a, s0 = o.from ?? 0.6, f = o.freq ?? 2.6, d = o.damp ?? 0.48;
  const k = spring(dt, f, d);
  const op = clamp(dt / (o.fade ?? 0.18));
  el.style.opacity = op;
  el.style.transform = `${o.pre || ''} translateY(${((1 - k) * (o.dy ?? 0)).toFixed(2)}px) scale(${lerp(s0, 1, k).toFixed(4)})`;
  return k;
}
/* 场景出场：模糊 + 淡出 + 轻微放大 */
function outro(el, t, a, dur = 0.45, o = {}) {
  if (typeof el === 'string') el = $(el);
  const k = E.inC(seg(t, a, a + dur));
  if (k <= 0) return 0;
  el.style.opacity = 1 - k;
  el.style.filter = `blur(${(k * (o.blur ?? 16)).toFixed(2)}px)`;
  if (o.scale !== false) el.style.transform = `scale(${1 + k * (o.scale ?? 0.05)}) translateY(${(-k * (o.dy ?? 0)).toFixed(1)}px)`;
  return k;
}

/* ---------- 里程计式年份 ---------- */
class Odometer {
  constructor(el, digits = 4) {
    this.el = el; this.cols = [];
    el.innerHTML = '';
    for (let i = 0; i < digits; i++) {
      const col = document.createElement('span');
      col.className = 'odo-col';
      col.innerHTML = '<span class="odo-d a">0</span><span class="odo-d b">1</span><span class="odo-sizer">0</span>';
      el.appendChild(col);
      this.cols.push(col);
    }
  }
  /* v: 连续数值（例如 2017.3 表示正在从 2017 滚到 2018），speed: 用于运动模糊 */
  set(v, speed = 0) {
    const n = this.cols.length;
    for (let i = 0; i < n; i++) {
      const p = Math.pow(10, n - 1 - i);
      // 带进位的里程计：低位从 9→10 的那段小数传给高位
      const base = Math.floor(v / p);
      const lower = v - base * p;
      const carry = p === 1 ? v - Math.floor(v) : clamp((lower - (p - 1)) / 1);
      const cur = ((base % 10) + 10) % 10, nxt = (cur + 1) % 10;
      const f = p === 1 ? v - Math.floor(v) : carry;
      const col = this.cols[i], a = col.children[0], b = col.children[1];
      if (a.textContent !== String(cur)) a.textContent = cur;
      if (b.textContent !== String(nxt)) b.textContent = nxt;
      const off = (f * 100).toFixed(3);
      a.style.transform = `translateY(${-off}%)`;
      b.style.transform = `translateY(${100 - off}%)`;
      const bl = f > 0.001 && f < 0.999 ? Math.min(6, speed * 0.9) : 0;
      const flt = bl > 0.05 ? `blur(${bl.toFixed(2)}px)` : 'none';
      a.style.filter = flt; b.style.filter = flt;
    }
  }
}

/* ---------- 数字滚动 ---------- */
function fmtInt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

/* ---------- 画布 ---------- */
function ctx2d(id) { const c = $(id); return c.getContext('2d'); }
