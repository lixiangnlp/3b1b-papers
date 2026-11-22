"""用 MiniMax 语音合成（T2A v2，同步 HTTP 接口）逐句生成旁白。

为什么用同步接口而不是异步长文本接口：动画要和旁白逐句对齐，每句需要单独的音频和时长；
每句都远小于同步接口 10000 字的上限，异步接口（面向十万字级长文、返回整段音频）反而不合适。

  export MINIMAX_API_KEY=...                         # 在 platform.minimax.cn 用户中心获取
  python tts/minimax_tts.py --project riemann        # 生成全部（未修改的句子走缓存）
  python tts/minimax_tts.py --project riemann --only intro_1 --force
  python tts/minimax_tts.py --project riemann --audition \\
      "Chinese (Mandarin)_Gentleman" "Chinese (Mandarin)_Male_Announcer"   # 试听几个音色

输出与 qwen3_tts.py 相同：build/<项目>/audio/<key>.wav + manifest.json，
所以之后的 render / assemble 步骤不需要任何改动。
"""

from __future__ import annotations

import argparse
import importlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tts"))
from projects import DEFAULT_PROJECT, PROJECTS, get_project  # noqa: E402
from qwen3_tts import line_hash, trim_and_normalize, write_wav  # noqa: E402

API_URL = os.environ.get("MINIMAX_API_URL", "https://api.minimax.cn/v1/t2a_v2")
DEFAULT_MODEL = "speech-2.8-turbo"
DEFAULT_VOICE = "Chinese (Mandarin)_Gentleman"   # 温润男声
SAMPLE_RATE = 32000
RETRY_CODES = {1000, 1001, 1002, 1039}           # 未知错误 / 超时 / 限流


class MiniMaxError(RuntimeError):
    pass


def synth(text: str, *, key: str, model: str, voice: str, speed: float, vol: float,
          pitch: int, emotion: str | None, tone: list[str], retries: int = 5) -> np.ndarray:
    body = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {"voice_id": voice, "speed": speed, "vol": vol, "pitch": pitch},
        "audio_setting": {"sample_rate": SAMPLE_RATE, "format": "wav", "channel": 1},
        "language_boost": "Chinese",
        "text_normalization_mode": "quality",
        "output_format": "hex",
    }
    if emotion:
        body["voice_setting"]["emotion"] = emotion
    if tone:
        body["pronunciation_dict"] = {"tone": tone}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(API_URL, data=data, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:
            err = f"网络错误：{e}"
        else:
            base = resp.get("base_resp") or {}
            code = base.get("status_code", -1)
            if code == 0 and resp.get("data") and resp["data"].get("audio"):
                with wave.open(io.BytesIO(bytes.fromhex(resp["data"]["audio"]))) as w:
                    pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                    if w.getnchannels() > 1:
                        pcm = pcm.reshape(-1, w.getnchannels()).mean(axis=1)
                return pcm.astype(np.float32) / 32768.0
            err = f"status_code={code} {base.get('status_msg')} trace_id={resp.get('trace_id')}"
            if code not in RETRY_CODES:
                raise MiniMaxError(err)
        wait = 2 ** attempt
        print(f"    重试（{err}），{wait}s 后 ...")
        time.sleep(wait)
    raise MiniMaxError(err)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", choices=list(PROJECTS), default=DEFAULT_PROJECT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--voice", default=DEFAULT_VOICE, help="MiniMax 系统音色 voice_id")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--vol", type=float, default=1.0)
    ap.add_argument("--pitch", type=int, default=0)
    ap.add_argument("--emotion", default=None, help="calm / happy / ...，默认由模型自动判断")
    ap.add_argument("--only", nargs="*", help="只生成这些 key")
    ap.add_argument("--force", action="store_true", help="忽略缓存，全部重新生成")
    ap.add_argument("-j", "--jobs", type=int, default=3, help="并发请求数")
    ap.add_argument("--audition", nargs="*", metavar="VOICE_ID",
                    help="用第一句旁白试听这些音色，输出到 <build>/voice_samples/，不改动 manifest")
    args = ap.parse_args()

    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not key:
        sys.exit("请先设置环境变量 MINIMAX_API_KEY")

    proj = get_project(args.project)
    narration = importlib.import_module("narration")
    speakable = narration.speakable
    tone = list(getattr(narration, "MINIMAX_PRONUNCIATION", []))
    common = dict(key=key, model=args.model, speed=args.speed, vol=args.vol, pitch=args.pitch,
                  emotion=args.emotion, tone=tone)

    lines = [(k, t) for scene in narration.NARRATION.values() for k, t in scene]

    if args.audition:
        out_dir = proj.build / "voice_samples"
        out_dir.mkdir(parents=True, exist_ok=True)
        text = speakable(lines[1][1])
        for v in args.audition:
            audio = trim_and_normalize(synth(text, voice=v, **common), SAMPLE_RATE)
            out = out_dir / (v.replace(" ", "_").replace("(", "").replace(")", "") + ".wav")
            write_wav(out, audio, SAMPLE_RATE)
            print(f"[audition] {v}: {len(audio) / SAMPLE_RATE:.1f}s -> {out.relative_to(ROOT)}")
        return

    cfg = {"engine": "minimax", "model": args.model, "voice": args.voice, "speed": args.speed,
           "vol": args.vol, "pitch": args.pitch, "emotion": args.emotion, "tone": tone}
    audio_dir = proj.audio_dir
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = audio_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}
    if args.only:
        lines = [(k, t) for k, t in lines if k in set(args.only)]

    todo = []
    for k, t in lines:
        h = line_hash(speakable(t), cfg)
        e = manifest.get(k)
        if not args.force and e and e.get("hash") == h and (audio_dir / f"{k}.wav").exists():
            print(f"  {k}: 已缓存 {e['duration']:.1f}s")
        else:
            todo.append((k, speakable(t), h))

    def one(item):
        k, spoken, h = item
        t0 = time.time()
        audio = trim_and_normalize(synth(spoken, voice=args.voice, **common), SAMPLE_RATE)
        write_wav(audio_dir / f"{k}.wav", audio, SAMPLE_RATE)
        dur = len(audio) / SAMPLE_RATE
        print(f"  {k}: {dur:.1f}s 音频，用时 {time.time() - t0:.1f}s")
        return k, {"file": f"{k}.wav", "duration": round(dur, 3), "hash": h}

    print(f"[minimax] {args.model} / {args.voice}：需要合成 {len(todo)} 句")
    with ThreadPoolExecutor(max(1, args.jobs)) as ex:
        for k, entry in ex.map(one, todo):
            manifest[k] = entry
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")

    total = sum(manifest[k]["duration"] for k, _ in lines if k in manifest)
    print(f"[minimax] 完成：{len(lines)} 句，总时长 {total / 60:.1f} 分钟 -> "
          f"{manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
