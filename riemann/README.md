# 黎曼猜想被证明了？——Levent Alpöge 与 Claude 的证明

面向大众的中文科普视频（3Blue1Brown 风格，Manim），约 12 分钟，10 个场景、45 句旁白。
旁白由 **MiniMax `speech-2.8-turbo`** 合成（音色 `Chinese (Mandarin)_Gentleman`，温润男声），
字幕由旁白时间轴自动生成。

| # | 场景 | 内容 |
|---|------|------|
| 1 | `S01_Intro` | 2026-11-20 的四页短文《Remark》、那句话、1700 万行 Lean 代码、提纲 |
| 2 | `S02_Primes` | 素数分布、高斯的 1/ln n、π(x) 与 li(x)、误差 √x·ln x 的包络 |
| 3 | `S03_Zeta` | ζ(s)、ζ(2)=π²/6、欧拉乘积、复平面、平凡零点、临界带与临界线 |
| 4 | `S04_Music` | 显式公式：用前 1~100 个零点重建素数阶梯；单个零点的波动与振幅 |
| 5 | `S05_History` | 1859–2004 时间线；函数域上的平行世界（韦伊、德利涅、斯捷潘诺夫） |
| 6 | `S06_Idea` | 斯捷潘诺夫的“重数”思想；整数上没有“求导”；θ 提升链与链长 √X |
| 7 | `S07_Collab` | 人与 AI 的分工、“Claude 在飞翔”、六周时间线、用到的数学分支 |
| 8 | `S08_Lean` | 25 万页的“书”、Lean 证明助手、`riemannHypothesis` 与 Mathlib 定义、代码规模 |
| 9 | `S09_Verify` | Buzzard 的四条标准；编译复现、陈述比对、多内核复核、社区联合声明 |
| 10 | `S10_Meaning` | 验证 ≠ 理解；克雷规则；Robin 不等式；未来的简化；结语与资料来源 |

## 构建

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt mpmath
export MINIMAX_API_KEY=...                                  # 不要写进仓库
.venv/bin/python build.py tts --project riemann --tts minimax
.venv/bin/python build.py render --project riemann -q h -j 4
.venv/bin/python build.py assemble --project riemann -q h --burn-subs
# 产物：build/riemann/riemann_hypothesis_alpoge_claude.mp4（+ .srt）
```

- 只重配某几句：`python tts/minimax_tts.py --project riemann --only intro_1 mean_5 --force`
- 换音色前先试听：`python tts/minimax_tts.py --project riemann --audition "Chinese (Mandarin)_Male_Announcer" ...`
- 读音问题：在 `narration.py` 的 `TTS_REPLACEMENTS` 里加替换规则。
- 不用 MiniMax 也行：`--tts qwen` 走本地 Qwen3-TTS（Apple Silicon 用 MLX，其他平台用 torch，见根目录 README）。

**为什么用同步接口**：动画按句与旁白对齐，需要每句单独的音频和时长；每句都远小于同步接口 10000 字的上限。
异步长文本接口面向十万字级别的文本、返回一整段音频，这里用不上。

## 资料与事实核对（2026-11-22）

- Levent Alpöge，*Remark*（4 页）：<https://alpo.ge/remark.pdf>
- 证明本体：<https://alpo.ge/lean.tar.gz.part01> … `part14`（约 239 MB；175,187 个 `.lean` 文件，约 1737 万行；
  `src/Main.lean` 中 `theorem riemannHypothesis : RiemannHypothesis := rhOfAll`；源码里没有 `sorry` 或自定义 `axiom`）
- Lean 与 Mathlib 社区联合声明（2026-11-21）：<https://leanprover-community.github.io/blog/posts/riemann-hypothesis/>
- Andrew Sutherland 的核查汇总：<https://math.mit.edu/~drew/grh/>
- 克雷数学研究所问题页（截至 2026-11-22 仍标为 Unsolved）：<https://www.claymath.org/millennium/riemann-hypothesis/>
- 《科学美国人》报道（Sutherland 的引语出处）

第 6 场“证明思路”是高度简化的科普比喻；技术细节以原文和 Lean 代码为准。
片中的“GRH”指 Lean 中实际验证的范围：所有狄利克雷 L 函数。
