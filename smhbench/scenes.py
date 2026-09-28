"""《SMH-Bench》3Blue1Brown 风格中文讲解 —— Manim 场景。

渲染单个场景:  manim -qm smhbench/scenes.py S03_HomeEnv
整片构建:      python build.py all --paper smhbench
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


def mono(text: str, size: float = 24, color=WHITE) -> Text:
    return Text(text, font="DejaVu Sans Mono", font_size=size, color=color)


def device(name: str, on: bool = False, color=BLUE_D, size: float = 22) -> VGroup:
    """一个设备小卡片：名字 + 右上角状态灯。"""
    card = token_box(name, color, size, pad=0.14)
    lamp = Dot(radius=0.07, color=ON if on else OFF).move_to(card[0].get_corner(UR) + DL * 0.12)
    g = VGroup(card, lamp)
    g.lamp = lamp
    return g


def set_lamp(dev: VGroup, on: bool):
    return dev.lamp.animate.set_color(ON if on else OFF)


def room(name: str, w: float, h: float, color=GREY_B) -> VGroup:
    box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2)
    label = zh(name, 22, color).next_to(box.get_corner(UL), DR, buff=0.1)
    return VGroup(box, label)


def check(color=OK) -> Text:
    return Text("✔", font_size=34, color=color)


def cross(color=BAD) -> Text:
    return Text("✘", font_size=34, color=color)


# ====================================================================== 1 开场
class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("intro_1"):
            bubble = RoundedRectangle(corner_radius=0.3, width=5.4, height=1.2,
                                      stroke_color=WHITE, fill_color=GREY_E, fill_opacity=0.6)
            say = zh("“我要看电影了。”", 40).move_to(bubble)
            spk = VGroup(Circle(0.45, color=BLUE_C, fill_opacity=0.3),
                         zh("音箱", 20).shift(DOWN * 0.8))
            spk.next_to(bubble, LEFT, buff=0.6)
            grp = VGroup(spk, bubble, say).move_to(UP * 0.3)
            self.play(FadeIn(spk, shift=RIGHT * 0.3))
            self.play(GrowFromCenter(bubble), Write(say), run_time=1.5)
            q = Text("?", font_size=90, color=YELLOW).next_to(grp, DOWN, buff=0.5)
            self.play(FadeIn(q, scale=0.5))

        with self.voice("intro_2"):
            self.play(FadeOut(q), grp.animate.scale(0.6).to_edge(UP, buff=0.4))
            living = room("客厅", 6.2, 3.6).shift(LEFT * 2.8 + DOWN * 0.9)
            bed = room("卧室", 3.6, 3.6).shift(RIGHT * 2.3 + DOWN * 0.9)
            pos = living[0].get_center()
            lamps = VGroup(device("主灯", True), device("氛围灯", True), device("电视"),
                           device("窗帘", True, TEAL_D)).arrange_in_grid(2, 2, buff=0.45).move_to(pos)
            bed_dev = VGroup(device("床头灯"), device("空调", True, TEAL_D)).arrange(DOWN, buff=0.4)
            bed_dev.move_to(bed[0])
            you = VGroup(Dot(color=YELLOW, radius=0.12), zh("你", 20, YELLOW)).arrange(RIGHT, buff=0.1)
            you.move_to(living[0].get_corner(DR) + UL * 0.4)
            self.play(Create(living), Create(bed), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(d, scale=0.8) for d in [*lamps, *bed_dev]], lag_ratio=0.15))
            self.play(FadeIn(you, scale=0.5))
            pref = zh("记忆中的偏好：看电影时灯光调到 20%", 24, YELLOW).next_to(VGroup(living, bed), DOWN, buff=0.25)
            self.play(Write(pref))
            self.play(set_lamp(lamps[0], False), set_lamp(lamps[2], True), set_lamp(lamps[3], False),
                      lamps[1][0][0].animate.set_fill(opacity=0.08), run_time=1.5)
            self.house = VGroup(living, bed, lamps, bed_dev, you, pref)

        with self.voice("intro_3"):
            self.play(FadeOut(self.house), FadeOut(grp))
            title = Text("SMH-Bench", font_size=80, weight=BOLD, color=BLUE_B)
            sub = Text("Benchmarking LLM Agents for Environment-Grounded\nReasoning and Action in Smart Homes",
                       font_size=26, color=GREY_B, line_spacing=0.8)
            meta = Text("Kuan Li et al.  ·  arXiv:2606.01912  ·  2026.06", font_size=22, color=GREY_B)
            head = VGroup(title, sub, meta).arrange(DOWN, buff=0.35).shift(UP * 0.6)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(meta, shift=UP * 0.2))
            ask = zh("大模型能否在真实、复杂、有状态的家里可靠地推理和行动？", 30, YELLOW)
            ask.next_to(head, DOWN, buff=0.7)
            self.play(Write(ask), run_time=2)
        self.clear()


# ====================================================================== 2 问题
class S02_Problem(VoiceScene):
    def construct(self):
        with self.voice("prob_1"):
            inst = zh("“关掉卧室的灯”", 32)
            api = mono('light.turn_off(\n  entity="bedroom")', 24, BLUE_B)
            gold = mono('light.turn_off(\n  entity="bedroom")', 24, GREEN_B)
            row = VGroup(inst, api, gold).arrange(RIGHT, buff=1.3).shift(UP * 1.2)
            a1 = Arrow(inst.get_right(), api.get_left(), buff=0.15, color=GREY_B)
            eq = Text("=?", font_size=36, color=YELLOW).move_to((api.get_right() + gold.get_left()) / 2)
            labels = VGroup(zh("指令", 22, GREY_B).next_to(inst, UP),
                            zh("模型输出", 22, GREY_B).next_to(api, UP),
                            zh("标准答案", 22, GREY_B).next_to(gold, UP))
            self.play(FadeIn(inst), FadeIn(labels[0]))
            self.play(GrowArrow(a1), Write(api), FadeIn(labels[1]))
            self.play(Write(gold), FadeIn(labels[2]), FadeIn(eq))
            self.play(Circumscribe(VGroup(api, gold), color=YELLOW))
            self.top = VGroup(inst, api, gold, a1, eq, labels)

        with self.voice("prob_2"):
            alt = VGroup(
                mono('light.turn_off("bed_1")\nlight.turn_off("bed_2")', 20, BLUE_B),
                mono('scene.activate("sleep")', 20, BLUE_B),
            ).arrange(RIGHT, buff=0.6).shift(DOWN * 0.6).to_edge(LEFT, buff=0.4)
            marks = VGroup(*[check().next_to(a, DOWN) for a in alt])
            verdict = VGroup(*[cross().next_to(m, RIGHT, buff=0.15) for m in marks])
            note = zh("都正确，但字面对不上", 22, GREY_B).next_to(alt, DOWN, buff=0.9)
            self.play(FadeIn(alt, shift=UP * 0.2))
            self.play(FadeIn(marks), FadeIn(verdict), Write(note))
            bad = mono('light.turn_off(\n  entity="bedroom")', 20, BLUE_B).shift(DOWN * 0.6).to_edge(RIGHT, buff=0.5)
            boom = zh("实际执行：该实体不存在", 22, BAD).next_to(bad, DOWN, buff=0.35)
            self.play(FadeIn(bad))
            self.play(Write(boom), Wiggle(bad))
            self.mid = VGroup(alt, marks, verdict, note, bad, boom)

        with self.voice("prob_3"):
            self.play(FadeOut(self.top), FadeOut(self.mid))
            r = room("卧室", 7, 3.4).shift(UP * 0.3)
            lamps = VGroup(device("吸顶灯", True), device("床头灯 A", True),
                           device("床头灯 B", False)).arrange(RIGHT, buff=0.8).move_to(r[0])
            self.play(Create(r), LaggedStart(*[FadeIn(d) for d in lamps], lag_ratio=0.2))
            state = zh("当前状态决定了正确答案", 28, YELLOW).next_to(r, DOWN, buff=0.4)
            self.play(Indicate(lamps[2], color=GREY_B))
            self.play(set_lamp(lamps[0], False), set_lamp(lamps[1], False), run_time=1.2)
            self.play(Write(state))
            self.bedroom = VGroup(r, lamps, state)

        with self.voice("prob_4"):
            self.play(self.bedroom.animate.scale(0.55).to_edge(LEFT, buff=0.5))
            old = zh("比对文字", 34, GREY_B)
            new = zh("执行 → 检查状态", 34, YELLOW)
            pair = VGroup(old, new).arrange(DOWN, buff=1.0).shift(RIGHT * 2.8)
            strike = Line(old.get_left(), old.get_right(), color=BAD, stroke_width=5)
            arr = Arrow(old.get_bottom(), new.get_top(), buff=0.15, color=WHITE)
            self.play(FadeIn(old))
            self.play(Create(strike))
            self.play(GrowArrow(arr), Write(new))
            self.play(Circumscribe(new, color=YELLOW))
        self.clear()


# ====================================================================== 3 HomeEnv
class S03_HomeEnv(VoiceScene):
    def construct(self):
        with self.voice("env_1"):
            title = Text("HomeEnv", font_size=72, weight=BOLD, color=BLUE_B)
            tags = VGroup(zh("可执行", 30, OK), zh("可验证", 30, OK)).arrange(RIGHT, buff=1)
            VGroup(title, tags).arrange(DOWN, buff=0.5)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tags], lag_ratio=0.4))
            self.head = VGroup(title, tags)

        with self.voice("env_2"):
            self.play(self.head.animate.scale(0.5).to_corner(UL))
            home = token_box("家", YELLOW, 30).shift(UP * 2.3)
            rooms = VGroup(token_box("客厅", BLUE_D, 24), token_box("卧室", BLUE_D, 24),
                           token_box("厨房", BLUE_D, 24)).arrange(RIGHT, buff=2.4).shift(UP * 0.8)
            devs = VGroup(token_box("灯", TEAL_D, 22), token_box("电视", TEAL_D, 22),
                          token_box("空调", TEAL_D, 22), token_box("窗帘", TEAL_D, 22),
                          token_box("冰箱", TEAL_D, 22)).arrange(RIGHT, buff=0.75).shift(DOWN * 0.7)
            parent = [0, 0, 1, 1, 2]
            e1 = VGroup(*[Line(home.get_bottom(), r.get_top(), color=GREY_B) for r in rooms])
            e2 = VGroup(*[Line(rooms[p].get_bottom(), d.get_top(), color=GREY_B) for p, d in zip(parent, devs)])
            self.play(FadeIn(home))
            self.play(Create(e1), LaggedStart(*[FadeIn(r) for r in rooms], lag_ratio=0.2))
            self.play(Create(e2), LaggedStart(*[FadeIn(d) for d in devs], lag_ratio=0.15))
            svc = VGroup(mono("turn_on / turn_off", 20, GREY_A),
                         mono("set_brightness(0-100)", 20, GREY_A),
                         mono("state: on, brightness=80", 20, YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            svc_box = SurroundingRectangle(svc, color=TEAL, buff=0.2)
            card = VGroup(svc_box, svc).next_to(devs[0], DOWN, buff=0.5).align_to(devs[0], LEFT)
            link = Line(devs[0].get_bottom(), svc_box.get_top(), color=TEAL)
            self.play(Create(link), FadeIn(card, shift=DOWN * 0.2))
            self.tree = VGroup(home, rooms, devs, e1, e2, card, link)

        with self.voice("env_3"):
            self.play(FadeOut(self.tree))
            calls = [
                ('light.turn_on("客厅/灯")', OK, "✔ 状态更新"),
                ('light.turn_on("阳台/灯")', BAD, "✘ 设备不存在"),
                ('tv.set_temperature(24)', BAD, "✘ 服务不支持"),
                ('light.set_brightness(150)', BAD, "✘ 参数越界"),
            ]
            rows = VGroup()
            for code, col, res in calls:
                c = Text(code, font=CJK_MONO, font_size=24, color=BLUE_B)
                r = zh(res, 24, col)
                rows.add(VGroup(c, r))
            for row in rows:
                row[1].next_to(row[0], RIGHT, buff=0.8)
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45).shift(DOWN * 0.2)
            for row in rows:
                row[1].set_x(3.8, LEFT)
            engine = token_box("HomeEnv 执行", YELLOW, 24).next_to(rows, UP, buff=0.6)
            for row in rows:
                self.play(FadeIn(row[0], shift=RIGHT * 0.3), run_time=0.5)
                self.play(FadeIn(row[1], scale=1.3), run_time=0.5)
            self.play(FadeIn(engine))
            self.rows = VGroup(rows, engine)

        with self.voice("env_4"):
            self.play(FadeOut(self.rows))
            col1 = self._verify_card("可执行任务", ["设备存在", "服务可用", "参数合法", "到达目标状态"], OK)
            col2 = self._verify_card("查询任务", ["按当前状态\n重新计算答案"], BLUE_C)
            col3 = self._verify_card("自动化任务", ["触发条件", "执行动作"], ORANGE)
            col4 = self._verify_card("模糊请求", ["是否真的\n需要追问"], PURPLE_B)
            self.cards = VGroup(col1, col2, col3, col4).arrange(RIGHT, buff=0.35, aligned_edge=UP).shift(DOWN * 0.2)
            self.play(FadeIn(col1, shift=UP * 0.3))
            self.play(LaggedStart(*[Write(i) for i in col1[2]], lag_ratio=0.4), run_time=2)
            self.play(FadeIn(col2, shift=UP * 0.3))

        with self.voice("env_5"):
            self.play(FadeIn(col3, shift=UP * 0.3))
            self.play(FadeIn(col4, shift=UP * 0.3))
            self.play(Circumscribe(col4, color=PURPLE_B))
        self.clear()

    def _verify_card(self, name, items, color):
        title = zh(name, 26, color)
        body = VGroup(*[zh("· " + t, 21) for t in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        body.next_to(title, DOWN, buff=0.4)
        frame = RoundedRectangle(corner_radius=0.15, width=3.1, height=4.2, stroke_color=color)
        VGroup(title, body).move_to(frame).align_to(frame, UP).shift(DOWN * 0.3)
        return VGroup(frame, title, body)


CJK_MONO = "DejaVu Sans Mono"


# ====================================================================== 4 基准
CATS = [
    ("单设备控制", BLUE_C, "显式指令"),
    ("状态查询", BLUE_C, "显式指令"),
    ("组合控制", TEAL, "多设备·条件"),
    ("自动化调度", ORANGE, "定时·触发"),
    ("模糊意图", PURPLE_B, "猜还是问"),
    ("多轮上下文", PURPLE_B, "承接对话"),
    ("个性化记忆", PINK, "用户偏好"),
]


class S04_Benchmark(VoiceScene):
    def construct(self):
        with self.voice("bench_1"):
            vt = ValueTracker(0)
            anchor = RIGHT * 0.9 + UP * 0.5
            num = always_redraw(lambda: Text(f"{int(vt.get_value()):,}", font_size=110, color=YELLOW)
                                .move_to(anchor, aligned_edge=RIGHT))
            unit = zh("个任务", 40).next_to(anchor, RIGHT, buff=0.3).shift(DOWN * 0.3)
            self.add(num)
            self.play(FadeIn(unit), vt.animate.set_value(1100), run_time=2.5)
            num.clear_updaters()
            grp = VGroup(num, unit)
            audit = zh("全部人工审核", 30, OK).next_to(grp, DOWN, buff=0.6)
            self.play(FadeIn(audit, shift=UP * 0.2))
            self.head = VGroup(num, unit, audit)

        with self.voice("bench_2"):
            self.play(self.head.animate.scale(0.45).to_corner(UL))
            hdr = zh("7 大类 · 22 个子类", 32, YELLOW).to_edge(UP, buff=0.5)
            self.play(Write(hdr))
            chips = VGroup()
            for name, col, hint in CATS:
                c = token_box(name, col, 26)
                h = zh(hint, 18, GREY_B).next_to(c, DOWN, buff=0.12)
                chips.add(VGroup(c, h))
            chips[:4].arrange(RIGHT, buff=0.5).shift(UP * 0.7)
            chips[4:].arrange(RIGHT, buff=0.5).shift(DOWN * 1.3)
            self.chips = chips
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips[:4]], lag_ratio=0.5), run_time=4)
            self.hdr = hdr

        with self.voice("bench_3"):
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips[4:]], lag_ratio=0.8), run_time=4)
            brace = Line(chips[4:].get_corner(DL), chips[4:].get_corner(DR), color=PURPLE_B)
            brace.shift(DOWN * 0.2)
            txt = zh("读懂人", 26, PURPLE_B).next_to(brace, DOWN)
            self.play(GrowFromCenter(brace), Write(txt))
            self.extra = VGroup(brace, txt)

        with self.voice("bench_4"):
            self.play(FadeOut(self.chips), FadeOut(self.extra))
            variants = VGroup(zh("“把客厅灯关了”", 28), zh("“客厅太亮了，关一下吧”", 28),
                              zh("“帮我熄掉客厅那盏灯”", 28)).arrange(DOWN, buff=0.4).shift(LEFT * 2)
            tgt = token_box("客厅灯 → off", YELLOW, 26).shift(RIGHT * 3.5)
            arrows = VGroup(*[Arrow(v.get_right(), tgt.get_left(), buff=0.2, color=GREY_B) for v in variants])
            self.play(LaggedStart(*[FadeIn(v, shift=RIGHT * 0.2) for v in variants], lag_ratio=0.3))
            self.play(FadeIn(tgt), LaggedStart(*map(GrowArrow, arrows)))
            lbl = zh("语言鲁棒性", 26, TEAL).next_to(variants, UP, buff=0.4)
            self.play(Write(lbl))
            self.ling = VGroup(variants, tgt, arrows, lbl)

        with self.voice("bench_5"):
            self.play(FadeOut(self.ling))
            tiers = VGroup(
                self._home(2, 2, "简单", "小公寓"),
                self._home(3, 3, "中等", "多房间"),
                self._home(5, 4, "复杂", "嵌套房间 · 最多 135 台设备"),
            ).arrange(RIGHT, buff=0.7, aligned_edge=DOWN).shift(DOWN * 0.3)
            for t in tiers:
                self.play(FadeIn(t[0]), LaggedStart(*[FadeIn(d, scale=0.5) for d in t[1]], lag_ratio=0.02),
                          FadeIn(t[2]), run_time=1.2)
        self.clear()

    def _home(self, cols, rows, name, desc):
        cell = 0.75 if cols < 5 else 0.62
        grid = VGroup(*[Square(cell, stroke_color=GREY_B, stroke_width=1.5)
                        for _ in range(cols * rows)]).arrange_in_grid(rows, cols, buff=0)
        rng = np.random.default_rng(cols * 7 + rows)
        per = 1 if cols == 2 else 2 if cols == 3 else 5
        dots = VGroup()
        for sq in grid:
            for _ in range(per):
                off = (rng.random(2) - 0.5) * cell * 0.7
                dots.add(Dot(sq.get_center() + np.array([off[0], off[1], 0]), radius=0.045,
                             color=ON if rng.random() < 0.4 else TEAL))
        lab = VGroup(zh(name, 28, YELLOW), zh(desc, 20, GREY_B)).arrange(DOWN, buff=0.12)
        lab.next_to(grid, DOWN, buff=0.3)
        return VGroup(grid, dots, lab)


# ====================================================================== 5 两种设置
class S05_Settings(VoiceScene):
    def construct(self):
        with self.voice("set_1"):
            dr = zh("直接推理  DR", 36, DR_COLOR).shift(LEFT * 3.5 + UP * 2.8)
            eia = zh("环境交互智能体  EIA", 36, EIA_COLOR).shift(RIGHT * 3.3 + UP * 2.8)
            div = DashedLine(UP * 3.3, DOWN * 3.5, color=GREY_D)
            self.play(Write(dr), Write(eia), Create(div))

        with self.voice("set_2"):
            state = VGroup(zh("完整状态摘要", 22), mono("客厅: 灯 on 80%\n卧室: 空调 off\n…", 18, GREY_A))
            state.arrange(DOWN, buff=0.15)
            sbox = SurroundingRectangle(state, color=DR_COLOR, buff=0.15)
            query = token_box("用户请求", BLUE_D, 22)
            ins = VGroup(VGroup(sbox, state), query).arrange(DOWN, buff=0.3).move_to(LEFT * 5 + DOWN * 0.3)
            llm = token_box("LLM", YELLOW, 32).move_to(LEFT * 3.1 + DOWN * 0.3)
            outs = VGroup(zh("动作序列", 20), zh("自动化规则", 20), zh("回复", 20)).arrange(DOWN, buff=0.3)
            outs.move_to(LEFT * 1.2 + DOWN * 0.3)
            a1 = Arrow(ins.get_right(), llm.get_left(), buff=0.1, color=GREY_B)
            a2 = Arrow(llm.get_right(), outs.get_left(), buff=0.1, color=GREY_B)
            self.play(FadeIn(ins, shift=RIGHT * 0.2))
            self.play(GrowArrow(a1), FadeIn(llm))
            self.play(GrowArrow(a2), LaggedStart(*[FadeIn(o) for o in outs], lag_ratio=0.3))
            once = zh("一步到位", 24, DR_COLOR).next_to(llm, DOWN, buff=1.4)
            self.play(Write(once))

        with self.voice("set_3"):
            center = RIGHT * 3.3 + DOWN * 0.4
            names = ["思考", "行动", "观察"]
            cols = [YELLOW, EIA_COLOR, TEAL]
            angs = [PI / 2, PI / 2 - 2 * PI / 3, PI / 2 + 2 * PI / 3]
            nodes = VGroup(*[token_box(n, c, 26).move_to(center + 1.5 * np.array([np.cos(a), np.sin(a), 0]))
                             for n, c, a in zip(names, cols, angs)])
            arcs = VGroup(*[CurvedArrow(nodes[i].get_center(), nodes[(i + 1) % 3].get_center(),
                                        angle=-TAU / 5, color=GREY_B, tip_length=0.2)
                            for i in range(3)])
            for a in arcs:
                a.scale(0.55)
            self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.3))
            self.play(Create(arcs))
            react = Text("ReAct", font_size=30, color=GREY_A).move_to(center)
            self.play(FadeIn(react))
            self.loop = VGroup(nodes, arcs, react)
            orbit = Circle(radius=1.5).move_to(center).rotate(PI / 2).flip(UP)
            runner = Dot(color=YELLOW, radius=0.1).move_to(orbit.point_from_proportion(0))
            self.play(MoveAlongPath(runner, orbit), run_time=2, rate_func=linear)
            self.play(FadeOut(runner))

        with self.voice("set_4"):
            self.play(self.loop.animate.scale(0.6).move_to(RIGHT * 5.6 + UP * 1.5))
            fog = VGroup(*[Square(0.9, stroke_width=1, stroke_color=GREY_D, fill_color=GREY_E,
                                  fill_opacity=0.9) for _ in range(12)]).arrange_in_grid(3, 4, buff=0.05)
            fog.move_to(RIGHT * 2.8 + DOWN * 1.2)
            vis = zh("只知道：房间 + 设备列表", 22, EIA_COLOR).next_to(fog, UP, buff=0.3)
            self.play(FadeIn(fog), Write(vis))
            probe = mono("get_state(...)", 20, EIA_COLOR).next_to(fog, DOWN, buff=0.25)
            self.play(FadeIn(probe))
            for i in [5, 6, 1, 10]:
                self.play(fog[i].animate.set_fill(opacity=0.0).set_stroke(TEAL, 2), run_time=0.45)
            po = zh("局部可观测", 26, YELLOW).next_to(probe, RIGHT, buff=0.5)
            self.play(Write(po))
        self.clear()


# ====================================================================== 6 结果
class S06_Results(VoiceScene):
    # 仅为示意趋势的相对高度，非论文数值
    SHAPE = [0.88, 0.84, 0.7, 0.45, 0.4, 0.55, 0.36]

    def construct(self):
        with self.voice("res_1"):
            n = VGroup(Text("13", font_size=110, color=YELLOW), zh("个大语言模型", 40)).arrange(RIGHT, buff=0.3)
            s = zh("× DR / EIA 两种设置", 30, GREY_B).next_to(n, DOWN, buff=0.4)
            self.play(Write(n))
            self.play(FadeIn(s))
            self.head = VGroup(n, s)

        with self.voice("res_2"):
            self.play(FadeOut(self.head))
            axis = Line(LEFT * 6 + DOWN * 2.2, RIGHT * 6 + DOWN * 2.2, color=GREY_B)
            bars, labels = VGroup(), VGroup()
            xs = np.linspace(-5.1, 5.1, len(CATS))
            for x, (name, col, _), v in zip(xs, CATS, self.SHAPE):
                b = Rectangle(width=1.0, height=4.2 * v, fill_color=col, fill_opacity=0.8, stroke_width=0)
                b.move_to([x, -2.2 + 2.1 * v, 0])
                bars.add(b)
                labels.add(zh(name, 20).next_to(axis, DOWN, buff=0.2).set_x(x))
            tag = zh("示意，非论文数值", 20, GREY_B).to_corner(UR)
            self.play(Create(axis), FadeIn(labels), FadeIn(tag))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars[:2]], lag_ratio=0.3))
            good = zh("表现不错", 26, OK).next_to(bars[:2], UP, buff=0.3)
            self.play(Write(good))
            self.bars, self.labels, self.axis, self.tag, self.good = bars, labels, axis, tag, good

        with self.voice("res_3"):
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in self.bars[2:]], lag_ratio=0.3), run_time=3)
            weak = VGroup(self.bars[3], self.bars[4], self.bars[6])
            self.play(*[Indicate(b, color=BAD, scale_factor=1.05) for b in weak])
            dip = zh("明显下滑", 26, BAD).next_to(self.bars[4], UP, buff=1.2)
            self.play(Write(dip))
            self.play(Circumscribe(self.tag, color=YELLOW))

        with self.voice("res_4"):
            self.clear(run_time=0.6)
            ax = Axes(x_range=[0, 3, 1], y_range=[0, 1, 0.25], x_length=7, y_length=4,
                      axis_config={"color": GREY_B, "include_ticks": False}).shift(DOWN * 0.3)
            xl = VGroup(*[zh(t, 22).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.3)
                          for i, t in enumerate(["简单", "中等", "复杂"])])
            yl = zh("成功率（示意）", 22, GREY_B).next_to(ax, UP, buff=0.2).align_to(ax, LEFT)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            pts = [ax.c2p(0.5, 0.82), ax.c2p(1.5, 0.66), ax.c2p(2.5, 0.42)]
            line = VMobject(color=YELLOW, stroke_width=5).set_points_smoothly(pts)
            dots = VGroup(*[Dot(p, color=YELLOW) for p in pts])
            self.play(Create(line), LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.5), run_time=2.5)
            note = zh("设备越多，越容易认错设备、读错状态", 24, BAD).next_to(ax, DOWN, buff=0.9)
            self.play(Write(note))
        self.clear()


# ====================================================================== 7 错误分析
class S07_Errors(VoiceScene):
    def construct(self):
        with self.voice("err_1"):
            t = zh("错误画像", 44, YELLOW).to_edge(UP, buff=0.5)
            dr = zh("DR", 36, DR_COLOR).shift(LEFT * 3.5 + UP * 1.8)
            eia = zh("EIA", 36, EIA_COLOR).shift(RIGHT * 3.5 + UP * 1.8)
            div = DashedLine(UP * 2.3, DOWN * 3.5, color=GREY_D)
            self.play(Write(t))
            self.play(FadeIn(dr), FadeIn(eia), Create(div))

        with self.voice("err_2"):
            ie = token_box("IE · 指令执行错误", EIA_COLOR, 24).shift(RIGHT * 3.5 + UP * 0.8)
            self.play(FadeIn(ie, scale=1.2))
            calls = VGroup(*[mono(c, 18, GREY_A) for c in
                             ["list_devices()", "get_state(灯)", "list_devices()", "get_state(灯)",
                              "set(brightness=卧室?)"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            calls.next_to(ie, DOWN, buff=0.35)
            calls[-1].set_color(BAD)
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.1) for c in calls[:4]], lag_ratio=0.5), run_time=2.5)
            rep = zh("冗余调用", 20, BAD).next_to(calls[:4], LEFT, buff=0.3)
            self.play(FadeIn(rep))
            self.play(FadeIn(calls[4]))
            mix = zh("参数边界混淆", 20, BAD).next_to(calls[4], LEFT, buff=0.3)
            self.play(FadeIn(mix))

        with self.voice("err_3"):
            ms = token_box("MS · 信息缺失", DR_COLOR, 24)
            av = token_box("AV · 动作校验", DR_COLOR, 24)
            VGroup(ms, av).arrange(DOWN, buff=0.35).move_to(LEFT * 3.5 + UP * 0.4)
            self.play(FadeIn(ms, scale=1.2), FadeIn(av, scale=1.2))
            jump = zh("信息不足就直接执行", 22, BAD).next_to(av, DOWN, buff=0.5)
            bolt = Arrow(jump.get_bottom() + DOWN * 0.1, jump.get_bottom() + DOWN * 1.1, color=BAD)
            act = mono("turn_off(all)", 20, BAD).next_to(bolt, DOWN, buff=0.1)
            self.play(Write(jump), GrowArrow(bolt), FadeIn(act))

        with self.voice("err_4"):
            self.clear(run_time=0.6)
            l = zh("能查的：查个没完", 32, EIA_COLOR)
            r = zh("不能查的：想当然", 32, DR_COLOR)
            VGroup(l, r).arrange(DOWN, buff=0.6).shift(UP * 0.8)
            self.play(FadeIn(l, shift=RIGHT * 0.3))
            self.play(FadeIn(r, shift=RIGHT * 0.3))
            key = zh("知道自己什么时候“还不知道”", 36, YELLOW).shift(DOWN * 1.6)
            self.play(Write(key), run_time=1.8)
            self.play(Circumscribe(key, color=YELLOW))
        self.clear()


# ====================================================================== 8 结尾
class S08_Outro(VoiceScene):
    def construct(self):
        with self.voice("out_1"):
            t = zh("下一代智能家居助手需要…", 40, YELLOW).to_edge(UP, buff=0.7)
            self.play(Write(t))
            self.t = t

        with self.voice("out_2"):
            items = [("状态落地", BLUE_C), ("澄清策略", PURPLE_B), ("偏好感知推理", PINK), ("规范的工具调用", TEAL)]
            cards = VGroup()
            for i, (name, col) in enumerate(items):
                num = Text(f"{i + 1}", font_size=56, color=col)
                txt = zh(name, 40)
                cards.add(VGroup(num, txt).arrange(RIGHT, buff=0.4))
            cards.arrange_in_grid(2, 2, buff=(1.8, 1.1), col_alignments="ll").shift(DOWN * 0.4)
            for c in cards:
                self.play(FadeIn(c, shift=UP * 0.2), run_time=0.8)
                self.wait(1.0)
            self.cards = cards

        with self.voice("out_3"):
            self.play(FadeOut(self.cards), FadeOut(self.t))
            a = zh("说得对不对", 44, GREY_B).shift(LEFT * 3)
            b = zh("做得成不成", 44, YELLOW).shift(RIGHT * 3)
            arr = Arrow(a.get_right(), b.get_left(), buff=0.3, color=WHITE)
            self.play(FadeIn(a))
            self.play(GrowArrow(arr), Write(b))
            self.play(Circumscribe(b, color=YELLOW))

        with self.voice("out_4"):
            self.clear(run_time=0.6)
            ref = VGroup(Text("SMH-Bench", font_size=60, weight=BOLD, color=BLUE_B),
                         Text("arXiv:2606.01912", font_size=32, color=GREY_B),
                         zh("感谢收看", 40)).arrange(DOWN, buff=0.45)
            self.play(Write(ref[0]), FadeIn(ref[1]))
            self.play(FadeIn(ref[2], shift=UP * 0.2))
        self.clear()
