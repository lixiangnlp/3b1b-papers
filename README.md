# 3b1b-papers · 3Blue1Brown 风格中文论文讲解

用 [Manim](https://www.manim.community/) 制作 3Blue1Brown 风格的中文论文讲解视频，
旁白逐句合成，动画与语音自动对齐。目前包含两期：

| `--paper` | 论文 | 时长 |
|---|---|---|
| `attention` | Vaswani et al., *Attention Is All You Need*（NeurIPS 2017） | ~10 分钟 · 10 场景 |
| `smhbench` | Kuan Li et al., *SMH-Bench: Benchmarking LLM Agents for Environment-Grounded Reasoning and Action in Smart Homes*（[arXiv:2606.01912](https://arxiv.org/abs/2606.01912)） | ~7 分钟 · 8 场景 |

## SMH-Bench 分集

| # | 场景 | 内容 |
|---|------|------|
| 1 | `S01_Intro` | “我要看电影了”：为什么智能家居不是指令翻译 |
| 2 | `S02_Problem` | 静态指令→API 比对的盲点；状态决定正确答案 |
| 3 | `S03_HomeEnv` | 家 → 房间 → 设备 → 服务/状态；执行时报错；四类验证方式 |
| 4 | `S04_Benchmark` | 1100 个人工审核任务、7 大类 22 子类、语言鲁棒性、三档家庭复杂度（最多 135 台设备） |
| 5 | `S05_Settings` | 直接推理 DR vs. 环境交互智能体 EIA（ReAct、局部可观测） |
| 6 | `S06_Results` | 13 个 LLM：显式控制/查询强，自动化/歧义/个性化弱，随家庭复杂度下降（柱状/折线为**示意**） |
| 7 | `S07_Errors` | EIA：IE 指令执行错误（冗余调用、参数边界混淆）；DR：MS 信息缺失 / AV 动作校验 |
| 8 | `S08_Outro` | 四个方向：状态落地、澄清策略、偏好感知、规范工具调用 |

> 结果场景中的柱子与折线只表示论文报告的**定性趋势**，并非论文中的具体数值，画面上已标注“示意”。

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
