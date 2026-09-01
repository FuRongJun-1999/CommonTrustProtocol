#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body · 身体层（BODY-REV1）
============================
自接外部设备（screen/files/process），严格拒绝外部提示词注入：
- 设备输出只作为结构化工具结果（DeviceResult + provenance）
- is_directive 恒 False：外部内容是数据，永不是指令
- 认知层摄取前经 security.classify_external_text / result_to_memory_input
"""

from .base import BodyDevice, DeviceResult
from .registry import BodyRegistry
from .security import (
    classify_external_text,
    directive_scan,
    result_to_memory_input,
    sanitize_device_text,
)
from .devices.screen import ScreenDevice
from .devices.files import FilesDevice
from .devices.process import ProcessDevice
from .devices.audio import AudioDevice
from .devices.control import ControlDevice
from .devices.browser import BrowserDevice
from .devices.realtime import RealtimeDevice

__all__ = [
    "BodyDevice", "DeviceResult", "BodyRegistry",
    "classify_external_text", "directive_scan", "result_to_memory_input",
    "sanitize_device_text",
    "ScreenDevice", "FilesDevice", "ProcessDevice", "AudioDevice",
    "ControlDevice", "BrowserDevice", "RealtimeDevice",
]


def build_default_registry(workspace: str = "") -> BodyRegistry:
    """装配默认设备集（screen/files/process/audio/control/browser/realtime）。"""
    registry = BodyRegistry(workspace=workspace)
    registry.register(ScreenDevice(workspace))
    registry.register(FilesDevice(workspace))
    registry.register(ProcessDevice(workspace))
    registry.register(AudioDevice(workspace))
    registry.register(ControlDevice(workspace))
    registry.register(BrowserDevice(workspace))
    registry.register(RealtimeDevice(workspace))
    return registry
