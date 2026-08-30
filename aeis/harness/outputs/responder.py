# -*- coding: utf-8 -*-
"""harness.outputs.responder · 输出（自定义音色 + 文字）
================================================
复用身体层 AudioDevice.say（nahida 引擎：GPT-SoVITS 常驻服务热加载）。
"""
import sys
import os

_AEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AEIS_ROOT not in sys.path:
    sys.path.insert(0, _AEIS_ROOT)


class Responder:
    """输出器：文字日志 + 可选语音（自定义）。"""

    def __init__(self, workspace: str = "", voice_enabled: bool = True, log=None):
        self.workspace = workspace
        self.voice_enabled = voice_enabled
        self.log = log or (lambda *a: None)
        self._audio = None

    def _get_audio(self):
        if self._audio is None and self.voice_enabled:
            try:
                from aeis.body import build_default_registry
                from aeis.body.devices.audio import AudioDevice
                self._audio = AudioDevice(self.workspace)
            except Exception as exc:
                self.log(f"语音输出不可用: {exc}")
                self._audio = None
        return self._audio

    def say_text(self, text: str):
        """文字输出。"""
        self.log(f"[灵枢] {text}")

    def say_voice(self, text: str):
        """自定义语音输出（失败静默降级为文字）。"""
        audio = self._get_audio()
        if audio is None:
            return False
        try:
            r = audio.invoke("say", {"text": text, "engine": "nahida"})
            return r.ok
        except Exception:
            return False

    def respond(self, text: str, voice: bool = True):
        """统一回复：文字 + 语音。"""
        self.say_text(text)
        if voice:
            self.say_voice(text)
