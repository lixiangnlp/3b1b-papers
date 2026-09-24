"""用本机部署的 Qwen3-TTS-1.7B（MLX，Apple Silicon）为旁白逐句生成音频。

输出:
  build/audio/<key>.wav        每句一个 24kHz 单声道 wav
  build/audio/manifest.json    {key: {file, duration, hash}}，供 Manim 场景同步

用法:
  python tts/qwen3_tts.py                          # 生成全部（已生成且未修改的句子会跳过）
  python tts/qwen3_tts.py --only qkv_1 qkv_2       # 只生成指定句子
  python tts/qwen3_tts.py --speaker Serena --instruct "语速稍快，热情"
  python tts/qwen3_tts.py --placeholder            # 无 MLX 环境：按字数生成静音占位音频
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "attention"))
from narration import NARRATION, speakable  # noqa: E402

AUDIO_DIR = ROOT / "build" / "audio"
MANIFEST = AUDIO_DIR / "manifest.json"

DEFAULT_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
LOCAL_MODEL = ROOT / "models" / "Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16"
DEFAULT_SPEAKER = "Uncle_Fu"
DEFAULT_INSTRUCT = "用平和、清晰、富有好奇心的语气讲解，像一位耐心的数学老师，语速适中，重点词稍作强调。"
DEFAULT_DESIGN = "一位三十多岁的男性科普讲解员，普通话标准，嗓音温暖低沉，语气平和、清晰，带着对数学的热情。"


def write_wav(path: Path, audio: np.ndarray, sr: int) -> None:
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def trim_and_normalize(audio: np.ndarray, sr: int, thresh_db: float = -45.0,
                       keep: float = 0.08, peak_db: float = -1.0) -> np.ndarray:
    """去掉首尾静音（各保留 keep 秒），并做峰值归一化。"""
    audio = audio.astype(np.float32)
    if audio.size == 0:
        return audio
    win = max(1, int(sr * 0.02))
    frames = audio[: len(audio) // win * win].reshape(-1, win)
    rms_db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    voiced = np.where(rms_db > thresh_db)[0]
    if voiced.size:
        start = max(0, voiced[0] * win - int(keep * sr))
        end = min(len(audio), (voiced[-1] + 1) * win + int(keep * sr))
        audio = audio[start:end]
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio * (10 ** (peak_db / 20) / peak)
    return audio


def line_hash(text: str, cfg: dict) -> str:
    blob = json.dumps({"text": text, **cfg}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


class QwenTTS:
    """mlx-audio 上的 Qwen3-TTS 推理封装，支持 CustomVoice / VoiceDesign / Base 三种变体。"""

    def __init__(self, model: str, mode: str, speaker: str, instruct: str | None,
                 temperature: float, seed: int | None):
        import mlx.core as mx
        from mlx_audio.tts.utils import load_model

        self.mx = mx
        self.mode = mode
        self.speaker = speaker
        self.instruct = instruct
        self.temperature = temperature
        self.seed = seed
        t0 = time.time()
        print(f"[tts] 加载模型 {model} ...")
        self.model = load_model(model)
        self.sr = int(getattr(self.model, "sample_rate", 24000))
        print(f"[tts] 模型就绪（{time.time() - t0:.1f}s），采样率 {self.sr} Hz")

    def synth(self, text: str) -> np.ndarray:
        if self.seed is not None:
            self.mx.random.seed(self.seed)
        common = dict(text=text, language="chinese", temperature=self.temperature)
        if self.mode == "custom":
            gen = self.model.generate_custom_voice(speaker=self.speaker, instruct=self.instruct, **common)
        elif self.mode == "design":
            gen = self.model.generate_voice_design(instruct=self.instruct or DEFAULT_DESIGN, **common)
        else:
            gen = self.model.generate(text=text, voice=self.speaker, lang_code="chinese",
                                      temperature=self.temperature)
        chunks = [np.array(r.audio, dtype=np.float32) for r in gen]
        return np.concatenate(chunks) if chunks else np.zeros(0, np.float32)


def placeholder_audio(text: str, sr: int = 24000) -> np.ndarray:
    sys.path.insert(0, str(ROOT / "attention"))
    from common import estimate_duration
    return np.zeros(int(estimate_duration(text) * sr), np.float32)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=None,
                    help=f"HF 仓库名或本地目录（默认优先 {LOCAL_MODEL.relative_to(ROOT)}，否则 {DEFAULT_MODEL}）")
    ap.add_argument("--mode", choices=["custom", "design", "base"], default="custom",
                    help="custom=预置音色+情感指令（1.7B-CustomVoice）；design=文字描述音色（1.7B-VoiceDesign）")
    ap.add_argument("--speaker", default=DEFAULT_SPEAKER,
                    help="CustomVoice 音色：Vivian / Serena / Uncle_Fu / Dylan / Eric / Ryan / Aiden")
    ap.add_argument("--instruct", default=None, help="情感/风格指令（design 模式下为音色描述）")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42, help="固定随机种子，让重跑结果更稳定")
    ap.add_argument("--only", nargs="*", help="只生成这些 key")
    ap.add_argument("--force", action="store_true", help="忽略缓存，全部重新生成")
    ap.add_argument("--placeholder", action="store_true", help="不调用模型，生成按字数估时的静音占位")
    args = ap.parse_args()

    model = args.model or (str(LOCAL_MODEL) if LOCAL_MODEL.exists() else DEFAULT_MODEL)
    instruct = args.instruct if args.instruct is not None else (
        DEFAULT_INSTRUCT if args.mode == "custom" else DEFAULT_DESIGN if args.mode == "design" else None)
    cfg = {"model": Path(model).name, "mode": args.mode, "speaker": args.speaker,
           "instruct": instruct, "temperature": args.temperature, "seed": args.seed,
           "placeholder": args.placeholder}

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text("utf-8")) if MANIFEST.exists() else {}

    lines = [(k, t) for scene in NARRATION.values() for k, t in scene]
    if args.only:
        lines = [(k, t) for k, t in lines if k in set(args.only)]

    tts = None
    total = 0.0
    for idx, (key, text) in enumerate(lines, 1):
        spoken = speakable(text)
        h = line_hash(spoken, cfg)
        out = AUDIO_DIR / f"{key}.wav"
        entry = manifest.get(key)
        if not args.force and entry and entry.get("hash") == h and out.exists():
            total += entry["duration"]
            print(f"[{idx:02d}/{len(lines)}] {key}: 已缓存 {entry['duration']:.1f}s")
            continue

        t0 = time.time()
        if args.placeholder:
            sr, audio = 24000, placeholder_audio(text)
        else:
            if tts is None:
                tts = QwenTTS(model, args.mode, args.speaker, instruct, args.temperature, args.seed)
            sr = tts.sr
            audio = trim_and_normalize(tts.synth(spoken), sr)
        write_wav(out, audio, sr)
        dur = len(audio) / sr
        total += dur
        manifest[key] = {"file": out.name, "duration": round(dur, 3), "hash": h}
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
        print(f"[{idx:02d}/{len(lines)}] {key}: {dur:.1f}s 音频，用时 {time.time() - t0:.1f}s")

    print(f"[tts] 完成：{len(lines)} 句，总时长 {total / 60:.1f} 分钟 -> {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
