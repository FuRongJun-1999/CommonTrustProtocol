#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""纳西妲音色常驻推理服务（GPT-SoVITS v2 · 热加载）。
协议：JSON-lines over stdio——
  请求: {"id": "..", "text": ".."}          → 合成 wav
  响应: {"id": "..", "ok": true, "wav": ".."}
       {"id": "..", "ok": false, "error": ".."}
启动后打印 READY（模型加载完成）再开始服务。
用途：灵枢 say 引擎 engine='nahida' 的后端——一次加载，每次说话只付推理成本。
"""
import sys, os, json, time, contextlib

BASE = r"D:\Program Files\ai_voice\GPT-SoVITS-v3lora-20250228"
os.chdir(BASE)  # yaml 内权重为相对路径，须以项目根为 cwd
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "GPT_SoVITS"))
OUT_DIR = os.path.join(BASE, "output")


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
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
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
