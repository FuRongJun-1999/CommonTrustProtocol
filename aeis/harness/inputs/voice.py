# -*- coding: utf-8 -*-
"""harness.inputs.voice · 语音输入（VAD 断句，复用身体层 AudioDevice）
================================================
一句话结束（停顿 = is_endpoint）→ 回调提交。控制词由主循环处理。
"""
import sys
import os
import threading

_AEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AEIS_ROOT not in sys.path:
    sys.path.insert(0, _AEIS_ROOT)

PAUSE_WORDS = ["暂停", "休息一下", "别说话", "静音"]
RESUME_WORDS = ["继续", "好了", "恢复"]
EXIT_WORDS = ["退出", "结束", "stop", "exit", "关闭"]


class VoiceInput(threading.Thread):
    """语音输入线程：持续 VAD 断句，每句回调 on_sentence(text)。"""

    def __init__(self, on_sentence, workspace: str = "", max_seconds: int = 10,
                 log=None):
        super().__init__(daemon=True)
        self.on_sentence = on_sentence
        self.workspace = workspace
        self.max_seconds = max_seconds
        self.log = log or (lambda *a: None)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        try:
            from aeis.body import build_default_registry
            from aeis.body.devices.audio import AudioDevice
            audio = AudioDevice(self.workspace)
            self.log("语音输入就绪（VAD 断句）")
            while not self._stop.is_set():
                r = audio.invoke("listen_stream",
                                 {"max_seconds": self.max_seconds,
                                  "max_sentences": 1, "source": "mic"})
                data = r.data or {}
                sentences = data.get("sentences", []) or []
                if not sentences:
                    continue
                text = str(sentences[0]).strip()
                if text:
                    self.on_sentence(text)
        except Exception as exc:
            self.log(f"语音输入异常: {exc}")
