#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.control · 电脑控制设备（BODY-REV1 批次 3 · 高危设备）
====================================================================
动作（白名单，全部经 pyautogui，可选依赖）：
- mouse_position: 当前鼠标坐标（只读）
- mouse_move: 移动鼠标（x, y）
- mouse_click: 点击（x, y, button）
- key_type: 键盘输入（text；禁特殊键序列）
- screenshot: 全屏截图（pyautogui 自带）

安全边界（高危设备强化）：
- danger_level: high（能力声明中标注——控制类设备直接操作宿主系统）
- 动作白名单：仅上述 5 个，无 shell/无文件写入
- key_type 文本上限 + 禁回车换行（防脚本注入类输入）
- 依赖缺失优雅降级（check 返回 unavailable + 安装提示）
- 输出容器化：provenance=device:control，is_directive 恒 False

注意：本设备能力直接控制宿主鼠标键盘——调用方须有明确授权场景。
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

KEY_TYPE_MAX = 200      # 键盘输入文本上限（字符）
MOVE_BOUND = 16384      # 坐标上限（防御性）


class ControlDevice(BodyDevice):
    """电脑控制设备（鼠标/键盘 · 高危 · 动作白名单）。"""

    name = "control"
    modality = "action"
    description = "电脑控制（鼠标/键盘 · 高危设备 · 动作白名单）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        self._pyautogui = None
        self._probe()

    def _probe(self) -> None:
        try:
            import pyautogui  # type: ignore

            self._pyautogui = pyautogui
            # 安全默认：移动失败保护（防失控飞屏）
            try:
                pyautogui.FAILSAFE = True
            except Exception:
                pass
        except Exception:
            pass

    # ---- 接口 ----

    def check(self) -> Dict:
        if self._pyautogui is None:
            return {"available": False, "detail": "pyautogui 未安装（pip install pyautogui）"}
        return {"available": True, "detail": "pyautogui 可用（FAILSAFE 已启用）"}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["actions"] = ["mouse_position", "mouse_move", "mouse_click",
                           "key_type", "screenshot"]
        caps["danger_level"] = "high"   # 高危设备标注（调用方须授权）
        caps["notes"] = "直接操作宿主鼠标键盘；key_type 禁换行"
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        if self._pyautogui is None:
            return self._fail("控制不可用：pip install pyautogui")
        p = params or {}
        try:
            if action == "mouse_position":
                return self._mouse_position()
            if action == "mouse_move":
                return self._mouse_move(p)
            if action == "mouse_click":
                return self._mouse_click(p)
            if action == "key_type":
                return self._key_type(p)
            if action == "screenshot":
                return self._screenshot()
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（白名单: mouse_position/mouse_move/mouse_click/key_type/screenshot）")

    # ---- 动作 ----

    def _coord(self, p: Dict, key: str, default: int) -> int:
        try:
            v = int(p.get(key, default))
        except (TypeError, ValueError):
            return default
        return max(-MOVE_BOUND, min(MOVE_BOUND, v))

    def _mouse_position(self) -> DeviceResult:
        x, y = self._pyautogui.position()
        return self._r({"x": int(x), "y": int(y)}, "mouse_position",
                       text_summary=f"鼠标位置 ({x}, {y})")

    def _mouse_move(self, p: Dict) -> DeviceResult:
        x = self._coord(p, "x", 0)
        y = self._coord(p, "y", 0)
        duration = max(0.0, min(float(p.get("duration", 0.3)), 5.0))
        self._pyautogui.moveTo(x, y, duration=duration)
        return self._r({"x": x, "y": y}, "mouse_move",
                       text_summary=f"鼠标移至 ({x}, {y})")

    def _mouse_click(self, p: Dict) -> DeviceResult:
        x = self._coord(p, "x", 0)
        y = self._coord(p, "y", 0)
        button = str(p.get("button", "left"))
        if button not in ("left", "right", "middle"):
            return self._fail(f"非法按键: {button}")
        self._pyautogui.click(x=x, y=y, button=button)
        return self._r({"x": x, "y": y, "button": button}, "mouse_click",
                       text_summary=f"已点击 ({x}, {y}) {button}")

    def _key_type(self, p: Dict) -> DeviceResult:
        text = str(p.get("text", ""))
        if not text:
            return self._fail("缺少 text")
        if len(text) > KEY_TYPE_MAX:
            return self._fail(f"文本过长（{len(text)} 字符，上限 {KEY_TYPE_MAX}）")
        if "\n" in text or "\r" in text:
            return self._fail("禁换行（防输入注入）")
        self._pyautogui.typewrite(text, interval=float(p.get("interval", 0.02)))
        return self._r({"chars": len(text)}, "key_type",
                       text_summary=f"已输入 {len(text)} 字符")

    def _screenshot(self) -> DeviceResult:
        image = self._pyautogui.screenshot()
        shot_dir = os.path.join(self.workspace, "screenshots") if self.workspace else ""

        if shot_dir:
            _os = os
            _os.makedirs(shot_dir, exist_ok=True)
            path = _os.path.join(shot_dir, f"ctl_{int(time.time() * 1000)}.png")
            image.save(path, format="PNG")
            meta = {"path": _os.path.abspath(path),
                    "bytes": _os.path.getsize(path),
                    "width": image.width, "height": image.height}
            return self._r(meta, "screenshot",
                           text_summary=f"控制截图已保存: {meta['path']}")
        import io

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return self._r({"bytes": len(buf.getvalue()), "in_memory": True,
                        "width": image.width, "height": image.height},
                       "screenshot", text_summary="控制截图（内存）")
