#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPRIM-REV1 视觉原语回归测试（语义时空图空间锚点）
====================================================
参照《Thinking with Visual Primitives》（DeepSeek V4）：视觉推理瓶颈
= 指代差距；视觉原语（bbox/点）是思维链的空间草稿纸。本模块把该思想
落地为确定性原语（零 LLM）：
1. VPrim 数据结构 + 锚点文本/描述/序列化
2. spatial_relation：确定性空间关系（上方/下方/左侧/包含/重叠/距离）
3. count_vprims：确定性计数（检测→定位→过滤→统计）
4. parse_anchor：推理链视觉锚点引用解析
5. 引擎 vprim_query：记忆 → 解析 → 计数/空间关系（MCP vprim 工具）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis.api import Agent  # noqa: E402
from aeis.vprim import (  # noqa: E402
    VPrim, spatial_relation, count_vprims, parse_anchor,
    vprims_to_scene_text, bbox_from_xywh,
)

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


def test_vprim_basic():
    moon = VPrim("moon", (420, 52, 484, 116), 0.52, source="yoloworld")
    check("锚点文本", moon.anchor_text() == "moon@(420,52,484,116)")
    check("描述格式", "64x64" in moon.describe() and "conf=0.52" in moon.describe())
    check("中心点", moon.center() == (452.0, 84.0))
    check("序列化", moon.to_dict()["category"] == "moon")
    check("xywh 转换", bbox_from_xywh(300, 200, 64, 64) == (300, 200, 364, 264))
    scene = vprims_to_scene_text([moon], "测试")
    check("场景文本", scene.startswith("[视觉原语 测试]") and "moon@" in scene)


def test_spatial_relations():
    moon = (420, 52, 484, 116)      # 上方小物体
    person = (208, 220, 654, 1136)  # 下方大物体
    left = (100, 400, 160, 460)
    right = (700, 400, 760, 460)
    big = (0, 0, 800, 600)          # 全屏

    check("上方", spatial_relation(moon, person)["relation"] == "above")
    check("下方", spatial_relation(person, moon)["relation"] == "below")
    check("左侧", spatial_relation(left, right)["relation"] == "left_of")
    check("右侧", spatial_relation(right, left)["relation"] == "right_of")
    check("包含", spatial_relation(big, moon)["relation"] == "contains")
    check("内部", spatial_relation(moon, big)["relation"] == "inside")
    check("距离字段", spatial_relation(moon, person)["distance"] > 0)
    check("重叠率字段", "overlap_ratio" in spatial_relation(moon, person))
    # 确定性：同输入同输出
    r1 = spatial_relation(moon, person)
    r2 = spatial_relation(moon, person)
    check("确定性", r1 == r2)


def test_count():
    vprims = [VPrim("moon", (1, 1, 10, 10), 0.5),
              VPrim("moon", (100, 100, 150, 150), 0.4),
              VPrim("person", (200, 200, 400, 900), 0.8)]
    c = count_vprims(vprims)
    check("总数", c["total"] == 3)
    check("分类计数", c["by_category"] == {"moon": 2, "person": 1})
    cm = count_vprims(vprims, "moon")
    check("过滤计数", cm["total"] == 2 and cm["filter"] == "moon")
    check("锚点列表", len(cm["anchors"]) == 2)


def test_parse_anchor():
    vp = parse_anchor("moon@(420,52,484,116)")
    check("解析类别", vp is not None and vp.category == "moon")
    check("解析坐标", vp.bbox == (420, 52, 484, 116))
    check("非锚点返回 None", parse_anchor("普通文本") is None)


def test_engine_query():
    a = Agent(identity="vprim-engine", db_path=":memory:")
    a.remember("[视觉原语 测试] moon@(420,52,484,116) 64x64 conf=0.52；"
               "person@(208,220,654,1136) 928x916 conf=0.83",
               importance=0.7, tags=["vision", "perception", "vprim"])
    c = a.vprim_query("count", {})
    check("引擎计数", c["status"] == "ok" and c["total"] == 2)
    s = a.vprim_query("spatial", {"a": [420, 52, 484, 116],
                                  "b": [208, 220, 654, 1136]})
    check("引擎空间关系", s["status"] == "ok" and s["spatial"]["relation"] == "above")
    an = a.vprim_query("anchors", {"limit": 5})
    check("引擎锚点列表", an["status"] == "ok" and len(an["anchors"]) == 2)
    bad = a.vprim_query("nope", {})
    check("未知动作", bad["status"] == "error")
    bad2 = a.vprim_query("spatial", {"a": [1, 2]})
    check("参数校验", bad2["status"] == "error")


def test_mcp_tool():
    """MCP vprim 工具注册（43 工具）。"""
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
    check("vprim 工具", "vprim" in tools)
    check("工具总数 43", len(tools) == 44, f"count={len(tools)}")
    proc.stdin.close()
    proc.wait(timeout=10)


def main():
    test_vprim_basic()
    test_spatial_relations()
    test_count()
    test_parse_anchor()
    test_engine_query()
    test_mcp_tool()
    print(f"\n===== VPRIM-REV1 视觉原语回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
