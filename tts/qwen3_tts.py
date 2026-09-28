"""Qwen3-TTS-1.7B（MLX，Apple Silicon）推理封装 + 公共音频工具。

逐句合成的主入口已移到 tts/synth.py（支持云端 TTS / 本机服务 / 多种后端）；
本文件保留 QwenTTS 类，供 synth.py 与 qwen3_server.py 复用。

"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

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


def main() -> None:
    """兼容旧用法：等价于 ``python tts/synth.py --backend qwen-mlx``。"""
    sys.argv[1:1] = ["--backend", "qwen-mlx"]
    from synth import main as synth_main
    synth_main()


if __name__ == "__main__":
    main()
