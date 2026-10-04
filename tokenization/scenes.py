"""《Tokenization: A Survey for Modern NLP》3Blue1Brown 风格中文讲解 —— Manim 场景。

渲染单个场景:  manim -qm tokenization/scenes.py S05_BPE
整片构建:      python build.py all --paper tokenization

图表数值取自论文：表 2.1、图 2.1、表 5.2、表 5.3、图 6.2、表 11.1/11.2 及正文示例。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from common import VoiceScene, token_box, zh  # noqa: E402

MONO = "DejaVu Sans Mono"
OK = GREEN_C
BAD = RED_C
SP = "▁"  # 词首空格标记（U+2581）
PALETTE = [BLUE_D, TEAL_D, GREEN_D, GOLD_E, MAROON_D, PURPLE_D, BLUE_E, TEAL_E]


def mono(text: str, size: float = 24, color=WHITE) -> Text:
    return Text(text, font=MONO, font_size=size, color=color)


def tok(text: str, color=BLUE_D, size: float = 26, pad: float = 0.12, font: str = MONO) -> VGroup:
    """一个词元方块。"""
    label = Text(text, font=font, font_size=size, color=WHITE)
    box = RoundedRectangle(corner_radius=0.06, width=max(label.width + 2 * pad, 0.42),
                           height=max(label.height, 0.32) + 2 * pad,
                           stroke_color=color, fill_color=color, fill_opacity=0.35, stroke_width=2)
    label.move_to(box)
    return VGroup(box, label)


def toks(pieces: list[str], size: float = 26, buff: float = 0.08, colors=None, font: str = MONO) -> VGroup:
    colors = colors or PALETTE
    g = VGroup(*[tok(p, colors[i % len(colors)], size, font=font) for i, p in enumerate(pieces)])
    return g.arrange(RIGHT, buff=buff)


def section_title(text: str, color=YELLOW) -> Text:
    return zh(text, 36, color).to_edge(UP, buff=0.45)


def caption(text: str, size: float = 22, color=GREY_B) -> Text:
    return zh(text, size, color)


def hbar_chart(rows, max_v, width=6.0, bar_h=0.34, gap=0.16, colors=None, fmt="{:g}", label_size=20,
               value_size=20, label_font=None):
    """横向条形图：rows = [(label, value)]，返回 VGroup(labels, bars, values)。"""
    labels, bars, vals = VGroup(), VGroup(), VGroup()
    for i, (lab, v) in enumerate(rows):
        y = -i * (bar_h + gap)
        col = (colors[i] if isinstance(colors, list) else colors) or BLUE_C
        b = Rectangle(width=max(v / max_v * width, 0.02), height=bar_h, fill_color=col, fill_opacity=0.85,
                      stroke_width=0)
        b.move_to([b.width / 2, y, 0])
        bars.add(b)
        t = Text(lab, font_size=label_size, font=label_font) if label_font else zh(lab, label_size)
        labels.add(t.next_to([0, y, 0], LEFT, buff=0.2))
        vals.add(Text(fmt.format(v), font_size=value_size).next_to(b, RIGHT, buff=0.12))
    return VGroup(labels, bars, vals)


# ====================================================================== 1 开场
class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("intro_1"):
            q = zh("strawberry 里有几个 r？", 44)
            q.shift(UP * 1.5)
            word = VGroup(*[Text(c, font=MONO, font_size=60) for c in "strawberry"]).arrange(RIGHT, buff=0.08)
            self.play(Write(q))
            self.play(FadeIn(word, shift=UP * 0.2))
            rs = [i for i, c in enumerate("strawberry") if c == "r"]
            self.play(*[word[i].animate.set_color(YELLOW) for i in rs])
            ans = VGroup(zh("正确答案：3", 32, OK), zh("模型常说：2", 32, BAD)).arrange(RIGHT, buff=1.5)
            ans.next_to(word, DOWN, buff=0.8)
            self.play(FadeIn(ans[0]))
            self.play(FadeIn(ans[1]))
            self.g = VGroup(q, word, ans)

        with self.voice("intro_2"):
            self.play(FadeOut(self.g[2]), FadeOut(self.g[0]))
            one = tok("strawberry", BLUE_D, 48).move_to(self.g[1])
            self.play(ReplacementTransform(self.g[1], one))
            idx = zh("→  一个编号", 30, GREY_A).next_to(one, RIGHT, buff=0.4)
            vec = mono("→  [0.31, -1.20, 0.84, …]", 26, GREY_A).next_to(one, DOWN, buff=0.5)
            self.play(FadeIn(idx))
            self.play(FadeIn(vec))
            t = zh("tokenization · 分词", 40, YELLOW).to_edge(UP, buff=0.8)
            self.play(Write(t))
            self.g = VGroup(one, idx, vec, t)

        with self.voice("intro_3"):
            self.play(FadeOut(self.g))
            title = VGroup(Text("Token", font_size=80, weight=BOLD, color=BLUE_B),
                           Text("ization", font_size=80, weight=BOLD, color=TEAL_B)).arrange(RIGHT, buff=0.12)
            sub = Text("A Survey for Modern NLP", font_size=36, color=GREY_A)
            auth = Text("Marco Cognetta, Christopher Akiki, … , Xiulin Yang, Yuval Pinter", font_size=20, color=GREY_B)
            stats = VGroup(zh("32 位作者", 28, YELLOW), zh("25 家机构", 28, YELLOW), zh("正文约 100 页", 28, YELLOW))
            stats.arrange(RIGHT, buff=1.0)
            head = VGroup(title, sub, auth, stats).arrange(DOWN, buff=0.35).shift(UP * 0.3)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(auth))
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in stats], lag_ratio=0.4))
            self.head = head

        with self.voice("intro_4"):
            self.play(FadeOut(self.head))
            core = token_box("分词 = 核心设计选择", YELLOW, 34)
            items = ["序列长度", "计算成本", "多语言公平", "评测", "安全"]
            sats = VGroup(*[token_box(s, BLUE_D, 26) for s in items])
            angles = np.linspace(PI / 2, PI / 2 - TAU, len(items), endpoint=False)
            for s, a in zip(sats, angles):
                s.move_to(2.6 * np.array([1.4 * np.cos(a), np.sin(a), 0]))
            lines = VGroup(*[Line(core.get_center(), s.get_center(), color=GREY_D).set_z_index(-1) for s in sats])
            self.play(GrowFromCenter(core))
            self.play(LaggedStart(*[AnimationGroup(Create(l), FadeIn(s)) for l, s in zip(lines, sats)], lag_ratio=0.3),
                      run_time=3)
            self.g = VGroup(core, sats, lines)

        with self.voice("intro_5"):
            self.play(FadeOut(self.g))
            parts = ["流水线与历史", "核心算法", "预分词 · 多语言 · 评测", "字节与视觉方案", "大模型 · 理论 · 安全"]
            rows = VGroup(*[VGroup(Text(f"{i + 1}", font_size=34, color=BLUE_B), zh(p, 30)).arrange(RIGHT, buff=0.4)
                            for i, p in enumerate(parts)]).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.4), run_time=4)
        self.clear()


# ====================================================================== 2 流水线（图 1.1）
class S02_Pipeline(VoiceScene):
    def construct(self):
        ys = [3.0, 1.9, 0.8, -0.4, -1.5, -2.7]
        x_lab = -5.0
        labels = ["原始文本", "规范化", "预分词", "分词", "ID 映射", "嵌入"]

        def stage(i):
            return zh(labels[i], 22, GREY_B).move_to([x_lab, ys[i], 0])

        with self.voice("pipe_1"):
            left = zh("文字", 44)
            right = zh("实数向量", 44, BLUE_B)
            VGroup(left, right).arrange(RIGHT, buff=4.0)
            gap = DoubleArrow(left.get_right(), right.get_left(), buff=0.3, color=YELLOW)
            gl = zh("分词：接口", 28, YELLOW).next_to(gap, UP)
            self.play(FadeIn(left), FadeIn(right))
            self.play(GrowFromCenter(gap), Write(gl))
            self.g = VGroup(left, right, gap, gl)

        with self.voice("pipe_2"):
            self.play(FadeOut(self.g))
            raw = mono("The ‘tokenization pipeline’.", 30).move_to([1, ys[0], 0])
            norm = mono('The "tokenization pipeline".', 30).move_to([1, ys[1], 0])
            pre = VGroup(*[mono(f"[{p}]", 26, TEAL_B) for p in ["The", f"{SP}\"", f"{SP}tokenization", f"{SP}pipeline", "\"", "."]])
            pre.arrange(RIGHT, buff=0.05).move_to([1, ys[2], 0])
            self.play(FadeIn(stage(0)), FadeIn(raw))
            a1 = Arrow(raw.get_bottom(), norm.get_top(), buff=0.05, color=GREY_B, max_tip_length_to_length_ratio=0.3)
            self.play(FadeIn(stage(1)), GrowArrow(a1), FadeIn(norm))
            a2 = Arrow(norm.get_bottom(), pre.get_top(), buff=0.05, color=GREY_B, max_tip_length_to_length_ratio=0.3)
            self.play(FadeIn(stage(2)), GrowArrow(a2), FadeIn(pre))
            self.pre = pre

        with self.voice("pipe_3"):
            pieces = ["The", f"{SP}\"", f"{SP}token", "ization", f"{SP}pipe", "line", "\"", "."]
            ts = toks(pieces, 24).move_to([1, ys[3], 0])
            ids = VGroup(*[mono(str(n), 20, GREY_A) for n in [1038, 187, 12336, 2633, 1574, 1273, 188, 156]])
            for i, t in zip(ids, ts):
                i.move_to([t.get_x(), ys[4], 0])
            vecs = VGroup(*[VGroup(*[Square(0.22, stroke_width=0.5, fill_opacity=0.9,
                                            fill_color=interpolate_color(ManimColor(BLUE_E), ManimColor(YELLOW),
                                                                         float(abs(np.sin(k * 1.7 + j)))))
                                     for j in range(4)]).arrange(DOWN, buff=0.02) for k in range(8)])
            for v, t in zip(vecs, ts):
                v.move_to([t.get_x(), ys[5] - 0.1, 0])
            self.play(FadeIn(stage(3)), TransformFromCopy(self.pre, ts), run_time=1.5)
            self.play(Indicate(VGroup(ts[2], ts[3]), color=YELLOW))
            self.play(FadeIn(stage(4)), LaggedStart(*[FadeIn(i) for i in ids], lag_ratio=0.1))
            self.play(FadeIn(stage(5)), LaggedStart(*[FadeIn(v) for v in vecs], lag_ratio=0.1))
            self.ts = ts

        with self.voice("pipe_4"):
            back = CurvedArrow(RIGHT * 6 + DOWN * 2.6, RIGHT * 6 + UP * 2.9, angle=PI / 2.5, color=ORANGE)
            bl = zh("反分词", 26, ORANGE).next_to(back, LEFT, buff=0.1).shift(LEFT * 0.4)
            self.play(Create(back), FadeIn(bl))

        with self.voice("pipe_5"):
            self.clear(run_time=0.6)
            tk = token_box("分词器", YELLOW, 36).shift(UP * 1.4)
            v = VGroup(token_box("词表 V", BLUE_D, 30), token_box("推理算法", TEAL_D, 30)).arrange(RIGHT, buff=1.2)
            v.next_to(tk, DOWN, buff=1.0)
            ls = VGroup(*[Line(tk.get_bottom(), x.get_top(), color=GREY_B) for x in v])
            self.play(FadeIn(tk))
            self.play(Create(ls), FadeIn(v))
            tl = VGroup(token_box("训练分词器", GREY_BROWN, 24), Arrow(ORIGIN, RIGHT, color=GREY_B),
                        token_box("训练语言模型", GREY_BROWN, 24), zh("（分词器从此固定）", 22, GREY_B)).arrange(RIGHT, buff=0.3)
            tl.to_edge(DOWN, buff=0.8)
            self.play(FadeIn(tl, shift=UP * 0.2))
        self.clear()


# ====================================================================== 3 粒度与历史
class S03_Granularity(VoiceScene):
    def construct(self):
        with self.voice("gran_1"):
            w = mono("disjointed", 44).shift(UP * 2.2)
            rows = VGroup(
                VGroup(zh("语素", 24, GREY_B), toks(["dis", "joint", "ed"], 28)).arrange(RIGHT, buff=0.5),
                VGroup(zh("字符", 24, GREY_B), toks(list("disjointed"), 28, 0.05)).arrange(RIGHT, buff=0.5),
                VGroup(zh("整词", 24, GREY_B), toks(["disjointed"], 28)).arrange(RIGHT, buff=0.5),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(DOWN * 0.2)
            self.play(Write(w))
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
            self.g = VGroup(w, rows)

        with self.voice("gran_2"):
            self.play(FadeOut(self.g))
            t = section_title("按词切分：未登录词")
            raw = mono("True or false: Americans are from America.", 28)
            tokd = VGroup(*[mono(x, 28, RED_B if x == "<OOV>" else WHITE)
                            for x in ["True", "or", "false", ":", "<OOV>", "are", "from", "America", "."]])
            tokd.arrange(RIGHT, buff=0.25)
            VGroup(raw, tokd).arrange(DOWN, buff=0.8)
            self.play(Write(t), FadeIn(raw))
            self.play(TransformFromCopy(raw, tokd))
            guess = zh("Germans？ tokenizers？ Americans？", 26, GREY_B).next_to(tokd[4], DOWN, buff=0.6)
            self.play(Circumscribe(tokd[4], color=RED), FadeIn(guess))
            self.g = VGroup(t, raw, tokd, guess)

        with self.voice("gran_3"):
            self.play(FadeOut(self.g))
            eq = VGroup(mono("1,000,000", 36, YELLOW), mono("×", 36), mono("4096", 36, TEAL_B), mono("≈", 36),
                        mono("4.1B", 40, RED_B)).arrange(RIGHT, buff=0.3).shift(UP * 1.2)
            lab = VGroup(zh("词表大小", 20, GREY_B).next_to(eq[0], DOWN), zh("嵌入维度", 20, GREY_B).next_to(eq[2], DOWN),
                         zh("嵌入层参数", 20, GREY_B).next_to(eq[4], DOWN))
            self.play(Write(eq), FadeIn(lab))
            total = Rectangle(width=8, height=0.6, stroke_color=GREY_B).shift(DOWN * 1.4)
            emb = Rectangle(width=8 * 4.1 / 8, height=0.6, fill_color=RED_C, fill_opacity=0.8, stroke_width=0)
            emb.align_to(total, LEFT).set_y(total.get_y())
            tl = zh("最小的 Llama 3：共 8B 参数", 22).next_to(total, DOWN, buff=0.2)
            self.play(Create(total), FadeIn(tl))
            self.play(GrowFromEdge(emb, LEFT))

        with self.voice("gran_4"):
            self.clear(run_time=0.5)
            t = section_title("按字符 / 字节切分")
            j = VGroup(zh("Japan", 32), toks(["4a", "61", "70", "61", "6e"], 26)).arrange(RIGHT, buff=0.6)
            n = VGroup(zh("日本", 32), toks(["e6", "97", "a5", "e6", "9c", "ac"], 26)).arrange(RIGHT, buff=0.6)
            VGroup(j, n).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
            v = zh("词表只需 256 个字节", 30, YELLOW).to_edge(DOWN, buff=1.0)
            self.play(Write(t))
            self.play(FadeIn(j, shift=RIGHT * 0.2))
            self.play(FadeIn(n, shift=RIGHT * 0.2))
            self.play(Write(v))

        with self.voice("gran_5"):
            self.clear(run_time=0.5)
            c = toks(list("California"), 30, 0.05)
            w = toks(["California"], 30)
            VGroup(VGroup(zh("字符", 24, GREY_B), c).arrange(RIGHT, buff=0.5),
                   VGroup(zh("整词", 24, GREY_B), w).arrange(RIGHT, buff=0.5)).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
            c.align_to(w, LEFT)
            self.play(FadeIn(c), FadeIn(w))
            br = Line(c.get_corner(DL), c.get_corner(DR), color=YELLOW).shift(DOWN * 0.2)
            self.play(Create(br))
            f = zh("序列长度 ×2  →  注意力计算 ≈ ×4", 30, YELLOW).to_edge(DOWN, buff=1.0)
            self.play(Write(f))

        with self.voice("gran_6"):
            self.clear(run_time=0.5)
            axis = Arrow(LEFT * 5.5, RIGHT * 5.5, buff=0, color=GREY_B).shift(DOWN * 0.3)
            ends = VGroup(zh("字符 / 字节", 26).next_to(axis.get_start(), DOWN), zh("整词", 26).next_to(axis.get_end(), DOWN))
            pros = VGroup(zh("无未登录词", 22, OK).next_to(ends[0], DOWN), zh("信息密度高", 22, OK).next_to(ends[1], DOWN))
            sub = token_box("子词：从数据中学出来", YELLOW, 30).move_to(axis.get_center() + UP * 1.2)
            ex = toks([f"{SP}token", "ization"], 28).next_to(sub, DOWN, buff=0.35)
            self.play(GrowArrow(axis), FadeIn(ends), FadeIn(pros))
            self.play(FadeIn(sub, shift=DOWN * 0.3), FadeIn(ex))
        self.clear()


# ====================================================================== 4 为什么重要
class S04_WhyMatters(VoiceScene):
    def construct(self):
        with self.voice("why_1"):
            vocab = Rectangle(width=1.2, height=4.4, stroke_color=BLUE_C, fill_color=BLUE_E, fill_opacity=0.5).shift(LEFT * 4)
            vl = zh("嵌入层\n|V| × d", 24).move_to(vocab)
            body = Rectangle(width=3.5, height=3, stroke_color=GREY_B, fill_color=GREY_E, fill_opacity=0.5)
            bl = zh("Transformer 层", 26).move_to(body)
            out = vocab.copy().shift(RIGHT * 8)
            ol = zh("输出层\nd × |V|", 24).move_to(out)
            a = VGroup(Arrow(vocab.get_right(), body.get_left(), color=GREY_B), Arrow(body.get_right(), out.get_left(), color=GREY_B))
            self.play(FadeIn(vocab), FadeIn(vl), FadeIn(body), FadeIn(bl), FadeIn(out), FadeIn(ol), GrowArrow(a[0]), GrowArrow(a[1]))
            self.g = VGroup(vocab, vl, body, bl, out, ol, a)

        with self.voice("why_2"):
            self.play(FadeOut(self.g))
            t = zh("嵌入 + 输出层占总参数的比例（表 2.1）", 28, YELLOW).to_edge(UP, buff=0.5)
            rows = [("Gemma 4 E2B", 59.80), ("Gemma 4 E4B", 47.15), ("Qwen3.5 0.8B", 32.90), ("Qwen3.5 9B", 22.12),
                    ("Ministral 3 8B", 12.65), ("gpt-oss-20b", 5.54), ("Gemma 4 31B", 4.59), ("gpt-oss-120b", 0.99)]
            ch = hbar_chart(rows, 60, width=6.5, colors=BLUE_C, fmt="{:.1f}%", label_font="DejaVu Sans")
            ch.move_to(ORIGIN).shift(RIGHT * 1.0 + DOWN * 0.3)
            self.play(Write(t), FadeIn(ch[0]))
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in ch[1]], lag_ratio=0.1), run_time=2.5)
            self.play(FadeIn(ch[2]))
            self.play(Indicate(VGroup(ch[0][0], ch[1][0], ch[2][0]), color=YELLOW))

        with self.voice("why_3"):
            self.clear(run_time=0.5)
            s = mono("sample sentence", 34).shift(UP * 2.5)
            cands = VGroup(toks(["sample", f"{SP}sent", "ence"], 24), toks(["sa", "m", "ple", f"{SP}sent", "en", "ce"], 24),
                           toks(["sample", f"{SP}se", "nt", "en", "ce"], 24), mono("…", 30))
            cands.arrange(DOWN, buff=0.35).shift(DOWN * 0.2)
            arrows = VGroup(*[Arrow(s.get_bottom(), c.get_top(), buff=0.1, color=GREY_D, stroke_width=2) for c in cands[:3]])
            self.play(FadeIn(s))
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(c)) for a, c in zip(arrows, cands)], lag_ratio=0.4),
                      FadeIn(cands[3]))
            f = mono("p(s) = Σ p(t),  t ∈ T(s)", 32, YELLOW).to_edge(DOWN, buff=0.6)
            self.play(Write(f))
            self.cands, self.f = cands, f

        with self.voice("why_4"):
            canon = SurroundingRectangle(self.cands[0], color=OK, buff=0.08)
            cl = zh("标准切分（近似）", 22, OK).next_to(canon, RIGHT, buff=0.3)
            self.play(Create(canon), FadeIn(cl))
            self.play(self.cands[1:].animate.set_opacity(0.3))

        with self.voice("why_5"):
            self.clear(run_time=0.5)
            t = zh("*CL 会议中提到分词的摘要（每千篇，图 2.1）", 26, YELLOW).to_edge(UP, buff=0.5)
            years = [2020, 2021, 2022, 2023, 2024, 2025]
            vals = [6.4, 6.8, 12.5, 12.9, 14, 20.3]
            base = -2.4
            bars, labs, nums = VGroup(), VGroup(), VGroup()
            for i, (y, v) in enumerate(zip(years, vals)):
                b = Rectangle(width=1.0, height=v * 0.22, fill_color=TEAL, fill_opacity=0.85, stroke_width=0)
                b.move_to([-4.5 + i * 1.8, base + b.height / 2, 0])
                bars.add(b)
                labs.add(Text(str(y), font_size=20).next_to(b, DOWN, buff=0.15).set_y(base - 0.25))
                nums.add(Text(f"{v:g}", font_size=22).next_to(b, UP, buff=0.1))
            self.play(Write(t), FadeIn(labs))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), run_time=2)
            self.play(FadeIn(nums))
            note = VGroup(zh("2025 年至多", 24, GREY_B), zh("≈ 2%", 40, BAD)).arrange(RIGHT, buff=0.2).move_to(LEFT * 3 + UP * 1.6)
            self.play(Write(note))
        self.clear()


# ====================================================================== 5 BPE
BPE_WORDS = [("low", 5), ("lower", 2), ("newest", 6), ("widest", 3)]
BPE_STEPS = [  # 真实运行的前 5 次合并（并列时取先出现者）
    ("e", "s", 9),
    ("es", "t", 9),
    ("est", "_", 9),
    ("l", "o", 7),
    ("lo", "w", 7),
]


def apply_merge(seq, a, b):
    out, i = [], 0
    while i < len(seq):
        if i < len(seq) - 1 and seq[i] == a and seq[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(seq[i])
            i += 1
    return out


class S05_BPE(VoiceScene):
    def construct(self):
        with self.voice("bpe_1"):
            t = Text("Byte-Pair Encoding", font_size=56, weight=BOLD, color=BLUE_B)
            s = VGroup(zh("1994：数据压缩", 26, GREY_B), Arrow(ORIGIN, RIGHT, color=GREY_B),
                       zh("2016：子词分词", 26, YELLOW)).arrange(RIGHT, buff=0.3).next_to(t, DOWN, buff=0.6)
            self.play(Write(t))
            self.play(FadeIn(s))
            self.g = VGroup(t, s)

        with self.voice("bpe_2"):
            self.play(self.g.animate.scale(0.5).to_corner(UL))
            loop = VGroup(zh("① 统计相邻符号对", 28), zh("② 合并最常见的一对", 28, YELLOW),
                          zh("③ 加入词表，重复", 28)).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
            self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.2) for x in loop], lag_ratio=0.5), run_time=3)
            back = CurvedArrow(loop[2].get_right() + RIGHT * 0.3, loop[0].get_right() + RIGHT * 0.3, angle=PI / 1.5, color=GREY_B)
            self.play(Create(back))
            self.loop = VGroup(loop, back)

        seqs = [list(w) + ["_"] for w, _ in BPE_WORDS]

        def build_rows(seqs_):
            rows = VGroup()
            for (w, c), sq in zip(BPE_WORDS, seqs_):
                r = VGroup(toks(sq, 24, 0.05), Text(f"× {c}", font_size=24, color=GREY_B))
                r.arrange(RIGHT, buff=0.4)
                rows.add(r)
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(LEFT * 2.6 + DOWN * 0.3)
            return rows

        with self.voice("bpe_3"):
            self.play(FadeOut(self.loop))
            rows = build_rows(seqs)
            mt = zh("合并表", 26, YELLOW).move_to(RIGHT * 4.2 + UP * 2.2)
            self.play(FadeIn(rows), FadeIn(mt))
            # 高亮 e s
            hl = VGroup()
            for r, sq in zip(rows, seqs):
                for i in range(len(sq) - 1):
                    if sq[i] == "e" and sq[i + 1] == "s":
                        hl.add(SurroundingRectangle(VGroup(r[0][i], r[0][i + 1]), color=YELLOW, buff=0.04))
            cnt = zh("e + s：6 + 3 = 9 次", 26, YELLOW).next_to(rows, DOWN, buff=0.5)
            self.play(Create(hl), FadeIn(cnt))
            seqs = [apply_merge(s, "e", "s") for s in seqs]
            new_rows = build_rows(seqs)
            m1 = mono("1. e s → es", 24).next_to(mt, DOWN, buff=0.3).align_to(mt, LEFT)
            self.play(FadeOut(hl), FadeOut(cnt), Transform(rows, new_rows), FadeIn(m1))
            self.rows, self.mt, self.mlist = rows, mt, VGroup(m1)

        with self.voice("bpe_4"):
            for k, (a, b, n) in enumerate(BPE_STEPS[1:], start=2):
                seqs = [apply_merge(s, a, b) for s in seqs]
                new_rows = build_rows(seqs)
                m = mono(f"{k}. {a} {b} → {a + b}", 24).next_to(self.mlist[-1], DOWN, buff=0.2).align_to(self.mt, LEFT)
                self.play(Transform(self.rows, new_rows), FadeIn(m, shift=LEFT * 0.2), run_time=1.0)
                self.mlist.add(m)
                self.wait(0.4)

        with self.voice("bpe_5"):
            self.play(FadeOut(self.rows))
            seq = list("lowest") + ["_"]
            lab = zh("新词：lowest", 26).move_to(LEFT * 2.6 + UP * 1.6)
            cur = toks(seq, 30, 0.05).move_to(LEFT * 2.6 + UP * 0.6)
            self.play(FadeIn(lab), FadeIn(cur))
            for k, (a, b, _) in enumerate(BPE_STEPS):
                seq = apply_merge(seq, a, b)
                nxt = toks(seq, 30, 0.05).move_to(cur)
                self.play(Indicate(self.mlist[k], color=YELLOW, scale_factor=1.1), Transform(cur, nxt), run_time=0.8)
            res = VGroup(zh("结果：", 26), toks(["low", "est_"], 30)).arrange(RIGHT, buff=0.3).next_to(cur, DOWN, buff=0.8)
            self.play(FadeIn(res))
            self.res = VGroup(lab, cur, res)

        with self.voice("bpe_6"):
            self.clear(run_time=0.5)
            a = VGroup(zh("字符级 BPE", 30), zh("2016", 22, GREY_B)).arrange(DOWN)
            b = VGroup(zh("字节级 BPE", 30, YELLOW), zh("GPT-2 · 2019", 22, GREY_B)).arrange(DOWN)
            VGroup(a, b).arrange(RIGHT, buff=2.5).shift(UP * 0.5)
            arr = Arrow(a.get_right(), b.get_left(), color=WHITE)
            self.play(FadeIn(a))
            self.play(GrowArrow(arr), FadeIn(b))
            d = zh("今天的事实标准：无未登录词", 28, OK).next_to(VGroup(a, b), DOWN, buff=0.8)
            self.play(Write(d))
        self.clear()


# ====================================================================== 6 BPE 变体
class S06_BPEVariants(VoiceScene):
    def construct(self):
        with self.voice("bpev_1"):
            t = section_title("BPE 的变体")
            probs = VGroup(token_box("垃圾词元", RED_E, 28), token_box("破坏语素边界", RED_E, 28),
                           token_box("不能跨越空格", RED_E, 28), token_box("语言不公平", RED_E, 28)).arrange(RIGHT, buff=0.4)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in probs], lag_ratio=0.3))
            self.play(Indicate(probs[0], color=YELLOW))
            self.t, self.probs = t, probs

        with self.voice("bpev_2"):
            self.play(FadeOut(self.probs))
            s1 = toks(["K", "e", "n", "t", "u", "c", "k", "y"], 30, 0.05)
            s2 = toks(["K", "entucky"], 30, 0.05)
            s3 = toks(["Kentucky"], 30)
            VGroup(s1, s2, s3).arrange(DOWN, buff=0.6)
            self.play(FadeIn(s1))
            self.play(TransformFromCopy(s1, s2))
            self.play(TransformFromCopy(s2, s3))
            junk = SurroundingRectangle(s2[1], color=BAD, buff=0.06)
            jl = zh("中间产物：之后几乎用不到，嵌入训练不足", 24, BAD).next_to(s3, DOWN, buff=0.6)
            self.play(Create(junk), Write(jl))
            self.g = VGroup(s1, s2, s3, junk, jl)

        with self.voice("bpev_3"):
            self.play(FadeOut(self.g))
            f = VGroup(zh("自身交并比 IoS(x) =", 30), mono("freq(x, y) / freq(x)", 30, YELLOW)).arrange(RIGHT, buff=0.3)
            f.shift(UP * 1)
            th = VGroup(zh("IoS > 0.9", 30, BAD), Arrow(ORIGIN, RIGHT, color=GREY_B), zh("移除词元", 30)).arrange(RIGHT, buff=0.3)
            th.next_to(f, DOWN, buff=0.8)
            names = zh("PickyBPE · ScaffoldBPE · 词表裁剪", 26, GREY_B).next_to(th, DOWN, buff=0.8)
            self.play(Write(f))
            self.play(FadeIn(th))
            self.play(FadeIn(names))
            self.g = VGroup(f, th, names)

        with self.voice("bpev_4"):
            self.play(FadeOut(self.g))
            bad = VGroup(zh("早期合并", 24, GREY_B), toks(["unh", "appy"], 30)).arrange(RIGHT, buff=0.4)
            good = VGroup(zh("语素边界", 24, GREY_B), toks(["un", "happy"], 30)).arrange(RIGHT, buff=0.4)
            VGroup(bad, good).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
            x = Text("✘", font_size=34, color=BAD).next_to(bad, RIGHT)
            ck = Text("✔", font_size=34, color=OK).next_to(good, RIGHT)
            self.play(FadeIn(bad), FadeIn(x))
            ko = zh("BPE-knockout：借助语素数据删除有害合并", 26, YELLOW).to_edge(DOWN, buff=1.0)
            self.play(Write(ko))
            self.play(FadeIn(good), FadeIn(ck))
            note = zh("（示意例子）", 18, GREY_B).to_corner(DR)
            self.play(FadeIn(note))
            self.g = VGroup(bad, good, x, ck, ko, note)

        with self.voice("bpev_5"):
            self.play(FadeOut(self.g))
            a = VGroup(zh("常规", 24, GREY_B), toks([f"{SP}New", f"{SP}York"], 30), toks([f"{SP}of", f"{SP}the"], 30)).arrange(RIGHT, buff=0.5)
            b = VGroup(zh("超词", 24, YELLOW), toks([f"{SP}New{SP}York"], 30, colors=[GOLD_E]),
                       toks([f"{SP}of{SP}the"], 30, colors=[GOLD_E])).arrange(RIGHT, buff=0.5)
            VGroup(a, b).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
            self.play(FadeIn(a))
            self.play(FadeIn(b, shift=UP * 0.2))
            names = zh("SuperBPE · BoundlessBPE：更高压缩率，更好的下游效果", 24, GREY_B).to_edge(DOWN, buff=1.0)
            self.play(FadeIn(names))
            self.g = VGroup(a, b, names)

        with self.voice("bpev_6"):
            self.play(FadeOut(self.g))
            langs = ["英语", "法语", "印地语", "斯瓦希里语"]
            vals = [4.2, 3.9, 2.1, 1.8]
            bars = VGroup()
            for i, (l, v) in enumerate(zip(langs, vals)):
                b = Rectangle(width=1.1, height=v, fill_color=BLUE_C, fill_opacity=0.8, stroke_width=0)
                b.move_to([-3 + i * 2, -2.3 + v / 2, 0])
                bars.add(VGroup(b, zh(l, 22).next_to(b, DOWN, buff=0.15).set_y(-2.6)))
            yl = zh("压缩率（示意）", 22, GREY_B).to_corner(UL, buff=0.9).shift(DOWN * 0.3)
            self.play(FadeIn(bars), FadeIn(yl))
            pick = SurroundingRectangle(bars[3], color=YELLOW)
            pl = zh("每轮先照顾压缩最差的语言", 26, YELLOW).to_edge(UP, buff=1.2).shift(RIGHT * 1.5)
            self.play(Create(pick), FadeIn(pl))
            self.play(bars[3][0].animate.stretch_to_fit_height(2.9, about_edge=DOWN),
                      bars[2][0].animate.stretch_to_fit_height(2.9, about_edge=DOWN), run_time=1.5)
            nm = zh("Parity-aware BPE", 28).next_to(pl, DOWN, buff=0.2)
            self.play(FadeIn(nm))
        self.clear()


# ====================================================================== 7 Unigram / WordPiece
class S07_Unigram(VoiceScene):
    def construct(self):
        with self.voice("uni_1"):
            l = VGroup(zh("BPE", 34, BLUE_B), zh("自底向上：合并", 24)).arrange(DOWN)
            r = VGroup(zh("Unigram", 34, TEAL_B), zh("自顶向下：修剪", 24)).arrange(DOWN)
            VGroup(l, r).arrange(RIGHT, buff=3).shift(UP * 2)
            up = VGroup(*[Rectangle(width=0.5 + 0.5 * i, height=0.35, fill_color=BLUE_D, fill_opacity=0.6, stroke_width=1)
                          for i in range(5)]).arrange(UP, buff=0.08).next_to(l, DOWN, buff=0.5)
            dn = VGroup(*[Rectangle(width=3 - 0.5 * i, height=0.35, fill_color=TEAL_D, fill_opacity=0.6, stroke_width=1)
                          for i in range(5)]).arrange(DOWN, buff=0.08).next_to(r, DOWN, buff=0.5)
            self.play(FadeIn(l), FadeIn(r))
            self.play(LaggedStart(*[FadeIn(x) for x in up], lag_ratio=0.2), LaggedStart(*[FadeIn(x) for x in dn], lag_ratio=0.2),
                      run_time=2.5)

        with self.voice("uni_2"):
            self.clear(run_time=0.5)
            cand = VGroup(*[tok(t, TEAL_D, 22) for t in
                            ["un", "fold", "ing", "unf", "old", "ol", "fo", "unfold", "ldi", "lding", "foldi", "u", "n"]])
            cand.arrange_in_grid(3, 5, buff=0.2).shift(UP * 1)
            em = VGroup(token_box("E：期望计数", BLUE_D, 24), token_box("M：更新概率", BLUE_D, 24),
                        token_box("修剪损失最小的", RED_E, 24)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.6)
            arrs = VGroup(*[Arrow(em[i].get_right(), em[i + 1].get_left(), buff=0.05, color=GREY_B) for i in range(2)])
            self.play(FadeIn(cand))
            self.play(FadeIn(em), GrowArrow(arrs[0]), GrowArrow(arrs[1]))
            for i in [3, 5, 8, 10]:
                self.play(cand[i].animate.set_opacity(0.15), run_time=0.5)
            self.g = VGroup(cand, em, arrs)

        with self.voice("uni_3"):
            self.play(FadeOut(self.g))
            w = mono("unfolding", 34).shift(UP * 2)
            best = toks(["un", "fold", "ing"], 30)
            p = mono("P = p(un)·p(fold)·p(ing)", 26, YELLOW)
            VGroup(best, p).arrange(DOWN, buff=0.4)
            vi = zh("维特比：概率最大的切法", 26, TEAL_B).to_edge(DOWN, buff=1.2)
            self.play(FadeIn(w))
            self.play(FadeIn(best), Write(p))
            self.play(FadeIn(vi))
            samp = zh("也可以按概率随机采样", 24, GREY_B).next_to(vi, DOWN, buff=0.3)
            self.play(FadeIn(samp))

        with self.voice("uni_4"):
            self.clear(run_time=0.5)
            t = section_title("WordPiece")
            f = mono("score(x, y) = P(x, y) / ( P(x) · P(y) )", 32, YELLOW)
            n = zh("像点互信息，而不是频率", 26, GREY_B).next_to(f, DOWN, buff=0.5)
            self.play(Write(t), Write(f))
            self.play(FadeIn(n))

        with self.voice("uni_5"):
            self.clear(run_time=0.5)
            rows = VGroup(
                VGroup(token_box("BERT 推理", BLUE_D, 24), zh("贪心最长匹配，只需词表", 24)).arrange(RIGHT, buff=0.4),
                VGroup(token_box("Hugging Face 训练", BLUE_D, 24), zh("内部跑的是 BPE", 24)).arrange(RIGHT, buff=0.4),
                VGroup(token_box("TensorFlow 训练", BLUE_D, 24), zh("自顶向下拆分", 24)).arrange(RIGHT, buff=0.4),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), run_time=3)
            fam = zh("“WordPiece” 是一个算法家族", 28, YELLOW).to_edge(DOWN, buff=1)
            self.play(Write(fam))

        with self.voice("uni_6"):
            self.clear(run_time=0.5)
            cards = VGroup(*[VGroup(token_box(n, c, 28), zh(d, 22, GREY_B)).arrange(DOWN, buff=0.25)
                             for n, c, d in [("SaGe", PURPLE_D, "考虑上下文"), ("VOLT", GOLD_E, "最优传输"),
                                             ("ConvexTok", TEAL_D, "整数线性规划")]]).arrange(RIGHT, buff=1.2)
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.5), run_time=3)
        self.clear()


# ====================================================================== 8 推理算法（例 3.3 / 图 3.2）
class S08_Inference(VoiceScene):
    def construct(self):
        chars = "abcdefg"
        xs = np.linspace(-4.5, 4.5, 8)
        y0 = 0.2

        def span(i, j, color, label, up):
            p1, p2 = np.array([xs[i], y0, 0]), np.array([xs[j], y0, 0])
            ang = (-1.6 if j - i <= 4 else -1.1) * (1 if up else -1)
            arc = ArcBetweenPoints(p1, p2, angle=ang, color=color, stroke_width=4)
            mid = arc.point_from_proportion(0.5)
            t = mono(label, 22, color).move_to(mid + (UP if up else DOWN) * 0.28)
            return VGroup(arc, t)

        with self.voice("inf_1"):
            t = section_title("同一个词表，不同的切法")
            nodes = VGroup(*[Dot([x, y0, 0], radius=0.07) for x in xs])
            nums = VGroup()
            letters = VGroup(*[mono(c, 26).move_to([(xs[i] + xs[i + 1]) / 2, y0 + 0.22, 0]) for i, c in enumerate(chars)])
            base = VGroup(*[Line(nodes[i].get_center(), nodes[i + 1].get_center(), color=GREY_D) for i in range(7)])
            vocab = VGroup(zh("词表：", 22, GREY_B), mono("a b c d e f g  abc  abcd  bcdef  defg", 22)).arrange(RIGHT, buff=0.2)
            vocab.to_edge(UP, buff=1.2)
            self.play(Write(t), FadeIn(nodes), FadeIn(nums), Create(base), FadeIn(letters))
            self.play(FadeIn(vocab))
            arcs = VGroup(span(0, 3, BLUE_C, "abc", True), span(0, 4, TEAL_C, "abcd", False),
                          span(1, 6, PURPLE_B, "bcdef", False), span(3, 7, GOLD, "defg", True))
            self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), run_time=2)
            self.arcs = arcs
            self.results = VGroup()

        def result(name, pieces, color, idx):
            r = VGroup(zh(name, 24, color), toks(pieces, 22, 0.05)).arrange(RIGHT, buff=0.3)
            r.move_to(LEFT * 3.0 + UP * (-1.75 - 0.55 * idx), aligned_edge=LEFT)
            return r

        with self.voice("inf_2"):
            self.play(*self.dim([0, 2, 3]))
            self.play(*self.dim([1], 1.0))
            r = result("MaxMatch", ["abcd", "e", "f", "g"], TEAL_C, 0)
            self.play(FadeIn(r))
            self.results.add(r)

        with self.voice("inf_3"):
            self.play(*self.dim([1]), *self.dim([2], 1.0))
            r = result("FLOTA", ["a", "bcdef", "g"], PURPLE_B, 1)
            self.play(FadeIn(r))
            self.results.add(r)

        with self.voice("inf_4"):
            self.play(*self.dim([2]), *self.dim([0, 3], 1.0))
            r = result("PathPiece", ["abc", "defg"], GOLD, 2)
            self.play(FadeIn(r))
            self.results.add(r)

        with self.voice("inf_5"):
            objs = VGroup(zh("最长前缀", 22, GREY_A), zh("最长词元", 22, GREY_A), zh("最少词元", 22, GREY_A))
            for o, r in zip(objs, self.results):
                o.next_to(r, RIGHT, buff=0.5).set_x(3.6, LEFT)
            self.play(LaggedStart(*[FadeIn(o) for o in objs], lag_ratio=0.4), run_time=2)

        with self.voice("inf_6"):
            self.clear(run_time=0.5)
            t = section_title("随机分词：BPE-dropout")
            w = mono("unrelated", 32).shift(UP * 1.6)
            samples = VGroup(toks(["un", "related"], 26), toks(["un", "rel", "ated"], 26), toks(["unre", "lat", "ed"], 26))
            samples.arrange(DOWN, buff=0.35).shift(DOWN * 0.3)
            self.play(Write(t), FadeIn(w))
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in samples], lag_ratio=0.5), run_time=2)
            da = zh("像图像旋转、裁剪一样的数据增强", 26, YELLOW).to_edge(DOWN, buff=0.8)
            self.play(Write(da))
            note = zh("（示意切分）", 18, GREY_B).to_corner(DR)
            self.play(FadeIn(note))
        self.clear()


    def dim(self, idx, v=0.2):
        return [a for i in idx for a in (self.arcs[i][0].animate.set_stroke(opacity=v), self.arcs[i][1].animate.set_opacity(v))]


# ====================================================================== 9 预分词
class S09_Pretokenization(VoiceScene):
    def construct(self):
        with self.voice("pre_1"):
            t = section_title("预分词")
            url = mono("youtube.com/watch?v=dQw4w9WgXcQ", 32).shift(UP * 0.8)
            parts = VGroup(*[mono(f"[{p}]", 24, TEAL_B) for p in
                             ["youtube", ".", "com", "/", "watch", "?", "v", "=", "dQw4w9WgXcQ"]]).arrange(RIGHT, buff=0.04)
            parts.next_to(url, DOWN, buff=0.8)
            self.play(Write(t), FadeIn(url))
            self.play(TransformFromCopy(url, parts))

        with self.voice("pre_2"):
            self.clear(run_time=0.5)
            raw = mono("What a week, huh?", 34).shift(UP * 1.4)
            pre = VGroup(*[mono(f"[{p}]", 30, TEAL_B) for p in ["What", f"{SP}a", f"{SP}week", ",", f"{SP}huh", "?"]])
            pre.arrange(RIGHT, buff=0.06)
            self.play(FadeIn(raw))
            self.play(TransformFromCopy(raw, pre))
            conv = VGroup(VGroup(zh("SentencePiece", 22, GREY_B), mono(f"{SP}week", 26)).arrange(RIGHT, buff=0.3),
                          VGroup(zh("GPT 系列", 22, GREY_B), mono("Ġweek", 26)).arrange(RIGHT, buff=0.3),
                          VGroup(zh("BERT", 22, GREY_B), mono("sent ##ence", 26)).arrange(RIGHT, buff=0.3)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(conv))

        with self.voice("pre_3"):
            self.clear(run_time=0.5)
            g2 = VGroup(zh("GPT-2", 26, BLUE_B), mono(r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+|…", 20)).arrange(DOWN, buff=0.2)
            g4 = VGroup(zh("GPT-4", 26, BLUE_B), mono(r"(?i:'s|'t|'re|…)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}|…", 20)).arrange(DOWN, buff=0.2)
            VGroup(g2, g4).arrange(DOWN, buff=0.7)
            self.play(FadeIn(g2))
            self.play(FadeIn(g4))
            hl = zh("数字最多三位一组", 24, YELLOW).next_to(g4, DOWN, buff=0.4)
            self.play(FadeIn(hl))
            edge = zh("更复杂 → 更多意想不到的边角情况", 24, BAD).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(edge))

        with self.voice("pre_4"):
            self.clear(run_time=0.5)
            n = mono("8675309", 48).shift(UP * 2.3)
            rows = VGroup(
                VGroup(zh("GPT-2", 24, GREY_B), toks(["86", "75", "309"], 30)).arrange(RIGHT, buff=0.5),
                VGroup(zh("Llama 2", 24, GREY_B), toks(list("8675309"), 30, 0.05)).arrange(RIGHT, buff=0.5),
                VGroup(zh("GPT-3.5 / Llama 3", 24, GREY_B), toks(["867", "530", "9"], 30)).arrange(RIGHT, buff=0.5),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).shift(DOWN * 0.3)
            for r in rows:
                r[1].set_x(1.5, LEFT)
            self.play(FadeIn(n))
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(0.6)
            self.rows, self.n = rows, n

        with self.voice("pre_5"):
            tail = SurroundingRectangle(self.rows[2][1][2], color=BAD, buff=0.05)
            self.play(Create(tail))
            rtl = VGroup(zh("从右往左", 24, OK), toks(["8", "675", "309"], 30)).arrange(RIGHT, buff=0.5)
            rtl.next_to(self.rows, DOWN, buff=0.5).align_to(self.rows, LEFT)
            rtl[1].set_x(1.5, LEFT)
            self.play(FadeIn(rtl, shift=UP * 0.2))
            yr = VGroup(zh("年份", 22, GREY_B), toks(["2026"], 28), zh("还是", 22, GREY_B), toks(["202", "6"], 28)).arrange(RIGHT, buff=0.3)
            yr.to_edge(DOWN, buff=0.3)
            self.play(FadeIn(yr))

        with self.voice("pre_6"):
            self.clear(run_time=0.5)
            s = zh("私は日本語を学ぶ。", 40).shift(UP * 2)
            bad = VGroup(zh("不加处理", 22, GREY_B), toks(["私は", "日本", "語を", "学ぶ", "。"], 30, font="Noto Sans CJK SC")).arrange(RIGHT, buff=0.4)
            good = VGroup(zh("形态分析后", 22, GREY_B), toks(["私", "は", "日本", "語", "を", "学ぶ", "。"], 30, font="Noto Sans CJK SC")).arrange(RIGHT, buff=0.4)
            VGroup(bad, good).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
            self.play(FadeIn(s))
            self.play(FadeIn(bad))
            self.play(Circumscribe(bad[1][2], color=BAD))
            self.play(FadeIn(good))
            mec = zh("MeCab · Juman++ · Sudachi", 22, GREY_B).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(mec))
        self.clear()


# ====================================================================== 10 文字系统
UDHR = [("英语", "Latin", 12321, 12333), ("俄语", "Cyrillic", 13493, 23416), ("中文", "Han", 4676, 10256),
        ("韩语", "Hangul", 6399, 13088), ("印地语", "Devanagari", 13165, 31565), ("阿姆哈拉语", "Ethiopic", 6393, 17223)]


class S10_Scripts(VoiceScene):
    def construct(self):
        with self.voice("scr_1"):
            t = section_title("UTF-8：变长编码")
            rows = VGroup(
                VGroup(mono("A", 34), mono("41", 26, TEAL_B), zh("1 字节", 22, GREY_B)),
                VGroup(Text("ж", font_size=34), mono("d0 b6", 26, TEAL_B), zh("2 字节", 22, GREY_B)),
                VGroup(zh("日", 34), mono("e6 97 a5", 26, TEAL_B), zh("3 字节", 22, GREY_B)),
                VGroup(Text("व", font="Noto Sans Devanagari", font_size=34), mono("e0 a4 b5", 26, TEAL_B), zh("3 字节", 22, GREY_B)),
            )
            for r in rows:
                r.arrange(RIGHT, buff=0.8)
                r[1].set_x(0)
                r[2].set_x(2.8)
                r[0].set_x(-2.5)
            rows.arrange(DOWN, buff=0.4)
            for r in rows:
                r[1].set_x(0)
                r[2].set_x(2.8)
                r[0].set_x(-2.5)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.3), run_time=2.5)

        chart = self._udhr()
        with self.voice("scr_2"):
            self.clear(run_time=0.5)
            t = zh("《世界人权宣言》：字符数 vs UTF-8 字节数（表 5.3）", 26, YELLOW).to_edge(UP, buff=0.4)
            lg = VGroup(VGroup(Square(0.25, fill_color=BLUE_C, fill_opacity=0.9, stroke_width=0), zh("字符", 20)).arrange(RIGHT, buff=0.1),
                        VGroup(Square(0.25, fill_color=ORANGE, fill_opacity=0.9, stroke_width=0), zh("字节", 20)).arrange(RIGHT, buff=0.1)
                        ).arrange(RIGHT, buff=0.5).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
            self.play(Write(t), FadeIn(lg), FadeIn(chart[0]))
            for i in (0, 1, 4):
                self.play(GrowFromEdge(chart[1][i], LEFT), GrowFromEdge(chart[2][i], LEFT), FadeIn(chart[3][i]), run_time=0.8)
                self.wait(0.8)
            self.chart = chart

        with self.voice("scr_3"):
            for i in (2, 3, 5):
                self.play(GrowFromEdge(self.chart[1][i], LEFT), GrowFromEdge(self.chart[2][i], LEFT), FadeIn(self.chart[3][i]),
                          run_time=0.7)
            self.play(Indicate(VGroup(self.chart[0][2], self.chart[1][2], self.chart[2][2]), color=YELLOW))

        with self.voice("scr_4"):
            self.clear(run_time=0.5)
            total = Rectangle(width=11, height=0.7, stroke_color=GREY_B).shift(UP * 0.6)
            used = Rectangle(width=11 * 1238 / 11172, height=0.7, fill_color=OK, fill_opacity=0.85, stroke_width=0)
            used.align_to(total, LEFT).set_y(total.get_y())
            l1 = zh("韩文音节：11,172 个", 28).next_to(total, UP, buff=0.3)
            l2 = zh("约 1,200 个覆盖维基百科 99.9% 的文本", 26, OK).next_to(total, DOWN, buff=0.3).align_to(total, LEFT)
            self.play(Create(total), FadeIn(l1))
            self.play(GrowFromEdge(used, LEFT), FadeIn(l2))

        with self.voice("scr_5"):
            self.clear(run_time=0.5)
            han = VGroup(zh("人  仯  少", 40), zh("共享部件 人 · 小 · ノ", 22, GREY_B),
                         mono("e4 ba ba | e4 bb af | e5 b0 91", 22, TEAL_B)).arrange(DOWN, buff=0.3)
            kor = VGroup(zh("렷  럿  렀", 40), zh("共享字母 ㄹ · ㅓ · ㅅ", 22, GREY_B),
                         mono("eb a0 b7 | eb 9f bf | eb a0 80", 22, TEAL_B)).arrange(DOWN, buff=0.3)
            VGroup(han, kor).arrange(RIGHT, buff=1.5)
            self.play(FadeIn(han), FadeIn(kor))
            note = zh("字形结构相近，字节序列却毫无关联", 26, YELLOW).to_edge(DOWN, buff=0.8)
            self.play(Write(note))

        with self.voice("scr_6"):
            self.clear(run_time=0.5)
            t = section_title("非连续形态：闪米特语言")
            root = VGroup(*[mono(c, 48, YELLOW) for c in "ktb"]).arrange(RIGHT, buff=1.2).shift(UP * 1.0)
            rl = zh("辅音词根 k-t-b（书写）", 24, GREY_B).next_to(root, UP, buff=0.3)
            words = VGroup(mono("kataba", 36), mono("kitāb", 36), mono("maktūb", 36)).arrange(RIGHT, buff=1.0).shift(DOWN * 0.6)
            self.play(Write(t), FadeIn(rl), FadeIn(root))
            self.play(FadeIn(words))
            nc = zh("词元只能是连续子串 → 无法表达词根；SPLINTER 先重排字符", 24).to_edge(DOWN, buff=0.7)
            self.play(Write(nc))

        self.clear()

    def _udhr(self):
        labels, cbars, bbars, vals = VGroup(), VGroup(), VGroup(), VGroup()
        sc = 6.5 / 32000
        for i, (name, script, ch, by) in enumerate(UDHR):
            y = 2.0 - i * 0.82
            labels.add(VGroup(zh(name, 22), Text(script, font_size=16, color=GREY_B)).arrange(DOWN, buff=0.03)
                       .next_to([-3.2, y, 0], LEFT, buff=0.2))
            c = Rectangle(width=ch * sc, height=0.26, fill_color=BLUE_C, fill_opacity=0.9, stroke_width=0)
            c.move_to([-3.2 + c.width / 2, y + 0.15, 0])
            b = Rectangle(width=by * sc, height=0.26, fill_color=ORANGE, fill_opacity=0.9, stroke_width=0)
            b.move_to([-3.2 + b.width / 2, y - 0.15, 0])
            cbars.add(c)
            bbars.add(b)
            vals.add(Text(f"{ch:,} / {by:,}", font_size=18).next_to(b, RIGHT, buff=0.15).set_y(y))
        return VGroup(labels, cbars, bbars, vals)


# ====================================================================== 11 多语言与词元税
class S11_Multilingual(VoiceScene):
    def construct(self):
        with self.voice("ml_1"):
            t = section_title("多语言：词表分配偏差")
            pie_data = [("英语", 0.46, BLUE_C), ("其他高资源", 0.34, TEAL_D), ("中资源", 0.14, GREEN_D), ("低资源", 0.06, RED_D)]
            start = PI / 2
            pie = VGroup()
            for name, v, col in pie_data:
                ang = -TAU * v
                s = AnnularSector(inner_radius=0, outer_radius=2.0, angle=ang, start_angle=start, fill_color=col,
                                  fill_opacity=0.85, stroke_color=BLACK, stroke_width=2)
                mid = start + ang / 2
                lab = zh(name, 20).move_to(2.6 * np.array([np.cos(mid), np.sin(mid), 0]))
                pie.add(VGroup(s, lab))
                start += ang
            pie.shift(DOWN * 0.4)
            note = zh("（示意）", 18, GREY_B).to_corner(DR)
            self.play(Write(t), LaggedStart(*[FadeIn(p) for p in pie], lag_ratio=0.3), FadeIn(note), run_time=2.5)

        with self.voice("ml_2"):
            self.clear(run_time=0.5)
            blk = lambda n, w: VGroup(*[RoundedRectangle(corner_radius=0.05, width=w, height=0.45, fill_color=PALETTE[k % 8],
                                                          fill_opacity=0.6, stroke_color=PALETTE[k % 8]) for k in range(n)]).arrange(RIGHT, buff=0.06)
            a = VGroup(zh("高资源语言", 24, GREY_B), blk(3, 1.6)).arrange(RIGHT, buff=0.4)
            b = VGroup(zh("低资源语言", 24, GREY_B), blk(9, 0.48)).arrange(RIGHT, buff=0.4)
            VGroup(a, b).arrange(DOWN, buff=0.6, aligned_edge=LEFT).shift(UP * 1.0)
            sm = zh("同一句话（示意）", 22, GREY_B).next_to(VGroup(a, b), UP, buff=0.3)
            self.play(FadeIn(sm), FadeIn(a))
            self.play(FadeIn(b))
            sq1 = Square(1.0, fill_color=BLUE_C, fill_opacity=0.6, stroke_width=1)
            sq2 = Square(2.0, fill_color=RED_C, fill_opacity=0.6, stroke_width=1)
            VGroup(sq1, sq2).arrange(RIGHT, buff=1.2, aligned_edge=DOWN).shift(DOWN * 1.8)
            l1 = zh("n 个词元", 20).next_to(sq1, DOWN, buff=0.1)
            l2 = zh("2n 个词元 → 注意力 ≈ 4 倍", 20, BAD).next_to(sq2, DOWN, buff=0.1)
            self.play(FadeIn(sq1), FadeIn(l1))
            self.play(GrowFromEdge(sq2, DOWN), FadeIn(l2))
            tax = zh("词元税", 40, BAD).next_to(sq2, RIGHT, buff=0.8)
            self.play(Write(tax))

        with self.voice("ml_3"):
            self.clear(run_time=0.5)
            t = zh("用 GPT-4o 生成《世界人权宣言》（图 6.2）", 28, YELLOW).to_edge(UP, buff=0.6)
            c1 = VGroup(zh("费用", 26, GREY_B), Text("3.8×", font_size=96, color=ORANGE), zh("缅甸语 vs 英语", 24)).arrange(DOWN, buff=0.25)
            c2 = VGroup(zh("折合劳动时间", 26, GREY_B), Text("54.3×", font_size=96, color=BAD), zh("缅甸 vs 美国", 24)).arrange(DOWN, buff=0.25)
            VGroup(c1, c2).arrange(RIGHT, buff=2.0).shift(DOWN * 0.3)
            self.play(Write(t))
            self.play(FadeIn(c1, shift=UP * 0.2))
            self.play(FadeIn(c2, shift=UP * 0.2))

        with self.voice("ml_4"):
            self.clear(run_time=0.5)
            t = zh("词表中中日韩词元的占比（表 5.2）", 28, YELLOW).to_edge(UP, buff=0.5)
            rows = [("GPT-2", 0.4), ("Llama 2", 3.0), ("GPT-OSS", 5.1), ("Llama 3", 5.8), ("Mistral-3.5", 7.2),
                    ("Gemma 3/4", 11.3), ("mBERT", 15.1), ("Qwen-3.5", 26.5), ("DeepSeek-v4", 29.1)]
            ch = hbar_chart(rows, 30, width=7, colors=TEAL, fmt="{:.1f}%", label_font="DejaVu Sans")
            ch.move_to(ORIGIN).shift(RIGHT * 0.8 + DOWN * 0.3)
            self.play(Write(t), FadeIn(ch[0]))
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in ch[1]], lag_ratio=0.12), run_time=3)
            self.play(FadeIn(ch[2]))
            self.play(Indicate(VGroup(ch[1][-2:], ch[0][-2:]), color=YELLOW))

        with self.voice("ml_5"):
            self.clear(run_time=0.5)
            items = [("按语言簇训练词表", "XLM-V"), ("优先压缩最差的语言", "Parity-aware BPE"),
                     ("字符 = 文字区块 + 索引", "SCRIPT"), ("按文字设定切分粒度", "MAGNET")]
            rows = VGroup(*[VGroup(token_box(n, BLUE_D, 22), zh(d, 24)).arrange(RIGHT, buff=0.4) for d, n in items])
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4), run_time=3)
        self.clear()


# ====================================================================== 12 评测
class S12_Evaluation(VoiceScene):
    def construct(self):
        with self.voice("eval_1"):
            t = section_title("如何评测分词器？")
            ext = VGroup(token_box("外部评测", BLUE_D, 30), zh("训练模型 → 看下游效果", 22, GREY_B)).arrange(DOWN, buff=0.3)
            ext.shift(LEFT * 3)
            cost = VGroup(zh("每次都要从头训练", 24, BAD), zh("受初始化、数据顺序等干扰", 24, BAD)).arrange(DOWN, buff=0.3)
            cost.next_to(ext, RIGHT, buff=1.2)
            self.play(Write(t), FadeIn(ext))
            self.play(FadeIn(cost))

        with self.voice("eval_2"):
            self.clear(run_time=0.5)
            s = mono("the same text", 30).shift(UP * 2.2)
            a = VGroup(toks(["the", "▁same", "▁text"], 24), mono("L = 6.0 / 3 = 2.0", 24)).arrange(RIGHT, buff=0.6)
            b = VGroup(toks(["th", "e", "▁sa", "me", "▁te", "xt"], 24), mono("L = 6.6 / 6 = 1.1", 24)).arrange(RIGHT, buff=0.6)
            VGroup(a, b).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(UP * 0.4)
            note = zh("（示意数值）切得越碎，每词元损失越低", 22, GREY_B).next_to(VGroup(a, b), DOWN, buff=0.3)
            self.play(FadeIn(s), FadeIn(a), FadeIn(b), FadeIn(note))
            f = VGroup(zh("每字节比特数", 28, YELLOW), mono("BPB = Σ −log p(tᵢ) / N_bytes", 28)).arrange(DOWN, buff=0.2)
            f.to_edge(DOWN, buff=0.5)
            self.play(Write(f))

        with self.voice("eval_3"):
            self.clear(run_time=0.5)
            tasks = [("数字母", "strawberry 里有几个 r？", "3"), ("拼写", "拼出 strawberry", "s t r a w b e r r y"),
                     ("替换", "把 r 都换成 z", "stzawbezzy")]
            rows = VGroup(*[VGroup(token_box(n, PURPLE_D, 22), zh(q, 24), mono("→ " + a, 22, OK)).arrange(RIGHT, buff=0.4)
                            for n, q, a in tasks]).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            hdr = zh("CUTE · CharBench：字母级任务", 28, YELLOW).to_edge(UP, buff=0.6)
            self.play(Write(hdr))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), run_time=3)

        with self.voice("eval_4"):
            self.clear(run_time=0.5)
            a = VGroup(mono("strawberry", 30), Arrow(ORIGIN, RIGHT * 0.8, color=GREY_B), toks(["strawberry"], 30)).arrange(RIGHT, buff=0.3)
            b = VGroup(mono("stzawbezzy", 30), Arrow(ORIGIN, RIGHT * 0.8, color=GREY_B),
                       toks(["st", "z", "aw", "be", "z", "zy"], 30)).arrange(RIGHT, buff=0.3)
            VGroup(a, b).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
            lab = zh("Llama 3 分词器", 24, GREY_B).to_edge(UP, buff=1.0)
            self.play(FadeIn(lab), FadeIn(a))
            self.play(FadeIn(b))
            self.play(Indicate(b[2], color=YELLOW))

        with self.voice("eval_5"):
            self.clear(run_time=0.5)
            t = section_title("内部评测：不用训练模型")
            ms = ["压缩率 / 词元数", "每词词元数（fertility）", "Rényi 效率", "语素对齐 F1", "认知合理性（阅读时间）", "跨语言 Gini 系数"]
            chips = VGroup(*[token_box(m, TEAL_D, 24) for m in ms]).arrange_in_grid(3, 2, buff=(0.6, 0.4))
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in chips], lag_ratio=0.25), run_time=3)
            self.chips = chips

        with self.voice("eval_6"):
            q = VGroup(zh("内部指标", 30), Text("⇄", font_size=40, color=YELLOW), zh("下游效果", 30)).arrange(RIGHT, buff=0.4)
            qm = Text("?", font_size=60, color=BAD).next_to(q, UP, buff=0.1)
            grp = VGroup(q, qm)
            grp.shift(DOWN * 2.6)
            self.play(self.chips.animate.shift(UP * 0.6).set_opacity(0.5))
            self.play(FadeIn(q), FadeIn(qm))
        self.clear()


# ====================================================================== 13 非标准切分
class S13_NonCanonical(VoiceScene):
    def construct(self):
        with self.voice("nc_1"):
            w = mono("tokenization", 36).shift(UP * 2.2)
            canon = VGroup(zh("标准", 22, OK), toks(["token", "ization"], 28)).arrange(RIGHT, buff=0.4)
            alts = VGroup(VGroup(zh("非标准", 22, GREY_B), toks(["token", "iz", "ation"], 28)).arrange(RIGHT, buff=0.4),
                          VGroup(zh("非标准", 22, GREY_B), toks(["to", "k", "en", "iz", "ation"], 28)).arrange(RIGHT, buff=0.4))
            alts.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            VGroup(canon, alts).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
            f = mono("最多 2^(n−1) 种切法", 30, YELLOW).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(w), FadeIn(canon))
            self.play(FadeIn(alts))
            self.play(Write(f))

        with self.voice("nc_2"):
            self.clear(run_time=0.5)
            t = zh("GPT-4 分词器（例 8.1）", 26, GREY_B).to_edge(UP, buff=0.6)
            rows = [("intelligence", [f"{SP}intelligence"], "[11478]"),
                    ("“intelligence”", ["“", "intelligence", "”"], "[330, 93375, 1]"),
                    ("intellegence", [f"{SP}intel", "leg", "ence"], "[14490, 1978, 768]")]
            g = VGroup(*[VGroup(mono(s, 26).set_width(3.6) if len(s) > 13 else mono(s, 26), toks(p, 24), mono(i, 20, GREY_A))
                         .arrange(RIGHT, buff=0.5) for s, p, i in rows]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
            for r in g:
                r[1].set_x(0.4, LEFT)
                r[2].next_to(r[1], RIGHT, buff=0.4)
            self.play(Write(t))
            for r in g:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(0.5)

        with self.voice("nc_3"):
            self.clear(run_time=0.5)
            img = Square(1.4, fill_color=BLUE_D, fill_opacity=0.6, stroke_color=BLUE_B)
            imgs = VGroup(img, img.copy().rotate(PI / 8), img.copy().scale(0.7)).arrange(RIGHT, buff=0.6)
            il = zh("图像：旋转、裁剪", 22, GREY_B).next_to(imgs, DOWN, buff=0.2)
            txt = VGroup(toks(["token", "ization"], 22), toks(["tok", "en", "ization"], 22), toks(["token", "iz", "ation"], 22))
            txt.arrange(DOWN, buff=0.2)
            tl = zh("文本：采样不同切法", 22, GREY_B).next_to(txt, DOWN, buff=0.2)
            left = VGroup(imgs, il)
            right = VGroup(txt, tl)
            VGroup(left, right).arrange(RIGHT, buff=1.5).shift(UP * 0.3)
            self.play(FadeIn(left))
            self.play(FadeIn(right))
            e = zh("ERNIE 5：预训练使用 BPE-dropout", 26, YELLOW).to_edge(DOWN, buff=0.7)
            self.play(Write(e))

        with self.voice("nc_4"):
            self.clear(run_time=0.5)
            f = mono("p(s) = Σ_{t ∈ T(s)} p(t)", 36, YELLOW).shift(UP * 1.6)
            h = VGroup(VGroup(zh("最可能的切法", 26), zh("NP 完全", 26, BAD)).arrange(RIGHT, buff=0.5),
                       VGroup(zh("精确边缘概率", 26), zh("#P 难", 26, BAD)).arrange(RIGHT, buff=0.5)).arrange(DOWN, buff=0.3)
            gap = zh("实证：与标准切分的差距通常 < 0.5%", 28, OK).to_edge(DOWN, buff=0.8)
            self.play(Write(f))
            self.play(FadeIn(h))
            self.play(Write(gap))
        self.clear()


# ====================================================================== 14 字节与隐式分词
class S14_ByteLatent(VoiceScene):
    def construct(self):
        with self.voice("byte_1"):
            t = section_title("直接在字节上建模")
            b = VGroup(token_box("ByT5", BLUE_D, 30), zh("100+ 种语言 · 噪声更鲁棒", 24, OK), zh("序列很长 · 训练推理慢", 24, BAD))
            b.arrange(DOWN, buff=0.35)
            self.play(Write(t), FadeIn(b))

        with self.voice("byte_2"):
            self.clear(run_time=0.5)
            inp = "_The_quick_brown"
            out = "_quick_brown_fox"
            xs = np.linspace(-5.6, 5.6, len(inp))
            bi = VGroup(*[mono(c, 22).move_to([x, -2.6, 0]) for c, x in zip(inp, xs)])
            bo = VGroup(*[mono(c, 22, TEAL_B).move_to([x, 2.6, 0]) for c, x in zip(out, xs)])
            enc = Rectangle(width=12, height=0.6, fill_color=BLUE_E, fill_opacity=0.5, stroke_color=BLUE_C).move_to([0, -1.8, 0])
            dec = enc.copy().set_fill(TEAL_E, 0.5).set_stroke(TEAL_C).move_to([0, 1.8, 0])
            el = zh("编码器（小）", 20).move_to(enc)
            dl = zh("解码器（小）", 20).move_to(dec)
            groups = [(0, 4), (4, 10), (10, 16)]
            lat = VGroup(*[Square(0.7, fill_color=YELLOW_E, fill_opacity=0.7, stroke_color=YELLOW)
                           .move_to([(xs[a] + xs[b - 1]) / 2, 0, 0]) for a, b in groups])
            glob = SurroundingRectangle(lat, color=YELLOW, buff=0.3)
            gl = zh("全局模块（大）· 隐式词元", 22, YELLOW).next_to(glob, RIGHT, buff=0.2).shift(LEFT * 3.5 + UP * 0.8)
            self.play(FadeIn(bi))
            self.play(FadeIn(enc), FadeIn(el))
            self.play(*[TransformFromCopy(VGroup(*bi[a:b]), lat[i]) for i, (a, b) in enumerate(groups)], run_time=1.5)
            self.play(Create(glob), FadeIn(gl))
            self.play(FadeIn(dec), FadeIn(dl))
            self.play(LaggedStart(*[FadeIn(c) for c in bo], lag_ratio=0.05), run_time=1.5)

        with self.voice("byte_3"):
            self.clear(run_time=0.5)
            t = zh("Byte Latent Transformer：按下一字节的熵切分", 28, YELLOW).to_edge(UP, buff=0.5)
            s = "The_quick_brown_fox"
            rng = np.random.default_rng(3)
            ent = [2.8, 1.2, 0.6, 2.6, 2.9, 1.4, 0.7, 0.5, 0.6, 2.7, 2.4, 1.1, 0.8, 0.6, 0.5, 2.8, 2.2, 0.9, 0.7]
            xs = np.linspace(-5.4, 5.4, len(s))
            bars = VGroup(*[Rectangle(width=0.4, height=e * 0.9, fill_color=TEAL if e < 2.0 else ORANGE, fill_opacity=0.85,
                                      stroke_width=0).move_to([x, -1.6 + e * 0.45, 0]) for e, x in zip(ent, xs)])
            chars = VGroup(*[mono(c, 22).move_to([x, -1.95, 0]) for c, x in zip(s, xs)])
            th = DashedLine([-6, -1.6 + 2.0 * 0.9, 0], [6, -1.6 + 2.0 * 0.9, 0], color=RED)
            tl = zh("阈值", 20, RED).next_to(th, RIGHT, buff=0.1).shift(LEFT * 0.8 + UP * 0.25)
            self.play(Write(t), FadeIn(chars))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.04), run_time=2)
            self.play(Create(th), FadeIn(tl))
            cuts = VGroup(*[DashedLine([x - 0.3, -2.3, 0], [x - 0.3, 2.0, 0], color=YELLOW, stroke_width=2)
                            for e, x in zip(ent, xs) if e >= 2.0])
            self.play(Create(cuts))
            note = zh("（示意熵值）", 18, GREY_B).to_corner(DR)
            self.play(FadeIn(note))

        with self.voice("byte_4"):
            self.clear(run_time=0.5)
            t = zh("同一句话，不同阈值（论文例 9.2）", 26, YELLOW).to_edge(UP, buff=0.6)
            rows = VGroup(
                VGroup(mono("2.5", 24, GREY_B), toks(["The_", "quick_", "brown_", "fox_", "jumped_over_the_", "lazy_", "dog."], 20)),
                VGroup(mono("2.0", 24, GREY_B), toks(["The_", "quick_", "brown_", "fox_", "jumped_", "over_", "the_", "lazy_", "dog."], 20)),
                VGroup(mono("1.5", 24, GREY_B), toks(["The_", "qui", "ck_", "b", "rown_", "f", "o", "x_", "jumped_", "over_", "the_", "la", "zy_", "d", "og", "."], 18, 0.04)),
            )
            for r in rows:
                r.arrange(RIGHT, buff=0.4)
            rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
            for r in rows:
                if r.width > 13:
                    r.scale_to_fit_width(13)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), run_time=3)
            h = zh("H-Net：自己学习边界，多层堆叠 → 语素 / 单词 / 短语", 24, TEAL_B).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(h))

        with self.voice("byte_5"):
            self.clear(run_time=0.5)
            a = VGroup(token_box("OLMo 3（BPE）", BLUE_D, 28), zh("已训练好的子词模型", 20, GREY_B)).arrange(DOWN)
            b = VGroup(token_box("Bolmo（字节级）", TEAL_D, 28), zh("边界预测器模仿 BPE 切分", 20, GREY_B)).arrange(DOWN)
            VGroup(a, b).arrange(RIGHT, buff=2.2)
            arr = Arrow(a.get_right(), b.get_left(), color=WHITE)
            al = zh("字节化", 24, YELLOW).next_to(arr, UP)
            self.play(FadeIn(a))
            self.play(GrowArrow(arr), FadeIn(al), FadeIn(b))
            c = zh("字母级任务 CUTE：明显超过原模型", 26, OK).to_edge(DOWN, buff=1.0)
            self.play(Write(c))

        with self.voice("byte_6"):
            self.clear(run_time=0.5)
            seq = VGroup(*[Square(0.45, fill_color=TEAL_D, fill_opacity=0.7, stroke_width=1) for _ in range(12)]).arrange(RIGHT, buff=0.05)
            seq.shift(UP * 0.8)
            sl = zh("逐字节生成：慢", 24, BAD).next_to(seq, UP, buff=0.3)
            self.play(FadeIn(sl))
            self.play(LaggedStart(*[FadeIn(s) for s in seq], lag_ratio=0.15), run_time=2.5)
            fast = zh("扩散 · 推测解码：并行生成一个片段", 26, YELLOW).shift(DOWN * 1.2)
            self.play(Write(fast))
        self.clear()


# ====================================================================== 15 视觉表示
class S15_Visual(VoiceScene):
    def construct(self):
        with self.voice("vis_1"):
            txt = zh("My cat enjoys eating warm oatmeal.", 32)
            img = Rectangle(width=txt.width + 0.6, height=1.2, fill_color=WHITE, fill_opacity=1, stroke_width=0)
            rend = Text("My cat enjoys eating warm oatmeal.", font="DejaVu Serif", font_size=30, color=BLACK).move_to(img)
            grp = VGroup(img, rend).shift(DOWN * 0.8)
            txt.shift(UP * 1.6)
            self.play(FadeIn(txt))
            self.play(TransformFromCopy(txt, grp))
            n = int(img.width / 0.6)
            grid = VGroup(*[Line([img.get_left()[0] + k * img.width / n, img.get_top()[1], 0],
                                 [img.get_left()[0] + k * img.width / n, img.get_bottom()[1], 0], color=RED, stroke_width=1.5)
                            for k in range(1, n)])
            self.play(Create(grid))
            no = zh("没有词表 → 没有未登录词", 26, OK).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(no))

        with self.voice("vis_2"):
            self.clear(run_time=0.5)
            p = VGroup(token_box("PIXEL", PURPLE_D, 34), zh("完全基于渲染文本预训练", 24, GREY_B),
                       zh("迁移到未见过的文字：大幅超过 BERT", 24, OK), zh("对字形扰动更鲁棒", 24, OK)).arrange(DOWN, buff=0.35)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in p], lag_ratio=0.4), run_time=3)

        with self.voice("vis_3"):
            self.clear(run_time=0.5)
            t = token_box("DeepSeek-OCR", BLUE_D, 30).to_edge(UP, buff=0.8)
            a = VGroup(Text("10×", font_size=90, color=YELLOW), zh("压缩率", 24, GREY_B)).arrange(DOWN)
            b = VGroup(Text("97%", font_size=90, color=OK), zh("还原准确率", 24, GREY_B)).arrange(DOWN)
            VGroup(a, b).arrange(RIGHT, buff=2.5)
            self.play(FadeIn(t))
            self.play(FadeIn(a, shift=UP * 0.2))
            self.play(FadeIn(b, shift=UP * 0.2))

        with self.voice("vis_4"):
            self.clear(run_time=0.5)
            l = VGroup(Text("o", font="DejaVu Sans", font_size=120), mono("U+006F", 24, GREY_B), zh("拉丁字母", 22)).arrange(DOWN, buff=0.2)
            c = VGroup(Text("о", font="DejaVu Sans", font_size=120), mono("U+043E", 24, GREY_B), zh("西里尔字母", 22)).arrange(DOWN, buff=0.2)
            VGroup(l, c).arrange(RIGHT, buff=3)
            eq = Text("=", font_size=80, color=BAD).move_to(VGroup(l[0], c[0]).get_center())
            self.play(FadeIn(l), FadeIn(c))
            self.play(FadeIn(eq))
            n = zh("像素相同，字节不同；零宽连接符在图片里直接消失", 26, YELLOW).to_edge(DOWN, buff=0.8)
            self.play(Write(n))

        with self.voice("vis_5"):
            self.clear(run_time=0.5)
            a = VGroup(token_box("文字 → 图像", TEAL_D, 28), zh("容易", 24, OK)).arrange(DOWN)
            b = VGroup(token_box("图像 → 文字", RED_E, 28), zh("有损，需要 OCR", 24, BAD)).arrange(DOWN)
            VGroup(a, b).arrange(RIGHT, buff=2)
            self.play(FadeIn(a))
            self.play(FadeIn(b))
            h = zh("常见做法：视觉编码器 + 子词输出", 26, YELLOW).to_edge(DOWN, buff=1)
            self.play(Write(h))
        self.clear()


# ====================================================================== 16 今天的大模型
class S16_ModernLLMs(VoiceScene):
    def construct(self):
        with self.voice("llm_1"):
            t = section_title("前沿大模型的分词器（表 11.1）")
            big = VGroup(Text("BPE", font_size=110, weight=BOLD, color=BLUE_B), zh("几乎清一色", 30)).arrange(DOWN, buff=0.3)
            r = zh("词表：约 100k – 275k", 30, YELLOW).next_to(big, DOWN, buff=0.6)
            self.play(Write(t), FadeIn(big))
            self.play(FadeIn(r))

        with self.voice("llm_2"):
            self.clear(run_time=0.5)
            t = zh("词表大小（千）与最长的英文词元", 26, YELLOW).to_edge(UP, buff=0.5)
            rows = [("Gemini / Gemma", 262, "ylmethylsulfanyl"), ("Qwen 3.5–3.7", 248, "latesAutoresizingMaskIntoConstraints"),
                    ("Llama 4 (Meta)", 202, "abcdefghijklmnopqrstuvwxyz"), ("GPT-4o / GPT-5.x", 200, "abcdefghijklmnopqrstuvwxyz"),
                    ("Kimi K2–K3", 163, "fontawesomeextension"), ("Mistral Medium 3.5", 131, "Chartplatzierungen"),
                    ("DeepSeek V3.2 / V4", 128, "superscriptsubscript")]
            g = VGroup()
            for i, (m, v, lt) in enumerate(rows):
                y = 2.2 - i * 0.7
                name = Text(m, font_size=20).move_to([-4.3, y, 0])
                bar = Rectangle(width=v / 280 * 3.2, height=0.32, fill_color=BLUE_C, fill_opacity=0.85, stroke_width=0)
                bar.move_to([-2.6 + bar.width / 2, y, 0])
                val = Text(f"{v}k", font_size=18).next_to(bar, RIGHT, buff=0.1)
                lng = mono(lt, 17, GOLD if lt.startswith("abc") else GREY_A).move_to([1.2, y, 0], aligned_edge=LEFT)
                g.add(VGroup(name, bar, val, lng))
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in g], lag_ratio=0.2), run_time=3.5)
            self.play(Indicate(VGroup(g[2][3], g[3][3]), color=YELLOW))

        with self.voice("llm_3"):
            self.clear(run_time=0.5)
            c = VGroup(token_box("Claude（未公开）", ORANGE, 30), zh("以下均为论文的估计", 22, GREY_B)).arrange(DOWN, buff=0.3).shift(UP * 1.8)
            facts = VGroup(zh("行为更像最短路径分词，而非标准 BPE", 24), zh("使用大小写标记词元", 24),
                           zh("词表：Claude 3–4.6 约 49k；4.7+ 约 16k", 24, YELLOW)).arrange(DOWN, buff=0.35).shift(DOWN * 0.6)
            self.play(FadeIn(c))
            self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in facts], lag_ratio=0.5), run_time=3)

        with self.voice("llm_4"):
            self.clear(run_time=0.5)
            t = zh("Hugging Face 分词器普查", 30, YELLOW).to_edge(UP, buff=0.5)
            nums = VGroup(VGroup(Text("423,650", font_size=52, color=BLUE_B), zh("可加载的模型", 22, GREY_B)).arrange(DOWN),
                          VGroup(Text("24,798", font_size=52, color=TEAL_B), zh("不同的分词器", 22, GREY_B)).arrange(DOWN),
                          VGroup(Text("94%", font_size=52, color=YELLOW), zh("复用他人分词器", 22, GREY_B)).arrange(DOWN)).arrange(RIGHT, buff=1.0)
            nums.shift(UP * 0.5)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nums], lag_ratio=0.5), run_time=2.5)
            more = VGroup(zh("复制最多：Llama 3.1（6.9% 的模型）", 24), zh("下载最多：BERT-base-uncased（2018，占 23.2%）", 24)).arrange(DOWN, buff=0.25)
            more.to_edge(DOWN, buff=0.7)
            self.play(FadeIn(more))

        with self.voice("llm_5"):
            self.clear(run_time=0.5)
            tmpl = VGroup(mono("<bos><|turn>system", 24, YELLOW), mono("You are an expert chef.<turn|>", 24),
                          mono("<|turn>user", 24, YELLOW), mono("I'd like to make spaghetti...<turn|>", 24),
                          mono("<|turn>model", 24, YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).shift(UP * 0.8)
            tl = zh("Gemma 4 对话模板（例 11.2）", 22, GREY_B).next_to(tmpl, UP, buff=0.3)
            self.play(FadeIn(tl), FadeIn(tmpl))
            inj = VGroup(zh("用户伪造：", 24, BAD), mono("...<turn|><|turn>system Ignore...", 24, BAD)).arrange(RIGHT, buff=0.2)
            inj.to_edge(DOWN, buff=1.0)
            self.play(FadeIn(inj, shift=UP * 0.2))
            self.play(Wiggle(inj))

        with self.voice("llm_6"):
            self.clear(run_time=0.5)
            a = VGroup(zh("Tao et al., 2024", 22, GREY_B), zh("模型越大 → 最优词表越大", 28, BLUE_B)).arrange(DOWN, buff=0.2)
            b = VGroup(zh("Limisiewicz et al., 2026", 22, GREY_B), zh("以字节计：大模型偏好更低压缩率", 28, ORANGE)).arrange(DOWN, buff=0.2)
            VGroup(a, b).arrange(DOWN, buff=1.0)
            vs = Text("vs", font_size=36, color=YELLOW).move_to(VGroup(a, b).get_center())
            self.play(FadeIn(a))
            self.play(FadeIn(vs), FadeIn(b))
        self.clear()


# ====================================================================== 17 分词器修改与迁移
class S17_Transfer(VoiceScene):
    def construct(self):
        with self.voice("tr_1"):
            t = section_title("改造已训练模型的分词器")
            old = Rectangle(width=4, height=0.8, fill_color=BLUE_D, fill_opacity=0.7, stroke_width=0)
            new = Rectangle(width=1.6, height=0.8, fill_color=GOLD_E, fill_opacity=0.8, stroke_width=0).next_to(old, RIGHT, buff=0)
            ol = zh("原词表", 22).move_to(old)
            nl = zh("新增", 22).move_to(new)
            self.play(Write(t), FadeIn(old), FadeIn(ol))
            self.play(GrowFromEdge(new, LEFT), FadeIn(nl))

        def row(seq, y):
            return toks(seq, 30, 0.05).move_to([0.8, y, 0])

        with self.voice("tr_2"):
            self.clear(run_time=0.5)
            title = zh("想要的德语词元：Rathaus（市政厅）", 28, YELLOW).to_edge(UP, buff=0.5)
            self.play(Write(title))
            steps = [list("Rathaus"), ["R", "at", "h", "a", "u", "s"], ["Rat", "h", "a", "u", "s"], ["Rat", "ha", "u", "s"],
                     ["Rat", "hau", "s"], ["Rat", "haus"], ["Rathaus"]]
            merges = ["", "a t", "R at", "h a", "ha u", "hau s", "Rat haus"]
            cur = row(steps[0], 1.2)
            lab = mono("", 22)
            self.play(FadeIn(cur))
            for s, m in zip(steps[1:], merges[1:]):
                nxt = row(s, 1.2)
                ml = mono(f"merge ({m})", 22, GREY_A).move_to([-4.6, 1.2, 0])
                self.play(Transform(cur, nxt), FadeTransform(lab, ml), run_time=0.7)
                lab = ml
            ck = Text("✔", font_size=36, color=OK).next_to(cur, RIGHT)
            self.play(FadeIn(ck))
            self.ok = VGroup(cur, lab, ck)

        with self.voice("tr_3"):
            cur = row(list("Rathaus"), -0.8)
            lab = zh("但英语合并 (t, h) 排在前面：", 24, BAD).move_to([-3.6, 0.1, 0])
            self.play(FadeIn(lab), FadeIn(cur))
            nxt = row(["R", "a", "th", "a", "u", "s"], -0.8)
            self.play(Transform(cur, nxt))
            self.play(Indicate(cur[2], color=BAD))
            x = zh("a t、h a 不再相邻 → Rathaus 永远无法形成", 26, BAD).next_to(cur, DOWN, buff=0.6)
            self.play(Write(x))

        with self.voice("tr_4"):
            self.clear(run_time=0.5)
            t = zh("新词元的嵌入初始化", 28, YELLOW).to_edge(UP, buff=0.6)
            old = VGroup(toks(["token"], 28), toks(["ization"], 28)).arrange(RIGHT, buff=1.2).shift(UP * 0.8)
            vecs = VGroup(*[VGroup(*[Square(0.25, fill_color=c, fill_opacity=0.8, stroke_width=0.5) for _ in range(5)]).arrange(RIGHT, buff=0.02)
                            .next_to(o, DOWN, buff=0.3) for o, c in zip(old, [BLUE_C, TEAL_C])])
            new = toks(["tokenization"], 28, colors=[GOLD_E]).shift(DOWN * 1.2)
            nv = VGroup(*[Square(0.25, fill_color=GREEN_C, fill_opacity=0.8, stroke_width=0.5) for _ in range(5)]).arrange(RIGHT, buff=0.02)
            nv.next_to(new, DOWN, buff=0.3)
            self.play(Write(t), FadeIn(old), FadeIn(vecs))
            self.play(FadeIn(new), TransformFromCopy(vecs, nv))
            avg = zh("平均", 24, GREY_B).next_to(nv, RIGHT, buff=0.3)
            hyper = zh("更进一步：超网络预测嵌入 → 零样本迁移", 24, TEAL_B).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(avg), FadeIn(hyper))

        with self.voice("tr_5"):
            self.clear(run_time=0.5)
            f = mono("KL(p_T ‖ p_S) = Σ_{t ∈ V} p_T(t) log p_T(t) / p_S(t)", 30, YELLOW).shift(UP * 1.2)
            n = zh("要求教师和学生共享词表 V，否则散度为无穷大", 26, BAD).next_to(f, DOWN, buff=0.5)
            m = zh("跨分词器蒸馏：对齐覆盖同一段文本的词元块（ULD · ALM …）", 24, TEAL_B).next_to(n, DOWN, buff=0.7)
            self.play(Write(f))
            self.play(FadeIn(n))
            self.play(FadeIn(m))
        self.clear()


# ====================================================================== 18 理论
class S18_Theory(VoiceScene):
    def construct(self):
        with self.voice("th_1"):
            f = mono("tok* = argmin_{tok ∈ T}  G(tok, D)", 38, YELLOW)
            n = zh("BPE、Unigram：贪心近似", 26, GREY_B).next_to(f, DOWN, buff=0.6)
            self.play(Write(f))
            self.play(FadeIn(n))

        words = ["aab", "aac", "aad", "ab", "ac", "ad"]
        with self.voice("th_2"):
            self.clear(run_time=0.5)
            t = zh("数据集 D（总长度 15），允许新增 3 个词元", 28, YELLOW).to_edge(UP, buff=0.5)
            col = VGroup(*[toks(list(w), 28, 0.04) for w in words]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            col.shift(LEFT * 3.5 + DOWN * 0.3)
            self.play(Write(t), LaggedStart(*[FadeIn(c) for c in col], lag_ratio=0.2))
            self.col = col

        with self.voice("th_3"):
            bpe = [["aa", "b"], ["aa", "c"], ["aa", "d"], ["ab"], ["ac"], ["a", "d"]]
            hdr = zh("BPE", 30, BLUE_B).move_to([0, 2.4, 0])
            b = VGroup(*[toks(s, 28, 0.04) for s in bpe]).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([0, -0.3, 0])
            b.align_to(self.col, UP)
            self.play(FadeIn(hdr))
            self.play(*[TransformFromCopy(self.col[i], b[i]) for i in range(6)], run_time=1.5)
            r1 = zh("长度 10", 30, BLUE_B).next_to(b, DOWN, buff=0.4)
            self.play(FadeIn(r1))

        with self.voice("th_4"):
            opt = [["a", "ab"], ["a", "ac"], ["a", "ad"], ["ab"], ["ac"], ["ad"]]
            hdr = zh("最优", 30, OK).move_to([3.8, 2.4, 0])
            o = VGroup(*[toks(s, 28, 0.04, colors=[TEAL_D, GOLD_E]) for s in opt]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            o.move_to([3.8, -0.3, 0]).align_to(self.col, UP)
            self.play(FadeIn(hdr))
            self.play(*[TransformFromCopy(self.col[i], o[i]) for i in range(6)], run_time=1.5)
            r2 = zh("长度 9", 30, OK).next_to(o, DOWN, buff=0.4)
            self.play(FadeIn(r2))

        with self.voice("th_5"):
            self.clear(run_time=0.5)
            rows = VGroup(zh("一般情形：NP 难，甚至 APX 完全（难以任意近似）", 28),
                          zh("压缩量：BPE ≥ 最优的 1/3", 28, OK),
                          zh("压缩后长度：可比最优差任意多倍", 28, BAD)).arrange(DOWN, buff=0.5)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), run_time=3)

        with self.voice("th_6"):
            self.clear(run_time=0.5)
            a = VGroup(Text("< 1%", font_size=90, color=OK), zh("真实语料上 BPE 与最优的差距", 24, GREY_B)).arrange(DOWN)
            b = VGroup(zh("《傲慢与偏见》", 34, YELLOW), zh("找到了可证明最优的分词器", 24, GREY_B)).arrange(DOWN)
            VGroup(a, b).arrange(RIGHT, buff=1.8)
            self.play(FadeIn(a))
            self.play(FadeIn(b))
        self.clear()


# ====================================================================== 19 安全与词元修复
class S19_Security(VoiceScene):
    def construct(self):
        with self.voice("sec_1"):
            a = VGroup(mono("attack", 40), Arrow(ORIGIN, RIGHT, color=GREY_B), toks([f"{SP}attack"], 32)).arrange(RIGHT, buff=0.4)
            b = VGroup(mono("аttаck", 40), Arrow(ORIGIN, RIGHT, color=GREY_B), toks([SP, "а", "tt", "а", "ck"], 32)).arrange(RIGHT, buff=0.4)
            VGroup(a, b).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
            cyr = zh("а = 西里尔字母（U+0430）", 24, BAD).to_edge(DOWN, buff=1)
            lab = zh("GPT-5 分词器", 22, GREY_B).to_edge(UP, buff=0.8)
            self.play(FadeIn(lab), FadeIn(a))
            self.play(FadeIn(b))
            self.play(Indicate(b[2][1], color=BAD), Indicate(b[2][3], color=BAD), FadeIn(cyr))

        with self.voice("sec_2"):
            self.clear(run_time=0.5)
            m = toks(["SolidGoldMagikarp"], 40, colors=[GOLD_E])
            ml = zh("训练不足的词元：嵌入近乎随机", 26, BAD).next_to(m, DOWN, buff=0.5)
            self.play(FadeIn(m))
            self.play(Write(ml))
            leak = zh("词表与合并顺序 → 可推断训练数据的语言构成", 24, GREY_B).to_edge(DOWN, buff=0.8)
            self.play(FadeIn(leak))

        with self.voice("sec_3"):
            self.clear(run_time=0.5)
            t = zh("词元修复（图 14.1）", 28, YELLOW).to_edge(UP, buff=0.5)
            p = toks(["Atten", "tion", f"{SP}is", f"{SP}all", f"{SP}you"], 28)
            nxt = toks([f"{SP}need"], 28, colors=[OK])
            VGroup(p, nxt).arrange(RIGHT, buff=0.4).shift(UP * 1)
            pr = mono("0.97", 26, OK).next_to(nxt, UP, buff=0.15)
            self.play(Write(t), FadeIn(p))
            self.play(FadeIn(nxt), FadeIn(pr))
            self.good = VGroup(p, nxt, pr)

        with self.voice("sec_4"):
            p2 = toks(["Atten", "tion", f"{SP}is", f"{SP}all", f"{SP}you", SP], 28)
            n2 = toks(["need"], 28, colors=[BAD])
            VGroup(p2, n2).arrange(RIGHT, buff=0.4).shift(DOWN * 0.8)
            pr2 = mono("≈ 0.01", 26, BAD).next_to(n2, UP, buff=0.15)
            self.play(FadeIn(p2))
            self.play(Indicate(p2[-1], color=BAD))
            self.play(FadeIn(n2), FadeIn(pr2))
            fix = zh("修复：退回最后一个词元，约束下一个词元以“▁”开头", 24, YELLOW).to_edge(DOWN, buff=0.6)
            self.play(Write(fix))
            self.play(Indicate(self.good[1], color=OK))

        with self.voice("sec_5"):
            self.clear(run_time=0.5)
            a = VGroup(zh("约束：字符级", 26), mono('{"name": "[a-z]+"}', 26, TEAL_B)).arrange(DOWN, buff=0.2)
            b = VGroup(zh("生成：子词级", 26), toks(['{"', "name", '":', ' "'], 26)).arrange(DOWN, buff=0.2)
            VGroup(a, b).arrange(RIGHT, buff=2)
            arr = Arrow(a.get_right(), b.get_left(), color=YELLOW)
            fsa = zh("子词自动机：每一步哪些词元合法", 26, YELLOW).to_edge(DOWN, buff=1)
            self.play(FadeIn(a), FadeIn(b))
            self.play(GrowArrow(arr), Write(fsa))
        self.clear()


# ====================================================================== 20 结尾
class S20_Outro(VoiceScene):
    def construct(self):
        with self.voice("out_1"):
            items = VGroup(token_box("推理速度 · 参数量", BLUE_D, 28), token_box("语言与文字的公平", TEAL_D, 28),
                           token_box("能力与安全的边界", GOLD_E, 28)).arrange(DOWN, buff=0.5)
            self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items], lag_ratio=0.5), run_time=3)
            self.g = items

        with self.voice("out_2"):
            self.play(FadeOut(self.g))
            center = token_box("BPE", BLUE_D, 40)
            around = ["BPE 变体", "Unigram", "WordPiece", "隐式字节分词", "视觉分词"]
            sats = VGroup(*[token_box(a, GREY_BROWN, 24) for a in around])
            for s, ang in zip(sats, np.linspace(PI / 2, PI / 2 - TAU, 5, endpoint=False)):
                s.move_to(2.5 * np.array([1.5 * np.cos(ang), np.sin(ang), 0]))
            self.play(GrowFromCenter(center))
            self.play(LaggedStart(*[FadeIn(s) for s in sats], lag_ratio=0.3), run_time=2.5)
            self.g = VGroup(center, sats)

        with self.voice("out_3"):
            self.play(FadeOut(self.g))
            t = zh("作者期待的三个方向", 34, YELLOW).to_edge(UP, buff=0.8)
            d = VGroup(*[VGroup(Text(f"{i + 1}", font_size=48, color=c), zh(n, 32)).arrange(RIGHT, buff=0.4)
                         for i, (n, c) in enumerate([("分词器的规模定律", BLUE_C), ("替代子词的新方案", TEAL), ("更好的评测基准", GOLD)])])
            d.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            self.play(Write(t))
            self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.2) for x in d], lag_ratio=0.5), run_time=3)

        with self.voice("out_4"):
            self.clear(run_time=0.5)
            w = VGroup(*[Text(c, font=MONO, font_size=60) for c in "strawberry"]).arrange(RIGHT, buff=0.08)
            self.play(FadeIn(w))
            self.play(*[w[i].animate.set_color(YELLOW) for i, c in enumerate("strawberry") if c == "r"])
            m = zh("问题也许在最开始的那一步", 32, YELLOW).next_to(w, DOWN, buff=0.8)
            self.play(Write(m))

        with self.voice("out_5"):
            self.clear(run_time=0.5)
            ref = VGroup(VGroup(Text("Token", font_size=64, weight=BOLD, color=BLUE_B),
                                Text("ization", font_size=64, weight=BOLD, color=TEAL_B)).arrange(RIGHT, buff=0.1),
                         Text("A Survey for Modern NLP", font_size=30, color=GREY_A),
                         Text("Cognetta, Akiki, … , Pinter  ·  2026", font_size=22, color=GREY_B),
                         zh("感谢收看", 40)).arrange(DOWN, buff=0.4)
            self.play(Write(ref[0]), FadeIn(ref[1]))
            self.play(FadeIn(ref[2]), FadeIn(ref[3], shift=UP * 0.2))
        self.clear()
