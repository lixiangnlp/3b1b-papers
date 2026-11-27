/* 小爱同学 logo：由原图几何重建（顶部正圆弧 + 两条外切线 + 右下正圆 + 拟合三次贝塞尔）。
 * 坐标系与原 447×447 图一致。四个色层叠放：粉（整个轮廓）< 蓝 < 黄、薄荷绿，统一被轮廓裁切。
 * 每层带一条“笔刷中线”蒙版，可以做丝带一笔画出来的动画。
 */
'use strict';

const LOGO = {
  sil: 'M183.223 118.401A50.150 50.150 0 0 1 270.378 116.717L350.765 251.825A64.470 64.470 0 0 1 248.315 328.871C235.321 315.004 215.904 293.724 195.120 283.390C172.994 303.307 157.803 349.190 122.740 349.190C89.321 349.190 73.777 319.659 88.490 292.604Z',
  // 粉色只露出顶部“帽子”：蓝色上沿曲线以上（向下多留 3 个单位，避免拼接缝）
  cap: 'M20 239.326L113.547 239.326L133.413 216.847C189.308 153.603 293.258 186.327 341.910 242.587L361.533 265.279L430 265.279L430 0L20 0Z',
  // 蓝色丝带：蓝色上沿以下、黄/绿上沿以上（向下多留 3）
  band: 'M20 236.326L113.547 236.326L133.413 213.847C189.308 150.603 293.258 183.327 341.910 239.587L361.533 262.279L430 262.279L430 292.102L370.481 292.102L357.100 270.985C316.584 207.046 235.691 227.527 195.120 286.390C160.390 262.962 107.302 262.974 85.000 305.400L73.368 327.529L20 327.529Z',
  blue: 'M20 236.326L113.547 236.326L133.413 213.847C189.308 150.603 293.258 183.327 341.910 239.587L361.533 262.279L430 262.279L430 440L20 440Z',
  yellow: 'M20 324.529L73.368 324.529L85.000 302.400C107.302 259.974 160.390 259.962 195.120 283.390L195.120 440L20 440Z',
  mint: 'M195.120 283.390C235.691 224.527 316.584 204.046 357.100 267.985L370.481 289.102L430 289.102L430 440L195.120 440Z',
  grads: {
    pink: { p1: [308.4, 139.1], p2: [144.72, 163.95], stops: [[0, '#FF6CA3'], [0.167, '#FF6CA3'], [0.333, '#FF6E9F'], [0.5, '#FF7D91'], [0.667, '#FE8F84'], [0.833, '#FF957C'], [1, '#FF957B']] },
    blue: { p1: [304.17, 279.98], p2: [141.39, 195.75], stops: [[0, '#0A8EF8'], [0.167, '#098EFE'], [0.333, '#0896FE'], [0.5, '#07A3FD'], [0.667, '#05B2FB'], [0.833, '#04C2FA'], [1, '#02CBF8']] },
    yellow: { p1: [178.87, 314.63], p2: [90.8, 299.56], stops: [[0, '#FCCD01'], [1, '#FCCD03']] },
    mint: { p1: [253.58, 328.35], p2: [321.2, 242.98], stops: [[0, '#11E6AD'], [0.167, '#11E5B1'], [0.333, '#0EE1B9'], [0.5, '#0DDEC4'], [0.667, '#09DBCE'], [0.833, '#07D8DA'], [1, '#06D6E2']] },
  },
  // 笔刷中线（画丝带用）：[路径, 笔宽]
  strokes: {
    yellow: ['M92 330C110 306 150 286 205 286', 96],
    pink: ['M128 246C150 200 182 132 227 128C272 132 304 196 348 256', 132],
    mint: ['M190 283C232 300 262 344 300 336C350 326 366 270 330 240', 128],
    blue: ['M360 268C326 222 280 196 228 200C172 206 128 238 92 296', 116],
  },
  // 轮廓包围盒（几何计算值）
  bx: 83.8, by: 92.2, bw: 276.0, bh: 257.1,
  cx: 221.8, cy: 220.75,
};
const LAYERS = ['pink', 'blue', 'yellow', 'mint'];

let __logoSeq = 0;
/* 生成一个 logo 实例。返回 {root, svg, set(state)}；root 绝对定位、以 logo 中心为原点 */
function makeLogo(parent, opt = {}) {
  const id = 'lg' + (++__logoSeq);
  const h = opt.height || 300;                 // logo 渲染高度（px）
  const s = h / LOGO.bh;
  const pad = opt.pad ?? 40;                   // 给光晕留的余量（logo 单位）
  const vb = [LOGO.bx - pad, LOGO.by - pad, LOGO.bw + 2 * pad, LOGO.bh + 2 * pad];
  const wpx = vb[2] * s, hpx = vb[3] * s;
  const g = LOGO.grads;
  const grad = n => `<linearGradient id="${id}g${n}" gradientUnits="userSpaceOnUse" x1="${g[n].p1[0]}" y1="${g[n].p1[1]}" x2="${g[n].p2[0]}" y2="${g[n].p2[1]}">${g[n].stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</linearGradient>`;
  const mask = n => `<mask id="${id}m${n}" maskUnits="userSpaceOnUse" x="0" y="0" width="447" height="447"><path d="${LOGO.strokes[n][0]}" fill="none" stroke="#fff" stroke-width="${LOGO.strokes[n][1]}" stroke-linecap="round" stroke-linejoin="round"/></mask>`;
  const body = (withMask) => `
    <g clip-path="url(#${id}sil)">
      <g ${withMask ? `mask="url(#${id}mpink)"` : ''} class="Lpink"><g clip-path="url(#${id}cap)"><rect x="60" y="60" width="330" height="330" fill="url(#${id}gpink)"/></g></g>
      <g ${withMask ? `mask="url(#${id}mblue)"` : ''} class="Lblue"><g clip-path="url(#${id}band)"><path d="${LOGO.blue}" fill="url(#${id}gblue)"/></g></g>
      <g ${withMask ? `mask="url(#${id}myellow)"` : ''} class="Lyellow"><path d="${LOGO.yellow}" fill="url(#${id}gyellow)"/></g>
      <g ${withMask ? `mask="url(#${id}mmint)"` : ''} class="Lmint"><path d="${LOGO.mint}" fill="url(#${id}gmint)"/></g>
      ${withMask ? `<rect class="shine" x="-120" y="60" width="110" height="360" fill="url(#${id}shine)" opacity="0"/>` : ''}
    </g>`;
  const defs = `<defs>${LAYERS.map(grad).join('')}${LAYERS.map(mask).join('')}
    <clipPath id="${id}sil"><path d="${LOGO.sil}"/></clipPath>
    <clipPath id="${id}cap"><path d="${LOGO.cap}"/></clipPath>
    <clipPath id="${id}band"><path d="${LOGO.band}"/></clipPath>
    <linearGradient id="${id}shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  </defs>`;
  const root = document.createElement('div');
  root.className = 'logo-inst';
  root.style.cssText = `position:absolute;left:0;top:0;width:0;height:0;`;
  const mk = (cls, withMask) => `<svg class="${cls}" xmlns="http://www.w3.org/2000/svg" viewBox="${vb.join(' ')}" width="${wpx}" height="${hpx}"
      style="position:absolute;left:${-(LOGO.cx - vb[0]) * s}px;top:${-(LOGO.cy - vb[1]) * s}px;overflow:visible">${withMask ? defs : ''}${body(true)}</svg>`;
  root.innerHTML = (opt.glow ? mk('logo-glow', false) : '') + mk('logo-main', true);
  parent.appendChild(root);
  const main = root.querySelector('.logo-main');
  const glow = root.querySelector('.logo-glow');
  const maskPaths = {};
  LAYERS.forEach(n => {
    const p = main.querySelector(`#${id}m${n} path`);
    const L = p.getTotalLength();
    maskPaths[n] = { p, L };
    p.style.strokeDasharray = `${L + 1} ${L + 1}`;
  });
  const shine = main.querySelector('.shine');
  const layerEls = {}; LAYERS.forEach(n => { layerEls[n] = $$(`.L${n}`, root); });
  let maskOn = true;
  const api = {
    root, main, glow, id, s, h,
    /* 设置各层“画出”的进度 0..1 */
    reveal(pr) {
      const all = LAYERS.every(n => (pr[n] ?? 1) >= 1);
      if (all !== !maskOn) {
        // 全部画完后拿掉蒙版：更清晰、更省
        maskOn = !all;
        LAYERS.forEach(n => layerEls[n].forEach(el => el.setAttribute('mask', maskOn ? `url(#${id}m${n})` : 'none')));
      }
      LAYERS.forEach(n => {
        const k = pr[n] ?? 1, { p, L } = maskPaths[n];
        p.style.strokeDashoffset = ((1 - k) * (L + 1)).toFixed(2);
        layerEls[n].forEach(el => { const v = k > 0 ? '' : 'hidden'; if (el.style.visibility !== v) el.style.visibility = v; });
      });
    },
    /* 笔刷头位置（logo 单位），用来放高光粒子 */
    head(n, k) { const { p, L } = maskPaths[n]; const q = p.getPointAtLength(clamp(k) * L); return [q.x, q.y]; },
    shine(k) { // k: 0..1 扫光进度
      if (!shine) return;
      if (k <= 0 || k >= 1) { shine.setAttribute('opacity', 0); return; }
      const x = lerp(-40, 420, E.ioS(k));
      shine.setAttribute('opacity', Math.sin(PI * k) * 0.95);
      shine.setAttribute('transform', `translate(${x} 0) rotate(18 0 220)`);
    },
    /* 位置：(x,y) 为 logo 中心在父容器中的像素坐标 */
    place(x, y, sc = 1, rot = 0, op = 1) {
      root.style.transform = `translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) scale(${sc.toFixed(4)}) rotate(${rot.toFixed(2)}deg)`;
      root.style.opacity = op;
    },
    glowAmt(a, blurPx = 34) {
      if (!glow) return;
      glow.style.opacity = a;
      glow.style.filter = `blur(${blurPx}px) saturate(1.35)`;
      glow.style.display = a > 0.002 ? '' : 'none';
    },
  };
  api.reveal({});
  return api;
}

/* 在离屏画布上画出 logo，按面积均匀采样 n 个点（带颜色），坐标单位：logo 高度=1，中心为原点 */
function logoPoints(n, seed = 1) {
  const S = 2, cw = 447 * S;
  const cv = document.createElement('canvas'); cv.width = cw; cv.height = cw;
  const x = cv.getContext('2d');
  x.scale(S, S);
  const g = LOGO.grads;
  const lg = nm => { const q = g[nm]; const gr = x.createLinearGradient(q.p1[0], q.p1[1], q.p2[0], q.p2[1]); q.stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  x.save(); x.clip(new Path2D(LOGO.sil));
  x.fillStyle = lg('pink'); x.fillRect(0, 0, 447, 447);
  x.save(); x.clip(new Path2D(LOGO.band)); x.fillStyle = lg('blue'); x.fill(new Path2D(LOGO.blue)); x.restore();
  x.fillStyle = lg('yellow'); x.fill(new Path2D(LOGO.yellow));
  x.fillStyle = lg('mint'); x.fill(new Path2D(LOGO.mint));
  x.restore();
  const img = x.getImageData(0, 0, cw, cw).data;
  const pts = [];
  let i = 0, tries = 0;
  while (pts.length < n && tries < n * 30) {
    tries++;
    const px = LOGO.bx + rnd(seed * 1000 + i * 2.13) * LOGO.bw, py = LOGO.by + rnd(seed * 777 + i * 3.71 + 0.5) * LOGO.bh;
    i++;
    const ix = Math.floor(px * S), iy = Math.floor(py * S), o = (iy * cw + ix) * 4;
    if (img[o + 3] < 250) continue;
    pts.push({ x: (px - LOGO.cx) / LOGO.bh, y: (py - LOGO.cy) / LOGO.bh, r: img[o], g: img[o + 1], b: img[o + 2] });
  }
  return pts;
}
