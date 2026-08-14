#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cosyvoice_tts · CosyVoice2 语音合成服务（GPU·4090 加速）
==========================================================
用 ComfyUI 环境的 CUDA torch 跑 CosyVoice2（系统 Python 是 CPU torch）。
通过 subprocess 调用，避免与灵枢主进程的 torch 冲突。

用法：python cosyvoice_tts.py <text> <参考音频路径> <输出wav路径> [提示文本]
"""

import os
import subprocess
import sys
import tempfile

# ComfyUI 环境的 python（有 CUDA torch）
COMFY_PYTHON = r"D:\Program Files\ai_ds\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe"
# CosyVoice 代码与模型
COSY_CODE = r"D:\Program Files\2_ai\AEIS\models\cosyvoice\cosyvoice_code"
COSY_MODEL = r"D:\Program Files\2_ai\AEIS\models\cosyvoice\cosyvoice2"

# 默认参考音频（System.Speech 生成的长音频，可被猫娘音色样本替换）
DEFAULT_REF = r"D:\Program Files\2_ai\AEIS\models\cosyvoice\out\ref_long.wav"
DEFAULT_REF_TEXT = ("今天天气真好我们去公园散步吧那里有很多花还有小鸟在唱歌"
                    "我们可以一起坐在长椅上看看天上的白云")


def synthesize(text: str, ref_wav: str = DEFAULT_REF, ref_text: str = DEFAULT_REF_TEXT,
               out_wav: str = None, timeout: int = 120) -> str:
    """合成文本 → wav 文件（GPU）。返回输出路径。"""
    if out_wav is None:
        out_wav = os.path.join(tempfile.gettempdir(), "lingxu_say.wav")
    script = f'''
import sys, os, time, torch
sys.path.insert(0, {COSY_CODE!r})
from cosyvoice.cli.cosyvoice import CosyVoice2
cosyvoice = CosyVoice2({COSY_MODEL!r}, load_jit=False, load_trt=False, fp16=True)
segments = []
for i, j in enumerate(cosyvoice.inference_zero_shot(
        {text!r}, {ref_text!r}, {ref_wav!r}, stream=False, text_frontend=True)):
    segments.append(j['tts_speech'])
import torchaudio
audio = torch.cat(segments, dim=1)
torchaudio.save({out_wav!r}, audio, cosyvoice.sample_rate)
print('OK')
'''
    proc = subprocess.run([COMFY_PYTHON, "-c", script],
                          capture_output=True, timeout=timeout,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if proc.returncode != 0 or b"OK" not in proc.stdout:
        err = proc.stderr.decode("utf-8", "replace")[-500:]
        raise RuntimeError(f"CosyVoice 合成失败: {err}")
    return out_wav


def main():
    if len(sys.argv) < 2:
        print("用法: python cosyvoice_tts.py <文本> [输出wav]")
        return 1
    text = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    path = synthesize(text, out_wav=out)
    print(f"已合成: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
