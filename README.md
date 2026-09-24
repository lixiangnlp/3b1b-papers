# 3b1b-papers · Attention Is All You Need

用 3Blue1Brown 风格（[Manim](https://www.manim.community/)）制作的中文论文讲解视频，
旁白由**本机部署**的 **Qwen3-TTS-1.7B（MLX）** 逐句合成，动画与语音自动对齐。

全片约 10 分钟，共 10 个场景、43 句旁白：

| # | 场景 | 内容 |
|---|------|------|
| 1 | `S01_Intro` | 论文、作者，Transformer 的影响，本期提纲 |
| 2 | `S02_RNN` | RNN 的串行瓶颈与长距离依赖，自注意力的想法 |
| 3 | `S03_Embedding` | 词嵌入：向量空间中的方向带有语义；上下文问题 |
| 4 | `S04_QKV` | 用“一只毛茸茸的蓝色小猫”讲 Query / Key / Value、点积、softmax、加权求和 |
| 5 | `S05_Formula` | 缩放点积注意力公式；为什么要除以 √dₖ（方差分析 + softmax 饱和动画） |
| 6 | `S06_MultiHead` | 多头注意力：8 个头的不同模式、拼接与 Wᴼ |
| 7 | `S07_Position` | 位置编码：正弦波、编码热力图、相对位置 = 旋转 |
| 8 | `S08_Architecture` | 编码器-解码器、FFN、残差 + LayerNorm、交叉注意力、因果掩码 |
| 9 | `S09_WhySelfAttention` | 复杂度 / 串行操作 / 路径长度对比，n² 的代价 |
| 10 | `S10_Results` | WMT14 BLEU、训练成本、BERT/GPT 谱系、结尾 |

## 目录

```
attention/
  narration.py   # 中文旁白稿（按场景分句，key 全片唯一）+ TTS 读音替换表
  common.py      # VoiceScene：旁白同步、中文字体、配色与小部件
  scenes.py      # 10 个 Manim 场景
tts/
  qwen3_tts.py   # Qwen3-TTS (mlx-audio) 逐句合成 + 缓存 + 去静音/归一化
scripts/
  setup_mac.sh   # Apple Silicon 一键装环境、下载模型、冒烟测试
build.py         # tts -> render -> assemble（拼接 + 字幕）
```

## 快速开始（Apple Silicon Mac）

```bash
bash scripts/setup_mac.sh            # 装 ffmpeg/pango/LaTeX、venv、mlx-audio，下载模型到 models/
source .venv/bin/activate
python build.py all -q h             # 1080p60，产物：build/attention_is_all_you_need.mp4 (+ .srt)
```

国内网络可加镜像：`HF_ENDPOINT=https://hf-mirror.com bash scripts/setup_mac.sh`。

模型默认是 `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16`（约 4 GB 内存），
下载到 `models/` 后脚本自动使用本地目录，之后可离线运行。

### 分步运行

```bash
python build.py tts                          # 只合成旁白 -> build/audio/*.wav + manifest.json
python build.py render -q m -j 4             # 720p30 渲染所有场景（4 个并行）
python build.py render -q h --scenes S04_QKV # 只重渲一个场景
python build.py assemble --burn-subs         # 拼接，并把字幕烧进画面
```

单独调试某个场景：`manim -pql attention/scenes.py S05_Formula`。

## 语音合成（Qwen3-TTS · MLX）

`tts/qwen3_tts.py` 基于 [mlx-audio](https://github.com/Blaizzy/mlx-audio) 在本机推理：

```bash
# 换音色 / 语气（CustomVoice 预置音色：Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden）
python tts/qwen3_tts.py --speaker Serena --instruct "语气轻快、充满好奇，语速适中"

# 用文字描述“设计”一个音色（需先下载 1.7B-VoiceDesign 模型）
MODEL=Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 bash scripts/setup_mac.sh
python tts/qwen3_tts.py --mode design --model models/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
    --instruct "三十多岁的男性科普讲解员，普通话标准，嗓音温暖低沉"

# 只重新合成某几句（比如对读音不满意）
python tts/qwen3_tts.py --only qkv_2 formula_3 --force
```

- **缓存**：每句的文本 + 音色 + 参数做哈希，未变化的句子不会重复合成；改稿后直接重跑即可。
- **读音**：`narration.py` 里的 `TTS_REPLACEMENTS` 把屏幕写法换成更好读的写法（如 `P100 → P一百`），读错的词在这里加规则。
- **稳定性**：默认 `--seed 42 --temperature 0.7`，同一句多次合成结果一致；想换一种读法就换个 seed。
- 默认去掉首尾静音并做 -1 dBFS 峰值归一化。

## 动画与语音如何对齐

场景继承 `VoiceScene`，每句旁白用一个 `with` 块包住它对应的动画：

```python
with self.voice("qkv_4"):          # 在当前时刻插入 build/audio/qkv_4.wav
    self.play(Create(grid))
    self.play(Write(dot))
# 离开 with 时自动 wait 到这句话读完（+0.35s 停顿）
```

- 时长从 `build/audio/manifest.json` 读取；没有音频时按字数估算（约 4.3 字/秒），所以**没有 Mac 也能先渲染出节奏正确的静音预览**：`python build.py all -q l --placeholder`。
- 如果某段动画比语音还长，渲染日志里会出现 `[voice] ... 动画比旁白长` 的提示。
- 每句的起止时间写入 `build/cues/<Scene>.json`，`assemble` 据此生成按标点切分的 SRT 字幕（默认作为软字幕封装进 mp4）。

## 其他平台

Manim 渲染在 Linux / Windows 上同样可用（需要 ffmpeg、pango、LaTeX），但 MLX 只能跑在 Apple Silicon 上。
可以在 Mac 上跑 `python build.py tts` 生成 `build/audio/`，再拷到别的机器上 `render` + `assemble`。

中文字体按 `PingFang SC → Hiragino Sans GB → Source Han Sans SC → Noto Sans CJK SC → Microsoft YaHei → WenQuanYi Zen Hei` 顺序自动选择，也可用环境变量 `CJK_FONT` 指定。

## 参考

- Vaswani et al., *Attention Is All You Need*, NeurIPS 2017. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- 3Blue1Brown, *Attention in transformers, visually explained*（本片的视觉风格参考）
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) · [mlx-audio](https://github.com/Blaizzy/mlx-audio)
