#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.registry · 设备注册表（BODY-REV1）
========================================
BodyRegistry：设备注册/发现/健康巡检/能力声明。
身体 = 自我的一部分（v1.13 语义延续）：设备清单与健康状态
同步进 self_model.state_description（cognition_report 可见）。
"""

import time
from typing import Dict, List, Optional

from .base import BodyDevice, DeviceResult


class BodyRegistry:
    """外部设备注册表（单引擎实例装配一次）。"""

    def __init__(self, workspace: str = ""):
        self.workspace = workspace
        self._devices: Dict[str, BodyDevice] = {}
        self._health_cache: Dict[str, Dict] = {}
        self._health_ts: float = 0.0
        self._health_ttl = 30.0  # 健康巡检缓存秒数

    # ---- 注册 ----

    def register(self, device: BodyDevice) -> "BodyRegistry":
        if device.name in self._devices:
            raise ValueError(f"设备 {device.name} 已注册")
        self._devices[device.name] = device
        return self

    def unregister(self, name: str) -> None:
        self._devices.pop(name, None)
        self._health_cache.pop(name, None)

    def get(self, name: str) -> Optional[BodyDevice]:
        return self._devices.get(name)

    def names(self) -> List[str]:
        return sorted(self._devices.keys())

    # ---- 能力声明 / 健康 ----

    def capabilities(self) -> List[Dict]:
        """全部设备的能力声明（body_devices 工具返回）。"""
        return [d.capabilities() for d in self._devices.values()]

    def health(self, refresh: bool = False) -> List[Dict]:
        """健康巡检（带 TTL 缓存）：每设备 check() 结果。"""
        now = time.time()
        if refresh or now - self._health_ts > self._health_ttl:
            self._health_cache = {
                name: dev.check() for name, dev in self._devices.items()
            }
            self._health_ts = now
        return [
            {"name": name, **self._health_cache.get(name, {"available": False, "detail": "未巡检"})}
            for name in sorted(self._devices)
        ]

    def summary(self) -> Dict:
        """身体摘要（sync_body_state 用）：
        {devices: [name...], available: [name...], unavailable: [name...]}"""
        health = self.health()
        return {
            "devices": [h["name"] for h in health],
            "available": [h["name"] for h in health if h.get("available")],
            "unavailable": [h["name"] for h in health if not h.get("available")],
        }

    # ---- 调用 ----

    def invoke(self, name: str, action: str, params: Optional[Dict] = None) -> DeviceResult:
        """统一设备调用。未知设备/未知动作 → 失败 DeviceResult（不抛异常）。"""
        device = self._devices.get(name)
        if device is None:
            return DeviceResult.failure(f"device:{name}", f"未知设备 {name}")
        try:
            return device.invoke(action, params or {})
        except Exception as exc:  # 设备实现异常 → 容器化失败（隔离边界）
            return DeviceResult.failure(f"device:{name}", str(exc))
