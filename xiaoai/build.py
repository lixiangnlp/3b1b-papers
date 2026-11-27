#!/usr/bin/env python3
"""《小爱同学 · 九年》一键构建。

  python3 build.py              # 全流程：卡点 → 配乐 → 逐帧渲染(60fps) → 合成 → 验收
  python3 build.py --fps 30     # 快速预览
  python3 build.py audio        # 只重做卡点和配乐（改了动画时间后用）
  python3 build.py mux          # 只重新合成（已有 build/silent.mp4 和 build/music.wav）

产物：build/xiaoai_2017-2026.mp4（1920×1080，H.264 High + AAC，-14 LUFS），
      build/music.m4a（给 index.html 浏览器播放用）
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
OUT = BUILD / 'xiaoai_2017-2026.mp4'


def run(cmd, **kw):
    print('$', ' '.join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def audio():
    run(['node', 'render.js', 'cues'])
    run([sys.executable, 'music.py'])


def loudnorm_args(src):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    txt = r.stderr
    j = json.loads(txt[txt.rindex('{'):txt.rindex('}') + 1])
    return (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
            f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")


def mux():
    ln = loudnorm_args(BUILD / 'music.wav')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(BUILD / 'silent.mp4'), '-i', str(BUILD / 'music.wav'),
         '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', ln + ',aresample=48000', '-c:a', 'aac', '-b:a', '256k', '-ac', '2',
         '-shortest', '-movflags', '+faststart', str(OUT)])
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(BUILD / 'music.wav'), '-af', ln, '-c:a', 'aac', '-b:a', '192k',
         str(BUILD / 'music.m4a')])
    # 验收
    run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,profile,width,height,r_frame_rate,pix_fmt,channels,sample_rate:format=duration,size',
         '-of', 'compact', str(OUT)])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(OUT), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    print('\n'.join(l for l in r.stderr.splitlines()[-14:] if any(k in l for k in ('I:', 'LRA:', 'Peak:'))))
    print('->', OUT)


def video(fps):
    run(['node', 'render.js', 'video', str(BUILD / 'silent.mp4'), '--fps', str(fps), '--workers', '3'])


if __name__ == '__main__':
    if not shutil.which('ffmpeg'):
        sys.exit('需要 ffmpeg')
    BUILD.mkdir(exist_ok=True)
    args = sys.argv[1:]
    fps = int(args[args.index('--fps') + 1]) if '--fps' in args else 60
    step = next((a for a in args if a in ('audio', 'video', 'mux', 'all')), 'all')
    if step in ('audio', 'all'):
        audio()
    if step in ('video', 'all'):
        video(fps)
    if step in ('mux', 'all'):
        mux()
