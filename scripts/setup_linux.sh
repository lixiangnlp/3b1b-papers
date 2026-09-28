#!/usr/bin/env bash
# Linux（Debian/Ubuntu）环境：Manim + ffmpeg + 中文字体 + 云端 TTS 客户端 + 离线兜底 TTS（sherpa-onnx Kokoro）
#
#   bash scripts/setup_linux.sh
#
# Qwen3-TTS-MLX 只能跑在 Apple Silicon 上；Linux 上优先使用云端 TTS（配置 AWS 凭证或 GOOGLE_API_KEY），
# 否则回退到本地 Kokoro 多语种模型（约 350MB，从 GitHub Releases 下载）。
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/3 系统依赖"
if command -v apt-get >/dev/null; then
  SUDO=$([[ $EUID -eq 0 ]] && echo "" || echo sudo)
  $SUDO apt-get install -y ffmpeg libpango1.0-dev libcairo2-dev pkg-config fonts-noto-cjk
fi

echo "==> 2/3 Python 虚拟环境"
[[ -d .venv ]] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt boto3 sherpa-onnx

echo "==> 3/3 离线兜底 TTS 模型 kokoro-multi-lang-v1_1"
mkdir -p models
if [[ ! -f models/kokoro-multi-lang-v1_1/model.onnx ]]; then
  curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2 \
    | tar xj -C models
fi
echo "完成。试试：source .venv/bin/activate && python build.py all --paper smhbench -q m"
