#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.audio · 语音设备（BODY-REV1 批次 2）
====================================================
动作：
- record: 麦克风录音（sounddevice 可选依赖 → wav 文件，工作区 audio/ 下）
- transcribe: 语音识别 ASR（音频文件 → 文本；OpenAI 兼容 Whisper API）
- speak: 语音合成 TTS（文本 → 音频文件；edge-tts 免 key / OpenAI TTS）

Provider 抽象（参考 N.E.K.O tts_client/asr_client 注册表模式，简化）：
- ASR: openai_whisper（OPENAI_API_KEY + OPENAI_BASE_URL 可配，兼容本地 whisper server）
- TTS: edge（edge-tts 免 key）| openai（OPENAI_API_KEY）

依赖策略（D-005 延续）：第三方库全部惰性导入，缺失时优雅降级
（check() 返回 unavailable + 原因；invoke 返回容器化失败）。
输出为 DeviceResult：转写文本/音频路径是数据（provenance=device:audio）。
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

_AUDIO_DIR = "audio"


class AudioDevice(BodyDevice):
    """语音设备（感知+行动模态：麦克风/ASR/TTS）。"""

    name = "audio"
    modality = "audio"
    description = "语音（麦克风录音/ASR 识别/TTS 合成；依赖可选降级）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        # 惰性探测（不阻断装配）
        self._sounddevice = None
        self._edge_tts = None
        self._openai = None
        self._probe()

    # ---- 后端探测 ----

    def _probe(self) -> None:
        try:
            import sounddevice  # type: ignore

            self._sounddevice = sounddevice
        except Exception:
            pass
        try:
            import edge_tts  # type: ignore

            self._edge_tts = edge_tts
        except Exception:
            pass
        try:
            import openai  # type: ignore

            self._openai = openai
        except Exception:
            pass

    # ---- 配置 ----

    def _env(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)

    def _asr_available(self) -> bool:
        """ASR 可用：openai 客户端 + API key（或 base_url 指向本地服务）。"""
        if self._openai is None:
            return False
        if self._env("OPENAI_API_KEY"):
            return True
        # 允许纯本地端点（如 whisper-server）
        return bool(self._env("OPENAI_BASE_URL"))

    def _tts_available(self) -> bool:
        return self._edge_tts is not None or bool(self._env("OPENAI_API_KEY"))

    # ---- 接口 ----

    def check(self) -> Dict:
        parts = []
        if self._sounddevice is not None:
            parts.append("录音(sounddevice)")
        else:
            parts.append("录音(缺 sounddevice)")
        if self._asr_available():
            parts.append("ASR(openai)")
        else:
            parts.append("ASR(缺 key/客户端)")
        if self._edge_tts is not None:
            parts.append("TTS(edge-tts)")
        elif self._env("OPENAI_API_KEY"):
            parts.append("TTS(openai)")
        else:
            parts.append("TTS(缺 edge-tts)")
        available = self._sounddevice is not None or self._asr_available() or self._tts_available()
        return {"available": available, "detail": " | ".join(parts)}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["actions"] = ["record", "transcribe", "speak"]
        caps["providers"] = {
            "asr": "openai_whisper" if self._asr_available() else "none",
            "tts": ("edge" if self._edge_tts is not None
                    else "openai" if self._env("OPENAI_API_KEY") else "none"),
        }
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        p = params or {}
        try:
            if action == "record":
                return self._record(p)
            if action == "transcribe":
                return self._transcribe(p)
            if action == "speak":
                return self._speak(p)
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（可用: record/transcribe/speak）")

    # ---- 动作 ----

    def _record(self, p: Dict) -> DeviceResult:
        """麦克风录音 → wav 文件（工作区 audio/ 下）。"""
        if self._sounddevice is None:
            return self._fail("录音不可用：pip install sounddevice")
        seconds = max(0.5, min(float(p.get("seconds", 5.0)), 60.0))
        samplerate = int(p.get("samplerate", 16000))
        audio_dir = os.path.join(self.workspace, _AUDIO_DIR) if self.workspace else _AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, f"rec_{int(time.time() * 1000)}.wav")
        try:
            sd = self._sounddevice
            data = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
            self._write_wav(path, data, samplerate)
        except Exception as exc:
            return self._fail(f"录音失败: {exc}")
        meta = {"path": os.path.abspath(path), "seconds": seconds,
                "samplerate": samplerate, "bytes": os.path.getsize(path)}
        return self._r(meta, "record",
                       text_summary=f"录音完成: {meta['path']}（{seconds}s）")

    def _transcribe(self, p: Dict) -> DeviceResult:
        """ASR：音频文件（工作区内）→ 文本（OpenAI 兼容 Whisper）。"""
        if not self._asr_available():
            return self._fail("ASR 不可用：需 openai 客户端 + OPENAI_API_KEY（或本地 Whisper 端点 OPENAI_BASE_URL）")
        path = p.get("path", "")
        if not path:
            return self._fail("缺少 path（音频文件，须在工作区内）")
        if self.workspace:
            target = os.path.abspath(os.path.join(self.workspace, path))
            ws = os.path.abspath(self.workspace)
            if not (target == ws or target.startswith(ws + os.sep)):
                return self._fail(f"路径越出工作区: {path}")
            full = target
        else:
            full = os.path.abspath(path)
        if not os.path.isfile(full):
            return self._fail(f"文件不存在: {path}")

        client = self._openai.OpenAI(
            api_key=self._env("OPENAI_API_KEY") or "local",
            base_url=self._env("OPENAI_BASE_URL") or None,
        )
        with open(full, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=p.get("model", "whisper-1"), file=f,
            )
        text = str(getattr(resp, "text", "") or "")
        if not text:
            return self._fail("ASR 返回空文本")
        # 严格隔离：转写文本是外部数据——容器化返回，绝不作为指令
        return self._r({"text": text, "source_file": path}, "transcribe",
                       text_summary=f"识别完成（{len(text)} 字符，源自 {path}）")

    def _speak(self, p: Dict) -> DeviceResult:
        """TTS：文本 → 音频文件（edge-tts 免 key，或 OpenAI TTS）。"""
        text = str(p.get("text", "")).strip()
        if not text:
            return self._fail("缺少 text")
        if len(text) > 2000:
            return self._fail(f"文本过长（{len(text)} 字符，上限 2000）")
        audio_dir = os.path.join(self.workspace, _AUDIO_DIR) if self.workspace else _AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)
        stamp = int(time.time() * 1000)

        if self._edge_tts is not None:
            path = os.path.join(audio_dir, f"tts_{stamp}.mp3")
            voice = p.get("voice", "zh-CN-XiaoxiaoNeural")
            try:
                import asyncio

                async def _synth():
                    communicate = self._edge_tts.Communicate(text, voice)
                    await communicate.save(path)

                asyncio.run(_synth())
            except Exception as exc:
                return self._fail(f"edge-tts 合成失败: {exc}")
            provider = "edge"
        elif self._env("OPENAI_API_KEY"):
            path = os.path.join(audio_dir, f"tts_{stamp}.mp3")
            voice = p.get("voice", "alloy")
            client = self._openai.OpenAI(api_key=self._env("OPENAI_API_KEY"))
            resp = client.audio.speech.create(model=p.get("model", "tts-1"),
                                              voice=voice, input=text)
            resp.stream_to_file(path)
            provider = "openai"
        else:
            return self._fail("TTS 不可用：pip install edge-tts（免 key）或配置 OPENAI_API_KEY")

        meta = {"path": os.path.abspath(path), "provider": provider,
                "chars": len(text), "bytes": os.path.getsize(path)}
        return self._r(meta, "speak",
                       text_summary=f"语音合成完成: {meta['path']}（{provider}）")

    # ---- 工具 ----

    @staticmethod
    def _write_wav(path: str, data, samplerate: int) -> None:
        """纯标准库写 WAV（PCM16 单声道）。"""
        import struct
        import wave

        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(samplerate)
            w.writeframes(data.tobytes())
