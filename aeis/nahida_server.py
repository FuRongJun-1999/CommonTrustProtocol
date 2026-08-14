#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""纳西妲音色常驻推理服务（GPT-SoVITS v2 · 热加载）。
协议：JSON-lines over stdio——
  请求: {"id": "..", "text": ".."}          → 合成 wav
  响应: {"id": "..", "ok": true, "wav": ".."}
       {"id": "..", "ok": false, "error": ".."}
启动后打印 READY（模型加载完成）再开始服务。
用途：灵枢 say 引擎 engine='nahida' 的后端——一次加载，每次说话只付推理成本。
节能：空闲超时（NAHIDA_IDLE_TIMEOUT 秒，默认 1800=30 分钟）无请求自动退出，
释放 GPU 显存（Windows 任务管理器电源标记高）；下次调用由 say 引擎自动拉起。
"""
import json
import os
import sys
import time, contextlib

BASE = r"D:\Program Files\ai_voice\GPT-SoVITS-v3lora-20250228"
os.chdir(BASE)  # yaml 内权重为相对路径，须以项目根为 cwd
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "GPT_SoVITS"))
OUT_DIR = os.path.join(BASE, "output")
IDLE_TIMEOUT = int(os.environ.get("NAHIDA_IDLE_TIMEOUT", "1800"))  # 30 分钟


def _infer(tts, text):
    """合成（静音库日志：TTS print 走 stderr，stdout 保持纯协议流）。"""
    with contextlib.redirect_stdout(sys.stderr):
        result = tts.run({
            "text": text,
            "text_lang": "zh",
            "ref_audio_path": os.path.join(
                BASE, "GPT_SoVITS", "pretrained_models", "纳西妲",
                "（如果是说踏鞴砂那个神秘事件与倾奇者之类的…我知道哦。）.wav"),
            "prompt_text": "如果是说踏鞴砂那个神秘事件与倾奇者之类的…我知道哦。",
            "prompt_lang": "zh",
            "top_k": 5, "top_p": 1, "temperature": 1,
            "text_split_method": "cut5",
            "speed_factor": 1.0,
            "seed": -1,
            "parallel_infer": True,
            "repetition_penalty": 1.35,
        })
        sr, audio = None, None
        if hasattr(result, "__iter__") and not isinstance(result, tuple):
            for frag in result:
                if isinstance(frag, tuple):
                    sr, audio = frag
        else:
            sr, audio = result
    if audio is None:
        raise RuntimeError("无合成输出")
    return sr, audio

def main():
    with contextlib.redirect_stdout(sys.stderr):
        from TTS_infer_pack.TTS import TTS
        tts = TTS(os.path.join(BASE, "GPT_SoVITS", "configs", "tts_infer.yaml"))
    print("READY", flush=True)
    last_request = time.time()
    while True:
        # 空闲超时节能：无请求自动退出（释放 GPU 显存）
        if IDLE_TIMEOUT > 0 and time.time() - last_request > IDLE_TIMEOUT:
            print(json.dumps({"ok": True, "event": "IDLE_EXIT",
                              "reason": f"空闲 {IDLE_TIMEOUT}s 自动退出（节能）"}),
                  flush=True)
            return 0
        # 非阻塞检查 stdin（select 不可靠时用短轮询 + 超时）
        import select
        if not sys.stdin.isatty():
            try:
                ready, _, _ = select.select([sys.stdin], [], [], 1.0)
            except Exception:
                ready = []
            if not ready:
                continue
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        last_request = time.time()
        try:
            req = json.loads(line)
            text = str(req.get("text", "")).strip()
            rid = str(req.get("id", ""))
            if not text:
                print(json.dumps({"id": rid, "ok": False, "error": "empty text"}), flush=True)
                continue
            os.makedirs(OUT_DIR, exist_ok=True)
            out_wav = os.path.join(OUT_DIR, f"nahida_{rid}.wav")
            t0 = time.time()
            sr, audio = _infer(tts, text)
            import soundfile as sf
            sf.write(out_wav, audio, sr)
            print(json.dumps({"id": rid, "ok": True, "wav": out_wav,
                              "secs": round(time.time() - t0, 2)}), flush=True)
        except Exception as exc:
            try:
                print(json.dumps({"id": rid, "ok": False, "error": str(exc)[:200]}), flush=True)
            except Exception:
                pass

if __name__ == "__main__":
    main()
