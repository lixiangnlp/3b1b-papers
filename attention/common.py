"""场景公共设施：旁白同步、中文字体、3b1b 风格的小部件。"""

from __future__ import annotations

import json
import os
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import manimpango
import numpy as np
from manim import (
    BLUE, BLUE_C, BLUE_D, DOWN, GREY_B, GREY_D, ORIGIN, RED, TEAL, UP, WHITE,
    YELLOW, RoundedRectangle, Scene, Text, VGroup, config, interpolate_color,
    ManimColor,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from narration import NARRATION_BY_KEY  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
AUDIO_DIR = BUILD / "audio"
CUES_DIR = BUILD / "cues"
MANIFEST = AUDIO_DIR / "manifest.json"

config.background_color = "#0F0F14"

# 按优先级挑选本机可用的中文字体（macOS / Linux / Windows）
_CJK_CANDIDATES = [
    os.environ.get("CJK_FONT", ""),
    "PingFang SC", "Hiragino Sans GB", "Source Han Sans SC", "Noto Sans CJK SC",
    "Noto Sans SC", "Microsoft YaHei", "WenQuanYi Zen Hei",
]


def _pick_font() -> str:
    available = set(manimpango.list_fonts())
    for name in _CJK_CANDIDATES:
        if name and name in available:
            return name
    return "sans-serif"


CJK_FONT = _pick_font()

Q_COLOR = YELLOW
K_COLOR = TEAL
V_COLOR = RED
E_COLOR = BLUE_C


def zh(text: str, size: float = 34, color=WHITE, **kwargs) -> Text:
    return Text(text, font=CJK_FONT, font_size=size, color=color, **kwargs)


def token_box(word: str, color=BLUE_D, size: float = 30, pad: float = 0.18) -> VGroup:
    label = zh(word, size)
    box = RoundedRectangle(
        corner_radius=0.08,
        width=max(label.width + 2 * pad, 0.7),
        height=label.height + 2 * pad,
        stroke_color=color, fill_color=color, fill_opacity=0.25, stroke_width=2,
    )
    label.move_to(box)
    return VGroup(box, label)


def heat_color(value: float, lo: float = -1.0, hi: float = 1.0) -> ManimColor:
    """蓝(低) - 黑 - 红(高) 的发散色标。"""
    t = float(np.clip((value - lo) / (hi - lo), 0, 1))
    if t < 0.5:
        return interpolate_color(ManimColor(BLUE), ManimColor(GREY_D), t * 2)
    return interpolate_color(ManimColor(GREY_D), ManimColor(RED), (t - 0.5) * 2)


def softmax(x, axis=-1):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


# ---------------------------------------------------------------- 旁白同步

CHARS_PER_SEC = 4.3  # 没有音频时估算时长用


def estimate_duration(text: str) -> float:
    cjk = len(re.findall(r"[一-鿿]", text))
    words = len(re.findall(r"[A-Za-z0-9.]+", text))
    pauses = len(re.findall(r"[，。；：？！、,.;:?!]", text))
    return cjk / CHARS_PER_SEC + words * 0.35 + pauses * 0.15


def _load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


@dataclass
class Voice:
    key: str
    text: str
    duration: float
    audio: Path | None


class VoiceScene(Scene):
    """带旁白的场景。

    用法::

        with self.voice("qkv_1") as v:
            self.play(Write(title), run_time=2)
        # 离开 with 块时自动 wait 到这句旁白读完

    若 build/audio 下有对应 wav，则嵌入音轨；否则按字数估算时长（静音预览）。
    每句的起止时间会写到 build/cues/<Scene>.json，供合成字幕使用。
    """

    pad_after = 0.35  # 句与句之间的停顿（秒）

    def setup(self):
        self._manifest = _load_manifest()
        self._cues: list[dict] = []

    def _resolve(self, key: str) -> Voice:
        text = NARRATION_BY_KEY[key]
        entry = self._manifest.get(key)
        if entry:
            path = AUDIO_DIR / entry["file"]
            if path.exists():
                return Voice(key, text, float(entry["duration"]), path)
        return Voice(key, text, estimate_duration(text), None)

    @property
    def now(self) -> float:
        return self.renderer.time

    @contextmanager
    def voice(self, key: str):
        v = self._resolve(key)
        start = self.now
        if v.audio is not None:
            self.add_sound(str(v.audio))
        yield v
        remaining = start + v.duration + self.pad_after - self.now
        if remaining > 1e-3:
            self.wait(remaining)
        elif remaining < -0.5:
            print(f"[voice] {type(self).__name__}/{key}: 动画比旁白长 {-remaining:.1f}s，"
                  f"会出现停顿，可考虑缩短 run_time")
        self._cues.append({"key": key, "start": start, "end": start + v.duration,
                           "text": v.text})

    def tear_down(self):
        CUES_DIR.mkdir(parents=True, exist_ok=True)
        out = CUES_DIR / f"{type(self).__name__}.json"
        out.write_text(json.dumps({"duration": self.now, "cues": self._cues},
                                  ensure_ascii=False, indent=1), encoding="utf-8")

    def clear(self, run_time: float = 0.8):
        from manim import FadeOut
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)


__all__ = [
    "VoiceScene", "zh", "token_box", "heat_color", "softmax", "CJK_FONT",
    "Q_COLOR", "K_COLOR", "V_COLOR", "E_COLOR", "GREY_B", "ORIGIN", "UP", "DOWN",
]
