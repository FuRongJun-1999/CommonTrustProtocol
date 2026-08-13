#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.screen · 屏幕设备（BODY-REV1）
============================================
动作：
- capture: 截图 → 保存到工作区 screenshots/ → 返回 meta（路径/尺寸/字节数）
- check: 可用性探测

依赖策略（三级降级，D-005 兜底）：
  mss（快速，Windows 原生）→ PIL.ImageGrab → ctypes user32（零依赖兜底）

输出为 DeviceResult：图像文件是感知数据，text_summary 仅描述性文本。
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

# 截图目录（相对工作区）
_SHOT_DIR = "screenshots"


class ScreenDevice(BodyDevice):
    """屏幕截图设备（感知模态 visual）。"""

    name = "screen"
    modality = "visual"
    description = "屏幕截图（mss → PIL → ctypes 三级降级，零依赖兜底）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        self._backend: Optional[str] = None
        self._probe()

    # ---- 后端探测 ----

    def _probe(self) -> None:
        for name, loader in (
            ("mss", self._load_mss),
            ("pil", self._load_pil),
            ("ctypes", self._load_ctypes),
        ):
            if loader():
                self._backend = name
                return
        self._backend = None

    def _load_mss(self) -> bool:
        try:
            import mss  # type: ignore

            mss.mss()
            self._mss = mss
            return True
        except Exception:
            return False

    def _load_pil(self) -> bool:
        try:
            from PIL import ImageGrab  # type: ignore

            ImageGrab.grab(bbox=(0, 0, 8, 8))
            self._imagegrab = ImageGrab
            return True
        except Exception:
            return False

    def _load_ctypes(self) -> bool:
        try:
            import ctypes  # noqa: F401

            self._ctypes = ctypes
            return True
        except Exception:
            return False

    # ---- 接口 ----

    def check(self) -> Dict:
        if self._backend is None:
            return {"available": False, "detail": "无可用截图后端（mss/PIL/ctypes 均不可用）"}
        return {"available": True, "detail": f"后端: {self._backend}"}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["backend"] = self._backend
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        if action == "capture":
            return self._capture(params or {})
        return self._fail(f"未知动作 {action}（可用: capture）")

    # ---- 动作 ----

    def _capture(self, params: Dict) -> DeviceResult:
        if self._backend is None:
            return self._fail("无可用截图后端")
        try:
            # ctypes 路径产出 BMP 字节（零依赖）；mss/pil 产出 PIL Image
            bmp_bytes = None
            image = None
            if self._backend == "ctypes":
                bmp_bytes, width, height = self._grab_ctypes()
            else:
                image = self._grab()
                if image is None:
                    return self._fail("截图失败（后端返回空）")
                width, height = image.size

            shot_dir = os.path.join(self.workspace, _SHOT_DIR) if self.workspace else ""
            meta = {"width": width, "height": height, "backend": self._backend}
            if shot_dir:
                os.makedirs(shot_dir, exist_ok=True)
                if bmp_bytes is not None:
                    path = os.path.join(shot_dir, f"shot_{int(time.time() * 1000)}.bmp")
                    with open(path, "wb") as f:
                        f.write(bmp_bytes)
                else:
                    path = os.path.join(shot_dir, f"shot_{int(time.time() * 1000)}.png")
                    image.save(path, format="PNG")
                meta["path"] = os.path.abspath(path)
                meta["bytes"] = os.path.getsize(path)
                summary = f"屏幕截图已保存: {meta['path']}（{width}x{height}）"
            else:
                if bmp_bytes is not None:
                    meta["bytes"] = len(bmp_bytes)
                    meta["in_memory"] = True
                else:
                    import io

                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    meta["bytes"] = len(buf.getvalue())
                    meta["in_memory"] = True
                summary = f"屏幕截图（内存 {meta['bytes']} 字节，{width}x{height}）"
            return self._r(meta, "capture", text_summary=summary)
        except Exception as exc:
            return self._fail(f"截图异常: {exc}")

    def _grab(self):
        """按已探测后端截图（mss/pil），返回 PIL Image 或 None。"""
        if self._backend == "mss":
            with self._mss.mss() as sct:
                raw = sct.grab(sct.monitors[1])
                from PIL import Image  # type: ignore

                return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        if self._backend == "pil":
            return self._imagegrab.grab()
        return None

    def _grab_ctypes(self):
        """ctypes user32 零依赖截图（GDI BitBlt → 自编码 BMP 字节）。

        返回 (bmp_bytes, width, height)——完全不依赖 PIL。
        """
        import struct

        ctypes = self._ctypes
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)
        memdc = gdi32.CreateCompatibleDC(hdc)
        bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
        gdi32.SelectObject(memdc, bmp)
        gdi32.BitBlt(memdc, 0, 0, w, h, hdc, 0, 0, 0x00CC0020)  # SRCCOPY
        row_padded = ((w * 3 + 3) // 4) * 4
        buf = ctypes.create_string_buffer(row_padded * h)
        gdi32.GetDIBits(memdc, bmp, 0, h, buf, None, 0)
        gdi32.DeleteObject(bmp)
        gdi32.DeleteDC(memdc)
        user32.ReleaseDC(0, hdc)

        # 组装 BMP 文件（BITMAPFILEHEADER + BITMAPINFOHEADER + 像素 BGR 自底向上）
        pixel_size = row_padded * h
        file_size = 14 + 40 + pixel_size
        header = struct.pack(
            "<2sIHHI", b"BM", file_size, 0, 0, 14 + 40
        )
        info = struct.pack(
            "<IiiHHIIiiII",
            40, w, h, 1, 24, 0, pixel_size, 2835, 2835, 0, 0,
        )
        return header + info + buf.raw, w, h
