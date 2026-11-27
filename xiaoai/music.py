#!/usr/bin/env python3
"""《小爱同学 · 九年》原创配乐 + 音效（numpy 合成，无任何采样素材）。

读 build/cues.json（render.js cues 生成），按画面卡点作曲，输出 build/music.wav（44.1 kHz 立体声）。
结构：
  开场（自由节奏）  “小爱同学”四个音节 = 四音动机；“我在”= 两音回应；丝带画 logo = 四段琶音；光铺满 = 和弦绽放
  第一幕 2017–2021  112.5 BPM，D 大调 I–V–vi–IV，每章 3 小节，切章落在强拍
  第二幕 2023–2025  暗场：先只有低频心跳和“神经元”铃声，再进入小调推进的律动
  第三幕 2026–结尾  回到大调；粒子汇聚时上行闪烁，logo 成形时主和弦落地；结尾重奏四音动机，“一直在”收束到主音
"""
import json
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
C = json.load(open('build/cues.json'))
M, EV = C['map'], C['events']
T = M['T']
N = int(SR * (T + 0.6))
BAR, T0 = M['BAR'], M['T0']
BEAT = BAR / 4
rng = np.random.default_rng(20170726)
CH = {c['key']: c for c in M['chapters']}
FIN = M['FIN']
DARK_A = CH['llm']['a']           # 暗场开始（强拍）
DARK_B = CH['agent']['a']         # 回到亮场（强拍）
FIN_A = FIN['a']

BUSES = ['drums', 'bass', 'pad', 'keys', 'bells', 'fx', 'sub']
B = {k: np.zeros((N, 2), np.float32) for k in BUSES}


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(max(d, 0.001) * SR)) / SR


def add(bus, sig, t, pan=0.0, gain=1.0):
    i = int(round(t * SR))
    if i >= N or len(sig) == 0:
        return
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        s2 = np.stack([sig * np.cos(a), sig * np.sin(a)], 1) * np.sqrt(2)
    else:
        s2 = sig
    if i < 0:
        s2 = s2[-i:]
        i = 0
    j = min(N, i + len(s2))
    B[bus][i:j] += (s2[:j - i] * gain).astype(np.float32)


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR / 2 - 100) / (SR / 2), output='sos'), x, axis=0)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc / (SR / 2), 'high', output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x, axis=0)


# ------------------------------------------------------------------ 乐器
def mallet(f, d=1.2, bright=1.0, hard=1.0):
    """木琴/钢片琴混合：基频 + 非谐泛音，高频衰减更快"""
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.6)
    s += 0.42 * bright * np.sin(2 * np.pi * f * 2.0 * t + 0.3) * np.exp(-t * 5.5)
    s += 0.22 * bright * hard * np.sin(2 * np.pi * f * 3.98 * t + 0.7) * np.exp(-t * 11)
    s += 0.08 * bright * hard * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 24)
    return s * np.minimum(1, t / 0.0025)


def bell(f, d=2.8, idx=2.4, ratio=3.5):
    """FM 铃：明亮、带一点金属感"""
    t = tt(d)
    I = idx * np.exp(-t * 3.2)
    s = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * ratio * t))
    s += 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 2.2)
    return s * np.exp(-t * 1.25) * np.minimum(1, t / 0.002)


def saw_stack(f, t, n=10, det=0.0):
    s = np.zeros_like(t)
    for k in range(1, n + 1):
        if f * k > 9000:
            break
        s += np.sin(2 * np.pi * f * (1 + det) * k * t + k * 0.37) / k
    return s


def pad(midis, d, att=0.8, rel=1.2, bright=1600, gain=1.0):
    """宽厚的合成垫音：每个音三支微失谐锯齿，左右声道失谐不同，低通柔化"""
    t = tt(d + rel)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    for m in midis:
        f = hz(m)
        for j, det in enumerate((-0.0042, 0.0, 0.0047)):
            ph = (j + 1) * 1.7
            L += saw_stack(f, t + ph * 0.001, 9, det)
            R += saw_stack(f, t + ph * 0.0013, 9, -det * 0.9)
    env = np.minimum(1, t / att) * np.clip((d + rel - t) / rel, 0, 1)
    x = np.stack([L, R], 1) * env[:, None]
    x = lp(x, bright, 2)
    return x / (len(midis) * 3) * gain


def bass(f, d, drive=1.8):
    t = tt(d)
    s = 0.55 * np.tanh(drive * np.sin(2 * np.pi * f * t)) + 0.75 * np.sin(2 * np.pi * 2 * f * t) + 0.45 * np.sin(2 * np.pi * 3 * f * t + 0.5) + 0.2 * np.sin(2 * np.pi * 4 * f * t)
    env = np.minimum(1, t / 0.006) * (0.35 + 0.65 * np.exp(-t * 5)) * np.clip((d - t) / 0.04, 0, 1)
    return s * env


def kick(punch=1.0):
    t = tt(0.36)
    f = 56 + 120 * np.exp(-t * 40)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)
    s += 0.3 * np.sin(2 * np.pi * 2 * np.cumsum(f) / SR) * np.exp(-t * 20)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 240) * 0.55 * punch
    return s + click


def clap():
    t = tt(0.24)
    n = bp(rng.standard_normal(len(t)), 900, 4200)
    e = np.exp(-t * 22) + sum(np.exp(-(t - k * 0.011) * 190) * (t >= k * 0.011) for k in range(3)) * 0.45
    return n * e * 0.9


def hat(d=0.06, open_=False):
    t = tt(d if not open_ else 0.28)
    return hp(rng.standard_normal(len(t)), 7200, 3) * np.exp(-t * (60 if not open_ else 14))


def shaker():
    t = tt(0.07)
    return bp(rng.standard_normal(len(t)), 3500, 11000) * np.sin(np.pi * t / 0.07) ** 2


def crash(d=2.4):
    t = tt(d)
    n = hp(rng.standard_normal((len(t), 2)), 4200, 2)
    return n * (np.exp(-t * 2.2) * np.minimum(1, t / 0.004))[:, None] * 0.5


def sub_boom(d=2.6, f0=72, f1=34):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    s += 0.25 * np.sin(2 * 2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)   # 二次谐波：小喇叭也能“感觉”到
    return s * np.minimum(1, t / 0.008)


def noise_sweep(d, lo0, hi0, lo1, hi1, shape='rise', segs=24, stereo=True):
    """分段带通的噪声扫频（上升 riser / 下降 / 呼啸）"""
    n = int(d * SR)
    out = np.zeros((n, 2))
    src = rng.standard_normal((n, 2))
    edges = np.linspace(0, n, segs + 1).astype(int)
    xf = int(0.02 * SR)
    for i in range(segs):
        a, b = max(0, edges[i] - xf), min(n, edges[i + 1] + xf)
        k = (i + 0.5) / segs
        lo, hi = lo0 + (lo1 - lo0) * k, hi0 + (hi1 - hi0) * k
        seg = bp(src[a:b], lo, hi, 2)
        w = np.ones(b - a)
        w[:min(xf, b - a)] = np.linspace(0, 1, min(xf, b - a))
        w[-min(xf, b - a):] = np.minimum(w[-min(xf, b - a):], np.linspace(1, 0, min(xf, b - a)))
        out[a:b] += seg * w[:, None]
    t = np.arange(n) / SR
    if shape == 'rise':
        env = (t / d) ** 2.2
    elif shape == 'swell':
        env = np.sin(np.pi * t / d) ** 2
    else:
        env = np.exp(-t * 3 / d)
    return out * env[:, None]


def riser(d):
    x = noise_sweep(d, 300, 900, 3000, 9000, 'rise')
    t = tt(d)
    f = 180 + 1400 * (t / d) ** 2
    s = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 1.5
    return x * 0.6 + np.stack([s, s], 1)


def whoosh(d=0.6, pan_from=-0.6, pan_to=0.6):
    x = noise_sweep(d, 400, 1800, 1500, 6000, 'swell')
    m = x.mean(1)
    p = np.linspace(pan_from, pan_to, len(m))
    a = (p + 1) * np.pi / 4
    return np.stack([m * np.cos(a), m * np.sin(a)], 1) * 1.6


def rev_swell(d=1.0):
    t = tt(d)
    n = hp(rng.standard_normal((len(t), 2)), 3000)
    return n * ((t / d) ** 3)[:, None] * 0.6


def tick():
    t = tt(0.03)
    n = bp(rng.standard_normal(len(t)), 1800, 7000) * np.exp(-t * 420)
    s = 0.5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 300)
    return (n + s) * 0.9


def pop(f0=520, f1=1250, d=0.1):
    t = tt(d)
    f = f0 + (f1 - f0) * np.sqrt(t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * np.minimum(1, t / 0.002)


def blip(f=880, up=1.33, d=0.16):
    t = tt(d)
    fr = f * (1 + (up - 1) * (1 - np.exp(-t * 60)))
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) + 0.25 * np.sin(2 * np.pi * 2 * np.cumsum(fr) / SR)) * np.exp(-t * 26) * np.minimum(1, t / 0.002)


def typeclick():
    t = tt(0.012)
    return bp(rng.standard_normal(len(t)), 2500, 8000) * np.exp(-t * 600)


# ------------------------------------------------------------------ 和声
DMAJ = [62, 64, 66, 67, 69, 71, 73]
PENTA = [62, 64, 66, 69, 71]                       # D 大调五声
CH_LIGHT = [('D', [50, 57, 62, 66], 38, [74, 78, 81, 86]),
            ('A', [49, 57, 61, 64], 45, [73, 76, 81, 85]),
            ('Bm', [50, 54, 59, 62], 47, [71, 74, 78, 83]),
            ('G', [50, 55, 59, 62], 43, [71, 74, 79, 83])]
CH_DARK = [CH_LIGHT[2], CH_LIGHT[3], CH_LIGHT[0], CH_LIGHT[1]]   # Bm–G–D–A

ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def bar_t(n):
    return T0 + n * BAR


def light_groove(b0, b1, prog=CH_LIGHT, intensity=1.0, arp=True, bassline=True):
    for n in range(b0, b1):
        name, padv, root, tones = prog[n % 4]
        tb = bar_t(n)
        add('pad', pad(padv, BAR, att=0.25, rel=0.6, bright=2200, gain=1.0), tb, gain=0.40 * intensity)
        for b in range(4):
            x = tb + b * BEAT
            if b in (0, 2):
                add('drums', kick(), x, gain=0.40 * intensity)
            if b in (1, 3):
                add('drums', clap(), x, pan=0.06, gain=0.34 * intensity)
            add('drums', hat(), x + BEAT / 2, pan=0.28, gain=0.46 * intensity)
            add('drums', shaker(), x + BEAT / 4, pan=-0.3, gain=0.11 * intensity)
            add('drums', shaker(), x + 3 * BEAT / 4, pan=-0.3, gain=0.14 * intensity)
        if n % 2 == 1:
            add('drums', kick(0.6), tb + 2.5 * BEAT, gain=0.2 * intensity)
        if bassline:
            for (off, mul, dur, g) in [(0, 1, 0.9, 1), (1.5, 2, 0.45, 0.7), (2, 1, 0.9, 0.9), (3.5, 1.5, 0.45, 0.6)]:
                add('bass', bass(hz(root) * mul, BEAT * dur), tb + off * BEAT, gain=0.19 * g * intensity)
        if arp:
            for i in range(8):
                note = tones[ARP[i]]
                acc = 1.15 if i % 4 == 0 else 0.85
                add('keys', mallet(hz(note), 0.9, bright=1.15), tb + i * BEAT / 2, pan=0.32 if i % 2 else -0.32, gain=0.16 * acc * intensity)


def dark_groove(b0, b1):
    for n in range(b0, b1):
        name, padv, root, tones = CH_DARK[(n - b0) % 4]
        tb = bar_t(n)
        add('pad', pad([v - 0 for v in padv], BAR, att=0.4, rel=0.8, bright=1300), tb, gain=0.30)
        for b in range(4):
            x = tb + b * BEAT
            add('drums', kick(0.8), x, gain=0.46)
            if b in (1, 3):
                add('drums', clap(), x, pan=-0.05, gain=0.30)
            for s16 in range(4):
                add('drums', hat(0.04), x + s16 * BEAT / 4, pan=0.25 if s16 % 2 else -0.15, gain=0.17 if s16 % 2 else 0.10)
            # 反拍低音（推进感）
            add('bass', bass(hz(root), BEAT * 0.42, drive=2.6), x + BEAT / 2, gain=0.17)
            add('bass', bass(hz(root + 12), BEAT * 0.2, drive=2.2), x + 3 * BEAT / 4, gain=0.09)
        # 高处的琶音铃
        for i in range(8):
            if (i + n) % 3 == 0:
                add('bells', bell(hz(tones[ARP[i]] + 12), 1.4, idx=1.6), tb + i * BEAT / 2, pan=0.45 if i % 2 else -0.45, gain=0.045)


# ------------------------------------------------------------------ 开场（自由节奏）
def intro():
    # 低沉的 D 持续音，慢慢升起
    add('pad', pad([38, 45, 50], 3.0, att=2.0, rel=1.2, bright=700), 0.0, gain=0.42)
    add('fx', noise_sweep(3.2, 2000, 5000, 4000, 9000, 'swell'), 0.1, gain=0.05)
    # “小爱同学”= 四音动机（A4 D5 F#5 A5），“我在”= 回应（F#5 → D5）
    for t_, m in zip(M['intro']['me'], [69, 74, 78, 81]):
        add('keys', mallet(hz(m), 1.2, bright=0.6, hard=0.4), t_ - 0.02, gain=0.24)
    for t_, m in zip(M['intro']['ai'], [78, 74]):
        add('bells', bell(hz(m), 3.0), t_ - 0.02, gain=0.24)
        add('bells', bell(hz(m + 12), 2.0, idx=1.2), t_ - 0.01, pan=0.3, gain=0.07)
    add('pad', pad([50, 57, 62, 64, 66], 3.4, att=0.5, rel=1.6, bright=1500), 2.55, gain=0.30)
    # 丝带画 logo：每条丝带一串上行琶音 + 一声“唰”
    runs = {'yellow': 62, 'pink': 66, 'mint': 69, 'blue': 74}
    for nm, (a, b) in M['intro']['strokes'].items():
        add('fx', whoosh(b - a + 0.25, -0.5, 0.5), a - 0.08, gain=0.10)
        base = runs[nm]
        for k in range(7):
            m = base + [0, 2, 4, 5, 7, 9, 12][k]
            add('keys', mallet(hz(m + 12), 0.8, bright=1.0), a + k * (b - a) / 9, pan=(k - 3) / 6, gain=0.08)
    # 扫光：一把铃
    sh = M['intro']['shine']
    for k, m in enumerate([86, 90, 93, 98]):
        add('bells', bell(hz(m), 1.8, idx=1.0), sh + k * 0.06, pan=(k - 1.5) * 0.3, gain=0.05)
    # 光铺满：反向镲吸入 + 和弦绽放 + 低频
    fa, fb = M['TL']['flood']
    add('fx', rev_swell(0.9), fa - 0.9, gain=0.22)
    add('sub', sub_boom(2.8, 64, 34), fa, gain=0.32)
    add('pad', pad([50, 57, 62, 66, 69, 76], 3.6, att=0.12, rel=2.0, bright=2600), fa, gain=0.38)
    add('drums', crash(3.0), fa, gain=0.22)
    # 标题四个字
    for k, m in enumerate([74, 78, 81, 86]):
        add('keys', mallet(hz(m), 1.4, bright=0.8), M['intro']['title'] + k * 0.07, pan=(k - 1.5) * 0.25, gain=0.13)
    add('pad', pad([43, 50, 55, 59, 62], 2.2, att=0.6, rel=0.8, bright=1500), 7.2, gain=0.22)
    # 停靠 → 第一章强拍之前的上升
    add('fx', riser(T0 - 7.9), 7.9, gain=0.16)
    add('pad', pad([45, 52, 57, 61, 64], 1.4, att=0.4, rel=0.3, bright=1800), T0 - 1.6, gain=0.20)


# ------------------------------------------------------------------ 编曲
def arrangement():
    n_light = round((DARK_A - T0) / BAR)               # 第一幕小节数
    light_groove(0, n_light - 1)
    # 第一幕最后一小节：鼓的加花 + 上升，冲进暗场
    tb = bar_t(n_light - 1)
    light_groove(n_light - 1, n_light, intensity=0.9, arp=True)
    for k in range(16):
        add('drums', clap(), tb + k * BEAT / 4, pan=(k % 2 - 0.5) * 0.2, gain=0.05 + 0.25 * (k / 15) ** 2)
    add('fx', riser(BAR + 0.2), tb, gain=0.26)
    # 章节强拍：镲 + 和弦重音
    for c in M['chapters']:
        if c['key'] in ('speaker',):
            add('drums', crash(2.6), c['a'], gain=0.30)
            add('sub', sub_boom(1.6, 80, 40), c['a'], gain=0.20)
        elif not c['dark'] and c['key'] != 'agent':
            add('drums', crash(1.8), c['a'], gain=0.16)
    # ---- 暗场：大模型（4 小节）
    a = DARK_A
    add('sub', sub_boom(3.6, 70, 30), a, gain=0.5)
    add('fx', noise_sweep(2.5, 200, 800, 80, 300, 'decay'), a, gain=0.25)
    add('pad', pad([47, 54, 59, 61, 66], BAR * 2, att=1.2, rel=1.5, bright=900), a, gain=0.42)
    add('pad', pad([43, 50, 55, 59, 66], BAR * 2, att=1.0, rel=1.5, bright=1100), a + 2 * BAR, gain=0.40)
    for k in range(8 * 4):                              # 心跳
        x = a + BAR + k * BEAT
        if x > a + 4 * BAR - 0.05:
            break
        if k % 2 == 0:
            add('drums', kick(0.3), x, gain=0.34)
            add('drums', kick(0.2), x + 0.16, gain=0.2)
    # 神经元：越来越密的五声音阶铃
    for i in range(70):
        u = (i / 70) ** 0.7
        x = a + 0.6 + u * (4 * BAR - 1.2) + rng.uniform(-0.05, 0.05)
        m = [71, 74, 76, 78, 81, 83, 86, 88][rng.integers(0, 8)]
        add('bells', bell(hz(m + 12), 2.2, idx=1.3), x, pan=rng.uniform(-0.8, 0.8), gain=0.018 + 0.03 * u)
    add('fx', riser(BAR * 1.0), a + 3 * BAR, gain=0.22)
    # ---- 暗场律动：上车 → 超级小爱 → 眼镜
    nb = round((CH['car']['a'] - T0) / BAR)
    ne = round((DARK_B - T0) / BAR)
    dark_groove(nb, ne)
    add('fx', whoosh(1.2, 0.8, -0.8), CH['car']['a'] - 0.2, gain=0.3)
    add('drums', crash(2.4), CH['car']['a'], gain=0.28)
    add('sub', sub_boom(1.6, 80, 40), CH['car']['a'], gain=0.26)
    add('drums', crash(2.4), CH['super']['a'], gain=0.24)
    add('fx', riser(1.7), CH['super']['a'] + 0.15, gain=0.14)
    add('drums', crash(2.0), CH['glasses']['a'], gain=0.2)
    # 回到亮场：吸气 + 大调
    tr = [x for x in M['trans'] if x['to'] == 'light'][-1]
    add('fx', rev_swell(1.1), DARK_B - 1.1, gain=0.25)
    add('drums', crash(2.8), DARK_B, gain=0.3)
    nf = round((FIN_A - T0) / BAR)
    light_groove(ne, nf, intensity=1.0)
    finale()


def finale():
    a = FIN_A
    fm = M['fin']
    # 鼓停，长垫音 + 粒子上升的闪烁
    add('pad', pad([43, 50, 55, 62, 64, 69], 1.6, att=0.3, rel=1.0, bright=1600), a, gain=0.32)
    add('pad', pad([45, 52, 57, 62, 64, 69], 1.6, att=0.6, rel=0.8, bright=1800), a + 1.5, gain=0.30)
    add('fx', riser(fm['form'] - a - 0.3), a + 0.3, gain=0.18)
    k = 0
    x = a + 0.35
    while x < fm['form'] - 0.05:                       # 越来越快的上行闪烁
        u = (x - a) / (fm['form'] - a)
        m = [74, 76, 78, 81, 83, 86, 88, 90, 93][k % 9] + (12 if u > 0.6 else 0)
        add('bells', bell(hz(m), 1.4, idx=1.0), x, pan=np.sin(k * 1.7) * 0.7, gain=0.03 + 0.04 * u)
        x += 0.16 * (1 - 0.75 * u)
        k += 1
    # logo 成形：主和弦落地
    f = fm['form']
    add('sub', sub_boom(3.4, 70, 34), f, gain=0.4)
    add('drums', crash(3.4), f, gain=0.28)
    add('pad', pad([38, 50, 57, 62, 66, 69, 76], 5.6, att=0.06, rel=2.5, bright=2400), f, gain=0.40)
    for i, m in enumerate([86, 90, 93, 98, 102]):
        add('bells', bell(hz(m), 2.4, idx=1.2), f + 0.05 + i * 0.07, pan=(i - 2) * 0.3, gain=0.06)
    # “九年，”：一句旋律
    for i, (dt, m) in enumerate([(0.0, 78), (0.35, 81), (0.7, 86), (1.4, 85), (1.75, 81)]):
        add('keys', mallet(hz(m), 1.6, bright=0.7), fm['nine'] + dt, gain=0.16)
    # 结尾的问答：四音动机再来一次，然后落到主音
    add('pad', pad([43, 50, 55, 59, 62], 1.7, att=0.4, rel=0.8, bright=1200), fm['me'][0] - 0.4, gain=0.22)
    for t_, m in zip(fm['me'], [69, 74, 78, 81]):
        add('keys', mallet(hz(m), 1.2, bright=0.6, hard=0.4), t_ - 0.02, gain=0.22)
    for i, (t_, m) in enumerate(zip(fm['ai'] + [fm['ai'][-1] + 0.25], [78, 76, 74])):
        add('bells', bell(hz(m), 3.4), t_ - 0.02, gain=0.24)
    add('pad', pad([38, 50, 57, 62, 66, 69], 6.5, att=0.3, rel=3.0, bright=1800), fm['ai'][0] - 0.05, gain=0.36)
    add('sub', sub_boom(2.4, 60, 36), fm['ai'][0], gain=0.18)
    # 片尾卡：最后一个和弦
    e = fm['end']
    add('pad', pad([38, 45, 50, 57, 62, 64, 66, 69], T - e + 0.4, att=0.8, rel=2.5, bright=1600), e, gain=0.30)
    for i, m in enumerate([74, 78, 81, 86, 88]):
        add('bells', bell(hz(m), 3.4, idx=0.9), e + 0.3 + i * 0.12, pan=(i - 2) * 0.25, gain=0.045)


# ------------------------------------------------------------------ 音效（按画面卡点）
def sfx():
    last = {}
    tile_i = 0
    tok_i = 0
    for t_, kind in EV:
        # 同类音效最小间隔，避免机关枪
        gap = {'tick': 0.035, 'type': 0.05, 'tile': 0.05}.get(kind, 0.03)
        if t_ - last.get(kind, -9) < gap:
            continue
        last[kind] = t_
        dark = DARK_A - 0.4 <= t_ < DARK_B - 0.4
        if kind == 'tick':
            g = 0.10 if t_ < T0 + 1.2 else 0.22
            add('fx', tick(), t_, pan=0.2, gain=g)
        elif kind == 'bubble':
            add('fx', blip(740, 1.25), t_, pan=0.25, gain=0.17)
        elif kind == 'bubble2':
            add('fx', blip(990, 1.33), t_, pan=-0.2, gain=0.16)
            add('bells', bell(hz(86), 1.2, idx=0.8), t_ + 0.02, gain=0.03)
        elif kind == 'chip':
            add('fx', pop(560, 1300), t_, pan=0.1, gain=0.12)
        elif kind == 'note':
            m = PENTA[int(t_ * 7) % 5] + 12
            add('keys', mallet(hz(m), 0.8), t_, pan=0.4, gain=0.07)
        elif kind == 'pop':
            add('fx', pop(480, 1150), t_, gain=0.16)
        elif kind == 'type':
            add('fx', typeclick(), t_, pan=0.15, gain=0.05)
        elif kind == 'hub':
            add('fx', pop(300, 760, 0.16), t_, gain=0.2)
            add('sub', sub_boom(0.6, 110, 60), t_, gain=0.12)
        elif kind == 'tile':
            m = DMAJ[tile_i % 7] + 12 + 12 * (tile_i // 7)
            add('fx', pop(hz(m) * 0.7, hz(m), 0.08), t_, pan=np.sin(tile_i * 1.9) * 0.6, gain=0.07)
            tile_i += 1
        elif kind == 'token':
            m = [71, 74, 76, 78, 81, 83][tok_i % 6] + 12
            add('bells', bell(hz(m), 1.8, idx=1.0), t_, pan=np.sin(tok_i * 2.3) * 0.7, gain=0.05)
            tok_i += 1
        elif kind == 'superhot':
            add('fx', noise_sweep(0.7, 2000, 6000, 5000, 12000, 'swell'), t_ - 0.1, gain=0.10)
            add('bells', bell(hz(81 + (5 if tile_i % 2 else 0)), 2.0, idx=1.4), t_, gain=0.10)
            tile_i += 1
        elif kind == 'swipe':
            add('fx', whoosh(0.5, -0.3, 0.3), t_ - 0.1, gain=0.12)
        elif kind == 'step':
            add('fx', pop(420, 900, 0.08), t_, gain=0.08)
        elif kind == 'check':
            add('keys', mallet(hz(81), 0.6, bright=1.1), t_ + 0.02, gain=0.15)
            add('keys', mallet(hz(88), 0.8, bright=1.1), t_ + 0.08, gain=0.13)
        elif kind == 'done':
            for i, m in enumerate([74, 78, 81, 86]):
                add('bells', bell(hz(m + 12), 1.8, idx=1.0), t_ + i * 0.06, pan=(i - 1.5) * 0.3, gain=0.06)
    # 画面里的其他动作
    ph = CH['phone']['a']
    add('fx', whoosh(0.45, 0.0, 0.0), ph + 1.05, gain=0.12)                       # 小爱面板升起
    add('fx', pop(900, 1500, 0.05), M['phoneToggle'], gain=0.14)                  # 闹钟开关
    mc = M['mauCross']
    for i, m in enumerate([81, 86, 90, 93]):                                      # 月活破亿
        add('bells', bell(hz(m + 12), 2.0, idx=1.1), mc + i * 0.05, pan=(i - 1.5) * 0.3, gain=0.06)
    add('drums', crash(1.6), mc, gain=0.10)


# ------------------------------------------------------------------ 混音
def reverb_ir(d=2.6, pre=0.02, damp=6000):
    t = tt(d)
    ir = rng.standard_normal((len(t), 2)) * np.exp(-t * 6.9 / d)[:, None]
    ir = lp(ir, damp, 1)
    ir[:int(pre * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0)).max()
    return ir


def mix():
    intro()
    arrangement()
    sfx()
    ir = reverb_ir()
    wet = {'pad': 0.30, 'keys': 0.26, 'bells': 0.42, 'fx': 0.16, 'drums': 0.06}
    out = np.zeros((N, 2))
    # 侧链：底鼓压一下垫音和低音，让节奏“呼吸”
    duck = np.ones(N)
    # （从鼓总线的低频包络近似底鼓位置）
    kick_env = np.abs(lp(B['drums'].mean(1), 120, 2))
    kick_env = np.convolve(kick_env, np.ones(int(0.01 * SR)) / int(0.01 * SR), 'same')
    kick_env /= kick_env.max() + 1e-9
    duck = 1 - 0.35 * np.clip(kick_env * 3, 0, 1)
    for k in BUSES:
        x = B[k].astype(np.float64)
        if k in ('pad', 'bass'):
            x *= duck[:, None]
        if k in wet:
            w = np.stack([fftconvolve(x[:, i], ir[:, i])[:N] for i in range(2)], 1)
            x = x * (1 - wet[k] * 0.5) + w * wet[k]
        out += x
    out = hp(out, 32, 2)
    out = out - 0.45 * lp(out, 95, 2)          # 低频搁架衰减：别让底鼓/低音吃掉外放的余量
    out = out + 0.55 * bp(out, 2200, 7000, 1)  # 一点“临场感”，小喇叭上更清楚
    out = lp(out, 15000, 1)
    t = np.arange(N) / SR
    out *= (np.minimum(1, t / 0.05) * np.clip((T + 0.3 - t) / 1.4, 0, 1))[:, None]
    pk = np.abs(out).max()
    out = np.tanh(out / pk * 1.25) / np.tanh(1.25) * 0.89
    from scipy.io import wavfile
    wavfile.write('build/music.wav', SR, (out * 32767).astype(np.int16))
    # 频谱占比自检（中频为主，笔记本/手机外放才听得清）
    m = out.mean(1)
    seg = m[int(SR * 12):int(SR * 42)]
    F = np.abs(np.fft.rfft(seg)) ** 2
    fr = np.fft.rfftfreq(len(seg), 1 / SR)
    rep = {f'{a}-{b}': round(100 * F[(fr >= a) & (fr < b)].sum() / F.sum(), 1) for a, b in [(0, 120), (120, 400), (400, 2000), (2000, 6000), (6000, 22050)]}
    print('spectrum % (12–42s):', rep)
    print('wrote build/music.wav', round(N / SR, 2), 's')


if __name__ == '__main__':
    mix()
