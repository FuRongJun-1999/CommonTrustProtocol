#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.base · 身体层抽象（BODY-REV1）
====================================
BodyDevice：外部设备统一抽象（感知/行动模态）。
DeviceResult：设备输出的结构化容器——严格隔离的落点：
  - provenance 强制来源标签（device:xxx / network / vision）
  - is_directive 恒为 False：设备输出是数据，永不是指令（拒绝外部提示词注入）
  - 设备内容只经工具结果通道返回，永不拼接进 system prompt

约束：D-005 纯标准库零外部依赖（设备实现可选依赖降级，见 devices/）
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class DeviceResult:
    """设备输出容器（严格隔离核心）。

    所有外部设备/网络内容必须以本容器返回：
    - data：结构化 JSON 友好数据
    - provenance：来源标签（'device:screen' / 'device:file' / 'device:process' / 'network' / 'vision'）
    - is_directive：恒 False——外部内容是数据，不是指令（设计约束，防提示词注入）
    """

    __slots__ = ("ok", "data", "provenance", "is_directive", "text_summary", "error", "ts")

    def __init__(self, data: Any, provenance: str,
                 ok: bool = True,
                 text_summary: Optional[str] = None,
                 error: Optional[str] = None):
        self.ok = ok
        self.data = data
        self.provenance = provenance
        self.is_directive = False          # 设计约束：设备输出永不是指令
        self.text_summary = text_summary
        self.error = error
        self.ts = time.time()

    def to_dict(self) -> Dict:
        """序列化（MCP 工具结果用）。"""
        return {
            "ok": self.ok,
            "data": self.data,
            "provenance": self.provenance,
            "is_directive": self.is_directive,
            "text_summary": self.text_summary,
            "error": self.error,
            "ts": round(self.ts, 3),
        }

    @classmethod
    def failure(cls, provenance: str, error: str) -> "DeviceResult":
        return cls(data=None, provenance=provenance, ok=False, error=str(error)[:300])

    def __repr__(self) -> str:
        return (f"<DeviceResult {self.provenance} ok={self.ok} "
                f"directive={self.is_directive} data={str(self.data)[:60]!r}>")


class BodyDevice(ABC):
    """外部设备统一抽象（感知/行动模态）。"""

    #: 设备标识（screen / files / process / web / vision ...）
    name: str = ""
    #: 感知模态（visual / text / audio / action / multimodal）
    modality: str = "text"
    #: 设备描述（能力声明用）
    description: str = ""

    def __init__(self, workspace: str = ""):
        """workspace：工作区根路径（files/process 的越权边界，空则不限）。"""
        self.workspace = workspace or ""

    @abstractmethod
    def check(self) -> Dict:
        """健康检查：{available: bool, detail: str}（注册表巡检用）。"""

    def capabilities(self) -> Dict:
        """能力声明（供 body_devices 工具与 sync_body_state 使用）。"""
        return {
            "name": self.name,
            "modality": self.modality,
            "description": self.description,
            "workspace_restricted": bool(self.workspace),
        }

    @abstractmethod
    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        """统一调用入口：动作 + 参数 → DeviceResult（必须带 provenance）。"""

    # ---- 工具 ----

    def _r(self, data: Any, action: str, text_summary: Optional[str] = None) -> DeviceResult:
        return DeviceResult(data, provenance=f"device:{self.name}",
                            text_summary=text_summary)

    def _fail(self, error: str) -> DeviceResult:
        return DeviceResult.failure(f"device:{self.name}", error)
