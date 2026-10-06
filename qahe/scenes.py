"""量子反常霍尔效应科普 —— Manim 场景（3Blue1Brown 风格）。

渲染单个场景:  manim -qm qahe/scenes.py S05_Edge
整片构建:      python build.py all --paper qahe

曲线均为示意图；数值（h/e²、30 mK、年份等）取自原始文献与公开资料。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from common import VoiceScene, token_box, zh  # noqa: E402

E_COL = BLUE_B       # 电子
B_COL = PURPLE_B     # 磁场
OK = GREEN_C
BAD = RED_C
SERIF = "DejaVu Serif"


def math(text: str, size: float = 40, color=WHITE) -> Text:
    return Text(text, font=SERIF, font_size=size, color=color, slant=ITALIC)


def section_title(text: str, color=YELLOW) -> Text:
    return zh(text, 36, color).to_edge(UP, buff=0.45)


def note(text: str = "（示意图）") -> Text:
    return zh(text, 18, GREY_B).to_corner(DR, buff=0.3)


def electron(pos=ORIGIN, r=0.09) -> Dot:
    return Dot(pos, radius=r, color=E_COL)


def b_field_dots(rect: Mobject, nx=7, ny=3, color=B_COL) -> VGroup:
    """⊙ 表示垂直纸面向外的磁场。"""
    g = VGroup()
    w, h = rect.width, rect.height
    for i in range(nx):
        for j in range(ny):
            p = rect.get_center() + np.array([(i + 0.5) / nx * w - w / 2, (j + 0.5) / ny * h - h / 2, 0])
            g.add(VGroup(Circle(0.09, color=color, stroke_width=2), Dot(radius=0.025, color=color)).move_to(p))
    return g


def axes(x_label: str, y_label: str, x_range=(-1, 1, 1), y_range=(-1, 1, 1), xl=7.0, yl=4.0) -> VGroup:
    ax = Axes(x_range=list(x_range), y_range=list(y_range), x_length=xl, y_length=yl,
              axis_config={"color": GREY_B, "include_ticks": False, "tip_length": 0.2})
    xlab = zh(x_label, 22, GREY_B).next_to(ax.x_axis.get_end(), DOWN, buff=0.15)
    ylab = zh(y_label, 22, GREY_B).next_to(ax.y_axis.get_end(), LEFT, buff=0.15)
    return VGroup(ax, xlab, ylab)


def numline(start, end, step, length=10, font_size=22) -> NumberLine:
    """带纯文本刻度标签的数轴（不依赖 LaTeX）。"""
    nl = NumberLine(x_range=[start, end, step], length=length, color=GREY_B)
    labels = VGroup(*[Text(str(int(v)), font_size=font_size, color=GREY_B).next_to(nl.n2p(v), DOWN, buff=0.15)
                      for v in np.arange(start, end + step / 2, step) if v <= end])
    nl.add(labels)
    return nl


# ====================================================================== 1 开场
class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("in_1"):
            box = Rectangle(width=7, height=3.2, stroke_color=GREY_B).shift(DOWN * 0.3)
            rng = np.random.default_rng(2)
            atoms = VGroup(*[Dot(box.get_center() + np.array([x, y, 0]), radius=0.12, color=GREY_D)
                             for x in np.linspace(-3, 3, 9) for y in np.linspace(-1.2, 1.2, 4)])
            es = VGroup(*[electron(box.get_center() + np.array([rng.uniform(-3, 3), rng.uniform(-1.3, 1.3), 0])) for _ in range(14)])
            heat = zh("碰撞 → 发热 → 浪费能量", 30, BAD).next_to(box, UP, buff=0.4)
            self.play(Create(box), FadeIn(atoms))
            self.play(FadeIn(es))
            for _ in range(3):
                self.play(*[e.animate.shift(np.array([rng.uniform(-0.6, 0.6), rng.uniform(-0.4, 0.4), 0])) for e in es],
                          run_time=0.7, rate_func=there_and_back_with_pause)
            self.play(Write(heat), box.animate.set_stroke(BAD, 4))
            self.g = VGroup(box, atoms, es, heat)

        with self.voice("in_2"):
            self.play(FadeOut(self.g))
            lanes = VGroup(*[Line(LEFT * 5.5, RIGHT * 5.5, color=GREY_D) for _ in range(4)]).arrange(DOWN, buff=0.8)
            for l in lanes:
                l.set_stroke(width=2)
            dashes = VGroup(*[DashedLine(LEFT * 5.5, RIGHT * 5.5, color=GREY_C, dash_length=0.3).move_to(
                (lanes[i].get_center() + lanes[i + 1].get_center()) / 2) for i in range(3)])
            cars = VGroup(*[electron(LEFT * 5 + UP * (lanes[i].get_y() + lanes[i + 1].get_y()) / 2) for i in range(3)])
            self.play(Create(lanes), Create(dashes))
            self.play(FadeIn(cars))
            self.play(*[c.animate.shift(RIGHT * 10) for c in cars], run_time=3, rate_func=linear)
            self.g = VGroup(lanes, dashes, cars)

        with self.voice("in_3"):
            self.play(FadeOut(self.g))
            title = zh("量子反常霍尔效应", 64, YELLOW)
            en = Text("Quantum Anomalous Hall Effect", font_size=30, color=GREY_A)
            yr = zh("2013 · 中国团队首次实验实现", 28)
            q = zh("“从中国实验室里第一次发表出的诺贝尔奖级的物理学论文” —— 杨振宁", 24, GREY_B)
            VGroup(title, en, yr, q).arrange(DOWN, buff=0.45)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(en), FadeIn(yr))
            self.play(FadeIn(q, shift=UP * 0.2))
            self.g = VGroup(title, en, yr, q)

        with self.voice("in_4"):
            self.play(FadeOut(self.g))
            items = ["前世今生", "物理原理", "对物理学和世界的影响", "发现者薛其坤"]
            rows = VGroup(*[VGroup(Text(f"{i + 1}", font_size=40, color=BLUE_B), zh(t, 34)).arrange(RIGHT, buff=0.4)
                            for i, t in enumerate(items)]).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.4), run_time=3)
        self.clear()


# ====================================================================== 2 霍尔效应
class S02_Hall(VoiceScene):
    def construct(self):
        slab = Rectangle(width=7, height=2.6, fill_color=GREY_E, fill_opacity=0.7, stroke_color=GREY_B).shift(DOWN * 0.3)

        with self.voice("hall_1"):
            t = zh("1879 · 埃德温·霍尔（约翰斯·霍普金斯大学研究生）", 26, YELLOW).to_edge(UP, buff=0.5)
            cur = Arrow(slab.get_left() + LEFT * 0.9, slab.get_left() + RIGHT * 0.2, color=ORANGE, buff=0)
            cl = zh("电流 I", 22, ORANGE).next_to(cur, UP, buff=0.1)
            bf = b_field_dots(slab)
            bl = zh("磁场 B（指向屏幕外）", 22, B_COL).next_to(slab, DOWN, buff=0.25)
            self.play(Write(t), FadeIn(slab))
            self.play(GrowArrow(cur), FadeIn(cl))
            self.play(FadeIn(bf), FadeIn(bl))
            self.t, self.bf, self.bl, self.cur, self.cl = t, bf, bl, cur, cl

        with self.voice("hall_2"):
            self.play(self.bf.animate.set_opacity(0.25))
            paths = VGroup()
            for k in range(4):
                start = slab.get_left() + RIGHT * (0.4 + 1.5 * k) + UP * (-0.2 + 0.1 * k)
                p = ArcBetweenPoints(start, start + RIGHT * 1.3 + UP * 1.0, angle=-PI / 3, color=E_COL)
                paths.add(p)
            dots = VGroup(*[electron(p.get_start()) for p in paths])
            self.play(FadeIn(dots))
            self.play(*[MoveAlongPath(d, p) for d, p in zip(dots, paths)], run_time=1.5)
            fl = zh("洛伦兹力：向一侧偏转", 24, E_COL).next_to(slab, UP, buff=0.15).shift(LEFT * 1.5)
            self.play(FadeIn(fl))
            minus = VGroup(*[Text("−", font_size=36, color=E_COL).move_to(slab.get_top() + DOWN * 0.25 + RIGHT * x)
                             for x in np.linspace(-3, 3, 8)])
            plus = VGroup(*[Text("+", font_size=36, color=RED_B).move_to(slab.get_bottom() + UP * 0.25 + RIGHT * x)
                            for x in np.linspace(-3, 3, 8)])
            self.play(FadeOut(dots), LaggedStart(*[FadeIn(m) for m in minus], lag_ratio=0.05),
                      LaggedStart(*[FadeIn(p) for p in plus], lag_ratio=0.05))
            vh = DoubleArrow(slab.get_right() + RIGHT * 0.5 + UP * 1.2, slab.get_right() + RIGHT * 0.5 + DOWN * 1.2,
                             color=YELLOW, buff=0)
            vl = zh("霍尔电压", 24, YELLOW).next_to(vh, RIGHT, buff=0.15)
            self.play(GrowFromCenter(vh), FadeIn(vl))
            self.g = VGroup(slab, self.bf, self.bl, self.cur, self.cl, minus, plus, vh, vl, fl, self.t)

        with self.voice("hall_3"):
            self.play(FadeOut(self.g))
            a = axes("磁场 B", "霍尔电阻 R_xy", (0, 1, 1), (0, 1, 1), 6, 4).shift(DOWN * 0.2)
            line = a[0].plot(lambda x: 0.9 * x, x_range=[0, 1], color=YELLOW, stroke_width=5)
            f = math("R_xy = V_H / I  ∝  B", 34, YELLOW).to_edge(UP, buff=0.6)
            self.play(Create(a), Write(f))
            self.play(Create(line), run_time=1.5)
            self.add(note())

        with self.voice("hall_4"):
            self.clear(run_time=0.5)
            uses = VGroup(*[VGroup(token_box(n, BLUE_D, 28), zh(d, 22, GREY_B)).arrange(DOWN, buff=0.25)
                            for n, d in [("手机", "电子罗盘"), ("汽车", "转速 / 位置传感器"), ("笔记本", "合盖检测")]]).arrange(RIGHT, buff=1.2)
            self.play(LaggedStart(*[FadeIn(u, shift=UP * 0.2) for u in uses], lag_ratio=0.4), run_time=2.5)
        self.clear()


# ====================================================================== 3 反常霍尔效应
class S03_Anomalous(VoiceScene):
    def construct(self):
        with self.voice("ano_1"):
            t = zh("1880 · 铁磁材料中的霍尔效应", 30, YELLOW).to_edge(UP, buff=0.5)
            slab = Rectangle(width=6, height=2.4, fill_color=GREY_E, fill_opacity=0.7, stroke_color=GREY_B).shift(DOWN * 0.2)
            spins = VGroup(*[Arrow(DOWN * 0.3, UP * 0.3, color=RED_B, buff=0, max_tip_length_to_length_ratio=0.35)
                             .move_to(slab.get_center() + np.array([x, y, 0]))
                             for x in np.linspace(-2.5, 2.5, 8) for y in (-0.6, 0.6)])
            sl = zh("铁：原子磁矩整齐排列", 24, RED_B).next_to(slab, DOWN, buff=0.3)
            self.play(Write(t), FadeIn(slab))
            self.play(LaggedStart(*[GrowArrow(s) for s in spins], lag_ratio=0.03), FadeIn(sl))
            self.g = VGroup(t, slab, spins, sl)

        with self.voice("ano_2"):
            self.play(FadeOut(self.g))
            a = axes("磁场 B", "霍尔电阻", (-1, 1, 1), (-1, 1, 1), 7, 4.2).shift(DOWN * 0.2)
            ax = a[0]
            normal = ax.plot(lambda x: 0.25 * x, x_range=[-1, 1], color=GREY_B, stroke_width=3)
            anom = ax.plot(lambda x: 0.75 * np.tanh(12 * x) + 0.15 * x, x_range=[-1, 1], color=YELLOW, stroke_width=5)
            ln = zh("普通金属", 22, GREY_B).next_to(ax.c2p(1, 0.25), RIGHT, buff=0.1)
            la = zh("铁磁材料：自身磁化贡献", 22, YELLOW).next_to(ax.c2p(0.55, 0.95), UP, buff=0.1)
            self.play(Create(a))
            self.play(Create(normal), FadeIn(ln))
            self.play(Create(anom), FadeIn(la), run_time=1.5)
            self.add(note())
            self.g = VGroup(a, normal, anom, ln, la)

        with self.voice("ano_3"):
            self.clear(run_time=0.5)
            q = zh("机制之谜：近一个世纪", 32)
            ans = VGroup(zh("线索：", 28, GREY_B), zh("贝里曲率", 40, YELLOW), zh("（能带的几何性质）", 24, GREY_B)).arrange(RIGHT, buff=0.3)
            VGroup(q, ans).arrange(DOWN, buff=0.8)
            self.play(FadeIn(q))
            self.play(FadeIn(ans, shift=UP * 0.2))
            self.play(Circumscribe(ans[1], color=YELLOW))
        self.clear()


# ====================================================================== 4 量子霍尔效应
class S04_QHE(VoiceScene):
    def construct(self):
        with self.voice("qhe_1"):
            t = zh("1980 年 2 月 · 冯·克利青 · 格勒诺布尔", 28, YELLOW).to_edge(UP, buff=0.5)
            conds = VGroup(token_box("二维电子系统", BLUE_D, 28), token_box("接近绝对零度", TEAL_D, 28),
                           token_box("强磁场", PURPLE_D, 28)).arrange(RIGHT, buff=0.6)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in conds], lag_ratio=0.4), run_time=2)
            self.g = VGroup(t, conds)

        a = axes("磁场 B", "电阻", (0, 1, 1), (0, 1, 1), 9, 5).shift(DOWN * 0.3)
        ax = a[0]

        steps = [(0.08, 0.25), (0.28, 1 / 3 - 0.25), (0.45, 0.5 - 1 / 3), (0.7, 0.5)]  # (位置, 跳变量)，平台 = 1/ν

        def stair(x):
            return 0.9 * sum(dh / (1 + np.exp(-(x - c) / 0.012)) for c, dh in steps)

        def rxx(x):
            return 0.3 * sum(np.exp(-((x - c) / 0.03) ** 2) for c, _ in steps)

        with self.voice("qhe_2"):
            self.play(FadeOut(self.g))
            self.play(Create(a))
            ryx = ax.plot(stair, x_range=[0.02, 1, 0.002], color=YELLOW, stroke_width=5, use_smoothing=False)
            rx = ax.plot(rxx, x_range=[0.02, 1, 0.002], color=TEAL, stroke_width=3, use_smoothing=False)
            l1 = zh("霍尔电阻：台阶", 22, YELLOW).next_to(ax.c2p(0.9, 0.9), UP, buff=0.1)
            l2 = zh("纵向电阻：平台处 ≈ 0", 22, TEAL).next_to(ax.c2p(0.6, 0.12), UP, buff=0.4)
            self.play(Create(ryx), run_time=2.5)
            self.play(FadeIn(l1))
            self.play(Create(rx), FadeIn(l2), run_time=1.5)
            self.add(note())
            self.plot = VGroup(a, ryx, rx, l1, l2)

        with self.voice("qhe_3"):
            labs = VGroup(*[math(f"h/{n}e²", 22, YELLOW).next_to(ax.c2p(0.02, 0.9 / n), LEFT, buff=0.1) for n in (1, 2, 3, 4)])
            lines = VGroup(*[DashedLine(ax.c2p(0, 0.9 / n), ax.c2p(1, 0.9 / n), color=GREY_D, stroke_width=1.5) for n in (1, 2, 3, 4)])
            self.play(Create(lines), FadeIn(labs))
            f = VGroup(math("R_xy = h / (ν e²)", 36, YELLOW), math("h / e² ≈ 25 812.807 Ω", 30)).arrange(DOWN, buff=0.2)
            f.arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.25)
            bg = BackgroundRectangle(f, fill_opacity=0.9, buff=0.15)
            self.play(FadeIn(bg), Write(f))

        with self.voice("qhe_4"):
            self.clear(run_time=0.5)
            pts = VGroup(zh("与材料无关", 30), zh("与形状无关", 30), zh("与杂质无关", 30)).arrange(DOWN, buff=0.4).shift(UP * 0.6)
            acc = zh("精确到 10⁻⁹ 量级", 34, YELLOW).next_to(pts, DOWN, buff=0.6)
            nob = zh("1985 年诺贝尔物理学奖 · 冯·克利青", 26, GREY_B).to_edge(DOWN, buff=0.7)
            self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.4))
            self.play(Write(acc))
            self.play(FadeIn(nob))

        with self.voice("qhe_5"):
            self.clear(run_time=0.5)
            tl = VGroup(*[VGroup(Text(y, font_size=30, color=BLUE_B), zh(d, 26)).arrange(RIGHT, buff=0.5) for y, d in [
                ("1990", "量子霍尔效应成为国际电阻标准"),
                ("1982", "发现分数量子霍尔效应"),
                ("1998", "分数量子霍尔效应相关研究获诺贝尔奖")]]).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in tl], lag_ratio=0.5), run_time=3)
        self.clear()


# ====================================================================== 5 边缘态
class S05_Edge(VoiceScene):
    def construct(self):
        sample = Rectangle(width=9, height=4.4, stroke_color=GREY_B, stroke_width=3).shift(DOWN * 0.3)

        with self.voice("edge_1"):
            self.play(Create(sample))
            circles = VGroup()
            for x in np.linspace(-3, 3, 5):
                for y in (-0.9, 0.5):
                    c = Circle(0.35, color=E_COL, stroke_width=2).move_to(sample.get_center() + np.array([x, y, 0]))
                    circles.add(c)
            dots = VGroup(*[electron(c.point_from_proportion(0)) for c in circles])
            self.play(LaggedStart(*[Create(c) for c in circles], lag_ratio=0.05), FadeIn(dots))
            self.play(*[MoveAlongPath(d, c) for d, c in zip(dots, circles)], run_time=2, rate_func=linear)
            lab = zh("内部：原地打转 → 绝缘", 26, E_COL).move_to(sample.get_center() + DOWN * 0.15)
            bg = BackgroundRectangle(lab, fill_opacity=0.85, buff=0.1)
            self.play(FadeIn(bg), FadeIn(lab))
            self.inside = VGroup(circles, dots, lab, bg)

        def skip_path(y, direction, n=8, r=0.3):
            pts = []
            x0 = -4.2 if direction > 0 else 4.2
            for k in range(n):
                cx = x0 + direction * k * 1.05
                for th in np.linspace(0, PI, 12):
                    pts.append([cx + direction * (r - r * np.cos(th)) * 1.75, y - np.sign(y + 0.3) * r * np.sin(th), 0])
            return VMobject(color=YELLOW, stroke_width=3).set_points_smoothly([np.array(p) for p in pts])

        with self.voice("edge_2"):
            self.play(self.inside.animate.set_opacity(0.25))
            top_y = sample.get_top()[1]
            bot_y = sample.get_bottom()[1]
            top = skip_path(top_y, -1)
            bot = skip_path(bot_y, 1)
            self.play(Create(top), Create(bot), run_time=2.5)
            at = Arrow(RIGHT * 2, LEFT * 2, color=YELLOW).next_to(sample, UP, buff=0.15)
            ab = Arrow(LEFT * 2, RIGHT * 2, color=YELLOW).next_to(sample, DOWN, buff=0.15)
            self.play(GrowArrow(at), GrowArrow(ab))
            self.edges = VGroup(top, bot, at, ab)

        with self.voice("edge_3"):
            imp = Dot(sample.get_bottom() + UP * 0.35, radius=0.16, color=RED_C)
            il = zh("杂质", 22, RED_C).next_to(imp, UP, buff=0.1)
            self.play(FadeIn(imp), FadeIn(il))
            e = electron(sample.get_bottom() + LEFT * 4 + UP * 0.3)
            detour = VMobject().set_points_smoothly([sample.get_bottom() + LEFT * 4 + UP * 0.3, sample.get_bottom() + LEFT * 0.6 + UP * 0.3,
                                                     sample.get_bottom() + UP * 0.75, sample.get_bottom() + RIGHT * 0.6 + UP * 0.3,
                                                     sample.get_bottom() + RIGHT * 4 + UP * 0.3])
            self.play(FadeIn(e))
            self.play(MoveAlongPath(e, detour), run_time=2.5, rate_func=linear)
            r = zh("无法掉头 → 无背散射 → 无损耗", 28, OK).move_to(sample.get_center())
            bg = BackgroundRectangle(r, fill_opacity=0.9, buff=0.15)
            self.play(FadeIn(bg), Write(r))

        with self.voice("edge_4"):
            self.clear(run_time=0.5)
            left = VGroup(zh("普通导体：拥挤的集市", 26, BAD), Square(2.6, stroke_color=GREY_B)).arrange(DOWN, buff=0.3)
            rng = np.random.default_rng(5)
            crowd = VGroup(*[electron(left[1].get_center() + np.array([rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1), 0]))
                             for _ in range(18)])
            right = VGroup(zh("量子霍尔：各走各的车道", 26, OK), Square(2.6, stroke_color=GREY_B)).arrange(DOWN, buff=0.3)
            VGroup(left, right).arrange(RIGHT, buff=1.5)
            crowd.move_to(left[1])
            lanes = VGroup(*[Line(right[1].get_left() + UP * y, right[1].get_right() + UP * y, color=GREY_D) for y in (-0.65, 0, 0.65)])
            cars = VGroup(*[electron(right[1].get_left() + RIGHT * 0.2 + UP * y) for y in (-0.33, 0.33, 0.98, -0.98)])
            self.play(FadeIn(left), FadeIn(crowd), FadeIn(right), Create(lanes), FadeIn(cars))
            self.play(*[c.animate.shift(np.array([rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0])) for c in crowd],
                      *[c.animate.shift(RIGHT * 2.2) for c in cars], run_time=2, rate_func=linear)
        self.clear()


# ====================================================================== 6 拓扑
class S06_Topology(VoiceScene):
    def construct(self):
        with self.voice("top_1"):
            t = zh("拓扑", 72, YELLOW)
            self.play(Write(t))
            self.t = t

        with self.voice("top_2"):
            self.play(self.t.animate.scale(0.5).to_edge(UP, buff=0.4))
            ball = Circle(1.1, fill_color=BLUE_D, fill_opacity=0.6, stroke_color=BLUE_B)
            donut = VGroup(Ellipse(width=2.8, height=1.8, fill_color=ORANGE, fill_opacity=0.6, stroke_color=ORANGE),
                           Ellipse(width=0.9, height=0.45, fill_color=config.background_color, fill_opacity=1, stroke_color=ORANGE))
            cup = VGroup(RoundedRectangle(corner_radius=0.2, width=1.6, height=1.8, fill_color=TEAL_D, fill_opacity=0.6, stroke_color=TEAL),
                         Annulus(inner_radius=0.3, outer_radius=0.55, fill_color=TEAL_D, fill_opacity=0.6, stroke_color=TEAL))
            cup[1].next_to(cup[0], RIGHT, buff=-0.1)
            g = VGroup(ball, donut, cup).arrange(RIGHT, buff=1.4).shift(UP * 0.2)
            labs = VGroup(zh("0 个洞", 26), zh("1 个洞", 26), zh("1 个洞", 26))
            for l, s in zip(labs, g):
                l.next_to(s, DOWN, buff=0.4)
            self.play(FadeIn(ball), FadeIn(labs[0]))
            self.play(ball.animate.stretch(1.4, 0).stretch(0.7, 1), run_time=1)
            self.play(ball.animate.stretch(1 / 1.4, 0).stretch(1 / 0.7, 1), run_time=1)
            self.play(FadeIn(donut), FadeIn(labs[1]))
            self.play(FadeIn(cup), FadeIn(labs[2]))
            no = zh("只能是整数，不能是 0.5 个", 28, YELLOW).to_edge(DOWN, buff=0.8)
            self.play(Write(no))

        with self.voice("top_3"):
            self.clear(run_time=0.5)
            t = zh("1982 · 索利斯等（TKNN）", 28, GREY_B).to_edge(UP, buff=0.6)
            f = VGroup(math("C = (1/2π) ∮ Ω(k) d²k", 44, YELLOW), zh("陈数 = 贝里曲率的总和 / 2π", 28)).arrange(DOWN, buff=0.4)
            eq = math("R_xy = h / (C e²)", 40).next_to(f, DOWN, buff=0.7)
            self.play(FadeIn(t), Write(f[0]))
            self.play(FadeIn(f[1]))
            self.play(Write(eq))

        with self.voice("top_4"):
            noise = VGroup(*[Dot(np.array([np.random.uniform(-6, 6), np.random.uniform(-3.5, 3.5), 0]), radius=0.05, color=RED_D)
                             for _ in range(60)])
            self.play(FadeIn(noise, lag_ratio=0.02), run_time=1.5)
            self.play(Indicate(eq, color=YELLOW))
            self.play(FadeOut(noise))

        with self.voice("top_5"):
            self.clear(run_time=0.5)
            n = VGroup(zh("2016 年诺贝尔物理学奖", 34, YELLOW), zh("索利斯 · 霍尔丹 · 科斯特利茨", 30), zh("拓扑相变与拓扑物态", 26, GREY_B)).arrange(DOWN, buff=0.4)
            self.play(FadeIn(n, shift=UP * 0.2))
        self.clear()


# ====================================================================== 7 霍尔丹模型
class S07_Haldane(VoiceScene):
    def construct(self):
        with self.voice("hal_1"):
            mag = VGroup(Annulus(inner_radius=0.9, outer_radius=1.6, fill_color=GREY_D, fill_opacity=0.8, stroke_color=GREY_B),
                         zh("超导磁体", 24)).arrange(DOWN, buff=0.3).shift(LEFT * 3)
            vals = VGroup(VGroup(zh("量子霍尔所需", 24, GREY_B), Text("~10 T", font_size=56, color=BAD)).arrange(DOWN),
                          VGroup(zh("冰箱贴", 24, GREY_B), Text("~0.01 T", font_size=40, color=GREY_A)).arrange(DOWN)).arrange(DOWN, buff=0.6)
            vals.shift(RIGHT * 2.5)
            self.play(FadeIn(mag))
            self.play(FadeIn(vals))
            self.add(note("（量级示意）"))

        with self.voice("hal_2"):
            self.clear(run_time=0.5)
            q = zh("不加外磁场，能实现量子霍尔效应吗？", 34, YELLOW).to_edge(UP, buff=0.6)
            h = zh("1988 · 霍尔丹：可以", 30).next_to(q, DOWN, buff=0.4)
            self.play(Write(q))
            self.play(FadeIn(h))
            self.q = VGroup(q, h)

        with self.voice("hal_3"):
            self.play(self.q.animate.scale(0.7).to_edge(UP, buff=0.3))
            hexes = VGroup()
            for i in range(-3, 4):
                for j in range(-1, 2):
                    c = np.array([i * 1.3 + (0.65 if j % 2 else 0), j * 1.12, 0])
                    hexes.add(RegularPolygon(6, radius=0.75, color=GREY_B, stroke_width=2).rotate(PI / 6).move_to(c))
            hexes.shift(DOWN * 0.5)
            self.play(Create(hexes), run_time=2)
            signs = VGroup()
            for k, hx in enumerate(hexes):
                c = hx.get_center()
                signs.add(Text("+", font_size=26, color=RED_B).move_to(c + UP * 0.28))
                signs.add(Text("−", font_size=30, color=BLUE_B).move_to(c + DOWN * 0.28))
            self.play(FadeIn(signs, lag_ratio=0.01))
            lab = zh("局部有磁通，平均磁场 = 0", 28, YELLOW).to_edge(DOWN, buff=0.5)
            bg = BackgroundRectangle(lab, fill_opacity=0.9, buff=0.1)
            self.play(FadeIn(bg), Write(lab))
            self.lat = VGroup(hexes, signs, lab, bg)

        with self.voice("hal_4"):
            self.play(FadeOut(self.lat), FadeOut(self.q))
            k = VGroup(zh("关键：", 30, GREY_B), zh("打破时间反演对称性", 40, YELLOW)).arrange(RIGHT, buff=0.3).shift(UP * 0.5)
            r = zh("= 量子反常霍尔效应的理论雏形", 30).next_to(k, DOWN, buff=0.6)
            self.play(FadeIn(k))
            self.play(Write(r))

        with self.voice("hal_5"):
            self.clear(run_time=0.5)
            tl = numline(1988, 2013, 5, 10, 24).shift(DOWN * 0.5)
            p1 = Dot(tl.n2p(1988), color=YELLOW)
            l1 = zh("理论模型", 24, YELLOW).next_to(p1, UP, buff=0.3)
            sleep = zh("纸面上沉睡二十多年 · 没有真实材料", 26, GREY_B).next_to(tl, UP, buff=1.2)
            self.play(Create(tl), FadeIn(p1), FadeIn(l1))
            self.play(FadeIn(sleep))
        self.clear()


# ====================================================================== 8 拓扑绝缘体
class S08_TI(VoiceScene):
    def construct(self):
        with self.voice("ti_1"):
            t = zh("拓扑绝缘体", 60, YELLOW)
            y = zh("2005 年前后", 28, GREY_B).next_to(t, DOWN, buff=0.4)
            self.play(Write(t), FadeIn(y))
            self.t = VGroup(t, y)

        with self.voice("ti_2"):
            self.play(self.t.animate.scale(0.5).to_edge(UP, buff=0.4))
            outer = RoundedRectangle(corner_radius=0.3, width=5, height=3.2, stroke_color=YELLOW, stroke_width=8)
            inner = RoundedRectangle(corner_radius=0.2, width=4.6, height=2.8, fill_color=GREY_E, fill_opacity=1, stroke_width=0)
            body = VGroup(outer, inner).shift(LEFT * 2.8)
            li = zh("内部：绝缘", 24).move_to(inner)
            ls = zh("表面：导电", 24, YELLOW).next_to(outer, DOWN, buff=0.25)
            self.play(FadeIn(body), FadeIn(li), FadeIn(ls))
            circ = Circle(1.3, color=GREY_B).shift(RIGHT * 3)
            arrows = VGroup()
            for th in np.linspace(0, TAU, 8, endpoint=False):
                p = circ.get_center() + 1.3 * np.array([np.cos(th), np.sin(th), 0])
                mom = Arrow(p, p + 0.6 * np.array([np.cos(th), np.sin(th), 0]), color=E_COL, buff=0, stroke_width=3,
                            max_tip_length_to_length_ratio=0.3)
                spin = Arrow(p, p + 0.5 * np.array([-np.sin(th), np.cos(th), 0]), color=RED_B, buff=0, stroke_width=3,
                             max_tip_length_to_length_ratio=0.3)
                arrows.add(mom, spin)
            lk = VGroup(zh("蓝：运动方向", 20, E_COL), zh("红：自旋方向", 20, RED_B)).arrange(DOWN, buff=0.1).next_to(circ, DOWN, buff=0.6)
            self.play(Create(circ), LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.05), FadeIn(lk), run_time=2)
            lock = zh("自旋–动量锁定", 26, YELLOW).next_to(circ, UP, buff=0.4)
            self.play(Write(lock))

        with self.voice("ti_3"):
            self.clear(run_time=0.5)
            tl = VGroup(*[VGroup(Text(y, font_size=32, color=BLUE_B), zh(d, 26)).arrange(RIGHT, buff=0.5) for y, d in [
                ("2007", "碲化汞量子阱：二维拓扑绝缘体被证实"),
                ("2009", "铋硒、铋碲：三维拓扑绝缘体")]]).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in tl], lag_ratio=0.5), run_time=2.5)

        with self.voice("ti_4"):
            self.clear(run_time=0.5)
            a = VGroup(token_box("拓扑绝缘体", TEAL_D, 30), zh("保持时间反演对称", 22, GREY_B), zh("量子自旋霍尔", 24)).arrange(DOWN, buff=0.25)
            plus = Text("+", font_size=60)
            m = VGroup(token_box("磁性", RED_E, 30), zh("打破时间反演对称", 22, GREY_B)).arrange(DOWN, buff=0.25)
            eq = Text("=", font_size=60)
            r = token_box("量子反常霍尔", GOLD_E, 30)
            g = VGroup(a, plus, m, eq, r).arrange(RIGHT, buff=0.5)
            self.play(FadeIn(a))
            self.play(FadeIn(plus), FadeIn(m))
            self.play(FadeIn(eq), FadeIn(r))
        self.clear()


# ====================================================================== 9 配方
class S09_Recipe(VoiceScene):
    def construct(self):
        with self.voice("rec_1"):
            t = zh("2010 · 理论配方（《科学》）", 30, YELLOW).to_edge(UP, buff=0.5)
            who = zh("方忠、戴希（中国科学院物理研究所） · 张首晟（斯坦福大学）等", 24, GREY_B).next_to(t, DOWN, buff=0.3)
            film = Rectangle(width=8, height=1.2, fill_color=TEAL_E, fill_opacity=0.7, stroke_color=TEAL).shift(DOWN * 0.5)
            fl = zh("拓扑绝缘体薄膜（铋碲 / 锑碲 / 铋硒）", 24).next_to(film, DOWN, buff=0.3)
            rng = np.random.default_rng(1)
            dop = VGroup(*[Dot(film.get_center() + np.array([rng.uniform(-3.8, 3.8), rng.uniform(-0.5, 0.5), 0]), radius=0.08,
                               color=RED_B) for _ in range(22)])
            dl = zh("掺入铬 / 铁等磁性原子", 24, RED_B).next_to(film, UP, buff=0.3)
            self.play(Write(t), FadeIn(who))
            self.play(FadeIn(film), FadeIn(fl))
            self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dop], lag_ratio=0.05), FadeIn(dl))

        conds = [("二维薄膜", "只有几纳米厚"), ("拓扑", "必须是拓扑绝缘体"), ("铁磁", "整齐、垂直于薄膜的磁序"), ("绝缘", "能量恰好落在能隙里")]
        cards = VGroup(*[VGroup(token_box(n, c, 32), zh(d, 20, GREY_B)).arrange(DOWN, buff=0.25)
                         for (n, d), c in zip(conds, [BLUE_D, TEAL_D, RED_E, GOLD_E])]).arrange(RIGHT, buff=0.6)

        with self.voice("rec_2"):
            self.clear(run_time=0.5)
            h = zh("四个条件，缺一不可", 36, YELLOW).to_edge(UP, buff=0.7)
            self.play(Write(h))

        with self.voice("rec_3"):
            for c in cards:
                self.play(FadeIn(c, shift=UP * 0.2), run_time=0.6)
                self.wait(1.4)

        with self.voice("rec_4"):
            clash = DoubleArrow(cards[2].get_bottom() + DOWN * 0.2, cards[3].get_bottom() + DOWN * 0.2, path_arc=PI / 2, color=BAD)
            cl = zh("掺磁 ↔ 绝缘：互相打架", 24, BAD).next_to(clash, DOWN, buff=0.1)
            self.play(Create(clash), FadeIn(cl))
            ath = zh("像要求一位运动员同时拿下短跑、跳高、游泳、举重四项世界冠军", 26, GREY_A).to_edge(DOWN, buff=0.5)
            self.play(Write(ath))
        self.clear()


# ====================================================================== 10 机制
class S10_Mechanism(VoiceScene):
    def construct(self):
        a = axes("动量 k", "能量 E", (-1, 1, 1), (-1, 1, 1), 6, 5).shift(LEFT * 2.5 + DOWN * 0.2)
        ax = a[0]

        with self.voice("mech_1"):
            self.play(Create(a))
            up = ax.plot(lambda k: abs(k) * 0.9, x_range=[-1, 1], color=YELLOW, stroke_width=5)
            dn = ax.plot(lambda k: -abs(k) * 0.9, x_range=[-1, 1], color=YELLOW, stroke_width=5)
            lab = zh("狄拉克锥：无能隙 → 表面导电", 26, YELLOW).to_edge(RIGHT, buff=0.5).shift(UP * 1)
            self.play(Create(up), Create(dn), FadeIn(lab))
            self.up, self.dn, self.lab = up, dn, lab

        with self.voice("mech_2"):
            gap = 0.35
            up2 = ax.plot(lambda k: np.sqrt((0.9 * k) ** 2 + gap ** 2), x_range=[-1, 1], color=YELLOW, stroke_width=5)
            dn2 = ax.plot(lambda k: -np.sqrt((0.9 * k) ** 2 + gap ** 2), x_range=[-1, 1], color=YELLOW, stroke_width=5)
            mag = zh("铁磁序 → 打破时间反演对称", 26, RED_B).next_to(self.lab, DOWN, buff=0.5).align_to(self.lab, LEFT)
            self.play(FadeIn(mag))
            self.play(Transform(self.up, up2), Transform(self.dn, dn2), run_time=2)
            br = DoubleArrow(ax.c2p(0, -gap), ax.c2p(0, gap), color=RED_B, buff=0, tip_length=0.15)
            gl = zh("能隙", 24, RED_B).next_to(br, RIGHT, buff=0.15)
            self.play(GrowFromCenter(br), FadeIn(gl))
            self.add(note())

        with self.voice("mech_3"):
            self.clear(run_time=0.5)
            top = Rectangle(width=7, height=0.5, fill_color=TEAL_D, fill_opacity=0.8, stroke_width=0).shift(UP * 1)
            mid = Rectangle(width=7, height=1.2, fill_color=GREY_E, fill_opacity=0.8, stroke_width=0).next_to(top, DOWN, buff=0)
            bot = top.copy().next_to(mid, DOWN, buff=0)
            lt = math("C = ½", 34, YELLOW).next_to(top, RIGHT, buff=0.4)
            lb = math("C = ½", 34, YELLOW).next_to(bot, RIGHT, buff=0.4)
            self.play(FadeIn(top), FadeIn(mid), FadeIn(bot))
            self.play(FadeIn(lt), FadeIn(lb))
            tot = math("½ + ½ = 1", 44, YELLOW).to_edge(DOWN, buff=0.8)
            self.play(Write(tot))

        with self.voice("mech_4"):
            self.clear(run_time=0.5)
            film = Rectangle(width=8, height=4, fill_color=GREY_E, fill_opacity=0.8, stroke_color=GREY_B).shift(DOWN * 0.3)
            lab = zh("内部、表面：绝缘", 26, GREY_A).move_to(film)
            loop = Rectangle(width=7.7, height=3.7, stroke_color=YELLOW, stroke_width=5).move_to(film)
            self.play(FadeIn(film), FadeIn(lab))
            self.play(Create(loop), run_time=2)
            e = electron(loop.point_from_proportion(0))
            self.play(MoveAlongPath(e, loop), run_time=2.5, rate_func=linear)
            res = VGroup(zh("零磁场", 26, OK), math("R_xy = h/e²", 30, YELLOW), math("R_xx → 0", 30, TEAL)).arrange(RIGHT, buff=0.8)
            res.next_to(film, UP, buff=0.3)
            self.play(FadeIn(res))
        self.clear()


# ====================================================================== 11 实验
class S11_Experiment(VoiceScene):
    def construct(self):
        with self.voice("exp_1"):
            t = zh("把材料一层原子一层原子地“长”出来", 34, YELLOW)
            self.play(Write(t))
            self.t = t

        with self.voice("exp_2"):
            self.play(self.t.animate.scale(0.7).to_edge(UP, buff=0.4))
            layers = VGroup(*[Rectangle(width=5, height=0.32, fill_color=c, fill_opacity=0.8, stroke_width=0.5)
                              for c in [GREY_D, TEAL_D, BLUE_D, TEAL_D, BLUE_D, TEAL_D, BLUE_D]]).arrange(UP, buff=0.02).shift(LEFT * 2.5 + DOWN * 1)
            sub = zh("衬底", 20, GREY_B).next_to(layers[0], DOWN, buff=0.1)
            ml = zh("分子束外延（MBE）", 26).next_to(layers, UP, buff=0.4)
            self.play(FadeIn(layers[0]), FadeIn(sub), FadeIn(ml))
            for l in layers[1:]:
                self.play(FadeIn(l, shift=DOWN * 0.4), run_time=0.35)
            tip = Triangle(fill_color=GREY_B, fill_opacity=1, stroke_width=0).rotate(PI).scale(0.4).move_to(RIGHT * 3 + UP * 0.8)
            atoms = VGroup(*[Dot(RIGHT * (1.5 + 0.4 * i) + DOWN * 0.3, radius=0.15, color=GOLD) for i in range(8)])
            sl = zh("扫描隧道显微镜（STM）", 26).next_to(atoms, DOWN, buff=0.5)
            self.play(FadeIn(tip), FadeIn(atoms), FadeIn(sl))
            self.play(tip.animate.shift(RIGHT * 2.8), run_time=1.5, rate_func=linear)

        with self.voice("exp_3"):
            self.clear(run_time=0.5)
            who = zh("清华大学 × 中国科学院物理研究所", 30).to_edge(UP, buff=0.7)
            vt = ValueTracker(0)
            num = always_redraw(lambda: Text(f"{int(vt.get_value()):,}", font_size=110, color=YELLOW).shift(UP * 0.2))
            lab = zh("个样品 · 历时 4 年", 30).next_to(num, DOWN, buff=0.4)
            self.play(FadeIn(who))
            self.add(num)
            self.play(vt.animate.set_value(1000), FadeIn(lab), run_time=3)
            num.clear_updaters()
            knobs = zh("调节：铬含量 · 铋锑比例 · 薄膜厚度", 26, GREY_B).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(knobs))

        a = axes("磁场 B", "霍尔电阻 ρ_yx", (-1, 1, 1), (-1.2, 1.2, 1), 7, 4.4).shift(DOWN * 0.4 + LEFT * 0.5)
        ax = a[0]

        with self.voice("exp_4"):
            self.clear(run_time=0.5)
            spec = VGroup(zh("掺铬 (Bi,Sb)₂Te₃ 薄膜 · 约 5 纳米", 24), zh("约 30 毫开 · 栅极调节", 24)).arrange(DOWN, buff=0.15)
            spec.to_corner(UR, buff=0.4)
            self.play(Create(a), FadeIn(spec))
            up = ax.plot(lambda b: np.tanh((b + 0.12) * 40), x_range=[-1, 1, 0.004], color=YELLOW, stroke_width=5, use_smoothing=False)
            dn = ax.plot(lambda b: np.tanh((b - 0.12) * 40), x_range=[-1, 1, 0.004], color=ORANGE, stroke_width=5, use_smoothing=False)
            hl = VGroup(DashedLine(ax.c2p(-1, 1), ax.c2p(1, 1), color=GREY_B), DashedLine(ax.c2p(-1, -1), ax.c2p(1, -1), color=GREY_B))
            hlab = math("h/e²", 26, YELLOW).next_to(ax.c2p(-1, 1), LEFT, buff=0.1)
            self.play(Create(hl), FadeIn(hlab))
            self.play(Create(up), Create(dn), run_time=2.5)
            zero = Dot(ax.c2p(0, 1), color=OK, radius=0.12)
            zl = zh("B = 0 时仍为 h/e²", 24, OK).next_to(ax.c2p(0.35, 1), UP, buff=0.25)
            self.play(FadeIn(zero, scale=2), FadeIn(zl))
            self.add(note("（示意图，依据 Chang et al., Science 2013 的描述）"))

        with self.voice("exp_5"):
            self.clear(run_time=0.5)
            pub = VGroup(zh("2013 年 3 月 · 《科学》", 32, YELLOW),
                         Text("Experimental Observation of the Quantum Anomalous Hall Effect\nin a Magnetic Topological Insulator",
                              font_size=22, color=GREY_A, line_spacing=0.8)).arrange(DOWN, buff=0.3).shift(UP * 1.2)
            tl = numline(1880, 2013, 20, 10, 22).shift(DOWN * 1.2)
            p1, p2 = Dot(tl.n2p(1880), color=TEAL), Dot(tl.n2p(2013), color=YELLOW)
            l1 = zh("反常霍尔效应", 22, TEAL).next_to(p1, UP)
            l2 = zh("量子化实现", 22, YELLOW).next_to(p2, UP)
            span = zh("130 多年", 30, YELLOW).next_to(tl, DOWN, buff=0.6)
            self.play(FadeIn(pub))
            self.play(Create(tl), FadeIn(p1), FadeIn(l1))
            self.play(FadeIn(p2), FadeIn(l2), Write(span))
        self.clear()


# ====================================================================== 12 薛其坤
class S12_Xue(VoiceScene):
    def construct(self):
        card = VGroup(zh("薛其坤", 64, YELLOW), zh("凝聚态物理学家 · 中国科学院院士", 26, GREY_A)).arrange(DOWN, buff=0.3)

        with self.voice("xue_1"):
            self.play(Write(card[0]), FadeIn(card[1]))
            self.play(card.animate.scale(0.55).to_corner(UL, buff=0.5))
            self.items = VGroup()
            self._add("1963.12", "生于山东蒙阴，沂蒙山区")
            self._add("1980", "考入山东大学光学系激光专业")

        with self.voice("xue_2"):
            self._add("1984–1987", "曲阜师范大学任教；考研两次未果")
            self._add("1987", "第三次考入中国科学院物理研究所")
            self._add("1994", "获博士学位")

        with self.voice("xue_3"):
            self._add("1992–1999", "日本东北大学 · 美国北卡罗来纳州立大学")
            self._add("1999", "回国，加入中国科学院物理研究所")

        with self.voice("xue_4"):
            self._add("2005", "当选中国科学院院士 · 清华大学教授")
            self._add("2013–2020", "清华大学副校长")
            self._add("2020–", "南方科技大学校长")

        with self.voice("xue_5"):
            self.play(FadeOut(self.items))
            clock = VGroup(Circle(1.3, color=WHITE), Dot(radius=0.06))
            hand1 = Line(ORIGIN, UP * 0.9, color=YELLOW, stroke_width=5)
            hand2 = Line(ORIGIN, RIGHT * 0.6, color=YELLOW, stroke_width=7)
            clk = VGroup(clock, hand1, hand2).shift(LEFT * 2.5)
            txt = VGroup(Text("7 : 00 → 23 : 00", font_size=44, color=YELLOW), zh("“7-11 院士”", 34)).arrange(DOWN, buff=0.4).shift(RIGHT * 2.3)
            self.play(FadeIn(clk))
            self.play(Rotate(hand1, -TAU * 2, about_point=clock.get_center()), run_time=2)
            self.play(FadeIn(txt))
            self.g = VGroup(clk, txt)

        with self.voice("xue_6"):
            self.play(FadeOut(self.g))
            a = Rectangle(width=6, height=0.6, fill_color=BLUE_D, fill_opacity=0.8, stroke_width=0)
            b = Rectangle(width=6, height=0.25, fill_color=GOLD_E, fill_opacity=0.9, stroke_width=0).next_to(a, UP, buff=0)
            la = zh("钛酸锶衬底", 22).move_to(a)
            lb = zh("单层铁硒", 20, GOLD).next_to(b, UP, buff=0.15)
            g = VGroup(a, b, la, lb).shift(DOWN * 0.3)
            t = zh("界面增强的高温超导（2012）", 30, YELLOW).next_to(g, UP, buff=0.8)
            self.play(FadeIn(a), FadeIn(la))
            self.play(FadeIn(b, shift=DOWN * 0.3), FadeIn(lb))
            self.play(Write(t))
            self.g = VGroup(g, t)

        with self.voice("xue_7"):
            self.play(FadeOut(self.g))
            aw = ["首届未来科学大奖 · 物质科学奖（2016）", "国家自然科学一等奖", "菲列兹·伦敦奖（国际低温物理）",
                  "巴克利奖（美国物理学会）", "国家最高科学技术奖（2024）"]
            rows = VGroup(*[VGroup(Text("★", font_size=28, color=GOLD), zh(x, 28)).arrange(RIGHT, buff=0.3) for x in aw])
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(DOWN * 0.2)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4), run_time=4)
        self.clear()

    def _add(self, year, text):
        row = VGroup(Text(year, font_size=26, color=BLUE_B), zh(text, 26)).arrange(RIGHT, buff=0.4)
        if len(self.items):
            row.next_to(self.items[-1], DOWN, buff=0.2).align_to(self.items[0], LEFT)
        else:
            row.move_to(LEFT * 3.2 + UP * 2.6, aligned_edge=LEFT)
        self.items.add(row)
        self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.6)


# ====================================================================== 13 对物理学的影响
class S13_Physics(VoiceScene):
    def construct(self):
        with self.voice("phy_1"):
            grid = VGroup(*[VGroup(token_box(n, c, 30), zh(y, 22, GREY_B)).arrange(DOWN, buff=0.2) for n, c, y in [
                ("霍尔效应", BLUE_D, "1879"), ("反常霍尔效应", TEAL_D, "1880"),
                ("量子霍尔效应", PURPLE_D, "1980"), ("量子反常霍尔效应", GOLD_E, "2013")]]).arrange_in_grid(2, 2, buff=(1.5, 0.9))
            hdr = zh("霍尔效应家族", 34, YELLOW).to_edge(UP, buff=0.6)
            self.play(Write(hdr))
            self.play(LaggedStart(*[FadeIn(g) for g in grid[:3]], lag_ratio=0.4))
            self.play(FadeIn(grid[3], scale=1.3))
            self.play(Circumscribe(grid[3], color=YELLOW))

        with self.voice("phy_2"):
            self.clear(run_time=0.5)
            a = VGroup(zh("强磁场下的特殊现象", 30, GREY_B)).shift(UP * 0.8)
            arr = Arrow(UP * 0.4, DOWN * 0.4, color=YELLOW)
            b = zh("材料本身的内禀拓扑性质", 34, YELLOW).shift(DOWN * 0.8)
            h = zh("证实了霍尔丹 1988 年的设想", 26).to_edge(DOWN, buff=0.8)
            self.play(FadeIn(a))
            self.play(GrowArrow(arr), Write(b))
            self.play(FadeIn(h))

        with self.voice("phy_3"):
            self.clear(run_time=0.5)
            tl = numline(2013, 2025, 2, 11, 22).shift(DOWN * 0.3)
            self.play(Create(tl))
            self.tl = tl
            self._ev(2013, "首次实现 · 约 30 mK", YELLOW, 1)
            self._ev(2015, "改进掺杂 · 1–2 K", TEAL, -1)
            self._ev(2020, "本征磁性拓扑绝缘体锰铋碲（复旦）", GREEN_C, 1)

        with self.voice("phy_4"):
            self._ev(2019.5, "转角石墨烯", BLUE_C, -1)
            self._ev(2023, "分数量子反常霍尔：二碲化钼", ORANGE, 1.8)
            self._ev(2024, "多层石墨烯", PINK, -1.8)
        self.clear()

    def _ev(self, year, text, color, side):
        d = Dot(self.tl.n2p(year), color=color, radius=0.1)
        lab = zh(text, 20, color).next_to(d, UP if side > 0 else DOWN, buff=0.3 + 0.5 * (abs(side) - 1))
        ln = Line(d.get_center(), lab.get_bottom() if side > 0 else lab.get_top(), color=color, stroke_width=1.5)
        self.play(FadeIn(d, scale=2), Create(ln), FadeIn(lab), run_time=0.8)
        self.wait(0.6)


# ====================================================================== 14 对世界的影响
class S14_World(VoiceScene):
    def construct(self):
        with self.voice("wld_1"):
            t = zh("前景一：低能耗电子器件", 32, YELLOW).to_edge(UP, buff=0.6)
            chip = VGroup(Square(2.4, fill_color=GREY_E, fill_opacity=1, stroke_color=GREY_B),
                          *[Line(ORIGIN, RIGHT * 0.4, color=GREY_B).move_to(np.array([1.4, y, 0])) for y in np.linspace(-0.9, 0.9, 5)],
                          *[Line(ORIGIN, RIGHT * 0.4, color=GREY_B).move_to(np.array([-1.4, y, 0])) for y in np.linspace(-0.9, 0.9, 5)])
            heat = VGroup(*[Arc(radius=0.4 + 0.25 * k, start_angle=PI / 4, angle=PI / 2, color=RED_C).move_to(UP * (1.6 + 0.25 * k))
                            for k in range(3)])
            self.play(Write(t), FadeIn(chip), FadeIn(heat))
            self.play(FadeOut(heat), chip[0].animate.set_stroke(YELLOW, 4))
            n = zh("边缘通道几乎无损耗 → 若能在更高温度实现，可大幅降低发热", 24).to_edge(DOWN, buff=0.8)
            self.play(FadeIn(n))

        with self.voice("wld_2"):
            self.clear(run_time=0.5)
            t = zh("影响二：计量学", 32, YELLOW).to_edge(UP, buff=0.6)
            a = VGroup(zh("传统量子电阻标准", 24, GREY_B), zh("需要强磁场", 26, BAD)).arrange(DOWN, buff=0.2)
            b = VGroup(zh("量子反常霍尔电阻标准（2024）", 24, GREY_B), zh("零外磁场 · 10⁻⁹ 精度", 26, OK)).arrange(DOWN, buff=0.2)
            VGroup(a, b).arrange(RIGHT, buff=1.5)
            arr = Arrow(a.get_right(), b.get_left(), color=WHITE)
            self.play(Write(t), FadeIn(a))
            self.play(GrowArrow(arr), FadeIn(b))
            src = zh("德国联邦物理技术研究院（PTB）等", 20, GREY_B).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(src))

        with self.voice("wld_3"):
            self.clear(run_time=0.5)
            cryo = RoundedRectangle(corner_radius=0.4, width=6, height=3.4, stroke_color=BLUE_B).shift(DOWN * 0.2)
            cl = zh("同一台低温设备", 24, BLUE_B).next_to(cryo, UP, buff=0.2)
            r = token_box("电阻标准（QAH）", GOLD_E, 26)
            v = token_box("电压标准（约瑟夫森）", TEAL_D, 26)
            VGroup(r, v).arrange(DOWN, buff=0.5).move_to(cryo)
            self.play(Create(cryo), FadeIn(cl))
            self.play(FadeIn(r), FadeIn(v))
            nn = zh("都不需要磁场 → 更简单、更便携", 26, OK).to_edge(DOWN, buff=0.5)
            self.play(Write(nn))

        with self.voice("wld_4"):
            self.clear(run_time=0.5)
            t = zh("前景三：拓扑量子计算", 32, YELLOW).to_edge(UP, buff=0.6)
            a = token_box("量子反常霍尔材料", GOLD_E, 28)
            b = token_box("超导体", BLUE_D, 28)
            c = token_box("更抗干扰的量子比特？", PURPLE_D, 28)
            g = VGroup(a, Text("+", font_size=48), b, Arrow(ORIGIN, RIGHT, color=WHITE), c).arrange(RIGHT, buff=0.35)
            if g.width > 13:
                g.scale_to_fit_width(13)
            s = zh("仍在探索之中", 24, GREY_B).next_to(g, DOWN, buff=0.6)
            self.play(Write(t))
            self.play(FadeIn(g, lag_ratio=0.2), run_time=2)
            self.play(FadeIn(s))
        self.clear()


# ====================================================================== 15 挑战
class S15_Challenge(VoiceScene):
    def construct(self):
        with self.voice("chl_1"):
            t = zh("温度：最大的挑战", 34, YELLOW).to_edge(UP, buff=0.6)
            ax = NumberLine(x_range=[-2, 3, 1], length=11, color=GREY_B).shift(DOWN * 0.5)
            ticks = VGroup(*[Text(l, font_size=22, color=GREY_B).next_to(ax.n2p(k), DOWN, buff=0.2)
                             for k, l in zip(range(-2, 4), ["0.01 K", "0.1 K", "1 K", "10 K", "100 K", "1000 K"])])
            self.play(Write(t), Create(ax), FadeIn(ticks))
            pts = [(np.log10(0.03), "2013：约 30 mK", YELLOW, 1), (np.log10(1.5), "目前：约 1–2 K", TEAL, 1),
                   (np.log10(300), "室温 300 K", BAD, 1)]
            for x, lab, col, s in pts:
                d = Dot(ax.n2p(x), color=col, radius=0.12)
                l = zh(lab, 22, col).next_to(d, UP, buff=0.4)
                self.play(FadeIn(d, scale=2), FadeIn(l), run_time=0.8)
            gap = DoubleArrow(ax.n2p(np.log10(1.5)) + UP * 1.4, ax.n2p(np.log10(300)) + UP * 1.4, color=BAD, buff=0)
            gl = zh("还有很长的路", 24, BAD).next_to(gap, UP, buff=0.1)
            self.play(GrowFromCenter(gap), FadeIn(gl))
            self.add(note("（对数坐标）"))

        with self.voice("chl_2"):
            self.clear(run_time=0.5)
            need = VGroup(token_box("更强的磁性", RED_E, 28), token_box("更大的能隙", TEAL_D, 28), token_box("更少的缺陷", BLUE_D, 28)).arrange(RIGHT, buff=0.6)
            how = zh("理论预言 × 材料生长 × 精密测量", 30, YELLOW).next_to(need, DOWN, buff=0.9)
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in need], lag_ratio=0.3))
            self.play(Write(how))
        self.clear()


# ====================================================================== 16 结尾
class S16_Outro(VoiceScene):
    def construct(self):
        with self.voice("out_1"):
            ev = [("1879", "霍尔效应"), ("1880", "反常霍尔效应"), ("1980", "量子霍尔效应"), ("1988", "霍尔丹模型"),
                  ("2010", "材料配方"), ("2013", "量子反常霍尔效应实验实现")]
            rows = VGroup(*[VGroup(Text(y, font_size=32, color=BLUE_B if y != "2013" else YELLOW),
                                   zh(d, 28, YELLOW if y == "2013" else WHITE)).arrange(RIGHT, buff=0.5) for y, d in ev])
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(0.8)
            self.rows = rows

        with self.voice("out_2"):
            self.play(self.rows.animate.set_opacity(0.3))
            m = zh("从一个偏转现象，到理解物质拓扑本质的窗口", 30, YELLOW)
            bg = BackgroundRectangle(m, fill_opacity=0.9, buff=0.3)
            self.play(FadeIn(bg), Write(m))

        with self.voice("out_3"):
            self.clear(run_time=0.5)
            a = zh("执着追问基础问题", 34)
            b = zh("一千多个样品背后的坚持", 34, YELLOW)
            c = zh("感谢收看", 40)
            VGroup(a, b, c).arrange(DOWN, buff=0.6)
            self.play(FadeIn(a))
            self.play(FadeIn(b))
            self.play(FadeIn(c, shift=UP * 0.2))
        self.clear()
