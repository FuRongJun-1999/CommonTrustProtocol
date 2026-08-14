#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉语义识别 v1 回归测试（YOLO-World 开放词汇 + 文生图词表）
==============================================================
1. 词表结构：分组/数量/中英映射/归一化
2. YOLO-World 提供者：工厂优先、classes 自定义（不实测检测——权重 338MB
   冷启动重，提供者装配与词表逻辑为纯逻辑测试；检测能力由实验观测记录）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis import vision_categories as vc  # noqa: E402
from aeis.vision import create_vision_provider, YOLOWorldVisionProvider  # noqa: E402

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


def test_categories():
    groups = vc.CORE_CATEGORIES
    check("词表分组", len(groups) >= 8, f"groups={len(groups)}")
    total = len(vc.category_list("en"))
    check("英文词表规模", total >= 150, f"count={total}")
    zh = vc.category_list("zh")
    check("中文词表同规模", len(zh) == total)
    # 关键物体在词表（文生图高频）
    for key in ["wolf", "moon", "dragon", "sword", "castle", "person",
                "cherry_blossoms", "mecha", "rainbow", "ice_cream"]:
        check(f"词表含 {key}", key in vc.DEFAULT_CLASSES)
    # 中英映射
    check("中文映射", vc.ZH_TO_EN["狼"] == "wolf" and vc.ZH_TO_EN["月亮"] == "moon")
    # 归一化
    check("混合归一化", vc.normalize_classes(["狼", "moon", "城堡"]) == ["wolf", "moon", "castle"])
    check("空参默认", vc.normalize_classes(None) == vc.DEFAULT_CLASSES)
    check("去重", vc.normalize_classes(["狼", "wolf", "狼"]) == ["wolf"])
    # 英文标签唯一性（YOLO-World set_classes 要求）
    en_list = vc.DEFAULT_CLASSES
    check("英文标签唯一", len(set(en_list)) == len(en_list))
    check("标签格式（无空格大写）",
          all(" " not in c and c == c.lower() for c in en_list))


def test_provider_factory():
    prov = create_vision_provider()
    check("工厂返回提供者", prov is not None)
    # 提供者链：world → yolov8 → null；本机 world 权重存在应优先
    if isinstance(prov, YOLOWorldVisionProvider):
        check("工厂优先 YOLO-World", prov.name == "yoloworld")
        check("world 可用性", prov.available() is True or "权重不存在" in (prov._load_error or ""))
    else:
        check("工厂降级链", prov.name in ("yolov8", "null"))


def test_mcp_see_classes():
    """MCP see 工具注册含 classes 参数。"""
    import json
    import subprocess

    env = dict(os.environ)
    env.setdefault("AEIS_DB", ":memory:")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "aeis.mcp.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        env=env, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def send(msg):
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    def notify(msg):
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "t", "version": "0"}}})
    notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = {t["name"]: t for t in r["result"]["tools"]}
    check("see 工具存在", "see" in tools)
    if "see" in tools:
        props = tools["see"]["inputSchema"].get("properties", {})
        check("see classes 参数", "classes" in props, f"props={sorted(props.keys())}")
    check("工具总数", len(tools) == 41, f"count={len(tools)}")
    proc.stdin.close()
    proc.wait(timeout=10)


def main():
    test_categories()
    test_provider_factory()
    test_mcp_see_classes()
    print(f"\n===== 视觉语义识别 v1 回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
