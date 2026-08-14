#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 读屏回归测试（screen.read_text · 文字=状态）
====================================================
管线：截图 → ROI 裁剪 → 降采样+灰度（高度压缩）→ rapidocr（本地 ONNX）
用途：游戏状态读取（血量/能量/卡名）等通用读屏——组合拳方案
（用户确认：通用能力必须识图；压缩+OCR 是快速通道）
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from aeis.api import Agent  # noqa: E402

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def make_state_image(path, scale_down=1):
    """合成"游戏状态"图：大字号数字 + 中文（模拟杀戮尖塔 UI）。"""
    img = Image.new("RGB", (800, 600), (30, 30, 40))
    d = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
        font_mid = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
    except Exception:
        font_big = font_mid = ImageFont.load_default()
    d.text((50, 40), "52/70", fill=(255, 255, 255), font=font_big)
    d.text((50, 120), "3/3", fill=(255, 220, 100), font=font_big)
    d.text((50, 200), "回合 2", fill=(200, 220, 255), font=font_mid)
    d.text((500, 40), "28", fill=(255, 100, 100), font=font_big)
    d.text((400, 400), "打击 痛击 防御", fill=(255, 255, 255), font=font_mid)
    if scale_down > 1:
        img = img.resize((800 // scale_down, 600 // scale_down))
    img.save(path)
    return path


def test_ocr_state():
    ws = tempfile.mkdtemp()
    img = make_state_image(os.path.join(ws, "state.png"))
    a = Agent(identity="ocr-state", db_path=":memory:")
    r = a.device_call("screen", "read_text",
                      {"screen": img, "scale": 2})
    check("OCR 成功", r["ok"] is True)
    text = r.get("data", {}).get("text", "")
    check("血量识别", "52/70" in text, text[:60])
    check("能量识别", "3/3" in text)
    check("回合识别", "回合" in text)
    check("敌人血量", "28" in text)
    check("卡名识别", "打击" in text and "痛击" in text)
    check("段级 bbox", r["data"]["count"] >= 3
          and r["data"]["segments"][0]["bbox"][0] >= 0)
    check("容器隔离", r["provenance"] == "device:screen"
          and r["is_directive"] is False)


def test_ocr_roi():
    """ROI 裁剪：只识别指定区域（更快更准）。"""
    ws = tempfile.mkdtemp()
    img = make_state_image(os.path.join(ws, "state.png"))
    a = Agent(identity="ocr-roi", db_path=":memory:")
    # 只读左上区域（血量/能量），不含手牌
    r = a.device_call("screen", "read_text",
                      {"screen": img, "roi": [0, 0, 300, 300], "scale": 2})
    text = r.get("data", {}).get("text", "")
    check("ROI 含血量", "52/70" in text)
    check("ROI 排除手牌", "打击" not in text, text[:60])


def test_ocr_fallback():
    """OCR 依赖缺失时优雅降级（不装 rapidocr 的环境）。"""
    import importlib
    import sys as _sys

    if importlib.util.find_spec("rapidocr_onnxruntime") is None:
        a = Agent(identity="ocr-fallback", db_path=":memory:")
        r = a.device_call("screen", "read_text", {})
        check("降级提示", not r["ok"] and "rapidocr" in r["error"])
    else:
        check("rapidocr 已装（跳过降级测试）", True)


def main():
    test_ocr_state()
    test_ocr_roi()
    test_ocr_fallback()
    print(f"\n===== OCR 读屏回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
