#!/usr/bin/env python3
"""一键构建《Attention Is All You Need》中文讲解视频。

  python build.py tts                 # Qwen3-TTS(MLX) 逐句合成旁白 -> build/audio
  python build.py render -q h         # Manim 渲染各场景（-q l/m/h/k = 480p15/720p30/1080p60/4K60）
  python build.py assemble            # 拼接场景 + 生成字幕 -> build/attention_is_all_you_need.mp4
  python build.py all -q h            # 以上三步
  python build.py all --placeholder   # 没有 Apple Silicon 时：静音占位音频，先看画面节奏

其余参数（--speaker / --instruct / --mode ...）会原样传给 tts/qwen3_tts.py。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "attention"))
from narration import SCENE_ORDER  # noqa: E402

BUILD = ROOT / "build"
QUALITY_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "p": "1440p60", "k": "2160p60"}
OUTPUT = BUILD / "attention_is_all_you_need.mp4"


def run(cmd: list[str], **kw) -> None:
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def scene_video(scene: str, q: str) -> Path:
    return BUILD / "media" / scene / "videos" / "scenes" / QUALITY_DIR[q] / f"{scene}.mp4"


# ------------------------------------------------------------------ steps
def step_tts(extra: list[str], placeholder: bool) -> None:
    cmd = [sys.executable, str(ROOT / "tts" / "qwen3_tts.py"), *extra]
    if placeholder:
        cmd.append("--placeholder")
    run(cmd)


def step_render(q: str, scenes: list[str], jobs: int) -> None:
    (BUILD / "logs").mkdir(parents=True, exist_ok=True)

    def one(scene: str) -> tuple[str, int]:
        # 每个场景单独的 media 目录，避免并行时 LaTeX 缓存互相覆盖
        cmd = [sys.executable, "-m", "manim", "render", f"-q{q}", "--media_dir",
               str(BUILD / "media" / scene), str(ROOT / "attention" / "scenes.py"), scene]
        log = BUILD / "logs" / f"{scene}.log"
        with log.open("w") as f:
            code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=ROOT).returncode
        print(f"  {scene}: {'OK' if code == 0 else f'失败，见 {log}'}")
        return scene, code

    print(f"[render] {len(scenes)} 个场景，质量 {QUALITY_DIR[q]}，并行 {jobs}")
    with ThreadPoolExecutor(jobs) as ex:
        failed = [s for s, c in ex.map(one, scenes) if c != 0]
    if failed:
        sys.exit(f"[render] 失败: {failed}")


def probe_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())


def has_audio(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def split_subtitle(text: str, max_len: int = 22) -> list[str]:
    """按标点把一句旁白切成适合屏幕显示的短行。"""
    parts = [p for p in re.split(r"(?<=[，。；：？！,;:?!])", text) if p.strip()]
    chunks, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > max_len:
            chunks.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        chunks.append(cur)
    return [c.strip().rstrip("，。；：,;") or c for c in chunks]


def fmt_ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def step_assemble(q: str, burn: bool) -> None:
    parts_dir = BUILD / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    concat_list = parts_dir / "concat.txt"
    srt_lines: list[str] = []
    offset, idx = 0.0, 1
    entries = []
    for scene in SCENE_ORDER:
        src = scene_video(scene, q)
        if not src.exists():
            sys.exit(f"[assemble] 缺少 {src}，请先 render")
        # 统一音轨（没有旁白的场景补静音），保证能无损 concat
        part = parts_dir / f"{scene}.mp4"
        audio_in = [] if has_audio(src) else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), *audio_in,
             "-map", "0:v:0", "-map", "0:a:0" if not audio_in else "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-shortest", str(part)])
        entries.append(f"file '{part.name}'")

        cues = json.loads((BUILD / "cues" / f"{scene}.json").read_text("utf-8"))["cues"]
        for c in cues:
            chunks = split_subtitle(c["text"])
            total = sum(len(x) for x in chunks)
            t = offset + c["start"]
            span = c["end"] - c["start"]
            for ch in chunks:
                d = span * len(ch) / total
                srt_lines += [str(idx), f"{fmt_ts(t)} --> {fmt_ts(t + d)}", ch, ""]
                idx += 1
                t += d
        offset += probe_duration(part)

    concat_list.write_text("\n".join(entries) + "\n", "utf-8")
    srt = OUTPUT.with_suffix(".srt")
    srt.write_text("\n".join(srt_lines), "utf-8")
    joined = parts_dir / "joined.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(joined)])
    if burn:
        style = "FontName=PingFang SC,FontSize=13,Outline=1,Shadow=0,MarginV=6"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined), "-vf",
             f"subtitles={srt}:force_style='{style}'", "-c:a", "copy", str(OUTPUT)])
    else:
        # 软字幕：播放器里可开关
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined), "-i", str(srt),
             "-map", "0", "-map", "1", "-c", "copy", "-c:s", "mov_text",
             "-metadata:s:s:0", "language=chi", str(OUTPUT)])
    print(f"[assemble] 完成：{OUTPUT.relative_to(ROOT)}（{offset / 60:.1f} 分钟），字幕 {srt.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["tts", "render", "assemble", "all"])
    ap.add_argument("-q", "--quality", choices=list(QUALITY_DIR), default="h")
    ap.add_argument("-j", "--jobs", type=int, default=2, help="并行渲染的场景数")
    ap.add_argument("--scenes", nargs="*", default=None, help="只渲染这些场景")
    ap.add_argument("--placeholder", action="store_true", help="用静音占位音频代替 TTS")
    ap.add_argument("--burn-subs", action="store_true", help="把字幕烧进画面（需要 ffmpeg 带 libass）")
    args, extra = ap.parse_known_args()

    if not shutil.which("ffmpeg"):
        sys.exit("需要 ffmpeg（macOS: brew install ffmpeg）")
    if args.step in ("tts", "all"):
        step_tts(extra, args.placeholder)
    if args.step in ("render", "all"):
        step_render(args.quality, args.scenes or SCENE_ORDER, args.jobs)
    if args.step in ("assemble", "all"):
        step_assemble(args.quality, args.burn_subs)


if __name__ == "__main__":
    main()
