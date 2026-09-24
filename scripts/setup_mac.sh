#!/usr/bin/env bash
# 在 Apple Silicon Mac 上一键准备环境：Manim + LaTeX + ffmpeg + mlx-audio + Qwen3-TTS-1.7B 模型
#
#   bash scripts/setup_mac.sh                 # 默认 1.7B-CustomVoice（预置音色 + 情感指令）
#   MODEL=Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 bash scripts/setup_mac.sh
#   HF_ENDPOINT=https://hf-mirror.com bash scripts/setup_mac.sh   # 国内镜像
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${MODEL:-Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16}"
PY="${PYTHON:-python3}"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "⚠️  MLX 只支持 Apple Silicon (arm64) 的 macOS。其他平台可以用 --placeholder 预览画面。"
  exit 1
fi

echo "==> 1/4 系统依赖（Homebrew）"
command -v brew >/dev/null || { echo "请先安装 Homebrew: https://brew.sh"; exit 1; }
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list pango >/dev/null 2>&1 || brew install pango pkg-config cairo
if ! command -v latex >/dev/null; then
  echo "    安装 BasicTeX（MathTex 需要 LaTeX，约 100MB）"
  brew install --cask basictex
  eval "$(/usr/libexec/path_helper)"
  sudo tlmgr update --self
  sudo tlmgr install standalone preview doublestroke relsize fundus-calligra wasysym physics \
    dvisvgm.universal-darwin dvisvgm rsfs wasy cm-super everysel ragged2e setspace babel-english
fi

echo "==> 2/4 Python 虚拟环境"
[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt -r requirements-tts.txt

echo "==> 3/4 下载模型 mlx-community/$MODEL -> models/$MODEL"
mkdir -p models
hf download "mlx-community/$MODEL" --local-dir "models/$MODEL"

echo "==> 4/4 冒烟测试：合成一句话"
python - <<PY
import time, numpy as np, wave
from mlx_audio.tts.utils import load_model
m = load_model("models/$MODEL")
t = time.time()
text = "你好，这里是 Transformer 论文讲解的本地语音合成测试。"
if "VoiceDesign" in "$MODEL":
    gen = m.generate_voice_design(text=text, language="chinese",
                                  instruct="温暖低沉的男性科普讲解员，普通话标准")
else:
    gen = m.generate_custom_voice(text=text, speaker="Uncle_Fu", language="chinese",
                                  instruct="平和清晰地讲解")
a = np.concatenate([np.array(r.audio) for r in gen])
pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
with wave.open("models/smoke_test.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(m.sample_rate); w.writeframes(pcm.tobytes())
print(f"OK: {len(a)/m.sample_rate:.1f}s 音频，用时 {time.time()-t:.1f}s -> models/smoke_test.wav")
PY
echo "✅ 环境就绪。下一步：source .venv/bin/activate && python build.py all -q h"
