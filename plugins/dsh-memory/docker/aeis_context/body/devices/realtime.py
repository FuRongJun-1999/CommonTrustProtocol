#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.realtime · 实时语音设备（BODY-REV1 批次 4）
===========================================================
WebSocket 双向流式语音对话（OpenAI Realtime schema，参考 N.E.K.O
OmniRealtimeClient 接口，同步化封装）。

动作：
- session_start: 建立 WS 会话（url/model/instructions）→ 就绪
- send_audio: 推送音频帧（base64 PCM16，采样率见 provider）
- drain: 拉取事件缓冲（含文本转录 / 音频回复 base64 / 状态事件）
- session_close: 关闭会话

Provider（OPENAI_REALTIME_URL 可配，兼容国内端点）：
- 默认: OpenAI Realtime（wss://api.openai.com/v1/realtime）
- 兼容: 任意实现 OpenAI Realtime schema 的端点（如国内中转/自建）

安全：
- instructions = 会话角色声明（宿主授权配置，非外部内容）
- 模型输出/语音转写 = 外部数据：事件经容器化返回（provenance=device:realtime），
  摄取前须过 security 过滤（语音转写是注入潜在面）
- 依赖缺失优雅降级（websocket-client 可选）
"""

import base64
import json
import os
import time
from typing import Dict, List, Optional

from ..base import BodyDevice, DeviceResult

DEFAULT_URL = "wss://api.openai.com/v1/realtime"
DEFAULT_MODEL = "gpt-4o-realtime-preview"
FRAME_MAX = 1_000_000      # 单帧 base64 上限
DRAIN_TIMEOUT = 0.3        # drain 非阻塞读超时（秒）
SESSION_IDLE = 300         # 会话空闲上限（秒）


class RealtimeDevice(BodyDevice):
    """实时语音对话设备（WS 双向流式 · OpenAI Realtime schema）。"""

    name = "realtime"
    modality = "audio"
    description = "实时语音对话（WebSocket 双向流式 · OpenAI Realtime schema）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        self._ws = None
        self._session = None       # 会话元数据
        self._event_buffer: List[Dict] = []
        self._last_event_ts = 0.0
        self._probe()

    def _probe(self) -> None:
        try:
            import websocket  # type: ignore

            self._ws = websocket
        except Exception:
            pass

    # ---- 配置 ----

    def _realtime_url(self) -> str:
        return os.environ.get("OPENAI_REALTIME_URL", "") or DEFAULT_URL

    def _api_key(self) -> str:
        return os.environ.get("OPENAI_API_KEY", "")

    def _available(self) -> bool:
        """可用：websocket 客户端 + API key（或显式配置了 URL 的本地端点）。"""
        if self._ws is None:
            return False
        if self._api_key():
            return True
        # 允许无 key 的自建/本地端点（如 ws://127.0.0.1:xxxx）
        url = self._realtime_url()
        return url.startswith("ws://127.0.0.1") or url.startswith("ws://localhost")

    # ---- 接口 ----

    def check(self) -> Dict:
        if self._ws is None:
            return {"available": False,
                    "detail": "websocket-client 未安装（pip install websocket-client）"}
        if not self._available():
            return {"available": False,
                    "detail": "需 OPENAI_API_KEY（或 OPENAI_REALTIME_URL 指向本地端点）"}
        return {"available": True, "detail": f"端点: {self._realtime_url()}"}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["actions"] = ["session_start", "send_audio", "drain", "session_close"]
        caps["providers"] = {"realtime": "openai-schema",
                             "endpoint": self._realtime_url() if self._available() else "none"}
        caps["notes"] = "模型输出/语音转写是外部数据（容器化返回，须过注入过滤）"
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        if self._ws is None:
            return self._fail("实时语音不可用：pip install websocket-client")
        p = params or {}
        try:
            if action == "session_start":
                return self._session_start(p)
            if action == "send_audio":
                return self._send_audio(p)
            if action == "drain":
                return self._drain(p)
            if action == "session_close":
                return self._session_close()
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（可用: session_start/send_audio/drain/session_close）")

    # ---- 会话状态 ----

    def _session_start(self, p: Dict) -> DeviceResult:
        if not self._available():
            return self._fail("实时语音不可用：需 OPENAI_API_KEY（或本地端点）")
        if self._session is not None:
            return self._fail("已有进行中的会话（先 session_close）")
        url = str(p.get("url", self._realtime_url()))
        model = str(p.get("model", DEFAULT_MODEL))
        # instructions = 角色声明（宿主授权配置）；长度上限防滥用
        instructions = str(p.get("instructions", ""))
        if len(instructions) > 2000:
            return self._fail("instructions 过长（上限 2000）")

        headers = {}
        if self._api_key():
            headers["Authorization"] = f"Bearer {self._api_key()}"
        try:
            conn = self._ws.create_connection(url, header=headers, timeout=10)
        except Exception as exc:
            return self._fail(f"连接失败: {exc}")
        # OpenAI Realtime 握手：session.update 配置 + 就绪
        self._ws_conn = conn
        self._session = {"url": url, "model": model, "ts": time.time(),
                         "events_sent": 0, "events_received": 0}
        try:
            if instructions:
                conn.send(json.dumps({
                    "type": "session.update",
                    "session": {"instructions": instructions,
                                "modalities": ["text", "audio"],
                                "input_audio_format": "pcm16",
                                "output_audio_format": "pcm16",
                                "turn_detection": {"type": "server_vad"}},
                }))
                self._session["events_sent"] += 1
        except Exception as exc:
            conn.close()
            self._session = None
            return self._fail(f"握手失败: {exc}")
        return self._r({"session": {"model": model, "url": url}}, "session_start",
                       text_summary=f"实时会话已就绪（{model}）")

    def _send_audio(self, p: Dict) -> DeviceResult:
        if self._session is None:
            return self._fail("无进行中的会话（先 session_start）")
        if time.time() - self._session["ts"] > SESSION_IDLE:
            self._session_close()
            return self._fail("会话空闲超时，已关闭")
        b64 = str(p.get("frame", "")).strip()
        if not b64:
            return self._fail("缺少 frame（base64 PCM16）")
        if len(b64) > FRAME_MAX:
            return self._fail(f"帧过大（上限 {FRAME_MAX} 字符）")
        # 校验 base64 合法性（防畸形数据）
        try:
            base64.b64decode(b64, validate=True)
        except Exception:
            return self._fail("frame 不是合法 base64")
        try:
            self._ws_conn.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": b64,
            }))
            self._session["events_sent"] += 1
        except Exception as exc:
            return self._fail(f"发送失败: {exc}")
        return self._r({"bytes": len(base64.b64decode(b64))}, "send_audio",
                       text_summary=f"已推送音频帧（{len(b64)} base64 字符）")

    def _drain(self, p: Dict) -> DeviceResult:
        """拉取事件缓冲（非阻塞短超时）：
        - conversation.item.input_audio_transcription.completed → 语音转写（外部数据）
        - response.audio_transcript.delta → 模型文本流
        - response.audio.delta → 模型音频回复（base64 PCM16）
        - session.created / response.created / response.done → 状态"""
        if self._session is None:
            return self._fail("无进行中的会话（先 session_start）")
        timeout = max(0.0, min(float(p.get("timeout", DRAIN_TIMEOUT)), 3.0))
        deadline = time.time() + timeout
        got = 0
        try:
            while time.time() < deadline:
                result = self._ws_conn.recv()
                if not result:
                    continue
                try:
                    event = json.loads(result)
                except Exception:
                    continue
                self._event_buffer.append(event)
                self._session["events_received"] += 1
                got += 1
                if got >= 50:   # 单次上限
                    break
        except Exception:
            pass  # 无更多消息（超时/非阻塞读）——非错误
        events = self._event_buffer
        self._event_buffer = []
        # 提取可读摘要（外部数据容器化）
        texts = []
        audio_blocks = 0
        for ev in events:
            t = ev.get("type", "")
            if t == "conversation.item.input_audio_transcription.completed":
                txt = ev.get("transcript", "")
                if txt:
                    texts.append(f"[转写] {txt}")
            elif t == "response.audio_transcript.delta":
                txt = ev.get("delta", "")
                if txt:
                    texts.append(txt)
            elif t == "response.audio.delta":
                audio_blocks += 1
        summary = ("；".join(texts[:5])[:300] if texts else
                   f"事件 {len(events)} 条（音频块 {audio_blocks}）")
        return self._r({"events": events, "count": len(events),
                        "transcript": "".join(texts) or None,
                        "audio_blocks": audio_blocks},
                       "drain", text_summary=f"实时事件: {summary}")

    def _session_close(self) -> DeviceResult:
        if self._session is None:
            return self._fail("无进行中的会话")
        try:
            self._ws_conn.close()
        except Exception:
            pass
        meta = {"sent": self._session["events_sent"],
                "received": self._session["events_received"]}
        self._session = None
        return self._r(meta, "session_close",
                       text_summary=f"会话已关闭（发 {meta['sent']} 收 {meta['received']}）")
