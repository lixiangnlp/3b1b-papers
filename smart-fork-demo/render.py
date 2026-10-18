"""First-person 'smart fork' camera render of eating a steak salad, bite by bite.

Camera is rigidly mounted on the fork neck looking along the tines (like the
reference smart-spoon video). World units are centimetres.
World: table plane z=0 textured with the salad photo, diner's face is a vertical
plane at y=YF facing +y, room is an environment map.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_IMG = os.environ.get('SALAD_IMG', os.path.join(HERE, 'steak_salad.png'))

W, H = 960, 544
FPS = 24
HFOV = math.radians(74.0)
K1 = 0.16                      # barrel distortion
TANH = math.tan(HFOV / 2)
RNG = np.random.default_rng(7)

S = 0.065                      # cm per photo px
TS = 4                         # texture upscale
XM, YF, ZM = 0.0, -32.0, 30.0  # mouth centre / face plane
Y_EDGE = -20.0                 # near edge of table
LIGHT = np.array([0.25, 0.30, 1.0]); LIGHT /= np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- utilities

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def box_blur(img, r, axis):
    if r < 1:
        return img
    n = img.shape[axis]
    pad = [(0, 0)] * img.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(img, pad, mode='edge')
    c = np.cumsum(p, axis=axis, dtype=np.float32)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def gblur(img, sigma):
    """Approximate Gaussian with three box passes."""
    if sigma < 0.4:
        return img
    r = max(1, int(round(math.sqrt(12 * sigma * sigma / 3 + 1) / 2)))
    out = img.astype(np.float32)
    for _ in range(3):
        out = box_blur(out, r, 0)
        out = box_blur(out, r, 1)
    return out


def bilinear(img, u, v):
    h, w = img.shape[:2]
    u = np.clip(u, 0, w - 1.001); v = np.clip(v, 0, h - 1.001)
    x0 = u.astype(np.int32); y0 = v.astype(np.int32)
    fx = (u - x0); fy = (v - y0)
    if img.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def value_noise(shape, scale, seed):
    r = np.random.default_rng(seed)
    small = r.random((shape[0] // scale + 3, shape[1] // scale + 3)).astype(np.float32)
    im = Image.fromarray(small).resize((small.shape[1] * scale, small.shape[0] * scale), Image.BICUBIC)
    return np.asarray(im)[:shape[0], :shape[1]]

# ---------------------------------------------------------------- camera rays

def make_rays(w, h):
    xs = (np.arange(w) + 0.5) / w * 2 - 1
    ys = ((np.arange(h) + 0.5) / h * 2 - 1) * (h / w)
    X, Y = np.meshgrid(xs, ys)
    f = 1 + K1 * (X * X + Y * Y)
    D = np.stack([X * f * TANH, Y * f * TANH, np.ones_like(X)], -1)
    return (D / np.linalg.norm(D, axis=-1, keepdims=True)).astype(np.float32)


def project_cam(P):
    """camera-space points (...,3) -> pixel coords (approximate inverse distortion)."""
    z = np.maximum(P[..., 2], 1e-3)
    xu = P[..., 0] / z / TANH; yu = P[..., 1] / z / TANH
    ru = np.sqrt(xu * xu + yu * yu) + 1e-9
    rd = ru.copy()
    for _ in range(6):
        rd = ru / (1 + K1 * rd * rd)
    s = rd / ru
    px = (xu * s + 1) * 0.5 * W
    py = (yu * s * (W / H) + 1) * 0.5 * H
    return px, py

# ---------------------------------------------------------------- fork rig
# fork frame: x right, y forward along fork, z up (normal of top surface).
ALPHA = math.radians(25.0)            # camera tilt below fork axis
CAM_F = np.array([0.0, -3.3, 2.2])   # camera position in fork frame
ANCHOR = np.array([0.0, 1.9, 0.12])   # where food sits on the tines
_zc = np.array([0, math.cos(ALPHA), -math.sin(ALPHA)])
_yc = np.array([0, -math.sin(ALPHA), -math.cos(ALPHA)])
M_FC = np.stack([np.array([1.0, 0, 0]), _yc, _zc], 1)   # fork_from_cam
TINE_X = np.array([-1.125, -0.375, 0.375, 1.125])
GAP_X = np.array([-0.75, 0.0, 0.75])
S_TIP = 3.9
SX0, SX1, SS0, SS1 = -6.0, 6.0, -10.0, 12.0   # shadow silhouette domain


def fork_h(s):
    return 0.03 * np.maximum(s, 0) ** 2 - 0.10 * np.maximum(-s - 3.2, 0)


def fork_dh(s):
    return 0.06 * np.maximum(s, 0) - 0.10 * (s < -3.2)


def fork_shape(x, s):
    """inside mask (float), top-surface relief dz and d(dz)/dx."""
    hw = 0.55 + 0.74 * smoothstep(-3.4, -0.5, s)
    palm = (s <= 0.0) & (np.abs(x) < hw) & (s > -12)
    inside = palm.astype(np.float32)
    dz = np.zeros_like(x); ddx = np.zeros_like(x)
    ax = np.abs(x)
    e = smoothstep(hw - 0.22, hw, ax)
    dz = np.where(palm, -0.07 * e, dz)
    ddx = np.where(palm, -0.07 * 6 * np.sign(x) * e * (1 - e) / 0.22 * 0.5, ddx)
    # tines
    w = 0.165 - 0.035 * np.clip(s / S_TIP, 0, 1)
    taper = np.sqrt(np.clip((S_TIP - s) / 0.5, 0, 1))
    w = w * np.where(s > S_TIP - 0.5, taper, 1.0)
    for xc in TINE_X:
        q = (x - xc) / np.maximum(w, 1e-3)
        t = (s > 0) & (s < S_TIP) & (np.abs(q) < 1)
        inside = np.where(t, 1.0, inside)
        dz = np.where(t, 0.06 * (1 - q * q), dz)
        ddx = np.where(t, -0.12 * q / np.maximum(w, 1e-3), ddx)
    # fillets at the bottom of the gaps
    for gc in GAP_X:
        g = (s > 0) & (s < 0.21) & (np.abs(x - gc) < 0.21) & (((x - gc) ** 2 + (s - 0.21) ** 2) > 0.21 ** 2)
        inside = np.where(g, 1.0, inside)
    return inside, dz, ddx


def render_fork():
    ss = 2
    D = make_rays(W * ss, H * ss)
    Df = D @ M_FC.T
    C = CAM_F
    t = (0.0 - C[2]) / np.minimum(Df[..., 2], -1e-4)
    for _ in range(8):
        s = C[1] + t * Df[..., 1]
        t = (fork_h(s) - C[2]) / np.minimum(Df[..., 2], -1e-4)
    P = C + t[..., None] * Df
    inside, dz, ddx = fork_shape(P[..., 0], P[..., 1])
    inside = inside * (t > 0) * (t < 30)
    n = np.stack([-ddx, -fork_dh(P[..., 1]), np.ones_like(ddx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    # anti-aliased downsample
    def down(a):
        if a.ndim == 2:
            return a.reshape(H, ss, W, ss).mean((1, 3))
        return a.reshape(H, ss, W, ss, a.shape[-1]).mean((1, 3))
    m = down(inside)
    wsum = np.maximum(m, 1e-4)
    def wdown(a):
        if a.ndim == 2:
            return down(a * inside) / wsum
        return down(a * inside[..., None]) / wsum[..., None]
    n2 = wdown(n); n2 /= np.maximum(np.linalg.norm(n2, axis=-1, keepdims=True), 1e-6)
    return dict(mask=m.astype(np.float32), t=wdown(t).astype(np.float32),
                n=n2.astype(np.float32), P=wdown(P).astype(np.float32))


def fork_silhouette():
    """top-down silhouette of the fork in (x,s) for shadow casting."""
    res = 0.025
    xs = np.arange(SX0, SX1, res); ss = np.arange(SS0, SS1, res)
    X, Sg = np.meshgrid(xs, ss)
    m, _, _ = fork_shape(X, Sg)
    return m.astype(np.float32), res

# ---------------------------------------------------------------- textures

def load_photo():
    im = Image.open(SRC_IMG).convert('RGB')
    big = im.resize((im.width * TS, im.height * TS), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    a = np.asarray(big).astype(np.float32) / 255.0
    # subtle fine grain so magnified food doesn't look plastic
    g = value_noise(a.shape[:2], 2, 11) - 0.5
    a = np.clip(a * (1 + 0.06 * g[..., None]), 0, 1)
    return a


def poly_mask(shape, poly, feather=1.5):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon([(x * TS, y * TS) for x, y in poly], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather * TS / 2))
    return np.asarray(m).astype(np.float32) / 255.0


def ellipse_poly(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def inpaint(tex, mask, dark=0.85, seed=0):
    """normalised-convolution fill of the masked area + grain."""
    m = (mask > 0.02).astype(np.float32)
    keep = 1 - m
    out = tex.copy()
    acc = np.zeros_like(tex); wacc = np.zeros(tex.shape[:2], np.float32)
    for sg in (6, 14, 30, 60):
        num = gblur(tex * keep[..., None], sg); den = gblur(keep, sg)
        fill = num / np.maximum(den[..., None], 1e-4)
        wgt = np.clip(den * 3, 0, 1) * (1 - np.clip(wacc, 0, 1))
        acc += fill * wgt[..., None]; wacc += wgt
    fill = acc / np.maximum(wacc[..., None], 1e-4)
    r = np.random.default_rng(seed)
    grain = gblur(r.random(tex.shape[:2]).astype(np.float32), 2.5) - 0.5
    grain2 = gblur(r.random(tex.shape[:2]).astype(np.float32), 8) - 0.5
    fill = fill * dark * (1 + 1.2 * grain[..., None] + 1.5 * grain2[..., None])
    mm = mask[..., None]
    return np.clip(out * (1 - mm) + fill * mm, 0, 1)


def build_pyramid(a):
    pyr = [a]
    for _ in range(4):
        b = pyr[-1]
        h, w = b.shape[0] // 2 * 2, b.shape[1] // 2 * 2
        b = b[:h, :w]
        pyr.append(0.25 * (b[0::2, 0::2] + b[1::2, 0::2] + b[0::2, 1::2] + b[1::2, 1::2]))
    return pyr


def make_env():
    """equirectangular room map, values roughly linear-ish 0..2"""
    ew, eh = 1024, 512
    az = (np.arange(ew) + 0.5) / ew * 2 * np.pi - np.pi
    el = np.pi / 2 - (np.arange(eh) + 0.5) / eh * np.pi
    AZ, EL = np.meshgrid(az, el)
    wall = np.array([0.46, 0.44, 0.45])
    ceil = np.array([0.78, 0.78, 0.80])
    floor = np.array([0.20, 0.18, 0.18])
    up = smoothstep(math.radians(28), math.radians(50), EL)[..., None]
    dn = smoothstep(math.radians(-20), math.radians(-45), EL)[..., None]
    env = wall * (1 - up) + ceil * up
    env = env * (1 - dn) + floor * dn
    # wall variation, furniture, window and ceiling lamp
    env *= (0.85 + 0.3 * value_noise((eh, ew), 64, 3))[..., None]
    def rect(a0, a1, e0, e1, col, soft=0.03):
        m = (smoothstep(math.radians(a0) - soft, math.radians(a0) + soft, AZ) *
             (1 - smoothstep(math.radians(a1) - soft, math.radians(a1) + soft, AZ)) *
             smoothstep(math.radians(e0) - soft, math.radians(e0) + soft, EL) *
             (1 - smoothstep(math.radians(e1) - soft, math.radians(e1) + soft, EL)))[..., None]
        return env * (1 - m) + np.array(col) * m
    env = rect(-150, -118, -8, 32, [1.35, 1.40, 1.55])      # window behind diner
    env = rect(-147, -121, 10, 12, [0.5, 0.5, 0.55], 0.01)   # window bar
    env = rect(120, 165, -28, 18, [0.16, 0.13, 0.12])        # dark cabinet
    env = rect(20, 60, -18, 4, [0.30, 0.27, 0.25])           # sofa back
    env = rect(-40, -25, -30, 40, [0.62, 0.58, 0.52])        # door
    lamp = np.exp(-(((AZ - 0.6) ** 2) + ((EL - 1.05) ** 2)) / 0.02)[..., None]
    env = env + lamp * np.array([1.6, 1.5, 1.3])
    env = gblur(env.astype(np.float32), 3)
    return env.astype(np.float32)


def sample_env(env, D):
    eh, ew = env.shape[:2]
    az = np.arctan2(D[..., 1], D[..., 0]); el = np.arcsin(np.clip(D[..., 2], -1, 1))
    u = (az + np.pi) / (2 * np.pi) * ew - 0.5
    v = (np.pi / 2 - el) / np.pi * eh - 0.5
    return bilinear(env, u % ew, v)

# ---------------------------------------------------------------- face

FN = None


def face_color(x, z, b, a):
    """x,z relative to mouth centre (cm). b,a = mouth opening half height / width.
    returns rgb, alpha(face silhouette), portal mask"""
    global FN
    if FN is None:
        FN = (value_noise((1024, 1024), 24, 21) - 0.5).astype(np.float32)
        FN = FN + 0.5 * (value_noise((1024, 1024), 6, 22) - 0.5)
        FN = gblur(FN, 3.0) + 0.05 * gblur(np.random.default_rng(24).random((1024, 1024)).astype(np.float32) - 0.5, 1.2)
    skin = np.array([0.80, 0.60, 0.52], np.float32)
    # head silhouette
    hx, hz = x / 7.4, (z - 4.0) / 11.5
    head = 1 - smoothstep(0.9, 1.05, np.sqrt(hx * hx + hz * hz))
    neck = (1 - smoothstep(4.0, 4.6, np.abs(x))) * smoothstep(-17, -15, z) * (1 - smoothstep(-6, -4, z))
    alpha = np.maximum(head, neck)
    shade = 0.95 - 0.35 * (x / 7.4) ** 2 - 0.25 * smoothstep(-3, -9, z)
    nz = bilinear(FN, (x * 40) % 1023, (z * 40) % 1023)
    col = skin[None, :] * shade[..., None] * (1 + 0.16 * nz[..., None])
    # redder cheeks/lip zone
    rz = np.exp(-((x / 3.2) ** 2 + ((z + 0.2) / 2.2) ** 2))
    col = col * (1 - 0.18 * rz[..., None]) + np.array([0.75, 0.42, 0.40]) * 0.18 * rz[..., None]
    # under-nose shadow and nostrils
    ns = np.exp(-((x / 1.9) ** 2) - ((z - 2.75) / 0.45) ** 2)
    col *= (1 - 0.35 * ns)[..., None]
    for sx in (-0.8, 0.8):
        nm = 1 - smoothstep(0.8, 1.0, np.sqrt(((x - sx) / 0.45) ** 2 + ((z - 3.0) / 0.25) ** 2))
        col = col * (1 - 0.75 * nm[..., None]) + np.array([0.12, 0.06, 0.06]) * 0.75 * nm[..., None]
    col *= (1 + 0.12 * smoothstep(3.2, 4.5, z) * np.exp(-(x / 2.0) ** 2))[..., None]
    # philtrum
    col *= (1 - 0.06 * np.exp(-(x / 0.35) ** 2) * smoothstep(0.9, 1.2, z) * (1 - smoothstep(2.0, 2.4, z)))[..., None]
    # mouth opening profile
    aa = a
    inside_w = np.clip(1 - (x / aa) ** 2, 0, 1)
    bz = b * np.sqrt(inside_w)
    lw = 2.6 + 0.3 * b
    corner = np.sqrt(np.clip(1 - (x / lw) ** 2, 0, 1))
    thin = 1 - 0.35 * min(b / 1.3, 1)
    U = thin * (0.70 - 0.20 * np.exp(-(x / 0.33) ** 2) + 0.12 * np.exp(-((np.abs(x) - 0.55) / 0.4) ** 2)) * corner
    L = thin * 0.85 * corner
    upper = (z > bz) & (z < bz + U)
    lower = (z < -bz) & (z > -bz - L)
    lip = np.array([0.70, 0.42, 0.41], np.float32)
    up_m = (smoothstep(-0.05, 0.25, z - bz) * (1 - smoothstep(U - 0.35, U + 0.05, z - bz)) * corner ** 0.5).astype(np.float32)
    lo_m = (smoothstep(-0.05, 0.25, -bz - z) * (1 - smoothstep(L - 0.45, L + 0.05, -bz - z)) * corner ** 0.5).astype(np.float32)
    lipcol = lip[None, :] * (1 + 0.08 * nz[..., None])
    # lower lip highlight, upper lip slightly darker (faces down)
    hl = np.exp(-(x / 1.2) ** 2 - ((z + bz + 0.35) / 0.18) ** 2)
    lo_c = lipcol * 1.02 + 0.10 * hl[..., None]
    up_c = lipcol * 0.86
    col = col * (1 - up_m[..., None]) + up_c * up_m[..., None]
    col = col * (1 - lo_m[..., None]) + lo_c * lo_m[..., None]
    # chin crease
    col *= (1 - 0.18 * np.exp(-(x / 1.6) ** 2 - ((z + bz + 1.9) / 0.35) ** 2))[..., None]
    # opening interior
    portal = (np.abs(x) < aa) & (np.abs(z) < bz)
    if b > 0.05:
        dark = (np.array([0.16, 0.05, 0.05], np.float32) * (0.35 + 0.65 * np.clip(1 - (np.abs(z) / np.maximum(bz, 1e-3)), 0, 1) ** 0.3 * 0 + 0.65 * np.clip((x / aa) ** 2 + (z / max(b, 1e-3)) ** 2, 0, 1))[..., None]).astype(np.float32)
        teeth = (z > bz - 0.30) & portal & (np.abs(x) < 1.4) & (b > 0.45)
        inner = np.where(teeth[..., None], np.array([0.62, 0.58, 0.52]) * 0.55, dark)
        tongue = (z < -bz * 0.2) & portal
        inner = np.where(tongue[..., None], np.array([0.30, 0.09, 0.09]), inner)
        col = np.where(portal[..., None], inner, col)
    # mouth corner shadow line
    col *= (1 - 0.35 * np.exp(-(z / 0.08) ** 2) * (corner > 0) * (b <= 0.05))[..., None]
    return col.astype(np.float32), alpha.astype(np.float32), portal

# ---------------------------------------------------------------- trajectory

def pchip(ts, ys, t):
    ts = np.asarray(ts, float); ys = np.asarray(ys, float)
    i = int(np.clip(np.searchsorted(ts, t) - 1, 0, len(ts) - 2))
    h = np.diff(ts); d = np.diff(ys) / h
    m = np.zeros_like(ys)
    for k in range(1, len(ys) - 1):
        if d[k - 1] * d[k] > 0:
            w1 = 2 * h[k] + h[k - 1]; w2 = h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    u = np.clip((t - ts[i]) / h[i], 0, 1)
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u
    h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
    return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]


def P(px, py):
    return np.array([(px - 200) * S, (189 - py) * S])


STEAK1 = [(47, 214), (76, 195), (104, 179), (113, 186), (126, 201), (98, 222), (73, 243), (58, 240), (46, 229)]
STEAK2 = [(68, 245), (98, 223), (127, 202), (138, 211), (144, 218), (115, 245), (85, 270), (73, 266), (64, 256)]
GREENS = [(100, 82), (128, 70), (160, 77), (171, 93), (152, 111), (117, 116), (98, 101)]
TOMATO = ellipse_poly(309, 138, 17.5, 19.5)

FOODS = [
    dict(name='steak', poly=STEAK1, thick=0.75, kind='slab', clone=(17, 26), psi=121, side=(0.33, 0.19, 0.14), dark=0.62),
    dict(name='greens', poly=GREENS, thick=0.35, kind='leaf', clone=(75, -30), psi=96, side=(0.15, 0.25, 0.10), dark=0.55),
    dict(name='tomato', poly=TOMATO, thick=1.6, kind='dome', clone=(10, 66), psi=78, side=(0.45, 0.08, 0.05), dark=0.6),
    dict(name='steak', poly=STEAK2, thick=0.75, kind='slab', clone=(17, 27), psi=124, side=(0.33, 0.19, 0.14), dark=0.62),
]
for f in FOODS:
    c = np.mean(np.array(f['poly']), 0)
    f['target'] = P(*c)

INTRO = 1.1
BITE = 7.2
T_TOTAL = INTRO + BITE * len(FOODS) + 0.6
MOUTH = np.array([XM, YF, ZM])


def build_keys():
    keys = []   # (t, Ax, Ay, Az, yaw, pitch, roll, mouth)
    keys.append((0.0, 0.5, -6.5, 11.0, 112, -40, 3, 0))
    swaps, eats = [], []
    for i, f in enumerate(FOODS):
        t0 = INTRO + i * BITE
        T = f['target']; ps = f['psi']
        h = np.array([math.cos(math.radians(ps)), math.sin(math.radians(ps))])
        def k(dt, xy, z, yaw, pitch, roll, mo):
            keys.append((t0 + dt, xy[0], xy[1], z, yaw, pitch, roll, mo))
        k(0.0, T - 2.2 * h, 6.5, ps - 9, -38, 4, 0)
        k(1.15, T - 0.8 * h, 2.4, ps - 3, -46, 2, 0)
        k(1.7, T - 0.12 * h, 0.25, ps, -50, 0.5, 0)
        k(1.95, T, -0.30, ps, -51, 0, 0)
        swaps.append(t0 + 1.95)
        k(2.3, T + 0.05 * h, -0.22, ps + 1, -49, -2, 0)
        k(2.85, T - 0.6 * h, 4.2, ps + 12, -32, -6, 0)
        mid = 0.5 * (T + MOUTH[:2]) + np.array([4.0, 0])
        k(3.55, mid, 17.0, 196, -6, -14, 0.6)
        k(4.25, MOUTH[:2] + np.array([0.35, 4.2]), ZM - 0.4, 266, 3, -4, 1.0)
        k(4.7, MOUTH[:2] + np.array([0.05, -1.6]), ZM - 0.05, 269, 4, -1, 1.0)
        k(4.95, MOUTH[:2] + np.array([0.0, -1.7]), ZM, 269, 4, -1, 0.9)
        k(5.25, MOUTH[:2] + np.array([0.0, -1.3]), ZM + 0.1, 269, 3, -1, 0.12)
        eats.append(t0 + 5.15)
        k(5.85, MOUTH[:2] + np.array([0.4, 4.6]), ZM - 0.9, 266, 0, -3, 0.0)
        nxt = FOODS[i + 1]['target'] if i + 1 < len(FOODS) else np.array([0.0, -2.0])
        k(6.6, 0.5 * (MOUTH[:2] + nxt) + np.array([3.0, 0]), 13.0, 205, -22, -8, 0)
    tl = INTRO + BITE * len(FOODS)
    keys.append((tl + 0.0, 0.5, -7.0, 8.5, 110, -38, 3, 0))
    keys.append((T_TOTAL + 0.5, 0.6, -6.6, 9.5, 108, -40, 2, 0))
    keys.sort(key=lambda r: r[0])
    return np.array(keys), swaps, eats


KEYS, SWAPS, EATS = build_keys()
_PH = RNG.random((7, 4)) * 2 * np.pi
_FR = np.array([0.55, 1.3, 2.7, 5.9])


def rig_pose(t):
    v = [pchip(KEYS[:, 0], KEYS[:, j], t) for j in range(1, 8)]
    A = np.array(v[0:3]); yaw, pitch, roll, mouth = v[3], v[4], v[5], v[6]
    # transport phases get more hand shake than the careful phases
    k_ = float(smoothstep(1.0, 6.0, A[2]))
    amp_p = 0.05 + 0.13 * k_
    amp_r = 0.35 + 0.55 * k_
    def nz(j):
        return sum(math.sin(2 * math.pi * _FR[q] * t + _PH[j, q]) / (1 + q) for q in range(4)) / 1.9
    A = A + amp_p * np.array([nz(0), nz(1), nz(2)])
    yaw += amp_r * nz(3); pitch += amp_r * nz(4); roll += amp_r * 1.5 * nz(5)
    # impact jolt when the tines go into the food
    for ts in SWAPS:
        dt = t - (ts - 0.1)
        if 0 < dt < 0.6:
            pitch += 1.4 * math.exp(-dt / 0.12) * math.sin(dt * 45)
    return A, yaw, pitch, roll, max(mouth, 0.0)


def rig_matrix(yaw, pitch, roll):
    ps, th, ph = map(math.radians, (yaw, pitch, roll))
    f = np.array([math.cos(th) * math.cos(ps), math.cos(th) * math.sin(ps), math.sin(th)])
    r0 = np.array([math.sin(ps), -math.cos(ps), 0.0])
    u0 = np.cross(r0, f)
    r = r0 * math.cos(ph) + u0 * math.sin(ph)
    u = u0 * math.cos(ph) - r0 * math.sin(ph)
    return np.stack([r, f, u], 1)    # world_from_fork


def pose_full(t):
    A, yaw, pitch, roll, mouth = rig_pose(t)
    R = rig_matrix(yaw, pitch, roll)
    C = A + R @ (CAM_F - ANCHOR)
    return A, R, C, mouth

# ---------------------------------------------------------------- food cards

class Food:
    def __init__(self, spec, tex):
        self.spec = spec
        m = poly_mask(tex.shape, spec['poly'])
        ys, xs = np.nonzero(m > 0.01)
        y0, y1, x0, x1 = ys.min() - 4, ys.max() + 5, xs.min() - 4, xs.max() + 5
        self.box = (x0, y0)
        self.rgb = tex[y0:y1, x0:x1].copy()
        self.a = m[y0:y1, x0:x1].copy()
        self.mask_full = m
        hh, ww = self.a.shape
        th = spec['thick']
        if spec['kind'] == 'slab':
            hm = th * smoothstep(0.15, 0.6, gblur(self.a, 4))
        elif spec['kind'] == 'dome':
            yy, xx = np.mgrid[0:hh, 0:ww]
            cy, cx = (hh - 1) / 2, (ww - 1) / 2
            r = np.sqrt(((xx - cx) / (ww / 2 - 4)) ** 2 + ((yy - cy) / (hh / 2 - 4)) ** 2)
            hm = th * np.sqrt(np.clip(1 - r * r, 0, 1)) * (0.75 + 0.25 * self.a)
        else:
            nzm = value_noise((hh, ww), 12, 5)
            hm = th * (0.35 + 0.65 * nzm) * smoothstep(0.1, 0.5, self.a)
        self.hm = hm.astype(np.float32)
        self.cache = None

    def attach(self, A, R):
        """freeze card pose in the fork frame at the moment of the stab."""
        th = self.spec['thick']
        x0, y0 = self.box
        def world(u, v):
            return np.array([(u / TS - 200) * S, (189 - v / TS) * S, -th])
        Ow = world(x0, y0)
        exw = np.array([S / TS, 0, 0]); eyw = np.array([0, -S / TS, 0])
        to_f = lambda p: R.T @ (p - A) + ANCHOR
        self.O = to_f(Ow); self.ex = R.T @ exw; self.ey = R.T @ eyw; self.n = R.T @ np.array([0, 0, 1.0])
        self.render()

    def render(self):
        D = make_rays(W, H)
        Df = (D @ M_FC.T).astype(np.float32)
        spec = self.spec
        th = spec['thick']
        N = {'slab': 12, 'dome': 18, 'leaf': 6}[spec['kind']]
        dh = th / N
        hh, ww = self.a.shape
        col = np.zeros((H, W, 3), np.float32); acc = np.zeros((H, W), np.float32)
        tdep = np.full((H, W), 1e4, np.float32)
        ex2 = self.ex @ self.ex; ey2 = self.ey @ self.ey
        side = np.array(spec['side'], np.float32)
        for k in range(N, -1, -1):          # top layer first (front to back)
            hk = k * dh
            Ok = self.O + self.n * hk
            denom = Df @ self.n
            t = ((Ok - CAM_F) @ self.n) / np.where(np.abs(denom) < 1e-5, 1e-5, denom)
            Pp = CAM_F + t[..., None] * Df - Ok
            u = (Pp @ self.ex) / ex2; v = (Pp @ self.ey) / ey2
            ok = (t > 0) & (u >= 0) & (v >= 0) & (u < ww - 1) & (v < hh - 1)
            if not ok.any():
                continue
            uu, vv = u[ok], v[ok]
            a = bilinear(self.a, uu, vv); hmv = bilinear(self.hm, uu, vv)
            al = a * np.clip((hmv - hk) / dh + 0.5, 0, 1)
            c = bilinear(self.rgb, uu, vv)
            frac = k / N
            top = np.clip((hmv - hk) / (2 * dh), 0, 1)       # 0 at surface, 1 deep inside (side wall)
            sidec = (c * 0.45 + side * 0.55) * (spec['dark'] + (1 - spec['dark']) * frac)
            c = c * (1 - top[..., None]) + sidec * top[..., None]
            c = c * (0.8 + 0.2 * frac)
            cur = acc[ok]
            wgt = (1 - cur) * al
            col[ok] += c * wgt[..., None]
            acc[ok] = cur + wgt
            hit = (cur < 0.5) & (cur + wgt >= 0.5)
            td = tdep[ok]; td[hit] = t[ok][hit]; tdep[ok] = td
        self.cache = dict(rgb=col / np.maximum(acc[..., None], 1e-4), a=acc, t=tdep)
        # shadow footprint in fork (x,s) plane
        vv, uu = np.nonzero(self.a > 0.4)
        sel = slice(None, None, 3)
        pts = self.O + uu[sel, None] * self.ex + vv[sel, None] * self.ey + self.hm[vv[sel], uu[sel], None] * self.n
        sil, res = SIL
        sh = np.zeros_like(sil)
        ix = ((pts[:, 0] - SX0) / res).astype(int); iy = ((pts[:, 1] - SS0) / res).astype(int)
        good = (ix >= 0) & (ix < sh.shape[1]) & (iy >= 0) & (iy < sh.shape[0])
        sh[iy[good], ix[good]] = 1
        sh = np.clip(gblur(sh, 2.5) * 4, 0, 1)
        self.sil = np.maximum(sil, sh)


# ---------------------------------------------------------------- scene setup

class Scene:
    def __init__(self):
        global SIL
        self.Dc = make_rays(W, H)
        self.fork = render_fork()
        self.fork['blurmask'] = gblur(self.fork['mask'], 2.0)
        SIL = fork_silhouette()
        self.sil_levels = self._sil_levels(SIL[0])
        tex = load_photo()
        self.tex_alpha = self._photo_alpha(tex.shape)
        self.foods = [Food(f, tex) for f in FOODS]
        self.tex_states = []
        cur = tex
        self.tex_states.append(build_pyramid(cur))
        for i, fd in enumerate(self.foods):
            dx, dy = fd.spec['clone']
            src = np.roll(cur, (-dy * TS, -dx * TS), axis=(0, 1))
            m = np.clip(gblur(np.clip(fd.mask_full * 1.6, 0, 1), 1.5 * TS), 0, 1)[..., None]
            dark = 0.72 if fd.spec['name'] == 'greens' else 0.8
            cur = cur * (1 - m) + src * dark * m
            self.tex_states.append(build_pyramid(cur))
        self.tabcol = np.median(np.concatenate([tex[:40, :40].reshape(-1, 3), tex[:40, -40:].reshape(-1, 3)]), 0)
        self.tabnoise = value_noise((512, 512), 32, 9) - 0.5
        self.env = make_env()
        self.attached = {}

    def _photo_alpha(self, shape):
        h, w = shape[:2]
        yy = np.minimum(np.arange(h), h - 1 - np.arange(h))[:, None]
        xx = np.minimum(np.arange(w), w - 1 - np.arange(w))[None, :]
        return smoothstep(0, 60, np.minimum(yy, xx)).astype(np.float32)

    def _sil_levels(self, sil):
        res = 0.025
        return [(r, gblur(sil, r / res) if r / res > 0.4 else sil) for r in (0.02, 0.12, 0.35, 0.8, 1.6)]

    # -- state at time t
    def state(self, t):
        removed = sum(1 for s in SWAPS if t >= s)
        card = None
        for i, (s, e) in enumerate(zip(SWAPS, EATS)):
            if s <= t < e:
                card = i
        return removed, card

    def card(self, i):
        if i not in self.attached:
            A, R, C, _ = pose_full(SWAPS[i])
            self.foods[i].attach(A, R)
            self.attached[i] = self.foods[i]
        return self.attached[i]

    # -- background ray cast
    def background(self, t, removed, sil):
        A, R, C, mouth = pose_full(t)
        Q = R @ M_FC
        Dw = self.Dc @ Q.T.astype(np.float32)
        col = sample_env(self.env, Dw)
        tb = np.full((H, W), 400.0, np.float32)
        portal = np.zeros((H, W), bool); tface = np.full((H, W), 1e4, np.float32)
        is_tab = np.zeros((H, W), bool)
        tblur = None
        # body / torso plane behind face
        yb = YF - 5.0
        with np.errstate(divide='ignore', invalid='ignore'):
            t_b = (yb - C[1]) / Dw[..., 1]
        Pb = C + t_b[..., None] * Dw
        bm = (t_b > 0) & (np.abs(Pb[..., 0] - XM) < 22) & (Pb[..., 2] < ZM - 9.5) & (Pb[..., 2] > -40)
        shirt = np.array([0.11, 0.12, 0.16], np.float32)
        col = np.where(bm[..., None], shirt * (0.8 + 0.4 * smoothstep(ZM - 30, ZM - 12, Pb[..., 2]))[..., None], col)
        tb = np.where(bm, t_b, tb)
        # table plane
        with np.errstate(divide='ignore', invalid='ignore'):
            t_t = -C[2] / Dw[..., 2]
        Pt = C + t_t[..., None] * Dw
        tm = (Dw[..., 2] < -1e-4) & (t_t > 0) & (Pt[..., 1] > Y_EDGE) & (np.abs(Pt[..., 0]) < 70) & (Pt[..., 1] < 80) & (t_t < tb)
        if tm.any():
            idx = np.nonzero(tm)
            X = Pt[..., 0][idx]; Y = Pt[..., 1][idx]; tt = t_t[idx]
            u = (X / S + 200) * TS; v = (189 - Y / S) * TS
            pyr = self.tex_states[removed]
            pixang = 2 * TANH / W
            foot = tt * pixang / (S / TS) / np.sqrt(np.clip(-Dw[..., 2][idx], 0.15, 1))
            lv = np.clip(np.log2(np.maximum(foot, 1.0)), 0, len(pyr) - 1.001)
            c = np.zeros((len(X), 3), np.float32)
            for L in range(len(pyr)):
                w_ = np.clip(1 - np.abs(lv - L), 0, 1)
                s_ = w_ > 0
                if s_.any():
                    c[s_] += w_[s_, None] * bilinear(pyr[L], u[s_] / 2 ** L, v[s_] / 2 ** L)
            pa = bilinear(self.tex_alpha, u, v) * (u > 0) * (v > 0) * (u < pyr[0].shape[1]) * (v < pyr[0].shape[0])
            tn = bilinear(self.tabnoise, (X * 3) % 511, (Y * 3) % 511)
            tabc = self.tabcol[None, :] * (1 + 0.12 * tn[:, None]) * (1 - 0.25 * smoothstep(25, 60, np.hypot(X, Y)))[:, None]
            c = c * pa[:, None] + tabc * (1 - pa[:, None])
            # fork/food shadow cast from overhead light
            Xw = np.stack([X, Y, np.zeros_like(X)], -1)
            Xf = (Xw - A) @ R + ANCHOR
            Lf = R.T @ LIGHT
            lam = (0.1 - Xf[:, 2]) / (Lf[2] if abs(Lf[2]) > 1e-3 else 1e-3)
            xs = Xf[:, 0] + lam * Lf[0]; ss = Xf[:, 1] + lam * Lf[1]
            pen = np.clip(0.10 * lam, 0.02, 1.6)
            occ = np.zeros_like(X)
            res = 0.025
            levels = self._sil_levels_for(sil)
            radii = np.array([r for r, _ in levels])
            li = np.clip(np.interp(pen, radii, np.arange(len(radii))), 0, len(radii) - 1)
            for j, (r, im) in enumerate(levels):
                w_ = np.clip(1 - np.abs(li - j), 0, 1)
                s_ = (w_ > 0) & (lam > 0)
                if s_.any():
                    occ[s_] += w_[s_] * bilinear(im, (xs[s_] - SX0) / res, (ss[s_] - SS0) / res) * \
                        ((xs[s_] > SX0) & (xs[s_] < SX1) & (ss[s_] > SS0) & (ss[s_] < SS1))
            c *= (1 - 0.45 * occ * smoothstep(0.3, 2.0, lam) * np.exp(-np.maximum(lam, 0) / 20))[:, None]
            col[idx] = c
            tb[idx] = tt
            is_tab[idx] = True
        # face plane (drawn over body/env, depth-tested against table)
        with np.errstate(divide='ignore', invalid='ignore'):
            t_f = (YF - C[1]) / Dw[..., 1]
        fm = (Dw[..., 1] < -1e-4) & (t_f > 0) & (t_f < tb + 0.0)
        if fm.any():
            idx = np.nonzero(fm)
            Pf = C + t_f[idx][:, None] * Dw[idx]
            x = Pf[:, 0] - XM; z = Pf[:, 2] - ZM
            a_open = 1.75 if mouth > 0.6 else 1.45 + 0.5 * mouth
            fc, fa, pr = face_color(x, z, mouth, a_open)
            light = 0.78
            col[idx] = col[idx] * (1 - fa[:, None]) + fc * light * fa[:, None]
            facehit = fa > 0.5
            tf = t_f[idx]
            newt = np.where(facehit, np.where(pr, tf + 3.0, tf), tb[idx])
            tb[idx] = newt
            tbl = tb.copy() if tblur is None else tblur
            tbl[idx] = np.where(facehit, tf, tbl[idx])
            tblur = tbl
            portal[idx] = pr & facehit
            tface[idx] = np.where(facehit, tf, 1e4)
        return dict(col=col, t=tb, is_tab=is_tab, tblur=tb if tblur is None else tblur, portal=portal, tface=tface, A=A, R=R, C=C, Dw=Dw, mouth=mouth)

    def _sil_levels_for(self, sil):
        if sil is SIL[0]:
            return self.sil_levels
        key = id(sil)
        if not hasattr(self, '_slc'):
            self._slc = {}
        if key not in self._slc:
            self._slc[key] = self._sil_levels(sil)
        return self._slc[key]

    # -- full frame
    def frame(self, t):
        removed, ci = self.state(t)
        card = self.card(ci) if ci is not None else None
        sil = card.sil if card is not None else SIL[0]
        # motion blur: average background sub-samples when moving fast
        A0, R0, _, _ = pose_full(t); A1, R1, _, _ = pose_full(t + 0.5 / FPS)
        ang = math.degrees(math.acos(np.clip((np.trace(R0.T @ R1) - 1) / 2, -1, 1)))
        lin = np.linalg.norm(A1 - A0)
        nsub = int(np.clip(1 + ang * 1.6 + lin * 0.9, 1, 6))
        bgs = [self.background(t + (k / max(nsub - 1, 1) - 0.5) * (0.5 / FPS) * (nsub > 1), removed, sil)
               for k in range(nsub)]
        bg = bgs[len(bgs) // 2]
        col = sum(b['col'] for b in bgs) / nsub
        # defocus (focus ~9cm, fixed-focus wide lens)
        zd = bg['tblur'] * self.Dc[..., 2]
        izd = 1.0 / np.maximum(zd, 0.5)
        coc = np.clip(30.0 * np.abs(izd - 1.0 / 6.0) + 90.0 * np.maximum(izd - 0.2, 0), 0, 14) + 0.5
        levels = [0.6, 1.5, 3.0, 5.5, 9.0, 14.0]
        blurred = [gblur(col, s) if s > 0.7 else col for s in levels]
        li = np.interp(coc, levels, np.arange(len(levels)))
        out = np.zeros_like(col)
        for j, bimg in enumerate(blurred):
            w_ = np.clip(1 - np.abs(li - j), 0, 1)
            out += bimg * w_[..., None]
        bgc = out
        A, R, C, mouth = bg['A'], bg['R'], bg['C'], bg['mouth']
        # local light: diner's head shadows the fork near the mouth
        dface = A[1] - YF
        local = 1 - 0.55 * smoothstep(9, 1.5, dface) * (A[2] > ZM - 8)
        # ---- fork shading
        F = self.fork
        n = F['n']; Df = self.Dc @ M_FC.T
        Lf = R.T @ LIGHT; upf = R.T @ np.array([0, 0, 1.0])
        diff = np.clip(n @ Lf, 0, 1); hemi = 0.5 + 0.5 * (n @ upf)
        V = -Df; Hh = Lf[None, None, :] + V; Hh /= np.linalg.norm(Hh, axis=-1, keepdims=True)
        nh = np.clip(np.sum(n * Hh, -1), 0, 1)
        spec = nh ** 70 * 0.55 + nh ** 8 * 0.10
        Rd = Df - 2 * np.sum(Df * n, -1, keepdims=True) * n
        Rc = Rd @ M_FC          # back to camera coords
        rx, ry = project_cam(np.where(Rc[..., 2:3] > 0.05, Rc, np.array([0, 0, 1.0])))
        refl_src = gblur(bgc, 10)
        refl = bilinear(refl_src, rx - 0.5, ry - 0.5)
        ndv = np.clip(np.sum(n * V, -1), 0, 1)
        fres = 0.04 + 0.96 * (1 - ndv) ** 5
        rw = (0.12 + 0.55 * fres) * (Rc[..., 2] > 0.05)
        alb = np.array([0.88, 0.88, 0.90], np.float32)
        fcol = alb * (0.5 * diff + 0.55 * hemi)[..., None] * local + spec[..., None] * local
        fcol = fcol * (1 - rw[..., None]) + refl * rw[..., None]
        # subsurface-ish glow of white plastic picking up the scene colour
        fcol = fcol * 0.9 + 0.1 * gblur(bgc, 20)
        edge = F['mask'] * (1 - smoothstep(0.55, 0.98, F['blurmask']))
        fcol = fcol * (1 - 0.35 * edge[..., None])
        fall = np.clip((F['t'] - 3.0) / 6.0, 0, 1)
        fcol = fcol * (1 - 0.18 * fall[..., None])
        ft = F['t']; fa = F['mask'].copy()
        # ---- depth tests
        def vis(tobj):
            v = (tobj < bg['t'] + 0.02).astype(np.float32)
            return v
        def mouthdark(tobj, c):
            inside = bg['portal'] & (tobj > bg['tface'])
            k = np.where(inside, 0.06 + 0.5 * np.exp(-np.clip(tobj - bg['tface'], 0, 50) / 0.5), 1.0)
            tint = np.where(inside[..., None], np.array([1.0, 0.7, 0.7], np.float32), 1.0)
            return c * k[..., None] * tint
        fa = fa * vis(ft)
        fcol = mouthdark(ft, fcol)
        res = bgc.copy()
        if card is not None:
            cc = card.cache
            cl = 0.75 + 0.35 * np.clip(card.n @ Lf, 0, 1)
            ccol = cc['rgb'] * cl * local
            ca = cc['a'] * np.maximum(vis(cc['t']), bg['is_tab'])
            ccol = mouthdark(cc['t'], ccol)
            card_front = cc['t'] <= ft + 0.05
            # far layer first then near
            o1 = res * (1 - fa[..., None]) + fcol * fa[..., None]
            o1 = o1 * (1 - ca[..., None]) + ccol * ca[..., None]
            o2 = res * (1 - ca[..., None]) + ccol * ca[..., None]
            o2 = o2 * (1 - fa[..., None]) + fcol * fa[..., None]
            res = np.where(card_front[..., None], o1, o2)
            # contact shadow of food on the tines
            sh = gblur(cc['a'], 6) * F['mask'] * (1 - cc['a'])
            res *= (1 - 0.35 * sh * (ft > cc['t'] - 0.5))[..., None]
        else:
            res = res * (1 - fa[..., None]) + fcol * fa[..., None]
        # slight lens softness on the whole image (fork included)
        res = gblur(res, 0.7) * 0.5 + res * 0.5
        return res.astype(np.float32)


def render_range(i0, i1, outdir):
    sc = Scene()
    lum = []
    for i in range(i0, i1):
        t = i / FPS
        img = sc.frame(t)
        y = img[..., 0] * 0.3 + img[..., 1] * 0.59 + img[..., 2] * 0.11
        hc = y[H // 6: -H // 6, W // 6: -W // 6]
        lum.append((i, float(hc.mean()), float(np.percentile(hc, 97))))
        Image.fromarray((np.clip(img * 0.75, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f'{outdir}/f{i:05d}.png')
    with open(f'{outdir}/lum_{i0:05d}.txt', 'w') as fh:
        for r in lum:
            fh.write('%d %.5f %.5f\n' % r)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        sc = Scene()
        outs = []
        for ts in sys.argv[3:]:
            img = sc.frame(float(ts))
            outs.append(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)))
        cols = 2
        rows = (len(outs) + 1) // 2
        sheet = Image.new('RGB', (W * cols, H * rows))
        for k, im in enumerate(outs):
            sheet.paste(im, ((k % cols) * W, (k // cols) * H))
        sheet.save(sys.argv[2])
    elif mode == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif mode == 'info':
        print('total', T_TOTAL, 'frames', int(T_TOTAL * FPS), 'swaps', SWAPS, 'eats', EATS)
