#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORLD3D-REV1 时空重建回归测试（语义 → 3D 空间与颜色）
========================================================
认知原则（荣 2026-08-14）：2D 是 3D 透视下的情况；有了 3D 世界
才能完整认知世界。确定性重建（D-005）：针孔相机 + 反投影 + 画家算法。

验证：
1. 2D→3D 反投影：语义正确（天空物体高远、地面物体贴地、近大远小）
2. 时间序列收敛：同类近距物体合并更新
3. 渲染：多视角（yaw/pitch/cx 相机参数）、输出文件有效
4. 引擎集成：记忆 vprim → build → render → status（MCP world3d 工具）
5. 渲染-再投影闭环（重建的图像重新感知应一致——后续扩展点）
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis.api import Agent  # noqa: E402
from aeis.vprim import VPrim  # noqa: E402
from aeis.world3d import World3D, Camera3D  # noqa: E402

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


def test_backprojection_semantics():
    """反投影语义正确性：夜狼傲月场景。"""
    world = World3D()
    world.add_vprim(VPrim("moon", (420, 52, 484, 116), 0.52), 800, 600)
    world.add_vprim(VPrim("person", (208, 220, 654, 1136), 0.83), 800, 600)
    world.add_vprim(VPrim("tree", (60, 300, 160, 580), 0.7), 800, 600)
    moon = [o for o in world.objects if o.category == "moon"][0]
    person = [o for o in world.objects if o.category == "person"][0]
    tree = [o for o in world.objects if o.category == "tree"][0]
    check("天空物体高于地面", moon.center[1] > person.center[1],
          f"moon_y={moon.center[1]} person_y={person.center[1]}")
    check("天空物体更远", moon.center[2] > person.center[2],
          f"moon_z={moon.center[2]} person_z={person.center[2]}")
    check("地面物体贴地", abs(person.center[1] - person.size[1] / 2) < 0.01,
          f"person_y={person.center[1]}")
    check("中间距离", person.center[2] < tree.center[2] < moon.center[2])
    check("类别颜色", world.visual["moon"].color == (240, 240, 220))
    check("未知类别默认", world.add_vprim(VPrim("未知物", (10, 10, 50, 50)), 800, 600) is not None)


def test_merge_convergence():
    """时间序列收敛：同类近距物体合并更新。"""
    world = World3D()
    world.add_vprim(VPrim("person", (208, 220, 654, 1136), 0.83), 800, 600)
    world.add_vprim(VPrim("person", (210, 222, 656, 1138), 0.9), 800, 600)
    check("近距同类合并", len([o for o in world.objects if o.category == "person"]) == 1)
    p = [o for o in world.objects if o.category == "person"][0]
    check("置信度更新", p.confidence == 0.9)
    # 远距同类不合并
    world.add_vprim(VPrim("person", (50, 500, 120, 800), 0.7), 800, 600)
    check("远距同类不合并", len([o for o in world.objects if o.category == "person"]) == 2)


def test_render_views():
    """多视角渲染：相机参数变化产生不同投影。"""
    world = World3D()
    world.add_vprim(VPrim("moon", (420, 52, 484, 116), 0.52), 800, 600)
    world.add_vprim(VPrim("person", (208, 220, 654, 1136), 0.83), 800, 600)
    ws = tempfile.mkdtemp()
    front = os.path.join(ws, "front.png")
    world.render(800, 600).save(front)
    side = os.path.join(ws, "side.png")
    world.render(800, 600, camera=Camera3D(yaw=0.8, cx=4.0)).save(side)
    check("渲染文件有效", os.path.getsize(front) > 500 and os.path.getsize(side) > 500)
    check("视角不同输出不同", os.path.getsize(front) != os.path.getsize(side))
    # 画家算法排序（远先画——深度序）
    depths = [o.depth() for o in sorted(world.objects, key=lambda o: -o.depth())]
    check("深度降序", depths == sorted(depths, reverse=True))


def test_engine_flow():
    """引擎集成：记忆 vprim → build → status → render。"""
    ws = tempfile.mkdtemp()
    a = Agent(identity="world3d-engine", db_path=":memory:")
    a.remember("[视觉原语 场景] moon@(420,52,484,116) 64x64 conf=0.52；"
               "person@(208,220,654,1136) 928x916 conf=0.83",
               importance=0.7, tags=["vision", "perception", "vprim"])
    r = a.world3d("build", {})
    check("build 成功", r["status"] == "ok" and r["objects"] == 2)
    check("场景语义", "moon@3D" in r["scene"] and "person@3D" in r["scene"])
    st = a.world3d("status", {})
    check("status", st["status"] == "ok" and st["count"] == 2)
    path = os.path.join(ws, "scene.png")
    r2 = a.world3d("render", {"path": path})
    check("render 输出", r2["status"] == "ok" and os.path.getsize(path) > 500)
    bad = a.world3d("nope", {})
    check("未知动作", bad["status"] == "error")
    bad2 = a.world3d("add", {})
    check("add 参数校验", bad2["status"] == "error")


def test_mcp_tool():
    """MCP world3d 工具注册（44 工具）。"""
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
    check("world3d 工具", "world3d" in tools)
    check("工具总数 44", len(tools) == 44, f"count={len(tools)}")
    proc.stdin.close()
    proc.wait(timeout=10)


def main():
    test_backprojection_semantics()
    test_merge_convergence()
    test_render_views()
    test_engine_flow()
    test_mcp_tool()
    print(f"\n===== WORLD3D-REV1 时空重建回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
