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

try:
    import numpy  # type: ignore
except ImportError:  # pragma: no cover - 纯标准库降级（_match_numpy 不可用）
    numpy = None

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
        if action == "snapshot_region":
            return self._snapshot_region(params or {})
        if action == "locate":
            return self._locate(params or {})
        if action == "diff":
            return self._diff(params or {})
        return self._fail(f"未知动作 {action}（可用: capture/snapshot_region/locate/diff）")

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

    # =====================================================================
    # 视觉面 v1（快速路线：locate 模板匹配 / diff 区域对比）
    # 语义：视觉 = 信息差处理——已知目标用模板匹配（确定性），
    #       变化检测用区域对比（注意力原语），均本地毫秒级。
    # 依赖链：opencv → numpy → 纯标准库（逐级降级，D-005 兜底）
    # =====================================================================

    def _load_image_array(self, path: str):
        """读图 → numpy 数组（RGB）。路径为空则截当前屏。"""
        if not path:
            img = self._grab()
        else:
            from PIL import Image  # type: ignore

            img = Image.open(path).convert("RGB")
        return numpy.asarray(img)

    def _snapshot_region(self, p: Dict) -> DeviceResult:
        """截取屏幕指定区域存为模板（locate 的模板来源）。"""
        try:
            x = int(p.get("x", 0))
            y = int(p.get("y", 0))
            w = int(p.get("w", 0))
            h = int(p.get("h", 0))
        except (TypeError, ValueError):
            return self._fail("x/y/w/h 必须为整数")
        if w <= 0 or h <= 0:
            return self._fail("区域宽高必须 > 0")
        if self._backend is None:
            return self._fail("无可用截图后端")
        shot_dir = os.path.join(self.workspace, "templates") if self.workspace else "templates"
        os.makedirs(shot_dir, exist_ok=True)
        full = self._grab()
        if full is None:
            return self._fail("截图失败")
        region = full.crop((x, y, x + w, y + h))
        path = os.path.join(shot_dir, f"tpl_{int(time.time() * 1000)}.png")
        region.save(path, format="PNG")
        meta = {"path": os.path.abspath(path), "x": x, "y": y, "w": w, "h": h}
        return self._r(meta, "snapshot_region",
                       text_summary=f"模板已保存: {meta['path']}（{w}x{h} @ {x},{y}）")

    def _locate(self, p: Dict) -> DeviceResult:
        """模板匹配：在屏幕/参考图中搜索模板位置（快速路线原语）。

        参数：template（模板路径，必填）；screen（参考图路径，空=当前屏）；
              threshold（匹配阈值 0~1，默认 0.8）。
        返回：{found, x, y, w, h, confidence, method}
        """
        template = str(p.get("template", "")).strip()
        if not template or not os.path.isfile(template):
            return self._fail("缺少有效 template 路径")
        try:
            threshold = max(0.1, min(float(p.get("threshold", 0.8)), 1.0))
        except (TypeError, ValueError):
            threshold = 0.8
        try:
            screen_arr = self._load_image_array(str(p.get("screen", "")))
            tpl_arr = self._load_image_array(template)
        except Exception as exc:
            return self._fail(f"图像读取失败: {exc}")
        if screen_arr.shape[0] < tpl_arr.shape[0] or screen_arr.shape[1] < tpl_arr.shape[1]:
            return self._fail("模板大于参考图")

        method = "opencv"
        try:
            import cv2  # type: ignore

            result = cv2.matchTemplate(screen_arr, tpl_arr, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
        except Exception:
            method = "numpy"
            max_val, max_loc = self._match_numpy(screen_arr, tpl_arr)
        h, w = tpl_arr.shape[:2]

        if max_val >= threshold:
            x, y = int(max_loc[0]), int(max_loc[1])
            data = {"found": True, "x": x, "y": y, "w": int(w), "h": int(h),
                    "confidence": round(float(max_val), 4), "method": method}
            return self._r(data, "locate",
                           text_summary=f"定位成功: ({x}, {y}) {w}x{h} conf={max_val:.2f}（{method}）")
        data = {"found": False, "x": None, "y": None,
                "confidence": round(float(max_val), 4), "method": method,
                "best_x": int(max_loc[0]), "best_y": int(max_loc[1])}
        return self._r(data, "locate",
                       text_summary=f"未找到（最佳 conf={max_val:.2f} < {threshold:.2f}，{method}）")

    def _match_numpy(self, screen_arr, tpl_arr):
        """numpy 滑动窗口匹配（归一化相关系数近似：SSD 负值）。"""
        sh, sw = screen_arr.shape[:2]
        th, tw = tpl_arr.shape[:2]
        tpl_flat = tpl_arr.astype(float).reshape(-1)
        best_val, best_loc = -1.0, (0, 0)
        step = max(1, min(th, tw) // 16)  # 步进采样加速
        t_norm = numpy.linalg.norm(tpl_flat)
        for y in range(0, sh - th + 1, step):
            for x in range(0, sw - tw + 1, step):
                win = screen_arr[y:y + th, x:x + tw].astype(float).reshape(-1)
                denom = numpy.linalg.norm(win) * t_norm
                if denom == 0:
                    continue
                sim = float(numpy.dot(win, tpl_flat) / denom)
                if sim > best_val:
                    best_val, best_loc = sim, (x, y)
        return best_val, best_loc

    def _diff(self, p: Dict) -> DeviceResult:
        """区域对比（注意力原语）：参考图 vs 当前图，返回变化区域。

        参数：reference（参考图路径，必填）；target（目标图，空=当前屏）；
              block（块大小，默认 16）；threshold（变化敏感度 0~1，默认 0.1）。
        返回：{changed: bool, regions: [{x,y,w,h,change}], change_ratio}
        """
        reference = str(p.get("reference", "")).strip()
        if not reference or not os.path.isfile(reference):
            return self._fail("缺少有效 reference 路径")
        try:
            block = max(4, min(int(p.get("block", 16)), 128))
            threshold = max(0.0, min(float(p.get("threshold", 0.1)), 1.0))
        except (TypeError, ValueError):
            block, threshold = 16, 0.1
        try:
            ref_arr = self._load_image_array(reference)
            cur_arr = self._load_image_array(str(p.get("target", "")))
        except Exception as exc:
            return self._fail(f"图像读取失败: {exc}")

        # 尺寸对齐（不同尺寸 → 以较小者为准，报告尺寸差异）
        if ref_arr.shape != cur_arr.shape:
            h = min(ref_arr.shape[0], cur_arr.shape[0])
            w = min(ref_arr.shape[1], cur_arr.shape[1])
            ref_arr, cur_arr = ref_arr[:h, :w], cur_arr[:h, :w]

        try:
            import cv2  # type: ignore

            diff_map = cv2.absdiff(cur_arr, ref_arr).mean(axis=2)
            changed_mask = diff_map > (threshold * 255)
        except Exception:
            changed_mask = (numpy.abs(cur_arr.astype(int) - ref_arr.astype(int))
                            .mean(axis=2) > (threshold * 255))

        h, w = changed_mask.shape
        regions = []
        step = block
        for y in range(0, h, step):
            for x in range(0, w, step):
                blk = changed_mask[y:y + step, x:x + step]
                if blk.any():
                    regions.append({
                        "x": int(x), "y": int(y),
                        "w": int(blk.shape[1]), "h": int(blk.shape[0]),
                        "change": round(float(blk.mean()), 4),
                    })
        # 相邻块合并（简并：仅报告变化比例与块数）
        change_ratio = round(float(changed_mask.mean()), 4)
        data = {
            "changed": change_ratio > 0,
            "change_ratio": change_ratio,
            "region_count": len(regions),
            "regions": regions[:100],
            "regions_truncated": len(regions) > 100,
        }
        summary = (f"画面{'有' if data['changed'] else '无'}变化"
                   f"（比例 {change_ratio:.2%}，{len(regions)} 块）")
        return self._r(data, "diff", text_summary=summary)

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
