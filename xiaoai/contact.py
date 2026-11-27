#!/usr/bin/env python3
"""把 build/stills/ 下的静帧拼成触表：python3 contact.py [cols] [out]"""
import glob, sys
from PIL import Image, ImageDraw

cols = int(sys.argv[1]) if len(sys.argv) > 1 else 4
out = sys.argv[2] if len(sys.argv) > 2 else 'build/contact.png'
fs = sorted(glob.glob('build/stills/t*.png'), key=lambda f: float(f.split('/t')[-1][:-4]))
W, H = 640, 360
rows = (len(fs) + cols - 1) // cols
im = Image.new('RGB', (W * cols, (H + 24) * rows), 'white')
d = ImageDraw.Draw(im)
for i, f in enumerate(fs):
    x, y = (i % cols) * W, (i // cols) * (H + 24)
    im.paste(Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS), (x, y))
    d.text((x + 8, y + H + 4), f.split('/t')[-1][:-4] + 's', fill='black')
im.save(out)
print(out, len(fs), 'frames')
