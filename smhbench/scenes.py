"""《SMH-Bench》3Blue1Brown 风格中文讲解（完整版）—— Manim 场景。

渲染单个场景:  manim -qm smhbench/scenes.py S12_Overall
整片构建:      python build.py all --paper smhbench

图表数据取自论文表 2、图 3、图 4 正文数值、图 6。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from common import VoiceScene, token_box, zh  # noqa: E402

ON = YELLOW
OFF = GREY_D
OK = GREEN_C
BAD = RED_C
DR_COLOR = TEAL
EIA_COLOR = ORANGE
MONO = "DejaVu Sans Mono"

# 七大类（TC1–TC7），配色在全片保持一致
TC = [
    ("TC1", "原子控制", BLUE_C),
    ("TC2", "组合控制", TEAL),
    ("TC3", "模糊意图", PURPLE_B),
    ("TC4", "自动化调度", ORANGE),
    ("TC5", "多轮交互", GREEN_C),
    ("TC6", "个性化记忆", PINK),
    ("TC7", "环境查询", GOLD),
]
TC_COUNT = [150, 250, 150, 150, 200, 100, 150]

# 表 2：模型 -> (DR[TC1..TC7, Avg], EIA[TC1..TC7, Avg])
TABLE2 = {
    "Qwen3.5-4B": ([68.7, 35.6, 44.7, 24.0, 48.0, 39.0, 75.0, 45.9], [69.3, 45.6, 72.0, 21.3, 65.0, 57.0, 76.0, 56.5]),
    "Qwen3.5-9B": ([73.3, 38.0, 47.3, 25.3, 51.5, 47.0, 77.0, 49.2], [76.7, 56.0, 69.3, 36.0, 74.0, 65.0, 81.0, 64.3]),
    "Qwen3.5-397B": ([92.7, 72.0, 76.7, 60.0, 85.0, 75.0, 84.0, 77.6], [88.0, 68.8, 86.7, 69.3, 74.5, 77.0, 92.0, 77.8]),
    "DeepSeek-V3.2": ([79.3, 60.8, 65.3, 52.0, 80.0, 68.0, 89.0, 69.5], [87.3, 52.8, 85.3, 64.0, 85.0, 74.0, 94.0, 75.5]),
    "MiniMax-M2.7": ([81.3, 55.6, 60.7, 38.7, 32.5, 32.0, 63.0, 51.8], [57.3, 23.6, 52.0, 42.0, 41.0, 27.0, 90.0, 52.1]),
    "GLM-5": ([80.7, 50.0, 49.3, 52.0, 71.0, 39.0, 78.0, 59.7], [88.7, 65.6, 83.3, 42.7, 76.0, 51.0, 87.0, 70.6]),
    "Qwen3.5-Plus": ([79.3, 51.6, 51.3, 50.0, 74.0, 71.0, 69.0, 62.6], [91.3, 57.2, 76.7, 42.7, 79.5, 65.0, 87.0, 70.0]),
    "GPT-5.4-Mini": ([80.7, 66.0, 61.3, 45.3, 79.0, 62.0, 89.0, 68.6], [89.3, 68.8, 86.0, 50.7, 81.0, 69.0, 86.0, 75.3]),
    "GPT-5.4": ([91.3, 78.8, 78.0, 65.3, 85.5, 75.0, 95.0, 80.9], [94.0, 78.0, 84.7, 49.3, 86.5, 74.0, 91.0, 79.6]),
    "Gemini-3.1-Flash": ([89.3, 73.6, 63.3, 62.7, 72.5, 71.0, 91.0, 74.2], [86.7, 69.6, 84.7, 48.7, 80.0, 73.0, 95.0, 75.6]),
    "Gemini-3.1-Pro": ([95.3, 81.2, 72.7, 70.7, 87.5, 88.0, 94.0, 83.5], [94.0, 84.4, 92.0, 64.0, 88.5, 86.0, 88.0, 85.2]),
    "Claude-Haiku-4.5": ([90.0, 73.2, 72.7, 64.0, 82.0, 77.0, 79.0, 76.6], [88.0, 73.6, 85.3, 48.0, 81.0, 73.0, 87.0, 76.2]),
    "Claude-Sonnet-4.6": ([90.7, 73.2, 61.3, 68.7, 84.0, 77.0, 85.0, 76.7], [93.3, 81.2, 91.3, 68.7, 85.0, 80.0, 92.0, 84.1]),
}
OPEN_SOURCE = {"Qwen3.5-4B", "Qwen3.5-9B", "Qwen3.5-397B", "DeepSeek-V3.2", "MiniMax-M2.7", "GLM-5"}


def mono(text: str, size: float = 24, color=WHITE) -> Text:
    return Text(text, font=MONO, font_size=size, color=color)


def math(text: str, size: float = 40, color=WHITE) -> Text:
    """无 LaTeX 的公式：衬线斜体。"""
    return Text(text, font="DejaVu Serif", font_size=size, color=color, slant=ITALIC)


def device(name: str, on: bool = False, color=BLUE_D, size: float = 22) -> VGroup:
    card = token_box(name, color, size, pad=0.14)
    lamp = Dot(radius=0.07, color=ON if on else OFF).move_to(card[0].get_corner(UR) + DL * 0.12)
    g = VGroup(card, lamp)
    g.lamp = lamp
    return g


def set_lamp(dev: VGroup, on: bool):
    return dev.lamp.animate.set_color(ON if on else OFF)


def room(name: str, w: float, h: float, color=GREY_B, size: float = 22) -> VGroup:
    box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2)
    label = zh(name, size, color).next_to(box.get_corner(UL), DR, buff=0.1)
    return VGroup(box, label)


def bubble(text: str, size: float = 30, width: float | None = None, color=WHITE) -> VGroup:
    t = zh(text, size, color)
    if width and t.width > width:
        t.scale_to_fit_width(width)
    b = RoundedRectangle(corner_radius=0.25, width=t.width + 0.6, height=t.height + 0.5,
                         stroke_color=GREY_B, fill_color=GREY_E, fill_opacity=0.7)
    t.move_to(b)
    return VGroup(b, t)


def tc_chip(i: int, size: float = 24, full: bool = True) -> VGroup:
    code, name, col = TC[i]
    return token_box(f"{code} {name}" if full else code, col, size)


def section_title(text: str, color=YELLOW) -> Text:
    return zh(text, 36, color).to_edge(UP, buff=0.45)


def heat(v: float) -> ManimColor:
    """成功率 20%→95% 映射到 深蓝 → 青 → 黄。"""
    t = float(np.clip((v - 20) / 75, 0, 1))
    if t < 0.5:
        return interpolate_color(ManimColor("#1d2b53"), ManimColor(TEAL_D), t * 2)
    return interpolate_color(ManimColor(TEAL_D), ManimColor(YELLOW), (t - 0.5) * 2)


# ====================================================================== 1 开场
class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("intro_1"):
            spk = VGroup(Circle(0.4, color=BLUE_C, fill_opacity=0.3), zh("音箱", 18).shift(DOWN * 0.65))
            say = bubble("“有点冷，把我常待的那几个房间的暖气，\n调成和昨晚一样的温度。”", 30)
            grp = VGroup(spk, say).arrange(RIGHT, buff=0.5)
            self.play(FadeIn(spk, shift=RIGHT * 0.3))
            self.play(GrowFromCenter(say[0]), Write(say[1]), run_time=2.5)
            self.say = VGroup(spk, say)

        with self.voice("intro_2"):
            self.play(self.say.animate.scale(0.6).to_edge(UP, buff=0.3))
            steps = VGroup(
                self._need("查实时温度", "客厅 18°  书房 17°  卧室 20°", BLUE_C),
                self._need("翻对话历史", "昨晚：24°", PINK),
                self._need("判断常待房间", "客厅 · 书房", GREEN_C),
            ).arrange(RIGHT, buff=0.5).shift(DOWN * 0.3)
            for s in steps:
                self.play(FadeIn(s, shift=UP * 0.3), run_time=0.8)
                self.wait(1.2)
            self.steps = steps

        with self.voice("intro_3"):
            words = VGroup(*[zh(w, 44, c) for w, c in
                             [("理解", BLUE_C), ("推理", TEAL), ("记忆", PINK), ("行动", YELLOW)]])
            words.arrange(RIGHT, buff=0.9).shift(DOWN * 0.3)
            self.play(FadeOut(self.steps))
            self.play(LaggedStart(*[FadeIn(w, scale=1.3) for w in words], lag_ratio=0.35), run_time=2.5)
            self.words = words

        with self.voice("intro_4"):
            self.play(FadeOut(self.words), FadeOut(self.say))
            title = Text("SMH-Bench", font_size=84, weight=BOLD, color=BLUE_B)
            sub = Text("Benchmarking LLM Agents for Environment-Grounded\nReasoning and Action in Smart Homes",
                       font_size=26, color=GREY_B, line_spacing=0.8)
            aff = zh("美的集团 AI 研究中心 · 北京邮电大学 · 东华大学 · 悉尼大学 · 北京大学", 22, GREY_B)
            meta = Text("Kuan Li, Shuo Zhang, Huacan Wang, … , Yi Xu   ·   arXiv:2606.01912   ·   2026.06",
                        font_size=20, color=GREY_B)
            self.head = VGroup(title, sub, aff, meta).arrange(DOWN, buff=0.3).shift(UP * 0.4)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(sub, shift=UP * 0.2))
            self.play(FadeIn(aff), FadeIn(meta))

        with self.voice("intro_5"):
            env = token_box("HomeEnv  可执行 · 可验证", TEAL_D, 26)
            n = token_box("1,100 个人工审核任务", YELLOW, 26)
            row = VGroup(env, n).arrange(RIGHT, buff=0.8).next_to(self.head, DOWN, buff=0.6)
            self.play(FadeIn(env, shift=UP * 0.2))
            self.play(FadeIn(n, shift=UP * 0.2))
            self.row = row

        with self.voice("intro_6"):
            self.play(FadeOut(self.head), FadeOut(self.row))
            parts = VGroup(*[
                VGroup(Text(f"{i + 1}", font_size=60, color=c), zh(t, 34))
                .arrange(DOWN, buff=0.3)
                for i, (t, c) in enumerate([("基准怎么搭", BLUE_C), ("模型成绩单", YELLOW), ("错在哪里", BAD)])
            ]).arrange(RIGHT, buff=1.8)
            self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.3) for p in parts], lag_ratio=0.5), run_time=3)
        self.clear()

    def _need(self, title, detail, color):
        t = zh(title, 28, color)
        d = zh(detail, 22, GREY_A)
        g = VGroup(t, d).arrange(DOWN, buff=0.3)
        frame = SurroundingRectangle(g, color=color, buff=0.3, corner_radius=0.15)
        return VGroup(frame, g)


# ====================================================================== 2 动机
class S02_Motivation(VoiceScene):
    def construct(self):
        with self.voice("mot_1"):
            inst = zh("“关掉卧室的灯”", 30)
            api = mono('light.turn_off(\n  "bedroom")', 22, BLUE_B)
            gold = mono('light.turn_off(\n  "bedroom")', 22, GREEN_B)
            row = VGroup(inst, api, gold).arrange(RIGHT, buff=1.2).shift(UP * 1.6)
            a1 = Arrow(inst.get_right(), api.get_left(), buff=0.15, color=GREY_B)
            eq = Text("=?", font_size=36, color=YELLOW).move_to((api.get_right() + gold.get_left()) / 2)
            labels = VGroup(zh("指令", 20, GREY_B).next_to(inst, UP),
                            zh("模型输出", 20, GREY_B).next_to(api, UP),
                            zh("标准答案", 20, GREY_B).next_to(gold, UP))
            self.play(FadeIn(inst), FadeIn(labels[0]))
            self.play(GrowArrow(a1), Write(api), FadeIn(labels[1]))
            self.play(Write(gold), FadeIn(labels[2]), FadeIn(eq))
            self.top = VGroup(row, a1, eq, labels)

        with self.voice("mot_2"):
            r = room("卧室", 6.5, 2.4).shift(DOWN * 1.2)
            lamps = VGroup(device("吸顶灯", True), device("床头灯 A", True),
                           device("床头灯 B", False)).arrange(RIGHT, buff=0.7).move_to(r[0])
            self.play(Create(r), LaggedStart(*[FadeIn(d) for d in lamps], lag_ratio=0.2))
            q = zh("状态？反馈？", 26, YELLOW).next_to(r, RIGHT, buff=0.3)
            self.play(Write(q))
            self.play(set_lamp(lamps[0], False), set_lamp(lamps[1], False), run_time=1.2)
            alt = mono('turn_off("bed_1"); turn_off("bed_2")', 20, BLUE_B).next_to(r, UP, buff=0.25)
            self.play(FadeIn(alt))
            ck = Text("✔", font_size=30, color=OK).next_to(alt, RIGHT)
            self.play(FadeIn(ck))
            self.mid = VGroup(r, lamps, q, alt, ck)

        with self.voice("mot_3"):
            self.play(FadeOut(self.top), FadeOut(self.mid))
            sim = token_box("SimuHome", TEAL_D, 32).shift(UP * 1)
            only = VGroup(token_box("简单查询", GREY_BROWN, 24), token_box("设备控制", GREY_BROWN, 24))
            only.arrange(RIGHT, buff=0.5).next_to(sim, DOWN, buff=0.6)
            self.play(FadeIn(sim))
            self.play(LaggedStart(*[FadeIn(o) for o in only], lag_ratio=0.3))
            self.sim = VGroup(sim, only)

        with self.voice("mot_4"):
            self.play(self.sim.animate.scale(0.6).to_corner(UL))
            real = VGroup(zh("跨设备 · 跨房间", 30), zh("实时状态", 30, BLUE_C),
                          zh("对话上下文", 30, GREEN_C), zh("个人偏好", 30, PINK)).arrange(DOWN, buff=0.35)
            self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.3) for x in real], lag_ratio=0.4), run_time=3)
            self.real = real

        with self.voice("mot_5"):
            self.play(FadeOut(self.real), FadeOut(self.sim))
            self.table = self._table()
            self.play(FadeIn(self.table[0]), FadeIn(self.table[1]))
            self.play(LaggedStart(*[FadeIn(c) for c in self.table[2][0]], lag_ratio=0.1), run_time=2)

        with self.voice("mot_6"):
            self.play(LaggedStart(*[FadeIn(c) for c in self.table[2][1]], lag_ratio=0.1), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(c) for c in self.table[2][2]], lag_ratio=0.1), run_time=1.5)
            self.play(Circumscribe(self.table[2][2], color=YELLOW))
        self.clear()

    def _table(self):
        cols = ["设备查询", "自动化", "澄清判断", "口语纠错", "多轮对话", "个性化记忆", "规模"]
        rows = [("HomeBench", [0, 0, 0, 0, 0, 0], "170K"),
                ("SimuHome", [1, 1, 1, 0, 0, 0], "600"),
                ("SMH-Bench", [1, 1, 1, 1, 1, 1], "1,100")]
        xs = np.linspace(-2.9, 5.6, len(cols))
        ys = [0.6, -0.4, -1.4]
        header = VGroup(*[zh(c, 22, GREY_B).move_to([x, 1.6, 0]) for x, c in zip(xs, cols)])
        names = VGroup(*[Text(n, font_size=28, color=YELLOW if n == "SMH-Bench" else WHITE)
                         .move_to([-5.3, y, 0]) for (n, _, _), y in zip(rows, ys)])
        cells = VGroup()
        for (n, marks, size), y in zip(rows, ys):
            row = VGroup()
            for x, m in zip(xs, marks):
                row.add(Text("✔" if m else "✘", font_size=30, color=OK if m else BAD).move_to([x, y, 0]))
            row.add(Text(size, font_size=28).move_to([xs[-1], y, 0]))
            cells.add(row)
        return VGroup(header, names, cells)


# ====================================================================== 3 形式化
class S03_Formulation(VoiceScene):
    def construct(self):
        title = section_title("任务形式化")
        with self.voice("form_1"):
            self.play(Write(title))
            h = math("Hₜ = ( R ,  D ,  φ ,  Xₜ ,  S )", 56).shift(UP * 1.4)
            self.play(Write(h), run_time=2)
            self.h = h

        with self.voice("form_2"):
            # 每个符号的位置（按字符索引近似取子对象）
            desc = [("R", "房间集合", BLUE_C), ("D", "设备集合", TEAL), ("φ", "设备 → 所在房间", GREEN_C),
                    ("Xₜ", "t 时刻的动态属性", YELLOW), ("S", "可调用的服务与参数", PINK)]
            cards = VGroup(*[VGroup(math(s, 36, c), zh(d, 24)).arrange(RIGHT, buff=0.4) for s, d, c in desc])
            cards.arrange(DOWN, aligned_edge=LEFT, buff=0.32).shift(DOWN * 1.2)
            for c in cards:
                self.play(FadeIn(c, shift=RIGHT * 0.2), run_time=0.6)
                self.wait(1.1)
            self.cards = cards

        with self.voice("form_3"):
            self.play(FadeOut(self.cards))
            a = math("a = [ dⱼ . sₖ ( p ) ]", 48, YELLOW).shift(DOWN * 0.2)
            self.play(Write(a))
            ex = mono('light_6152.set_brightness(70)', 26, BLUE_B).next_to(a, DOWN, buff=0.4)
            self.play(FadeIn(ex, shift=UP * 0.2))
            t = math("Hₜ₊₁ = T ( Hₜ ,  a )", 44).next_to(ex, DOWN, buff=0.5)
            self.play(Write(t))
            self.act = VGroup(a, ex, t)

        with self.voice("form_4"):
            self.play(FadeOut(self.act), FadeOut(self.h))
            states = VGroup(*[Circle(0.45, color=BLUE_C, fill_opacity=0.15) for _ in range(4)])
            states.arrange(RIGHT, buff=1.6)
            labels = VGroup(*[math(s, 30).move_to(c) for s, c in zip(["H₀", "H₁", "H₂", "Hₙ"], states)])
            arrows = VGroup(*[Arrow(states[i].get_right(), states[i + 1].get_left(), buff=0.1, color=GREY_B)
                              for i in range(3)])
            alabels = VGroup(*[math(s, 26, YELLOW).next_to(ar, UP, buff=0.1)
                               for s, ar in zip(["a₁", "a₂", "…"], arrows)])
            self.play(FadeIn(states[0]), FadeIn(labels[0]))
            for i in range(3):
                self.play(GrowArrow(arrows[i]), FadeIn(alabels[i]), FadeIn(states[i + 1]), FadeIn(labels[i + 1]),
                          run_time=0.8)
            self.chain = VGroup(states, labels, arrows, alabels)

        with self.voice("form_5"):
            self.play(self.chain.animate.scale(0.6).to_edge(UP, buff=1.2))
            tau = math("τ = ( H₀ ,  u ,  C ,  M ,  g )", 52).shift(UP * 0.1)
            self.play(Write(tau))
            desc = VGroup(*[VGroup(math(s, 30, c), zh(d, 22)).arrange(DOWN, buff=0.15)
                            for s, d, c in [("H₀", "初始状态", BLUE_C), ("u", "用户指令", WHITE),
                                            ("C", "对话历史", GREEN_C), ("M", "用户记忆", PINK),
                                            ("g", "任务目标", YELLOW)]]).arrange(RIGHT, buff=0.8)
            desc.next_to(tau, DOWN, buff=0.6)
            self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.2) for d in desc], lag_ratio=0.3), run_time=3)
            self.tau = VGroup(tau, desc)

        with self.voice("form_6"):
            self.play(FadeOut(self.tau), FadeOut(self.chain))
            outs = VGroup(token_box("服务调用", BLUE_D, 28), token_box("自然语言回答", GOLD, 28),
                          token_box("澄清问题", PURPLE_B, 28), token_box("定时规则", ORANGE, 28))
            outs.arrange_in_grid(2, 2, buff=(1.2, 0.8)).shift(DOWN * 0.3)
            self.play(LaggedStart(*[FadeIn(o, scale=0.8) for o in outs], lag_ratio=0.4), run_time=2.5)
            self.outs = outs

        with self.voice("form_7"):
            self.play(FadeOut(self.outs))
            r = room("家", 8, 3).shift(DOWN * 0.4)
            devs = VGroup(device("目标灯", False), device("空调", True, TEAL_D), device("窗帘", False, TEAL_D),
                          device("音箱", True)).arrange(RIGHT, buff=0.7).move_to(r[0])
            self.play(Create(r), FadeIn(devs))
            self.play(set_lamp(devs[0], True))
            ok = zh("Hₙ 满足目标", 26, OK).next_to(devs[0], DOWN, buff=0.4)
            self.play(FadeIn(ok))
            keep = SurroundingRectangle(devs[1:], color=YELLOW, buff=0.15)
            kt = zh("无关设备保持不变", 26, YELLOW).next_to(keep, DOWN, buff=0.35)
            self.play(Create(keep), Write(kt))
        self.clear()


# ====================================================================== 4 HomeEnv
class S04_HomeEnv(VoiceScene):
    def construct(self):
        with self.voice("env_1"):
            title = Text("HomeEnv", font_size=72, weight=BOLD, color=BLUE_B).shift(UP * 1.2)
            parts = VGroup(token_box("① 状态空间", BLUE_D, 28), token_box("② 操作引擎", TEAL_D, 28),
                           token_box("③ 交互接口", GOLD_E, 28)).arrange(RIGHT, buff=0.6).shift(DOWN * 0.6)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in parts], lag_ratio=0.4))
            self.head = VGroup(title, parts)

        with self.voice("env_2"):
            self.play(FadeOut(self.head))
            home = room("家", 11, 5.6, GREY_B).shift(DOWN * 0.3)
            bed = room("主卧", 5, 4.2, BLUE_C).move_to(home[0]).shift(LEFT * 2.5)
            bath = room("卫生间", 2.2, 1.8, TEAL).move_to(bed[0]).shift(RIGHT * 1.1 + DOWN * 0.9)
            liv = room("客厅", 4.6, 4.2, BLUE_C).move_to(home[0]).shift(RIGHT * 2.9)
            self.play(Create(home))
            self.play(Create(bed), Create(liv))
            self.play(Create(bath))
            devs = VGroup(device("吸顶灯", True).move_to(bed[0]).shift(LEFT * 1.3 + UP * 0.9),
                          device("空调", True, TEAL_D).move_to(bed[0]).shift(LEFT * 1.3 + DOWN * 0.3),
                          device("排气扇").move_to(bath[0]).shift(DOWN * 0.1),
                          device("电视").move_to(liv[0]).shift(UP * 0.9),
                          device("窗帘", True, TEAL_D).move_to(liv[0]).shift(DOWN * 0.3))
            self.play(LaggedStart(*[FadeIn(d, scale=0.7) for d in devs], lag_ratio=0.2))
            self.home = VGroup(home, bed, bath, liv, devs)
            self.ac = devs[1]

        with self.voice("env_3"):
            self.play(self.home.animate.scale(0.55).to_edge(LEFT, buff=0.3))
            attrs = VGroup(zh("属性（当前状态）", 24, YELLOW),
                           mono("state = on", 20), mono("target_temperature = 26", 20),
                           mono("humidity = 55", 20), mono("mode = cool", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            svcs = VGroup(zh("服务（可执行操作）", 24, TEAL),
                          mono("turn_on() / turn_off()", 20), mono("set_temperature(t: 16–30)", 20),
                          mono("set_mode(cool|heat|dry)", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            panel = VGroup(attrs, svcs).arrange(DOWN, aligned_edge=LEFT, buff=0.5).to_edge(RIGHT, buff=0.9)
            frame = SurroundingRectangle(panel, color=GREY_B, buff=0.25, corner_radius=0.15)
            link = DashedLine(self.ac.get_right(), frame.get_left(), color=GREY_B)
            self.play(Create(link), Create(frame))
            self.play(FadeIn(attrs, shift=LEFT * 0.2))
            self.play(FadeIn(svcs, shift=LEFT * 0.2))
            self.panel = VGroup(frame, panel, link)

        with self.voice("env_4"):
            self.play(FadeOut(self.panel), FadeOut(self.home))
            act = mono('{ device: 空调_主卧, op: set_temperature, args: {t: 24} }', 22, BLUE_B)
            act.shift(UP * 2)
            engine = token_box("操作引擎", TEAL_D, 30)
            checks = VGroup(zh("操作存在？", 24), zh("类型合法？", 24), zh("范围 / 可选值合法？", 24))
            checks.arrange(RIGHT, buff=0.8).shift(DOWN * 1.3)
            a1 = Arrow(act.get_bottom(), engine.get_top(), color=GREY_B)
            self.play(FadeIn(act))
            self.play(GrowArrow(a1), FadeIn(engine))
            self.play(LaggedStart(*[FadeIn(c) for c in checks], lag_ratio=0.4), run_time=2)
            self.eng = VGroup(act, engine, checks, a1)

        with self.voice("env_5"):
            good = VGroup(mono("set_temperature(24)", 22, BLUE_B), zh("✔ 执行，属性更新", 24, OK)).arrange(RIGHT, buff=0.6)
            bad = VGroup(mono("set_temperature(45)", 22, BLUE_B), zh("✘ 拒绝，状态不变", 24, BAD)).arrange(RIGHT, buff=0.6)
            VGroup(good, bad).arrange(DOWN, buff=0.4, aligned_edge=LEFT).shift(DOWN * 2.6)
            self.play(FadeIn(good, shift=UP * 0.2))
            self.play(FadeIn(bad, shift=UP * 0.2))
            self.eng.add(good, bad)

        with self.voice("env_6"):
            self.play(FadeOut(self.eng))
            agent = token_box("智能体", YELLOW, 30).shift(LEFT * 4.5)
            envb = token_box("HomeEnv", TEAL_D, 30).shift(RIGHT * 4.5)
            qs = VGroup(*[mono(s, 20, GREY_A) for s in
                          ["get_layout()", "devices_in(room)", "devices_of(type)", "get_state(d)", "get_services(d)"]])
            qs.arrange(DOWN, aligned_edge=LEFT, buff=0.12).shift(UP * 1.3)
            ql = zh("查询", 24, BLUE_C).next_to(qs, UP, buff=0.2)
            cs = mono("control(d, op, args)", 20, GREY_A).shift(DOWN * 0.8)
            cl = zh("控制", 24, ORANGE).next_to(cs, UP, buff=0.2)
            self.play(FadeIn(agent), FadeIn(envb))
            self.play(FadeIn(ql), LaggedStart(*[FadeIn(q) for q in qs], lag_ratio=0.2), run_time=2)
            self.play(FadeIn(cl), FadeIn(cs))
            obs = Arrow(envb.get_bottom() + DOWN * 0.9, agent.get_bottom() + DOWN * 0.9, path_arc=-0.5,
                        color=GREEN_C)
            ol = zh("观察结果", 22, GREEN_C).next_to(obs, DOWN, buff=0.1)
            self.play(Create(obs), FadeIn(ol))
        self.clear()


# ====================================================================== 5 TC1 / TC2
class S05_Control(VoiceScene):
    def construct(self):
        with self.voice("ctl_1"):
            chips = VGroup(*[tc_chip(i, 24) for i in range(7)])
            chips[:4].arrange(RIGHT, buff=0.3)
            chips[4:].arrange(RIGHT, buff=0.3)
            VGroup(chips[:4], chips[4:]).arrange(DOWN, buff=0.5)
            hdr = zh("7 大类 · 22 个子类", 40, YELLOW).next_to(chips, UP, buff=0.8)
            self.play(Write(hdr))
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips], lag_ratio=0.15), run_time=2.5)
            self.chips, self.hdr = chips, hdr

        with self.voice("ctl_2"):
            self.play(FadeOut(self.hdr), FadeOut(self.chips[1:]), self.chips[0].animate.to_corner(UL))
            subs = VGroup(*[token_box(s, BLUE_E, 22) for s in ["清晰指令", "口语化", "带噪声"]])
            subs.arrange(RIGHT, buff=0.4).next_to(self.chips[0], RIGHT, buff=0.5)
            self.play(LaggedStart(*[FadeIn(s) for s in subs], lag_ratio=0.3))
            say = zh("“把卧室的温湿度传感器，不对，是客厅那个传感器，改个名字。”", 28).shift(UP * 0.5)
            self.play(Write(say), run_time=2)
            wrong = Line(say[2:11].get_left(), say[2:11].get_right(), color=BAD, stroke_width=4)
            self.play(Create(wrong))
            tgt = VGroup(device("卧室传感器", False, GREY_D), device("客厅传感器", True, BLUE_D)).arrange(RIGHT, buff=1.5)
            tgt.shift(DOWN * 1.4)
            x = Text("✘", font_size=30, color=BAD).next_to(tgt[0], DOWN)
            ck = Text("✔", font_size=30, color=OK).next_to(tgt[1], DOWN)
            self.play(FadeIn(tgt), FadeIn(x), FadeIn(ck))
            self.tc1 = VGroup(self.chips[0], subs, say, wrong, tgt, x, ck)

        with self.voice("ctl_3"):
            self.play(FadeOut(self.tc1))
            c2 = tc_chip(1, 26).to_corner(UL)
            subs = VGroup(*[token_box(s, TEAL_E, 24) for s in ["显式多设备", "批量操作", "依赖状态", "依赖房间", "Top-N 选择"]])
            subs.arrange(RIGHT, buff=0.3).shift(UP * 0.5)
            self.play(FadeIn(c2))
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in subs], lag_ratio=0.3), run_time=2.5)
            self.c2, self.subs = c2, subs

        with self.voice("ctl_4"):
            self.play(FadeOut(self.subs))
            say = bubble("“除了走廊，把所有湿度高于 60% 的房间里的风扇和空调都打开。”", 26).next_to(self.c2, DOWN, buff=0.3)
            say.set_x(0)
            self.play(FadeIn(say[0]), Write(say[1]), run_time=2.5)
            self.say = say

        with self.voice("ctl_5"):
            names = ["客厅", "卧室", "书房", "厨房", "走廊", "卫生间"]
            hums = [65, 48, 70, 58, 72, 81]
            rooms = VGroup()
            for n, h in zip(names, hums):
                r = room(n, 3.4, 1.6, GREY_B, 20)
                hv = mono(f"湿度 {h}%", 18, GREY_A).move_to(r[0]).shift(UP * 0.1 + RIGHT * 0.5)
                devs = VGroup(device("风扇", size=16), device("空调", size=16, color=TEAL_D)).arrange(RIGHT, buff=0.15)
                devs.move_to(r[0]).shift(DOWN * 0.4)
                rooms.add(VGroup(r, hv, devs))
            rooms.arrange_in_grid(2, 3, buff=0.25).shift(DOWN * 1.3)
            self.play(FadeIn(rooms))
            # ① 读湿度并筛选
            hi = [i for i, h in enumerate(hums) if h > 60]
            self.play(*[rooms[i][1].animate.set_color(YELLOW) for i in hi],
                      *[rooms[i][0][0].animate.set_stroke(YELLOW, 3) for i in hi])
            # ② 排除走廊
            hall = names.index("走廊")
            self.play(rooms[hall][0][0].animate.set_stroke(BAD, 3), rooms[hall].animate.set_opacity(0.35))
            # ③ 只动目标房间的设备
            targets = [i for i in hi if i != hall]
            self.play(*[set_lamp(rooms[i][2][k], True) for i in targets for k in range(2)], run_time=1.2)
            keep = zh("其余设备：一个都不碰", 24, YELLOW).to_edge(DOWN, buff=0.15)
            self.play(FadeIn(keep))
        self.clear()


# ====================================================================== 6 TC3 / TC4
class S06_Ambiguity(VoiceScene):
    def construct(self):
        with self.voice("amb_1"):
            c3 = tc_chip(2, 26).to_corner(UL)
            say = bubble("“餐厅热得像个蒸笼。”", 40).shift(UP * 0.5)
            self.play(FadeIn(c3))
            self.play(FadeIn(say[0]), Write(say[1]))
            self.c3, self.say = c3, say

        with self.voice("amb_2"):
            self.play(self.say.animate.scale(0.7).shift(UP * 1.2))
            fork = VGroup(
                VGroup(token_box("执行", OK, 28), zh("餐厅空调 → 制冷 24°", 22, GREY_A)).arrange(DOWN, buff=0.25),
                VGroup(token_box("澄清", PURPLE_B, 28), zh("“要开空调还是开窗？”", 22, GREY_A)).arrange(DOWN, buff=0.25),
            ).arrange(RIGHT, buff=2.5).shift(DOWN * 1)
            arrs = VGroup(*[Arrow(self.say.get_bottom(), f[0].get_top(), buff=0.2, color=GREY_B) for f in fork])
            self.play(GrowArrow(arrs[0]), FadeIn(fork[0]))
            self.play(GrowArrow(arrs[1]), FadeIn(fork[1]))
            self.fork = VGroup(fork, arrs)

        with self.voice("amb_3"):
            self.play(FadeOut(self.fork), FadeOut(self.say))
            cols = VGroup(*[
                VGroup(token_box(t, PURPLE_E, 26), zh(e, 24)).arrange(DOWN, buff=0.4)
                for t, e in [("状态层面", "“房间太暗了”"), ("场景层面", "“我要休息一会儿”"),
                             ("缺少参数", "“用烤箱热一下午饭”")]
            ]).arrange(RIGHT, buff=0.9)
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cols], lag_ratio=0.6), run_time=3)
            ask = zh("→ “热几分钟？”", 26, PURPLE_B).next_to(cols[2], DOWN, buff=0.4)
            self.play(Write(ask))
            self.cols = VGroup(cols, ask)

        with self.voice("amb_4"):
            self.play(FadeOut(self.cols), FadeOut(self.c3))
            c4 = tc_chip(3, 26).to_corner(UL)
            now = token_box("立刻执行", GREY_BROWN, 28).shift(LEFT * 3)
            rule = token_box("持久规则  IF … THEN …", ORANGE, 28).shift(RIGHT * 2.5)
            arr = Arrow(now.get_right(), rule.get_left(), color=WHITE)
            self.play(FadeIn(c4), FadeIn(now))
            self.play(GrowArrow(arr), FadeIn(rule))
            self.c4, self.r = c4, VGroup(now, rule, arr)

        with self.voice("amb_5"):
            self.play(FadeOut(self.r))
            rows = VGroup(
                self._rule("按时间", "cron: 0 0 22 * * ?", "锁门 + 布防"),
                self._rule("按状态", "厨房无人 > 900 s", "关玄关风扇灯"),
                self._rule("时间 + 状态", "每天 14:00 且 厨房 > 35°", "启动扫地机"),
            ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).shift(DOWN * 0.2)
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.8)
                self.wait(1.6)
        self.clear()

    def _rule(self, kind, trig, act):
        k = zh(kind, 26, ORANGE)
        k.width  # noqa: B018
        t = VGroup(zh("触发", 20, GREY_B), mono(trig, 20, YELLOW)).arrange(RIGHT, buff=0.2)
        a = VGroup(zh("动作", 20, GREY_B), zh(act, 22)).arrange(RIGHT, buff=0.2)
        g = VGroup(k, t, Arrow(ORIGIN, RIGHT * 0.8, color=GREY_B), a).arrange(RIGHT, buff=0.35)
        k.set_x(-5.3)
        VGroup(*g[1:]).next_to(k, RIGHT, buff=0.6).shift(RIGHT * (1.9 - k.width))
        return g


# ====================================================================== 7 TC5 / TC6 / TC7
class S07_Context(VoiceScene):
    def construct(self):
        with self.voice("ctx_1"):
            c5 = tc_chip(4, 26).to_corner(UL)
            prev = bubble("上一轮：打开次卧风扇灯，方向正转", 24).shift(UP * 1 + LEFT * 2)
            cur = bubble("这一轮：……", 24).shift(DOWN * 0.3 + RIGHT * 2)
            opts = VGroup(zh("继承", 28, GREEN_C), zh("修改", 28, YELLOW), zh("替换", 28, BAD)).arrange(RIGHT, buff=0.8)
            opts.shift(DOWN * 1.8)
            self.play(FadeIn(c5), FadeIn(prev))
            self.play(FadeIn(cur))
            self.play(LaggedStart(*[FadeIn(o, scale=1.2) for o in opts], lag_ratio=0.3))
            self.c5, self.g = c5, VGroup(prev, cur, opts)

        with self.voice("ctx_2"):
            self.play(FadeOut(self.g))
            items = VGroup(*[
                VGroup(token_box(t, GREEN_E, 22), zh(e, 22)).arrange(RIGHT, buff=0.4)
                for t, e in [("延续上文", "“把它的名字改一下” → 它 = 上一轮的传感器"),
                             ("话题切换", "新请求不再沿用上一轮的目标"),
                             ("指代消解", "“把音箱也打开” → 同一个房间的音箱"),
                             ("用户纠正", "“别调次卧了，开男孩房的风扇” → 次卧恢复原状")]
            ]).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(DOWN * 0.2)
            for it in items:
                self.play(FadeIn(it, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(1.3)
            self.items = items

        with self.voice("ctx_3"):
            self.play(FadeOut(self.items), FadeOut(self.c5))
            c6 = tc_chip(5, 26).to_corner(UL)
            st = VGroup(token_box("短期记忆", PINK, 28), zh("刚刚的对话", 22, GREY_B)).arrange(DOWN)
            lt = VGroup(token_box("长期记忆", PINK, 28), zh("用户的习惯", 22, GREY_B)).arrange(DOWN)
            VGroup(st, lt).arrange(RIGHT, buff=2)
            self.play(FadeIn(c6), FadeIn(st), FadeIn(lt))
            self.c6, self.m = c6, VGroup(st, lt)

        with self.voice("ctx_4"):
            self.play(FadeOut(self.m))
            say = bubble("“该睡觉了。”", 36).shift(LEFT * 4 + UP * 0.8)
            mem = VGroup(zh("记忆", 22, PINK), mono("湿度 → 50%", 20), mono("呼吸灯 → off", 20),
                         mono("模式 → 入睡", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            memf = VGroup(SurroundingRectangle(mem, color=PINK, buff=0.2, corner_radius=0.1), mem).shift(UP * 0.8)
            cube = device("空气魔方", False, TEAL_D, 26).shift(RIGHT * 4 + UP * 0.8)
            a1 = Arrow(say.get_right(), memf.get_left(), color=GREY_B)
            a2 = Arrow(memf.get_right(), cube.get_left(), color=GREY_B)
            self.play(FadeIn(say))
            self.play(GrowArrow(a1), FadeIn(memf))
            self.play(GrowArrow(a2), FadeIn(cube))
            self.play(set_lamp(cube, True))
            self.g = VGroup(say, memf, cube, a1, a2)

        with self.voice("ctx_5"):
            self.play(FadeOut(self.g), FadeOut(self.c6))
            c7 = tc_chip(6, 26).to_corner(UL)
            q = bubble("“现在有几台风扇灯是灯和风扇都开着的？”", 28).shift(UP * 1.2)
            lamps = VGroup(*[device(f"风扇灯{i + 1}", i == 1, size=20) for i in range(4)]).arrange(RIGHT, buff=0.4)
            lamps.shift(DOWN * 0.6)
            self.play(FadeIn(c7), FadeIn(q))
            self.play(FadeIn(lamps))
            ans = zh("只读，不改变任何设备", 24, GOLD).next_to(lamps, DOWN, buff=0.5)
            self.play(Write(ans))
            self.g = VGroup(c7, q, lamps, ans)

        with self.voice("ctx_6"):
            self.play(FadeOut(self.g))
            caps = ["状态落地", "目标选择", "澄清", "规则构建", "对话追踪", "记忆使用", "查询推理", "不碰无关设备"]
            chips = VGroup(*[token_box(c, BLUE_E if i < 7 else YELLOW, 26) for i, c in enumerate(caps)])
            chips.arrange_in_grid(2, 4, buff=(0.4, 0.6))
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in chips], lag_ratio=0.3), run_time=4)
            self.play(Indicate(chips[-1], color=YELLOW))
        self.clear()


# ====================================================================== 8 构建流水线
class S08_Pipeline(VoiceScene):
    def construct(self):
        title = section_title("环境优先的数据构建流水线")
        steps = VGroup(*[
            VGroup(Text(f"{i + 1}", font_size=40, color=c), zh(t, 24)).arrange(DOWN, buff=0.2)
            for i, (t, c) in enumerate([("构建家的实例", BLUE_C), ("生成任务与指令", GREEN_C),
                                        ("HomeEnv 校验", TEAL), ("人工审核", YELLOW)])
        ]).arrange(RIGHT, buff=1.3).shift(UP * 1.5)
        arrows = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.2, color=GREY_B)
                          for i in range(3)])
        with self.voice("pipe_1"):
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in steps], lag_ratio=0.4),
                      LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.4), run_time=3)

        detail = VGroup()

        def show(i, mob):
            nonlocal detail
            anims = [steps[j].animate.set_opacity(1 if j == i else 0.35) for j in range(4)]
            if len(detail):
                anims.append(FadeOut(detail))
            self.play(*anims, run_time=0.6)
            mob.next_to(steps, DOWN, buff=0.8).set_x(0)
            self.play(FadeIn(mob, shift=UP * 0.2))
            detail = mob

        with self.voice("pipe_2"):
            simple = VGroup(*[Square(0.9, color=BLUE_C) for _ in range(4)]).arrange(RIGHT, buff=0.2)
            sl = zh("简单 / 中等：各自独立生成", 22).next_to(simple, DOWN)
            big = Square(2.0, color=YELLOW)
            grid = VGroup(*[Square(0.4, stroke_width=1, color=GREY_B) for _ in range(20)]).arrange_in_grid(4, 5, buff=0.05)
            grid.move_to(big)
            bl = zh("复杂：共享一个密集大宅", 22).next_to(big, DOWN)
            show(0, VGroup(VGroup(simple, sl), VGroup(big, grid, bl)).arrange(RIGHT, buff=1.5))

        with self.voice("pipe_3"):
            spec = VGroup(zh("结构化规格", 22, GREEN_C), mono("target: 客厅灯\nstate: on, 70%\nrule: brightness<50", 18))
            spec.arrange(DOWN, buff=0.15)
            specf = VGroup(SurroundingRectangle(spec, color=GREEN_C, buff=0.2), spec)
            gpt = token_box("GPT-5", GREY_BROWN, 26)
            utt = bubble("“客厅有点暗，把暗的灯调到七成亮”", 22)
            row = VGroup(token_box("家的状态", BLUE_D, 22), gpt, specf, token_box("GPT-5", GREY_BROWN, 26), utt)
            row.arrange(RIGHT, buff=0.35).scale_to_fit_width(13)
            show(1, row)

        with self.voice("pipe_4"):
            items = VGroup(*[VGroup(Text("✔", font_size=26, color=OK), zh(t, 24)).arrange(RIGHT, buff=0.2)
                             for t in ["设备存在", "服务可用", "参数合法", "参考操作到达目标状态"]])
            items.arrange(RIGHT, buff=0.6)
            show(2, VGroup(zh("可执行任务", 26, TEAL), items).arrange(DOWN, buff=0.4))

        with self.voice("pipe_5"):
            items2 = VGroup(*[VGroup(Text("✔", font_size=26, color=OK), zh(t, 24)).arrange(RIGHT, buff=0.2)
                              for t in ["重算查询答案", "核对触发与动作", "确认确实需要澄清"]]).arrange(RIGHT, buff=0.6)
            grp = VGroup(zh("不可执行任务", 26, TEAL), items2).arrange(DOWN, buff=0.4)
            grp.next_to(detail, DOWN, buff=0.5).set_x(0)
            self.play(FadeIn(grp, shift=UP * 0.2))
            fix = zh("不一致 → 修改或删除", 24, BAD).next_to(grp, DOWN, buff=0.35)
            self.play(Write(fix))
            detail = VGroup(detail, grp, fix)

        with self.voice("pipe_6"):
            items3 = VGroup(*[token_box(t, YELLOW_E, 24) for t in ["指令是否自然", "类别是否对齐", "上下文 / 记忆冲突"]])
            items3.arrange(RIGHT, buff=0.5)
            note = zh("捕捉模拟器发现不了的语义、语用错误", 24, GREY_B)
            show(3, VGroup(items3, note).arrange(DOWN, buff=0.4))
        self.clear()


# ====================================================================== 9 数据统计
class S09_Stats(VoiceScene):
    def construct(self):
        title = section_title("数据分布")
        axis = Line(LEFT * 6 + DOWN * 2.3, RIGHT * 6 + DOWN * 2.3, color=GREY_B)
        xs = np.linspace(-5.1, 5.1, 7)
        scale = 3.6 / 250
        bars, vals, labels = VGroup(), VGroup(), VGroup()
        for x, (code, name, col), n in zip(xs, TC, TC_COUNT):
            b = Rectangle(width=1.1, height=n * scale, fill_color=col, fill_opacity=0.85, stroke_width=0)
            b.move_to([x, -2.3 + n * scale / 2, 0])
            bars.add(b)
            vals.add(Text(str(n), font_size=26).next_to(b, UP, buff=0.1))
            labels.add(VGroup(Text(code, font_size=20, color=col), zh(name, 20)).arrange(DOWN, buff=0.08)
                       .next_to(axis, DOWN, buff=0.15).set_x(x))
        order1 = [1, 4]
        order2 = [0, 2, 3, 6, 5]

        with self.voice("stat_1"):
            self.play(Write(title), Create(axis), FadeIn(labels))
            self.play(*[GrowFromEdge(bars[i], DOWN) for i in order1], run_time=1.5)
            self.play(*[FadeIn(vals[i]) for i in order1])

        with self.voice("stat_2"):
            self.play(LaggedStart(*[GrowFromEdge(bars[i], DOWN) for i in order2], lag_ratio=0.2), run_time=2.5)
            self.play(*[FadeIn(vals[i]) for i in order2])
            total = zh("合计 1,100", 28, YELLOW).to_corner(UR, buff=0.6)
            self.play(Write(total))

        with self.voice("stat_3"):
            self.clear(run_time=0.6)
            title2 = section_title("按家的复杂度分层")
            parts = [(550, "简单", BLUE_C), (330, "中等", TEAL), (220, "复杂", YELLOW)]
            w = 11.0 / 1100
            segs = VGroup()
            for n, name, col in parts:
                r = Rectangle(width=n * w, height=0.9, fill_color=col, fill_opacity=0.8, stroke_width=0)
                segs.add(r)
            segs.arrange(RIGHT, buff=0).shift(UP * 1.2)
            seg_l = VGroup(*[VGroup(zh(name, 24, BLACK), Text(str(n), font_size=24, color=BLACK)).arrange(RIGHT, buff=0.2)
                             .move_to(s) for s, (n, name, _) in zip(segs, parts)])
            self.play(Write(title2))
            self.play(LaggedStart(*[GrowFromEdge(s, LEFT) for s in segs], lag_ratio=0.5), run_time=2)
            self.play(FadeIn(seg_l))
            self.segs = VGroup(segs, seg_l)

        with self.voice("stat_4"):
            h1 = self._home(2, 3, "简单", "平均 5.5 个房间 · 5.5 台设备", 1, BLUE_C)
            h2 = self._home(3, 4, "中等", "平均 10.5 个房间 · 35 台设备", 3, TEAL)
            VGroup(h1, h2).arrange(RIGHT, buff=0.8, aligned_edge=DOWN).shift(DOWN * 1.3 + LEFT * 2.8)
            self.play(FadeIn(h1[0]), FadeIn(h1[1]), FadeIn(h1[2]))
            self.play(FadeIn(h2[0]), FadeIn(h2[1]), FadeIn(h2[2]))
            self.h = VGroup(h1, h2)

        with self.voice("stat_5"):
            h3 = self._home(6, 5, "复杂", "31 个嵌套房间 · 135 台设备 · 17 种类型", 5, YELLOW, cell=0.38)
            h3.next_to(self.h, RIGHT, buff=0.7, aligned_edge=DOWN)
            self.play(FadeIn(h3[0]), LaggedStart(*[FadeIn(d, scale=0.3) for d in h3[1]], lag_ratio=0.01),
                      FadeIn(h3[2]), run_time=2.5)
        self.clear()

    def _home(self, cols, rows, name, desc, per, color, cell=0.5):
        grid = VGroup(*[Square(cell, stroke_color=GREY_B, stroke_width=1.2) for _ in range(cols * rows)])
        grid.arrange_in_grid(rows, cols, buff=0)
        rng = np.random.default_rng(cols * 7 + rows)
        dots = VGroup()
        for sq in grid:
            for _ in range(per if rng.random() < 0.85 else per - 1):
                off = (rng.random(2) - 0.5) * cell * 0.7
                dots.add(Dot(sq.get_center() + np.array([off[0], off[1], 0]), radius=0.035,
                             color=ON if rng.random() < 0.4 else TEAL))
        lab = VGroup(zh(name, 26, color), zh(desc, 18, GREY_B)).arrange(DOWN, buff=0.1).next_to(grid, DOWN, buff=0.25)
        return VGroup(grid, dots, lab)


# ====================================================================== 10 评测协议
class S10_Protocol(VoiceScene):
    def construct(self):
        with self.voice("prot_1"):
            title = section_title("混合评测协议")
            rule = VGroup(token_box("规则校验", TEAL_D, 30), zh("能在环境里验证的", 22, GREY_B)).arrange(DOWN)
            judge = VGroup(token_box("大模型裁判", PURPLE_E, 30), zh("需要语义判断的", 22, GREY_B)).arrange(DOWN)
            VGroup(rule, judge).arrange(RIGHT, buff=2.5)
            self.play(Write(title))
            self.play(FadeIn(rule, shift=UP * 0.2))
            self.play(FadeIn(judge, shift=UP * 0.2))
            self.g = VGroup(rule, judge)
            self.title = title

        with self.voice("prot_2"):
            self.play(FadeOut(self.g))
            names = ["客厅灯", "空调", "窗帘", "电视", "音箱"]
            goal = [1, 0, 0, 0, 1]
            before = [0, 0, 0, 0, 0]
            after_ok = [1, 0, 0, 0, 1]
            after_bad = [1, 0, 1, 0, 1]
            col = lambda v: ON if v else OFF  # noqa: E731

            def row(vals, label, color=WHITE):
                cells = VGroup(*[VGroup(Square(0.7, stroke_color=GREY_B, fill_color=col(v), fill_opacity=0.8))
                                 for v in vals]).arrange(RIGHT, buff=0.15)
                return VGroup(zh(label, 22, color).next_to(cells, LEFT, buff=0.4), cells)

            hdr = VGroup(*[zh(n, 18, GREY_B) for n in names])
            r0 = row(before, "执行前")
            r1 = row(goal, "目标", YELLOW)
            r2 = row(after_ok, "模型 A")
            r3 = row(after_bad, "模型 B")
            tbl = VGroup(r0, r1, r2, r3).arrange(DOWN, buff=0.3, aligned_edge=RIGHT).shift(DOWN * 0.3)
            for h, sq in zip(hdr, r0[1]):
                h.next_to(sq, UP, buff=0.15)
            self.play(FadeIn(hdr), FadeIn(r0), FadeIn(r1))
            self.play(FadeIn(r2))
            self.play(FadeIn(Text("✔", font_size=34, color=OK).next_to(r2, RIGHT, buff=0.4)))
            self.play(FadeIn(r3))
            bad = SurroundingRectangle(r3[1][2], color=BAD, buff=0.05)
            self.play(Create(bad), FadeIn(Text("✘", font_size=34, color=BAD).next_to(r3, RIGHT, buff=0.4)))
            note = zh("多开一盏灯，也算失败", 24, BAD).next_to(tbl, DOWN, buff=0.4)
            self.play(Write(note))

        with self.voice("prot_3"):
            self.clear(run_time=0.6)
            t = VGroup(tc_chip(3, 24), zh("双重校验", 30, YELLOW)).arrange(RIGHT, buff=0.4).to_edge(UP, buff=0.5)
            trig = VGroup(zh("① 触发校验", 28, ORANGE),
                          VGroup(zh("定时：", 22), mono("cron 时间一致", 20)).arrange(RIGHT),
                          VGroup(zh("状态：", 22), zh("在与标准答案相同的设备状态下触发", 22)).arrange(RIGHT)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            act = VGroup(zh("② 动作校验", 28, ORANGE), zh("执行后状态逐项比对", 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            VGroup(trig, act).arrange(DOWN, aligned_edge=LEFT, buff=0.6).shift(DOWN * 0.3)
            self.play(FadeIn(t))
            self.play(FadeIn(trig, shift=RIGHT * 0.2), run_time=1.2)
            self.play(FadeIn(act, shift=RIGHT * 0.2))

        with self.voice("prot_4"):
            self.clear(run_time=0.6)
            judge = token_box("GPT-5 裁判", PURPLE_E, 32).shift(UP * 0.3)
            ins = VGroup(VGroup(tc_chip(2, 22), zh("澄清是否恰当", 20, GREY_B)).arrange(DOWN),
                         VGroup(tc_chip(6, 22), zh("回答是否正确", 20, GREY_B)).arrange(DOWN)).arrange(RIGHT, buff=3)
            ins.shift(UP * 0.3)
            self.play(FadeIn(judge))
            self.play(FadeIn(ins))
            self.j = VGroup(judge, ins)

        with self.voice("prot_5"):
            self.play(self.j.animate.shift(UP * 1.5))
            vt = ValueTracker(0)
            num = always_redraw(lambda: Text(f"{vt.get_value():.0f}%", font_size=96, color=YELLOW).shift(DOWN * 1))
            cap = zh("与人类专家一致（200 条盲审）", 26).shift(DOWN * 2.4)
            self.add(num)
            self.play(vt.animate.set_value(98), FadeIn(cap), run_time=2.5)
            num.clear_updaters()
        self.clear()


# ====================================================================== 11 两种设置
class S11_Settings(VoiceScene):
    def construct(self):
        with self.voice("set_1"):
            n = VGroup(Text("13", font_size=100, color=YELLOW), zh("个大语言模型", 38)).arrange(RIGHT, buff=0.3)
            s = zh("同一个初始状态 · 同一个评分器 · 不同的接口", 28, GREY_B).next_to(n, DOWN, buff=0.5)
            self.play(Write(n))
            self.play(FadeIn(s))
            self.g = VGroup(n, s)

        dr = zh("直接推理  DR", 34, DR_COLOR).move_to(LEFT * 3.5 + UP * 3)
        eia = zh("环境交互智能体  EIA", 34, EIA_COLOR).move_to(RIGHT * 3.4 + UP * 3)
        div = DashedLine(UP * 3.4, DOWN * 3.6, color=GREY_D)

        with self.voice("set_2"):
            self.play(FadeOut(self.g))
            self.play(Write(dr), Write(eia), Create(div))
            ctx = VGroup(zh("完整上下文", 22, DR_COLOR),
                         mono("rooms, devices, values\nservices, ranges, enums", 16, GREY_A)).arrange(DOWN, buff=0.12)
            ctxf = VGroup(SurroundingRectangle(ctx, color=DR_COLOR, buff=0.15), ctx).move_to(LEFT * 5.0 + UP * 1.5)
            llm = token_box("LLM", YELLOW, 30).move_to(LEFT * 2.2 + UP * 1.5)
            js = mono('{mode, response, actions}', 18, BLUE_B).move_to(LEFT * 2.2 + UP * 0.4)
            self.play(FadeIn(ctxf))
            self.play(GrowArrow(Arrow(ctxf.get_right(), llm.get_left(), buff=0.1, color=GREY_B)), FadeIn(llm))
            self.play(GrowArrow(Arrow(llm.get_bottom(), js.get_top(), buff=0.1, color=GREY_B)), FadeIn(js))
            self.js = js

        with self.voice("set_3"):
            no = zh("✘ 不能查询  ✘ 无执行反馈", 22, BAD).move_to(LEFT * 3.5 + DOWN * 0.6)
            replay = VGroup(zh("在全新的 HomeEnv 副本中重放", 22), Text("→  最终状态", font_size=22, color=GREY_A))
            replay.arrange(DOWN, buff=0.15).move_to(LEFT * 3.5 + DOWN * 1.6)
            self.play(FadeIn(no))
            self.play(FadeIn(replay, shift=UP * 0.2))

        with self.voice("set_4"):
            center = RIGHT * 3.4 + UP * 0.6
            names, cols = ["思考", "行动", "观察"], [YELLOW, EIA_COLOR, TEAL]
            angs = [PI / 2, PI / 2 - 2 * PI / 3, PI / 2 + 2 * PI / 3]
            nodes = VGroup(*[token_box(n, c, 22).move_to(center + 1.2 * np.array([np.cos(a), np.sin(a), 0]))
                             for n, c, a in zip(names, cols, angs)])
            ring = Circle(radius=1.2, color=GREY_B, stroke_width=2).move_to(center)
            react = Text("ReAct", font_size=24, color=GREY_A).move_to(center)
            self.play(Create(ring), LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.3), FadeIn(react))
            orbit = Circle(radius=1.2).move_to(center).rotate(PI / 2).flip(UP)
            runner = Dot(color=YELLOW, radius=0.09).move_to(orbit.point_from_proportion(0))
            self.play(MoveAlongPath(runner, orbit), run_time=2, rate_func=linear)
            self.play(FadeOut(runner))
            self.loop = VGroup(ring, nodes, react)

        with self.voice("set_5"):
            self.play(self.loop.animate.scale(0.6).move_to(RIGHT * 5.6 + UP * 1.9))
            fog = VGroup(*[Square(0.55, stroke_width=1, stroke_color=GREY_D, fill_color=GREY_E, fill_opacity=0.95)
                           for _ in range(15)]).arrange_in_grid(3, 5, buff=0.04).move_to(RIGHT * 2.6 + UP * 1.0)
            vis = zh("初始只见：房间列表 + 设备索引", 20, EIA_COLOR).next_to(fog, DOWN, buff=0.2)
            self.play(FadeIn(fog), FadeIn(vis))
            q = mono("query_device(what, did, room, tags)", 18, BLUE_B)
            c = mono("control_device(did, locator, arguments)", 18, EIA_COLOR)
            VGroup(q, c).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(vis, DOWN, buff=0.35).set_x(3.4)
            self.play(FadeIn(q))
            for i in [6, 7, 2, 12]:
                self.play(fog[i].animate.set_fill(opacity=0).set_stroke(TEAL, 2), run_time=0.35)
            self.play(FadeIn(c))
            diff = zh("前后快照之差 = 预测", 22, GREY_A).next_to(c, DOWN, buff=0.3)
            self.play(FadeIn(diff))

        with self.voice("set_6"):
            a = zh("一眼看全局，一次写对", 28, DR_COLOR).move_to(LEFT * 3.5 + DOWN * 3)
            b = zh("边查边做，知道何时停", 28, EIA_COLOR).move_to(RIGHT * 3.4 + DOWN * 3.2)
            self.play(Write(a))
            self.play(Write(b))
            self.play(Indicate(b, color=YELLOW))
        self.clear()


# ====================================================================== 12 总成绩
class S12_Overall(VoiceScene):
    def construct(self):
        models = sorted(TABLE2, key=lambda m: TABLE2[m][1][7])
        n = len(models)
        ys = np.linspace(2.6, -3.1, n)[::-1]  # 低分在下
        x0, scale = -2.6, 7.6 / 100
        with self.voice("all_1"):
            title = zh("EIA 平均成功率（%）", 30, YELLOW).to_corner(UL, buff=0.4)
            legend = VGroup(VGroup(Square(0.22, fill_color=BLUE_C, fill_opacity=0.9, stroke_width=0), zh("开源", 18)).arrange(RIGHT, buff=0.1),
                            VGroup(Square(0.22, fill_color=GREY_B, fill_opacity=0.9, stroke_width=0), zh("闭源", 18)).arrange(RIGHT, buff=0.1)
                            ).arrange(RIGHT, buff=0.4).to_corner(UR, buff=0.45)
            self.play(Write(title), FadeIn(legend))
            bars, names, vals = VGroup(), VGroup(), VGroup()
            for m, y in zip(models, ys):
                v = TABLE2[m][1][7]
                col = BLUE_C if m in OPEN_SOURCE else GREY_B
                b = Rectangle(width=v * scale, height=0.3, fill_color=col, fill_opacity=0.85, stroke_width=0)
                b.move_to([x0 + v * scale / 2, y, 0])
                bars.add(b)
                names.add(Text(m, font_size=19).next_to([x0, y, 0], LEFT, buff=0.2))
                vals.add(Text(f"{v:.1f}", font_size=19).next_to(b, RIGHT, buff=0.12))
            self.play(FadeIn(names), LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.08), run_time=3)
            self.play(FadeIn(vals))
            self.bars, self.names, self.vals, self.models = bars, names, vals, models

        def hl(model, color=YELLOW):
            i = self.models.index(model)
            return SurroundingRectangle(VGroup(self.names[i], self.vals[i]), color=color, buff=0.06)

        with self.voice("all_2"):
            h1 = hl("Gemini-3.1-Pro")
            t1 = zh("DR 83.5", 20, DR_COLOR).next_to(h1, RIGHT, buff=0.2)
            self.play(Create(h1), FadeIn(t1))
            h2 = hl("Claude-Sonnet-4.6")
            self.play(Create(h2))
            self.hl = VGroup(h1, t1, h2)

        with self.voice("all_3"):
            h3 = hl("DeepSeek-V3.2", BLUE_C)
            t3 = zh("开源最佳 · DR 69.5", 20, BLUE_C).next_to(h3, RIGHT, buff=0.2)
            self.play(Create(h3), FadeIn(t3))
            self.hl.add(h3, t3)

        with self.voice("all_4"):
            h4 = hl("Qwen3.5-4B", BLUE_C)
            h5 = hl("MiniMax-M2.7", BAD)
            self.play(Create(h4))
            self.play(Create(h5))
            top = self.bars[-1].get_right()
            low = self.bars[0].get_right()
            gap = DoubleArrow([low[0], ys[0] - 0.35, 0], [top[0], ys[0] - 0.35, 0], buff=0, color=BAD,
                              tip_length=0.15, stroke_width=3)
            gl = zh("33.1 个百分点", 20, BAD).next_to(gap, DOWN, buff=0.08)
            self.play(GrowFromCenter(gap), FadeIn(gl))

        with self.voice("all_5"):
            q = zh("平均数会掩盖什么？", 36, YELLOW)
            bg = BackgroundRectangle(q, fill_opacity=0.9, buff=0.3)
            self.play(FadeIn(bg), Write(q))
        self.clear()


# ====================================================================== 13 能力热力图
class S13_Capability(VoiceScene):
    def construct(self):
        models = sorted(TABLE2, key=lambda m: TABLE2[m][1][7])
        cw, ch = 1.05, 0.39
        x0, y0 = -3.3, 2.4
        cells = VGroup()
        texts = VGroup()
        for r, m in enumerate(models):
            for c in range(7):
                v = TABLE2[m][1][c]
                sq = Rectangle(width=cw, height=ch, fill_color=heat(v), fill_opacity=1, stroke_color=BLACK,
                               stroke_width=1).move_to([x0 + c * cw, y0 - r * ch, 0])
                cells.add(sq)
                texts.add(Text(f"{v:.1f}", font_size=15, color=BLACK if v > 70 else WHITE).move_to(sq))
        rowl = VGroup(*[Text(m, font_size=17).next_to([x0 - cw / 2, y0 - r * ch, 0], LEFT, buff=0.15)
                        for r, m in enumerate(models)])
        coll = VGroup(*[VGroup(Text(TC[c][0], font_size=18, color=TC[c][2]), zh(TC[c][1], 15))
                        .arrange(DOWN, buff=0.04).move_to([x0 + c * cw, y0 + 0.55, 0]) for c in range(7)])
        grid = lambda c: VGroup(*[cells[r * 7 + c] for r in range(len(models))])  # noqa: E731
        idx = lambda m, c: models.index(m) * 7 + c  # noqa: E731

        with self.voice("cap_1"):
            self.play(FadeIn(rowl), FadeIn(coll))
            self.play(LaggedStart(*[FadeIn(s) for s in cells], lag_ratio=0.005), run_time=2.5)
            self.play(FadeIn(texts))
            tag = zh("EIA 设置 · 表 2", 20, GREY_B).to_corner(DR, buff=0.3)
            self.play(FadeIn(tag))

        with self.voice("cap_2"):
            b1 = SurroundingRectangle(grid(0), color=WHITE, buff=0.03)
            b7 = SurroundingRectangle(grid(6), color=WHITE, buff=0.03)
            self.play(Create(b1), Create(b7))
            marks = VGroup(*[SurroundingRectangle(cells[idx(m, c)], color=RED_B, buff=0.02, stroke_width=4)
                             for m in ["Gemini-3.1-Pro", "Qwen3.5-4B"] for c in (0, 6)])
            self.play(Create(marks))
            self.b = VGroup(b1, b7, marks)

        with self.voice("cap_3"):
            self.play(FadeOut(self.b))
            a = cells[idx("DeepSeek-V3.2", 0)]
            b = cells[idx("DeepSeek-V3.2", 1)]
            ra, rb = [SurroundingRectangle(x, color=RED_B, buff=0.02, stroke_width=4) for x in (a, b)]
            arr = CurvedArrow(a.get_top() + UP * 0.05, b.get_top() + UP * 0.05, angle=-PI / 2, color=RED_B)
            lab = zh("87.3 → 52.8", 22, RED_B).to_edge(RIGHT, buff=0.5).shift(UP * 1)
            self.play(Create(ra), Create(rb), Create(arr), FadeIn(lab))
            self.d = VGroup(ra, rb, arr, lab)

        with self.voice("cap_4"):
            self.play(FadeOut(self.d))
            b4 = SurroundingRectangle(grid(3), color=RED_B, buff=0.03, stroke_width=5)
            self.play(Create(b4))
            bn = zh("共同瓶颈", 26, RED_B).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
            self.play(Write(bn))
            notes = VGroup(Text("Gemini-3.1-Pro", font_size=18), Text("EIA 64.0 / DR 70.7", font_size=18),
                           Text("Qwen3.5-4B", font_size=18), Text("EIA 21.3", font_size=18))
            notes.arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(bn, DOWN, buff=0.3).to_edge(RIGHT, buff=0.4)
            self.play(FadeIn(notes))
            self.e = VGroup(b4, bn, notes)

        with self.voice("cap_5"):
            self.play(FadeOut(self.e))
            low = VGroup(grid(0), grid(6))
            high = VGroup(grid(1), grid(2), grid(3), grid(5))
            lt = zh("底层设备操作", 22, BLUE_C).to_edge(RIGHT, buff=0.4).shift(UP * 1)
            ht = zh("空间 · 时间\n组合推理", 22, YELLOW).next_to(lt, DOWN, buff=0.4).to_edge(RIGHT, buff=0.5)
            self.play(Indicate(low, color=BLUE_C, scale_factor=1.0), FadeIn(lt))
            self.play(Indicate(high, color=YELLOW, scale_factor=1.0), FadeIn(ht))
        self.clear()


# ====================================================================== 14 DR vs EIA
class S14_Modes(VoiceScene):
    def construct(self):
        # 论文表 2 的 ∆Avg.(EIA–DR) 列
        delta = {"Qwen3.5-4B": 10.6, "Qwen3.5-9B": 15.1, "Qwen3.5-397B": 0.2, "DeepSeek-V3.2": 6.0,
                 "MiniMax-M2.7": 0.3, "GLM-5": 10.9, "Qwen3.5-Plus": 7.4, "GPT-5.4-Mini": 6.7, "GPT-5.4": -1.3,
                 "Gemini-3.1-Flash": 1.4, "Gemini-3.1-Pro": 1.7, "Claude-Haiku-4.5": -0.4, "Claude-Sonnet-4.6": 7.4}
        models = sorted(delta, key=delta.get)
        n = len(models)
        ys = np.linspace(-3.0, 2.5, n)
        zero = -0.5
        sc = 0.28
        with self.voice("mode_1"):
            title = zh("∆ 平均成功率 = EIA − DR（百分点）", 28, YELLOW).to_corner(UL, buff=0.4)
            axis = Line([zero, -3.3, 0], [zero, 2.8, 0], color=GREY_B)
            self.play(Write(title), Create(axis))
            bars, names, vals = VGroup(), VGroup(), VGroup()
            for m, y in zip(models, ys):
                d = delta[m]
                col = EIA_COLOR if d >= 0 else DR_COLOR
                w = max(abs(d) * sc, 0.02)
                b = Rectangle(width=w, height=0.3, fill_color=col, fill_opacity=0.9, stroke_width=0)
                b.move_to([zero + np.sign(d) * w / 2 if d else zero, y, 0])
                bars.add(b)
                names.add(Text(m, font_size=18).next_to([zero - 0.1 if d >= 0 else zero - w - 0.1, y, 0], LEFT, buff=0.1))
                vals.add(Text(f"{d:+.1f}", font_size=18, color=col).next_to(b, RIGHT if d >= 0 else LEFT, buff=0.1))
                if d < 0:
                    vals[-1].next_to(b, LEFT, buff=0.1)
                    names[-1].next_to(vals[-1], LEFT, buff=0.2)
            self.play(FadeIn(names), LaggedStart(*[GrowFromEdge(b, LEFT if delta[m] >= 0 else RIGHT)
                                                   for b, m in zip(bars, models)], lag_ratio=0.08), run_time=3)
            self.play(FadeIn(vals))
            lg = VGroup(zh("EIA 更好", 20, EIA_COLOR), zh("DR 更好", 20, DR_COLOR)).arrange(DOWN, aligned_edge=LEFT)
            lg.to_corner(DR, buff=0.4)
            self.play(FadeIn(lg))
            self.models, self.names, self.vals = models, names, vals
            self.chart = VGroup(title, axis, bars, names, vals, lg)

        def hl(m, color=YELLOW):
            i = self.models.index(m)
            return SurroundingRectangle(VGroup(self.names[i], self.vals[i]), color=color, buff=0.05)

        with self.voice("mode_2"):
            h = VGroup(hl("Qwen3.5-9B"), hl("GLM-5"))
            self.play(Create(h))
            self.h = h

        with self.voice("mode_3"):
            self.play(FadeOut(self.chart), FadeOut(self.h))
            self._pair("Claude-Sonnet-4.6 · TC3 模糊意图", 61.3, 91.3)

        with self.voice("mode_4"):
            self.clear(run_time=0.5)
            self._pair("GPT-5.4 · TC4 自动化调度", 65.3, 49.3)
            note = zh("整体：DR 比 EIA 高 1.3 个百分点", 24, DR_COLOR).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(note))

        with self.voice("mode_5"):
            self.clear(run_time=0.5)
            steps = VGroup(*[Circle(0.35, color=EIA_COLOR, fill_opacity=0.2) for _ in range(5)]).arrange(RIGHT, buff=0.8)
            steps.shift(UP * 0.8)
            arrs = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.05, color=GREY_B)
                            for i in range(4)])
            self.play(FadeIn(steps[0]))
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(s)) for a, s in zip(arrs, steps[1:])],
                                  lag_ratio=0.5), run_time=2)
            self.play(steps[1].animate.set_color(BAD))
            self.play(*[s.animate.set_color(BAD) for s in steps[2:]], run_time=1.2)
            l1 = zh("EIA：一步错，步步错", 26, EIA_COLOR).next_to(steps, DOWN, buff=0.4)
            one = Circle(0.5, color=DR_COLOR, fill_opacity=0.25).shift(DOWN * 2)
            l2 = zh("DR：单次全局推理", 26, DR_COLOR).next_to(one, RIGHT, buff=0.4)
            self.play(FadeIn(l1))
            self.play(FadeIn(one), FadeIn(l2))
        self.clear()

    def _pair(self, title, dr, eia):
        t = zh(title, 30, YELLOW).to_edge(UP, buff=0.8)
        base = -2.2
        sc = 4.2 / 100
        bars = VGroup()
        for i, (v, name, col) in enumerate([(dr, "DR", DR_COLOR), (eia, "EIA", EIA_COLOR)]):
            b = Rectangle(width=1.6, height=v * sc, fill_color=col, fill_opacity=0.85, stroke_width=0)
            b.move_to([(-1.5 if i == 0 else 1.5), base + v * sc / 2, 0])
            lab = zh(name, 26, col).next_to(b, DOWN, buff=0.2)
            val = Text(f"{v:.1f}%", font_size=32).next_to(b, UP, buff=0.15)
            bars.add(VGroup(b, lab, val))
        self.play(Write(t))
        self.play(GrowFromEdge(bars[0][0], DOWN), FadeIn(bars[0][1]), FadeIn(bars[0][2]))
        self.play(GrowFromEdge(bars[1][0], DOWN), FadeIn(bars[1][1]), FadeIn(bars[1][2]))
        d = eia - dr
        arr = Arrow(bars[0][2].get_right(), bars[1][2].get_left(), buff=0.2, color=OK if d > 0 else BAD)
        dl = Text(f"{d:+.1f}", font_size=28, color=OK if d > 0 else BAD).next_to(arr, UP, buff=0.1)
        self.play(GrowArrow(arr), FadeIn(dl))


# ====================================================================== 15 复杂度 / 思考
class S15_Complexity(VoiceScene):
    def construct(self):
        with self.voice("cx_1"):
            title = zh("DR 设置：成功率 vs 家的复杂度（图 4 正文数值）", 26, YELLOW).to_corner(UL, buff=0.4)
            ax = Axes(x_range=[0, 3, 1], y_range=[40, 100, 20], x_length=7, y_length=4.5,
                      axis_config={"color": GREY_B, "include_ticks": False}).shift(DOWN * 0.3 + LEFT * 1)
            ylab = VGroup(*[Text(str(v), font_size=18, color=GREY_B).next_to(ax.c2p(0, v), LEFT, buff=0.15)
                            for v in (40, 60, 80, 100)])
            xl = VGroup(zh("简单", 22).next_to(ax.c2p(0.5, 40), DOWN, buff=0.25),
                        zh("复杂", 22).next_to(ax.c2p(2.5, 40), DOWN, buff=0.25))
            self.play(Write(title), Create(ax), FadeIn(ylab), FadeIn(xl))
            self.ax = ax

        with self.voice("cx_2"):
            for name, a, b, col in [("Gemini-3.1-Pro", 95.3, 83.8, BLUE_C), ("Qwen3.5-9B", 73.3, 46.7, BAD)]:
                p1, p2 = self.ax.c2p(0.5, a), self.ax.c2p(2.5, b)
                ln = Line(p1, p2, color=col, stroke_width=5)
                d1, d2 = Dot(p1, color=col), Dot(p2, color=col)
                v1 = Text(f"{a}", font_size=20, color=col).next_to(d1, UP, buff=0.1)
                v2 = Text(f"{b}", font_size=20, color=col).next_to(d2, UP, buff=0.1)
                lab = Text(name, font_size=20, color=col).next_to(d2, RIGHT, buff=0.2)
                self.play(FadeIn(d1), FadeIn(v1))
                self.play(Create(ln), FadeIn(d2), FadeIn(v2), FadeIn(lab), run_time=1.5)
            note = zh("EIA 设置下趋势相同", 22, GREY_B).to_corner(DR, buff=0.5)
            self.play(FadeIn(note))

        with self.voice("cx_3"):
            self.clear(run_time=0.6)
            qs = VGroup(zh("该查什么？", 36, BLUE_C), zh("该忽略什么？", 36, PURPLE_B), zh("什么时候该停？", 36, YELLOW))
            qs.arrange(DOWN, buff=0.5).shift(RIGHT * 2)
            tool = VGroup(token_box("工具", TEAL_D, 30), zh("能查到状态、找到设备", 22, GREY_B)).arrange(DOWN)
            tool.shift(LEFT * 4)
            self.play(FadeIn(tool))
            self.play(LaggedStart(*[FadeIn(q, shift=LEFT * 0.3) for q in qs], lag_ratio=0.5), run_time=3)

        with self.voice("cx_4"):
            self.clear(run_time=0.6)
            t = zh("DeepSeek-V3.2 关闭思考后的总分下降", 30, YELLOW).to_edge(UP, buff=0.8)
            self.play(Write(t))
            sc = 0.2
            bars = VGroup()
            for i, (name, v, col) in enumerate([("EIA", 7.3, EIA_COLOR), ("DR", 18.3, DR_COLOR)]):
                b = Rectangle(width=v * sc, height=0.7, fill_color=col, fill_opacity=0.85, stroke_width=0)
                b.move_to([-2 + v * sc / 2, 0.5 - i * 1.3, 0])
                lab = zh(name, 26, col).next_to([-2, b.get_y(), 0], LEFT, buff=0.3)
                val = Text(f"−{v}", font_size=30).next_to(b, RIGHT, buff=0.2)
                bars.add(VGroup(b, lab, val))
            for b in bars:
                self.play(GrowFromEdge(b[0], LEFT), FadeIn(b[1]), FadeIn(b[2]))

        with self.voice("cx_5"):
            l = VGroup(zh("可观察的状态 · 明确的动作", 24, EIA_COLOR), zh("工具可以弥补推理", 22)).arrange(DOWN, buff=0.2)
            r = VGroup(zh("潜在偏好 · 多步协调 · 决定查什么", 24, DR_COLOR), zh("思考不可替代", 22)).arrange(DOWN, buff=0.2)
            VGroup(l, r).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(l, shift=UP * 0.2))
            self.play(FadeIn(r, shift=UP * 0.2))

        with self.voice("cx_6"):
            self.clear(run_time=0.6)
            t = zh("22 个子类上的分工", 32, YELLOW).to_edge(UP, buff=0.7)
            drc = VGroup(zh("DR 更强", 30, DR_COLOR),
                         *[zh(s, 24) for s in ["原子控制", "组合控制", "记忆", "多轮交互"]],
                         zh("证据已在提示中", 20, GREY_B)).arrange(DOWN, buff=0.25)
            eic = VGroup(zh("EIA 更合适", 30, EIA_COLOR),
                         *[zh(s, 24) for s in ["模糊意图", "设备查询"]],
                         zh("需要补齐信息、检查状态", 20, GREY_B)).arrange(DOWN, buff=0.25)
            VGroup(drc, eic).arrange(RIGHT, buff=2.5, aligned_edge=UP).shift(DOWN * 0.3)
            self.play(Write(t))
            self.play(FadeIn(drc, shift=RIGHT * 0.2), run_time=1.2)
            self.play(FadeIn(eic, shift=LEFT * 0.2), run_time=1.2)
        self.clear()


# ====================================================================== 16 错误分析
ERR = {
    "SO": ("结构化输出", BLUE_C), "MS": ("模式选择", PURPLE_B), "AJ": ("自动化判断", ORANGE),
    "AV/TV": ("动作 / 工具不合法", RED_C), "IE": ("交互效率", YELLOW), "FRF": ("格式 / 运行失败", GREY_B),
}


def pie(data: list[tuple[str, float]], radius: float = 1.7) -> VGroup:
    g = VGroup()
    start = PI / 2
    total = sum(v for _, v in data)
    for key, v in data:
        ang = -TAU * v / total
        col = ERR[key][1]
        s = AnnularSector(inner_radius=radius * 0.45, outer_radius=radius, angle=ang, start_angle=start,
                          fill_color=col, fill_opacity=0.9, stroke_color=BLACK, stroke_width=2)
        mid = start + ang / 2
        lab = VGroup(Text(key.split("/")[0] if key == "AV/TV" else key, font_size=20, color=BLACK if col in (YELLOW,) else WHITE),
                     Text(f"{v}%", font_size=16, color=BLACK if col in (YELLOW,) else WHITE)).arrange(DOWN, buff=0.03)
        lab.move_to(radius * 0.73 * np.array([np.cos(mid), np.sin(mid), 0]))
        if v < 7:
            lab.move_to(radius * 1.22 * np.array([np.cos(mid), np.sin(mid), 0])).set_color(col)
        g.add(VGroup(s, lab))
        start += ang
    return g


class S16_Errors(VoiceScene):
    def construct(self):
        with self.voice("err_1"):
            t = zh("六类错误", 44, YELLOW)
            self.play(Write(t))
            self.t = t

        with self.voice("err_2"):
            self.play(self.t.animate.scale(0.7).to_edge(UP, buff=0.4))
            rows = VGroup(*[
                VGroup(token_box(k, ERR[k][1], 22), zh(d, 22)).arrange(RIGHT, buff=0.35)
                for k, d in [("SO", "结构化输出：缺字段 / 格式不对"),
                             ("MS", "模式选择：执行与澄清选错"),
                             ("AJ", "自动化判断：条件校验失败"),
                             ("AV/TV", "动作 / 工具调用不合法"),
                             ("IE", "交互效率：工具调用过多"),
                             ("FRF", "JSON 无法解析，运行失败")]
            ]).arrange(DOWN, aligned_edge=LEFT, buff=0.25).shift(DOWN * 0.3)
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
                self.wait(0.9)
            self.rows = rows

        eia = pie([("SO", 51.0), ("IE", 29.0), ("AV/TV", 14.7), ("AJ", 5.4)]).shift(LEFT * 3.4 + DOWN * 0.4)
        dr = pie([("SO", 39.3), ("MS", 28.2), ("AV/TV", 24.6), ("FRF", 6.1), ("AJ", 1.8)]).shift(RIGHT * 3.4 + DOWN * 0.4)
        el = zh("EIA", 30, EIA_COLOR).next_to(eia, UP, buff=0.3)
        dl = zh("DR", 30, DR_COLOR).next_to(dr, UP, buff=0.3)

        with self.voice("err_3"):
            self.play(FadeOut(self.rows), FadeOut(self.t))
            cap = zh("DeepSeek-V3.2 的错误分布（图 6）", 26, GREY_B).to_edge(UP, buff=0.4)
            self.play(FadeIn(cap), FadeIn(el))
            self.play(LaggedStart(*[FadeIn(s, scale=0.8) for s in eia], lag_ratio=0.4), run_time=3)

        with self.voice("err_4"):
            ie = eia[1]
            self.play(ie.animate.shift(0.25 * normalize(ie[1].get_center() - eia.get_center())))
            calls = VGroup(*[mono(c, 16, GREY_A) for c in
                             ["query_device(...)", "query_device(...)", "query_device(...)", "control(did=?, …)"]])
            calls.arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(eia, DOWN, buff=0.3)
            calls[-1].set_color(BAD)
            self.play(LaggedStart(*[FadeIn(c) for c in calls], lag_ratio=0.4), run_time=2)
            self.calls = calls

        with self.voice("err_5"):
            self.play(FadeIn(dl))
            self.play(LaggedStart(*[FadeIn(s, scale=0.8) for s in dr], lag_ratio=0.4), run_time=3)

        with self.voice("err_6"):
            for k in (1, 2):
                self.play(dr[k].animate.shift(0.25 * normalize(dr[k][1].get_center() - dr.get_center())), run_time=0.6)
            jump = zh("信息不足就直接执行", 22, BAD).next_to(dr, DOWN, buff=0.4)
            self.play(Write(jump))

        with self.voice("err_7"):
            self.play(Indicate(eia[0], color=WHITE), Indicate(dr[0], color=WHITE))
            l1 = zh("能查的：查个没完", 26, EIA_COLOR)
            l2 = zh("不能查的：想当然", 26, DR_COLOR)
            l3 = zh("两边都还没能稳定地按格式交卷", 26, YELLOW)
            g = VGroup(l1, l2, l3).arrange(DOWN, buff=0.25)
            bg = BackgroundRectangle(g, fill_opacity=0.92, buff=0.35)
            self.play(FadeIn(bg), FadeIn(l1))
            self.play(FadeIn(l2))
            self.play(Write(l3))
        self.clear()


# ====================================================================== 17 附录 + 总结
class S17_Outro(VoiceScene):
    def construct(self):
        with self.voice("out_1"):
            t = zh("附录一览", 36, GREY_B).to_edge(UP, buff=0.6)
            items = VGroup(*[
                VGroup(Text(k, font_size=26, color=BLUE_C), zh(v, 24)).arrange(RIGHT, buff=0.4)
                for k, v in [("A", "HomeEnv 完整状态结构"), ("B", "任务生成规则与示例"),
                             ("C", "22 个子类的例句与判分条件"), ("D", "两种设置的实现与完整轨迹"),
                             ("E", "四个代表模型的完整错误分布"), ("F · G", "子类级结果 · 提示词模板")]
            ]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items], lag_ratio=0.3), run_time=4)

        with self.voice("out_2"):
            self.clear(run_time=0.6)
            facts = VGroup(token_box("HomeEnv：用状态转移评判", TEAL_D, 28),
                           token_box("1,100 条人工审核任务", YELLOW_E, 28),
                           token_box("7 大类 · 22 子类", BLUE_D, 28),
                           token_box("小公寓 → 135 台设备", GREEN_E, 28)).arrange_in_grid(2, 2, buff=(0.6, 0.6))
            self.play(LaggedStart(*[FadeIn(f, scale=0.8) for f in facts], lag_ratio=0.4), run_time=3)
            self.facts = facts

        with self.voice("out_3"):
            self.play(FadeOut(self.facts))
            good = VGroup(zh("做得好", 32, OK), zh("明确控制", 26), zh("简单查询", 26)).arrange(DOWN, buff=0.3)
            bad = VGroup(zh("仍不可靠", 32, BAD), zh("自动化", 26), zh("歧义消解", 26), zh("个性化记忆", 26),
                         zh("复杂的家", 26)).arrange(DOWN, buff=0.3)
            VGroup(good, bad).arrange(RIGHT, buff=3, aligned_edge=UP)
            self.play(FadeIn(good, shift=UP * 0.2))
            self.play(FadeIn(bad, shift=UP * 0.2))
            self.gb = VGroup(good, bad)

        with self.voice("out_4"):
            self.play(FadeOut(self.gb))
            t = zh("下一代智能家居助手需要…", 36, YELLOW).to_edge(UP, buff=0.7)
            cards = VGroup(*[VGroup(Text(f"{i + 1}", font_size=52, color=c), zh(n, 36)).arrange(RIGHT, buff=0.4)
                             for i, (n, c) in enumerate([("状态落地", BLUE_C), ("澄清策略", PURPLE_B),
                                                         ("偏好感知推理", PINK), ("规范的工具调用", TEAL)])])
            cards.arrange_in_grid(2, 2, buff=(1.6, 1.0), col_alignments="ll").shift(DOWN * 0.3)
            self.play(Write(t))
            for c in cards:
                self.play(FadeIn(c, shift=UP * 0.2), run_time=0.7)
                self.wait(0.8)
            self.cards = VGroup(t, cards)

        with self.voice("out_5"):
            self.play(FadeOut(self.cards))
            say = bubble("“把我常待的房间，调成昨晚的温度。”", 32).shift(UP * 1.6)
            need = VGroup(zh("该查什么", 30, BLUE_C), zh("记得住什么", 30, PINK), zh("何时该问", 30, PURPLE_B),
                          zh("别碰不该碰的", 30, YELLOW)).arrange(RIGHT, buff=0.7).shift(DOWN * 0.6)
            self.play(FadeIn(say))
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in need], lag_ratio=0.5), run_time=3)

        with self.voice("out_6"):
            self.clear(run_time=0.6)
            ref = VGroup(Text("SMH-Bench", font_size=64, weight=BOLD, color=BLUE_B),
                         Text("arXiv:2606.01912", font_size=32, color=GREY_B),
                         zh("数据与代码：即将开源", 26, GREY_B),
                         zh("感谢收看", 40)).arrange(DOWN, buff=0.4)
            self.play(Write(ref[0]), FadeIn(ref[1]))
            self.play(FadeIn(ref[2]), FadeIn(ref[3], shift=UP * 0.2))
        self.clear()
