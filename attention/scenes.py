"""《Attention Is All You Need》3Blue1Brown 风格中文讲解 —— Manim 场景。

渲染单个场景:  manim -qm attention/scenes.py S04_QKV
整片构建:      python build.py all
"""

from __future__ import annotations

import numpy as np
from manim import *  # noqa: F401,F403

from common import (
    CJK_FONT, E_COLOR, K_COLOR, Q_COLOR, V_COLOR, VoiceScene, heat_color,
    softmax, token_box, zh,
)


# ====================================================================== 1 开场
class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("intro_1"):
            title = Tex(r"\textbf{Attention Is All You Need}", font_size=64)
            authors = Tex(
                r"Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin",
                font_size=24, color=GREY_B,
            )
            venue = Tex(r"Google Brain \& Google Research \quad NeurIPS 2017",
                        font_size=24, color=GREY_B)
            head = VGroup(title, authors, venue).arrange(DOWN, buff=0.3).shift(UP * 0.6)
            sub = zh("注意力，就是你所需要的全部", 40, YELLOW).next_to(head, DOWN, buff=0.7)
            self.play(Write(title), run_time=2.5)
            self.play(FadeIn(authors, shift=UP * 0.2), FadeIn(venue, shift=UP * 0.2))
            self.wait(1.5)
            self.play(Write(sub), run_time=1.5)

        with self.voice("intro_2"):
            self.play(FadeOut(authors), FadeOut(venue), FadeOut(sub),
                      head[0].animate.scale(0.6).to_edge(UP))
            models = ["GPT", "BERT", "T5", "LLaMA", "Qwen", "Claude"]
            chips = VGroup(*[token_box(m, BLUE_D, 28) for m in models])
            chips.arrange(RIGHT, buff=0.35).shift(UP * 0.9)
            core = token_box("Transformer", YELLOW, 40).shift(DOWN * 1.5)
            arrows = VGroup(*[Arrow(c.get_bottom(), core.get_top() + RIGHT * (i - 2.5) * 0.3, buff=0.1,
                                    stroke_width=2, color=GREY_B) for i, c in enumerate(chips)])
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in chips],
                                  lag_ratio=0.15))
            self.play(GrowFromCenter(core), LaggedStart(*map(GrowArrow, arrows)))
            gpt = Tex(r"G", r"enerative ", r"P", r"re-trained ", r"T", r"ransformer",
                      font_size=44).shift(DOWN * 3)
            gpt[0].set_color(BLUE_B)
            gpt[2].set_color(BLUE_B)
            gpt[4].set_color(YELLOW)
            gpt[5].set_color(YELLOW)
            self.wait(2)
            self.play(Write(gpt))
            self.play(Indicate(gpt[4], scale_factor=1.6), Indicate(core, scale_factor=1.1))

        with self.voice("intro_3"):
            self.play(FadeOut(chips), FadeOut(arrows), FadeOut(core), FadeOut(gpt))
            items = ["RNN 的瓶颈", "词嵌入", "Query · Key · Value", "缩放点积注意力",
                     "多头注意力", "位置编码", "整体架构", "结果与影响"]
            rows = VGroup(*[
                VGroup(Text(f"{i + 1:02d}", font_size=26, color=BLUE_B),
                       zh(s, 28)).arrange(RIGHT, buff=0.35)
                for i, s in enumerate(items)
            ])
            rows.arrange_in_grid(rows=4, cols=2, col_alignments="ll",
                                 buff=(1.6, 0.4)).shift(DOWN * 0.4)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows],
                                  lag_ratio=0.25), run_time=4)
        self.clear()


# ====================================================================== 2 RNN
class S02_RNN(VoiceScene):
    def construct(self):
        words = ["今天", "的", "天气", "真", "不错"]
        n = len(words)
        xs = np.linspace(-5, 5, n)
        tokens = VGroup(*[token_box(w, BLUE_D).move_to([x, -2.3, 0]) for w, x in zip(words, xs)])
        cells = VGroup(*[
            Square(1.1, stroke_color=GREY_B, fill_color=GREY_D, fill_opacity=0.6).move_to([x, 0, 0])
            for x in xs
        ])
        labels = VGroup(*[MathTex(f"h_{i + 1}", font_size=32).move_to(c) for i, c in enumerate(cells)])
        ups = VGroup(*[Arrow(t.get_top(), c.get_bottom(), buff=0.1, stroke_width=3, color=GREY_B)
                       for t, c in zip(tokens, cells)])
        rights = VGroup(*[Arrow(cells[i].get_right(), cells[i + 1].get_left(), buff=0.08,
                                stroke_width=3, color=YELLOW) for i in range(n - 1)])

        with self.voice("rnn_1"):
            title = zh("循环神经网络 RNN", 40).to_edge(UP)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in tokens], lag_ratio=0.2))
            self.play(Create(cells), Write(labels), *map(GrowArrow, ups))
            self.play(LaggedStart(*map(GrowArrow, rights), lag_ratio=0.3))
            memory = Dot(color=YELLOW, radius=0.12).move_to(cells[0])
            self.play(FadeIn(memory, scale=2))
            for i in range(1, n):
                self.play(memory.animate.move_to(cells[i]),
                          cells[i].animate.set_fill(YELLOW_E, 0.8), run_time=0.6)
                self.play(cells[i].animate.set_fill(GREY_D, 0.6), run_time=0.25)

        with self.voice("rnn_2"):
            steps = VGroup(*[MathTex(f"t={i + 1}", font_size=28, color=GREY_B).next_to(c, UP, 0.2)
                             for i, c in enumerate(cells)])
            self.play(FadeOut(memory), LaggedStart(*map(FadeIn, steps), lag_ratio=0.2))
            gpu_title = zh("GPU 计算核心", 26, GREY_B)
            cores = VGroup(*[Square(0.22, stroke_width=1, stroke_color=GREY_B, fill_color=GREY_D,
                                    fill_opacity=1) for _ in range(48)]).arrange_in_grid(4, 12, buff=0.08)
            gpu = VGroup(gpu_title, cores).arrange(DOWN, buff=0.15).to_corner(UR, buff=0.3)
            self.play(title.animate.to_edge(LEFT), FadeIn(gpu))
            for i in range(n):
                self.play(cells[i].animate.set_fill(YELLOW_E, 0.8),
                          cores[i].animate.set_fill(YELLOW, 1), run_time=0.5)
                self.play(cells[i].animate.set_fill(GREY_D, 0.6),
                          cores[i].animate.set_fill(GREY_D, 1), run_time=0.2)
            serial = zh("串行：n 个词需要 n 步", 30, RED).to_edge(DOWN, buff=0.35)
            self.play(Write(serial))

        with self.voice("rnn_3"):
            self.play(FadeOut(gpu), FadeOut(serial), FadeOut(steps))
            info = VGroup(*[
                Rectangle(width=0.9, height=0.25, stroke_width=0, fill_color=BLUE,
                          fill_opacity=op).next_to(c, UP, 0.25)
                for c, op in zip(cells, [1.0, 0.65, 0.4, 0.22, 0.1])
            ])
            tag = zh("“今天”的信息", 24, BLUE_B).next_to(info[0], UP, 0.2)
            self.play(FadeIn(info[0]), Write(tag))
            for i in range(1, n):
                self.play(TransformFromCopy(info[i - 1], info[i]), run_time=0.7)
            fade = zh("逐步稀释", 30, BLUE_B).next_to(info[-1], UP, 0.3)
            self.play(Write(fade))
            dist = DoubleArrow(tokens[0].get_bottom(), tokens[-1].get_bottom(), buff=0.1,
                               color=RED, tip_length=0.2).shift(DOWN * 0.5)
            self.play(GrowFromCenter(dist))

        with self.voice("rnn_4"):
            self.play(*[FadeOut(m) for m in [cells, labels, ups, rights, info, tag, fade, dist, title]])
            self.play(tokens.animate.move_to(DOWN * 0.8))
            arcs = VGroup()
            for i in range(n):
                for j in range(n):
                    if i != j:
                        arcs.add(CurvedArrow(tokens[i].get_top() + RIGHT * 0.08 * np.sign(j - i),
                                             tokens[j].get_top(), angle=-TAU / 6 if j > i else TAU / 6,
                                             stroke_width=1.8, tip_length=0.12,
                                             color=interpolate_color(ManimColor(YELLOW), ManimColor(TEAL), (i + j) / (2 * n))))
            new_title = zh("Transformer：每个词直接看向所有词", 38).to_edge(UP)
            self.play(Write(new_title))
            self.play(LaggedStart(*map(Create, arcs), lag_ratio=0.02), run_time=3)
            attn = zh("注意力 Attention", 44, YELLOW).next_to(tokens, DOWN, buff=0.8)
            self.play(FadeIn(attn, scale=1.3))
        self.clear()


# ====================================================================== 3 词嵌入
class S03_Embedding(VoiceScene):
    def construct(self):
        with self.voice("emb_1"):
            word = token_box("小猫", BLUE_D, 36).shift(LEFT * 4)
            vec = Matrix([["0.12"], ["-0.83"], ["0.47"], [r"\vdots"], ["1.05"]],
                         v_buff=0.6, element_alignment_corner=ORIGIN).scale(0.8)
            vec.set_color(E_COLOR).shift(RIGHT * 1.5)
            arrow = Arrow(word.get_right(), vec.get_left(), buff=0.3)
            lookup = MathTex(r"W_E", font_size=40).next_to(arrow, UP)
            cap = zh("词嵌入 Embedding", 36).to_edge(UP)
            self.play(Write(cap), FadeIn(word, shift=RIGHT))
            self.play(GrowArrow(arrow), Write(lookup))
            self.play(Write(vec), run_time=2)
            brace = Brace(vec, RIGHT)
            dim = zh("高维向量", 28, GREY_B).next_to(brace, RIGHT)
            self.play(GrowFromCenter(brace), FadeIn(dim))

        plane = NumberPlane(x_range=[-6, 6], y_range=[-3.5, 3.5],
                            background_line_style={"stroke_opacity": 0.25})
        coords = {"小猫": (2.2, 1.6), "小狗": (2.8, 1.0), "国王": (-3.2, 2.2), "女王": (-4.0, 1.2),
                  "苹果": (1.2, -1.6), "香蕉": (2.9, -1.9), "奔跑": (-2.5, -1.8)}
        colors = [BLUE_B, BLUE_B, GOLD, GOLD, GREEN, GREEN, PURPLE_B]
        arrows = VGroup()
        tags = VGroup()
        for (w, (x, y)), c in zip(coords.items(), colors):
            a = Arrow(ORIGIN, [x, y, 0], buff=0, color=c, stroke_width=4)
            t = zh(w, 26, c).next_to(a.get_end(), UR * 0.5 if x > 0 else UL * 0.5, buff=0.1)
            arrows.add(a)
            tags.add(t)

        with self.voice("emb_2"):
            self.play(*[FadeOut(m) for m in [word, vec, arrow, lookup, brace, dim, cap]])
            self.play(Create(plane), run_time=1.5)
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(t)) for a, t in zip(arrows, tags)],
                                  lag_ratio=0.25), run_time=4)
            for i, j in [(0, 1), (2, 3), (4, 5)]:
                ang = Angle(arrows[i], arrows[j], radius=0.9, other_angle=(i == 2))
                self.play(Create(ang), run_time=0.5)
                self.play(FadeOut(ang), run_time=0.4)

        with self.voice("emb_3"):
            p1 = VGroup(token_box("吃", GREY_D, 26), token_box("苹果", GREEN_D, 26)).arrange(RIGHT, buff=0.1)
            p2 = VGroup(token_box("苹果", GREEN_D, 26), token_box("手机", GREY_D, 26)).arrange(RIGHT, buff=0.1)
            phr = VGroup(p1, p2).arrange(RIGHT, buff=1.2).to_corner(UR).shift(DOWN * 0.1)
            bg = BackgroundRectangle(phr, buff=0.2, fill_opacity=0.85)
            self.play(FadeIn(bg), FadeIn(phr))
            apple = arrows[4]
            l1 = DashedLine(p1[1].get_bottom(), apple.get_end(), color=GREEN_B, stroke_width=2)
            l2 = DashedLine(p2[0].get_bottom(), apple.get_end(), color=GREEN_B, stroke_width=2)
            self.play(Create(l1), Create(l2))
            same = zh("同一个初始向量", 28, GREEN_B).next_to(apple.get_end(), DOWN, buff=0.6)
            self.play(Indicate(apple, color=YELLOW), Write(same))

        with self.voice("emb_4"):
            fruit = Arrow(ORIGIN, [2.4, -2.6, 0], buff=0, color=GREEN_B, stroke_width=4)
            tech = Arrow(ORIGIN, [-0.7, -2.9, 0], buff=0, color=PURPLE_B, stroke_width=4)
            self.play(FadeOut(same), FadeOut(l1), FadeOut(l2))
            self.play(TransformFromCopy(apple, fruit), p1[1][0].animate.set_stroke(YELLOW, 4))
            t1 = zh("吃苹果", 22, GREEN_B).next_to(fruit.get_end(), RIGHT, 0.1)
            self.play(FadeIn(t1))
            self.play(TransformFromCopy(apple, tech), p2[0][0].animate.set_stroke(YELLOW, 4))
            t2 = zh("苹果手机", 22, PURPLE_B).next_to(tech.get_end(), LEFT, 0.1)
            self.play(FadeIn(t2))
            d = MathTex(r"d_{\text{model}} = 512", font_size=44).to_corner(DL)
            d_bg = BackgroundRectangle(d, buff=0.15, fill_opacity=0.85)
            self.play(FadeIn(d_bg), Write(d))
        self.clear()


# ====================================================================== 4 Q K V
class S04_QKV(VoiceScene):
    WORDS = ["一只", "毛茸茸", "的", "蓝色", "小猫"]
    # 分数 S[i][j] = K_i · Q_j（行：键，列：查询）
    SCORES = np.array([
        [2.1, -0.4, 0.3, -0.6, 0.2],
        [0.5, 1.8, -1.2, 1.1, 4.2],
        [-0.8, 0.2, 1.5, -0.3, -1.6],
        [-0.2, 1.3, -0.9, 2.2, 3.9],
        [0.4, 0.6, -0.5, 0.9, 1.4],
    ])

    def construct(self):
        n = 5
        cw, ch = 1.15, 0.95  # 格子宽、高
        gx0, gy0 = -1.5, 1.0  # 左上格子中心
        col_x = [gx0 + j * cw for j in range(n)]
        row_y = [gy0 - i * ch for i in range(n)]

        top = VGroup(*[token_box(w, BLUE_D, 20, 0.1) for w in self.WORDS])
        for t, x in zip(top, col_x):
            t.move_to([x, 3.4, 0])
        phrase = VGroup(*[token_box(w, BLUE_D, 36) for w in self.WORDS]).arrange(RIGHT, buff=0.15)

        with self.voice("qkv_1"):
            self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.3) for p in phrase], lag_ratio=0.15))
            q = zh("有形容词在修饰我吗？", 30, Q_COLOR).next_to(phrase[-1], DOWN, buff=0.6).shift(LEFT)
            bubble = SurroundingRectangle(q, corner_radius=0.2, buff=0.2, color=Q_COLOR)
            self.play(phrase[-1].animate.set_color(Q_COLOR))
            self.play(Create(bubble), Write(q))
            adj = VGroup(phrase[1], phrase[3])
            self.play(Indicate(adj, color=TEAL))

        E = VGroup(*[MathTex(rf"\vec{{E}}_{j + 1}", font_size=30, color=E_COLOR).move_to([x, 2.75, 0])
                     for j, x in enumerate(col_x)])
        Q = VGroup(*[MathTex(rf"\vec{{Q}}_{j + 1}", font_size=30, color=Q_COLOR).move_to([x, 1.75, 0])
                     for j, x in enumerate(col_x)])

        with self.voice("qkv_2"):
            self.play(FadeOut(q), FadeOut(bubble),
                      *[ReplacementTransform(p, t) for p, t in zip(phrase, top)])
            self.play(LaggedStart(*[FadeIn(e, shift=DOWN * 0.2) for e in E], lag_ratio=0.1))
            wq = MathTex(r"W_Q", font_size=36, color=Q_COLOR).move_to([col_x[-1] + 1.0, 2.25, 0])
            downs = VGroup(*[Arrow(e.get_bottom(), q_.get_top(), buff=0.08, stroke_width=2,
                                   max_tip_length_to_length_ratio=0.3, color=Q_COLOR)
                             for e, q_ in zip(E, Q)])
            self.play(Write(wq), LaggedStart(*map(GrowArrow, downs), lag_ratio=0.1))
            self.play(LaggedStart(*[TransformFromCopy(e, q_) for e, q_ in zip(E, Q)], lag_ratio=0.1))
            qd = VGroup(zh("Query", 26, Q_COLOR), zh("我在找什么？", 26)).arrange(DOWN, aligned_edge=LEFT)
            qd.next_to(wq, RIGHT, buff=0.3)
            self.play(FadeIn(qd, shift=LEFT * 0.2))

        left_tok = VGroup(*[token_box(w, BLUE_D, 22, 0.1) for w in self.WORDS])
        K = VGroup(*[MathTex(rf"\vec{{K}}_{i + 1}", font_size=30, color=K_COLOR) for i in range(n)])
        for i, y in enumerate(row_y):
            K[i].move_to([gx0 - 1.0, y, 0])
            left_tok[i].move_to([gx0 - 2.6, y, 0])
        wk = MathTex(r"W_K", font_size=34, color=K_COLOR).move_to([gx0 - 1.8, row_y[0] + 0.75, 0])
        side_note = [5.4, 2.4, 0]

        with self.voice("qkv_3"):
            self.play(FadeOut(downs), FadeOut(E), FadeOut(wq), FadeOut(qd))
            self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in left_tok], lag_ratio=0.1))
            self.play(Write(wk), LaggedStart(*[TransformFromCopy(t, k) for t, k in zip(left_tok, K)],
                                             lag_ratio=0.1))
            kd = VGroup(zh("Key", 26, K_COLOR), zh("我是什么", 26)).arrange(DOWN, aligned_edge=LEFT)
            kd.move_to(side_note)
            self.play(FadeIn(kd, shift=RIGHT * 0.2))

        grid = VGroup(*[
            Rectangle(width=cw, height=ch, stroke_width=1, stroke_color=GREY_B).move_to([col_x[j], row_y[i], 0])
            for i in range(n) for j in range(n)
        ])
        S = self.SCORES
        nums = VGroup(*[
            Text(f"{S[i, j]:+.1f}", font_size=20, color=heat_color(S[i, j], -2, 4)).move_to(grid[i * n + j])
            for i in range(n) for j in range(n)
        ])
        with self.voice("qkv_4"):
            self.play(Create(grid), run_time=1.2)
            dot = MathTex(r"\vec{K}_2 \cdot \vec{Q}_5", font_size=34).to_edge(RIGHT).shift(UP * 0.5)
            self.play(Indicate(K[1]), Indicate(Q[4]), Write(dot))
            self.play(TransformFromCopy(dot, nums[1 * n + 4]))
            self.play(LaggedStart(*[FadeIn(nums[k], scale=0.5) for k in range(n * n) if k != n + 4],
                                  lag_ratio=0.05), run_time=2.5)
            self.play(FadeOut(dot))

        with self.voice("qkv_5"):
            col = SurroundingRectangle(VGroup(Q[4], grid[4], grid[4 * n + 4]), color=Q_COLOR, buff=0.05)
            self.play(Create(col))
            hi = VGroup(grid[1 * n + 4], grid[3 * n + 4])
            self.play(*[c.animate.set_fill(RED, 0.35) for c in hi],
                      Indicate(left_tok[1]), Indicate(left_tok[3]))
            self.play(grid[2 * n + 4].animate.set_fill(BLUE, 0.35), Indicate(left_tok[2], color=BLUE))

        W = softmax(S, axis=0)
        circles = VGroup(*[
            Circle(radius=0.04 + 0.3 * W[i, j], stroke_width=0, fill_color=WHITE,
                   fill_opacity=0.9).move_to(grid[i * n + j]).shift(UP * 0.1)
            for i in range(n) for j in range(n)
        ])
        wnums = VGroup(*[
            Text(f"{W[i, j]:.2f}", font_size=16, color=GREY_A).move_to(grid[i * n + j]).shift(DOWN * 0.34 + RIGHT * 0.33)
            for i in range(n) for j in range(n)
        ])
        with self.voice("qkv_6"):
            self.play(*[c.animate.set_fill(opacity=0) for c in grid])
            sm = MathTex(r"\mathrm{softmax}", font_size=36).next_to(grid, RIGHT, buff=0.5)
            self.play(Write(sm))
            self.play(ReplacementTransform(nums, circles), FadeIn(wnums), run_time=2)
            sums = VGroup(*[MathTex(r"\Sigma=1", font_size=22, color=GREY_B)
                            .next_to(grid[(n - 1) * n + j], DOWN, 0.15) for j in range(n)])
            self.play(LaggedStart(*map(FadeIn, sums), lag_ratio=0.1))

        with self.voice("qkv_7"):
            V = VGroup(*[MathTex(rf"\vec{{V}}_{i + 1}", font_size=30, color=V_COLOR).move_to(K[i])
                         for i in range(n)])
            wv = MathTex(r"W_V", font_size=34, color=V_COLOR).move_to(wk)
            vd = VGroup(zh("Value", 26, V_COLOR), zh("关注我，就给你这个", 26)).arrange(DOWN, aligned_edge=LEFT)
            vd.move_to(side_note)
            self.play(ReplacementTransform(K, V), ReplacementTransform(wk, wv),
                      ReplacementTransform(kd, vd), FadeOut(sm), FadeOut(sums))

        with self.voice("qkv_8"):
            keep = {i * n + 4 for i in range(n)}
            others = [circles[k] for k in range(n * n) if k not in keep] + \
                     [wnums[k] for k in range(n * n) if k not in keep]
            self.play(*[m.animate.set_opacity(0.12) for m in others])
            w5 = W[:, 4]
            terms = [rf"{w5[i]:.2f}\,\vec{{V}}_{i + 1}" for i in range(n)]
            eq = MathTex(r"\Delta\vec{E}_5 = ", " + ".join(terms), font_size=30)
            eq.move_to([0, 3.4, 0])
            self.play(FadeOut(top), FadeOut(vd))
            self.play(Write(eq), run_time=2)

            origin = np.array([4.6, -1.6, 0])
            e5 = Arrow(origin, origin + np.array([0.3, 1.7, 0]), buff=0, color=E_COLOR)
            delta = Arrow(e5.get_end(), e5.get_end() + np.array([1.2, 0.6, 0]), buff=0, color=V_COLOR)
            new = Arrow(origin, delta.get_end(), buff=0, color=YELLOW)
            l_e5 = zh("小猫", 22, E_COLOR).next_to(e5, LEFT, 0.1)
            l_new = zh("毛茸茸的\n蓝色小猫", 22, YELLOW).next_to(new.get_end(), UP, 0.15)
            self.play(FadeOut(col), GrowArrow(e5), FadeIn(l_e5))
            self.play(GrowArrow(delta))
            self.play(GrowArrow(new), Write(l_new))
        self.clear()


# ====================================================================== 5 公式
class S05_Formula(VoiceScene):
    def construct(self):
        formula = MathTex(
            r"\mathrm{Attention}(Q,K,V)", "=", r"\mathrm{softmax}\Big(",
            r"{Q K^{\top}", r"\over", r"\sqrt{d_k}}", r"\Big)", "V",
            font_size=58,
        )
        formula[3].set_color(YELLOW)
        formula[5].set_color(TEAL)
        formula[7].set_color(V_COLOR)

        with self.voice("formula_1"):
            name = zh("缩放点积注意力  Scaled Dot-Product Attention", 34, GREY_B).to_edge(UP)
            self.play(Write(formula), run_time=3)
            self.play(FadeIn(name, shift=DOWN * 0.2))

        with self.voice("formula_2"):
            self.play(formula.animate.shift(UP * 1.2))
            steps = [
                (formula[3], "所有查询 · 所有键", YELLOW),
                (formula[2], "分数 → 权重", WHITE),
                (formula[7], "加权求和", V_COLOR),
            ]
            prev = None
            for part, txt, c in steps:
                box = SurroundingRectangle(part, color=c, buff=0.08)
                label = zh(txt, 28, c).next_to(box, DOWN, buff=0.35)
                if prev is None:
                    self.play(Create(box), FadeIn(label))
                else:
                    self.play(ReplacementTransform(prev[0], box), FadeOut(prev[1]), FadeIn(label))
                self.wait(1.2)
                prev = (box, label)
            self.play(FadeOut(prev[0]), FadeOut(prev[1]))

            def block(w, h, c, tex):
                r = Rectangle(width=w, height=h, stroke_color=c, fill_color=c, fill_opacity=0.25)
                return VGroup(r, MathTex(tex, font_size=34).move_to(r))
            qb = block(0.9, 1.8, YELLOW, "Q")
            kb = block(1.8, 0.9, TEAL, r"K^{\top}")
            sb = block(1.8, 1.8, WHITE, r"n\times n")
            vb = block(0.9, 1.8, V_COLOR, "V")
            ob = block(0.9, 1.8, BLUE_C, r"\text{out}")
            shapes = VGroup(qb, MathTex(r"\times"), kb, MathTex("="), sb, MathTex(r"\times"), vb,
                            MathTex("="), ob).arrange(RIGHT, buff=0.3).shift(DOWN * 1.6)
            self.play(LaggedStart(*[FadeIn(s) for s in shapes], lag_ratio=0.15), run_time=3)
            gpu = zh("几次矩阵乘法 → GPU 并行", 30, GREEN).to_edge(DOWN, buff=0.3)
            self.play(Write(gpu))

        with self.voice("formula_3"):
            self.play(FadeOut(shapes), FadeOut(gpu), FadeOut(name),
                      formula.animate.scale(0.7).to_edge(UP))
            box = SurroundingRectangle(formula[5], color=TEAL, buff=0.08)
            self.play(Create(box))
            var = MathTex(r"q\cdot k=\sum_{i=1}^{d_k} q_i k_i", r"\qquad",
                          r"\mathrm{Var}(q\cdot k)=d_k", font_size=38).next_to(formula, DOWN, 0.5)
            self.play(Write(var))
            axes = Axes(x_range=[-40, 40, 10], y_range=[0, 0.22, 0.1], x_length=10, y_length=3.2,
                        tips=False, axis_config={"stroke_opacity": 0.6}).shift(DOWN * 1.7)
            self.play(Create(axes))
            curves = VGroup()
            labels = VGroup()
            for d, c in [(4, BLUE), (64, GREEN), (512, YELLOW)]:
                s = np.sqrt(d)
                g = axes.plot(lambda x, s=s: np.exp(-x * x / (2 * s * s)) / (s * np.sqrt(TAU)),
                              x_range=[-40, 40, 0.2], color=c)
                lab = MathTex(rf"d_k={d}", font_size=28, color=c)
                curves.add(g)
                labels.add(lab)
            labels.arrange(DOWN, aligned_edge=LEFT).next_to(axes, RIGHT, buff=-1.2).shift(UP * 0.8)
            for g, lab in zip(curves, labels):
                self.play(Create(g), FadeIn(lab), run_time=1.2)

        with self.voice("formula_4"):
            self.play(*[FadeOut(m) for m in [var, axes, curves, labels]])
            base = np.array([0.6, 0.1, -0.3, 0.45, -0.2, 0.3, -0.5, 0.2])
            scale = ValueTracker(8.0)
            m = len(base)
            bar_axes = Axes(x_range=[0, m, 1], y_range=[0, 1, 0.5], x_length=8, y_length=3.4,
                            tips=False, axis_config={"include_ticks": False}).shift(DOWN * 0.9)

            def bars():
                p = softmax(base * scale.get_value())
                g = VGroup()
                for i, v in enumerate(p):
                    h = max(bar_axes.y_axis.unit_size * v, 1e-3)
                    r = Rectangle(width=0.7, height=h, stroke_width=0, fill_color=BLUE_C, fill_opacity=0.9)
                    r.move_to(bar_axes.c2p(i + 0.5, 0), aligned_edge=DOWN)
                    g.add(r)
                return g
            bar_g = always_redraw(bars)
            status = always_redraw(lambda: MathTex(
                rf"\mathrm{{softmax}}({scale.get_value():.1f}\cdot s)", font_size=34
            ).next_to(bar_axes, UP, buff=0.2))
            raw = zh("未缩放：几乎 one-hot，梯度≈0", 28, RED).to_edge(DOWN, buff=0.35)
            self.play(Create(bar_axes), FadeIn(bar_g), FadeIn(status))
            self.play(Write(raw))
            self.wait(1.5)
            ok = zh("除以 √dₖ：分布平滑，梯度正常", 28, GREEN).to_edge(DOWN, buff=0.35)
            self.play(scale.animate.set_value(1.0), ReplacementTransform(raw, ok), run_time=3)
        self.clear()


# ====================================================================== 6 多头
class S06_MultiHead(VoiceScene):
    def construct(self):
        words = ["小明", "说", "他", "买", "的", "书", "很", "有趣"]
        toks = VGroup(*[token_box(w, BLUE_D, 32) for w in words]).arrange(RIGHT, buff=0.35)
        toks.shift(DOWN * 0.8)

        def link(i, j, c, up=True):
            a = toks[i].get_top() if up else toks[i].get_bottom()
            b = toks[j].get_top() if up else toks[j].get_bottom()
            return CurvedArrow(a, b, angle=(1 if up else -1) * TAU / 5 * np.sign(i - j),
                               color=c, stroke_width=3, tip_length=0.15)

        with self.voice("multi_1"):
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in toks], lag_ratio=0.1))
            rels = [(link(2, 0, YELLOW), zh("代词 → 指代", 24, YELLOW)),
                    (link(7, 5, TEAL, up=False), zh("谓语 → 主语", 24, TEAL)),
                    (link(3, 5, PINK), zh("动词 → 宾语", 24, PINK))]
            legend = VGroup(*[r[1] for r in rels]).arrange(DOWN, aligned_edge=LEFT).to_corner(UR)
            for arc, lab in rels:
                self.play(Create(arc), FadeIn(lab, shift=LEFT * 0.2))
                self.wait(0.6)
            q = zh("一组 Q、K、V 只能学一种关系", 32).to_edge(UP)
            self.play(Write(q))

        rng = np.random.default_rng(3)
        m = 8
        patterns = [
            np.eye(m), np.eye(m, k=-1) + 0.05, np.eye(m, k=1) + 0.05,
            np.tile(np.eye(m)[0], (m, 1)) + 0.1,
            np.ones((m, m)), rng.random((m, m)) ** 4,
            np.flipud(np.eye(m)) + 0.1, np.tril(rng.random((m, m))) ** 2,
        ]
        heads = VGroup()
        for h, P in enumerate(patterns):
            P = P / P.sum(axis=1, keepdims=True)
            img = np.clip(P / P.max(), 0, 1)
            sq = VGroup(*[
                Square(0.19, stroke_width=0, fill_color=interpolate_color(ManimColor("#101820"),
                                                                           ManimColor(YELLOW), img[r, c]),
                       fill_opacity=1)
                for r in range(m) for c in range(m)
            ]).arrange_in_grid(m, m, buff=0.015)
            frame = SurroundingRectangle(sq, color=GREY_B, stroke_width=1, buff=0.04)
            lab = MathTex(rf"\mathrm{{head}}_{h + 1}", font_size=26).next_to(frame, UP, 0.1)
            heads.add(VGroup(frame, sq, lab))
        heads.arrange_in_grid(2, 4, buff=(0.5, 0.45)).shift(DOWN * 0.2)

        with self.voice("multi_2"):
            self.play(*[FadeOut(mb) for mb in self.mobjects])
            title = zh("多头注意力 Multi-Head Attention", 36).to_edge(UP)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(h, scale=0.8) for h in heads], lag_ratio=0.12), run_time=3)
            proj = MathTex(r"512 \xrightarrow{\;W_i^Q,\,W_i^K,\,W_i^V\;} 64", font_size=38)
            proj.to_edge(DOWN, buff=0.4)
            self.play(Write(proj))

        with self.voice("multi_3"):
            self.play(FadeOut(proj))
            colors = [BLUE, TEAL, GREEN, YELLOW, GOLD, ORANGE, RED, PINK]
            strips = VGroup(*[
                Rectangle(width=0.55, height=0.4, stroke_width=1, fill_color=c, fill_opacity=0.8)
                for c in colors
            ]).arrange(RIGHT, buff=0)
            wo = MathTex(r"\times\, W^O", font_size=40)
            out = Rectangle(width=strips.width, height=0.4, fill_color=BLUE_C, fill_opacity=0.9,
                            stroke_width=1)
            VGroup(strips, wo, out).arrange(RIGHT, buff=0.35).shift(DOWN * 0.9)
            self.play(heads.animate.scale(0.55).shift(UP * 1.2))
            self.play(LaggedStart(*[TransformFromCopy(h[1], s) for h, s in zip(heads, strips)],
                                  lag_ratio=0.1), run_time=2)
            cat = Brace(strips, DOWN)
            cat_t = MathTex(r"8\times 64 = 512", font_size=32).next_to(cat, DOWN, 0.1)
            self.play(GrowFromCenter(cat), Write(cat_t))
            self.play(Write(wo), GrowFromEdge(out, LEFT))
            eq = MathTex(r"\mathrm{MultiHead}(Q,K,V)=\mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_8)\,W^O",
                         font_size=34).to_edge(DOWN, buff=0.3)
            self.play(Write(eq))
        self.clear()


# ====================================================================== 7 位置编码
def positional_encoding(n_pos: int, d: int) -> np.ndarray:
    pos = np.arange(n_pos)[:, None]
    i = np.arange(d // 2)[None, :]
    ang = pos / np.power(10000, 2 * i / d)
    pe = np.zeros((n_pos, d))
    pe[:, 0::2] = np.sin(ang)
    pe[:, 1::2] = np.cos(ang)
    return pe


class S07_Position(VoiceScene):
    def construct(self):
        with self.voice("pos_1"):
            r1 = VGroup(*[token_box(w, BLUE_D, 36) for w in ["狗", "咬", "人"]]).arrange(RIGHT, buff=0.3)
            r1.shift(UP * 1.2 + LEFT * 3)
            r2 = VGroup(*[token_box(w, BLUE_D, 36) for w in ["人", "咬", "狗"]]).arrange(RIGHT, buff=0.3)
            r2.shift(UP * 1.2 + RIGHT * 3)
            self.play(FadeIn(r1))
            self.play(TransformFromCopy(r1[0], r2[2], path_arc=-PI / 2),
                      TransformFromCopy(r1[2], r2[0], path_arc=PI / 2),
                      TransformFromCopy(r1[1], r2[1]), run_time=1.5)
            neq = zh("意思完全相反", 28, GREY_B).next_to(VGroup(r1, r2), UP, 0.4)
            self.play(FadeIn(neq))
            outs = VGroup()
            for row, perm in [(r1, [0, 1, 2]), (r2, [2, 1, 0])]:
                g = VGroup()
                for k, t in enumerate(row):
                    vals = [[0.8, -0.3, 0.5], [0.1, 0.9, -0.6], [-0.7, 0.2, 0.4]][perm[k]]
                    col = VGroup(*[Square(0.35, stroke_width=0.5, fill_color=heat_color(v),
                                          fill_opacity=1) for v in vals]).arrange(DOWN, buff=0)
                    col.next_to(t, DOWN, 0.8)
                    g.add(col)
                outs.add(g)
            self.play(*[FadeIn(g, shift=DOWN * 0.3) for g in outs])
            same = zh("注意力输出：一模一样（只是换了顺序）", 30, RED).to_edge(DOWN, buff=0.8)
            self.play(Write(same))

        with self.voice("pos_2"):
            self.play(*[FadeOut(m) for m in self.mobjects])
            eq = MathTex(r"\vec{x}_{\,pos}", "=", r"\vec{E}_{\,token}", "+", r"\vec{PE}_{\,pos}",
                         font_size=56)
            eq[2].set_color(E_COLOR)
            eq[4].set_color(YELLOW)
            self.play(Write(eq))
            b = Brace(eq[4], DOWN)
            bt = zh("位置编码（512 维）", 28, YELLOW).next_to(b, DOWN)
            self.play(GrowFromCenter(b), FadeIn(bt))

        with self.voice("pos_3"):
            self.play(FadeOut(b), FadeOut(bt), eq.animate.scale(0.6).to_edge(UP))
            axes_list = VGroup()
            waves = VGroup()
            freqs = [1.0, 0.45, 0.2, 0.08]
            for k, f in enumerate(freqs):
                ax = Axes(x_range=[0, 20, 5], y_range=[-1, 1, 1], x_length=5.3, y_length=0.9,
                          tips=False, axis_config={"stroke_opacity": 0.4, "include_ticks": False})
                axes_list.add(ax)
            axes_list.arrange(DOWN, buff=0.35).to_edge(LEFT, buff=1.1).shift(DOWN * 0.4)
            colors = [YELLOW, GOLD, GREEN, TEAL]
            for ax, f, c in zip(axes_list, freqs, colors):
                waves.add(ax.plot(lambda x, f=f: np.sin(f * x), x_range=[0, 20, 0.05], color=c))
            tags = VGroup(*[MathTex(rf"i={k}", font_size=24, color=c).next_to(ax, LEFT, 0.15)
                            for k, (ax, c) in enumerate(zip(axes_list, colors))])
            self.play(Create(axes_list), FadeIn(tags))
            self.play(LaggedStart(*map(Create, waves), lag_ratio=0.2), run_time=2)
            t = ValueTracker(2)
            line = always_redraw(lambda: DashedLine(
                axes_list[0].c2p(t.get_value(), 1.3), axes_list[-1].c2p(t.get_value(), -1.3),
                color=WHITE, stroke_width=2))
            dots = always_redraw(lambda: VGroup(*[
                Dot(ax.c2p(t.get_value(), np.sin(f * t.get_value())), color=c, radius=0.07)
                for ax, f, c in zip(axes_list, freqs, colors)]))
            plab = always_redraw(lambda: MathTex(rf"pos={t.get_value():.0f}", font_size=28)
                                 .next_to(axes_list[0].c2p(t.get_value(), 1.3), UP, 0.1))
            self.play(Create(line), FadeIn(dots), FadeIn(plab))
            self.play(t.animate.set_value(15), run_time=3, rate_func=there_and_back_with_pause)

            pe = positional_encoding(50, 64)
            rgb = np.zeros((*pe.shape, 3))
            neg, pos_ = np.array([0.23, 0.47, 0.85]), np.array([0.95, 0.35, 0.3])
            dark = np.array([0.08, 0.08, 0.1])
            v = pe[..., None]
            rgb = np.where(v > 0, dark + v * (pos_ - dark), dark - v * (neg - dark))
            img = ImageMobject((rgb * 255).astype(np.uint8))
            img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            img.width = 5.2
            img.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.4)
            xl = zh("维度 →", 22, GREY_B).next_to(img, DOWN, 0.15)
            yl = zh("位置 →", 22, GREY_B).rotate(-PI / 2).next_to(img, LEFT, 0.15)
            self.play(FadeIn(img), FadeIn(xl), FadeIn(yl))

        with self.voice("pos_4"):
            self.play(*[FadeOut(m) for m in [axes_list, waves, tags, line, dots, plab, img, xl, yl]])
            f1 = MathTex(r"PE_{(pos,\,2i)} = \sin\!\left(pos / 10000^{2i/d_{\text{model}}}\right)", font_size=36)
            f2 = MathTex(r"PE_{(pos,\,2i+1)} = \cos\!\left(pos / 10000^{2i/d_{\text{model}}}\right)", font_size=36)
            fs = VGroup(f1, f2).arrange(DOWN, aligned_edge=LEFT).next_to(eq, DOWN, 0.4)
            self.play(Write(fs))
            circ = Circle(radius=1.5, color=GREY_B).shift(DOWN * 1.6 + LEFT * 3)
            ang = ValueTracker(0.6)
            w = 0.45
            p = always_redraw(lambda: Dot(circ.point_at_angle(ang.get_value()), color=YELLOW))
            hand = always_redraw(lambda: Line(circ.get_center(), circ.point_at_angle(ang.get_value()),
                                              color=YELLOW))
            lab = MathTex(r"(\sin\omega_i pos,\ \cos\omega_i pos)", font_size=28).next_to(circ, UP, 0.2)
            self.play(Create(circ), Create(hand), FadeIn(p), FadeIn(lab))
            ghost = Dot(circ.point_at_angle(0.6), color=GREY_B)
            self.add(ghost)
            self.play(ang.animate.set_value(0.6 + 3 * w), run_time=2)
            arc = Arc(radius=0.6, start_angle=0.6, angle=3 * w, arc_center=circ.get_center(), color=TEAL)
            rot = MathTex(r"PE_{pos+k} = M_k \, PE_{pos}", font_size=40, color=TEAL)
            rot.next_to(circ, RIGHT, buff=1.2)
            note = zh("旋转矩阵，只与偏移 k 有关", 26, GREY_B).next_to(rot, DOWN, 0.3)
            self.play(Create(arc), Write(rot))
            self.play(FadeIn(note))
        self.clear()


# ====================================================================== 8 架构
def arch_box(text: str, color, width=2.7, height=0.44, size=20):
    r = RoundedRectangle(corner_radius=0.08, width=width, height=height, stroke_color=color,
                         fill_color=color, fill_opacity=0.3, stroke_width=2)
    return VGroup(r, zh(text, size).move_to(r))


class S08_Architecture(VoiceScene):
    def construct(self):
        ATT, NORM, FFN, EMB = ORANGE, YELLOW_E, BLUE_C, PINK
        gap = 0.1

        enc_emb = arch_box("输入嵌入", EMB)
        enc_pe = VGroup(Circle(0.16, color=WHITE), MathTex("+", font_size=28))
        enc_sub = VGroup(arch_box("多头自注意力", ATT), arch_box("Add & Norm", NORM),
                         arch_box("前馈网络 FFN", FFN), arch_box("Add & Norm", NORM))
        enc_sub.arrange(UP, buff=gap)
        enc_col = VGroup(enc_emb, enc_pe, enc_sub).arrange(UP, buff=0.3)
        enc_frame = SurroundingRectangle(enc_sub, color=GREY_B, buff=0.15, corner_radius=0.1)
        enc_n = MathTex(r"\times 6", font_size=32).next_to(enc_frame, LEFT, 0.15)
        encoder = VGroup(enc_col, enc_frame, enc_n)

        dec_emb = arch_box("输出嵌入（右移）", EMB)
        dec_pe = VGroup(Circle(0.16, color=WHITE), MathTex("+", font_size=28))
        dec_sub = VGroup(arch_box("掩码多头自注意力", ATT), arch_box("Add & Norm", NORM),
                         arch_box("交叉注意力", ATT), arch_box("Add & Norm", NORM),
                         arch_box("前馈网络 FFN", FFN), arch_box("Add & Norm", NORM))
        dec_sub.arrange(UP, buff=gap)
        dec_frame = SurroundingRectangle(dec_sub, color=GREY_B, buff=0.15, corner_radius=0.1)
        dec_head = VGroup(arch_box("Linear", GREY_B), arch_box("Softmax", GREEN_D),
                          zh("输出概率", 22)).arrange(UP, buff=gap)
        dec_col = VGroup(dec_emb, dec_pe, dec_sub, dec_head).arrange(UP, buff=0.3)
        dec_frame.move_to(dec_sub)
        dec_n = MathTex(r"\times 6", font_size=32).next_to(dec_frame, RIGHT, 0.15)
        decoder = VGroup(dec_col, dec_frame, dec_n)

        VGroup(encoder, decoder).arrange(RIGHT, buff=2.0, aligned_edge=DOWN).to_edge(DOWN, buff=0.25)
        enc_frame.move_to(enc_sub)
        enc_n.next_to(enc_frame, LEFT, 0.15)
        dec_n.next_to(dec_frame, RIGHT, 0.15)

        def flow(col):
            return VGroup(*[Arrow(col[k].get_top(), col[k + 1].get_bottom(), buff=0.03, stroke_width=2,
                                  max_tip_length_to_length_ratio=0.35, color=GREY_B)
                            for k in range(len(col) - 1)])
        arrows = VGroup(flow([enc_emb, enc_pe, enc_sub[0]]),
                        flow([dec_emb, dec_pe, dec_sub[0]]),
                        flow([dec_sub[-1], dec_head[0], dec_head[1], dec_head[2]]))
        enc_out = CubicBezier(enc_sub[-1].get_top(), enc_sub[-1].get_top() + UP * 0.6,
                              dec_sub[2].get_left() + LEFT * 1.4, dec_sub[2].get_left(),
                              color=TEAL, stroke_width=3)
        enc_lab = zh("编码器", 30).next_to(enc_frame, UP, 0.8)
        dec_lab = zh("解码器", 30).next_to(dec_head, LEFT, 0.8)
        diagram = VGroup(encoder, decoder, arrows, enc_out, enc_lab, dec_lab)

        with self.voice("arch_1"):
            self.play(LaggedStart(FadeIn(encoder, shift=UP * 0.3), FadeIn(decoder, shift=UP * 0.3),
                                  lag_ratio=0.4), run_time=2.5)
            self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.2), Create(enc_out))
            self.play(Write(enc_lab), Write(dec_lab))
            trans = VGroup(zh("英文", 24, GREY_B), zh("→", 24), zh("德文", 24, GREY_B)).arrange(RIGHT)
            trans.to_corner(UR)
            self.play(FadeIn(trans))

        side = RIGHT * 0.1

        def dimmer(*mobs):
            return SurroundingRectangle(VGroup(*mobs), buff=0.12, stroke_width=0,
                                        fill_color=config.background_color, fill_opacity=0.78)
        dim_dec = dimmer(decoder, dec_lab)
        dim_enc = dimmer(encoder, enc_lab)
        with self.voice("arch_2"):
            self.play(FadeOut(trans), FadeIn(dim_dec))
            self.play(Indicate(enc_n, scale_factor=1.6), Circumscribe(enc_frame, color=YELLOW))
            self.play(Indicate(enc_sub[0]), Indicate(enc_sub[2]))
            detail = VGroup(
                MathTex(r"\mathrm{FFN}(x)=\max(0,\,xW_1+b_1)\,W_2+b_2", font_size=30),
                MathTex(r"512 \to 2048 \to 512", font_size=34, color=FFN),
            ).arrange(DOWN).to_corner(UR).shift(side)
            bg = BackgroundRectangle(detail, buff=0.2, fill_opacity=0.92)
            self.play(FadeIn(bg), Write(detail))

        with self.voice("arch_3"):
            self.play(FadeOut(detail), FadeOut(bg))
            res = VGroup()
            for a, b in [(0, 1), (2, 3)]:
                start = enc_sub[a].get_bottom() + DOWN * 0.05
                end = enc_sub[b].get_right()
                res.add(CubicBezier(start + RIGHT * 1.0, start + RIGHT * 2.0,
                                    end + RIGHT * 0.8, end, color=YELLOW, stroke_width=3))
            self.play(*[Indicate(enc_sub[k], color=YELLOW) for k in (1, 3)])
            self.play(LaggedStart(*map(Create, res), lag_ratio=0.4), run_time=2)
            ln = MathTex(r"\mathrm{LayerNorm}\big(x+\mathrm{Sublayer}(x)\big)", font_size=36)
            ln.to_corner(UR).shift(side)
            bg = BackgroundRectangle(ln, buff=0.2, fill_opacity=0.92)
            self.play(FadeIn(bg), Write(ln))
            self.play(ShowPassingFlash(res.copy().set_stroke(WHITE, 6), time_width=0.4), run_time=1.5)

        with self.voice("arch_4"):
            self.play(FadeOut(ln), FadeOut(bg), FadeOut(res), FadeOut(dim_dec), FadeIn(dim_enc))
            self.play(Indicate(dec_n, scale_factor=1.6), Circumscribe(dec_sub[2], color=TEAL))
            self.play(ShowPassingFlash(enc_out.copy().set_stroke(WHITE, 6), time_width=0.5), run_time=1.5)
            qkv = VGroup(zh("Q：来自解码器", 24, Q_COLOR), zh("K, V：来自编码器", 24, K_COLOR))
            qkv.arrange(DOWN, aligned_edge=LEFT).to_corner(UR)
            bg = BackgroundRectangle(qkv, buff=0.2, fill_opacity=0.92)
            self.play(FadeIn(bg), Write(qkv))

        with self.voice("arch_5"):
            self.play(FadeOut(qkv), FadeOut(bg), FadeOut(dim_enc))
            self.play(diagram.animate.scale(0.78).to_edge(LEFT, buff=0.2))
            self.play(Circumscribe(dec_sub[0], color=ORANGE))
            m = 6
            mask = VGroup()
            for r in range(m):
                for c in range(m):
                    ok = c <= r
                    sq = Square(0.55, stroke_width=1, stroke_color=GREY_B,
                                fill_color=ORANGE if ok else "#1a1a24", fill_opacity=0.55 if ok else 1)
                    mask.add(sq)
            mask.arrange_in_grid(m, m, buff=0).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.2)
            infs = VGroup(*[MathTex(r"-\infty", font_size=18, color=RED).move_to(mask[r * m + c])
                            for r in range(m) for c in range(m) if c > r])
            mt = zh("第 t 行只能看 ≤ t 的位置", 24).next_to(mask, UP, 0.3)
            self.play(Create(mask), FadeIn(mt))
            self.play(LaggedStart(*map(FadeIn, infs), lag_ratio=0.05))
            zeros = VGroup(*[MathTex("0", font_size=22, color=GREY_B).move_to(x) for x in infs])
            sm = MathTex(r"\xrightarrow{\mathrm{softmax}}", font_size=34).next_to(mask, DOWN, 0.2)
            self.play(Write(sm))
            self.play(ReplacementTransform(infs, zeros))

        with self.voice("arch_6"):
            self.play(*[FadeOut(x) for x in [mask, mt, zeros, sm]])
            self.play(Circumscribe(dec_head, color=GREEN))
            probs = [("Katze", 0.62), ("Hund", 0.18), ("Maus", 0.09), ("Kater", 0.06), ("…", 0.05)]
            rows = VGroup()
            for w, p in probs:
                bar = Rectangle(width=4 * p + 0.02, height=0.35, stroke_width=0, fill_color=GREEN,
                                fill_opacity=0.85)
                row = VGroup(zh(w, 26), bar, Text(f"{p:.2f}", font_size=22)).arrange(RIGHT, buff=0.2)
                rows.add(row)
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(RIGHT, buff=0.8)
            nt = zh("下一个词的概率", 26, GREY_B).next_to(rows, UP, 0.3)
            self.play(FadeIn(nt), LaggedStart(*[GrowFromEdge(r, LEFT) for r in rows], lag_ratio=0.15))
            gen = VGroup(*[token_box(w, GREEN_D, 22, 0.1) for w in ["Die", "Katze", "saß", "<eos>"]])
            gen.arrange(RIGHT, buff=0.1).next_to(rows, DOWN, 0.6)
            self.play(LaggedStart(*[FadeIn(g, shift=LEFT * 0.2) for g in gen], lag_ratio=0.5), run_time=2.5)
        self.clear()


# ====================================================================== 9 为什么是自注意力
class S09_WhySelfAttention(VoiceScene):
    def construct(self):
        header = [zh("层类型", 26), zh("每层复杂度", 26), zh("串行操作", 26), zh("最大路径长度", 26)]
        data = [
            [zh("自注意力", 26, YELLOW), MathTex(r"O(n^2\cdot d)"), MathTex(r"O(1)"), MathTex(r"O(1)")],
            [zh("循环层", 26, BLUE_B), MathTex(r"O(n\cdot d^2)"), MathTex(r"O(n)"), MathTex(r"O(n)")],
            [zh("卷积层", 26, GREEN_B), MathTex(r"O(k\cdot n\cdot d^2)"), MathTex(r"O(1)"),
             MathTex(r"O(\log_k n)")],
        ]
        table = MobjectTable([header, *data], include_outer_lines=False,
                             line_config={"stroke_width": 1, "stroke_opacity": 0.5},
                             h_buff=0.7, v_buff=0.4).scale(0.9).shift(UP * 0.8)

        with self.voice("why_1"):
            t = zh("为什么是自注意力？", 38).to_edge(UP, buff=0.3)
            self.play(Write(t))
            self.play(table.create(), run_time=3)
            col = table.get_columns()[1]
            box = SurroundingRectangle(col, color=YELLOW, buff=0.1)
            self.play(Create(box))
            ex = MathTex(r"n=50,\ d=512:\quad n^2 d \approx 1.3\times10^6 \ \ll\ n d^2 \approx 1.3\times10^7",
                         font_size=34).next_to(table, DOWN, 0.6)
            self.play(Write(ex))

        with self.voice("why_2"):
            box2 = SurroundingRectangle(VGroup(table.get_columns()[2], table.get_columns()[3]),
                                        color=TEAL, buff=0.1)
            self.play(ReplacementTransform(box, box2), FadeOut(ex))
            self.play(Indicate(table.get_rows()[1]))
            toks = VGroup(*[Dot(radius=0.08) for _ in range(8)]).arrange(RIGHT, buff=0.6).shift(DOWN * 2.3)
            chain = VGroup(*[Line(toks[i], toks[i + 1], color=BLUE_B, buff=0.1) for i in range(7)])
            direct = ArcBetweenPoints(toks[0].get_center(), toks[-1].get_center(), angle=-PI / 3,
                                      color=YELLOW)
            self.play(FadeIn(toks))
            self.play(Create(chain), run_time=2)
            rl = zh("RNN：n 步", 24, BLUE_B).next_to(toks, DOWN, 0.3)
            self.play(FadeIn(rl))
            self.play(Create(direct))
            al = zh("自注意力：1 步", 24, YELLOW).next_to(direct, UP, 0.1)
            self.play(FadeIn(al))

        with self.voice("why_3"):
            self.play(*[FadeOut(m) for m in [table, box2, toks, chain, direct, rl, al]])
            axes = Axes(x_range=[0, 10, 2], y_range=[0, 100, 25], x_length=7, y_length=4.2,
                        tips=False).shift(DOWN * 0.4 + LEFT * 1.5)
            xl = zh("上下文长度 n", 24, GREY_B).next_to(axes, DOWN, 0.2)
            yl = zh("计算量", 24, GREY_B).next_to(axes, LEFT, 0.2)
            self.play(Create(axes), FadeIn(xl), FadeIn(yl))
            curve = axes.plot(lambda x: x * x, x_range=[0, 10], color=RED)
            lin = axes.plot(lambda x: 10 * x, x_range=[0, 10], color=GREY_B, stroke_opacity=0.6)
            self.play(Create(lin), run_time=1)
            self.play(Create(curve), run_time=2.5)
            lab = MathTex(r"\propto n^2", color=RED, font_size=40).next_to(curve.get_end(), RIGHT)
            self.play(Write(lab))
            follow = VGroup(*[zh(s, 24, GREY_A) for s in
                              ["稀疏注意力", "线性注意力", "FlashAttention", "滑动窗口 …"]])
            follow.arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6)
            self.play(LaggedStart(*[FadeIn(f, shift=LEFT * 0.2) for f in follow], lag_ratio=0.3))
        self.clear()


# ====================================================================== 10 结果与影响
class S10_Results(VoiceScene):
    def construct(self):
        results = [("GNMT+RL", 24.6), ("ConvS2S", 25.16), ("MoE", 26.03),
                   ("ConvS2S 集成", 26.36), ("Transformer\nbase", 27.3), ("Transformer\nbig", 28.4)]
        ax = Axes(x_range=[0, len(results), 1], y_range=[23, 29, 1], x_length=10, y_length=4.2,
                  tips=False, axis_config={"include_ticks": False},
                  y_axis_config={"include_numbers": True, "font_size": 22,
                                 "include_ticks": True}).shift(DOWN * 0.6)

        with self.voice("res_1"):
            t = zh("WMT 2014 英→德  BLEU", 34).to_edge(UP, buff=0.35)
            note = zh("纵轴从 23 开始", 18, GREY_B).next_to(ax, UP, 0.1).align_to(ax, LEFT)
            self.play(Write(t), Create(ax), FadeIn(note))
            bars = VGroup()
            for i, (name, v) in enumerate(results):
                is_t = name.startswith("Transformer")
                c = YELLOW if is_t else BLUE_D
                top = ax.c2p(i + 0.5, v)
                bottom = ax.c2p(i + 0.5, 23)
                bar = Rectangle(width=1.1, height=top[1] - bottom[1], stroke_width=0, fill_color=c,
                                fill_opacity=0.85).move_to(bottom, aligned_edge=DOWN)
                val = Text(f"{v:g}", font_size=22).next_to(bar, UP, 0.08)
                lab = zh(name, 18, GREY_A).next_to(bottom, DOWN, 0.12)
                bars.add(VGroup(bar, val, lab))
            self.play(LaggedStart(*[AnimationGroup(GrowFromEdge(b[0], DOWN), FadeIn(b[1]), FadeIn(b[2]))
                                    for b in bars], lag_ratio=0.3), run_time=4)
            gain = MathTex(r"+2.0", color=YELLOW, font_size=36).next_to(bars[-1][1], UP, 0.15)
            self.play(Write(gain), Indicate(bars[-1][0], color=YELLOW))
            fr = VGroup(zh("英→法", 26, GREY_B), Text("41.8", font_size=36, color=YELLOW)).arrange(RIGHT)
            fr.to_corner(UR).shift(DOWN * 0.8)
            self.play(FadeIn(fr, shift=LEFT * 0.3))

        with self.voice("res_2"):
            self.play(*[FadeOut(m) for m in self.mobjects])
            gpus = VGroup(*[
                VGroup(RoundedRectangle(corner_radius=0.08, width=1.1, height=0.7, color=GREEN,
                                        fill_opacity=0.25),
                       Text("P100", font_size=18)).arrange(ORIGIN)
                for _ in range(8)
            ]).arrange_in_grid(2, 4, buff=0.25).shift(UP * 0.8)
            self.play(LaggedStart(*[FadeIn(g, scale=0.7) for g in gpus], lag_ratio=0.1))
            days = zh("× 3.5 天", 40, YELLOW).next_to(gpus, DOWN, 0.5)
            self.play(Write(days))
            flops = VGroup(MathTex(r"2.3\times10^{19}", font_size=34, color=YELLOW),
                           zh("vs", 26, GREY_B),
                           MathTex(r"7.7\times10^{19}", font_size=34, color=BLUE_B),
                           zh("（ConvS2S 集成，FLOPs）", 22, GREY_B)).arrange(RIGHT, buff=0.3)
            flops.next_to(days, DOWN, 0.5)
            self.play(FadeIn(flops, shift=UP * 0.2))

        with self.voice("res_3"):
            self.play(*[FadeOut(m) for m in self.mobjects])
            root = token_box("Transformer (2017)", YELLOW, 30).shift(UP * 2.3)
            enc = token_box("仅编码器：BERT (2018)", TEAL, 22).shift(LEFT * 4.6 + UP * 0.4)
            both = token_box("编码器-解码器：T5 (2019)", GREY_B, 22).shift(DOWN * 0.3)
            dec = token_box("仅解码器：GPT (2018)", ORANGE, 22).shift(RIGHT * 4.6 + UP * 0.4)
            llm = token_box("GPT-3 → ChatGPT → 今天的大语言模型", RED, 24).shift(RIGHT * 3.2 + DOWN * 1.7)
            edges = VGroup(*[Arrow(root.get_bottom(), x.get_top(), buff=0.1, color=GREY_B)
                             for x in (enc, both, dec)],
                           Arrow(dec.get_bottom(), llm.get_top(), buff=0.1, color=GREY_B))
            self.play(FadeIn(root, scale=1.2))
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(e), FadeIn(x, shift=DOWN * 0.2))
                                    for e, x in zip(edges[:3], (enc, both, dec))], lag_ratio=0.4),
                      run_time=3)
            self.play(GrowArrow(edges[3]), FadeIn(llm, shift=DOWN * 0.2))
            core = MathTex(r"\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V",
                           font_size=40).to_edge(DOWN, buff=0.4)
            self.play(Write(core))

        with self.voice("res_4"):
            self.play(*[FadeOut(m) for m in self.mobjects])
            title = Tex(r"\textbf{Attention Is All You Need}", font_size=60)
            self.play(Write(title), run_time=2.5)
            self.wait(2)
            nearly = zh("（几乎）", 36, GREY_B).next_to(title, DOWN, 0.4)
            self.play(FadeIn(nearly, shift=UP * 0.2))
            self.wait(2)
            thanks = zh("感谢收看", 44, YELLOW).next_to(nearly, DOWN, 0.8)
            self.play(Write(thanks))
        self.clear(run_time=1.5)
