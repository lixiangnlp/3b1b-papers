"""Camera post-processing: auto exposure, webcam colour cast, vignette, sensor noise, encode."""
import glob, math, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

FPS = 24
fdir, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(f'{fdir}/f*.png'))
lum = {}
for fn in glob.glob(f'{fdir}/lum_*.txt'):
    for line in open(fn):
        i, m, p = line.split()
        lum[int(i)] = (float(m) / 0.75 * 0.75, float(p))
n = len(files)
mean = np.array([lum[i][0] for i in range(n)]); p97 = np.array([lum[i][1] for i in range(n)])

# auto-exposure with lag (slow to brighten, a bit faster to darken), like a cheap webcam
target = 0.44
raw = np.clip(target / np.maximum(mean, 1e-3), 0.55, 2.4)
raw = np.minimum(raw, 1.25 / np.maximum(p97, 1e-3))
gain = np.zeros(n); g = raw[0]
for i in range(n):
    tau = 0.45 if raw[i] > g else 0.25
    g += (raw[i] - g) * (1 - math.exp(-1 / (FPS * tau)))
    gain[i] = g

H, W = 544, 960
yy, xx = np.mgrid[0:H, 0:W]
r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (W / 2)) ** 2
vign = (1 - 0.32 * r2)[..., None].astype(np.float32)
rng = np.random.default_rng(3)


def blur(a, r):
    k = np.exp(-0.5 * (np.arange(-3, 4) / r) ** 2); k /= k.sum()
    a = sum(np.roll(a, j - 3, 0) * k[j] for j in range(7))
    return sum(np.roll(a, j - 3, 1) * k[j] for j in range(7)).astype(np.float32)


enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
for i, fn in enumerate(files):
    x = np.asarray(Image.open(fn)).astype(np.float32) / 255.0 / 0.75
    x = x * gain[i]
    # cool / purple-ish white balance of the reference camera
    x = x * np.array([0.92, 0.94, 1.08], np.float32)
    y = x.mean(-1, keepdims=True)
    x = y + (x - y) * 0.86                       # mild desaturation
    x = x * vign
    # sensor noise grows with exposure gain; luma grain + blotchy chroma noise
    s = 0.016 * gain[i] ** 0.8
    ln = blur(rng.standard_normal((H, W)), 0.55)[..., None] * s
    cn = np.stack([blur(rng.standard_normal((H, W)), 1.6) for _ in range(3)], -1) * s * 0.9
    x = x + ln + cn
    # highlight roll-off and lifted, purple shadows
    x = 1.08 * (1 - np.exp(-1.35 * np.maximum(x, 0))) / (1 - math.exp(-1.35))
    x = x * 0.93 + np.array([0.035, 0.028, 0.06], np.float32) * (1 - np.clip(x, 0, 1))
    x = np.clip(x, 0, 1)
    img = Image.fromarray((x * 255 + 0.5).astype(np.uint8))
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=1))   # webcam sharpening
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait()
print('done', n, 'frames; gain range', gain.min(), gain.max())
