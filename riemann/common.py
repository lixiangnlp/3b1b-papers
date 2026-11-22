"""黎曼猜想一期的场景公共设施：旁白同步、中文/等宽字体、配色与小部件。

VoiceScene 的用法与 attention/common.py 相同，只是音频、cues 都放在 build/riemann/ 下。
"""

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
    BLUE_C, GREY_B, GREY_D, ORANGE, RED, TEAL, WHITE, YELLOW,
    RoundedRectangle, Scene, Text, VGroup, config, DOWN, LEFT, RIGHT, UP,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from narration import NARRATION_BY_KEY  # noqa: E402
from projects import PROJECTS  # noqa: E402

PROJECT = PROJECTS["riemann"]
BUILD = PROJECT.build
AUDIO_DIR = PROJECT.audio_dir
CUES_DIR = BUILD / "cues"
DATA_DIR = BUILD / "data"
MANIFEST = AUDIO_DIR / "manifest.json"

config.background_color = "#0F0F14"

_CJK_CANDIDATES = [
    os.environ.get("CJK_FONT", ""),
    "PingFang SC", "Hiragino Sans GB", "Source Han Sans SC", "Noto Sans CJK SC",
    "Noto Sans SC", "Microsoft YaHei", "WenQuanYi Zen Hei",
]
_MONO_CANDIDATES = [os.environ.get("MONO_FONT", ""), "JetBrains Mono", "Menlo",
                    "SF Mono", "DejaVu Sans Mono", "Consolas", "Courier New"]


def _pick(cands: list[str], fallback: str) -> str:
    available = set(manimpango.list_fonts())
    for name in cands:
        if name and name in available:
            return name
    return fallback


CJK_FONT = _pick(_CJK_CANDIDATES, "sans-serif")
MONO_FONT = _pick(_MONO_CANDIDATES, "monospace")

PRIME_COLOR = YELLOW
ZERO_COLOR = RED
LINE_COLOR = YELLOW
STRIP_COLOR = BLUE_C
CLAUDE_COLOR = "#D97757"
HUMAN_COLOR = TEAL
LEAN_COLOR = "#7FB2F0"
OK_COLOR = "#83C167"

# 黎曼 ζ 函数前 100 个非平凡零点的虚部（上半平面），由 mpmath.zetazero 计算，保留 6 位小数
_ZERO_CACHE = DATA_DIR / "zeta_zeros.json"


def zeta_zeros(n: int = 100) -> list[float]:
    if _ZERO_CACHE.exists():
        zs = json.loads(_ZERO_CACHE.read_text())
        if len(zs) >= n:
            return zs[:n]
    import mpmath
    mpmath.mp.dps = 20
    zs = [round(float(mpmath.zetazero(k).imag), 6) for k in range(1, n + 1)]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _ZERO_CACHE.write_text(json.dumps(zs))
    return zs


def zh(text: str, size: float = 34, color=WHITE, **kwargs) -> Text:
    return Text(text, font=CJK_FONT, font_size=size, color=color, **kwargs)


def mono(text: str, size: float = 26, color=WHITE, **kwargs) -> Text:
    return Text(text, font=MONO_FONT, font_size=size, color=color, **kwargs)


def tag(word: str, color=BLUE_C, size: float = 28, pad: float = 0.18, font: str | None = None) -> VGroup:
    label = Text(word, font=font or CJK_FONT, font_size=size, color=WHITE)
    box = RoundedRectangle(
        corner_radius=0.08,
        width=max(label.width + 2 * pad, 0.7),
        height=label.height + 2 * pad,
        stroke_color=color, fill_color=color, fill_opacity=0.25, stroke_width=2,
    )
    label.move_to(box)
    return VGroup(box, label)


def quote_card(en: str, zh_text: str | None = None, source: str | None = None,
               width: float = 11.5, en_size: float = 30, color=WHITE, t2c: dict | None = None) -> VGroup:
    """英文原文（斜体）+ 中文译文 + 出处的引用卡片。"""
    parts = [Text(en, font="Latin Modern Roman", slant="ITALIC", font_size=en_size, color=WHITE if t2c else color,
                  line_spacing=1.1, t2c=t2c or {})]
    if zh_text:
        parts.append(zh(zh_text, 28, GREY_B))
    if source:
        parts.append(zh(source, 22, GREY_D))
    body = VGroup(*parts).arrange(DOWN, buff=0.35)
    if body.width > width - 0.8:
        body.scale_to_fit_width(width - 0.8)
    frame = RoundedRectangle(corner_radius=0.15, width=width, height=body.height + 0.9,
                             stroke_color=GREY_D, stroke_width=2, fill_color="#1A1A22",
                             fill_opacity=1)
    bar = RoundedRectangle(corner_radius=0.04, width=0.08, height=body.height + 0.5,
                           stroke_width=0, fill_color=color, fill_opacity=0.9)
    body.move_to(frame)
    bar.next_to(frame.get_left(), RIGHT, buff=0.18)
    return VGroup(frame, bar, body)


def check_mark(color=OK_COLOR, size: float = 40) -> Text:
    return Text("✓", font="DejaVu Sans", font_size=size, color=color, weight="BOLD")


def cross_mark(color=RED, size: float = 40) -> Text:
    return Text("✗", font="DejaVu Sans", font_size=size, color=color, weight="BOLD")


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
    """带旁白的场景（见 attention/common.py 的说明）。"""

    pad_after = 0.35

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

    def remaining(self, v: Voice, margin: float = 0.0) -> float:
        """这句旁白还剩多少秒（用于把一段动画铺满整句）。"""
        return max(0.5, v.duration - margin - (self.now - self._voice_start(v)))

    def _voice_start(self, v: Voice) -> float:
        return getattr(v, "_start", self.now)

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
    "VoiceScene", "zh", "mono", "tag", "quote_card", "check_mark", "cross_mark", "zeta_zeros",
    "CJK_FONT", "MONO_FONT", "PRIME_COLOR", "ZERO_COLOR", "LINE_COLOR", "STRIP_COLOR",
    "CLAUDE_COLOR", "HUMAN_COLOR", "LEAN_COLOR", "OK_COLOR", "GREY_B", "GREY_D",
    "UP", "DOWN", "LEFT", "RIGHT", "ORANGE",
]
