"""本机 Qwen3-TTS-1.7B（MLX）HTTP 服务：模型只加载一次，供 synth.py 的 qwen-http 后端调用。

  python tts/qwen3_server.py                 # 默认 127.0.0.1:8765，CustomVoice 模型
  python tts/qwen3_server.py --port 9000 --model models/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 --mode design

接口:
  GET  /health                         -> {"ok": true, "model": ...}
  POST /tts {"text", "speaker"?, "instruct"?}  -> audio/wav
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import threading
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qwen3_tts import DEFAULT_DESIGN, DEFAULT_INSTRUCT, DEFAULT_MODEL, DEFAULT_SPEAKER, LOCAL_MODEL, QwenTTS  # noqa: E402


def wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
    return buf.getvalue()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--model", default=str(LOCAL_MODEL) if LOCAL_MODEL.exists() else DEFAULT_MODEL)
    ap.add_argument("--mode", choices=["custom", "design", "base"], default="custom")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    tts = QwenTTS(args.model, args.mode, DEFAULT_SPEAKER, DEFAULT_INSTRUCT, args.temperature, args.seed)
    lock = threading.Lock()  # MLX 推理串行执行

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._send(200, json.dumps({"ok": True, "model": Path(args.model).name}).encode(),
                           "application/json")
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self):
            if self.path != "/tts":
                return self._send(404, b"not found", "text/plain")
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            with lock:
                tts.speaker = req.get("speaker") or DEFAULT_SPEAKER
                tts.instruct = req.get("instruct") or (
                    DEFAULT_DESIGN if args.mode == "design" else DEFAULT_INSTRUCT)
                audio = tts.synth(req["text"])
            self._send(200, wav_bytes(audio, tts.sr), "audio/wav")

    print(f"[qwen3-server] http://{args.host}:{args.port}  模型 {args.model}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
