"""逐句为旁白合成语音：优先云端高质量 TTS，其次本机 Qwen3-TTS，最后离线兜底。

输出:
  build/<paper>/audio/<key>.wav        每句一个单声道 wav
  build/<paper>/audio/manifest.json    {key: {file, duration, hash, backend}}，供 Manim 场景同步

后端（--backend auto 时按此顺序选第一个可用的）:
  minimax    MiniMax T2A v2（需 MINIMAX_API_KEY；默认 speech-2.8-turbo + male-qn-qingse）
  polly      AWS Polly 神经网络语音（需 AWS 凭证；中文音色 Zhiyu）
  google     Google Cloud TTS（需 GOOGLE_API_KEY 或 gcloud 访问令牌；默认 Chirp3-HD 音色）
  qwen-http  本机 Qwen3-TTS-1.7B-MLX 服务（python tts/qwen3_server.py 启动，QWEN_TTS_URL 可改地址）
  qwen-mlx   进程内加载 Qwen3-TTS-1.7B-MLX（仅 Apple Silicon）
  kokoro     sherpa-onnx + Kokoro 多语种模型（任意平台离线运行，models/kokoro-multi-lang-v1_1）
  placeholder  静音占位，按字数估时

用法:
  python tts/synth.py --paper smhbench                    # 自动选择后端
  python tts/synth.py --paper smhbench --backend qwen-http
  python tts/synth.py --paper smhbench --only res_3 --force
"""

from __future__ import annotations

import argparse
import base64
import importlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from qwen3_tts import (  # noqa: E402
    DEFAULT_INSTRUCT, DEFAULT_MODEL, DEFAULT_SPEAKER, LOCAL_MODEL, line_hash,
    trim_and_normalize, write_wav,
)

QWEN_URL = os.environ.get("QWEN_TTS_URL", "http://127.0.0.1:8765")
KOKORO_DIR = ROOT / "models" / "kokoro-multi-lang-v1_1"


def decode_audio(data: bytes) -> tuple[np.ndarray, int]:
    """用 ffmpeg 把 mp3/wav 等字节流解码为 24kHz 单声道 float32。"""
    sr = 24000
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "pipe:1"], input=data, capture_output=True, check=True)
    return np.frombuffer(out.stdout, np.float32).copy(), sr


# ------------------------------------------------------------------ 后端
class MiniMax:
    """MiniMax T2A v2（同步 HTTP）。密钥只从环境变量 MINIMAX_API_KEY 读取。"""
    name = "minimax"

    def __init__(self, voice: str | None = None, speed: float = 1.0):
        self.key = os.environ["MINIMAX_API_KEY"]
        self.url = f"https://{os.environ.get('MINIMAX_HOST', 'api.minimaxi.com')}/v1/t2a_v2"
        self.model = os.environ.get("MINIMAX_MODEL", "speech-2.8-turbo")
        self.voice = voice or "male-qn-qingse"
        self.speed = speed
        self.synth("你好")

    def synth(self, text: str):
        body = {"model": self.model, "text": text, "stream": False, "language_boost": "Chinese",
                "output_format": "hex",
                "voice_setting": {"voice_id": self.voice, "speed": self.speed, "vol": 1, "pitch": 0},
                "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1}}
        req = urllib.request.Request(self.url, json.dumps(body).encode(), {
            "Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    resp = json.load(r)
                base = resp.get("base_resp", {})
                if base.get("status_code", 0) != 0:
                    raise RuntimeError(f"MiniMax {base.get('status_code')}: {base.get('status_msg')}")
                return decode_audio(bytes.fromhex(resp["data"]["audio"]))
            except (OSError, RuntimeError):
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))


class Polly:
    name = "polly"

    def __init__(self, voice: str | None = None):
        import boto3
        self.voice = voice or "Zhiyu"
        self.client = boto3.client("polly", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        self.synth("你好")  # 验证凭证

    def synth(self, text: str):
        r = self.client.synthesize_speech(Text=text, VoiceId=self.voice, Engine="neural",
                                          OutputFormat="mp3", LanguageCode="cmn-CN")
        return decode_audio(r["AudioStream"].read())


class Google:
    name = "google"

    def __init__(self, voice: str | None = None):
        self.voice = voice or "cmn-CN-Chirp3-HD-Charon"
        self.key = os.environ.get("GOOGLE_API_KEY")
        self.token = None
        if not self.key:
            self.token = os.environ.get("GOOGLE_ACCESS_TOKEN") or subprocess.run(
                ["gcloud", "auth", "print-access-token"], capture_output=True, text=True,
                check=True).stdout.strip()
        self.synth("你好")

    def synth(self, text: str):
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {"Content-Type": "application/json"}
        if self.key:
            url += f"?key={self.key}"
        else:
            headers["Authorization"] = f"Bearer {self.token}"
        body = {"input": {"text": text},
                "voice": {"languageCode": "cmn-CN", "name": self.voice},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000}}
        req = urllib.request.Request(url, json.dumps(body).encode(), headers)
        with urllib.request.urlopen(req, timeout=60) as r:
            return decode_audio(base64.b64decode(json.load(r)["audioContent"]))


class QwenHTTP:
    name = "qwen-http"

    def __init__(self, voice: str | None = None, instruct: str | None = None):
        self.voice, self.instruct = voice, instruct  # None -> 服务端默认
        with urllib.request.urlopen(f"{QWEN_URL}/health", timeout=3) as r:
            json.load(r)

    def synth(self, text: str):
        body = json.dumps({"text": text, "speaker": self.voice, "instruct": self.instruct}).encode()
        req = urllib.request.Request(f"{QWEN_URL}/tts", body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return decode_audio(r.read())


class QwenMLX:
    name = "qwen-mlx"

    def __init__(self, voice: str | None = None, instruct: str | None = None):
        from qwen3_tts import QwenTTS
        model = str(LOCAL_MODEL) if LOCAL_MODEL.exists() else DEFAULT_MODEL
        self.tts = QwenTTS(model, "custom", voice or DEFAULT_SPEAKER, instruct or DEFAULT_INSTRUCT,
                           0.7, 42)

    def synth(self, text: str):
        return self.tts.synth(text), self.tts.sr


class Kokoro:
    name = "kokoro"

    def __init__(self, voice: str | None = None, speed: float = 1.0):
        import sherpa_onnx
        d = KOKORO_DIR
        if not (d / "model.onnx").exists():
            raise FileNotFoundError(f"缺少 {d}，见 scripts/setup_linux.sh")
        kcfg = sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=str(d / "model.onnx"), voices=str(d / "voices.bin"), tokens=str(d / "tokens.txt"),
            data_dir=str(d / "espeak-ng-data"), dict_dir=str(d / "dict"),
            lexicon=f"{d / 'lexicon-us-en.txt'},{d / 'lexicon-zh.txt'}")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kcfg, num_threads=os.cpu_count() or 4),
            rule_fsts=f"{d / 'date-zh.fst'},{d / 'phone-zh.fst'},{d / 'number-zh.fst'}")
        self.tts = sherpa_onnx.OfflineTts(cfg)
        self.sid = int(voice) if voice else 67  # 中文男声（zm_*），音高较低、平稳
        self.speed = speed

    def synth(self, text: str):
        g = self.tts.generate(text, sid=self.sid, speed=self.speed)
        return np.asarray(g.samples, np.float32), g.sample_rate


class Placeholder:
    name = "placeholder"

    def __init__(self, **_):
        pass

    def synth(self, text: str):
        cjk = len(re.findall(r"[一-鿿]", text))
        words = len(re.findall(r"[A-Za-z0-9.]+", text))
        dur = cjk / 4.3 + words * 0.35
        return np.zeros(int(dur * 24000), np.float32), 24000


BACKENDS = {"minimax": MiniMax, "polly": Polly, "google": Google, "qwen-http": QwenHTTP, "qwen-mlx": QwenMLX,
            "kokoro": Kokoro, "placeholder": Placeholder}
AUTO_ORDER = ["minimax", "polly", "google", "qwen-http", "qwen-mlx", "kokoro"]


def make_backend(name: str, voice: str | None, instruct: str | None, speed: float):
    names = AUTO_ORDER if name == "auto" else [name]
    for n in names:
        kw = {"voice": voice} if n in ("polly", "google") else \
             {"voice": voice, "instruct": instruct} if n.startswith("qwen") else \
             {"voice": voice, "speed": speed} if n in ("kokoro", "minimax") else {}
        try:
            b = BACKENDS[n](**kw)
            print(f"[tts] 使用后端：{n}")
            return b
        except Exception as e:  # noqa: BLE001
            msg = str(e).splitlines()[0][:120] if str(e) else type(e).__name__
            print(f"[tts] 后端 {n} 不可用：{msg}")
    sys.exit("[tts] 没有可用的 TTS 后端")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", default=os.environ.get("PAPER", "attention"))
    ap.add_argument("--backend", choices=["auto", *BACKENDS], default="auto")
    ap.add_argument("--voice", "--speaker", dest="voice", default=None,
                    help="音色：Polly VoiceId / Google 音色名 / Qwen speaker / Kokoro 说话人编号")
    ap.add_argument("--instruct", default=None, help="Qwen3-TTS 风格指令")
    ap.add_argument("--speed", type=float, default=1.0, help="语速（MiniMax / Kokoro）")
    ap.add_argument("--only", nargs="*", help="只生成这些 key")
    ap.add_argument("--force", action="store_true", help="忽略缓存")
    ap.add_argument("--placeholder", action="store_true", help="等价于 --backend placeholder")
    args = ap.parse_args()
    if args.placeholder:
        args.backend = "placeholder"

    sys.path.insert(0, str(ROOT / args.paper))
    narration = importlib.import_module("narration")
    audio_dir = ROOT / "build" / args.paper / "audio"
    manifest_path = audio_dir / "manifest.json"
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}

    lines = [(k, t) for scene in narration.NARRATION.values() for k, t in scene]
    if args.only:
        lines = [(k, t) for k, t in lines if k in set(args.only)]

    backend = None
    total = 0.0
    for idx, (key, text) in enumerate(lines, 1):
        spoken = narration.speakable(text)
        out = audio_dir / f"{key}.wav"
        entry = manifest.get(key)
        if not args.force and entry and entry.get("text_hash") == line_hash(spoken, {}) \
                and out.exists() and (args.backend in ("auto", entry.get("backend"))):
            total += entry["duration"]
            print(f"[{idx:02d}/{len(lines)}] {key}: 已缓存（{entry.get('backend')}）{entry['duration']:.1f}s")
            continue
        if backend is None:
            backend = make_backend(args.backend, args.voice, args.instruct, args.speed)
        t0 = time.time()
        audio, sr = backend.synth(spoken)
        if backend.name != "placeholder":
            audio = trim_and_normalize(audio, sr)
        write_wav(out, audio, sr)
        dur = len(audio) / sr
        total += dur
        manifest[key] = {"file": out.name, "duration": round(dur, 3), "backend": backend.name,
                         "text_hash": line_hash(spoken, {})}
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
        print(f"[{idx:02d}/{len(lines)}] {key}: {dur:.1f}s，用时 {time.time() - t0:.1f}s")

    print(f"[tts] 完成：{len(lines)} 句，总时长 {total / 60:.1f} 分钟 -> {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
