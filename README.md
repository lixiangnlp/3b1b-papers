# 3b1b-papers · 3Blue1Brown 风格中文论文讲解

用 [Manim](https://www.manim.community/) 制作 3Blue1Brown 风格的中文论文讲解视频，
旁白逐句合成，动画与语音自动对齐。目前包含两期：

| `--paper` | 论文 | 时长 |
|---|---|---|
| `attention` | Vaswani et al., *Attention Is All You Need*（NeurIPS 2017） | ~10 分钟 · 10 场景 |
| `smhbench` | Kuan Li et al., *SMH-Bench: Benchmarking LLM Agents for Environment-Grounded Reasoning and Action in Smart Homes*（[arXiv:2606.01912](https://arxiv.org/abs/2606.01912)） | ~20 分钟 · 17 场景 |

## SMH-Bench 分集（完整版，依据论文全文）

| # | 场景 | 内容 |
|---|------|------|
| 1 | `S01_Intro` | “调成昨晚的温度”：理解、推理、记忆、行动；作者与机构；三部分提纲 |
| 2 | `S02_Motivation` | 静态指令→API 映射的盲点；表 1：HomeBench / SimuHome / SMH-Bench 能力对比 |
| 3 | `S03_Formulation` | Hₜ=(R,D,φ,Xₜ,S)、动作与状态转移、实例 τ=(H₀,u,C,M,g)、四种输出、无关状态保持 |
| 4 | `S04_HomeEnv` | 嵌套房间的状态空间、属性与服务、操作引擎的合法性检查、查询/控制接口 |
| 5 | `S05_Control` | TC1 原子控制（含带噪声纠错）；TC2 组合控制五子类，“湿度高于 60%”例子的逐步执行 |
| 6 | `S06_Ambiguity` | TC3 模糊意图（执行 vs 澄清、三子类）；TC4 自动化调度三种触发 |
| 7 | `S07_Context` | TC5 多轮交互四子类；TC6 短期/长期记忆；TC7 环境查询 |
| 8 | `S08_Pipeline` | 环境优先的四步构建：家实例、GPT-5 规格与指令、HomeEnv 校验、人工审核 |
| 9 | `S09_Stats` | 图 3 类别分布；简单/中等/复杂 550/330/220；房间与设备规模 |
| 10 | `S10_Protocol` | 规则校验 + 无关状态保持、TC4 双重校验、GPT-5 裁判与 98% 人机一致率 |
| 11 | `S11_Settings` | DR（完整上下文、一次作答、重放）vs EIA（ReAct、query/control_device、快照差分） |
| 12 | `S12_Overall` | 表 2：13 个模型 EIA 平均成功率排行 |
| 13 | `S13_Capability` | 表 2 热力图：TC1/TC7 最易，TC4 为共同瓶颈 |
| 14 | `S14_Modes` | ∆(EIA−DR)；Claude-Sonnet-4.6 TC3、GPT-5.4 TC4 的对比；级联误差 |
| 15 | `S15_Complexity` | 图 4 复杂度下降、DeepSeek-V3.2 关闭思考的消融（图 5）、子类分工 |
| 16 | `S16_Errors` | 表 3 六类错误与图 6 DeepSeek-V3.2 错误分布 |
| 17 | `S17_Outro` | 附录一览（简介）、总结与四个方向 |

图表数值均取自论文正文；图 4 只绘制正文给出的两个模型的端点数值。

## 目录

```
attention/  smhbench/
  narration.py   # 中文旁白稿（按场景分句，key 全片唯一）+ TTS 读音替换表
  scenes.py      # Manim 场景
shared/
  common.py      # VoiceScene：旁白同步、中文字体、配色与小部件（各期共用）
tts/
  synth.py       # 逐句合成入口：云端 TTS > 本机 Qwen3-TTS 服务 > 进程内 MLX > 离线 Kokoro
  qwen3_server.py# 本机 Qwen3-TTS-1.7B（MLX）HTTP 服务
  qwen3_tts.py   # Qwen3-TTS (mlx-audio) 推理封装 + 去静音/归一化
scripts/
  setup_mac.sh   # Apple Silicon：环境 + 下载 Qwen3-TTS 模型
  setup_linux.sh # Linux：环境 + 离线兜底 TTS 模型
build.py         # tts -> render -> assemble（拼接 + 字幕），产物在 build/<paper>/
```

## 快速开始

```bash
bash scripts/setup_mac.sh              # 或 Linux：bash scripts/setup_linux.sh
source .venv/bin/activate
python build.py all --paper smhbench -q h --burn-subs   # -> build/smhbench/smh_bench.mp4 (+ .srt)
python build.py all --paper attention -q h              # -> build/attention/attention_is_all_you_need.mp4
```

国内网络可加镜像：`HF_ENDPOINT=https://hf-mirror.com bash scripts/setup_mac.sh`。
`attention` 一期用到了 `Tex/MathTex`，需要 LaTeX；`smhbench` 只用 `Text`，无需 LaTeX。

### 分步运行

```bash
python build.py tts --paper smhbench                          # 只合成旁白 -> build/smhbench/audio/
python build.py render --paper smhbench -q m -j 4             # 720p30 渲染所有场景
python build.py render --paper smhbench -q h --scenes S03_HomeEnv
python build.py assemble --paper smhbench --burn-subs         # 拼接，并把字幕烧进画面
```

单独调试某个场景：`manim -pql smhbench/scenes.py S05_Settings`。

## 语音合成

`tts/synth.py --backend auto`（默认）按以下顺序选第一个可用的后端：

| 后端 | 条件 | 说明 |
|---|---|---|
| `minimax` | `MINIMAX_API_KEY` | MiniMax T2A v2，默认 `speech-2.8-turbo` + `male-qn-qingse`（`MINIMAX_MODEL`/`MINIMAX_HOST`/`--voice`/`--speed` 可改） |
| `polly` | 有效的 AWS 凭证 | AWS Polly 神经网络中文音色 `Zhiyu` |
| `google` | `GOOGLE_API_KEY` 或 gcloud 登录 | Google Cloud TTS，默认 `cmn-CN-Chirp3-HD-Charon` |
| `qwen-http` | 本机已启动 `tts/qwen3_server.py` | Qwen3-TTS-1.7B-MLX 服务（地址可用 `QWEN_TTS_URL` 覆盖） |
| `qwen-mlx` | Apple Silicon + mlx-audio | 进程内加载 Qwen3-TTS-1.7B |
| `kokoro` | `models/kokoro-multi-lang-v1_1` | sherpa-onnx 离线推理，任意平台可用，默认中文男声 `sid=67` |

```bash
# 在 Mac 上启动本机 Qwen3-TTS 服务（模型只加载一次），再合成
python tts/qwen3_server.py &                                  # 127.0.0.1:8765
python build.py tts --paper smhbench --backend qwen-http --voice Uncle_Fu \
    --instruct "用平和、清晰、富有好奇心的语气讲解"

# 用文字描述“设计”音色（需先下载 1.7B-VoiceDesign 模型）
python tts/qwen3_server.py --mode design --model models/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 &
python build.py tts --paper smhbench --backend qwen-http --force \
    --instruct "三十多岁的男性科普讲解员，普通话标准，嗓音温暖低沉"

# 云端：AWS Polly / Google
python build.py tts --paper smhbench --backend polly --force
GOOGLE_API_KEY=... python build.py tts --paper smhbench --backend google --force

# 只重新合成某几句
python tts/synth.py --paper smhbench --only res_3 err_2 --force
```

最终配音（MiniMax speech-2.8-turbo · male-qn-qingse · 语速 1.0）：

```bash
export MINIMAX_API_KEY=...        # 不要写进仓库
python build.py all --paper smhbench -q h --burn-subs --backend minimax --force
```

- **缓存**：manifest 里记录每句文本哈希与所用后端；文本未变化的句子不会重复合成。显式指定 `--backend` 时，其他后端生成的句子会被重新合成。
- **读音**：`narration.py` 里的 `TTS_REPLACEMENTS` 把屏幕写法换成更好读的写法（如 `SMH-Bench → S M H Bench`）。
- 默认去掉首尾静音并做 -1 dBFS 峰值归一化。

## 动画与语音如何对齐

场景继承 `VoiceScene`，每句旁白用一个 `with` 块包住它对应的动画：

```python
with self.voice("qkv_4"):          # 在当前时刻插入 build/<paper>/audio/qkv_4.wav
    self.play(Create(grid))
    self.play(Write(dot))
# 离开 with 时自动 wait 到这句话读完（+0.35s 停顿）
```

- 时长从 `build/<paper>/audio/manifest.json` 读取；没有音频时按字数估算（约 4.3 字/秒），所以**没有 Mac 也能先渲染出节奏正确的静音预览**：`python build.py all --paper smhbench -q l --placeholder`。
- 如果某段动画比语音还长，渲染日志里会出现 `[voice] ... 动画比旁白长` 的提示。
- 每句的起止时间写入 `build/<paper>/cues/<Scene>.json`，`assemble` 据此生成按标点切分的 SRT 字幕（默认作为软字幕封装进 mp4）。

## 其他平台

Manim 渲染在 Linux / Windows 上同样可用（需要 ffmpeg、pango；`attention` 一期还需要 LaTeX）。MLX 只能跑在 Apple Silicon 上：可以在 Mac 上跑 `python build.py tts --paper <paper>` 生成 `build/<paper>/audio/`，再拷到别的机器上 `render` + `assemble`；或者直接用云端 / Kokoro 后端。

中文字体按 `PingFang SC → Hiragino Sans GB → Source Han Sans SC → Noto Sans CJK SC → Microsoft YaHei → WenQuanYi Zen Hei` 顺序自动选择，也可用环境变量 `CJK_FONT` 指定。

## 参考

- Kuan Li et al., *SMH-Bench*, 2026. [arXiv:2606.01912](https://arxiv.org/abs/2606.01912)
- Vaswani et al., *Attention Is All You Need*, NeurIPS 2017. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- 3Blue1Brown, *Attention in transformers, visually explained*（本片的视觉风格参考）
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) · [mlx-audio](https://github.com/Blaizzy/mlx-audio) · [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)
