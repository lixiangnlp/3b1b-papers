"""《黎曼猜想被证明了？》3Blue1Brown 风格中文科普 —— Manim 场景。

渲染单个场景:  manim -qm riemann/scenes.py S03_Zeta
整片构建:      python build.py all --project riemann
"""

from __future__ import annotations

import math

import mpmath
import numpy as np
from manim import *  # noqa: F401,F403

from common import (
    CLAUDE_COLOR, HUMAN_COLOR, LEAN_COLOR, LINE_COLOR, OK_COLOR, PRIME_COLOR,
    STRIP_COLOR, ZERO_COLOR, VoiceScene, check_mark, cross_mark, mono, quote_card, tag,
    zeta_zeros, zh,
)

BG_CARD = "#1A1A22"


# ---------------------------------------------------------------- 数据
def primes_upto(n: int) -> np.ndarray:
    sieve = np.ones(n + 1, bool)
    sieve[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    return np.nonzero(sieve)[0]


def prime_pi(n: int) -> np.ndarray:
    """pi[k] = 不超过 k 的素数个数。"""
    is_p = np.zeros(n + 1, int)
    is_p[primes_upto(n)] = 1
    return np.cumsum(is_p)


def li(x: float) -> float:
    return float(mpmath.li(x))


def psi_exact(x: float) -> float:
    """切比雪夫 ψ(x) = Σ_{p^k ≤ x} ln p。"""
    total = 0.0
    for p in primes_upto(int(x)):
        pk = p
        while pk <= x:
            total += math.log(p)
            pk *= p
    return total


def psi_explicit(x: float, zeros: list[float]) -> float:
    """显式公式：ψ(x) ≈ x − Σ_ρ x^ρ/ρ − ln 2π − ½ ln(1 − x⁻²)，只取给定的零点（含共轭）。"""
    s = x - math.log(2 * math.pi) - 0.5 * math.log(1 - x ** -2)
    lx = math.log(x)
    for t in zeros:
        rho = complex(0.5, t)
        s -= 2 * (complex(math.cos(t * lx), math.sin(t * lx)) * math.sqrt(x) / rho).real
    return s


def sigma_upto(n: int) -> np.ndarray:
    s = np.zeros(n + 1, np.int64)
    for d in range(1, n + 1):
        s[d::d] += d
    return s


def staircase(axes: Axes, xs, ys, color=WHITE, width=3) -> VMobject:
    """由跳跃点构造阶梯折线。xs 递增，ys[i] 为 [xs[i], xs[i+1]) 上的取值。"""
    pts = []
    for i in range(len(xs) - 1):
        pts.append(axes.c2p(xs[i], ys[i]))
        pts.append(axes.c2p(xs[i + 1], ys[i]))
    m = VMobject(stroke_color=color, stroke_width=width)
    m.set_points_as_corners(pts)
    return m


def person(color=HUMAN_COLOR, scale=1.0) -> VGroup:
    head = Circle(radius=0.32, fill_color=color, fill_opacity=0.9, stroke_width=0)
    body = RoundedRectangle(corner_radius=0.3, width=1.05, height=0.75, fill_color=color,
                            fill_opacity=0.55, stroke_width=0).next_to(head, DOWN, buff=0.08)
    return VGroup(head, body).scale(scale)


def claude_badge(scale=1.0) -> VGroup:
    box = RoundedRectangle(corner_radius=0.25, width=1.3, height=1.3, fill_color=CLAUDE_COLOR,
                           fill_opacity=0.9, stroke_width=0)
    star = VGroup(*[Line(ORIGIN, 0.42 * np.array([math.cos(a), math.sin(a), 0]),
                         stroke_width=7, stroke_color=WHITE)
                    for a in np.linspace(0, 2 * PI, 9)[:-1]]).move_to(box)
    return VGroup(box, star).scale(scale)


def sparkle(point, color=YELLOW, r=0.18) -> VGroup:
    return VGroup(*[Line(point, point + r * np.array([math.cos(a), math.sin(a), 0]),
                         stroke_width=3, stroke_color=color)
                    for a in np.linspace(0, 2 * PI, 7)[:-1]])


def numbered(items: list[str], size=30, color=BLUE_B) -> VGroup:
    return VGroup(*[
        VGroup(Text(f"{i + 1:02d}", font_size=size - 2, color=color), zh(s, size)).arrange(RIGHT, buff=0.35)
        for i, s in enumerate(items)
    ]).arrange(DOWN, aligned_edge=LEFT, buff=0.38)


# ====================================================================== 1 开场
REAL_LEAN_LINES = [  # 直接摘自 alpo.ge/lean.tar.gz 中的源码
    "theorem riemannHypothesis : RiemannHypothesis := rhOfAll",
    "theorem psi_mul_mul (n : ℕ) (q : ℤ) (l₁ k l₂ : U2) :",
    "theorem exists_isHilbertSum_isIrreducible_finite :",
    "theorem continuous_infPart : Continuous (infPart K n) :=",
    "theorem isAdmissible_cuspSubmodule (U : Submodule ℂ (cuspForms K n))",
    "theorem cuspidalDecay_holds : CuspidalExponentialDecay (E := E) := by",
    "theorem hm_add_right (Hm : Matrix (Fin g) (Fin g) ℂ) (z w w' : Fin g → ℂ) :",
    "theorem exists_wData_of_logRes (hQ : FinalTheorems.FinTypeQE)",
    "def IsUnivRing (m : ℕ) (π : B →ₐ[R] JetR R (Fin n) m) : Prop :=",
    "theorem b3c : ConjugationSecondOrderBound := by",
    "theorem tj_finite (w : Ad3.Pl) (j : ℕ) :",
    "def good (N : ℕ) (A : GF F) : Prop := ∀ i j, (N : Af F) * A.val i j ∈ Ohat F",
    "theorem jF_sa {F : Type} [Field F] [NumberField F] (c α : Fˣ) (β : F) :",
    "lemma prof_le_lo {s T r : ℝ} (hT : 0 < T) (hr : 0 < r) :",
    "theorem UpperTheory.V.U3.pt_inertia_above :",
    "theorem adelic_index_eq : PI.AdIndexEq.IndexEq :=",
    "theorem avgSmooth_of (h4 : SobChart) : AvgSmooth := by",
    "def gam (s : ℝ) : ℝ := Real.Gamma s / Real.Gamma (1 - s)",
    "def Phi : E ⊗[F] Fv F v →ₗ[F] Af F ⊗[F] E :=",
    "theorem LFunction_eq_zero_re : DirichletLZerosOnLine := claimAll.2.1",
]


class S01_Intro(VoiceScene):
    def construct(self):
        with self.voice("intro_1"):
            date = zh("2026 年 11 月 20 日", 34, GREY_B).to_edge(UP, buff=0.6)
            paper = RoundedRectangle(corner_radius=0.05, width=3.4, height=4.4, fill_color="#F4F1EA",
                                     fill_opacity=1, stroke_width=0)
            ptitle = Text("Remark", font="Latin Modern Roman", font_size=38, color="#222222")
            pauthor = Text("Levent Alpöge", font="Latin Modern Roman", font_size=22, color="#444444")
            head = VGroup(ptitle, pauthor).arrange(DOWN, buff=0.15).move_to(paper.get_top() + DOWN * 0.8)
            lines = VGroup(*[Line(LEFT * 1.3, RIGHT * (1.3 if i % 5 != 4 else 0.3), stroke_width=3,
                                  stroke_color="#9A968C") for i in range(14)])
            lines.arrange(DOWN, buff=0.17).next_to(head, DOWN, buff=0.35)
            doc = VGroup(paper, head, lines).shift(RIGHT * 2.6 + DOWN * 0.3)
            url = mono("alpo.ge/remark.pdf", 24, GREY_B).next_to(doc, DOWN, buff=0.25)
            who = VGroup(
                person(scale=1.2),
                Text("Levent Alpöge", font_size=36),
                zh("莱文特·阿尔珀格", 28, GREY_B),
                zh("Anthropic · 数学家", 26, HUMAN_COLOR),
            ).arrange(DOWN, buff=0.25).shift(LEFT * 3.2 + DOWN * 0.2)
            self.play(Write(date), run_time=1.5)
            self.play(FadeIn(who, shift=RIGHT * 0.3), run_time=1.5)
            self.play(FadeIn(paper, shift=UP * 0.3), Write(head), run_time=1.5)
            self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08), run_time=2)
            self.play(FadeIn(url))
            self.wait(2.5)
            badge = zh("4 页", 30, YELLOW).next_to(paper, UR, buff=-0.2).shift(RIGHT * 0.5)
            self.play(FadeIn(badge, scale=1.4))

        with self.voice("intro_2"):
            q = quote_card("“I believe I have, working with Claude,\n discovered a proof of the Riemann Hypothesis.”",
                           "“我相信，我和 Claude 一起，找到了黎曼猜想的证明。”",
                           width=12, en_size=34,
                           t2c={"Claude": CLAUDE_COLOR, "Riemann Hypothesis": YELLOW})
            self.play(FadeOut(VGroup(who, doc, url, badge, date)), run_time=0.6)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=1.5)

        with self.voice("intro_3"):
            self.play(q.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=1)
            rh = zh("黎曼猜想", 64, YELLOW).shift(UP * 0.9)
            years = VGroup(MathTex(r"1859", font_size=48), MathTex(r"\longrightarrow", font_size=48),
                           MathTex(r"2026", font_size=48)).arrange(RIGHT, buff=0.3).next_to(rh, DOWN, buff=0.35)
            span = zh("悬而未决 167 年", 30, GREY_B).next_to(years, DOWN, buff=0.25)
            self.play(Write(rh), run_time=1.2)
            self.play(FadeIn(years, shift=UP * 0.2), FadeIn(span), run_time=1.2)
            self.wait(2.5)
            self.play(FadeOut(VGroup(rh, years, span)), run_time=0.6)
            code = VGroup(*[mono(l, 20, LEAN_COLOR if i % 3 else GREY_B) for i, l in enumerate(REAL_LEAN_LINES)])
            code.arrange(DOWN, aligned_edge=LEFT, buff=0.16).to_edge(LEFT, buff=0.6)
            code.align_to(q, DOWN).shift(DOWN * (code.height + 0.5))
            code.set_opacity(0.85)
            fade_mask = Rectangle(width=16, height=1.2, fill_color=config.background_color, fill_opacity=1,
                                  stroke_width=0).to_edge(DOWN, buff=0)
            counter_val = ValueTracker(0)
            counter = always_redraw(lambda: VGroup(
                Text(f"{int(counter_val.get_value()):,}", font_size=56, color=YELLOW, weight=BOLD),
                zh("行 Lean 代码", 30),
            ).arrange(DOWN, buff=0.2).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.6))
            bg = Rectangle(width=5.6, height=2.6, fill_color=config.background_color, fill_opacity=0.92,
                           stroke_width=0).move_to(counter).set_x(config.frame_width / 2 - 2.8)
            self.add(code, fade_mask, q)
            self.play(FadeIn(code), run_time=0.5)
            self.add(bg, counter)
            self.play(code.animate.shift(UP * 2.8), counter_val.animate.set_value(17_374_187),
                      rate_func=linear, run_time=5)

        with self.voice("intro_4"):
            self.play(FadeOut(VGroup(code, fade_mask, q, counter, bg)), run_time=0.8)
            counter.clear_updaters()
            title = zh("本期内容", 40, YELLOW).to_edge(UP, buff=0.8)
            items = numbered(["黎曼猜想到底在说什么", "证明的思路，大概长什么样",
                              "人和 AI 是怎样分工的", "全世界如何在一天之内检查这份证明"], 34)
            items.next_to(title, DOWN, buff=0.7)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in items], lag_ratio=0.45),
                      run_time=7)
        self.clear()


# ====================================================================== 2 素数
class S02_Primes(VoiceScene):
    def construct(self):
        primes = set(primes_upto(100).tolist())
        with self.voice("primes_1"):
            cells = VGroup()
            for n in range(1, 101):
                cells.add(Text(str(n), font_size=24, color=GREY_B))
            cells.arrange_in_grid(rows=10, cols=10, buff=(0.32, 0.2))
            cells.scale_to_fit_width(5.6).to_edge(LEFT, buff=0.6)
            self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.01), run_time=2)
            first = [2, 3, 5, 7, 11, 13]
            for p in first:
                self.play(cells[p - 1].animate.set_color(PRIME_COLOR).scale(1.25), run_time=0.35)
            rest = [cells[n - 1] for n in sorted(primes) if n not in first]
            self.play(*[c.animate.set_color(PRIME_COLOR).scale(1.25) for c in rest],
                      *[cells[n - 1].animate.set_opacity(0.35) for n in range(1, 101) if n not in primes],
                      run_time=1.5)
            atom = zh("素数：整数的“原子”", 36, PRIME_COLOR).move_to(RIGHT * 3.4 + UP * 2)
            facts = VGroup(
                MathTex(r"60 = 2^2 \times 3 \times 5", font_size=48),
                MathTex(r"91 = 7 \times 13", font_size=48),
                MathTex(r"2026 = 2 \times 1013", font_size=48),
            ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(atom, DOWN, buff=0.6)
            for f in facts:
                f.set_color_by_tex_to_color_map({})
            uniq = zh("每个整数都能唯一地分解成素数之积", 26, GREY_B).next_to(facts, DOWN, buff=0.5).set_x(3.4)
            self.play(Write(atom), run_time=1)
            self.play(LaggedStart(*[Write(f) for f in facts], lag_ratio=0.5), run_time=3)
            self.play(FadeIn(uniq))

        with self.voice("primes_2"):
            self.play(FadeOut(VGroup(cells, atom, facts, uniq)), run_time=0.7)
            nl = NumberLine(x_range=[0, 100, 10], length=12.5, include_numbers=True, font_size=24,
                            stroke_width=2).shift(DOWN * 0.3)
            ticks = VGroup(*[Line(nl.n2p(p) + DOWN * 0.18, nl.n2p(p) + UP * 0.45, stroke_width=4,
                                  color=PRIME_COLOR) for p in sorted(primes)])
            self.play(Create(nl), run_time=1)
            self.play(LaggedStart(*[GrowFromEdge(t, DOWN) for t in ticks], lag_ratio=0.05), run_time=2.5)
            twin = Brace(VGroup(ticks[4], ticks[5]), UP, buff=0.1)
            twin_l = zh("11 与 13：紧挨着", 26, PRIME_COLOR).next_to(twin, UP, buff=0.1)
            self.play(GrowFromCenter(twin), FadeIn(twin_l), run_time=1)
            self.wait(1.5)
            gap = Brace(Line(nl.n2p(89), nl.n2p(97)), UP, buff=0.55)
            gap_l = zh("89 → 97：一片荒漠", 26, RED).next_to(gap, UP, buff=0.1)
            desert = Rectangle(width=nl.n2p(97)[0] - nl.n2p(89)[0], height=0.5, fill_color=RED,
                               fill_opacity=0.18, stroke_width=0).move_to(
                (nl.n2p(89) + nl.n2p(97)) / 2 + UP * 0.15)
            self.play(GrowFromCenter(gap), FadeIn(gap_l), FadeIn(desert), run_time=1)

        with self.voice("primes_3"):
            self.play(FadeOut(VGroup(nl, ticks, twin, twin_l, gap, gap_l, desert)), run_time=0.7)
            N = 1000
            pi = prime_pi(N)
            ax = Axes(x_range=[0, N, 200], y_range=[0, 180, 40], x_length=8.2, y_length=5.2,
                      axis_config={"include_numbers": True, "font_size": 22, "stroke_width": 2},
                      tips=False).to_edge(LEFT, buff=0.8).shift(DOWN * 0.45)
            ps = primes_upto(N)
            xs = [0, *ps.tolist(), N]
            ys = [0, *range(1, len(ps) + 1)]
            stair = staircase(ax, xs, ys, PRIME_COLOR, 2.5)
            curve = ax.plot(lambda x: li(x) - li(2), x_range=[2, N, 4], color=BLUE_C, stroke_width=4)
            prob = MathTex(r"P(n \text{ is prime}) \approx \frac{1}{\ln n}", font_size=40)
            prob_zh = zh("一个数是素数的概率", 24, GREY_B)
            gauss = VGroup(zh("高斯，约 1792 年", 26, GREY_B), prob, prob_zh).arrange(DOWN, buff=0.25)
            gauss.to_edge(RIGHT, buff=0.4).shift(UP * 1.8)
            lbl_pi = MathTex(r"\pi(x)", color=PRIME_COLOR, font_size=40)
            lbl_pi_zh = zh("真实的素数个数", 22, PRIME_COLOR)
            lbl_li = MathTex(r"\int_2^x \frac{dt}{\ln t}", color=BLUE_C, font_size=40)
            lbl_li_zh = zh("概率的累加", 22, BLUE_C)
            legend = VGroup(VGroup(lbl_pi, lbl_pi_zh).arrange(DOWN, buff=0.1),
                            VGroup(lbl_li, lbl_li_zh).arrange(DOWN, buff=0.1)).arrange(DOWN, buff=0.4)
            legend.next_to(gauss, DOWN, buff=0.6)
            self.play(Create(ax), run_time=1.2)
            self.play(Create(stair), run_time=3.5, rate_func=linear)
            self.play(FadeIn(lbl_pi), FadeIn(lbl_pi_zh))
            self.play(Write(gauss), run_time=2)
            self.wait(2)
            self.play(Create(curve), run_time=3)
            self.play(FadeIn(lbl_li), FadeIn(lbl_li_zh))

        with self.voice("primes_4"):
            self.play(FadeOut(VGroup(gauss, legend)), run_time=0.6)
            zoom_box = Rectangle(width=1.6, height=1.0, color=WHITE).move_to(ax.c2p(700, 125))
            q = zh("误差有多大？", 34, WHITE).to_edge(RIGHT, buff=1.2).shift(UP * 2)
            self.play(Create(zoom_box), Write(q), run_time=1.2)
            self.wait(1)
            self.play(FadeOut(VGroup(ax, stair, curve, zoom_box, lbl_pi, lbl_pi_zh, lbl_li, lbl_li_zh, q)),
                      run_time=0.7)
            M = 100_000
            pi = prime_pi(M)
            ax2 = Axes(x_range=[0, M, 20000], y_range=[-160, 160, 80], x_length=9.5, y_length=4.6,
                       axis_config={"font_size": 20, "stroke_width": 2}, tips=False,
                       x_axis_config={"include_numbers": True},
                       y_axis_config={"include_numbers": True}).to_edge(LEFT, buff=0.8).shift(DOWN * 0.9)
            xs = np.linspace(3000, M, 700)
            err_pts = [ax2.c2p(x, li(x) - pi[int(x)]) for x in xs]
            err = VMobject(stroke_color=PRIME_COLOR, stroke_width=2.5).set_points_as_corners(err_pts)
            env = lambda x: math.sqrt(x) * math.log(x) / (8 * math.pi)  # noqa: E731
            up = ax2.plot(env, x_range=[3000, M, 500], color=BLUE_C, stroke_width=3)
            dn = ax2.plot(lambda x: -env(x), x_range=[3000, M, 500], color=BLUE_C, stroke_width=3)
            up, dn = DashedVMobject(up, num_dashes=50), DashedVMobject(dn, num_dashes=50)
            err_l = MathTex(r"\mathrm{li}(x) - \pi(x)", font_size=34, color=PRIME_COLOR).next_to(
                ax2.c2p(M, 40), RIGHT, buff=0.15)
            env_l = MathTex(r"\pm\frac{\sqrt{x}\,\ln x}{8\pi}", font_size=34, color=BLUE_C).next_to(
                ax2.c2p(M, 140), RIGHT, buff=0.15)
            rh = MathTex(r"\pi(x) = \mathrm{li}(x) + O\!\left(\sqrt{x}\,\ln x\right)", font_size=46)
            rh_l = zh("黎曼猜想 ⇔", 34, YELLOW)
            top = VGroup(rh_l, rh).arrange(RIGHT, buff=0.35).to_edge(UP, buff=0.5)
            self.play(Create(ax2), run_time=1)
            self.play(Create(err), FadeIn(err_l), run_time=2.5)
            self.play(Write(top), run_time=2)
            self.play(Create(up), Create(dn), FadeIn(env_l), run_time=2)
            quote = VGroup(Text("“optimal control on the count of prime numbers”", font="Latin Modern Roman",
                                slant=ITALIC, font_size=30),
                           zh("对素数计数的“最优控制” —— Alpöge", 24, GREY_B)).arrange(DOWN, buff=0.15)
            quote.next_to(top, DOWN, buff=0.3)
            self.wait(3)
            self.play(FadeIn(quote, shift=UP * 0.2), run_time=1)
        self.clear()


# ====================================================================== 3 ζ 函数
class S03_Zeta(VoiceScene):
    def construct(self):
        with self.voice("zeta_1"):
            title = zh("黎曼 ζ 函数", 40, YELLOW).to_edge(UP, buff=0.6)
            zeta = MathTex(r"\zeta(s)", r"=", r"1", r"+", r"\frac{1}{2^s}", r"+", r"\frac{1}{3^s}", r"+",
                           r"\frac{1}{4^s}", r"+", r"\cdots", font_size=60).shift(UP * 1.2)
            self.play(Write(title), run_time=1)
            self.play(Write(zeta), run_time=3)
            ex = MathTex(r"\zeta(2) = 1 + \frac{1}{4} + \frac{1}{9} + \frac{1}{16} + \cdots = \frac{\pi^2}{6}",
                         font_size=50).shift(DOWN * 0.6)
            self.wait(2)
            self.play(Write(ex), run_time=2.5)
            nl = NumberLine(x_range=[1, 1.7, 0.1], length=9, include_numbers=True, font_size=22,
                            decimal_number_config={"num_decimal_places": 1}).shift(DOWN * 2.4)
            target = Line(nl.n2p(math.pi ** 2 / 6) + DOWN * 0.3, nl.n2p(math.pi ** 2 / 6) + UP * 0.3,
                          color=YELLOW, stroke_width=4)
            tl = MathTex(r"\pi^2/6", font_size=30, color=YELLOW).next_to(target, UP, buff=0.1)
            k = ValueTracker(1)
            dot = always_redraw(lambda: Dot(nl.n2p(sum(1 / n ** 2 for n in range(1, int(k.get_value()) + 1))),
                                            color=BLUE_C, radius=0.09))
            self.play(Create(nl), Create(target), FadeIn(tl), FadeIn(dot), run_time=1.2)
            self.play(k.animate.set_value(60), run_time=4, rate_func=rate_functions.ease_out_cubic)
            dot.clear_updaters()

        with self.voice("zeta_2"):
            self.play(FadeOut(VGroup(ex, nl, target, tl, dot)), zeta.animate.shift(UP * 0.3), run_time=0.8)
            euler = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^s}", r"=",
                            r"\prod_{p}", r"\frac{1}{1 - p^{-s}}", font_size=64).shift(DOWN * 0.8)
            euler[2].set_color(PRIME_COLOR)
            euler[3].set_color(PRIME_COLOR)
            b1 = Brace(euler[0], DOWN)
            l1 = zh("所有正整数", 28).next_to(b1, DOWN)
            b2 = Brace(VGroup(euler[2], euler[3]), DOWN, color=PRIME_COLOR)
            l2 = zh("所有素数", 28, PRIME_COLOR).next_to(b2, DOWN)
            who = zh("欧拉，1737 年", 26, GREY_B).to_corner(DR, buff=0.6)
            self.play(Write(euler), FadeIn(who), run_time=3)
            self.play(GrowFromCenter(b1), FadeIn(l1), run_time=1)
            self.play(GrowFromCenter(b2), FadeIn(l2), run_time=1)
            self.play(Indicate(euler[1], scale_factor=1.8, color=YELLOW), run_time=1.5)

        with self.voice("zeta_3"):
            self.play(FadeOut(VGroup(title, zeta, euler, b1, l1, b2, l2, who)), run_time=0.7)
            ax = Axes(x_range=[-9, 3, 1], y_range=[-45, 45, 15], x_length=11, y_length=7.2,
                      axis_config={"stroke_width": 2, "font_size": 20}, tips=False,
                      x_axis_config={"numbers_to_include": [-8, -6, -4, -2, 1, 2]},
                      y_axis_config={"numbers_to_include": [-30, -15, 15, 30]}).shift(LEFT * 0.6)
            self.ax = ax
            re_l = MathTex(r"\mathrm{Re}(s)", font_size=28).next_to(ax.x_axis.get_right(), UP, buff=0.15)
            im_l = MathTex(r"\mathrm{Im}(s)", font_size=28).next_to(ax.y_axis.get_top(), RIGHT, buff=0.15)
            s_def = MathTex(r"s = \sigma + i\,t", font_size=40).to_corner(UR, buff=0.5)
            self.play(Create(ax), FadeIn(re_l), FadeIn(im_l), Write(s_def), run_time=2)
            pole = Cross(scale_factor=0.12, stroke_color=BLUE_C).move_to(ax.c2p(1, 0))
            pole_l = zh("s = 1：极点", 22, BLUE_C).next_to(pole, DR, buff=0.12).shift(DOWN * 0.25)
            ext = zh("解析延拓：ζ 定义在整个复平面上（s = 1 除外）", 24, GREY_B).to_corner(DL, buff=0.4)
            self.play(Create(pole), FadeIn(pole_l), FadeIn(ext), run_time=1.5)
            q = zh("ζ(s) = 0 的点在哪里？", 30, YELLOW).next_to(s_def, DOWN, buff=0.35).align_to(s_def, RIGHT)
            self.play(Write(q), run_time=1.2)

        with self.voice("zeta_4"):
            triv = VGroup(*[Dot(ax.c2p(-2 * k, 0), color=GREY_B, radius=0.09) for k in range(1, 5)])
            triv_l = zh("平凡零点 −2, −4, −6, …", 24, GREY_B).next_to(ax.c2p(-5, 0), UP, buff=0.35)
            self.play(LaggedStart(*[GrowFromCenter(d) for d in triv], lag_ratio=0.3), FadeIn(triv_l), run_time=2)
            self.wait(2.5)
            strip = Rectangle(width=ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0], height=ax.y_length,
                              fill_color=STRIP_COLOR, fill_opacity=0.22, stroke_width=0)
            strip.move_to(ax.c2p(0.5, 0))
            strip_l = zh("临界带  0 < Re(s) < 1", 24, STRIP_COLOR).next_to(strip, RIGHT, buff=0.15).shift(UP * 2.6)
            self.play(FadeOut(ext), FadeOut(q), FadeIn(strip), Write(strip_l), run_time=2)

        with self.voice("zeta_5"):
            zs = zeta_zeros(8)
            crit = DashedLine(ax.c2p(0.5, -45), ax.c2p(0.5, 45), color=LINE_COLOR, stroke_width=3)
            crit_l = MathTex(r"\mathrm{Re}(s) = \tfrac12", font_size=32, color=LINE_COLOR).next_to(
                ax.c2p(1, 23), RIGHT, buff=0.2)
            dots = VGroup()
            for t in zs:
                if t < 45:
                    dots.add(Dot(ax.c2p(0.5, t), color=ZERO_COLOR, radius=0.075),
                             Dot(ax.c2p(0.5, -t), color=ZERO_COLOR, radius=0.075))
            first = MathTex(r"\tfrac12 + 14.1347\,i", font_size=28, color=ZERO_COLOR).next_to(
                ax.c2p(1, zs[0]), RIGHT, buff=0.2)
            self.play(Create(crit), FadeIn(crit_l), run_time=1.5)
            self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15), run_time=3)
            self.play(FadeIn(first))
            self.wait(1.5)
            box_txt = VGroup(zh("黎曼猜想", 34, YELLOW),
                             zh("所有非平凡零点", 26), MathTex(r"\mathrm{Re}(s) = \tfrac12", font_size=40)
                             ).arrange(DOWN, buff=0.2)
            panel = SurroundingRectangle(box_txt, color=YELLOW, buff=0.3, fill_color=BG_CARD, fill_opacity=0.95)
            card = VGroup(panel, box_txt).to_corner(DR, buff=0.4)
            self.play(FadeIn(card, shift=LEFT * 0.3), run_time=1.5)
        self.clear()


# ====================================================================== 4 素数的音乐
class S04_Music(VoiceScene):
    def construct(self):
        zs = zeta_zeros(100)
        X0, X1 = 1.6, 30
        with self.voice("music_1"):
            formula = MathTex(r"\psi(x)", r"=", r"x", r"-", r"\sum_{\rho} \frac{x^{\rho}}{\rho}", r"-",
                              r"\ln 2\pi - \tfrac12 \ln\!\left(1 - x^{-2}\right)", font_size=44).to_edge(UP, buff=0.35)
            formula[0].set_color(PRIME_COLOR)
            formula[4].set_color(ZERO_COLOR)
            b = Brace(formula[4], DOWN, buff=0.08, color=ZERO_COLOR)
            bl = zh("每个零点 ρ 贡献一个波动", 22, ZERO_COLOR).next_to(b, DOWN, buff=0.08)
            ax = Axes(x_range=[0, X1, 5], y_range=[0, 32, 10], x_length=10.5, y_length=4.4,
                      axis_config={"include_numbers": True, "font_size": 20, "stroke_width": 2},
                      tips=False).to_edge(DOWN, buff=0.4)
            jumps = []
            for p in primes_upto(X1):
                pk = p
                while pk <= X1:
                    jumps.append((pk, math.log(p)))
                    pk *= p
            jumps.sort()
            xs, ys, acc = [0], [0], 0.0
            for x, h in jumps:
                xs.append(x)
                acc += h
                ys.append(acc)
            xs.append(X1)
            stair = staircase(ax, xs, ys, PRIME_COLOR, 3)
            diag = ax.plot(lambda x: x, x_range=[0, X1], color=GREY_B, stroke_width=2)
            note = zh("ψ(x)：在每个素数幂 pᵏ 处跳高 ln p 的“素数阶梯”", 22, PRIME_COLOR).next_to(ax, UP, buff=0.05).to_edge(LEFT, buff=1)
            self.play(Write(formula), run_time=2.5)
            self.play(Create(ax), run_time=1)
            self.play(Create(stair), FadeIn(note), run_time=2.5, rate_func=linear)
            self.play(Create(diag), run_time=1)
            self.play(GrowFromCenter(b), FadeIn(bl), run_time=1)

        def approx(n):
            return ax.plot(lambda x: max(-1, psi_explicit(x, zs[:n])), x_range=[X0, X1, 0.02],
                           color=ZERO_COLOR, stroke_width=3, use_smoothing=False)

        with self.voice("music_2"):
            n_val = Integer(1, font_size=40, color=ZERO_COLOR)
            n_lbl = VGroup(zh("使用的零点个数：", 28), n_val).arrange(RIGHT, buff=0.2).next_to(ax, UP, buff=0.05).to_edge(RIGHT, buff=0.8)
            cur = approx(1)
            self.play(FadeOut(note), FadeOut(diag), Create(cur), FadeIn(n_lbl), run_time=1.5)
            for n in (3, 10, 30, 100):
                nxt = approx(n)
                self.play(Transform(cur, nxt), n_val.animate.set_value(n), run_time=1.8)
                self.wait(0.3)

        with self.voice("music_3"):
            self.play(FadeOut(VGroup(ax, stair, cur, n_lbl, b, bl, formula)), run_time=0.6)
            ax2 = Axes(x_range=[0, 100, 20], y_range=[-8, 8, 4], x_length=10, y_length=4.6,
                       axis_config={"include_numbers": True, "font_size": 20, "stroke_width": 2},
                       tips=False).to_edge(DOWN, buff=0.4)
            t = zs[0]

            def wave(sig):
                rho = complex(sig, t)
                return lambda x: 2 * (x ** complex(sig, t) / rho).real

            def envelope(sig, sgn):
                return lambda x: sgn * 2 * x ** sig / abs(complex(sig, t))

            w1 = ax2.plot(wave(0.5), x_range=[1, 100, 0.05], color=ZERO_COLOR, stroke_width=3)
            e1 = VGroup(*[DashedVMobject(ax2.plot(envelope(0.5, s), x_range=[1, 100, 1], color=ZERO_COLOR,
                                                  stroke_width=2, stroke_opacity=0.6), num_dashes=40) for s in (1, -1)])
            l1 = MathTex(r"\rho = \tfrac12 + 14.13\,i", font_size=34, color=ZERO_COLOR)
            l1z = zh("振幅 ∝ √x", 24, ZERO_COLOR)
            g1 = VGroup(l1, l1z).arrange(RIGHT, buff=0.25).move_to(LEFT * 3.3 + UP * 1.75)
            freq = zh("虚部 t → 频率", 30).move_to(LEFT * 3.3 + UP * 3.1)
            amp = zh("实部 σ → 振幅增长的快慢", 30).move_to(RIGHT * 2.8 + UP * 3.1)
            self.play(Create(ax2), FadeIn(freq), run_time=1.2)
            self.play(Create(w1), FadeIn(g1), run_time=2.5)
            self.play(FadeIn(amp), Create(e1), run_time=1.5)
            self.wait(1.5)
            w2 = ax2.plot(wave(0.85), x_range=[1, 100, 0.05], color=ORANGE, stroke_width=3)
            l2 = MathTex(r"\rho = 0.85 + 14.13\,i", font_size=34, color=ORANGE)
            l2z = zh("假想：离开临界线", 24, ORANGE)
            g2 = VGroup(l2, l2z).arrange(RIGHT, buff=0.25).move_to(RIGHT * 3.0 + UP * 1.75)
            self.play(Create(w2), FadeIn(g2), run_time=2.5)

        with self.voice("music_4"):
            self.play(FadeOut(VGroup(ax2, w1, w2, e1, g1, g2, freq, amp)), run_time=0.6)
            line = DashedLine(UP * 3.4, DOWN * 3.4, color=LINE_COLOR, stroke_width=3).shift(LEFT * 3.5)
            dots = VGroup(*[Dot(line.get_center() + UP * (z - 25) / 8, color=ZERO_COLOR, radius=0.08)
                            for z in zs[:9]])
            res = VGroup(
                zh("所有零点的实部 = 1/2", 32),
                MathTex(r"\Longrightarrow", font_size=48),
                zh("每个波动的振幅都不超过 √x 的量级", 32),
                zh("素数的误差最小", 32, YELLOW),
            ).arrange(DOWN, buff=0.35).shift(RIGHT * 2.2 + UP * 0.6)
            title = zh("“素数的音乐”", 44, YELLOW).next_to(res, DOWN, buff=0.7)
            self.play(Create(line), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1), run_time=1.5)
            self.play(LaggedStart(*[Broadcast(Circle(radius=0.6, color=ZERO_COLOR, stroke_width=2).move_to(d),
                                              n_mobs=3, focal_point=d.get_center(), run_time=2.5)
                                    for d in dots], lag_ratio=0.12),
                      Write(res), run_time=4)
            self.play(Write(title), run_time=1.5)
            self.play(LaggedStart(*[Broadcast(Circle(radius=0.6, color=ZERO_COLOR, stroke_width=2).move_to(d),
                                              n_mobs=3, focal_point=d.get_center(), run_time=2.5)
                                    for d in dots], lag_ratio=0.12), run_time=3)
        self.clear()


# ====================================================================== 5 历史
class S05_History(VoiceScene):
    def construct(self):
        tl = NumberLine(x_range=[1850, 2030, 10], length=12.6, include_numbers=False, stroke_width=2,
                        tick_size=0.06).shift(DOWN * 0.2)
        decade_labels = VGroup(*[Text(str(y), font_size=18, color=GREY_D).next_to(tl.n2p(y), DOWN, buff=0.15)
                                 for y in range(1850, 2031, 30)])

        def event(year, text, up=True, color=WHITE, size=22, stem_len=0.9):
            d = Dot(tl.n2p(year), color=color, radius=0.08)
            lab = VGroup(Text(str(year), font_size=22, color=color, weight=BOLD), zh(text, size, color))
            lab.arrange(DOWN, buff=0.08)
            stem = Line(tl.n2p(year), tl.n2p(year) + (UP if up else DOWN) * stem_len, stroke_width=1.5, color=GREY_D)
            lab.next_to(stem.get_end(), UP if up else DOWN, buff=0.08)
            return VGroup(d, stem, lab)

        with self.voice("hist_1"):
            title = zh("167 年的攻坚", 40, YELLOW).to_edge(UP, buff=0.5)
            self.play(Write(title), Create(tl), FadeIn(decade_labels), run_time=1.5)
            e1859 = event(1859, "黎曼的论文", True, YELLOW)
            e1900 = event(1900, "希尔伯特 23 问题\n之第 8 问题", False)
            e2000 = event(2000, "克雷千禧年大奖难题\n悬赏 100 万美元", True, OK_COLOR)
            for e in (e1859, e1900, e2000):
                self.play(FadeIn(e, shift=UP * 0.2), run_time=1.2)
                self.wait(2.2)

        with self.voice("hist_2"):
            e1914 = event(1914, "哈代：线上有\n无穷多个零点", True, BLUE_C)
            e1989 = event(1989, "康瑞：≥ 40%\n的零点在线上", False, BLUE_C)
            e2004 = event(2004, "计算验证：\n前 10 万亿个零点", False, BLUE_C, stem_len=2.2)
            e1989[2].shift(LEFT * 0.4)
            for e in (e1914, e1989, e2004):
                self.play(FadeIn(e, shift=UP * 0.2), run_time=1.2)
                self.wait(2.2)
            allq = zh("“全部”？", 44, RED).move_to(tl.n2p(2018) + UP * 2.2)
            self.play(Write(allq), run_time=1)

        with self.voice("hist_3"):
            self.play(FadeOut(VGroup(tl, decade_labels, e1859, e1900, e2000, e1914, e1989, e2004, allq)),
                      run_time=0.7)
            left = VGroup(zh("整数的世界", 32, WHITE), MathTex(r"\mathbb{Z}", font_size=60),
                          MathTex(r"\zeta(s)", font_size=44), zh("黎曼猜想：？", 30, RED)).arrange(DOWN, buff=0.4)
            right = VGroup(zh("平行世界：有限域上的多项式", 30, BLUE_C), MathTex(r"\mathbb{F}_q[t]", font_size=60),
                           zh("曲线的 ζ 函数", 28),
                           VGroup(zh("1940 年代  韦伊（曲线）", 26), check_mark(size=34)).arrange(RIGHT, buff=0.2),
                           VGroup(zh("1974  德利涅（一般情形）", 26), check_mark(size=34)).arrange(RIGHT, buff=0.2),
                           ).arrange(DOWN, buff=0.35)
            left.shift(LEFT * 3.5 + DOWN * 0.3)
            right.shift(RIGHT * 3.0 + DOWN * 0.3)
            sep = DashedLine(UP * 2.6, DOWN * 3.2, color=GREY_D)
            self.play(FadeIn(left, shift=RIGHT * 0.3), Create(sep), run_time=1.5)
            self.wait(1.5)
            self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.3) for m in right[:3]], lag_ratio=0.4), run_time=3)
            self.wait(1.5)
            self.play(FadeIn(right[3], shift=UP * 0.2), run_time=1)
            self.wait(1.5)
            self.play(FadeIn(right[4], shift=UP * 0.2), run_time=1)

        with self.voice("hist_4"):
            step = VGroup(zh("1969  斯捷潘诺夫：初等证法", 28, YELLOW)).next_to(right, DOWN, buff=0.4)
            self.play(FadeIn(step, shift=UP * 0.2), run_time=1)
            arrow = CurvedArrow(step.get_left() + LEFT * 0.1, left[3].get_right() + RIGHT * 0.1,
                                color=YELLOW, angle=-PI / 4)
            alab = zh("2026：灵感源头", 26, YELLOW).next_to(arrow, DOWN, buff=0.1)
            self.wait(2)
            self.play(Create(arrow), FadeIn(alab), run_time=2)
            self.play(Indicate(left[3], color=YELLOW), run_time=1.5)
        self.clear()


# ====================================================================== 6 证明思路
class S06_Idea(VoiceScene):
    def construct(self):
        foot = zh("高度简化的比喻，并非证明本身", 20, GREY_D).to_corner(DR, buff=0.25)
        pts = [1.0, 2.5, 4.0, 5.2]
        with self.voice("idea_1"):
            self.add(foot)
            title = zh("斯捷潘诺夫的方法：让辅助多项式“重重地”为零", 32, YELLOW).to_edge(UP, buff=0.5)
            ax = Axes(x_range=[0, 6, 1], y_range=[-2, 2.6, 1], x_length=10, y_length=4.6,
                      axis_config={"stroke_width": 2}, tips=False).shift(DOWN * 0.6)
            dots = VGroup(*[Dot(ax.c2p(p, 0), color=PRIME_COLOR, radius=0.1) for p in pts])
            dl = zh("曲线上要数的点", 24, PRIME_COLOR).next_to(dots[0], DOWN, buff=0.3)
            f1 = ax.plot(lambda x: 0.4 * np.prod([x - p for p in pts]), x_range=[0.8, 5.4], color=BLUE_C,
                         stroke_width=4)
            f2 = ax.plot(lambda x: 0.1 * np.prod([(x - p) ** 2 for p in pts]), x_range=[0.8, 5.4], color=BLUE_C,
                         stroke_width=4)
            m1 = zh("重数 1：从零点穿过", 28, BLUE_C).to_corner(UR, buff=0.6).shift(DOWN * 1)
            m2 = zh("重数 2：贴着零点，“重重地”为零", 28, BLUE_C).to_corner(UR, buff=0.6).shift(DOWN * 1)
            self.play(Write(title), Create(ax), run_time=1.5)
            self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.2), FadeIn(dl), run_time=1.5)
            self.wait(2)
            self.play(Create(f1), FadeIn(m1), run_time=2)
            self.wait(2)
            self.play(Transform(f1, f2), Transform(m1, m2), run_time=2)
            self.play(*[Flash(d, color=YELLOW) for d in dots], run_time=1)

        with self.voice("idea_2"):
            self.play(FadeOut(VGroup(ax, dots, dl, f1, m1)), run_time=0.6)
            ineq = MathTex(r"N", r"\times", r"m", r"\le", r"\deg f", font_size=60).shift(UP * 1.2)
            ineq[0].set_color(PRIME_COLOR)
            ineq[2].set_color(BLUE_C)
            legend = VGroup(zh("N：点的个数", 26, PRIME_COLOR), zh("m：每个点上的重数", 26, BLUE_C),
                            zh("deg f：多项式的次数", 26)).arrange(RIGHT, buff=0.7).next_to(ineq, UP, buff=0.5)
            total = 12
            bar = VGroup(*[Rectangle(width=0.8, height=0.5, stroke_color=GREY_B, stroke_width=1.5)
                           for _ in range(total)]).arrange(RIGHT, buff=0).shift(DOWN * 1)
            bl = zh("次数 = 零点“容量”", 24, GREY_B).next_to(bar, DOWN, buff=0.2)
            self.play(Write(ineq), FadeIn(legend), run_time=2)
            self.play(Create(bar), FadeIn(bl), run_time=1)
            colors = [PRIME_COLOR, TEAL, ORANGE, PINK]
            fills = VGroup()
            for i in range(4):
                g = VGroup(*[bar[i * 3 + j].copy().set_fill(colors[i], 0.6) for j in range(3)])
                fills.add(g)
            self.play(LaggedStart(*[FadeIn(g) for g in fills], lag_ratio=0.4), run_time=2)
            res = MathTex(r"\Longrightarrow\ N \le \frac{\deg f}{m}", font_size=56, color=YELLOW).next_to(bar, DOWN, buff=1.0)
            self.play(Write(res), run_time=1.5)

        with self.voice("idea_3"):
            self.play(FadeOut(VGroup(ineq, legend, bar, bl, fills, res)), run_time=0.6)
            lhs = VGroup(zh("多项式的世界", 30, BLUE_C),
                         MathTex(r"f(a) = f'(a) = f''(a) = 0", font_size=44),
                         MathTex(r"\Longrightarrow\ \text{multiplicity} \ge 3", font_size=40),
                         zh("用求导来衡量重数", 26, GREY_B)).arrange(DOWN, buff=0.4).shift(LEFT * 3.3)
            rhs = VGroup(zh("整数的世界", 30, PRIME_COLOR),
                         MathTex(r"\frac{d}{dn}\, 7 = \;?", font_size=56),
                         zh("对整数“求导”？", 28), cross_mark(size=60)).arrange(DOWN, buff=0.4).shift(RIGHT * 3.3)
            self.play(FadeIn(lhs, shift=RIGHT * 0.3), run_time=2)
            self.wait(2.5)
            self.play(FadeIn(rhs[:3], shift=LEFT * 0.3), run_time=2)
            self.play(GrowFromCenter(rhs[3]), run_time=0.8)

        with self.voice("idea_4"):
            self.play(FadeOut(VGroup(lhs, rhs, title)), run_time=0.6)
            title2 = VGroup(zh("突破：用一连串 θ 提升来模拟重数", 34, YELLOW),
                            zh("θ 提升：把自守形式（对称性极强的函数）搬运到更大的群上", 24, GREY_B)
                            ).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.5)
            names = [r"U(X_0)", r"U(X_1)", r"U(X_2)", r"U(X_3)", r"\cdots", r"U(X_m)"]
            boxes = VGroup()
            for nm in names:
                t = MathTex(nm, font_size=40)
                if nm == r"\cdots":
                    boxes.add(t)
                else:
                    boxes.add(VGroup(SurroundingRectangle(t, buff=0.2, color=BLUE_C, corner_radius=0.1), t))
            boxes.arrange(RIGHT, buff=0.85).shift(UP * 0.1)
            arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.08, stroke_width=3,
                                    max_tip_length_to_length_ratio=0.25, color=GREY_B) for i in range(len(boxes) - 1)])
            thetas = VGroup(*[MathTex(r"\theta", font_size=32, color=YELLOW).next_to(a, UP, buff=0.05) for a in arrows])
            plus = VGroup(*[zh("+1 重数", 20, OK_COLOR).next_to(a, DOWN, buff=0.6) for a in arrows])
            mult = ValueTracker(0)
            mlabel = always_redraw(lambda: VGroup(zh("累计重数：", 30),
                                                  Integer(int(mult.get_value()), font_size=44, color=OK_COLOR)
                                                  ).arrange(RIGHT, buff=0.2).shift(DOWN * 2))
            credit = VGroup(Text("Alpöge", font_size=24, color=HUMAN_COLOR), Text("+", font_size=24),
                            Text("Claude", font_size=24, color=CLAUDE_COLOR)).arrange(RIGHT, buff=0.15).next_to(mlabel, DOWN, buff=0.4)
            self.play(FadeIn(title2), run_time=1.5)
            self.play(FadeIn(boxes[0]), FadeIn(mlabel), run_time=1)
            for i in range(len(arrows)):
                anims = [GrowArrow(arrows[i]), FadeIn(thetas[i]), FadeIn(boxes[i + 1], shift=RIGHT * 0.2),
                         FadeIn(plus[i], shift=UP * 0.1)]
                if names[i + 1] != r"\cdots":
                    anims.append(mult.animate.set_value(mult.get_value() + (1 if i < 3 else 0)))
                self.play(*anims, run_time=1.1)
                self.wait(0.6)
            mlabel.clear_updaters()
            m_final = VGroup(zh("累计重数：", 30), MathTex("m", font_size=48, color=OK_COLOR)).arrange(RIGHT, buff=0.2).move_to(mlabel)
            self.play(Transform(mlabel, m_final), FadeIn(credit), run_time=1)

        with self.voice("idea_5"):
            self.play(FadeOut(VGroup(title2, plus, credit)), VGroup(boxes, arrows, thetas, mlabel).animate.scale(0.7).to_edge(UP, buff=0.8),
                      run_time=1)
            vm = VGroup(zh("长度为 X 的冯·曼戈尔特和", 28),
                        MathTex(r"\sum_{n \le X} \Lambda(n)", font_size=52),
                        MathTex(r"\Lambda(n) = \begin{cases}\ln p & n = p^k \\ 0 & \text{otherwise}\end{cases}",
                                font_size=30, color=GREY_B)).arrange(DOWN, buff=0.25).shift(LEFT * 3.5 + DOWN * 0.5)
            arrow = Arrow(LEFT * 1, RIGHT * 1, color=CLAUDE_COLOR).shift(DOWN * 0.5)
            claude_l = Text("Claude", font_size=24, color=CLAUDE_COLOR).next_to(arrow, UP, buff=0.1)
            chain = VGroup(zh("θ 提升的链长", 28), MathTex(r"m \approx \sqrt{X}", font_size=72, color=YELLOW)
                           ).arrange(DOWN, buff=0.3).shift(RIGHT * 3.5 + DOWN * 0.5)
            self.play(FadeIn(vm, shift=RIGHT * 0.2), run_time=2.5)
            self.wait(2.5)
            self.play(GrowArrow(arrow), FadeIn(claude_l), run_time=1)
            self.play(Write(chain), run_time=2)
            self.play(Circumscribe(chain[1], color=YELLOW), run_time=1.5)
            q = Text("“(And yet, what else could it be?)”", font="Latin Modern Roman", slant=ITALIC,
                     font_size=32).to_edge(DOWN, buff=1.0)
            qz = zh("“然而，它还能是别的什么呢？”", 24, GREY_B).next_to(q, DOWN, buff=0.15)
            self.wait(1)
            self.play(FadeIn(q), FadeIn(qz), run_time=1.5)
        self.clear()


# ====================================================================== 7 人与 AI
class S07_Collab(VoiceScene):
    def construct(self):
        with self.voice("collab_1"):
            human = VGroup(person(scale=1.3), Text("Levent Alpöge", font_size=28, color=HUMAN_COLOR)
                           ).arrange(DOWN, buff=0.2).shift(LEFT * 4 + UP * 0.6)
            ai = VGroup(claude_badge(1.0), Text("Claude", font_size=28, color=CLAUDE_COLOR)
                        ).arrange(DOWN, buff=0.2).shift(RIGHT * 4 + UP * 0.6)
            plan = zh("学生时代的秘密计划：用几十年攻克它", 28).shift(DOWN * 1.6)
            tools = ["解析数论", "代数几何", "自守形式", "函数域", "表示论", "算术几何"]
            tg = VGroup(*[tag(t, HUMAN_COLOR, 22) for t in tools]).arrange_in_grid(rows=2, buff=(0.25, 0.2))
            tg.next_to(human, RIGHT, buff=0.6)
            self.play(FadeIn(human, shift=RIGHT * 0.3), FadeIn(ai, shift=LEFT * 0.3), run_time=1.5)
            self.play(Write(plan), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(t, scale=0.8) for t in tg], lag_ratio=0.25), run_time=3)

        with self.voice("collab_2"):
            self.play(FadeOut(VGroup(plan, tg)), human.animate.scale(0.6).move_to(LEFT * 5.6 + UP * 2.7),
                      ai.animate.scale(0.6).move_to(LEFT * 5.6 + UP * 0.9), run_time=1)
            track_h = Line(LEFT * 4.6 + UP * 2.5, RIGHT * 5 + UP * 2.5, color=GREY_D, stroke_width=3)
            track_a = Line(LEFT * 4.6 + UP * 0.9, RIGHT * 5 + UP * 0.9, color=GREY_D, stroke_width=3)
            flag = VGroup(*[Square(0.18, fill_color=WHITE if (i + j) % 2 == 0 else BLACK, fill_opacity=1,
                                   stroke_width=0).move_to(RIGHT * (5.15 + 0.18 * i) + UP * (3.0 - 0.18 * j))
                            for i in range(2) for j in range(14)])
            fin = zh("终点", 22).next_to(flag, UP, buff=0.1)
            h_dot = Dot(track_h.get_start(), color=HUMAN_COLOR, radius=0.14)
            a_dot = Dot(track_a.get_start(), color=CLAUDE_COLOR, radius=0.14)
            self.play(Create(track_h), Create(track_a), FadeIn(flag), FadeIn(fin), FadeIn(h_dot), FadeIn(a_dot),
                      run_time=1)
            m1 = zh("玩具模型：结合两个截然不同的想法", 22, HUMAN_COLOR).next_to(track_h.point_from_proportion(0.28), UP, buff=0.2)
            m2 = zh("引向正确的情形", 22, HUMAN_COLOR).next_to(track_h.point_from_proportion(0.62), DOWN, buff=0.25)
            self.play(h_dot.animate.move_to(track_h.point_from_proportion(0.3)),
                      a_dot.animate.move_to(track_a.point_from_proportion(0.2)), FadeIn(m1), run_time=2)
            self.play(h_dot.animate.move_to(track_h.point_from_proportion(0.6)),
                      a_dot.animate.move_to(track_a.point_from_proportion(0.5)), FadeIn(m2), run_time=2)
            self.wait(1)
            self.play(h_dot.animate.move_to(track_h.point_from_proportion(0.72)),
                      a_dot.animate.move_to(track_a.get_end()), run_time=2, rate_func=rate_functions.rush_into)
            sparks = VGroup(*[sparkle(track_a.get_end() + np.array([dx, dy, 0]), YELLOW if k % 2 else CLAUDE_COLOR)
                              for k, (dx, dy) in enumerate([(-0.4, 0.4), (0.3, 0.5), (-0.2, -0.45), (0.45, -0.3), (-0.7, 0)])])
            self.play(LaggedStart(*[GrowFromCenter(s) for s in sparks], lag_ratio=0.2), run_time=1)
            q = quote_card("“Claude far outpaced me near the finish line.\n No, Claude flew, and danced, and sparkled near that finish line.”",
                           "“Claude 在终点线附近远远超过了我。不，Claude 在飞翔，在起舞，在闪闪发光。”",
                           width=12.5, en_size=28, color=CLAUDE_COLOR).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=1.5)

        with self.voice("collab_3"):
            self.play(FadeOut(VGroup(track_h, track_a, flag, fin, h_dot, a_dot, m1, m2, sparks, q, human, ai)),
                      run_time=0.7)
            from datetime import date
            d0 = date(2026, 10, 6)
            days = lambda d: (d - d0).days  # noqa: E731
            axis = NumberLine(x_range=[0, 41, 7], length=11.5, include_numbers=False, stroke_width=2).shift(UP * 1.2)
            events = [(date(2026, 10, 6), "斯捷潘诺夫行列式", True),
                      (date(2026, 10, 14), "GGP 周期与行列式", False),
                      (date(2026, 10, 19), "选定岩泽塔", True),
                      (date(2026, 11, 15), "迭代 θ 提升", False),
                      (date(2026, 11, 16), "GRH", True)]
            ev = VGroup()
            for d, txt, up in events:
                p = axis.n2p(days(d))
                dot = Dot(p, color=CLAUDE_COLOR if d.month == 11 else HUMAN_COLOR)
                lab = VGroup(Text(f"{d.month}/{d.day}", font_size=20, color=GREY_B),
                             zh(txt, 22, YELLOW if txt == "GRH" else WHITE)).arrange(DOWN, buff=0.06)
                lab.next_to(dot, UP if up else DOWN, buff=0.2)
                ev.add(VGroup(dot, lab))
            six = zh("≈ 6 周", 40, YELLOW).next_to(axis, DOWN, buff=1.1).shift(LEFT * 3)
            self.play(Create(axis), run_time=1)
            self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in ev], lag_ratio=0.3), run_time=3)
            self.play(Write(six))
            fields = ["自守形式", "θ 提升", "岩泽理论", "相对迹公式", "GGP 周期", "K 理论", "Chowla–Selberg 公式",
                      "Siegel 质量公式", "Vandiver 猜想", "Bost 斜率不等式", "Rallis 跷跷板", "庞加莱级数",
                      "Weyl 律", "Behrend 构造"]
            cloud = VGroup(*[tag(f, BLUE_D if i % 2 else PURPLE_D, 20) for i, f in enumerate(fields)])
            cloud.arrange_in_grid(rows=3, buff=(0.25, 0.25)).scale_to_fit_width(12.5).to_edge(DOWN, buff=0.4)
            self.play(FadeOut(six), LaggedStart(*[FadeIn(c, scale=0.7) for c in cloud], lag_ratio=0.15), run_time=4)
            src = zh("时间线与名词均摘自 Alpöge 的《Remark》", 18, GREY_D).to_corner(UR, buff=0.25)
            self.play(FadeIn(src))

        with self.voice("collab_4"):
            self.play(FadeOut(VGroup(axis, ev, cloud, src)), run_time=0.6)
            caveat = zh("“我个人对高阶群上的自守形式掌握不多”", 28, GREY_B).to_edge(UP, buff=1.0)
            q = quote_card("“I am presenting the world with a complete argument\n before having mastered a massive neighbourhood\n around its mathematics.”",
                           "“我是在还没有掌握它周围大片数学的情况下，就把一个完整的论证交给了世界。”",
                           "—— Levent Alpöge，《Remark》", width=12, en_size=32, color=HUMAN_COLOR).shift(DOWN * 0.5)
            self.play(FadeIn(caveat), run_time=1)
            self.wait(2.5)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=1.5)
        self.clear()


# ====================================================================== 8 Lean
class S08_Lean(VoiceScene):
    def construct(self):
        with self.voice("lean_1"):
            pages = VGroup(*[Rectangle(width=2.4, height=0.06, fill_color="#F4F1EA", fill_opacity=1,
                                       stroke_color="#9A968C", stroke_width=0.5) for _ in range(40)])
            pages.arrange(UP, buff=0.03).shift(LEFT * 3.8 + DOWN * 0.2)
            pages.rotate(0.03)
            n = ValueTracker(0)
            cnt = always_redraw(lambda: VGroup(Text(f"{int(n.get_value()):,}+", font_size=44, color=YELLOW, weight=BOLD),
                                               zh("页", 30)).arrange(RIGHT, buff=0.15).next_to(pages, DOWN, buff=0.3))
            book = zh("Claude 写的 GRH“书”", 30, CLAUDE_COLOR).next_to(pages, UP, buff=0.3)
            self.play(FadeIn(book), run_time=0.8)
            self.add(cnt)
            self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.05),
                      n.animate.set_value(250_000), run_time=4)
            cnt.clear_updaters()
            page = RoundedRectangle(corner_radius=0.05, width=7, height=3.6, fill_color="#F4F1EA", fill_opacity=1,
                                    stroke_width=0).shift(RIGHT * 2.4 + UP * 0.4)
            thm = VGroup(
                Text("Theorem 1.", font="Latin Modern Roman", weight=BOLD, font_size=30, color="#222222"),
                Text("Since the reals are totally ordered,", font="Latin Modern Roman", slant=ITALIC, font_size=28,
                     color="#222222"),
                MathTex(r"\text{if } \sigma \neq \tfrac12 \text{ then } \sigma > \tfrac12 \text{ or } \sigma < \tfrac12.",
                        font_size=38, color="#222222"),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(page)
            zh_t = zh("“因为实数是全序的，所以若 σ ≠ 1/2，则 σ > 1/2 或 σ < 1/2。”", 24, GREY_B).next_to(page, DOWN, buff=0.4)
            self.wait(3)
            self.play(FadeIn(page, shift=LEFT * 0.4), run_time=1)
            self.play(Write(thm), run_time=3)
            self.play(FadeIn(zh_t), run_time=1)
            self.wait(2)
            lol = zh("（阿尔珀格：“我当然被逗乐了”）", 22, GREY_D).next_to(zh_t, DOWN, buff=0.2)
            self.play(FadeIn(lol))

        with self.voice("lean_2"):
            self.play(FadeOut(VGroup(page, thm, zh_t, lol, book)), pages.animate.set_opacity(0.25), cnt.animate.set_opacity(0.3),
                      run_time=0.8)
            nope = zh("没人读得完", 30, RED).move_to(pages)
            self.play(FadeIn(nope, scale=1.3), run_time=0.8)
            self.wait(1)
            self.play(FadeOut(VGroup(pages, cnt, nope)), run_time=0.6)
            lean = VGroup(Text("Lean", font_size=54, weight=BOLD, color=LEAN_COLOR), zh("证明助手", 30)
                          ).arrange(RIGHT, buff=0.3).to_edge(UP, buff=0.6)
            self.play(FadeIn(lean), run_time=1)
            steps = VGroup(*[tag(s, LEAN_COLOR, 24) for s in ["引理 1", "引理 2", "引理 3", "……", "定理"]])
            steps.arrange(RIGHT, buff=0.8).shift(UP * 0.3)
            arr = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.08, color=GREY_B,
                                 stroke_width=3) for i in range(4)])
            kernel = tag("Lean 内核：逐步检查", OK_COLOR, 26).shift(DOWN * 1.8)
            self.play(LaggedStart(*[FadeIn(s) for s in steps], lag_ratio=0.2), LaggedStart(*[GrowArrow(a) for a in arr]),
                      run_time=2)
            self.play(FadeIn(kernel), run_time=0.8)
            ticks = VGroup(*[check_mark(size=34).next_to(s, UP, buff=0.12) for s in steps])
            self.play(LaggedStart(*[FadeIn(t, scale=1.4) for t in ticks], lag_ratio=0.25), run_time=2)
            gap = VGroup(cross_mark(size=40), zh("跳步？不被允许", 24, RED)).arrange(RIGHT, buff=0.15).next_to(kernel, DOWN, buff=0.4)
            self.play(FadeIn(gap), run_time=0.8)

        with self.voice("lean_3"):
            self.play(FadeOut(VGroup(steps, arr, kernel, ticks, gap)), run_time=0.6)
            path = mono("src/Main.lean", 22, GREY_B)
            code = Text("theorem riemannHypothesis : RiemannHypothesis := rhOfAll", font="JetBrains Mono",
                        font_size=28, t2c={"theorem": "#C678DD", "riemannHypothesis": "#61AFEF",
                                           "RiemannHypothesis": YELLOW, "rhOfAll": "#98C379"})
            panel = SurroundingRectangle(code, buff=0.35, color=GREY_D, fill_color=BG_CARD, fill_opacity=1,
                                         corner_radius=0.1)
            blk = VGroup(panel, code).shift(UP * 0.8)
            path.next_to(panel, UP, buff=0.12).align_to(panel, LEFT)
            self.play(FadeIn(blk), FadeIn(path), run_time=1.2)
            self.wait(1)
            ul = Underline(code[len("theorem riemannHypothesis : "):len("theorem riemannHypothesis : RiemannHypothesis")],
                           color=YELLOW)
            self.play(Create(ul), run_time=1)
            ml = VGroup(zh("Mathlib 中的标准定义", 30, YELLOW), zh("由 Lean 与数论专家审核，并非作者自定义", 24, GREY_B)
                        ).arrange(DOWN, buff=0.15).shift(DOWN * 1.8)
            a = Arrow(ul.get_bottom(), ml.get_top(), color=YELLOW, buff=0.15)
            self.wait(2)
            self.play(GrowArrow(a), FadeIn(ml), run_time=1.5)

        with self.voice("lean_4"):
            self.play(FadeOut(VGroup(blk, path, ul, a, ml)), run_time=0.6)
            lines = [
                ("def RiemannHypothesis : Prop :=", "Mathlib 中的定义"),
                ("  ∀ (s : ℂ) (_ : riemannZeta s = 0)", "对任意复数 s，若 ζ(s) = 0"),
                ("    (_ : ¬∃ n : ℕ, s = -2 * (n + 1))", "且 s 不是 −2, −4, −6, …"),
                ("    (_ : s ≠ 1),", "且 s ≠ 1"),
                ("    s.re = 1 / 2", "⇒ s 的实部 = 1/2"),
            ]
            code = VGroup(*[Text(c, font="JetBrains Mono", font_size=24,
                                 t2c={"def": "#C678DD", "RiemannHypothesis": YELLOW, "Prop": "#E5C07B",
                                      "riemannZeta": "#61AFEF", "s.re": "#61AFEF"}) for c, _ in lines])
            code.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
            code[1].shift(RIGHT * 0.3)
            for c in code[2:]:
                c.shift(RIGHT * 0.6)
            panel = SurroundingRectangle(code, buff=0.35, color=GREY_D, fill_color=BG_CARD, fill_opacity=1,
                                         corner_radius=0.1)
            blk = VGroup(panel, code).to_edge(LEFT, buff=0.4)
            notes = VGroup(*[zh(z, 24, GREY_B).next_to(code[i], RIGHT, buff=0.3).set_x(4.3)
                             for i, (_, z) in enumerate(lines)])
            for i, nmo in enumerate(notes):
                nmo.set_y(code[i].get_y()).set_x(panel.get_right()[0] + 0.3 + nmo.width / 2)
            self.play(FadeIn(blk), run_time=1)
            for i in range(1, len(lines)):
                self.play(code[i].animate.set_color(WHITE).scale(1.0), FadeIn(notes[i], shift=LEFT * 0.2), run_time=1.2)
                self.wait(0.8)
            self.play(Circumscribe(code[4], color=YELLOW), notes[4].animate.set_color(YELLOW), run_time=1.2)

        with self.voice("lean_5"):
            self.play(FadeOut(VGroup(blk, notes)), run_time=0.6)
            libs = [("Development", 12_232_663), ("Formalism", 3_200_748), ("GroundTheory", 1_119_138),
                    ("ReciprocityTheory", 563_016), ("CompanionTheory", 194_218), ("其他", 64_404)]
            W, H = 6.8, 4.6
            total = sum(v for _, v in libs)
            rects = VGroup()
            x0 = -W / 2
            w_dev = W * libs[0][1] / total
            cols = [BLUE_D, TEAL_D, PURPLE_D, MAROON_D, GOLD_D, GREY_D]
            r = Rectangle(width=w_dev, height=H, fill_color=cols[0], fill_opacity=0.6, stroke_color=WHITE,
                          stroke_width=1.5).move_to([x0 + w_dev / 2, 0, 0])
            rects.add(VGroup(r, VGroup(Text(libs[0][0], font_size=22), Text(f"{libs[0][1] / 1e6:.1f}M 行", font_size=20,
                                                                              color=GREY_B)).arrange(DOWN, buff=0.1).move_to(r)))
            rest = libs[1:]
            rest_total = sum(v for _, v in rest)
            y = H / 2
            wr = W - w_dev
            for i, (nm, v) in enumerate(rest):
                h = H * v / rest_total
                rr = Rectangle(width=wr, height=h, fill_color=cols[i + 1], fill_opacity=0.6, stroke_color=WHITE,
                               stroke_width=1.5).move_to([x0 + w_dev + wr / 2, y - h / 2, 0])
                y -= h
                lab = Text(nm if h > 0.45 else "", font_size=16) if nm != "其他" else zh("", 14)
                if h > 0.45:
                    lab.move_to(rr)
                    if lab.width > wr - 0.1:
                        lab.scale_to_fit_width(wr - 0.15)
                rects.add(VGroup(rr, lab))
            rects.shift(LEFT * 2.9 + DOWN * 0.3)
            stats = VGroup(
                VGroup(Text("175,187", font_size=44, color=YELLOW, weight=BOLD), zh("个文件", 26)).arrange(RIGHT, buff=0.15),
                VGroup(Text("≈ 17,370,000", font_size=40, color=YELLOW, weight=BOLD), zh("行", 26)).arrange(RIGHT, buff=0.15),
                VGroup(Text("0", font_size=44, color=OK_COLOR, weight=BOLD), zh("处 sorry（跳过的证明）", 26)).arrange(RIGHT, buff=0.15),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(rects, RIGHT, buff=0.6)
            self.play(LaggedStart(*[FadeIn(r) for r in rects], lag_ratio=0.15), run_time=2)
            self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in stats], lag_ratio=0.5), run_time=3)
            self.wait(2.5)
            bonus = VGroup(zh("另外还证明了：所有狄利克雷 L 函数的广义黎曼猜想", 26), check_mark(size=34)
                           ).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(bonus, shift=UP * 0.2), run_time=1)
        self.clear()


# ====================================================================== 9 核查
class S09_Verify(VoiceScene):
    def construct(self):
        crit = ["陈述正确吗？", "能编译吗？", "证明的是这个陈述吗？", "证明本身有效吗？"]
        with self.voice("verify_1"):
            title = VGroup(zh("检查 AI 生成的 Lean 证明：四条标准", 34, YELLOW),
                           zh("Kevin Buzzard，2026-11-12", 22, GREY_B)).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.4)
            rows = VGroup()
            for i, c in enumerate(crit):
                box = Square(0.45, stroke_color=GREY_B, stroke_width=2)
                rows.add(VGroup(box, Text(f"{i + 1}", font_size=26, color=BLUE_B), zh(c, 30)).arrange(RIGHT, buff=0.3))
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(DOWN * 0.4)
            self.play(Write(title), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.3), run_time=3)
        mini = rows.copy()

        def tick(i):
            return check_mark(size=38).move_to(mini[i][0])

        with self.voice("verify_2"):
            self.play(mini.animate.scale(0.6).to_corner(UL, buff=0.4).shift(DOWN * 0.9), FadeOut(rows), run_time=1)
            t1 = tick(0)
            c1 = VGroup(zh("① 用 Mathlib 里早已审核过的标准定义", 26), check_mark(size=32)).arrange(RIGHT, buff=0.2).shift(UP * 1.6 + RIGHT * 1.6)
            self.play(FadeIn(c1), FadeIn(t1, scale=1.5), run_time=1.2)
            self.wait(2.5)
            machines = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.5, height=0.35, stroke_color=LEAN_COLOR,
                                                 stroke_width=1.5) for _ in range(24)])
            machines.arrange_in_grid(rows=3, buff=0.18).shift(RIGHT * 1.6 + DOWN * 0.1)
            ml = zh("② 几十人各自重新编译", 26).next_to(machines, UP, buff=0.3)
            self.play(FadeIn(ml), LaggedStart(*[Create(m) for m in machines], lag_ratio=0.05), run_time=2)
            self.play(LaggedStart(*[m.animate.set_fill(OK_COLOR, 0.6) for m in machines], lag_ratio=0.05), run_time=2)
            same = VGroup(zh("同一个导出文件", 24), mono("sha256 5ea74b91…244e", 22, YELLOW),
                          zh("61,570,595,788 字节", 24, GREY_B)).arrange(DOWN, buff=0.12).next_to(machines, DOWN, buff=0.35)
            self.play(FadeIn(same, shift=UP * 0.2), FadeIn(tick(1), scale=1.5), run_time=1.5)
        self.add(t1)

        with self.voice("verify_3"):
            self.play(FadeOut(VGroup(c1, machines, ml, same)), run_time=0.6)
            ch = VGroup(zh("陈述文件", 26, YELLOW), mono("只 import Mathlib", 20, GREY_B)).arrange(DOWN, buff=0.1)
            ch_box = SurroundingRectangle(ch, buff=0.3, color=YELLOW, corner_radius=0.1)
            so = VGroup(zh("阿尔珀格的证明", 26, LEAN_COLOR), mono("Main.lean", 20, GREY_B)).arrange(DOWN, buff=0.1)
            so_box = SurroundingRectangle(so, buff=0.3, color=LEAN_COLOR, corner_radius=0.1)
            left = VGroup(ch_box, ch).move_to(LEFT * 4.3 + DOWN * 0.4)
            right = VGroup(so_box, so).move_to(RIGHT * 4.3 + DOWN * 0.4)
            tools = VGroup(tag("comparator", GREY_B, 22, font="JetBrains Mono"),
                           tag("con-leche --compare", GREY_B, 22, font="JetBrains Mono")).arrange(DOWN, buff=0.25).move_to(DOWN * 0.4)
            eq = MathTex(r"=", font_size=90, color=OK_COLOR).next_to(tools, DOWN, buff=0.4)
            self.play(FadeIn(left), FadeIn(right), run_time=1.5)
            self.play(FadeIn(tools, scale=0.9), run_time=1.5)
            self.wait(2)
            self.play(Write(eq), FadeIn(tick(2), scale=1.5), run_time=1.5)
            note = zh("③ 证明的定理与标准陈述完全一致", 26).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(note))

        with self.voice("verify_4"):
            self.play(FadeOut(VGroup(left, right, tools, eq, note)), run_time=0.6)
            export = VGroup(zh("导出的证明", 26), Text("1,468,418", font_size=30, color=YELLOW), zh("条声明", 22)
                            ).arrange(DOWN, buff=0.1)
            ebox = SurroundingRectangle(export, buff=0.3, color=YELLOW, corner_radius=0.1)
            exp = VGroup(ebox, export).shift(LEFT * 1.2)
            checkers = [("Lean 官方内核", "C++"), ("nanoda", "Rust"), ("con-leche / con-ron", "自带形式化正确性证明"),
                        ("lean4lean", "用 Lean 写成")]
            cg = VGroup(*[VGroup(tag(a, LEAN_COLOR, 22), zh(b, 18, GREY_B)).arrange(DOWN, buff=0.08) for a, b in checkers])
            cg.arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(RIGHT * 3.8)
            arrows = VGroup(*[Arrow(ebox.get_right(), c[0].get_left(), buff=0.1, stroke_width=2.5, color=GREY_B) for c in cg])
            self.play(FadeIn(exp), run_time=1)
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(c)) for a, c in zip(arrows, cg)], lag_ratio=0.4),
                      run_time=4)
            oks = VGroup(*[check_mark(size=32).next_to(c[0], RIGHT, buff=0.15) for c in cg])
            self.play(LaggedStart(*[FadeIn(o, scale=1.5) for o in oks], lag_ratio=0.3), run_time=2.5)
            self.wait(2)
            ax_l = VGroup(zh("用到的公理：", 24), mono("propext · Classical.choice · Quot.sound", 22, OK_COLOR)
                          ).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(ax_l, shift=UP * 0.2), FadeIn(tick(3), scale=1.5), run_time=1.5)

        with self.voice("verify_5"):
            self.play(FadeOut(VGroup(exp, cg, arrows, oks, ax_l, mini, title, t1)), run_time=0.6)
            for m in list(self.mobjects):
                self.remove(m)
            q = quote_card("“We have full confidence that Alpöge's proof\n of the Riemann Hypothesis is correct.”",
                           "“我们完全确信，阿尔珀格对黎曼猜想的证明是正确的。”",
                           "—— Lean 与 Mathlib 社区联合声明（Lean FRO、Mathlib Initiative 背书），2026-11-21",
                           width=12, en_size=34, color=OK_COLOR).shift(UP * 0.8)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=1.5)
            self.wait(5)
            drew = VGroup(zh("核查汇总：Andrew Sutherland（MIT）", 28),
                          VGroup(zh("运行检查所用的工具：", 26, GREY_B), Text("Claude Code", font_size=28, color=CLAUDE_COLOR)
                                 ).arrange(RIGHT, buff=0.15)).arrange(DOWN, buff=0.2).next_to(q, DOWN, buff=0.6)
            self.play(FadeIn(drew, shift=UP * 0.2), run_time=1.5)
        self.clear()


# ====================================================================== 10 意义
class S10_Meaning(VoiceScene):
    def construct(self):
        with self.voice("mean_1"):
            v = VGroup(zh("被验证", 54, OK_COLOR), check_mark(size=60)).arrange(RIGHT, buff=0.3)
            u = VGroup(zh("被理解", 54, GREY_B), Text("…", font_size=60, color=GREY_B)).arrange(RIGHT, buff=0.3)
            VGroup(v, u).arrange(RIGHT, buff=2.5).shift(UP * 0.8)
            bar_bg = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.3, stroke_color=GREY_D).next_to(u, DOWN, buff=0.5)
            bar = RoundedRectangle(corner_radius=0.1, width=0.25, height=0.3, fill_color=GREY_B, fill_opacity=0.8,
                                   stroke_width=0).align_to(bar_bg, LEFT).set_y(bar_bg.get_y())
            bar_v = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.3, fill_color=OK_COLOR, fill_opacity=0.8,
                                     stroke_width=0).next_to(v, DOWN, buff=0.5)
            self.play(FadeIn(v, shift=UP * 0.2), FadeIn(bar_v), run_time=1.5)
            self.wait(1)
            self.play(FadeIn(u, shift=UP * 0.2), FadeIn(bar_bg), FadeIn(bar), run_time=1.5)
            why = zh("Lean 说明它是对的；但它“为什么”对，还没有人真正读懂", 28).shift(DOWN * 1.6)
            self.play(Write(why), run_time=2)

        with self.voice("mean_2"):
            self.play(FadeOut(VGroup(v, u, bar_bg, bar, bar_v, why)), run_time=0.6)
            title = zh("克雷研究所的规则", 34, YELLOW).to_edge(UP, buff=0.5)
            steps = VGroup(tag("在合格期刊发表", BLUE_D, 26), tag("等待两年", BLUE_D, 26), tag("数学界普遍认可", BLUE_D, 26))
            steps.arrange(RIGHT, buff=1.0).shift(UP * 1.5)
            arr = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.1, color=GREY_B) for i in range(2)])
            status = VGroup(zh("克雷官网（2026-11-22）：", 26, GREY_B),
                            Text("Unsolved", font_size=30, color=RED, weight=BOLD)).arrange(RIGHT, buff=0.2).next_to(steps, DOWN, buff=0.5)
            self.play(Write(title), run_time=1)
            self.play(LaggedStart(*[FadeIn(s) for s in steps], lag_ratio=0.4), LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.4),
                      run_time=3)
            self.wait(1.5)
            self.play(FadeIn(status), run_time=1)
            self.wait(1.5)
            q = quote_card("“This is indeed an historic moment.”\n“There is much work to be done to understand\n the mathematical details of the proof.”",
                           "“这确实是一个历史性时刻。” “要理解证明的数学细节，还有大量工作要做。”",
                           "—— Andrew Sutherland（MIT），据《科学美国人》", width=12, en_size=30, color=BLUE_C).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=1.5)

        with self.voice("mean_3"):
            self.play(FadeOut(VGroup(title, steps, arr, status, q)), run_time=0.6)
            robin = MathTex(r"\sigma(n)", r"<", r"e^{\gamma}\, n \ln\ln n", r"\quad (n > 5040)", font_size=50).to_edge(UP, buff=0.5)
            robin[0].set_color(PRIME_COLOR)
            sig = MathTex(r"\sigma(12) = 1+2+3+4+6+12 = 28", font_size=34, color=GREY_B).next_to(robin, DOWN, buff=0.25)
            src = zh("Robin 不等式：与黎曼猜想等价（Robin, 1984）", 22, GREY_B).next_to(sig, DOWN, buff=0.15)
            self.play(Write(robin), run_time=2)
            self.play(FadeIn(sig), FadeIn(src), run_time=1.5)
            N = 100_000
            s = sigma_upto(N)
            ns = np.arange(3, N + 1)
            ratio = s[3:] / (ns * np.log(np.log(ns)))
            ax = Axes(x_range=[0.5, 5, 1], y_range=[1.3, 2.0, 0.1], x_length=10, y_length=3.6, tips=False,
                      axis_config={"stroke_width": 2, "font_size": 20},
                      y_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 1}},
                      ).to_edge(DOWN, buff=0.5)
            xl = VGroup(*[MathTex(f"10^{k}", font_size=26).next_to(ax.c2p(k, 1.3), DOWN, buff=0.15) for k in range(1, 6)])
            bins = np.linspace(np.log10(3), np.log10(N), 260)
            idx = np.digitize(np.log10(ns), bins)
            pts = VGroup()
            for b in np.unique(idx):
                sel = np.nonzero(idx == b)[0]
                j = sel[np.argmax(ratio[sel])]
                if 1.3 < ratio[j] < 2.0:
                    n = ns[j]
                    pts.add(Dot(ax.c2p(math.log10(n), ratio[j]), radius=0.035,
                                color=RED if n <= 5040 and ratio[j] >= math.exp(0.5772156649) else PRIME_COLOR))
            bound = DashedLine(ax.c2p(0.5, math.exp(0.5772156649)), ax.c2p(5, math.exp(0.5772156649)), color=BLUE_C)
            bl = MathTex(r"e^{\gamma} \approx 1.781", font_size=30, color=BLUE_C).next_to(bound, RIGHT, buff=0.1).shift(UP * 0.2)
            mark = DashedLine(ax.c2p(math.log10(5040), 1.3), ax.c2p(math.log10(5040), 2.0), color=GREY_B, stroke_width=1.5)
            ml = Text("n = 5040", font_size=20, color=GREY_B).next_to(ax.c2p(math.log10(5040), 1.32), RIGHT, buff=0.08)
            yl = MathTex(r"\frac{\sigma(n)}{n \ln\ln n}", font_size=28).next_to(ax.y_axis, LEFT, buff=0.55).shift(UP * 1.2)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.5)
            self.play(Create(bound), FadeIn(bl), run_time=1)
            self.play(LaggedStart(*[FadeIn(p) for p in pts], lag_ratio=0.01), run_time=4)
            self.play(Create(mark), FadeIn(ml), run_time=1)
            cap = zh("5040 之后，再也没有越过这条线", 24, YELLOW).move_to(ax.c2p(3.9, 1.93))
            self.play(FadeIn(cap), run_time=1)

        with self.voice("mean_4"):
            self.play(FadeOut(VGroup(robin, sig, src, ax, xl, yl, bound, bl, pts, mark, ml, cap)), run_time=0.6)
            now = VGroup(zh("现在", 30, GREY_B), zh("长得惊人", 44)).arrange(DOWN, buff=0.2).shift(LEFT * 3.5 + UP * 1)
            fut = VGroup(zh("直觉", 30, GREY_B), zh("会被大大简化", 44, YELLOW)).arrange(DOWN, buff=0.2).shift(RIGHT * 3.2 + UP * 1)
            arr = Arrow(now.get_right(), fut.get_left(), buff=0.4, color=GREY_B)
            todo = VGroup(*[tag(t, HUMAN_COLOR, 30) for t in ["理解它", "讲清楚它", "好好地写出来"]]).arrange(RIGHT, buff=0.6).shift(DOWN * 1.6)
            self.play(FadeIn(now), run_time=1)
            self.play(GrowArrow(arr), FadeIn(fut), run_time=1.5)
            self.wait(3)
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in todo], lag_ratio=0.5), run_time=3)

        with self.voice("mean_5"):
            self.play(FadeOut(VGroup(now, fut, arr, todo)), run_time=0.6)
            line = DashedLine(UP * 3.6, DOWN * 3.6, color=LINE_COLOR, stroke_width=2, stroke_opacity=0.5).shift(LEFT * 5.5)
            dots = VGroup(*[Dot(line.get_center() + UP * (z - 28) / 8, color=ZERO_COLOR, radius=0.06)
                            for z in zeta_zeros(12)])
            q = quote_card("“…a glimpse towards the miracles that lie ahead,\n and shows us the joy and wonder\n we are about to find in the simplest things.”",
                           "“……瞥见前方的奇迹，让我们看到，在最简单的事物里，即将找到的喜悦与惊奇。”",
                           "—— Levent Alpöge，《Remark》", width=11, en_size=32, color=YELLOW).shift(RIGHT * 0.8)
            self.play(Create(line), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1), run_time=2)
            self.play(FadeIn(q, shift=UP * 0.3), run_time=2)
            self.wait(6)
            thanks = zh("感谢收看", 40).next_to(q, DOWN, buff=0.5)
            self.play(FadeIn(thanks), run_time=1)

        self.play(FadeOut(VGroup(q, thanks)), run_time=0.8)
        refs = VGroup(
            zh("资料来源", 30, YELLOW),
            zh("Levent Alpöge，《Remark》，2026-11-20 · alpo.ge/remark.pdf", 22),
            zh("Lean 证明代码库 · alpo.ge/lean.tar.gz.part01–14", 22),
            zh("Lean 与 Mathlib 社区联合声明，2026-11-21 · leanprover-community.github.io/blog", 22),
            zh("Andrew Sutherland，核查汇总 · math.mit.edu/~drew/grh", 22),
            zh("克雷数学研究所 · claymath.org/millennium/riemann-hypothesis", 22),
            zh("《科学美国人》报道，2026-11-21", 22),
            zh("证明思路部分为高度简化的科普比喻；技术细节以原文与 Lean 代码为准。", 20, GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).shift(RIGHT * 0.6)
        self.play(FadeIn(refs, shift=UP * 0.2), run_time=1.2)
        self.wait(5)
        self.clear(1.2)
